package dev.godpc.industrialcolonies.geology;

import com.google.gson.*;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.pieces.*;
import net.minecraft.world.level.levelgen.structure.structures.*;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.*;
import static dev.godpc.industrialcolonies.geology.GeologyConfig.*;
import static dev.godpc.industrialcolonies.geology.GeologyMath.*;

/** Vein volume limits the connected mine layout. Structure placement rolls remain vanilla. */
public final class MineshaftVeins {
    private static final DeferredRegister<StructurePieceType> PIECES=DeferredRegister.create(Registries.STRUCTURE_PIECE,"industrial_colonies");
    public static final DeferredHolder<StructurePieceType,StructurePieceType> WORKING=PIECES.register("mineshaft_ore_working",()->MineshaftVeinPiece::new);
    public static final DeferredHolder<StructurePieceType,StructurePieceType> MASSIVE_MARKER=PIECES.register("massive_mine_marker",()->MassiveMinePiece::new);
    private MineshaftVeins() {}
    public static void register(IEventBus bus){PIECES.register(bus);}
    public static void attach(Structure.GenerationContext context,Structure.GenerationStub stub,MineshaftStructure.Type type){
        if(!enabled())return;
        var builder=stub.getPiecesBuilder();var original=builder.build().pieces();
        if(original.stream().anyMatch(p->p instanceof MineshaftVeinPiece))return;
        var room=original.stream().filter(p->p instanceof MineshaftPieces.MineShaftRoom).findFirst().orElseThrow();
        var boxes=original.stream().map(p->{var b=p.getBoundingBox();return new BoundingBox(b.minX(),b.minY(),b.minZ(),b.maxX(),b.maxY(),b.maxZ());}).toList();
        long salt=seed(context.seed(),context.chunkPos().x,context.chunkPos().z,0x4d494e455645494eL);
        Direction[] directions={Direction.NORTH,Direction.EAST,Direction.SOUTH,Direction.WEST};
        BlockPos best=null;Direction facing=null;int score=-1;
        var roomBox=room.getBoundingBox();
        for(int i=0;i<4;i++){
            Direction d=directions[(bounded(salt,4)+i)%4];
            int x=d==Direction.WEST?roomBox.minX():d==Direction.EAST?roomBox.maxX():roomBox.getCenter().getX();
            int z=d==Direction.NORTH?roomBox.minZ():d==Direction.SOUTH?roomBox.maxZ():roomBox.getCenter().getZ();
            BlockPos door=new BlockPos(x,roomBox.minY()+1,z);
            int available=MineshaftVeinPiece.availableBody(door,d,boxes,context.heightAccessor().getMinBuildHeight(),context.heightAccessor().getMaxBuildHeight());
            if(available>score){score=available;best=door;facing=d;}
        }
        if(score<=0)throw new IllegalStateException("Mineshaft has no space for an ore working");
        var site=sample(context,best.getX(),best.getZ());
        var planner=new GeologyPlanner(context.seed(),get(),(x,z)->site);
        List<JsonObject> definitions=planner.definitions();double[] weights=new double[definitions.size()];
        for(int i=0;i<weights.length;i++)weights[i]=planner.weight(definitions.get(i),site,best.getY());
        int chosen=weighted(weights,unit(salt+17));
        if(chosen<0)throw new IllegalStateException("Geology rules forbid every ore at an enabled mineshaft");
        JsonObject definition=definitions.get(chosen);
        double suitability=(planner.biomeWeight(definition,site)+planner.depthWeight(definition,best.getY()))/2;
        int quality=weighted(planner.qualityProbabilities(suitability),unit(salt+22));
        int lo=integer(definition,"normalSizeMin",1),hi=integer(definition,"normalSizeMax",lo);
        int volume=(int)Math.round((lo+bounded(salt+23,hi-lo+1))*numbers(object(get().settings(),"quality"),"sizeMultipliers")[quality]);
        double rich=number(definition,"normalRichOrePercent",0)*numbers(object(get().settings(),"quality"),"richMultipliers")[quality];
        BlockPos center=roomBox.getCenter();
        var body=GeologyMath.shape(salt,volume,definition.get("id").getAsString().equals("coal"));
        int minX=body.stream().mapToInt(Voxel::x).min().orElse(0),maxX=body.stream().mapToInt(Voxel::x).max().orElse(0);
        int minY=body.stream().mapToInt(Voxel::y).min().orElse(0),maxY=body.stream().mapToInt(Voxel::y).max().orElse(0);
        int minZ=body.stream().mapToInt(Voxel::z).min().orElse(0),maxZ=body.stream().mapToInt(Voxel::z).max().orElse(0);
        var envelope=new BoundingBox(center.getX()+minX,center.getY()+minY,center.getZ()+minZ,center.getX()+maxX,center.getY()+maxY,center.getZ()+maxZ);
        var retained=fitMine(original,room,envelope);
        builder.clear();retained.forEach(builder::addPiece);
        var protectedMine=retained.stream().map(StructurePiece::getBoundingBox).toList();
        builder.addPiece(new MineshaftVeinPiece(best,facing,protectedMine,salt,definition,type,
                center,volume,Math.min(1,rich),
                context.heightAccessor().getMinBuildHeight(),context.heightAccessor().getMaxBuildHeight()));
    }
    /** Keep complete vanilla pieces, a connected entrance, and additional galleries within vein reach. */
    public static List<StructurePiece> fitMine(List<StructurePiece> original,StructurePiece room,BoundingBox envelope){
        // A long first corridor can extend outside even a valid small deposit. Preserve paths
        // to the nearest two corridors so pruning cannot turn a real mine into an empty room.
        var parents=new IdentityHashMap<StructurePiece,StructurePiece>();
        var queue=new ArrayDeque<StructurePiece>();parents.put(room,null);queue.add(room);
        var required=Collections.newSetFromMap(new IdentityHashMap<StructurePiece,Boolean>());
        required.add(room);int corridors=0;
        while(!queue.isEmpty()&&corridors<2){
            var current=queue.removeFirst();
            if(current instanceof MineshaftPieces.MineShaftCorridor){
                corridors++;
                for(var p=current;p!=null;p=parents.get(p))required.add(p);
            }
            for(var p:original)if(!parents.containsKey(p)&&current.getBoundingBox().inflatedBy(1).intersects(p.getBoundingBox())){
                parents.put(p,current);queue.addLast(p);
            }
        }
        var retained=new ArrayList<StructurePiece>();retained.add(room);boolean added;
        do{added=false;for(var p:original){
            if(retained.contains(p)||(!required.contains(p)&&!envelope.isInside(p.getBoundingBox().getCenter())))continue;
            if(retained.stream().anyMatch(r->r.getBoundingBox().inflatedBy(1).intersects(p.getBoundingBox()))){retained.add(p);added=true;}
        }}while(added);
        return List.copyOf(retained);
    }
    private static GeologyPlanner.Site sample(Structure.GenerationContext c,int x,int z){
        int surface=c.chunkGenerator().getBaseHeight(x,z,Heightmap.Types.OCEAN_FLOOR_WG,c.heightAccessor(),c.randomState());
        String biome=biome(c,x,surface+4,z);Set<String> groups=families(biome);
        for(int dy=16;groups.isEmpty()&&dy<=96;dy+=16){String upper=biome(c,x,surface+dy,z);Set<String> next=families(upper);if(!next.isEmpty()){groups=next;biome=upper;}}
        var thresholds=object(get().settings(),"terrainThresholds");
        int mountain=integer(thresholds,"mountainSurfaceY",120),extreme=integer(thresholds,"extremeSurfaceY",190);
        String terrain=surface>=extreme?"extreme":surface>=mountain||groups.contains("mountain_highland")?"mountain":"normal";
        if(!terrain.equals("normal")){Set<String> expanded=new LinkedHashSet<>(groups);expanded.add("mountain_highland");groups=Set.copyOf(expanded);}
        return new GeologyPlanner.Site(biome,groups,terrain,surface);
    }
    private static String biome(Structure.GenerationContext c,int x,int y,int z){
        return c.biomeSource().getNoiseBiome(QuartPos.fromBlock(x),QuartPos.fromBlock(y),QuartPos.fromBlock(z),c.randomState().sampler())
                .unwrapKey().map(k->k.location().toString()).orElse("minecraft:plains");
    }
}
