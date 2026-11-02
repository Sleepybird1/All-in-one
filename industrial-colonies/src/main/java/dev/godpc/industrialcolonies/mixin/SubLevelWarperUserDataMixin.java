package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.llamalad7.mixinextras.sugar.Local;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import dev.ryanhcode.sable.sublevel.SubLevel;
import net.minecraft.nbt.CompoundTag;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;

/** Preserves every mod's Sable user-data root when Cosmonautics reallocates a ship. */
@Pseudo
@Mixin(targets = "dev.egg.SubLevelWarper", remap = false)
public abstract class SubLevelWarperUserDataMixin {
    @ModifyExpressionValue(
            method = "WarpSubLevels(Ljava/util/Collection;Ldev/ryanhcode/sable/api/sublevel/ServerSubLevelContainer;Ldev/ryanhcode/sable/api/sublevel/ServerSubLevelContainer;Lorg/joml/Vector3d;Lorg/joml/Vector3d;)V",
            at = @At(
                    value = "INVOKE",
                    target = "Ldev/ryanhcode/sable/api/sublevel/ServerSubLevelContainer;allocateNewSubLevel(Ldev/ryanhcode/sable/companion/math/Pose3d;)Ldev/ryanhcode/sable/sublevel/SubLevel;"),
            require = 1)
    private static SubLevel industrialColonies$copyWholeUserDataRoot(
            SubLevel allocated,
            @Local(name = "serverSubLevel") ServerSubLevel source
    ) {
        if (allocated instanceof ServerSubLevel destination) {
            CompoundTag sourceData = source.getUserDataTag();
            if (sourceData != null) {
                destination.setUserDataTag(sourceData.copy());
            }
        }
        return allocated;
    }
}
