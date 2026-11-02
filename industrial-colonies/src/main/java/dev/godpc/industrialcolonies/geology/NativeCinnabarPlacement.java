package dev.godpc.industrialcolonies.geology;

import java.io.IOException;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.WorldGenRegion;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.chunk.*;
import net.minecraft.world.level.chunk.status.ChunkStatus;
import net.minecraft.world.level.levelgen.Heightmap;

/** Explicit surface-stage entry. No automatic hooks; all resource groups share caller's open ledger. */
public final class NativeCinnabarPlacement {
    private NativeCinnabarPlacement(){}
    private static List<CinnabarConcentrations.Selection> plans(ServerLevel level,List<NativeMountainRangeSurvey.SavedConcentrations> sources)throws IOException{
        if(sources.isEmpty()||sources.size()>64)throw new IllegalArgumentException("Explicit bounded saved range group required");
        var plans=new ArrayList<CinnabarConcentrations.Selection>();
        for(var source:sources){source.requireLevel(level);plans.addAll(source.completed());}return List.copyOf(plans);
    }
    public static CinnabarOwnerPlacement.Intent intent(ServerLevel level,ChunkPos owner,List<NativeMountainRangeSurvey.SavedConcentrations> sources)throws IOException{
        return CinnabarOwnerPlacement.intent(owner.x,owner.z,plans(level,sources));
    }
    public static CinnabarOwnerPlacement.Result place(WorldGenRegion region,ChunkAccess owner,
            NativeMountainRangeSurvey.SavedConcentrations selections)throws IOException{
        return place(region,owner,List.of(selections));
    }
    public static CinnabarOwnerPlacement.Result place(WorldGenRegion region,ChunkAccess owner,
            List<NativeMountainRangeSurvey.SavedConcentrations> sources)throws IOException{
        var plans=plans(region.getLevel(),sources);
        var intent=CinnabarOwnerPlacement.intent(owner.getPos().x,owner.getPos().z,plans);
        if(region.getLevel().dimension()!=Level.OVERWORLD||!region.getCenter().equals(owner.getPos())
                ||!(owner instanceof ProtoChunk)||owner instanceof ImposterProtoChunk||owner.isUpgrading()
                ||owner.getPersistedStatus().isBefore(ChunkStatus.CARVERS)||!owner.getPersistedStatus().isBefore(ChunkStatus.FEATURES)
                ||!owner.hasData(MiningOreOwnership.LEDGER)||owner.getData(MiningOreOwnership.LEDGER).sealed()
                ||owner.getData(MiningOreOwnership.LEDGER).failed())throw new IllegalStateException("Fresh surface owner and shared open provenance required");
        if(!owner.getData(MiningOreOwnership.LEDGER).surfacePending(intent.identity()))throw new IllegalStateException("Matching saved surface intent required");
        // Neighbor terrain must exist before exterior tests. false forbids implicit chunk creation;
        // WorldGenRegion also enforces its supplied generation cache. Never acquire server chunks here.
        for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++){
            var chunk=region.getChunk(owner.getPos().x+dx,owner.getPos().z+dz,ChunkStatus.CARVERS,false);
            if(chunk==null||chunk.getPersistedStatus().isBefore(ChunkStatus.CARVERS))throw new IllegalStateException("Surface neighbor terrain unavailable");
            if(dx==0&&dz==0&&chunk!=owner)throw new IllegalStateException("Foreign surface owner");
        }
        var id=ResourceLocation.parse("industrial_colonies:cinnabar");
        if(!BuiltInRegistries.BLOCK.containsKey(id))throw new IllegalStateException("Missing cinnabar block");
        var output=BuiltInRegistries.BLOCK.get(id).defaultBlockState();
        int before=owner.getData(MiningOreOwnership.LEDGER).remaining();
        var result=CinnabarOwnerPlacement.place(owner.getPos().x,owner.getPos().z,plans,new CinnabarOwnerPlacement.Access(){
            private BlockPos pos(GeologyMath.Voxel voxel){return new BlockPos(voxel.x(),voxel.y(),voxel.z());}
            public CinnabarOwnerPlacement.Material material(GeologyMath.Voxel voxel){
                var state=region.getBlockState(pos(voxel));
                if((voxel.x()>>4)==owner.getPos().x&&(voxel.z()>>4)==owner.getPos().z&&owner.getData(MiningOreOwnership.LEDGER).claimed(voxel.x(),voxel.y(),voxel.z()))return CinnabarOwnerPlacement.Material.OTHER;
                return state.equals(output)?CinnabarOwnerPlacement.Material.CINNABAR:GeologyFeature.replaceable(state)?CinnabarOwnerPlacement.Material.REPLACEABLE:CinnabarOwnerPlacement.Material.OTHER;
            }
            public boolean exterior(CinnabarSurfaceGeometry.Face face){
                var air=pos(face.front()).offset(face.dx(),face.dy(),face.dz());
                return region.getBlockState(air).isAir()&&air.getY()>=region.getHeight(Heightmap.Types.WORLD_SURFACE,air.getX(),air.getZ());
            }
            public boolean write(GeologyMath.Voxel voxel){return region.setBlock(pos(voxel),output,2);}
            public void record(String key,GeologyMath.Voxel voxel){
                owner.getData(MiningOreOwnership.LEDGER).recordGenerated(key,voxel.x(),voxel.y(),voxel.z());owner.setUnsaved(true);
            }
            public void abort(){MiningOreOwnership.abort(owner);}
        });
        if(result.status()==CinnabarOwnerPlacement.Status.WRITTEN){
            try{
                if(result.expected()!=intent.targets().size()||result.written()!=result.expected()||owner.getData(MiningOreOwnership.LEDGER).remaining()!=before+result.written())throw new IllegalStateException("Surface write/provenance counts differ");
            }catch(RuntimeException|Error failure){MiningOreOwnership.abort(owner);throw failure;}
            // Do not mask a post-seal save-dirty failure with an invalid attempt to abort a sealed ledger.
            owner.getData(MiningOreOwnership.LEDGER).finishSurface(intent.identity());owner.setUnsaved(true);
        }
        return result;
    }
}
