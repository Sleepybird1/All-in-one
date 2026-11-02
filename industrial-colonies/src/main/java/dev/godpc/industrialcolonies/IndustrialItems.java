package dev.godpc.industrialcolonies;

import net.minecraft.world.item.Item;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.BucketItem;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.PickaxeItem;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.tags.BlockTags;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.common.SimpleTier;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Items that exist specifically to express the pack's research progression. */
public final class IndustrialItems {
    private static final DeferredRegister.Items ITEMS =
            DeferredRegister.createItems(IndustrialColonies.MOD_ID);

    public static final DeferredItem<BlockItem> MATTER_STABILIZER =
            ITEMS.registerSimpleBlockItem("matter_stabilizer", IndustrialBlocks.MATTER_STABILIZER);

    public static final DeferredItem<AssemblyWorkpieceItem> ASSEMBLY_WORKPIECE =
            ITEMS.registerItem("assembly_workpiece", AssemblyWorkpieceItem::new);

    public static final DeferredItem<Item> PREPARED_SILICON_WAFER =
            ITEMS.registerSimpleItem("prepared_silicon_wafer");
    public static final DeferredItem<Item> ETCHED_SILICON_WAFER =
            ITEMS.registerSimpleItem("etched_silicon_wafer");
    public static final DeferredItem<Item> PRECISION_WAFER_MASK = ITEMS.registerSimpleItem("precision_wafer_mask");
    public static final DeferredItem<Item> PATTERNED_SILICON_WAFER = ITEMS.registerSimpleItem("patterned_silicon_wafer");
    public static final DeferredItem<Item> ANNEALED_SILICON_WAFER = ITEMS.registerSimpleItem("annealed_silicon_wafer");
    public static final DeferredItem<Item> COPPER_CONTACT_FRAME = ITEMS.registerSimpleItem("copper_contact_frame");
    public static final DeferredItem<Item> GOLD_BONDING_WIRE = ITEMS.registerSimpleItem("gold_bonding_wire");

    /** Physical authorization computer required aboard a Cosmonautics ship. */
    public static final DeferredItem<BlockItem> ORBITAL_FLIGHT_COMPUTER =
            ITEMS.registerSimpleBlockItem(
                    "orbital_flight_computer",
                    IndustrialBlocks.ORBITAL_FLIGHT_COMPUTER);

    /** Physical Mars-descent authorization computer installed aboard a ship. */
    public static final DeferredItem<BlockItem> MARS_NAVIGATION_COMPUTER =
            ITEMS.registerSimpleBlockItem(
                    "mars_navigation_computer",
                    IndustrialBlocks.MARS_NAVIGATION_COMPUTER);

    /** Physical Venus-descent authorization computer installed aboard a ship. */
    public static final DeferredItem<BlockItem> VENUS_NAVIGATION_COMPUTER =
            ITEMS.registerSimpleBlockItem(
                    "venus_navigation_computer",
                    IndustrialBlocks.VENUS_NAVIGATION_COMPUTER);

    /** Physical Mercury-descent authorization computer installed aboard a ship. */
    public static final DeferredItem<BlockItem> MERCURY_NAVIGATION_COMPUTER =
            ITEMS.registerSimpleBlockItem(
                    "mercury_navigation_computer",
                    IndustrialBlocks.MERCURY_NAVIGATION_COMPUTER);

    /** Final physical route computer; also signs the exact Sol/Glacio crystal. */
    public static final DeferredItem<BlockItem> INTERSTELLAR_NAVIGATION_COMPUTER =
            ITEMS.registerSimpleBlockItem(
                    "interstellar_navigation_computer",
                    IndustrialBlocks.INTERSTELLAR_NAVIGATION_COMPUTER);

    /** Physical station controller; the block itself stores commissioning state. */
    public static final DeferredItem<BlockItem> STATION_SERVICES_CONTROLLER =
            ITEMS.registerSimpleBlockItem(
                    "station_services_controller",
                    IndustrialBlocks.STATION_SERVICES_CONTROLLER);

    /** Station-only atmospheric extraction machine. */
    public static final DeferredItem<BlockItem> ATMOSPHERIC_SCOOP =
            ITEMS.registerSimpleBlockItem(
                    "atmospheric_scoop",
                    IndustrialBlocks.ATMOSPHERIC_SCOOP);

    /** Portable one-bucket proof of physical gas-giant extraction. */
    public static final DeferredItem<BucketItem> GAS_GIANT_CONDENSATE_BUCKET =
            ITEMS.register(
                    "gas_giant_condensate_bucket",
                    () -> new BucketItem(
                            IndustrialFluids.GAS_GIANT_CONDENSATE.get(),
                            new Item.Properties()
                                    .craftRemainder(Items.BUCKET)
                                    .stacksTo(1)
                                    .rarity(Rarity.RARE)));

    /** Physical Earth-return ancestor for the future Warp Drive charge. */
    public static final DeferredItem<Item> WARP_CHARGE_PRECURSOR =
            ITEMS.registerSimpleItem(
                    "warp_charge_precursor",
                    new Item.Properties().stacksTo(1).fireResistant().rarity(Rarity.EPIC));

    /** Single-use physical charge consumed when a signed warp begins. */
    public static final DeferredItem<Item> INTERSTELLAR_WARP_CHARGE =
            ITEMS.registerSimpleItem(
                    "interstellar_warp_charge",
                    new Item.Properties().stacksTo(1).fireResistant().rarity(Rarity.EPIC));

    /**
     * A reusable shipyard plan after the Orbital Flight Computer has signed
     * its guidance envelope. The computer is a retained Deployer tool, so the
     * physical block item remains available for installation aboard the ship.
     */
    public static final DeferredItem<Item> GUIDANCE_CERTIFIED_PLAN =
            ITEMS.registerSimpleItem(
                    "guidance_certified_plan",
                    new Item.Properties().stacksTo(1));

    /**
     * The same shipyard plan after a completed Thruster Mount has certified
     * its load path. The mount is retained for installation on the vessel.
     */
    public static final DeferredItem<Item> PROPULSION_CERTIFIED_PLAN =
            ITEMS.registerSimpleItem(
                    "propulsion_certified_plan",
                    new Item.Properties().stacksTo(1));

    /**
     * Deliberately poor but softlock-safe first mining tier.
     *
     * <p>It can harvest everything a stone tool can, including the copper and
     * iron needed to enter the pack's real metallurgy/tool-building path, but
     * its 48 uses and low mining speed make it an emergency implement rather
     * than a tool worth keeping.</p>
     */
    private static final Tier CRUDE_FLINT_TIER = new SimpleTier(
            BlockTags.INCORRECT_FOR_STONE_TOOL,
            48,
            2.5F,
            0.0F,
            1,
            () -> Ingredient.of(Items.FLINT));

    public static final DeferredItem<PickaxeItem> CRUDE_FLINT_PICKAXE =
            ITEMS.register(
                    "crude_flint_pickaxe",
                    () -> new PickaxeItem(
                            CRUDE_FLINT_TIER,
                            new Item.Properties().attributes(
                                    PickaxeItem.createAttributes(
                                            CRUDE_FLINT_TIER,
                                            0.5F,
                                            -3.2F))));

    /**
     * A construction-grade intermediate produced at Yellorium Refinement.
     *
     * <p>Extreme Reactors only registers {@code bigreactors:yellorium_dust}
     * when Thermal is installed. The target pack does not include Thermal, so
     * relying on that optional compatibility item makes every pre-fuel nuclear
     * construction recipe invalid. This owned item keeps the intended split:
     * Yellorium ingots and compound are structural alloy forms and only the
     * later enriched uranium pellet is reactor fuel.</p>
     */
    public static final DeferredItem<Item> YELLORIUM_COMPOUND =
            ITEMS.registerSimpleItem("yellorium_compound");

    /**
     * A solid reactor charge crystallized from one full bucket-equivalent of
     * Mekanism Fissile Fuel.
     *
     * <p>Extreme Reactors' generic Yellorium and uranium source tags are
     * removed by the pack configuration. Only the dedicated item tag that
     * contains this pellet maps to the first-tier reactor reactant, keeping
     * early manufactured Yellorium alloy structural rather than fuel.</p>
     */
    public static final DeferredItem<Item> ENRICHED_URANIUM_FUEL_PELLET =
            ITEMS.registerSimpleItem(
                    "enriched_uranium_fuel_pellet",
                    new Item.Properties().fireResistant().rarity(Rarity.RARE));

    /*
     * Source-owned planetary metallurgy intermediates.  Ad Astra supplies the
     * raw ores and finished metals; these stacks make the physical crushing,
     * enrichment, leaching, and electrode-reduction stages explicit without
     * replacing its canonical ingot, nugget, block, or plate identities.
     */
    public static final DeferredItem<Item> DESH_GRIT =
            ITEMS.registerSimpleItem("desh_grit");
    public static final DeferredItem<Item> DESH_CONCENTRATE =
            ITEMS.registerSimpleItem("desh_concentrate");
    public static final DeferredItem<Item> DESH_LEACHED_COMPOUND =
            ITEMS.registerSimpleItem("desh_leached_compound");
    public static final DeferredItem<Item> OSTRUM_GRIT =
            ITEMS.registerSimpleItem("ostrum_grit");
    public static final DeferredItem<Item> OSTRUM_CONCENTRATE =
            ITEMS.registerSimpleItem("ostrum_concentrate");
    public static final DeferredItem<Item> OSTRUM_LEACHED_COMPOUND =
            ITEMS.registerSimpleItem("ostrum_leached_compound");
    public static final DeferredItem<Item> CALORITE_GRIT =
            ITEMS.registerSimpleItem("calorite_grit");
    public static final DeferredItem<Item> CALORITE_CONCENTRATE =
            ITEMS.registerSimpleItem("calorite_concentrate");
    public static final DeferredItem<Item> CALORITE_LEACHED_COMPOUND =
            ITEMS.registerSimpleItem("calorite_leached_compound");

    /*
     * Unique, unobtainable intermediate stacks for the ComputerCraft factory
     * sequences. Reusing one of Create's generic incomplete items would let a
     * partially assembled cheap component enter an unrelated late-game
     * sequence. Keeping one transitional item per recipe makes every assembly
     * lane closed and deterministic.
     */
    public static final DeferredItem<Item> UNFINISHED_COMPUTERCRAFT_CABLE =
            ITEMS.registerSimpleItem("unfinished_computercraft_cable", new Item.Properties().stacksTo(1));
    public static final DeferredItem<Item> UNFINISHED_COMPUTERCRAFT_WIRED_MODEM =
            ITEMS.registerSimpleItem("unfinished_computercraft_wired_modem", new Item.Properties().stacksTo(1));
    public static final DeferredItem<Item> UNFINISHED_COMPUTERCRAFT_WIRELESS_MODEM =
            ITEMS.registerSimpleItem("unfinished_computercraft_wireless_modem", new Item.Properties().stacksTo(1));
    public static final DeferredItem<Item> UNFINISHED_COMPUTERCRAFT_SPEAKER =
            ITEMS.registerSimpleItem("unfinished_computercraft_speaker", new Item.Properties().stacksTo(1));
    public static final DeferredItem<Item> UNFINISHED_COMPUTERCRAFT_REDSTONE_RELAY =
            ITEMS.registerSimpleItem("unfinished_computercraft_redstone_relay", new Item.Properties().stacksTo(1));
    public static final DeferredItem<Item> UNFINISHED_COMPUTERCRAFT_ADVANCED_WIRELESS_MODEM =
            ITEMS.registerSimpleItem(
                    "unfinished_computercraft_advanced_wireless_modem",
                    new Item.Properties().stacksTo(1));
    public static final DeferredItem<Item> UNFINISHED_COMPUTERCRAFT_ADVANCED_COMPUTER =
            ITEMS.registerSimpleItem(
                    "unfinished_computercraft_advanced_computer",
                    new Item.Properties().stacksTo(1));
    public static final DeferredItem<Item> UNFINISHED_COMPUTERCRAFT_ADVANCED_MONITOR =
            ITEMS.registerSimpleItem(
                    "unfinished_computercraft_advanced_monitor",
                    new Item.Properties().stacksTo(1));
    public static final DeferredItem<Item> UNFINISHED_COMPUTERCRAFT_ADVANCED_POCKET_COMPUTER =
            ITEMS.registerSimpleItem(
                    "unfinished_computercraft_advanced_pocket_computer",
                    new Item.Properties().stacksTo(1));
    public static final DeferredItem<Item> UNFINISHED_COMPUTERCRAFT_ADVANCED_TURTLE =
            ITEMS.registerSimpleItem(
                    "unfinished_computercraft_advanced_turtle",
                    new Item.Properties().stacksTo(1));

    /** Closed transitional stack for the Applied Create stress-buffer assembly line. */
    public static final DeferredItem<Item> UNFINISHED_STRESS_STORAGE_COMPONENT =
            ITEMS.registerSimpleItem(
                    "unfinished_stress_storage_component",
                    new Item.Properties().stacksTo(1));

    /** Closed transitional stack for the four-layer 1M MEGA cell assembly line. */
    public static final DeferredItem<Item> UNFINISHED_MEGA_CELL_COMPONENT_1M =
            ITEMS.registerSimpleItem(
                    "unfinished_mega_cell_component_1m",
                    new Item.Properties().stacksTo(1));

    /**
     * A post-nuclear megaproject component that represents compressed mass.
     *
     * <p>Its recipe consumes nine different 9x AllTheCompressed bulk-material
     * blocks. Keeping the artifact in this mod makes it a stable FTB Quests
     * target while AllTheCompressed remains responsible only for expressing
     * the enormous raw-mass requirement.</p>
     */
    public static final DeferredItem<Item> BLACK_HOLE =
            ITEMS.registerSimpleItem(
                    "black_hole",
                    new Item.Properties().stacksTo(1).fireResistant().rarity(Rarity.EPIC));

    /** Transitional item used only while the reserve core is being assembled. */
    public static final DeferredItem<Item> UNFINISHED_INDUSTRIAL_RESERVE_CORE =
            ITEMS.registerSimpleItem(
                    "unfinished_industrial_reserve_core",
                    new Item.Properties().stacksTo(1));

    /**
     * Physical proof that the fuel, acid, polymer, and actinide factories can
     * sustain megaproject-scale throughput.
     */
    public static final DeferredItem<Item> INDUSTRIAL_RESERVE_CORE =
            ITEMS.registerSimpleItem(
                    "industrial_reserve_core",
                    new Item.Properties().stacksTo(1).fireResistant().rarity(Rarity.EPIC));

    /**
     * The capstone artifact for the base pack's industrial progression.
     *
     * <p>The Industrial Star consumes the Black Hole, the Industrial Reserve
     * Core, and every manufactured Allthemodium alloy family. Future expansion
     * chapters can use it as the launch point for orbital progression.</p>
     */
    public static final DeferredItem<Item> INDUSTRIAL_STAR =
            ITEMS.registerSimpleItem(
                    "industrial_star",
                    new Item.Properties().stacksTo(1).fireResistant().rarity(Rarity.EPIC));

    private IndustrialItems() {
    }

    public static void register(IEventBus modEventBus) {
        ITEMS.register(modEventBus);
    }
}
