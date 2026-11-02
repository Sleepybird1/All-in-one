package dev.godpc.industrialcolonies;

import net.minecraft.core.NonNullList;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.item.ItemStack;

/** Decision55: preserve three-wire fabrication while capping its exact Arc return. */
public final class CopperWireRecovery {
    private CopperWireRecovery() {}

    public static NonNullList<ItemStack> limit(Object recipe, NonNullList<ItemStack> original) {
        try {
            Object input=recipe.getClass().getField("input").get(recipe);
            if(!Integer.valueOf(1).equals(input.getClass().getMethod("getCount").invoke(input)))return original;
            Object resolved=input.getClass().getMethod("getMatchingStacks").invoke(input);
            if(!(resolved instanceof ItemStack[] stacks)||stacks.length!=1
                ||!BuiltInRegistries.ITEM.getKey(stacks[0].getItem()).toString().equals("tfmg:copper_wire"))return original;
        } catch(ReflectiveOperationException failure) {
            throw new IllegalStateException("Cannot inspect exact copper recovery input",failure);
        }
        var result=NonNullList.<ItemStack>create();
        int remaining=3;
        for(ItemStack stack:original) {
            ItemStack copy=stack.copy();
            if(BuiltInRegistries.ITEM.getKey(copy.getItem()).toString().equals("immersiveengineering:nugget_copper")) {
                int retained=Math.min(copy.getCount(),remaining);
                copy.setCount(retained);remaining-=retained;
            }
            if(!copy.isEmpty())result.add(copy);
        }
        return result;
    }
}
