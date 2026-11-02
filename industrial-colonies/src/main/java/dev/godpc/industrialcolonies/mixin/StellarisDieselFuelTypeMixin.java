package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.st0x0ef.stellaris.common.registry.ItemsRegistry;
import dev.godpc.industrialcolonies.processing.StellarisDieselIdentity;
import net.minecraft.world.item.*;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.At;

@Pseudo
@Mixin(targets="com.st0x0ef.stellaris.common.vehicle_upgrade.FuelType$Type",remap=false)
public abstract class StellarisDieselFuelTypeMixin {
    @WrapOperation(method="getTypeBasedOnItem",at=@At(value="INVOKE",target="Lnet/minecraft/world/item/ItemStack;is(Lnet/minecraft/world/item/Item;)Z"),require=1)
    private static boolean industrialColonies$canonicalDieselType(ItemStack stack,Item expected,Operation<Boolean> original){
        return original.call(stack,expected)||(expected==ItemsRegistry.DIESEL_BUCKET.get()&&StellarisDieselIdentity.canonicalBucket(stack));
    }
}
