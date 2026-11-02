package dev.godpc.industrialcolonies.mixin.jei;

import com.george_vi.electroenergetics.CEEBlocks;
import mezz.jei.api.registration.IIngredientAliasRegistration;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Overwrite;
import org.spongepowered.asm.mixin.Pseudo;

/** Optional compatibility for the installed ElectroEnergetics 1.1.1 / JEI 19.51 pair. */
@Pseudo
@Mixin(targets = "com.george_vi.electroenergetics.compat.CEEJEI", remap = false)
public abstract class ElectroEnergeticsJeiAliasesMixin {
    /**
     * @author Industrial Colonies
     * @reason Keep the original aliases through JEI's public ItemStack overload;
     * the addon's private TypedItemStack dependency no longer exists in JEI 19.51.
     */
    @Overwrite(remap = false)
    public void registerIngredientAliases(IIngredientAliasRegistration registration) {
        registration.addAlias(CEEBlocks.SF6_BREAKER.asStack(), "sf6");
        registration.addAlias(CEEBlocks.HV_SWITCH.asStack(), "hv switch");
        registration.addAlias(CEEBlocks.HV_CAPACITOR.asStack(), "hv capacitor");
        registration.addAlias(CEEBlocks.ALTERNATOR_ROTOR.asStack(), "generator");
        registration.addAlias(CEEBlocks.STATOR.asStack(), "generator");
        registration.addAlias(CEEBlocks.ALTERNATOR_BRUSHES.asStack(), "generator");
        registration.addAlias(CEEBlocks.THREE_PHASE_ALTERNATOR_BRUSHES.asStack(), "generator");
        // Preserve the addon's repeated registration; this patch changes only its API dependency.
        registration.addAlias(CEEBlocks.THREE_PHASE_ALTERNATOR_BRUSHES.asStack(), "generator");
    }
}
