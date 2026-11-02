# Collectible surface prospecting rocks

Small loose rocks sit on dry, solid natural ground. Each clue site contains 2–4 rocks of the same material. The shapes reuse the approved geology textures; they are small ground models, not additional full-sized ore blocks.

Right-click with an empty hand to collect one, or break it by hand. Each rock gives one existing low-yield geological processing feed; loose coal gives one coal. They do not respawn after collection, and no new processing recipe is needed.

## Reading a clue

Most naturally generated sites indicate a nearby matching regional deposit. Hematite points toward iron-bearing hematite, cassiterite toward tin, sphalerite toward zinc, and so on. The clue does not tell you the depth, quality or size of the deposit. Small rocks do not promise rich ore.

The default proposes **95% deposit-linked sites** and **5% false leads**. A linked site is only placed after checking for actual surviving matching deposit blocks in the same chunk, within the planned formation. False leads are offset 160–224 blocks from the candidate deposit and require no vein beneath them. Both branches look and behave identically.

Ground conditions can prevent either type from appearing. The 95/5 split is a selection setting, not a measured guarantee that exactly 95% of encountered rocks have ore beneath them. Player-placed rocks are not geological evidence.

The 21 supported materials are hematite, magnetite, chalcopyrite, sphalerite, galena, pentlandite, bauxite, spodumene rock, argentite, wolframite rock, dolomite, graphite rock, phosphate rock, ultramafic rock, ilmenite, bertrandite, borax rock, cassiterite, chromite, cinnabar and coal. Existing gold flakes remain separate; radioactive surface rocks are not added.

## Configuration and world generation

`config/industrial_colonies/worldgen/surface_rocks.json` is created automatically. Change `linkedSiteChance` or `enabled`, then restart Minecraft. This file is separate from existing world-generation overrides.

Rocks appear only in newly generated chunks. No existing saves are rewritten or retroactively decorated. Placement is deterministic and stays within the owning chunk.

## Validation status

- Java 21 / NeoForge build passed.
- Archive audit: all 42 existing PNGs, existing recipes and unrelated class/resource entries are unchanged. Only the geology hooks, version metadata and added translations change existing entries; new entries supply cave traces and surface rocks.
- All eight required native GameTests passed in `isolated-runtime/cave-traces-01/launch-surface-r2.log` (2m59s). Each of the 21 types passed hand-break loot, right-click pickup and duplicate-pickup rejection. A 50,000-site selector sample produced 47,550 linked proposals (95.1%).
- The fresh-world check observed four genuine Pentlandite rocks in chunk [277,133] with matching surviving deposit blocks, and two unrelated Hematite rocks in chunk [21031,145]. This verifies both branches, not an encountered-clue reliability percentage across the world.
- The first natural search stopped at 396 regional candidates without finding a rare decoy. The passing test widened its bounded search to at most 4,092 candidates without changing production rarity. Its original failed log is retained as `launch-surface-r1.log`.
- Full-client render: PASS, all 21 models / 252 quads, with a captured and visually inspected native screenshot. Evidence: `isolated-runtime/surface-client-02/launch.log` and `surface-rocks.png`; launch completed in 1m30s. The first attempt failed before rendering in the Quark/Zeta bootstrap; the successful fresh retry supplied the verified clean Minecraft input used by earlier Connector tests.
- Runtime-tested candidate SHA-256: `C4BCAA9D8068B592A435AF18492A66E3C495BB3112A29C31796B5F25541E5BC2`. Final candidate SHA-256: `7219C29073CF45918E4BD8A64127E4D83147CC277120E334BE10242882078749`. The final build fixes duplicated "Rock" words in display names. Archive comparison verified identical code/model bytes and semantically identical loot; loot JSON key order also changed. The final Java/NeoForge build passed; the game was not rerun for this display-name-only correction.
- Installed as 0.5.1 in **All in one**, September 9, 2026 at 18:21 Eastern. The installed JAR hash matches the final candidate. Previous 0.5.0 is backed up under `_industrial_colonies_backups/cave-traces-0.5.1-20260909-182157/`. No saves, recipes or existing configs were replaced. Receipt: `build/cave-deployment.json`.
- The user clarified that the goal is giving caves a reason to be explored. The chosen approach is the installed cave-wall resource patches plus occasional natural major-deposit discoveries, complemented by collectible surface clues. No mandatory connection between every cave and major vein is pending or claimed.
