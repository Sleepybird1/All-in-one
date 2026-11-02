package dev.godpc.industrialcolonies;
import com.zizazr.kjsgen.core.*;
import com.zizazr.kjsgen.codegen.JsUtil;
import com.zizazr.kjsgen.codegen.handlers.CreateSequencedAssemblyCodegen;
import java.util.*;

/** Retain the native outer recipe and suffixes; replace only its one-line nested operations. */
public final class ExtendedSequenceCodegen {
    public static String generate(RecipeInstance recipe,RecipeTypeDefinition type) {
        String[] lines=new CreateSequencedAssemblyCodegen().generate(recipe,type).split("\n",-1);
        int stage=0,total=CreateSpecialModel.seqLen(recipe,type);
        String trans=JsUtil.ingredient(recipe.slot("transitional"));
        for(int line=0;line<lines.length;line++) {
            if(!lines[line].startsWith("    event.recipes.create."))continue;
            String family=CreateSpecialModel.stepTypeId(recipe,type,stage);
            String operation=lines[line].strip();
            if(operation.endsWith(","))operation=operation.substring(0,operation.length()-1);
            if(SequenceStageOptions.basin(family)) {
                var inputs=new ArrayList<String>();inputs.add(trans);
                int itemCount=1,fluidCount=0;
                for(int n=0;n<4;n++) {
                    var extra=recipe.slot(SequenceStageOptions.key(stage,"Extra"+n));
                    if(extra.isEmpty())continue;
                    if(extra.components()!=null && !extra.components().isBlank())throw new IllegalArgumentException("Stage extra inputs with components are not supported");
                    if(extra.chance()!=1.0F)throw new IllegalArgumentException("Stage inputs cannot be probabilistic");
                    if(extra.kind()==ContentKind.ITEM || extra.kind()==ContentKind.ITEM_TAG) {
                        if(extra.count()<1 || extra.count()>63)throw new IllegalArgumentException("Stage item count must be 1..63");
                        itemCount+=extra.count();
                        for(int count=0;count<extra.count();count++)inputs.add("{"+(extra.kind()==ContentKind.ITEM?"item":"tag")+": "+JsUtil.quote(extra.id())+"}");
                    } else if(extra.kind()==ContentKind.FLUID || extra.kind()==ContentKind.FLUID_TAG) {
                        if(extra.amount()<1)throw new IllegalArgumentException("Stage fluid amount must be positive");
                        fluidCount++;inputs.add(JsUtil.ingredient(extra));
                    } else throw new IllegalArgumentException("Basin stages require item or fluid ingredients");
                }
                if(itemCount>64 || fluidCount>2)throw new IllegalArgumentException("A basin supports at most 64 item inputs and two fluid inputs");
                var recipeFamily=MachineRecipeRouting.family(family).orElseThrow();
                String runtime=MachineRecipeRouting.runtimeTypeId(recipeFamily,MachineRecipeRouting.selectedStepMachine(recipe,stage,recipeFamily));
                operation="event.recipes."+runtime.replace(':','.')+"("+trans+", ["+String.join(", ",inputs)+"] )";
                String heat=SequenceStageOptions.heat(recipe,type,stage);
                if(!Set.of("none","lowheated","heated","superheated").contains(heat))throw new IllegalArgumentException("Unknown stage heat: "+heat);
                operation+=".merge({heat_requirement: "+JsUtil.quote(heat)+", processing_time: "+SequenceStageOptions.ticks(recipe,type,stage)+"})";
            } else if(SequenceStageOptions.FANS.contains(family)) {
                var carrier=recipe.slot("transitional");
                if(carrier.kind()!=ContentKind.ITEM)throw new IllegalArgumentException("Assembly workpiece must be a concrete item");
                String id=JsUtil.quote(carrier.id());
                var fanFamily=MachineRecipeRouting.sequenceFamily(family).orElseThrow();
                var selection=recipe.slot(MachineRecipeRouting.stepSlotKey(stage,fanFamily));
                var machine=MachineRecipeRouting.machineByContent(fanFamily,selection);
                if(!selection.isEmpty() && machine==null)throw new IllegalArgumentException("Invalid fan selection at stage "+(stage+1));
                // Empty legacy selections remain unrestricted; choosing a fan makes the binding exact.
                String suffix=machine==null?"":"_"+machine.id();
                operation="event.custom({type: 'industrial_colonies:assembly_"+family+suffix+"', ingredients: [{item: "+id+"}], results: [{id: "+id+"}], processing_time: "+SequenceStageOptions.ticks(recipe,type,stage)+"})";
            } else if(family.equals("deploying")) {
                operation+=ToolUseOptions.deploySuffix(ToolUseOptions.mode(recipe,type,SequenceStageOptions.key(stage,"ToolUse")),CreateSpecialModel.stepItem(recipe,stage),ToolUseOptions.damage(recipe,type,SequenceStageOptions.key(stage,"ToolDamage")));
            } else if(family.equals("cutting") && !recipe.param(type,SequenceStageOptions.key(stage,"Ticks")).isEmpty()) {
                operation+=".merge({processing_time: "+SequenceStageOptions.ticks(recipe,type,stage)+"})";
            }
            lines[line]="    "+operation+(stage<total-1?",":"");stage++;
        }
        if(stage!=total)throw new IllegalStateException("Native assembly exporter layout changed; refusing to rewrite stages");
        return String.join("\n",lines);
    }
}
