param([string]$ProjectRoot = (Split-Path $PSScriptRoot -Parent))
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$entries = [ordered]@{}
$backupEntries = [ordered]@{}
$pending = [System.Collections.Generic.List[string]]::new()

# Read-only manifest input collector. Explicit task-owned families prevent old
# progression changes, build caches, or copied third-party mods entering the list.
function Relative-Path([string]$Path) {
    return [IO.Path]::GetRelativePath($ProjectRoot, [IO.Path]::GetFullPath($Path)).Replace('\','/')
}
function File-Record([string]$Path) {
    $item = Get-Item -LiteralPath $Path
    return [ordered]@{
        path = Relative-Path $item.FullName
        bytes = $item.Length
        sha256 = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash
    }
}
function Add-Authored([string]$Path, [string]$Category, [string]$Change = 'created', [string]$Evidence = 'Explicit task-owned new file family; confirmed author inventory.', [string]$Backup = '', [switch]$Optional) {
    $full = if ([IO.Path]::IsPathFullyQualified($Path)) { $Path } else { Join-Path $ProjectRoot $Path }
    if (-not (Test-Path -LiteralPath $full -PathType Leaf)) {
        if ($Optional) { $pending.Add($Path); return }
        throw "Expected worldgen-authored file missing: $Path"
    }
    $record = File-Record $full
    if ($entries.Contains($record.path)) { return }
    $record.category = $Category
    $record.change = $Change
    $record.evidence = $Evidence
    if ($Backup) {
        $backupFull = if ([IO.Path]::IsPathFullyQualified($Backup)) { $Backup } else { Join-Path $ProjectRoot $Backup }
        if (-not (Test-Path -LiteralPath $backupFull -PathType Leaf)) { throw "Expected original backup missing: $Backup" }
        $b = File-Record $backupFull
        $record.originalBackup = $b.path
        $record.originalSha256 = $b.sha256
        $backupEntries[$b.path] = $b
    }
    $entries[$record.path] = $record
}

$assetManifestPath = Join-Path $ProjectRoot 'WORLDGEN_GEOLOGY_ASSETS.json'
$assets = Get-Content -LiteralPath $assetManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
foreach ($asset in $assets.changedFiles) {
    $change = if ($asset.backup) { 'modified' } else { 'created' }
    $backup = if ($asset.backup) { [string]$asset.backup } else { '' }
    Add-Authored "src/main/resources/$($asset.file)" 'approved_asset_export' $change 'WORLDGEN_GEOLOGY_ASSETS.json changedFiles; backup marks a pre-existing file, null marks a new export.' $backup
}
foreach ($file in Get-ChildItem -LiteralPath (Join-Path $ProjectRoot 'src/main/java/dev/godpc/industrialcolonies/geology') -File -Filter '*.java') {
    Add-Authored $file.FullName 'geology_java'
}
foreach ($file in Get-ChildItem -LiteralPath (Join-Path $ProjectRoot 'src/main/java/dev/godpc/industrialcolonies/geology/oil') -File -Filter '*.java') {
    Add-Authored $file.FullName 'oil_java'
}
foreach ($name in @('GeologyStructureManagerAccessor','GeologyNoiseVeinsMixin','GeologyPlacedFeatureGuardMixin','GeologyFossilOverlayMixin','GeologyQuarkFairyRingMixin','GeologyCarversMixin')) {
    Add-Authored "src/main/java/dev/godpc/industrialcolonies/mixin/$name.java" 'suppression_mixins'
}
Add-Authored 'src/main/java/dev/godpc/industrialcolonies/IndustrialColonies.java' 'existing_integration' 'modified' 'Existing mod entrypoint; original preserved before worldgen integration.' 'backups/geology-foundation-20260908/IndustrialColonies.java'
Add-Authored 'src/main/resources/industrial_colonies.mixins.json' 'existing_integration' 'modified' 'Existing mixin registration list; original preserved before worldgen integration.' 'backups/geology-foundation-20260908/industrial_colonies.mixins.json'
foreach ($file in Get-ChildItem -LiteralPath (Join-Path $ProjectRoot 'src/main/resources/data/industrial_colonies/geology') -File -Filter '*.json') {
    Add-Authored $file.FullName 'central_worldgen_configuration'
}
foreach ($file in Get-ChildItem -LiteralPath (Join-Path $ProjectRoot 'src/main/resources/data/industrial_colonies/tags/worldgen/placed_feature/geology') -File -Filter '*.json') {
    Add-Authored $file.FullName 'suppression_data'
}
foreach ($name in @('geology_remove_default_ores','geology_add_decorative_strata','geology_add_fireclay_strata','add_regional_geology')) {
    Add-Authored "src/main/resources/data/industrial_colonies/neoforge/biome_modifier/$name.json" 'geology_feature_data'
}
foreach ($kind in @('configured_feature','placed_feature')) {
    foreach ($name in @('regional_geology','geology_create_decorative_strata','geology_tfmg_fireclay_strata')) {
        Add-Authored "src/main/resources/data/industrial_colonies/worldgen/$kind/$name.json" 'geology_feature_data'
    }
}
Add-Authored 'src/main/resources/data/regions_unexplored/lithostitched/surface_rule/overworld/caves/redstone_caves.json' 'suppression_data' 'created' 'New pack override of installed RU data; original remains in the unmodified RU JAR.'
Add-Authored 'src/main/resources/data/industrial_colonies/worldgen/configured_feature/regional_oil_reservoir.json' 'oil_feature_data'
foreach ($path in @('src/main/resources/data/industrial_colonies/worldgen/placed_feature/regional_oil_field.json','src/main/resources/data/industrial_colonies/neoforge/biome_modifier/add_regional_oil_fields.json')) {
    Add-Authored $path 'oil_feature_data' 'modified' 'Oil author confirmed replacement of the pre-existing dry-biome regional placement policy; no original backup captured by this task.'
}
Add-Authored 'src/main/resources/data/industrial_colonies/structure/geology_smoke_empty.nbt' 'gametest_template'

foreach ($path in @(
    'scripts/export-approved-geology-assets.ps1',
    'tools/audit_geology_worldgen.py',
    'tools/validate_geology_integration.ps1',
    'tools/get_worldgen_change_inventory.ps1',
    'tools/create_geology_gametest_template.ps1',
    'tools/prepare_geology_gametest.ps1',
    'tools/prepare_offline_epoll_repo.ps1',
    'tools/GeologyPlannerSelfTest.java',
    'tools/test_geology_planner.ps1',
    'tools/test-support/net/neoforged/fml/loading/FMLPaths.java',
    'tools/java/dev/godpc/industrialcolonies/geology/oil/OilFieldPlannerTest.java',
    'tools/validate_oil_worldgen_framework.ps1'
)) { Add-Authored $path 'authored_tools_and_tests' }
Add-Authored '../refresh-worldgen-snapshot.ps1' 'authored_tools_and_tests' 'created' 'Task-authored mechanical inventory refresh helper, outside the project but within the shared workspace.'
foreach ($path in @('tools/prepare_offline_devlaunch_repo.ps1')) {
    if (Test-Path -LiteralPath (Join-Path $ProjectRoot $path) -PathType Leaf) { Add-Authored $path 'authored_tools_and_tests' }
}
foreach ($file in Get-ChildItem -LiteralPath (Join-Path $ProjectRoot 'tools/terrain-smoke') -Recurse -File) {
    Add-Authored $file.FullName 'development_only_terrain_tests'
}
foreach ($family in @('client-smoke','controlled-geology','oil-smoke')) {
    $familyRoot = Join-Path $ProjectRoot "tools/$family"
    if (-not (Test-Path -LiteralPath $familyRoot -PathType Container)) { continue }
    foreach ($file in Get-ChildItem -LiteralPath $familyRoot -Recurse -File) {
        $relative = [IO.Path]::GetRelativePath($familyRoot, $file.FullName).Replace('\','/')
        # Test source/control families only: never collect generated classes,
        # copied dependencies, runtime screenshots, or cache contents as authored.
        if ($relative -match '(^|/)(?:build(?:-[^/]*)?|\.gradle[^/]*|\.?cache[^/]*|__pycache__|compiled|classes|out|bin|node_modules|screenshots|logs)(/|$)') { continue }
        if ($file.Name -notmatch '\.(?:java|json|toml|mcmeta|nbt|ps1|py|gradle|md|properties|template|bat|cmd|sh)$') { continue }
        Add-Authored $file.FullName 'development_only_acceptance_tests'
    }
}
foreach ($path in @('tools/validate_regional_finite_oil_fields.py','tools/test_validate_regional_finite_oil_fields.py')) {
    Add-Authored $path 'authored_tools_and_tests' 'modified' 'Oil author confirmed updating the pre-existing validation/mutation tests to the new regional reservoir policy.'
}
foreach ($path in @('WORLDGEN_BIOME_ASSIGNMENTS.md','WORLDGEN_GEOLOGY_ASSETS.json','WORLDGEN_SUPPRESSION_AUDIT.md','OIL_WORLDGEN_FRAMEWORK.md','WORLDGEN_ISOLATED_RUNTIME_SMOKE.md','WORLDGEN_TERRAIN_ORDER_REGRESSION.md')) {
    Add-Authored $path 'reports_and_manifests'
}
Add-Authored 'REGIONAL_OIL_FIELDS.md' 'reports_and_manifests' 'modified' 'Oil author confirmed updating the existing finite-reservoir document; processing/extraction remains unchanged.'
foreach ($path in @('WORLDGEN_PLANNER_TESTS.md','WORLDGEN_IMPLEMENTATION_REPORT.md','WORLDGEN_FINAL_ACCEPTANCE.md')) {
    Add-Authored $path 'reports_and_manifests' -Optional
}

$isolatedStages = [System.Collections.Generic.List[object]]::new()
$clientStages = [System.Collections.Generic.List[object]]::new()
$isolatedRoot = Join-Path $ProjectRoot 'isolated-runtime'
if (Test-Path -LiteralPath $isolatedRoot -PathType Container) {
    foreach ($directory in Get-ChildItem -LiteralPath $isolatedRoot -Directory -Filter 'geology-gametest-*') {
        $preparation = Join-Path $directory.FullName 'preparation.json'
        if (-not (Test-Path -LiteralPath $preparation -PathType Leaf)) { continue }
        $stage = Get-Content -LiteralPath $preparation -Raw -Encoding UTF8 | ConvertFrom-Json
        $controls = [System.Collections.Generic.List[object]]::new()
        foreach ($name in @('preparation.json','geology-smoke.init.gradle','server.properties','offline-assets.properties','rendering-exclusions.json','gametest-exclusions.json','gametest-dimension-fixture.json','worlds/geology-smoke-world/datapacks/ic-gametest-dimensions/pack.mcmeta','worlds/geology-smoke-world/datapacks/ic-gametest-dimensions/data/minecraft/worldgen/world_preset/flat.json')) {
            $file = Join-Path $directory.FullName $name
            if (Test-Path -LiteralPath $file -PathType Leaf) { $controls.Add((File-Record $file)) }
        }
        foreach ($name in @('terrain-smoke.init.gradle','terrain-worlds/terrain-a/datapacks/ic-normal-terrain-fixture/pack.mcmeta','terrain-worlds/terrain-a/datapacks/ic-normal-terrain-fixture/data/minecraft/worldgen/world_preset/flat.json','terrain-worlds/terrain-b/datapacks/ic-normal-terrain-fixture/pack.mcmeta','terrain-worlds/terrain-b/datapacks/ic-normal-terrain-fixture/data/minecraft/worldgen/world_preset/flat.json')) {
            $file = Join-Path $directory.FullName $name
            if (Test-Path -LiteralPath $file -PathType Leaf) { $controls.Add((File-Record $file)) }
        }
        foreach ($world in @('terrain-a-fixed1','terrain-b-fixed1')) {
            foreach ($suffix in @('pack.mcmeta','data/minecraft/worldgen/world_preset/flat.json')) {
                $file = Join-Path $directory.FullName "terrain-worlds/$world/datapacks/ic-normal-terrain-fixture/$suffix"
                if (Test-Path -LiteralPath $file -PathType Leaf) { $controls.Add((File-Record $file)) }
            }
        }
        # Exact new acceptance-fixture paths only, never a recursive world/save scan.
        foreach ($name in @(
            'controlled-worlds/world-controlled-a1/datapacks/ic_normal_terrain/pack.mcmeta',
            'controlled-worlds/world-controlled-a1/datapacks/ic_normal_terrain/data/minecraft/worldgen/world_preset/flat.json',
            'controlled-worlds/world-controlled-a2/datapacks/ic_normal_terrain/pack.mcmeta',
            'controlled-worlds/world-controlled-a2/datapacks/ic_normal_terrain/data/minecraft/worldgen/world_preset/flat.json',
            'final-acceptance-worlds/final-a1/datapacks/ic_normal_terrain/pack.mcmeta',
            'final-acceptance-worlds/final-a1/datapacks/ic_normal_terrain/data/minecraft/worldgen/world_preset/flat.json',
            'final-acceptance-worlds/final-a2/datapacks/ic_normal_terrain/pack.mcmeta',
            'final-acceptance-worlds/final-a2/datapacks/ic_normal_terrain/data/minecraft/worldgen/world_preset/flat.json'
        )) {
            $file = Join-Path $directory.FullName $name
            if (Test-Path -LiteralPath $file -PathType Leaf) { $controls.Add((File-Record $file)) }
        }
        # Oil's world name is fixed; the operator may name its fixture datapack.
        # Recognize ONLY the two known authored template files, and only when
        # both are exact copies. Never inventory arbitrary datapack/save content.
        $oilDatapacks = Join-Path $directory.FullName 'oil-worlds/oil-native/datapacks'
        if (Test-Path -LiteralPath $oilDatapacks -PathType Container) {
            foreach ($fixture in Get-ChildItem -LiteralPath $oilDatapacks -Directory) {
                $fixtureRecords = [System.Collections.Generic.List[object]]::new()
                foreach ($suffix in @('pack.mcmeta','data/minecraft/worldgen/world_preset/flat.json')) {
                    $source = Join-Path $ProjectRoot "tools/terrain-smoke/world-template/$suffix"
                    $copy = Join-Path $fixture.FullName $suffix
                    if ((Test-Path -LiteralPath $source -PathType Leaf) -and (Test-Path -LiteralPath $copy -PathType Leaf)) {
                        $record = File-Record $copy
                        if ($record.sha256 -eq (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash) { $fixtureRecords.Add($record) }
                    }
                }
                if ($fixtureRecords.Count -eq 2) { foreach ($record in $fixtureRecords) { $controls.Add($record) } }
            }
        }
        $stagedCandidate = Join-Path $directory.FullName ('mods/' + [IO.Path]::GetFileName($stage.candidate))
        $currentCandidate = if (Test-Path -LiteralPath $stagedCandidate -PathType Leaf) { File-Record $stagedCandidate } else { $null }
        $activeJars = @(Get-ChildItem -LiteralPath (Join-Path $directory.FullName 'mods') -File -Filter '*.jar')
        $heldDirectory = Join-Path $directory.FullName 'excluded-rendering-mods'
        $heldJars = @(if (Test-Path -LiteralPath $heldDirectory -PathType Container) { Get-ChildItem -LiteralPath $heldDirectory -File -Filter '*.jar' })
        $heldGameTestDirectory = Join-Path $directory.FullName 'excluded-gametest-incompatible-mods'
        $heldGameTestJars = @(if (Test-Path -LiteralPath $heldGameTestDirectory -PathType Container) { Get-ChildItem -LiteralPath $heldGameTestDirectory -File -Filter '*.jar' })
        $offlineRepository = Join-Path $directory.FullName 'offline-maven'
        $repositorySummary = $null
        if (Test-Path -LiteralPath $offlineRepository -PathType Container) {
            $repositoryFiles = @(Get-ChildItem -LiteralPath $offlineRepository -Recurse -File)
            $repositorySummary = [ordered]@{
                path = Relative-Path $offlineRepository
                fileCount = $repositoryFiles.Count
                bytes = ($repositoryFiles | Measure-Object -Property Length -Sum).Sum
                modules = @('io.netty:netty-transport-native-epoll:4.1.97.Final','net.neoforged:DevLaunch:1.0.2')
                classification = 'Unchanged third-party dependencies, Maven metadata and checksum sidecars; not authored project source.'
                provenanceReport = 'WORLDGEN_ISOLATED_RUNTIME_SMOKE.md'
            }
        }
        $isolatedStages.Add([ordered]@{
            path = Relative-Path $directory.FullName
            purpose = 'Isolated development smoke-test copies, not live deployment; copied files are not newly authored changes.'
            preparationMode = $stage.mode
            installedJarCount = $stage.installedJarCount
            copiedInstalledJars = $stage.copiedInstalledJars
            stagedJarCount = $stage.stagedJarCount
            stagedModBytes = $stage.modBytes
            initialCountMeaning = 'stagedJarCount and stagedModBytes describe the original preparation snapshot, before approved disposable-stage rendering exclusions.'
            currentActiveJarCount = $activeJars.Count
            currentActiveModBytes = ($activeJars | Measure-Object -Property Length -Sum).Sum
            heldRenderingJarCount = $heldJars.Count
            heldRenderingJarBytes = ($heldJars | Measure-Object -Property Length -Sum).Sum
            heldRenderingJarScope = 'Unchanged third-party JARs held outside the active disposable-stage mods directory under rendering-exclusions.json; not deleted and no live pack changes.'
            heldGameTestJarCount = $heldGameTestJars.Count
            heldGameTestJarBytes = ($heldGameTestJars | Measure-Object -Property Length -Sum).Sum
            heldGameTestJarScope = 'Separately approved dual-side Distant Horizons exclusion under gametest-exclusions.json; preserved unchanged, not a rendering-only classification.'
            candidateSha256AtPreparation = $stage.candidateSha256
            currentStagedCandidate = $currentCandidate
            copiedInputFolders = @($stage.inputFolders)
            noSavesCopied = $stage.noSavesCopied
            noLinksCreated = $stage.noLinksCreated
            noEulaWrittenByPreparation = $stage.noEulaWritten
            authoredControlFiles = @($controls)
            thirdPartyOfflineRepository = $repositorySummary
            exclusions = 'Third-party/candidate JAR copies, copied config/scripts/data, logs, generated caches and runtime save output are summarized, not expanded as authored source changes.'
        })
    }
    foreach ($directory in Get-ChildItem -LiteralPath $isolatedRoot -Directory -Filter 'client-render-*') {
        $preparation = Join-Path $directory.FullName 'client-preparation.json'
        if (-not (Test-Path -LiteralPath $preparation -PathType Leaf)) { continue }
        $stage = Get-Content -LiteralPath $preparation -Raw -Encoding UTF8 | ConvertFrom-Json
        $controls = [System.Collections.Generic.List[object]]::new()
        foreach ($name in @('client-preparation.json','client-smoke.init.gradle','offline-assets.properties')) {
            $file = Join-Path $directory.FullName $name
            if (Test-Path -LiteralPath $file -PathType Leaf) { $controls.Add((File-Record $file)) }
        }
        $stagedCandidate = Join-Path $directory.FullName 'mods/industrial_colonies-0.4.0.jar'
        $currentCandidate = if (Test-Path -LiteralPath $stagedCandidate -PathType Leaf) { File-Record $stagedCandidate } else { $null }
        $activeJars = @(Get-ChildItem -LiteralPath (Join-Path $directory.FullName 'mods') -File -Filter '*.jar')
        $clientStages.Add([ordered]@{
            path = Relative-Path $directory.FullName
            purpose = 'Separate full-client acceptance copy; restores held original server-test JARs only in this new stage, not live deployment.'
            preparationMode = $stage.mode
            stagedJarCountAtPreparation = $stage.stagedJarCount
            currentActiveJarCount = $activeJars.Count
            currentActiveModBytes = ($activeJars | Measure-Object -Property Length -Sum).Sum
            restoredHeldJarsAtPreparation = @($stage.restoredHeldJars)
            candidateSha256AtPreparation = $stage.candidateSha256
            currentStagedCandidate = $currentCandidate
            noAccountsOrSavesCopiedByPreparation = $stage.noAccountsOrSavesCopied
            authoredControlFiles = @($controls)
            exclusions = 'Copied 239-JAR input roster, copied config/scripts/data/offline dependencies, generated launch arguments, runtime reports/screenshots/logs/caches and new save output are not authored source changes.'
        })
    }
}

$deliveryRoot = [IO.Path]::GetFullPath((Join-Path $ProjectRoot '../../outputs/geology-framework-20260909'))
$deliveryFiles = [System.Collections.Generic.List[object]]::new()
foreach ($relative in @('industrial_colonies-0.4.0.jar','README.md','worldgen-config-defaults/biome_families.json','worldgen-config-defaults/deposit_families.json','worldgen-config-defaults/oil.json','worldgen-config-defaults/settings.json')) {
    $file = Join-Path $deliveryRoot $relative
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Final delivery file missing: $file" }
    $record = File-Record $file
    $record.absolutePath = [IO.Path]::GetFullPath($file)
    $record.role = if ($relative -eq 'README.md') { 'newly_authored_delivery_readme' } elseif ($relative.EndsWith('.jar')) { 'copied_compiled_candidate' } else { 'copied_authoritative_default' }
    if ($relative.StartsWith('worldgen-config-defaults/')) {
        $source = 'src/main/resources/data/industrial_colonies/geology/' + [IO.Path]::GetFileName($relative)
        $record.sourcePath = $source
        $record.matchesSourceBytes = $record.sha256 -eq (Get-FileHash -LiteralPath (Join-Path $ProjectRoot $source) -Algorithm SHA256).Hash
        if (-not $record.matchesSourceBytes) { throw "Delivery config differs from source: $relative" }
    }
    $deliveryFiles.Add($record)
}
$sorted = @($entries.Values | ForEach-Object { [pscustomobject]$_ } | Sort-Object -Property path)
$categories = @($sorted | Group-Object category | Sort-Object Name | ForEach-Object { [ordered]@{category=$_.Name;files=$_.Count} })
$manifest = [ordered]@{
    version = 1
    generatedUtc = [DateTime]::UtcNow.ToString('o')
    projectRoot = $ProjectRoot
    scope = 'Current Industrial Colonies Overworld resource-generation framework task only; not the historical recipe/texture design backlog.'
    hashAlgorithm = 'SHA-256'
    coverageMethod = 'Explicit author-confirmed file families plus 295 entries from WORLDGEN_GEOLOGY_ASSETS.json. Creation/modification status uses recorded original backups and author-confirmed pre-existing files, not broad modification timestamps.'
    authoredFileCount = $sorted.Count
    createdFileCount = @($sorted | Where-Object change -eq 'created').Count
    modifiedFileCount = @($sorted | Where-Object change -eq 'modified').Count
    categories = $categories
    files = $sorted
    originalBackups = @($backupEntries.Values | ForEach-Object { [pscustomobject]$_ } | Sort-Object -Property path)
    regressionSnapshots = @(foreach ($path in @('backups/terrain-order-fix-20260909/GeologyFeature.java','backups/terrain-order-fix-20260909/industrial_colonies.mixins.json','backups/terrain-order-fix-20260909/industrial_colonies-0.4.0-before-terrain-fix.jar','backups/diamond-boundary-fix-20260909/GeologyFeature.java','backups/diamond-boundary-fix-20260909/industrial_colonies-0.4.0-before-diamond-fix.jar')) { File-Record (Join-Path $ProjectRoot $path) })
    isolatedStages = @($isolatedStages)
    clientStages = @($clientStages)
    delivery = [ordered]@{
        path = $deliveryRoot
        files = @($deliveryFiles)
        role = 'Six final handoff files, counted separately from project-authored source. Five are copies; README.md is newly authored delivery documentation.'
        deployment = 'Not installed into the live pack. Foundation acceptance is bounded to the exact evidence and limitations in WORLDGEN_FINAL_ACCEPTANCE.md; not blanket certification of the entire modpack or final economy.'
        acceptanceReport = 'WORLDGEN_FINAL_ACCEPTANCE.md'
    }
    pendingReports = @($pending)
    generatedIndexFiles = @('WORLDGEN_CHANGE_MANIFEST.json','WORLDGEN_CHANGE_MANIFEST.md')
    indexHashPolicy = 'The two manifest index files are listed here but excluded from their own content-hash set to avoid recursive self-hashing. All authored file entries, original backups, isolated authored control files and six delivery files carry current SHA-256 values.'
    excludedUnchangedExamples = @('build.gradle','src/main/resources/data/industrial_colonies/neoforge/biome_modifier/remove_tfmg_global_oil_deposits.json','src/main/resources/data/industrial_colonies/tags/worldgen/biome/oil_bearing_biomes.json','OIL_PROCESSING_PARALLELISM.md','WORLDGEN_INDUSTRIAL_RESOURCE_AUDIT.md','WORLDGEN_INDUSTRIAL_RESOURCE_AUDIT.json')
    excludedGeneratedFamilies = @('build/','build-*/','.gradle*/','tools/__pycache__/','compiled JAR outputs','copied isolated-runtime mod/config/script/data trees')
    deletedAuthoredFiles = @()
    notes = @('Source model and source reference textures are inputs, not modified files.','No live pack paths or user saves were edited by these authored file changes.','Hashes are a point-in-time inventory; refresh after any later edit.','Modified legacy oil files lacking captured originals are identified honestly; no backup availability is implied.','The initial preparation.json candidate hash is historical; currentStagedCandidate and delivery describe the final copied candidate.','No standalone prepare_offline_devlaunch_repo.ps1 existed at the final inventory; DevLaunch validation/copy logic is in prepare_geology_gametest.ps1.')
}
$manifest | ConvertTo-Json -Depth 16 -Compress
