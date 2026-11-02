package dev.godpc.industrialcolonies;
import com.zizazr.kjsgen.core.RecipeInstance;
import java.util.Map;
public final class KjsGenVatCompatibility {
 private KjsGenVatCompatibility(){}
 public static boolean vat(String id){return id.equals("industrial_colonies:tfmg_chemical_vat")||id.equals("industrial_colonies:tfmg_chemical_vat_machine")||KjsGenVatCanvasModel.namedVat(id)!=null;}
 public static String alias(String id,Map<String,?> slots,String key){
  if(!vat(id)||slots.containsKey(key))return null;
  String family=key.matches("input[1-4]")?"ingredients":key.matches("output[1-4]")?"results":null;
  if(family==null||slots.keySet().stream().noneMatch(k->k.matches(family+"[0-9]+")))return null;
  return family+(Integer.parseInt(key.substring(key.length()-1))-1);
 }
 /** Effective value only: old project JSON is not rewritten just to show the new controls. */
 public static String legacyParameter(RecipeInstance recipe,String key){
  if(!vat(recipe.typeId())||recipe.parameters().containsKey(key))return null;
  if(key.equals("attachmentDrive")||key.equals("electrodeType")||key.equals("electrodeCount")){
   String setup=recipe.parameters().containsKey("machineSetup")?recipe.paramRaw("machineSetup"):legacyParameter(recipe,"machineSetup");
   if(setup==null)return null;
   var ids=KjsGenVatCanvasModel.values(setup);
   return switch(key){
    case "attachmentDrive" -> ids.contains("tfmg:centrifuge")?"Centrifuge":ids.contains("tfmg:mixing")?"Mixer":"None";
    case "electrodeType" -> ids.contains("tfmg:graphite_electrode")?"Graphite":"Standard";
    default -> Long.toString(ids.stream().filter(v->v.equals("tfmg:electrode")||v.equals("tfmg:graphite_electrode")).count());
   };
  }
  if(key.equals("allowedVatTypes"))return switch(String.valueOf(recipe.paramRaw("vatMode"))){
   case "steel"->"'tfmg:steel_vat'";case "firebrick"->"'tfmg:firebrick_lined_vat'";
   case "both"->"'tfmg:steel_vat', 'tfmg:firebrick_lined_vat'";default->null;
  };
  if(key.equals("machineSetup"))return switch(String.valueOf(recipe.paramRaw("machineMode"))){
   case "mixing"->"'tfmg:mixing'";case "two_electrodes"->"'tfmg:electrode', 'tfmg:electrode'";default->null;
  };
  return null;
 }
}
