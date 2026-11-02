package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.transport.PortableJerrycanStorage;
import java.util.function.Supplier;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.fluids.SimpleFluidContent;
import net.neoforged.neoforge.fluids.capability.templates.FluidHandlerItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Constant;
import org.spongepowered.asm.mixin.injection.ModifyConstant;
import org.spongepowered.asm.mixin.injection.Redirect;

@Pseudo
@Mixin(targets = "blusunrize.immersiveengineering.common.items.JerrycanItem", remap = false)
public abstract class PortableJerrycanMixin {
    @Redirect(method = "lambda$registerCapabilities$1", at = @At(value = "NEW",
            target = "net/neoforged/neoforge/fluids/capability/templates/FluidHandlerItemStack"), require = 1)
    private static FluidHandlerItemStack industrialColonies$boundedCan(
            Supplier<DataComponentType<SimpleFluidContent>> component, ItemStack stack, int capacity) {
        return new PortableJerrycanStorage(component, stack, capacity);
    }

    @ModifyConstant(method = "lambda$appendHoverText$0", constant = @Constant(intValue = 10000), require = 1)
    private static int industrialColonies$displayCapacity(int original) { return Math.min(original, 8000); }
}
