# Global Overworld landmark placement

Prepared September 11, 2026. Installation is proven only by an APPLIED receipt in progression/global-landmarks/deployment.json.

The user's latest global-chain request supersedes the earlier independent village, maritime and mansion grids. One structure set selects among 100 weighted, biome-compatible Overworld landmarks. It uses random-spread spacing 384 chunks, separation 256 chunks, and frequency 0.5: candidate origins are at least 4,096 blocks apart and half of candidates are filtered before generation. This exceeds the requested 2,000-block floor and implements the later practical 4,000-block threshold. Distances refer to origins, not the closest edges of large buildings. Failed biome or terrain checks leave additional empty areas.

Villages, dungeons, ruins, boss ships, ordinary wrecks, meteorites and road signs share this placement. Large dungeons have weight 10 (vanilla mansion 20), ordinary sites 150, ships 300. Village weights remain vanilla 1,000, small CTOV 20, other settlements 1, conditional on eligible biomes. Native biome restrictions remain; massive desert structures still use desert habitats. The global sparsity is stricter than mansion spacing. Native weighted fallback can try another compatible entry when a chosen structure fails; only one can generate per site.

56 former independent sets are disabled, while mixed sets retain only separately owned entries. CTOV's dynamic injections are disabled to prevent bypasses. Overworld Modern Foundry clay/slime/sky islands are disabled. The existing Ad Astra oil-well removal and Venus-only Dragon Tower are preserved.

Mineshafts retain the previously requested rate. Strongholds, buried treasure, fossils and separately configured off-world structures retain their own placement. Intentional underwater structures retain their habitat; land structures receive the dry/flat full-footprint guard. Feature-based decorations are outside this structure-set policy.

Native acceptance checks compare all loaded weights and placement fields, reject independent active sets containing a pooled landmark, check island suppression, sample 289 candidate origins for each of three seeds, and preserve village, terrain, Glacio, Venus and recipe regression coverage. Source: tools/build_global_landmarks.py.

Existing generated chunks and saved structures are unchanged. A restart and newly generated terrain are required.
