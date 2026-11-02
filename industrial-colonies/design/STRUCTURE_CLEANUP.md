# Ocean clutter and planetary expeditions

User direction, September 11: Modern Foundry floating slime islands are overwhelmingly common; make them disabled or extremely rare. Keep interesting boss ships but make them rare and prevent ships stacking. Remove jungle villages. Move the Block Factory Dragon Tower out of the Overworld and make large off-world dungeons rewarding destinations.

## Placement changes

| Content | Result |
|---|---|
| Modern Foundry ocean islands | Spacing 96, separation 48 chunks; frequency 0.05, previously spacing 30 / frequency 0.5 |
| Modern Foundry sky islands | Spacing 128, separation 64 chunks; frequency 0.05, previously spacing 35 / frequency 0.5 |
| Large surface ships | One shared `industrial_colonies:rare_maritime_sites` structure set, spacing 128 / separation 64 chunks |
| CTOV jungle and jungle-tree villages | Disabled for small, medium and large sizes |
| Block Factory Dragon Tower | Eligible only in the installed Ad Astra and Stellaris Venus biomes |

The island candidate densities fall by approximately 99.02% and 99.25%, respectively. These are placement-candidate calculations, not guaranteed counts per ocean: biome and terrain checks still determine whether a candidate generates. Nether and End islands remain unchanged, and the rare Overworld islands still provide their materials.

The shared maritime set retains Block Factory's Kraken Ship (weight 3), MineColonies' Ship (weight 2) and Iron's Spellbooks' Impaled Icebreaker (weight 1). Their independent original structure sets have frequency zero. The shared set selects at most one accepted structure at each site; a 64-chunk separation is comfortably larger than these structures' footprints. Biome suitability remains native to each ship. This prevents independent rolls for these three large ships occupying the same site. Vanilla underwater shipwrecks and other unrelated structures are unchanged.

CTOV's enabled-village config removes `jungle` and `jungle_tree`. All six corresponding structure definitions additionally use an empty biome tag, so enabling a config variant cannot silently restore the unwanted styles. Jungle pillager outposts are outside the village request and remain unchanged.

## Venus Dragon Tower

The tower retains its native structure type, size, templates and spacing of 96 / 24 chunks. Only its biome eligibility changes. Venus provides a later expedition destination appropriate to the Infernal Dragon; the pack's existing travel requirements still apply. Both installed Venus implementations are supported; neither Overworld nor other planet biomes are included.

The Infernal Dragon and three native tower guard types gain explicit oxygen, heat and acid-rain survival tags for their destination. Player life-support and travel requirements are not relaxed.

Existing chest loot and boss trophies remain. Additional loot pools are conditioned on being on Venus:

- Common chests add two supply rolls of gold, steel or copper.
- Treasure chests add four rolls of titanium, tungsten, platinum, pink high-density semiconductors or netherite, plus one or two enchanted golden apples.
- A player-killed Infernal Dragon guarantees 24–32 titanium ingots, 16–24 tungsten ingots, 16–24 high-density semiconductors, 4–6 netherite ingots and 2–3 enchanted golden apples, in addition to native bones and skull.

Boss bonus pools require a player kill. Their location conditions prevent existing Overworld towers from providing these planetary bonuses. Rewards are optional production savings and valuable combat supplies; no new mandatory dungeon recipe gate is introduced.

## Scope and verification

September 11 follow-up: Ad Astra ocean oil wells are now disabled at the user's request. `tools/disable_ad_astra_oil_wells.py` installs two overrides: `ad_astra:oil_well` structure-set frequency is zero and its native biome eligibility tag is replaced with an empty list. The installed mod's structure/tag linkage and both installed file hashes were verified; this small follow-up was not run through a new game launch. TFMG oil generation and all fuel recipes are unchanged. Receipt and backup location: `progression/oil-well-removal/deployment.json`. Restart before exploring new terrain; existing wells remain in saved chunks.

Source: `tools/build_structure_cleanup.py` and `progression/structure-cleanup/`. The scoped resource/config migration is deployed with the semiconductor/UI update. Native checks inspect the loaded structure sets and biome eligibility, sample 169 maritime candidates, check that no alternate large-ship set remains active, generate a valid multi-piece tower start using actual Venus terrain, verify atmosphere tags, and compare 100 treasure rolls on Venus with 100 in the Overworld.

Only newly generated terrain uses these placements. Existing ships, islands, villages and towers are not deleted, and saves/chunks are not edited. Removing existing generated structures would be a separate destructive world-editing task.

Installed status and backup location are recorded in `progression/structure-cleanup/deployment.json` when its status is `APPLIED`.

## Installed acceptance

Installed 2026-09-11T17:15:27.381369-04:00 with Industrial Colonies 0.5.3. Native revision r3 passed both required GameTests, including all 296 material recipes (145,310 assertions), 41 ownership checks, the 1,000 mB block closure, advanced semiconductor gates and Venus structure/loot checks. The client slot-rendering test passed and its seven-fluid screenshot was visually inspected. Exactly seven effective recipes changed; 26,444 unrelated recipes were preserved.

Backup: `C:\Users\GodPC\curseforge\minecraft\Instances\All in one\_industrial_colonies_backups\advanced-semiconductors-20260911-171526`. Live saves were not edited.
