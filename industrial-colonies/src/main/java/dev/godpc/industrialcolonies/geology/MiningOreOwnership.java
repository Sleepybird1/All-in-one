package dev.godpc.industrialcolonies.geology;

import net.minecraft.core.*;
import net.minecraft.nbt.ByteArrayTag;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.*;
import net.minecraft.world.level.chunk.*;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.attachment.*;
import net.neoforged.neoforge.registries.*;
import java.io.*;
import java.util.List;

/** Provenance travels with the same native chunk as its blocks; missing history never certifies ore. */
public final class MiningOreOwnership {
    private static final DeferredRegister<AttachmentType<?>> TYPES=DeferredRegister.create(NeoForgeRegistries.Keys.ATTACHMENT_TYPES,"industrial_colonies");
    public static final DeferredHolder<AttachmentType<?>,AttachmentType<MiningOreLedger>> LEDGER=TYPES.register("natural_ore_ledger",()->
        AttachmentType.builder(holder->{var ledger=fresh(chunk(holder));ledger.seal();return ledger;})
        .serialize(new IAttachmentSerializer<ByteArrayTag,MiningOreLedger>() {
            public MiningOreLedger read(IAttachmentHolder holder,ByteArrayTag tag,HolderLookup.Provider provider){
                var c=chunk(holder);
                try{return MiningOreLedger.decode(tag.getAsByteArray(),c.getPos().x,c.getPos().z,c.getMinBuildHeight(),c.getMaxBuildHeight());}
                catch(IOException e){throw new IllegalStateException("Invalid natural ore provenance",e);}
            }
            public ByteArrayTag write(MiningOreLedger ledger,HolderLookup.Provider provider){
                try{return new ByteArrayTag(ledger.encode());}catch(IOException e){throw new IllegalStateException(e);}
            }
        }).build());
    private MiningOreOwnership(){}
    public static final DeferredHolder<AttachmentType<?>,AttachmentType<MiningChunkProgress>> PROGRESS=TYPES.register("mining_chunk_progress",()->
        AttachmentType.builder(MiningChunkProgress::new).serialize(new IAttachmentSerializer<CompoundTag,MiningChunkProgress>(){
            public MiningChunkProgress read(IAttachmentHolder holder,CompoundTag tag,HolderLookup.Provider registries){return MiningChunkProgress.load(chunk(holder),tag);}
            public CompoundTag write(MiningChunkProgress progress,HolderLookup.Provider registries){return progress.save();}
        }).build());
    public static final DeferredHolder<AttachmentType<?>,AttachmentType<MiningHarvestBuffer>> OUTPUT=TYPES.register("mining_retained_output",()->
        AttachmentType.builder(MiningHarvestBuffer::new).serialize(new IAttachmentSerializer<CompoundTag,MiningHarvestBuffer>(){
            public MiningHarvestBuffer read(IAttachmentHolder holder,CompoundTag tag,HolderLookup.Provider registries){return MiningHarvestBuffer.load(chunk(holder),tag,registries);}
            public CompoundTag write(MiningHarvestBuffer buffer,HolderLookup.Provider registries){return buffer.save(registries);}
        }).build());
    private static ChunkAccess chunk(IAttachmentHolder holder){if(holder instanceof ChunkAccess c)return c;throw new IllegalArgumentException("Ore provenance is chunk-only");}
    private static MiningOreLedger fresh(ChunkAccess c){return new MiningOreLedger(c.getPos().x,c.getPos().z,c.getMinBuildHeight(),c.getMaxBuildHeight());}
    public static void register(IEventBus bus){TYPES.register(bus);}
    /** Only the native CARVERS hook may open a previously untracked proto chunk. */
    public static boolean begin(ChunkAccess chunk){
        if(!(chunk instanceof ProtoChunk)||chunk instanceof ImposterProtoChunk||chunk.hasData(LEDGER))return false;
        chunk.setData(LEDGER,fresh(chunk));chunk.setUnsaved(true);return true;
    }
    public static void seal(ChunkAccess chunk){if(chunk.hasData(LEDGER)){chunk.getData(LEDGER).seal();chunk.setUnsaved(true);}}
    /** Failed generation retains diagnostic claims but must hold, never report an empty deposit. */
    public static void abort(ChunkAccess chunk){
        if(!chunk.hasData(LEDGER))throw new IllegalStateException("No generation provenance to abort");
        chunk.getData(LEDGER).abort();chunk.setUnsaved(true);
    }
    public static void record(WorldGenLevel level,ChunkPos pos,GeologyPlanner.Plan plan,List<BlockPos> actual){
        var c=level.getChunk(pos.x,pos.z);
        if(!c.hasData(LEDGER)||c.getData(LEDGER).sealed())return;
        var scope=new MiningScanScope(level.getLevel().dimension().location().toString(),plan.id(),plan.candidate().regionX(),plan.candidate().regionZ(),
                MassiveDeposits.body(plan,MassiveDeposits.settings(GeologyConfig.get())),c.getMinBuildHeight(),c.getMaxBuildHeight());
        String key=scope.key();var ledger=c.getData(LEDGER);
        for(var p:actual)ledger.recordGenerated(key,p.getX(),p.getY(),p.getZ());c.setUnsaved(true);
    }
    public static void changed(ChunkAccess chunk,BlockPos pos,BlockState state){
        if(chunk.hasData(LEDGER)&&chunk.getData(LEDGER).invalidate(pos.getX(),pos.getY(),pos.getZ()))chunk.setUnsaved(true);
        if(chunk.hasData(OUTPUT)){chunk.getData(OUTPUT).sourceChanged(pos,state.isAir(),MiningPhysicalHarvest.activeOperation());chunk.setUnsaved(true);}
    }
    /** Continent writer supplies only final successful placements, never the geometric reserve. */
    public static void recordContinent(ChunkAccess chunk,ContinentOccurrenceLedger.Request request,List<BlockPos> actual){
        if(!chunk.hasData(LEDGER)||chunk.getData(LEDGER).sealed())throw new IllegalStateException("Open native owner provenance required");
        var cells=actual.stream().map(p->new MiningOreLedger.Cell(p.getX(),p.getY(),p.getZ())).toList();
        chunk.getData(LEDGER).recordGeneratedBatch(ContinentOreProvenance.key(request),cells);chunk.setUnsaved(true);
    }
    public static boolean owns(ChunkAccess chunk,MiningScanScope scope,BlockPos pos){
        return chunk.hasData(LEDGER)&&chunk.getData(LEDGER).owns(scope.key(),pos.getX(),pos.getY(),pos.getZ());
    }
    public static void recordCoal(ChunkAccess chunk,CoalMiningReservation reservation,List<BlockPos> actual){
        if(!chunk.hasData(LEDGER)||chunk.getData(LEDGER).sealed()||chunk.getData(LEDGER).failed())throw new IllegalStateException("Open native owner provenance required");
        var scope=MiningScanScope.coal(reservation,chunk.getMinBuildHeight(),chunk.getMaxBuildHeight());
        if(actual.stream().anyMatch(p->!scope.contains(p.getX(),p.getY(),p.getZ())))throw new IllegalArgumentException("Coal write outside saved seam");
        var cells=actual.stream().map(p->new MiningOreLedger.Cell(p.getX(),p.getY(),p.getZ())).toList();
        chunk.getData(LEDGER).recordGeneratedBatch(reservation.key(),cells);chunk.setUnsaved(true);
    }
}
