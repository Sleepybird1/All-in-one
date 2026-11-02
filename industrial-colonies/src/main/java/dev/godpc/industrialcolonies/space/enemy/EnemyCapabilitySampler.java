package dev.godpc.industrialcolonies.space.enemy;

import dev.devce.rocketnautics.content.blocks.RCSThrusterBlockEntity;
import dev.devce.rocketnautics.content.blocks.RocketThrusterBlockEntity;
import dev.godpc.industrialcolonies.space.RcsActuatorLease;
import dev.godpc.industrialcolonies.space.RocketActuatorLease;
import dev.godpc.industrialcolonies.space.SpaceflightAuthorization;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.neoforged.neoforge.capabilities.Capabilities;
import java.util.*;

/** Bounded read-only observations, never control/lease/firing authority.
 * Energy is reported per block, not summed across aliased face capabilities.
 * A mounted cannon still needs a separate finite-ammunition and aim audit. */
public final class EnemyCapabilitySampler {
    public record Component(BlockPos position, String kind, boolean available, String reason, int supply, UUID attachment, String contents) {
        public Component(BlockPos position,String kind,boolean available,String reason,int supply) { this(position,kind,available,reason,supply,null,null); }
    }
    public record Snapshot(UUID body, long tick, List<Component> components) {
        public Snapshot { components = List.copyOf(components); }
    }
    private final ServerSubLevel body;
    private final NativeEnemyHull hull;
    private final List<BlockPos> positions;
    private EnemyCapabilitySampler(ServerSubLevel body, NativeEnemyHull hull, Collection<BlockPos> positions) {
        this.body = Objects.requireNonNull(body); this.hull = Objects.requireNonNull(hull);
        if (!hull.belongsTo(body) || positions == null || positions.isEmpty() || positions.size() > 128
                || positions.stream().anyMatch(p -> p==null || !hull.observes(p)) || new HashSet<>(positions).size()!=positions.size())
            throw new IllegalArgumentException("Invalid capability manifest");
        this.positions = positions.stream().map(BlockPos::immutable).toList();
    }
    public static EnemyCapabilitySampler commission(ServerSubLevel body, NativeEnemyHull hull, Collection<BlockPos> positions) {
        return new EnemyCapabilitySampler(body,hull,positions);
    }
    public Optional<Snapshot> sample() {
        var level=body.getLevel();
        if (!level.getServer().isSameThread()) throw new IllegalStateException("Server-thread capability sample required");
        if (!hull.validate() || SpaceflightAuthorization.automationDisabled(body)) return Optional.empty();
        var result=new ArrayList<Component>();
        for (var p:positions) {
            if (!level.hasChunkAt(p) || Sable.HELPER.getContaining(level,p)!=body) return Optional.empty();
            var be=level.getBlockEntity(p);
            if (be==null || be.isRemoved()) return Optional.empty();
            if (be instanceof RCSThrusterBlockEntity engine) {
                boolean free=!engine.isActive()&&!level.hasNeighborSignal(p)
                        &&!engine.getPersistentData().contains(RcsActuatorLease.SAVED_MARKER);
                result.add(new Component(p,"RCS",free,free?"DISARMED_LEASE_CANDIDATE":"CONTROL_BUSY",0));
            }
            if (be instanceof RocketThrusterBlockEntity engine) {
                var saved=engine.saveWithoutMetadata(level.registryAccess());
                boolean free=!engine.isActive()&&!saved.getBoolean("TargetActive")&&saved.getFloat("TargetThrottle")==0
                        &&!engine.getPersistentData().contains(RocketActuatorLease.SAVED_MARKER);
                int fuel=engine.fuelTank.getFluidAmount();
                result.add(new Component(p,"ROCKET",free&&fuel>0,!free?"CONTROL_BUSY":fuel==0?"FUEL_UNAVAILABLE":"FUELED_LEASE_CANDIDATE",fuel));
            }
            int stored=0; boolean extracting=false; boolean energy=false;
            for (var side:Direction.values()) {
                var cap=level.getCapability(Capabilities.EnergyStorage.BLOCK,p,side);
                if (cap!=null) { energy=true; int value=cap.getEnergyStored(); if(value<0)return Optional.empty();
                    stored=Math.max(stored,value); extracting|=cap.canExtract()&&value>0; }
            }
            if (energy) result.add(new Component(p,"ENERGY",extracting,extracting?"STORED_EXTRACTABLE_FE":"NO_EXTRACTABLE_FE",stored));
            if (be.getClass().getName().equals("rbasamoyai.createbigcannons.cannon_control.cannon_mount.CannonMountBlockEntity")) {
                try {
                    Object attachment=be.getClass().getMethod("getContraption").invoke(be);
                    boolean mounted=Boolean.TRUE.equals(be.getClass().getMethod("isRunning").invoke(be))
                            &&attachment instanceof net.minecraft.world.entity.Entity entity&&!entity.isRemoved();
                    int visibleAmmo=0; UUID entityId=null; String signature=""; boolean armed=false;
                    if (mounted) {
                        var entity=(net.minecraft.world.entity.Entity)attachment; entityId=entity.getUUID();
                        Object cannon=attachment.getClass().getMethod("getContraption").invoke(attachment);
                        if (cannon!=null && cannon.getClass().getName().equals("rbasamoyai.createbigcannons.cannon_control.contraption.MountedAutocannonContraption")) {
                            Object entities=cannon.getClass().getField("presentBlockEntities").get(cannon);
                            if (!(entities instanceof Map<?,?> blocks)||blocks.size()>256)return Optional.empty();
                            Object start=cannon.getClass().getMethod("getStartPos").invoke(cannon);
                            Object breech=blocks.get(start);
                            Class<?> breechType=Class.forName("rbasamoyai.createbigcannons.cannons.autocannon.breech.AbstractAutocannonBreechBlockEntity");
                            if(breechType.isInstance(breech)) {
                                armed=((Number)breechType.getMethod("getFireRate").invoke(breech)).intValue()!=0;
                                Object input=breechType.getMethod("getInputBuffer").invoke(breech);
                                if(!(input instanceof Collection<?> queue)||queue.size()>64)return Optional.empty();
                                Class<?> ammoType=Class.forName("rbasamoyai.createbigcannons.munitions.autocannon.AutocannonAmmoItem");
                                for(Object entry:queue) {
                                    if(!(entry instanceof net.minecraft.world.item.ItemStack stack)||stack.isEmpty()||!ammoType.isInstance(stack.getItem())
                                            ||ammoType.getMethod("getEntityType",net.minecraft.world.item.ItemStack.class).invoke(stack.getItem(),stack)==null)return Optional.empty();
                                    visibleAmmo=Math.addExact(visibleAmmo,stack.getCount());
                                    signature+=stack.save(level.registryAccess()).toString()+"\n";
                                    if(visibleAmmo>4096||signature.length()>65536)return Optional.empty();
                                }
                            }
                        }
                    }
                    // Queued rounds are a readiness hint; magazine/output custody and aim need separate audits.
                    result.add(new Component(p,"CANNON",mounted&&!armed&&visibleAmmo>0,!mounted?"UNASSEMBLED":armed?"CONTROL_BUSY":visibleAmmo==0?"AMMUNITION_UNAVAILABLE":"LOADED_WEAPON_CANDIDATE",visibleAmmo,entityId,signature));
                } catch (ReflectiveOperationException|RuntimeException unsupported) { return Optional.empty(); }
            }
        }
        return Optional.of(new Snapshot(body.getUniqueId(),level.getGameTime(),result));
    }
    /** Samples are valid only for the immediate server-thread decision, then resample. */
    public boolean current(Snapshot snapshot) {
        if(snapshot==null||!snapshot.body().equals(body.getUniqueId())||snapshot.tick()!=body.getLevel().getGameTime())return false;
        return sample().filter(snapshot::equals).isPresent();
    }
}
