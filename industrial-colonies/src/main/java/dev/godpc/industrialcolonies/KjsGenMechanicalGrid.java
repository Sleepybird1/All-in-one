package dev.godpc.industrialcolonies;

import com.zizazr.kjsgen.core.CreateSpecialModel;
import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeDefinition;

/**
 * Small model adapter for KJSGen's Create mechanical-crafting grid.
 *
 * <p>KJSGen 2.0.5 already persists dynamic cells as {@code cell_<row>_<column>}
 * and its native code generator reads {@code gridW}/{@code gridH} up to
 * {@link CreateSpecialModel#GRID_MAX}. The bundled grid canvas simply has no
 * controls that mutate those parameters. Keeping the mutation here lets the
 * client mixin stay presentation-only and preserves every existing cell while
 * a recipe grows or shrinks. Shrinking changes only the visible dimensions;
 * cells outside the rectangle remain in the recipe so expanding it again is
 * lossless.</p>
 */
public final class KjsGenMechanicalGrid {
    public static final String WIDTH_PARAMETER = "gridW";
    public static final String HEIGHT_PARAMETER = "gridH";
    public static final int GRID_POLICY_MAX = 7;

    private KjsGenMechanicalGrid() {
    }

    public static boolean supports(RecipeInstance recipe, RecipeTypeDefinition type) {
        if (recipe == null || type == null || !"grid".equals(type.editorKind())) {
            return false;
        }
        return MachineRecipeRouting.familyForEditorType(recipe.typeId())
                .map(family -> "mechanical_crafting".equals(family.id()))
                .orElse(false);
    }

    public static int columns(RecipeInstance recipe, RecipeTypeDefinition type) {
        return CreateSpecialModel.gridW(recipe, type);
    }

    public static int rows(RecipeInstance recipe, RecipeTypeDefinition type) {
        return CreateSpecialModel.gridH(recipe, type);
    }

    public static int maximumSize() {
        return Math.min(GRID_POLICY_MAX, CreateSpecialModel.GRID_MAX);
    }

    public static boolean addColumn(RecipeInstance recipe, RecipeTypeDefinition type) {
        return grow(recipe, WIDTH_PARAMETER, columns(recipe, type));
    }

    public static boolean addRow(RecipeInstance recipe, RecipeTypeDefinition type) {
        return grow(recipe, HEIGHT_PARAMETER, rows(recipe, type));
    }

    public static boolean removeColumn(RecipeInstance recipe, RecipeTypeDefinition type) {
        return shrink(recipe, WIDTH_PARAMETER, columns(recipe, type));
    }

    public static boolean removeRow(RecipeInstance recipe, RecipeTypeDefinition type) {
        return shrink(recipe, HEIGHT_PARAMETER, rows(recipe, type));
    }

    private static boolean grow(RecipeInstance recipe, String parameter, int current) {
        if (current >= maximumSize()) {
            return false;
        }
        recipe.setParam(parameter, Integer.toString(current + 1));
        return true;
    }

    private static boolean shrink(RecipeInstance recipe, String parameter, int current) {
        if (current <= 1) {
            return false;
        }
        recipe.setParam(parameter, Integer.toString(current - 1));
        return true;
    }
}
