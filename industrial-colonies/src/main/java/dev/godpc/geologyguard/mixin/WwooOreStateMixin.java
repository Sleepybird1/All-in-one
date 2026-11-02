package dev.godpc.geologyguard.mixin;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import dev.godpc.geologyguard.WwooOrePolicy;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.OreFeature;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(OreFeature.class)
public abstract class WwooOreStateMixin {
    @ModifyExpressionValue(method = "doPlace", at = @At(value = "FIELD", target =
        "Lnet/minecraft/world/level/levelgen/feature/configurations/OreConfiguration$TargetBlockState;state:Lnet/minecraft/world/level/block/state/BlockState;"), require = 1)
    private BlockState industrialColonies$oreState(BlockState original) {
        return WwooOrePolicy.replace(original);
    }
}
