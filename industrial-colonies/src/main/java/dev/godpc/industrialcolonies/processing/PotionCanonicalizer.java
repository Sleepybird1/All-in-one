package dev.godpc.industrialcolonies.processing;

import blusunrize.immersiveengineering.common.register.IEDataComponents;
import blusunrize.immersiveengineering.common.register.IEFluids;
import com.simibubi.create.AllDataComponents;
import com.simibubi.create.AllFluids;
import com.simibubi.create.content.fluids.potion.PotionFluid.BottleType;
import io.redspace.ironsspellbooks.registries.ComponentRegistry;
import io.redspace.ironsspellbooks.registries.FluidRegistry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.neoforged.neoforge.fluids.FluidStack;

/** Detached projection only. No producer, inventory or recipe hook registers this adapter. */
public final class PotionCanonicalizer {
    public record Projection(String status, FluidStack fluid) {
        public boolean accepted() { return status.equals("CANONICAL") || status.equals("UNCHANGED"); }
    }

    public static Projection project(FluidStack source) {
        if (source.isEmpty()) return new Projection("UNCHANGED", source.copy());
        boolean create = AllFluids.POTION.get().isSame(source.getFluid());
        boolean spellbooks = source.is(FluidRegistry.POTION_FLUID.get());
        boolean engineering = source.is(IEFluids.POTION.get());
        if (!create && !spellbooks && !engineering) {
            String id = BuiltInRegistries.FLUID.getKey(source.getFluid()).toString();
            return new Projection(id.equals("modernfoundry:potion") ? "HELD_LEGACY_FORMAT" : "UNCHANGED", source.copy());
        }
        if (!source.has(DataComponents.POTION_CONTENTS))
            return new Projection("HELD_MISSING_CONTENTS", source.copy());
        var createType = source.get(AllDataComponents.POTION_FLUID_BOTTLE_TYPE);
        var spellType = source.get(ComponentRegistry.POTION_BOTTLE_TYPE);
        var engineeringType = source.get(IEDataComponents.POTION_BOTTLE_TYPE);
        String ownerType = create ? name(createType) : spellbooks ? name(spellType) : name(engineeringType);
        if ((createType != null && !createType.name().equals(ownerType))
                || (spellType != null && !spellType.name().equals(ownerType))
                || (engineeringType != null && !engineeringType.name().equals(ownerType)))
            return new Projection("HELD_CONFLICTING_BOTTLES", source.copy());
        if (create && spellType == null && engineeringType == null)
            return new Projection("CANONICAL", source.copy());
        FluidStack result = new FluidStack(AllFluids.POTION.get().getSource(), source.getAmount());
        result.applyComponents(source.getComponentsPatch());
        result.remove(ComponentRegistry.POTION_BOTTLE_TYPE.get());
        result.remove(IEDataComponents.POTION_BOTTLE_TYPE.get());
        result.set(AllDataComponents.POTION_FLUID_BOTTLE_TYPE, BottleType.valueOf(ownerType));
        return new Projection("CANONICAL", result);
    }

    private static String name(Enum<?> value) { return value == null ? "REGULAR" : value.name(); }
}
