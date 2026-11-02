package dev.godpc.industrialcolonies.geology;

import com.google.gson.*;
import java.io.Reader;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.Consumer;
import static dev.godpc.industrialcolonies.geology.GeologyConfig.*;
import static dev.godpc.industrialcolonies.geology.GeologyMath.*;

/** Exercises production planner/math without Minecraft, world writes, or a Gradle build. */
public final class GeologyPlannerSelfTest {
    private static long checks;
    private static Config config;
    private static final class CountingSampler implements GeologyPlanner.Sampler {
        int calls;
        public GeologyPlanner.Site sample(int x,int z) {
            calls++;
            // A deterministic patchwork, including multi-family terrain. Count calls separately:
            // this arithmetic is NOT a benchmark of Minecraft/Tectonic noise-column cost.
            int family=bounded(seed(19,Math.floorDiv(x,900),Math.floorDiv(z,900),73),6);
            return switch(family) {
                case 0 -> new GeologyPlanner.Site("test:mountain",Set.of("mountain_highland","cold_high_altitude"),"mountain",150);
                case 1 -> new GeologyPlanner.Site("test:badlands",Set.of("arid_badlands","desert_basin"),"normal",80);
                case 2 -> new GeologyPlanner.Site("test:wetland",Set.of("wetland","ordinary_forest"),"normal",63);
                case 3 -> new GeologyPlanner.Site("test:ocean",Set.of("coastal_oceanic"),"normal",35);
                case 4 -> new GeologyPlanner.Site("test:volcano",Set.of("mountain_highland","volcanic_ashen"),"extreme",210);
                default -> new GeologyPlanner.Site("test:plains",Set.of("sedimentary_plains","ordinary_plains"),"normal",70);
            };
        }
    }

    public static void main(String[] args) throws Exception {
        Path resources=Path.of(args[0]).resolve("src/main/resources/data/industrial_colonies/geology");
        config=new Config(read(resources.resolve("settings.json")),read(resources.resolve("biome_families.json")),read(resources.resolve("deposit_families.json")));
        validate(config);
        invalidOverrideTests();
        mathAndQuality();
        richPoolSplitTests();
        biomeVetoes();
        spacingAndOrder();
        shapeTests();
        quotasAndAssociationData();
        uraniumGuaranteeOverhead();
        broadPhaseTests();
        microProbabilityModel();
        System.out.printf("PASS: %,d planner/math/data assertions. World mutation and actual Minecraft noise performance are intentionally not covered.%n",checks);
    }

    private static JsonObject read(Path path) throws Exception {
        try(Reader reader=Files.newBufferedReader(path)){return JsonParser.parseReader(reader).getAsJsonObject();}
    }
    private static void require(boolean ok,String message){checks++;if(!ok)throw new AssertionError(message);}
    private static void near(double actual,double wanted,String message){require(Math.abs(actual-wanted)<1e-9,message+": "+actual+" != "+wanted);}
    private static GeologyPlanner planner(CountingSampler sampler){return new GeologyPlanner(246813579L,config,sampler);}

    private static Config copyConfig(){return new Config(config.settings().deepCopy(),config.biomes().deepCopy(),config.deposits().deepCopy());}
    private static JsonObject first(Config c){return array(c.deposits(),"deposits").get(0).getAsJsonObject();}
    private static void rejects(String label,Consumer<Config> edit){
        Config changed=copyConfig();edit.accept(changed);boolean rejected=false;
        try{validate(changed);}catch(IllegalArgumentException expected){rejected=true;}
        require(rejected,"Unsafe override accepted: "+label);
    }
    private static void invalidOverrideTests(){
        long before=checks;
        rejects("zero intended cap",c->object(c.settings(),"geometry").addProperty("maxIntendedBlocks",0));
        rejects("above intended cap",c->object(c.settings(),"geometry").addProperty("maxIntendedBlocks",100001));
        rejects("quality-adjusted maximum",c->object(c.settings(),"quality").getAsJsonArray("sizeMultipliers").set(3,new JsonPrimitive(1000)));
        rejects("normal size exceeds quality-adjusted cap",c->first(c).addProperty("normalSizeMax",50000));
        rejects("negative size multiplier",c->object(c.settings(),"quality").getAsJsonArray("sizeMultipliers").set(0,new JsonPrimitive(-1)));
        rejects("nonfinite size multiplier",c->object(c.settings(),"quality").getAsJsonArray("sizeMultipliers").set(0,new JsonPrimitive(Double.NaN)));
        rejects("nonfinite rich multiplier",c->object(c.settings(),"quality").getAsJsonArray("richMultipliers").set(0,new JsonPrimitive(Double.POSITIVE_INFINITY)));
        rejects("invalid quality total",c->object(c.settings(),"quality").getAsJsonArray("base").set(0,new JsonPrimitive(.8)));
        rejects("nonfinite quality probability",c->object(c.settings(),"quality").getAsJsonArray("base").set(0,new JsonPrimitive(Double.NaN)));
        rejects("too small region",c->c.settings().addProperty("regionSize",127));
        rejects("too large region",c->c.settings().addProperty("regionSize",65537));
        rejects("global scan radius",c->c.settings().addProperty("globalMinSpacing",512*17));
        rejects("same family scan radius",c->first(c).addProperty("sameFamilyMinSpacing",512*33));
        rejects("configured geometric scan radius",c->object(c.settings(),"geometry").addProperty("regionSearchRadius",9));
        rejects("negative geometric scan radius",c->object(c.settings(),"geometry").addProperty("regionSearchRadius",-1));
        rejects("cave scan radius",c->object(c.settings(),"geometry").addProperty("caveSearchRange",129));
        for(double bad:new double[]{Double.NaN,Double.POSITIVE_INFINITY,Double.NEGATIVE_INFINITY,-1}){
            rejects("global spacing "+bad,c->c.settings().addProperty("globalMinSpacing",bad));
            rejects("family spacing "+bad,c->first(c).addProperty("sameFamilyMinSpacing",bad));
            rejects("base weight "+bad,c->first(c).addProperty("baseWeight",bad));
            rejects("biome weight "+bad,c->object(first(c),"biomeWeights").addProperty("mountain_highland",bad));
            rejects("depth weight "+bad,c->first(c).getAsJsonArray("depthWeights").set(0,new JsonPrimitive(bad)));
            rejects("rich pool weight "+bad,c->first(c).getAsJsonArray("richOres").get(0).getAsJsonObject().addProperty("weight",bad));
        }
        rejects("all zero rich pool",c->first(c).getAsJsonArray("richOres").get(0).getAsJsonObject().addProperty("weight",0));
        rejects("overflowing rich pool total",c->{
            JsonArray ores=first(c).getAsJsonArray("richOres");JsonObject huge=ores.get(0).getAsJsonObject().deepCopy();
            huge.addProperty("weight",Double.MAX_VALUE);ores.set(0,huge);ores.add(huge.deepCopy());
        });
        rejects("inverted depth anchors",c->object(c.settings(),"depth").addProperty("shallowY",-10));
        rejects("negative micro frequency",c->object(c.settings(),"micro").addProperty("frequencyMultiplier",-1));
        rejects("nonfinite micro frequency",c->object(c.settings(),"micro").addProperty("frequencyMultiplier",Double.NaN));
        for(String anchor:List.of("shallowY","midY","deepY","minY","maxY"))
            for(double bad:new double[]{Double.NaN,Double.POSITIVE_INFINITY,Double.NEGATIVE_INFINITY})
                rejects("depth anchor "+anchor+" "+bad,c->object(c.settings(),"depth").addProperty(anchor,bad));
        for(String property:List.of("majorWeight","caveExposure","indicatorExposure"))
            for(double bad:new double[]{Double.NaN,Double.POSITIVE_INFINITY,Double.NEGATIVE_INFINITY,-1})
                rejects("terrain multiplier "+property+" "+bad,c->object(object(c.settings(),"terrain"),"normal").addProperty(property,bad));
        for(double bad:new double[]{Double.NaN,Double.POSITIVE_INFINITY,Double.NEGATIVE_INFINITY,-1})
            rejects("trace resource weight "+bad,c->object(c.settings(),"trace").getAsJsonArray("resources").get(0).getAsJsonObject().addProperty("weight",bad));
        for(int bad:new int[]{-1,129}){
            rejects("trace surface depth "+bad,c->object(c.settings(),"trace").addProperty("maxSurfaceDepth",bad));
            rejects("placer riverbank radius "+bad,c->object(c.settings(),"placer").addProperty("maxRiverbankDistance",bad));
        }
        System.out.printf("Safety: %,d invalid configuration mutations rejected (volume/quality, finite weights/spacing/depth/terrain, bounded searches and trace rules).%n",checks-before);
    }

    private static void mathAndQuality() {
        GeologyPlanner p=planner(new CountingSampler());
        double[] w={.5,2,1.25};
        near(depth(100,42,0,-44,w),.5,"Shallow clamp");
        near(depth(42,42,0,-44,w),.5,"Shallow anchor");
        near(depth(21,42,0,-44,w),1.25,"Shallow-mid interpolation");
        near(depth(0,42,0,-44,w),2,"Mid anchor");
        near(depth(-22,42,0,-44,w),1.625,"Mid-deep interpolation");
        near(depth(-44,42,0,-44,w),1.25,"Deep anchor");
        near(depth(-100,42,0,-44,w),1.25,"Deep clamp");
        require(weighted(new double[]{0,0},.5)==-1,"Empty weighted pool");
        require(weighted(new double[]{0,2,0},0)==1,"Zero-weight boundary selected");
        JsonObject q=object(config.settings(),"quality");
        String[] names={"poor","base","good","ideal"};double[] scores={.5,1,1.5,2.5};
        for(int point=0;point<4;point++) {
            double[] wanted=numbers(q,names[point]),actual=p.qualityProbabilities(scores[point]);
            for(int i=0;i<4;i++)near(actual[i],wanted[i],"Quality anchor "+names[point]);
            int[] counts=new int[4];
            for(int i=0;i<100000;i++){int tier=weighted(actual,unit(i*11L+191));require(tier>=0&&tier<4,"Invalid quality roll");counts[tier]++;}
            for(int i=0;i<4;i++)require(Math.abs(counts[i]/100000.0-wanted[i])<.008,"Quality distribution drift "+names[point]);
        }
        for(double suitability=-1;suitability<5;suitability+=.025){
            double[] actual=p.qualityProbabilities(suitability);double sum=0;
            for(double probability:actual){require(probability>=0&&probability<=1,"Quality lerp out of range");sum+=probability;}
            near(sum,1,"Quality normalization");
        }
        System.out.println("Math: depth interpolation and all four quality distributions pass (400,000 deterministic rolls).");
    }

    private static void splitRejects(int target,double[] weights,String label){
        boolean rejected=false;try{split(target,weights,73);}catch(IllegalArgumentException expected){rejected=true;}
        require(rejected,"Unsafe rich pool split accepted: "+label);
    }
    private static void richPoolSplitTests(){
        long before=checks;
        splitRejects(-1,new double[]{1},"negative target");
        splitRejects(1,new double[0],"empty positive pool");
        splitRejects(1,new double[]{0,0,0},"zero positive pool");
        for(double bad:new double[]{-1,Double.NaN,Double.POSITIVE_INFINITY,Double.NEGATIVE_INFINITY}){
            splitRejects(10,new double[]{.7,bad,.05},"bad weight "+bad);
            splitRejects(0,new double[]{bad},"bad weight in zero target "+bad);
        }
        splitRejects(1,new double[]{Double.MAX_VALUE,Double.MAX_VALUE},"overflowing finite weights");
        splitRejects(0,new double[]{Double.MAX_VALUE,Double.MAX_VALUE},"overflow at zero target");
        require(split(0,new double[0],1).length==0,"Empty zero pool changed shape");
        require(Arrays.equals(split(0,new double[]{0,0,0},1),new int[3]),"Zero-weight zero target invented output");
        double[][] fixtures={{.7,.25,.05},{70,25,5},{0,.7,0,.25,.05,0},{0,3,0},{Double.MAX_VALUE},{Double.MIN_VALUE,Double.MIN_VALUE},{1e-250,2e-250,7e-250}};
        for(double[] weights:fixtures)for(int target:new int[]{0,1,2,3,10,19,100,100000,Integer.MAX_VALUE})for(int trial=0;trial<512;trial++){
            double[] original=weights.clone();long random=seed(90210,target,trial,481);
            int[] parts=split(target,weights,random);require(parts.length==weights.length,"Rich split changed entry count");
            require(Arrays.equals(parts,split(target,weights,random)),"Rich split is not reproducible");
            require(Arrays.equals(weights,original),"Rich split mutated caller weights");
            long sum=0;
            for(int i=0;i<parts.length;i++){
                require(parts[i]>=0&&parts[i]<=target,"Rich split allocation out of bounds");
                if(weights[i]==0)require(parts[i]==0,"Zero-weight rich entry received blocks");
                sum+=parts[i];
            }
            require(sum==target,"Rich split did not conserve exact target");
        }
        // Actual production split, not a copied algorithm: exercise tiny per-chunk PGM pools.
        // Iridium is the LAST 5% entry; at target ten its expected allocation is 0.5, not zero.
        double[] pgm={70,25,5};int samples=100000;
        for(int target:new int[]{1,2,3,5,10,19}){
            long[] total=new long[3];int iridiumPresent=0;
            for(int trial=0;trial<samples;trial++){
                long random=seed(402,target,trial,91);int[] parts=split(target,pgm,random);
                require(Arrays.equals(parts,split(target,pgm,random)),"Statistical rich split is not repeatable");
                require((long)parts[0]+parts[1]+parts[2]==target,"Tiny PGM pool lost blocks");
                for(int i=0;i<3;i++){require(parts[i]>=0,"Tiny PGM allocation is negative");total[i]+=parts[i];}
                if(parts[2]>0)iridiumPresent++;
                if(target==10)require(parts[2]==0||parts[2]==1,"Half-block expected Iridium pool should round to zero or one");
            }
            double[] means={total[0]/(double)samples,total[1]/(double)samples,total[2]/(double)samples};
            for(int i=0;i<3;i++)require(Math.abs(means[i]-target*pgm[i]/100)<.006,"Biased 70/25/5 split at target "+target+", entry "+i);
            require(iridiumPresent>0&&iridiumPresent<samples,"Rare last entry lost chance at small target "+target);
            System.out.printf("PGM split: target=%d, %,d seeds; mean [Os,Pt,Ir]=[%.5f,%.5f,%.5f], Iridium present=%,d.%n",target,samples,means[0],means[1],means[2],iridiumPresent);
        }
        System.out.printf("Rich pool split: %,d direct production assertions; conservation, determinism, zero weights, invalid arrays, integer-limit target, and 600,000 tiny-pool samples pass.%n",checks-before);
    }

    private static void biomeVetoes() {
        GeologyPlanner p=planner(new CountingSampler());
        JsonObject d=p.definitions().get(0).deepCopy();
        d.add("biomeWeights",JsonParser.parseString("{\"allowed\":2.5,\"banned\":0}"));
        GeologyPlanner.Site overlap=new GeologyPlanner.Site("test:overlap",Set.of("allowed","banned"),"normal",70);
        near(p.biomeWeight(d,overlap),0,"Explicit zero did not veto positive overlap");
        d.add("hardBiomeExclusions",JsonParser.parseString("[\"allowed\"]"));
        near(p.biomeWeight(d,new GeologyPlanner.Site("test:x",Set.of("allowed"),"normal",70)),0,"Family hard exclusion");
        d.add("hardBiomeExclusions",JsonParser.parseString("[\"test:x\"]"));
        near(p.biomeWeight(d,new GeologyPlanner.Site("test:x",Set.of("allowed"),"normal",70)),0,"ID hard exclusion");
        d.add("hardBiomeExclusions",new JsonArray());d.add("hardTerrainExclusions",JsonParser.parseString("[\"mountain\"]"));
        near(p.biomeWeight(d,new GeologyPlanner.Site("test:x",Set.of("allowed"),"mountain",160)),0,"Terrain hard exclusion");
    }

    private static String signature(GeologyPlanner.Decision d) {
        return d.plan()==null?d.reason():d.plan().id()+":"+d.plan().candidate()+":"+d.plan().quality()+":"+d.plan().normalSize()+":"+d.plan().intendedSize()+":"+d.plan().richFraction();
    }
    private static void spacingAndOrder() throws Exception {
        CountingSampler samples=new CountingSampler();GeologyPlanner p=planner(samples);
        long started=System.nanoTime();
        for(int x=-1;x<=1;x++)for(int z=-1;z<=1;z++)p.decide(x,z);
        System.out.printf("Cold first 3x3 decisions: %d sampler calls, %.2f ms Java-only wall time.%n",samples.calls,(System.nanoTime()-started)/1e6);
        Map<String,String> forward=new HashMap<>();List<int[]> coordinates=new ArrayList<>();List<GeologyPlanner.Plan> accepted=new ArrayList<>();
        started=System.nanoTime();
        for(int x=-16;x<16;x++)for(int z=-16;z<16;z++){
            coordinates.add(new int[]{x,z});GeologyPlanner.Decision d=p.decide(x,z);forward.put(x+":"+z,signature(d));
            if(d.plan()!=null){accepted.add(d.plan());require(d.plan().eligibleFamilies().contains(GeologyPlanner.family(d.plan().definition())),"Selected ineligible family");}
        }
        System.out.printf("32x32 regions: %d accepted deposits; %d total sampler calls; %.2f ms Java-only. Coverage=%.2f km2.%n",accepted.size(),samples.calls,(System.nanoTime()-started)/1e6,1024.0*p.regionSize()*p.regionSize()/1e6);
        require(!accepted.isEmpty(),"No deposits accepted by fixture");
        for(int i=0;i<accepted.size();i++)for(int j=i+1;j<accepted.size();j++){
            var a=accepted.get(i);var b=accepted.get(j);long dx=(long)a.candidate().x()-b.candidate().x(),dz=(long)a.candidate().z()-b.candidate().z();long distance=dx*dx+dz*dz;
            double global=number(config.settings(),"globalMinSpacing",800);require(distance>=global*global,"Global spacing broken");
            if(GeologyPlanner.family(a.definition()).equals(GeologyPlanner.family(b.definition()))){
                double minimum=Math.max(number(a.definition(),"sameFamilyMinSpacing",global),number(b.definition(),"sameFamilyMinSpacing",global));
                require(distance>=minimum*minimum,"Same-family spacing broken: "+a.id()+" / "+b.id());
            }
        }
        GeologyPlanner reverse=planner(new CountingSampler());Collections.reverse(coordinates);
        for(int[] c:coordinates)require(forward.get(c[0]+":"+c[1]).equals(signature(reverse.decide(c[0],c[1]))),"Region traversal order changed a plan");
        Collections.shuffle(coordinates,new Random(88));GeologyPlanner shuffled=planner(new CountingSampler());
        for(int[] c:coordinates)require(forward.get(c[0]+":"+c[1]).equals(signature(shuffled.decide(c[0],c[1]))),"Shuffled traversal changed a plan");
        GeologyPlanner concurrent=planner(new CountingSampler());
        try(ExecutorService workers=Executors.newFixedThreadPool(4)){
            List<Callable<Boolean>> jobs=new ArrayList<>();
            for(int[] c:coordinates)jobs.add(()->forward.get(c[0]+":"+c[1]).equals(signature(concurrent.decide(c[0],c[1]))));
            for(Future<Boolean> result:workers.invokeAll(jobs))require(result.get(),"Concurrent region evaluation changed a plan");
        }
        int warm=samples.calls;for(int[] c:coordinates)p.decide(c[0],c[1]);require(warm==samples.calls,"Warm decisions resampled terrain");
        Map<String,Integer> distribution=new TreeMap<>();for(var plan:accepted)distribution.merge(plan.id(),1,Integer::sum);
        System.out.println("Accepted family distribution: "+distribution);
    }

    private static void shapeTests() {
        long started=System.nanoTime();
        for(boolean seam:new boolean[]{false,true})for(int size:new int[]{1,64,1000,5500,22000}){
            long seed=33+size;List<Voxel> voxels=shape(seed,size,seam);Set<Voxel> unique=new HashSet<>(voxels);
            require(voxels.size()==size&&unique.size()==size,"Shape does not have exact unique intended size");
            require(voxels.equals(shape(seed,size,seam)),"Repeated shape differs");
            Set<Voxel> visited=new HashSet<>();ArrayDeque<Voxel> queue=new ArrayDeque<>();queue.add(voxels.get(0));
            while(!queue.isEmpty()){
                Voxel v=queue.removeFirst();if(!visited.add(v))continue;
                for(Voxel neighbor:List.of(new Voxel(v.x()+1,v.y(),v.z()),new Voxel(v.x()-1,v.y(),v.z()),new Voxel(v.x(),v.y()+1,v.z()),new Voxel(v.x(),v.y()-1,v.z()),new Voxel(v.x(),v.y(),v.z()+1),new Voxel(v.x(),v.y(),v.z()-1)))
                    if(unique.contains(neighbor)&&!visited.contains(neighbor))queue.addLast(neighbor);
            }
            require(visited.size()==size,"Disconnected host shape");
            int[] low={Integer.MAX_VALUE,Integer.MAX_VALUE,Integer.MAX_VALUE},high={Integer.MIN_VALUE,Integer.MIN_VALUE,Integer.MIN_VALUE};
            for(Voxel v:voxels){int[] xyz={v.x(),v.y(),v.z()};for(int a=0;a<3;a++){low[a]=Math.min(low[a],xyz[a]);high[a]=Math.max(high[a],xyz[a]);}}
            if(seam&&size>=1000)require(high[1]-low[1]<Math.min(high[0]-low[0],high[2]-low[2]),"Coal formation is not a flattened seam");
            if(size==22000)System.out.printf("22,000-block %s shape bounds: %dx%dx%d (XYZ).%n",seam?"coal":"host",high[0]-low[0]+1,high[1]-low[1]+1,high[2]-low[2]+1);
        }
        System.out.printf("Exact size/connectedness/repeated geometry tests: %.2f ms.%n",(System.nanoTime()-started)/1e6);
    }

    private static void quotasAndAssociationData() {
        require(quota(0,.5,1,true)==0,"Empty host cannot produce guaranteed ore");
        require(quota(1,.0001,1,true)==1,"Positive guarantee lost");
        require(quota(10,3,1,true)==10,"Quota exceeds available host");
        require(quota(100,0,1,true)==0,"Zero fraction guarantee invented material");
        double fraction=.00875;long sum=0;
        for(int i=0;i<100000;i++){int q=quota(333,fraction,i,false);require(q==2||q==3,"Quota not stochastic floor/ceil");sum+=q;}
        require(Math.abs(sum/100000.0-333*fraction)<.005,"Quota stochastic mean drift");
        for(JsonElement e:array(config.deposits(),"deposits")){
            JsonObject d=e.getAsJsonObject();for(JsonElement a:array(d,"associated")){
                JsonObject rule=a.getAsJsonObject();double[] chance=numbers(rule,"chanceByQuality");require(chance.length==4,"Association lacks quality chance array");
                for(double c:chance)require(c>=0&&c<=1,"Invalid association chance");
                if(string(d,"id","").equals("uranium")){for(double c:chance)near(c,1,"Uranium did not guarantee Thorium association roll");require(bool(rule,"guaranteeWhenPositive",false),"Uranium requires positive association guarantee");}
                if(string(rule,"type","").equals("depth_percentage"))for(JsonElement b:array(rule,"depthBands"))require(integer(b.getAsJsonObject(),"maxY",0)<=-20,"Graphite diamond band above -20");
            }
        }
        // Diagnostic for the current caller: applying a deposit-wide guarantee separately in tiny
        // clipped chunks raises totals. This tests math, not Minecraft placement, and reports the risk.
        int total=0;for(int part=0;part<40;part++)total+=quota(25,.005,part,true);
        System.out.printf("Association diagnostic: 1,000 host blocks split into 40 chunks at 0.5%% gives %d with per-chunk guarantee; deposit-wide percentage target is 5.%n",total);
    }

    private static void uraniumGuaranteeOverhead() {
        for(int size:new int[]{600,900,1200,1500,2000}){
            double fraction=size<=1200?.005:.01;
            double total=0;int max=0,min=Integer.MAX_VALUE,maxChunks=0,tests=0;
            List<Voxel> geometry=shape(7342,size,false);
            for(int ox=0;ox<16;ox++)for(int oz=0;oz<16;oz++){
                Map<String,Integer> chunks=new HashMap<>();
                for(Voxel v:geometry)chunks.merge(Math.floorDiv(v.x()+ox,16)+":"+Math.floorDiv(v.z()+oz,16),1,Integer::sum);
                int count=0,part=0;for(int actual:chunks.values())count+=quota(actual,fraction,ox*301L+oz*17L+part++,true);
                maxChunks=Math.max(maxChunks,chunks.size());min=Math.min(min,count);max=Math.max(max,count);total+=count;tests++;
            }
            System.out.printf("Compact Uranium minimum diagnostic: size=%d fraction=%.3f target=%.1f mean=%.2f range=%d..%d maxChunks=%d across256 offsets.%n",size,fraction,size*fraction,total/tests,min,max,maxChunks);
        }
    }

    private static void broadPhaseTests(){
        long started=System.nanoTime();int shapes=0,chunkChecks=0;int maximumHorizontal=0;
        for(int region:new int[]{128,512}){
            Config tiny=copyConfig();tiny.settings().addProperty("regionSize",region);
            tiny.settings().addProperty("majorAttemptChance",1);
            object(tiny.settings(),"geometry").addProperty("maxIntendedBlocks",100000);
            object(tiny.settings(),"geometry").addProperty("regionSearchRadius",0);
            validate(tiny);
            CountingSampler sampler=new CountingSampler();GeologyPlanner p=new GeologyPlanner(246813579L,tiny,sampler);
            int reach=(int)Math.ceil(6*Math.cbrt(100000));
            int search=Math.max(0,(int)Math.ceil((double)reach/region));
            for(int rx:new int[]{-2,-1,0,1}){
                int rz=-rx-1;var center=p.raw(rx,rz);require(center!=null,"Broad-phase forced candidate fixture failed");
                for(boolean coal:new boolean[]{false,true})for(int size:new int[]{22000,100000}){
                    List<Voxel> voxels=shape(center.seed(),size,coal);shapes++;
                    require(voxels.size()==size,"Maximum-size generated shape is incomplete");
                    Set<Long> chunks=new HashSet<>();
                    for(Voxel v:voxels){
                        maximumHorizontal=Math.max(maximumHorizontal,Math.max(Math.abs(v.x()),Math.abs(v.z())));
                        require(Math.abs(v.x())<=reach&&Math.abs(v.z())<=reach,"Conservative reach is smaller than an actual shape");
                        int cx=Math.floorDiv(center.x()+v.x(),16),cz=Math.floorDiv(center.z()+v.z(),16);
                        chunks.add(((long)cx<<32)^(cz&0xffffffffL));
                    }
                    for(long packed:chunks){
                        int cx=(int)(packed>>32),cz=(int)packed;
                        int viewerRegionX=Math.floorDiv(cx*16+8,region),viewerRegionZ=Math.floorDiv(cz*16+8,region);
                        require(Math.abs(rx-viewerRegionX)<=search&&Math.abs(rz-viewerRegionZ)<=search,"Automatic region search omitted an occupied boundary chunk");
                        int before=sampler.calls;
                        require(p.mayReach(rx,rz,cx*16,cz*16,cx*16+15,cz*16+15,reach),"mayReach falsely rejected a real shape chunk");
                        require(before==sampler.calls,"mayReach sampled terrain");chunkChecks++;
                    }
                    require(!p.mayReach(rx,rz,center.x()+reach+32,center.z()+reach+32,center.x()+reach+47,center.z()+reach+47,reach),"Far chunk was not broad-phase rejected");
                }
            }
        }
        System.out.printf("Broad phase: %d generated shapes (up to100,000; host+coal), %d occupied-chunk checks; max observed horizontal reach=%d <= configured279; %.2f ms.%n",shapes,chunkChecks,maximumHorizontal,(System.nanoTime()-started)/1e6);
        CountingSampler samples=new CountingSampler();GeologyPlanner p=planner(samples);int reach=(int)Math.ceil(6*Math.cbrt(integer(object(config.settings(),"geometry"),"maxIntendedBlocks",50000)));
        int considered=0,admitted=0;started=System.nanoTime();
        for(int cx=-32;cx<32;cx++)for(int cz=-32;cz<32;cz++){
            int rx=Math.floorDiv(cx*16+8,p.regionSize()),rz=Math.floorDiv(cz*16+8,p.regionSize());
            int search=Math.max(integer(object(config.settings(),"geometry"),"regionSearchRadius",1),(int)Math.ceil((double)reach/p.regionSize()));
            for(int x=rx-search;x<=rx+search;x++)for(int z=rz-search;z<=rz+search;z++){
                considered++;if(!p.mayReach(x,z,cx*16,cz*16,cx*16+15,cz*16+15,reach))continue;
                admitted++;p.decide(x,z);
            }
        }
        System.out.printf("64x64 chunk broad-phase model: %,d of%,d region/chunk pairs require decisions; %d terrain sampler calls total; %.2f ms Java-only.%n",admitted,considered,samples.calls,(System.nanoTime()-started)/1e6);
    }

    private static void microProbabilityModel(){
        // Mirrors the source's pure gate+selection arithmetic, not the WorldGenLevel method.
        // Two equally weighted families with occurrence probabilities .003 and .0001.
        int high=0,low=0,sampled=0;int count=1000000;
        for(int i=0;i<count;i++){
            long s=seed(246813579L,i-500000,37,0x4d4943524fL);
            boolean mineral=unit(s+4)<.003,diamond=unit(s+8)<.0002;
            if(mineral||diamond)sampled++;
            if(!mineral)continue;
            int selected=weighted(new double[]{1,1},unit(s+5));
            if(unit(s+4)<(selected==0?.003:.0001)){if(selected==0)high++;else low++;}
        }
        require(Math.abs(high-count*.5*.003)<180,"Micro model high-rate family occurrence drift");
        require(Math.abs(low-count*.5*.0001)<30,"Micro model low-rate family occurrence drift");
        require(sampled>2800&&sampled<3700,"Coarse gate failed expected sampling reduction");
        System.out.printf("Pure micro model: high=%d (~1500 expected), low=%d (~50 expected); %d/1,000,000 chunks reach terrain sampling. Not a runtime block-generation test.%n",high,low,sampled);
    }
}
