package dev.godpc.industrialcolonies.processing;

import blusunrize.immersiveengineering.api.crafting.RefineryRecipe;
import com.mojang.serialization.JsonOps;
import io.redspace.ironsspellbooks.recipe_types.alchemist_cauldron.BrewAlchemistCauldronRecipe;
import io.redspace.ironsspellbooks.registries.FluidRegistry;
import java.util.*;
import net.minecraft.core.HolderLookup;
import net.minecraft.resources.*;
import net.minecraft.world.item.crafting.*;
import net.neoforged.neoforge.fluids.FluidStack;

/** Detached, source-pinned potion consumer projection. No runtime registration. */
public final class PotionRecipeNormalizer {
    public record Rule(ResourceLocation id, String beforeSHA256, String afterSHA256) {}
    public record Result(Map<ResourceLocation, RecipeHolder<?>> recipes,
                         Map<ResourceLocation, String> status, int changed, boolean held) {}

    public static Result normalize(Map<ResourceLocation, RecipeHolder<?>> originals,
                                   HolderLookup.Provider registries, List<Rule> rules) {
        var proposed = new LinkedHashMap<>(originals);
        var statuses = new LinkedHashMap<ResourceLocation, String>();
        var ops = RegistryOps.create(JsonOps.INSTANCE, registries);
        int changed = 0;
        boolean held = false;
        for (var rule : rules) {
            if (statuses.containsKey(rule.id())) throw new IllegalArgumentException("Duplicate potion rule");
            var holder = originals.get(rule.id());
            if (holder == null) { statuses.put(rule.id(), "ABSENT"); continue; }
            try {
                var recipe = holder.value();
                if (!(recipe instanceof BrewAlchemistCauldronRecipe) && !(recipe instanceof RefineryRecipe))
                    throw new IllegalArgumentException("Unsupported potion recipe class");
                var before = Recipe.CODEC.encodeStart(ops, recipe).getOrThrow();
                String hash = EffectiveFluidNormalizer.fingerprint(before);
                if (hash.equals(rule.afterSHA256())) { statuses.put(rule.id(), "ALREADY_CANONICAL"); continue; }
                if (!hash.equals(rule.beforeSHA256())) throw new IllegalArgumentException("Effective recipe changed");
                var expected = before.getAsJsonObject().deepCopy();
                if (recipe instanceof BrewAlchemistCauldronRecipe cauldron) {
                    if (!cauldron.fluidIn().is(FluidRegistry.POTION_FLUID.get()))
                        throw new IllegalArgumentException("Not a Spellbooks potion input");
                    var projection = PotionCanonicalizer.project(cauldron.fluidIn());
                    if (!projection.status().equals("CANONICAL"))
                        throw new IllegalArgumentException(projection.status());
                    expected.add("base_fluid", FluidStack.CODEC.encodeStart(ops, projection.fluid()).getOrThrow());
                } else {
                    var input = expected.getAsJsonObject("input1");
                    if (!input.get("fluids").isJsonPrimitive()
                            || !input.get("fluids").getAsString().equals("immersiveengineering:potion"))
                        throw new IllegalArgumentException("Not an explicit IE potion input");
                    input.addProperty("fluids", "create:potion");
                }
                if (!EffectiveFluidNormalizer.fingerprint(expected).equals(rule.afterSHA256()))
                    throw new IllegalArgumentException("Unqualified potion projection");
                var replacement = Recipe.CODEC.parse(ops, expected).getOrThrow();
                if (replacement.getClass() != recipe.getClass()
                        || !expected.equals(Recipe.CODEC.encodeStart(ops, replacement).getOrThrow()))
                    throw new IllegalArgumentException("Potion codec changed other fields");
                proposed.put(rule.id(), new RecipeHolder<>(rule.id(), replacement));
                statuses.put(rule.id(), "CHANGED");
                changed++;
            } catch (RuntimeException e) {
                held = true;
                statuses.put(rule.id(), "HELD: " + e.getMessage());
            }
        }
        // Do not publish a partly converted consumer set when one source has changed.
        if (held) statuses.replaceAll((id, status) -> status.equals("CHANGED") ? "HELD_BATCH" : status);
        return new Result(Collections.unmodifiableMap(new LinkedHashMap<>(held ? originals : proposed)),
                Collections.unmodifiableMap(statuses), held ? 0 : changed, held);
    }
}
