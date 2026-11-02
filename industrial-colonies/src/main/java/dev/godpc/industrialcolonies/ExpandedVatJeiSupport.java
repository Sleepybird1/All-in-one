package dev.godpc.industrialcolonies;

import com.drmangotea.tfmg.recipes.VatMachineRecipe;
import com.drmangotea.tfmg.registry.TFMGGuiTextures;
import com.simibubi.create.compat.jei.category.CreateRecipeCategory;
import com.simibubi.create.foundation.item.ItemHelper;
import mezz.jei.api.gui.builder.IRecipeLayoutBuilder;
import mezz.jei.api.gui.drawable.IDrawable;
import mezz.jei.api.recipe.RecipeIngredientRole;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.world.item.ItemStack;

import java.util.ArrayList;
import java.util.List;

/** Uses the same native ingredient condensation, fluid rendering and output tooltips as TFMG. */
public final class ExpandedVatJeiSupport {
    private ExpandedVatJeiSupport() { }
    public static boolean expanded(VatMachineRecipe recipe) {
        return ExpandedVatJeiLayout.expanded(ItemHelper.condenseIngredients(recipe.getIngredients()).size());
    }
    /** Exact counted requirements, using native artwork at the native three attachment positions. */
    public static void drawMachines(List<String> ids, GuiGraphics graphics) {
        for (var attachment : ExpandedVatJeiLayout.machineAttachments(ids)) {
            int x = attachment.x();
            TFMGGuiTextures.VAT_MACHINE.render(graphics, x, 0);
            switch (attachment.id()) {
                case "tfmg:mixing" -> TFMGGuiTextures.MIXER.render(graphics, x - 7, 32);
                case "tfmg:centrifuge" -> TFMGGuiTextures.CENTRIFUGE.render(graphics, x, 32);
                case "tfmg:electrode" -> TFMGGuiTextures.ELECTRODE.render(graphics, x + 9, 32);
                case "tfmg:graphite_electrode" -> TFMGGuiTextures.GRAPHITE_ELECTRODE.render(graphics, x + 8, 32);
                default -> throw new AssertionError("Validated attachment was lost");
            }
        }
    }
    public static void setRecipe(IRecipeLayoutBuilder builder, VatMachineRecipe recipe) {
        var items = ItemHelper.condenseIngredients(recipe.getIngredients());
        var fluids = recipe.getFluidIngredients();
        var itemOutputs = recipe.getRollableResults();
        var fluidOutputs = recipe.getFluidResults();
        // Never silently omit an imported ingredient or result that exceeds the physical/editor capacity.
        ExpandedVatJeiLayout.requireCapacity(items.size(), fluids.size(), itemOutputs.size(), fluidOutputs.size());
        for (int index = 0; index < fluids.size(); index++) {
            var position = ExpandedVatJeiLayout.fluidInput(index, fluids.size());
            CreateRecipeCategory.addFluidSlot(builder, position.x(), position.y(), fluids.get(index))
                    .setSlotName("expanded_vat_fluid_input_" + index);
        }
        for (int index = 0; index < items.size(); index++) {
            var condensed = items.get(index);
            var variants = new ArrayList<ItemStack>();
            // Native TFMG copies every alternative, including components, before setting the repeated-input count.
            for (ItemStack stack : condensed.getFirst().getItems()) {
                ItemStack copy = stack.copy();
                copy.setCount(condensed.getSecond().getValue());
                variants.add(copy);
            }
            var position = ExpandedVatJeiLayout.itemInput(index);
            builder.addSlot(RecipeIngredientRole.INPUT, position.x(), position.y())
                    .setBackground(CreateRecipeCategory.getRenderedSlot(), -1, -1)
                    .setSlotName("expanded_vat_item_input_" + index).addItemStacks(variants);
        }
        for (int index = 0; index < fluidOutputs.size(); index++) {
            var position = ExpandedVatJeiLayout.fluidOutput(index);
            CreateRecipeCategory.addFluidSlot(builder, position.x(), position.y(), fluidOutputs.get(index))
                    .setSlotName("expanded_vat_fluid_output_" + index);
        }
        for (int index = 0; index < itemOutputs.size(); index++) {
            var output = itemOutputs.get(index);
            var position = ExpandedVatJeiLayout.itemOutput(index);
            builder.addSlot(RecipeIngredientRole.OUTPUT, position.x(), position.y())
                    .setBackground(CreateRecipeCategory.getRenderedSlot(output), -1, -1)
                    .setSlotName("expanded_vat_item_output_" + index)
                    .addRichTooltipCallback(CreateRecipeCategory.addStochasticTooltip(output))
                    .addItemStack(output.getStack());
        }
    }
    /** This category has one shared size. Ordinary recipes retain their native coordinates in its left area. */
    public static IDrawable background(IDrawable nativeBackground) {
        return new IDrawable() {
            @Override public int getWidth() { return Math.max(ExpandedVatJeiLayout.WIDTH, nativeBackground.getWidth()); }
            @Override public int getHeight() { return Math.max(ExpandedVatJeiLayout.HEIGHT, nativeBackground.getHeight()); }
            @Override public void draw(GuiGraphics graphics, int x, int y) { nativeBackground.draw(graphics, x, y); }
        };
    }
}
