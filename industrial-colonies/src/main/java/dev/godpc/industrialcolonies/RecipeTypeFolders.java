package dev.godpc.industrialcolonies;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/** Presentation-only grouping. Saved type IDs, definitions and machine selection never change. */
public final class RecipeTypeFolders {
    public static final String ALL = "";
    public record Entry(String id, String modId, String requiresMod, String icon, String label) { }
    public record Folder(String id, String label, int matches) { }
    private static final List<String> ORDER = List.of("minecraft", "create", "tfmg", "mekanism",
            "nuclearcraft", "modernfoundry", "createmetallurgy", "ae2", "industrial_colonies");
    private static final Map<String, String> LABELS = Map.ofEntries(
            Map.entry("minecraft", "Minecraft"), Map.entry("create", "Create"),
            Map.entry("tfmg", "TFMG"), Map.entry("mekanism", "Mekanism"),
            Map.entry("nuclearcraft", "NuclearCraft"), Map.entry("modernfoundry", "Modern Foundry"),
            Map.entry("createmetallurgy", "Create: Metallurgy"), Map.entry("ae2", "Applied Energistics 2"),
            Map.entry("industrial_colonies", "Industrial Colonies"),
            Map.entry("immersiveengineering", "Immersive Engineering"),
            Map.entry("ad_astra", "Ad Astra"), Map.entry("pneumaticcraft", "PneumaticCraft"));

    private RecipeTypeFolders() { }

    /** Old ATM-only workaround layouts still resolve saved cards, but are not new-card choices. */
    public static boolean visibleInPicker(Entry entry) {
        return !clean(entry.id()).startsWith("industrial_colonies:atm_");
    }

    /** Pack wrappers belong to their actual process mod, not the wrapper's namespace. */
    public static String origin(Entry entry) {
        String namespace = namespace(entry.id());
        if (!namespace.equals("kjsgen") && !namespace.equals("industrial_colonies")) return namespace;
        String path = clean(entry.id()).replaceFirst("^[^:]*:", "");
        for (String mod : List.of("modernfoundry", "nuclearcraft", "mekanism", "tfmg", "ae2", "create")) {
            if (path.startsWith(mod + "_") || path.equals(mod)) return mod;
        }
        if (path.startsWith("metallurgy_") || path.equals("basin_melting")) return "createmetallurgy";
        for (String candidate : List.of(clean(entry.modId()), clean(entry.requiresMod()), namespace(entry.icon()))) {
            if (!candidate.isBlank() && !candidate.equals("kjsgen") && !candidate.equals("industrial_colonies")
                    && !candidate.endsWith("_legacy_layout")) return candidate;
        }
        return "industrial_colonies";
    }

    public static String label(String mod) {
        return LABELS.getOrDefault(mod, titleCase(mod));
    }

    public static boolean matches(Entry entry, String query) {
        String needle = clean(query).trim();
        return needle.isEmpty() || clean(entry.id()).contains(needle) || clean(entry.modId()).contains(needle)
                || clean(entry.label()).contains(needle) || clean(label(origin(entry))).contains(needle);
    }

    /** Keep zero-result folders visible while searching so the current folder never silently changes. */
    public static List<Folder> folders(Collection<Entry> entries, String query) {
        Map<String, Integer> counts = new LinkedHashMap<>();
        int total = 0;
        for (Entry entry : entries) {
            String mod = origin(entry);
            boolean match = matches(entry, query);
            counts.merge(mod, match ? 1 : 0, Integer::sum);
            if (match) total++;
        }
        List<Folder> result = new ArrayList<>();
        result.add(new Folder(ALL, "All recipe types", total));
        counts.entrySet().stream().sorted(Comparator
                .<Map.Entry<String, Integer>>comparingInt(value -> priority(value.getKey()))
                .thenComparing(value -> label(value.getKey()), String.CASE_INSENSITIVE_ORDER))
                .forEach(value -> result.add(new Folder(value.getKey(), label(value.getKey()), value.getValue())));
        return List.copyOf(result);
    }

    public static boolean inFolder(Entry entry, String folder, String query) {
        return (folder == null || folder.isEmpty() || origin(entry).equals(folder)) && matches(entry, query);
    }

    public static int maxOffset(int count, int visibleRows) { return Math.max(0, count - Math.max(1, visibleRows)); }
    public static int clampOffset(int value, int count, int visibleRows) {
        return Math.max(0, Math.min(value, maxOffset(count, visibleRows)));
    }
    private static int priority(String mod) { int index = ORDER.indexOf(mod); return index < 0 ? ORDER.size() : index; }
    private static String namespace(String id) { String value = clean(id); int colon = value.indexOf(':'); return colon > 0 ? value.substring(0, colon) : ""; }
    private static String clean(String value) { return value == null ? "" : value.toLowerCase(Locale.ROOT); }
    private static String titleCase(String value) {
        StringBuilder result = new StringBuilder();
        for (String word : value.replace('_', ' ').split(" +")) {
            if (word.isEmpty()) continue;
            if (!result.isEmpty()) result.append(' ');
            result.append(Character.toUpperCase(word.charAt(0))).append(word.substring(1));
        }
        return result.toString();
    }
}
