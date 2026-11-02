package dev.godpc.industrialcolonies;
import com.zizazr.kjsgen.core.*;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.fluids.FluidUtil;

/** Explicit picker action only: never rewrites an authored bucket ingredient automatically. */
public final class KjsGenFluidChoice {
 private KjsGenFluidChoice() {}
 public static SlotContent chooseFluid(SlotDefinition definition,ContentKind kind,String id,int amount) {
  if(!definition.allowsFluid())throw new IllegalArgumentException("This recipe slot cannot contain fluids");
  var key=ResourceLocation.tryParse(id);
  if(kind==ContentKind.FLUID && key!=null && BuiltInRegistries.FLUID.containsKey(key))
   return SlotContent.fluid(id,Math.max(1,amount));
  if(kind==ContentKind.ITEM && key!=null && BuiltInRegistries.ITEM.containsKey(key)) {
   var contained=FluidUtil.getFluidContained(new ItemStack(BuiltInRegistries.ITEM.get(key)));
   if(contained.isPresent() && !contained.get().isEmpty()) {
    var fluid=contained.get();return SlotContent.fluid(BuiltInRegistries.FLUID.getKey(fluid.getFluid()).toString(),fluid.getAmount());
   }
  }
  return SlotContent.fluid("",1000); // User chooses a registered fluid next; empty identity cannot be exported.
 }
}
