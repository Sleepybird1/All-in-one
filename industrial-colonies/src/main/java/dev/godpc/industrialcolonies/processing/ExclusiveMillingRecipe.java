package dev.godpc.industrialcolonies.processing;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import com.simibubi.create.content.kinetics.millstone.MillingRecipe;
import com.simibubi.create.content.processing.recipe.ProcessingOutput;
import com.simibubi.create.content.processing.recipe.ProcessingRecipeParams;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeSerializer;

import java.util.ArrayList;
import java.util.List;

/**
 * Native Create milling, but results are mutually exclusive weighted alternatives.
 * The recipe remains in Create's MILLING type so millstones and the normal JEI category discover it.
 * Crude milling is deliberately distinct from the same rock's proper crushing-to-dust recipe.
 * recovery_chance is the separate chance to recover anything. Results each have count=1;
 * their chance values form one categorical distribution (PGM: Os .70 / Pt .25 / Ir .05).
 */
public final class ExclusiveMillingRecipe extends MillingRecipe {
    private final double recoveryChance;

    public ExclusiveMillingRecipe(ProcessingRecipeParams params, double recoveryChance) {
        super(params);
        this.recoveryChance = recoveryChance;
    }
    public double recoveryChance() { return recoveryChance; }

    @Override public RecipeSerializer<?> getSerializer() { return ProcessingRecipeRuntime.EXCLUSIVE_MILLING.get(); }

    @Override public List<String> validate() {
        List<String> errors = new ArrayList<>(super.validate());
        try {
            ExclusiveRecovery.validate(recoveryChance, weights(getRollableResults()));
            for (ProcessingOutput output : getRollableResults()) {
                if (output.getStack().isEmpty() || output.getStack().getCount() != 1)
                    errors.add("Exclusive milling outputs must be nonempty count=1 items");
            }
            if (!getFluidResults().isEmpty()) errors.add("Exclusive milling cannot also emit fluids");
        } catch (IllegalArgumentException exception) { errors.add(exception.getMessage()); }
        return errors;
    }

    @Override public List<ItemStack> rollResults(RandomSource random) {
        return rollResults(getRollableResults(), random);
    }

    @Override public List<ItemStack> rollResults(List<ProcessingOutput> outputs, RandomSource random) {
        // Deliberately never call super: its independent per-output rolls can yield all three PGMs.
        int index = ExclusiveRecovery.select(recoveryChance, weights(outputs), random.nextDouble(), random.nextDouble());
        if (index < 0) return List.of();
        ItemStack result = outputs.get(index).getStack().copy();
        if (result.isEmpty() || result.getCount() != 1) throw new IllegalStateException("Invalid exclusive milling output");
        return List.of(result);
    }

    private static double[] weights(List<ProcessingOutput> outputs) {
        double[] weights = new double[outputs.size()];
        for (int i = 0; i < outputs.size(); i++) weights[i] = outputs.get(i).getChance();
        return weights;
    }

    public static final class Serializer implements RecipeSerializer<ExclusiveMillingRecipe> {
        private static final MapCodec<ExclusiveMillingRecipe> CODEC = RecordCodecBuilder.<ExclusiveMillingRecipe>mapCodec(instance -> instance.group(
                ProcessingRecipeParams.CODEC.forGetter(ExclusiveMillingRecipe::getParams),
                Codec.doubleRange(0, 1).fieldOf("recovery_chance").forGetter(ExclusiveMillingRecipe::recoveryChance)
        ).apply(instance, ExclusiveMillingRecipe::new)).validate(recipe -> {
            List<String> errors = recipe.validate();
            return errors.isEmpty() ? com.mojang.serialization.DataResult.success(recipe)
                    : com.mojang.serialization.DataResult.error(() -> String.join("; ", errors));
        });
        private static final StreamCodec<RegistryFriendlyByteBuf, ExclusiveMillingRecipe> STREAM_CODEC = new StreamCodec<>() {
            @Override public ExclusiveMillingRecipe decode(RegistryFriendlyByteBuf buffer) {
                ExclusiveMillingRecipe recipe = new ExclusiveMillingRecipe(ProcessingRecipeParams.STREAM_CODEC.decode(buffer), buffer.readDouble());
                List<String> errors = recipe.validate();
                if (!errors.isEmpty()) throw new IllegalArgumentException(String.join("; ", errors));
                return recipe;
            }
            @Override public void encode(RegistryFriendlyByteBuf buffer, ExclusiveMillingRecipe recipe) {
                ProcessingRecipeParams.STREAM_CODEC.encode(buffer, recipe.getParams());
                buffer.writeDouble(recipe.recoveryChance());
            }
        };
        @Override public MapCodec<ExclusiveMillingRecipe> codec() { return CODEC; }
        @Override public StreamCodec<RegistryFriendlyByteBuf, ExclusiveMillingRecipe> streamCodec() { return STREAM_CODEC; }
    }
}
