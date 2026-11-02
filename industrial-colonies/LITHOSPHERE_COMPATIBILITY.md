# Lithosphere / WWOO geology compatibility

## Status

Implementation and static preparation are complete. **Runtime acceptance is pending** on the rebuilt compatibility candidate and newly prepared worlds. No Minecraft or Gradle process was launched for this task, no new stage was copied yet, and no live pack, save, prior test stage or positive historical evidence was changed. Earlier Tectonic acceptance is not reclassified as Lithosphere acceptance.

## Exact audited input changes

Compared with the 239-JAR client preparation snapshot, the current live folder contains 241 JARs:

- Added `lithosphere 1.6 17.06.2025 (1.20.5 - 1.21.5).jar`, `wwoo-neoforge-2.6.7.jar`, and `cristellib-neoforge-1.21.1-3.1.7.jar`.
- Removed `tectonic-3.0.26-neoforge-21.1.jar`.
- The live Industrial Colonies JAR remains the previously undeployed baseline, not the tested foundation candidate. Every other same-name JAR matched the prior SHA-256 snapshot. This was not treated as a user-caused regression.

Lithosphere's exact JAR SHA-256 is `F66D1C35BD9F36F861C5BD607050D6906413F8EF003941520E96434537B70394`; its `data/minecraft/worldgen/noise_settings/overworld.json` SHA-256 is `E78449FBA92C289267BDDB3E315B670F860B3B183FD0208541BE8BAE8676805E`.

Lithosphere contains no custom generator classes. Its vanilla-key Overworld noise/dimension data use minimum Y -64, height 576, maximum build Y 511, default stone, sea level 63 and vanilla deepslate surface rules. The prior Tectonic noise height was 384 (maximum Y 319). `GeologyCarversMixin` targets the standard `NoiseBasedChunkGenerator.applyCarvers` AIR tail; no replacement production hook or new mixin was necessary. Changed cave probabilities, surface behavior and greater height still need real-world acceptance. The approved geology depth limits and elevation/oil veto thresholds were not rescaled without a design instruction.

WWOO's actual datapacks live under nested `resources/*/data/`, not just the JAR's top-level `data/`. Its main pack does not override noise settings, dimension types or world presets. Its two direct resource collisions with Lithosphere are the river-noise definition and surface-lava placed feature; these landscape decisions remain untouched.

## Narrow production fixes

### Economic ore suppression

New optional tag `data/industrial_colonies/tags/worldgen/placed_feature/geology/wwoo.json` contains only:

- `wythers:ores/ore_coal_windswept`
- `wythers:ores/ore_diamond_volcanic`
- `wythers:ores/ore_gold_volcanic`
- `wythers:ores/ore_iron_windswept`
- `wythers:ores/ore_redstone_windswept`

The master suppression tag now includes this child, bringing the audited total from 68 to 73. The existing all-step Overworld biome removal and direct-placement guard share that tag. This closes WWOO's Y64–256 ore route, including the inline basalt-to-deepslate-diamond feature, without deleting registrations. `wythers:ores/ore_lava_volcanic`, landscapes, vegetation and unrelated special resources are not suppressed.

### Pale Garden

`minecraft:pale_garden` now belongs to `ordinary_forest`, matching the installed Vanilla Backport/WWOO forest identity. It receives existing forest suitability and oil rules, including existing terrain vetoes. No numeric weight, rarity, spacing, depth, yield or quality value changed. All other biome-family assignments remain exactly the prior final candidate's assignments.

### Decorative geology, not lava

The live WWOO configuration is left byte-for-byte unchanged: `removeOres=true`; navigable rivers, cliffs/coves and towering tepuis are false. The `wwoo_remove_ores` pack zeros seven decorative placed-feature counts, changes five configured decorative definitions, and separately zeros two lava-spring counts. Turning the entire option off would change lava policy, so this implementation does **not** do that.

`GeologyCompatibilityPacks` registers the conditional, required, `Pack.Position.TOP` server datapack `industrial_colonies:resourcepacks/ic_wwoo_decorative` only when WWOO is loaded. `GeologyBootstrap` attaches its supported NeoForge `AddPackFindersEvent` listener. The source is `src/main/resources/resourcepacks/ic_wwoo_decorative/`.

Exactly twelve resource definitions are copied byte-for-byte from the original Minecraft 1.21.1 client JAR, SHA-1 `30C73B1C5DA787909B2F73340419FDF13B9DEF88`:

| Kind | Exact names under `data/minecraft/worldgen/` |
| --- | --- |
| `configured_feature` | `ore_andesite`, `ore_diorite`, `ore_granite`, `ore_dirt`, `ore_gravel` |
| `placed_feature` | `ore_andesite_lower`, `ore_andesite_upper`, `ore_diorite_lower`, `ore_diorite_upper`, `ore_granite_lower`, `ore_granite_upper`, `ore_dirt` |

The original `spring_lava`, `spring_lava_frozen`, WWOO volcanic lava, river noise and other surface/carver files are not present in this override. Per-resource byte hashes and provenance are stored in the pack's `source_manifest.json`; `tools/lithosphere-compat/sync-decorative-overlay.ps1` verifies them without writing by default. Its explicit `-Write` mode performs only that bounded original-source extraction.

TOP priority expresses the intended ordering; it is **not yet a claimed effective-runtime result**. The new compatibility GameTest requires all twelve effective resource providers to be this compatibility pack and every byte hash to match the original. It additionally requires both lava-spring definitions to remain the WWOO zero-count definitions. A resource-priority failure must be fixed, not waived.

## Prepared tests and safety boundaries

`tools/terrain-smoke/src/.../TerrainGameTests.java` accepts explicit expected provider/mod, dimension/noise height and optional raw noise-resource SHA-256 properties. Defaults remain Tectonic / -64 / 384 for repeatability of earlier harness usage; no earlier report is changed. The Lithosphere harness sets `mr_lithosphere`, provider `lithosphere`, -64 / 576 and the exact installed noise hash, and rejects simultaneous Tectonic loading.

The new `LithosphereCompatibilityGameTests` checks the five effective suppression-tag entries, removal from Overworld biome feature lists, and both actual placement guard entry points. Its proxy permits only guard context/registry reads; an uncancelled feature throws before any world read/write. It also verifies Pale Garden, the twelve effective decorative overrides, and retained lava policies. It requests no chunks and writes no blocks.

`tools/lithosphere-compat/prepare-lithosphere-smoke.ps1` defaults to a read-only plan. After the root agent builds the candidate, explicit `-Stage` uses the established offline preparator to create a new physical copy; old stages and live inputs remain untouched. Candidate compatibility resources/classes are required before copying. No saves/accounts or configuration links are copied. The copied WWOO configuration is hash-verified unchanged. A stage records all active JAR hashes, the candidate identity and Lithosphere input hash.

The explicit `-ServerCompatibleSubset` switch retains the same six previously authorized GameTest-incompatible original JARs in the new stage's recoverable `excluded-server-test-only/` directory: Sodium, Iris, ETF, EMF, Euphoria Patcher and the separately approved Distant Horizons exception. Each must match the previously approved exact artifact hash. This leaves **235 active original-pack/candidate JARs from the 241 inputs**, plus the source-set test addon. No new exclusion is inferred. Full-client verification would restore all six in a separate client stage; this preparator does not launch either variant.

The new `lithosphere-smoke.init.gradle` layers only after the **new stage's** generated geology init. It must not be layered onto the old terrain/final init. The normal-world fixture is the unchanged existing vanilla-noise preset plus the required original Rocketnautics deep-space stem. Referencing `minecraft:overworld` lets installed Lithosphere supply the effective settings; the fixture does not copy/reinvent its terrain. Fresh revisions guard worlds and report paths against reuse.

Suggested root-controlled sequence (no command below has been launched here):

```powershell
& .\tools\lithosphere-compat\prepare-lithosphere-smoke.ps1 -CandidateJar <rebuilt-jar> -ServerCompatibleSubset -Stage
# Use the exact new stage path and commands returned in lithosphere-preparation.json.
# Run A and B separately with terrainOrder=a/b and compatRevision=r1.
& .\tools\terrain-smoke\compare-terrain-reports.ps1 -Stage <new-stage> -Revision lithosphere-r1
```

With the current four production tests, each invocation selects six required tests: four production, the natural terrain check, and the compatibility check. Controlled/trace tests are not selected. The existing natural test remains bounded to three formations, at most 60 explicit FULL chunks and an eight-minute wall guard. Implicit Minecraft dependency chunks are not capped by that explicit count. It still requires exact A/B final block/count equality and does not certify broad distribution, existing-world seams, visuals or processing progression. No new resourcepack, resource noise or numeric geometry shortcut was added to force a result.

## Checks completed so far

- Exact twelve-file mechanical extraction and subsequent read-only byte validation: PASS.
- Compatibility static audit: **81 assertions PASS**; five economic IDs, twelve exact overrides, all **42 approved geological PNGs unchanged**, all settings/deposit/oil numeric source files byte-identical to the final `5A4CCD0B…` baseline.
- General geology integration audit: **1,150 static assertions PASS**, 73 suppression IDs; original 1254×1254 Bertrandite exception retained.
- Installed-JAR worldgen audit: **73 IDs resolved, zero errors**; original Create/TFMG decorative-stratum preservation still passes.
- Both new PowerShell scripts parsed; read-only stage plan ran successfully against 241 live inputs. It correctly reported that the currently built pre-compatibility candidate needs rebuilding and created no directory.
- Production/addon compile, effective builtin-pack priority, new Lithosphere startup and fresh-world A/B: **pending root-controlled build/runtime**. This document does not claim those passed.

## File scope

Modified: the master suppression tag, `biome_families.json`, `GeologyBootstrap.java`, `tools/validate_geology_integration.ps1`, and the test-only `TerrainGameTests.java`.

Added: the optional `geology/wwoo.json` tag; `GeologyCompatibilityPacks.java`; the 12-resource builtin pack plus `pack.mcmeta` and source manifest; this document; and `tools/lithosphere-compat/` containing the no-write compatibility test, fresh-stage initializer/preparator, exact source-copy validator and static compatibility audit. No approved texture, production geometry, deposit profile, numeric generation setting, oil rule, live configuration or old runtime evidence was changed.
