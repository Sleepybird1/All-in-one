#!/usr/bin/env python3
"""Late-game mechanical-grid redesigns for recipe design v2.

The seed's first late-game pass often used a dense, mirrored 5x5 perimeter as
a substitute for difficulty.  This module keeps large-grid crafting for
assemblies whose physical scale warrants it, but makes the grid describe the
object: control faces, fluid vessels, manifolds, consoles, door frames,
satellites, field coils, scoops, and drive cores.  Small ports, personal gear,
sensors, vents, and a single-block liquifier are reduced to focused 3x3
mechanical assemblies.

Only ``comment``, ``pattern``, and ``key`` are changed.  Output, node, phase,
order, removals, exclusivity, dependencies, and conditional metadata remain
owned by the seed entry and are preserved verbatim.
"""

from __future__ import annotations

from typing import Any


TARGET_PHASES = {
    "Nuclear Engineering",
    "Orbital Engineering",
    "Planetary Industry",
    "Outer System Industry",
    "Interstellar Escape",
}


def _grid(comment: str, pattern: list[str], key: dict[str, str]) -> dict[str, Any]:
    if not pattern:
        raise ValueError("Mechanical grid must contain at least one row")
    width = len(pattern[0])
    if width < 1 or width > 5 or len(pattern) > 5:
        raise ValueError(f"Mechanical grid exceeds the 5x5 editor: {pattern!r}")
    if any(len(row) != width for row in pattern):
        raise ValueError(f"Mechanical grid must be rectangular: {pattern!r}")
    used = set("".join(pattern)) - {" "}
    defined = set(key)
    if used != defined:
        raise ValueError(
            f"Mechanical grid symbols do not match key: "
            f"missing={sorted(used - defined)}, unused={sorted(defined - used)}"
        )
    return {"comment": comment, "pattern": pattern, "key": key}


_REDESIGNS: dict[str, dict[str, Any]] = {
    # ------------------------------------------------------------------
    # Nuclear Engineering
    # ------------------------------------------------------------------
    "industrial_colonies:nuclear/basic_reactor_controller": _grid(
        "Build a five-wide reactor control console: open monitor rail, engineering logic, redstone interlock, operator computer, and one elite safety controller on a restrained reactor-casing frame",
        [
            " M M ",
            "BEREB",
            "BRCRB",
            "  A  ",
            " BBB ",
        ],
        {
            "B": "bigreactors:basic_reactorcasing",
            "M": "computercraft:monitor_advanced",
            "E": "ae2:engineering_processor",
            "R": "computercraft:redstone_relay",
            "C": "computercraft:computer_advanced",
            "A": "mekanism:elite_control_circuit",
        },
    ),
    "industrial_colonies:nuclear/basic_reactor_power_tap": _grid(
        "Assemble the reactor power tap as a compact transformer interface between the reactor casing, accumulator, engineering governor, and grid connector",
        [
            "BCB",
            "TAG",
            "BTB",
        ],
        {
            "B": "bigreactors:basic_reactorcasing",
            "C": "electroenergetics:connector",
            "T": "tfmg:transformer",
            "A": "electroenergetics:accumulator",
            "G": "ae2:engineering_processor",
        },
    ),
    "industrial_colonies:nuclear/reinforced_reactor_controller": _grid(
        "Rebuild the proven basic controller into a reinforced console with radiance shielding, redundant ultimate interlocks, engineering logic, monitors, and a dedicated operator computer",
        [
            " RMR ",
            "RUEUR",
            "M B M",
            "R C R",
            " RQR ",
        ],
        {
            "R": "bigreactors:reinforced_reactorcasing",
            "M": "computercraft:monitor_advanced",
            "U": "mekanism:ultimate_control_circuit",
            "E": "ae2:engineering_processor",
            "B": "bigreactors:basic_reactorcontroller",
            "C": "computercraft:computer_advanced",
            "Q": "create:refined_radiance_casing",
        },
    ),
    "industrial_colonies:nuclear/reinforced_computer_port": _grid(
        "Build a focused reinforced network port from a hardened shell, wired modem crossbar, ultimate interface controller, and one advanced host computer",
        [
            "RWR",
            "WUW",
            "RCR",
        ],
        {
            "R": "bigreactors:reinforced_reactorcasing",
            "W": "computercraft:wired_modem",
            "U": "mekanism:ultimate_control_circuit",
            "C": "computercraft:computer_advanced",
        },
    ),
    "industrial_colonies:bigreactors/energizer/controller": _grid(
        "Lay out the Energizer control cabinet as a monitored high-voltage path with transformer and capacitor banks feeding a computer, elite interlock, engineering governor, and Energizer casing core",
        [
            " RMR ",
            "RTPTR",
            "MUCUM",
            "R E R",
            " RAR ",
        ],
        {
            "R": "create:refined_radiance_casing",
            "M": "computercraft:monitor_advanced",
            "T": "tfmg:transformer",
            "P": "tfmg:capacitor_item",
            "U": "mekanism:elite_control_circuit",
            "C": "computercraft:computer_advanced",
            "E": "ae2:engineering_processor",
            "A": "bigreactors:energizercasing",
        },
    ),
    "industrial_colonies:bigreactors/fluidizer/controller": _grid(
        "Build the Fluidizer console around a visible three-vat process bank, paired electric pumps, computerized control, a Fluidizer casing core, and redundant elite chemical interlocks",
        [
            " RMR ",
            "RVVVR",
            "MPCPM",
            "RUAUR",
            " RER ",
        ],
        {
            "R": "create:refined_radiance_casing",
            "M": "computercraft:monitor_advanced",
            "V": "tfmg:steel_chemical_vat",
            "P": "tfmg:electric_pump",
            "C": "computercraft:computer_advanced",
            "U": "mekanism:elite_control_circuit",
            "A": "bigreactors:fluidizercasing",
            "E": "ae2:engineering_processor",
        },
    ),
    "industrial_colonies:bigreactors/reprocessor/controller": _grid(
        "Assemble the reprocessor as an actual material-flow controller: waste injector and collector above the chemical vat, output port below, monitored casing core, inherited reactor controls, and late digital supervision",
        [
            " RWK ",
            "R V R",
            "MABAM",
            "RUCER",
            " ROR ",
        ],
        {
            "R": "create:refined_radiance_casing",
            "W": "bigreactors:reprocessorwasteinjector",
            "K": "bigreactors:reprocessorcollector",
            "V": "tfmg:steel_chemical_vat",
            "M": "computercraft:monitor_advanced",
            "A": "bigreactors:reprocessorcasing",
            "B": "bigreactors:basic_reactorcontroller",
            "U": "mekanism:ultimate_control_circuit",
            "C": "computercraft:computer_advanced",
            "E": "ae2:engineering_processor",
            "O": "bigreactors:reprocessoroutputport",
        },
    ),

    # ------------------------------------------------------------------
    # Orbital Engineering
    # ------------------------------------------------------------------
    "industrial_colonies:space/orbital_flight_computer": _grid(
        "Construct an open avionics rack with one of each late alloy, monitored ComputerCraft authority, redundant ultimate control and energy, engineering logic, TFMG backplanes, and the single Industrial Star authorization core",
        [
            " V M ",
            "TUEUT",
            "Q C Q",
            "T S T",
            " A N ",
        ],
        {
            "V": "allthemodium:vibranium_allthemodium_alloy_ingot",
            "M": "computercraft:monitor_advanced",
            "T": "tfmg:circuit_board",
            "U": "mekanism:ultimate_control_circuit",
            "E": "ae2:engineering_processor",
            "Q": "mekanism:ultimate_energy_cube",
            "C": "computercraft:computer_advanced",
            "S": "industrial_colonies:industrial_star",
            "A": "allthemodium:unobtainium_allthemodium_alloy_ingot",
            "N": "allthemodium:unobtainium_vibranium_alloy_ingot",
        },
    ),
    "industrial_colonies:space/propulsion/thruster_mount": _grid(
        "Build the thruster mount as an open load-bearing frame: transformer at the crown, mechanism and avionics layer, twin propellant feeds, ultimate controller, nozzle, and hose anchor",
        [
            "F T F",
            "HMCBH",
            "P U P",
            "H E H",
            "F N F",
        ],
        {
            "F": "tfmg:steel_frame",
            "T": "tfmg:transformer",
            "H": "tfmg:heavy_plate",
            "M": "tfmg:steel_mechanism",
            "C": "tfmg:circuit_board",
            "B": "computercraft:computer_advanced",
            "P": "rocketnautics:engine_pipes",
            "U": "mekanism:ultimate_control_circuit",
            "E": "rocketnautics:engine_nozzle",
            "N": "rocketnautics:hose_anchor",
        },
    ),
    "industrial_colonies:space/life_support/gas_tank": _grid(
        "Form two pressure vessels as vertical rubber-lined heavy-plate cylinders around elite chemical storage, with a valve neck and steel service pipe",
        [
            "  V  ",
            " RHR ",
            "RHTHR",
            " RHR ",
            "  P  ",
        ],
        {
            "V": "tfmg:steel_fluid_valve",
            "R": "tfmg:rubber_sheet",
            "H": "tfmg:heavy_plate",
            "T": "mekanism:elite_chemical_tank",
            "P": "tfmg:steel_pipe",
        },
    ),
    "industrial_colonies:space/life_support/large_gas_tank": _grid(
        "Stack two proven gas tanks inside a tall heavy shell, joining them through a steel manifold and valve to one ultimate chemical-storage base",
        [
            "  V  ",
            " HPH ",
            "H G H",
            "H G H",
            "HHUHH",
        ],
        {
            "V": "tfmg:steel_fluid_valve",
            "H": "tfmg:heavy_plate",
            "P": "tfmg:steel_pipe",
            "G": "ad_astra:gas_tank",
            "U": "mekanism:ultimate_chemical_tank",
        },
    ),
    "industrial_colonies:space/life_support/oxygen_gear": _grid(
        "Assemble personal oxygen gear as a compact rubber harness carrying a regulated valve, plastic manifold, electric pump, and TFMG control board",
        [
            "RVR",
            "PEP",
            "RCR",
        ],
        {
            "R": "tfmg:rubber_sheet",
            "V": "tfmg:steel_fluid_valve",
            "P": "tfmg:plastic_sheet",
            "E": "tfmg:electric_pump",
            "C": "tfmg:circuit_board",
        },
    ),
    "industrial_colonies:space/life_support/oxygen_loader": _grid(
        "Build a full oxygen-loading tower with twin intake fans, a pipe-and-control header, regulated process chamber, storage tank, electric pump, and heavy service base",
        [
            "F   F",
            "HPCPH",
            "V L V",
            "HTETH",
            " HHH ",
        ],
        {
            "F": "ad_astra:fan",
            "H": "tfmg:heavy_plate",
            "P": "tfmg:steel_pipe",
            "C": "tfmg:circuit_board",
            "V": "tfmg:steel_fluid_valve",
            "L": "mekanism:rotary_condensentrator",
            "T": "ad_astra:gas_tank",
            "E": "tfmg:electric_pump",
        },
    ),
    "industrial_colonies:space/life_support/oxygen_distributor": _grid(
        "Construct the station manifold around a proven loader and personal regulator, twin large reservoirs, fan and valve banks, computerized distribution control, and an ultimate power source",
        [
            "F V F",
            "HCOCH",
            "G L G",
            "HCTCH",
            "F U F",
        ],
        {
            "F": "ad_astra:fan",
            "V": "tfmg:steel_fluid_valve",
            "H": "tfmg:heavy_plate",
            "C": "tfmg:circuit_board",
            "O": "ad_astra:oxygen_gear",
            "G": "ad_astra:large_gas_tank",
            "L": "ad_astra:oxygen_loader",
            "T": "computercraft:computer_advanced",
            "U": "mekanism:ultimate_energy_cube",
        },
    ),
    "industrial_colonies:space/life_support/oxygen_sensor": _grid(
        "Build the oxygen sensor as a compact glass sampling head over a plastic TFMG board, calculation processor, airflow fan, and sealed rubber backing",
        [
            " G ",
            "PCP",
            "FER",
        ],
        {
            "G": "minecraft:tinted_glass",
            "P": "tfmg:plastic_sheet",
            "C": "tfmg:circuit_board",
            "F": "ad_astra:fan",
            "E": "ae2:calculation_processor",
            "R": "tfmg:rubber_sheet",
        },
    ),
    "industrial_colonies:space/life_support/vent": _grid(
        "Stamp a bulk set of station vents from two rubber-isolated heavy-plate rails around a three-pipe airflow manifold",
        [
            "HRH",
            "PPP",
            "HRH",
        ],
        {
            "H": "tfmg:heavy_plate",
            "R": "tfmg:rubber_sheet",
            "P": "tfmg:steel_pipe",
        },
    ),
    "industrial_colonies:space/life_support/airlock": _grid(
        "Construct a matched double airlock in its real door-frame silhouette, with paired plated doors, redundant oxygen sensing and computers, heavy structure, and a continuous rubber pressure seal",
        [
            "RHHHR",
            "HFCSH",
            "HT TH",
            "HFCSH",
            "RHHHR",
        ],
        {
            "R": "tfmg:rubber_sheet",
            "H": "tfmg:heavy_plate",
            "F": "tfmg:steel_frame",
            "C": "computercraft:computer_advanced",
            "S": "ad_astra:oxygen_sensor",
            "T": "tfmg:heavy_plated_door",
        },
    ),
    "industrial_colonies:space/construction/physics_assembler": _grid(
        "Build an open multi-axis construction gantry: piston crown, paired motor carriages, ventilated frame, computer and ultimate controls, TFMG backplanes, and the certified contraption diagram",
        [
            "F P F",
            "HMPMH",
            "F V F",
            "BUCUB",
            "F D F",
        ],
        {
            "F": "tfmg:steel_frame",
            "P": "create:mechanical_piston",
            "H": "tfmg:heavy_plate",
            "M": "tfmg:electric_motor",
            "V": "ad_astra:vent",
            "B": "tfmg:circuit_board",
            "U": "mekanism:ultimate_control_circuit",
            "C": "computercraft:computer_advanced",
            "D": "simulated:contraption_diagram",
        },
    ),
    "industrial_colonies:space/navigation/navigation_table": _grid(
        "Build the navigation workstation as a twin-monitor console over distinct optical, velocity, and gimbal channels, with one computer, ultimate and engineering control, TFMG backplanes, and a heavy bench base",
        [
            " M M ",
            "F C F",
            "BOVGB",
            "FUEUF",
            "HHHHH",
        ],
        {
            "M": "computercraft:monitor_advanced",
            "F": "tfmg:steel_frame",
            "C": "computercraft:computer_advanced",
            "B": "tfmg:circuit_board",
            "O": "simulated:optical_sensor",
            "V": "simulated:velocity_sensor",
            "G": "simulated:gimbal_sensor",
            "U": "mekanism:ultimate_control_circuit",
            "E": "ae2:engineering_processor",
            "H": "tfmg:heavy_plate",
        },
    ),
    "industrial_colonies:space/navigation/sputnik": _grid(
        "Assemble Sputnik in a satellite cross: aluminum skin, steel spars, optical, gimbal, and velocity sensors around the navigation table, with lightning rods as antenna booms and a TFMG controller",
        [
            "A O A",
            "F G F",
            "LCNCL",
            "F V F",
            "A L A",
        ],
        {
            "A": "tfmg:aluminum_sheet",
            "O": "simulated:optical_sensor",
            "F": "tfmg:steel_frame",
            "G": "simulated:gimbal_sensor",
            "L": "minecraft:lightning_rod",
            "C": "tfmg:circuit_board",
            "N": "simulated:navigation_table",
            "V": "simulated:velocity_sensor",
        },
    ),
    "industrial_colonies:space/dockyard/docking_connector": _grid(
        "Build two open docking heads around literal item, fluid, and energy interfaces, a wired-modem data link, ultimate handshake controller, electric actuator, and heavy framed jaws",
        [
            "H I H",
            "FPCPF",
            "E D E",
            "F U F",
            "H M H",
        ],
        {
            "H": "tfmg:heavy_plate",
            "I": "create:portable_storage_interface",
            "F": "tfmg:steel_frame",
            "P": "create:portable_fluid_interface",
            "C": "computercraft:cable",
            "E": "createaddition:portable_energy_interface",
            "D": "computercraft:wired_modem",
            "U": "mekanism:ultimate_control_circuit",
            "M": "tfmg:electric_motor",
        },
    ),

    # ------------------------------------------------------------------
    # Planetary Industry
    # ------------------------------------------------------------------
    "industrial_colonies:planetary/navigation/mars_navigation_computer": _grid(
        "Build a Desh-framed descent console around the inherited orbital computer and navigation table, with one monitor, etched backplane, engineering logic, TFMG board pair, and local ComputerCraft authority",
        [
            " P A ",
            "IBEBI",
            "PCNCP",
            "I O I",
            " P M ",
        ],
        {
            "P": "ad_astra:desh_plate",
            "A": "computercraft:monitor_advanced",
            "I": "ad_astra:desh_ingot",
            "B": "tfmg:etched_circuit_board",
            "E": "ae2:engineering_processor",
            "C": "tfmg:circuit_board",
            "N": "simulated:navigation_table",
            "O": "industrial_colonies:orbital_flight_computer",
            "M": "computercraft:computer_advanced",
        },
    ),
    "industrial_colonies:planetary/outpost/solar_panel": _grid(
        "Fabricate four outpost panels as three photovoltaic cell rows in a Desh support lattice over a transformer bus, ultimate cable terminals, and one engineering regulator",
        [
            "PDPDP",
            "DPPPD",
            "PDPDP",
            "DDTDD",
            "C E C",
        ],
        {
            "P": "ad_astra:photovoltaic_etrium_cell",
            "D": "ad_astra:desh_plate",
            "T": "tfmg:transformer",
            "C": "mekanism:ultimate_universal_cable",
            "E": "ae2:engineering_processor",
        },
    ),
    "industrial_colonies:planetary/outpost/water_pump": _grid(
        "Build a Desh pump tower with electric pump head, elite controller, steel intake manifold, fluid tank, valve, and broad structural foot instead of mirroring unrelated parts around its edge",
        [
            "  P  ",
            " DUD ",
            "DSTSD",
            "D V D",
            "DDDDD",
        ],
        {
            "P": "tfmg:electric_pump",
            "D": "ad_astra:desh_plate",
            "U": "mekanism:elite_control_circuit",
            "S": "tfmg:steel_pipe",
            "T": "tfmg:steel_fluid_tank",
            "V": "tfmg:steel_fluid_valve",
        },
    ),
    "industrial_colonies:planetary/outpost/gravity_normalizer": _grid(
        "Assemble the gravity normalizer as an open field-coil cross centered on an ultimate energy cube, with cable poles, transformer emitters, an Etrionic capacitor, engineering governor, and ultimate control",
        [
            "  T  ",
            " DCD ",
            "TWQWT",
            " DED ",
            "  U  ",
        ],
        {
            "T": "tfmg:transformer",
            "D": "ad_astra:desh_plate",
            "C": "ad_astra:etrionic_capacitor",
            "W": "mekanism:ultimate_universal_cable",
            "Q": "mekanism:ultimate_energy_cube",
            "E": "ae2:engineering_processor",
            "U": "mekanism:ultimate_control_circuit",
        },
    ),
    "industrial_colonies:planetary/outpost/energizer": _grid(
        "Construct the outpost Energizer as a two-post Ostrum charging gantry with capacitor banks, transformer bridge, ultimate energy cube and control, engineering supervision, and a reinforced Ostrum-block base",
        [
            "O   O",
            "OCQCO",
            "T E T",
            "OCUCO",
            " BBB ",
        ],
        {
            "O": "ad_astra:ostrum_plate",
            "C": "ad_astra:etrionic_capacitor",
            "Q": "mekanism:ultimate_energy_cube",
            "T": "tfmg:transformer",
            "E": "ae2:engineering_processor",
            "U": "mekanism:ultimate_control_circuit",
            "B": "ad_astra:ostrum_block",
        },
    ),
    "industrial_colonies:planetary/outpost/nutritional_liquifier": _grid(
        "Build the single-block food processor as a compact Ostrum pump head, paired fluid valves, elite control, etched TFMG logic, Mekanism casing, and a literal cooking vessel",
        [
            "OPO",
            "FUF",
            "TCB",
        ],
        {
            "O": "ad_astra:ostrum_plate",
            "P": "tfmg:electric_pump",
            "F": "tfmg:steel_fluid_valve",
            "U": "mekanism:elite_control_circuit",
            "T": "tfmg:etched_circuit_board",
            "C": "mekanism:steel_casing",
            "B": "farmersdelight:cooking_pot",
        },
    ),
    "industrial_colonies:planetary/venus/navigation_computer": _grid(
        "Wire every commissioned outpost service into an open Ostrum mission console around the Mars computer and shared navigation table, with one etched backplane, engineering governor, and local host computer",
        [
            "S W G",
            "P B P",
            "Z C L",
            "P N P",
            " E M ",
        ],
        {
            "S": "ad_astra:solar_panel",
            "W": "ad_astra:water_pump",
            "G": "ad_astra:gravity_normalizer",
            "P": "ad_astra:ostrum_plate",
            "B": "tfmg:etched_circuit_board",
            "Z": "ad_astra:energizer",
            "C": "industrial_colonies:mars_navigation_computer",
            "L": "mekanism:nutritional_liquifier",
            "N": "simulated:navigation_table",
            "E": "ae2:engineering_processor",
            "M": "computercraft:computer_advanced",
        },
    ),
    "industrial_colonies:planetary/venus/netherite_space_helmet": _grid(
        "Assemble the Venus helmet in its actual visor-and-seal silhouette around the Netherite helmet, with Ostrum shell, Desh thermal layer, tinted visor, twin vents, oxygen sensor, and one engineering controller",
        [
            " OOO ",
            "O D O",
            "OGNGO",
            "OVSVO",
            "  E  ",
        ],
        {
            "O": "ad_astra:ostrum_plate",
            "D": "ad_astra:desh_plate",
            "G": "minecraft:tinted_glass",
            "N": "minecraft:netherite_helmet",
            "V": "ad_astra:vent",
            "S": "ad_astra:oxygen_sensor",
            "E": "ae2:engineering_processor",
        },
    ),
    "industrial_colonies:planetary/venus/netherite_space_pants": _grid(
        "Assemble the pressure trousers in a legged silhouette around Netherite leggings, with Ostrum armor, Desh insulation, regulated gas tanks, paired valves, an ultimate cable spine, and engineering control",
        [
            "OOOOO",
            "OPCPO",
            "OTNTO",
            "O D O",
            "O E O",
        ],
        {
            "O": "ad_astra:ostrum_plate",
            "P": "tfmg:steel_fluid_valve",
            "C": "mekanism:ultimate_universal_cable",
            "T": "ad_astra:gas_tank",
            "N": "minecraft:netherite_leggings",
            "D": "ad_astra:desh_plate",
            "E": "ae2:engineering_processor",
        },
    ),
    "industrial_colonies:planetary/mercury/navigation_computer": _grid(
        "Build the Mercury console as a Calorite-framed telemetry stack: Sputnik reference and ultimate control above engineering logic, etched backplanes around the navigation table, then the complete Venus computer and host computer",
        [
            " S U ",
            "C E C",
            "B N B",
            "C V C",
            " P M ",
        ],
        {
            "S": "rocketnautics:sputnik",
            "U": "mekanism:ultimate_control_circuit",
            "C": "ad_astra:calorite_plate",
            "E": "ae2:engineering_processor",
            "B": "tfmg:etched_circuit_board",
            "N": "simulated:navigation_table",
            "V": "industrial_colonies:venus_navigation_computer",
            "P": "ad_astra:calorite_block",
            "M": "computercraft:computer_advanced",
        },
    ),

    # ------------------------------------------------------------------
    # Outer System Industry and Interstellar Escape
    # ------------------------------------------------------------------
    "industrial_colonies:outer_station/station_services_controller": _grid(
        "Build the station-services rack as a titanium-framed heavy cabinet linking oxygen distribution, ultimate control and energy, local computer authority, Mercury navigation, and gravity normalization",
        [
            " T T ",
            "HOUOH",
            "C E C",
            "HAMGH",
            " T T ",
        ],
        {
            "T": "rocketnautics:titanium_ingot",
            "H": "tfmg:heavy_machinery_casing",
            "O": "ad_astra:oxygen_distributor",
            "U": "mekanism:ultimate_control_circuit",
            "C": "ad_astra:calorite_plate",
            "E": "mekanism:ultimate_energy_cube",
            "A": "computercraft:computer_advanced",
            "M": "industrial_colonies:mercury_navigation_computer",
            "G": "ad_astra:gravity_normalizer",
        },
    ),
    "industrial_colonies:outer_station/atmospheric_scoop": _grid(
        "Construct the scoop as an open intake funnel: fan and control crown, titanium-Calorite throat, twin industrial pump lines into a large gas reservoir, station-services authority, and a rocket nozzle outlet",
        [
            "F U F",
            "T C T",
            "PEGEP",
            "H S H",
            "  N  ",
        ],
        {
            "F": "ad_astra:fan",
            "U": "mekanism:ultimate_control_circuit",
            "T": "rocketnautics:titanium_block",
            "C": "ad_astra:calorite_plate",
            "P": "tfmg:industrial_pipe",
            "E": "tfmg:electric_pump",
            "G": "ad_astra:large_gas_tank",
            "H": "tfmg:heavy_machinery_casing",
            "S": "industrial_colonies:station_services_controller",
            "N": "rocketnautics:engine_nozzle",
        },
    ),
    "industrial_colonies:outer_station/warp_charge_precursor": _grid(
        "Seat the required eight returned condensate canisters at the corners of a titanium-Calorite containment frame around Mercury matter, engineering stabilizers, Moon Crystal field media, one Industrial Star, and an ultimate arming circuit",
        [
            "B   B",
            "BTCTB",
            "MEWEM",
            "BCSCB",
            "B U B",
        ],
        {
            "B": "industrial_colonies:gas_giant_condensate_bucket",
            "T": "rocketnautics:titanium_block",
            "C": "ad_astra:calorite_block",
            "M": "ad_astra:mercury_iron_ore",
            "E": "ae2:engineering_processor",
            "W": "cosmowarp:moon_crystal",
            "S": "industrial_colonies:industrial_star",
            "U": "mekanism:ultimate_control_circuit",
        },
    ),
    "industrial_colonies:interstellar/navigation_computer": _grid(
        "Build the interstellar authority as an open redundant avionics rack: Moon Crystal and quantum references, engineering logic, Mercury navigation, live station services, ultimate control, antimatter reference, and an independent host computer",
        [
            " WQW ",
            "T A T",
            "C M C",
            "TUSUT",
            " QER ",
        ],
        {
            "W": "cosmowarp:moon_crystal",
            "Q": "ae2:quantum_entangled_singularity",
            "T": "rocketnautics:titanium_alloy_sheet",
            "A": "ae2:engineering_processor",
            "C": "ad_astra:calorite_plate",
            "M": "industrial_colonies:mercury_navigation_computer",
            "U": "mekanism:ultimate_control_circuit",
            "S": "industrial_colonies:station_services_controller",
            "E": "mekanism:pellet_antimatter",
            "R": "computercraft:computer_advanced",
        },
    ),
    "industrial_colonies:interstellar/unsigned_route_crystal": _grid(
        "Form the unsigned route medium as a diamond-shaped Moon Crystal and quantum lattice around redundant host computers, one Industrial Star core, Calorite shielding, engineering logic, and an ultimate signing interface",
        [
            "  M  ",
            " TQT ",
            "MPSPM",
            " CEC ",
            "  N  ",
        ],
        {
            "M": "cosmowarp:moon_crystal",
            "T": "rocketnautics:titanium_alloy_sheet",
            "Q": "ae2:quantum_entangled_singularity",
            "P": "computercraft:computer_advanced",
            "S": "industrial_colonies:industrial_star",
            "C": "ad_astra:calorite_plate",
            "E": "ae2:engineering_processor",
            "N": "mekanism:ultimate_control_circuit",
        },
    ),
    "industrial_colonies:interstellar/warp_drive": _grid(
        "Assemble the reusable Warp Drive as an open engine core: titanium casing and heavy supports around four ultimate power stores, paired quantum field anchors, ultimate control, Moon Crystal medium, dedicated navigation authority, and the Industrial Star core",
        [
            "T H T",
            "EQUQE",
            "C M C",
            "EHDHE",
            "T I T",
        ],
        {
            "T": "rocketnautics:titanium_casing",
            "H": "tfmg:heavy_machinery_casing",
            "E": "mekanism:ultimate_energy_cube",
            "Q": "ae2:quantum_entangled_singularity",
            "U": "mekanism:ultimate_control_circuit",
            "C": "ad_astra:calorite_plate",
            "M": "cosmowarp:moon_crystal",
            "D": "industrial_colonies:interstellar_navigation_computer",
            "I": "industrial_colonies:industrial_star",
        },
    ),
}


# These grids were explicitly audited and intentionally retained.  They
# already communicate the physical assembly, and the user specifically cited
# turbine-style recipes as a good reference.  Keeping them here makes coverage
# of the original 43 late-game 5x5 grids reviewable rather than implicit.
_AUDITED_UNCHANGED: dict[str, str] = {
    "industrial_colonies:bigreactors/basic_turbine/controller": (
        "Purpose-built turbine control cabinet; retain the approved turbine design."
    ),
    "industrial_colonies:bigreactors/reinforced_turbine/controller": (
        "Purpose-built reinforced turbine cabinet with inherited controller and reprocessor."
    ),
    "industrial_colonies:space/propulsion/engine_nozzle": (
        "Already forms a clear tapered nozzle silhouette from titanium alloy and heavy plate."
    ),
    "industrial_colonies:space/life_support/fan": (
        "Already forms a clear radial fan around a motor and propellers with open corners."
    ),
    "industrial_colonies:planetary/venus/netherite_space_suit": (
        "Already uses a torso silhouette and meaningful tank, regulator, distributor, and cable subassemblies."
    ),
    "industrial_colonies:planetary/venus/netherite_space_boots": (
        "Already uses a boot/leg silhouette with tanks, valves, insulation, and active airflow."
    ),
}


_AUDITED_IDS = frozenset(_REDESIGNS) | frozenset(_AUDITED_UNCHANGED)


# These grid redesigns are deliberately replaced by process-oriented recipes
# later in apply_recipe_design_v2.  On a rerun the persisted seed therefore
# already contains the downstream type; leave that body to its owning pass.
_DOWNSTREAM_REPLACEMENT_TYPES = {
    # recipe_design_v2_shape_refinement
    "industrial_colonies:planetary/venus/netherite_space_helmet": "sequenced_assembly",
    "industrial_colonies:planetary/venus/netherite_space_pants": "sequenced_assembly",
    "industrial_colonies:interstellar/unsigned_route_crystal": "sequenced_assembly",
    "industrial_colonies:outer_station/warp_charge_precursor": "sequenced_assembly",
    # recipe_design_v2_process_corrections
    "industrial_colonies:nuclear/basic_reactor_power_tap": "sequenced_assembly",
    "industrial_colonies:nuclear/reinforced_computer_port": "sequenced_assembly",
}


def apply(data: dict[str, Any]) -> None:
    """Apply the late-grid redesign to ``data`` in place.

    The function is idempotent.  It validates that every audited seed target
    exists exactly once, then edits only the three presentation/body fields
    owned by this pass.  In particular it never rebuilds a recipe dictionary,
    so all progression and removal metadata survives untouched.
    """

    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        raise TypeError("Managed recipe data must contain a recipes list")

    positions: dict[str, list[int]] = {}
    for index, recipe in enumerate(recipes):
        if isinstance(recipe, dict) and isinstance(recipe.get("id"), str):
            positions.setdefault(recipe["id"], []).append(index)

    missing = sorted(recipe_id for recipe_id in _AUDITED_IDS if recipe_id not in positions)
    duplicated = sorted(
        recipe_id for recipe_id in _AUDITED_IDS if len(positions.get(recipe_id, [])) > 1
    )
    if missing or duplicated:
        details: list[str] = []
        if missing:
            details.append(f"missing={missing}")
        if duplicated:
            details.append(f"duplicated={duplicated}")
        raise AssertionError("Late-grid recipe targets do not match seed: " + "; ".join(details))

    for recipe_id, body in _REDESIGNS.items():
        recipe = recipes[positions[recipe_id][0]]
        if recipe.get("phase") not in TARGET_PHASES:
            raise AssertionError(
                f"Late-grid target moved outside audited phases: {recipe_id} -> {recipe.get('phase')!r}"
            )
        recipe_type = recipe.get("type")
        if recipe_type != "mechanical_crafting":
            if recipe_type == _DOWNSTREAM_REPLACEMENT_TYPES.get(recipe_id):
                continue
            raise AssertionError(
                f"Late-grid target has an unexpected recipe type: "
                f"{recipe_id} -> {recipe_type!r}"
            )
        recipe["comment"] = body["comment"]
        recipe["pattern"] = list(body["pattern"])
        recipe["key"] = dict(body["key"])
