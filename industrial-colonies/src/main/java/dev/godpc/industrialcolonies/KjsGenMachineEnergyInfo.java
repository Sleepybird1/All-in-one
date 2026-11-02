package dev.godpc.industrialcolonies;

import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeDefinition;
import java.math.BigDecimal;
import java.nio.file.Files;
import java.nio.file.Path;
import java.text.DecimalFormat;
import java.text.DecimalFormatSymbols;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.regex.Pattern;

/** Read-only native recipe facts. These values never become recipe parameters. */
public final class KjsGenMachineEnergyInfo {
    private KjsGenMachineEnergyInfo() {}
    public record Row(String label, String value, String explanation) {}
    public record Settings(Map<String, BigDecimal> values, String source) {
        public Settings { values = Map.copyOf(values); }
        public Optional<BigDecimal> value(String key) {
            return Optional.ofNullable(values.get(key)).filter(v -> v.signum() >= 0);
        }
    }
    private static final Map<String, String> MEK_USAGE = Map.ofEntries(
        Map.entry("enriching", "enrichmentChamber"), Map.entry("compressing", "osmiumCompressor"),
        Map.entry("combining", "combiner"), Map.entry("crushing", "crusher"),
        Map.entry("metallurgic_infusing", "metallurgicInfuser"), Map.entry("purifying", "purificationChamber"),
        Map.entry("smelting", "energizedSmelter"), Map.entry("rotary", "rotaryCondensentrator"),
        Map.entry("oxidizing", "chemicalOxidizer"), Map.entry("chemical_infusing", "chemicalInfuser"),
        Map.entry("injecting", "chemicalInjectionChamber"), Map.entry("sawing", "precisionSawmill"),
        Map.entry("dissolution", "chemicalDissolutionChamber"), Map.entry("washing", "chemicalWasher"),
        Map.entry("crystallizing", "chemicalCrystallizer"), Map.entry("reaction", "pressurizedReactionBase"),
        Map.entry("centrifuging", "isotopicCentrifuge"), Map.entry("nucleosynthesizing", "antiprotonicNucleosynthesizer"),
        Map.entry("pigment_extracting", "pigmentExtractor"), Map.entry("pigment_mixing", "pigmentMixer"),
        Map.entry("painting", "paintingMachine"));
    // Constants verified in the installed 10.7.19.85 classes. Unlisted families remain machine-dependent.
    private static final Map<String, Integer> MEK_TICKS = Map.ofEntries(
        Map.entry("compressing", 200),
        Map.entry("crystallizing", 200), Map.entry("dissolution", 100), Map.entry("oxidizing", 100),
        Map.entry("combining", 200), Map.entry("metallurgic_infusing", 200), Map.entry("painting", 200),
        Map.entry("pigment_extracting", 100), Map.entry("sawing", 200), Map.entry("chemical_infusing", 1));

    /** Prefer loaded native settings; file values are explicitly a local baseline when unavailable. */
    public static Settings loadSettings(Path configDirectory) {
        Map<String, BigDecimal> result = new LinkedHashMap<>();
        for (String key : MEK_USAGE.values()) readNumber(configDirectory.resolve("Mekanism/machine-usage.toml"), key)
            .ifPresent(v -> result.put("mek." + key, v));
        readNumber(configDirectory.resolve("tfmg-common.toml"), "electrolysisMinimumCurrent")
            .ifPresent(v -> result.put("tfmg.minimumCurrent", v));
        boolean loadedMek = false, loadedTfmg = false;
        try {
            Object usage = Class.forName("mekanism.common.config.MekanismConfig").getField("usage").get(null);
            for (String key : MEK_USAGE.values()) {
                Object cached = usage.getClass().getField(key).get(usage);
                BigDecimal value = new BigDecimal(cached.getClass().getMethod("get").invoke(cached).toString());
                if (value.signum() >= 0) result.put("mek." + key, value);
            }
            loadedMek = true;
        } catch (ReflectiveOperationException | LinkageError | RuntimeException unavailable) {
            // No native bootstrap is attempted by the caller; missing loaded data uses the labeled file baseline.
        }
        try {
            Object server = Class.forName("com.drmangotea.tfmg.config.TFMGConfigs").getMethod("common").invoke(null);
            Object machines = server.getClass().getField("machines").get(server);
            Object cached = machines.getClass().getField("electrolysisMinimumCurrent").get(machines);
            BigDecimal value = new BigDecimal(cached.getClass().getMethod("get").invoke(cached).toString());
            if (value.signum() >= 0) result.put("tfmg.minimumCurrent", value);
            loadedTfmg = true;
        } catch (ReflectiveOperationException | LinkageError | RuntimeException unavailable) {
            // See the source label below; never substitute an invented power cost.
        }
        return new Settings(result, "Mekanism: " + (loadedMek ? "loaded settings" : "local config baseline")
            + "; TFMG: " + (loadedTfmg ? "loaded settings" : "local config baseline"));
    }
    private static Optional<BigDecimal> readNumber(Path file, String key) {
        try {
            var matcher = Pattern.compile("(?m)^\\s*" + Pattern.quote(key)
                + "\\s*=\\s*([0-9]+(?:\\.[0-9]+)?)\\s*(?:#.*)?$").matcher(Files.readString(file));
            return matcher.find() ? Optional.of(new BigDecimal(matcher.group(1))) : Optional.empty();
        } catch (java.io.IOException | NumberFormatException unavailable) { return Optional.empty(); }
    }

    public static List<Row> describe(RecipeInstance recipe, RecipeTypeDefinition type, Settings settings) {
        String id = type.id(), mod = type.modId();
        String source = settings.source() + ". Base values exclude upgrades, catalysts and extra infrastructure.";
        if (KjsGenVatCompatibility.vat(id)) return vat(recipe, type, settings);
        if (id.equals("industrial_colonies:tfmg_polarizing")) {
            TfmgPolarizerCodegen.ElectricalSettings electrical;
            try { electrical=TfmgPolarizerCodegen.electricalSettings(recipe); }
            catch (IllegalArgumentException invalid) { return rows("Invalid time", "TFMG electricity", "Invalid power", "Not exportable", invalid.getMessage()); }
            if (electrical.custom() || electrical.legacyAtm()) return rows(
                electrical.ticks()+" powered ticks ("+(electrical.ticks()/20.0)+" s)", "TFMG electricity",
                ">="+format(BigDecimal.valueOf(electrical.power()))+" native power",
                ">="+((long)electrical.ticks()*electrical.power())+" native power-ticks",
                (electrical.custom()?"Editable power_required and processing_time are serialized, synchronized and enforced exactly. ":"Legacy ATM fallback; set positive Power Required to use fully editable per-recipe values. ")
                    +"Active resistance adapts to the requested load, capped at native30 ohms. Native1000V safety is unchanged; underpowered/overloaded ticks do not count. "
                    +"Input and full recipe, including power, bind saved charge. Actual sources/network determine resource use; this is not a fixed FE bill.");
            return rows("200 charge ticks (10 s)", "TFMG electricity", ">=2,000 native power", "Voltage-dependent",
                "Native recipes without explicit custom power/time keep their stock cycle. Edit power/time to create a real per-recipe electrical recipe; energy type stays TFMG electricity.");
        }
        if (id.startsWith("industrial_colonies:nuclearcraft_")
                && type.parameter("energyPerTick").isPresent() && type.parameter("processTime").isPresent()) {
            var ticks = number(recipe, type, "processTime", false);
            var rate = number(recipe, type, "energyPerTick", false);
            return rows(time(ticks), "Forge Energy (FE)", amount(rate, " FE/t base"), total(rate, ticks, " FE base"),
                "Native recipe energy_per_tick and process_time. Their editable controls remain below. "
                    + "The product is a base recipe budget; configuration, speed/energy upgrades, catalyst and tick rounding may change actual consumption.");
        }
        if (id.startsWith("kjsgen:mekanism_") || id.startsWith("industrial_colonies:mekanism_")) {
            String family = id.substring(id.indexOf("mekanism_") + "mekanism_".length());
            if (family.equals("energy_conversion")) {
                var energy = number(recipe, type, "energy", false);
                return rows("Item conversion", "Stored energy (J)", amount(energy, " J produced"), "Produces energy",
                    "This recipe defines an item's energy value, not machine power consumption. Its native unit is Mekanism joules.");
            }
            if (family.equals("chemical_conversion")) return rows("Item conversion", "No standalone machine", "No recipe power charge", "Slot conversion",
                "Defines an item-to-chemical conversion in a machine input slot. The consuming machine has its own operating energy.");
            if (family.equals("activating") || family.equals("evaporating")) return rows("Environment-dependent",
                family.equals("activating") ? "Solar radiation" : "Heat", "World/machine conditions", "Not a fixed electrical bill",
                "The native recipe does not carry a per-recipe duration or electrical charge; environmental conditions govern throughput.");
            Optional<BigDecimal> ticks = type.parameter("duration").isPresent()
                ? number(recipe, type, "duration", false)
                : Optional.ofNullable(MEK_TICKS.get(family)).map(BigDecimal::valueOf);
            Optional<BigDecimal> rate = Optional.ofNullable(MEK_USAGE.get(family)).flatMap(k -> settings.value("mek." + k));
            String detail = source + " Mekanism energy is joules (J); it is not FE. ";
            if (family.equals("reaction")) {
                var extra = number(recipe, type, "energyRequired", true);
                rate = rate.isPresent() && extra.isPresent() ? Optional.of(rate.get().add(extra.get())) : Optional.empty();
                detail += "PRC energyRequired is additional J per processing tick, added to pressurizedReactionBase; duration is native recipe ticks. ";
            }
            if (family.equals("separating")) detail += "The native separating recipe energyMultiplier scales its machine cost; no arbitrary energy type is supported. ";
            if (ticks.isEmpty()) detail += "This family has a machine/throughput-controlled cycle; no unverified fixed total is asserted. ";
            return rows(time(ticks), "Mekanism joules (J)", amount(rate, " J/t base"), total(rate, ticks, " J base"), detail);
        }
        if (id.contains("modernfoundry") && (id.contains("casting_table") || id.contains("casting_basin"))) {
            String key = type.parameter("coolingTime").isPresent() ? "coolingTime" : "cooling_time";
            return rows(time(number(recipe, type, key, false)), "Passive cooling", "No electrical recipe charge", "Heat/cooling cycle",
                "Casting uses the native cooling time and previously molten feed. Upstream melting/heating is a separate cost.");
        }
        if (mod.equals("create") || id.startsWith("kjsgen:create_") || id.startsWith("create:")) return rows(
            "Native machine cycle", "Kinetic / heat by machine", "RPM / stress / heat source", "Machine-dependent",
            "Create uses native kinetic stress and speed, and heat where the process requires it. SU is a capacity/load measure, not an energy-per-recipe unit; no FE conversion or ignored duration is invented.");
        if (mod.equals("tfmg") || id.contains(":tfmg_")) return rows("Native machine cycle", "TFMG machine power",
            "Machine/configuration-dependent", "No fixed recipe energy field",
            "This environment keeps its machine's native energy system. Its recipe does not supply a qualified, editable energy budget.");
        return List.of();
    }

    private static List<Row> vat(RecipeInstance recipe, RecipeTypeDefinition type, Settings settings) {
        String drive = effective(recipe, type, "attachmentDrive"), electrode = effective(recipe, type, "electrodeType");
        var count = decimal(effective(recipe, type, "electrodeCount"), true);
        boolean kinetic = drive.equals("Mixer") || drive.equals("Centrifuge");
        boolean electric = count.isPresent() && count.get().signum() > 0;
        String energy = electric ? (kinetic ? "Kinetic + TFMG electricity" : "TFMG electricity")
            : kinetic ? "Kinetic shaft power" : "Heat / passive process";
        String rate = electric ? "Electrode/voltage-dependent" : kinetic ? "SU depends on RPM" : "No powered attachment";
        if (electric && electrode.equals("Graphite")) {
            var minimum = settings.value("tfmg.minimumCurrent");
            if (minimum.isPresent()) rate = ">=" + format(minimum.get().pow(2).multiply(BigDecimal.valueOf(300)).multiply(count.get())) + " native power";
        }
        return rows(time(number(recipe, type, "processingTime", false)), energy, rate,
            electric ? "Voltage/time-dependent" : kinetic ? "No fixed SU energy bill" : "Heat/fuel separate",
            "processingTime is native eligible processing ticks (20 ticks = 1 nominal second); loss of power/heat can pause it. "
                + settings.source() + ". Graphite resistance is300; minimum rated load is count * resistance * minimumCurrent^2. "
                + "Actual load depends on operating voltage/current and network updates, and is not an enforced fixed FE-per-recipe charge. "
                + "The mixer/centrifuge also needs native kinetic drive. Energy type follows attachments and cannot be freely changed.");
    }
    private static String effective(RecipeInstance recipe, RecipeTypeDefinition type, String key) {
        String legacy = KjsGenVatCompatibility.legacyParameter(recipe, key);
        return legacy == null ? recipe.param(type, key) : legacy;
    }
    private static List<Row> rows(String time, String energy, String rate, String total, String details) {
        return List.of(new Row("Time", time, details), new Row("Energy", energy, details),
            new Row("Rate", rate, details), new Row("Cost", total, details));
    }
    private static Optional<BigDecimal> number(RecipeInstance r, RecipeTypeDefinition t, String key, boolean allowZero) {
        return decimal(r.param(t, key), allowZero);
    }
    private static Optional<BigDecimal> decimal(String value, boolean allowZero) {
        try {
            if (value == null || !value.matches("[0-9]+")) return Optional.empty();
            BigDecimal parsed = new BigDecimal(value);
            return parsed.signum() > 0 || allowZero && parsed.signum() == 0 ? Optional.of(parsed) : Optional.empty();
        } catch (NumberFormatException invalid) { return Optional.empty(); }
    }
    private static String time(Optional<BigDecimal> ticks) {
        return ticks.map(v -> format(v) + " t (" + format(v.divide(BigDecimal.valueOf(20))) + " s base)")
            .orElse("Machine-controlled / invalid value");
    }
    private static String amount(Optional<BigDecimal> value, String unit) {
        return value.map(v -> format(v) + unit).orElse("Machine/configuration-dependent");
    }
    private static String total(Optional<BigDecimal> rate, Optional<BigDecimal> ticks, String unit) {
        return rate.isPresent() && ticks.isPresent() ? format(rate.get().multiply(ticks.get())) + unit : "Machine-dependent";
    }
    private static String format(BigDecimal value) {
        return new DecimalFormat("#,##0.###", DecimalFormatSymbols.getInstance(Locale.ROOT)).format(value);
    }
}
