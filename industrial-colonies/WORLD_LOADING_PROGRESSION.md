# Powered World-Loading Progression

This slice closes three ways to bypass the pack's intended powered-factory progression while preserving ordinary FTB Chunks land claims.

## Recipe policy

- `ae2:network/crystal_resonance_generator` is retired by exact recipe ID. The Crystal Resonance Generator is an energy source with no ongoing fuel or grid-infrastructure requirement, so the pack deliberately provides no replacement producer.
- `advancedperipherals:chunk_controller` is rebuilt as a 5x5 Create Mechanical Crafting recipe in **High-Energy Grid**. It requires an AE2 Spatial Anchor, Ultimate Energy Cube, Advanced Computer, Advanced Wireless Modem, and Engineering Processor. This also gates the Chunky Turtle route that consumes the controller.
- `mekanism:dimensional_stabilizer` is rebuilt as a 5x5 Create Mechanical Crafting recipe in **High-Energy Grid**. It requires an AE2 Spatial Anchor, Ultimate Energy Cube, Ultimate Control Circuit, Advanced Computer, and Engineering Processor.
- Only the three exact installed stock recipe IDs are removed. There is no namespace-wide AE2, Advanced Peripherals, or Mekanism removal.

All three gated world-loading devices are grouped under `CR01 — World Loading Technology`. The Spatial Anchor recipe remains the common infrastructure prerequisite used by the two larger builds.

## FTB Chunks pack default

The authoritative pack source is `pack-config-overrides/ftbchunks-world.snbt`; deployment copies it to `<instance>/config/ftbchunks-world.snbt`, which is the location documented and loaded by FTB Chunks 2101.1.21 for modpack defaults.

The relevant values are:

- `disable_protection: false` — claimed chunks retain normal protection.
- `claiming.max_claimed_chunks: 500` — claiming remains available.
- `force_loading.max_force_loaded_chunks: 0` — ordinary players receive no free FTB Chunks force-load quota.
- `force_loading.hard_team_force_limit: 0` — in FTB Chunks this value means “no additional hard team cap,” not “zero chunks.” The zero quota is therefore set on `max_force_loaded_chunks`.
- `force_loading.force_load_mode: "default"` — the online/offline policy is unchanged; quota, not a global feature disable, closes the bypass.

FTB Ranks permissions and explicit extra-force-chunk grants can override the configured maximum. Those remain deliberate administrator controls rather than normal player progression.

## Existing-world migration

The pack-level file does not delete claims, alter claim ownership, or disable protection. FTB Chunks recalculates team limits from the updated config, so teams without an override receive a zero force-load allowance on the next config/world load.

Two pieces of state are intentionally not overwritten by deployment:

1. A world-local `<world>/serverconfig/ftbchunks-world.snbt` overrides the pack default. Server owners must set its `force_loading.max_force_loaded_chunks` to `0` themselves; the deployment script does not overwrite administrator-owned world configuration.
2. Existing force-load marks are persistent team data. Lowering the quota prevents new free marks but does not automatically erase old ones. An administrator should clear legacy marks with FTB Chunks' `unload_all` command as part of migration, after making a world backup. This clears force-loading state without unclaiming the chunks.

The two currently audited local worlds had empty FTB Chunks chunk maps, so they had no legacy force-load marks to clear at audit time. This observation is not a substitute for checking any additional server worlds before rollout.

## Verification

Run:

```text
python tools/validate_world_loading_progression.py --catalog <recipe-catalog-current>
python -m unittest tools/test_validate_world_loading_progression.py
```

The deployment preflight invokes the validator with the selected static recipe catalog. It fails closed if an installed update adds a second stock producer for one of these outputs, if a physical gate is removed, or if the FTB Chunks source grants a positive free force-load quota.
