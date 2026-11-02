package dev.godpc.industrialcolonies.mixin;
import com.simibubi.create.content.processing.sequenced.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

@Mixin(SequencedAssemblyRecipe.class)
public interface AssemblyRecipeAccessor {
    @Invoker("appliesTo") boolean industrialColonies$applies(ResourceLocation id, ItemStack stack);
    @Invoker("getNextRecipe") SequencedRecipe<?> industrialColonies$next(ItemStack stack);
    @Invoker("advance") ItemStack industrialColonies$advance(ResourceLocation id, ItemStack stack, RandomSource random);
}
