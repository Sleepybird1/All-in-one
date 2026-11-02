package dev.godpc.geologyguard.mixin;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import dev.godpc.geologyguard.WwooOrePolicy;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.DiskFeature;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(DiskFeature.class)
public abstract class WwooDiskStateMixin {
    @ModifyExpressionValue(method = "placeColumn", at = @At(value = "INVOKE", target =
        "Lnet/minecraft/world/level/levelgen/feature/stateproviders/RuleBasedBlockStateProvider;getState(Lnet/minecraft/world/level/WorldGenLevel;Lnet/minecraft/util/RandomSource;Lnet/minecraft/core/BlockPos;)Lnet/minecraft/world/level/block/state/BlockState;"), require = 1)
    private BlockState industrialColonies$oreState(BlockState original) {
        return WwooOrePolicy.replace(original);
    }
}
