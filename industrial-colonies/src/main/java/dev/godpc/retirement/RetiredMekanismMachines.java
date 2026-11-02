package dev.godpc.retirement;
import java.util.Set;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.level.block.state.BlockState;

/** Exact user-selected manufacturing families; registrations and saved contents remain intact. */
public final class RetiredMekanismMachines {
 public static final Set<String> IDS=Set.of("mekanism:precision_sawmill","mekanism:combiner",
  "mekanism:basic_sawing_factory","mekanism:advanced_sawing_factory","mekanism:elite_sawing_factory","mekanism:ultimate_sawing_factory",
  "mekanism:basic_combining_factory","mekanism:advanced_combining_factory","mekanism:elite_combining_factory","mekanism:ultimate_combining_factory");
 public static boolean contains(BlockState state){return IDS.contains(BuiltInRegistries.BLOCK.getKey(state.getBlock()).toString());}
 private RetiredMekanismMachines(){}
}
