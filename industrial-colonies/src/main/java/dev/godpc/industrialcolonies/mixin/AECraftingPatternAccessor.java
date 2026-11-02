package dev.godpc.industrialcolonies.mixin;

import appeng.crafting.pattern.AECraftingPattern;
import net.minecraft.world.item.crafting.RecipeHolder;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** Exposes the exact vanilla crafting recipe encoded by an AE2 crafting pattern. */
@Mixin(value = AECraftingPattern.class, remap = false)
public interface AECraftingPatternAccessor {
    @Accessor("recipeHolder")
    RecipeHolder<?> industrialColonies$getRecipeHolder();
}
