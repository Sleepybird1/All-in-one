package dev.godpc.industrialcolonies.mixin.jei;

import mezz.jei.api.helpers.IPlatformFluidHelper;
import mezz.jei.api.registration.ISubtypeRegistration;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Overwrite;
import org.spongepowered.asm.mixin.Pseudo;

/** Create owns its potion-fluid subtype registration; TFMG 1.2.0 duplicates it exactly. */
@Pseudo
@Mixin(targets = "com.drmangotea.tfmg.recipes.jei.TFMGJei", remap = false)
public abstract class TFMGPotionSubtypeMixin {
    /**
     * @author Industrial Colonies
     * @reason Retain Create's identical native source/flowing potion interpreters
     * without TFMG registering them a second time. The audited TFMG method has
     * no TFMG-owned fluids or other side effects; re-audit it before upgrading.
     */
    @Overwrite(remap = false)
    public <T> void registerFluidSubtypes(ISubtypeRegistration registration,
                                         IPlatformFluidHelper<T> fluidHelper) {
        // Create's own JEI plugin registers both fluids, independently of plugin order.
    }
}
