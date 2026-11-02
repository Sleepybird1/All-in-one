package dev.godpc.industrialcolonies.geology;

import com.google.gson.JsonObject;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.logging.LogUtils;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import static dev.godpc.industrialcolonies.geology.GeologyConfig.*;

/** OP-only observations and read-only prediction. No debug command places blocks or force-loads chunks. */
public final class GeologyDebug {
    public record Counts(int host,int richTarget,int richPlaced,Map<String,Integer> associated,Map<String,String> rolls,int indicators) {}
    private static final Map<Long,Map<Long,Counts>> OBSERVED=new ConcurrentHashMap<>();
    private static final Set<Long> REJECTIONS=ConcurrentHashMap.newKeySet();
    private GeologyDebug(){}
    public static void clear(){OBSERVED.clear();REJECTIONS.clear();}
    public static void rejected(int rx,int rz,GeologyPlanner.Decision decision){
        if(!bool(get().settings(),"debug",false))return;
        long key=((long)rx<<32)^(rz&0xffffffffL);if(REJECTIONS.size()>8192)REJECTIONS.clear();
        if(REJECTIONS.add(key))LogUtils.getLogger().info("IC geology region {}, {} rejected: {} candidate={}",rx,rz,decision.reason(),decision.candidate());
    }
    public static void record(ServerLevel level,ChunkPos chunk,GeologyPlanner.Plan plan,int actual,int target,int rich,
                              Map<String,Integer> associated,Map<String,String> rolls,int indicators){
        if(OBSERVED.size()>2048)OBSERVED.clear();
        OBSERVED.computeIfAbsent(plan.candidate().seed(),k->new ConcurrentHashMap<>()).put(chunk.toLong(),
                new Counts(actual,target,rich,Map.copyOf(associated),Map.copyOf(rolls),indicators));
        if(bool(get().settings(),"debug",false))LogUtils.getLogger().info("IC geology {} quality={} center={}, {}, {} intended={} chunk={} actualHost={} richTarget={} richPlaced={} associated={} rolls={} indicators={}",
                plan.id(),plan.quality(),plan.candidate().x(),plan.candidate().y(),plan.candidate().z(),plan.intendedSize(),chunk,actual,target,rich,associated,rolls,indicators);
    }
    private static String describe(GeologyPlanner.Plan plan){
        var c=plan.candidate();String[] names={"Poor","Normal","Rich","Exceptional"};
        Map<Long,Counts> chunks=OBSERVED.getOrDefault(c.seed(),Map.of());
        int actual=chunks.values().stream().mapToInt(Counts::host).sum(),rich=chunks.values().stream().mapToInt(Counts::richPlaced).sum();
        Map<String,Integer> associated=new TreeMap<>();chunks.values().forEach(v->v.associated.forEach((k,n)->associated.merge(k,n,Integer::sum)));
        return plan.id()+" / "+names[plan.quality()]+" @ "+c.x()+", "+c.y()+", "+c.z()+"; biome="+c.site().biome()+" "+c.site().families()+
                "; terrain="+c.site().terrain()+"; suitability="+String.format(Locale.ROOT,"%.3f",plan.suitability())+
                "; base="+plan.normalSize()+" intended="+plan.intendedSize()+" richFraction="+plan.richFraction()+
                "; observed this session: "+chunks.size()+" chunks, host="+actual+", rich="+rich+", associated="+associated;
    }
    public static void registerCommands(RegisterCommandsEvent event){
        event.getDispatcher().register(Commands.literal("icgeology").requires(s->s.hasPermission(4))
                .then(Commands.literal("config").executes(c->{c.getSource().sendSuccess(()->Component.literal("Worldgen config: "+directory()+". Restart after edits; only newly generated chunks change. 1000 mB/ingot; 9000 mB/storage block. No processing recipes added."),false);return 1;}))
                .then(Commands.literal("report").executes(c->{
                    var source=c.getSource();if(source.getLevel().dimension()!=Level.OVERWORLD){source.sendFailure(Component.literal("Overworld only."));return 0;}
                    var world=GeologyWorld.of(source.getLevel());int region=world.planner.regionSize();
                    int x=Math.floorDiv((int)Math.floor(source.getPosition().x),region),z=Math.floorDiv((int)Math.floor(source.getPosition().z),region);
                    source.sendSuccess(()->Component.literal("Inspecting regional candidate without loading chunks…"),false);
                    CompletableFuture.supplyAsync(()->world.planner.decide(x,z)).whenComplete((decision,error)->source.getServer().execute(()->{
                        if(error!=null)source.sendFailure(Component.literal("Geology report failed: "+error.getMessage()));
                        else source.sendSuccess(()->Component.literal(decision.plan()==null?"Region "+x+","+z+" rejected: "+decision.reason():describe(decision.plan())),false);
                    }));return 1;
                }))
                .then(Commands.literal("locate").then(Commands.argument("family",StringArgumentType.word())
                        .suggests((context,builder)->{builder.suggest("any");for(var d:GeologyWorld.of(context.getSource().getLevel()).planner.definitions())builder.suggest(d.get("id").getAsString());return builder.buildFuture();})
                        .then(Commands.argument("regions",IntegerArgumentType.integer(1,8)).executes(c->{
                            var source=c.getSource();if(source.getLevel().dimension()!=Level.OVERWORLD){source.sendFailure(Component.literal("Overworld only."));return 0;}
                            if(NativeContinentLevels.find(source.getLevel()).isPresent()){
                                source.sendFailure(Component.literal("This world uses continent veins; use /icveins locate <family> [radiusBlocks]. The regional predictor does not locate the new catalog."));return 0;
                            }
                            String family=StringArgumentType.getString(c,"family");int radius=IntegerArgumentType.getInteger(c,"regions");
                            var world=GeologyWorld.of(source.getLevel());var origin=source.getPosition();int size=world.planner.regionSize();
                            int rx=Math.floorDiv((int)Math.floor(origin.x),size),rz=Math.floorDiv((int)Math.floor(origin.z),size);
                            source.sendSuccess(()->Component.literal("Predicting deposits asynchronously; no chunks are being loaded. This is not proof of terrain-clipped block counts."),false);
                            CompletableFuture.supplyAsync(()->{
                                GeologyPlanner.Plan nearest=null;double distance=Double.MAX_VALUE;
                                for(int x=rx-radius;x<=rx+radius;x++)for(int z=rz-radius;z<=rz+radius;z++){
                                    var plan=world.planner.decide(x,z).plan();if(plan==null||!(family.equals("any")||plan.id().equals(family)))continue;
                                    double dx=plan.candidate().x()-origin.x,dz=plan.candidate().z()-origin.z,d=dx*dx+dz*dz;
                                    if(d<distance){distance=d;nearest=plan;}
                                }
                                return nearest;
                            }).whenComplete((plan,error)->source.getServer().execute(()->{
                                if(error!=null)source.sendFailure(Component.literal("Geology locate failed: "+error.getMessage()));
                                else source.sendSuccess(()->Component.literal(plan==null?"No matching accepted deposit in this search area.":describe(plan)),false);
                            }));return 1;
                        }))))
                .then(Commands.literal("simulate").then(Commands.argument("family",StringArgumentType.word()).executes(c->{
                    String id=StringArgumentType.getString(c,"family");var source=c.getSource();
                    for(var element:array(get().deposits(),"deposits")){JsonObject d=element.getAsJsonObject();if(!d.get("id").getAsString().equals(id))continue;
                        for(int q=0;q<4;q++){
                            int tier=q;double size=numbers(object(get().settings(),"quality"),"sizeMultipliers")[q];
                            double fraction=number(d,"normalRichOrePercent",0)*numbers(object(get().settings(),"quality"),"richMultipliers")[q];
                            source.sendSuccess(()->Component.literal(id+" tier="+tier+" intended range="+(int)(integer(d,"normalSizeMin",0)*size)+".."+(int)(integer(d,"normalSizeMax",0)*size)+"; rich target=actual host × "+fraction+"; association rules="+array(d,"associated")),false);
                        }return 1;
                    }source.sendFailure(Component.literal("Unknown deposit ID: "+id));return 0;
                }))));
    }
}
