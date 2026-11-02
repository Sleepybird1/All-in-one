package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.st0x0ef.stellaris.common.registry.TagRegistry;
import dev.godpc.industrialcolonies.processing.StellarisDieselIdentity;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.*;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.At;

/** Return the emptied diesel container without classifying diesel as generic rocket fuel. */
@Pseudo
@Mixin(targets="com.st0x0ef.stellaris.common.entities.vehicles.RocketEntity",remap=false)
public abstract class StellarisDieselRocketContainerMixin {
    @WrapOperation(method="tryFillUpRocket",at=@At(value="INVOKE",target="Lnet/minecraft/world/item/ItemStack;is(Lnet/minecraft/tags/TagKey;)Z"),require=1)
    private boolean industrialColonies$returnDieselBucket(ItemStack stack,TagKey<Item> expected,Operation<Boolean> original){
        return original.call(stack,expected)||(expected.equals(TagRegistry.FUEL)&&StellarisDieselIdentity.dieselBucket(stack));
    }
}
