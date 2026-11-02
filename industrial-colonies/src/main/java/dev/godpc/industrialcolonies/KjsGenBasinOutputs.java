package dev.godpc.industrialcolonies;
import com.zizazr.kjsgen.core.*;
import java.util.*;

/** Additive fields keep legacy singular outputs intact and never activate stale outputN fields. */
public final class KjsGenBasinOutputs {
 private KjsGenBasinOutputs(){}
 public static RecipeTypeDefinition extend(RecipeTypeDefinition source) {
  if(source.slots().stream().anyMatch(s->s.key().equals("icFluidOutput0")))return source;
  var output=source.slots().stream().filter(s->s.key().equals("output")).findFirst().orElseThrow();
  var slots=new ArrayList<>(source.slots());
  for(int i=0;i<2;i++)slots.add(new SlotDefinition("icFluidOutput"+i,SlotRole.OUTPUT,output.x()+20*i,output.y()+24,false,false,false,true,false,true,false,false));
  return new RecipeTypeDefinition(source.id(),source.modId(),source.iconItem(),Math.max(source.canvasWidth(),output.x()+62),Math.max(source.canvasHeight(),output.y()+44),slots,source.decorations(),source.parameters(),source.codegenId(),source.requiresMod(),source.editorKind(),source.jeiCategory());
 }
 public static void validate(RecipeInstance recipe,RecipeTypeDefinition type) {
  int inputs=0,outputs=0;
  for(var slot:type.slots())for(var content:slot.list()?recipe.listSlots(slot.key()):List.of(recipe.slot(slot.key()))) {
   if(content.isEmpty())continue;
   if(content.kind()==ContentKind.FLUID||content.kind()==ContentKind.FLUID_TAG) {
    if(content.amount()<1)throw new IllegalArgumentException("Fluid amounts must be positive whole mB");
    if(slot.role()==SlotRole.INPUT)inputs++;
    if(slot.role()==SlotRole.OUTPUT)outputs++;
   }
  }
  if(inputs>2||outputs>2)throw new IllegalArgumentException("Create basin supports at most two fluid inputs and two fluid outputs");
 }
}
