package dev.godpc.industrialcolonies.geology.oil;

import com.drmangotea.tfmg.content.machinery.oil_processing.pumpjack.base.FluidReservoir;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler.FluidAction;
import net.neoforged.neoforge.fluids.capability.templates.FluidTank;
import java.io.IOException;
import java.util.*;

/** Opt-in native save/accounting adapter. No event or mixin registration.
 * The owner must serialize this with its reservoir and qualify tank/save custody. */
public final class NativeOilBalance {
    public static final String EXACT="IndustrialColoniesExactOilV1";
    public static final String SCOPE="IndustrialColoniesOilScopeV1";
    private final FluidReservoir reservoir;
    private final String scope;
    private OilReserveBalance balance;
    private boolean busy,held;
    private static String scope(OilFieldBudget.Key key,FluidReservoir reservoir){return OilFieldBudget.select(key).fingerprint()+"/"+reservoir.id;}
    private NativeOilBalance(FluidReservoir reservoir,OilReserveBalance balance,OilFieldBudget.Key key){this.reservoir=reservoir;this.balance=balance;this.scope=scope(key,reservoir);}
    private static void authority(OilFieldBudget.Key key,FluidReservoir reservoir,CompoundTag saved)throws IOException {
        if(!key.dimension().equals("minecraft:overworld"))throw new IOException("Native oil authority is Overworld-only");
        if(!saved.contains("Id",Tag.TAG_LONG)||saved.getLong("Id")!=reservoir.id
                ||!saved.contains("Reserves",Tag.TAG_INT)||saved.getInt("Reserves")!=reservoir.oilReserves)
            throw new IOException("Saved/native oil identity or reserve mismatch");
    }
    /** Explicit legacy classification is required; never call as a fallback after load fails. */
    public static NativeOilBalance migrateLegacy(OilFieldBudget.Key key,FluidReservoir reservoir,CompoundTag saved)throws IOException {
        authority(key,reservoir,saved);
        if(saved.contains(EXACT)||saved.contains(SCOPE))throw new IOException("Exact oil marker forbids legacy remigration");
        try{return new NativeOilBalance(reservoir,OilReserveBalance.migrateLegacy(key.fieldIdentity(),reservoir.oilReserves),key);}
        catch(IllegalArgumentException e){throw new IOException("Invalid legacy oil",e);}
    }
    /** Explicit fresh-field admission only. The durable permit cannot be replayed after restart.
     * Caller must publish the returned exact state before enabling extraction. */
    public static NativeOilBalance commission(OilFieldBudget.Key key,FluidReservoir reservoir,CompoundTag saved,OilFieldAllocations.CommissionPermit permit)throws IOException {
        authority(key,reservoir,saved);
        if(reservoir.oilReserves!=0||saved.contains(EXACT)||saved.contains(SCOPE))throw new IOException("New oil field must be empty and uncommissioned");
        if(reservoir.deposits==null||reservoir.deposits.size()!=1||!Objects.equals(reservoir.deposits.getFirst(),reservoir.id))throw new IOException("New oil field must have only its founding well");
        if(permit==null)throw new IOException("Missing durable oil commissioning permit");
        var budget=permit.take(key,reservoir.id);
        var exact=new OilReserveBalance(key.fieldIdentity(),budget.totalMb());
        var state=new NativeOilBalance(reservoir,exact,key);
        reservoir.oilReserves=exact.nativeBuckets();
        saved.putInt("Reserves",reservoir.oilReserves);
        state.save(saved);
        return state;
    }
    public static NativeOilBalance load(OilFieldBudget.Key key,FluidReservoir reservoir,CompoundTag saved)throws IOException {
        authority(key,reservoir,saved);
        if(!saved.contains(EXACT,Tag.TAG_BYTE_ARRAY))throw new IOException("Missing exact oil state");
        if(!saved.contains(SCOPE,Tag.TAG_STRING)||!saved.getString(SCOPE).equals(scope(key,reservoir)))throw new IOException("Oil environment/category/native identity scope changed");
        return new NativeOilBalance(reservoir,OilReserveBalance.decode(saved.getByteArray(EXACT),key.fieldIdentity(),reservoir.oilReserves),key);
    }
    public synchronized void save(CompoundTag saved)throws IOException {
        ready();
        if(!saved.contains("Id",Tag.TAG_LONG)||saved.getLong("Id")!=reservoir.id
                ||!saved.contains("Reserves",Tag.TAG_INT)||saved.getInt("Reserves")!=reservoir.oilReserves)
            throw new IOException("Save target is not the owning native reservoir");
        saved.putByteArray(EXACT,balance.encode());
        saved.putString(SCOPE,scope);
    }
    /** A native tank adapter returns FluidTank.fill(EXECUTE)'s actual accepted amount.
     * It must not initiate nested extraction; throws make the outcome held/uncertain. */
    @FunctionalInterface public interface Fill {int execute(int maximumMb)throws Exception;}
    /** Uses the native tank's accepted return; the caller supplies the admitted crude-oil type. */
    public synchronized int extractInto(String dimension,List<FluidReservoir> all,long well,int miningRate,FluidTank tank,FluidStack fluid)throws IOException {
        ready();Objects.requireNonNull(tank);Objects.requireNonNull(fluid);
        if(fluid.isEmpty())throw new IOException("Missing admitted oil fluid");
        int free=tank.getCapacity()-tank.getFluidAmount();
        return extract(dimension,all,well,miningRate,free,amount->tank.fill(fluid.copyWithAmount(amount),FluidAction.EXECUTE));
    }
    public synchronized int extract(String dimension,List<FluidReservoir> all,long well,int miningRate,int freeCapacity,Fill fill)throws IOException {
        ready();Objects.requireNonNull(fill);
        if(!"minecraft:overworld".equals(dimension))throw new IOException("Non-Overworld oil access");
        int matching=0,owners=0;
        for(var entry:all){
            if(entry==reservoir)owners++;
            if(entry.deposits==null)throw new IOException("Missing well membership");
            if(entry.id==reservoir.id&&entry!=reservoir)throw new IOException("Duplicate native reservoir identity");
            if(entry.deposits.contains(well)){
                matching++;
                if(entry!=reservoir||Collections.frequency(entry.deposits,well)!=1)throw new IOException("Ambiguous oil well membership");
            }
        }
        if(owners!=1||matching!=1)throw new IOException("Oil reservoir ownership changed");
        if(miningRate<0||freeCapacity<0)throw new IOException("Invalid native fill limits");
        // Native process requires room for the whole mining-rate request.
        if(miningRate>freeCapacity||miningRate==0||balance.remainingMb()==0)return 0;
        int allowed=balance.available(miningRate,freeCapacity);busy=true;
        try{
            int accepted=fill.execute(allowed);
            if(held||accepted<0||accepted>allowed||reservoir.oilReserves!=balance.nativeBuckets())throw new IOException("Uncertain or invalid accepted oil fill");
            balance=balance.consume(accepted);reservoir.oilReserves=balance.nativeBuckets();return accepted;
        }catch(Exception e){held=true;throw new IOException("Oil fill outcome held; do not retry or remigrate",e);}
        finally{busy=false;}
    }
    public synchronized long remainingMb()throws IOException {ready();return balance.remainingMb();}
    private void ready()throws IOException {
        if(busy){held=true;throw new IOException("Reentrant oil extraction");}
        if(held||reservoir.oilReserves!=balance.nativeBuckets())throw new IOException("Oil balance held or native mirror changed");
    }
}
