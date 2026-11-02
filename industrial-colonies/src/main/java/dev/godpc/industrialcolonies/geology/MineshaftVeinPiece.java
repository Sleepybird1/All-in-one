package dev.godpc.industrialcolonies.geology;

import com.google.gson.*;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.pieces.*;
import net.minecraft.world.level.levelgen.structure.structures.MineshaftStructure;
import static dev.godpc.industrialcolonies.geology.GeologyMath.*;

/** A short working excavated into one bounded ore body, attached to the original central room.
 * Original piece volumes are protected. Every read/write is clipped to the supplied owning chunk.
 * This is structure terrain: the solid ore face may occupy natural air or fluid, like other structure walls. */
public final class MineshaftVeinPiece extends StructurePiece {
    private BlockPos door;
    private final Direction outward;
    private List<BoundingBox> protectedBoxes;
    private final long salt;
    private final String host,floor;
    private final JsonArray rich;
    private double richFraction;
    private int bodyVolume;
    private BlockPos bodyCenter;
    private boolean coalSeam;
    private List<Voxel> attractors=List.of();
    private Map<BlockPos,BlockState> bodyCache;
    private JsonObject placementDefinition=new JsonObject();
    public MineshaftVeinPiece(BlockPos door,Direction outward,List<BoundingBox> protectedBoxes,long salt,JsonObject definition,MineshaftStructure.Type type,int min,int max){
        super(MineshaftVeins.WORKING.get(),0,bounds(door,outward,min,max));
        this.door=door;this.outward=outward;this.protectedBoxes=List.copyOf(protectedBoxes);this.salt=salt;
        host=definition.get("hostRock").getAsString();rich=definition.getAsJsonArray("richOres").deepCopy();richFraction=definition.get("normalRichOrePercent").getAsDouble();
        floor=type==MineshaftStructure.Type.MESA?"minecraft:dark_oak_planks":"minecraft:oak_planks";
    }
    public MineshaftVeinPiece(BlockPos door,Direction outward,List<BoundingBox> boxes,long salt,JsonObject definition,MineshaftStructure.Type type,BlockPos center,int volume,double fraction,int min,int max){
        this(door,outward,boxes,salt,definition,type,min,max);
        bodyCenter=center;bodyVolume=volume;richFraction=fraction;coalSeam=definition.get("id").getAsString().equals("coal");
        if(definition.has("placement"))placementDefinition.add("placement",definition.get("placement").deepCopy());
        // A bounded set of corridor centers pulls lobes toward the mine, conserving ore volume.
        attractors=boxes.stream().limit(16).map(b->new Voxel(b.getCenter().getX()-center.getX(),b.getCenter().getY()-center.getY(),b.getCenter().getZ()-center.getZ())).toList();
        var points=bodyPositions();
        boundingBox=new BoundingBox(points.stream().mapToInt(BlockPos::getX).min().orElse(center.getX()),Math.max(min+1,points.stream().mapToInt(BlockPos::getY).min().orElse(center.getY())),points.stream().mapToInt(BlockPos::getZ).min().orElse(center.getZ()),points.stream().mapToInt(BlockPos::getX).max().orElse(center.getX()),Math.min(max-2,points.stream().mapToInt(BlockPos::getY).max().orElse(center.getY())),points.stream().mapToInt(BlockPos::getZ).max().orElse(center.getZ()));
    }
    public MineshaftVeinPiece(StructurePieceSerializationContext context,CompoundTag tag){
        super(MineshaftVeins.WORKING.get(),tag);
        door=BlockPos.of(tag.getLong("Door"));outward=Direction.from2DDataValue(tag.getInt("Outward"));salt=tag.getLong("VeinSeed");
        host=tag.getString("Host");floor=tag.getString("Floor");rich=JsonParser.parseString(tag.getString("Rich")).getAsJsonArray();richFraction=tag.getDouble("RichFraction");
        bodyVolume=tag.getInt("BodyVolume");
        if(tag.contains("PlacementRules"))placementDefinition=JsonParser.parseString(tag.getString("PlacementRules")).getAsJsonObject();
        if(bodyVolume>0){bodyCenter=BlockPos.of(tag.getLong("BodyCenter"));coalSeam=tag.getBoolean("CoalSeam");int[] a=tag.getIntArray("Attractors");if(a.length%3!=0)throw new IllegalArgumentException("Invalid tunnel attractors");List<Voxel> points=new ArrayList<>();for(int i=0;i<a.length;i+=3)points.add(new Voxel(a[i],a[i+1],a[i+2]));attractors=List.copyOf(points);}
        int[] packed=tag.getIntArray("Protected");if(packed.length%6!=0)throw new IllegalArgumentException("Invalid protected mineshaft boxes");
        List<BoundingBox> boxes=new ArrayList<>();for(int i=0;i<packed.length;i+=6)boxes.add(new BoundingBox(packed[i],packed[i+1],packed[i+2],packed[i+3],packed[i+4],packed[i+5]));protectedBoxes=List.copyOf(boxes);
    }
    @Override protected void addAdditionalSaveData(StructurePieceSerializationContext c,CompoundTag tag){
        tag.putLong("Door",door.asLong());tag.putInt("Outward",outward.get2DDataValue());tag.putLong("VeinSeed",salt);
        tag.putString("Host",host);tag.putString("Floor",floor);tag.putString("Rich",rich.toString());tag.putDouble("RichFraction",richFraction);
        if(bodyVolume>0&&placementDefinition.has("placement"))tag.putString("PlacementRules",placementDefinition.toString());
        if(bodyVolume>0){tag.putInt("BodyVolume",bodyVolume);tag.putLong("BodyCenter",bodyCenter.asLong());tag.putBoolean("CoalSeam",coalSeam);int[] a=new int[attractors.size()*3];for(int j=0;j<attractors.size();j++){a[j*3]=attractors.get(j).x();a[j*3+1]=attractors.get(j).y();a[j*3+2]=attractors.get(j).z();}tag.putIntArray("Attractors",a);}
        int[] packed=new int[protectedBoxes.size()*6];int i=0;
        for(var b:protectedBoxes){packed[i++]=b.minX();packed[i++]=b.minY();packed[i++]=b.minZ();packed[i++]=b.maxX();packed[i++]=b.maxY();packed[i++]=b.maxZ();}tag.putIntArray("Protected",packed);
    }
    public BlockPos door(){return door;}
    public String host(){return host;}
    @Override public void move(int x,int y,int z){
        super.move(x,y,z);door=door.offset(x,y,z);
        if(bodyCenter!=null)bodyCenter=bodyCenter.offset(x,y,z);bodyCache=null;
        protectedBoxes=protectedBoxes.stream().map(b->new BoundingBox(b.minX()+x,b.minY()+y,b.minZ()+z,b.maxX()+x,b.maxY()+y,b.maxZ()+z)).toList();
    }
    public static BlockPos position(BlockPos origin,Direction d,int along,int across,int height){
        return origin.offset(d.getStepX()*along-d.getStepZ()*across,height,d.getStepZ()*along+d.getStepX()*across);
    }
    private static BoundingBox bounds(BlockPos p,Direction d,int min,int max){
        BlockPos a=position(p,d,0,-4,-2),b=position(p,d,14,4,5);
        return new BoundingBox(Math.min(a.getX(),b.getX()),Math.max(min+1,p.getY()-2),Math.min(a.getZ(),b.getZ()),
                Math.max(a.getX(),b.getX()),Math.min(max-2,p.getY()+5),Math.max(a.getZ(),b.getZ()));
    }
    private static boolean body(int along,int across,int height){
        double a=(along-9)/5.0,b=across/4.0,c=(height-1)/3.0;return a*a+b*b+c*c<=1;
    }
    private static boolean working(int along,int across,int height){return along>=1&&along<=4&&Math.abs(across)<=2&&height>=-1&&height<=3;}
    private static boolean protectedAt(BlockPos p,List<BoundingBox> boxes){return boxes.stream().anyMatch(b->b.isInside(p));}
    public static int availableBody(BlockPos door,Direction direction,List<BoundingBox> boxes,int min,int max){
        int count=0;for(int t=0;t<=14;t++)for(int w=-4;w<=4;w++)for(int h=-2;h<=5;h++){
            BlockPos p=position(door,direction,t,w,h);if(p.getY()>min&&p.getY()<max-1&&body(t,w,h)&&!protectedAt(p,boxes))count++;
        }return count;
    }
    public Map<BlockPos,BlockState> plannedBlocks(){
        if(bodyVolume>0)return plannedBody();
        Map<BlockPos,BlockState> result=new LinkedHashMap<>();double[] weights=new double[rich.size()];
        for(int i=0;i<weights.length;i++)weights[i]=rich.get(i).getAsJsonObject().get("weight").getAsDouble();
        BlockState hostState=GeologyFeature.state(host),floorState=GeologyFeature.state(floor);
        for(int t=0;t<=14;t++)for(int w=-4;w<=4;w++)for(int h=-2;h<=5;h++){
            if(!body(t,w,h)&&!working(t,w,h))continue;
            BlockPos p=position(door,outward,t,w,h);if(!boundingBox.isInside(p)||protectedAt(p,protectedBoxes))continue;
            BlockState state=hostState;
            long cluster=seed(salt^mix(Math.floorDiv(h,2)),Math.floorDiv(t,2),Math.floorDiv(w,2),33);
            int selected=weighted(weights,unit(cluster+1));
            if(selected>=0&&unit(cluster)<richFraction)state=GeologyFeature.state(rich.get(selected).getAsJsonObject().get("block").getAsString());
            if(t<=4&&Math.abs(w)<=1&&h>=0&&h<=2)state=Blocks.CAVE_AIR.defaultBlockState();
            else if(t<=4&&Math.abs(w)<=1&&h==-1)state=floorState;
            result.put(p,state);
        }
        return Collections.unmodifiableMap(result);
    }
    private List<BlockPos> bodyPositions(){return GeologyMath.shape(salt,bodyVolume,coalSeam,attractors).stream().map(v->bodyCenter.offset(v.x(),v.y(),v.z())).toList();}
    private Map<BlockPos,BlockState> plannedBody(){
        if(bodyCache!=null)return bodyCache;
        var positions=bodyPositions().stream().filter(p->boundingBox.isInside(p)&&!protectedAt(p,protectedBoxes)).sorted(Comparator.comparingLong(p->mix(p.asLong()^salt))).toList();
        int target=quota(positions.size(),richFraction,salt,false);double[] weights=new double[rich.size()];for(int i=0;i<weights.length;i++)weights[i]=rich.get(i).getAsJsonObject().get("weight").getAsDouble();
        Map<BlockPos,BlockState> result=new LinkedHashMap<>();BlockState hostState=GeologyFeature.state(host);
        for(int i=0;i<positions.size();i++){BlockPos p=positions.get(i);int selected=i<target?weighted(weights,unit(p.asLong()^salt^71)):-1;result.put(p,selected<0?hostState:GeologyFeature.state(rich.get(selected).getAsJsonObject().get("block").getAsString()));}
        return bodyCache=Collections.unmodifiableMap(result);
    }
    @Override public void postProcess(WorldGenLevel level,StructureManager manager,ChunkGenerator generator,RandomSource random,BoundingBox clip,ChunkPos owner,BlockPos origin){
        if(level.getLevel().dimension()!=Level.OVERWORLD)return;
        Map<Long,GeologyPlanner.Site> placementSites=new HashMap<>();
        for(var entry:plannedBlocks().entrySet()){
            BlockPos p=entry.getKey();if(!clip.isInside(p)||(p.getX()>>4)!=owner.x||(p.getZ()>>4)!=owner.z)continue;
            BlockState current=level.getBlockState(p);
            if(bodyVolume>0&&!GeologyFeature.allowedPlacement(GeologyWorld.of(level.getLevel()),placementDefinition,p,placementSites))continue;
            if(bodyVolume>0&&!GeologyFeature.replaceable(current))continue;
            if(current.is(Blocks.BEDROCK)||current.is(Blocks.BARRIER)||current.hasBlockEntity())continue;
            level.setBlock(p,entry.getValue(),2);
        }
    }
}
