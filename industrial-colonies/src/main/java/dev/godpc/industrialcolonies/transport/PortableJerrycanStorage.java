package dev.godpc.industrialcolonies.transport;

import java.util.function.Supplier;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.SimpleFluidContent;
import net.neoforged.neoforge.fluids.capability.templates.FluidHandlerItemStack;

/** Keep legacy cargo extractable without reporting a negative insertion into an overfull can. */
public final class PortableJerrycanStorage extends FluidHandlerItemStack {
    public PortableJerrycanStorage(Supplier<DataComponentType<SimpleFluidContent>> component,
                                   ItemStack container, int nativeCapacity) {
        super(component, container, Math.min(nativeCapacity, 8000));
    }

    @Override
    public int fill(FluidStack resource, FluidAction action) {
        if (getFluidInTank(0).getAmount() >= getTankCapacity(0)) return 0;
        return super.fill(resource, action);
    }
}
