package dev.godpc.industrialcolonies;

import com.simibubi.create.content.processing.sequenced.SequencedAssemblyItem;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

/** A separate inventory identity; the selected finished item supplies appearance only. */
public final class AssemblyWorkpieceItem extends SequencedAssemblyItem {
    public static final String ID = "industrial_colonies:assembly_workpiece";
    public static final String APPEARANCE = "industrial_colonies:workpiece_appearance";

    public AssemblyWorkpieceItem(Properties properties) { super(properties); }

    public static ItemStack appearance(ItemStack stack) {
        if (!(stack.getItem() instanceof AssemblyWorkpieceItem)) return ItemStack.EMPTY;
        var data = stack.get(DataComponents.CUSTOM_DATA);
        if (data == null) return ItemStack.EMPTY;
        var id = ResourceLocation.tryParse(data.copyTag().getString(APPEARANCE));
        if (id == null || !BuiltInRegistries.ITEM.containsKey(id)) return ItemStack.EMPTY;
        var item = BuiltInRegistries.ITEM.get(id);
        if (item == Items.AIR || item instanceof AssemblyWorkpieceItem) return ItemStack.EMPTY;
        return new ItemStack(item);
    }

    @Override public Component getName(ItemStack stack) {
        var appearance = appearance(stack);
        return appearance.isEmpty() ? Component.translatable("item.industrial_colonies.assembly_workpiece")
                : Component.translatable("item.industrial_colonies.assembly_workpiece.named", appearance.getHoverName());
    }
}
