package dev.godpc.industrialcolonies.geology;

import com.google.gson.*;
import net.neoforged.fml.loading.FMLPaths;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** Restart-scoped configuration. Invalid overrides fail loudly rather than silently restoring scattered ores. */
public final class GeologyConfig {
    public record Config(JsonObject settings, JsonObject biomes, JsonObject deposits) {}
    private static volatile Config current;
    private GeologyConfig() {}
    public static Config get() {
        Config c = current;
        if (c == null) synchronized (GeologyConfig.class) {
            if (current == null) {
                c = new Config(externalOrBundled("settings.json"), externalOrBundled("biome_families.json"),
                        externalOrBundled("deposit_families.json"));
                validate(c);
                current = c;
            }
            c = current;
        }
        return c;
    }
    public static Path directory() { return FMLPaths.CONFIGDIR.get().resolve("industrial_colonies/worldgen"); }
    public static JsonObject externalOrBundled(String file) {
        if (!file.matches("[a-z_]+\\.json")) throw new IllegalArgumentException("Invalid geology config name: " + file);
        Path path = directory().resolve(file);
        try {
            if (!Files.exists(path)) {
                Files.createDirectories(path.getParent());
                try (InputStream in = GeologyConfig.class.getResourceAsStream("/data/industrial_colonies/geology/" + file)) {
                    if (in == null) throw new IOException("Missing bundled geology config: " + file);
                    try { Files.copy(in, path); } catch (FileAlreadyExistsException ignored) { /* concurrent first load */ }
                }
            }
            try (Reader reader = Files.newBufferedReader(path, StandardCharsets.UTF_8)) {
                return JsonParser.parseReader(reader).getAsJsonObject();
            }
        } catch (IOException | RuntimeException e) { throw new IllegalStateException("Cannot load geology configuration " + path, e); }
    }
    public static Set<String> families(String biomeId) {
        Set<String> result = new LinkedHashSet<>();
        get().biomes.entrySet().forEach(e -> {
            if (e.getValue().isJsonArray()) for (JsonElement id : e.getValue().getAsJsonArray())
                if (id.isJsonPrimitive() && id.getAsString().equals(biomeId)) result.add(e.getKey());
        });
        return Set.copyOf(result);
    }
    public static boolean enabled() { return bool(get().settings, "enabled", true); }
    public static boolean suppressDefaultOres() { return enabled() && bool(get().settings, "suppressDefaultOres", true); }
    public static double number(JsonObject o, String key, double fallback) {
        return o.has(key) ? o.get(key).getAsDouble() : fallback;
    }
    public static int integer(JsonObject o, String key, int fallback) { return (int) number(o, key, fallback); }
    public static boolean bool(JsonObject o, String key, boolean fallback) { return o.has(key) ? o.get(key).getAsBoolean() : fallback; }
    public static String string(JsonObject o, String key, String fallback) { return o.has(key) ? o.get(key).getAsString() : fallback; }
    public static JsonObject object(JsonObject o, String key) { return o.has(key) ? o.getAsJsonObject(key) : new JsonObject(); }
    public static JsonArray array(JsonObject o, String key) { return o.has(key) ? o.getAsJsonArray(key) : new JsonArray(); }
    public static double[] numbers(JsonObject o, String key) {
        JsonArray a = array(o, key); double[] result = new double[a.size()];
        for (int i=0; i<result.length; i++) result[i]=a.get(i).getAsDouble();
        return result;
    }
    public static boolean contains(JsonArray a, String value) {
        for (JsonElement v : a) if (v.getAsString().equals(value)) return true;
        return false;
    }
    public static void validate(Config c) {
        int region=integer(c.settings,"regionSize",0);
        require(region>=128&&region<=65536,"regionSize safety range is 128..65536");
        double global=number(c.settings,"globalMinSpacing",0);
        require(Double.isFinite(global)&&global>=32&&global/region<=16,"globalMinSpacing must be >=32 and span at most 16 regional cells");
        probability(number(c.settings,"majorAttemptChance",0),"majorAttemptChance");
        JsonObject quality = object(c.settings,"quality");
        JsonObject geometry=object(c.settings,"geometry");
        int maxIntended=integer(geometry,"maxIntendedBlocks",50000);
        require(maxIntended>0&&maxIntended<=FiniteOreLimits.MAX_BLOCKS,"maxIntendedBlocks safety range is 1..300000");
        require(integer(geometry,"regionSearchRadius",1)>=0&&integer(geometry,"regionSearchRadius",1)<=8,"regionSearchRadius safety range is 0..8 (automatic geometric minimum still applies)");
        require(integer(geometry,"caveSearchRange",24)>=0&&integer(geometry,"caveSearchRange",24)<=128,"caveSearchRange safety range is 0..128");
        require(integer(geometry,"richClusterMin",3)>0&&integer(geometry,"richClusterMax",8)>=integer(geometry,"richClusterMin",3),"Invalid rich cluster size range");
        JsonObject depth=object(c.settings,"depth");
        for(String anchor:List.of("shallowY","midY","deepY","minY","maxY"))require(Double.isFinite(number(depth,anchor,0)),"Nonfinite depth anchor: "+anchor);
        require(integer(depth,"minY",-60)<=integer(depth,"maxY",64),"Invalid depth bounds");
        require(number(depth,"shallowY",42)>number(depth,"midY",0)&&number(depth,"midY",0)>number(depth,"deepY",-44),"Depth anchors must be descending");
        for(JsonElement terrain:object(c.settings,"terrain").asMap().values())if(terrain.isJsonObject()){
            for(String property:List.of("majorWeight","caveExposure","indicatorExposure")){
                double value=number(terrain.getAsJsonObject(),property,1);require(Double.isFinite(value)&&value>=0,"Invalid terrain multiplier: "+property);
            }
        }
        for (String name : List.of("base","poor","good","ideal")) {
            double[] values = numbers(quality,name); require(values.length==4,"Four quality probabilities required: "+name);
            double sum=0; for(double v:values){probability(v,name);sum+=v;}
            require(Math.abs(sum-1)<.00001,"Quality probabilities must sum to 1: "+name);
        }
        for(String name:List.of("sizeMultipliers","richMultipliers")) {
            double[] values=numbers(quality,name);require(values.length==4,"Four multipliers required: "+name);
            for(double v:values) require(Double.isFinite(v)&&v>=0,"Invalid multiplier "+name);
        }
        Set<String> ids=new HashSet<>();
        double maximumSize=Arrays.stream(numbers(quality,"sizeMultipliers")).max().orElse(0);
        for(JsonElement element:array(c.deposits,"deposits")) {
            JsonObject d=element.getAsJsonObject();String id=d.get("id").getAsString();
            require(ids.add(id),"Duplicate deposit: "+id);
            int lo=integer(d,"normalSizeMin",0),hi=integer(d,"normalSizeMax",0);
            require(lo>0&&hi>=lo&&hi<=FiniteOreLimits.MAX_BLOCKS,"Invalid size range for "+id);
            boolean fixedVeridium=id.equals(WorldStartVeridiumPolicy.FAMILY)&&WorldStartVeridiumPolicy.enabled(c);
            if(fixedVeridium)WorldStartVeridiumPolicy.validate(c);
            require(hi*(fixedVeridium?1:maximumSize)<=maxIntended,"Quality-adjusted size exceeds maxIntendedBlocks: "+id);
            require(numbers(d,"depthWeights").length==3,"Three depth weights required: "+id);
            for(double value:numbers(d,"depthWeights"))require(Double.isFinite(value)&&value>=0,"Invalid depth weight: "+id);
            probability(number(d,"normalRichOrePercent",0),id+" rich fraction");
            double same=number(d,"sameFamilyMinSpacing",0);
            require(Double.isFinite(same)&&same>=global&&same/region<=32,"Same-family spacing must be >=global and span at most 32 cells: "+id);
            require(Double.isFinite(number(d,"baseWeight",0))&&number(d,"baseWeight",0)>=0,"Invalid selection weight: "+id);
            if(d.has("placement")){
                JsonObject placement=object(d,"placement");
                if(placement.has("absoluteY")){
                    double[] band=numbers(placement,"absoluteY");
                    require(band.length==2,"Absolute Y requires two endpoints: "+id);
                    for(double y:band)require(Double.isFinite(y)&&y==Math.rint(y)&&y>=-2048&&y<2032,"Invalid absolute Y: "+id);
                    require(band[0]<=band[1],"Inverted absolute Y band: "+id);
                    require(!placement.has("minY")&&!placement.has("surfaceDepthMin")&&!placement.has("surfaceDepthMax"),"Do not mix absolute Y and surface-depth rules: "+id);
                }else{
                    double min=number(placement,"minY",-2048),near=number(placement,"surfaceDepthMin",8),far=number(placement,"surfaceDepthMax",40);
                    require(Double.isFinite(min)&&min==Math.rint(min)&&min>=-2048&&min<2032,"Invalid placement minimum: "+id);
                    require(Double.isFinite(near)&&Double.isFinite(far)&&near==Math.rint(near)&&far==Math.rint(far)&&near>=3&&near<=far&&far<=256,"Invalid surface depth band: "+id);
                    require(!array(placement,"requiredSurfaceBiomes").isEmpty(),"Restricted placement needs explicit surface biomes: "+id);
                }
                for(JsonElement biome:array(placement,"requiredSurfaceBiomes"))require(biome.isJsonPrimitive()&&biome.getAsString().matches("[a-z0-9_.-]+:[a-z0-9_./-]+"),"Invalid placement biome: "+id);
            }
            for(JsonElement w:object(d,"biomeWeights").asMap().values()) require(w.getAsDouble()>=0&&Double.isFinite(w.getAsDouble()),"Invalid biome weight: "+id);
            if(array(d,"richOres").isEmpty()) require(number(d,"normalRichOrePercent",0)==0,"Rich percentage requires an approved rich block: "+id);
            double richWeights=0;
            for(JsonElement e:array(d,"richOres")){double w=number(e.getAsJsonObject(),"weight",1);require(Double.isFinite(w)&&w>=0,"Invalid rich pool weight: "+id);richWeights+=w;}
            require(Double.isFinite(richWeights)&&(array(d,"richOres").isEmpty()||richWeights>0),"Rich ore pool requires a finite positive total weight: "+id);
            for(JsonElement e:array(d,"associated")){
                JsonObject a=e.getAsJsonObject();double[] chances=numbers(a,"chanceByQuality");require(chances.length==4,"Four associated chances required: "+id);
                for(double chance:chances)probability(chance,id+" association chance");
                String type=string(a,"type","");require(type.equals("percentage")||type.equals("depth_percentage"),"Unknown associated rule: "+id);
                if(type.equals("percentage")){
                    JsonArray rates=array(a,"byQuality");require(rates.size()==4,"Four associated ranges required: "+id);
                    for(JsonElement range:rates){JsonArray pair=range.getAsJsonArray();require(pair.size()==2,"Associated fraction needs min/max: "+id);
                        double min=pair.get(0).getAsDouble(),max=pair.get(1).getAsDouble();probability(min,id);probability(max,id);require(min<=max,"Inverted associated range: "+id);}
                }else for(JsonElement b:array(a,"depthBands")){
                    JsonObject band=b.getAsJsonObject();double[] rates=numbers(band,"byQuality");require(rates.length==4,"Four depth-associated rates required: "+id);
                    for(double rate:rates)probability(rate,id);require(integer(band,"minY",0)<=integer(band,"maxY",0),"Inverted associated depth band: "+id);
                }
                validateCluster(a,id+" association");
            }
            JsonObject micro=object(d,"micro");probability(number(micro,"chance",0),id+" micro");validateCluster(micro,id+" micro");
            GraphitePlacement.validate(d);
            GeologyPlacement.validate(d,c.biomes());
        }
        require(!ids.isEmpty(),"No deposit families configured");
        if(MassiveDeposits.enabled(c))MassiveDeposits.settings(c);
        if(bool(geometry,"fitWholeFormations",false)){
            require(!MassiveDeposits.enabled(c),"Whole finite-formation fitting is not qualified for massive geometry");
            require(maxIntended<=FiniteOreLimits.MAX_BLOCKS,"Finite formation fitting supports up to300000positions");
            double clearance=number(geometry,"formationBedrockClearance",Double.NaN);
            require(Double.isFinite(clearance)&&clearance==Math.rint(clearance)&&clearance>=1&&clearance<=64,"Explicit bedrock clearance1..64 required for formation fitting");
        }
        JsonObject economy=object(c.settings,"economy");
        require(number(economy,"ingotMb",1000)==1000&&number(economy,"storageBlockMb",9000)==9000,"Universal metal volume must remain 1000 mB/ingot and 9000 mB/storage block");
        for(String key:List.of("trace","placer")){JsonObject rules=object(c.settings,key);probability(number(rules,"chancePerAttempt",0),key);
            require(integer(rules,"attemptsPerChunk",0)>=0&&integer(rules,"attemptsPerChunk",0)<=128,"Attempt count must be 0..128: "+key);}
        JsonObject trace=object(c.settings,"trace");
        require(integer(trace,"maxSurfaceDepth",3)>=0&&integer(trace,"maxSurfaceDepth",3)<=128,"trace.maxSurfaceDepth safety range is 0..128");
        for(JsonElement resource:array(trace,"resources")){JsonObject entry=resource.getAsJsonObject();double w=number(entry,"weight",1);
            require(Double.isFinite(w)&&w>=0,"Invalid trace resource weight");validateCluster(entry,"trace resource");}
        int bank=integer(object(c.settings,"placer"),"maxRiverbankDistance",8);require(bank>=0&&bank<=128,"maxRiverbankDistance safety range is 0..128");
        JsonObject micro=object(c.settings,"micro");probability(number(micro,"maxChancePerChunk",1),"micro cap");
        require(Double.isFinite(number(micro,"frequencyMultiplier",1))&&number(micro,"frequencyMultiplier",1)>=0,"Invalid micro frequency multiplier");
        require(integer(micro,"maxBlocks",3)>0&&integer(micro,"maxBlocks",3)<=64,"micro.maxBlocks safety range is 1..64");
    }
    private static void validateCluster(JsonObject o,String id){int min=integer(o,"clusterMin",integer(o,"min",1)),max=integer(o,"clusterMax",integer(o,"max",2));
        require(min>0&&max>=min&&max<=64,"Invalid cluster size: "+id);probability(number(o,"jackpotChance",0),id+" jackpot");
        require(integer(o,"jackpotMax",3)>0&&integer(o,"jackpotMax",3)<=64,"Invalid jackpot size: "+id);}
    private static void probability(double n,String label){require(Double.isFinite(n)&&n>=0&&n<=1,"Invalid probability: "+label);}
    private static void require(boolean ok,String message){if(!ok)throw new IllegalArgumentException(message);}
}
