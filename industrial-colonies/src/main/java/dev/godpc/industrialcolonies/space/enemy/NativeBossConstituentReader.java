package dev.godpc.industrialcolonies.space.enemy;

import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.state.BlockState;
import rbasamoyai.createbigcannons.cannon_control.cannon_mount.CannonMountBlockEntity;
import rbasamoyai.createbigcannons.cannon_control.contraption.MountedAutocannonContraption;
import java.util.*;

/** Unregistered read-only constituent reader. Known bodies must come from the
 * live lineage owner, never a UUID lookup that silently substitutes a body.
 * Missing/replaced/unloaded cells are UNKNOWN, not evidence of destruction.
 * Durable mutation and destruction records must be reconciled separately. */
public final class NativeBossConstituentReader {
    public sealed interface Address permits HullCell, MountedCell { UUID body(); }
    public record HullCell(UUID body, BlockPos position) implements Address {
        public HullCell { Objects.requireNonNull(body); position=Objects.requireNonNull(position).immutable(); }
    }
    public record MountedCell(UUID body, BlockPos mount, UUID entity, BlockPos local) implements Address {
        public MountedCell {
            Objects.requireNonNull(body); Objects.requireNonNull(entity);
            mount=Objects.requireNonNull(mount).immutable(); local=Objects.requireNonNull(local).immutable();
        }
    }
    public record Part(Address address, BlockState expected) {
        public Part { Objects.requireNonNull(address); Objects.requireNonNull(expected);
            if(expected.isAir())throw new IllegalArgumentException("Intact nonair state required"); }
    }
    private final UUID encounter, authority;
    private final ServerLevel level;
    private final Map<UUID, ServerSubLevel> bodies;
    private final Map<String, Part> manifest;
    private final long revision;
    private record MountedSlot(UUID entity, BlockPos local) {}

    public NativeBossConstituentReader(UUID encounter, UUID authority, ServerLevel level,
            Map<UUID, ServerSubLevel> knownBodies, long revision, Map<String, Part> manifest) {
        this.encounter=Objects.requireNonNull(encounter);this.authority=Objects.requireNonNull(authority);
        this.level=Objects.requireNonNull(level);this.revision=revision;
        this.bodies=Map.copyOf(knownBodies);this.manifest=Map.copyOf(manifest);
        if(revision<0 || bodies.isEmpty() || bodies.size()>128 || manifest.isEmpty() || manifest.size()>128
                || manifest.keySet().stream().anyMatch(s->s.isBlank()||s.length()>128))
            throw new IllegalArgumentException("Invalid bounded constituent manifest");
        // Alias addresses cannot count the same physical cell twice.
        var slots=new HashSet<Object>();
        var hullPositions=new HashSet<BlockPos>();
        for(var part:manifest.values()) {
            if(!bodies.containsKey(part.address().body()))throw new IllegalArgumentException("Unknown body");
            if(part.address() instanceof HullCell cell) {
                if(!hullPositions.add(cell.position()))throw new IllegalArgumentException("Duplicate native hull cell");
            } else if(part.address() instanceof MountedCell cell) {
                if(!slots.add(new MountedSlot(cell.entity(),cell.local())))
                    throw new IllegalArgumentException("Duplicate native mounted cell");
            }
        }
        for(var entry:bodies.entrySet())if(!entry.getKey().equals(entry.getValue().getUniqueId())||entry.getValue().getLevel()!=level)
            throw new IllegalArgumentException("Body identity/level mismatch");
    }
    /** Only the caller's verified lineage/revision supplies scope. No ownership
     * is inferred from a copied encounter tag or an entity's spatial proximity. */
    public EnemyBossDefeat.Observation observe(boolean enabled) {
        if(!level.getServer().isSameThread())throw new IllegalStateException("Server thread required");
        var values=new HashMap<String,EnemyBossDefeat.Condition>();boolean complete=true;
        for(var entry:manifest.entrySet()) {
            boolean intact;
            try { intact=read(entry.getValue()); }
            catch(RuntimeException unavailable) { intact=false; }
            values.put(entry.getKey(),intact?EnemyBossDefeat.Condition.INTACT:EnemyBossDefeat.Condition.UNKNOWN);
            complete &= intact;
        }
        return new EnemyBossDefeat.Observation(encounter,authority,level.getGameTime(),revision,complete,enabled,values);
    }
    private boolean read(Part part) {
        var body=bodies.get(part.address().body());
        if(body==null||body.isRemoved()||body.getLevel()!=level)return false;
        if(part.address() instanceof HullCell cell) {
            if(!level.hasChunkAt(cell.position())||Sable.HELPER.getContaining(level,cell.position())!=body
                    ||!level.getBlockState(cell.position()).equals(part.expected()))return false;
            if(part.expected().hasBlockEntity()) {
                var be=level.getBlockEntity(cell.position());
                return be!=null&&!be.isRemoved()&&Sable.HELPER.getContaining(be)==body;
            }
            return true;
        }
        var cell=(MountedCell)part.address();
        if(!level.hasChunkAt(cell.mount())||Sable.HELPER.getContaining(level,cell.mount())!=body)return false;
        var be=level.getBlockEntity(cell.mount());
        if(!(be instanceof CannonMountBlockEntity mount)||mount.isRemoved()||!mount.isRunning()
                ||Sable.HELPER.getContaining(mount)!=body)return false;
        var entity=mount.getContraption();
        if(entity==null||!entity.getUUID().equals(cell.entity())||entity.isRemoved()||entity.level()!=level
                ||level.getEntity(cell.entity())!=entity||entity.getController()!=mount||!entity.getPassengers().isEmpty())return false;
        if(!(entity.getContraption() instanceof MountedAutocannonContraption cannon))return false;
        var blocks=cannon.getBlocks();
        if(blocks.isEmpty()||blocks.size()>256)return false;
        var block=blocks.get(cell.local());
        if(block==null||!block.state().equals(part.expected()))return false;
        if(part.expected().hasBlockEntity()) {
            var machine=cannon.presentBlockEntities.get(cell.local());
            if(machine==null||machine.isRemoved()||!machine.getBlockState().equals(part.expected()))return false;
        }
        return true;
    }
}
