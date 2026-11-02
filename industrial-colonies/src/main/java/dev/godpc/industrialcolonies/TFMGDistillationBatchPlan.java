package dev.godpc.industrialcolonies;

import com.drmangotea.tfmg.content.decoration.tanks.steel.SteelTankBlockEntity;
import com.drmangotea.tfmg.content.machinery.oil_processing.distillation_tower.controller.DistillationControllerBlock;
import com.drmangotea.tfmg.content.machinery.oil_processing.distillation_tower.controller.DistillationControllerBlockEntity;
import com.drmangotea.tfmg.content.machinery.oil_processing.distillation_tower.output.DistillationOutputBlockEntity.DistillationOutputMode;
import net.neoforged.neoforge.fluids.capability.IFluidHandler.FluidAction;
import java.util.ArrayList;
import net.neoforged.neoforge.fluids.FluidStack;

/** Commit one native heat-scaled batch after the tower's native structural checks. */
public final class TFMGDistillationBatchPlan {
    private TFMGDistillationBatchPlan() {}

    public static void complete(DistillationControllerBlockEntity controller) {
        var level = controller.getLevel();
        var recipe = controller.recipe;
        if (level == null || level.isClientSide || recipe == null) return;
        var back = DistillationControllerBlock.getFacing(controller.getBlockState()).getOpposite();
        if (!(level.getBlockEntity(controller.getBlockPos().relative(back)) instanceof SteelTankBlockEntity tower)
                || tower.activeHeat <= 0) return;
        var outputs = controller.getOutputs();
        if (outputs.size() != recipe.getFluidResults().size()
                || !recipe.getInputFluid().test(controller.tank.getFluid())) return;
        // Preserve native half-heat scaling and whole-mB truncation. Charge the
        // complete input once; dividing it by six loses remainder and undercharges
        // every recipe with fewer than six output ports.
        long scaledInput = (long) recipe.getInputFluid().amount() * tower.activeHeat / 2;
        if (scaledInput <= 0 || scaledInput > controller.tank.getFluidAmount()) return;
        var products = new ArrayList<FluidStack>();
        for (int i = 0; i < outputs.size(); i++) {
            var product = recipe.getFluidResults().get(i).copy();
            long amount = (long) product.getAmount() * tower.activeHeat / 2;
            if (amount > Integer.MAX_VALUE) return;
            product.setAmount((int) amount);
            var output = outputs.get(i);
            if (output.mode.get() == DistillationOutputMode.KEEP_FLUID
                    && output.tank.fill(product, FluidAction.SIMULATE) != product.getAmount()) return;
            products.add(product);
        }
        // All tanks are local to the same server-thread operation. Explicit native
        // void modes still discard overflow; KEEP_FLUID never loses a partial batch.
        controller.tank.drain((int) scaledInput, FluidAction.EXECUTE);
        for (int i = 0; i < outputs.size(); i++)
            outputs.get(i).tank.fill(products.get(i), FluidAction.EXECUTE);
    }
}
