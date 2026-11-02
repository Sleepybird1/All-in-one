package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import dev.godpc.industrialcolonies.processing.PotionIdentityRuntime;
import io.redspace.ironsspellbooks.block.alchemist_cauldron.AlchemistCauldronTile.AlchemistCauldronFluidHandler;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler.FluidAction;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;

/** Only native brew-batch call sites: storage, fill and external drain stay native. */
@Pseudo
@Mixin(targets="io.redspace.ironsspellbooks.block.alchemist_cauldron.AlchemistCauldronTile",remap=false)
public abstract class SpellbooksCauldronBatchMixin {
    @ModifyArg(method="tryMeltInput",at=@At(value="INVOKE",target="Lio/redspace/ironsspellbooks/recipe_types/alchemist_cauldron/BrewAlchemistCauldronRecipe$Input;<init>(Lnet/neoforged/neoforge/fluids/FluidStack;Lnet/minecraft/world/item/ItemStack;)V"),index=0,require=1)
    private FluidStack industrialColonies$lookup(FluidStack original) {
        return PotionIdentityRuntime.produced(original);
    }

    @WrapOperation(method="tryMeltInput",at=@At(value="INVOKE",target="Lio/redspace/ironsspellbooks/block/alchemist_cauldron/AlchemistCauldronTile$AlchemistCauldronFluidHandler;contains(Lnet/neoforged/neoforge/fluids/FluidStack;I)Z"),require=1)
    private boolean industrialColonies$contains(AlchemistCauldronFluidHandler handler,FluidStack query,int amount,Operation<Boolean> original) {
        return original.call(handler,PotionIdentityRuntime.storedQuery(handler,query,amount),amount);
    }

    // Ordinal 0 drains scroll recycling water; ordinal 1 is the reviewed brew batch.
    @WrapOperation(method="tryMeltInput",at=@At(value="INVOKE",target="Lio/redspace/ironsspellbooks/block/alchemist_cauldron/AlchemistCauldronTile$AlchemistCauldronFluidHandler;drain(Lnet/neoforged/neoforge/fluids/FluidStack;Lnet/neoforged/neoforge/fluids/capability/IFluidHandler$FluidAction;)Lnet/neoforged/neoforge/fluids/FluidStack;",ordinal=1),require=1)
    private FluidStack industrialColonies$drain(AlchemistCauldronFluidHandler handler,FluidStack query,FluidAction action,Operation<FluidStack> original) {
        return original.call(handler,PotionIdentityRuntime.storedQuery(handler,query,query.getAmount()),action);
    }
}
