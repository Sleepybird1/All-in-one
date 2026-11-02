package dev.godpc.industrialcolonies;

import com.zizazr.kjsgen.core.*;
import com.zizazr.kjsgen.codegen.*;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import java.util.*;

/** Opt-in native tool semantics; existing recipes retain their original behavior. */
public final class ToolUseOptions {
    public static final String MODE="icToolUse", ITEM="icToolItem", DAMAGE="icToolDamage";
    public static final List<String> DEPLOY_MODES=List.of("native","keep","damage");
    private ToolUseOptions() {}
    public static RecipeTypeDefinition extend(RecipeTypeDefinition s,boolean crafting,String codegen) {
        var p=new ArrayList<>(s.parameters());
        if(p.stream().noneMatch(v->v.key().equals(MODE))) {
            p.add(ParameterDefinition.ofEnum(MODE,"native",crafting?List.of("native","consume","keep","damage"):DEPLOY_MODES));
            if(crafting){p.add(ParameterDefinition.ofString(ITEM,""));p.add(ParameterDefinition.ofInt(DAMAGE,1));}
        }
        if(p.stream().noneMatch(v->v.key().equals(DAMAGE)))p.add(ParameterDefinition.ofInt(DAMAGE,1));
        return new RecipeTypeDefinition(s.id(),s.modId(),s.iconItem(),s.canvasWidth(),s.canvasHeight(),s.slots(),s.decorations(),p,codegen,s.requiresMod(),s.editorKind(),s.jeiCategory());
    }
    public static String mode(RecipeInstance recipe,RecipeTypeDefinition type,String key) {
        String v=recipe.param(type,key);return v.isBlank()?"native":v.equals("damage_1")?"damage":v;
    }
    public static void requireDamageable(SlotContent item) {
        if(item.kind()!=ContentKind.ITEM)throw new IllegalArgumentException("Damage tool requires a concrete item, not a tag");
        var id=ResourceLocation.tryParse(item.id());
        if(id==null || !BuiltInRegistries.ITEM.containsKey(id) || BuiltInRegistries.ITEM.get(id).getDefaultInstance().getMaxDamage()<=0)
            throw new IllegalArgumentException("Selected tool has no durability: "+item.id());
    }
    public static int damage(RecipeInstance recipe,RecipeTypeDefinition type,String key){
        String raw=recipe.param(type,key);if(raw.isBlank())return 1;
        try{int value=Integer.parseInt(raw);if(value>0)return value;}catch(NumberFormatException ignored){}
        throw new IllegalArgumentException("Tool damage must be a positive whole number");
    }
    public static String deploySuffix(String mode,SlotContent held){return deploySuffix(mode,held,1);}
    public static String deploySuffix(String mode,SlotContent held,int damage) {
        return switch(mode) {
            case "native" -> "";
            case "keep" -> ".merge({keep_held_item: true, processing_time: 0})";
            case "damage_1", "damage" -> { requireDamageable(held);if(damage<1)throw new IllegalArgumentException("Tool damage must be positive");yield ".merge({keep_held_item: false, industrial_tool_damage: "+damage+", processing_time: 0})"; }
            default -> throw new IllegalArgumentException("Unknown tool use mode: "+mode);
        };
    }
    public static String craftingSuffix(RecipeInstance recipe,RecipeTypeDefinition type) {
        String mode=mode(recipe,type,MODE);if(mode.equals("native"))return "";
        String id=recipe.param(type,ITEM).trim();
        if(!id.matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))throw new IllegalArgumentException("Choose a tool item ID already present in the crafting ingredients");
        // Require an existing exact ingredient: no hidden ingredient insertion or ambiguous tag matching.
        var json=recipe.toJson().getAsJsonObject("slots");boolean found=false;
        for(var entry:json.entrySet()) {
            String key=entry.getKey();
            if(key.startsWith("output") || key.equals("result"))continue;
            var slot=recipe.slot(key);if(slot.kind()==ContentKind.ITEM && slot.id().equals(id))found=true;
        }
        if(!found)throw new IllegalArgumentException("Tool must already be an exact ingredient in this recipe: "+id);
        return switch(mode) {
            case "keep" -> ".keepIngredient("+JsUtil.quote(id)+")";
            case "consume" -> ".consumeIngredient("+JsUtil.quote(id)+")";
            case "damage" -> {
                requireDamageable(SlotContent.item(id,1));
                int damage;try{damage=Integer.parseInt(recipe.param(type,DAMAGE));}catch(NumberFormatException e){throw new IllegalArgumentException("Tool damage must be a positive integer");}
                if(damage<1)throw new IllegalArgumentException("Tool damage must be positive");
                yield ".damageIngredient("+JsUtil.quote(id)+", "+damage+")";
            }
            default -> throw new IllegalArgumentException("Unknown crafting tool use mode: "+mode);
        };
    }
    public record CraftingCodegen(RecipeCodegen delegate) implements RecipeCodegen {
        public String generate(RecipeInstance r,RecipeTypeDefinition t){return new NativeCraftingCodegen(delegate).generate(r,t)+craftingSuffix(r,t);}
        public Optional<String> removeTypeId(RecipeInstance r,RecipeTypeDefinition t){return new NativeCraftingCodegen(delegate).removeTypeId(r,t);}
    }
}
