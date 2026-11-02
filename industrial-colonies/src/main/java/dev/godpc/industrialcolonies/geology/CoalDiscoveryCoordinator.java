package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** Fixed-order discovery of an entire saved coal layout. No partial layout is placement-ready.
 * Each advance uses at most budget new column queries plus one revalidation per saved slot.
 * A changed/unfittable slot stops the layout; later slots are never substituted or redrawn. */
public final class CoalDiscoveryCoordinator {
    public enum Status { SEARCHING, READY, UNFITTED, HELD }
    public record Progress(Status status,int selected,int slots,
            Map<String,CoalDiscoveryJournal.Progress> deposits) {
        public Progress { deposits=Collections.unmodifiableMap(new LinkedHashMap<>(deposits)); }
    }
    public record Binding(CoalPlacementRequest request,GeographicColumnSurvey.Window window,
            CoalDiscoveryJournal.Qualifier qualifier,CoalHabitatPreference preference) {
        public Binding { Objects.requireNonNull(request);Objects.requireNonNull(window);Objects.requireNonNull(qualifier); }
        public Binding(CoalPlacementRequest request,GeographicColumnSurvey.Window window,CoalDiscoveryJournal.Qualifier qualifier){this(request,window,qualifier,null);}
    }
    @FunctionalInterface public interface Factory {
        Binding bind(String slot,ContinentSpacing coalSpacing)throws IOException;
    }
    private final Path directory;
    private final CoalAllocationJournal allocation;
    private final CoalLayoutPolicy.Plan plan;
    private final Factory factory;
    private final ContinentSpacing outsideCoal;
    private final String scope;
    private ContinentCoordinatorManifest manifest;

    private CoalDiscoveryCoordinator(Path directory,CoalAllocationJournal allocation,
            ContinentSpacing outsideCoal,Factory factory)throws IOException {
        this.directory=Objects.requireNonNull(directory).toAbsolutePath().normalize();
        this.allocation=Objects.requireNonNull(allocation);this.outsideCoal=Objects.requireNonNull(outsideCoal);
        this.factory=Objects.requireNonNull(factory);plan=allocation.snapshot();
        for(var c:outsideCoal.preceding())if(plan.deposits().stream().anyMatch(d->centerName(d.slot()).equals(c.family())))
            throw new IllegalArgumentException("External coal center aliases a local slot");
        // The first binding commits all factory terrain/world policy before any cursor is started.
        var first=binding(plan.deposits().getFirst(),outsideCoal);
        scope=scope(first);
    }
    public static CoalDiscoveryCoordinator create(Path directory,CoalAllocationJournal allocation,
            ContinentSpacing outsideCoal,Factory factory)throws IOException {
        var c=new CoalDiscoveryCoordinator(directory,allocation,outsideCoal,factory);
        Files.createDirectory(c.directory);
        c.manifest=ContinentCoordinatorManifest.create(c.directory.resolve("coordinator.bin"),c.scope,c.plan.deposits().size());
        return c;
    }
    public static CoalDiscoveryCoordinator open(Path directory,CoalAllocationJournal allocation,
            ContinentSpacing outsideCoal,Factory factory)throws IOException {
        var c=new CoalDiscoveryCoordinator(directory,allocation,outsideCoal,factory);
        c.manifest=ContinentCoordinatorManifest.open(c.directory.resolve("coordinator.bin"),c.scope,c.plan.deposits().size());
        c.inspect(0);return c;
    }
    /** Includes native requalification of every already selected slot, even after READY. */
    public Progress advance(int budget)throws IOException {
        if(budget<1||budget>4096)throw new IllegalArgumentException("Coal coordinator budget1..4096");
        return inspect(budget);
    }
    public Progress inspect()throws IOException { return inspect(0); }
    public Map<String,NativeCoalCandidateQualifier.Selection> selections()throws IOException {
        var state=inspect();if(state.status()!=Status.READY)throw new IllegalStateException("Complete fitting coal layout required");
        var result=new LinkedHashMap<String,NativeCoalCandidateQualifier.Selection>();
        state.deposits().forEach((slot,p)->result.put(slot,p.selected()));
        return Collections.unmodifiableMap(result);
    }
    private Progress inspect(int budget)throws IOException {
        if(!plan.equals(allocation.snapshot()))throw new IOException("Coal allocation changed");
        if(!scope.equals(scope(binding(plan.deposits().getFirst(),outsideCoal))))throw new IOException("Coal terrain policy changed");
        int started=manifest.started(),selected=0;
        var centers=new ArrayList<>(outsideCoal.preceding());
        var states=new LinkedHashMap<String,CoalDiscoveryJournal.Progress>();
        for(int index=0;index<plan.deposits().size();index++) {
            var deposit=plan.deposits().get(index);Path path=directory.resolve("search-"+deposit.slot()+".bin");
            var spacing=new ContinentSpacing(outsideCoal.minimumDistance(),centers);
            var binding=binding(deposit,spacing);CoalDiscoveryJournal journal;
            if(index<started)journal=CoalDiscoveryJournal.open(path,binding.request(),binding.window(),binding.preference());
            else {
                if(Files.exists(path,LinkOption.NOFOLLOW_LINKS)||Files.exists(path.resolveSibling(path.getFileName()+".started"),LinkOption.NOFOLLOW_LINKS))
                    throw new IOException("Coal slot exists outside commissioning prefix");
                if(budget==0)return new Progress(Status.SEARCHING,selected,plan.deposits().size(),states);
                manifest.start(index);started=index+1;
                journal=CoalDiscoveryJournal.create(path,binding.request(),binding.window(),binding.preference());
            }
            var state=journal.snapshot();
            // Enforce spacing in the coordinator as well as in the native terrain qualifier.
            CoalDiscoveryJournal.Qualifier checked=(x,z)->spacing.allows(x,z)?binding.qualifier().qualify(x,z):Optional.empty();
            if(state.status()==CoalDiscoveryJournal.Status.SELECTED)state=journal.advance(1,checked);
            else if(state.status()==CoalDiscoveryJournal.Status.SEARCHING&&budget>0) {
                long before=state.visited();state=journal.advance(budget,checked);
                budget-=Math.toIntExact(state.visited()-before);
            }
            states.put(deposit.slot(),state);
            switch(state.status()) {
                case HELD_CHANGED_SELECTION: return new Progress(Status.HELD,selected,plan.deposits().size(),states);
                case UNFITTED: return new Progress(Status.UNFITTED,selected,plan.deposits().size(),states);
                case SEARCHING:
                    if(started>index+1)throw new IOException("Later coal slot started before predecessor selected");
                    return new Progress(Status.SEARCHING,selected,plan.deposits().size(),states);
                case SELECTED:
                    selected++;var p=state.selected();centers.add(new ContinentSpacing.Center(centerName(deposit.slot()),p.x(),p.z()));
            }
        }
        return new Progress(Status.READY,selected,plan.deposits().size(),states);
    }
    private Binding binding(CoalLayoutPolicy.Deposit deposit,ContinentSpacing spacing)throws IOException {
        var b=Objects.requireNonNull(factory.bind(deposit.slot(),spacing));b.request().verify();
        if(!b.request().scope().equals(allocation.scope())||!b.request().continent().equals(allocation.continent())
                ||!b.request().deposit().equals(deposit))throw new IOException("Coal factory changed saved slot authority");
        return b;
    }
    private static String centerName(String slot){return "coal_"+slot;}
    private String scope(Binding first){return hash("industrial-colonies/coal-coordinator/v1\n"+plan.identity()+"\n"+outsideCoal+"\n"
            +first.request().fingerprint()+"\n"+first.window()+(first.preference()==null?"":"\nHABITAT_V1\n"+first.preference().fingerprint()));}
    private static String hash(String value) {
        try{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8)));}
        catch(NoSuchAlgorithmException e){throw new AssertionError(e);}
    }
}
