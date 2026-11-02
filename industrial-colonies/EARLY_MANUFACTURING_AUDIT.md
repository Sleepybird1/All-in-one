# Early manufacturing audit

> Implementation update: the bounded correction described here is now source-owned in
> `progression/managed_recipe_overhaul.seed.json`. The shared generated manifest and
> KJSGen project were deliberately not regenerated during this implementation pass.

## Outcome

The primitive-to-Brass chain is reachable, but the current early manifest does not yet describe its real physical order. The installed recipes form an acyclic route when read as machines and materials:

`crude flint tool -> copper modular workshop -> Andesite drive -> Mechanical Press -> sheet-metal machines and fluids -> Steam -> heated Brass -> Deployer and Mechanical Crafters -> Precision Mechanisms -> crushing and trains`

The principal defects are not missing ingredients. They are eight outputs assigned one age too early, four manual sheet recipes that bypass the first Press, and blanket output removals that delete useful factory upgrades and the Schedule reset recipe.

This was a read-only implementation audit. No seed, assignment, generated KJSGen file, KubeJS script, quest, Draw.io file, deployment source, or live-pack file was changed. The companion [EARLY_MANUFACTURING_AUDIT.plan.json](EARLY_MANUFACTURING_AUDIT.plan.json) is the machine-readable implementation plan.

## Audited baseline

The two assigned phases contain 49 outputs. The current builder handles them as follows:

| Current handling | Count | Meaning |
|---|---:|---|
| Auto-generated stock replacement | 42 | The installed recipe is copied under an Industrial Colonies auto-generated ID. |
| Processing-only skip | 5 | Andesite Casing, Brass Casing, Precision Mechanism, Railway Casing, and Track remain installed processing recipes. |
| Excluded material | 2 | Andesite Alloy and Brass Ingot remain stock material routes. |
| Explicit Encased upgrades | 4 | Copper/Brass Presses and Deployers are authored in the seed. |
| Expanded Copper family | 10 | Mixer, Saw, Fan, Roller, Depot, Gearbox, Clutch, Chain Conveyor, Automatic Clutch, and Configurable Gearbox. |
| **Compiled recipes in these phases** | **56** | 34 Mechanical Foundations and 22 Steam & Brass cards. |

The 42 generated recipes mostly reproduce their stock bill of materials. That gives the manifest removal ownership without adding meaningful progression, and in several cases it removes a better automated producer.

Evidence was checked against the current nested-aware catalog, the live registry export, and source JSON inside the installed JARs. The catalog SHA-256 is `21C274B8C8A02BC2BDF32A4F2A3BE1720894B8A59D8283773474A424133C1574`; the audited seed SHA-256 is `023B573D264A2A91E775A3673505B735B9BCA4A42C2D687D7A93E6360D7CE5CE`.

## Correct physical order

### 0. Primitive salvage

The existing primitive script is coherent. `industrial_colonies:crude_flint_pickaxe` supplies a deliberately poor stone-tier bridge, while the replacements for `modernfoundry:tables/part_builder` and `modernfoundry:tables/tinker_station` require copper. That lets the crude tool reach copper and iron without reopening the ordinary vanilla tool ladder.

No additional recipe gate is needed here. The important invariant is that the first Create machine must not require a sheet that only that machine can make.

### 1. Andesite drive

The installed hand recipes `create:crafting/materials/andesite_alloy` and `create:crafting/materials/andesite_alloy_from_zinc` provide a small bootstrap from Andesite plus iron or zinc nuggets. The two installed mixing recipes then become the factory-scale continuation. Andesite Casing correctly remains item application from stripped wood.

Shafts, Cogwheels, a Water Wheel, and a Millstone can therefore precede the first Press. This is the correct low-power starter factory.

### 2. Sheet-metal workshop

The Mechanical Press is the real first manufacturing gate. It must be craftable from ingots, an iron block, Andesite components, and drivetrain parts—never from an iron or copper sheet.

Once built, it supplies the installed `create:pressing/iron_ingot`, `create:pressing/copper_ingot`, and `create:pressing/gold_ingot` routes. Iron sheets then make the Whisk and Propeller; copper sheets make fluid infrastructure and Copper Casing. That gives the Press several immediate downstream uses rather than making it a one-off quest object.

### 3. Mechanical factory and fluids

The Mixer, Fan, and Saw are naturally post-Press because their Whisk, Propeller, and saw blade consume iron plates. Fluid Pipes, Tanks, Chutes, Item Vaults, the Item Drain, Spout, and Hose Pulley are likewise sheet-metal infrastructure.

The stock Mechanical Pump is the weak point: `create:crafting/kinetics/mechanical_pump` is only one Cogwheel plus one Fluid Pipe. The bounded replacement below turns it into a real reusable pump assembly and then consumes that assembly in the first Steam Engine.

### 4. Steam before precision Brass

`create:steam_engine` needs a gold plate in the installed recipe, so it already follows the Press. It does not need Brass and should be the power-production bridge into the rest of the phase. The recommended explicit recipe additionally consumes the hardened Mechanical Pump, Copper Casings, and a copper pressure body. This makes fluid handling—not an age label—the prerequisite.

### 5. Heated Brass

The installed Brass route is sound and should stay stock:

- `create:crafting/kinetics/empty_blaze_burner` needs four iron plates and Netherrack.
- Capturing a Blaze produces the functional `create:blaze_burner` through runtime interaction rather than a static recipe.
- `create:mixing/brass_ingot` requires heated mixing of copper and zinc.
- Brass Casing remains item application; Create Metallurgy's molten casting is a valid factory alternative.
- Brass Hand and Electron Tube both depend on Press-made components.

Create Metallurgy's `createmetallurgy:alloying/brass` is also heated and produces molten Brass for casting. It is a second industrial line, not a hand-crafting loophole.

### 6. Brass automation before precision

Deployer and Mechanical Crafters must be available before Precision Mechanisms and Crushing Wheels:

- `create:crafting/kinetics/deployer` uses an Electron Tube, Andesite Casing, and Brass Hand.
- `create:crafting/kinetics/mechanical_crafter` uses an Electron Tube, Brass Casing, and Crafting Table.
- `create:sequenced_assembly/precision_mechanism` requires a working Deployer line.
- `create:mechanical_crafting/crushing_wheel` requires a Mechanical Crafter array even though Mechanical Crafters do not appear as recipe ingredients.

That infrastructure dependency is invisible to the current item-only DAG. A focused validator must assert it explicitly.

### 7. Precision, bulk processing, and trains

Create's installed Precision Mechanism sequence is appropriate and should remain. Its repeated Cogwheel, Large Cogwheel, and iron-nugget deployments are exactly the recognizable manufactured component the pack needs.

The existing Encased upgrades are acyclic in their current direction:

- `industrial_colonies:manufacturing/copper_deployer` upgrades the native Deployer and does not consume a Precision Mechanism.
- `industrial_colonies:manufacturing/brass_press` and `industrial_colonies:manufacturing/brass_deployer` consume Precision Mechanisms, so they are later precision-line upgrades.

Do not bind the Precision Mechanism recipe to the Brass Press or Brass Deployer. Either change would make the precision component depend on a machine that already consumes that component.

Tracks remain a real Deployer/Press sequence. The later `createmetallurgy:sequenced_assembly/steel_track` is a useful Steel alternative, not a bypass. Railway Casing remains Brass Casing plus an obsidian plate. Train Controls correctly follow Precision Mechanisms; stations, signals, and observers can branch earlier from railway casing.

## Confirmed defects

### Eight assignments are physically one phase early

The following outputs are assigned to Mechanical Foundations even though their installed acquisition is Brass-age:

| Output | Exact installed recipe | Physical prerequisite |
|---|---|---|
| `create:content_observer` | `create:crafting/logistics/content_observer` | Brass Casing and Electron Tube |
| `create:stockpile_switch` | `create:crafting/logistics/stockpile_switch` | Brass Casing and Electron Tube |
| `create:pulse_repeater` | `create:crafting/logistics/pulse_repeater` | Brass plate |
| `create:pulse_extender` | `create:crafting/logistics/pulse_extender` | Brass plate |
| `create:deployer` | `create:crafting/kinetics/deployer` | Brass Hand and Electron Tube |
| `create:mechanical_arm` | `create:crafting/kinetics/mechanical_arm` | Brass plates, Brass Casing, Precision Mechanism |
| `create:rotation_speed_controller` | `create:crafting/kinetics/rotation_speed_controller` | Brass Casing and Precision Mechanism |
| `create:crushing_wheel` | `create:mechanical_crafting/crushing_wheel` | Mechanical Crafter capability |

This is not a closed recipe cycle because the stock ingredients still enforce the later acquisition. It is a semantic and validation defect: the report says Mechanical while the game recipe says Brass.

### The hand Hammer bypasses the Press

`createdieselgenerators:crafting/hammer` is available from Andesite Alloy, iron, and a wooden rod. Its four Hammering recipes directly make the four early Create sheets:

- `createdieselgenerators:hammering/iron_sheet`
- `createdieselgenerators:hammering/copper_sheet`
- `createdieselgenerators:hammering/gold_sheet`
- `createdieselgenerators:hammering/brass_sheet`

Those four exact recipes should be retired. The Hammer item and unrelated Hammering recipes should remain. Create Metallurgy plate casting should also remain because it is an actual machine/foundry production line.

### Output exclusivity deletes factory rewards

The generated Shaft recipe removes `create:cutting/andesite_alloy`, even though the Saw route is exactly the efficiency reward the player should receive for building a factory. The Cogwheel recipes similarly remove `create:deploying/cogwheel` and `create:deploying/large_cogwheel`.

Foundational components need both routes: a small hand bootstrap and a later automated throughput route. They should stay stock/unmanaged, or an explicit hand replacement must remove only its one hand recipe ID.

### Schedule reuse is accidentally removed

The generated Schedule card removes both the construction recipe and `create:crafting/appliances/schedule_clear`. The latter is not a shortcut; it clears a programmed Schedule so the item can be reused. Preserve it exactly.

The same exact-removal principle applies to later-to-earlier compatibility conversions. The current broad removals should preserve:

- `create:crafting/logistics/packager_from_conversion`
- `create_connected:crafting/kinetics/fluid_tank_from_conversion`
- `create_connected:crafting/kinetics/item_vault_from_conversion`
- `create:crafting/kinetics/track_observer_from_other_plates`

They convert equivalent or later infrastructure and do not create an early material bypass.

### Daylight Detector is not actually exclusive

The mod catalog exposes `modernfoundry:common/glass/vanilla/daylight_detector`, which the builder selected and replaced. The installed Minecraft 1.21.1 JAR also contains the canonical `minecraft:daylight_detector` recipe. Removing only the Modern Foundry ID leaves the vanilla recipe active.

The recommended batch simply removes Daylight Detector from auto-management and leaves both recipes. It is a utility ingredient, not a useful factory milestone.

### Most Copper variants do not yet perform unique work

The Copper Press, Copper Deployer, and Copper Mechanical Saw have real authored consumers in the later electronics path. The other nine Copper family items occur only as their own generated output and as the input to the next casing tier. That is casing escalation, not functional progression.

Keep the three useful machines on the core route. Leave the Mixer, Fan, Roller, Depot, Gearbox, Clutch, Chain Conveyor, Automatic Clutch, and Configurable Gearbox optional until an exclusive recipe genuinely needs each environment. This follows the design rule that Create Encased is a manufacturing system without forcing every redundant visual variant into the spine.

## Bounded explicit recipe batch

The companion JSON provides seed-ready structures. The intended recipes are summarized here.

### Mechanical Press

Recipe ID: `industrial_colonies:mechanical/mechanical_press`

```text
S G S     S = Create Shaft
A C A     G = Create Cogwheel
I B I     A = Andesite Alloy
          C = Andesite Casing
          I = Iron Ingot
          B = Iron Block
```

Output: one `create:mechanical_press`. Remove only `create:crafting/kinetics/mechanical_press`.

This is deliberately substantial, but it contains no plate and therefore cannot circularly require itself.

### Mechanical Pump

Recipe ID: `industrial_colonies:mechanical/mechanical_pump`

```text
  S       S = Copper Sheet
P A P     P = Fluid Pipe
  C       A = Andesite Casing
          C = Cogwheel
```

Output: one `create:mechanical_pump`. Remove only `create:crafting/kinetics/mechanical_pump`.

### Steam Engine

Recipe ID: `industrial_colonies:steam/steam_engine`

```text
G S G     G = Golden Sheet
A P A     S = Shaft
C B C     A = Andesite Alloy
          P = hardened Mechanical Pump
          C = Copper Casing
          B = Copper Block
```

Output: one `create:steam_engine`. Remove only `create:crafting/kinetics/steam_engine`.

This consumes the fluid-handling milestone without consuming the tank array the player still needs to operate the engine.

### Native Deployer

Recipe ID: `industrial_colonies:brass/deployer`

```text
S E S     S = Shaft
A C A     E = Electron Tube
  B       A = Andesite Alloy
          C = Andesite Casing
          B = Brass Hand
```

Output: one `create:deployer`. Remove only `create:crafting/kinetics/deployer`.

### Mechanical Crafters

Recipe ID: `industrial_colonies:brass/mechanical_crafter`

```text
A E A     A = Andesite Alloy
B C B     E = Electron Tube
A R A     B = Brass Sheet
          C = Brass Casing
          R = Crafting Table
```

Output: three `create:mechanical_crafter`. Remove only `create:crafting/kinetics/mechanical_crafter`.

The three-block yield remains practical for large arrays, but each batch now represents a real Brass workshop rather than one tube, one casing, and one table.

## Exact preserve policy

The next implementation should not replace processing merely to reduce the builder's skipped count. Preserve these installed routes:

- Andesite bootstrap and automation: `create:crafting/materials/andesite_alloy`, `create:crafting/materials/andesite_alloy_from_zinc`, `create:mixing/andesite_alloy`, `create:mixing/andesite_alloy_from_zinc`, both Andesite Casing item-application recipes, `create:cutting/andesite_alloy`, and both Cogwheel deploying recipes.
- Brass material routes: `create:mixing/brass_ingot`, both Brass Casing item-application recipes, `createmetallurgy:casting_in_basin/brass_casing`, and `createmetallurgy:casting_in_table/brass/ingot`.
- Precision and rail processing: `create:sequenced_assembly/precision_mechanism`, `create:sequenced_assembly/track`, `createmetallurgy:sequenced_assembly/steel_track`, and `create:item_application/railway_casing`.
- Reuse and compatibility: `create:crafting/appliances/schedule_clear` and the exact down-conversion/alternate recipes listed above.

## Acceptance criteria for implementation

1. Compile the five explicit replacements and four exact Hammering retirements without output-wide removal.
2. Prove that the Mechanical Press recipe contains no sheet.
3. Prove that no Create Diesel Generators Hammering recipe still outputs the four early Create sheets.
4. Prove that Shaft cutting, Cogwheel deploying, Large Cogwheel deploying, and Schedule clearing survive compilation.
5. Add capability assertions for heated Brass, Deployer-based Precision Mechanisms, Mechanical-Crafter Crushing Wheels, and Deployer/Press Tracks.
6. Prove the corrected capability order is acyclic.
7. Keep the existing four explicit Copper/Brass Press and Deployer upgrades unchanged in this bounded batch.

This batch fixes the real early spine without turning every small Create utility into a custom recipe or making the Encased casing ladder mandatory for its own sake.
