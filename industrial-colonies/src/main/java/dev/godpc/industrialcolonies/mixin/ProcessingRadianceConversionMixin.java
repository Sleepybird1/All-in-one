package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.content.legacy.ChromaticCompoundItem;
import com.simibubi.create.infrastructure.config.AllConfigs;
import net.createmod.catnip.config.ConfigBase;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** A thrown Chromatic Compound must not skip the new engineered Radiance chain. */
@Mixin(value = ChromaticCompoundItem.class, remap = false)
public abstract class ProcessingRadianceConversionMixin {
    @Redirect(method = "onEntityItemUpdate", at = @At(value = "INVOKE",
            target = "Lnet/createmod/catnip/config/ConfigBase$ConfigBool;get()Ljava/lang/Object;"), require = 2)
    private Object industrialColonies$engineeredRadianceOnly(ConfigBase.ConfigBool setting) {
        // Preserve the separate Shadow Steel switch; only the light/beacon shortcut is retired.
        return setting == AllConfigs.server().recipes.enableRefinedRadianceRecipe ? Boolean.FALSE : setting.get();
    }
}
