package dev.godpc.industrialcolonies.geology;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.*;
import net.minecraft.core.registries.*;
import net.minecraft.nbt.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.*;
import net.minecraft.world.item.ItemStack;
import com.simibubi.create.content.kinetics.drill.DrillBlockEntity;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.entity.*;
import net.minecraft.world.level.block.state.*;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.material.PushReaction;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.*;
import net.neoforged.neoforge.items.IItemHandler;
import net.neoforged.neoforge.capabilities.*;
import java.util.*;

/** World-generated geological access point. No item, crafting recipe or independent ore reserve. */
public final class MiningNodes {
    private static final DeferredRegister.Blocks BLOCKS=DeferredRegister.createBlocks("industrial_colonies");
    private static final DeferredRegister<BlockEntityType<?>> ENTITIES=DeferredRegister.create(Registries.BLOCK_ENTITY_TYPE,"industrial_colonies");
    public static final DeferredBlock<NodeBlock> NODE=BLOCKS.registerBlock("ore_extraction_node",NodeBlock::new,
        BlockBehaviour.Properties.ofFullCopy(Blocks.BEDROCK).noLootTable().pushReaction(PushReaction.BLOCK));
    public static final DeferredHolder<BlockEntityType<?>,BlockEntityType<NodeEntity>> TYPE=ENTITIES.register("ore_extraction_node",()->BlockEntityType.Builder.of(NodeEntity::new,NODE.get()).build(null));
    public static final EnumProperty<NodeAppearance> APPEARANCE=EnumProperty.create("appearance",NodeAppearance.class);
    private MiningNodes(){}
    public static void register(IEventBus bus){BLOCKS.register(bus);ENTITIES.register(bus);bus.addListener(MiningNodes::capabilities);}
    private static void capabilities(RegisterCapabilitiesEvent event){event.registerBlockEntity(Capabilities.ItemHandler.BLOCK,TYPE.get(),(node,side)->node.output);}
    /** Structure access points retain their legacy air-only placement rule. */
    public static void place(WorldGenLevel level,BlockPos pos,MiningScanScope scope){place(level,pos,scope,false);}
    /** A finite vein access point sits immediately above its reserved body, never replacing owned ore. */
    public static BlockPos independentAnchor(MiningScanScope scope){
        if(!scope.isContinent()||scope.family().equals("cinnabar"))throw new IllegalArgumentException("Finite underground vein required");
        var c=scope.reservedCandidate();return new BlockPos(c.x(),Math.addExact(scope.bounds().maxY(),1),c.z());
    }
    public static void placeIndependent(WorldGenLevel level,net.minecraft.world.level.chunk.ChunkAccess owner,MiningScanScope scope,Set<BlockPos> reserved){
        var pos=independentAnchor(scope);
        if(!new ChunkPos(pos).equals(owner.getPos())||pos.getY()<scope.minBuildY()||pos.getY()>=scope.maxBuildYExclusive()||reserved.contains(pos))return;
        place(level,pos,scope,true);
    }
    private static void place(WorldGenLevel level,BlockPos pos,MiningScanScope scope,boolean naturalStone){
        var blocks=new LinkedHashSet<Block>();
        var definition=GeologyConfig.array(GeologyConfig.get().deposits(),"deposits").asList().stream()
            .map(e->e.getAsJsonObject()).filter(d->d.get("id").getAsString().equals(scope.family())).findFirst().orElseThrow();
        add(blocks,definition.get("hostRock").getAsString());
        for(String field:new String[]{"richOres","associated"})for(var e:GeologyConfig.array(definition,field))add(blocks,e.getAsJsonObject().get("block").getAsString());
        var state=level.getBlockState(pos);
        if(state.is(NODE.get())){
            if(level.getBlockEntity(pos) instanceof NodeEntity existing&&existing.scope()==null)existing.bind(scope,blocks);
            return;
        }
        // Do not overwrite water, containers or another structure's solid blocks.
        if(!level.getFluidState(pos).isEmpty()||state.hasBlockEntity())return;
        if(!state.isAir()&&!(naturalStone&&(state.is(net.minecraft.tags.BlockTags.BASE_STONE_OVERWORLD)
            ||state.is(net.minecraft.tags.BlockTags.STONE_ORE_REPLACEABLES)||state.is(net.minecraft.tags.BlockTags.DEEPSLATE_ORE_REPLACEABLES))))return;
        if(level.setBlock(pos,NODE.get().defaultBlockState().setValue(APPEARANCE,NodeAppearance.forFamily(scope.family())),2)&&level.getBlockEntity(pos) instanceof NodeEntity node)node.bind(scope,blocks);
    }
    private static void add(Set<Block> blocks,String id){
        var key=ResourceLocation.parse(id);if(!BuiltInRegistries.BLOCK.containsKey(key))throw new IllegalArgumentException("Missing node ore "+id);
        var block=BuiltInRegistries.BLOCK.get(key);if(block==Blocks.AIR)throw new IllegalArgumentException("Empty node ore");blocks.add(block);
    }
    public static final class NodeBlock extends BaseEntityBlock {
        private static final MapCodec<NodeBlock> CODEC=simpleCodec(NodeBlock::new);
        public NodeBlock(Properties properties){super(properties);registerDefaultState(stateDefinition.any().setValue(APPEARANCE,NodeAppearance.GENERIC));}
        @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block,BlockState> builder){builder.add(APPEARANCE);}
        @Override protected MapCodec<? extends BaseEntityBlock> codec(){return CODEC;}
        @Override public BlockEntity newBlockEntity(BlockPos pos,BlockState state){return new NodeEntity(pos,state);}
        @Override protected RenderShape getRenderShape(BlockState state){return RenderShape.MODEL;}
        @Override public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level,BlockState state,BlockEntityType<T> type){
            return level.isClientSide?null:createTickerHelper(type,TYPE.get(),NodeEntity::tick);
        }
    }
    public static final class NodeEntity extends BlockEntity {
        private MiningScanScope scope;
        private MiningNodeSurvey.Session materialSurvey;
        private long materialSurveyRetryAt;
        private final Map<java.util.UUID,Long> yieldRequests=new HashMap<>();
        public void requestYield(net.minecraft.server.level.ServerPlayer player){
            if(!(level instanceof ServerLevel server)||player.serverLevel()!=server||player.distanceToSqr(worldPosition.getCenter())>64)return;
            var result=inspectMaterials();
            if(result.complete()){sendYield(player,result);return;}
            if(yieldRequests.size()<8||yieldRequests.containsKey(player.getUUID()))yieldRequests.put(player.getUUID(),server.getGameTime()+200);
            player.displayClientMessage(net.minecraft.network.chat.Component.literal("Not fully counted"),true);
        }
        private void sendYield(net.minecraft.server.level.ServerPlayer player,MiningNodeSurvey.Result result){
            var estimate=NodeYieldCalculator.estimate((ServerLevel)level,scope.family(),result);
            player.displayClientMessage(net.minecraft.network.chat.Component.literal(estimate.map(NodeYieldCalculator.Range::display).orElse("Yield not known")),true);
        }
        private void finishYieldRequests(ServerLevel server){
            if(yieldRequests.isEmpty())return;
            var result=materialSurvey==null?null:materialSurvey.result();
            var iterator=yieldRequests.entrySet().iterator();
            while(iterator.hasNext()){
                var request=iterator.next();var player=server.getServer().getPlayerList().getPlayer(request.getKey());
                if(player==null||player.serverLevel()!=server||player.distanceToSqr(worldPosition.getCenter())>64||server.getGameTime()>request.getValue()){iterator.remove();continue;}
                if(result!=null&&result.complete()){sendYield(player,result);iterator.remove();}
            }
        }
        private BlockPos anchor;
        private Set<Block> ores=Set.of();
        private static final TicketType<BlockPos> ACCESS=TicketType.create("industrial_mining",Comparator.comparingLong(BlockPos::asLong),40);
        // Advisory traversal resets on reload. Only remote chunk-local progress is authoritative.
        private long chunkIndex;
        private ChunkPos leased;
        private float workCredit;
        private String status="Unbound";
        private final IItemHandler output=new IItemHandler(){
            private void slot(int slot){if(slot<0||slot>=64)throw new IndexOutOfBoundsException(slot);}
            public int getSlots(){return 64;}
            public ItemStack getStackInSlot(int slot){slot(slot);var access=access();return access==null?ItemStack.EMPTY:access.getStackInSlot(slot);}
            public ItemStack insertItem(int slot,ItemStack stack,boolean simulate){slot(slot);return stack.copy();}
            public ItemStack extractItem(int slot,int amount,boolean simulate){slot(slot);var access=access();return access==null?ItemStack.EMPTY:access.extractItem(slot,amount,simulate);}
            public int getSlotLimit(int slot){slot(slot);return 64;}
            public boolean isItemValid(int slot,ItemStack stack){slot(slot);return false;}
        };
        public NodeEntity(BlockPos pos,BlockState state){super(TYPE.get(),pos,state);}
        public MiningScanScope scope(){return scope;}
        /** Exact physical material breakdown only when every owner chunk is loaded, sealed and unchanged. */
        public MiningNodeSurvey.Result inspectMaterials(){
            if(!bound()||!(level instanceof ServerLevel server)||!scope.isContinent())return new MiningNodeSurvey.Result(false,Map.of(),"Not fully counted");
            if(materialSurvey==null||materialSurvey.finished()&&!materialSurvey.valid()&&server.getGameTime()>=materialSurveyRetryAt){
                materialSurvey=new MiningNodeSurvey.Session(server,scope,ores);materialSurveyRetryAt=server.getGameTime()+100;
            }
            return materialSurvey.result();
        }

        public Set<Block> ores(){return ores;}
        public String status(){return status;}
        public ChunkPos leasedChunk(){return leased;}
        private ChunkPos target(){
            var b=scope.bounds();long width=(long)Math.floorDiv(b.maxX(),16)-Math.floorDiv(b.minX(),16)+1;
            long depth=(long)Math.floorDiv(b.maxZ(),16)-Math.floorDiv(b.minZ(),16)+1;
            long firstX=Math.max(0,Math.min(width-1,(long)(anchor.getX()>>4)-Math.floorDiv(b.minX(),16)));
            long firstZ=Math.max(0,Math.min(depth-1,(long)(anchor.getZ()>>4)-Math.floorDiv(b.minZ(),16)));
            long index=(firstZ*width+firstX+chunkIndex)%(width*depth);
            return chunkIndex>=width*depth?null:new ChunkPos(Math.toIntExact(Math.floorDiv(b.minX(),16)+index%width),Math.toIntExact(Math.floorDiv(b.minZ(),16)+index/width));
        }
        private MiningOutputAccess access(){
            if(isRemoved()||!bound()||!(level instanceof ServerLevel server))return null;
            var target=target();return target==null?null:new MiningOutputAccess(server,scope,target);
        }
        private void release(){if(leased!=null&&level instanceof ServerLevel server)server.getChunkSource().removeRegionTicket(ACCESS,leased,0,worldPosition);leased=null;}
        @Override public void setRemoved(){release();super.setRemoved();}
        public static void tick(Level level,BlockPos pos,BlockState state,NodeEntity node){
            if(!(level instanceof ServerLevel server))return;
            if(node.bound()){
                var appearance=NodeAppearance.forFamily(node.scope.family());
                if(state.getValue(APPEARANCE)!=appearance)server.setBlock(pos,state.setValue(APPEARANCE,appearance),2);
            }
            if(node.materialSurvey!=null&&node.bound())node.materialSurvey.tick(4096);
            node.finishYieldRequests(server);
            if(!node.bound()){node.status="Unbound";node.workCredit=0;node.release();return;}
            BlockPos drillPos=null;
            for(var direction:Direction.values()){var candidate=pos.relative(direction);if(MiningDrillWork.inspect(server,pos,candidate)==MiningDrillWork.Status.WORK){drillPos=candidate;break;}}
            if(drillPos==null){node.status="No powered drill";node.workCredit=0;node.release();return;}
            var target=node.target();if(target==null){node.status="Exhausted";node.release();return;}
            if(!target.equals(node.leased)){node.release();node.leased=target;}
            server.getChunkSource().addRegionTicket(ACCESS,target,0,pos);
            if(server.getChunkSource().getChunkNow(target.x,target.z)==null){node.status="Loading ore chunk";return;}
            var drill=(DrillBlockEntity)server.getBlockEntity(drillPos);node.workCredit+=Math.min(Math.abs(drill.getSpeed()),256)/64f;
            if(node.workCredit<20)return;node.workCredit=0;
            var result=MiningDrillWork.step(server,pos,drillPos,node.scope,target,512,node.ores);
            if(result.work()==null){node.status="Waiting for drill";return;}
            node.status=result.work().status().name();
            if(result.work().status()==MiningChunkWork.Status.COMPLETE){node.chunkIndex++;node.release();}
        }
        public boolean bound(){return scope!=null&&worldPosition.equals(anchor)&&level!=null
            &&scope.dimension().equals(level.dimension().location().toString())&&scope.minBuildY()==level.getMinBuildHeight()&&scope.maxBuildYExclusive()==level.getMaxBuildHeight();}
        void bind(MiningScanScope value,Set<Block> palette){
            if(palette.isEmpty()||palette.size()>128)throw new IllegalArgumentException("Invalid node palette");
            if(scope!=null){if(!scope.equals(value)||!ores.equals(palette)||!worldPosition.equals(anchor))throw new IllegalStateException("Cannot rebind mining node");return;}
            scope=value;anchor=worldPosition.immutable();ores=Set.copyOf(palette);setChanged();
        }
        @Override protected void saveAdditional(CompoundTag tag,HolderLookup.Provider registries){
            super.saveAdditional(tag,registries);if(scope==null)return;
            var s=MiningScopeTags.save(scope);s.putInt("Version",scope.isContinent()?2:1);
            s.putLong("Anchor",anchor.asLong());var list=new ListTag();ores.stream().map(BuiltInRegistries.BLOCK::getKey).map(Object::toString).sorted().forEach(id->list.add(StringTag.valueOf(id)));s.put("Ores",list);tag.put("Mine",s);
        }
        @Override protected void loadAdditional(CompoundTag tag,HolderLookup.Provider registries){
            super.loadAdditional(tag,registries);release();yieldRequests.clear();materialSurvey=null;materialSurveyRetryAt=0;scope=null;anchor=null;ores=Set.of();chunkIndex=0;workCredit=0;status="Unbound";if(!tag.contains("Mine",Tag.TAG_COMPOUND))return;
            var s=tag.getCompound("Mine");int version=s.getInt("Version");if((version!=1&&version!=2)||!s.contains("Anchor",Tag.TAG_LONG))throw new IllegalArgumentException("Invalid mining node version/anchor");
            if(version==2&&s.getInt("ScopeVersion")!=2||version==1&&s.contains("ScopeVersion"))throw new IllegalArgumentException("Mining node/scope versions disagree");
            var list=s.getList("Ores",Tag.TAG_STRING);if(list.isEmpty()||list.size()>128)throw new IllegalArgumentException("Invalid saved node palette");
            var palette=new LinkedHashSet<Block>();for(int i=0;i<list.size();i++)add(palette,list.getString(i));
            scope=MiningScopeTags.load(s);
            anchor=BlockPos.of(s.getLong("Anchor"));ores=Set.copyOf(palette);
        }
    }
}
