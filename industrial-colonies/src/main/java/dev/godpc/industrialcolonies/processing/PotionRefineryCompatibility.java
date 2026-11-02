package dev.godpc.industrialcolonies.processing;

import blusunrize.immersiveengineering.api.crafting.RefineryRecipe;
import blusunrize.immersiveengineering.common.blocks.multiblocks.process.*;
import com.mojang.serialization.JsonOps;
import net.minecraft.resources.*;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.level.Level;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.crafting.FluidIngredient;
import net.neoforged.neoforge.server.ServerLifecycleHooks;

/** Narrow compatibility for the reviewed refinery consumer; no fluid/storage rewriting. */
public final class PotionRefineryCompatibility {
    public static final ResourceLocation RECIPE=ResourceLocation.parse("immersiveengineering:refinery/high_power_biodiesel");

    private static RefineryRecipe current() {
        var server=ServerLifecycleHooks.getCurrentServer();
        if(server==null||!server.isSameThread()||!PotionIdentityRuntime.ready(server.getRecipeManager())) return null;
        var recipe=server.getRecipeManager().byKey(RECIPE).map(h->h.value()).orElse(null);
        return recipe instanceof RefineryRecipe refinery?refinery:null;
    }
    public static FluidStack lookup(FluidIngredient ingredient,FluidStack original) {
        var recipe=current();
        return recipe!=null&&recipe.input1!=null&&recipe.input1.ingredient()==ingredient
                ?PotionIdentityRuntime.produced(original):original;
    }
    public static boolean affected(MultiblockProcess<?,?> process) {
        return PotionIdentityRuntime.enabled()&&RECIPE.equals(process.getRecipeId());
    }
    private static RefineryRecipe reviewed(MultiblockProcess<?,?> process,Level level) {
        var live=current();
        if(live==null||!RECIPE.equals(process.getRecipeId())||!(process.getRecipe(level) instanceof RefineryRecipe pending)) return null;
        if(pending==live) return pending;
        // Reload may replace the holder while a native queue retains its recipe object.
        var ops=RegistryOps.create(JsonOps.INSTANCE,level.registryAccess());
        try {
            return EffectiveFluidNormalizer.fingerprint(Recipe.CODEC.encodeStart(ops,pending).getOrThrow())
                    .equals(EffectiveFluidNormalizer.fingerprint(Recipe.CODEC.encodeStart(ops,live).getOrThrow()))?pending:null;
        } catch(RuntimeException e) { return null; }
    }
    public static boolean canProcess(MultiblockProcess<?,?> process,ProcessContext<?> context,Level level) {
        if(!affected(process)) return true;
        var recipe=reviewed(process,level);
        if(recipe==null||recipe.input1==null||!(process instanceof MultiblockProcessInMachine<?> machine)) return false;
        int[] slots=machine.getInputTanks();var tanks=context.getInternalTanks();
        // The installed refinery binds its two independent input tanks; never spend output storage.
        if(slots==null||slots.length!=2||slots[0]!=0||slots[1]!=1||tanks.length<2||tanks[0]==null||tanks[1]==null) return false;
        var a=tanks[0].getFluid();var b=tanks[1].getFluid();
        return (recipe.input0.test(a)&&recipe.input1.test(PotionIdentityRuntime.produced(b)))
                ||(recipe.input0.test(b)&&recipe.input1.test(PotionIdentityRuntime.produced(a)));
    }
    public static FluidStack consumption(MultiblockProcess<?,?> process,FluidIngredient ingredient,FluidStack original,Level level) {
        var server=ServerLifecycleHooks.getCurrentServer();
        if(server==null||!server.isSameThread()) return original;
        var recipe=reviewed(process,level);
        return recipe!=null&&recipe.input1!=null&&recipe.input1.ingredient()==ingredient
                ?PotionIdentityRuntime.produced(original):original;
    }
}
