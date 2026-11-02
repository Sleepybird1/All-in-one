package dev.godpc.industrialcolonies;

import com.google.gson.*;
import com.zizazr.kjsgen.codegen.*;
import com.zizazr.kjsgen.core.*;
import java.util.*;

/** Exact universal-processor arrays and native machine capacities from NuclearCraft 1.3.0-rc1.
 * Specialized reactor, heat, fuel and world-generation codecs are deliberately separate.
 */
public final class NuclearCraftManufacturingCodegen implements RecipeCodegen {
    public static final String ID="industrial_colonies:nuclearcraft_manufacturing";
    public record Shape(int fluidInputs,int itemInputs,int fluidOutputs,int itemOutputs) {}
    public static final Map<String,Shape> SHAPES=Map.ofEntries(
        Map.entry("gas_scrubber", new Shape(1,0,1,0)),
        Map.entry("manufactory", new Shape(0,1,0,1)),
        Map.entry("alloy_smelter", new Shape(0,2,0,1)),
        Map.entry("assembler", new Shape(0,6,0,1)),
        Map.entry("centrifuge", new Shape(1,0,6,0)),
        Map.entry("chemical_reactor", new Shape(2,0,2,0)),
        Map.entry("crystallizer", new Shape(1,0,0,1)),
        Map.entry("decay_hastener", new Shape(0,1,0,1)),
        Map.entry("electrolyzer", new Shape(1,0,4,0)),
        Map.entry("extractor", new Shape(0,1,1,1)),
        Map.entry("fluid_enricher", new Shape(1,1,1,0)),
        Map.entry("fluid_infuser", new Shape(1,1,0,1)),
        Map.entry("fuel_reprocessor", new Shape(0,1,0,8)),
        Map.entry("ingot_former", new Shape(1,0,0,1)),
        Map.entry("isotope_separator", new Shape(0,1,0,2)),
        Map.entry("melter", new Shape(0,1,1,0)),
        Map.entry("pressurizer", new Shape(0,1,0,1)),
        Map.entry("rock_crusher", new Shape(0,1,0,3)),
        Map.entry("steam_turbine", new Shape(1,0,1,0)),
        Map.entry("supercooler", new Shape(1,0,1,0)),
        Map.entry("subatomic_liquifier", new Shape(1,1,1,0)),
        Map.entry("irradiator", new Shape(1,1,1,1)),
        Map.entry("pump", new Shape(0,1,1,0)),
        Map.entry("leacher", new Shape(1,1,1,0)),
        Map.entry("analyzer", new Shape(0,1,0,1)));
    private static String family(RecipeInstance recipe) {
        String prefix="industrial_colonies:nuclearcraft_";
        if (!recipe.typeId().startsWith(prefix) || !SHAPES.containsKey(recipe.typeId().substring(prefix.length())))
            throw new IllegalArgumentException("Unsupported NuclearCraft processor editor: "+recipe.typeId());
        return recipe.typeId().substring(prefix.length());
    }
    /** Normalize known persisted template layouts without changing any saved card slot identity.
     * Apply after user-layout loading and resource reload; no files are rewritten.
     */
    public static RecipeTypeDefinition extendDefinition(RecipeTypeDefinition source) {
        String prefix="industrial_colonies:nuclearcraft_";
        if(!source.id().startsWith(prefix)||!SHAPES.containsKey(source.id().substring(prefix.length())))
            throw new IllegalArgumentException("Not a known NuclearCraft processor layout");
        var slots=new ArrayList<SlotDefinition>();
        for(SlotDefinition slot:source.slots())slots.add(new SlotDefinition(slot.key(),slot.role(),slot.x(),slot.y(),slot.required(),
            slot.allowsItem(),slot.allowsTag(),slot.allowsFluid(),slot.allowsChemical(),true,slot.allowsChance(),slot.list()));
        if(source.id().endsWith(":nuclearcraft_assembler")&&slots.stream().anyMatch(s->s.key().equals("in0"))&&slots.stream().noneMatch(s->s.key().equals("in5")))
            slots.add(new SlotDefinition("in5",SlotRole.INPUT,56,32,false,true,true,false,false,true,false,false));
        var parameters=new ArrayList<>(source.parameters().stream().filter(p->!p.key().equals("__template")).toList());
        if(parameters.stream().noneMatch(p->p.key().equals("energyPerTick")))parameters.add(ParameterDefinition.ofInt("energyPerTick",50));
        if(parameters.stream().noneMatch(p->p.key().equals("processTime")))parameters.add(ParameterDefinition.ofInt("processTime",200));
        return new RecipeTypeDefinition(source.id(),source.modId(),source.iconItem(),source.canvasWidth(),source.canvasHeight(),slots,
            source.decorations(),parameters,ID,source.requiresMod(),source.editorKind(),source.jeiCategory());
    }
    @Override public String generate(RecipeInstance recipe,RecipeTypeDefinition type) {
        String family=family(recipe);
        if (!recipe.typeId().equals(type.id())) throw new IllegalArgumentException("Recipe and editor type differ");
        Shape shape=SHAPES.get(family);
        JsonObject data=new JsonObject();data.addProperty("type","nuclearcraft:"+family);
        Map<String,Integer> counts=new HashMap<>();Set<String> represented=new HashSet<>();
        for (SlotDefinition definition:type.slots()) {
            represented.add(definition.key());SlotContent slot=recipe.slot(definition.key());
            if (slot.isEmpty()) {if(definition.required())throw new IllegalArgumentException("Missing "+definition.key());continue;}
            if (!definition.accepts(slot.kind())) throw new IllegalArgumentException("Wrong content for "+definition.key());
            boolean output=definition.role()==SlotRole.OUTPUT;
            if (definition.role()!=SlotRole.INPUT && !output) throw new IllegalArgumentException("Unsupported processor catalyst slot");
            boolean item=slot.kind()==ContentKind.ITEM||slot.kind()==ContentKind.ITEM_TAG;
            boolean fluid=slot.kind()==ContentKind.FLUID||slot.kind()==ContentKind.FLUID_TAG;
            if (!item&&!fluid) throw new IllegalArgumentException("Processors use items and fluids, not Mekanism chemicals");
            boolean tag=slot.kind()==ContentKind.ITEM_TAG||slot.kind()==ContentKind.FLUID_TAG;
            if(output&&tag)throw new IllegalArgumentException("Output must be concrete");
            if(!slot.id().matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))throw new IllegalArgumentException("Invalid resource identity");
            if(slot.components()!=null&&!slot.components().isBlank())throw new IllegalArgumentException("Component predicates unsupported");
            if(slot.chance()!=1)throw new IllegalArgumentException("Universal processor output codec has no chance field");
            int amount=item?slot.count():slot.amount();if(amount<=0)throw new IllegalArgumentException("Positive amount required");
            String key=(item?"item":"fluid")+(output?"_outputs":"_inputs");
            JsonArray values=data.has(key)?data.getAsJsonArray(key):new JsonArray();
            JsonObject value=new JsonObject();value.addProperty(tag?"tag":item?"item":"fluid",slot.id());
            if(!item||!output||amount!=1||recipe.paramRaw("__nativeOutputCount").equals("true"))value.addProperty(item?"count":"amount",amount);
            values.add(value);data.add(key,values);counts.merge(key,1,Integer::sum);
        }
        for(var entry:recipe.slots().entrySet())if(!entry.getValue().isEmpty()&&!represented.contains(entry.getKey()))
            throw new IllegalArgumentException("Unrepresented NuclearCraft slot: "+entry.getKey());
        capacity(counts,"fluid_inputs",shape.fluidInputs());capacity(counts,"item_inputs",shape.itemInputs());
        capacity(counts,"fluid_outputs",shape.fluidOutputs());capacity(counts,"item_outputs",shape.itemOutputs());
        if(counts.getOrDefault("fluid_inputs",0)+counts.getOrDefault("item_inputs",0)==0)throw new IllegalArgumentException("Processor input required");
        if(counts.getOrDefault("fluid_outputs",0)+counts.getOrDefault("item_outputs",0)==0)throw new IllegalArgumentException("Processor output required");
        data.addProperty("energy_per_tick",positive(recipe.param(type,"energyPerTick"),"Energy per tick"));
        data.addProperty("process_time",positive(recipe.param(type,"processTime"),"Process time"));
        if(!recipe.paramRaw("__nativeConditions").isBlank())throw new IllegalArgumentException("Conditional import unsupported");
        if(!recipe.recipeId().matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))throw new IllegalArgumentException("Explicit valid recipe ID required");
        return "event.custom("+data+").id("+JsUtil.quote(recipe.recipeId())+")";
    }
    private static void capacity(Map<String,Integer> counts,String key,int maximum) {
        if(counts.getOrDefault(key,0)>maximum)throw new IllegalArgumentException("Native "+key+" capacity is "+maximum);
    }
    private static int positive(String value,String label) {
        int n;try{n=Integer.parseInt(value);}catch(NumberFormatException e){throw new IllegalArgumentException(label+" must be a whole number",e);}
        if(n<=0)throw new IllegalArgumentException(label+" must be positive");return n;
    }
    @Override public Optional<String> removeTypeId(RecipeInstance recipe,RecipeTypeDefinition type){return Optional.of("nuclearcraft:"+family(recipe));}
}
