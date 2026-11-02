package dev.godpc.industrialcolonies.space.collision;

import com.google.gson.*;
import dev.godpc.industrialcolonies.space.enemy.EnemyHullIdentity;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.level.block.state.BlockState;
import net.sprocketgames.create_aeronautics_automated_logistics.block.entity.ShipTransponderBlockEntity;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.function.BooleanSupplier;
import org.joml.Vector3d;

/** Explicit staged hull-only impact session. No event registration or automatic
 * resume. Inputs must come from complete native pre-step capture; this adapter
 * never interprets the solver's raw scalar. Native inventory destruction and
 * automatic fragment adoption are deliberately outside this initial writer.
 * A forced intent plus atomic receipt is audit evidence, not native-save atomicity. */
public final class CollisionHullDamage implements AutoCloseable {
    private static final Map<net.minecraft.server.level.ServerLevel,Map<UUID,CollisionHullDamage>> ACTIVE=new WeakHashMap<>();
    public record Outcome(int removed,String reason) {}
    private record Owner(UUID identity,String kind) {}
    private record Block(BlockPos position,BlockState state,double cost) {}
    private final ServerSubLevel body;
    private final UUID physical;
    private final Owner owner;
    private final Set<UUID> approvedPlayers,approvedNpcs;
    private final BooleanSupplier enabled;
    private final Path directory,pending;
    private final CollisionEpisodeBudget budget;
    private final long created;
    private String held;

    private CollisionHullDamage(ServerSubLevel body,Owner owner,Set<UUID> players,Set<UUID> npcs,
                                BooleanSupplier enabled,Path directory,CollisionEpisodeBudget budget) {
        this.body=body;physical=body.getUniqueId();this.owner=owner;
        approvedPlayers=Set.copyOf(players);approvedNpcs=Set.copyOf(npcs);this.enabled=enabled;
        this.directory=directory;pending=directory.resolve(physical+".pending");this.budget=budget;
        created=body.getLevel().getGameTime();
    }
    public static Optional<CollisionHullDamage> open(ServerSubLevel body,Set<UUID> approvedPlayers,
            Set<UUID> approvedNpcs,BooleanSupplier enabled,Path directory,CollisionEpisodeBudget budget) {
        if(body==null||approvedPlayers==null||approvedNpcs==null||enabled==null||directory==null||budget==null
                ||approvedPlayers.size()>128||approvedNpcs.size()>128
                ||!body.getLevel().getServer().isSameThread())return Optional.empty();
        try {
            if(!enabled.getAsBoolean())return Optional.empty();
            var sessions=ACTIVE.computeIfAbsent(body.getLevel(),unused->new HashMap<>());
            if(sessions.containsKey(body.getUniqueId())||sessions.size()>=64)return Optional.empty();
            Owner owner=observeOwner(body,approvedPlayers,approvedNpcs);
            Path root=directory.toAbsolutePath().normalize();Files.createDirectories(root);
            if(Files.isSymbolicLink(root)||Files.exists(root.resolve(body.getUniqueId()+".pending")))return Optional.empty();
            try(var entries=Files.list(root)){if(entries.limit(1025).count()>1024)return Optional.empty();}
            var session=new CollisionHullDamage(body,owner,approvedPlayers,approvedNpcs,enabled,root,budget);
            sessions.put(body.getUniqueId(),session);return Optional.of(session);
        }catch(IOException|RuntimeException refused){return Optional.empty();}
    }
    private static Owner observeOwner(ServerSubLevel b,Set<UUID> players,Set<UUID> npcs) {
        if(b.isRemoved()||!b.getPlot().getLoadedChunks().iterator().hasNext())throw new IllegalStateException("Unavailable body");
        Set<UUID> owners=new HashSet<>();int scanned=0;
        for(var holder:b.getPlot().getLoadedChunks())for(var be:holder.getChunk().getBlockEntities().values()){
            if(++scanned>128)throw new IllegalStateException("Ownership scan budget");
            if(be instanceof ShipTransponderBlockEntity t){
                if(t.isRemoved()||!b.getLevel().hasChunkAt(t.getBlockPos())||Sable.HELPER.getContaining(t)!=b)
                    throw new IllegalStateException("Unavailable owner");
                t.ownerId().ifPresent(owners::add);
            }
        }
        if(b.getUserDataTag()!=null&&b.getUserDataTag().contains(EnemyHullIdentity.KEY)){
            var npc=EnemyHullIdentity.read(b);
            if(!npc.originalBody()||!owners.isEmpty()||!npcs.contains(npc.encounter()))throw new IllegalStateException("Foreign NPC/fragment");
            return new Owner(npc.encounter(),"COMMISSIONED_NPC");
        }
        if(owners.size()!=1||!players.contains(owners.iterator().next()))throw new IllegalStateException("Unapproved player body");
        return new Owner(owners.iterator().next(),"NATIVE_TRANSPONDER");
    }
    private void current() {
        if(!body.getLevel().getServer().isSameThread())throw new IllegalStateException("Server-thread damage required");
        if(held!=null)throw new IllegalStateException(held);
        if(!enabled.getAsBoolean())throw new IllegalStateException("FEATURE_DISABLED");
        if(body.getLevel().getGameTime()<created||!body.getUniqueId().equals(physical)
                ||!observeOwner(body,approvedPlayers,approvedNpcs).equals(owner))throw new IllegalStateException("AUTHORITY_EXPIRED_OR_CHANGED");
    }
    public Outcome impact(long observedTick,CollisionObservationBuffer.Contact contact,
                          List<CollisionContactMotion.Step> steps) {
        int removed=0;
        try {
            current();long now=body.getLevel().getGameTime();
            if(observedTick<0||now<observedTick||now-observedTick>1)return new Outcome(0,"STALE_CONTACT");
            if(steps==null||steps.isEmpty())return new Outcome(0,"MISSING_NATIVE_CAPTURE");
            var first=steps.getFirst();boolean isA=contact.bodyA()==body.getRuntimeId();
            if(!isA&&contact.bodyB()!=body.getRuntimeId())return new Outcome(0,"FOREIGN_RUNTIME_ID");
            if(!(isA?first.first():first.second()).identity().equals(physical))return new Outcome(0,"FOREIGN_PHYSICAL_ID");
            double currentMass=body.getMassTracker().getMass();
            if(steps.stream().anyMatch(s->Double.compare((isA?s.first():s.second()).mass(),currentMass)!=0))
                return new Outcome(0,"HULL_MASS_CHANGED_SINCE_CAPTURE");
            var motion=CollisionContactMotion.estimate(observedTick,contact,first.first().identity(),first.second().identity(),steps,
                    new CollisionContactMotion.Tolerance(0.00001,0.3));
            if(!motion.accepted())return new Outcome(0,motion.reason());
            var pair=new CollisionEpisodeBudget.Pair(first.first().identity(),first.second().identity());
            long budgetTick=Integer.toUnsignedLong(body.getLevel().getServer().getTickCount());
            if(motion.minimumClosing()<3){budget.observe(budgetTick,pair,physical,0);return new Outcome(0,"BELOW_STRUCTURAL_THRESHOLD");}
            int cap=motion.minimumClosing()<7?4:16;
            var plan=plan(isA?contact.localPointA():contact.localPointB(),isA?contact.rawVectorA():contact.rawVectorB(),cap,motion.minimumEnergy());
            var grant=budget.observe(budgetTick,pair,physical,plan.size());
            if(grant.blocks()==0)return new Outcome(0,grant.reason());
            plan=List.copyOf(plan.subList(0,grant.blocks()));
            JsonObject intent=intent(observedTick,motion,plan);
            persistIntent(intent);
            for(Block block:plan){
                current();if(!eligible(block.position(),block.state()))throw new IllegalStateException("PLANNED_BLOCK_CHANGED");
                if(!body.getLevel().destroyBlock(block.position(),true))throw new IllegalStateException("NATIVE_BREAK_REFUSED");
                removed++;
            }
            Path receipt=directory.resolve(physical+"-"+UUID.randomUUID()+".receipt");
            Files.move(pending,receipt,StandardCopyOption.ATOMIC_MOVE);
            return new Outcome(removed,"APPLIED_NATIVE_BREAKS");
        }catch(IOException|RuntimeException stopped){held=stopped.toString();return new Outcome(removed,"HELD: "+held);}
    }
    private List<Block> plan(CollisionObservationBuffer.Vector local,CollisionObservationBuffer.Vector normal,int cap,double energy){
        var level=body.getLevel();var origin=body.logicalPose().rotationPoint();
        var start=new Vector3d(local.x(),local.y(),local.z()).add(origin);
        var inward=new Vector3d(normal.x(),normal.y(),normal.z()).normalize().negate();
        Set<BlockPos> seen=new HashSet<>();List<Block> result=new ArrayList<>();
        // Bounded inward ray: damage remains near this actual contact, never random distant blocks.
        for(int i=0;i<64&&result.size()<cap;i++){
            var point=new Vector3d(inward).mul(0.02+i*0.25).add(start);
            var pos=BlockPos.containing(point.x,point.y,point.z).immutable();if(!seen.add(pos))continue;
            if(!level.hasChunkAt(pos)||Sable.HELPER.getContaining(level,pos)!=body)break;
            BlockState state=level.getBlockState(pos);
            if(state.isAir())continue;
            if(!eligible(pos,state))break;
            double cost=100*Math.max(0.1,state.getDestroySpeed(level,pos));
            if(!Double.isFinite(cost)||cost>energy)break;
            result.add(new Block(pos,state,cost));energy-=cost;
        }
        return result;
    }
    private boolean eligible(BlockPos pos,BlockState expected){
        var level=body.getLevel();if(!level.hasChunkAt(pos)||Sable.HELPER.getContaining(level,pos)!=body)return false;
        var actual=level.getBlockState(pos);
        return actual.equals(expected)&&!actual.isAir()&&!actual.hasBlockEntity()&&level.getBlockEntity(pos)==null
                &&actual.getFluidState().isEmpty()&&actual.getDestroySpeed(level,pos)>=0;
    }
    private JsonObject intent(long tick,CollisionContactMotion.Result motion,List<Block> plan){
        JsonObject result=new JsonObject();result.addProperty("schema","IC_COLLISION_INTENT_1");
        result.addProperty("body",physical.toString());result.addProperty("owner",owner.identity().toString());
        result.addProperty("ownerKind",owner.kind());result.addProperty("dimension",body.getLevel().dimension().location().toString());
        result.addProperty("tick",tick);result.addProperty("minimumClosing",motion.minimumClosing());
        result.addProperty("minimumNativeUnitEnergy",motion.minimumEnergy());
        JsonArray blocks=new JsonArray();for(Block block:plan){var row=new JsonObject();row.addProperty("x",block.position().getX());row.addProperty("y",block.position().getY());row.addProperty("z",block.position().getZ());row.addProperty("block",BuiltInRegistries.BLOCK.getKey(block.state().getBlock()).toString());row.addProperty("state",block.state().toString());row.addProperty("cost",block.cost());blocks.add(row);}result.add("blocks",blocks);return result;
    }
    private void persistIntent(JsonObject intent)throws IOException {
        try(var entries=Files.list(directory)){if(entries.limit(1025).count()>1024)throw new IOException("Journal capacity held");}
        byte[] bytes=new Gson().toJson(intent).getBytes(StandardCharsets.UTF_8);
        if(bytes.length>32768)throw new IOException("Intent bound exceeded");
        try(var channel=FileChannel.open(pending,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)){
            ByteBuffer buffer=ByteBuffer.wrap(bytes);while(buffer.hasRemaining())channel.write(buffer);channel.force(true);
        }
    }
    public boolean held(){return held!=null;}
    /** Poll even without contacts so disable/ownership loss is held before later re-enable. */
    public Outcome poll(){if(held!=null)return new Outcome(0,"HELD: "+held);try{current();return new Outcome(0,"ARMED");}catch(RuntimeException stopped){held=stopped.toString();return new Outcome(0,"HELD: "+held);}}
    @Override public void close(){
        if(!body.getLevel().getServer().isSameThread())throw new IllegalStateException("Server-thread close required");
        held="EXPLICITLY_CLOSED";var sessions=ACTIVE.get(body.getLevel());if(sessions!=null){sessions.remove(physical,this);if(sessions.isEmpty())ACTIVE.remove(body.getLevel());}
    }
}
