# Changelog

## 2026-11-01 — accumulated Industrial Colonies / All-in-one checkpoint

This is a broad repository synchronization after the September21pack commit, preserving the six newer GitHub portrait/icon commits. It combines current installed pack files and review data with the separate source/development snapshot. Inclusion in Git is not a new deployment or a claim that every staged feature is finished.

### Pack and development source

- Include Industrial Colonies Java/resources, Gradle setup, build dependencies, design documents, processing/progression definitions, pack overrides and authoring/test tools in the main repository.
- Capture installed Industrial Colonies and auxiliary foundry, tree/resin and berry-comfort packages, plus the actual current mod/version additions, removals and enabled/disabled filenames. Binary archives use Git LFS.
- Preserve source master tracking at204/289complete(70.6%). Saved native worlds, caches, build output and large private evidence remain local.

### Recipes, manufacturing and material forms

- Capture the current KJSGen Approved, Personal, Progression, Material Processing, Maybe, Deferred, Disabled and Rejected project files and review ledger without flattening their decisions into gameplay approval.
- Include separate canonical plate/sheet/rod/dust registrations and assets, material-specific coloring, duplicate/retired-item compatibility and JEI authoring visibility. Ordinary plate/sheet forms are distinct; Heavy Plate is not a generic Steel Plate.
- Preserve accepted NuclearCraft composite-plating appearance and Lead-Graphite Composite replacement for retired Basic Plating; chassis ingredient ownership uses TFMG Steel Frame.
- Include installed manufacturing/fusion recipe scripts, exact-machine sequence routing, bootstrap fixes, rubber ownership, installer-based Mekanism upgrade gates and existing recipe-ownership cleanup.
- Record69rebalanced construction drafts and1rejected quantum-processor machine correction with native generation/validation and review-policy evidence. New drafts are not auto-exported. Brass Pattern Provider was judged worse and still needs a rethink; the batch is not user-approved as a whole.
- Clear397restore-default rejection records and prepare85native default recipes for67affected runtime outputs. Fixture-tested late restoration avoids the undefined-to-boolean callback failure; native reload/JEI results still need verification. Three competing NuclearCraft fluid-tank cards moved to Disabled.

### Fusion, nuclear power and machines

- Include the approved Fusion Control Bearing item, exact5x5recipe, accepted nickel-frame/Allthemodium geometry and separate inventory/held rendering. Later longer-rod geometry is retained.
- Include the current Fusion Control Unit 3D frame with pipes, coils, full front circuit board, raised chip carriers/dies/pins and contact clearance. Rejected sprite-sticker and flat-module experiments are not selected replacements.
- Capture compact Pulse Power and Magnet Protection models and their saved mixed-tier electronics sequences. Keep the latest pending controller's Platinum-bed/Osmiridium/Iridium/shielding sequence distinct from older installed exports.
- Include current MSR controller/cell/port and shielded Fuel Reprocessor review drafts. Preserve the user-liked Reprocessor layout while strengthening material/control prerequisites.
- Reactor order is Fission → MSR → Fusion as practical energy progression. Prior reactors should make later manufacturing practical, but skipping a tier remains possible. Immense fusion manufacturing/operating-energy targets are design-only; actual numeric power balance is not implemented.

### World, resource and physical-industry work

- Include current finite-deposit, clue/prospecting, cave/surface-resource and continent-binding configuration and source; staged resource/depletion, tree/resin, foundry capacity and processing work retain their documented acceptance limits.
- Include machine/recipe ownership, late manufacturing, material processing, regional oil, worldgen/structure and physical logistics source/design snapshots. Historical native results do not certify the entire current source snapshot.
- Keep geographic/resource/yield decisions and finite factory-demand balancing in the linked source task/design documents.

### Space, ships and AE2 design notes

- Consolidate ship/freight/station/oxygen/propulsion and recovery development notes with clear staged/installed/native status. No new saved-world movement or runtime flight is performed by this checkpoint.
- Record chest-first AE storage: ME Chest as initial one-cell host, standard Drive much later, Extended Drive at endgame. Matter Stabilizer's selected ship exception is ME Chests only; old stabilized-drive proposals are superseded.
- Record individual-cell power on occupied bytes at ordinal1×/2×/4×/8×rates; earlier cells are not repriced. Base power, tier interaction, cell ranking/counting and anti-swapping/subnet bypass rules remain undecided.
- Record expensive late-game stackable Energy Efficiency Cards with diminishing extra savings.50%first-card and10percentage-point second-card examples are provisional, not an implementation.
- Keep item-per-byte/weighted-item/per-type-cap alternatives unselected; preserve silos/vaults for bulk and consider Storage Bus access to physical inventories. Huge top-tier digital capacities still need their own cost/capacity curve.
- Retain30stacks-per-connected-Vault-block/oneitemtype, cargo-dependent Vault mass, volume-scaled Copycat material mass, passive physical storage, late cells/housings and competing-tank ownership as design tasks where not yet implemented.

### Validation and remaining work

- Publication checks cover JSON readability, changed script syntax, content/hash inventory, preserved remote changes, staged sensitive-file checks and LFS pointer coverage. No game restart, full build, native reload, save conversion or new gameplay acceptance is implied.
- Earlier69draft+1material native generation/validation, exact-item/no-retired-basic-chassis checks, candidate-cycle checks and real Rhino/Java callback regression are retained as scoped evidence, not comprehensive survival or JEI proof.
- Continue from README To do and Design notes. Exact recipe pricing, power rates and efficiency percentages remain open; preserve approved/personal edits and parked decisions.

See [publication inventory](docs/checkpoints/2026-11-01/PUBLICATION_INVENTORY.json), [mod changes](docs/checkpoints/2026-11-01/MOD_CHANGES.md), [source checkpoint history](docs/checkpoints/2026-11-01/SOURCE_COMMIT_HISTORY.tsv), and [historical desktop action log](docs/history/DESKTOP_ACTION_LOG_2026-11-01.md).
