package dev.godpc.industrialcolonies;

import java.util.Map;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;

/** Canonicalize only fresh duplicate food/crop/seed drops, never saved inventory or unique dishes. */
@EventBusSubscriber(modid="industrial_colonies")
public final class FoodPriorityDrops {
    private static final Map<String,String> REPLACEMENTS = Map.ofEntries(
        Map.entry("pamhc2crops:cabbageitem", "farmersdelight:cabbage"),
        Map.entry("pamhc2crops:onionitem", "farmersdelight:onion"),
        Map.entry("pamhc2crops:riceitem", "farmersdelight:rice"),
        Map.entry("pamhc2crops:tomatoitem", "farmersdelight:tomato"),
        Map.entry("pamhc2foodcore:baconandeggsitem", "farmersdelight:bacon_and_eggs"),
        Map.entry("pamhc2foodcore:friedeggitem", "farmersdelight:fried_egg"),
        Map.entry("pamhc2foodcore:fruitsaladitem", "farmersdelight:fruit_salad"),
        Map.entry("pamhc2foodcore:melonjuiceitem", "farmersdelight:melon_juice"),
        Map.entry("pamhc2foodcore:melonpopsicleitem", "farmersdelight:melon_popsicle"),
        Map.entry("pamhc2foodcore:noodlesoupitem", "farmersdelight:noodle_soup"),
        Map.entry("pamhc2foodcore:pumpkinsoupitem", "farmersdelight:pumpkin_soup"),
        Map.entry("pamhc2foodextended:applecideritem", "farmersdelight:apple_cider"),
        Map.entry("pamhc2foodextended:friedriceitem", "farmersdelight:fried_rice"),
        Map.entry("pamhc2foodextended:mixedsaladitem", "farmersdelight:mixed_salad"),
        Map.entry("pamhc2foodextended:vegetablesoupitem", "farmersdelight:vegetable_soup"),
        Map.entry("pamhc2foodcore:hotchocolateitem", "farmersdelight:hot_cocoa"),
        Map.entry("pamhc2foodcore:pastaitem", "farmersdelight:raw_pasta"),
        Map.entry("pamhc2foodcore:basichamburgeritem", "farmersdelight:hamburger"),
        Map.entry("pamhc2foodcore:basicchickensandwichitem", "farmersdelight:chicken_sandwich"),
        Map.entry("pamhc2crops:cabbageseeditem", "farmersdelight:cabbage_seeds"),
        Map.entry("pamhc2crops:tomatoseeditem", "farmersdelight:tomato_seeds"),
        Map.entry("pamhc2crops:onionseeditem", "farmersdelight:onion"),
        Map.entry("pamhc2crops:riceseeditem", "farmersdelight:rice"));
    @SubscribeEvent
    public static void spawned(EntityJoinLevelEvent event) {
        if(event.getLevel().isClientSide() || event.loadedFromDisk()
                || !(event.getEntity() instanceof ItemEntity entity)) return;
        var original = entity.getItem();
        String replacement = REPLACEMENTS.get(BuiltInRegistries.ITEM.getKey(original.getItem()).toString());
        if(replacement == null) return;
        var key = ResourceLocation.parse(replacement);
        if(!BuiltInRegistries.ITEM.containsKey(key)) return;
        var item = BuiltInRegistries.ITEM.get(key);
        int count = original.getCount();
        // Preserve oversized stacks rather than deleting overflow when target stack limits differ.
        if(count > item.getDefaultMaxStackSize()) return;
        entity.setItem(new ItemStack(item, count));
    }
}
