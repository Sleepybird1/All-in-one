package dev.godpc.industrialcolonies.geology;

import java.util.*;

/** Deposit-fitted gallery geometry. No world access, reserve changes or occurrence rolls. */
public final class FiniteMineLayout {
    public enum Heading {
        NORTH(0,-1),EAST(1,0),SOUTH(0,1),WEST(-1,0);
        public final int dx,dz;
        Heading(int dx,int dz){this.dx=dx;this.dz=dz;}
        public Heading opposite(){return values()[(ordinal()+2)%4];}
    }
    public enum Kind { CORRIDOR, CROSSING }
    public record Segment(Kind kind,Heading heading,MassiveDepositGeometry.Bounds bounds){
        public Segment{Objects.requireNonNull(kind);Objects.requireNonNull(heading);Objects.requireNonNull(bounds);}
    }
    public record Plan(MassiveDepositGeometry.Bounds chamber,List<Segment> segments,int corridors,int examinedChambers){
        public Plan{
            Objects.requireNonNull(chamber);segments=List.copyOf(segments);
            if(corridors<2||corridors!=segments.stream().filter(s->s.kind()==Kind.CORRIDOR).count()
                    ||segments.size()>127||examinedChambers<1)throw new IllegalArgumentException("Connected finite gallery plan required");
        }
    }
    private record Junction(int x,int floorY,int z,int halfWidth,int depth,Heading back) {}
    private record Draft(MassiveDepositGeometry.Bounds chamber,List<Segment> segments,int corridors) {}
    private FiniteMineLayout() {}

    /** Check actual finite voxel centres nearest first. The reservation and its geometry never change. */
    public static Optional<Plan> plan(MiningScanScope scope){
        if(!scope.isContinent())throw new IllegalArgumentException("Actual finite reservation required");
        var c=scope.reservedCandidate();
        var centers=new ArrayList<>(GeologyMath.shape(c.geometrySeed(),c.cells(),scope.isCoal()));
        centers.sort(Comparator.comparingLong((GeologyMath.Voxel p)->(long)p.x()*p.x()+(long)p.y()*p.y()+(long)p.z()*p.z())
                .thenComparingInt(GeologyMath.Voxel::x).thenComparingInt(GeologyMath.Voxel::y).thenComparingInt(GeologyMath.Voxel::z));
        int examined=0,target=Math.min(16,2+c.cells()/5000);Draft best=null;
        for(var p:centers){
            int x=Math.addExact(c.x(),p.x()),y=Math.addExact(c.y(),p.y()),z=Math.addExact(c.z(),p.z());
            var chamber=new MassiveDepositGeometry.Bounds(x-2,y-2,z-2,x+2,y+1,z+2);
            if(!scope.enclosesEnvelope(chamber))continue;
            examined++;var draft=build(scope,chamber);
            if(best==null||draft.corridors()>best.corridors()
                    ||draft.corridors()==best.corridors()&&draft.segments().size()>best.segments().size())best=draft;
            if(best.corridors()>=target||examined>=64&&best.corridors()>=2)
                return Optional.of(new Plan(best.chamber(),best.segments(),best.corridors(),examined));
        }
        return best==null||best.corridors()<2?Optional.empty():Optional.of(new Plan(best.chamber(),best.segments(),best.corridors(),examined));
    }
    private static Draft build(MiningScanScope scope,MassiveDepositGeometry.Bounds chamber){
        var occupied=new ArrayList<MassiveDepositGeometry.Bounds>();occupied.add(chamber);
        var segments=new ArrayList<Segment>();var queue=new ArrayDeque<Junction>();
        queue.add(new Junction(chamber.minX()+2,chamber.minY()+1,chamber.minZ()+2,2,0,null));int corridors=0;
        while(!queue.isEmpty()&&segments.size()<127){
            var parent=queue.removeFirst();
            for(var heading:Heading.values()){
                if(segments.size()>=127)break;if(heading==parent.back())continue;
                int start=parent.halfWidth()+1,end=start+4;
                var gallery=heading.dx==0
                        ?new MassiveDepositGeometry.Bounds(parent.x()-1,parent.floorY(),parent.z()+Math.min(heading.dz*start,heading.dz*end),parent.x()+1,parent.floorY()+2,parent.z()+Math.max(heading.dz*start,heading.dz*end))
                        :new MassiveDepositGeometry.Bounds(parent.x()+Math.min(heading.dx*start,heading.dx*end),parent.floorY(),parent.z()-1,parent.x()+Math.max(heading.dx*start,heading.dx*end),parent.floorY()+2,parent.z()+1);
                if(!admit(scope,gallery,occupied))continue;
                segments.add(new Segment(Kind.CORRIDOR,heading,gallery));occupied.add(gallery);corridors++;
                if(parent.depth()>=8||segments.size()>=127)continue;
                int distance=end+3,cx=parent.x()+heading.dx*distance,cz=parent.z()+heading.dz*distance;
                var crossing=new MassiveDepositGeometry.Bounds(cx-2,parent.floorY(),cz-2,cx+2,parent.floorY()+2,cz+2);
                if(!admit(scope,crossing,occupied))continue;
                segments.add(new Segment(Kind.CROSSING,heading,crossing));occupied.add(crossing);
                queue.addLast(new Junction(cx,parent.floorY(),cz,2,parent.depth()+1,heading.opposite()));
            }
        }
        return new Draft(chamber,List.copyOf(segments),corridors);
    }
    private static boolean admit(MiningScanScope scope,MassiveDepositGeometry.Bounds box,List<MassiveDepositGeometry.Bounds> occupied){
        if(!scope.enclosesEnvelope(box))return false;
        for(var other:occupied)if(box.minX()<=other.maxX()&&box.maxX()>=other.minX()&&box.minY()<=other.maxY()&&box.maxY()>=other.minY()
                &&box.minZ()<=other.maxZ()&&box.maxZ()>=other.minZ())return false;
        return true;
    }
}
