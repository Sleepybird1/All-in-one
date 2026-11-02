package dev.godpc.industrialcolonies.mixin;

import java.util.function.Predicate;
import dev.godpc.industrialcolonies.worldgen.SurfaceStructureTerrain;
import dev.godpc.industrialcolonies.geology.LightningDragonNativeGate;
import dev.godpc.industrialcolonies.geology.WorldStartStructureSpacing;
import net.minecraft.core.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.biome.*;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplateManager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(Structure.class)
public abstract class SurfaceStructureTerrainMixin {
    @Inject(method="generate",at=@At("HEAD"),cancellable=true)
    private void industrialColonies$lightningContinentGate(RegistryAccess access,ChunkGenerator generator,
            BiomeSource biomes,RandomState random,StructureTemplateManager templates,long seed,
            ChunkPos chunk,int references,LevelHeightAccessor height,Predicate<Holder<Biome>> validBiome,
            CallbackInfoReturnable<StructureStart> cir) {
        if(!WorldStartStructureSpacing.allows((Structure)(Object)this,random,chunk)
                ||!LightningDragonNativeGate.allows((Structure)(Object)this,access,random,chunk))
            cir.setReturnValue(StructureStart.INVALID_START);
    }
    @Inject(method="generate",at=@At("RETURN"),cancellable=true)
    private void industrialColonies$requireDryLevelSite(RegistryAccess access,ChunkGenerator generator,
            BiomeSource biomes,RandomState random,StructureTemplateManager templates,long seed,
            ChunkPos chunk,int references,LevelHeightAccessor height,Predicate<Holder<Biome>> validBiome,
            CallbackInfoReturnable<StructureStart> cir) {
        var start=cir.getReturnValue();
        if(start.isValid()&&SurfaceStructureTerrain.shouldCheck((Structure)(Object)this,access)
                &&(!SurfaceStructureTerrain.fits(start,generator,random,height)
                ||!SurfaceStructureTerrain.summitFits(start,access,generator,random,height)))cir.setReturnValue(StructureStart.INVALID_START);
    }
}
