package dev.godpc.industrialcolonies.geology;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;

/** Bounded read-only nearest observation. The reader must validate existing saved records. */
public final class RecordedVeinLookup {
    public record Site(String family,int x,int y,int z,int reserved,String biome) {}
    public record Result(Optional<Site> nearest,int journals) {}
    @FunctionalInterface public interface Reader { List<Site> read(Path file) throws IOException; }
    private RecordedVeinLookup() {}
    public static Result scan(Path root,String family,double x,double z,int radius,Reader reader) throws IOException {
        if(family==null||!family.matches("[a-z0-9_]{1,80}")||!Double.isFinite(x)||!Double.isFinite(z)
                ||radius<1||radius>131072)throw new IllegalArgumentException("Bounded family/position/radius required");
        if(!Files.isDirectory(root,LinkOption.NOFOLLOW_LINKS)||Files.isSymbolicLink(root))throw new IOException("Saved occurrence directory unavailable");
        Site nearest=null;double best=(double)radius*radius;int directories=0,journals=0;
        try(var entries=Files.newDirectoryStream(root,"continent-*")) {
            for(Path directory:entries) {
                if(Thread.currentThread().isInterrupted())throw new IOException("Recorded lookup interrupted");
                if(++directories>4096)throw new IOException("Recorded lookup directory limit reached; no complete nearest result");
                if(!directory.getFileName().toString().matches("continent-[0-9a-f]{8}-[0-9a-f]{8}-[0-9a-f]{8}")
                        ||Files.isSymbolicLink(directory)||!Files.isDirectory(directory,LinkOption.NOFOLLOW_LINKS))
                    throw new IOException("Unexpected saved continent directory");
                Path file=directory.resolve("occurrences.bin");
                if(!Files.exists(file,LinkOption.NOFOLLOW_LINKS))continue;
                if(Files.isSymbolicLink(file)||!Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS))throw new IOException("Unexpected occurrence file");
                journals++;
                for(var site:reader.read(file)) {
                    if(!site.family().equals(family))continue;
                    double dx=site.x()-x,dz=site.z()-z,distance=dx*dx+dz*dz;
                    if(distance<best||distance==best&&(nearest==null||compare(site,nearest)<0)){nearest=site;best=distance;}
                }
            }
        }
        return new Result(Optional.ofNullable(nearest),journals);
    }
    private static int compare(Site a,Site b){int c=Integer.compare(a.x(),b.x());if(c==0)c=Integer.compare(a.z(),b.z());return c==0?Integer.compare(a.y(),b.y()):c;}
}
