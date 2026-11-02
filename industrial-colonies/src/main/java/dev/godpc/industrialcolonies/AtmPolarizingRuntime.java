package dev.godpc.industrialcolonies;

import com.drmangotea.tfmg.config.TFMGConfigs;
import com.drmangotea.tfmg.content.electricity.base.IElectric;
import com.drmangotea.tfmg.content.electricity.storage.AccumulatorBlockEntity;
import com.drmangotea.tfmg.content.electricity.utilities.polarizer.PolarizerBlockEntity;
import com.drmangotea.tfmg.recipes.PolarizingRecipe;
import dev.godpc.industrialcolonies.processing.PoweredPolarizingRecipe;
import com.google.gson.*;
import com.mojang.serialization.JsonOps;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.RegistryOps;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeHolder;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.TreeMap;

/** Actual installed native electrical facts; never fabricates a recipe FE amount or extracts twice. */
public final class AtmPolarizingRuntime {
    private AtmPolarizingRuntime() {}
    /** Broad identity first: malformed amounts/results must be held, never returned to the cheap native path. */
    public static boolean applies(ItemStack input, PolarizingRecipe recipe) {
        if (recipe instanceof PoweredPolarizingRecipe) return true;
        if (input.isEmpty()) return false;
        return AtmPolarizingPolicy.managed(BuiltInRegistries.ITEM.getKey(input.getItem()).toString(),
            recipe.getRollableResults().stream().map(result -> BuiltInRegistries.ITEM.getKey(result.getStack().getItem()).toString()).toList());
    }
    public static boolean validShape(ItemStack input, PolarizingRecipe recipe) {
        try { powerRequired(recipe); requiredTicks(recipe); }
        catch (IllegalArgumentException invalid) { return false; }
        if (!applies(input, recipe) || recipe.getProcessingDuration() < 0 || recipe.getProcessingDuration() > AtmPolarizingPolicy.MAX_TICKS
            || input.getCount() != 1 || recipe.getIngredients().size() != 1
            || recipe.getRollableResults().size() != 1 || !recipe.getIngredients().getFirst().test(input)) return false;
        var result = recipe.getRollableResults().getFirst();
        return AtmPolarizingPolicy.admissible(input.getCount(), recipe.getIngredients().size(), recipe.getRollableResults().size(),
                result.getStack().getCount(), result.getChance(), recipe.getIngredients().getFirst().test(input))
            && (recipe instanceof PoweredPolarizingRecipe || AtmPolarizingPolicy.applies(BuiltInRegistries.ITEM.getKey(input.getItem()).toString(),
                BuiltInRegistries.ITEM.getKey(result.getStack().getItem()).toString()));
    }
    public static int powerRequired(PolarizingRecipe recipe) {
        return recipe instanceof PoweredPolarizingRecipe powered ? AtmPolarizingPolicy.validatePower(powered.powerRequired()) : AtmPolarizingPolicy.MIN_POWER;
    }
    public static int requiredTicks(PolarizingRecipe recipe) {
        return recipe instanceof PoweredPolarizingRecipe ? AtmPolarizingPolicy.validateExplicitTicks(recipe.getProcessingDuration())
            : AtmPolarizingPolicy.requiredTicks(recipe.getProcessingDuration());
    }
    public static String binding(PolarizerBlockEntity machine, RecipeHolder<PolarizingRecipe> holder, ItemStack input) {
        var ops = RegistryOps.create(JsonOps.INSTANCE, machine.getLevel().registryAccess());
        String data = "polarizing-electrical-v2|" + powerRequired(holder.value()) + "|" + requiredTicks(holder.value()) + "|" + holder.id() + "|"
            + canonical(Recipe.CODEC.encodeStart(ops, holder.value()).getOrThrow()) + "|"
            + canonical(ItemStack.CODEC.encodeStart(ops, input).getOrThrow());
        try { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(data.getBytes(StandardCharsets.UTF_8))); }
        catch (java.security.NoSuchAlgorithmException impossible) { throw new IllegalStateException(impossible); }
    }
    private static String canonical(JsonElement value) {
        if (value.isJsonObject()) {
            TreeMap<String,JsonElement> sorted = new TreeMap<>(); value.getAsJsonObject().entrySet().forEach(e -> sorted.put(e.getKey(), e.getValue()));
            JsonObject result = new JsonObject(); sorted.forEach((key, child) -> result.add(key, JsonParser.parseString(canonical(child))));
            return result.toString();
        }
        if (value.isJsonArray()) { JsonArray result = new JsonArray(); value.getAsJsonArray().forEach(child -> result.add(JsonParser.parseString(canonical(child)))); return result.toString(); }
        return value.toString();
    }
    public static boolean supplied(PolarizerBlockEntity machine, int requestedPower) {
        try {
            int voltage = machine.getData().getVoltage(), maximum = machine.getMaxVoltage();
            if (voltage <= 0 || maximum > 0 && voltage > maximum
                || machine.getMaxCurrent() > 0 && machine.getCurrent() > machine.getMaxCurrent()) return false;
            var members = machine.getOrCreateElectricNetwork().members;
            if (!members.contains(machine)) return false;
            long generation = 0, demand = 0;
            for (IElectric member : members) {
                int generated = member.powerGeneration(), used = member.getPowerUsage();
                if (generated < 0 || used < 0) return false;
                generation += generated; demand += used;
            }
            if (!AtmPolarizingPolicy.supplyReady(machine.getPowerUsage(), machine.getData().notEnoughPower, generation, demand, requestedPower)) return false;
            // Native Accumulator.tick uses this exact loaded conversion and proportional withdrawal.
            // Its advertised output only checks energy>0; refuse a nearly empty source rather than crediting free power.
            for (IElectric member : members) if (member instanceof AccumulatorBlockEntity accumulator && member.powerGeneration() > 0) {
                if (accumulator.getData().networkPowerGeneration != generation) return false;
                double rate = TFMGConfigs.common().machines.FEtoWattTickConversionRate.get();
                if (!Double.isFinite(rate) || rate <= 0) return false;
                int nativeWithdrawal = AtmPolarizingPolicy.nativeAccumulatorWithdrawal(accumulator.powerGeneration(), (int) generation, (int) demand, rate);
                if (accumulator.energy == null || accumulator.energy.getEnergyStored() < nativeWithdrawal) return false;
            }
            return true;
        } catch (RuntimeException | LinkageError unavailable) { return false; }
    }
}
