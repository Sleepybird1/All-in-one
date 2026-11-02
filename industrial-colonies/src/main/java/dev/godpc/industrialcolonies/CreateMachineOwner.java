package dev.godpc.industrialcolonies;

import net.minecraft.Util;
import net.minecraft.core.UUIDUtil;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.common.util.BlockSnapshot;
import net.neoforged.neoforge.event.level.BlockEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

import java.util.UUID;

/** Persistent player ownership for recipe-processing block entities without a native owner. */
public final class CreateMachineOwner {
    private static final DeferredRegister<AttachmentType<?>> ATTACHMENTS =
            DeferredRegister.create(NeoForgeRegistries.Keys.ATTACHMENT_TYPES, IndustrialColonies.MOD_ID);

    private static final DeferredHolder<AttachmentType<?>, AttachmentType<UUID>> OWNER = ATTACHMENTS.register(
            "create_machine_owner",
            () -> AttachmentType.builder(() -> Util.NIL_UUID)
                    .serialize(UUIDUtil.CODEC, owner -> !Util.NIL_UUID.equals(owner))
                    .build());

    private CreateMachineOwner() {
    }

    public static void register(IEventBus modEventBus) {
        ATTACHMENTS.register(modEventBus);
        NeoForge.EVENT_BUS.addListener(CreateMachineOwner::onEntityPlace);
    }

    public static UUID get(BlockEntity blockEntity) {
        UUID owner = blockEntity.getExistingDataOrNull(OWNER.get());
        return owner == null || Util.NIL_UUID.equals(owner) ? null : owner;
    }

    private static void onEntityPlace(BlockEvent.EntityPlaceEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }

        if (event instanceof BlockEvent.EntityMultiPlaceEvent multiPlaceEvent) {
            for (BlockSnapshot snapshot : multiPlaceEvent.getReplacedBlockSnapshots()) {
                stamp(snapshot.getLevel(), snapshot.getPos(), player.getUUID());
            }
            return;
        }

        stamp(event.getLevel(), event.getPos(), player.getUUID());
    }

    private static void stamp(LevelAccessor level, net.minecraft.core.BlockPos pos, UUID owner) {
        BlockEntity blockEntity = level.getBlockEntity(pos);
        if (blockEntity == null) {
            return;
        }

        // The attachment id is retained for old-world Create machine ownership,
        // but the same value now covers vanilla and addon processing machines.
        blockEntity.setData(OWNER.get(), owner);
        blockEntity.setChanged();
    }
}
