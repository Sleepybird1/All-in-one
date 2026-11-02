package dev.godpc.industrialcolonies.mixin;

import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.fluids.capability.IFluidHandlerItem;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** A completed drink pays its full native food cost, even above the tank transfer rate. */
@Pseudo
@Mixin(targets = "mekanism.common.item.gear.ItemCanteen", remap = false)
public abstract class MekanismCanteenConsumptionMixin {
    @Redirect(method = "finishUsingItem", at = @At(value = "INVOKE", target =
            "Lnet/neoforged/neoforge/fluids/capability/IFluidHandlerItem;drain(ILnet/neoforged/neoforge/fluids/capability/IFluidHandler$FluidAction;)Lnet/neoforged/neoforge/fluids/FluidStack;"), require = 1)
    private FluidStack industrialColonies$consumeWholeDrink(IFluidHandlerItem handler, int amount,
                                                           IFluidHandler.FluidAction action) {
        // Only this completed drink bypasses per-call transfer limits. Filling and pipes stay native.
        if (action.simulate()) return handler.drain(amount, action);
        FluidStack consumed = FluidStack.EMPTY;
        int remaining = amount;
        while (remaining > 0) {
            FluidStack part = handler.drain(remaining, action);
            if (part.isEmpty()) break;
            if (consumed.isEmpty()) consumed = part.copy();
            else consumed.grow(part.getAmount());
            remaining -= part.getAmount();
        }
        return consumed;
    }
}
