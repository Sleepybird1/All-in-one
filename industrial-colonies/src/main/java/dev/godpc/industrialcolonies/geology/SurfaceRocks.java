package dev.godpc.industrialcolonies.geology;

import com.mojang.serialization.MapCodec;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.*;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.*;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.*;

/** Small ground models that hand-collect into existing processing feeds. No new ore cubes or recipes. */
public final class SurfaceRocks {
    public static final List<String> MATERIALS=List.of("hematite","magnetite","chalcopyrite","sphalerite","galena","pentlandite",
            "bauxite","spodumene_rock","argentite","wolframite_rock","dolomite","graphite_rock","phosphate_rock",
            "ultramafic_rock","ilmenite","bertrandite","borax_rock","cassiterite","chromite","cinnabar","coal");
    private static final DeferredRegister.Blocks BLOCKS=DeferredRegister.createBlocks("industrial_colonies");
    private static final DeferredRegister.Items ITEMS=DeferredRegister.createItems("industrial_colonies");
    private static final Map<String,DeferredBlock<? extends Block>> ROCKS=new LinkedHashMap<>();
    static {
        for(String material:MATERIALS){
            var block=BLOCKS.registerBlock("loose_"+material,GroundRock::new,
                    BlockBehaviour.Properties.of().instabreak().noCollission().noOcclusion().sound(SoundType.STONE));
            ROCKS.put(material,block);ITEMS.registerSimpleBlockItem("loose_"+material,block);
        }
    }
    private SurfaceRocks() {}
    public static void register(IEventBus bus){BLOCKS.register(bus);ITEMS.register(bus);}
    public static Block block(String material){return ROCKS.get(material).get();}
    public static String materialForHost(String host){
        if(host.equals("minecraft:coal_ore"))return "coal";
        if(!host.startsWith("industrial_colonies:"))return null;
        String material=host.substring("industrial_colonies:".length());return MATERIALS.contains(material)?material:null;
    }
    public static ItemStack pickup(Block block){
        for(var entry:ROCKS.entrySet())if(entry.getValue().get()==block){
            String material=entry.getKey();return new ItemStack(material.equals("coal")?Items.COAL:GeologyBlocks.block(material).asItem());
        }
        throw new IllegalArgumentException("Unknown surface rock");
    }
    public static final class GroundRock extends Block {
        private static final MapCodec<GroundRock> CODEC=simpleCodec(GroundRock::new);
        private static final VoxelShape SHAPE=Shapes.or(Block.box(4,0,5,11,3,12),Block.box(8,0,3,13,2,8));
        public GroundRock(BlockBehaviour.Properties properties){super(properties);}
        @Override public MapCodec<? extends Block> codec(){return CODEC;}
        @Override protected VoxelShape getShape(BlockState s,BlockGetter level,BlockPos p,CollisionContext context){return SHAPE;}
        @Override protected boolean canSurvive(BlockState s,LevelReader level,BlockPos p){return level.getBlockState(p.below()).isFaceSturdy(level,p.below(),Direction.UP)&&level.getFluidState(p).isEmpty();}
        @Override protected BlockState updateShape(BlockState s,Direction d,BlockState neighbor,LevelAccessor level,BlockPos p,BlockPos np){
            return s.canSurvive(level,p)?super.updateShape(s,d,neighbor,level,p,np):Blocks.AIR.defaultBlockState();
        }
        @Override protected InteractionResult useWithoutItem(BlockState s,Level level,BlockPos p,Player player,BlockHitResult hit){
            if(!player.mayBuild())return InteractionResult.PASS;
            if(!level.isClientSide&&level.removeBlock(p,false)){
                ItemStack stack=pickup(this);if(!player.getInventory().add(stack))player.drop(stack,false);
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }
        @Override public void appendHoverText(ItemStack stack,Item.TooltipContext context,List<Component> lines,TooltipFlag flag){
            lines.add(Component.translatable("tooltip.industrial_colonies.surface_rock"));
        }
    }
}
