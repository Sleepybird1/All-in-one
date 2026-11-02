package dev.godpc.industrialcolonies.geology;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;

/** Server-thread source discovery for automatic exposed cinnabar generation.
 * No chunk requests, ore writes, fallback deposits, new presence rolls or implicit recovery.
 * The caller explicitly commissions policy/paths and must wire both native generation phases. */
public final class MountainCinnabarSources {
 public record Progress(boolean ready,int ownerColumns,List<NativeMountainRangeSurvey.SavedConcentrations> sources){
  public Progress{sources=List.copyOf(sources);}
 }
 private final ServerLevel level;
 private final Path surveys,allocations;
 private final String preset,terrainArtifact;
 private final int observationLimit;
 private final CinnabarConcentrations.Policy policy;
 private final GeologyWorld world;
 private final ReTerraForgedGeography geography;
 private final Map<Long,Set<Session>> observed=new HashMap<>();
 private final List<Session> sessions=new ArrayList<>();
 private Session active;
 private long clock;
 private static final int IDLE_RESIDENT_RANGES=2;

 public MountainCinnabarSources(ServerLevel level,Path directory,String preset,String terrainArtifact,
         int observationLimit,CinnabarConcentrations.Policy policy)throws IOException{
  this.level=Objects.requireNonNull(level);thread();this.preset=Objects.requireNonNull(preset);
  this.terrainArtifact=Objects.requireNonNull(terrainArtifact);this.policy=Objects.requireNonNull(policy);
  new MountainRangeSurvey(new MountainRangeSurvey.Column(0,0),observationLimit);this.observationLimit=observationLimit;
  surveys=directory.resolve("surveys");allocations=directory.resolve("allocations");
  Files.createDirectories(surveys);world=GeologyWorld.of(level);geography=ReTerraForgedGeography.fromRandomState(level.getChunkSource().randomState());
  try(var files=Files.list(surveys)){
   for(var path:files.sorted().toList()){
    String name=path.getFileName().toString();
    if(name.endsWith(".lock"))continue;
    if(name.endsWith(".bin.pages")){
     if(!Files.isDirectory(path,LinkOption.NOFOLLOW_LINKS)||!Files.isRegularFile(path.resolveSibling(name.substring(0,name.length()-6)),LinkOption.NOFOLLOW_LINKS))throw new IOException("Orphaned mountain continuation pages");
     continue;
    }
    if(name.endsWith(".started")){
     if(!Files.isRegularFile(path.resolveSibling(name.substring(0,name.length()-8)),LinkOption.NOFOLLOW_LINKS))throw new IOException("Missing commissioned mountain survey");
     continue;
    }
    if(!name.matches("range_-?[0-9]+_-?[0-9]+\\.bin")||!Files.isRegularFile(path,LinkOption.NOFOLLOW_LINKS))throw new IOException("Unknown or unresolved mountain survey entry: "+name);
    String[] fields=name.substring(6,name.length()-4).split("_");
    var seed=new MountainRangeSurvey.Column(Integer.parseInt(fields[0]),Integer.parseInt(fields[1]));
    var session=new Session(seed,path,false);sessions.add(session);session.index();trim(null);
   }
  }
 }
 public Ticket owner(ChunkPos owner){thread();return new Ticket(owner);}
 /** In-flight sources remain pinned until FEATURES finishes. Evicted idle sources
  * reopen their original journals and repeat the complete native terrain audit. */
 public void release(Ticket ticket){
  thread();if(ticket.closed)return;ticket.closed=true;
  for(var session:ticket.required)session.pins--;
  ticket.required.clear();trim(null);
 }
 private void trim(Session except){
  var idle=sessions.stream().filter(s->s.survey!=null&&s.pins==0&&s.topologyComplete&&s!=active&&s!=except)
    .sorted(Comparator.comparingLong(s->s.used)).toList();
  int allowed=Math.max(0,IDLE_RESIDENT_RANGES-(except!=null&&except.pins==0&&except.topologyComplete?1:0));
  for(int i=0;i<idle.size()-allowed;i++)idle.get(i).evict();
 }
 private void thread(){if(!level.getServer().isSameThread())throw new IllegalStateException("Cinnabar source discovery requires native server thread");}
 private Path surveyPath(MountainRangeSurvey.Column seed){return surveys.resolve("range_"+seed.x()+"_"+seed.z()+".bin");}
 private long tile(MountainRangeSurvey.Column p){return ((long)(p.x()>>6)<<32)^((p.z()>>6)&0xffffffffL);}
 private Session observed(MountainRangeSurvey.Column p)throws IOException{
  Session found=null;var bucket=observed.get(tile(p));
  if(bucket!=null)for(var session:bucket)if(session.survey!=null&&session.survey.observedMountain(p)){
   if(found!=null&&found!=session)throw new IOException("Overlapping commissioned mountain sources require explicit reconciliation");found=session;
  }
  return found;
 }

 public final class Ticket {
  private final ChunkPos owner;
  private final LinkedHashSet<Session> required=new LinkedHashSet<>();
  private int column;
  private boolean closed;
  private MountainRangeSurvey.Column waiting;
  private Ticket(ChunkPos owner){this.owner=Objects.requireNonNull(owner);}
  /** Budget covers native owner-column tests and topology reads. Geometry fitting is
   * one bounded existing planner evaluation, not a claimed CPU-time bound. */
  public Progress advance(int budget)throws IOException{
   thread();if(closed)throw new IOException("Cinnabar owner source ticket already released");
   if(budget<1||budget>4096)throw new IllegalArgumentException("Cinnabar source budget1..4096");
   if(active!=null&&active.done)active=null;
   if(active!=null){active.advance(budget);if(active.done)active=null;return progress();}
   while(budget>0&&column<256){
    if(waiting==null){
     int x=owner.getMinBlockX()+column%16,z=owner.getMinBlockZ()+column/16;column++;budget--;
     // Only actual native mountains reaching the selected elevation can request
     // a source. No biome whitelist or manufactured cave/surface is admitted.
     if(!geography.sample(x,z).mountain()||world.height(x,z)-1<policy.minimumY())continue;
     waiting=new MountainRangeSurvey.Column(x,z);
    }
    if(budget==0)return progress();
    Session known=observed(waiting);
    if(known==null){
     // Complete previously commissioned partial topology before creating another
     // entry seed, so restart can never manufacture an independent supply request.
     known=sessions.stream().filter(s->!s.topologyComplete&&!s.done).findFirst().orElse(null);
     if(known!=null){active=known;active.advance(Math.max(1,budget));return progress();}
     for(var saved:sessions)if(saved.topologyComplete&&saved.encloses(waiting)){
      saved.load();saved.index();trim(saved);known=observed(waiting);if(known!=null)break;
     }
    }
    if(known==null){
     var path=surveyPath(waiting);if(Files.exists(path,LinkOption.NOFOLLOW_LINKS)||Files.exists(path.resolveSibling(path.getFileName()+".started"),LinkOption.NOFOLLOW_LINKS))throw new IOException("Existing cinnabar survey cannot be recreated");
     known=new Session(waiting,path,true);sessions.add(known);
     required.add(known);known.pins++;waiting=null;
     active=known;active.advance(Math.max(1,budget));return progress();
    }
    if(required.add(known))known.pins++;known.used=++clock;waiting=null;
    if(!known.done){active=known;active.advance(Math.max(1,budget));return progress();}
   }
   return progress();
  }
  public Progress progress()throws IOException{
   thread();if(closed)throw new IOException("Cinnabar owner source ticket already released");
   boolean ready=column==256&&waiting==null&&required.stream().allMatch(s->s.done);
   if(!ready)return new Progress(false,column,List.of());
   var sources=new ArrayList<NativeMountainRangeSurvey.SavedConcentrations>();var identities=new HashSet<String>();
   for(var session:required)if(session.saved!=null&&identities.add(session.component))sources.add(session.saved);
   if(sources.size()>64)throw new IOException("Surface source group exceeds native transaction bound");
   return new Progress(true,column,sources);
  }
 }

 private final class Session {
  final MountainRangeSurvey.Column seed;
  final Path path;
  NativeMountainRangeSurvey survey;
  boolean topologyComplete,done;
  int indexed,heightIndex,pins;
  int minX=Integer.MAX_VALUE,minZ=Integer.MAX_VALUE,maxX=Integer.MIN_VALUE,maxZ=Integer.MIN_VALUE;
  long used;
  boolean eligibleHeight;
  String component;
  MountainRangeSurvey.Range range;
  NativeMountainRangeSurvey.Concentrations fitting;
  NativeMountainRangeSurvey.SavedConcentrations saved;
  Session(MountainRangeSurvey.Column seed,Path path,boolean create)throws IOException{
   this.seed=seed;this.path=path;
   survey=new NativeMountainRangeSurvey(level,path,create,preset,terrainArtifact,seed,observationLimit);
   used=++clock;
  }
  boolean encloses(MountainRangeSurvey.Column p){return p.x()>=minX&&p.x()<=maxX&&p.z()>=minZ&&p.z()<=maxZ;}
  void load()throws IOException{
   if(survey==null)survey=new NativeMountainRangeSurvey(level,path,false,preset,terrainArtifact,seed,observationLimit);
   used=++clock;
  }
  void evict(){
   if(pins!=0||!topologyComplete||this==active)throw new IllegalStateException("Cannot evict active/pinned mountain source");
   observed.values().forEach(bucket->bucket.remove(this));observed.entrySet().removeIf(e->e.getValue().isEmpty());
   survey=null;range=null;fitting=null;saved=null;component=null;indexed=heightIndex=0;eligibleHeight=done=false;
  }
  void index()throws IOException{
   load();
   var snapshot=survey.observationsSince(indexed);
   for(var row:snapshot.rows()){
    if(row.mountain()){
     minX=Math.min(minX,row.column().x());maxX=Math.max(maxX,row.column().x());minZ=Math.min(minZ,row.column().z());maxZ=Math.max(maxZ,row.column().z());
     // These rows already came from this survey's guarded observation snapshot.
     // Checking our own membership again repeats deep configuration comparison
     // for every indexed column. Only another source can constitute an overlap.
     var bucket=observed.get(tile(row.column()));
     if(bucket!=null)for(var other:bucket){
      if(other!=this&&other.survey!=null&&other.survey.observedMountain(row.column()))
       throw new IOException("Overlapping commissioned mountain sources require explicit reconciliation");
     }
     observed.computeIfAbsent(tile(row.column()),ignored->new LinkedHashSet<>()).add(this);
    }
   }
   indexed+=snapshot.rows().size();
   topologyComplete=snapshot.status()==MountainRangeSurvey.Status.COMPLETE;
  }
  void advance(int budget)throws IOException{
   if(done)return;
   load();
   var topology=survey.advance(budget);index();
   if(topology.phase()!=MountainRangeJournal.Phase.COMPLETE){
    if(topology.phase()!=MountainRangeJournal.Phase.DISCOVERING&&topology.phase()!=MountainRangeJournal.Phase.VERIFYING)throw new IOException("Cinnabar mountain topology held: "+topology);
    return;
   }
   if(range==null){range=survey.completedRange();component=survey.completedIdentity();}
   // A range entirely below the minimum or above the zero-frequency ceiling
   // cannot be a qualifying source. Audit the complete range before saying so.
   if(!eligibleHeight){
    for(int i=0;i<budget&&heightIndex<range.members().size();i++){
     var p=range.members().get(heightIndex++);int top=world.height(p.x(),p.z())-1;
     if(top>=policy.minimumY()&&top<400){eligibleHeight=true;break;}
    }
    if(!eligibleHeight){if(heightIndex==range.members().size())done=true;return;}
   }
   if(fitting==null&&saved==null){
    boolean create=!Files.exists(allocations,LinkOption.NOFOLLOW_LINKS);
    survey.reserveCinnabar(allocations,create,policy);
    if(Files.exists(allocations.resolve(component+".selections"),LinkOption.NOFOLLOW_LINKS))saved=survey.savedConcentrations(allocations,policy);
    else fitting=survey.concentrations(allocations,policy);
   }
   if(saved==null){
    var result=fitting.advance(1);
    if(result.status()==CinnabarConcentrations.Status.READY)saved=fitting.save(allocations);
    else if(result.status()!=CinnabarConcentrations.Status.SEARCHING)throw new IOException("Finite exposed cinnabar request held: "+result);
    return;
   }
   var result=saved.advance(1);
   if(result.phase()==CinnabarSelectionJournal.Phase.READY){saved.completed();done=true;}
   else if(result.phase()!=CinnabarSelectionJournal.Phase.VERIFYING)throw new IOException("Saved cinnabar selection held: "+result);
  }
 }
}
