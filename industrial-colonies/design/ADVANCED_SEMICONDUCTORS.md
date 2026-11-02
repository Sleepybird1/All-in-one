# Starter and high-density semiconductors

The user accepted the existing recipe as the starter and requested a more expensive pink generation representing finer features on the same wafer area. They also requested all recipes in the KubeJS Gen UI and a fix for fluids missing from ingredient slots.

TFMG's pink texture belongs to `tfmg:n_semiconductor`; its green texture belongs to `tfmg:p_semiconductor`. Display names now identify these as High-Density Semiconductor and Starter Semiconductor. N/P are retained registry IDs for compatibility, not a statement that electrical doping polarity determines technology generation.

## Manufacturing

The green recipe remains unchanged, including its two-part yield and Copper machinery. Existing high-purity silicon preparation and initial wafer etching are preserved.

The pink route starts from the same etched wafer and requires:

1. Two finer patterned layers with Brass alignment tooling. Each layer consumes a plastic resist film, a precision wafer mask, 250 mB sulfuric acid and a 250 mB water rinse. Masks are manufactured in Copper machinery from a glass pane, an iron sheet and black dye, yielding four masks.
2. Dopant activation and heat treatment in a superheated, size-3 firebrick-lined chemical vat. One patterned wafer consumes 200 mB phosphoric acid and 250 mB hydrogen in 1,200 ticks, yielding one annealed high-density wafer.
3. Brass dicing and packaging after a 250 mB rinse, consuming one copper contact frame, one fine gold bonding wire and one plastic sheet. Output remains two pink semiconductors per wafer.

Copper cutting and pressing form two contact frames per copper sheet. Brass cutting and forming produce four fine gold bonding wires per gold sheet. Thus a pair of pink semiconductors consumes one-quarter gold sheet and one-half copper sheet for its connections, in addition to masks, films, reagents and heat. These recipes abstract industrial operations for gameplay; they do not model literal photolithography equipment or feature sizes.

The starter transistor recipe now uses two green parts instead of one green and one pink. It still produces four transistors using Copper machines. This breaks the otherwise circular dependency between pink semiconductors and the transistors required for the first Brass Deployer. Later existing recipes that consume pink semiconductors retain that requirement.

## Editor fix

KubeJS Gen's ingredient renderer previously passed fluids through an item-icon helper. The client mixin now draws registered fluid textures with their tint and amount directly, including fluids without bucket items. Fluid tags resolve to a representative tagged fluid; unresolved fluids show a visible question-mark fallback. Existing item and chemical rendering is unchanged, and fluid probability badges are retained.

All five new components are registered items with localized names and existing model references. All seven changed/added recipe cards are merged into the captured live project, preserving existing recipe UUIDs and 682 unrelated cards. The editor's native exporter remains authoritative.

## Sources and acceptance

Authoring: `tools/build_advanced_semiconductors.py`, `progression/advanced-semiconductors/`, and Industrial Colonies 0.5.3. The captured baseline is the live project after the full-bucket correction, not an older managed project.

Native tests check the green/Brass separation, advanced contacts, fine-pattern and annealing requirements, transistor bootstrap, exclusivity and the previous material/ownership/block checks. `tools/check_advanced_semiconductors.py` verifies that exactly seven effective recipes change and all other loaded recipes remain identical. The isolated client fixture calls the actual editor mixin and captures seven fluid slots, including acid/gas ingredients.

Deployment status and backup location are recorded in `progression/advanced-semiconductors/deployment.json`. The scoped installer requires native and client acceptance, verifies live edits and asset/JAR hashes, backs up changed files and refuses to replace the mod while the live game is running. Saves are not edited. Minecraft must be restarted to load the new items and client renderer.

## Installed acceptance

Installed 2026-09-11T17:15:27.381369-04:00 with Industrial Colonies 0.5.3. Native revision r3 passed both required GameTests, including all 296 material recipes (145,310 assertions), 41 ownership checks, the 1,000 mB block closure, advanced semiconductor gates and Venus structure/loot checks. The client slot-rendering test passed and its seven-fluid screenshot was visually inspected. Exactly seven effective recipes changed; 26,444 unrelated recipes were preserved.

Backup: `C:\Users\GodPC\curseforge\minecraft\Instances\All in one\_industrial_colonies_backups\advanced-semiconductors-20260911-171526`. Live saves were not edited.
