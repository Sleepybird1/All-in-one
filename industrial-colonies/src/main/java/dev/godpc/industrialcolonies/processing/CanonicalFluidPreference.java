package dev.godpc.industrialcolonies.processing;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.material.Fluid;

/** Exact approved fluid output choices, never a tag-membership or recipe mutation. */
public final class CanonicalFluidPreference {
    private CanonicalFluidPreference() {}
    public static Fluid select(TagKey<?> tag) {
        if (!tag.registry().equals(Registries.FLUID)) return null;
        String target = switch (tag.location().toString()) {
            case "c:molten_steel" -> "tfmg:molten_steel";
            case "c:sulfuric_acid" -> "tfmg:sulfuric_acid";
            default -> null;
        };
        if (target == null) return null;
        var id = ResourceLocation.parse(target);
        if (!BuiltInRegistries.FLUID.containsKey(id)) return null;
        Fluid fluid = BuiltInRegistries.FLUID.get(id);
        // A missing or deliberately restricted tag retains Hilt's own behavior.
        return fluid.builtInRegistryHolder().is(TagKey.create(Registries.FLUID, tag.location())) ? fluid : null;
    }
}
