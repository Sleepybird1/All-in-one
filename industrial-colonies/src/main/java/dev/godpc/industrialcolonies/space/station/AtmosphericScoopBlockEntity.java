package dev.godpc.industrialcolonies.space.station;

import dev.godpc.industrialcolonies.IndustrialBlockEntities;
import dev.godpc.industrialcolonies.IndustrialFluids;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.api.block.BlockEntitySubLevelActor;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.energy.EnergyStorage;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.fluids.capability.templates.FluidTank;

/** Produces one bucket of condensate only after a continuous verified cycle. */
public final class AtmosphericScoopBlockEntity extends BlockEntity
        implements BlockEntitySubLevelActor {
    public static final int ENERGY_CAPACITY = 16_000_000;
    public static final int ENERGY_TRANSFER = 65_536;
    public static final int ENERGY_PER_TICK = 8_192;
    public static final int COOLANT_CAPACITY = 32_000;
    public static final int COOLANT_PER_TICK = 4;
    public static final int CONDENSATE_CAPACITY = 16_000;
    public static final int CONDENSATE_PER_CYCLE = 1_000;
    public static final int CYCLE_TICKS = 400;
    private static final ResourceLocation COOLING_FLUID = ResourceLocation.fromNamespaceAndPath(
            "tfmg", "cooling_fluid");
    private static final Set<String> VALID_STATUSES = Set.of(
            "idle",
            "not_on_sublevel",
            "station_not_commissioned",
            "life_support_offline",
            "outside_gas_giant_band",
            "output_full",
            "insufficient_power",
            "insufficient_coolant",
            "coolant_debit_failed",
            "power_debit_failed",
            "extracting",
            "output_race",
            "cycle_complete");

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
            AtmosphericScoopBlockEntity::isValidCoolingFluid) {
        @Override
        protected void onContentsChanged() {
            setChanged();
        }
    };
    private final FluidTank condensate = new FluidTank(
            CONDENSATE_CAPACITY,
            AtmosphericScoopBlockEntity::isValidCondensate) {
        @Override
        protected void onContentsChanged() {
            setChanged();
        }
    };
    private final IFluidHandler fluids = new TwoTankHandler();
    private int progress;
    private String status = "idle";

    public AtmosphericScoopBlockEntity(BlockPos pos, BlockState state) {
        super(IndustrialBlockEntities.ATMOSPHERIC_SCOOP.get(), pos, state);
    }

    public EnergyStorage energyStorage() {
        return energy;
    }

    public IFluidHandler fluidHandler() {
        return fluids;
    }

    public Component statusMessage() {
        return Component.translatable(
                "message.industrial_colonies.scoop.status",
                status,
                progress,
                CYCLE_TICKS,
                energy.getEnergyStored(),
                coolant.getFluidAmount(),
                condensate.getFluidAmount());
    }

    public static void serverTick(
            Level level,
            BlockPos pos,
            BlockState state,
            AtmosphericScoopBlockEntity scoop
    ) {
        scoop.tickServer();
    }

    private void tickServer() {
        if (!(level instanceof net.minecraft.server.level.ServerLevel serverLevel)
                || !(Sable.HELPER.getContaining(this) instanceof ServerSubLevel station)
                || station.isRemoved()) {
            fail("not_on_sublevel");
            return;
        }
        StationMetadata metadata = StationMetadata.read(station).orElse(null);
        if (metadata == null
                || metadata.role() != StationRole.STATION
                || !metadata.commissioned()
                || !metadata.hasFreshServices(serverLevel.getGameTime())
                || !metadata.hasValidIdentity(serverLevel.getServer())
                || !StationServicesControllerBlockEntity.isLiveFor(station, metadata)) {
            fail("station_not_commissioned");
            return;
        }
        if (!StationLifeSupport.hasLiveCoverage(station, worldPosition)) {
            fail("life_support_offline");
            return;
        }
        if (!GasGiantOrbitVerifier.isInExtractionBand(station)) {
            fail("outside_gas_giant_band");
            return;
        }
        if (condensate.getSpace() < CONDENSATE_PER_CYCLE) {
            fail("output_full");
            return;
        }
        if (energy.extractEnergy(ENERGY_PER_TICK, true) < ENERGY_PER_TICK) {
            fail("insufficient_power");
            return;
        }
        FluidStack simulated = coolant.drain(COOLANT_PER_TICK, IFluidHandler.FluidAction.SIMULATE);
        if (simulated.getAmount() < COOLANT_PER_TICK || !isValidCoolingFluid(simulated)) {
            fail("insufficient_coolant");
            return;
        }

        FluidStack coolantDebit = coolant.drain(
                COOLANT_PER_TICK, IFluidHandler.FluidAction.EXECUTE);
        if (coolantDebit.getAmount() != COOLANT_PER_TICK
                || !isValidCoolingFluid(coolantDebit)) {
            if (!coolantDebit.isEmpty()) {
                coolant.fill(coolantDebit, IFluidHandler.FluidAction.EXECUTE);
            }
            fail("coolant_debit_failed");
            return;
        }
        int energyDebit = energy.extractEnergy(ENERGY_PER_TICK, false);
        if (energyDebit != ENERGY_PER_TICK) {
            if (energyDebit > 0) {
                energy.receiveEnergy(energyDebit, false);
            }
            coolant.fill(coolantDebit, IFluidHandler.FluidAction.EXECUTE);
            fail("power_debit_failed");
            return;
        }
        progress++;
        status = "extracting";
        if (progress >= CYCLE_TICKS) {
            FluidStack product = new FluidStack(
                    IndustrialFluids.GAS_GIANT_CONDENSATE.get(),
                    CONDENSATE_PER_CYCLE);
            if (condensate.fill(product, IFluidHandler.FluidAction.EXECUTE) != CONDENSATE_PER_CYCLE) {
                fail("output_race");
                return;
            }
            progress = 0;
            status = "cycle_complete";
        }
        setChanged();
    }

    private void fail(String newStatus) {
        if (progress != 0 || !newStatus.equals(status)) {
            progress = 0;
            status = newStatus;
            setChanged();
        }
    }

    private static boolean isValidCoolingFluid(FluidStack stack) {
        return !stack.isEmpty()
                && BuiltInRegistries.FLUID.getKey(stack.getFluid()).equals(COOLING_FLUID)
                && stack.isComponentsPatchEmpty();
    }

    private static boolean isValidCondensate(FluidStack stack) {
        return !stack.isEmpty()
                && stack.getFluid() == IndustrialFluids.GAS_GIANT_CONDENSATE.get()
                && stack.isComponentsPatchEmpty();
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        tag.put("Energy", energy.serializeNBT(registries));
        tag.put("Coolant", coolant.writeToNBT(registries, new CompoundTag()));
        tag.put("Condensate", condensate.writeToNBT(registries, new CompoundTag()));
        tag.putInt("Progress", progress);
        tag.putString("Status", status);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        int storedEnergy = tag.get("Energy") instanceof net.minecraft.nbt.IntTag energyTag
                        && energyTag.getAsInt() >= 0
                        && energyTag.getAsInt() <= ENERGY_CAPACITY
                ? energyTag.getAsInt()
                : 0;
        energy.deserializeNBT(registries, net.minecraft.nbt.IntTag.valueOf(storedEnergy));
        StationServicesControllerBlockEntity.loadValidatedTank(
                coolant,
                tag,
                "Coolant",
                registries,
                COOLANT_CAPACITY,
                AtmosphericScoopBlockEntity::isValidCoolingFluid);
        StationServicesControllerBlockEntity.loadValidatedTank(
                condensate,
                tag,
                "Condensate",
                registries,
                CONDENSATE_CAPACITY,
                AtmosphericScoopBlockEntity::isValidCondensate);
        progress = tag.get("Progress") instanceof net.minecraft.nbt.IntTag progressTag
                        && progressTag.getAsInt() >= 0
                        && progressTag.getAsInt() < CYCLE_TICKS
                ? progressTag.getAsInt()
                : 0;
        String loadedStatus = tag.contains("Status", Tag.TAG_STRING)
                ? tag.getString("Status")
                : "idle";
        status = VALID_STATUSES.contains(loadedStatus) ? loadedStatus : "idle";
    }

    private final class TwoTankHandler implements IFluidHandler {
        @Override
        public int getTanks() {
            return 2;
        }

        @Override
        public FluidStack getFluidInTank(int tank) {
            return tank == 0
                    ? coolant.getFluidInTank(0)
                    : tank == 1 ? condensate.getFluidInTank(0) : FluidStack.EMPTY;
        }

        @Override
        public int getTankCapacity(int tank) {
            return tank == 0 ? COOLANT_CAPACITY : tank == 1 ? CONDENSATE_CAPACITY : 0;
        }

        @Override
        public boolean isFluidValid(int tank, FluidStack stack) {
            return tank == 0 && coolant.isFluidValid(stack);
        }

        @Override
        public int fill(FluidStack resource, FluidAction action) {
            return coolant.fill(resource, action);
        }

        @Override
        public FluidStack drain(FluidStack resource, FluidAction action) {
            if (resource.isEmpty()
                    || resource.getFluid() != IndustrialFluids.GAS_GIANT_CONDENSATE.get()) {
                return FluidStack.EMPTY;
            }
            return condensate.drain(resource, action);
        }

        @Override
        public FluidStack drain(int maxDrain, FluidAction action) {
            return condensate.drain(maxDrain, action);
        }
    }
}
