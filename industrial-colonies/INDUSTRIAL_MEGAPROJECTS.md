# Industrial Megaprojects

The base-pack capstone appears in the item-only FTB Quests chapter named
`Industrial Endgame`. The chapter is guidance, not a gate; the recipes and
their physical dependencies are authoritative.

## Objective order

```text
Black Hole -> Industrial Reserve Core -> Industrial Star
```

## Black Hole

The Black Hole is an intermediate component made in one normal 3x3 crafting
grid. It consumes exactly one 9x compressed block from each approved renewable
bulk stream: cobblestone, stone, gravel, dirt, basalt, blackstone, oak logs,
sand, and oak planks. No metal, gem, or Allthemodium-family material is part of
this recipe.

Each 9x block represents `9^9 = 387,420,489` base blocks. The nine inputs
together therefore represent `3,486,784,401` manufactured base blocks.

## Industrial Reserve Core

One Reserve Core runs through 512 Creative-tier Sequenced Assembly loops. Each
loop deploys eight HDPE Pellets and one Plutonium Pellet, fills twice with
1,000 mB of TFMG Sulfuric Acid, and fills ten times with 1,000 mB of TFMG
Diesel.

One completed core therefore physically consumes:

- 4,096 `mekanism:hdpe_pellet`
- 512 `mekanism:pellet_plutonium`
- 1,024,000 mB `tfmg:sulfuric_acid`
- 5,120,000 mB `tfmg:diesel`

The HDPE and plutonium inputs stand in for their full Mekanism chemical-gas
chains. Sulfuric Acid remains TFMG-vat-only, and Diesel remains TFMG-canonical.

## Industrial Star

The Industrial Star is the final base-pack artifact. A 5x5 Creative-tier
Mechanical Crafting recipe combines the Black Hole, Industrial Reserve Core,
Ultimate Control Circuits, and all three manufactured Allthemodium alloy ingot
families. It is the intended handoff point for future orbital and space-travel
expansion content.

FTB Quests observes one completed item at each step and emits no reward or
stage. A player can only make the artifacts by satisfying the recipes above.
