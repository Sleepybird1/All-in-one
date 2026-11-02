package dev.godpc.industrialcolonies.mixin;

import com.drmangotea.tfmg.recipes.PolarizingRecipe;
import com.drmangotea.tfmg.content.electricity.utilities.polarizer.PolarizerBlockEntity;
import dev.godpc.industrialcolonies.AtmPolarizingPolicy;
import dev.godpc.industrialcolonies.AtmPolarizingRuntime;
import dev.godpc.industrialcolonies.PolarizingChargeState;
import dev.godpc.industrialcolonies.MachineRecipeStageGate;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.core.HolderLookup;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.Optional;

/** Filters the TFMG Polarizer's direct holder lookup before its capacitor can run. */
@Mixin(
        targets = "com.drmangotea.tfmg.content.electricity.utilities.polarizer.PolarizerBlockEntity",
        remap = false
)
public abstract class TFMGPolarizerBlockEntityMixin {
    @Unique private final PolarizingChargeState industrialColonies$charge = new PolarizingChargeState();
    @Unique private RecipeHolder<PolarizingRecipe> industrialColonies$cachedRecipe;
    @Unique private ItemStack industrialColonies$cachedInput = ItemStack.EMPTY;
    @Unique private String industrialColonies$cachedBinding;

    @Unique private String industrialColonies$binding(PolarizerBlockEntity machine, RecipeHolder<PolarizingRecipe> holder) {
        ItemStack input = machine.inventory.getStackInSlot(0);
        if (industrialColonies$cachedRecipe == null || industrialColonies$cachedRecipe.value() != holder.value()
                || !industrialColonies$cachedRecipe.id().equals(holder.id())
                || !ItemStack.isSameItemSameComponents(input, industrialColonies$cachedInput)
                || input.getCount() != industrialColonies$cachedInput.getCount()) {
            industrialColonies$cachedRecipe = holder; industrialColonies$cachedInput = input.copy();
            industrialColonies$cachedBinding = AtmPolarizingRuntime.binding(machine, holder, input);
        }
        return industrialColonies$cachedBinding;
    }
    @Unique private Optional<RecipeHolder<PolarizingRecipe>> industrialColonies$selected(PolarizerBlockEntity machine) {
        if (machine.getLevel() == null) return Optional.empty();
        ItemStack input = machine.inventory.getStackInSlot(0);
        return machine.getRecipe(input).filter(holder -> AtmPolarizingRuntime.applies(input, holder.value()));
    }
    @Unique private void industrialColonies$reset(PolarizerBlockEntity machine) {
        if (!industrialColonies$charge.binding().isEmpty()) {
            industrialColonies$charge.clear(); machine.capacitorPercentage = 0; machine.setChanged();
        }
        industrialColonies$cachedRecipe = null; industrialColonies$cachedBinding = null;
        industrialColonies$cachedInput = ItemStack.EMPTY;
    }

    /** Draw the required real native load below the unchanged native 1000V safety ceiling. */
    @Inject(method = "resistance", at = @At("RETURN"), cancellable = true)
    private void industrialColonies$atmLoad(CallbackInfoReturnable<Float> callback) {
        var machine = (PolarizerBlockEntity) (Object) this;
        if (!machine.chargeCapacitors || machine.inventory == null) return;
        try {
            var holder = industrialColonies$selected(machine);
            if (holder.isPresent() && AtmPolarizingRuntime.validShape(machine.inventory.getStackInSlot(0), holder.get().value()))
                callback.setReturnValue(AtmPolarizingPolicy.resistanceForPower(AtmPolarizingRuntime.powerRequired(holder.get().value())));
        } catch (RuntimeException | LinkageError unavailable) { /* Preserve native resistance and hold work. */ }
    }

    /** Preserve native electrical updates, then replace only ATM's fixed 200-tick server cycle. */
    @Inject(method = "tick", at = @At(value = "INVOKE", target = "Lcom/drmangotea/tfmg/content/electricity/base/ElectricBlockEntity;tick()V", shift = At.Shift.AFTER), cancellable = true)
    private void industrialColonies$paidAtmCycle(CallbackInfo callback) {
        var machine = (PolarizerBlockEntity) (Object) this;
        if (machine.getLevel() == null || machine.getLevel().isClientSide) return;
        var selected = industrialColonies$selected(machine);
        if (selected.isEmpty()) { industrialColonies$reset(machine); return; }
        callback.cancel();
        try {
            var holder = selected.get();
            if (!AtmPolarizingRuntime.validShape(machine.inventory.getStackInSlot(0), holder.value())) {
                industrialColonies$reset(machine); machine.capacitorPercentage = 0;
                if (machine.chargeCapacitors) { machine.chargeCapacitors = false; machine.updateNextTick(); }
                return;
            }
            String key = industrialColonies$binding(machine, holder);
            int required = AtmPolarizingRuntime.requiredTicks(holder.value());
            industrialColonies$charge.bind(key, required);
            if (!machine.chargeCapacitors) { machine.chargeCapacitors = true; machine.updateNextTick(); }
            boolean supplied = AtmPolarizingRuntime.supplied(machine, AtmPolarizingRuntime.powerRequired(holder.value()));
            boolean credited = industrialColonies$charge.credit(key, required, machine.getLevel().getGameTime(), supplied);
            machine.capacitorPercentage = industrialColonies$charge.displayedCharge();
            if (credited) {
                machine.setChanged();
                if (industrialColonies$charge.paid() % 20 == 0) machine.sendData();
            }
            if (industrialColonies$charge.ready(key, required, supplied)) machine.performRecipe(holder.value());
        } catch (RuntimeException | LinkageError invalidRecipe) {
            industrialColonies$reset(machine); machine.capacitorPercentage = 0;
        }
    }

    /** An inventory callback can call performRecipe directly; a stock cached charge must never pay ATM work. */
    @Inject(method = "onInventoryChanged", at = @At("HEAD"))
    private void industrialColonies$bindInput(int slot, CallbackInfo callback) {
        var machine = (PolarizerBlockEntity) (Object) this;
        if (machine.getLevel() == null || machine.getLevel().isClientSide) return;
        try {
            var holder = industrialColonies$selected(machine);
            if (holder.isEmpty()) { industrialColonies$reset(machine); return; }
            if (!AtmPolarizingRuntime.validShape(machine.inventory.getStackInSlot(0), holder.get().value())) {
                industrialColonies$reset(machine); machine.capacitorPercentage = 0; return;
            }
            industrialColonies$charge.bind(industrialColonies$binding(machine, holder.get()),
                AtmPolarizingRuntime.requiredTicks(holder.get().value()));
            machine.capacitorPercentage = industrialColonies$charge.displayedCharge();
        } catch (RuntimeException | LinkageError invalidRecipe) { industrialColonies$reset(machine); machine.capacitorPercentage = 0; }
    }

    @Inject(method = "performRecipe", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$completionGuard(PolarizingRecipe recipe, CallbackInfo callback) {
        var machine = (PolarizerBlockEntity) (Object) this;
        if (!AtmPolarizingRuntime.applies(machine.inventory.getStackInSlot(0), recipe)) return;
        if (!AtmPolarizingRuntime.validShape(machine.inventory.getStackInSlot(0), recipe)) { callback.cancel(); return; }
        try {
            var holder = industrialColonies$selected(machine);
            if (machine.getLevel() == null || machine.getLevel().isClientSide || holder.isEmpty()
                || holder.get().value() != recipe
                || !industrialColonies$charge.ready(industrialColonies$binding(machine, holder.get()),
                    AtmPolarizingRuntime.requiredTicks(recipe), AtmPolarizingRuntime.supplied(machine, AtmPolarizingRuntime.powerRequired(recipe)))) callback.cancel();
        } catch (RuntimeException | LinkageError invalidRecipe) { callback.cancel(); }
    }

    @Inject(method = "write", at = @At("TAIL"))
    private void industrialColonies$saveCharge(CompoundTag tag, HolderLookup.Provider registries, boolean packet, CallbackInfo callback) {
        CompoundTag progress = new CompoundTag();
        progress.putString("binding", industrialColonies$charge.binding());
        progress.putInt("required", industrialColonies$charge.required()); progress.putInt("paid", industrialColonies$charge.paid());
        progress.putLong("lastTick", industrialColonies$charge.lastTick()); tag.put("ICAtmPolarizing", progress);
    }
    @Inject(method = "read", at = @At("TAIL"))
    private void industrialColonies$loadCharge(CompoundTag tag, HolderLookup.Provider registries, boolean packet, CallbackInfo callback) {
        CompoundTag progress = tag.getCompound("ICAtmPolarizing");
        industrialColonies$charge.restore(progress.getString("binding"), progress.getInt("required"), progress.getInt("paid"), progress.getLong("lastTick"));
        industrialColonies$cachedRecipe = null; industrialColonies$cachedBinding = null; industrialColonies$cachedInput = ItemStack.EMPTY;
    }

    @Inject(method = "getRecipe", at = @At("RETURN"), cancellable = true, remap = false)
    private void industrialColonies$denyLockedPolarizingRecipe(
            ItemStack input,
            CallbackInfoReturnable<Optional<RecipeHolder<PolarizingRecipe>>> callback
    ) {
        Optional<RecipeHolder<PolarizingRecipe>> recipe = callback.getReturnValue();
        BlockEntity machine = (BlockEntity) (Object) this;
        if (recipe != null && recipe.isPresent()
                && !MachineRecipeStageGate.canUse(machine, recipe.get())) {
            callback.setReturnValue(Optional.empty());
        }
    }
}
