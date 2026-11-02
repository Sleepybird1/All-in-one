package dev.godpc.industrialcolonies.processing;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.util.Arrays;
import java.util.Random;
import java.util.UUID;

/** Pure Java 21 state-machine, safety-validation and categorical-roll tests; not a Minecraft runtime claim. */
public final class ProcessingRuntimeSelfTest {
    private static long assertions;
    private static int rejected;
    public static void main(String[] args) {
        manualSessions();
        configs();
        exclusiveRecovery();
        System.out.println("PROCESSING_RUNTIME_PURE PASS assertions=" + assertions + " invalidCases=" + rejected);
    }
    private static void manualSessions() {
        ManualWorkSessions work = new ManualWorkSessions();
        UUID a = new UUID(1, 1), b = new UUID(2, 2);
        var s1 = new ManualWorkSessions.Station("minecraft:overworld", 4);
        var s2 = new ManualWorkSessions.Station("minecraft:overworld", 8);
        var nether = new ManualWorkSessions.Station("minecraft:the_nether", 4);
        require(work.begin(a, s1, 10), "First station accepted");
        require(!work.begin(a, s2, 10), "Player cannot queue another station");
        require(!work.begin(b, s1, 10), "Station cannot take another player");
        require(work.begin(b, nether, 10), "Dimension isolates equal block position");
        require(work.size() == 2, "Two independent sessions");
        for (long tick = 10; tick < 1210; tick++) require(!ManualWorkSessions.finished(10, tick, 1200), "No early finish");
        require(ManualWorkSessions.finished(10, 1210, 1200), "Exactly sixty seconds");
        require(!ManualWorkSessions.finished(10, 9, 1200), "Time reversal cannot finish");
        work.cancel(a);
        require(work.get(a) == null && work.size() == 1, "Cancellation removes both reservation sides");
        require(work.begin(a, s1, 2000), "Restart has fresh start time");
        require(!ManualWorkSessions.finished(work.get(a).startedAt(), 2001, 1200), "Interrupted progress not retained");
        work.clear();
        require(work.size() == 0 && work.begin(b, s1, 3000), "Server stop clears station ownership");
        work.cancel(a); // No effect on another player's reservation.
        require(!work.begin(a, s1, 3000), "Unrelated logout cannot release another player's station");
        require(ManualWorkSessions.mayContinue(1, true, true, true, true, true, true), "Valid one-item attended frame");
        for (int count = 0; count <= 64; count++) {
            for (int flags = 0; flags < 64; flags++) {
                boolean actual = ManualWorkSessions.mayContinue(count, (flags & 1) != 0, (flags & 2) != 0,
                        (flags & 4) != 0, (flags & 8) != 0, (flags & 16) != 0, (flags & 32) != 0);
                require(actual == (count == 1 && flags == 63), "Count/burner/liveness/target/reach interruptions all fail closed");
            }
        }
        reject(() -> ManualWorkSessions.finished(0, 10, 0));
    }
    private static JsonObject defaults() {
        return JsonParser.parseString("{\"enabled\":true,\"heatingTicks\":1200,\"hammerCooldownTicks\":20,\"hammerDamage\":1,\"reach\":4.5,\"manualNoBatch\":true}").getAsJsonObject();
    }
    private static void configs() {
        ManualCinnabarConfig config = ManualCinnabarConfig.fromJson(defaults());
        require(config.heatingTicks() == 1200 && config.manualNoBatch(), "Default manual duration/nonbatch");
        for (String key : new String[]{"enabled", "heatingTicks", "hammerCooldownTicks", "hammerDamage", "reach", "manualNoBatch"}) {
            JsonObject missing = defaults(); missing.remove(key); reject(() -> ManualCinnabarConfig.fromJson(missing));
        }
        for (String key : new String[]{"heatingTicks", "hammerCooldownTicks", "hammerDamage"}) {
            for (double bad : new double[]{-1, 0, 0.5, Double.NaN, Double.POSITIVE_INFINITY, 1e20}) {
                JsonObject changed = defaults(); changed.addProperty(key, bad); reject(() -> ManualCinnabarConfig.fromJson(changed));
            }
            JsonObject text = defaults(); text.addProperty(key, "1200"); reject(() -> ManualCinnabarConfig.fromJson(text));
        }
        for (double bad : new double[]{-1, 0, 5.01, Double.NaN, Double.POSITIVE_INFINITY}) {
            JsonObject changed = defaults(); changed.addProperty("reach", bad); reject(() -> ManualCinnabarConfig.fromJson(changed));
        }
        JsonObject batching = defaults(); batching.addProperty("manualNoBatch", false); reject(() -> ManualCinnabarConfig.fromJson(batching));
        JsonObject text = defaults(); text.addProperty("manualNoBatch", "true"); reject(() -> ManualCinnabarConfig.fromJson(text));
        new ManualCinnabarConfig(true, 20, 1, 1, 1, true);
        new ManualCinnabarConfig(true, 72000, 1200, 100, 5, true);
        reject(() -> new ManualCinnabarConfig(true, 72001, 20, 1, 4.5, true));
        reject(() -> new ManualCinnabarConfig(true, 1200, 1201, 1, 4.5, true));
        reject(() -> new ManualCinnabarConfig(true, 1200, 20, 101, 4.5, true));
    }
    private static void exclusiveRecovery() {
        double[] weights = {.70, .25, .05};
        int[] exact = new int[3];
        for (int i = 0; i < 10000; i++) exact[ExclusiveRecovery.select(1, weights, 0, (i + .5) / 10000)]++;
        require(Arrays.equals(exact, new int[]{7000, 2500, 500}), "Exact categorical 70/25/5 interval partition");
        require(ExclusiveRecovery.select(1, weights, 0, 0) == 0, "First interval");
        require(ExclusiveRecovery.select(1, weights, 0, .7) == 1, "70% boundary starts platinum");
        require(ExclusiveRecovery.select(1, weights, 0, .95) == 2, "95% boundary starts iridium");
        require(ExclusiveRecovery.select(.25, weights, .25, 0) == -1, "Recovery boundary fails");
        Random random = new Random(0xC011AB4L);
        int[] counts = new int[4];
        for (int i = 0; i < 600000; i++) {
            int result = ExclusiveRecovery.select(.20, weights, random.nextDouble(), random.nextDouble());
            require(result >= -1 && result <= 2, "One category or no recovery, never independent multi-output rolls");
            counts[result + 1]++;
            require(ExclusiveRecovery.select(0, weights, random.nextDouble(), random.nextDouble()) == -1, "Zero recovery yields nothing");
        }
        require(Math.abs(counts[0] / 600000d - .80) < .005, "Crude recovery rate");
        int success = 600000 - counts[0];
        require(Math.abs(counts[1] / (double) success - .70) < .005, "Osmium share");
        require(Math.abs(counts[2] / (double) success - .25) < .005, "Platinum share");
        require(Math.abs(counts[3] / (double) success - .05) < .005, "Iridium share");
        for (double chance : new double[]{-1, 1.01, Double.NaN, Double.POSITIVE_INFINITY}) reject(() -> ExclusiveRecovery.validate(chance, weights));
        for (double[] bad : new double[][]{{}, {0, 0, 0}, {.7, .25, .06}, {.7, .25, -.05}, {Double.NaN, 1}, new double[10]})
            reject(() -> ExclusiveRecovery.validate(1, bad));
        reject(() -> ExclusiveRecovery.select(1, weights, 1, 0));
        reject(() -> ExclusiveRecovery.select(1, weights, 0, 1));
        require(ExclusiveRecovery.select(1, new double[]{0, 1, 0}, 0, 0) == 1, "Zero-weight categories never selected");
    }
    private static void require(boolean condition, String message) { assertions++; if (!condition) throw new AssertionError(message); }
    private static void reject(Runnable action) {
        try { action.run(); } catch (RuntimeException expected) { rejected++; assertions++; return; }
        throw new AssertionError("Invalid case was silently accepted");
    }
}
