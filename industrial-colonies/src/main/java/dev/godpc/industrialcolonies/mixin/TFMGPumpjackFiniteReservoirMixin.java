package dev.godpc.industrialcolonies.mixin;

import com.drmangotea.tfmg.TFMG;
import com.drmangotea.tfmg.config.TFMGConfigs;
import com.drmangotea.tfmg.content.machinery.oil_processing.pumpjack.base.FluidReservoir;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.neoforged.neoforge.fluids.capability.templates.FluidTank;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Finishes TFMG 1.2.0's reservoir implementation.
 *
 * <p>The bundled TFMG build creates and persists finite reservoir records, but
 * its pumpjack process method never consumes {@code oilReserves}. Treat one
 * reserve unit as one bucket and probabilistically account for sub-bucket
 * extraction. This preserves arbitrary kinetic speeds without granting free,
 * bottomless crude oil.</p>
 */
@Mixin(
        targets = "com.drmangotea.tfmg.content.machinery.oil_processing.pumpjack.base.PumpjackBaseBlockEntity",
        remap = false
)
public abstract class TFMGPumpjackFiniteReservoirMixin {
    private static final int MILLIBUCKETS_PER_RESERVE = 1_000;

    @Shadow
    public FluidTank tank;

    @Shadow
    public BlockPos deposit;

    @Shadow
    public int miningRate;

    @Unique
    private int industrialColonies$oilBeforeProcess;

    @Inject(method = "process", at = @At("HEAD"), cancellable = true, remap = false)
    private void industrialColonies$stopDepletedOilField(CallbackInfo callback) {
        this.industrialColonies$oilBeforeProcess = this.tank.getFluidAmount();

        BlockEntity pumpjack = (BlockEntity) (Object) this;
        if (pumpjack.getLevel() == null
                || pumpjack.getLevel().isClientSide
                || this.deposit == null
                || Boolean.TRUE.equals(TFMGConfigs.common().worldgen.infiniteDeposits.get())) {
            return;
        }

        FluidReservoir reservoir = TFMG.DEPOSITS.getReservoirFor(this.deposit.asLong());
        if (reservoir != null && reservoir.oilReserves <= 0) {
            this.miningRate = 0;
            callback.cancel();
        }
    }

    @Inject(method = "process", at = @At("RETURN"), remap = false)
    private void industrialColonies$consumeOilFieldReserve(CallbackInfo callback) {
        BlockEntity pumpjack = (BlockEntity) (Object) this;
        if (pumpjack.getLevel() == null
                || pumpjack.getLevel().isClientSide
                || this.deposit == null
                || Boolean.TRUE.equals(TFMGConfigs.common().worldgen.infiniteDeposits.get())) {
            return;
        }

        int extracted = this.tank.getFluidAmount() - this.industrialColonies$oilBeforeProcess;
        if (extracted <= 0) {
            return;
        }

        FluidReservoir reservoir = TFMG.DEPOSITS.getReservoirFor(this.deposit.asLong());
        if (reservoir == null || reservoir.oilReserves <= 0) {
            return;
        }

        int consumed = extracted / MILLIBUCKETS_PER_RESERVE;
        int remainder = extracted % MILLIBUCKETS_PER_RESERVE;
        if (remainder > 0 && pumpjack.getLevel().getRandom().nextInt(MILLIBUCKETS_PER_RESERVE) < remainder) {
            consumed++;
        }
        if (consumed <= 0) {
            return;
        }

        reservoir.oilReserves = Math.max(0, reservoir.oilReserves - consumed);
        TFMG.DEPOSITS.markDirty();
    }
}
