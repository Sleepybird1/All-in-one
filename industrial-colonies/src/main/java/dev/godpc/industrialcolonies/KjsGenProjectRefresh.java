package dev.godpc.industrialcolonies;

import com.google.gson.*;
import com.zizazr.kjsgen.core.RecipeProject;
import com.zizazr.kjsgen.core.RecipeTypeRegistry;
import java.io.IOException;
import java.nio.file.*;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

/** Local project custody only. Never invokes export or resource reload. */
public final class KjsGenProjectRefresh {
    private static final Gson JSON = new GsonBuilder().setPrettyPrinting().create();
    private record Baseline(String hash, JsonObject project) {}
    private static final Map<Path, Baseline> BASES = new HashMap<>();
    private static final Map<Path, String> LAST_RECOVERY = new HashMap<>();
    private static Path key(Path p) { return p.toAbsolutePath().normalize(); }
    public static Path stateRoot(Path p) { return key(p).getParent().getParent().getParent().resolve("local/kjsgen-project-refresh"); }
    public static String hash(byte[] bytes) {
        try { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes)); }
        catch (Exception e) { throw new IllegalStateException(e); }
    }
    public static String fingerprint(RecipeProject p) {
        JsonObject json=p.toJson();
        // Native upserts remove/reappend cards on the server without echoing that order
        // to their author. Compare contents, not incidental server list ordering.
        for(String field:List.of("recipes","removals")){
            List<JsonElement> rows=new ArrayList<>();json.getAsJsonArray(field).forEach(rows::add);
            rows.sort(Comparator.comparing(e->e.getAsJsonObject().get("uid").getAsString()));
            JsonArray sorted=new JsonArray();rows.forEach(sorted::add);json.add(field,sorted);
        }
        return hash(canonical(json).toString().getBytes(StandardCharsets.UTF_8));
    }
    private static JsonElement canonical(JsonElement value){
        if(value.isJsonObject()){
            JsonObject result=new JsonObject();value.getAsJsonObject().keySet().stream().sorted().forEach(k->result.add(k,canonical(value.getAsJsonObject().get(k))));return result;
        }
        if(value.isJsonArray()){JsonArray result=new JsonArray();value.getAsJsonArray().forEach(e->result.add(canonical(e)));return result;}
        // Float.toString is the native JSON wire value (0.6), while Gson equality
        // promotes a Float to double (0.6000000238...). Compare exact serialized
        // decimals, without a tolerance or coercing strings/unknown fields.
        if(value.isJsonPrimitive() && value.getAsJsonPrimitive().isNumber())
            return new JsonPrimitive(new java.math.BigDecimal(value.getAsString()).stripTrailingZeros());
        return value;
    }
    private static boolean same(JsonElement left,JsonElement right) {
        if(left==null || right==null)return left==right;
        return canonical(left).toString().equals(canonical(right).toString());
    }
    private static byte[] bytes(JsonObject p) { return JSON.toJson(p).getBytes(StandardCharsets.UTF_8); }
    private static byte[] read(Path p) throws IOException {
        if (!Files.exists(p, LinkOption.NOFOLLOW_LINKS)) return null;
        if (!Files.isRegularFile(p, LinkOption.NOFOLLOW_LINKS)) throw new IOException("Project is not a regular file.");
        return Files.readAllBytes(p);
    }
    private static String digest(byte[] bytes) { return bytes == null ? "MISSING" : hash(bytes); }
    private static JsonObject parse(byte[] bytes) throws IOException {
        try { return JsonParser.parseString(new String(bytes, StandardCharsets.UTF_8)).getAsJsonObject(); }
        catch (Exception e) { throw new IOException("Disk project is invalid JSON; nothing reloaded.", e); }
    }
    public static synchronized void loaded(Path path, RecipeProject project) throws IOException {
        path = key(path);
        if (!BASES.containsKey(path)) {
            byte[] disk = read(path);
            if (disk != null) {
                // Reject a concurrent replacement between upstream parse and this observation.
                if (!same(RecipeProject.fromJson(parse(disk)).toJson(),project.toJson()))
                    throw new IOException("Project changed during load. Retry opening it.");
                BASES.put(path, new Baseline(digest(disk), project.toJson().deepCopy()));
            }
        }
    }
    private static Path recovery(Path path, byte[] disk, JsonObject memory, Baseline base, String reason) throws IOException {
        String signature = digest(disk) + hash(bytes(memory));
        if (signature.equals(LAST_RECOVERY.get(path))) return stateRoot(path);
        Path dir = stateRoot(path).resolve("recovery/" + UUID.randomUUID());
        Files.createDirectories(dir);
        if (disk != null) Files.write(dir.resolve("disk.json"), disk);
        Files.write(dir.resolve("memory.json"), bytes(memory));
        if (base != null) Files.write(dir.resolve("baseline.json"), bytes(base.project));
        Files.writeString(dir.resolve("note.txt"), reason + "\nProject: " + path);
        LAST_RECOVERY.put(path, signature);
        return dir;
    }
    private interface Work<T> { T run() throws IOException; }
    private static <T> T locked(Path path, Work<T> work) throws IOException {
        Files.createDirectories(path.getParent());
        Path lock = stateRoot(path).resolve("locks/" + path.getFileName() + ".lock");
        Files.createDirectories(lock.getParent());
        try (var channel = FileChannel.open(lock, StandardOpenOption.CREATE, StandardOpenOption.WRITE)) {
            try (var held = channel.tryLock(0, 1, false)) {
                if (held == null) throw new IOException("Project is being updated. Retry shortly.");
                return work.run();
            } catch (java.nio.channels.OverlappingFileLockException e) { throw new IOException("Project update already in progress.", e); }
        }
    }
    private static void atomic(Path path, byte[] expected, byte[] next) throws IOException {
        Path tmp = Files.createTempFile(path.getParent(), ".ic-refresh-", ".tmp");
        try {
            Files.write(tmp, next);
            if (!Arrays.equals(expected, read(path))) throw new IOException("Project changed again; retry refresh.");
            Files.move(tmp, path, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
        } finally { Files.deleteIfExists(tmp); }
    }
    public static synchronized void save(Path file, RecipeProject project) throws IOException {
        Path path = key(file);
        locked(path, () -> {
            byte[] disk = read(path); Baseline base = BASES.get(path);
            JsonObject memory = project.toJson();
            if ((base == null && disk != null) || (base != null && !base.hash.equals(digest(disk)))) {
                Path backup = recovery(path, disk, memory, base, "SAVE BLOCKED: external disk change; use Refresh from disk.");
                throw new IOException("External project change. Use Refresh from disk; both versions preserved in " + backup);
            }
            byte[] next = bytes(memory);
            atomic(path, disk, next);
            BASES.put(path, new Baseline(digest(next), memory.deepCopy()));
            LAST_RECOVERY.remove(path);
            return null;
        });
    }
    public static synchronized boolean changed(Path file) throws IOException {
        Path p = key(file); Baseline b = BASES.get(p);
        return b == null || !b.hash.equals(digest(read(p)));
    }
    public static synchronized void requireUnchangedIfTracked(Path file) throws IOException {
        Path p=key(file);
        if(BASES.containsKey(p) && changed(p)) throw new IOException("Project changed on disk. Refresh it before moving recipes.");
    }
    public static synchronized void acceptOwnWrite(Path file,RecipeProject project) throws IOException {
        Path p=key(file);byte[] disk=read(p);
        if(disk==null || !same(parse(disk),project.toJson())) throw new IOException("Project changed after internal move.");
        BASES.put(p,new Baseline(digest(disk),project.toJson().deepCopy()));
    }
    public static synchronized RecipeProject refresh(Path file, RecipeProject memory) throws IOException {
        Path path = key(file);
        return locked(path, () -> {
            byte[] diskBytes = read(path); Baseline base = BASES.get(path);
            if (base == null || diskBytes == null) throw new IOException("No loaded baseline or disk file; refresh refused.");
            JsonObject disk = parse(diskBytes);
            Path backup = recovery(path, diskBytes, memory.toJson(), base, "Manual refresh: preserve disk, editor/server memory and baseline.");
            JsonObject merged;
            try { merged = merge(normalizeListSlots(base.project), normalizeListSlots(memory.toJson()), normalizeListSlots(disk)); }
            catch (IOException e) { throw new IOException(e.getMessage() + " Both versions preserved in " + backup, e); }
            RecipeProject result;
            try {
                result = RecipeProject.fromJson(merged);
                if (!result.name().equals(memory.name())) throw new IOException("External project rename is not supported by refresh.");
                if (!same(result.toJson(),merged)) throw new IOException("Project contains unsupported or noncanonical fields; refresh refused to avoid losing data.");
            } catch (RuntimeException e) { throw new IOException("Invalid project; nothing replaced.", e); }
            byte[] next = same(merged,disk) ? diskBytes : bytes(merged);
            if (!Arrays.equals(next, diskBytes)) atomic(path, diskBytes, next);
            else if (!Arrays.equals(diskBytes, read(path))) throw new IOException("Disk changed during refresh; retry.");
            BASES.put(path, new Baseline(digest(next), merged.deepCopy()));
            LAST_RECOVERY.remove(path);
            return result;
        });
    }
    /** Recognize only KJSGen's lossless singleton-to-list spelling migration.
     * Work on raw JSON copies so unknown fields remain available to the strict roundtrip guard.
     * Normalize all three inputs before merging so edits to the same logical slot still conflict.
     */
    static JsonObject normalizeListSlots(JsonObject project) throws IOException {
        JsonObject normalized=project.deepCopy();
        if(!normalized.has("recipes")||!normalized.get("recipes").isJsonArray())return normalized;
        for(JsonElement row:normalized.getAsJsonArray("recipes")) {
            if(!row.isJsonObject())continue;
            JsonObject recipe=row.getAsJsonObject();
            if(!recipe.has("type")||!recipe.has("slots")||!recipe.get("slots").isJsonObject())continue;
            var type=RecipeTypeRegistry.get(recipe.get("type").getAsString());
            if(type.isEmpty())continue;
            JsonObject slots=recipe.getAsJsonObject("slots");
            for(var definition:type.get().slots()) {
                String key=definition.key();
                if(!definition.list()||!slots.has(key))continue;
                for(String existing:slots.keySet()) {
                    if(existing.startsWith(key)&&existing.length()>key.length()
                            &&existing.substring(key.length()).chars().allMatch(Character::isDigit))
                        throw new IOException("Ambiguous legacy/list slots: "+key+" and "+existing+"; nothing reloaded.");
                }
                JsonElement content=slots.remove(key);slots.add(key+"0",content);
            }
        }
        return normalized;
    }
    /** Merge objects recursively; recipe/removal arrays are keyed by UID. Other arrays are atomic. */
    public static JsonObject merge(JsonObject base, JsonObject memory, JsonObject disk) throws IOException {
        for(JsonObject project:List.of(base,memory,disk)) for(String field:List.of("recipes","removals")) {
            if(!project.has(field) || !project.get(field).isJsonArray()) throw new IOException("Missing project array: "+field);
            indexed(project.getAsJsonArray(field));
        }
        return value(base, memory, disk, "project").getAsJsonObject();
    }
    private static JsonElement cloneValue(JsonElement v) { return v == null ? null : v.deepCopy(); }
    private static JsonElement value(JsonElement b, JsonElement m, JsonElement d, String at) throws IOException {
        if (same(m, d)) return cloneValue(m);
        if (same(b, m)) return cloneValue(d);
        if (same(b, d)) return cloneValue(m);
        if (b != null && m != null && d != null && b.isJsonObject() && m.isJsonObject() && d.isJsonObject()) {
            JsonObject result = new JsonObject(); Set<String> keys = new LinkedHashSet<>();
            keys.addAll(b.getAsJsonObject().keySet()); keys.addAll(d.getAsJsonObject().keySet()); keys.addAll(m.getAsJsonObject().keySet());
            for (String k : keys) {
                JsonElement v = value(b.getAsJsonObject().get(k), m.getAsJsonObject().get(k), d.getAsJsonObject().get(k), at + "." + k);
                if (v != null) result.add(k, v);
            }
            return result;
        }
        if ((at.equals("project.recipes") || at.equals("project.removals")) && b != null && m != null && d != null && b.isJsonArray() && m.isJsonArray() && d.isJsonArray()) {
            JsonObject bm = indexed(b.getAsJsonArray()), mm = indexed(m.getAsJsonArray()), dm = indexed(d.getAsJsonArray());
            JsonObject merged = value(bm, mm, dm, at + ".byUid").getAsJsonObject();
            // Reordering existing cards on both sides is deliberately not silently resolved.
            List<String> common = bm.keySet().stream().filter(k -> mm.has(k) && dm.has(k)).toList();
            List<String> mo = mm.keySet().stream().filter(common::contains).toList(), dd = dm.keySet().stream().filter(common::contains).toList();
            if (!mo.equals(common) && !dd.equals(common) && !mo.equals(dd)) throw new IOException("Conflicting recipe order at " + at);
            Set<String> order = new LinkedHashSet<>();
            if (!mo.equals(common)) { order.addAll(mm.keySet()); order.addAll(dm.keySet()); }
            else { order.addAll(dm.keySet()); order.addAll(mm.keySet()); }
            JsonArray result = new JsonArray(); for (String k : order) if (merged.has(k)) result.add(merged.get(k));
            return result;
        }
        throw new IOException("Conflicting edits at " + at + "; resolve this field before refreshing.");
    }
    private static JsonObject indexed(JsonArray rows) throws IOException {
        JsonObject map = new JsonObject();
        for (JsonElement e : rows) {
            if (!e.isJsonObject() || !e.getAsJsonObject().has("uid")) throw new IOException("Missing recipe/removal UID.");
            String uid = e.getAsJsonObject().get("uid").getAsString();
            if (uid.isBlank() || map.has(uid)) throw new IOException("Duplicate/empty recipe/removal UID.");
            map.add(uid, e);
        }
        return map;
    }
}
