package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import dev.godpc.industrialcolonies.space.*;
import dev.ryanhcode.sable.sublevel.storage.serialization.SubLevelData;
import net.minecraft.server.level.ServerLevel;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

/** Sable's configured load-time damping remains unchanged for unrelated bodies.
 * Only the linear-velocity multiplier is replaced; no post-load impulse occurs. */
@Mixin(targets="dev.ryanhcode.sable.sublevel.storage.serialization.SubLevelSerializer",remap=false)
public abstract class FreightLinearMotionLoadMixin {
 @ModifyExpressionValue(method="fullyLoad",at=@At(value="INVOKE",target="Lnet/neoforged/neoforge/common/ModConfigSpec$DoubleValue;getAsDouble()D",ordinal=0),require=1)
 private static double ic$preserveCommittedLinearMotion(double original,ServerLevel level,SubLevelData data){
  if(!level.getServer().isSameThread())return original;
  return FreightMotionPersistence.preserves(FreightJourneyControl.journal(level.getServer()),level.dimension().location().toString(),data.uuid())?1.0:original;
 }
}
