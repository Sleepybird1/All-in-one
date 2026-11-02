package dev.godpc.industrialcolonies.client.jei;

import com.simibubi.create.AllBlocks;
import com.simibubi.create.compat.jei.category.sequencedAssembly.SequencedAssemblySubCategory;
import com.simibubi.create.content.processing.sequenced.SequencedRecipe;
import com.simibubi.create.content.kinetics.mixer.MixingRecipe;
import com.simibubi.create.content.processing.basin.BasinRecipe;
import dev.godpc.industrialcolonies.processing.AssemblyFanRecipes;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import com.simibubi.create.compat.jei.category.CreateRecipeCategory;
import mezz.jei.api.gui.builder.IRecipeLayoutBuilder;
import mezz.jei.api.recipe.IFocusGroup;
import mezz.jei.api.recipe.RecipeIngredientRole;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.ItemStack;
import com.mojang.serialization.JsonOps;
import java.util.*;

/** Explicit machine/heat/time display for the additional assembly operations. */
public final class ExtendedAssemblyCategory extends SequencedAssemblySubCategory {
    public ExtendedAssemblyCategory() { super(80); }
    @Override public void setRecipe(IRecipeLayoutBuilder builder, SequencedRecipe<?> sequence, IFocusGroup focuses, int x) {
        var recipe=sequence.getRecipe();
        // Collapse expanded counted ingredients into one visible counted slot per distinct input.
        var ingredients=new LinkedHashMap<String,Ingredient>();
        var counts=new HashMap<String,Integer>();
        for(int n=1;n<recipe.getIngredients().size();n++) {
            var ingredient=recipe.getIngredients().get(n);
            String key=Ingredient.CODEC.encodeStart(JsonOps.INSTANCE,ingredient).getOrThrow().toString();
            ingredients.putIfAbsent(key,ingredient);counts.merge(key,1,Integer::sum);
        }
        int slot=0;
        for(var entry:ingredients.entrySet()) {
            var stacks=Arrays.stream(entry.getValue().getItems()).map(s->s.copyWithCount(counts.get(entry.getKey()))).toList();
            builder.addSlot(RecipeIngredientRole.INPUT,x+3+(slot%4)*19,15+(slot/4)*19)
                .setBackground(CreateRecipeCategory.getRenderedSlot(),-1,-1).addItemStacks(stacks);
            slot++;
        }
        for(var fluid:recipe.getFluidIngredients()) {
            CreateRecipeCategory.addFluidSlot(builder,x+3+(slot%4)*19,15+(slot/4)*19,fluid);slot++;
        }
    }
    @Override public void draw(SequencedRecipe<?> sequence, GuiGraphics graphics, double x, double y, int index) {
        var recipe = sequence.getRecipe();
        var machine = recipe instanceof MixingRecipe ? AllBlocks.MECHANICAL_MIXER
                : recipe instanceof BasinRecipe ? AllBlocks.MECHANICAL_PRESS : AllBlocks.ENCASED_FAN;
        var binding=dev.godpc.industrialcolonies.TieredRecipeBindings.get(recipe);
        var icon=binding!=null && binding.machine()!=null
                ? new net.minecraft.world.item.ItemStack(net.minecraft.core.registries.BuiltInRegistries.ITEM.get(
                    net.minecraft.resources.ResourceLocation.parse(binding.machine().item()))) : machine.asStack();
        graphics.renderItem(icon, 18, 67);
        String operation = recipe instanceof AssemblyFanRecipes.FanRecipe fan ? fan.mode
                : recipe instanceof MixingRecipe ? "Mixing" : "Compacting";
        var font = Minecraft.getInstance().font;
        graphics.drawString(font, operation, 2, 54, 0xFF404040, false);
        if (recipe instanceof BasinRecipe) {
            graphics.renderItem(AllBlocks.BASIN.asStack(), 45, 67);
            graphics.drawString(font, recipe.getRequiredHeat().getSerializedName(), 2, 86, 0xFF404040, false);
        }
        graphics.drawString(font, recipe.getProcessingDuration() + " ticks", 2, 100, 0xFF404040, false);
    }
}
