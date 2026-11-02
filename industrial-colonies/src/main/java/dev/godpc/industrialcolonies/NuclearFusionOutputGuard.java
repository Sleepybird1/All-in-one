package dev.godpc.industrialcolonies;

import java.util.List;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;

/** Product capacity checks; the native tick retains ownership of heat and cooling. */
public final class NuclearFusionOutputGuard {
    private NuclearFusionOutputGuard() {}

    public static boolean canContinue(Object reaction,Object controller) {
        try {
            var field=reaction.getClass().getDeclaredField("currentRecipe");
            field.setAccessible(true);
            return canStart(controller,field.get(reaction));
        } catch(ReflectiveOperationException|RuntimeException failure) {
            return false;
        }
    }

    public static boolean canStart(Object controller,Object recipe) {
        if(controller==null||recipe==null)return false;
        try {
            Object nativeTanks=controller.getClass().getMethod("fluidTanks").invoke(controller);
            if(!(nativeTanks instanceof IFluidHandler tanks))return false;
            Object value=recipe.getClass().getMethod("outputs").invoke(recipe);
            if(!(value instanceof List<?> outputs)||outputs.size()>4)return false;
            var fill=nativeTanks.getClass().getMethod("fillTank",int.class,FluidStack.class,IFluidHandler.FluidAction.class);
            for(int i=0;i<outputs.size();i++) {
                Object resolved=outputs.get(i).getClass().getMethod("resolve").invoke(outputs.get(i));
                if(!(resolved instanceof FluidStack output)||output.isEmpty())return false;
                int tank=3+i;
                if(tank>=tanks.getTanks())return false;
                FluidStack stored=tanks.getFluidInTank(tank);
                if(!stored.isEmpty()&&!FluidStack.isSameFluidSameComponents(stored,output))return false;
                if((long)tanks.getTankCapacity(tank)-stored.getAmount()<output.getAmount())return false;
                if(!Integer.valueOf(output.getAmount()).equals(fill.invoke(nativeTanks,tank,output.copy(),IFluidHandler.FluidAction.SIMULATE)))return false;
            }
            return true;
        } catch(ReflectiveOperationException|RuntimeException failure) {
            return false;
        }
    }
}
