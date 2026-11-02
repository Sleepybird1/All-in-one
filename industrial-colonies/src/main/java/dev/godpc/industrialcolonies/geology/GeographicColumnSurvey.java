package dev.godpc.industrialcolonies.geology;

import java.util.*;

/** Exact bounded-window census, with no inference of whole-continent completeness.
 * Native region/biome groups are not necessarily connected geographic districts. */
public final class GeographicColumnSurvey {
    public record Window(int minX,int minZ,int maxX,int maxZ) {
        public Window {
            if(minX>maxX||minZ>maxZ||minX < -16777216||minZ < -16777216
                    ||maxX>16777216||maxZ>16777216)throw new IllegalArgumentException("Exact native coordinate window required");
        }
        public long width(){return (long)maxX-minX+1;}
        public long columns(){return Math.multiplyExact(width(),(long)maxZ-minZ+1);}
    }
    public record Column(ReTerraForgedGeography.Sample geography,String surfaceBiome,int baseSurfaceY) {
        public Column {
            Objects.requireNonNull(geography);
            if(surfaceBiome==null||!surfaceBiome.matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))throw new IllegalArgumentException("Registered biome key required");
        }
    }
    public record Group(ReTerraForgedGeography.ContinentKey continent,
                        ReTerraForgedGeography.TerrainKey region,String biome) {}
    public record Area(long columns,long mountainColumns,int minSurfaceY,int maxSurfaceY,long boundaryColumns) {}
    public enum Status { IN_PROGRESS, COMPLETE_WINDOW }
    public record Snapshot(Window window,long visited,Status status,Map<Group,Area> groups) {
        public Snapshot { groups=Map.copyOf(groups); }
    }
    @FunctionalInterface public interface Source { Column read(int x,int z); }
    private final Window window;
    private final Source source;
    private final Map<Group,Area> groups=new LinkedHashMap<>();
    private long visited;
    public GeographicColumnSurvey(Window window,Source source){this.window=Objects.requireNonNull(window);this.source=Objects.requireNonNull(source);}
    /** At most budget native queries. A failed read does not advance or count that column. */
    public Snapshot advance(int budget){
        if(budget<1||budget>65536)throw new IllegalArgumentException("Column budget must be1..65536");
        for(int i=0;i<budget&&visited<window.columns();i++){
            int x=(int)(window.minX()+visited%window.width());
            int z=(int)(window.minZ()+visited/window.width());
            Column column=Objects.requireNonNull(source.read(x,z));
            var g=column.geography();var key=new Group(g.continent(),g.region(),column.surfaceBiome());
            Area old=groups.get(key);long mountain=g.mountain()?1:0;
            long edge=x==window.minX()||x==window.maxX()||z==window.minZ()||z==window.maxZ()?1:0;
            groups.put(key,old==null?new Area(1,mountain,column.baseSurfaceY(),column.baseSurfaceY(),edge):
                    new Area(old.columns()+1,old.mountainColumns()+mountain,Math.min(old.minSurfaceY(),column.baseSurfaceY()),
                            Math.max(old.maxSurfaceY(),column.baseSurfaceY()),old.boundaryColumns()+edge));
            visited++;
        }
        return snapshot();
    }
    public Snapshot snapshot(){return new Snapshot(window,visited,visited==window.columns()?Status.COMPLETE_WINDOW:Status.IN_PROGRESS,groups);}
}
