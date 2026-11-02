# Ship damage, repairs and encounters — review proposal

October 12, 2026. Prepared for the user's overnight review. These are proposed design values, not installed settings or accepted gameplay. Recipe costs remain expressed in existing part families until the construction batch is reconciled. The proposal-preparation task can finish independently; collision implementation, fracture custody, difficulty qualification, rewards and integrated combat remain separate tasks.

The intended experience is a ship that can survive an awkward docking attempt, suffer localized damage in a serious collision, and lose a section in a crash. Damage should create a repair or salvage problem without making an entire inventory disappear. Factories, trains and physical freight remain useful; repairing and refuelling a ship should draw on the same manufacturing chains used to build it.

## Proposed balance

| System | Starting proposal | Player-facing result |
|---|---|---|
| Low-speed contact | No additional hull damage below 1 block/second of closing speed along the contact normal | Docking bumps and stationary rubbing do not grind a ship apart. Native collision response still occurs. |
| Glancing contact | Measure normal closing speed at the actual contact point, including angular motion; tangential speed alone does not set damage | A scrape is less destructive than a direct impact at the same overall speed. |
| Moderate impact | From 1 to 3 blocks/second, allow localized wear only; no newly removed blocks | Pilots get visible damage to repair before structural failure. Exact visual implementation is separate. |
| Damaging impact | From 3 to 7 blocks/second, allow local hull failure, beginning at the contact surface | A collision damages the nose or wing that hits, rather than random distant blocks. |
| Severe crash | At 7 blocks/second or above, permit deeper local damage and native splitting when structural connections are actually lost | A ship can break apart because its connecting structure is destroyed. There is no scripted whole-ship explosion. |
| Damage work budget | At most 16 structural removals from one fresh contact episode, 32 per ship per server tick, and 64 globally per server tick | Limits sudden server work. A cap does not authorize repeatedly charging a resting contact. |
| Contact deduplication | Aggregate solver contacts for the same body pair and local impact region; release the episode after 10 separated ticks | Multiple physics substeps cannot multiply one impact into dozens of independent hits. |
| Material resistance | Start with native block resistance where meaningful; compare accepted hull materials in a calibration fixture before setting multipliers | Better hull construction matters. Decorative blocks do not become arbitrary invulnerable armor. |
| Repair access | Manual repairs while safely held; dockside maintenance for substantial reconstruction | Emergency patching is possible, while major repairs support a workshop and supply line. |
| Repair cost | Replace missing blocks with the exact corresponding blocks; repair wear using matching plate/frame parts, with no upgrade in material grade | A cheap patch does not turn into stronger armor or a complete free machine. |
| Repair throughput | Proposed dockside limit: one ordinary hull block per second; machinery reinstatement requires its real finished item | Large repairs have a time and manufacturing cost. No final recipe price is implied. |
| Cargo damage | Structural hull damage first; inventory-bearing blocks enter the damage pool only after their native break/drop and restart behavior is qualified | Storage is not permanently invulnerable, but an untested duplicate/drop path cannot be enabled. |
| Fragments | Let Sable perform topology splitting. Preserve physical cargo and body lineage; stop invalidated automation leases | Broken sections remain actual wreckage. Splitting never manufactures a second owner, inventory or encounter reward. |
| Empty debris | Proposed cleanup after 10 unloaded minutes, only for verified empty NPC debris with no player ownership or boarding | Abandoned empty debris can be reclaimed without deleting valuable wrecks. Time alone never authorizes cargo deletion. |
| Salvage | Surviving hull blocks and existing cargo are the initial reward; no extra loot roll for the same recovered material | Salvage is useful without paying twice for one wreck. Additional encounter rewards need their own durable once-only receipt. |
| First encounter | One scout, one pass, at most one native shot, then retreat | Introduces hostile ships without an endless chase or immediate fleet battle. This matches the bounded shape of the existing controller. |
| Escalation | Start with one active encounter per participating player and two globally; do not escalate from inventory value or total playtime alone | Carrying valuable freight does not secretly summon a stronger opponent. Actual supported defensive hardware and an explicit encounter tier determine eligibility. |
| Encounter pacing | Proposed 15-minute quiet interval after completion, plus 0–5 minutes of deterministic jitter; held/unresolved encounters occupy their reservations | Predictable minimum recovery time, without restart farming or repeated rerolls. Automatic spawning stays off until its full admission path is qualified. |
| Target selection | Explicitly approved player-owned targets or commissioned hostile NPCs; friendly exclusion wins | A neutral base, unrelated ship, or nearby player cannot become collateral merely by being close. |
| Warning and escape | Proposed 10-second warning before approach; failed safety or ownership checks hold, and no automatic resume follows | Players can understand the threat. A repaired sensor or re-enabled switch does not unexpectedly resume firing. |
| Weapon economy | Native ammunition, loading and cooldowns; no infinite ammunition or shortened cooldown to fit a design target | Manufacturing and resupply constrain firepower. Existing one-shot tests do not justify sustained volleys. |
| Retreat | Disengage on lost propulsion, unsafe clearance, invalid aim, ammunition exhaustion or loss of target authority | A damaged AI should not teleport or issue impossible thrust demands to continue fighting. |
| Boss encounter | An explicit late-game opt-in mission, separate from ambient scouts | A large battle cannot appear while the player is still learning the first ship systems. Boss geometry, weapons and rewards remain unbuilt. |
| Jetpacks and storage | Keep the recorded transport-preserving limits: short personal flight, modest portable tanks, late digital storage | A jetpack or pocket tank should not replace ships, trains, vaults and bulk logistics. Exact item-specific values belong to their balance tasks. |

## Collision calculation and custody boundary

Measure both bodies in one verified native frame. At a contact point, use `v_contact = v_linear + angular_velocity × offset_from_center_of_mass`. Project relative contact velocity onto the verified normal and retain only the closing component. Convert native time units explicitly before comparing with the blocks-per-second thresholds above. Do not compare a blocks-per-tick reading directly with these numbers, use distance from an old position as an impulse, or equate orbital speed with local collision severity.

As an initial calibration model, normal impact energy is `0.5 × effective_mass × closing_speed²`, with reduced mass for two dynamic bodies and the dynamic body's mass for a static obstacle. Native engine mass units are not established kilograms. This is an ordering/calibration input, not a ready-to-use block damage formula. Verify contact orientation, angular contribution, participating mass and solver event timing before any damage write. Unknown or stale observations refuse additional damage. Do not alter the native physical impulse to make a damage test pass.

Deduplicate contact manifolds and charge one bounded damage budget per episode. Long resting contacts and repeated substeps must not repeatedly spend the original collision energy. Persistent wear must be capped, tied to exact blocks/body lineage, and cleared or migrated only with validated native block replacement or splitting. New blocks must not inherit an unrelated predecessor's damage.

Use native block removal and native splitting. Do not copy inventories into replacement fragments, restore cargo from an earlier snapshot, duplicate block drops, or delete the source before ownership is certain. Record a durable intent before destructive work; after interruption, compare actual native bodies, blocks and inventory totals before settling the result. Any ambiguity holds subsequent automated damage or cleanup rather than replaying removal. This proposal does not claim a transaction can make arbitrary native calls atomic.

Separate the global collision-damage feature switch from enemy automation control. Both remain disabled for production in this proposal. When collision damage is eventually enabled, stopping enemy automation must still stop enemy actuators immediately; it must not silently change native physics. Restart cannot replay an encounter, a damage budget, a repair debit or a salvage reward.

## Implementation and validation sequence

| Work | Required proof before claiming completion |
|---|---|
| Collision observation | Isolated ordinary native contacts at rest, a glancing scrape, head-on impact and rotating-arm impact; verify units, normals and unique episode identity. |
| Local hull damage | Threshold boundary tests, unknown-owner refusal, protected foreign body refusal, and bounded server work; low-speed cases remove no blocks. |
| Structural breakup | Damage a real connecting section and observe Sable split; account for every surviving block, body identity, controller and finite resource. Reuse existing fragment identity evidence where unchanged. |
| Cargo-bearing damage | Native chest/tank/machine break paths, full output space and blocked output; exact total items, fluids and metadata before and after, including held restart. |
| Crash recovery | Separate before-write, after-partial-write and acknowledged restart cases; preserve actual persisted state and never reconstruct lost material to make a test pass. |
| Repair | Debit once, place once, output/cargo capacity checks, interrupted repair hold, no stronger replacement from cheaper input and no duplicate refund. |
| Encounter difficulty | Genuine approved player ownership and supported equipment sampling; unapproved/friendly/unknown equipment refuse. Then qualify one conservative scout before sustained combat. |
| Rewards and salvage | Once-only settlement tied to persistent encounter identity, player boarding/ownership changes, repeated unload/restart and duplicate-claim refusal. |
| Integrated playthrough | Real player acquisition, finite supplies, warnings, retreat, repairs and transport tradeoffs. Automated component tests cannot substitute for this review. |

## Evidence reused and limits

- `workflow/enemy-ships/native-hull/FRAGMENT_REVIEW.json`: accepted bounded native fragmentation retained 18 remaining blocks, six chests, 15 papers and 21 diamonds across five bodies/three roots. That was a supplied fixture, not collision severity calibration or arbitrary inventory destruction.
- `industrial-colonies/src/main/java/dev/godpc/industrialcolonies/space/enemy/EnemyEncounterController.java`: current staged controller is one pass/one shot and uses a short local envelope. Its permitted attack range is 12–48 local blocks and lifetime at most 600 ticks; these are technical limits, not a certified global encounter design. Do not stretch them merely to implement the proposed pacing.
- `industrial-colonies/src/main/java/dev/godpc/industrialcolonies/space/enemy/EnemyImpactAuthority.java`: rechecks exact current ship ownership and target body before guarded impact; entity damage is unqualified. Collision work needs its own authority path and must not borrow projectile admission as a general permission to destroy blocks.
- `workflow/enemy-ships/native-player-access/PLAN.md`: genuine player ownership and capability prerequisites remain distinct from NPC fixture acceptance. No player is invented while the user is asleep.
- `industrial-colonies/MASTER_TASKS.json`: enemy work currently has 19/24 tasks complete; difficulty, first boss, rewards, salvage and integrated acceptance remain open. This document closes only preparation of a reviewable design proposal.

No production installation, automatic encounter activation, recipe export, save edit or push accompanies this proposal. The next collision implementation step is a read-only native contact observer in an isolated fixture, before adding block damage.
