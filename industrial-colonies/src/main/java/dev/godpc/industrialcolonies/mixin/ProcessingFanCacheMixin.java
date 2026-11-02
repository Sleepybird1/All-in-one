package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.content.kinetics.belt.behaviour.TransportedItemStackHandlerBehaviour;
import com.simibubi.create.content.kinetics.belt.transport.TransportedItemStack;
import com.simibubi.create.content.kinetics.fan.processing.FanProcessing;
import com.simibubi.create.content.kinetics.fan.processing.FanProcessingType;
import dev.godpc.industrialcolonies.processing.FanRecipeCache;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Create caches rejection by process type, not fan identity. Re-evaluate only machine-bound inputs. */
@Mixin(FanProcessing.class)
public abstract class ProcessingFanCacheMixin {
    @Inject(method = "canProcess(Lnet/minecraft/world/entity/item/ItemEntity;Lcom/simibubi/create/content/kinetics/fan/processing/FanProcessingType;)Z",
            at = @At("HEAD"), cancellable = true)
    private static void industrialColonies$refreshEntity(ItemEntity entity, FanProcessingType type,
                                                        CallbackInfoReturnable<Boolean> callback) {
        if (!FanRecipeCache.tierSensitive(entity.getItem(), entity.level())) return;
        boolean allowed = type.canProcess(entity.getItem(), entity.level());
        CompoundTag createData = entity.getPersistentData().getCompound("CreateData");
        CompoundTag processing = createData.getCompound("Processing");
        if (!allowed || (processing.contains("Time") && processing.getInt("Time") < 0)) createData.remove("Processing");
        callback.setReturnValue(allowed);
    }

    @Inject(method = "applyProcessing(Lcom/simibubi/create/content/kinetics/belt/transport/TransportedItemStack;Lnet/minecraft/world/level/Level;Lcom/simibubi/create/content/kinetics/fan/processing/FanProcessingType;)Lcom/simibubi/create/content/kinetics/belt/behaviour/TransportedItemStackHandlerBehaviour$TransportedResult;",
            at = @At("HEAD"), cancellable = true)
    private static void industrialColonies$refreshTransported(TransportedItemStack transported, Level level,
            FanProcessingType type, CallbackInfoReturnable<TransportedItemStackHandlerBehaviour.TransportedResult> callback) {
        if (!FanRecipeCache.tierSensitive(transported.stack, level)) return;
        if (!type.canProcess(transported.stack, level)) {
            transported.clearFanProcessingData();
            callback.setReturnValue(TransportedItemStackHandlerBehaviour.TransportedResult.doNothing());
        } else if (transported.processingTime < 0) {
            transported.clearFanProcessingData();
        }
    }
}
