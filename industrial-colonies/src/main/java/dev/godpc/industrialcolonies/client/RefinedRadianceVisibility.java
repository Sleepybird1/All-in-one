package dev.godpc.industrialcolonies.client;

import com.simibubi.create.AllCreativeModeTabs;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.BuildCreativeModeTabContentsEvent;

import java.util.ArrayList;
import java.util.List;

/**
 * Restores the useful Refined Radiance family to Create's creative tab and to
 * ingredient viewers. Create 6 retains the legacy material and casing, while
 * Create Encased intentionally filters a very large set of redundant variants.
 * Keeping an explicit allow-list exposes the progression machines without
 * bringing the decorative zero-stress cog/shaft explosion back into searches.
 */
public final class RefinedRadianceVisibility {
    private static final List<ResourceLocation> VISIBLE_ITEMS = List.of(
            id("create", "refined_radiance"),
            id("create", "refined_radiance_casing"),
            id("createcasing", "refined_radiance_press"),
            id("createcasing", "refined_radiance_deployer"),
            id("createcasing", "refined_radiance_mixer"),
            id("createcasing", "refined_radiance_encased_fan"),
            id("createcasing", "refined_radiance_mechanical_saw"),
            id("createcasing", "refined_radiance_mechanical_drill"),
            id("createcasing", "refined_radiance_mechanical_roller"),
            id("createcasing", "refined_radiance_depot"),
            id("createcasing", "refined_radiance_chain_conveyor"),
            id("createcasing", "refined_radiance_gearbox"),
            id("createcasing", "refined_radiance_clutch"),
            id("createcasing", "refined_radiance_automatic_clutch"),
            id("createcasing", "refined_radiance_configurable_gearbox"),
            id("createcasing", "refined_radiance_adjustable_chain_gearshift"),
            id("createcasing", "refined_radiance_gearshift"),
            id("createcasing", "refined_radiance_encased_chain_drive"),
            id("createcasing", "refined_radiance_portable_storage_interface"),
            id("createcasing", "refined_radiance_mechanical_harvester"),
            id("createcasing", "refined_radiance_mechanical_plough")
    );

    private RefinedRadianceVisibility() {
    }

    public static void register(IEventBus modEventBus) {
        modEventBus.addListener(RefinedRadianceVisibility::addToCreateTab);
    }

    public static List<ItemStack> itemStacks() {
        List<ItemStack> stacks = new ArrayList<>(VISIBLE_ITEMS.size());
        for (ResourceLocation itemId : VISIBLE_ITEMS) {
            Item item = BuiltInRegistries.ITEM.get(itemId);
            if (item != Items.AIR) {
                stacks.add(new ItemStack(item));
            }
        }
        return List.copyOf(stacks);
    }

    private static void addToCreateTab(BuildCreativeModeTabContentsEvent event) {
        if (!event.getTabKey().equals(AllCreativeModeTabs.BASE_CREATIVE_TAB.getKey())) {
            return;
        }
        for (ItemStack stack : itemStacks()) {
            event.accept(stack, CreativeModeTab.TabVisibility.PARENT_AND_SEARCH_TABS);
        }
    }

    private static ResourceLocation id(String namespace, String path) {
        return ResourceLocation.fromNamespaceAndPath(namespace, path);
    }
}
