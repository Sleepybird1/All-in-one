# Vanilla-led village distribution

User direction, September 11: villages from all mods should occur where a Minecraft village would occur; most should be small regular villages, with CTOV rare because of its large loot supply. Applied to Overworld villages and generated MineColonies colonies/camps; native alien and Nether settlements retain their separate destination context.

Authoring source: `tools/build_village_distribution.py`, `progression/village-distribution/`. Current installation is proven only by an `APPLIED` deployment receipt in that directory.

## Placement and size

The later global-spacing request supersedes the earlier separate vanilla village grid. All 27 village choices participate in `industrial_colonies:global_landmarks`, alongside other Overworld landmarks. Its 384/256-chunk spacing/separation and 0.5 frequency keep candidate origins at least 4,096 blocks apart. Their original biome eligibility is intersected with the union of the five native village-biome tags. This blocks non-vanilla village habitats without expanding a style into unrelated biomes. The empty jungle-village restriction is preserved.

All five vanilla village styles use jigsaw depth 4 instead of 6, reducing extended roads and village spread while retaining native houses, inhabitants and loot. The separate full-footprint terrain guard still requires dry, nearly level ground; being in an eligible biome alone does not permit a village to bridge a river.

## Selection weights

- Each of the five vanilla village styles has weight 1,000.
- Five small CTOV styles—plains, desert, savanna, snowy igloo and taiga—have weight 20 each.
- Other eligible Overworld settlements have weight 1 each.
- Medium, large, fortified and other CTOV variants are absent from the shared spawn pool.

CTOV's automatic small/medium/large village injection is disabled in its config so it cannot add its original high-weight pool back. Its automatic pillager-outpost injection is also disabled; outpost variants participate in the global pool. CTOV remains an occasional small-village variant, around 2% of eligible selection weight in the usual matching biome, not a guarantee of an exact observed fraction. Biome filtering and whole-structure terrain rejection affect actual encounters.

Standalone Overworld village/camp sets are disabled. Pooled entries are removed from mixed sets; entirely pooled sets have frequency zero. MineColonies' remaining Nether colony retains its original placement frequency, since the removed Overworld styles were never eligible there. Alien villages and Nether piglin villages retain their own generation. Ships share the global grid.

## Validation

Native tests inspect all 83 restricted structure definitions, compare the loaded shared pool against the authored 27 entries, verify the native placement fields, reject alternate active settlement sets, check vanilla depth 4, and calculate eligible vanilla selection weight for each vanilla village biome. The minimum must remain at least 95%. Existing Glacio, dry-terrain, jungle-removal, Venus, ownership and recipe acceptance checks run with this candidate.

The combined installer backs up exact replaced files and verifies all installed hashes while preserving unrelated recipe/UI assets and prior worldgen policies. Existing worlds are not rewritten: restart, then explore newly generated terrain to see the new distribution.
