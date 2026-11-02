package dev.godpc.industrialcolonies.geology.oil;

import com.drmangotea.tfmg.worldgen.deposits.OilDepositFeature;
import com.mojang.logging.LogUtils;
import dev.godpc.industrialcolonies.geology.GeologyConfig;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import org.slf4j.Logger;

/** Regional oil fields made from TFMG's native scanner-compatible deposit columns. */
public final class OilReservoirFeature extends Feature<NoneFeatureConfiguration> {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final OilDepositFeature NATIVE_DEPOSIT = new OilDepositFeature(NoneFeatureConfiguration.CODEC);

    public OilReservoirFeature() {
        super(NoneFeatureConfiguration.CODEC);
    }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context) {
        WorldGenLevel level = context.level();
        OilRules rules = OilRules.get();
        if (!GeologyConfig.enabled() || !rules.enabled() || !level.getLevel().dimension().equals(Level.OVERWORLD)) return false;
        // Native TFMG deposit markers and the unchanged scanner agree on Y=-64 in this pack.
        if (rules.reservoirY() < level.getMinBuildHeight() || rules.reservoirY() + 25 >= level.getMaxBuildHeight()) return false;
        int chunkX = Math.floorDiv(context.origin().getX(), 16);
        int chunkZ = Math.floorDiv(context.origin().getZ(), 16);
        int cellX = Math.floorDiv(chunkX * 16, rules.regionSize());
        int cellZ = Math.floorDiv(chunkZ * 16, rules.regionSize());
        boolean placed = false;
        // Config validation keeps each complete field inside its own regional cell. One coordinate
        // calculation replaces neighbor searches; this neither loads nor decorates another chunk.
        OilFieldPlanner.Field field = OilFieldPlanner.field(level.getSeed(), rules.salt(), cellX, cellZ,
                rules.regionSize(), rules.regionMargin(), rules.radiusMin(), rules.radiusMax(), rules.wellsMin(), rules.wellsMax());
        if (field.wells().stream().noneMatch(well -> well.chunkX() == chunkX && well.chunkZ() == chunkZ)) return false;
        Surface center = surface(context, field.centerX(), field.centerZ());
        double weight = rules.weight(center.families());
        if (!OilFieldPlanner.accepted(field.roll(), weight, rules.fieldChance(), rules.weightNormalizer())) {
            debug(rules, field, "biome/field roll rejected", weight, 0);
            return false;
        }
        if (!terrainAllowed(context, rules, field.centerX(), field.centerZ(), center)) {
            debug(rules, field, "center terrain veto", weight, 0);
            return false;
        }
        int generated = 0;
        for (OilFieldPlanner.Well well : field.wells()) {
            if (well.chunkX() != chunkX || well.chunkZ() != chunkZ) continue;
            Surface local = surface(context, well.x(), well.z());
            if (rules.weight(local.families()) <= 0 || !terrainAllowed(context, rules, well.x(), well.z(), local)) continue;
            // Validate every horizontal position the native radius-one column may touch. A basin
            // next to a mountain/volcano cannot leak oil into the prohibited side of the boundary.
            boolean footprintAllowed = true;
            for (int[] offset : new int[][] {{1, 0}, {-1, 0}, {0, 1}, {0, -1}}) {
                Surface edge = surface(context, well.x() + offset[0], well.z() + offset[1]);
                if (rules.weight(edge.families()) <= 0 || edge.height() > rules.maximumSurfaceY()) {
                    footprintAllowed = false;
                    break;
                }
            }
            if (!footprintAllowed) continue;
            BlockPos position = new BlockPos(well.x(), rules.reservoirY(), well.z());
            if (!level.ensureCanWrite(position) || !level.ensureCanWrite(position.above(25))) continue;
            NATIVE_DEPOSIT.placeDeposit(position, level, RandomSource.create(well.seed()));
            generated++;
            placed = true;
        }
        debug(rules, field, generated == 0 ? "local well veto" : "native columns placed", weight, generated);
        return placed;
    }

    private static boolean terrainAllowed(FeaturePlaceContext<?> context, OilRules rules, int x, int z, Surface center) {
        if (center.height() > rules.maximumSurfaceY() || rules.weight(center.families()) <= 0) return false;
        int low = center.height();
        int high = center.height();
        int radius = rules.terrainSampleRadius();
        for (int[] offset : new int[][] {{radius, 0}, {-radius, 0}, {0, radius}, {0, -radius}}) {
            int height = height(context, x + offset[0], z + offset[1]);
            low = Math.min(low, height);
            high = Math.max(high, height);
        }
        return high <= rules.maximumSurfaceY() && high - low <= rules.maximumRelief();
    }

    /** Base noise sampling never requests a neighboring chunk, even at a regional boundary. */
    private static int height(FeaturePlaceContext<?> context, int x, int z) {
        return context.chunkGenerator().getBaseHeight(x, z, Heightmap.Types.OCEAN_FLOOR_WG,
                context.level(), context.level().getLevel().getChunkSource().randomState());
    }

    private static Surface surface(FeaturePlaceContext<?> context, int x, int z) {
        ChunkGenerator generator = context.chunkGenerator();
        RandomState random = context.level().getLevel().getChunkSource().randomState();
        int height = height(context, x, z);
        Holder<Biome> biome = generator.getBiomeSource().getNoiseBiome(Math.floorDiv(x, 4),
                Math.floorDiv(Math.max(height, generator.getSeaLevel()), 4), Math.floorDiv(z, 4), random.sampler());
        String id = biome.unwrapKey().map(key -> key.location().toString()).orElse("");
        return new Surface(height, GeologyConfig.families(id));
    }

    private static void debug(OilRules rules, OilFieldPlanner.Field field, String reason, double weight, int columns) {
        if (rules.debug()) LOGGER.info("Geology oil center=({}, {}) radius={} biomeWeight={} roll={} columns={} reason={}",
                field.centerX(), field.centerZ(), field.radius(), weight, field.roll(), columns, reason);
    }

    private record Surface(int height, Set<String> families) {}
}
