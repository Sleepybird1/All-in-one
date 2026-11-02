package dev.godpc.industrialcolonies.geology;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.logging.LogUtils;
import java.awt.image.BufferedImage;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import javax.imageio.ImageIO;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

/** Bounded CI smoke checks; NeoForge only discovers these in a development GameTest run. */
@GameTestHolder("industrial_colonies")
@PrefixGameTestTemplate(false)
public final class GeologyGameTests {
    private static final String TEMPLATE = "geology_smoke_empty";

    private GeologyGameTests() {
    }

    @GameTest(template = TEMPLATE, timeoutTicks = 200)
    public static void approvedRegistryAndTags(GameTestHelper helper) {
        helper.assertTrue(GeologyBlocks.APPROVED_IDS.size() == 40, "Expected exactly 40 approved custom cubes");
        TagKey<Block> rocks = TagKey.create(Registries.BLOCK, id("geological_rocks"));
        TagKey<Block> rich = TagKey.create(Registries.BLOCK, id("rich_ores"));
        TagKey<Block> genericOres = TagKey.create(Registries.BLOCK, ResourceLocation.parse("c:ores"));
        int rockCount = 0;
        int richCount = 0;
        for (String name : GeologyBlocks.APPROVED_IDS) {
            ResourceLocation key = id(name);
            helper.assertTrue(BuiltInRegistries.BLOCK.containsKey(key), "Missing block " + key);
            helper.assertTrue(BuiltInRegistries.ITEM.containsKey(key), "Missing item " + key);
            Block block = GeologyBlocks.block(name);
            Item item = BuiltInRegistries.ITEM.get(key);
            helper.assertTrue(item instanceof BlockItem blockItem && blockItem.getBlock() == block,
                    "Incorrect BlockItem binding " + key);
            BlockState state = block.defaultBlockState();
            helper.assertTrue(state.is(BlockTags.MINEABLE_WITH_PICKAXE), "Missing pickaxe tag " + key);
            if (state.is(rocks)) {
                rockCount++;
                helper.assertFalse(state.is(genericOres), "Low-yield rock entered generic c:ores: " + key);
            }
            if (state.is(rich)) {
                richCount++;
            }
        }
        helper.assertTrue(rockCount == 20 && richCount == 16, "Expected 20 low-yield and 16 rich cubes");
        helper.assertTrue(BuiltInRegistries.BLOCK.get(id("gold_flakes")) == GeologyBlocks.GOLD_FLAKES.get(),
                "Missing placer block");
        helper.assertTrue(BuiltInRegistries.ITEM.get(id("gold_flake")) == GeologyBlocks.GOLD_FLAKE.get(),
                "Missing Gold Flake item");
        helper.assertTrue(BuiltInRegistries.CREATIVE_MODE_TAB.containsKey(id("geology_resources")),
                "Missing unified resources tab");
        LogUtils.getLogger().info("GEOLOGY_SMOKE registry PASS; source={}",
                GeologyBlocks.class.getProtectionDomain().getCodeSource().getLocation());
        helper.succeed();
    }

    @GameTest(template = TEMPLATE, timeoutTicks = 200)
    public static void configurationAndWorldgenRegistries(GameTestHelper helper) throws Exception {
        // Force target transformation even though the CI world uses a flat test arena.
        assertMixinHandler(helper, "net.minecraft.world.level.levelgen.NoiseBasedChunkGenerator", "industrialColonies$withoutDefaultVeins");
        assertMixinHandler(helper, "net.minecraft.world.level.levelgen.NoiseBasedChunkGenerator", "industrialColonies$placeGeologyAfterCarvers");
        assertMixinHandler(helper, "net.minecraft.world.level.levelgen.placement.PlacedFeature", "industrialColonies$guard");
        assertMixinHandler(helper, "net.minecraft.world.level.levelgen.feature.FossilFeature", "industrialColonies$preserveBonesWithoutOreOverlay");
        if (net.neoforged.fml.ModList.get().isLoaded("quark")) {
            assertMixinHandler(helper, "org.violetmoon.quark.content.world.gen.FairyRingGenerator", "industrialColonies$keepFlowersAndEmeralds");
        }
        Object structures = helper.getLevel().structureManager();
        helper.assertTrue(structures instanceof dev.godpc.industrialcolonies.mixin.GeologyStructureManagerAccessor,
                "StructureManager accessor mixin was not applied");
        helper.assertTrue(((dev.godpc.industrialcolonies.mixin.GeologyStructureManagerAccessor) structures)
                        .industrialColonies$level() == helper.getLevel(), "StructureManager accessor targets the wrong level");
        LogUtils.getLogger().info("GEOLOGY_SMOKE required geology mixin applications PASS");
        GeologyConfig.Config config = GeologyConfig.get();
        GeologyConfig.validate(config);
        helper.assertTrue(config.deposits().getAsJsonArray("deposits").size() == 24,
                "Expected the approved 23 deposit profiles plus regular Gold");
        for (JsonElement entry : config.deposits().getAsJsonArray("deposits")) {
            JsonObject deposit = entry.getAsJsonObject();
            helper.assertTrue(BuiltInRegistries.BLOCK.containsKey(ResourceLocation.parse(deposit.get("hostRock").getAsString())),
                    "Unregistered host in loaded configuration: " + deposit.get("id"));
            for (JsonElement rich : deposit.getAsJsonArray("richOres")) {
                helper.assertTrue(BuiltInRegistries.BLOCK.containsKey(ResourceLocation.parse(rich.getAsJsonObject().get("block").getAsString())),
                        "Unregistered rich ore in loaded configuration");
            }
            for (JsonElement association : deposit.getAsJsonArray("associated")) {
                helper.assertTrue(BuiltInRegistries.BLOCK.containsKey(ResourceLocation.parse(association.getAsJsonObject().get("block").getAsString())),
                        "Unregistered associated ore in loaded configuration");
            }
        }
        helper.assertTrue(helper.getLevel().registryAccess().registryOrThrow(Registries.CONFIGURED_FEATURE)
                        .containsKey(id("regional_geology")), "Missing decoded regional_geology configured feature");
        helper.assertTrue(helper.getLevel().registryAccess().registryOrThrow(Registries.PLACED_FEATURE)
                        .containsKey(id("regional_geology")), "Missing decoded regional_geology placed feature");
        var biomes = helper.getLevel().registryAccess().registryOrThrow(Registries.BIOME);
        for (var family : config.biomes().entrySet()) {
            if (!family.getValue().isJsonArray()) {
                continue;
            }
            for (JsonElement biome : family.getValue().getAsJsonArray()) {
                helper.assertTrue(biomes.containsKey(ResourceLocation.parse(biome.getAsString())),
                        "Unregistered configured biome " + biome.getAsString());
            }
        }
        LogUtils.getLogger().info("GEOLOGY_SMOKE config/datapack PASS");
        helper.succeed();
    }

    @GameTest(template = TEMPLATE, timeoutTicks = 200)
    public static void rockLootAndPlacerBehavior(GameTestHelper helper) {
        BlockPos position = helper.absolutePos(new BlockPos(1, 1, 1));
        for (String name : GeologyBlocks.APPROVED_IDS) {
            Block block = GeologyBlocks.block(name);
            // Processing batch explicitly changes only these four rich-rock drops.
            Item expected = switch (name) {
                case "diamond_ore" -> Items.DIAMOND;
                case "rich_hematite", "rich_magnetite" -> Items.RAW_IRON;
                case "rich_copper_ore" -> Items.RAW_COPPER;
                case "rich_sphalerite" -> BuiltInRegistries.ITEM.get(ResourceLocation.parse("create:raw_zinc"));
                default -> block.asItem();
            };
            List<ItemStack> drops = Block.getDrops(block.defaultBlockState(), helper.getLevel(), position,
                    null, null, new ItemStack(Items.DIAMOND_PICKAXE));
            helper.assertTrue(drops.size() == 1 && drops.getFirst().is(expected) && drops.getFirst().getCount() == 1,
                    "Unexpected geological loot/global loot modification for " + name);
        }
        helper.setBlock(new BlockPos(1, 0, 1), Blocks.STONE);
        helper.setBlock(new BlockPos(1, 1, 1), GeologyBlocks.GOLD_FLAKES.get());
        BlockState flakes = GeologyBlocks.GOLD_FLAKES.get().defaultBlockState();
        helper.assertTrue(flakes.canSurvive(helper.getLevel(), position), "Placer flakes cannot sit on a riverbank block");
        helper.assertTrue(flakes.getCollisionShape(helper.getLevel(), position).isEmpty(), "Placer flakes obstruct movement");
        helper.assertTrue(flakes.getShape(helper.getLevel(), position).bounds().maxY <= 0.0625,
                "Placer occurrence became a full host block");
        List<ItemStack> drops = Block.getDrops(flakes, helper.getLevel(), position, null, null, ItemStack.EMPTY);
        helper.assertTrue(drops.size() == 1 && drops.getFirst().is(GeologyBlocks.GOLD_FLAKE.get())
                        && drops.getFirst().getCount() == 1, "Placer must drop one Gold Flake, not an ingot/nugget");
        helper.setBlock(new BlockPos(1, 0, 1), Blocks.AIR);
        helper.assertFalse(flakes.canSurvive(helper.getLevel(), position), "Unsupported placer flakes can float");
        LogUtils.getLogger().info("GEOLOGY_SMOKE loot/placer PASS");
        helper.succeed();
    }

    @GameTest(template = TEMPLATE, timeoutTicks = 200)
    public static void packagedModelsAndTextures(GameTestHelper helper) throws Exception {
        Set<String> texturePaths = new HashSet<>();
        for (String name : GeologyBlocks.APPROVED_IDS) {
            JsonObject model = readJson("/assets/industrial_colonies/models/block/" + name + ".json");
            String parent = model.get("parent").getAsString();
            helper.assertTrue(parent.equals("minecraft:block/cube_all") || parent.equals("minecraft:block/cube"),
                    "Unexpected cube model " + name);
            for (var texture : model.getAsJsonObject("textures").entrySet()) {
                String location = texture.getValue().getAsString();
                ResourceLocation resource = ResourceLocation.parse(location);
                String path = "/assets/" + resource.getNamespace() + "/textures/" + resource.getPath() + ".png";
                if (texturePaths.add(path)) {
                    try (InputStream input = requireResource(path)) {
                        BufferedImage image = ImageIO.read(input);
                        helper.assertTrue(image != null, "PNG decode failed " + path);
                        int expectedSize = name.equals("bertrandite") ? 1254 : 16;
                        helper.assertTrue(image.getWidth() == expectedSize && image.getHeight() == expectedSize,
                                "Approved PNG size changed " + path);
                    }
                }
            }
            readJson("/assets/industrial_colonies/blockstates/" + name + ".json");
            readJson("/assets/industrial_colonies/models/item/" + name + ".json");
        }
        helper.assertTrue(texturePaths.size() == 42, "Expected 42 exact PNG assets, including three Spodumene maps");
        LogUtils.getLogger().info("GEOLOGY_SMOKE packaged assets PASS (headless decode, not GPU atlas validation)");
        helper.succeed();
    }

    private static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath("industrial_colonies", path);
    }

    private static void assertMixinHandler(GameTestHelper helper, String target, String handler) throws Exception {
        Class<?> transformed = Class.forName(target, true, GeologyGameTests.class.getClassLoader());
        helper.assertTrue(java.util.Arrays.stream(transformed.getDeclaredMethods())
                        .anyMatch(method -> method.getName().contains(handler)),
                "Required geology mixin handler missing from " + target + ": " + handler);
    }

    private static InputStream requireResource(String path) {
        InputStream input = GeologyGameTests.class.getResourceAsStream(path);
        if (input == null) {
            throw new IllegalStateException("Missing packaged resource " + path);
        }
        return input;
    }

    private static JsonObject readJson(String path) throws Exception {
        try (InputStream input = requireResource(path);
                InputStreamReader reader = new InputStreamReader(input, StandardCharsets.UTF_8)) {
            return JsonParser.parseReader(reader).getAsJsonObject();
        }
    }
}
