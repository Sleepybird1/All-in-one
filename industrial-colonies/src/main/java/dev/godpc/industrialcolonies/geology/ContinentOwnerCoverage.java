package dev.godpc.industrialcolonies.geology;

import java.util.*;

/** Exact 16x16 native identity coverage. Corners or a center sample cannot certify a border chunk. */
public final class ContinentOwnerCoverage {
 @FunctionalInterface public interface Sampler { ReTerraForgedGeography.ContinentKey at(int x,int z); }
 private final int chunkX,chunkZ;
 private final List<ReTerraForgedGeography.ContinentKey> columns,keys;
 private ContinentOwnerCoverage(int x,int z,List<ReTerraForgedGeography.ContinentKey> columns){
  chunkX=x;chunkZ=z;this.columns=List.copyOf(columns);
  var unique=new TreeSet<ReTerraForgedGeography.ContinentKey>(Comparator.comparingInt(ReTerraForgedGeography.ContinentKey::centerX).thenComparingInt(ReTerraForgedGeography.ContinentKey::centerZ).thenComparingInt(ReTerraForgedGeography.ContinentKey::identityBits));
  unique.addAll(columns);keys=List.copyOf(unique);
 }
 public static ContinentOwnerCoverage sample(int chunkX,int chunkZ,Sampler sampler){
  Objects.requireNonNull(sampler);long x=(long)chunkX*16,z=(long)chunkZ*16;
  if(x<=-ContinentEnvelope.LIMIT||z<=-ContinentEnvelope.LIMIT||x+15>=ContinentEnvelope.LIMIT||z+15>=ContinentEnvelope.LIMIT)throw new IllegalArgumentException("Owner outside exact native geography domain");
  var columns=new ArrayList<ReTerraForgedGeography.ContinentKey>(256);
  for(int dz=0;dz<16;dz++)for(int dx=0;dx<16;dx++)columns.add(Objects.requireNonNull(sampler.at((int)x+dx,(int)z+dz)));
  return new ContinentOwnerCoverage(chunkX,chunkZ,columns);
 }
 public int chunkX(){return chunkX;}public int chunkZ(){return chunkZ;}
 public List<ReTerraForgedGeography.ContinentKey> keys(){return keys;}
 public boolean contains(ReTerraForgedGeography.ContinentKey key,int x,int z){
  return Math.floorDiv(x,16)==chunkX&&Math.floorDiv(z,16)==chunkZ&&columns.get((z&15)*16+(x&15)).equals(key);
 }
}
