package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.worldgen.MountainSurface;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.ChunkGenerator;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(ChunkGenerator.class)
public abstract class MountainSurfaceMixin {
    @Inject(method="applyBiomeDecoration",at=@At("RETURN"))
    private void industrialColonies$finishMountainSurface(WorldGenLevel level,ChunkAccess chunk,
            StructureManager structures,CallbackInfo ci) {
        if(level.getLevel().dimension().equals(Level.OVERWORLD))MountainSurface.finish(chunk);
    }
}
