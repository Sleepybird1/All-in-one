package dev.godpc.industrialcolonies.geology;
import net.minecraft.nbt.*;
import java.io.IOException;

/** Shared node/chunk encoding with explicit new-scope tags and readable legacy fields. */
public final class MiningScopeTags {
 public static CompoundTag save(MiningScanScope s){
  var t=new CompoundTag();
  if(s.isContinent()){t.putInt("ScopeVersion",2);try{t.putByteArray("ContinentScope",ContinentMiningCodec.encode(s));}catch(IOException e){throw new IllegalStateException(e);}return t;}
  var b=s.body();t.putString("Dimension",s.dimension());t.putString("Family",s.family());t.putInt("RegionX",s.regionX());t.putInt("RegionZ",s.regionZ());t.putInt("MinY",s.minBuildY());t.putInt("MaxY",s.maxBuildYExclusive());t.putLong("Seed",b.seed());t.putDouble("X",b.cx());t.putDouble("Y",b.cy());t.putDouble("Z",b.cz());t.putDouble("RX",b.rx());t.putDouble("RY",b.ry());t.putDouble("RZ",b.rz());return t;
 }
 public static MiningScanScope load(CompoundTag t){
  if(t.contains("ScopeVersion")&&!t.contains("ScopeVersion",Tag.TAG_INT))throw new IllegalArgumentException("Invalid scope version type");int v=t.contains("ScopeVersion")?t.getInt("ScopeVersion"):1;
  if(v==2){if(!t.contains("ContinentScope",Tag.TAG_BYTE_ARRAY))throw new IllegalArgumentException("Missing continent scope");try{return ContinentMiningCodec.decode(t.getByteArray("ContinentScope"));}catch(IOException e){throw new IllegalArgumentException(e);}}
  if(v!=1||t.contains("ContinentScope"))throw new IllegalArgumentException("Unknown or mismatched scope version");
  var b=new MassiveDepositGeometry.Body(t.getLong("Seed"),t.getDouble("X"),t.getDouble("Y"),t.getDouble("Z"),t.getDouble("RX"),t.getDouble("RY"),t.getDouble("RZ"));return new MiningScanScope(t.getString("Dimension"),t.getString("Family"),t.getInt("RegionX"),t.getInt("RegionZ"),b,t.getInt("MinY"),t.getInt("MaxY"));
 }
 private MiningScopeTags(){}
}
