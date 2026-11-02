# Early manufacturing progression

## Implemented correction

The opening Create factory now follows physical manufacturing capability rather than
copying every installed crafting recipe into KJSGen:

`Andesite drive -> Mechanical Press -> sheet metal and fluids -> Mechanical Pump -> Steam Engine -> heated Brass -> Deployer and Mechanical Crafters -> precision and rail production`

Five recipes are explicitly owned by the source seed:

| Stage | Managed recipe | Output | Exact installed recipe retired |
|---|---|---|---|
| Sheet-metal workshop | `industrial_colonies:mechanical/mechanical_press` | Mechanical Press | `create:crafting/kinetics/mechanical_press` |
| Fluid workshop | `industrial_colonies:mechanical/mechanical_pump` | Mechanical Pump | `create:crafting/kinetics/mechanical_pump` |
| Steam power | `industrial_colonies:steam/steam_engine` | Steam Engine | `create:crafting/kinetics/steam_engine` |
| Brass automation | `industrial_colonies:brass/deployer` | native Deployer | `create:crafting/kinetics/deployer` |
| Brass automation | `industrial_colonies:brass/mechanical_crafter` | 3 Mechanical Crafters | `create:crafting/kinetics/mechanical_crafter` |

The Press contains no sheet input. The Pump consumes Press-made copper sheet and fluid
infrastructure. The Steam Engine consumes that Pump. The Deployer and Mechanical
Crafters require heated-Brass-era parts but deliberately do not require a Precision
Mechanism, avoiding a machine-capability cycle.

## Exact bypass retirement

Only the four Create Diesel Generators hand-hammer sheet recipes are retired:

- `createdieselgenerators:hammering/iron_sheet`
- `createdieselgenerators:hammering/copper_sheet`
- `createdieselgenerators:hammering/gold_sheet`
- `createdieselgenerators:hammering/brass_sheet`

The Hammer item, unrelated hammering recipes, Create pressing, and Create Metallurgy
casting routes remain available.

## Stock factory routes preserved

Seventeen foundational outputs are now excluded from generic auto ownership. This
keeps the hand bootstrap and the later cutting/deploying throughput routes together
for Shafts and Cogwheels, and leaves Andesite/Brass casing application, heated Brass,
Precision Mechanisms, Tracks, and Railway Casings in their native processing systems.

The seed also carries a 24-ID `preserve_recipe_ids` contract. The manifest assembler
filters those IDs from automatically discovered removals and rejects any explicit or
additional removal that conflicts with the preserve list. In particular this protects:

- Shaft cutting and Cogwheel deploying;
- Schedule clearing/reuse;
- Packager, Fluid Tank, Item Vault, and Track Observer conversions;
- heated Brass and casing routes;
- Precision Mechanism, Track, steel Track, and Railway Casing processing.

Both Daylight Detector recipes remain stock because the output is unmanaged.

## Phase correction

The Advanced Redstone, Advanced Mechanical Technology, and Early Crushing nodes now
map to `Steam & Brass`. This reclassifies all eight audited Brass-capability outputs
without changing Draw.io topology or MineColonies/quest content.

The existing Copper Press, Copper Deployer, Brass Press, and Brass Deployer recipes
are byte-for-field guarded by the focused validator and were not redesigned.

## Verification boundary

Run:

```text
python tools/test_early_manufacturing_progression.py
python tools/validate_early_manufacturing_progression.py --manifest <isolated-manifest>
python tools/validate_managed_recipe_overhaul.py --manifest <isolated-manifest> --output <isolated-kjsgen>
python tools/validate_physical_progression.py --manifest <isolated-manifest> --output <isolated-kjsgen> --report <isolated-report>
```

This correction changes source authority only. Shared generated artifacts and the live
pack must be updated later by the owning integration task.

The isolated final build contained 323 managed recipes (198 automatically derived),
391 compiled KJSGen cards, and 707 exact removals. Fifteen focused mutation tests and
two manifest-builder tests passed. The managed DAG validator completed with zero
warnings; physical progression, casing-tier progression, bypass retirement, the prior
Power Backbone batch, and the petroleum/engine slice also passed against the isolated
manifest.
