MINECRAFT MOD ASSET EXPORT
Scan reached end: True
Top-level archive files selected: 306
Source records including bundled archives: 602
Resources copied successfully: 198734
Extraction warnings: 1

Upload ALL item-assets-NNN.zip files from this output folder.
They are independent standard ZIP files, not multipart pieces requiring reassembly.
SOURCES.csv maps sources/mNNNN/ to original archive filenames and candidate status.
WARNINGS.txt records gaps; do not treat partial scans as complete coverage.

Included: PNG textures, animation metadata, models, blockstates, English names,
and mod metadata. Some non-item textures are included to preserve custom paths.
Excluded: Java classes, sounds, recipes, saves, logs, accounts, and mod executables.
Bundled JARs were read but not copied whole or executed.

LIMITATIONS:
- These are source assets, not a complete rendered inventory-icon export.
- Model paths help identify item candidates, but are not a runtime item registry.
- 3D models, custom renderers, tinting, animation and item states need further work.
- Filename status does not prove whether the loader enabled a mod.
- Mod sources remain separate; no guessed resource precedence or old/new merging.
- Active resource packs, kubejs/assets and vanilla client assets are NOT scanned.
- Only archive files directly in the selected mods folder were scanned.
- Safety limits may omit oversized assets/bundles; consult WARNINGS.txt.
- Asset rights remain with their creators. This export does not authorize publication.