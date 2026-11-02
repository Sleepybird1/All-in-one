package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.geology.GeologyConfig;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.util.RandomSource;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.*;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.placement.PlacedFeature;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Retrogen/direct placement can bypass biome feature lists; apply the same Overworld-only suppression there. */
@Mixin(PlacedFeature.class)
public abstract class GeologyPlacedFeatureGuardMixin {
    private static final TagKey<PlacedFeature> IC_FORBIDDEN=TagKey.create(Registries.PLACED_FEATURE,ResourceLocation.fromNamespaceAndPath("industrial_colonies","geology/default_ore_features"));
    @Inject(method={"place","placeWithBiomeCheck"},at=@At("HEAD"),cancellable=true)
    private void industrialColonies$guard(WorldGenLevel level,ChunkGenerator generator,RandomSource random,BlockPos pos,CallbackInfoReturnable<Boolean> ci){
        if(level.getLevel().dimension()!=Level.OVERWORLD||!GeologyConfig.suppressDefaultOres())return;
        var registry=level.registryAccess().registryOrThrow(Registries.PLACED_FEATURE);
        registry.getResourceKey((PlacedFeature)(Object)this).flatMap(registry::getHolder).ifPresent(holder->{if(holder.is(IC_FORBIDDEN))ci.setReturnValue(false);});
    }
}
