package dev.godpc.industrialcolonies.space;
/** Transient state only; no chemical inventory is stored here. */
public interface ChemicalDockAccess {
    long ic$chemicalEpoch();
    ChemicalDockService.Lease ic$chemicalLease();
    void ic$chemicalLease(ChemicalDockService.Lease lease);
    void ic$revokeChemical();
}
