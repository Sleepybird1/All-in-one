# Current metal-unit direction — October 10

## Latest correction: iron recovery is not steel

Fireproof Vat consumes1Crushed Raw Iron ->10mB Molten Iron. Magnetite1/rich3 and hematite5/rich9 produce10/30/50/90mBiron respectively. Steel is a separate later recipe. This supersedes the older paragraph below that treated the current vat recovery as steel at9mB each. Fireproof setup is three electrodes; exact type not yet specified for this iron recipe. No gameplay/card edits or exports made.

User allows per-material exceptions to the10mBore-intermediate baseline when balancing needs them. Rich copper10crushed selected; zinc should remain higher (current proposal12rich). Bauxite6/12powder accepted; proposed heated Steel Vat with centrifuge and side electrodes, output identity and attachment support still to verify. Retain finished-ingot dust and gold-flake exceptions.

### Historical discussion below — superseded where it conflicts

Latest user decision supersedes the short-lived144mB proposal and earlier100mB/1000mB design. Retain the observed Create Metallurgy convention:10mB per nugget,90mB per ingot,810mB per finished metal block;9nuggets/ingot,9ingots/block. User requests adjusting melting/processing yields to this baseline instead of implementing the144mB migration. No144mB implementation occurred; do not delete unrelated existing code or historical evidence.

This is desired policy, not proof all live recipes already match. The user observed90mB iron casting and810mB block casting in game. Bundled TFMG casting independently inspected at144mB still requires reconciliation before claiming pack-wide consistency. Existing100/1000overrides require a targeted audit; do not wholesale remove guards or overwrite Personal Recipes. No installation, gameplay export, save edits or bulk fluid rescaling authorized by this note.

Steel planning: TFMG blast furnace and fireproof chemical vat both consume crushed raw iron; crushing determines ore-grade yield. Proposed10crushed from rich hematite would yield9mB each in the vat for90mB total (one ingot). Exact80%early return requires7.2mB each, so a single-input integer-mB recipe could use7mB (70/90=77.78%) or batching if machine/editor support is verified. These quantities and rich-hematite crushing count remain proposals, not applied recipes. Preserve last-read Personal Recipes regular magnetite1/rich3crushed outputs.

Next: review chosen steel output with user; inventory effective casting/melting/conversion overrides for90/810consistency. Runtime acceptance NOT_RUN. Counts unchanged176/261(67.4%),enemy0/24(0%),space24/24(100%).

## Molten-metal canonicalization — latest user direction

Apply the ingot preference order to molten variants: Create first, then Modern Foundry, then the metal source mod. Select one canonical molten identity and its corresponding appearance per metal, using only existing supplied fluids. Do not confuse visual texture unification with recipe/capability interchangeability. Exact Create/addon namespace preference must be reconciled with the existing ingot policy before selecting identities; base Create is not assumed to provide every molten metal. User observed multiple molten iron variants including Metalwork. Audit actual registered fluids, producer/consumer recipes, tags and unit conversions; mere identical names or textures do not establish compatibility. Preserve existing inventories/tanks; no fluid deletion or live conversion authorized. Coordinate with10/90/810unit policy, melting/casting and recovery checks. Implementation remains staged/pending, no installation/export.

## Cinnabar production proposal

User selects cinnabar crushing into Create Cinder Flour instead of the netherrack crushing source, and delegates a proposed amount for review. Current proposal:1cinnabar ->2Cinder Flour. Neither recipe replacement nor deletion has been applied. Check downstream outputs and old cinnabar-to-redstone routes before staged replacement to avoid retaining unintended alternative yields.

## October10 chromium crushing and recovery decision

User selects1Chromite ->1Chromium Dust and1Rich Chromium Ore ->4Chromium Dust. Four dust must yield one90mBingot only through Fireproof Chemical Vat; earlier recovery stays below an ingot. Apply iron early/best efficiency ratio, interpreted as7:9, not a change to iron crushing counts. Derived review proposal:4dust ->70mB early /90mB fireproof (2dust ->35/45 also mathematically exact). Single-dust best value22.5mB requires batching or fractional support; do not silently round. Batch ingredient support and machine assignment NOT_RUN; this is design, no recipe/card writes or export.

Read-only finding: live zz_industrial_material_processing.js includes chromium consolidation4NuclearCraft Chromium Dust ->1NuclearCraft Chromium Ingot in IE Arc Furnace. Effective surviving recipe not verified against later policy scripts. Review/remove incompatible bypasses only with complete replacement; generic dust/ingot grinding and melting cycles also need checking. No claim that only Fireproof currently achieves the target.

Next output choice: dolomite, bertrandite, borax, thorium or cobalt. Overall176/261(67.4%),progression32/79(40.5%).
