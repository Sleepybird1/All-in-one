package dev.godpc.industrialcolonies.geology.oil;

import com.drmangotea.tfmg.content.machinery.oil_processing.pumpjack.base.FluidReservoir;
import net.minecraft.nbt.*;
import java.io.IOException;
import java.util.*;

/** Opt-in per-server owner. Not globally installed. Native load must restore saved well links first. */
public final class NativeOilSession {
    public static final String FORMAT="IndustrialColoniesOilSession";
    private final Map<Long,FluidReservoir> owners;
    private final Map<Long,NativeOilBalance> balances;
    private final Map<Long,OilFieldBudget.Key> keys;
    private boolean closed;
    private long revocations;
    private NativeOilSession(Map<Long,FluidReservoir> owners,Map<Long,NativeOilBalance> balances,Map<Long,OilFieldBudget.Key> keys){this.owners=new HashMap<>(owners);this.balances=new HashMap<>(balances);this.keys=new HashMap<>(keys);}
    /** legacy=true is an explicit one-time operator decision, never an automatic load fallback. */
    public static NativeOilSession open(List<FluidReservoir> nativeList,Map<Long,OilFieldBudget.Key> keys,CompoundTag root,boolean legacy)throws IOException {
        boolean marked=root.contains(FORMAT);
        if(legacy&&marked)throw new IOException("Exact session cannot remigrate");
        if(!legacy&&(!root.contains(FORMAT,Tag.TAG_INT)||root.getInt(FORMAT)!=1))throw new IOException("Missing or unsupported exact oil session");
        var records=validate(nativeList,root);var owners=new HashMap<Long,FluidReservoir>();var balances=new HashMap<Long,NativeOilBalance>();
        if(keys.size()!=nativeList.size())throw new IOException("Oil field authority set mismatch");
        var fields=new HashSet<String>();
        OilFieldBudget.Key environment=null;
        for(var r:nativeList){
            var key=keys.get(r.id);if(key==null||!fields.add(key.fieldIdentity()))throw new IOException("Missing or repeated oil field authority");
            if(environment==null)environment=key;
            if(key.worldSeed()!=environment.worldSeed()||!key.dimension().equals(environment.dimension())||!key.presetSha256().equals(environment.presetSha256()))throw new IOException("Mixed oil world authority");
            var balance=legacy?NativeOilBalance.migrateLegacy(key,r,records.get(r.id)):NativeOilBalance.load(key,r,records.get(r.id));
            owners.put(r.id,r);balances.put(r.id,balance);
        }
        return new NativeOilSession(owners,balances,keys);
    }
    /** Must persist the complete supplied root and return an independently read-back root.
     * A failed/uncertain publication closes the session; it never grants another permit. */
    @FunctionalInterface public interface Publish {CompoundTag persistAndRead(CompoundTag root)throws Exception;}
    public synchronized void admitNew(List<FluidReservoir> current,CompoundTag nativeRoot,FluidReservoir added,
            OilFieldBudget.Key key,OilFieldAllocations.CommissionPermit permit,Publish publish)throws IOException {
        if(closed||added==null||publish==null||owners.containsKey(added.id))throw new IOException("Invalid new oil admission");
        var previous=new ArrayList<FluidReservoir>();int found=0;
        for(var r:current){if(r==added)found++;else previous.add(r);}
        if(found!=1)throw new IOException("New reservoir is not uniquely present");
        current(previous);
        for(var existing:keys.values()){
            if(existing.fieldIdentity().equals(key.fieldIdentity()))throw new IOException("Field already admitted");
            if(existing.worldSeed()!=key.worldSeed()||!existing.dimension().equals(key.dimension())||!existing.presetSha256().equals(key.presetSha256()))throw new IOException("New field environment differs");
        }
        var copy=nativeRoot.copy();var records=validate(current,copy);
        for(var r:previous)balances.get(r.id).save(records.get(r.id));
        // Close before consuming authority or calling external persistence, including reentrant calls.
        var admittedObjects=List.copyOf(current);long epoch=revocations;closed=true;
        try {
            var balance=NativeOilBalance.commission(key,added,records.get(added.id),permit);
            copy.putInt(FORMAT,1);var expected=copy.copy();
            var readback=publish.persistAndRead(copy);
            if(epoch!=revocations||current.size()!=admittedObjects.size())throw new IOException("Oil admission revoked or native set changed");
            for(int i=0;i<current.size();i++)if(current.get(i)!=admittedObjects.get(i))throw new IOException("Oil admission native object changed");
            if(readback==null||!expected.equals(readback))throw new IOException("Oil admission publication differs");
            validate(current,readback);
            for(var r:previous)balances.get(r.id).remainingMb();
            balance.remainingMb();
            owners.put(added.id,added);balances.put(added.id,balance);keys.put(added.id,key);
            closed=false;
        }catch(Exception e){throw new IOException("Oil admission held; audit persisted state before reopening",e);}
    }
    /** Produce a copy only after all native records and balances pass validation. */
    public synchronized CompoundTag save(List<FluidReservoir> current,CompoundTag nativeRoot)throws IOException {
        current(current);var copy=nativeRoot.copy();var records=validate(current,copy);
        for(var r:current)balances.get(r.id).save(records.get(r.id));
        copy.putInt(FORMAT,1);return copy;
    }
    public synchronized long remainingForWell(List<FluidReservoir> current,long well)throws IOException {return forWell(current,well).remainingMb();}
    public synchronized int extract(List<FluidReservoir> current,String dimension,long well,int rate,int capacity,NativeOilBalance.Fill fill)throws IOException {
        return forWell(current,well).extract(dimension,current,well,rate,capacity,fill);
    }
    public synchronized int extractInto(List<FluidReservoir> current,String dimension,long well,int rate,net.neoforged.neoforge.fluids.capability.templates.FluidTank tank,net.neoforged.neoforge.fluids.FluidStack fluid)throws IOException {
        return forWell(current,well).extractInto(dimension,current,well,rate,tank,fluid);
    }
    private NativeOilBalance forWell(List<FluidReservoir> current,long well)throws IOException {
        current(current);FluidReservoir match=null;
        var wells=new HashSet<Long>();
        for(var r:current){
            if(r.deposits==null)throw new IOException("Missing native oil links");
            for(Long pos:r.deposits){if(pos==null||!wells.add(pos))throw new IOException("Ambiguous native well");if(pos==well)match=r;}
        }
        if(match==null)throw new IOException("Unadmitted oil well");
        return balances.get(match.id);
    }
    public synchronized void close(){closed=true;revocations++;}
    private void current(List<FluidReservoir> current)throws IOException {
        if(closed||current.size()!=owners.size())throw new IOException("Oil session closed or reservoir set changed");
        var ids=new HashSet<Long>();
        for(var r:current)if(r==null||!ids.add(r.id)||owners.get(r.id)!=r)throw new IOException("Native oil reservoir replaced");
    }
    private static Map<Long,CompoundTag> validate(List<FluidReservoir> current,CompoundTag root)throws IOException {
        if(!root.contains("reservoirCount",Tag.TAG_INT)||root.getInt("reservoirCount")!=current.size())throw new IOException("Native oil save count mismatch");
        var records=new HashMap<Long,CompoundTag>();var allWells=new HashSet<Long>();
        for(int i=0;i<current.size();i++){
            var r=current.get(i);if(r==null||r.deposits==null||r.deposits.isEmpty()||r.deposits.size()>65536)throw new IOException("Invalid native well list");
            String name="FluidReservoir"+i;if(!root.contains(name,Tag.TAG_COMPOUND))throw new IOException("Missing native oil record");
            var tag=root.getCompound(name);
            if(!tag.contains("Id",Tag.TAG_LONG)||tag.getLong("Id")!=r.id||records.put(r.id,tag)!=null
                    ||!tag.contains("Reserves",Tag.TAG_INT)||tag.getInt("Reserves")!=r.oilReserves
                    ||!tag.contains("DepositCount",Tag.TAG_INT)||tag.getInt("DepositCount")!=r.deposits.size())throw new IOException("Native oil record mismatch");
            var savedWells=new HashSet<Long>();
            for(int j=0;j<r.deposits.size();j++){
                String field="Deposit"+j;if(!tag.contains(field,Tag.TAG_LONG)||!savedWells.add(tag.getLong(field)))throw new IOException("Invalid saved oil links");
            }
            if(!savedWells.equals(new HashSet<>(r.deposits))||savedWells.size()!=r.deposits.size()||!savedWells.contains(r.id))throw new IOException("Native/saved well membership differs");
            for(long well:savedWells)if(!allWells.add(well))throw new IOException("Well belongs to multiple oil fields");
        }
        return records;
    }
}
