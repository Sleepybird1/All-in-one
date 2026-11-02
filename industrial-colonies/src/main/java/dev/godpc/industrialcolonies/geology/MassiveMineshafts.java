package dev.godpc.industrialcolonies.geology;

import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.structures.MineshaftPieces;
import static dev.godpc.industrialcolonies.geology.GeologyConfig.*;

/** Experimental deposit-first mine admission; legacy attachment and saved pieces remain separate. */
public final class MassiveMineshafts {
    private MassiveMineshafts() {}
    public static boolean attach(Structure.GenerationContext context,Structure.GenerationStub stub,GeologyWorld world) {
        var builder=stub.getPiecesBuilder();var original=builder.build().pieces();
        if(original.stream().anyMatch(p->p instanceof MassiveMinePiece))return true;
        var room=original.stream().filter(p->p instanceof MineshaftPieces.MineShaftRoom).findFirst().orElse(null);
        if(room==null)return false;
        for(var deposit:MassiveDeposits.discover(world.planner,MassiveDeposits.settings(get()),context.chunkPos().x,context.chunkPos().z)){
            int minimum=Math.max(context.heightAccessor().getMinBuildHeight(),integer(object(deposit.plan().definition(),"placement"),"minY",context.heightAccessor().getMinBuildHeight()+1)-1);
            var retained=fit(original,room,deposit.body(),minimum,context.heightAccessor().getMaxBuildHeight());
            if(retained.isEmpty()||!permitted(retained,deposit,world))continue;
            builder.clear();retained.forEach(builder::addPiece);builder.addPiece(new MassiveMinePiece(room.getBoundingBox(),deposit));
            return true;
        }
        return false;
    }
    private static boolean permitted(List<StructurePiece> pieces,MassiveDeposits.Deposit deposit,GeologyWorld world){
        var sites=new HashMap<Long,GeologyPlanner.Site>();
        var priorByChunk=new HashMap<Long,List<MassiveDepositGeometry.Body>>();
        var settings=MassiveDeposits.settings(get());
        var selected=deposit.plan().candidate();
        for(var piece:pieces){
            var b=piece.getBoundingBox();
            for(int x=b.minX();x<=b.maxX();x++)for(int z=b.minZ();z<=b.maxZ();z++){
                if(!GeologyFeature.allowedPlacement(world,deposit.plan().definition(),new BlockPos(x,b.minY(),z),sites))return false;
                // A conflicting body can reach a far gallery without touching the mine's origin chunk.
                var earlier=priorByChunk.computeIfAbsent(ChunkPos.asLong(x>>4,z>>4),key->{
                    var chunk=new ChunkPos(key);
                    return MassiveDeposits.discover(world.planner,settings,chunk.x,chunk.z).stream().filter(other->{
                        var c=other.plan().candidate();return c.regionX()<selected.regionX()||(c.regionX()==selected.regionX()&&c.regionZ()<selected.regionZ());
                    }).map(MassiveDeposits.Deposit::body).toList();
                });
                if(earlier.isEmpty())continue;
                for(int y=b.minY();y<=b.maxY();y++)if(deposit.body().contains(x,y,z))for(var prior:earlier)if(prior.contains(x,y,z))return false;
            }
        }
        return true;
    }
    /** Full-piece envelopes; mineral-bearing depth is measured separately without growing the deposit. */
    public static List<StructurePiece> fit(List<StructurePiece> original,StructurePiece room,MassiveDepositGeometry.Body body,int minY,int maxY) {
        return fit(original,room,piece->fits(piece,body,minY,maxY));
    }
    /** Uses the same connected-gallery policy for exact finite continent reservations. */
    public static List<StructurePiece> fit(List<StructurePiece> original,StructurePiece room,MiningScanScope scope){
        return fit(original,room,piece->{var b=piece.getBoundingBox();return b.minY()>scope.minBuildY()&&b.maxY()<scope.maxBuildYExclusive()-1
            &&scope.enclosesEnvelope(new MassiveDepositGeometry.Bounds(b.minX(),b.minY(),b.minZ(),b.maxX(),b.maxY(),b.maxZ()));});
    }
    private static List<StructurePiece> fit(List<StructurePiece> original,StructurePiece room,java.util.function.Predicate<StructurePiece> fits) {
        if(!original.contains(room)||!fits.test(room))return List.of();
        Set<StructurePiece> eligible=Collections.newSetFromMap(new IdentityHashMap<>());
        for(var piece:original){
            if(piece==room||fits.test(piece))eligible.add(piece);
        }
        // Do not let an approximate bounding-box adjacency graph prune an intact vanilla layout.
        if(eligible.size()==original.size())return original.stream().anyMatch(p->p instanceof MineshaftPieces.MineShaftCorridor)?List.copyOf(original):List.of();
        var result=new ArrayList<StructurePiece>();var queue=new ArrayDeque<StructurePiece>();result.add(room);queue.add(room);
        while(!queue.isEmpty()){
            var current=queue.removeFirst();
            for(var piece:original)if(eligible.contains(piece)&&!result.contains(piece)&&current.getBoundingBox().inflatedBy(1).intersects(piece.getBoundingBox())){
                result.add(piece);queue.addLast(piece);
            }
        }
        long available=original.stream().filter(p->p instanceof MineshaftPieces.MineShaftCorridor).count();
        long kept=result.stream().filter(p->p instanceof MineshaftPieces.MineShaftCorridor).count();
        // Reject the candidate rather than turn a valid mine into a room with missing galleries.
        if(kept<Math.min(2,available)||kept==0)return List.of();
        return List.copyOf(result);
    }
    private static boolean fits(StructurePiece piece,MassiveDepositGeometry.Body body,int minY,int maxY){
        var box=piece.getBoundingBox();
        return box.minY()>minY&&box.maxY()<maxY-1&&body.enclosesEnvelope(new MassiveDepositGeometry.Bounds(box.minX(),box.minY(),box.minZ(),box.maxX(),box.maxY(),box.maxZ()));
    }
}
