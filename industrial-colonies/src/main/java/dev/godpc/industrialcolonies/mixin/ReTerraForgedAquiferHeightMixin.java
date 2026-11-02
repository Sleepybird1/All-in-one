package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.geology.ReTerraForgedAquiferCompatibility;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.Aquifer;
import net.minecraft.world.level.levelgen.NoiseChunk;
import net.minecraft.world.level.levelgen.NoiseRouter;
import net.minecraft.world.level.levelgen.NoiseSettings;
import net.minecraft.world.level.levelgen.PositionalRandomFactory;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/**
 * Terrain-height culling cannot bound later cave-carver queries. Preserve the
 * original noise-settings range for aquifer caches while retaining terrain culling.
 */
@Mixin(targets = "net.minecraft.world.level.levelgen.Aquifer$NoiseBasedAquifer")
public abstract class ReTerraForgedAquiferHeightMixin {
    @ModifyVariable(method = "<init>", at = @At("HEAD"), argsOnly = true, ordinal = 1)
    private static int industrialColonies$restoreAquiferCoverage(int suppliedHeight, NoiseChunk chunk, ChunkPos pos,
            NoiseRouter router, PositionalRandomFactory random, int minY, int height, Aquifer.FluidPicker fluids) {
        if (!ReTerraForgedAquiferCompatibility.isAffectedBuild()) return suppliedHeight;
        NoiseSettings settings = ((NoiseChunkSettingsAccessor) (Object) chunk).industrialColonies$noiseSettings();
        if (settings.minY() != minY || suppliedHeight >= settings.height()) return suppliedHeight;
        return settings.height();
    }
}
