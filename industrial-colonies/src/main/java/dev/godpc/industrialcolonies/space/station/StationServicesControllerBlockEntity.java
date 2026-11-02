package dev.godpc.industrialcolonies.space.station;

import dev.godpc.industrialcolonies.IndustrialBlockEntities;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.api.block.BlockEntitySubLevelActor;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import dev.ryanhcode.sable.sublevel.plot.PlotChunkHolder;
import java.util.Optional;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.IntTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.energy.EnergyStorage;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.fluids.capability.templates.FluidTank;

/** Sustained-power and cooling authority for a commissioned Sable station. */
public final class StationServicesControllerBlockEntity extends BlockEntity
        implements BlockEntitySubLevelActor {
    public static final int ENERGY_CAPACITY = 8_000_000;
    public static final int ENERGY_TRANSFER = 32_768;
    public static final int ENERGY_PER_TICK = 4_096;
    public static final int COOLANT_CAPACITY = 16_000;
    public static final int COOLANT_PER_TICK = 1;
    public static final int COMMISSIONING_TICKS = 600;
    private static final ResourceLocation COOLING_FLUID = ResourceLocation.fromNamespaceAndPath(
            "tfmg", "cooling_fluid");
    private static final Set<String> VALID_STATUSES = Set.of(
            "unconfigured",
            "not_on_sublevel",
            "invalid_identity",
            "life_support_offline",
            "insufficient_power",
            "insufficient_coolant",
            "coolant_debit_failed",
            "power_debit_failed",
            "commissioning",
            "commissioned",
            "removed");

    private final EnergyStorage energy = new EnergyStorage(
            ENERGY_CAPACITY, ENERGY_TRANSFER, ENERGY_TRANSFER) {
        @Override
        public int receiveEnergy(int amount, boolean simulate) {
            int accepted = super.receiveEnergy(amount, simulate);
            if (!simulate && accepted > 0) {
                setChanged();
            }
            return accepted;
        }

        @Override
        public int extractEnergy(int amount, boolean simulate) {
            int extracted = super.extractEnergy(amount, simulate);
            if (!simulate && extracted > 0) {
                setChanged();
            }
            return extracted;
        }
    };
    private final FluidTank coolant = new FluidTank(
            COOLANT_CAPACITY,
            StationServicesControllerBlockEntity::isValidCoolingFluid) {
        @Override
        protected void onContentsChanged() {
            setChanged();
        }
    };
    private int commissioningProgress;
    private String status = "unconfigured";
    private long lastSuccessfulServiceTick = Long.MIN_VALUE;

    public StationServicesControllerBlockEntity(BlockPos pos, BlockState state) {
        super(IndustrialBlockEntities.STATION_SERVICES_CONTROLLER.get(), pos, state);
    }

    public EnergyStorage energyStorage() {
        return energy;
    }

    public IFluidHandler fluidHandler() {
        return coolant;
    }

    /**
     * Resolves the exact live controller named by the metadata. A persisted
     * heartbeat alone is never authority: the block entity must still be
     * loaded, on the same Sable sublevel, recently ticked, oxygen-covered, and
     * able to fund another service tick.
     */
    public static boolean isLiveFor(ServerSubLevel station, StationMetadata metadata) {
        StationMetadata current = StationMetadata.read(station).orElse(null);
        if (station.isRemoved()
                || metadata == null
                || !metadata.equals(current)
                || !metadata.commissioned()
                || !metadata.hasFreshServices(station.getLevel().getGameTime())
                || !metadata.hasValidIdentity(station.getLevel().getServer())) {
            return false;
        }
        StationServicesControllerBlockEntity matching = null;
        for (PlotChunkHolder holder : station.getPlot().getLoadedChunks()) {
            for (BlockEntity blockEntity : holder.getChunk().getBlockEntities().values()) {
                if (!(blockEntity instanceof StationServicesControllerBlockEntity controller)
                        || controller.isRemoved()
                        || controller.getLevel() != station.getLevel()
                        || Sable.HELPER.getContaining(controller) != station
                        || !metadata.matchesController(station, controller.getBlockPos())) {
                    continue;
                }
                if (matching != null) {
                    return false;
                }
                matching = controller;
            }
        }
        if (matching == null) {
            return false;
        }
        long age = station.getLevel().getGameTime() - matching.lastSuccessfulServiceTick;
        return age >= 0L
                && age <= 1L
                && matching.hasServiceResources()
                && StationLifeSupport.hasLiveCoverage(station, matching.getBlockPos());
    }

    public Component interact(ServerPlayer player) {
        if (!(Sable.HELPER.getContaining(this) instanceof ServerSubLevel station)
                || station.isRemoved()) {
            return Component.translatable("message.industrial_colonies.station.not_on_sublevel");
        }
        Optional<StationMetadata> existing = StationMetadata.read(station);
        if (existing.isEmpty() && StationMetadata.hasRoot(station)) {
            return Component.translatable("message.industrial_colonies.station.corrupt_metadata");
        }
        if (existing.isPresent() && !existing.get().isAuthorized(player)) {
            return Component.translatable("message.industrial_colonies.station.not_authorized");
        }
        if (player.isShiftKeyDown()) {
            if (existing.isEmpty()) {
                return Component.translatable("message.industrial_colonies.station.not_configured");
            }
            existing.get().asShip().write(station);
            commissioningProgress = 0;
            status = "commissioning";
            setChanged();
            return Component.translatable("message.industrial_colonies.station.ship_role");
        }
        StationMetadata metadata = existing.orElseGet(() -> StationMetadata.begin(
                station, player, worldPosition).orElse(null));
        if (metadata == null) {
            return Component.translatable("message.industrial_colonies.station.team_unavailable");
        }
        if (metadata.role() != StationRole.STATION || !metadata.matchesController(station, worldPosition)) {
            metadata = new StationMetadata(
                    StationRole.STATION,
                    false,
                    metadata.owner(),
                    metadata.team(),
                    worldPosition.subtract(station.getPlot().getCenterBlock()),
                    0L,
                    0L,
                    0L);
            metadata.write(station);
            commissioningProgress = 0;
        }
        return Component.translatable(
                "message.industrial_colonies.station.status",
                status,
                commissioningProgress,
                COMMISSIONING_TICKS,
                energy.getEnergyStored(),
                coolant.getFluidAmount());
    }

    public static void serverTick(
            Level level,
            BlockPos pos,
            BlockState state,
            StationServicesControllerBlockEntity controller
    ) {
        controller.tickServer();
    }

    private void tickServer() {
        if (!(level instanceof net.minecraft.server.level.ServerLevel serverLevel)
                || !(Sable.HELPER.getContaining(this) instanceof ServerSubLevel station)
                || station.isRemoved()) {
            fail("not_on_sublevel", null, null);
            return;
        }
        StationMetadata metadata = StationMetadata.read(station).orElse(null);
        if (metadata == null
                || !metadata.matchesController(station, worldPosition)
                || !metadata.hasValidIdentity(serverLevel.getServer())) {
            fail("invalid_identity", station, metadata);
            return;
        }
        if (!StationLifeSupport.hasLiveCoverage(station, worldPosition)) {
            fail("life_support_offline", station, metadata);
            return;
        }
        if (energy.extractEnergy(ENERGY_PER_TICK, true) < ENERGY_PER_TICK) {
            fail("insufficient_power", station, metadata);
            return;
        }
        FluidStack simulated = coolant.drain(COOLANT_PER_TICK, IFluidHandler.FluidAction.SIMULATE);
        if (simulated.getAmount() < COOLANT_PER_TICK || !isValidCoolingFluid(simulated)) {
            fail("insufficient_coolant", station, metadata);
            return;
        }

        FluidStack coolantDebit = coolant.drain(
                COOLANT_PER_TICK, IFluidHandler.FluidAction.EXECUTE);
        if (coolantDebit.getAmount() != COOLANT_PER_TICK
                || !isValidCoolingFluid(coolantDebit)) {
            if (!coolantDebit.isEmpty()) {
                coolant.fill(coolantDebit, IFluidHandler.FluidAction.EXECUTE);
            }
            fail("coolant_debit_failed", station, metadata);
            return;
        }
        int energyDebit = energy.extractEnergy(ENERGY_PER_TICK, false);
        if (energyDebit != ENERGY_PER_TICK) {
            if (energyDebit > 0) {
                energy.receiveEnergy(energyDebit, false);
            }
            coolant.fill(coolantDebit, IFluidHandler.FluidAction.EXECUTE);
            fail("power_debit_failed", station, metadata);
            return;
        }
        long gameTime = serverLevel.getGameTime();
        if (!metadata.commissioned()) {
            commissioningProgress++;
            status = "commissioning";
            if (commissioningProgress >= COMMISSIONING_TICKS) {
                metadata.commissioned(gameTime).write(station);
                status = "commissioned";
            }
        } else {
            commissioningProgress = COMMISSIONING_TICKS;
            metadata.heartbeat(gameTime).write(station);
            status = "commissioned";
        }
        lastSuccessfulServiceTick = gameTime;
        setChanged();
    }

    private void fail(String newStatus, ServerSubLevel station, StationMetadata metadata) {
        lastSuccessfulServiceTick = Long.MIN_VALUE;
        if (commissioningProgress != 0 || !newStatus.equals(status)) {
            commissioningProgress = 0;
            status = newStatus;
            setChanged();
        }
        if (station != null && metadata != null && metadata.commissioned()) {
            metadata.decommissioned().write(station);
        }
    }

    private boolean hasServiceResources() {
        FluidStack fluid = coolant.drain(COOLANT_PER_TICK, IFluidHandler.FluidAction.SIMULATE);
        return energy.extractEnergy(ENERGY_PER_TICK, true) == ENERGY_PER_TICK
                && fluid.getAmount() == COOLANT_PER_TICK
                && isValidCoolingFluid(fluid);
    }

    private static boolean isValidCoolingFluid(FluidStack stack) {
        return !stack.isEmpty()
                && BuiltInRegistries.FLUID.getKey(stack.getFluid()).equals(COOLING_FLUID)
                && stack.isComponentsPatchEmpty();
    }

    /** Immediately invalidates durable station authority for a real block removal. */
    void decommissionForBlockRemoval() {
        lastSuccessfulServiceTick = Long.MIN_VALUE;
        if (Sable.HELPER.getContaining(this) instanceof ServerSubLevel station
                && !station.isRemoved()) {
            StationMetadata.read(station)
                    .filter(metadata -> metadata.matchesController(station, worldPosition))
                    .filter(StationMetadata::commissioned)
                    .ifPresent(metadata -> metadata.decommissioned().write(station));
        }
        commissioningProgress = 0;
        status = "removed";
    }

    @Override
    public void setRemoved() {
        // Chunk/sublevel unload and server shutdown also call setRemoved.
        // Drop only transient live authority here; durable metadata and cycle
        // state survive and cannot become live again until a successful tick.
        lastSuccessfulServiceTick = Long.MIN_VALUE;
        super.setRemoved();
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        tag.put("Energy", energy.serializeNBT(registries));
        tag.put("Coolant", coolant.writeToNBT(registries, new CompoundTag()));
        tag.putInt("CommissioningProgress", commissioningProgress);
        tag.putString("Status", status);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        int storedEnergy = tag.get("Energy") instanceof IntTag energyTag
                        && energyTag.getAsInt() >= 0
                        && energyTag.getAsInt() <= ENERGY_CAPACITY
                ? energyTag.getAsInt()
                : 0;
        energy.deserializeNBT(registries, IntTag.valueOf(storedEnergy));
        loadValidatedTank(
                coolant,
                tag,
                "Coolant",
                registries,
                COOLANT_CAPACITY,
                StationServicesControllerBlockEntity::isValidCoolingFluid);
        commissioningProgress = tag.get("CommissioningProgress") instanceof IntTag progressTag
                        && progressTag.getAsInt() >= 0
                        && progressTag.getAsInt() < COMMISSIONING_TICKS
                ? progressTag.getAsInt()
                : 0;
        String loadedStatus = tag.contains("Status", Tag.TAG_STRING)
                ? tag.getString("Status")
                : "unconfigured";
        status = VALID_STATUSES.contains(loadedStatus) ? loadedStatus : "unconfigured";
        lastSuccessfulServiceTick = Long.MIN_VALUE;
    }

    static void loadValidatedTank(
            FluidTank tank,
            CompoundTag root,
            String key,
            HolderLookup.Provider registries,
            int capacity,
            java.util.function.Predicate<FluidStack> validator
    ) {
        tank.setFluid(FluidStack.EMPTY);
        if (!root.contains(key, Tag.TAG_COMPOUND)) {
            return;
        }
        CompoundTag tankTag = root.getCompound(key);
        if (!tankTag.contains("Fluid", Tag.TAG_COMPOUND)) {
            return;
        }
        FluidStack loaded = FluidStack.parseOptional(registries, tankTag.getCompound("Fluid"));
        if (!loaded.isEmpty()
                && loaded.getAmount() > 0
                && loaded.getAmount() <= capacity
                && validator.test(loaded)) {
            tank.setFluid(loaded.copy());
        }
    }
}
