package dev.godpc.industrialcolonies.processing;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.common.util.FakePlayer;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/** Attended Low Heat roasting and one-stroke hammering; never an inventory/recipe automation endpoint. */
public final class ManualCinnabar {
    private static final ResourceLocation CINNABAR = id("industrial_colonies:cinnabar");
    private static final ResourceLocation ROASTED = id("industrial_colonies:roasted_cinnabar");
    private static final ResourceLocation BURNER = id("createlowheated:basic_burner");
    private static final ResourceLocation HAMMER = id("immersiveengineering:hammer");
    private static final ManualWorkSessions WORK = new ManualWorkSessions();
    private static final Map<UUID, Long> HAMMER_READY = new HashMap<>();
    private static boolean registered;
    private ManualCinnabar() {}

    public static void register() {
        if (registered) return;
        registered = true;
        ManualCinnabarConfig.get();
        NeoForge.EVENT_BUS.addListener(ManualCinnabar::interact);
        NeoForge.EVENT_BUS.addListener(ManualCinnabar::tick);
        NeoForge.EVENT_BUS.addListener(ManualCinnabar::logout);
        NeoForge.EVENT_BUS.addListener(ManualCinnabar::stopped);
    }

    private static void interact(PlayerInteractEvent.RightClickBlock event) {
        ManualCinnabarConfig config = ManualCinnabarConfig.get();
        if (!config.enabled() || event.getHand() != InteractionHand.MAIN_HAND) return;
        ItemStack main = event.getEntity().getMainHandItem();
        ItemStack off = event.getEntity().getOffhandItem();
        BlockState state = event.getLevel().getBlockState(event.getPos());
        boolean roasting = is(main, CINNABAR) && BuiltInRegistries.BLOCK.getKey(state.getBlock()).equals(BURNER);
        boolean hammering = is(main, HAMMER) && is(off, ROASTED);
        if (!roasting && !hammering) return;

        // Cancel native item/block interaction on both logical sides; the server alone grants anything.
        event.setCanceled(true);
        event.setCancellationResult(InteractionResult.SUCCESS);
        if (!(event.getEntity() instanceof ServerPlayer player) || !realPlayer(player)) return;
        if (player.isSpectator() || !player.isAlive()) return;
        if (!aimedAt(player, event.getPos(), config.reach())) {
            message(player, "Stand near and look directly at the work surface.");
            return;
        }
        if (roasting) {
            if (main.getCount() != 1) {
                message(player, "Hold exactly ONE Cinnabar in your main hand. Manual roasting cannot batch.");
                return;
            }
            if (!litBurner(state)) {
                message(player, "Fuel and light the Create Low Heat Basic Burner first.");
                return;
            }
            if (WORK.get(player.getUUID()) != null) {
                message(player, "Keep looking at your lit burner; changing item, target or position interrupts roasting.");
                return;
            }
            ManualWorkSessions.Station station = new ManualWorkSessions.Station(
                    player.level().dimension().location().toString(), event.getPos().asLong());
            if (!WORK.begin(player.getUUID(), station, player.level().getGameTime())) {
                message(player, "This burner is already being attended by another player.");
                return;
            }
            message(player, "Roasting one Cinnabar: keep holding it and looking at this lit burner ("
                    + ((config.heatingTicks() + 19) / 20) + " seconds). No automatic repeat.");
            return;
        }

        if (off.getCount() != 1 || !main.isDamageableItem() || main.getDamageValue() >= main.getMaxDamage()) {
            message(player, "Use a working Engineer's Hammer and exactly ONE Roasted Cinnabar in your off hand.");
            return;
        }
        if (event.getFace() != Direction.UP || !state.isFaceSturdy(player.level(), event.getPos(), Direction.UP)) {
            message(player, "Strike the top of a solid block, with one Roasted Cinnabar in your off hand.");
            return;
        }
        long now = player.level().getGameTime();
        if (now < HAMMER_READY.getOrDefault(player.getUUID(), Long.MIN_VALUE)) {
            message(player, "Let the hammer recover before the next strike.");
            return;
        }
        WORK.cancel(player.getUUID());
        HAMMER_READY.put(player.getUUID(), now + config.hammerCooldownTicks());
        // Replacement (not give/shrink) prevents inventory-full loss or accidental multi-output.
        player.setItemInHand(InteractionHand.OFF_HAND, new ItemStack(Items.REDSTONE));
        var hammerItem = main.getItem();
        main.hurtAndBreak(config.hammerDamage(), player, EquipmentSlot.MAINHAND);
        player.getCooldowns().addCooldown(hammerItem, config.hammerCooldownTicks());
        message(player, "One Roasted Cinnabar crushed into Redstone. Hammer durability consumed.");
    }

    private static void tick(PlayerTickEvent.Post event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || !realPlayer(player)) return;
        ManualWorkSessions.Session session = WORK.get(player.getUUID());
        if (session == null) return;
        ManualCinnabarConfig config = ManualCinnabarConfig.get();
        BlockPos pos = BlockPos.of(session.station().position());
        boolean sameDimension = player.level().dimension().location().toString().equals(session.station().dimension());
        boolean loaded = sameDimension && player.level().hasChunkAt(pos);
        ItemStack held = player.getMainHandItem();
        if (!config.enabled() || !ManualWorkSessions.mayContinue(held.getCount(), player.isAlive() && !player.isSpectator(),
                sameDimension, is(held, CINNABAR), loaded && litBurner(player.level().getBlockState(pos)),
                player.getEyePosition().distanceToSqr(Vec3.atCenterOf(pos)) <= config.reach() * config.reach(),
                loaded && aimedAt(player, pos, config.reach()))) {
            WORK.cancel(player.getUUID());
            message(player, "Roasting interrupted; your Cinnabar is unchanged. Start again at a lit burner.");
            return;
        }
        long now = player.level().getGameTime();
        if (ManualWorkSessions.finished(session.startedAt(), now, config.heatingTicks())) {
            WORK.cancel(player.getUUID());
            if (!BuiltInRegistries.ITEM.containsKey(ROASTED)) throw new IllegalStateException("Missing manual output " + ROASTED);
            player.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(BuiltInRegistries.ITEM.get(ROASTED)));
            message(player, "Roasted Cinnabar ready. Put ONE in your off hand; use an Engineer's Hammer on a solid block top.");
        } else if ((now - session.startedAt()) % 20 == 0) {
            long seconds = (config.heatingTicks() - (now - session.startedAt()) + 19) / 20;
            message(player, "Roasting one Cinnabar: " + seconds + "s remaining. Stay focused on the lit burner.");
        }
    }
    private static boolean litBurner(BlockState state) {
        return BuiltInRegistries.BLOCK.getKey(state.getBlock()).equals(BURNER)
                && state.hasProperty(BlockStateProperties.LIT) && state.getValue(BlockStateProperties.LIT);
    }
    private static boolean aimedAt(ServerPlayer player, BlockPos pos, double reach) {
        HitResult hit = player.pick(reach, 0, false);
        return hit instanceof BlockHitResult block && hit.getType() == HitResult.Type.BLOCK && block.getBlockPos().equals(pos);
    }
    private static boolean is(ItemStack stack, ResourceLocation id) {
        return !stack.isEmpty() && BuiltInRegistries.ITEM.getKey(stack.getItem()).equals(id);
    }
    private static boolean realPlayer(ServerPlayer player) {
        return !(player instanceof FakePlayer) && player.getServer() != null
                && player.getServer().getPlayerList().getPlayer(player.getUUID()) == player;
    }
    private static ResourceLocation id(String value) { return ResourceLocation.parse(value); }
    private static void message(ServerPlayer player, String text) { player.displayClientMessage(Component.literal(text), true); }
    private static void logout(PlayerEvent.PlayerLoggedOutEvent event) {
        WORK.cancel(event.getEntity().getUUID()); HAMMER_READY.remove(event.getEntity().getUUID());
    }
    private static void stopped(ServerStoppedEvent event) { WORK.clear(); HAMMER_READY.clear(); }
}
