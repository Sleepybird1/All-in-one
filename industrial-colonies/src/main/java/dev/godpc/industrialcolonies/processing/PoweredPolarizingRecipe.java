package dev.godpc.industrialcolonies.processing;

import com.drmangotea.tfmg.recipes.PolarizingRecipe;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import com.simibubi.create.content.processing.recipe.ProcessingRecipeParams;
import dev.godpc.industrialcolonies.AtmPolarizingPolicy;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.item.crafting.RecipeSerializer;
import java.util.ArrayList;
import java.util.List;

/** One real serializer, retaining TFMG's native POLARIZING recipe type and machine lookup. */
public final class PoweredPolarizingRecipe extends PolarizingRecipe {
    public static final String SERIALIZER_ID = "industrial_colonies:powered_polarizing";
    public static final Codec<Integer> POWER_CODEC = Codec.intRange(1, AtmPolarizingPolicy.MAX_POWER);
    private final int powerRequired;
    public PoweredPolarizingRecipe(ProcessingRecipeParams params, int powerRequired) {
        super(checkPower(params, powerRequired));
        this.powerRequired = powerRequired;
        AtmPolarizingPolicy.validateExplicitTicks(getProcessingDuration());
        List<String> errors = validate();
        if (!errors.isEmpty()) throw new IllegalArgumentException(String.join("; ", errors));
    }
    private static ProcessingRecipeParams checkPower(ProcessingRecipeParams params, int power) {
        AtmPolarizingPolicy.validatePower(power);
        return java.util.Objects.requireNonNull(params, "Polarizing parameters required");
    }
    public int powerRequired() { return powerRequired; }
    @Override public RecipeSerializer<?> getSerializer() { return ProcessingRecipeRuntime.POWERED_POLARIZING.get(); }
    // Deliberately inherit getType/getTypeInfo from native PolarizingRecipe: this is not a second machine route.
    @Override public List<String> validate() {
        List<String> errors = new ArrayList<>(super.validate());
        if (getIngredients().size() != 1 || getRollableResults().size() != 1
            || !getFluidIngredients().isEmpty() || !getFluidResults().isEmpty())
            errors.add("Powered polarization requires exactly one item input and one item result");
        else {
            var output = getRollableResults().getFirst();
            if (output.getStack().isEmpty() || output.getStack().getCount() != 1 || output.getChance() != 1)
                errors.add("Powered polarization result must be guaranteed and count one");
        }
        try { AtmPolarizingPolicy.validatePower(powerRequired); AtmPolarizingPolicy.validateExplicitTicks(getProcessingDuration()); }
        catch (IllegalArgumentException invalid) { errors.add(invalid.getMessage()); }
        return errors;
    }
    private record Fields(ProcessingRecipeParams params, int power) { }
    public static final class Serializer implements RecipeSerializer<PoweredPolarizingRecipe> {
        private static final MapCodec<Fields> FIELDS = RecordCodecBuilder.mapCodec(instance -> instance.group(
            ProcessingRecipeParams.CODEC.forGetter(Fields::params),
            POWER_CODEC.fieldOf("power_required").forGetter(Fields::power)
        ).apply(instance, Fields::new));
        private static final MapCodec<PoweredPolarizingRecipe> CODEC = FIELDS.flatXmap(fields -> {
            try { return DataResult.success(new PoweredPolarizingRecipe(fields.params(), fields.power())); }
            catch (IllegalArgumentException invalid) { return DataResult.error(invalid::getMessage); }
        }, recipe -> {
            List<String> errors = recipe.validate();
            return errors.isEmpty() ? DataResult.success(new Fields(recipe.getParams(), recipe.powerRequired()))
                : DataResult.error(() -> String.join("; ", errors));
        });
        private static final StreamCodec<RegistryFriendlyByteBuf, PoweredPolarizingRecipe> STREAM = new StreamCodec<>() {
            @Override public PoweredPolarizingRecipe decode(RegistryFriendlyByteBuf buffer) {
                ProcessingRecipeParams params = ProcessingRecipeParams.STREAM_CODEC.decode(buffer);
                return new PoweredPolarizingRecipe(params, buffer.readVarInt());
            }
            @Override public void encode(RegistryFriendlyByteBuf buffer, PoweredPolarizingRecipe recipe) {
                List<String> errors = recipe.validate();
                if (!errors.isEmpty()) throw new IllegalArgumentException(String.join("; ", errors));
                ProcessingRecipeParams.STREAM_CODEC.encode(buffer, recipe.getParams());
                buffer.writeVarInt(recipe.powerRequired());
            }
        };
        @Override public MapCodec<PoweredPolarizingRecipe> codec() { return CODEC; }
        @Override public StreamCodec<RegistryFriendlyByteBuf, PoweredPolarizingRecipe> streamCodec() { return STREAM; }
    }
}
