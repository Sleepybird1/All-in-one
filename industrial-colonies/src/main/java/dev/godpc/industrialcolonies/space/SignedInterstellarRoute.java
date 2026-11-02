package dev.godpc.industrialcolonies.space;

import dev.waco0311.cosmowarp.block.entity.WarpDriveBlockEntity;
import dev.waco0311.cosmowarp.data.WarpPoint;
import dev.waco0311.cosmowarp.registry.ModDataComponents;
import dev.waco0311.cosmowarp.registry.ModItems;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.Level;

/** Exact source-authored, bidirectional Sol-to-Glacio route contract. */
public final class SignedInterstellarRoute {
    public static final int SCHEMA = 1;
    public static final String ROUTE_ID = "sol_glacio_v1";
    public static final String SIGNATURE =
            "3075d9ba54e0d5aff1fcd3d799e9a3906df93fcc5f68ffa019db07d19f4903ec";
    public static final String CUSTOM_DATA_KEY = "industrial_colonies:interstellar_route";

    public static final UUID SOL_POINT_ID =
            UUID.fromString("2d85acb9-5567-5292-9bb1-8420dc590f3a");
    public static final UUID GLACIO_POINT_ID =
            UUID.fromString("c27cc553-9d70-5170-ab7c-2af238ed19b3");
    public static final String SOL_POINT_NAME = "Sol Industrial Anchorage";
    public static final String GLACIO_POINT_NAME = "Glacio Industrial Anchorage";
    public static final BlockPos SOL_POINT_POS = new BlockPos(0, 256, 0);
    public static final BlockPos GLACIO_POINT_POS = new BlockPos(0, 256, 0);

    public static final ResourceKey<Level> SOL_DIMENSION = ResourceKey.create(
            Registries.DIMENSION,
            ResourceLocation.fromNamespaceAndPath("minecraft", "overworld"));
    public static final ResourceKey<Level> GLACIO_DIMENSION = ResourceKey.create(
            Registries.DIMENSION,
            ResourceLocation.fromNamespaceAndPath("ad_astra", "glacio"));

    public static final WarpPoint SOL_POINT = new WarpPoint(
            SOL_POINT_ID, SOL_POINT_NAME, SOL_DIMENSION, SOL_POINT_POS);
    public static final WarpPoint GLACIO_POINT = new WarpPoint(
            GLACIO_POINT_ID, GLACIO_POINT_NAME, GLACIO_DIMENSION, GLACIO_POINT_POS);
    public static final List<WarpPoint> EXACT_POINT_SET = List.of(SOL_POINT, GLACIO_POINT);

    private SignedInterstellarRoute() {
    }

    /**
     * Replaces every mutable Cosmowarp route field with the exact pack-owned
     * route and selects the only destination valid from the current endpoint.
     */
    public static boolean signForDimension(
            ItemStack crystal,
            ResourceKey<Level> currentDimension
    ) {
        if (!crystal.is(ModItems.WARP_CRYSTAL.get())) {
            return false;
        }
        UUID target;
        if (SOL_DIMENSION.equals(currentDimension)) {
            target = GLACIO_POINT_ID;
        } else if (GLACIO_DIMENSION.equals(currentDimension)) {
            target = SOL_POINT_ID;
        } else {
            return false;
        }
        crystal.set(ModDataComponents.WARP_POINTS.get(), EXACT_POINT_SET);
        crystal.set(ModDataComponents.SELECTED_WARP_POINT.get(), target);
        crystal.set(DataComponents.CUSTOM_DATA, CustomData.of(expectedCustomData()));
        return true;
    }

    /**
     * Resolves a route only when the item, signature, complete point set,
     * selected UUID, source dimension, and opposite destination all match.
     * Every mismatch fails closed.
     */
    public static Optional<Route> resolve(WarpDriveBlockEntity drive) {
        if (drive.getLevel() == null) {
            return Optional.empty();
        }
        ItemStack crystal = drive.getCrystalSlot().getStackInSlot(0);
        if (!isExactSignedCrystal(crystal)) {
            return Optional.empty();
        }
        Optional<UUID> selected = drive.getSelectedId();
        if (selected.isEmpty()) {
            return Optional.empty();
        }
        ResourceKey<Level> source = drive.getLevel().dimension();
        if (SOL_DIMENSION.equals(source) && GLACIO_POINT_ID.equals(selected.get())) {
            return Optional.of(new Route(SOL_POINT, GLACIO_POINT, true));
        }
        if (GLACIO_DIMENSION.equals(source) && SOL_POINT_ID.equals(selected.get())) {
            return Optional.of(new Route(GLACIO_POINT, SOL_POINT, false));
        }
        return Optional.empty();
    }

    public static boolean isExactSignedCrystal(ItemStack crystal) {
        if (!crystal.is(ModItems.WARP_CRYSTAL.get())) {
            return false;
        }
        List<WarpPoint> points = crystal.getOrDefault(
                ModDataComponents.WARP_POINTS.get(), List.of());
        if (!EXACT_POINT_SET.equals(points)) {
            return false;
        }
        UUID selected = crystal.get(ModDataComponents.SELECTED_WARP_POINT.get());
        if (!SOL_POINT_ID.equals(selected) && !GLACIO_POINT_ID.equals(selected)) {
            return false;
        }
        CustomData customData = crystal.get(DataComponents.CUSTOM_DATA);
        return customData != null && expectedCustomData().equals(customData.copyTag());
    }

    public static CompoundTag expectedCustomData() {
        CompoundTag route = new CompoundTag();
        route.putInt("schema", SCHEMA);
        route.putString("route", ROUTE_ID);
        route.putString("signature", SIGNATURE);
        CompoundTag root = new CompoundTag();
        root.put(CUSTOM_DATA_KEY, route);
        return root;
    }

    public record Route(WarpPoint source, WarpPoint target, boolean inboundToGlacio) {
    }
}
