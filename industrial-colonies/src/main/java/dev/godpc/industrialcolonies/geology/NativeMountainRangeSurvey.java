package dev.godpc.industrialcolonies.geology;

import net.minecraft.server.level.ServerLevel;
import java.io.*;
import java.nio.file.Path;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;

/** Opt-in read-only native adapter. Caller supplies independently verified preset/artifact hashes.
 * No automatic registration, ore placement or per-range supply claim. */
public final class NativeMountainRangeSurvey {
    private final ServerLevel level;
    private final Object randomState;
    private final ReTerraForgedGeography geography;
    private final GeologyConfig.Config config;
    private final PagedMountainRangeJournal journal;
    public NativeMountainRangeSurvey(ServerLevel level,Path path,boolean create,String verifiedPresetSha256,
            String verifiedTerrainArtifactSha256,MountainRangeSurvey.Column seed,int maximumObservations)throws IOException{
        this.level=Objects.requireNonNull(level);requireThread();
        if(verifiedTerrainArtifactSha256==null||!verifiedTerrainArtifactSha256.matches("[a-f0-9]{64}"))throw new IllegalArgumentException("Verified terrain artifact identity required");
        randomState=level.getChunkSource().randomState();geography=ReTerraForgedGeography.fromRandomState(randomState);
        var current=GeologyConfig.get();config=new GeologyConfig.Config(current.settings().deepCopy(),current.biomes().deepCopy(),current.deposits().deepCopy());
        var identity=new MountainRangeJournal.Identity(level.getSeed(),level.dimension().location().toString(),verifiedPresetSha256,
                classifierFingerprint(verifiedTerrainArtifactSha256,config),seed,maximumObservations);
        journal=create?PagedMountainRangeJournal.create(path,identity):PagedMountainRangeJournal.open(path,identity);
    }
    public MountainRangeJournal.Progress advance(int budget)throws IOException{
        checkConfiguration();
        try{return NativeAccurateTerrain.query(level,()->{
            try{return journal.advance(budget,(x,z)->{checkConfiguration();return geography.sample(x,z).mountain();});}
            catch(IOException e){throw new UncheckedIOException(e);}
        });}catch(UncheckedIOException e){throw e.getCause();}
    }
    public MountainRangeJournal.Progress progress()throws IOException{checkConfiguration();return journal.progress();}
    /** Routing observations only. This never grants current terrain or placement authority;
     * callers must finish the journal's native audit before using a saved source. */
    public MountainRangeSurvey.Snapshot savedObservations()throws IOException{checkConfiguration();return journal.savedSnapshot();}
    public record Observations(List<MountainRangeSurvey.Observation> rows,MountainRangeSurvey.Status status){
        public Observations{rows=List.copyOf(rows);}
    }
    public Observations observationsSince(int cursor)throws IOException{
        checkConfiguration();return new Observations(journal.observationsSince(cursor),journal.savedStatus());
    }
    /** Routing hint only; never placement or completed-range authority. */
    public boolean observedMountain(MountainRangeSurvey.Column column)throws IOException{checkConfiguration();return journal.observedMountain(column);}
    public MountainRangeSurvey.Range completedRange()throws IOException{checkConfiguration();return journal.completedRange();}
    public String completedIdentity()throws IOException{checkConfiguration();return journal.completedIdentity();}
    /** Save explicit finite requests only after actual terrain has been completely audited. */
    public CinnabarRangeAllocations.Allocation reserveCinnabar(Path directory,boolean create,String policySha256,
            CinnabarRangeAllocations.Plan plan)throws IOException{
        checkConfiguration();journal.completedIdentity();
        var allocations=create?CinnabarRangeAllocations.create(directory,journal.identity().environmentFingerprint(),policySha256)
                :CinnabarRangeAllocations.open(directory,journal.identity().environmentFingerprint(),policySha256);
        return allocations.reserve(journal,plan);
    }
    public CinnabarRangeAllocations.Allocation savedCinnabar(Path directory,String policySha256)throws IOException{
        checkConfiguration();return CinnabarRangeAllocations.open(directory,journal.identity().environmentFingerprint(),policySha256).existing(journal);
    }
    public CinnabarRangeAllocations.Allocation reserveCinnabar(Path directory,boolean create,CinnabarConcentrations.Policy policy)throws IOException{
        checkConfiguration();String component=journal.completedIdentity();
        return reserveCinnabar(directory,create,policy.fingerprint(),CinnabarConcentrations.proposedAllocation(component,policy.concentrations()));
    }
    public Concentrations concentrations(Path directory,CinnabarConcentrations.Policy policy)throws IOException{
        checkConfiguration();var saved=savedCinnabar(directory,policy.fingerprint());
        return new Concentrations(new CinnabarConcentrations(journal.completedRange(),saved,policy));
    }
    public SavedConcentrations savedConcentrations(Path directory,CinnabarConcentrations.Policy policy)throws IOException{
        var planner=concentrations(directory,policy).planner;
        return new SavedConcentrations(directory,planner,CinnabarSelectionJournal.open(selectionPath(directory,planner),planner));
    }
    private Path selectionPath(Path directory,CinnabarConcentrations planner){return directory.resolve(planner.allocation().componentIdentity()+".selections");}
    /** Still read-only: caller must persist/revalidate selected plans before any generation writes. */
    public final class Concentrations {
        private final CinnabarConcentrations planner;
        private Concentrations(CinnabarConcentrations planner){this.planner=planner;}
        public CinnabarConcentrations.Progress advance(int budget)throws IOException{
            checkConfiguration();var world=GeologyWorld.of(level);
            return planner.advance(budget,(x,z)->{checkConfiguration();return world.height(x,z)-1;});
        }
        public CinnabarConcentrations.Progress progress()throws IOException{checkConfiguration();return planner.progress();}
        public List<CinnabarConcentrations.Selection> completed()throws IOException{checkConfiguration();return planner.completed();}
        public SavedConcentrations save(Path directory)throws IOException{
            checkConfiguration();if(!savedCinnabar(directory,planner.policy().fingerprint()).equals(planner.allocation()))throw new IOException("Concentration allocation changed");
            return new SavedConcentrations(directory,planner,CinnabarSelectionJournal.create(selectionPath(directory,planner),planner));
        }
    }
    public final class SavedConcentrations {
        private final Path directory;
        private final CinnabarConcentrations planner;
        private final CinnabarSelectionJournal selections;
        private SavedConcentrations(Path directory,CinnabarConcentrations planner,CinnabarSelectionJournal selections){this.directory=directory;this.planner=planner;this.selections=selections;}
        private void check()throws IOException{
            checkConfiguration();if(!savedCinnabar(directory,planner.policy().fingerprint()).equals(planner.allocation()))throw new IOException("Saved concentration allocation changed");
        }
        public void requireLevel(ServerLevel requested)throws IOException{check();if(requested!=level)throw new IOException("Foreign native level for saved concentrations");}
        public CinnabarSelectionJournal.Progress advance(int budget)throws IOException{
            check();var world=GeologyWorld.of(level);return selections.advance(budget,(x,z)->{checkConfiguration();return world.height(x,z)-1;});
        }
        public CinnabarSelectionJournal.Progress progress()throws IOException{check();return selections.progress();}
        public List<CinnabarConcentrations.Selection> completed()throws IOException{check();return selections.completed();}
    }
    private void requireThread(){if(!level.getServer().isSameThread())throw new IllegalStateException("Native mountain survey requires server thread");}
    private void checkConfiguration()throws IOException{
        requireThread();if(level.getChunkSource().randomState()!=randomState||!config.equals(GeologyConfig.get()))throw new IOException("Native mountain classifier context changed");
    }
    private static String classifierFingerprint(String artifact,GeologyConfig.Config config){
        try{
            var digest=MessageDigest.getInstance("SHA-256");
            for(String value:List.of("IC_NATIVE_MOUNTAIN_CARDINAL_V1",artifact,config.settings().toString(),config.biomes().toString(),config.deposits().toString())){
                byte[] bytes=value.getBytes(StandardCharsets.UTF_8);digest.update(java.nio.ByteBuffer.allocate(4).putInt(bytes.length).array());digest.update(bytes);
            }
            return HexFormat.of().formatHex(digest.digest());
        }catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
    }
}
