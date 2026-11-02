package dev.godpc.industrialcolonies.research;

import dev.godpc.industrialcolonies.IndustrialColonies;
import net.minecraft.resources.ResourceLocation;

import java.util.Set;

/**
 * Stable identifiers used by the custom MineColonies research integration.
 */
public final class IndustrialResearchIds {
    public static final ResourceLocation TECH_TREE = ResourceLocation.fromNamespaceAndPath(
            IndustrialColonies.MOD_ID, "tech_tree");

    public static final Set<ResourceLocation> LEGACY_BRANCHES = Set.of(
            legacyBranch("mechanical_foundations"),
            legacyBranch("steam_and_rail"),
            legacyBranch("steel_and_metallurgy"),
            legacyBranch("petroleum_and_engines"),
            legacyBranch("industrial_electronics"),
            legacyBranch("electrical_grid"),
            legacyBranch("factory_engineering"),
            legacyBranch("digital_computing"),
            legacyBranch("digital_logistics"),
            legacyBranch("nuclear_engineering"),
            legacyBranch("nuclear_fuel_cycle")
    );

    private IndustrialResearchIds() {
    }

    public static boolean isTechTree(ResourceLocation branch) {
        return TECH_TREE.equals(branch);
    }

    private static ResourceLocation legacyBranch(String path) {
        return ResourceLocation.fromNamespaceAndPath(IndustrialColonies.MOD_ID, path);
    }
}
