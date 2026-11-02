package dev.godpc.industrialcolonies;

import igentuman.nr.radiation.simulation.inventory.SlotProviders;
import igentuman.nr.radiation.simulation.inventory.VanillaSlotProvider;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;

/** Same native hash and visit order, without materializing vanilla RadiatedSlot records/streams. */
public final class RadiationInventoryHash {
    private static final EquipmentSlot[] EQUIPMENT = EquipmentSlot.values();
    private RadiationInventoryHash() {}

    public static int compute(LivingEntity entity) {
        int hash = 1;
        for (var provider : SlotProviders.all()) {
            // Subclasses may provide different slots; retain their native implementation.
            if (provider.getClass() == VanillaSlotProvider.class) {
                for (var slot : EQUIPMENT) {
                    if (slot.isArmor()) {
                        var stack = entity.getItemBySlot(slot);
                        if (!stack.isEmpty()) hash = append(hash, stack);
                    }
                }
                var offhand = entity.getOffhandItem();
                if (!offhand.isEmpty()) hash = append(hash, offhand);
                if (entity instanceof Player player) {
                    var items = player.getInventory().items;
                    for (int i = 0; i < items.size(); i++) {
                        var stack = items.get(i);
                        if (!stack.isEmpty()) hash = append(hash, stack);
                    }
                } else {
                    var mainhand = entity.getMainHandItem();
                    if (!mainhand.isEmpty()) hash = append(hash, mainhand);
                }
            } else {
                var iterator = provider.slots(entity).iterator();
                while (iterator.hasNext()) hash = append(hash, iterator.next().stack());
            }
        }
        return hash;
    }

    private static int append(int hash, ItemStack stack) {
        return 31 * hash + (stack.isEmpty() ? 0 : stack.getItem().hashCode() * 31 + stack.getCount());
    }
}
