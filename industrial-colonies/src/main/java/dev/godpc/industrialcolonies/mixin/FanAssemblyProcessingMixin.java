package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.content.kinetics.belt.behaviour.TransportedItemStackHandlerBehaviour.TransportedResult;
import com.simibubi.create.content.kinetics.belt.transport.TransportedItemStack;
import com.simibubi.create.content.kinetics.fan.processing.*;
import dev.godpc.industrialcolonies.processing.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import java.util.*;

@Mixin(value=FanProcessing.class, priority=1100)
public abstract class FanAssemblyProcessingMixin {
    @Unique private static final Map<TransportedItemStack, AssemblyCookTimer.State> industrialColonies$timers = new WeakHashMap<>();
    @Unique private static final String industrialColonies$timerKey = "IndustrialColoniesAssemblyCooking";

    @Inject(method="canProcess(Lnet/minecraft/world/entity/item/ItemEntity;Lcom/simibubi/create/content/kinetics/fan/processing/FanProcessingType;)Z",at=@At("HEAD"),cancellable=true)
    private static void industrialColonies$canCook(ItemEntity entity, FanProcessingType type, CallbackInfoReturnable<Boolean> ci) {
        if (AssemblyRuntime.fan(entity.level(),entity.getItem(),type).isPresent()) ci.setReturnValue(true);
        else if (AssemblyRuntime.active(entity.getItem())) ci.setReturnValue(false);
    }
    @Inject(method="applyProcessing(Lnet/minecraft/world/entity/item/ItemEntity;Lcom/simibubi/create/content/kinetics/fan/processing/FanProcessingType;)Z",at=@At("HEAD"),cancellable=true)
    private static void industrialColonies$cookEntity(ItemEntity entity, FanProcessingType type, CallbackInfoReturnable<Boolean> ci) {
        var match = AssemblyRuntime.fan(entity.level(),entity.getItem(),type);
        if (match.isEmpty()) {
            entity.getPersistentData().remove(industrialColonies$timerKey);
            if (AssemblyRuntime.active(entity.getItem())) ci.setReturnValue(false);
            return;
        }
        ci.setReturnValue(false);
        if (entity.level().isClientSide) return;
        var saved = entity.getPersistentData().getCompound(industrialColonies$timerKey);
        AssemblyCookTimer.State before = saved.contains("Key") ? new AssemblyCookTimer.State(saved.getString("Key"),saved.getLong("Tick"),saved.getInt("Remaining")) : null;
        var state = AssemblyCookTimer.tick(before, match.get().key()+"/"+AssemblyRuntime.fanMode(type), match.get().ticks(), entity.level().getGameTime());
        var nbt = new CompoundTag(); nbt.putString("Key",state.key()); nbt.putLong("Tick",state.lastTick()); nbt.putInt("Remaining",state.remaining());
        entity.getPersistentData().put(industrialColonies$timerKey,nbt);
        if (state.remaining() != 0) return;
        var outputs = AssemblyRuntime.fanResults(match.get(),entity.level());
        entity.getPersistentData().remove(industrialColonies$timerKey);
        if (outputs.isEmpty()) entity.discard();
        else {
            entity.setItem(outputs.getFirst());
            for (int i=1;i<outputs.size();i++) {
                var extra = new ItemEntity(entity.level(),entity.getX(),entity.getY(),entity.getZ(),outputs.get(i));
                extra.setDeltaMovement(entity.getDeltaMovement());entity.level().addFreshEntity(extra);
            }
        }
        ci.setReturnValue(true);
    }
    @Inject(method="applyProcessing(Lcom/simibubi/create/content/kinetics/belt/transport/TransportedItemStack;Lnet/minecraft/world/level/Level;Lcom/simibubi/create/content/kinetics/fan/processing/FanProcessingType;)Lcom/simibubi/create/content/kinetics/belt/behaviour/TransportedItemStackHandlerBehaviour$TransportedResult;",at=@At("HEAD"),cancellable=true)
    private static void industrialColonies$cookTransported(TransportedItemStack item, Level level, FanProcessingType type, CallbackInfoReturnable<TransportedResult> ci) {
        var match = AssemblyRuntime.fan(level,item.stack,type);
        if (match.isEmpty()) {
            industrialColonies$timers.remove(item);
            if (AssemblyRuntime.active(item.stack)) ci.setReturnValue(TransportedResult.doNothing());
            return;
        }
        ci.setReturnValue(TransportedResult.doNothing());
        if (level.isClientSide) return;
        var state = AssemblyCookTimer.tick(industrialColonies$timers.get(item), match.get().key()+"/"+AssemblyRuntime.fanMode(type),match.get().ticks(),level.getGameTime());
        industrialColonies$timers.put(item,state);
        if (state.remaining()!=0) return;
        industrialColonies$timers.remove(item);
        var outputs = new ArrayList<TransportedItemStack>();
        for (var stack : AssemblyRuntime.fanResults(match.get(),level)) {
            var next = item.getSimilar();next.stack=stack;next.clearFanProcessingData();outputs.add(next);
        }
        ci.setReturnValue(TransportedResult.convertTo(outputs));
    }
}
