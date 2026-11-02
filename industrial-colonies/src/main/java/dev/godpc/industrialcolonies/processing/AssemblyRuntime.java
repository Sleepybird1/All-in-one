package dev.godpc.industrialcolonies.processing;

import com.simibubi.create.AllDataComponents;
import com.simibubi.create.content.kinetics.mixer.MixingRecipe;
import com.simibubi.create.content.kinetics.mixer.CompactingRecipe;
import com.simibubi.create.content.kinetics.fan.processing.*;
import com.simibubi.create.content.processing.basin.BasinRecipe;
import com.simibubi.create.content.processing.recipe.*;
import com.simibubi.create.content.processing.sequenced.SequencedAssemblyRecipe;
import dev.godpc.industrialcolonies.*;
import dev.godpc.industrialcolonies.mixin.AssemblyRecipeAccessor;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.level.Level;
import net.neoforged.neoforge.common.crafting.DataComponentIngredient;
import java.util.*;

/** Resolve every step by its native assembly component; never cache a result supplier across workpieces. */
public final class AssemblyRuntime {
    private static final Map<BasinRecipe, Match> BASIN_STEPS = Collections.synchronizedMap(new WeakHashMap<>());
    public record Match(RecipeHolder<SequencedAssemblyRecipe> parent, ProcessingRecipe<?, ?> step, ItemStack carrier) {
        public ItemStack advance(Level level) {
            return ((AssemblyRecipeAccessor)parent.value()).industrialColonies$advance(parent.id(), carrier, level.random);
        }
        public int ticks() { return Math.max(1, step.getProcessingDuration() == 0 ? 100 : step.getProcessingDuration()); }
        public String key() { return parent.id() + "/" + carrier.get(AllDataComponents.SEQUENCED_ASSEMBLY) + "/" + carrier.getCount(); }
    }
    public static List<Match> matches(Level level, ItemStack carrier) {
        if (carrier.isEmpty()) return List.of();
        var matches = new ArrayList<Match>();
        for (var parent : CreateRecipeStageGate.allowedSequencedAssemblies(level)) {
            var access = (AssemblyRecipeAccessor)parent.value();
            if (!access.industrialColonies$applies(parent.id(), carrier)) continue;
            var step = access.industrialColonies$next(carrier).getRecipe();
            if (!CreateRecipeStageGate.machineMatches(step, CreateMachineContext.current())) continue;
            matches.add(new Match(parent, step, carrier.copy()));
        }
        return matches;
    }
    public static boolean active(ItemStack stack) { return stack.has(AllDataComponents.SEQUENCED_ASSEMBLY); }
    public static String fanMode(FanProcessingType type) {
        if (type == AllFanProcessingTypes.SMOKING) return "smoking";
        if (type == AllFanProcessingTypes.BLASTING) return "blasting";
        if (type == AllFanProcessingTypes.SPLASHING) return "splashing";
        if (type == AllFanProcessingTypes.HAUNTING) return "haunting";
        return "";
    }
    public static Optional<Match> fan(Level level, ItemStack carrier, FanProcessingType type) {
        return matches(level, carrier).stream().filter(m -> m.step() instanceof AssemblyFanRecipes.FanRecipe f
                && f.mode.equals(fanMode(type))).findFirst();
    }
    public static List<ItemStack> fanResults(Match match, Level level) {
        var result = new ArrayList<ItemStack>();
        for (int n = 0; n < match.carrier().getCount(); n++) {
            ItemStack next = match.advance(level);
            if (!next.isEmpty()) result.add(next);
        }
        return result;
    }
    public static BasinRecipe prepareBasin(Match match, Level level) {
        if (!(match.step() instanceof BasinRecipe original)) throw new IllegalArgumentException("Not a basin stage");
        var params = new BasinParams(original, match.carrier());
        BasinRecipe prepared = original instanceof MixingRecipe ? new MixingRecipe(params) : new CompactingRecipe(params);
        var binding = TieredRecipeBindings.get(original);
        if (binding != null) TieredRecipeBindings.bind(prepared, binding);
        prepared.enforceNextResult(() -> match.advance(level));
        BASIN_STEPS.put(prepared, match);
        return prepared;
    }
    public static Match basinMatch(BasinRecipe recipe) { return BASIN_STEPS.get(recipe); }
    private static final class BasinParams extends ProcessingRecipeParams {
        BasinParams(BasinRecipe original, ItemStack carrier) {
            ingredients.addAll(original.getIngredients());
            // A raw item of the same type or another assembly's workpiece must not satisfy this stage.
            ingredients.set(0, DataComponentIngredient.of(true, carrier.copyWithCount(1)));
            fluidIngredients.addAll(original.getFluidIngredients());
            results.addAll(original.getRollableResults());
            processingDuration = original.getProcessingDuration();
            requiredHeat = original.getRequiredHeat();
        }
    }
}
