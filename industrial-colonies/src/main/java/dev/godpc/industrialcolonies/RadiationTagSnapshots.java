package dev.godpc.industrialcolonies;

import igentuman.nr.api.RadiationProfile;
import igentuman.nr.api.binding.Bindings;
import java.util.Map;
import java.util.function.Supplier;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.material.Fluid;

/** Cache binding maps, never evaluated profiles, item data, tag membership or radiation dose. */
public final class RadiationTagSnapshots {
    private static final VersionedReadOnlySnapshot<TagKey<Item>, Supplier<RadiationProfile>> ITEMS = new VersionedReadOnlySnapshot<>();
    private static final VersionedReadOnlySnapshot<TagKey<Block>, Supplier<RadiationProfile>> BLOCKS = new VersionedReadOnlySnapshot<>();
    private static final VersionedReadOnlySnapshot<TagKey<Fluid>, Supplier<RadiationProfile>> FLUIDS = new VersionedReadOnlySnapshot<>();
    private RadiationTagSnapshots() {}
    public static void invalidate() { ITEMS.invalidate(); BLOCKS.invalidate(); FLUIDS.invalidate(); }
    public static Map<TagKey<Item>, Supplier<RadiationProfile>> items() { return ITEMS.get(Bindings::itemTags); }
    public static Map<TagKey<Block>, Supplier<RadiationProfile>> blocks() { return BLOCKS.get(Bindings::blockTags); }
    public static Map<TagKey<Fluid>, Supplier<RadiationProfile>> fluids() { return FLUIDS.get(Bindings::fluidTags); }
}
