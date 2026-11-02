# Geological oil reservoir framework

Oil is an independent system, not a mineral-deposit family. This replaces the old dry-biome-only 1/32 placement filter. It does **not** alter petroleum recipes, fluids, native scanner behavior, pumpjack extraction, persisted reserve sizes, or the existing finite-reservoir mixin.

## Central configuration

Bundled defaults: `src/main/resources/data/industrial_colonies/geology/oil.json`.

External override: `config/industrial_colonies/worldgen/oil.json`, via `GeologyConfig.externalOrBundled`. Biome membership is shared through `GeologyConfig.families` and the master biome-family JSON. Exact biome IDs are not duplicated in the oil Java implementation.

- Strong desert/badlands/outback and coastal/oceanic families: relative weight **2.5**.
- Sedimentary/plains/prairie/steppe families: **1.25**.
- Lowland forest/wetland families: **0.5**.
- Mountain/highland, volcanic/ashen, cold high-altitude: **0**, with unconditional veto even if another family has a positive weight.
- Unclassified biomes: zero until assigned to a recognized family.

The default regional probability is `0.65 × biome weight / 2.5`. This is a probability **per regional candidate**, not per chunk. A homogeneous eligible basin therefore accepts about 65% of its candidate regions; plains about 32.5%; lowland forest about 13%. Terrain can further reject them. Positive overlapping families use their maximum weight, never sum; hard exclusions win.

`hard_terrain_exclusions` also rejects surface elevations above Y100 and more than 32 blocks of local relief within four cardinal samples 32 blocks away. This closes the Tectonic case where an ordinary plains/forest biome occupies mountainous terrain. Values are initial editable guardrails, not claims of geological classification accuracy. Use new-world inspection to tune their conservatism. Ocean-floor height is used so seawater does not make offshore terrain look elevated.

## Native compatibility and chunk ownership

The installed **TFMG 1.2.0** `OilDepositFeature` API was inspected with `javap -p -c`:

- `place(FeaturePlaceContext<NoneFeatureConfiguration>)` applies a 1/20 roll, then moves multiple deposit origins by up to 20 blocks per axis per iteration; total reach can exceed 100 blocks.
- Public `placeDeposit(BlockPos, WorldGenLevel, RandomSource)` writes one native deposit marker, a column extending fewer than 25 blocks upward, optional crude neighbors at horizontal distance one, and native fossilstone around the column base.

Calling the entire native field builder from one chunk would prevent complete terrain vetos and could write outside the safe generation region. Instead `OilFieldPlanner` hashes world seed + configurable salt + regional coordinates into field centers and native well positions. Each well is generated only by the chunk containing it. Positions are constrained to local X/Z 1..14, so the native radius-one footprint stays entirely inside that same chunk. Every affected horizontal column is checked against the biome veto before placement.

Default fields use 1024-block regions with a 192-block center margin, radius 32..80, and 3..7 native well candidates. Duplicate candidate positions are deduplicated. Rejected terrain can reduce or eliminate a field's generated wells; the configured count is intentionally a candidate count, not a guarantee. Regions are deterministic across negative coordinates and chunk-generation order. Nearby native deposit markers continue to be grouped into reservoirs by TFMG itself.

Oil geology does not share the mineral generator's 800-block or same-family spacing rules. Oil currently has its own margin-based regional separation. Offshore and onshore use the same well-count/radius defaults; larger offshore reserves, pressure, extraction-rate rebalance, and final petroleum processing remain explicitly deferred.

The custom placed feature is installed in all Overworld biomes, then central family and terrain rules decide eligibility. `remove_tfmg_global_oil_deposits.json` still removes the native global feature. The old `oil_bearing_biomes.json` is no longer an active gate and is retained only as legacy data.

The custom placed feature has no external Create config filter or additional random-placement filter. Its central oil rules and the Industrial Colonies generation master switch are authoritative; disabling Create's unrelated decorative worldgen does not silently disable this oil system.

Y=-64 is the current TFMG scanner contract. Although it is explicit in the config, changing it without matching scanner support is not supported. Existing generated oil blocks and saved reservoirs are not removed or retro-generated.

## Registration and diagnostics

`GeologyBootstrap` calls `OilWorldgen.register(bus)`. `OilRules.invalidate()` is the oil config-cache invalidation hook for a parent reload command. In the absence of a reload hook, restart after external-config changes.

Set `debug_logging` to true to log field center/radius, selected weight, deterministic roll, generated native column count, and candidate/terrain rejection reason. Logs are only emitted for chunks owning candidate wells, not every empty chunk.

## Verification

- `tools/validate_oil_worldgen_framework.ps1`: checks central data, approved weights and hard exclusions, native-deposit delegation, no neighboring chunk requests, registration data, and continued stock-feature suppression/finite extraction.
- `tools/java/dev/godpc/industrialcolonies/geology/oil/OilFieldPlannerTest.java`: actual Java planner regression test over 10,000 regional fields, world-seed determinism, negative coordinates, weight normalization, generation traversal order, and every native horizontal footprint's chunk ownership.
- Full NeoForge compile is performed by the parent task; no parallel Gradle invocation is required for this subtask.
- Required runtime follow-up: new chunks in a normal Tectonic/RU world; verify offshore/desert/plains scanner finds, mountain/volcanic absences, region-border continuity and unchanged finite extraction. A superflat world is useful for UI checks, not geological distribution validation.

`validate_regional_finite_oil_fields.py` and its mutation tests have also been updated from the superseded desert-only 1/32 contract while retaining all finite-extraction/CDG compatibility assertions. Mountain-weight, offshore exclusion and cross-region radius mutations must fail.
