package dev.godpc.industrialcolonies.geology;
import java.io.*;
import java.security.*;
import java.util.*;

/** Immutable legacy field or exact continent reservation. Geometry alone never proves natural ore. */
public final class MiningScanScope {
 private final String dimension,family,key,geometryFingerprint;
 private final int regionX,regionZ,minBuildY,maxBuildYExclusive;
 private final MassiveDepositGeometry.Body body;
 private final ContinentOccurrenceLedger.Request occurrence;
 private final CoalMiningReservation coal;
 private final ContinentOccurrenceLedger.Candidate finiteCandidate;
 private final Set<GeologyMath.Voxel> offsets;
 private final MassiveDepositGeometry.Bounds bounds;
 public MiningScanScope(String dimension,String family,int regionX,int regionZ,MassiveDepositGeometry.Body body,int minBuildY,int maxBuildYExclusive){
  if(dimension==null||!dimension.matches("[a-z0-9_.-]+:[a-z0-9_./-]+")||dimension.length()>256||family==null||!family.matches("[a-z0-9_.:/-]+")||family.length()>128)throw new IllegalArgumentException("Invalid deposit identity");
  this.dimension=dimension;this.family=family;this.regionX=regionX;this.regionZ=regionZ;this.body=Objects.requireNonNull(body);this.minBuildY=minBuildY;this.maxBuildYExclusive=maxBuildYExclusive;
  occurrence=null;coal=null;finiteCandidate=null;offsets=Set.of();bounds=body.bounds();geometryFingerprint="";new MiningScanCursor(bounds,minBuildY,maxBuildYExclusive,0);
  try{var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);out.writeUTF(dimension);out.writeUTF(family);out.writeInt(regionX);out.writeInt(regionZ);out.writeLong(body.seed());out.flush();key=hash(bytes.toByteArray());}catch(IOException e){throw new AssertionError(e);}
 }
 private MiningScanScope(ContinentOccurrenceLedger.Request request,CoalMiningReservation coal,int minY,int maxY){
  if((request==null)==(coal==null))throw new IllegalArgumentException("Exactly one finite authority required");
  occurrence=request;this.coal=coal;
  if(coal==null)finiteCandidate=request.candidate();else {var s=coal.selected();finiteCandidate=new ContinentOccurrenceLedger.Candidate(s.x(),s.y(),s.z(),s.geometrySeed(),s.cells(),s.biome());}
  var c=finiteCandidate;
  if(minY>=maxY||(long)maxY-minY>4096)throw new IllegalArgumentException("Invalid continent mining height");
  dimension=coal!=null?coal.scope().dimension():request.key().dimension();family=coal!=null?"coal":request.key().family();regionX=c.x()>>4;regionZ=c.z()>>4;body=null;minBuildY=minY;maxBuildYExclusive=maxY;key=coal!=null?coal.key():ContinentOreProvenance.key(request);
  var shape=GeologyMath.shape(c.geometrySeed(),c.cells(),coal!=null);offsets=Set.copyOf(shape);if(offsets.size()!=c.cells())throw new IllegalArgumentException("Unique finite body required");
  int lx=Integer.MAX_VALUE,ly=lx,lz=lx,hx=Integer.MIN_VALUE,hy=hx,hz=hx;
  try{var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);out.writeUTF(coal!=null?"IC_COAL_SCAN_GEOMETRY_V1":"IC_CONTINENT_SCAN_GEOMETRY_V1");
   for(var p:shape){int x=Math.addExact(c.x(),p.x()),y=Math.addExact(c.y(),p.y()),z=Math.addExact(c.z(),p.z());
    if(Math.abs((long)x)>ContinentEnvelope.LIMIT||Math.abs((long)z)>ContinentEnvelope.LIMIT||y<=minY||y>=maxY-1)throw new IllegalArgumentException("Body outside admitted build interval");
    lx=Math.min(lx,x);ly=Math.min(ly,y);lz=Math.min(lz,z);hx=Math.max(hx,x);hy=Math.max(hy,y);hz=Math.max(hz,z);out.writeInt(x);out.writeInt(y);out.writeInt(z);
   }out.flush();geometryFingerprint=hash(bytes.toByteArray());
  }catch(IOException e){throw new AssertionError(e);}
  bounds=new MassiveDepositGeometry.Bounds(lx,ly,lz,hx,hy,hz);new MiningScanCursor(bounds,minY,maxY,0);
 }
 public static MiningScanScope continent(ContinentOccurrenceLedger.Request request,int minY,int maxY){return new MiningScanScope(Objects.requireNonNull(request),null,minY,maxY);}
 public static MiningScanScope coal(CoalMiningReservation reservation,int minY,int maxY){return new MiningScanScope(null,Objects.requireNonNull(reservation),minY,maxY);}
 /** Exact owner-chunk coverage for finite reservations, without loading terrain. */
 public List<Long> observationChunks(){
  if(!isContinent())throw new IllegalStateException("Finite reservation required for exact owner coverage");
  var chunks=new TreeSet<Long>();var c=candidate();
  for(var p:offsets){int x=Math.addExact(c.x(),p.x()),z=Math.addExact(c.z(),p.z());chunks.add(((long)(z>>4)<<32)|((x>>4)&0xffffffffL));}
  return List.copyOf(chunks);
 }
 public boolean isContinent(){return occurrence!=null||coal!=null;}
 public boolean isCoal(){return coal!=null;}
 public CoalMiningReservation coalReservation(){if(coal==null)throw new IllegalStateException("Not a coal reservation");return coal;}
 public long worldSeed(){return coal!=null?coal.scope().worldSeed():occurrence().key().worldSeed();}
 public String presetSha256(){return coal!=null?coal.scope().presetSha256():occurrence().key().presetSha256();}
 public ReTerraForgedGeography.ContinentKey continentKey(){return coal!=null?coal.continent():occurrence().key().continent();}
 public String depositSlot(){return coal!=null?"coal/"+coal.slot():family;}
 public ContinentOccurrenceLedger.Request occurrence(){if(occurrence==null)throw new IllegalStateException("Legacy scope has no continent occurrence");return occurrence;}
 public String geometryFingerprint(){return geometryFingerprint;}
 public MassiveDepositGeometry.Body body(){if(body==null)throw new IllegalStateException("Continent reservation is not a massive field");return body;}
 public MassiveDepositGeometry.Bounds bounds(){return bounds;}
 /** Whole-piece containment, bounded by the finite reserve rather than a filled bounding box. */
 public boolean enclosesEnvelope(MassiveDepositGeometry.Bounds box){
  Objects.requireNonNull(box);if(!bounds.contains(box))return false;
  if(body!=null)return body.enclosesEnvelope(box);
  long x=(long)box.maxX()-box.minX()+1,y=(long)box.maxY()-box.minY()+1,z=(long)box.maxZ()-box.minZ()+1;
  // Each dimension is bounded by scope bounds; divide before multiplication to refuse huge boxes.
  long budget=offsets.size();if(x>budget||y>budget/x||z>budget/(x*y))return false;
  for(long bx=box.minX();bx<=box.maxX();bx++)for(long bz=box.minZ();bz<=box.maxZ();bz++)for(long by=box.minY();by<=box.maxY();by++)if(!contains((int)bx,(int)by,(int)bz))return false;
  return true;
 }
 private ContinentOccurrenceLedger.Candidate candidate(){return finiteCandidate;}
 /** Immutable selected geometry shared by ordinary occurrences and separately journaled coal seams. */
 public ContinentOccurrenceLedger.Candidate reservedCandidate(){if(!isContinent())throw new IllegalStateException("Finite reservation required");return finiteCandidate;}
 public boolean contains(int x,int y,int z){if(!bounds.contains(x,y,z))return false;if(body!=null)return body.contains(x,y,z);var c=candidate();return offsets.contains(new GeologyMath.Voxel(x-c.x(),y-c.y(),z-c.z()));}
 public MiningScanCursor cursor(long index){return new MiningScanCursor(bounds,minBuildY,maxBuildYExclusive,index);}
 public String dimension(){return dimension;}public String family(){return family;}public int regionX(){return regionX;}public int regionZ(){return regionZ;}public int minBuildY(){return minBuildY;}public int maxBuildYExclusive(){return maxBuildYExclusive;}public String key(){return key;}
 @Override public boolean equals(Object o){return o instanceof MiningScanScope s&&dimension.equals(s.dimension)&&family.equals(s.family)&&regionX==s.regionX&&regionZ==s.regionZ&&minBuildY==s.minBuildY&&maxBuildYExclusive==s.maxBuildYExclusive&&Objects.equals(body,s.body)&&Objects.equals(occurrence,s.occurrence)&&Objects.equals(coal,s.coal)&&geometryFingerprint.equals(s.geometryFingerprint);}
 @Override public int hashCode(){return Objects.hash(dimension,family,regionX,regionZ,body,occurrence,coal,minBuildY,maxBuildYExclusive,geometryFingerprint);}
 @Override public String toString(){return "MiningScanScope[family="+family+", key="+key+", continent="+isContinent()+"]";}
 private static String hash(byte[] data){try{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(data));}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
}
