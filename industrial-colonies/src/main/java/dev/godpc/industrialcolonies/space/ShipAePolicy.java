package dev.godpc.industrialcolonies.space;

import appeng.api.networking.IGrid;
import appeng.api.networking.IGridNode;
import appeng.api.parts.IPartHost;
import appeng.api.stacks.AEKeyType;
import appeng.api.storage.IStorageProvider;
import appeng.api.storage.StorageCells;
import appeng.api.storage.cells.IBasicCellItem;
import appeng.blockentity.storage.DriveBlockEntity;
import appeng.blockentity.storage.MEChestBlockEntity;
import appeng.blockentity.AEBaseInvBlockEntity;
import appeng.me.InWorldGridNode;
import appeng.me.helpers.IGridConnectedBlockEntity;
import appeng.parts.AEBasePart;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import java.util.*;

/** Read-only custody policy. Never changes cell contents, mounts, grid identity or saved state. */
public final class ShipAePolicy {
    public static final String DISABLED_MESSAGE = "Ship AE2 disabled: one Matter Stabilizer per item cell, each cell on one local network; maximum 4 KiB across the whole ship; no fluid/gas cells, external storage or off-ship links.";
    private ShipAePolicy() {}

    public static ServerSubLevel body(BlockEntity be) {
        return Sable.HELPER.getContaining(be) instanceof ServerSubLevel ship ? ship : null;
    }
    private static ServerSubLevel body(IGridNode node) {
        if (node instanceof InWorldGridNode world) {
            return Sable.HELPER.getContaining(node.getLevel(), world.getLocation()) instanceof ServerSubLevel ship ? ship : null;
        }
        Object owner = node.getOwner();
        if (owner instanceof BlockEntity be) return body(be);
        if (owner instanceof AEBasePart part) return body(part.getBlockEntity());
        return null;
    }
    private static BlockEntity host(IGridNode node) {
        if (node.getOwner() instanceof BlockEntity be) return be;
        if (node.getOwner() instanceof AEBasePart part) return part.getBlockEntity();
        return null;
    }
    private static boolean localNode(IGridNode node, ServerSubLevel ship, Set<BlockEntity> present) {
        BlockEntity be = host(node);
        return be != null && !be.isRemoved() && present.contains(be) && body(node) == ship && safeProvider(node);
    }
    public static boolean allowed(IGrid grid) {
        try { return checked(grid); } catch (RuntimeException unknown) { return false; }
    }
    private static boolean checked(IGrid grid) {
        if (grid == null) return true;
        Set<ServerSubLevel> ships = Collections.newSetFromMap(new IdentityHashMap<>());
        for (IGridNode node : grid.getNodes()) {
            ServerSubLevel ship = body(node);
            if (ship != null) ships.add(ship);
        }
        if (ships.isEmpty()) return true; // Existing ground networks unchanged.
        if (ships.size() != 1) return false;
        ServerSubLevel ship = ships.iterator().next();
        if (!ship.getLevel().getServer().isSameThread() || ship.isRemoved()) return false;
        for (IGridNode node : grid.getNodes()) {
            if (body(node) != ship || !safeProvider(node)) return false;
        }
        return allowed(ship);
    }
    public static boolean allowedSource(IGrid grid, appeng.api.networking.security.IActionSource source) {
        if (source == null || source.player().isEmpty()) return true;
        var body = Sable.HELPER.getContaining(source.player().get());
        if (body == null) return true;
        if (grid == null || grid.isEmpty()) return false;
        for (IGridNode node : grid.getNodes()) if (body(node) != body) return false;
        return true;
    }
    public static boolean allowedSource(BlockEntity be, appeng.api.networking.security.IActionSource source) {
        if (source == null || source.player().isEmpty()) return true;
        var passenger = Sable.HELPER.getContaining(source.player().get());
        return passenger == null || body(be) == passenger;
    }
    private static boolean safeProvider(IGridNode node) {
        Object owner = node.getOwner();
        // Bridges can be idle/disconnected while scanned; reject their presence, not just an active link.
        if (owner.getClass().getName().contains(".qnb.")
                || owner.getClass().getName().toLowerCase(Locale.ROOT).contains("quantumbridge")) return false;
        return node.getService(IStorageProvider.class) == null
                || owner instanceof DriveBlockEntity || owner instanceof MEChestBlockEntity;
    }
    public static boolean allowed(BlockEntity be) {
        try { return checked(be); } catch (RuntimeException unknown) { return false; }
    }
    private static boolean checked(BlockEntity be) {
        ServerSubLevel ship = body(be);
        if (ship == null) return true;
        if (!allowed(ship)) return false;
        if (be instanceof IGridConnectedBlockEntity host) {
            IGridNode node = host.getGridNode();
            return node == null || allowed(node.getGrid());
        }
        return true;
    }
    private static boolean cell(ItemStack stack, ShipAeBudget budget) {
        if (stack.isEmpty() || !StorageCells.isCellHandled(stack)) return true;
        if (!(stack.getItem() instanceof IBasicCellItem item)) return false;
        return budget.add(item.getBytes(stack), stack.getCount(), item.getKeyType() == AEKeyType.items(), true);
    }
    public static boolean allowed(ServerSubLevel ship) {
        try { return checked(ship); } catch (RuntimeException unknown) { return false; }
    }
    private static boolean checked(ServerSubLevel ship) {
        if (ship.isRemoved() || !ship.getLevel().getServer().isSameThread()) return false;
        ShipAeBudget budget = new ShipAeBudget();
        int checked = 0;
        int stabilizers = 0;
        // Snapshot live custody first. An unloaded/stale grid provider is not
        // credited as zero capacity merely because it is absent from this scan.
        Set<BlockEntity> present = Collections.newSetFromMap(new IdentityHashMap<>());
        if (ship.getPlot().getLoadedChunks().size() > 256) return false;
        for (var holder : ship.getPlot().getLoadedChunks()) {
            if (holder == null || holder.getChunk() == null) return false;
            for (BlockEntity be : holder.getChunk().getBlockEntities().values()) {
                if (++checked > 4096 || be.isRemoved() || body(be) != ship) return false;
                present.add(be);
            }
        }
        for (BlockEntity be : present) {
            if (be instanceof MatterStabilizerBlockEntity && be.getBlockState().getBlock() instanceof MatterStabilizerBlock) stabilizers++;
            if (be instanceof IGridConnectedBlockEntity host) {
                IGridNode node = host.getGridNode();
                if (node != null) {
                    if (!localNode(node, ship, present)) return false;
                    for (IGridNode peer : node.getGrid().getNodes())
                        if (!localNode(peer, ship, present)) return false;
                }
            }
            if (be instanceof IPartHost parts) {
                for (Direction side : Direction.values()) {
                    var part = parts.getPart(side);
                    if (part != null && part.getGridNode() != null) {
                        if (!localNode(part.getGridNode(), ship, present)) return false;
                        for (IGridNode peer : part.getGridNode().getGrid().getNodes())
                            if (!localNode(peer, ship, present)) return false;
                    }
                }
            }
            if (be instanceof AEBaseInvBlockEntity inventory)
                for (ItemStack stack : inventory.getInternalInventory()) {
                    if (!stack.isEmpty() && StorageCells.isCellHandled(stack)) {
                        // A stabilizer slot is reserved per physical cell, not per drive
                        // or grid. The containing storage must have exactly one live local grid.
                        if (!(be instanceof IGridConnectedBlockEntity storageHost)
                                || storageHost.getGridNode() == null
                                || storageHost.getGridNode().getGrid() == null) return false;
                    }
                    if (!cell(stack, budget)) return false;
                }
        }
        return budget.authorized(stabilizers);
    }
}
