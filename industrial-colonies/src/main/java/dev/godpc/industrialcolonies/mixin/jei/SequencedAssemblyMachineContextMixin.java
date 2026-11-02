package dev.godpc.industrialcolonies.mixin.jei;

import com.simibubi.create.compat.jei.category.sequencedAssembly.SequencedAssemblySubCategory;
import com.simibubi.create.content.processing.sequenced.SequencedRecipe;
import dev.godpc.industrialcolonies.client.jei.JeiMachineVisualContext;
import net.minecraft.client.gui.GuiGraphics;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Renders the selected Press, Deployer, Saw, or Spout for machine-bound inner
 * Sequenced Assembly steps. Native inner steps have no binding and stay
 * generic.
 */
@Mixin(targets = {
        "com.simibubi.create.compat.jei.category.sequencedAssembly.SequencedAssemblySubCategory$AssemblyPressing",
        "com.simibubi.create.compat.jei.category.sequencedAssembly.SequencedAssemblySubCategory$AssemblyDeploying",
        "com.simibubi.create.compat.jei.category.sequencedAssembly.SequencedAssemblySubCategory$AssemblyCutting",
        "com.simibubi.create.compat.jei.category.sequencedAssembly.SequencedAssemblySubCategory$AssemblySpouting"
}, remap = false)
public abstract class SequencedAssemblyMachineContextMixin extends SequencedAssemblySubCategory {
    protected SequencedAssemblyMachineContextMixin(int width) {
        super(width);
    }

    @Inject(method = "draw", at = @At("HEAD"))
    private void industrialColonies$beginStepMachine(
            SequencedRecipe<?> recipe,
            GuiGraphics graphics,
            double mouseX,
            double mouseY,
            int index,
            CallbackInfo ci
    ) {
        JeiMachineVisualContext.push(recipe.getRecipe());
    }

    @Inject(method = "draw", at = @At("RETURN"))
    private void industrialColonies$endStepMachine(
            SequencedRecipe<?> recipe,
            GuiGraphics graphics,
            double mouseX,
            double mouseY,
            int index,
            CallbackInfo ci
    ) {
        JeiMachineVisualContext.pop();
    }
}
