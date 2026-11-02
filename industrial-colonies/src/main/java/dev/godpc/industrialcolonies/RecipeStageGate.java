package dev.godpc.industrialcolonies;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.logging.LogUtils;
import dev.ftb.mods.ftbteams.api.FTBTeamsAPI;
import dev.ftb.mods.ftbteams.api.TeamStagesHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.ResourceManagerReloadListener;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.AddReloadListenerEvent;
import org.slf4j.Logger;

import java.io.IOException;
import java.io.Reader;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Shared, exact-recipe-id to MineColonies-research-stage mapping.
 *
 * <p>Consumers decide how to identify the responsible team. Player crafting
 * supplies a real {@link ServerPlayer}; owned machines can resolve their owner
 * before testing the stage returned by {@link #requiredStage(ResourceLocation)}.
 * Unmapped recipes are deliberately outside this gate.</p>
 */
public final class RecipeStageGate {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final ResourceLocation MANIFEST = ResourceLocation.fromNamespaceAndPath(
            IndustrialColonies.MOD_ID, "progression/recipe_stages.json");

    private static volatile Map<ResourceLocation, ResourceLocation> requiredStages = Map.of();

    private RecipeStageGate() {
    }

    public static void register() {
        NeoForge.EVENT_BUS.addListener(RecipeStageGate::addReloadListener);
    }

    private static void addReloadListener(AddReloadListenerEvent event) {
        event.addListener((ResourceManagerReloadListener) RecipeStageGate::reload);
    }

    private static void reload(ResourceManager resourceManager) {
        Map<ResourceLocation, ResourceLocation> loaded = loadManifest(resourceManager);
        requiredStages = loaded;
        MekanismRecipeStageGate.clearRecipeIdCache();
        CreateRecipeStageGate.clearRecipeIdCache();
        MachineRecipeStageGate.clearRecipeIdCache();
        LOGGER.info("Loaded {} shared recipe-stage mappings", loaded.size());
    }

    private static Map<ResourceLocation, ResourceLocation> loadManifest(ResourceManager resourceManager) {
        try (Reader reader = resourceManager.getResourceOrThrow(MANIFEST).openAsReader()) {
            JsonElement rootElement = JsonParser.parseReader(reader);
            if (!rootElement.isJsonObject()) {
                throw new IllegalStateException("Recipe-stage manifest root must be an object");
            }
            JsonElement recipesElement = rootElement.getAsJsonObject().get("recipes");
            if (recipesElement == null || !recipesElement.isJsonObject()) {
                throw new IllegalStateException("Recipe-stage manifest is missing its recipes object");
            }

            Map<ResourceLocation, ResourceLocation> loaded = new LinkedHashMap<>();
            JsonObject recipes = recipesElement.getAsJsonObject();
            for (Map.Entry<String, JsonElement> entry : recipes.entrySet()) {
                if (!entry.getValue().isJsonPrimitive() || !entry.getValue().getAsJsonPrimitive().isString()) {
                    throw new IllegalStateException("Stage id for recipe " + entry.getKey() + " must be a string");
                }
                ResourceLocation recipeId = requireResourceLocation(entry.getKey(), "recipe");
                ResourceLocation researchId = requireResourceLocation(entry.getValue().getAsString(), "research");
                if (!IndustrialColonies.MOD_ID.equals(researchId.getNamespace())) {
                    throw new IllegalStateException("Research id must belong to " + IndustrialColonies.MOD_ID
                            + ": " + researchId);
                }
                loaded.put(recipeId, researchId);
            }
            return Map.copyOf(loaded);
        } catch (IOException exception) {
            throw new IllegalStateException("Unable to load " + MANIFEST, exception);
        }
    }

    private static ResourceLocation requireResourceLocation(String value, String kind) {
        ResourceLocation id = ResourceLocation.tryParse(value);
        if (id == null) {
            throw new IllegalStateException("Invalid " + kind + " resource id in " + MANIFEST + ": " + value);
        }
        return id;
    }

    public static ResourceLocation requiredStage(ResourceLocation recipeId) {
        return requiredStages.get(recipeId);
    }

    /**
     * Tests a real server player's FTB team for the exact stage assigned to
     * the exact recipe holder id. Missing manager/team/stage fails closed.
     */
    public static boolean canUse(ServerPlayer player, RecipeHolder<?> recipe) {
        return canUse(player.getUUID(), recipe.id());
    }

    /** Tests the current FTB team for a persistently owned machine's player UUID. */
    public static boolean canUse(UUID playerId, ResourceLocation recipeId) {
        ResourceLocation requiredStage = requiredStages.get(recipeId);
        if (requiredStage == null) {
            return true;
        }

        FTBTeamsAPI.API api = FTBTeamsAPI.api();
        if (!api.isManagerLoaded()) {
            return false;
        }
        return api.getManager().getTeamForPlayerID(playerId)
                .filter(team -> TeamStagesHelper.hasTeamStage(team, requiredStage.toString()))
                .isPresent();
    }
}
