package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import dev.godpc.industrialcolonies.geology.VeinMinePlacement;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

/** Only the biome veto changes; native liquid-boundary checks still run unchanged. */
@Mixin(targets="net.minecraft.world.level.levelgen.structure.structures.MineshaftPieces$MineShaftPiece")
public abstract class VeinMineBiomeAdmissionMixin {
    @ModifyExpressionValue(method="isInInvalidLocation",at=@At(value="INVOKE",target="Lnet/minecraft/core/Holder;is(Lnet/minecraft/tags/TagKey;)Z"),require=1)
    private boolean industrialColonies$allowLinkedDeepDarkMine(boolean blocked) {
        return blocked&&!VeinMinePlacement.linked();
    }
}
