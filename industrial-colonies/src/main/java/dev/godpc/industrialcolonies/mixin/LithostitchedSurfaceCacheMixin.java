package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import net.minecraft.world.level.levelgen.SurfaceRules;
import net.neoforged.fml.ModList;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Coerce;

/** Native additions must not be hidden by TerraBlender's previously computed cache. */
@Pseudo
@Mixin(targets="dev.worldgen.lithostitched.worldgen.surface.SurfaceRuleManager",remap=false)
public abstract class LithostitchedSurfaceCacheMixin {
 @WrapOperation(method="applySurfaceRules",at=@At(value="INVOKE",target="Ldev/worldgen/lithostitched/mixin/common/NoiseGeneratorSettingsAccessor;setSurfaceRule(Lnet/minecraft/world/level/levelgen/SurfaceRules$RuleSource;)V"),require=1)
 private static void industrialColonies$refreshNativeSurfaceCache(@Coerce Object settings,SurfaceRules.RuleSource rule,Operation<Void> original){
  original.call(settings,rule);
  if(!ModList.get().isLoaded("terrablender"))return;
  try{
   // Exact installed TerraBlender field; no rule definition or world block is changed.
   var cache=settings.getClass().getDeclaredField("namespacedSurfaceRuleSource");
   cache.setAccessible(true);cache.set(settings,null);
  }catch(ReflectiveOperationException failure){
   throw new IllegalStateException("Unsupported TerraBlender surface-rule cache API",failure);
  }
 }
}
