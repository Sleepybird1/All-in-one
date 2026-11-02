package dev.godpc.industrialcolonies.geology;

import net.minecraft.core.QuartPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.levelgen.Heightmap;

/** Queries generator data without requesting full chunks or placing blocks.
 * Base height/noise biome precede structures and final surface material replacement. */
public final class NativeGeographicColumnSource implements GeographicColumnSurvey.Source {
    private final ServerLevel level;
    private final ReTerraForgedGeography geography;
    public NativeGeographicColumnSource(ServerLevel level){
        this.level=java.util.Objects.requireNonNull(level);
        this.geography=ReTerraForgedGeography.fromRandomState(level.getChunkSource().randomState());
    }
    @Override public GeographicColumnSurvey.Column read(int x,int z){
        var sample=geography.sample(x,z);
        var source=level.getChunkSource();var generator=source.getGenerator();var state=source.randomState();
        int y=generator.getBaseHeight(x,z,Heightmap.Types.WORLD_SURFACE_WG,level,state)-1;
        var biome=generator.getBiomeSource().getNoiseBiome(QuartPos.fromBlock(x),QuartPos.fromBlock(y),QuartPos.fromBlock(z),state.sampler());
        String id=biome.unwrapKey().orElseThrow(()->new IllegalStateException("Unregistered native biome")).location().toString();
        return new GeographicColumnSurvey.Column(sample,id,y);
    }
}
