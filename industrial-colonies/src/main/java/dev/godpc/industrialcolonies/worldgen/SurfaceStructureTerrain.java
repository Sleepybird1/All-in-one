package dev.godpc.industrialcolonies.worldgen;

import java.util.HashMap;
import java.util.Map;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.LevelHeightAccessor;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.GenerationStep;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.levelgen.structure.*;

/** Reject complete surface starts before any piece or terrain adaptation is placed. */
public final class SurfaceStructureTerrain {
    public static final TagKey<Structure> EXEMPT=TagKey.create(Registries.STRUCTURE,
            ResourceLocation.parse("industrial_colonies:terrain_fitting_exempt"));
    public static final int MAX_HEIGHT_RANGE=6;
    public static final TagKey<Structure> SUMMIT_ONLY=TagKey.create(Registries.STRUCTURE,
            ResourceLocation.parse("industrial_colonies:summit_only"));
    public record Ground(int y,boolean wet) {}
    @FunctionalInterface public interface GroundReader { Ground read(int x,int z); }

    public static boolean fits(BoundingBox box,GroundReader reader) {
        int loX=box.minX()-1,hiX=box.maxX()+1,loZ=box.minZ()-1,hiZ=box.maxZ()+1;
        Map<Long,Ground> cache=new HashMap<>();
        GroundReader cached=(x,z)->cache.computeIfAbsent(((long)x<<32)^(z&0xffffffffL),k->reader.read(x,z));
        int[] range={Integer.MAX_VALUE,Integer.MIN_VALUE};
        // Reject unsuitable large sites cheaply, then check EVERY column. A
        // center/corner-only test misses narrow rivers between village pieces.
        for(int z=loZ;z<=hiZ;z+=16)for(int x=loX;x<=hiX;x+=16)
            if(!accept(cached.read(x,z),range))return false;
        for(int z=loZ;z<=hiZ;z++)for(int x=loX;x<=hiX;x++) {
            Ground ground=cached.read(x,z);
            if(!accept(ground,range))return false;
            if(x>loX&&Math.abs(ground.y()-cached.read(x-1,z).y())>2)return false;
            if(z>loZ&&Math.abs(ground.y()-cached.read(x,z-1).y())>2)return false;
        }
        return true;
    }
    private static boolean accept(Ground ground,int[] range) {
        if(ground.wet())return false;
        range[0]=Math.min(range[0],ground.y());range[1]=Math.max(range[1],ground.y());
        return range[1]-range[0]<=MAX_HEIGHT_RANGE;
    }
    public static Ground ground(ChunkGenerator generator,RandomState random,LevelHeightAccessor height,int x,int z) {
        var column=generator.getBaseColumn(x,z,height,random);
        for(int y=height.getMaxBuildHeight()-1;y>=height.getMinBuildHeight();y--) {
            var state=column.getBlock(y);
            if(!state.isAir())return new Ground(y,!state.getFluidState().isEmpty());
        }
        return new Ground(height.getMinBuildHeight(),true);
    }
    public static boolean shouldCheck(Structure structure,net.minecraft.core.RegistryAccess access) {
        var registry=access.registryOrThrow(Registries.STRUCTURE);
        var key=registry.getResourceKey(structure);
        // These bunkers have surface-projected entrances despite their declared
        // underground generation step. Their entire site still needs support.
        boolean surfaceEntrance=key.isPresent()&&java.util.Set.of("stellaris:earth_operation_base",
                "stellaris:mercury_lava_mines").contains(key.get().location().toString());
        if(structure.step()!=GenerationStep.Decoration.SURFACE_STRUCTURES&&!surfaceEntrance)return false;
        return key.isPresent()&&!registry.getHolderOrThrow(key.get()).is(EXEMPT);
    }
    public static boolean fits(StructureStart start,ChunkGenerator generator,RandomState random,LevelHeightAccessor height) {
        // getBoundingBox includes the beard/terrain adaptation margin. Check the
        // actual pieces plus one block instead, without changing their positions.
        var boxes=start.getPieces().stream().map(StructurePiece::getBoundingBox).toList();
        var box=BoundingBox.encapsulatingBoxes(boxes).orElseThrow();
        return fits(box,(x,z)->ground(generator,random,height,x,z));
    }
    public static boolean summit(BoundingBox box,GroundReader reader,int seaLevel) {
        int x=box.getCenter().getX(),z=box.getCenter().getZ();
        Ground center=reader.read(x,z);
        if(center.wet()||center.y()<seaLevel+160)return false;
        // A broad, supported summit must fall away in every direction. Reject
        // shoulders on a higher mountain and high but otherwise flat plains.
        int radius=Math.max(box.getXSpan(),box.getZSpan())/2+32;
        for(int dz=-1;dz<=1;dz++)for(int dx=-1;dx<=1;dx++) {
            if(dx==0&&dz==0)continue;
            if(reader.read(x+dx*radius,z+dz*radius).y()>center.y()+6)return false;
            if(reader.read(x+dx*(radius+64),z+dz*(radius+64)).y()>center.y()-12)return false;
        }
        return true;
    }
    public static boolean summitFits(StructureStart start,net.minecraft.core.RegistryAccess access,
            ChunkGenerator generator,RandomState random,LevelHeightAccessor height) {
        var registry=access.registryOrThrow(Registries.STRUCTURE);
        var key=registry.getResourceKey(start.getStructure()).orElseThrow();
        if(!registry.getHolderOrThrow(key).is(SUMMIT_ONLY))return true;
        var box=BoundingBox.encapsulatingBoxes(start.getPieces().stream().map(StructurePiece::getBoundingBox).toList()).orElseThrow();
        return summit(box,(x,z)->ground(generator,random,height,x,z),generator.getSeaLevel());
    }
}
