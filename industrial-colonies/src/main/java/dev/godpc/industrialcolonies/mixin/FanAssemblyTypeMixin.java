package dev.godpc.industrialcolonies.mixin;
import com.simibubi.create.content.kinetics.fan.processing.FanProcessingType;
import dev.godpc.industrialcolonies.processing.AssemblyRuntime;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(targets={
 "com.simibubi.create.content.kinetics.fan.processing.AllFanProcessingTypes$SmokingType",
 "com.simibubi.create.content.kinetics.fan.processing.AllFanProcessingTypes$BlastingType",
 "com.simibubi.create.content.kinetics.fan.processing.AllFanProcessingTypes$SplashingType",
 "com.simibubi.create.content.kinetics.fan.processing.AllFanProcessingTypes$HauntingType"})
public abstract class FanAssemblyTypeMixin {
    @Inject(method="canProcess",at=@At("HEAD"),cancellable=true)
    private void industrialColonies$assemblyInput(ItemStack stack, Level level, CallbackInfoReturnable<Boolean> ci) {
        if (AssemblyRuntime.fan(level,stack,(FanProcessingType)(Object)this).isPresent()) ci.setReturnValue(true);
        else if (AssemblyRuntime.active(stack)) ci.setReturnValue(false);
    }
}
