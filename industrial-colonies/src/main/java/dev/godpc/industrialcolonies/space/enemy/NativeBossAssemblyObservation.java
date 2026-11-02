package dev.godpc.industrialcolonies.space.enemy;

import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.api.SubLevelAssemblyHelper.AssemblyTransform;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.state.BlockState;
import java.util.*;

/** Unregistered synchronous observer for the native moveBlocks boundary.
 * Never removes blocks, assembles a ship, marks destruction or commands it.
 * A caller must hold combat for the complete mutation and retain uncertainty
 * after an exception; pre-split listeners alone cannot commit a relocation. */
public final class NativeBossAssemblyObservation {
    private record Cell(String module, BlockPos from, BlockPos to, BlockState state) {}
    private final ServerLevel level;
    private final ServerSubLevel source;
    private final EnemyBossModules baseline;
    private final UUID encounter, root;
    private final long tick;
    private final List<Cell> cells;
    private boolean consumed;

    private NativeBossAssemblyObservation(ServerLevel level, ServerSubLevel source, EnemyBossModules baseline,
            UUID encounter, UUID root, List<Cell> cells) {
        this.level=level;this.source=source;this.baseline=baseline;this.encounter=encounter;this.root=root;
        this.tick=level.getGameTime();this.cells=List.copyOf(cells);
    }
    public static NativeBossAssemblyObservation before(ServerLevel level, ServerSubLevel source,
            EnemyBossModules baseline, AssemblyTransform transform, Set<BlockPos> moving) {
        var identity=EnemyHullIdentity.read(source);
        return beforeKnown(level,source,baseline,transform,moving,identity.encounter(),identity.root());
    }
    /** Called only by the live lineage owner for an already observed exact body. */
    static NativeBossAssemblyObservation beforeKnown(ServerLevel level, ServerSubLevel source,
            EnemyBossModules baseline, AssemblyTransform transform, Set<BlockPos> moving, UUID encounter, UUID root) {
        if (level==null || source==null || baseline==null || transform==null
                || !level.getServer().isSameThread() || source.getLevel()!=level || source.isRemoved()
                || transform.getLevel()!=level || moving==null || moving.size()>4096)
            throw new IllegalStateException("Invalid synchronous assembly scope");
        if(!baseline.belongsTo(encounter,root))throw new IllegalStateException("Foreign module ledger");
        if(source.getUserDataTag()!=null&&source.getUserDataTag().contains(EnemyHullIdentity.KEY)) {
            var identity=EnemyHullIdentity.read(source);
            if(!identity.encounter().equals(encounter)||!identity.root().equals(root))
                throw new IllegalStateException("Source identity changed");
        }
        var cells=new ArrayList<Cell>();
        for(var entry:baseline.modules().entrySet()) {
            var module=entry.getValue();
            if(module.destroyed() || !module.location().body().equals(source.getUniqueId()))continue;
            var loc=module.location();var from=new BlockPos(loc.x(),loc.y(),loc.z());
            if(!moving.contains(from))continue;
            if(!level.hasChunkAt(from) || Sable.HELPER.getContaining(level,from)!=source)
                throw new IllegalStateException("Module custody unavailable");
            var state=level.getBlockState(from);
            if(state.isAir())throw new IllegalStateException("Missing source module");
            cells.add(new Cell(entry.getKey(),from.immutable(),transform.apply(from).immutable(),transform.apply(state)));
        }
        if(cells.isEmpty())throw new IllegalStateException("No commissioned modules in movement");
        return new NativeBossAssemblyObservation(level,source,baseline,encounter,root,cells);
    }
    public EnemyBossModules after(ServerSubLevel destination) {
        if(!level.getServer().isSameThread())throw new IllegalStateException("Server thread required");
        if(consumed)throw new IllegalStateException("Assembly observation already consumed");
        consumed=true;
        if(level.getGameTime()!=tick || destination==null || destination==source || destination.isRemoved()
                || destination.getLevel()!=level)throw new IllegalStateException("Invalid completed assembly");
        // Sable records parent provenance but does NOT copy encounter metadata.
        boolean tagged=destination.getUserDataTag()!=null
                &&destination.getUserDataTag().contains(EnemyHullIdentity.KEY);
        var identity=tagged?EnemyHullIdentity.read(destination):null;
        if(!EnemyBossFragmentProvenance.matches(source.getUniqueId(),destination.getUniqueId(),
                destination.getSplitFromSubLevel(),encounter,root,tagged,
                identity==null?null:identity.encounter(),identity==null?null:identity.root()))
            throw new IllegalStateException("Fragment identity mismatch");
        var changes=new ArrayList<EnemyBossModules.Change>();
        for(var cell:cells) {
            if(!level.hasChunkAt(cell.from())||!level.hasChunkAt(cell.to())
                    ||!level.getBlockState(cell.from()).isAir()
                    ||Sable.HELPER.getContaining(level,cell.to())!=destination
                    ||!level.getBlockState(cell.to()).equals(cell.state()))
                throw new IllegalStateException("Incomplete or changed native movement");
            changes.add(new EnemyBossModules.Change(cell.module(),location(source,cell.from()),location(destination,cell.to())));
        }
        return baseline.apply(encounter,root,baseline.revision(),changes);
    }
    private static EnemyBossModules.Location location(ServerSubLevel body,BlockPos p) {
        return new EnemyBossModules.Location(body.getUniqueId(),p.getX(),p.getY(),p.getZ());
    }
}
