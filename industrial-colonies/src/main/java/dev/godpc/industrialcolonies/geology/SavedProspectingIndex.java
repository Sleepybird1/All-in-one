package dev.godpc.industrialcolonies.geology;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;

/** Read-only saved occurrence decisions. Absence is reported only for an explicit saved decision. */
public final class SavedProspectingIndex {
    public record Site(String family, int x, int z, ReTerraForgedGeography.ContinentKey continent) {}
    public record Answer(Optional<Site> site, boolean currentContinent, boolean explicitlyAbsent) {}
    private final List<Site> sites;
    private final Map<ReTerraForgedGeography.ContinentKey, Set<String>> absent;

    public SavedProspectingIndex(List<Site> sites,
            Map<ReTerraForgedGeography.ContinentKey, Set<String>> absent) {
        this.sites = List.copyOf(sites);
        var copy = new HashMap<ReTerraForgedGeography.ContinentKey, Set<String>>();
        absent.forEach((key, values) -> copy.put(key, Set.copyOf(values)));
        this.absent = Map.copyOf(copy);
    }

    public static SavedProspectingIndex read(NativeContinentLevels.RecordedLookup descriptor) throws IOException {
        Path root = descriptor.directory();
        if (!Files.isDirectory(root, LinkOption.NOFOLLOW_LINKS) || Files.isSymbolicLink(root))
            throw new IOException("Saved prospecting directory unavailable");
        var sites = new ArrayList<Site>();
        var absent = new HashMap<ReTerraForgedGeography.ContinentKey, Set<String>>();
        int count = 0;
        try (var directories = Files.newDirectoryStream(root, "continent-*")) {
            for (var directory : directories) {
                if (Thread.currentThread().isInterrupted() || ++count > 4096)
                    throw new IOException("Saved prospecting read interrupted or bounded limit reached");
                String name = directory.getFileName().toString();
                if(name.matches("continent-[0-9a-f]{8}-[0-9a-f]{8}-[0-9a-f]{8}\\.(started|policy)")){
                    if(!Files.isRegularFile(directory,LinkOption.NOFOLLOW_LINKS)||Files.isSymbolicLink(directory)
                        ||Files.size(directory)!=(name.endsWith(".policy")?64:0))throw new IOException("Invalid continent commissioning metadata");
                    continue;
                }
                if (!name.matches("continent-[0-9a-f]{8}-[0-9a-f]{8}-[0-9a-f]{8}")
                        || Files.isSymbolicLink(directory) || !Files.isDirectory(directory, LinkOption.NOFOLLOW_LINKS))
                    throw new IOException("Unexpected continent directory");
                var parts = name.substring("continent-".length()).split("-");
                var continent = new ReTerraForgedGeography.ContinentKey(
                        Integer.parseUnsignedInt(parts[0], 16), Integer.parseUnsignedInt(parts[1], 16),
                        Integer.parseUnsignedInt(parts[2], 16));
                Path file = directory.resolve("occurrences.bin");
                if (!Files.exists(file, LinkOption.NOFOLLOW_LINKS)) continue;
                if (Files.isSymbolicLink(file) || !Files.isRegularFile(file, LinkOption.NOFOLLOW_LINKS))
                    throw new IOException("Unexpected occurrence file");
                var rows = ContinentOccurrenceLedger.open(file, descriptor.scope(), continent).snapshot();
                for (var row : rows.values()) {
                    var request = row.request();
                    if (row.present()) {
                        var candidate = request.candidate();
                        sites.add(new Site(request.key().family(), candidate.x(), candidate.z(), continent));
                    } else absent.computeIfAbsent(continent, ignored -> new HashSet<>()).add(request.key().family());
                }
            }
        }
        return new SavedProspectingIndex(sites, absent);
    }

    public Answer nearest(String family, int x, int z, ReTerraForgedGeography.ContinentKey continent) {
        Site local = null, remote = null;
        long localDistance = Long.MAX_VALUE, remoteDistance = Long.MAX_VALUE;
        for (var site : sites) {
            if (!site.family().equals(family)) continue;
            long dx = (long) site.x() - x, dz = (long) site.z() - z;
            long distance = Math.addExact(Math.multiplyExact(dx, dx), Math.multiplyExact(dz, dz));
            if (site.continent().equals(continent)) {
                if (before(site, distance, local, localDistance)) { local = site; localDistance = distance; }
            } else if (before(site, distance, remote, remoteDistance)) { remote = site; remoteDistance = distance; }
        }
        boolean knownAbsent = absent.getOrDefault(continent, Set.of()).contains(family);
        return new Answer(Optional.ofNullable(local != null ? local : remote), local != null, knownAbsent && local == null);
    }

    private static boolean before(Site site, long distance, Site prior, long priorDistance) {
        return prior == null || distance < priorDistance || distance == priorDistance
                && (site.x() < prior.x() || site.x() == prior.x() && site.z() < prior.z());
    }
}
