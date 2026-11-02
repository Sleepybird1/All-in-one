package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.security.*;
import java.util.*;

/** Pure durable survey cursor and prospecting index; never grants ore placement authority. */
public final class SpawnSurveyState {
 public static final int MAX_POINTS=65536,MAX_STEPS=200000,MAX_SITES=8192;
 public record Origin(int x,int y,int z) {}
 public record Point(int x,int z) {}
 public record Site(String family,int x,int y,int z,String kind) {
  public Site {if(family==null||!family.matches("[a-z0-9_]{1,80}")||kind==null||!Set.of("CANONICAL_PLAN","REGIONAL_PREDICTION","LOCAL_PREDICTION").contains(kind)||Math.abs((long)x)>16777216||Math.abs((long)z)>16777216)throw new IllegalArgumentException("Survey site");}
 }
 private final String identity;private final Set<String> targets;private final int stride;
 private Origin origin;private long epoch=1;private int point,phase,steps;private String pause="";
 private final Set<String> seen=new TreeSet<>(),found=new TreeSet<>();
 private final LinkedHashSet<Site> sites=new LinkedHashSet<>();
 public SpawnSurveyState(String identity,Set<String> targets,int stride,Origin origin){
  if(identity==null||!identity.matches("[a-f0-9]{64}")||targets.isEmpty()||targets.size()>128||targets.stream().anyMatch(s->!s.matches("[a-z0-9_]{1,80}"))||stride<64||stride>4096)throw new IllegalArgumentException("Survey identity/targets/stride");
  this.identity=identity;this.targets=Collections.unmodifiableSet(new TreeSet<>(targets));this.stride=stride;this.origin=Objects.requireNonNull(origin);
 }
 public void require(String expected,Set<String> families,int step){if(!identity.equals(expected)||!targets.equals(families)||stride!=step)throw new IllegalStateException("Saved survey policy changed; progress retained and held");}
 public boolean moveSpawn(Origin next){if(origin.equals(next))return false;origin=Objects.requireNonNull(next);epoch=Math.addExact(epoch,1);point=phase=steps=0;seen.clear();found.clear();pause="";return true;}
 public Origin origin(){return origin;}public long epoch(){return epoch;}public int pointIndex(){return point;}public int phase(){return phase;}public int steps(){return steps;}
 public Set<String> missing(){var result=new TreeSet<>(targets);result.removeAll(found);return Set.copyOf(result);}
 public boolean complete(){return found.containsAll(targets);}public boolean paused(){return !pause.isEmpty();}public String reason(){return pause;}
 public void pause(String reason){pause=Objects.requireNonNull(reason).substring(0,Math.min(512,reason.length()));if(pause.isBlank())pause="Survey paused";}
 public void resume(){pause="";steps=0;}
 public void beginStep(){if(paused()||complete())throw new IllegalStateException("Survey terminal/paused");if(point>=MAX_POINTS||steps>=MAX_STEPS){pause("Survey work limit reached; missing "+new TreeSet<>(missing()));return;}steps++;}
 public Point point(){var offset=offset(point);long x=(long)origin.x()+offset.x()*(long)stride,z=(long)origin.z()+offset.z()*(long)stride;if(Math.abs(x)>16773120||Math.abs(z)>16773120)throw new IllegalStateException("Survey reached supported coordinate boundary");return new Point((int)x,(int)z);}
 public static Point offset(int index){if(index<0||index>=MAX_POINTS)throw new IllegalArgumentException("Survey point index");if(index==0)return new Point(0,0);int ring=(int)Math.ceil((Math.sqrt(index+1)-1)/2);int start=(2*ring-1)*(2*ring-1),side=2*ring,o=index-start;return switch(o/side){case 0->new Point(-ring+o,-ring);case 1->new Point(ring,-ring+o-side);case 2->new Point(ring-(o-2*side),ring);default->new Point(-ring,ring-(o-3*side));};}
 public boolean seen(String key){return seen.contains(key);}public void markSeen(String key){if(key==null||key.length()>100||seen.size()>=4096&&!seen.contains(key))throw new IllegalStateException("Survey continent capacity");seen.add(key);}
 public void nextPhase(){if(phase>=2){phase=0;point++;}else phase++;}
 public void record(Site site){if(!targets.contains(site.family()))throw new IllegalArgumentException("Foreign survey family");if(sites.size()>=MAX_SITES&&!sites.contains(site))throw new IllegalStateException("Survey location capacity reached");sites.add(site);found.add(site.family());}
 public List<Site> sites(){return List.copyOf(sites);}
 public Optional<Site> nearest(String family,double x,double z,int radius){if(!targets.contains(family)||radius<1||radius>131072||!Double.isFinite(x)||!Double.isFinite(z))return Optional.empty();return sites.stream().filter(s->s.family().equals(family)&&Math.hypot(s.x()-x,s.z()-z)<=radius).min(Comparator.comparingDouble((Site s)->Math.hypot(s.x()-x,s.z()-z)).thenComparingInt(Site::x).thenComparingInt(Site::z).thenComparingInt(Site::y));}
 public byte[] encode()throws IOException{
  var bytes=new ByteArrayOutputStream();try(var out=new DataOutputStream(bytes)){out.writeInt(0x49435331);out.writeUTF(identity);out.writeInt(stride);out.writeInt(origin.x());out.writeInt(origin.y());out.writeInt(origin.z());out.writeLong(epoch);out.writeInt(point);out.writeInt(phase);out.writeInt(steps);out.writeUTF(pause);strings(out,targets);strings(out,seen);strings(out,found);out.writeInt(sites.size());for(var s:sites){out.writeUTF(s.family());out.writeInt(s.x());out.writeInt(s.y());out.writeInt(s.z());out.writeUTF(s.kind());}}
  byte[] body=bytes.toByteArray();if(body.length>1048544)throw new IOException("Survey size limit");bytes.write(digest(body));return bytes.toByteArray();
 }
 public static SpawnSurveyState decode(byte[] bytes)throws IOException{
  if(bytes.length<36||bytes.length>1048576)throw new IOException("Survey size");byte[] body=Arrays.copyOf(bytes,bytes.length-32);if(!MessageDigest.isEqual(digest(body),Arrays.copyOfRange(bytes,body.length,bytes.length)))throw new IOException("Survey checksum");
  try(var in=new DataInputStream(new ByteArrayInputStream(body))){if(in.readInt()!=0x49435331)throw new IOException("Survey format");String id=in.readUTF();int stride=in.readInt();var origin=new Origin(in.readInt(),in.readInt(),in.readInt());long epoch=in.readLong();int point=in.readInt(),phase=in.readInt(),steps=in.readInt();String pause=in.readUTF();var targets=strings(in,128);var s=new SpawnSurveyState(id,targets,stride,origin);s.epoch=epoch;s.point=point;s.phase=phase;s.steps=steps;s.pause=pause;s.seen.addAll(strings(in,4096));s.found.addAll(strings(in,128));int count=in.readInt();if(count<0||count>MAX_SITES)throw new IOException("Survey site count");for(int i=0;i<count;i++){var site=new Site(in.readUTF(),in.readInt(),in.readInt(),in.readInt(),in.readUTF());if(!targets.contains(site.family())||!s.sites.add(site))throw new IOException("Foreign/duplicate site");}if(in.available()!=0||epoch<1||point<0||point>MAX_POINTS||phase<0||phase>2||steps<0||steps>MAX_STEPS||pause.length()>512||!targets.containsAll(s.found)||!s.sites.stream().map(Site::family).collect(java.util.stream.Collectors.toSet()).containsAll(s.found))throw new IOException("Invalid survey state");return s;}
  catch(IllegalArgumentException e){throw new IOException("Invalid survey data",e);}
 }
 private static void strings(DataOutputStream out,Collection<String> values)throws IOException{out.writeInt(values.size());for(String value:values)out.writeUTF(value);}
 private static Set<String> strings(DataInputStream in,int limit)throws IOException{int count=in.readInt();if(count<0||count>limit)throw new IOException("Survey collection size");var result=new TreeSet<String>();for(int i=0;i<count;i++){String value=in.readUTF();if(value.length()>100||!result.add(value))throw new IOException("Survey duplicate/unbounded value");}return result;}
 private static byte[] digest(byte[] bytes){try{return MessageDigest.getInstance("SHA-256").digest(bytes);}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
}
