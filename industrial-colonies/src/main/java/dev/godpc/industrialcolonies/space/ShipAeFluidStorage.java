package dev.godpc.industrialcolonies.space;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.fluids.FluidStack;
import java.util.function.BooleanSupplier;
/** Held capability references are checked again after assembly. Ground fluids unchanged. */
public record ShipAeFluidStorage(IFluidHandler delegate, BooleanSupplier allowed) implements IFluidHandler {
 public int getTanks(){return allowed.getAsBoolean()?delegate.getTanks():0;}
 public FluidStack getFluidInTank(int tank){return allowed.getAsBoolean()?delegate.getFluidInTank(tank):FluidStack.EMPTY;}
 public int getTankCapacity(int tank){return allowed.getAsBoolean()?delegate.getTankCapacity(tank):0;}
 public boolean isFluidValid(int tank,FluidStack stack){return allowed.getAsBoolean()&&delegate.isFluidValid(tank,stack);}
 public int fill(FluidStack stack,FluidAction mode){return allowed.getAsBoolean()?delegate.fill(stack,mode):0;}
 public FluidStack drain(FluidStack stack,FluidAction mode){return allowed.getAsBoolean()?delegate.drain(stack,mode):FluidStack.EMPTY;}
 public FluidStack drain(int amount,FluidAction mode){return allowed.getAsBoolean()?delegate.drain(amount,mode):FluidStack.EMPTY;}
}
