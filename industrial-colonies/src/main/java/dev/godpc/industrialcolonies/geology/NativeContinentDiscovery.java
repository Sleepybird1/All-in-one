package dev.godpc.industrialcolonies.geology;

import java.io.IOException;
import java.nio.file.Path;
import java.util.*;

/** Staged server-thread coordinator; no event registration or terrain writes.
 * Persist selection before occurrence. A restart between those commits can only
 * revalidate the same selection and reuse the same presence domain, never rediscover. */
public final class NativeContinentDiscovery {
    public enum Status { SEARCHING, EXHAUSTED, HELD, ABSENT, PRESENT }
    /** Read-only last native observation; never grants placement or changes committed input. */
    public Optional<NativeContinentCandidateQualifier.Selection> observedSelection(){return qualifier.selection();}
    /** Exact durable cursor for shared-budget accounting, without another native terrain read. */
    public long visited()throws IOException{return search.snapshot().visited();}
    public record Progress(Status status,ContinentCandidateSearch.Checkpoint search,
            Optional<ContinentOccurrenceLedger.Entry> occurrence,Optional<GeologyPlanner.Plan> plan) {}
    private final NativeContinentCandidateQualifier qualifier;
    private final ContinentSearchJournal search;
    private final ContinentOccurrenceLedger occurrences;
    private final double chance;
    private NativeContinentDiscovery(NativeContinentCandidateQualifier qualifier,ContinentSearchJournal search,
            ContinentOccurrenceLedger occurrences,double chance){
        this.qualifier=qualifier;this.search=search;this.occurrences=Objects.requireNonNull(occurrences);this.chance=chance;
    }
    public static NativeContinentDiscovery create(Path searchPath,NativeContinentCandidateQualifier qualifier,
            ContinentOccurrenceLedger occurrences,double chance)throws IOException{
        qualifier.checkConfiguration();
        if(occurrences.snapshot().containsKey(qualifier.key().family()))throw new IOException("Existing occurrence forbids new discovery");
        return new NativeContinentDiscovery(qualifier,ContinentSearchJournal.create(searchPath,qualifier.key(),qualifier.window(),chance,qualifier.traversal()),occurrences,chance);
    }
    public static NativeContinentDiscovery open(Path searchPath,NativeContinentCandidateQualifier qualifier,
            ContinentOccurrenceLedger occurrences,double chance)throws IOException{
        qualifier.checkConfiguration();
        return new NativeContinentDiscovery(qualifier,ContinentSearchJournal.open(searchPath,qualifier.key(),qualifier.window(),chance,qualifier.traversal()),occurrences,chance);
    }
    public Progress advance(int budget)throws IOException{
        if(budget<1||budget>4096)throw new IllegalArgumentException("Search budget1..4096");
        qualifier.checkConfiguration();
        var cursor=search.snapshot();var known=occurrences.snapshot().get(qualifier.key().family());
        if(cursor.status()==ContinentCandidateSearch.Status.HELD_CHANGED_CANDIDATE)return result(Status.HELD,cursor,known,null);
        if(known!=null){
            var r=known.request();var c=r.candidate();
            if(cursor.status()!=ContinentCandidateSearch.Status.SELECTED||cursor.selected().x()!=c.x()||cursor.selected().z()!=c.z())
                throw new IOException("Occurrence does not match saved discovery; explicit recovery required");
            if(!r.key().equals(qualifier.key())||Double.doubleToLongBits(qualifier.chanceFor(c.biome(),chance))!=Double.doubleToLongBits(r.chance()))
                return result(Status.HELD,cursor,known,null);
            // Absence is terminal. Do not re-query terrain, consume another cursor,
            // re-roll presence or require this deposit's old location still to fit.
            if(!known.present())return result(Status.ABSENT,cursor,known,null);
            qualifier.retainCommitted(known);
        }
        cursor=search.advance(budget,qualifier);
        switch(cursor.status()){
            case SEARCHING: return result(Status.SEARCHING,cursor,null,null);
            case EXHAUSTED_WINDOW: return result(Status.EXHAUSTED,cursor,null,null);
            case HELD_CHANGED_CANDIDATE: return result(Status.HELD,cursor,known,null);
            case SELECTED: break;
        }
        var selected=qualifier.selection().orElseThrow(()->new IllegalStateException("Native selection unavailable"));
        if(selected.x()!=cursor.selected().x()||selected.z()!=cursor.selected().z())throw new IllegalStateException("Native cursor mismatch");
        var admitted=qualifier.admitOccurrence(occurrences,selected,qualifier.chanceFor(selected.biome(),chance));
        var entry=admitted.decision().entry();
        Status status=admitted.decision().status()==ContinentOccurrenceLedger.Status.HELD_CHANGED_INPUT?Status.HELD:
                entry.present()?Status.PRESENT:Status.ABSENT;
        return new Progress(status,cursor,Optional.of(entry),admitted.plan());
    }
    private static Progress result(Status status,ContinentCandidateSearch.Checkpoint cursor,
            ContinentOccurrenceLedger.Entry entry,GeologyPlanner.Plan plan){
        return new Progress(status,cursor,Optional.ofNullable(entry),Optional.ofNullable(plan));
    }
}
