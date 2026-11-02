> SUPERSEDED by the later October10 user decision:10mB/nugget,90mB/ingot,810mB/block. Do not implement this144mB migration. See METAL_UNITS_90_DECISION.md. Retained as historical discussion.

# October 10 metal-unit decision — staged migration required

User replaces the prior100mB ingot /1000mB ten-ingot block design with144mB per ingot and9ingots per finished storage block (1296mB). Proposed corresponding conventional nugget value16mB,9nuggets per ingot; user did not separately specify nuggets. This is a design decision and authorization to prepare coordinated staged adjustments, not production installation or gameplay export.

Existing installed overrides must be reconciled: melting/casting, canonical fluid bridges, ingot/nugget/block compression and breakdown, metal tooltips, authored cards and material-return checks. Default recipes are not assumed mutually consistent merely because TFMG uses144mB. Preserve user Personal Recipes edits and existing staged work. Do not run historical migration builders blindly: they capture older baselines and encode100/1000. Existing tanks/saves are untouched.

Steel uses TFMG industrial blasting at the early stage; Immersive Engineering is not a substitute unless needed and separately selected. Both TFMG blast furnace and later fireproof chemical vat consume crushed raw iron, not hematite/magnetite directly. Crushing determines ore-grade yield. Target rich hematite gives approximately0.8ingot via early blasting and1ingot via fireproof vat. Exact crushed count/output quantities remain proposed. Under144mB,10crushed requires14.4mB each for exact1ingot, impossible as a single integer-mB output;9crushed with16mB each is a proposal, not approved. Early13mB each would give117mB/144=81.25%, not exact80%. Alternative batching requires verified machine/editor support. Do not apply either without recipe review.

Current live Personal Recipes last inspected:49cards, regular magnetite1crushed and rich magnetite3. No dedicated steel production card; mechanism byproduct is not starter steel production. No live recipe changes made.

Next: read-only inventory of active unit overrides and candidate scope, then staged coherent migration and conservation tests; installation remains separate. Runtime validation NOT_RUN. Overall176/261(67.4%),enemy0/24(0%),space24/24(100%).
