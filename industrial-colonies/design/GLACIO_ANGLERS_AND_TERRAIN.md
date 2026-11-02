# Glacio Anglers and dry land structures

Authority: September 11 user requests to move Cataclysm's Deepling Angler to another planet, explicitly selecting Glacio, and to prevent villages, portals and other land structures from occupying rivers or uneven terrain. The working interpretation preserves ships and intentionally underwater structures, plus underground and airborne structures that do not have a land foundation.

## Glacio habitat

`tools/build_glacio_anglers.py` authors `progression/glacio-anglers/`. Glacio's native noise terrain, surface rules, biomes and ores are retained. Its uniform fluid picker is retained, the default fluid becomes water, and the water table is set to Y=0 to fill lower caverns beneath its frozen surface. An initial randomized-aquifer candidate left the sampled caves dry and was rejected during validation. This changes new Glacio terrain only.

Deepling Anglers are removed from the native deep-ocean biome spawn tables and added to both Glacio biomes. Native weight 2, one-mob groups, water-only spawning and random spawn-roll restrictions are retained. Ordinary Deeplings are not moved. Anglers and their native companion lionfish gain Ad Astra cold tolerance. Player survival requirements are unchanged.

Ten Sunken City templates contain 17 `deepling_angler` data markers, which are replaced with ordinary `deepling` markers. All other template bytes, including blocks and loot, are preserved apart from NBT string lengths and compression. Native Minecraft template loading is checked by the runtime test. Existing entities and saved structures are not edited.

## Terrain placement

Industrial Colonies 0.5.4 adds `SurfaceStructureTerrainMixin` and `SurfaceStructureTerrain`. The guard evaluates a completed surface-structure layout before returning its start, so rejection happens before any pieces or terrain adaptation are placed. It checks every terrain column within the union bounding rectangle of its pieces, with a one-block margin. Any exposed fluid, more than six blocks of overall elevation range, or a neighboring two-column difference above two blocks rejects the whole structure. A coarse first pass rejects unsuitable sites early; it never replaces the complete column check for accepted sites.

The check uses the chunk generator's base terrain without requesting neighboring chunks during the structure-start phase. This avoids recursive chunk-generation deadlocks and checks the river/ocean terrain under an entire village, not only its center. Later decorative features, player-placed water and existing saved structures are outside this pre-placement check. Structures implemented entirely as features rather than registered structure starts do not pass through the base Structure generation method.

`data/industrial_colonies/tags/worldgen/structure/terrain_fitting_exempt.json` records exceptions: ships, deliberate underwater structures, rare Foundry islands, a satellite, and explicitly underground structures whose mods label them as surface structures. Other generation stages, including ordinary mineshafts, remain outside this surface-foundation rule. Spacing settings are unchanged; rejected terrain means fewer successful structures, especially large villages and mountain variants.

## Verification and installation

The isolated tests check actual vanilla and CTOV village generation and ruined portals on dry versus water-covered terrain, narrow interior water strips and ledges, and ship/underwater exemptions. Glacio tests inspect all biome spawn tables, parse the ten modified native templates, generate actual Glacio chunks, test the native aquatic spawn rules and observe an Angler and its lionfish for cold survival. Existing recipe, ownership, bucket-volume and Venus checks run alongside these tests.

Installation is complete only when `progression/glacio-anglers/deployment.json` records `APPLIED`. The installer preserves recipe/UI files, backs up exact changed targets, requires the live game closed for the JAR replacement and verifies installed hashes. A restart and newly generated terrain are required for world-generation changes.
