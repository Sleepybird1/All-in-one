package dev.godpc.industrialcolonies;

import com.mojang.serialization.MapCodec;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeSerializer;

import java.util.function.Supplier;

/**
 * Delegates every field, validation rule and network encoding operation to the
 * matching Create serializer, then attaches the tier-specific runtime identity.
 */
public final class TieredRecipeSerializer implements RecipeSerializer<Recipe<?>> {
    private final Supplier<RecipeSerializer<?>> delegate;
    private final Supplier<TieredRecipeBindings.Binding> binding;

    public TieredRecipeSerializer(
            Supplier<RecipeSerializer<?>> delegate,
            Supplier<TieredRecipeBindings.Binding> binding
    ) {
        this.delegate = delegate;
        this.binding = binding;
    }

    @Override
    @SuppressWarnings({"unchecked", "rawtypes"})
    public MapCodec<Recipe<?>> codec() {
        MapCodec<Recipe<?>> codec = (MapCodec) delegate.get().codec();
        return codec.xmap(this::bind, recipe -> recipe);
    }

    @Override
    @SuppressWarnings({"unchecked", "rawtypes"})
    public StreamCodec<RegistryFriendlyByteBuf, Recipe<?>> streamCodec() {
        StreamCodec<RegistryFriendlyByteBuf, Recipe<?>> codec = (StreamCodec) delegate.get().streamCodec();
        return codec.map(this::bind, recipe -> recipe);
    }

    private Recipe<?> bind(Recipe<?> recipe) {
        return TieredRecipeBindings.bind(recipe, binding.get());
    }
}
