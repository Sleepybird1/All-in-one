package dev.godpc.industrialcolonies.mixin;

import net.minecraft.world.level.levelgen.NoiseChunk;
import net.minecraft.world.level.levelgen.NoiseSettings;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

@Mixin(NoiseChunk.class)
public interface NoiseChunkSettingsAccessor {
    @Accessor("noiseSettings")
    NoiseSettings industrialColonies$noiseSettings();
}
