package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.content.processing.basin.*;
import com.simibubi.create.content.kinetics.mixer.*;
import com.simibubi.create.content.kinetics.press.*;
import dev.godpc.industrialcolonies.CreateMachineContext;
import dev.godpc.industrialcolonies.CreateRecipeStageGate;
import dev.godpc.industrialcolonies.processing.AssemblyRuntime;
import net.minecraft.world.item.crafting.*;
import net.neoforged.neoforge.capabilities.Capabilities;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
import java.util.*;

@Mixin(BasinOperatingBlockEntity.class)
public abstract class BasinAssemblyLookupMixin {
    @Shadow protected abstract Optional<BasinBlockEntity> getBasin();
    @Shadow protected abstract <I extends RecipeInput> boolean matchBasinRecipe(Recipe<I> recipe);
    @Shadow protected Recipe<?> currentRecipe;
    @Inject(method="getMatchingRecipes",at=@At("RETURN"),cancellable=true)
    private void industrialColonies$assemblyRecipes(CallbackInfoReturnable<List<Recipe<?>>> ci) {
        var machine = (BasinOperatingBlockEntity)(Object)this;
        var level = machine.getLevel();
        var basin = getBasin();
        if (level == null || basin.isEmpty()) return;
        if (!(machine instanceof MechanicalMixerBlockEntity) && !(machine instanceof MechanicalPressBlockEntity)) return;
        var inventory = level.getCapability(Capabilities.ItemHandler.BLOCK, basin.get().getBlockPos(), null);
        if (inventory == null) return;
        var candidates = new ArrayList<Recipe<?>>();
        try (var scope = CreateMachineContext.enter(machine)) {
            for (int slot = 0; slot < inventory.getSlots(); slot++) {
                for (var match : AssemblyRuntime.matches(level, inventory.getStackInSlot(slot))) {
                    if (machine instanceof MechanicalMixerBlockEntity && !(match.step() instanceof MixingRecipe)) continue;
                    if (machine instanceof MechanicalPressBlockEntity && !(match.step() instanceof CompactingRecipe)) continue;
                    var prepared = AssemblyRuntime.prepareBasin(match, level);
                    if (matchBasinRecipe(prepared)) candidates.add(prepared);
                }
            }
        }
        candidates.addAll(ci.getReturnValue());
        ci.setReturnValue(candidates);
    }
    @Inject(method="applyBasinRecipe",at=@At("HEAD"),cancellable=true)
    private void industrialColonies$revalidateAssembly(CallbackInfo ci) {
        if (!(currentRecipe instanceof BasinRecipe basin) || AssemblyRuntime.basinMatch(basin) == null) return;
        var match=AssemblyRuntime.basinMatch(basin);
        var machine=(BasinOperatingBlockEntity)(Object)this;
        var level=machine.getLevel();
        if(level==null || !CreateRecipeStageGate.canUse(level,match.parent(),machine)
                || level.getRecipeManager().byKey(match.parent().id()).filter(h->h.value()==match.parent().value()).isEmpty()) {
            ci.cancel();return;
        }
        // Re-check inputs, exact progress, heat, output space and owner at the moment of consumption.
        if (!matchBasinRecipe(currentRecipe)) ci.cancel();
    }
}
