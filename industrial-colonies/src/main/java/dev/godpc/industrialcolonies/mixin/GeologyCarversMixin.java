package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.geology.GeologyFeature;
import dev.godpc.industrialcolonies.geology.GeologyConfig;
import dev.godpc.industrialcolonies.geology.MiningOreOwnership;
import dev.godpc.industrialcolonies.geology.MassiveDeposits;
import net.minecraft.server.level.WorldGenRegion;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.biome.BiomeManager;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.levelgen.GenerationStep;
import net.minecraft.world.level.levelgen.NoiseBasedChunkGenerator;
import net.minecraft.world.level.levelgen.RandomState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** FEATURES requires CARVERS throughout its write radius, making this a real cross-chunk phase barrier. */
@Mixin(NoiseBasedChunkGenerator.class)
public abstract class GeologyCarversMixin {
    @Inject(method="applyCarvers",at=@At("TAIL"))
    private void industrialColonies$placeGeologyAfterCarvers(WorldGenRegion level,long seed,RandomState random,
            BiomeManager biomeManager,StructureManager structureManager,ChunkAccess chunk,GenerationStep.Carving step,CallbackInfo ci){
        if(GeologyConfig.enabled()&&step==GenerationStep.Carving.AIR&&level.getLevel().dimension()==Level.OVERWORLD&&!chunk.isUpgrading()){
            boolean opened=MassiveDeposits.enabled(GeologyConfig.get())&&MiningOreOwnership.begin(chunk);
            try{GeologyFeature.generateDeposits(level,chunk.getPos());if(opened)MiningOreOwnership.seal(chunk);}
            catch(RuntimeException|Error failure){if(opened)MiningOreOwnership.abort(chunk);throw failure;}
        }
    }
}
