package dev.godpc.industrialcolonies;

import com.drmangotea.tfmg.content.machinery.vat.base.VatBlockEntity;
import com.drmangotea.tfmg.content.machinery.vat.base.VatInventory;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;

/** Input-only capacity extension. Native output inventory and its indices stay unchanged. */
public final class TFMGExpandedVatInventory extends VatInventory {
    public static final int INPUT_SLOTS = 24;
    public static final int MAX_INGREDIENT_UNITS = 128;

    public TFMGExpandedVatInventory(VatBlockEntity vat) { super(INPUT_SLOTS, vat); }

    @Override
    public void deserializeNBT(HolderLookup.Provider lookup, CompoundTag original) {
        super.deserializeNBT(lookup, expandedInputTag(original));
    }

    public static CompoundTag expandedInputTag(CompoundTag original) {
        int declared = original.getInt("Size");
        if (declared < 0 || declared > INPUT_SLOTS)
            throw new IllegalArgumentException("Unsupported saved Chemical Vat input capacity: " + declared);
        // Reject unknown slots rather than truncating them during an older-save migration.
        for (Tag element : original.getList("Items", Tag.TAG_COMPOUND)) {
            int slot = ((CompoundTag) element).getInt("Slot");
            if (slot < 0 || slot >= INPUT_SLOTS)
                throw new IllegalArgumentException("Out-of-range saved Chemical Vat input slot: " + slot);
        }
        CompoundTag expanded = original.copy();
        expanded.putInt("Size", INPUT_SLOTS);
        return expanded;
    }
}
