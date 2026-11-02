package dev.godpc.industrialcolonies.geology;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import java.io.*;
import java.nio.file.Path;
import java.util.*;

/** Native binding of the complete coal layout. Explicit create/open only; no runtime registration.
 * Owner reservations are exposed only after all saved slots requalify, with exact distinct cells.
 * Reservations do not confer provenance, perform physical writes or guarantee mineable yield. */
public final class NativeCoalCoordinator {
    private final ServerLevel level;
    private final CoalAllocationJournal allocation;
    private final Map<String,NativeCoalCandidateQualifier> qualifiers=new HashMap<>();
    private final CoalDiscoveryCoordinator discovery;

    private NativeCoalCoordinator(boolean create,Path directory,ServerLevel level,CoalAllocationJournal allocation,
            String preset,int initialY,Set<String> eligibleBiomes,ContinentSpacing outsideCoal,
            ContinentSpacing otherSpacing)throws IOException {
        this(create,directory,level,allocation,preset,initialY,eligibleBiomes,outsideCoal,otherSpacing,null);
    }
    private NativeCoalCoordinator(boolean create,Path directory,ServerLevel level,CoalAllocationJournal allocation,
            String preset,int initialY,Set<String> eligibleBiomes,ContinentSpacing outsideCoal,
            ContinentSpacing otherSpacing,CoalHabitatPreference preference)throws IOException {
        this.level=Objects.requireNonNull(level);this.allocation=Objects.requireNonNull(allocation);requireThread();
        var biomes=Set.copyOf(eligibleBiomes);
        CoalDiscoveryCoordinator.Factory factory=(slot,spacing)->{
            var qualifier=new NativeCoalCandidateQualifier(level,allocation,slot,preset,initialY,biomes,spacing,otherSpacing,preference);
            qualifiers.put(slot,qualifier);
            return new CoalDiscoveryCoordinator.Binding(qualifier.request(),qualifier.window(),
                    (x,z)->qualifier.qualifies(x,z)?qualifier.selection():Optional.empty(),preference);
        };
        discovery=create?CoalDiscoveryCoordinator.create(directory,allocation,outsideCoal,factory)
                :CoalDiscoveryCoordinator.open(directory,allocation,outsideCoal,factory);
    }
    public static NativeCoalCoordinator create(Path directory,ServerLevel level,CoalAllocationJournal allocation,
            String preset,int initialY,Set<String> biomes,ContinentSpacing outsideCoal,ContinentSpacing otherSpacing)throws IOException {
        return new NativeCoalCoordinator(true,directory,level,allocation,preset,initialY,biomes,outsideCoal,otherSpacing);
    }
    public static NativeCoalCoordinator open(Path directory,ServerLevel level,CoalAllocationJournal allocation,
            String preset,int initialY,Set<String> biomes,ContinentSpacing outsideCoal,ContinentSpacing otherSpacing)throws IOException {
        return new NativeCoalCoordinator(false,directory,level,allocation,preset,initialY,biomes,outsideCoal,otherSpacing);
    }
    public CoalDiscoveryCoordinator.Progress advance(int budget)throws IOException { requireThread();return discovery.advance(budget); }
    public static NativeCoalCoordinator create(Path directory,ServerLevel level,CoalAllocationJournal allocation,
            String preset,CoalRuntimePolicy policy,ContinentSpacing outsideCoal,ContinentSpacing otherSpacing)throws IOException {
        return new NativeCoalCoordinator(true,directory,level,allocation,preset,policy.initialY(),policy.biomes(),outsideCoal,otherSpacing,policy.preference());
    }
    public static NativeCoalCoordinator open(Path directory,ServerLevel level,CoalAllocationJournal allocation,
            String preset,CoalRuntimePolicy policy,ContinentSpacing outsideCoal,ContinentSpacing otherSpacing)throws IOException {
        return new NativeCoalCoordinator(false,directory,level,allocation,preset,policy.initialY(),policy.biomes(),outsideCoal,otherSpacing,policy.preference());
    }
    public CoalDiscoveryCoordinator.Progress inspect()throws IOException { requireThread();return discovery.inspect(); }
    void requireLevel(ServerLevel supplied)throws IOException {
        requireThread();if(supplied!=level)throw new IllegalArgumentException("Different coal generation level");allocation.snapshot();
    }
    public ReTerraForgedGeography.ContinentKey continent(){return allocation.continent();}
    record Admission(GeologyPlanner.Plan plan,CoalMiningReservation reservation){}
    Admission admit(String slot)throws IOException {
        requireThread();var selected=discovery.selections().get(slot);
        if(selected==null)throw new IllegalArgumentException("Unknown saved coal slot");
        var q=qualifiers.get(slot);return new Admission(q.verifiedPlan(selected),CoalMiningReservation.bind(q.request(),selected));
    }
    public List<MiningScanScope> mineScopes()throws IOException {
        requireThread();var selected=discovery.selections();var scopes=new ArrayList<MiningScanScope>();
        for(var entry:selected.entrySet())scopes.add(MiningScanScope.coal(CoalMiningReservation.bind(qualifiers.get(entry.getKey()).request(),entry.getValue()),level.getMinBuildHeight(),level.getMaxBuildHeight()));
        return ContinentMineshafts.validated(scopes,level.getSeed(),level.getMinBuildHeight(),level.getMaxBuildHeight());
    }
    public Map<String,String> ownerProvenanceKeys(ChunkPos owner)throws IOException {
        var reservations=ownerReservations().getOrDefault(owner.toLong(),Map.of());var result=new LinkedHashMap<String,String>();
        for(String slot:reservations.keySet())result.put(slot,admit(slot).reservation().key());return Collections.unmodifiableMap(result);
    }
    /** Per owner, then exact saved slot. No mutable plan or geology definition escapes. */
    public Map<Long,Map<String,List<BlockPos>>> ownerReservations()throws IOException {
        requireThread();var selections=discovery.selections();var world=GeologyWorld.of(level);
        var result=new TreeMap<Long,Map<String,List<BlockPos>>>();var occupied=new HashSet<BlockPos>();
        for(var entry:selections.entrySet()) {
            var plan=qualifiers.get(entry.getKey()).verifiedPlan(entry.getValue());var cells=world.shape(plan);
            if(cells.size()!=entry.getValue().cells())throw new IOException("Coal shape differs from exact reserve");
            for(var p:cells) {
                if(!occupied.add(p))throw new IOException("Coal formations overlap");
                result.computeIfAbsent(new ChunkPos(p).toLong(),k->new LinkedHashMap<>())
                        .computeIfAbsent(entry.getKey(),k->new ArrayList<>()).add(p.immutable());
            }
        }
        result.replaceAll((owner,slots)->{
            var frozen=new LinkedHashMap<String,List<BlockPos>>();slots.forEach((slot,cells)->frozen.put(slot,List.copyOf(cells)));
            return Collections.unmodifiableMap(frozen);
        });
        return Collections.unmodifiableMap(result);
    }
    private void requireThread(){if(!level.getServer().isSameThread())throw new IllegalStateException("Native server thread required");}
}
