package dev.godpc.industrialcolonies.mixin;
import com.simibubi.create.content.kinetics.deployer.*;
import com.llamalad7.mixinextras.injector.wrapoperation.*;
import com.llamalad7.mixinextras.sugar.Local;
import dev.godpc.industrialcolonies.DeployerToolDamage;
import net.minecraft.world.item.*;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.entity.*;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(value=BeltDeployerCallbacks.class,remap=false)
public abstract class DeployerToolDamageMixin {
 @WrapOperation(method="activate",at=@At(value="INVOKE",target="Lnet/minecraft/world/item/ItemStack;hurtAndBreak(ILnet/minecraft/world/entity/LivingEntity;Lnet/minecraft/world/entity/EquipmentSlot;)V"))
 private static void industrialColonies$wear(ItemStack tool,int amount,LivingEntity entity,EquipmentSlot slot,Operation<Void> original,@Local(argsOnly=true) Recipe<?> recipe) {
  int damage=recipe instanceof ItemApplicationRecipe application && application.getParams() instanceof DeployerToolDamage configured?configured.industrialColonies$damage():amount;
  original.call(tool,damage,entity,slot);
 }
}
