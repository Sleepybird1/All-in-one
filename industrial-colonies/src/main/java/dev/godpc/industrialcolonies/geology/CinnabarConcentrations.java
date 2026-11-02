package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;
import static dev.godpc.industrialcolonies.geology.GeologyMath.*;
import static dev.godpc.industrialcolonies.geology.CinnabarSurfaceGeometry.*;
import static dev.godpc.industrialcolonies.geology.MountainRangeSurvey.Column;

/** Read-only deterministic fitting of finite saved requests. READY is geometry, not ore custody. */
public final class CinnabarConcentrations {
    public record Policy(int concentrations,int minimumY,double coverage,int maximumThickness,int maximumWidth,int maximumAnchors){
        public Policy {
            if(concentrations<1||concentrations>64||minimumY<-2048||minimumY>300
                    ||!Double.isFinite(coverage)||coverage<.6||coverage>.8||maximumThickness<1||maximumThickness>3
                    ||maximumWidth<1||maximumWidth>128||maximumAnchors<1||maximumAnchors>MountainRangeSurvey.MAX_OBSERVATIONS)
                throw new IllegalArgumentException("Invalid finite cinnabar fitting policy");
        }
        public String fingerprint(){
            String value="IC_CINNABAR_CONCENTRATIONS_V1\n1000:80,5000:18,15000:2\n"+concentrations+":"+minimumY+":"+Double.toHexString(coverage)+":"+maximumThickness+":"+maximumWidth+":"+maximumAnchors;
            try{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8)));}
            catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
        }
    }
    public enum Status { SEARCHING, READY, HELD_UNFITTED, HELD_LIMIT, HELD_DOMAIN }
    public record Selection(String identity,Column anchor,int anchorY,int width,double frequencyRoll,Plan geometry) {}
    public record Progress(Status status,int selected,int requested,int anchorIndex,int width,long evaluations) {}
    @FunctionalInterface public interface Heights {int topY(int x,int z)throws IOException;}
    private final CinnabarRangeAllocations.Allocation allocation;
    private final Policy policy;
    private final List<Column> anchors;
    private final Set<Column> members;
    private final List<Selection> selections=new ArrayList<>();
    private final Set<Voxel> occupied=new HashSet<>();
    private int anchorIndex,width=1;
    private long evaluations;
    private Status status=Status.SEARCHING;
    /** Explicit count remains a design input; size probabilities come from the saved chart. */
    public static CinnabarRangeAllocations.Plan proposedAllocation(String component,int concentrationCount){
        if(concentrationCount<1||concentrationCount>64)throw new IllegalArgumentException("Explicit concentration count required");
        long seed=componentSeed(component);var reserves=new ArrayList<Integer>();
        for(int slot=0;slot<concentrationCount;slot++){
            double roll=unit(seed(seed,slot,0,0x53495a45));reserves.add(roll<.8?1000:roll<.98?5000:15000);
        }
        return new CinnabarRangeAllocations.Plan(reserves);
    }
    public CinnabarConcentrations(MountainRangeSurvey.Range range,CinnabarRangeAllocations.Allocation allocation,Policy policy){
        this.allocation=Objects.requireNonNull(allocation);this.policy=Objects.requireNonNull(policy);Objects.requireNonNull(range);
        if(allocation.plan().concentrationReserves().size()!=policy.concentrations())throw new IllegalArgumentException("Saved allocation/policy count differs");
        members=Set.copyOf(range.members());if(members.size()!=range.members().size())throw new IllegalArgumentException("Invalid range members");
        long component=componentSeed(allocation.componentIdentity());var order=new ArrayList<>(members);
        order.sort(Comparator.<Column>comparingLong(p->seed(component,p.x(),p.z(),0x414e4348)).thenComparing(Comparator.naturalOrder()));anchors=List.copyOf(order);
    }
    public Progress progress(){return new Progress(status,selections.size(),policy.concentrations(),anchorIndex,width,evaluations);}
    public CinnabarRangeAllocations.Allocation allocation(){return allocation;}
    public Policy policy(){return policy;}
    /** Reconstruct an already saved location, never search for a substitute. Null means no longer fitting. */
    public Selection revalidate(int slot,Column anchor,int savedWidth,Heights heights)throws IOException{
        Objects.requireNonNull(heights);
        if(slot<0||slot>=policy.concentrations()||!members.contains(anchor)||savedWidth<1||savedWidth>policy.maximumWidth())throw new IllegalArgumentException("Invalid saved concentration location");
        int x=anchor.x()-savedWidth/2,z=anchor.z()-savedWidth/2;
        if((long)x-4<-MountainRangeSurvey.COORDINATE_LIMIT||(long)z-4<-MountainRangeSurvey.COORDINATE_LIMIT
                ||(long)x+savedWidth+4>MountainRangeSurvey.COORDINATE_LIMIT||(long)z+savedWidth+4>MountainRangeSurvey.COORDINATE_LIMIT)throw new IllegalArgumentException("Saved concentration outside native domain");
        int y=heights.topY(anchor.x(),anchor.z());double roll=frequencyRoll(allocation.componentIdentity(),slot);Plan full;
        try{
            full=CinnabarSurfaceGeometry.plan(seed(componentSeed(allocation.componentIdentity()),slot,0,0x47454f4d),x,z,savedWidth,y,policy.minimumY(),roll,policy.coverage(),policy.maximumThickness(),new Terrain(){
                public int topY(int px,int pz){try{return heights.topY(px,pz);}catch(IOException e){throw new UncheckedIOException(e);}}
                public boolean mountain(int px,int pz){return members.contains(new Column(px,pz));}
            });
        }catch(UncheckedIOException e){throw e.getCause();}
        Plan fitted=exactBudget(full,allocation.plan().concentrationReserves().get(slot),policy.maximumThickness());
        return fitted==null?null:new Selection(allocation.concentrationIdentity(slot),anchor,y,savedWidth,roll,fitted);
    }
    public List<Selection> completed(){if(status!=Status.READY)throw new IllegalStateException("Unfitted cinnabar requests cannot be released");return List.copyOf(selections);}
    public double currentFrequencyRoll(){return frequencyRoll(allocation.componentIdentity(),selections.size());}
    public static double frequencyRoll(String component,int slot){if(slot<0||slot>=64)throw new IllegalArgumentException("Slot outside allocation bounds");return unit(seed(componentSeed(component),slot,0,0x46524551));}
    /** Budget counts bounded geometry evaluations, not native CPU time or block writes. */
    public Progress advance(int budget,Heights heights)throws IOException{
        if(budget<1||budget>64)throw new IllegalArgumentException("Geometry evaluation budget1..64");Objects.requireNonNull(heights);
        for(int i=0;i<budget&&status==Status.SEARCHING;i++){
            if(anchorIndex>=anchors.size()){status=Status.HELD_UNFITTED;break;}
            if(anchorIndex>=policy.maximumAnchors()){status=Status.HELD_LIMIT;break;}
            Column anchor=anchors.get(anchorIndex);
            // Geometry probes up to four columns outside its footprint. Never lose native float precision.
            int x=anchor.x()-width/2,z=anchor.z()-width/2;
            if((long)x-4<-MountainRangeSurvey.COORDINATE_LIMIT||(long)z-4<-MountainRangeSurvey.COORDINATE_LIMIT
                    ||(long)x+width+4>MountainRangeSurvey.COORDINATE_LIMIT||(long)z+width+4>MountainRangeSurvey.COORDINATE_LIMIT){status=Status.HELD_DOMAIN;break;}
            int y=heights.topY(anchor.x(),anchor.z());double roll=currentFrequencyRoll();
            if(roll>=frequency(y,policy.minimumY())){evaluations++;nextAnchor();continue;}
            Plan full;
            try{
                long geometrySeed=seed(componentSeed(allocation.componentIdentity()),selections.size(),0,0x47454f4d);
                full=CinnabarSurfaceGeometry.plan(geometrySeed,x,z,width,y,policy.minimumY(),roll,policy.coverage(),policy.maximumThickness(),new Terrain(){
                    public int topY(int px,int pz){try{return heights.topY(px,pz);}catch(IOException e){throw new UncheckedIOException(e);}}
                    public boolean mountain(int px,int pz){return members.contains(new Column(px,pz));}
                });
            }catch(UncheckedIOException e){throw e.getCause();}
            // Failed reads leave this evaluation/cursor untouched. No new random roll on retry.
            evaluations++;int target=allocation.plan().concentrationReserves().get(selections.size());
            Plan fitted=exactBudget(full,target,policy.maximumThickness());
            if(fitted!=null&&Collections.disjoint(occupied,fitted.blocks())){
                selections.add(new Selection(allocation.concentrationIdentity(selections.size()),anchor,y,width,roll,fitted));occupied.addAll(fitted.blocks());
                anchorIndex=0;width=1;if(selections.size()==policy.concentrations())status=Status.READY;
            }else if(width==policy.maximumWidth()||full.strokes().size()>target){nextAnchor();}else width++;
        }
        return progress();
    }
    private void nextAnchor(){anchorIndex++;width=1;}
    /** Retain every selected visible front; use1..3 inward layers to meet the exact finite request. */
    private static Plan exactBudget(Plan full,int target,int thickness){
        if(!full.admitted())return null;
        Set<Voxel> chosen=new HashSet<>();for(var stroke:full.strokes())chosen.add(stroke.face().front());
        if(chosen.size()>target||full.blocks().size()<target)return null;
        for(int depth=1;depth<thickness&&chosen.size()<target;depth++)for(var stroke:full.strokes()){
            if(stroke.blocks().size()>depth&&chosen.containsAll(stroke.blocks().subList(0,depth)))chosen.add(stroke.blocks().get(depth));
            if(chosen.size()==target)break;
        }
        if(chosen.size()!=target)throw new IllegalStateException("Finite surface budget could not retain stroke prefixes");
        var strokes=new ArrayList<Stroke>();
        for(var stroke:full.strokes()){
            var blocks=new ArrayList<Voxel>();for(var block:stroke.blocks()){if(!chosen.contains(block))break;blocks.add(block);}
            if(blocks.isEmpty())throw new IllegalStateException("Selected exposed front lost");strokes.add(new Stroke(stroke.face(),blocks));
        }
        var result=new Plan(true,"exact finite surface request",full.frequency(),full.eligibleFronts(),strokes);
        if(!result.blocks().equals(chosen))throw new IllegalStateException("Finite surface union differs");return result;
    }
    private static long componentSeed(String component){
        if(component==null||!component.matches("[0-9a-f]{64}"))throw new IllegalArgumentException("Canonical component identity required");
        long value=0;for(int i=0;i<64;i+=16)value=mix(value^Long.parseUnsignedLong(component.substring(i,i+16),16));return value;
    }
}
