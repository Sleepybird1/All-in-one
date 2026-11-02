package dev.godpc.industrialcolonies.processing;

import com.mojang.serialization.JsonOps;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.*;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.material.Fluid;

/** Opt-in bridge only while the exact reviewed refinery is present. No saved-fluid rewrite. */
public final class SpaceOilIdentity {
    private static final ResourceLocation RECIPE=ResourceLocation.parse("stellaris:fuel_refining");
    private static final String EXPECTED="26eceb94b4f538e0813ea71dbd00b94b69393c5849aaa60cec761d0c9cc54b52";
    public static boolean ready(Level level) {
        if(level==null||!Boolean.getBoolean("industrial_colonies.canonicalSpaceOil")) return false;
        var holder=level.getRecipeManager().byKey(RECIPE).orElse(null);
        if(holder==null) return false;
        try {
            var encoded=Recipe.CODEC.encodeStart(RegistryOps.create(JsonOps.INSTANCE,level.registryAccess()),holder.value()).getOrThrow();
            var fingerprint=EffectiveFluidNormalizer.fingerprint(encoded);
            return fingerprint.equals(EXPECTED)||(StellarisDieselIdentity.enabled()&&fingerprint.equals("6aa6466f3c1750c2efb0318dbf1498822d99396332da950f6777db46f6a7cc8d"));
        }catch(RuntimeException error){return false;}
    }
    public static Fluid preferred(){return BuiltInRegistries.FLUID.get(ResourceLocation.parse("ad_astra:oil"));}
    public static Fluid selected(Level level,Fluid original){return ready(level)?preferred():original;}
}
