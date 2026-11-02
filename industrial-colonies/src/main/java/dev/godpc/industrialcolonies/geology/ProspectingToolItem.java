package dev.godpc.industrialcolonies.geology;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.core.component.DataComponents;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import java.util.ArrayList;
import java.util.Collections;

/** Directional survival hints from existing observations, without generating terrain. */
public final class ProspectingToolItem extends Item {
    public ProspectingToolItem(Properties properties) { super(properties); }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        var stack = player.getItemInHand(hand);
        if (!(player instanceof net.minecraft.server.level.ServerPlayer server))
            return InteractionResultHolder.success(stack);
        var families = new ArrayList<String>();
        for (var entry : GeologyConfig.array(GeologyConfig.get().deposits(), "deposits")) {
            var row = entry.getAsJsonObject();
            families.add(row.get("id").getAsString());
        }
        Collections.sort(families);
        if (families.isEmpty()) return InteractionResultHolder.pass(stack);
        var data = stack.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
        String selected = data.getString("ProspectingResource");
        if (!families.contains(selected)) selected = families.contains("sphalerite") ? "sphalerite" : families.getFirst();
        if (player.isShiftKeyDown()) {
            ProspectingSearch.cancel(server);
            selected = families.get((families.indexOf(selected) + 1) % families.size());
            data.putString("ProspectingResource", selected);
            stack.set(DataComponents.CUSTOM_DATA, CustomData.of(data));
            player.displayClientMessage(Component.literal("Selected resource: " + selected.replace('_', ' ')), true);
        } else ProspectingSearch.request(server, selected);
        player.getCooldowns().addCooldown(this, 20);
        return InteractionResultHolder.consume(stack);
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        if (context.getPlayer() == null) return InteractionResult.PASS;
        if (!(context.getLevel() instanceof ServerLevel level)) return InteractionResult.SUCCESS;
        var pos = context.getClickedPos();
        if(level.getBlockEntity(pos) instanceof MiningNodes.NodeEntity node){
            node.requestYield((net.minecraft.server.level.ServerPlayer)context.getPlayer());
            context.getPlayer().getCooldowns().addCooldown(this,20);
            return InteractionResult.CONSUME;
        }
        String host = BuiltInRegistries.BLOCK.getKey(level.getBlockState(pos).getBlock()).toString();
        String family = null;
        for (var entry : GeologyConfig.array(GeologyConfig.get().deposits(), "deposits")) {
            var row = entry.getAsJsonObject();
            if (host.equals(GeologyConfig.string(row, "hostRock", ""))) {
                family = row.get("id").getAsString();
                break;
            }
        }
        if (family == null) {
            context.getPlayer().displayClientMessage(Component.translatable("message.industrial_colonies.prospecting.sample"), true);
            return InteractionResult.CONSUME;
        }
        var source = NearbyVeinClues.nearest(level, family, pos.getX(), pos.getZ());
        Component result;
        if (source.isEmpty()) {
            result = Component.translatable("message.industrial_colonies.prospecting.unknown");
        } else if (source.get().distanceSquared() <= 16L * 16L) {
            result = Component.translatable("message.industrial_colonies.prospecting.close");
        } else {
            var point = source.get();
            String direction = ProspectingBearing.roughDirection(level.getSeed(), family, pos.getX(), pos.getZ(),
                    (long) point.x() - pos.getX(), (long) point.z() - pos.getZ());
            result = Component.translatable("message.industrial_colonies.prospecting.direction",
                    Component.translatable("strength.industrial_colonies." + ProspectingBearing.strength(point.distanceSquared())),
                    Component.translatable("direction.industrial_colonies." + direction));
        }
        context.getPlayer().displayClientMessage(result, true);
        context.getPlayer().getCooldowns().addCooldown(this, 10);
        return InteractionResult.CONSUME;
    }
}
