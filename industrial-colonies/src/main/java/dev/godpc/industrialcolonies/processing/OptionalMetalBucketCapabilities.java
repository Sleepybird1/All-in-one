package dev.godpc.industrialcolonies.processing;

import java.util.Set;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.BucketItem;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.capabilities.RegisterCapabilitiesEvent;
import net.neoforged.neoforge.fluids.capability.wrappers.FluidBucketWrapper;

/** Restore ordinary bucket transport for the inspected optional-metal bucket subclass. */
public final class OptionalMetalBucketCapabilities {
    private static final Set<String> METALS = Set.of("aluminum", "bronze", "constantan",
            "electrum", "invar", "lead", "lithium", "nickel", "osmium", "silver", "tin");
    private static final String CLASS_NAME =
            "fr.lucreeper74.createmetallurgy.content.fluids.TagDependentBucketItem";
    private OptionalMetalBucketCapabilities() {}
    public static void register(IEventBus bus) {
        bus.addListener(EventPriority.LOWEST, OptionalMetalBucketCapabilities::capabilities);
    }
    private static void capabilities(RegisterCapabilitiesEvent event) {
        for (String metal : METALS) {
            var fluidId = ResourceLocation.fromNamespaceAndPath("createmetallurgy", "molten_" + metal);
            var itemId = ResourceLocation.fromNamespaceAndPath("createmetallurgy", "molten_" + metal + "_bucket");
            if (!BuiltInRegistries.ITEM.containsKey(itemId) || !BuiltInRegistries.FLUID.containsKey(fluidId)) continue;
            var item = BuiltInRegistries.ITEM.get(itemId);
            var fluid = BuiltInRegistries.FLUID.get(fluidId);
            // Never claim component-bearing containers, unknown subclasses or a future native provider.
            if (!(item instanceof BucketItem bucket) || !item.getClass().getName().equals(CLASS_NAME)
                    || bucket.content != fluid || fluid.getBucket() != item
                    || event.isItemRegistered(Capabilities.FluidHandler.ITEM, item)) continue;
            event.registerItem(Capabilities.FluidHandler.ITEM,
                    (stack, context) -> new FluidBucketWrapper(stack), item);
        }
    }
}
