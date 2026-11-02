package dev.godpc.industrialcolonies;

import com.google.gson.Gson;
import com.google.gson.annotations.SerializedName;
import com.simibubi.create.AllRecipeTypes;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Optional;

/**
 * The single source of truth for editor schemas and runtime recipe registrations.
 */
public record TieredRecipeCatalog(
        @SerializedName("schema_version") int schemaVersion,
        String model,
        List<Tier> tiers,
        @SerializedName("recipe_families") List<RecipeFamily> recipeFamilies
) {
    private static final String RESOURCE = "/data/industrial_colonies/tier_recipe_environments.json";

    public static TieredRecipeCatalog load() {
        try (InputStream stream = TieredRecipeCatalog.class.getResourceAsStream(RESOURCE)) {
            if (stream == null) {
                throw new IllegalStateException("Missing tier recipe catalog: " + RESOURCE);
            }

            TieredRecipeCatalog catalog = new Gson().fromJson(
                    new InputStreamReader(stream, StandardCharsets.UTF_8), TieredRecipeCatalog.class);
            if (catalog == null || catalog.tiers == null || catalog.recipeFamilies == null) {
                throw new IllegalStateException("Invalid tier recipe catalog: " + RESOURCE);
            }
            if (catalog.schemaVersion < 2) {
                throw new IllegalStateException("Unsupported machine recipe catalog schema: " + catalog.schemaVersion);
            }
            return catalog;
        } catch (IOException exception) {
            throw new IllegalStateException("Unable to read tier recipe catalog: " + RESOURCE, exception);
        }
    }

    public record Tier(
            String id,
            @SerializedName("display_name") String displayName,
            @SerializedName("casing_item") String casingItem
    ) {
    }

    public record RecipeFamily(
            String id,
            @SerializedName("display_name") String displayName,
            String icon,
            String schema,
            @SerializedName("create_type") String createType,
            List<Machine> machines
    ) {
        public RecipeFamily {
            machines = machines == null ? List.of() : List.copyOf(machines);
        }

        public AllRecipeTypes baseType() {
            return AllRecipeTypes.valueOf(createType);
        }

        /** Only families with real alternatives need an exclusive machine selector. */
        public boolean supportsMachineSelection() {
            return machines.size() > 1;
        }

        public Optional<Machine> machine(String id) {
            return machines.stream().filter(machine -> machine.id().equals(id)).findFirst();
        }

        public Machine baseMachine() {
            return machine("base").orElse(null);
        }

        /**
         * Maps the old tier × family matrix onto real machine identities. A
         * valid Encased variant keeps its exact identity. A nonsensical old
         * pair (for example andesite_pressing) safely aliases to the native
         * Create machine instead of becoming unusable.
         */
        public Machine machineForLegacyTier(Tier tier) {
            if (!supportsMachineSelection()) {
                return null;
            }
            return machine(tier.id()).orElseGet(this::baseMachine);
        }
    }

    public record Machine(
            String id,
            @SerializedName("display_name") String displayName,
            String item,
            String tier,
            @SerializedName("block_ids") List<String> blockIds
    ) {
        public Machine {
            blockIds = blockIds == null ? List.of() : List.copyOf(blockIds);
        }

        public boolean isBase() {
            return "base".equals(id);
        }
    }
}
