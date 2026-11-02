package dev.godpc.industrialcolonies;

import dev.godpc.industrialcolonies.food.FoodDiversityData;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

/** Persistent player-owned data used by Industrial Colonies systems. */
public final class IndustrialAttachments {
    private static final DeferredRegister<AttachmentType<?>> ATTACHMENTS =
            DeferredRegister.create(NeoForgeRegistries.ATTACHMENT_TYPES, IndustrialColonies.MOD_ID);

    public static final DeferredHolder<AttachmentType<?>, AttachmentType<FoodDiversityData>> FOOD_DIVERSITY =
            ATTACHMENTS.register(
                    "food_diversity",
                    () -> AttachmentType.<FoodDiversityData>builder(() -> new FoodDiversityData())
                            .serialize(FoodDiversityData.CODEC)
                            .copyOnDeath()
                            .build());

    private IndustrialAttachments() {
    }

    public static void register(IEventBus modEventBus) {
        ATTACHMENTS.register(modEventBus);
    }
}
