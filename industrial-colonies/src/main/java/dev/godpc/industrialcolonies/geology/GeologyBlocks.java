package dev.godpc.industrialcolonies.geology;

import com.mojang.serialization.MapCodec;
import dev.godpc.industrialcolonies.IndustrialColonies;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.SimpleWaterloggedBlock;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.level.material.Fluids;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * The approved geological roster, without finished-material recipes or tool progression.
 * Textures are byte-for-byte exports from the approved V27 Blockbench project.
 * Potential material amounts belong to geology data, never to an ore-equals-ingot rule.
 */
public final class GeologyBlocks {
    private static final DeferredRegister.Blocks BLOCKS =
            DeferredRegister.createBlocks(IndustrialColonies.MOD_ID);
    private static final DeferredRegister.Items ITEMS =
            DeferredRegister.createItems(IndustrialColonies.MOD_ID);
    private static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, IndustrialColonies.MOD_ID);
    private static final Map<String, DeferredBlock<Block>> GEOLOGY_BLOCKS = new LinkedHashMap<>();
    private static final Map<String, DeferredItem<BlockItem>> GEOLOGY_ITEMS = new LinkedHashMap<>();

    /** Stable approved display order; no duplicate Coal block or discarded dark-Lead host. */
    public static final List<String> APPROVED_IDS = List.of(
            "sphalerite", "rich_sphalerite", "rich_copper_ore", "chalcopyrite",
            "hematite", "magnetite", "bauxite", "cinnabar", "spodumene_rock", "spodumene_ore",
            "argentite", "rich_silver_ore", "wolframite_rock", "rich_wolframite_ore", "rich_bauxite",
            "pentlandite", "rich_nickel_ore", "rich_hematite", "rich_magnetite", "galena", "rich_galena_ore",
            "dolomite", "graphite_rock", "phosphate_rock", "diamond_ore", "cobalt_ore", "uraninite", "thorium_ore",
            "ultramafic_rock", "rich_osmium_ore", "rich_iridium_ore", "rich_platinum_ore",
            "ilmenite", "rich_ilmenite_ore", "bertrandite", "borax_rock", "cassiterite", "chromite",
            "rich_tin_ore", "rich_chromium_ore");

    static {
        for (String id : APPROVED_IDS) {
            DeferredBlock<Block> block = BLOCKS.registerBlock(
                    id, Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.STONE)
                            .strength(3.0F, 3.0F).requiresCorrectToolForDrops());
            GEOLOGY_BLOCKS.put(id, block);
            GEOLOGY_ITEMS.put(id, ITEMS.registerSimpleBlockItem(id, block));
        }
    }

    /** A small, hand-collectable placer occurrence, not a new Gold host rock. */
    public static final DeferredBlock<Block> GOLD_FLAKES = BLOCKS.registerBlock(
            "gold_flakes", GeologyBlocks::newGoldFlakes,
            BlockBehaviour.Properties.of().instabreak().noCollission().noOcclusion().sound(SoundType.METAL));
    public static final DeferredItem<BlockItem> GOLD_FLAKES_ITEM =
            ITEMS.registerSimpleBlockItem("gold_flakes", GOLD_FLAKES);
    public static final DeferredItem<Item> GOLD_FLAKE = ITEMS.registerSimpleItem("gold_flake");
    public static final DeferredItem<ProspectingToolItem> PROSPECTING_TOOL =
            ITEMS.register("prospecting_tool", () -> new ProspectingToolItem(new Item.Properties().stacksTo(1)));

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> RESOURCE_TAB = TABS.register(
            "geology_resources",
            () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.industrial_colonies.geology_resources"))
                    .icon(() -> new ItemStack(GEOLOGY_ITEMS.get("hematite").get()))
                    .displayItems((parameters, output) -> {
                        GEOLOGY_ITEMS.values().forEach(item -> output.accept(item.get()));
                        output.accept(GOLD_FLAKES_ITEM.get());
                        output.accept(GOLD_FLAKE.get());
                        output.accept(PROSPECTING_TOOL.get());
                    })
                    .build());

    private GeologyBlocks() {
    }

    /** Register once on the mod bus, before registry events fire. */
    public static void register(IEventBus modEventBus) {
        BLOCKS.register(modEventBus);
        ITEMS.register(modEventBus);
        TABS.register(modEventBus);
    }

    /** Resolve an approved path, or its industrial_colonies-qualified ID; unknown IDs fail loudly. */
    public static Block block(String path) {
        String prefix = IndustrialColonies.MOD_ID + ":";
        String local = path.startsWith(prefix) ? path.substring(prefix.length()) : path;
        if (local.equals("gold_flakes")) {
            return GOLD_FLAKES.get();
        }
        DeferredBlock<Block> block = GEOLOGY_BLOCKS.get(local);
        if (block == null) {
            throw new IllegalArgumentException("Not an approved Industrial Colonies geological block: " + path);
        }
        return block.get();
    }

    /** Registration handles for the 40 approved cubes, excluding the separate placer occurrence. */
    public static Map<String, DeferredBlock<Block>> geologyBlocks() {
        return Collections.unmodifiableMap(GEOLOGY_BLOCKS);
    }

    private static Block newGoldFlakes(BlockBehaviour.Properties properties) {
        return new GoldFlakesBlock(properties);
    }

    /** Tiny solid-ground flakes with no collision or tool requirement. */
    private static final class GoldFlakesBlock extends Block implements SimpleWaterloggedBlock {
        private static final MapCodec<GoldFlakesBlock> CODEC = simpleCodec(GoldFlakesBlock::new);
        private static final VoxelShape SHAPE = Shapes.or(
                Block.box(3.0, 0.0, 4.0, 6.0, 0.5, 7.0),
                Block.box(9.0, 0.0, 8.0, 12.0, 0.5, 10.0),
                Block.box(6.0, 0.0, 11.0, 8.0, 0.5, 13.0));

        private GoldFlakesBlock(BlockBehaviour.Properties properties) {
            super(properties);
            registerDefaultState(stateDefinition.any().setValue(BlockStateProperties.WATERLOGGED, false));
        }

        @Override
        protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
            builder.add(BlockStateProperties.WATERLOGGED);
        }

        @Override
        public BlockState getStateForPlacement(BlockPlaceContext context) {
            return defaultBlockState().setValue(BlockStateProperties.WATERLOGGED,
                    context.getLevel().getFluidState(context.getClickedPos()).getType() == Fluids.WATER);
        }

        @Override
        protected FluidState getFluidState(BlockState state) {
            return state.getValue(BlockStateProperties.WATERLOGGED)
                    ? Fluids.WATER.getSource(false) : super.getFluidState(state);
        }

        @Override
        public MapCodec<? extends Block> codec() {
            return CODEC;
        }

        @Override
        protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
            return SHAPE;
        }

        @Override
        protected boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
            BlockPos below = pos.below();
            return level.getBlockState(below).isFaceSturdy(level, below, Direction.UP);
        }

        @Override
        protected BlockState updateShape(BlockState state, Direction direction, BlockState neighbor,
                LevelAccessor level, BlockPos pos, BlockPos neighborPos) {
            if (state.getValue(BlockStateProperties.WATERLOGGED)) {
                level.scheduleTick(pos, Fluids.WATER, Fluids.WATER.getTickDelay(level));
            }
            return state.canSurvive(level, pos)
                    ? super.updateShape(state, direction, neighbor, level, pos, neighborPos)
                    : state.getFluidState().createLegacyBlock();
        }
    }
}
