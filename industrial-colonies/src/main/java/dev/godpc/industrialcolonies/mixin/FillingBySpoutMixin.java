package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.AllRecipeTypes;
import com.simibubi.create.content.fluids.spout.FillingBySpout;
import dev.godpc.industrialcolonies.CreateRecipeStageGate;
import net.minecraft.world.item.crafting.RecipeInput;
import net.minecraft.world.item.crafting.RecipeManager;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

import java.util.List;

/** Closes FillingBySpout's two direct-list lookups that bypass AllRecipeTypes.find. */
@Mixin(FillingBySpout.class)
public abstract class FillingBySpoutMixin {
    @SuppressWarnings("rawtypes")
    @Redirect(
            method = {
                    "getRequiredAmountForItem(Lnet/minecraft/world/level/Level;"
                            + "Lnet/minecraft/world/item/ItemStack;"
                            + "Lnet/neoforged/neoforge/fluids/FluidStack;)I",
                    "lambda$fillItem$1(Lnet/minecraft/world/level/Level;"
                            + "Lnet/minecraft/world/item/crafting/SingleRecipeInput;"
                            + "Lnet/neoforged/neoforge/fluids/FluidStack;)"
                            + "Lnet/minecraft/world/item/crafting/RecipeHolder;"
            },
            at = @At(
                    value = "INVOKE",
                    target = "Lnet/minecraft/world/item/crafting/RecipeManager;getRecipesFor("
                            + "Lnet/minecraft/world/item/crafting/RecipeType;"
                            + "Lnet/minecraft/world/item/crafting/RecipeInput;"
                            + "Lnet/minecraft/world/level/Level;)Ljava/util/List;"
            )
    )
    private static List industrialColonies$allowedFillingRecipes(
            RecipeManager manager,
            RecipeType<?> ignoredType,
            RecipeInput input,
            Level level
    ) {
        return CreateRecipeStageGate.matchingAllowedRecipes(AllRecipeTypes.FILLING, input, level);
    }
}
