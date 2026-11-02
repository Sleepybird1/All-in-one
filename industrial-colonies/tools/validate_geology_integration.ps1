param(
    [string]$ProjectRoot = (Split-Path $PSScriptRoot -Parent),
    [switch]$AllowReferenceTextures
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$resources = Join-Path $ProjectRoot 'src/main/resources'
$java = Join-Path $ProjectRoot 'src/main/java/dev/godpc/industrialcolonies'
$script:checks = 0
$nonNativeTextures = [System.Collections.Generic.List[string]]::new()
function Assert-Geology([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
    $script:checks++
}
function Read-Text([string]$Path) { Get-Content -LiteralPath $Path -Raw -Encoding UTF8 }
function Read-Json([string]$Path) { (Read-Text $Path) | ConvertFrom-Json }
function Require-File([string]$Relative) {
    $path = Join-Path $resources $Relative
    Assert-Geology (Test-Path -LiteralPath $path -PathType Leaf) "Missing resource: $Relative"
    return $path
}
function Get-Property($Object, [string]$Name) {
    $property = $Object.PSObject.Properties[$Name]
    if ($null -ne $property) { return $property.Value }
    return $null
}

# Read-only source/data checks. This does not launch a game, modify configs, build,
# or prove bytecode injections/data codecs succeed at runtime.
$blocksSource = Read-Text (Join-Path $java 'geology/GeologyBlocks.java')
$idsSection = [regex]::Match($blocksSource, '(?s)APPROVED_IDS\s*=\s*List\.of\((.*?)\);')
Assert-Geology $idsSection.Success 'Could not read the explicit geological block roster.'
$ids = @([regex]::Matches($idsSection.Groups[1].Value, '"([a-z0-9_]+)"') | ForEach-Object { $_.Groups[1].Value })
Assert-Geology ($ids.Count -eq 40) "Expected the 40 approved cubes; found $($ids.Count)."
Assert-Geology (@($ids | Sort-Object -Unique).Count -eq $ids.Count) 'Duplicate block IDs in approved roster.'
$knownBlocks = @{}
foreach ($id in $ids) { $knownBlocks["industrial_colonies:$id"] = $true }
$knownBlocks['industrial_colonies:gold_flakes'] = $true
$knownBlocks['minecraft:coal_ore'] = $true
$knownBlocks['minecraft:gold_ore'] = $true
$language = Read-Json (Require-File 'assets/industrial_colonies/lang/en_us.json')
foreach ($id in ($ids + @('gold_flakes'))) {
    $blockstate = (Read-Text (Require-File "assets/industrial_colonies/blockstates/$id.json")) | ConvertFrom-Json -AsHashtable
    $variant = $blockstate['variants']['']
    Assert-Geology ($variant['model'] -eq "industrial_colonies:block/$id") "Wrong blockstate model: $id"
    $model = Read-Json (Require-File "assets/industrial_colonies/models/block/$id.json")
    $itemModel = Read-Json (Require-File "assets/industrial_colonies/models/item/$id.json")
    Assert-Geology ($itemModel.parent -eq "industrial_colonies:block/$id") "Wrong block-item model: $id"
    $loot = Read-Json (Require-File "data/industrial_colonies/loot_table/blocks/$id.json")
    $expectedDrop = if ($id -eq 'gold_flakes') { 'industrial_colonies:gold_flake' } elseif ($id -eq 'diamond_ore') { 'minecraft:diamond' } else { "industrial_colonies:$id" }
    Assert-Geology ($loot.pools[0].entries[0].name -eq $expectedDrop) "Wrong geological drop: $id"
    Assert-Geology ($null -ne $language.PSObject.Properties["block.industrial_colonies.$id"]) "Missing block display name: $id"
    if ($id -ne 'gold_flakes') {
        Assert-Geology ($model.parent -in @('minecraft:block/cube_all','minecraft:block/cube')) "Expected unchanged cube geometry: $id"
        $textureRefs = @($model.textures.PSObject.Properties.Value | Sort-Object -Unique)
        foreach ($ref in $textureRefs) {
            Assert-Geology ($ref -match "^industrial_colonies:block/geology/$([regex]::Escape($id))(_top|_side|_bottom)?$") "Wrong cube texture reference: $id -> $ref"
            $texture = Require-File ("assets/industrial_colonies/textures/" + $ref.Split(':')[1] + '.png')
            $bytes = [System.IO.File]::ReadAllBytes($texture)
            Assert-Geology ($bytes.Length -gt 24 -and $bytes[0] -eq 137 -and $bytes[1] -eq 80 -and $bytes[2] -eq 78 -and $bytes[3] -eq 71) "Not a PNG: $ref"
            # PNG's IHDR width/height are unsigned big-endian, bytes 16..23.
            $width = ($bytes[16] * 16777216) + ($bytes[17] * 65536) + ($bytes[18] * 256) + $bytes[19]
            $height = ($bytes[20] * 16777216) + ($bytes[21] * 65536) + ($bytes[22] * 256) + $bytes[23]
            if ($width -ne 16 -or $height -ne 16) { $nonNativeTextures.Add("$ref ($width x $height)") }
        }
    }
}
$null = Read-Json (Require-File 'assets/industrial_colonies/models/item/gold_flake.json')
Assert-Geology ($blocksSource.Contains('ITEMS.registerSimpleItem("gold_flake")')) 'Gold flake item is not registered.'

$settings = Read-Json (Require-File 'data/industrial_colonies/geology/settings.json')
$biomes = Read-Json (Require-File 'data/industrial_colonies/geology/biome_families.json')
$deposits = (Read-Json (Require-File 'data/industrial_colonies/geology/deposit_families.json')).deposits
Assert-Geology ($settings.economy.ingotMb -eq 1000 -and $settings.economy.storageBlockMb -eq 9000) 'Universal molten-volume metadata changed.'
$requiredFamilies = @('mountain_highland','arid_badlands','tropical_humid','sedimentary_plains','coastal_oceanic','volcanic_ashen','wetland','cold_high_altitude','ordinary_forest','ordinary_plains','desert_basin')
foreach ($family in $requiredFamilies) {
    Assert-Geology ($null -ne $biomes.PSObject.Properties[$family]) "Missing biome family: $family"
    $assigned = @($biomes.PSObject.Properties[$family].Value)
    Assert-Geology (@($assigned | Sort-Object -Unique).Count -eq $assigned.Count) "Duplicate biome in family: $family"
}
Assert-Geology (@($deposits.id | Sort-Object -Unique).Count -eq @($deposits).Count) 'Duplicate deposit IDs.'
foreach ($deposit in $deposits) {
    $refs = @($deposit.hostRock) + @($deposit.richOres | ForEach-Object { $_.block }) + @($deposit.associated | ForEach-Object { $_.block })
    foreach ($ref in $refs) { Assert-Geology ($knownBlocks.ContainsKey($ref)) "Unregistered or unapproved generated block $ref in $($deposit.id)" }
    foreach ($mapping in $deposit.biomeWeights.PSObject.Properties) {
        Assert-Geology ($requiredFamilies -contains $mapping.Name) "Unknown biome family $($mapping.Name) in $($deposit.id)"
    }
    Assert-Geology (@($deposit.depthWeights).Count -eq 3) "Wrong depth weight count in $($deposit.id)"
    Assert-Geology ($deposit.sameFamilyMinSpacing -ge $settings.globalMinSpacing) "Family spacing smaller than global: $($deposit.id)"
}
foreach ($resource in $settings.trace.resources) { Assert-Geology ($knownBlocks.ContainsKey($resource.block)) "Unknown trace block $($resource.block)" }
Assert-Geology ($knownBlocks.ContainsKey($settings.micro.diamond.block)) 'Unknown diamond micro block.'
Assert-Geology (@($deposits | Where-Object { $_.id -in @('cobalt','osmium','iridium','platinum') }).Count -eq 0) 'Associated ore became a forbidden independent major deposit.'
$nickel = @($deposits | Where-Object id -eq 'pentlandite')[0]
Assert-Geology (@($nickel.associated | Where-Object block -eq 'industrial_colonies:cobalt_ore').Count -eq 1) 'Cobalt association missing from Pentlandite.'
$graphite = @($deposits | Where-Object id -eq 'graphite_rock')[0]
Assert-Geology (@($graphite.richOres).Count -eq 0) 'A forbidden rich Graphite block was introduced.'
Assert-Geology (@($graphite.associated | Where-Object block -eq 'industrial_colonies:diamond_ore').Count -eq 1) 'Graphite diamond association missing.'
$uranium = @($deposits | Where-Object id -eq 'uranium')[0]
$thoriumRule = @($uranium.associated | Where-Object block -eq 'industrial_colonies:thorium_ore')[0]
Assert-Geology (@($thoriumRule.chanceByQuality | Where-Object { $_ -ne 1 }).Count -eq 0) 'Major Uranium no longer guarantees a Thorium association roll.'

$configured = Read-Json (Require-File 'data/industrial_colonies/worldgen/configured_feature/regional_geology.json')
Assert-Geology ($configured.type -eq 'industrial_colonies:regional_geology') 'Configured geology feature has the wrong type.'
$placed = Read-Json (Require-File 'data/industrial_colonies/worldgen/placed_feature/regional_geology.json')
Assert-Geology ($placed.feature -eq 'industrial_colonies:regional_geology' -and @($placed.placement).Count -eq 0) 'Geology must run once per owning chunk without extra placement multiplicity.'
$bootstrap = Read-Text (Join-Path $java 'geology/GeologyBootstrap.java')
Assert-Geology ($bootstrap -match 'FEATURES\.register\("regional_geology",\s*GeologyFeature::new\)') 'Feature registry entry missing.'
Assert-Geology ($bootstrap.Contains('GeologyBlocks.register(bus)') -and $bootstrap.Contains('FEATURES.register(bus)')) 'Geology deferred registers are not connected to the mod bus.'
Assert-Geology ((Read-Text (Join-Path $java 'IndustrialColonies.java')).Contains('GeologyBootstrap.register(modEventBus)')) 'Geology bootstrap is not called by the mod.'
$feature = Read-Text (Join-Path $java 'geology/GeologyFeature.java')
Assert-Geology ($feature.Contains('Level.OVERWORLD') -and $feature.Contains('!enabled()')) 'Geology feature is missing actual-dimension/master-enable guards.'
# The controlled ceiling regression exercises the overload; these source contracts also
# ensure the actual independent-diamond branch supplies its configured ceiling.
$diamondCall = [regex]::Match($feature, '(?s)if\s*\(tryDiamond\b.*?return\s+tiny\((?<arguments>.*?)\)>0;')
Assert-Geology ($diamondCall.Success -and $diamondCall.Groups['arguments'].Value -match 'seed\s*\+\s*10\s*,\s*integer\(diamond,\s*"maxY",\s*-20\)\s*$') 'Independent diamond placement must pass configured maxY to the bounded tiny overload.'
$boundedTiny = [regex]::Match($feature, '(?s)private\s+static\s+int\s+tiny\([^{}]*int\s+maximumY\)\s*\{(?<body>.*?)\n\s*\}')
Assert-Geology ($boundedTiny.Success -and $boundedTiny.Groups['body'].Value -match 'candidates\.removeIf\(p\s*->[^;]*p\.getY\(\)\s*>\s*maximumY') 'Bounded tiny placement must exclude every candidate above maximumY before clustering.'
$additionFiles = @(Get-ChildItem -LiteralPath (Join-Path $resources 'data/industrial_colonies/neoforge/biome_modifier') -Filter '*.json' -File)
$geologyAdditions = @($additionFiles | Where-Object { (Read-Text $_.FullName) -match '"features"\s*:\s*"industrial_colonies:regional_geology"' })
Assert-Geology ($geologyAdditions.Count -eq 1) 'Geology placement must have exactly one biome modifier registration.'
$addition = Read-Json $geologyAdditions[0].FullName
Assert-Geology ($addition.biomes -eq '#minecraft:is_overworld' -and $addition.step -eq 'underground_ores') 'Geology added to wrong biomes or decoration stage.'

$script:forbidden = @{}
$script:seenTags = @{}
function Expand-FeatureTag([string]$Id) {
    Assert-Geology (-not $script:seenTags.ContainsKey($Id)) "Repeated/cyclic suppression tag: $Id"
    $script:seenTags[$Id] = $true
    $parts = $Id -split ':', 2
    $tag = Read-Json (Require-File "data/$($parts[0])/tags/worldgen/placed_feature/$($parts[1]).json")
    foreach ($entry in $tag.values) {
        $value = if ($entry -is [string]) { $entry } else { $entry.id }
        if ($value.StartsWith('#')) { Expand-FeatureTag $value.Substring(1); continue }
        Assert-Geology (-not $script:forbidden.ContainsKey($value)) "Duplicate forbidden feature: $value"
        $script:forbidden[$value] = $true
        if (-not $value.StartsWith('minecraft:')) {
            Assert-Geology ($entry -isnot [string] -and (Get-Property $entry 'required') -eq $false) "Optional mod feature is a hard-required tag entry: $value"
        }
    }
}
Expand-FeatureTag 'industrial_colonies:geology/default_ore_features'
Assert-Geology ($script:forbidden.Count -eq 73) "Audited suppression manifest changed from 73 IDs: $($script:forbidden.Count). Re-audit installed generators."
foreach ($id in @('ore_coal_windswept','ore_diamond_volcanic','ore_gold_volcanic','ore_iron_windswept','ore_redstone_windswept')) {
    Assert-Geology ($script:forbidden.ContainsKey("wythers:ores/$id")) "WWOO economic source escaped suppression: $id"
}
Assert-Geology (-not $script:forbidden.ContainsKey('wythers:ores/ore_lava_volcanic')) 'WWOO non-resource volcanic lava must remain unchanged.'
Assert-Geology (@($biomes.ordinary_forest) -contains 'minecraft:pale_garden') 'Vanilla Backport/WWOO Pale Garden must inherit ordinary-forest geology.'
foreach ($id in $script:forbidden.Keys) {
    Assert-Geology ($id -notmatch '(emerald|lapis|fluorite|quartz|salt|nether|end_|mars|moon|mercury|venus)') "Protected/default or non-Overworld source accidentally suppressed: $id"
}
$remove = Read-Json (Require-File 'data/industrial_colonies/neoforge/biome_modifier/geology_remove_default_ores.json')
Assert-Geology ($remove.type -eq 'neoforge:remove_features' -and $remove.biomes -eq '#minecraft:is_overworld') 'Suppression modifier is not an Overworld-only feature removal.'
Assert-Geology ($remove.features -eq '#industrial_colonies:geology/default_ore_features') 'Removal and runtime guard manifests diverged.'
Assert-Geology (@($remove.steps).Count -eq 11 -and @($remove.steps | Sort-Object -Unique).Count -eq 11) 'Suppression must inspect all 11 decoration stages.'
$guard = Read-Text (Join-Path $java 'mixin/GeologyPlacedFeatureGuardMixin.java')
Assert-Geology ($guard.Contains('"industrial_colonies","geology/default_ore_features"')) 'Placed-feature Java guard points at a different suppression tag.'

$mixins = Read-Json (Require-File 'industrial_colonies.mixins.json')
$requiredMixins = @('GeologyStructureManagerAccessor','GeologyNoiseVeinsMixin','GeologyPlacedFeatureGuardMixin','GeologyFossilOverlayMixin','GeologyQuarkFairyRingMixin','GeologyCarversMixin')
foreach ($mixin in $requiredMixins) {
    Assert-Geology (@($mixins.mixins | Where-Object { $_ -eq $mixin }).Count -eq 1) "Required mixin missing or registered twice: $mixin"
    $source = Join-Path $java "mixin/$mixin.java"
    Assert-Geology (Test-Path -LiteralPath $source -PathType Leaf) "Registered mixin source missing: $mixin"
    if ($mixin -notin @('GeologyStructureManagerAccessor','GeologyCarversMixin')) {
        $sourceText = Read-Text $source
        Assert-Geology ($sourceText.Contains('GeologyConfig.suppressDefaultOres()') -and $sourceText.Contains('Level.OVERWORLD')) "Mixin suppression lacks config/actual Overworld guard: $mixin"
    }
}
$carver = Read-Text (Join-Path $java 'mixin/GeologyCarversMixin.java')
Assert-Geology ($carver.Contains('applyCarvers') -and $carver.Contains('TAIL') -and $carver.Contains('GenerationStep.Carving.AIR')) 'Geology must use the post-AIR-carver chunk dependency barrier.'
Assert-Geology ($carver.Contains('GeologyConfig.enabled()') -and $carver.Contains('Level.OVERWORLD')) 'Post-carver geology needs explicit master-enable and dimension guards.'
Assert-Geology ($feature.Contains('generateDeposits') -and $carver.Contains('GeologyFeature.generateDeposits')) 'Post-carver hook must invoke owner-chunk mineral placement.'
$quark = Read-Text (Join-Path $java 'mixin/GeologyQuarkFairyRingMixin.java')
Assert-Geology ($quark.Contains('@Pseudo') -and $quark.Contains('Blocks.DIAMOND_ORE') -and $quark.Contains('Blocks.DEEPSLATE_DIAMOND_ORE')) 'Quark optional guard must target only diamond blocks.'
Assert-Geology (-not $quark.Contains('state.is(Blocks.EMERALD_ORE)')) 'Quark emerald prize must remain untouched.'
$fossil = Read-Text (Join-Path $java 'mixin/GeologyFossilOverlayMixin.java')
Assert-Geology ($fossil -match 'ordinal\s*=\s*1' -and $fossil -match 'require\s*=\s*1') 'Fossil hook must skip exactly the second overlay template.'
$ruRule = Read-Text (Require-File 'data/regions_unexplored/lithostitched/surface_rule/overworld/caves/redstone_caves.json')
Assert-Geology ($ruRule -notmatch 'raw_redstone_block|redstone_ore') 'RU surface override still contains an economic Redstone block.'
$null = $ruRule | ConvertFrom-Json

if ($nonNativeTextures.Count -gt 0) {
    Write-Warning ('Non-native reference texture dimensions: ' + ($nonNativeTextures -join ', '))
    Assert-Geology $AllowReferenceTextures.IsPresent 'Expected native16 textures. Re-run -AllowReferenceTextures only if exact high-resolution reference preservation is an intentional documented exception.'
}
Write-Output "PASS: $script:checks static geology integration assertions; 40 cubes + placer, $(@($deposits).Count) deposits, 73 suppressed placed features, six registered geology mixins/accessors; $($nonNativeTextures.Count) non-native texture exceptions."
Write-Output 'Scope: source/resource consistency only. Run installed-jar audit and isolated GameTest/client smoke tests separately; no game or live config was changed.'
