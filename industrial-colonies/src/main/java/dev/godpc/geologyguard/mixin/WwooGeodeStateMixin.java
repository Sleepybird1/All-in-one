package dev.godpc.geologyguard.mixin;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import dev.godpc.geologyguard.WwooOrePolicy;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.GeodeFeature;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(GeodeFeature.class)
public abstract class WwooGeodeStateMixin {
    @ModifyExpressionValue(method = "place", at = @At(value = "INVOKE", target =
        "Lnet/minecraft/world/level/levelgen/feature/stateproviders/BlockStateProvider;getState(Lnet/minecraft/util/RandomSource;Lnet/minecraft/core/BlockPos;)Lnet/minecraft/world/level/block/state/BlockState;"), require = 5, allow = 5)
    private BlockState industrialColonies$oreState(BlockState original) {
        return WwooOrePolicy.replace(original);
    }
}
