package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.st0x0ef.stellaris.common.registry.ItemsRegistry;
import dev.godpc.industrialcolonies.processing.StellarisDieselIdentity;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;

/** Preserve the native empty-bucket return for the canonical fuel bucket too. */
@Pseudo
@Mixin(targets="com.st0x0ef.stellaris.common.entities.vehicles.RoverEntity",remap=false)
public abstract class StellarisRoverFuelContainerMixin {
    @WrapOperation(method="tryFillUpRover",at=@At(value="INVOKE",target="Lnet/minecraft/world/item/ItemStack;is(Lnet/minecraft/world/item/Item;)Z"),require=2)
    private boolean industrialColonies$returnCanonicalFuelBucket(ItemStack stack,Item expected,Operation<Boolean> original){
        if(original.call(stack,expected)) return true;
        return expected==ItemsRegistry.FUEL_BUCKET.get()
                &&(BuiltInRegistries.ITEM.getKey(stack.getItem()).equals(ResourceLocation.parse("ad_astra:fuel_bucket"))
                ||StellarisDieselIdentity.dieselBucket(stack));
    }
}
