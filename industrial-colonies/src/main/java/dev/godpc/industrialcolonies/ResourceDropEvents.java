package dev.godpc.industrialcolonies;
import net.minecraft.world.entity.item.ItemEntity;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;

/** Canonicalizes newly spawned literal drops; never deletes stacks or edits saved inventories. */
@EventBusSubscriber(modid="industrial_colonies")
public final class ResourceDropEvents {
    @SubscribeEvent
    public static void spawned(EntityJoinLevelEvent event) {
        if(event.getLevel().isClientSide() || event.loadedFromDisk() || !(event.getEntity() instanceof ItemEntity item))return;
        var original=item.getItem();var replacement=ResourceCanonicalization.canonical(original);
        if(replacement!=original)item.setItem(replacement);
    }
}
