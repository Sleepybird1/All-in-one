package dev.godpc.industrialcolonies.food;

import com.mojang.logging.LogUtils;
import dev.godpc.industrialcolonies.IndustrialAttachments;
import dev.godpc.industrialcolonies.IndustrialColonies;
import java.util.OptionalInt;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.living.LivingEntityUseItemEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import org.slf4j.Logger;

/**
 * Rewards genuine cuisine variety with a small, bounded permanent-health bonus.
 *
 * <p>Eligibility deliberately uses {@link ItemStack#getFoodProperties} rather
 * than hard-coded mod item lists. Pam's HarvestCraft, Farmer's Delight, vanilla,
 * and future food mods therefore participate automatically. Identity is the
 * registry item id: consuming another copy or an NBT variant never farms the
 * same diversity point twice.</p>
 */
public final class FoodDiversityProgression {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final ResourceLocation MAX_HEALTH_MODIFIER_ID =
            ResourceLocation.fromNamespaceAndPath(IndustrialColonies.MOD_ID, "food_diversity_health");

    private FoodDiversityProgression() {
    }

    public static void register() {
        NeoForge.EVENT_BUS.addListener(FoodDiversityProgression::onFoodFinished);
        NeoForge.EVENT_BUS.addListener(FoodDiversityProgression::onPlayerLogin);
        NeoForge.EVENT_BUS.addListener(FoodDiversityProgression::onPlayerRespawn);
        NeoForge.EVENT_BUS.addListener(FoodDiversityProgression::onRegisterCommands);
        LOGGER.info(
                "Food diversity progression enabled: {} milestones, capped at +{} max health",
                FoodDiversityMilestones.UNIQUE_FOOD_MILESTONES.length,
                FoodDiversityMilestones.MAX_BONUS_HEALTH);
    }

    private static void onFoodFinished(LivingEntityUseItemEvent.Finish event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }

        ItemStack consumed = event.getItem();
        FoodProperties foodProperties = consumed.getFoodProperties(player);
        if (foodProperties == null || consumed.isEmpty()) {
            return;
        }

        ResourceLocation foodId = BuiltInRegistries.ITEM.getKey(consumed.getItem());
        FoodDiversityData current = player.getData(IndustrialAttachments.FOOD_DIVERSITY);
        if (current.hasEaten(foodId)) {
            return;
        }

        int previousBonus = FoodDiversityMilestones.bonusHealth(current.uniqueFoodCount());
        FoodDiversityData updated = current.withFood(foodId);
        player.setData(IndustrialAttachments.FOOD_DIVERSITY, updated);
        int updatedCount = updated.uniqueFoodCount();
        int updatedBonus = FoodDiversityMilestones.bonusHealth(updatedCount);
        reconcileMaxHealth(player, updatedCount);

        if (updatedBonus > previousBonus) {
            player.heal(updatedBonus - previousBonus);
            player.sendSystemMessage(Component.translatable(
                            "message.industrial_colonies.food_diversity.milestone",
                            updatedCount,
                            updatedBonus / 2)
                    .withStyle(ChatFormatting.GOLD));
        }

        showProgress(player, updatedCount, consumed.getHoverName(), true);
    }

    private static void onPlayerLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            reconcileMaxHealth(player, foodCount(player));
        }
    }

    private static void onPlayerRespawn(PlayerEvent.PlayerRespawnEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            reconcileMaxHealth(player, foodCount(player));
        }
    }

    private static void onRegisterCommands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("cuisine").executes(context -> {
            ServerPlayer player = context.getSource().getPlayerOrException();
            int count = foodCount(player);
            showProgress(player, count, Component.empty(), false);
            return count;
        }));
    }

    private static int foodCount(ServerPlayer player) {
        return player.getData(IndustrialAttachments.FOOD_DIVERSITY).uniqueFoodCount();
    }

    private static void reconcileMaxHealth(ServerPlayer player, int uniqueFoodCount) {
        AttributeInstance maxHealth = player.getAttribute(Attributes.MAX_HEALTH);
        if (maxHealth == null) {
            return;
        }

        int desiredBonus = FoodDiversityMilestones.bonusHealth(uniqueFoodCount);
        AttributeModifier existing = maxHealth.getModifier(MAX_HEALTH_MODIFIER_ID);
        if (desiredBonus == 0) {
            if (existing != null) {
                maxHealth.removeModifier(MAX_HEALTH_MODIFIER_ID);
            }
            return;
        }

        if (existing == null || existing.amount() != desiredBonus
                || existing.operation() != AttributeModifier.Operation.ADD_VALUE) {
            maxHealth.addOrReplacePermanentModifier(new AttributeModifier(
                    MAX_HEALTH_MODIFIER_ID,
                    desiredBonus,
                    AttributeModifier.Operation.ADD_VALUE));
        }
    }

    private static void showProgress(
            ServerPlayer player,
            int uniqueFoodCount,
            Component foodName,
            boolean actionBar) {
        OptionalInt next = FoodDiversityMilestones.nextMilestone(uniqueFoodCount);
        Component message;
        if (next.isPresent()) {
            int remaining = next.getAsInt() - uniqueFoodCount;
            message = actionBar
                    ? Component.translatable(
                            "message.industrial_colonies.food_diversity.new_food",
                            foodName,
                            uniqueFoodCount,
                            remaining)
                    : Component.translatable(
                            "message.industrial_colonies.food_diversity.progress",
                            uniqueFoodCount,
                            next.getAsInt(),
                            remaining);
        } else {
            message = Component.translatable(
                    "message.industrial_colonies.food_diversity.complete",
                    uniqueFoodCount,
                    FoodDiversityMilestones.MAX_BONUS_HEALTH / 2);
        }
        player.displayClientMessage(message.copy().withStyle(ChatFormatting.GREEN), actionBar);
    }
}
