package dev.godpc.industrialcolonies.space;

import java.util.Objects;
import java.util.function.Supplier;
import mekanism.api.Action;
import mekanism.api.chemical.ChemicalStack;
import mekanism.api.chemical.IChemicalHandler;

/** Unregistered prototype: a revocable view of one existing tank, never another cargo owner. */
public final class ChemicalDockView implements IChemicalHandler {
    private final Supplier<IChemicalHandler> authorizedTarget;
    private boolean revoked;
    private boolean busy;

    /** Resolver must check the server thread, reciprocal physical link, epoch and backing-tank identity. */
    public ChemicalDockView(Supplier<IChemicalHandler> authorizedTarget) {
        this.authorizedTarget=Objects.requireNonNull(authorizedTarget);
    }

    /** An old handle stays revoked after reconnect; the new physical link needs a new view. */
    public void revoke() { revoked=true; }

    private <T> T access(int tank, T denied, java.util.function.Function<IChemicalHandler,T> operation) {
        if(revoked || busy)return denied;
        busy=true;
        try {
            IChemicalHandler target=authorizedTarget.get();
            if(revoked || target==null || target instanceof ChemicalDockView)return denied;
            if(tank>=0 && tank>=target.getChemicalTanks())return denied;
            return operation.apply(target);
        } finally {busy=false;}
    }

    @Override public int getChemicalTanks() {return access(-1,0,IChemicalHandler::getChemicalTanks);}
    @Override public ChemicalStack getChemicalInTank(int tank) {
        return tank<0?ChemicalStack.EMPTY:access(tank,ChemicalStack.EMPTY,h->h.getChemicalInTank(tank).copy());
    }
    @Override public void setChemicalInTank(int tank,ChemicalStack stack) {
        throw new UnsupportedOperationException("Dock views support insertion/extraction, not replacing tank ownership");
    }
    @Override public long getChemicalTankCapacity(int tank) {
        return tank<0?0:access(tank,0L,h->h.getChemicalTankCapacity(tank));
    }
    @Override public boolean isValid(int tank,ChemicalStack stack) {
        return tank>=0 && access(tank,false,h->h.isValid(tank,stack.copy()));
    }
    @Override public ChemicalStack insertChemical(int tank,ChemicalStack stack,Action action) {
        Objects.requireNonNull(stack);Objects.requireNonNull(action);
        return tank<0?stack.copy():access(tank,stack.copy(),h->h.insertChemical(tank,stack.copy(),action).copy());
    }
    @Override public ChemicalStack extractChemical(int tank,long amount,Action action) {
        Objects.requireNonNull(action);
        return tank<0 || amount<=0?ChemicalStack.EMPTY:access(tank,ChemicalStack.EMPTY,h->h.extractChemical(tank,amount,action).copy());
    }
}
