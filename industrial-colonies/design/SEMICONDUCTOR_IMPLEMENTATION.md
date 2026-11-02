# Semiconductor manufacturing extension

This document records the initial migration. The installed pink/green generation split and latest project are now described in `ADVANCED_SEMICONDUCTORS.md`; the original N/P parity below is historical.

Authority: the user explicitly requested semiconductor recipes be included after the pre-semiconductor migration. This extends the earlier cutoff; future exotic machine tiers remain outside scope.

Status: installed September 10, 2026 at 22:09 EDT, native revision `r2`. Both required native tests passed, including 145,310 material assertions and the semiconductor acceptance checks. Backup: `All in one/_industrial_colonies_backups/semiconductors-20260910-220952`.

Authoring source: `tools/build_semiconductor_progression.py`, with the current installed project captured under `progression/semiconductors/`. Do not regenerate from the old managed project or pre-semiconductor baseline. The migration preserves 679 unrelated cards and the four existing semiconductor endpoint UUIDs. The etching recipe retains its existing quantities and machinery.

## Required chain

1. Existing sand grinding and superheated carbon reduction produce metallurgical TFMG silicon.
2. Existing hydrochloric-acid purification produces purified silicon precursor; existing superheated hydrogen treatment in a firebrick-lined vat produces High-Purity Silicon.
3. One High-Purity Silicon undergoes two passes of Copper Saw cutting, 250 mB water rinsing and Copper Press finishing, producing two Prepared Silicon Wafers.
4. Each prepared wafer consumes 500 mB sulfuric acid in a heated steel Chemical Vat, minimum size 3, for 600 ticks, yielding one Etched Silicon Wafer.
5. An etched wafer follows either the N or P sequence twice: 100 mB dopant solution, 250 mB water, one copper wire, one plastic sheet, Copper Saw dicing and Copper Press finishing. Copper Deployers attach the wire and insulation. Each completed sequence yields two canonical TFMG semiconductors.

N uses the existing Phosphoric Acid from conditioned phosphate rock and acid extraction. P uses existing NuclearCraft Boric Acid from dissolved borax and acid treatment. These are game-scale deposition recipes, not a claim to model a physical diffusion furnace. Capacitors, redstone and sulfur dust are no longer consumed as semiconductor ingredients. Packaging and contacts follow etching, rather than being embedded in metallurgical silicon before purification.

## Bootstrap and ownership

The existing Mekanism chemical infuser/separator route uses circuit boards. Requiring it for the first silicon purification would make a cycle. A new heated size-3 steel-vat recipe combines 250 mB existing chlorine and 250 mB existing TFMG hydrogen into 250 mB existing Mekanism hydrochloric-acid fluid in 600 ticks. Its 1:1 consumption matches native chemical infusing; this is a slower entry route with heat and vat infrastructure, not free acid or enhanced salt recovery. Later Mekanism gas processing remains intact.

Chlorine is available from the already installed powered two-electrode brine-vat route. Hydrogen is available from that route or existing coke-dust processing. Electrode holders use Copper machinery, steel casing, steel/lead and copper wire; the Copper entry machines themselves use Weathered machinery and structural components. Native TFMG sulfuric acid uses sulfur, nitrate and water; phosphate and borate feed preparation use existing crushing/mixing/vat operations. Firebrick-lined vats, industrial mixers and heat have pre-semiconductor acquisition routes. None of these entry paths requires an Industrial Iron machine, finished circuit board, transistor or semiconductor. This is a dependency review; powered factory throughput is not measured by the native recipe tests.

The three old material-catalog shortcuts (direct N/P vat production and one-step wafer cutting) are disabled by the late semiconductor ownership script. The remaining 296 of the original 299 material recipes are unchanged. Both original and script-added recipes are filtered so alternate producers cannot bypass wafer preparation, etching or Copper processing. Existing transistor and circuit-board recipes consume the same canonical semiconductor items and require no migration of saved items.

## Verification and installation evidence

The isolated native harness exports the candidate through KJSGen before loading KubeJS. It verifies all 296 retained material recipes, all 41 prior ownership endpoints, four exclusive semiconductor outputs, removed shortcuts, input purity, dopant amounts, yields, two-pass sequences, heated vat requirements and Copper capability acceptance/rejection. It does not run a full powered production line or visually inspect client JEI.

`progression/semiconductors/deployment.json`, when present with status `APPLIED`, records the tested revision, backup and installed hashes. Installation changes only the default project, its generated export block and the new semiconductor policy script. Existing material and ownership scripts and the 0.5.2 JAR remain unchanged. Restart Minecraft after installation.
