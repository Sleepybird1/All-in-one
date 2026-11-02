package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.AllBlocks;
import com.simibubi.create.content.kinetics.mixer.MixingRecipe;
import com.simibubi.create.content.kinetics.mixer.CompactingRecipe;
import com.simibubi.create.content.processing.basin.BasinRecipe;
import com.simibubi.create.content.processing.sequenced.IAssemblyRecipe;
import com.simibubi.create.compat.jei.category.sequencedAssembly.SequencedAssemblySubCategory;
import dev.godpc.industrialcolonies.client.jei.ExtendedAssemblyCategory;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.ItemLike;
import net.neoforged.neoforge.fluids.crafting.SizedFluidIngredient;
import org.spongepowered.asm.mixin.Mixin;
import java.util.*;
import java.util.function.Supplier;

@Mixin({MixingRecipe.class, CompactingRecipe.class})
public abstract class BasinAssemblyRecipeMixin implements IAssemblyRecipe {
    @Override public boolean supportsAssembly() {
        var recipe = (BasinRecipe)(Object)this;
        return !recipe.getIngredients().isEmpty() && recipe.getFluidResults().isEmpty() && recipe.getRollableResults().size() == 1;
    }
    @Override public Component getDescriptionForAssembly() {
        return Component.literal((Object)this instanceof MixingRecipe ? "Basin Mixing" : "Basin Compacting");
    }
    @Override public void addRequiredMachines(Set<ItemLike> machines) {
        machines.add(AllBlocks.BASIN.get());
        machines.add((Object)this instanceof MixingRecipe ? AllBlocks.MECHANICAL_MIXER.get() : AllBlocks.MECHANICAL_PRESS.get());
    }
    @Override public void addAssemblyIngredients(List<Ingredient> ingredients) {
        var all = ((BasinRecipe)(Object)this).getIngredients();
        ingredients.addAll(all.subList(1, all.size()));
    }
    @Override public void addAssemblyFluidIngredients(List<SizedFluidIngredient> ingredients) {
        ingredients.addAll(((BasinRecipe)(Object)this).getFluidIngredients());
    }
    @Override public Supplier<Supplier<SequencedAssemblySubCategory>> getJEISubCategory() { return () -> ExtendedAssemblyCategory::new; }
}
