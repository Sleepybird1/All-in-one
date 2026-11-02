param([string]$ProjectRoot = (Split-Path $PSScriptRoot -Parent))
$ErrorActionPreference = 'Stop'
$dataRoot = Join-Path $ProjectRoot 'src/main/resources/data/industrial_colonies'
$oilRules = Get-Content -Raw -LiteralPath (Join-Path $dataRoot 'geology/oil.json') | ConvertFrom-Json
$placed = Get-Content -Raw -LiteralPath (Join-Path $dataRoot 'worldgen/placed_feature/regional_oil_field.json') | ConvertFrom-Json
$configured = Get-Content -Raw -LiteralPath (Join-Path $dataRoot 'worldgen/configured_feature/regional_oil_reservoir.json') | ConvertFrom-Json
$added = Get-Content -Raw -LiteralPath (Join-Path $dataRoot 'neoforge/biome_modifier/add_regional_oil_fields.json') | ConvertFrom-Json
$removed = Get-Content -Raw -LiteralPath (Join-Path $dataRoot 'neoforge/biome_modifier/remove_tfmg_global_oil_deposits.json') | ConvertFrom-Json
function Require([bool]$Condition, [string]$Message) { if (!$Condition) { throw $Message } }
Require ($oilRules.reservoir_y -eq -64) 'TFMG scanner Y=-64 contract changed'
foreach ($family in @('mountain_highland', 'volcanic_ashen', 'cold_high_altitude')) {
    Require ($oilRules.hard_biome_exclusions -contains $family) "Missing hard oil veto: $family"
    Require ($oilRules.biome_weights.$family -eq 0) "Prohibited oil biome has a nonzero weight: $family"
}
foreach ($family in @('desert_basin', 'arid_badlands', 'coastal_oceanic')) {
    Require ($oilRules.biome_weights.$family -eq 2.5) "Strong basin weight mismatch: $family"
}
foreach ($family in @('sedimentary_plains', 'ordinary_plains')) {
    Require ($oilRules.biome_weights.$family -eq 1.25) "Secondary basin weight mismatch: $family"
}
Require ($oilRules.biome_weights.ordinary_forest -eq 0.5 -and $oilRules.biome_weights.wetland -eq 0.5) 'Lowland weights mismatch'
Require ($oilRules.unclassified_weight -eq 0) 'Unknown biomes should fail closed'
Require ($oilRules.regional_fields.center_margin_blocks -gt ($oilRules.regional_fields.radius_max_blocks + 16)) 'Regional field may escape own cell'
Require ($oilRules.regional_fields.native_wells_max -le 32) 'Unbounded per-field native calls'
Require ($placed.feature -eq 'industrial_colonies:regional_oil_reservoir') 'Wrong regional configured feature'
Require ($configured.type -eq 'industrial_colonies:regional_oil_reservoir') 'Wrong custom oil feature type'
Require ($placed.placement.Count -eq 0) 'Custom oil must use only its central rules, without external Create config filters or extra rolls'
Require ($added.biomes -eq '#minecraft:is_overworld') 'Offshore/custom biomes excluded before classification'
Require ($added.features -eq 'industrial_colonies:regional_oil_field') 'Wrong added oil feature'
Require ($removed.features -eq 'tfmg:oil_deposit' -and $removed.biomes -eq '#minecraft:is_overworld') 'Default TFMG generation bypass remains'
$javaRoot = Join-Path $ProjectRoot 'src/main/java/dev/godpc/industrialcolonies'
$feature = Get-Content -Raw -LiteralPath (Join-Path $javaRoot 'geology/oil/OilReservoirFeature.java')
Require ($feature.Contains('NATIVE_DEPOSIT.placeDeposit(')) 'Native TFMG well builder is not retained'
Require (!$feature.Contains('NATIVE_DEPOSIT.place(')) 'Unsafe native random-walk field builder is used'
Require (!$feature.Contains('getChunk(')) 'Oil generation requests neighboring chunks'
Require ($feature.Contains('maximumRelief()') -and $feature.Contains('maximumSurfaceY()')) 'Terrain hard exclusions missing'
$mixin = Get-Content -Raw -LiteralPath (Join-Path $javaRoot 'mixin/TFMGPumpjackFiniteReservoirMixin.java')
Require ($mixin.Contains('reservoir.oilReserves = Math.max(0, reservoir.oilReserves - consumed)')) 'Finite TFMG extraction no longer present'
'PASS: central oil configuration, exact biome weights, hard vetoes, bounded regional geometry, native TFMG compatibility, and default-feature suppression.'
