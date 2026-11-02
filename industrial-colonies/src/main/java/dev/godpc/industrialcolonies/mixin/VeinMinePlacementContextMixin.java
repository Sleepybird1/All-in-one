package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.wrapmethod.WrapMethod;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import dev.godpc.industrialcolonies.geology.*;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.*;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.structures.MineshaftStructure;
import org.spongepowered.asm.mixin.*;
import java.util.List;

@Mixin(StructureStart.class)
public abstract class VeinMinePlacementContextMixin {
    @Shadow public abstract List<StructurePiece> getPieces();
    @Shadow public abstract Structure getStructure();
    @WrapMethod(method="placeInChunk")
    private void industrialColonies$linkedMineFrame(WorldGenLevel level,StructureManager manager,ChunkGenerator generator,
            RandomSource random,BoundingBox box,ChunkPos chunk,Operation<Void> original) {
        var markers=getPieces().stream().filter(p->p instanceof MassiveMinePiece).map(p->(MassiveMinePiece)p).toList();
        boolean linked=getStructure() instanceof MineshaftStructure&&markers.size()==1
                &&markers.getFirst().extractionScope(level.getLevel()).isContinent();
        VeinMinePlacement.during(linked,()->original.call(level,manager,generator,random,box,chunk));
    }
}
