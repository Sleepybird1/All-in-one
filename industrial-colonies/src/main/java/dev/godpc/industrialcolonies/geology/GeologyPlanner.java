package dev.godpc.industrialcolonies.geology;

import com.google.gson.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import static dev.godpc.industrialcolonies.geology.GeologyConfig.*;
import static dev.godpc.industrialcolonies.geology.GeologyMath.*;

/** Order-independent regional reservations. Never consults saved chunks to decide spacing. */
public final class GeologyPlanner {
    public record Site(String biome,Set<String> families,String terrain,int surfaceY) {}
    public interface Sampler {
        Site sample(int x,int z);
        default int caveY(int x,int z,int preferred,int min,int max){return preferred;}
        default int fitY(Plan plan){throw new IllegalStateException("Whole-formation fitting requires a terrain sampler");}
    }
    public record Candidate(int regionX,int regionZ,int x,int y,int z,long seed,Site site) {}
    public record Plan(Candidate candidate,JsonObject definition,int quality,int normalSize,int intendedSize,
                       double suitability,double richFraction,List<String> eligibleFamilies) {
        public String id(){return definition.get("id").getAsString();}
    }
    public record Decision(Candidate candidate,Plan plan,String reason) {}
    private final long worldSeed;
    private final Config config;
    private final Sampler sampler;
    private final List<JsonObject> definitions;
    private final int regionSize,globalSpacing,maxSpacing;
    private final Map<String,Double> spacing=new HashMap<>();
    private final ConcurrentHashMap<Long,Optional<Candidate>> rawCache=new ConcurrentHashMap<>();
    private final ConcurrentHashMap<Long,Boolean> globalCache=new ConcurrentHashMap<>();
    private final ConcurrentHashMap<Long,Decision> decisions=new ConcurrentHashMap<>();
    public GeologyPlanner(long seed,Config config,Sampler sampler){
        this.worldSeed=seed;this.config=config;this.sampler=sampler;
        this.regionSize=integer(config.settings(),"regionSize",512);
        this.globalSpacing=integer(config.settings(),"globalMinSpacing",800);
        definitions=new ArrayList<>();
        for(JsonElement d:array(config.deposits(),"deposits")){
            JsonObject def=d.getAsJsonObject();definitions.add(def);
            spacing.merge(family(def),number(def,"sameFamilyMinSpacing",globalSpacing),Math::max);
        }
        maxSpacing=(int)Math.ceil(spacing.values().stream().mapToDouble(Double::doubleValue).max().orElse(globalSpacing));
    }
    public int regionSize(){return regionSize;}
    /** Cheap broad phase before any terrain/noise query. Conservative bound includes the longest coal seams. */
    public boolean mayReach(int rx,int rz,int minX,int minZ,int maxX,int maxZ,int reach){
        long seed=seed(worldSeed,rx,rz,0x494347454f4c4f47L);
        long x=(long)rx*regionSize+bounded(seed+1,regionSize),z=(long)rz*regionSize+bounded(seed+2,regionSize);
        return x>=Integer.MIN_VALUE&&x<=Integer.MAX_VALUE&&z>=Integer.MIN_VALUE&&z<=Integer.MAX_VALUE
                &&x>=(long)minX-reach&&x<=(long)maxX+reach&&z>=(long)minZ-reach&&z<=(long)maxZ+reach;
    }
    public List<JsonObject> definitions(){return List.copyOf(definitions);}
    public static String family(JsonObject d){return string(d,"spacingFamily",string(d,"id",""));}
    private static long key(int x,int z){return ((long)x<<32)^(z&0xffffffffL);}
    public Candidate raw(int rx,int rz){
        long key=key(rx,rz);Optional<Candidate> found=rawCache.get(key);if(found!=null)return found.orElse(null);
        long seed=seed(worldSeed,rx,rz,0x494347454f4c4f47L);
        int x=rx*regionSize+bounded(seed+1,regionSize),z=rz*regionSize+bounded(seed+2,regionSize);
        double chance=number(config.settings(),"majorAttemptChance",.65);
        double maximum=1;
        for(JsonElement t:object(config.settings(),"terrain").asMap().values())
            if(t.isJsonObject())maximum=Math.max(maximum,number(t.getAsJsonObject(),"majorWeight",1));
        Candidate result=null;
        if(unit(seed+3)<Math.min(1,chance*maximum)){
            Site site=sampler.sample(x,z);
            JsonObject terrain=object(object(config.settings(),"terrain"),site.terrain());
            if(unit(seed+3)<Math.min(1,chance*number(terrain,"majorWeight",1))&&
                    !contains(array(config.settings(),"hardTerrainExclusions"),site.terrain())){
                JsonObject depth=object(config.settings(),"depth");int min=integer(depth,"minY",-60);
                int max=Math.min(integer(depth,"maxY",64),site.surfaceY()-8);
                if(max>=min){
                    int y=min+bounded(seed+4,max-min+1);
                    double exposure=number(terrain,"caveExposure",1);
                    if(exposure>1&&unit(seed+5)<1-1/exposure)y=sampler.caveY(x,z,y,min,max);
                    result=new Candidate(rx,rz,x,y,z,seed,site);
                }
            }
        }
        trim(rawCache,32768);rawCache.putIfAbsent(key,Optional.ofNullable(result));return result;
    }
    public boolean globallyAdmitted(Candidate a){
        long key=key(a.regionX,a.regionZ);Boolean known=globalCache.get(key);if(known!=null)return known;
        int radius=(int)Math.ceil((double)globalSpacing/regionSize)+1;boolean admitted=true;
        outer:for(int rx=a.regionX-radius;rx<=a.regionX+radius;rx++)for(int rz=a.regionZ-radius;rz<=a.regionZ+radius;rz++){
            if(rx==a.regionX&&rz==a.regionZ)continue;
            long otherSeed=seed(worldSeed,rx,rz,0x494347454f4c4f47L);
            if(Long.compareUnsigned(mix(otherSeed+11),mix(a.seed+11))>=0)continue;
            Candidate b=raw(rx,rz);if(b!=null&&distance2(a,b)<(long)globalSpacing*globalSpacing){admitted=false;break outer;}
        }
        trim(globalCache,32768);globalCache.putIfAbsent(key,admitted);return admitted;
    }
    public double biomeWeight(JsonObject d,Site site){
        if(contains(array(d,"hardBiomeExclusions"),site.biome)||contains(array(d,"hardTerrainExclusions"),site.terrain))return 0;
        JsonObject weights=object(d,"biomeWeights");double sum=0;int count=0;
        for(String group:site.families){
            if(contains(array(d,"hardBiomeExclusions"),group))return 0;
            if(weights.has(group)){double weight=weights.get(group).getAsDouble();if(weight==0)return 0;sum+=weight;count++;}
        }
        return count==0?1:sum/count; // documented arithmetic blend; any explicit zero remains a veto
    }
    public double depthWeight(JsonObject d,int y){
        JsonObject p=object(config.settings(),"depth");
        return depth(y,number(p,"shallowY",42),number(p,"midY",0),number(p,"deepY",-44),numbers(d,"depthWeights"));
    }
    public static boolean placementAllows(JsonObject d,Site site,int y){
        if(!GeologyPlacement.habitatAllows(d,site))return false;
        int[] surface=GeologyPlacement.restrictSurfaceDepth(d,site,y,y);
        if(surface[0]>surface[1])return false;
        JsonObject rules=object(d,"placement");
        if(rules.has("absoluteY")){
            double[] band=GeologyPlacement.absoluteY(d,site);
            if((y<band[0]||y>band[1])&&!GraphitePlacement.diamondDepth(d,y))return false;
        }
        if(y<integer(rules,"minY",Integer.MIN_VALUE))return false;
        JsonArray biomes=array(rules,"requiredSurfaceBiomes");
        return biomes.isEmpty()||contains(biomes,site.biome());
    }
    public double weight(JsonObject d,Site site,int y){return placementAllows(d,site,y)?number(d,"baseWeight",1)*biomeWeight(d,site)*depthWeight(d,y):0;}
    /** Small clusters use the same absolute band, with their existing six-block surface cover. */
    public static int microY(JsonObject d,Site site,int legacyY,long seed){
        if(!GeologyPlacement.habitatAllows(d,site))return Integer.MIN_VALUE;
        JsonObject rules=object(d,"placement");
        if(!rules.has("absoluteY"))return legacyY;
        double[] band=GeologyPlacement.absoluteY(d,site);
        int low=(int)band[0],high=Math.min((int)band[1],site.surfaceY()-GeologyPlacement.centerCover(d,site,6));
        int[] surface=GeologyPlacement.restrictSurfaceDepth(d,site,low,high);low=surface[0];high=surface[1];
        return high<low?Integer.MIN_VALUE:low+bounded(seed+3,high-low+1);
    }
    /** A family-specific elevation does not move other mineral candidates or add another placement roll. */
    public int plannedY(JsonObject d,Candidate a){
        if(!GeologyPlacement.habitatAllows(d,a.site))return Integer.MIN_VALUE;
        JsonObject rules=object(d,"placement");
        if(GraphitePlacement.diamondDepth(d,a.y))return a.y;
        if(rules.has("absoluteY")){
            double[] band=GeologyPlacement.absoluteY(d,a.site);int low=(int)band[0],high=Math.min((int)band[1],a.site.surfaceY()-GeologyPlacement.centerCover(d,a.site,8));
            int[] surface=GeologyPlacement.restrictSurfaceDepth(d,a.site,low,high);low=surface[0];high=surface[1];
            return high<low?Integer.MIN_VALUE:low+bounded(a.seed+104,high-low+1);
        }
        if(!rules.has("surfaceDepthMin"))return a.y;
        int low=Math.max(integer(rules,"minY",Integer.MIN_VALUE),a.site.surfaceY()-integer(rules,"surfaceDepthMax",40));
        int high=a.site.surfaceY()-integer(rules,"surfaceDepthMin",8);
        return high<low?Integer.MIN_VALUE:low+bounded(a.seed+104,high-low+1);
    }
    private double plannedWeight(JsonObject d,Candidate a){int y=plannedY(d,a);return y==Integer.MIN_VALUE?0:weight(d,a.site,y);}
    public Decision decide(int rx,int rz){
        long key=key(rx,rz);Decision found=decisions.get(key);if(found!=null)return found;
        Candidate a=raw(rx,rz);Decision result;
        if(a==null)result=new Decision(null,null,"base probability / hard terrain / no usable depth");
        else if(!globallyAdmitted(a))result=new Decision(a,null,"global spacing reservation");
        else{
            // Each spacing family has its own seeded reservation priority. Compute eligibility BEFORE selecting a rock.
            Set<String> eligible=new LinkedHashSet<>();
            for(JsonObject d:definitions)if(plannedWeight(d,a)>0)eligible.add(family(d));
            int radius=(int)Math.ceil((double)maxSpacing/regionSize)+1;
            for(int nx=rx-radius;nx<=rx+radius&&!eligible.isEmpty();nx++)for(int nz=rz-radius;nz<=rz+radius&&!eligible.isEmpty();nz++){
                if(nx==rx&&nz==rz)continue;Candidate b=raw(nx,nz);if(b==null)continue;
                long dist=distance2(a,b);if(dist>=(long)maxSpacing*maxSpacing)continue;
                if(!globallyAdmitted(b))continue;
                for(Iterator<String> it=eligible.iterator();it.hasNext();){String family=it.next();double minimum=spacing.get(family);
                    if(dist>=minimum*minimum||Long.compareUnsigned(mix(b.seed^family.hashCode()),mix(a.seed^family.hashCode()))>=0)continue;
                    boolean competing=definitions.stream().anyMatch(d->family(d).equals(family)&&plannedWeight(d,b)>0);
                    if(competing)it.remove();
                }
            }
            double[] pool=new double[definitions.size()];
            for(int i=0;i<pool.length;i++){JsonObject d=definitions.get(i);if(eligible.contains(family(d)))pool[i]=plannedWeight(d,a);}
            int selected=weighted(pool,unit(a.seed+21));
            if(selected<0)result=new Decision(a,null,"no eligible family after biome/depth/same-family spacing");
            else{
                JsonObject def=definitions.get(selected);
                a=new Candidate(a.regionX,a.regionZ,a.x,plannedY(def,a),a.z,a.seed,a.site);
                double suitability=(biomeWeight(def,a.site)+depthWeight(def,a.y))/2;
                int quality=weighted(qualityProbabilities(suitability),unit(a.seed+22));
                int lo=integer(def,"normalSizeMin",1),hi=integer(def,"normalSizeMax",lo);
                int normal=lo+bounded(a.seed+23,hi-lo+1);
                JsonObject q=object(config.settings(),"quality");
                int intended=Math.max(1,(int)Math.round(normal*numbers(q,"sizeMultipliers")[quality]));
                // Coal is outside the optional catalog. Apply its chart tiers explicitly;
                // poor/rich quality must not shrink/enlarge the agreed ore-block reserve.
                if(def.get("id").getAsString().equals("coal")&&bool(object(config.settings(),"worldStartResources"),"enabled",false))
                    normal=intended=ChartDepositSizes.coal(a.seed+23);
                double rich=Math.min(1,number(def,"normalRichOrePercent",0)*numbers(q,"richMultipliers")[quality]);
                Plan plan=new Plan(a,def,quality,normal,intended,suitability,rich,List.copyOf(eligible));
                if(bool(object(config.settings(),"geometry"),"fitWholeFormations",false)){
                    int fitted=sampler.fitY(plan);
                    if(fitted==Integer.MIN_VALUE)plan=null;
                    else {a=new Candidate(a.regionX,a.regionZ,a.x,fitted,a.z,a.seed,a.site);plan=new Plan(a,def,quality,normal,intended,suitability,rich,List.copyOf(eligible));}
                }
                result=new Decision(a,plan,plan==null?"whole formation does not fit terrain":"accepted");
            }
        }
        trim(decisions,8192);decisions.putIfAbsent(key,result);return result;
    }
    public double[] qualityProbabilities(double suitability){
        JsonObject q=object(config.settings(),"quality");String low,high;double t;
        if(suitability<1){low="poor";high="base";t=(suitability-.5)/.5;}
        else if(suitability<1.5){low="base";high="good";t=(suitability-1)/.5;}
        else{low="good";high="ideal";t=(suitability-1.5);}
        double[] a=numbers(q,low),b=numbers(q,high);for(int i=0;i<4;i++)a[i]=lerp(a[i],b[i],t);return a;
    }
    private static long distance2(Candidate a,Candidate b){long x=(long)a.x-b.x,z=(long)a.z-b.z;return x*x+z*z;}
    private static void trim(Map<?,?> map,int maximum){if(map.size()>maximum)map.clear();}
}
