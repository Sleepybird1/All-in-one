# Progression and machine ownership

Authority: user notes received September 10, 2026. The verbatim source is `PROGRESSION_MACHINE_OWNERSHIP_USER_NOTES.txt`. It takes precedence over this summary and older progression audits. Status: the pre-semiconductor scope is implemented and installed; see `PRE_SEMICONDUCTOR_IMPLEMENTATION.md`. Later machine-tier and nuclear-specific ownership work remains outside that completed scope.

Subsequent installed extensions: `SEMICONDUCTOR_IMPLEMENTATION.md` and `METAL_UNIT_MIGRATION.md`. The later `BUCKET_BLOCK_MIGRATION.md` is the current metal-volume authority: 100 mB per ingot, 1,000 mB per finished storage block and 10 mB per nugget. `ADVANCED_SEMICONDUCTORS.md` records the installed Brass/gold pink generation and starter transistor bootstrap. `STRUCTURE_CLEANUP.md` records the installed exploration/world-generation changes.

## Function ownership

| Function | Primary family | Required boundary |
|---|---|---|
| Crushing/grinding | Create Crushing Wheels | Completely disable Mekanism Crusher and overlapping generic alternatives; include factory/upgrade bypasses in the audit. |
| Melting/casting | Modern Foundry | Retire competing bypasses. |
| Alloying | Create Mixer and designated capability tiers | Foundry alloying stays disabled, including automatic molten alloying. |
| Washing/airflow separation | Create Fans and Encased fan tiers | Overlapping washing machines must not bypass the assigned tier. |
| Chemicals/gases/acids/reagents | Primarily Mekanism | Chemical infrastructure remains useful; generic ore multiplication is not its role. |
| Oil refining | Primarily TFMG | Preserve its normal refining unless specifically modified. |
| Nuclear fuel/isotopes/reprocessing/enrichment/breeding | NuclearCraft where appropriate | Audit competing nuclear routes against this assignment. |

One processing function has one primary family. Installed duplicate machines do not automatically deserve a progression role. Existing specialized material-processing exceptions must be identified explicitly rather than silently broadened or removed.

## Capability tiers

September 20 user clarification: **Cast Iron builds Weathered Iron machines; Weathered Iron supports later Steel / Industrial Iron progression.** Titanium/Tungsten-before-Industrial-Iron remains mandatory. The user's current approved brick/frame cards were recovered from the live authoring project. The staged correction uses their existing eight-step frame, canonical TFMG cast iron and a basic sheet-press bootstrap exception; six Weathered machine bills use cast frames. This is not installed or proof of the full first-metal chain. Current evidence: `../../workflow/early-survival/high-integration/approved/REPORT.md`. Preserve intervening live edits when integrating; do not reinstall an older full project.

| Tier | Intended role |
|---|---|
| Basic/Andesite Create | Recognizable default machinery, logistics and mechanical automation. Retain normal recipes wherever possible. |
| Weathered Iron | First heavy industry and TFMG entry: structural parts, steel/reinforced/boiler plates, frames, mechanisms, bearings, valves, pumps and pressure hardware. Press forms parts; deployer assembles mechanical subassemblies. |
| Copper | Conductive parts, basic/intermediate electronics and precision electronic subassemblies. |
| Brass | More complex circuits, processors/control assemblies, denser electronics and the beginning of higher-voltage manufacture. |
| Train | Heavy electrical machinery, transformers, large coils, high-current switching, transmission, generators and traction hardware. Shares high-voltage work with Brass. |
| Industrial Iron | Advanced electromechanical heavy industry, Titanium/Tungsten structures, advanced electronics, harsh chemistry/metallurgy, stronger airflow and Refined Radiance-era work. |

Create defines function; Encased tiers unlock capability, not merely speed. Chromium's conditioned chromite washing requires Industrial Iron Fan + water; ordinary and Weathered fans must reject it.

Basic Create exceptions include the custom low-heat Andesite Alloy recipe, owned material processing, disabled Foundry alloying and higher-tier recipe exclusion from normal machines. Do not redesign basic Create just to make it more expensive.

Electronics costs should come from purified inputs, foil/sheets, precision parts, subassemblies, sequenced manufacturing, machine capabilities and factory infrastructure. Do not add arbitrary Diamonds, Radium, Allthemodium or unrelated exotic inputs for expense alone. Semiconductor manufacturing was subsequently authorized and installed; see `SEMICONDUCTOR_IMPLEMENTATION.md` for its required wafer/dopant chain and bootstrap.

## Higher-tier Create stress demand — September 26 design note

Approved direction, **not implemented**: this applies to **every machine tier**, not just Weathered Iron. Each higher tier should consume more Create stress units using a multiplier relative to the corresponding base Create machine. The base machine is **1x**; Weathered Iron is the first upgraded stage, and Industrial Iron must demand more than Weathered Iron. Compare the same machine function at the **same RPM**, so higher tier demand is not confused with a speed change.

Weathered Iron may use **1.5x or 2x**; the user has not selected between them. Later tiers should increase further, but their exact multipliers and tier mapping are undecided. Do not invent an exponential ladder or treat either Weathered example as finalized.

Copper, Brass and Train machinery should have especially substantial stress/power demand for their electronics-manufacturing roles. Heating-related machines, particularly fans, will **probably** have high costs; this emphasis is tentative, not a selected multiplier. Balance may combine tier-wide multipliers with machine/function-specific adjustments. Exact values and ordering across families remain undecided; this does not establish a new linear age order or replace existing capability gates.

The user's words "power" and "energy" describe demand, not authorization for an FE conversion or simultaneous FE and SU charges. Use each machine's actual resource model; any different resource model needs its own decision.

This note does not change runtime configuration, recipes, RPM, processing speed, output, machine ownership or the established capability hierarchy. Implementation and gameplay tests: **NOT_RUN**. This documentation adds no completed master task.

## Final machine assembly

Processing machines manufacture components; Mechanical Crafters assemble finished industrial machines and functional blocks. Higher-tier machines must not have simple crafting-table bypasses. Preserve basic Create's default/bootstrap exceptions.

Hard maximum: both grid dimensions must be at most 7. Suggested envelopes: basic 3–4, Weathered 4–5, Copper/Brass/Train 5–6, Industrial Iron 6–7. Reserve 7×7 for major assemblies. Larger conceptual complexity goes into subassemblies, never a larger grid. Layouts should represent frames, drive parts, working heads and controls where practical rather than random ingredient filling.

First-machine acquisition needs special care: Weathered components cannot be the sole inputs to the first Weathered machines if those components require those same machines. TFMG entry cannot depend on electronics whose own factory needs Weathered/TFMG infrastructure. Likewise Industrial Iron's Titanium/Tungsten chemistry must remain available before Industrial Iron itself. These are implementation checks, not new user-approved exception recipes.

Do not design or implement future exotic tiers unless requested. Existing later content is not automatically authorized for deletion.

## Audit and follow-through

See `PROGRESSION_MACHINE_OWNERSHIP_AUDIT.md` and `machine_ownership_snapshot.json` for the initial, pre-change comparison. See `PRE_SEMICONDUCTOR_IMPLEMENTATION.md` for installed changes, native validation and the remaining boundary. A source card alone is not proof of a loaded runtime recipe.
