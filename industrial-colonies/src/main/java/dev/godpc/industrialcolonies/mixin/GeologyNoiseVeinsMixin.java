package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.geology.GeologyConfig;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.WorldGenRegion;
import net.minecraft.world.level.*;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.blending.Blender;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** Preserve Tectonic's terrain/surface/aquifers; disable only Overworld's hidden vanilla giant iron/copper ore veins. */
@Mixin(NoiseBasedChunkGenerator.class)
public abstract class GeologyNoiseVeinsMixin {
    @Redirect(method="createNoiseChunk",at=@At(value="INVOKE",target="Lnet/minecraft/world/level/levelgen/NoiseChunk;forChunk(Lnet/minecraft/world/level/chunk/ChunkAccess;Lnet/minecraft/world/level/levelgen/RandomState;Lnet/minecraft/world/level/levelgen/DensityFunctions$BeardifierOrMarker;Lnet/minecraft/world/level/levelgen/NoiseGeneratorSettings;Lnet/minecraft/world/level/levelgen/Aquifer$FluidPicker;Lnet/minecraft/world/level/levelgen/blending/Blender;)Lnet/minecraft/world/level/levelgen/NoiseChunk;"))
    private NoiseChunk industrialColonies$withoutDefaultVeins(ChunkAccess chunk,RandomState random,DensityFunctions.BeardifierOrMarker beardifier,
            NoiseGeneratorSettings settings,Aquifer.FluidPicker fluidPicker,Blender blender,
            ChunkAccess originalChunk,StructureManager structures,Blender originalBlender,RandomState originalRandom){
        LevelAccessor accessor=((GeologyStructureManagerAccessor)structures).industrialColonies$level();
        ServerLevel level=accessor instanceof ServerLevel server?server:accessor instanceof WorldGenRegion region?region.getLevel():null;
        if(level!=null&&level.dimension()==Level.OVERWORLD&&GeologyConfig.suppressDefaultOres()&&settings.oreVeinsEnabled()){
            settings=new NoiseGeneratorSettings(settings.noiseSettings(),settings.defaultBlock(),settings.defaultFluid(),settings.noiseRouter(),
                    settings.surfaceRule(),settings.spawnTarget(),settings.seaLevel(),settings.disableMobGeneration(),settings.isAquifersEnabled(),false,settings.useLegacyRandomSource());
        }
        return NoiseChunk.forChunk(chunk,random,beardifier,settings,fluidPicker,blender);
    }
}
