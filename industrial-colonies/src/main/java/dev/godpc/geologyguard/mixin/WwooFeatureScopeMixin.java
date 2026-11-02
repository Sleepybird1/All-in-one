package dev.godpc.geologyguard.mixin;

import com.llamalad7.mixinextras.injector.wrapmethod.WrapMethod;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import dev.godpc.geologyguard.WwooOrePolicy;
import dev.godpc.industrialcolonies.geology.GeologyConfig;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.placement.PlacedFeature;
import org.spongepowered.asm.mixin.Mixin;

@Mixin(PlacedFeature.class)
public abstract class WwooFeatureScopeMixin {
    @WrapMethod(method = {"place", "placeWithBiomeCheck"})
    private boolean industrialColonies$oreScope(WorldGenLevel level, ChunkGenerator generator,
            RandomSource random, BlockPos pos, Operation<Boolean> original) {
        var previous = WwooOrePolicy.scope();
        var id = level.registryAccess().registryOrThrow(Registries.PLACED_FEATURE).getKey((PlacedFeature)(Object)this);
        var selected = WwooOrePolicy.scopeFor(id, level.getLevel().dimension(), GeologyConfig.suppressDefaultOres());
        WwooOrePolicy.restore(selected != null ? selected : previous);
        try { return original.call(level, generator, random, pos); }
        finally { WwooOrePolicy.restore(previous); }
    }
}
