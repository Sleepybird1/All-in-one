# Development-only normal-terrain acceptance test

This source set is not part of the shipped Industrial Colonies JAR. It runs against the unchanged candidate from the isolated stage, plus that stage's documented 233-JAR server-compatible subset. Do not install the addon or fixture into the live pack.

The `world-template` datapack replaces the GameTest server's hardcoded flat preset with the exact vanilla normal-preset dimension objects, plus the installed Rocketnautics deep-space object required by that mod. The Overworld still references `minecraft:overworld` noise settings, allowing the installed Tectonic resource to apply. GameTest fixes the seed to 0 and disables structures; this is not a full survival-world test. Two distinct fresh world directories are required.

The harness checks the actual noise-generator type, settings key and Tectonic resource provenance. It searches up to 289 regional decisions for three accepted multi-chunk formations with approved rich pools. It prefers two spacing families, but reports the actual diversity if the bounded search yields only one. Plans with seeded host-indicator placement are excluded to avoid confusing pre-rich host counts with later indicator blocks. Default geology configuration is not modified.

Each selected shape may request 2–25 full chunks; at most 60 distinct target chunks are requested across all three shapes. Requests occur serially, one per server tick. Temporary test tickets hold only these target chunks until scanning finishes. Minecraft can generate additional dependency chunks; the target cap is not a cap on all terrain work. The eight-minute test wall guard cannot interrupt an individual synchronous chunk request, so watch the external process and preserve diagnostics if it stalls.

For each formation the test compares final low-yield host, rich and associated blocks against production placement observations. Rich quotas and weighted pool splits must match. Actual terrain-clipped size need not equal intended size. The test records full sorted shape-state and retained-material SHA-256 hashes, biome evidence, boundary adjacency and request timings. A passing report does not itself require observed RU biomes or a nonzero boundary adjacency; inspect those fields before claiming that coverage. Same-material trace generation or later feature overwrites can cause a recount failure and must be investigated, not automatically waived.

Launch through both the stage's `geology-smoke.init.gradle` and `terrain-smoke.init.gradle`, with `-PterrainOrder=a` or `b`. Keep Gradle offline and the documented approval/exclusion constraints. `a` and `b` use separate fresh worlds and reverse direct chunk requests. The corrected runs add `-PterrainRevision=fixed1`, producing distinct `terrain-a-fixed1` and `terrain-b-fixed1` worlds/reports; the original mismatching A/B worlds remain preserved. Future runs need a new revision and fresh fixture copies, not these already-generated directories. The test source set needs its own DevLaunch runtime dependency because it is attached after the original run was configured.

After both tests finish, from the project root:

```powershell
& .\tools\terrain-smoke\compare-terrain-reports.ps1 -Stage '.\isolated-runtime\geology-gametest-20260909-001051-895' -Revision fixed1
```

Comparison requires both reports to pass, identical settings and selected formations, exactly reversed direct requests, and identical per-formation state hashes, counts and biome metadata. Minecraft's dependency-halo order is not fully controlled. This small same-seed check does not certify all resources, all quality tiers, population distributions, oil, graphics or recovery economics.

Timing interpretation: search elapsed includes nested spacing/noise sampling, shape creation and report IO. A full-chunk request includes other mods, dependency generation, IO and waiting. Neither number is a geology-only benchmark.
