# Foundry Route-Parity Audit

Status: **implemented in the authoritative seed**.

## Decision

Keep both foundry systems, but replace the eight generic automatic gate rings with real Industrial-Iron manufacturing. Do not restore the cheap stock endpoint recipes.

TFMG remains first. Create Metallurgy's casting blocks are upgrades of TFMG casting/refractory hardware; its alloy mixer consumes a TFMG industrial mixer. Modern Foundry's scorched endpoints then consume the earlier casting line or TFMG pressure-rated fluid infrastructure.

## Why the subsystems cannot be deleted

| System | Audited functional recipes | Distinct output references | Output references with no producer outside that namespace |
|---|---:|---:|---:|
| Create Metallurgy casting + alloy finishing | 149 | 148 | 60 |
| Modern Foundry table/basin routes | 773 | 496 | 385 |
| TFMG casting | 5 | 5 | n/a |

Create Metallurgy also has **424** installed recipes across melting, bulk melting, alloying, and casting. TFMG's **5** casting recipes are canonical for its own industrial line, not replacements for hundreds of unique foundry routes.

## Manufacturing result

- 7 Industrial-Iron compacting recipes.
- 1 Industrial-Iron sequenced assembly, upgrading the TFMG Industrial Mixer into the Create Metallurgy Foundry Mixer.
- 9 exact stock recipe removals.
- 8 automatic gate-ring owners retired.
- 0 assignment edits and 0 subsystem deletions.

This supersedes the tentative `redundant_should_retire` label. Its required parity proof failed, while physical TFMG-first gating remains intact.

## Implemented proof

The authoritative seed adds the eight source-owned contracts without changing assignments. Its post-batch SHA-256 is `FEAFDF1383C840D750AA93D45F17A28DBEEA8E6B8FFDE0C9995177FA0873BAB3`; the unchanged assignments SHA-256 is `329FA3F02EFDF9544CC3F4923FFF995EB8C3502401526A6521449134CDCCE24E`. An isolated rebuild produced 329 managed recipes (75 automatic), 397 compiled KJSGen cards, 661 exact removals, 33 intentional skips, and no dependency warning.
