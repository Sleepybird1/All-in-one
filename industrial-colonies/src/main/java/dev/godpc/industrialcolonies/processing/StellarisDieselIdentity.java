package dev.godpc.industrialcolonies.processing;

import com.st0x0ef.stellaris.common.registry.FluidRegistry;
import com.st0x0ef.stellaris.common.registry.ItemsRegistry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.material.Fluid;

/** Exact opt-in identity compatibility, not a general diesel or energy equivalence rule. */
public final class StellarisDieselIdentity {
    private static final ResourceLocation FLUID=ResourceLocation.parse("tfmg:diesel");
    private static final ResourceLocation BUCKET=ResourceLocation.parse("tfmg:diesel_bucket");
    public static boolean enabled(){return Boolean.getBoolean("industrial_colonies.canonicalSpaceDiesel");}
    public static boolean canonical(Fluid fluid){return enabled()&&BuiltInRegistries.FLUID.getKey(fluid).equals(FLUID);}
    public static boolean alias(Fluid actual,Fluid expected){return expected==FluidRegistry.DIESEL_STILL.get()&&canonical(actual);}
    public static boolean canonicalBucket(ItemStack stack){return enabled()&&!stack.isEmpty()&&BuiltInRegistries.ITEM.getKey(stack.getItem()).equals(BUCKET);}
    public static boolean dieselBucket(ItemStack stack){return enabled()&&(stack.is(ItemsRegistry.DIESEL_BUCKET.get())||canonicalBucket(stack));}
}
