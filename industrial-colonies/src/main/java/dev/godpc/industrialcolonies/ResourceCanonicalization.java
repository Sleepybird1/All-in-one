package dev.godpc.industrialcolonies;

import com.google.gson.JsonParser;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.trading.ItemCost;
import java.nio.file.*;
import java.util.*;

/** Runtime acquisition boundaries share the explicit recipe/viewer ownership table. */
public final class ResourceCanonicalization {
    private record Policy(Map<String,String> aliases, Set<String> retired, Set<String> blockedTradeResults) {}
    private static final Policy POLICY=load();
    private ResourceCanonicalization() {}
    private static Policy load() {
        Path path=Path.of("kubejs/config/industrial-resource-owners.json");
        if(!Files.exists(path))return new Policy(Map.of(),Set.of(),Set.of());
        try {
            var root=JsonParser.parseString(Files.readString(path)).getAsJsonObject();
            Map<String,String> aliases=new HashMap<>();Set<String> retired=new HashSet<>();
            for(var row:root.getAsJsonArray("rules")){
                var rule=row.getAsJsonObject();String chosen=rule.get("canonical").getAsString();
                for(var old:rule.getAsJsonArray("alternatives"))aliases.put(old.getAsString(),chosen);
            }
            for(var old:root.getAsJsonArray("retiredOnly"))retired.add(old.getAsString());
            Set<String> blockedTradeResults=new HashSet<>();
            if(root.has("blockedTradeResults"))for(var entry:root.getAsJsonArray("blockedTradeResults"))blockedTradeResults.add(entry.getAsString());
            return new Policy(Map.copyOf(aliases),Set.copyOf(retired),Set.copyOf(blockedTradeResults));
        } catch(Exception failure) {
            System.err.println("[Industrial Colonies] Cannot load acquisition owners: "+failure.getMessage());
            return new Policy(Map.of(),Set.of(),Set.of());
        }
    }
    public static boolean retired(ItemStack stack) {
        return !stack.isEmpty() && POLICY.retired.contains(BuiltInRegistries.ITEM.getKey(stack.getItem()).toString());
    }
    public static boolean blockedTradeResult(ItemStack stack) {
        return !stack.isEmpty() && POLICY.blockedTradeResults.contains(BuiltInRegistries.ITEM.getKey(stack.getItem()).toString());
    }
    public static ItemStack canonical(ItemStack stack) {
        if(stack.isEmpty())return stack;
        String id=POLICY.aliases.get(BuiltInRegistries.ITEM.getKey(stack.getItem()).toString());
        if(id==null)return stack;
        var item=BuiltInRegistries.ITEM.get(ResourceLocation.parse(id));
        return item==Items.AIR ? stack : stack.transmuteCopy(item);
    }
    public static ItemCost canonical(ItemCost cost) {
        var original=cost.item().value();String id=POLICY.aliases.get(BuiltInRegistries.ITEM.getKey(original).toString());
        if(id==null)return cost;
        var item=BuiltInRegistries.ITEM.get(ResourceLocation.parse(id));
        return item==Items.AIR ? cost : new ItemCost(item.builtInRegistryHolder(),cost.count(),cost.components());
    }
}
