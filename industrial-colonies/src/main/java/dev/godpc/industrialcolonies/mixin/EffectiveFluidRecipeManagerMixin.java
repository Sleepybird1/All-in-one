package dev.godpc.industrialcolonies.mixin;

import com.google.common.collect.ImmutableMultimap;
import dev.godpc.industrialcolonies.processing.EffectiveFluidNormalizer;
import dev.godpc.industrialcolonies.processing.Co2FlowingNormalizer;
import java.util.Map;
import net.minecraft.core.HolderLookup;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.crafting.*;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Normalize the parsed effective map after scripts/conditions have run. */
@Mixin(value = RecipeManager.class, priority = 900)
public abstract class EffectiveFluidRecipeManagerMixin {
    @Shadow @Final private HolderLookup.Provider registries;
    @Shadow private Map<ResourceLocation, RecipeHolder<?>> byName;
    @Shadow private com.google.common.collect.Multimap<RecipeType<?>, RecipeHolder<?>> byType;

    @Inject(method = {"apply(Ljava/util/Map;Lnet/minecraft/server/packs/resources/ResourceManager;Lnet/minecraft/util/profiling/ProfilerFiller;)V", "replaceRecipes"}, at = @At("RETURN"))
    private void industrialColonies$normalizeEffectiveFluids(CallbackInfo ci) {
        var result = EffectiveFluidNormalizer.apply((RecipeManager)(Object)this, byName, registries);
        var recipes = result.recipes();
        int changed = result.changed();
        // Explicit order: CO2 depends on the existing oxygen/hydrogen identity pass.
        if (Boolean.getBoolean("industrial_colonies.co2Flowing")) {
            var co2 = Co2FlowingNormalizer.normalize(recipes, registries);
            recipes = co2.recipes();
            changed += co2.changed();
            if (co2.held()) org.slf4j.LoggerFactory.getLogger(EffectiveFluidRecipeManagerMixin.class)
                .warn("CO2 source/flowing compatibility held: {}", co2.status());
        }
        if (changed == 0) return;
        var types = ImmutableMultimap.<RecipeType<?>, RecipeHolder<?>>builder();
        recipes.values().forEach(holder -> types.put(holder.value().getType(), holder));
        byName = recipes;
        byType = types.build();
    }
}
