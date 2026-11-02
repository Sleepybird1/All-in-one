# Mountain surfaces and Stellaris placement

September 12, 2026 INSTALLED: Industrial Colonies 0.5.5. Check
`progression/mountain-surface/deployment.json` for installation status; a build or
passing test alone does not mean the live instance has been updated.

The cliff building at approximately X=5496, Z=20673 was identified from the
now-deleted ReTerraForgedNEW (2) save as `stellaris:earth_satellite`. Its saved
piece box was [5480,401,20648,5504,442,20672]. Its native definition projects onto
WORLD_SURFACE_WG; the earlier airborne exemption was incorrect and is removed.
The Earth Operation Base is surface-projected but declares underground_structures.
It and Mercury Lava Mines now receive the dry/flat footprint check despite that
generation-step label. The second screenshot was not independently identified
before its world was deleted; the operation base is a definition-audit finding.

The satellite must pass both the full dry/flat footprint test and a summit test:
at least 160 blocks above sea level; no higher shoulder at an inner ring; ground
at least 12 blocks lower in all eight sampled directions at the outer ring.
The rings extend beyond the footprint. This deliberately makes these sites rare.
It selects suitable summits rather than moving structures to arbitrary peaks or
flattening mountains. The test samples surrounding terrain and is not a
mathematical proof of a regional maximum.

Both Earth buildings now share the existing 384/256-chunk, frequency-0.5 global
landmark roll. Their independent sets have frequency zero. Stellaris meteors
are split: `industrial_colonies:stellaris_overworld_meteor` is in the global pool,
while the native structure excludes Overworld biomes and retains other native
eligibility, including the Moon. Final shared pool: 103 entries. Seven exact
KubeJS resource candidates are listed in `progression/mountain-surface/live-manifest.json`.

After Overworld biome decoration, `MountainSurface` replaces exposed natural
ground with snow blocks in stable patches starting at Y=320, continuous from
Y=400. It leaves ore, roofs, foliage, fluids and air unchanged, does not fill
caves, and does not alter mountain geometry. Full snow blocks provide persistent
coverage in warm biome IDs on tall mountains. It does not blanket ground hidden
under a tree canopy. No other dimension receives this surface pass.

Natural Regions Unexplored peat grass/dirt/coarse dirt/podzol/mud above Y=135 is
replaced with stone, including cave surfaces. Y=135 is the pack policy chosen from
the current THE PACK dirtMin=95 plus dirtVariance=40; it is a fixed pack threshold,
not dynamically bound to future preset slider changes. Lowland peat remains.
Farmland and paths are excluded. Existing chunks/saves are never rewritten.

Validation: production build passed; native r15 passed all four required tests
with 102 global entries. Final r16 PASSED all four required tests, including the meteor split and native biome
eligibility. The surface tests use a real tall ProtoChunk to check high cave peat,
preserved lowland peat, snow on rock and preserved ore. Summit tests exercise
supported peaks, shoulders and high plains. This fixture does not establish a
visual result in the user's ReTerraForged preset; newly generated terrain after
installation is the visual acceptance check.
