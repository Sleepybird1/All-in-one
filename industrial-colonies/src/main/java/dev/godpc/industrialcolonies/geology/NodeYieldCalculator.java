package dev.godpc.industrialcolonies.geology;

import com.google.gson.*;
import java.util.*;
import net.minecraft.core.registries.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.storage.loot.LootTable;
import modernmods.modernfoundry.library.recipe.TinkerRecipeTypes;
import modernmods.modernfoundry.library.recipe.melting.*;
import modernmods.modernfoundry.common.config.Config;

/** Explicit-use estimate from a verified physical breakdown and the currently loaded melting recipes.
 * Never samples random loot, creates items, loads chunks or substitutes a recipe that is not present. */
public final class NodeYieldCalculator {
    public record Range(long minimum,long maximum) {
        public Range {if(minimum<0||maximum<minimum)throw new IllegalArgumentException("Invalid yield range");}
        public String display(){return String.format(Locale.ROOT,"%,d–%,d",minimum,maximum);}
    }
    private record Drop(String item,int count) {}
    private record Container(ItemStack stack,IMeltingContainer.IOreRate oreRate) implements IMeltingContainer {
        public ItemStack getStack(){return stack;}
        public IMeltingContainer.IOreRate getOreRate(){return oreRate;}
    }
    private NodeYieldCalculator(){}

    public static Optional<Range> estimate(ServerLevel level,String family,MiningNodeSurvey.Result observation){
        if(!observation.complete())return Optional.empty();
        try {
            var definition=GeologyConfig.array(GeologyConfig.get().deposits(),"deposits").asList().stream()
                .map(JsonElement::getAsJsonObject).filter(d->d.get("id").getAsString().equals(family)).findFirst().orElseThrow();
            var materials=GeologyConfig.array(definition,"primaryMaterials").asList().stream().map(JsonElement::getAsString).toList();
            if(materials.size()!=1)return Optional.empty();
            var recipes=level.getRecipeManager().getAllRecipesFor(TinkerRecipeTypes.MELTING.get());
            if(recipes.size()>8192||observation.blocks().size()>128)return Optional.empty();
            long minimum=0,maximum=0;
            for(var entry:observation.blocks().entrySet()) {
                var block=BuiltInRegistries.BLOCK.get(ResourceLocation.parse(entry.getKey()));
                var key=block.getLootTable();
                var table=level.getServer().reloadableRegistries().getLootTable(key);
                var json=LootTable.DIRECT_CODEC.encodeStart(level.registryAccess().createSerializationContext(com.mojang.serialization.JsonOps.INSTANCE),table).getOrThrow().getAsJsonObject();
                var drops=drops(json);if(drops==null)return Optional.empty();
                for(var drop:drops){
                    var item=BuiltInRegistries.ITEM.get(ResourceLocation.parse(drop.item()));
                    var stack=new ItemStack(item);
                    long low=Long.MAX_VALUE,high=0;
                    for(String material:materials){
                        var molten=TagKey.create(Registries.FLUID,ResourceLocation.parse("c:molten_"+material));
                        var ingots=TagKey.create(Registries.ITEM,ResourceLocation.parse("c:ingots/"+material));
                        int unit=0;
                        for(var holder:recipes)if(holder.value() instanceof MeltingRecipe recipe){
                            for(var ingot:BuiltInRegistries.ITEM.getTagOrEmpty(ingots)){
                                if(recipe.getInput().test(new ItemStack(ingot.value()))){
                                    var output=recipe.getOutput();
                                    if(!output.isEmpty()&&output.getFluid().is(molten)){
                                        if(unit!=0&&unit!=output.getAmount())return Optional.empty();
                                        unit=output.getAmount();
                                    }
                                }
                            }
                        }
                        if(unit==0)continue;
                        for(var holder:recipes)if(holder.value() instanceof MeltingRecipe recipe&&recipe.getInput().test(stack)){
                            for(var rate:List.of(Config.COMMON.melterOreRate,Config.COMMON.smelteryOreRate,Config.COMMON.foundryOreRate)){
                                var output=recipe.getOutput(new Container(stack,rate));
                                if(output.isEmpty()||!output.getFluid().is(molten))continue;
                                long total=Math.multiplyExact(Math.multiplyExact(entry.getValue(),drop.count()),output.getAmount());
                                low=Math.min(low,total/unit);high=Math.max(high,Math.floorDiv(Math.addExact(total,unit-1),unit));
                            }
                        }
                    }
                    // A self-dropping host rock with no current processing recipe contributes no metal.
                    // Other unsupported drops are unknown, rather than invented one-for-one metal.
                    if(low==Long.MAX_VALUE){
                        if(drop.item().equals(entry.getKey()))continue;
                        return Optional.empty();
                    }
                    minimum=Math.addExact(minimum,low);maximum=Math.addExact(maximum,high);
                }
            }
            if(maximum==0&&observation.total()!=0)return Optional.empty();
            return Optional.of(new Range(minimum,maximum));
        }catch(RuntimeException failure){return Optional.empty();}
    }

    /** Only deterministic empty-tool loot is admitted; unfamiliar conditions/functions remain unknown. */
    private static List<Drop> drops(JsonObject table){
        var result=new ArrayList<Drop>();
        if(table.has("functions")&&!table.getAsJsonArray("functions").isEmpty())return null;
        if(!table.has("pools"))return result;
        for(var element:table.getAsJsonArray("pools")){
            var pool=element.getAsJsonObject();if(constant(pool.get("rolls"))!=1||pool.has("functions")&&!pool.getAsJsonArray("functions").isEmpty())return null;
            if(pool.has("bonus_rolls")&&constant(pool.get("bonus_rolls"))!=0)return null;
            if(!conditions(pool))continue;
            var entries=pool.getAsJsonArray("entries");if(entries.size()!=1)return null;
            var drop=entry(entries.get(0).getAsJsonObject());if(drop==null)return null;result.addAll(drop);
        }
        return result;
    }
    private static List<Drop> entry(JsonObject e){
        if(!conditions(e))return List.of();
        String type=e.get("type").getAsString();
        if(type.equals("minecraft:alternatives")){
            for(var child:e.getAsJsonArray("children")){var object=child.getAsJsonObject();if(conditions(object))return entry(object);}
            return List.of();
        }
        if(!type.equals("minecraft:item"))return null;
        int count=1;
        if(e.has("functions"))for(var f:e.getAsJsonArray("functions")){
            var function=f.getAsJsonObject();String name=function.get("function").getAsString();
            if(name.equals("minecraft:explosion_decay"))continue;
            if(name.equals("minecraft:set_count")&&!function.has("conditions")){count=constant(function.get("count"));if(count<0)return null;}
            else return null;
        }
        return List.of(new Drop(e.get("name").getAsString(),count));
    }
    private static int constant(JsonElement e){
        if(e==null)return -1;
        if(e.isJsonPrimitive())return e.getAsBigDecimal().intValueExact();
        var o=e.getAsJsonObject();return o.has("type")&&o.get("type").getAsString().equals("minecraft:constant")?constant(o.get("value")):-1;
    }
    private static boolean conditions(JsonObject e){
        if(!e.has("conditions"))return true;
        for(var c:e.getAsJsonArray("conditions")){
            String condition=c.getAsJsonObject().get("condition").getAsString();
            if(condition.equals("minecraft:survives_explosion"))continue;
            if(condition.equals("minecraft:match_tool"))return false;
            throw new IllegalArgumentException("Unsupported deterministic loot condition");
        }
        return true;
    }
}
