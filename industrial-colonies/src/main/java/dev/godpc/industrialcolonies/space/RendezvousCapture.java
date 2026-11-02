package dev.godpc.industrialcolonies.space;

import dev.ryanhcode.sable.Sable;
import dev.devce.rocketnautics.content.blocks.RCSThrusterBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.LeverBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import java.util.*;

/** One-shot capture output through two explicitly bound existing physical levers.
 * No blocks are created and no connector fields, constraints or inventories are
 * changed directly. Success leaves normal levers on so an established physical
 * dock remains latched across navigation shutdown/restart. Manual lever control
 * remains available; this is not an automatic restart of navigation.
 */
public final class RendezvousCapture {
    public record Result(boolean activated,String reason){}
    private RendezvousCapture(){}
    public static Result activate(RendezvousApproach approach,BlockPos shipLever,BlockPos targetLever){
        if(approach==null||shipLever==null||targetLever==null)return new Result(false,"INVALID_BINDING");
        var admission=approach.claimCapture();if(admission.isEmpty())return new Result(false,"NO_FRESH_ADMISSION");
        var ticket=admission.get();var endpoints=List.of(ticket.ship(),ticket.target());
        var positions=List.of(shipLever.immutable(),targetLever.immutable());
        ServerLevel level=ticket.ship().body().getLevel();
        if(positions.get(0).equals(positions.get(1)))return new Result(false,"DUPLICATE_OUTPUT");
        var before=new ArrayList<BlockState>();
        for(int i=0;i<2;i++){
            var endpoint=endpoints.get(i);var position=positions.get(i);
            if(endpoint.body().isRemoved()||endpoint.body().getLevel()!=level||SpaceflightAuthorization.automationDisabled(endpoint.body())
                    ||!level.hasChunkAt(position)||!level.hasChunkAt(endpoint.port())||Sable.HELPER.getContaining(level,position)!=endpoint.body()
                    ||Sable.HELPER.getContaining(level,endpoint.port())!=endpoint.body())return new Result(false,"BINDING_UNAVAILABLE");
            var state=level.getBlockState(position);var port=level.getBlockState(endpoint.port());
            if(!(state.getBlock() instanceof LeverBlock)||state.getValue(LeverBlock.POWERED)
                    ||!BuiltInRegistries.BLOCK.getKey(port.getBlock()).toString().equals("simulated:docking_connector")
                    ||!port.hasProperty(BlockStateProperties.FACING)||port.getValue(BlockStateProperties.FACING)!=endpoint.outward()
                    ||level.hasNeighborSignal(endpoint.port()))return new Result(false,"MANUAL_POWER_OR_WRONG_HARDWARE");
            before.add(state);
        }
        int applied=0;
        try{
            var rcsSignals=new IdentityHashMap<RCSThrusterBlockEntity,Integer>();
            for(var endpoint:endpoints)for(var holder:endpoint.body().getPlot().getLoadedChunks())
                for(var blockEntity:holder.getChunk().getBlockEntities().values())
                    if(blockEntity instanceof RCSThrusterBlockEntity engine&&Sable.HELPER.getContaining(engine)==endpoint.body())
                        rcsSignals.put(engine,level.getBestNeighborSignal(engine.getBlockPos()));
            for(int i=0;i<2;i++){
                if(level.getBlockState(positions.get(i))!=before.get(i))throw new IllegalStateException("OUTPUT_CHANGED");
                applied=i+1;((LeverBlock)before.get(i).getBlock()).pull(before.get(i),level,positions.get(i),null);
                if(!level.getBlockState(positions.get(i)).getValue(LeverBlock.POWERED))throw new IllegalStateException("OUTPUT_NOT_POWERED");
            }
            for(var endpoint:endpoints)if(!level.hasNeighborSignal(endpoint.port()))throw new IllegalStateException("OUTPUT_NOT_WIRED_TO_PORT");
            for(var entry:rcsSignals.entrySet()){
                var engine=entry.getKey();
                if(engine.isRemoved()||level.getBlockEntity(engine.getBlockPos())!=engine
                        ||level.getBestNeighborSignal(engine.getBlockPos())!=entry.getValue())
                    throw new IllegalStateException("RCS_INTERFERENCE");
            }
            return new Result(true,"PHYSICAL_CAPTURE_POWER_ON");
        }catch(RuntimeException failure){
            boolean restored=true;
            for(int i=applied-1;i>=0;i--)try{
                var expected=before.get(i).setValue(LeverBlock.POWERED,true);
                if(level.getBlockState(positions.get(i))==expected)((LeverBlock)expected.getBlock()).pull(expected,level,positions.get(i),null);
                else if(level.getBlockState(positions.get(i))!=before.get(i))restored=false;
            }catch(RuntimeException rollback){restored=false;}
            return new Result(false,restored?("RCS_INTERFERENCE".equals(failure.getMessage())
                    ?"CAPTURE_RCS_INTERFERENCE_ROLLED_BACK":"CAPTURE_OUTPUT_FAILED_ROLLED_BACK")
                    :"CAPTURE_OUTPUT_FAILED_CHECK_LEVERS");
        }
    }
}
