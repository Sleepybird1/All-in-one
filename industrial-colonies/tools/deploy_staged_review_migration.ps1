[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string] $LivePackPath,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string] $StagedDirectory,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string] $BuiltFullJar,

    [switch] $PlanOnly
)

# This deployer intentionally owns one narrow transaction: the completed
# KJSGen review/deferred migration, the full Industrial Colonies JAR, and
# explicitly hash-pinned supplemental artifacts. It never derives a write
# target from a staged file name alone.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-AbsolutePath {
    param([Parameter(Mandatory)][string] $Path)
    return [System.IO.Path]::GetFullPath($Path)
}

function Test-SamePath {
    param(
        [Parameter(Mandatory)][string] $Left,
        [Parameter(Mandatory)][string] $Right
    )
    return (Get-AbsolutePath $Left).Equals(
        (Get-AbsolutePath $Right),
        [System.StringComparison]::OrdinalIgnoreCase
    )
}

function Assert-DescendantPath {
    param(
        [Parameter(Mandatory)][string] $Parent,
        [Parameter(Mandatory)][string] $Child,
        [Parameter(Mandatory)][string] $Label
    )
    $parentFull = (Get-AbsolutePath $Parent).TrimEnd('\') + '\'
    $childFull = Get-AbsolutePath $Child
    if (-not $childFull.StartsWith($parentFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "$Label escapes its required parent: $childFull"
    }
    return $childFull
}

function Get-RequiredProperty {
    param(
        [Parameter(Mandatory)][object] $Object,
        [Parameter(Mandatory)][string] $Name,
        [Parameter(Mandatory)][string] $Label
    )
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) {
        throw "$Label is missing required property '$Name'."
    }
    return $property.Value
}

function Get-OptionalProperty {
    param(
        [Parameter(Mandatory)][object] $Object,
        [Parameter(Mandatory)][string] $Name
    )
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) { return $null }
    return $property.Value
}

function Read-JsonObject {
    param(
        [Parameter(Mandatory)][string] $Path,
        [Parameter(Mandatory)][string] $Label
    )
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Missing ${Label}: $Path"
    }
    try {
        $document = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    }
    catch {
        throw "Invalid JSON in ${Label} at ${Path}: $($_.Exception.Message)"
    }
    if ($null -eq $document -or $document -is [System.Array]) {
        throw "$Label must contain one JSON object: $Path"
    }
    return $document
}

function Get-Sha256 {
    param([Parameter(Mandatory)][string] $Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Cannot hash missing file: $Path"
    }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()
}

function Normalize-Sha256 {
    param(
        [Parameter(Mandatory)][object] $Value,
        [Parameter(Mandatory)][string] $Label
    )
    $hash = ([string] $Value).Trim() -replace '^(?i)sha256:', ''
    if ($hash -notmatch '^[0-9A-Fa-f]{64}$') {
        throw "$Label is not a SHA-256 digest: $Value"
    }
    return $hash.ToUpperInvariant()
}

function Assert-FileHash {
    param(
        [Parameter(Mandatory)][string] $Path,
        [Parameter(Mandatory)][string] $ExpectedHash,
        [Parameter(Mandatory)][string] $Label
    )
    $actual = Get-Sha256 $Path
    if ($actual -ne $ExpectedHash) {
        throw "$Label hash mismatch. Expected $ExpectedHash, found $actual at $Path"
    }
}

function Get-PinnedFileState {
    param([Parameter(Mandatory)][string] $Path)
    $full = Get-AbsolutePath $Path
    $exists = Test-Path -LiteralPath $full -PathType Leaf
    if (-not $exists -and (Test-Path -LiteralPath $full)) {
        throw "Expected a file or an absent path, but found another filesystem object: $full"
    }
    return [pscustomobject]@{
        Path = $full
        Exists = $exists
        Sha256 = if ($exists) { Get-Sha256 $full } else { $null }
    }
}

function Assert-PinnedFileState {
    param(
        [Parameter(Mandatory)][object] $Expected,
        [Parameter(Mandatory)][string] $Label
    )
    $actual = Get-PinnedFileState ([string] $Expected.Path)
    if ([bool] $actual.Exists -ne [bool] $Expected.Exists) {
        throw "$Label existence changed after planning: $($Expected.Path)"
    }
    if ($actual.Exists -and ([string] $actual.Sha256) -ne ([string] $Expected.Sha256)) {
        throw "$Label changed after planning. Expected $($Expected.Sha256), found $($actual.Sha256): $($Expected.Path)"
    }
}

function Assert-JavaStopped {
    $javaProcesses = @(Get-Process -Name java, javaw -ErrorAction SilentlyContinue)
    if ($javaProcesses.Count -gt 0) {
        $details = @($javaProcesses | ForEach-Object { "$($_.ProcessName):$($_.Id)" }) -join ', '
        throw "Refusing deployment while Java is running. Close Minecraft and every java/javaw process first. Running: $details"
    }
}

function Assert-FullIndustrialColoniesJar {
    param([Parameter(Mandatory)][string] $Path)
    if ([System.IO.Path]::GetExtension($Path) -ine '.jar') {
        throw "BuiltFullJar must be a .jar file: $Path"
    }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = $null
    try {
        $archive = [System.IO.Compression.ZipFile]::OpenRead($Path)
        $entryNames = [System.Collections.Generic.HashSet[string]]::new(
            [System.StringComparer]::Ordinal
        )
        $recipeJson = 0
        $advancementJson = 0
        foreach ($entry in $archive.Entries) {
            [void] $entryNames.Add($entry.FullName)
            if ($entry.FullName -match '^data/.+/recipe/.+\.json$') { $recipeJson++ }
            if ($entry.FullName -match '^data/.+/advancement/.+\.json$') { $advancementJson++ }
        }
        foreach ($requiredEntry in @(
                'META-INF/neoforge.mods.toml',
                'dev/godpc/industrialcolonies/IndustrialColonies.class',
                'dev/godpc/industrialcolonies/KjsGenRecipeReviewStore.class',
                'industrial_colonies.mixins.json'
        )) {
            if (-not $entryNames.Contains($requiredEntry)) {
                throw "BuiltFullJar is not the full Industrial Colonies artifact; missing JAR entry $requiredEntry"
            }
        }
        if ($recipeJson -lt 1 -or $advancementJson -lt 1) {
            throw "BuiltFullJar lacks native recipe or advancement overrides ($recipeJson recipes, $advancementJson advancements)."
        }
    }
    catch {
        throw "BuiltFullJar validation failed for ${Path}: $($_.Exception.Message)"
    }
    finally {
        if ($null -ne $archive) { $archive.Dispose() }
    }
}

function Resolve-ManifestFilePath {
    param(
        [Parameter(Mandatory)][object] $Value,
        [Parameter(Mandatory)][string] $ManifestDirectory,
        [Parameter(Mandatory)][string] $Label
    )
    $text = [string] $Value
    if ([string]::IsNullOrWhiteSpace($text)) {
        throw "$Label contains a blank path."
    }
    if ([System.IO.Path]::IsPathRooted($text)) {
        return Get-AbsolutePath $text
    }
    return Get-AbsolutePath (Join-Path $ManifestDirectory $text)
}

function Assert-ProjectArtifactShape {
    param(
        [Parameter(Mandatory)][string] $LogicalName,
        [Parameter(Mandatory)][string] $Path
    )
    $document = Read-JsonObject $Path "staged $LogicalName artifact"
    if ($LogicalName -eq 'ledger') {
        if ((Get-RequiredProperty $document 'schemaVersion' 'review ledger') -ne 1) {
            throw 'The staged review ledger must use schemaVersion 1.'
        }
        if ([string] (Get-RequiredProperty $document 'project' 'review ledger') -ine 'default') {
            throw 'The staged review ledger must belong to Default.'
        }
        [void] (Get-RequiredProperty $document 'reviews' 'review ledger')
        return
    }

    $expectedProjectNames = @{
        default = 'default'
        approved = 'approved recipes'
        rejected = 'rejected recipes'
        deferred = 'deferred'
        disabled = 'disabled recipes'
    }
    $actualName = ([string] (Get-RequiredProperty $document 'name' "staged $LogicalName project")).Replace('_', ' ').Trim().ToLowerInvariant()
    while ($actualName.Contains('  ')) { $actualName = $actualName.Replace('  ', ' ') }
    if ($actualName -ne $expectedProjectNames[$LogicalName]) {
        throw "Staged $LogicalName project has unexpected name '$actualName'."
    }
    $recipes = @(Get-RequiredProperty $document 'recipes' "staged $LogicalName project")
    $removals = @(Get-RequiredProperty $document 'removals' "staged $LogicalName project")
    if ($LogicalName -ne 'default' -and $removals.Count -ne 0) {
        throw "Review archive $LogicalName unexpectedly contains removals."
    }
    $ids = @($recipes | ForEach-Object { [string] (Get-RequiredProperty $_ 'recipeId' "$LogicalName recipe") })
    $uids = @($recipes | ForEach-Object { [string] (Get-RequiredProperty $_ 'uid' "$LogicalName recipe") })
    if (@($ids | Where-Object { [string]::IsNullOrWhiteSpace($_) }).Count -gt 0 -or
        @($uids | Where-Object { [string]::IsNullOrWhiteSpace($_) }).Count -gt 0) {
        throw "Staged $LogicalName contains a recipe without an ID or UID."
    }
    if (@($ids | Group-Object | Where-Object Count -gt 1).Count -gt 0 -or
        @($uids | Group-Object | Where-Object Count -gt 1).Count -gt 0) {
        throw "Staged $LogicalName contains duplicate recipe IDs or UIDs."
    }
}

function Copy-VerifiedFile {
    param(
        [Parameter(Mandatory)][string] $Source,
        [Parameter(Mandatory)][string] $Destination,
        [Parameter(Mandatory)][string] $ExpectedHash
    )
    $parent = Split-Path -Parent $Destination
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    Copy-Item -LiteralPath $Source -Destination $Destination
    Assert-FileHash $Destination $ExpectedHash "copied file from $Source"
}

function Install-AtomicPreparedFile {
    param(
        [Parameter(Mandatory)][string] $Prepared,
        [Parameter(Mandatory)][string] $Destination,
        [Parameter(Mandatory)][bool] $DestinationExisted
    )
    if ($DestinationExisted) {
        $replaceScratch = Join-Path (Split-Path -Parent $Destination) (
            '.' + (Split-Path -Leaf $Destination) + '.replaced-' + [guid]::NewGuid().ToString('N')
        )
        try {
            [System.IO.File]::Replace($Prepared, $Destination, $replaceScratch, $true)
        }
        finally {
            if (Test-Path -LiteralPath $replaceScratch -PathType Leaf) {
                Remove-Item -LiteralPath $replaceScratch -Force -ErrorAction SilentlyContinue
            }
        }
    }
    else {
        [System.IO.File]::Move($Prepared, $Destination)
    }
}

function Restore-AtomicFile {
    param(
        [Parameter(Mandatory)][object] $PreviousState,
        [AllowNull()][string] $BackupPath,
        [Parameter(Mandatory)][string] $BackupRoot
    )
    $destination = [string] $PreviousState.Path
    if ([bool] $PreviousState.Exists) {
        if ([string]::IsNullOrWhiteSpace($BackupPath) -or -not (Test-Path -LiteralPath $BackupPath -PathType Leaf)) {
            throw "Rollback backup is missing for $destination"
        }
        Assert-FileHash $BackupPath ([string] $PreviousState.Sha256) "rollback backup for $destination"
        $parent = Split-Path -Parent $destination
        $temporary = Join-Path $parent ('.' + (Split-Path -Leaf $destination) + '.rollback-' + [guid]::NewGuid().ToString('N'))
        try {
            Copy-VerifiedFile $BackupPath $temporary ([string] $PreviousState.Sha256)
            Install-AtomicPreparedFile $temporary $destination (Test-Path -LiteralPath $destination -PathType Leaf)
        }
        finally {
            if (Test-Path -LiteralPath $temporary -PathType Leaf) {
                Remove-Item -LiteralPath $temporary -Force -ErrorAction SilentlyContinue
            }
        }
        return
    }

    if (Test-Path -LiteralPath $destination -PathType Leaf) {
        $relative = [System.IO.Path]::GetRelativePath($script:LiveRoot, $destination)
        $failedPath = Assert-DescendantPath $BackupRoot (
            Join-Path (Join-Path $BackupRoot 'failed-install-created') $relative
        ) 'failed-install recovery path'
        $failedParent = Split-Path -Parent $failedPath
        if (-not (Test-Path -LiteralPath $failedParent -PathType Container)) {
            New-Item -ItemType Directory -Path $failedParent -Force | Out-Null
        }
        [System.IO.File]::Move($destination, $failedPath)
    }
}

$script:LiveRoot = Get-AbsolutePath $LivePackPath
$stagedRoot = Get-AbsolutePath $StagedDirectory
$builtJarPath = Get-AbsolutePath $BuiltFullJar

if (-not (Test-Path -LiteralPath $script:LiveRoot -PathType Container)) {
    throw "LivePackPath does not exist: $script:LiveRoot"
}
if (-not (Test-Path -LiteralPath (Join-Path $script:LiveRoot 'minecraftinstance.json') -PathType Leaf)) {
    throw "LivePackPath is not a CurseForge Minecraft instance: $script:LiveRoot"
}
if (-not (Test-Path -LiteralPath $stagedRoot -PathType Container)) {
    throw "StagedDirectory does not exist: $stagedRoot"
}
if (-not (Test-Path -LiteralPath $builtJarPath -PathType Leaf)) {
    throw "BuiltFullJar does not exist: $builtJarPath"
}
Assert-JavaStopped
Assert-FullIndustrialColoniesJar $builtJarPath
$builtJarHash = Get-Sha256 $builtJarPath

$modsRoot = Assert-DescendantPath $script:LiveRoot (Join-Path $script:LiveRoot 'mods') 'mods directory'
$activeJars = @(
    Get-ChildItem -LiteralPath $modsRoot -File |
        Where-Object { $_.Name -match '(?i)^industrial_colonies-.+\.jar$' }
)
if ($activeJars.Count -ne 1) {
    throw "Expected exactly one active Industrial Colonies JAR, found $($activeJars.Count) in $modsRoot"
}
$liveJar = Get-AbsolutePath $activeJars[0].FullName
if (Test-SamePath $builtJarPath $liveJar) {
    throw 'BuiltFullJar must be an out-of-place build artifact, not the active live JAR.'
}

$knownLivePaths = [ordered]@{
    ledger = Assert-DescendantPath $script:LiveRoot (Join-Path $script:LiveRoot 'kjsgen\industrial_colonies_sync\default.recipe_reviews.json') 'review ledger'
    default = Assert-DescendantPath $script:LiveRoot (Join-Path $script:LiveRoot 'kjsgen\projects\default.json') 'Default project'
    approved = Assert-DescendantPath $script:LiveRoot (Join-Path $script:LiveRoot 'kjsgen\projects\approved_recipes.json') 'Approved project'
    rejected = Assert-DescendantPath $script:LiveRoot (Join-Path $script:LiveRoot 'kjsgen\projects\rejected_recipes.json') 'Rejected project'
    deferred = Assert-DescendantPath $script:LiveRoot (Join-Path $script:LiveRoot 'kjsgen\projects\Deferred.json') 'Deferred project'
    disabled = Assert-DescendantPath $script:LiveRoot (Join-Path $script:LiveRoot 'kjsgen\projects\disabled_recipes.json') 'Disabled project'
    maybe = Assert-DescendantPath $script:LiveRoot (Join-Path $script:LiveRoot 'kjsgen\projects\maybe_recipes.json') 'legacy Maybe project'
    generatedScript = Assert-DescendantPath $script:LiveRoot (Join-Path $script:LiveRoot 'kubejs\server_scripts\kjsgen_recipes.js') 'generated KJSGen script'
    quest = Assert-DescendantPath $script:LiveRoot (Join-Path $script:LiveRoot 'config\ftbquests\quests\chapters\mekanized_industry.snbt') 'Mekanized Industry quest file'
}

foreach ($requiredLiveName in @('ledger', 'default', 'approved', 'rejected', 'disabled', 'generatedScript', 'quest')) {
    if (-not (Test-Path -LiteralPath $knownLivePaths[$requiredLiveName] -PathType Leaf)) {
        throw "Required live $requiredLiveName file is missing: $($knownLivePaths[$requiredLiveName])"
    }
}
$legacyMaybeExists = Test-Path -LiteralPath $knownLivePaths.maybe -PathType Leaf
$deferredExists = Test-Path -LiteralPath $knownLivePaths.deferred -PathType Leaf
if ($legacyMaybeExists -and $deferredExists) {
    throw 'Both maybe_recipes.json and Deferred.json are active. Refusing an ambiguous partial migration.'
}
if (-not $legacyMaybeExists -and -not $deferredExists) {
    throw 'Neither maybe_recipes.json nor Deferred.json exists; the review archive state is incomplete.'
}

$migrationManifestPath = Assert-DescendantPath $stagedRoot (Join-Path $stagedRoot 'migration_manifest.json') 'migration manifest'
$migrationManifest = Read-JsonObject $migrationManifestPath 'migration manifest'
if ((Get-RequiredProperty $migrationManifest 'schemaVersion' 'migration manifest') -ne 1) {
    throw 'migration_manifest.json must use schemaVersion 1.'
}
$manifestSourcePack = Get-AbsolutePath ([string] (Get-RequiredProperty $migrationManifest 'sourcePack' 'migration manifest'))
if (-not (Test-SamePath $manifestSourcePack $script:LiveRoot)) {
    throw "The migration manifest was staged from a different pack: $manifestSourcePack"
}

$migrationSourceFiles = Get-RequiredProperty $migrationManifest 'sourceFiles' 'migration manifest'
$migrationOutputFiles = Get-RequiredProperty $migrationManifest 'outputFiles' 'migration manifest'
$fixedSourceKeys = @('ledger', 'default', 'approved', 'rejected', 'disabled')
$archiveSourceKey = $null
if ($null -ne $migrationSourceFiles.PSObject.Properties['maybe']) { $archiveSourceKey = 'maybe' }
if ($null -ne $migrationSourceFiles.PSObject.Properties['deferred']) {
    if ($null -ne $archiveSourceKey) { throw 'Migration sourceFiles may not contain both maybe and deferred.' }
    $archiveSourceKey = 'deferred'
}
if ($null -eq $archiveSourceKey) {
    throw 'Migration sourceFiles must pin either the legacy Maybe archive or the Deferred archive.'
}
$allowedSourceKeys = @($fixedSourceKeys) + @($archiveSourceKey)
$unexpectedSourceKeys = @($migrationSourceFiles.PSObject.Properties.Name | Where-Object { $_ -notin $allowedSourceKeys })
if ($unexpectedSourceKeys.Count -gt 0) {
    throw "Migration sourceFiles contains unsupported entries: $($unexpectedSourceKeys -join ', ')"
}

$manifestDirectory = Split-Path -Parent $migrationManifestPath
$sourcePins = [System.Collections.Generic.List[object]]::new()
foreach ($logicalName in $allowedSourceKeys) {
    $entry = Get-RequiredProperty $migrationSourceFiles $logicalName 'migration sourceFiles'
    $sourcePath = Resolve-ManifestFilePath (Get-RequiredProperty $entry 'path' "migration source $logicalName") $manifestDirectory "migration source $logicalName"
    $expectedLivePath = $knownLivePaths[$logicalName]
    if (-not (Test-SamePath $sourcePath $expectedLivePath)) {
        throw "Migration source '$logicalName' is not its fixed live path. Expected $expectedLivePath, found $sourcePath"
    }
    $expectedHash = Normalize-Sha256 (Get-RequiredProperty $entry 'sha256' "migration source $logicalName") "migration source $logicalName"
    Assert-FileHash $sourcePath $expectedHash "live migration source $logicalName"
    $sourcePins.Add([pscustomobject]@{ Path = $sourcePath; Sha256 = $expectedHash; Label = "live migration source $logicalName" })
}

$requiredOutputKeys = @('ledger', 'default', 'approved', 'rejected', 'deferred', 'disabled')
$unexpectedOutputKeys = @($migrationOutputFiles.PSObject.Properties.Name | Where-Object { $_ -notin $requiredOutputKeys })
if ($unexpectedOutputKeys.Count -gt 0) {
    throw "Migration outputFiles contains unsupported entries: $($unexpectedOutputKeys -join ', ')"
}
$expectedOutputNames = @{
    ledger = 'default.recipe_reviews.json'
    default = 'default.json'
    approved = 'approved_recipes.json'
    rejected = 'rejected_recipes.json'
    deferred = 'Deferred.json'
    disabled = 'disabled_recipes.json'
}
$finalSources = @{}
foreach ($logicalName in $requiredOutputKeys) {
    $entry = Get-RequiredProperty $migrationOutputFiles $logicalName 'migration outputFiles'
    $outputPath = Resolve-ManifestFilePath (Get-RequiredProperty $entry 'path' "migration output $logicalName") $manifestDirectory "migration output $logicalName"
    if ((Split-Path -Leaf $outputPath) -ine $expectedOutputNames[$logicalName]) {
        throw "Migration output '$logicalName' has unexpected file name: $outputPath"
    }
    $outputHash = Normalize-Sha256 (Get-RequiredProperty $entry 'sha256' "migration output $logicalName") "migration output $logicalName"
    Assert-FileHash $outputPath $outputHash "staged migration output $logicalName"
    $finalSources[$logicalName] = [pscustomobject]@{ Path = $outputPath; Sha256 = $outputHash }
}

# A steel transform is a second, hash-pinned stage. Every artifact must consume
# the exact preceding migration artifact with the same base name and must write
# its result inside StagedDirectory. This preserves approved/rejected/deferred
# decisions while permitting their card fingerprints to be updated together.
$steelReportPath = Join-Path $stagedRoot 'steel_frame_transform_report.json'
if (Test-Path -LiteralPath $steelReportPath -PathType Leaf) {
    $steelReport = Read-JsonObject $steelReportPath 'steel-frame transform report'
    if ((Get-RequiredProperty $steelReport 'schemaVersion' 'steel-frame transform report') -ne 1 -or
        [string] (Get-RequiredProperty $steelReport 'operation' 'steel-frame transform report') -ne 'replace_mekanism_steel_casing_with_tfmg_steel_frame') {
        throw 'steel_frame_transform_report.json has an unsupported schema or operation.'
    }
    $baseManifest = Get-OptionalProperty $steelReport 'baseMigrationManifest'
    if ($null -eq $baseManifest) {
        throw 'The steel transform must pin its copied base migration manifest.'
    }
    if ($null -ne $baseManifest) {
        $stagedManifestPath = Resolve-ManifestFilePath (Get-RequiredProperty $baseManifest 'stagedPath' 'baseMigrationManifest') $stagedRoot 'baseMigrationManifest stagedPath'
        if (-not (Test-SamePath $stagedManifestPath $migrationManifestPath)) {
            throw 'The steel transform does not pin the migration manifest supplied to this deployer.'
        }
        $stagedManifestHash = Normalize-Sha256 (Get-RequiredProperty $baseManifest 'stagedSha256' 'baseMigrationManifest') 'baseMigrationManifest stagedSha256'
        Assert-FileHash $migrationManifestPath $stagedManifestHash 'steel-pinned migration manifest'
        $inputManifestPathValue = Get-OptionalProperty $baseManifest 'inputPath'
        $inputManifestHashValue = Get-OptionalProperty $baseManifest 'inputSha256'
        if ($null -ne $inputManifestPathValue -or $null -ne $inputManifestHashValue) {
            if ($null -eq $inputManifestPathValue -or $null -eq $inputManifestHashValue) {
                throw 'baseMigrationManifest must provide both inputPath and inputSha256 when either is present.'
            }
            $inputManifestPath = Resolve-ManifestFilePath $inputManifestPathValue $stagedRoot 'baseMigrationManifest inputPath'
            $inputManifestHash = Normalize-Sha256 $inputManifestHashValue 'baseMigrationManifest inputSha256'
            Assert-FileHash $inputManifestPath $inputManifestHash 'steel transform input migration manifest'
        }
    }
    $artifacts = @(Get-RequiredProperty $steelReport 'artifacts' 'steel-frame transform report')
    if ($artifacts.Count -lt 1) { throw 'Steel-frame transform report contains no artifacts.' }
    $seenSteelFiles = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($artifact in $artifacts) {
        $fileName = [string] (Get-RequiredProperty $artifact 'fileName' 'steel artifact')
        if (-not $seenSteelFiles.Add($fileName)) { throw "Steel report repeats artifact $fileName" }
        $logicalName = @($expectedOutputNames.Keys | Where-Object { $expectedOutputNames[$_] -ieq $fileName })
        if ($logicalName.Count -ne 1) { throw "Steel report contains unsupported artifact $fileName" }
        $logicalName = [string] $logicalName[0]
        $inputPath = Resolve-ManifestFilePath (Get-RequiredProperty $artifact 'inputPath' "steel artifact $fileName") $stagedRoot "steel artifact $fileName input"
        $inputHash = Normalize-Sha256 (Get-RequiredProperty $artifact 'inputSha256' "steel artifact $fileName") "steel artifact $fileName input"
        if (-not (Test-SamePath $inputPath $finalSources[$logicalName].Path) -or $inputHash -ne $finalSources[$logicalName].Sha256) {
            throw "Steel artifact $fileName does not consume the exact staged migration output."
        }
        Assert-FileHash $inputPath $inputHash "steel artifact $fileName input"
        $stagedPath = Resolve-ManifestFilePath (Get-RequiredProperty $artifact 'stagedPath' "steel artifact $fileName") $stagedRoot "steel artifact $fileName output"
        [void] (Assert-DescendantPath $stagedRoot $stagedPath "steel artifact $fileName output")
        if ((Split-Path -Leaf $stagedPath) -ine $fileName) {
            throw "Steel artifact path/fileName mismatch for $fileName"
        }
        $stagedHash = Normalize-Sha256 (Get-RequiredProperty $artifact 'stagedSha256' "steel artifact $fileName") "steel artifact $fileName output"
        Assert-FileHash $stagedPath $stagedHash "steel artifact $fileName output"
        $finalSources[$logicalName] = [pscustomobject]@{ Path = $stagedPath; Sha256 = $stagedHash }
    }
    $missingSteelFiles = @($expectedOutputNames.Values | Where-Object { -not $seenSteelFiles.Contains([string] $_) })
    if ($missingSteelFiles.Count -gt 0) {
        throw "Steel report does not pin every final review artifact: $($missingSteelFiles -join ', ')"
    }
}
else {
    foreach ($logicalName in $requiredOutputKeys) {
        [void] (Assert-DescendantPath $stagedRoot $finalSources[$logicalName].Path "staged migration output $logicalName")
    }
}

foreach ($logicalName in $requiredOutputKeys) {
    Assert-ProjectArtifactShape $logicalName $finalSources[$logicalName].Path
}

$installItems = [System.Collections.Generic.List[object]]::new()
$plannedDestinations = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
function Add-InstallItem {
    param(
        [Parameter(Mandatory)][string] $Label,
        [Parameter(Mandatory)][string] $Source,
        [Parameter(Mandatory)][string] $SourceHash,
        [Parameter(Mandatory)][string] $Destination
    )
    if (-not $plannedDestinations.Add((Get-AbsolutePath $Destination))) {
        throw "More than one artifact targets $Destination"
    }
    $installItems.Add([pscustomobject]@{
        Label = $Label
        Source = Get-AbsolutePath $Source
        SourceHash = $SourceHash
        Destination = Get-AbsolutePath $Destination
        Prepared = $null
        Committed = $false
    })
}

foreach ($logicalName in $requiredOutputKeys) {
    Add-InstallItem "review artifact $logicalName" $finalSources[$logicalName].Path $finalSources[$logicalName].Sha256 $knownLivePaths[$logicalName]
}
Add-InstallItem 'full Industrial Colonies JAR' $builtJarPath $builtJarHash $liveJar

# Supplemental writes require an explicit source hash and an explicit expected
# live-input hash. The FTB quest source is intentionally represented here;
# this script never writes an entire FTB Quests directory.
$extraManifestPath = Join-Path $stagedRoot 'policy_deployment_manifest.json'
if (-not (Test-Path -LiteralPath $extraManifestPath -PathType Leaf)) {
    throw "Missing policy_deployment_manifest.json. It must explicitly pin the JAR and mekanized_industry.snbt source/live hashes: $extraManifestPath"
}
$extraManifest = Read-JsonObject $extraManifestPath 'supplemental deployment manifest'
if ((Get-RequiredProperty $extraManifest 'schemaVersion' 'supplemental deployment manifest') -ne 1) {
    throw 'policy_deployment_manifest.json must use schemaVersion 1.'
}
$policyOperation = [string] (Get-RequiredProperty $extraManifest 'operation' 'supplemental deployment manifest')
if ($policyOperation -ne 'deploy_review_deferred_and_tfmg_steel_frame_policy') {
    throw "Unsupported policy deployment operation: $policyOperation"
}
$extraArtifacts = @(Get-RequiredProperty $extraManifest 'artifacts' 'supplemental deployment manifest')
$questArtifactSeen = $false
$jarArtifactSeen = $false
foreach ($artifact in $extraArtifacts) {
    $kind = [string] (Get-RequiredProperty $artifact 'kind' 'policy artifact')
    if ($kind -notin @('jar', 'ftbquest', 'file')) {
        throw "Unsupported policy artifact kind: $kind"
    }
    $label = "policy $kind artifact"
    $source = Resolve-ManifestFilePath (Get-RequiredProperty $artifact 'source' $label) (Split-Path -Parent $extraManifestPath) "$label source"
    $sourceHash = Normalize-Sha256 (Get-RequiredProperty $artifact 'sourceSha256' $label) "$label source"
    Assert-FileHash $source $sourceHash "$label source"
    $relativeDestination = [string] (Get-RequiredProperty $artifact 'target' $label)
    if ([string]::IsNullOrWhiteSpace($relativeDestination) -or [System.IO.Path]::IsPathRooted($relativeDestination)) {
        throw "$label has an invalid target."
    }
    $destination = Assert-DescendantPath $script:LiveRoot (Join-Path $script:LiveRoot $relativeDestination) "$label destination"
    $expectedLiveHashValue = Get-OptionalProperty $artifact 'expectedLiveSha256'
    $expectedLiveAbsentValue = Get-OptionalProperty $artifact 'expectedLiveAbsent'
    if ($null -ne $expectedLiveHashValue -and $expectedLiveAbsentValue -eq $true) {
        throw "$label cannot specify both expectedLiveSha256 and expectedLiveAbsent."
    }
    if ($null -eq $expectedLiveHashValue -and $expectedLiveAbsentValue -ne $true) {
        throw "$label must specify expectedLiveSha256 or expectedLiveAbsent: true."
    }
    $expectedState = Get-PinnedFileState $destination
    if ($null -ne $expectedLiveHashValue) {
        $expectedLiveHash = Normalize-Sha256 $expectedLiveHashValue "$label expected live input"
        if (-not $expectedState.Exists -or $expectedState.Sha256 -ne $expectedLiveHash) {
            throw "$label live input does not match expectedLiveSha256 at $destination"
        }
    }
    elseif ($expectedState.Exists) {
        throw "$label expected an absent live destination, but one exists: $destination"
    }
    if ($kind -eq 'jar') {
        if (-not (Test-SamePath $source $builtJarPath) -or $sourceHash -ne $builtJarHash) {
            throw 'The policy JAR artifact does not pin the BuiltFullJar argument exactly.'
        }
        if (-not (Test-SamePath $destination $liveJar)) {
            throw 'The policy JAR artifact does not target the single active Industrial Colonies JAR.'
        }
        if ($jarArtifactSeen) { throw 'The policy manifest contains more than one JAR artifact.' }
        $jarArtifactSeen = $true
        continue
    }

    if ($kind -eq 'ftbquest') {
        if (-not (Test-SamePath $destination $knownLivePaths.quest)) {
            throw 'The ftbquest policy artifact may target only mekanized_industry.snbt.'
        }
        [void] (Assert-DescendantPath $stagedRoot $source 'staged Mekanized Industry quest source')
        if ((Get-RequiredProperty $artifact 'exactReplacements' $label) -ne 2) {
            throw 'The Mekanized Industry quest artifact must attest exactly two policy substitutions.'
        }
        if ($questArtifactSeen) { throw 'The policy manifest contains more than one Mekanized Industry quest artifact.' }
        $questArtifactSeen = $true
    }
    Add-InstallItem $label $source $sourceHash $destination
}
if (-not $questArtifactSeen) {
    throw 'policy_deployment_manifest.json must include the exact config/ftbquests/quests/chapters/mekanized_industry.snbt destination.'
}
if (-not $jarArtifactSeen) {
    throw 'policy_deployment_manifest.json must include the exact BuiltFullJar and active JAR hashes.'
}

$manifestPins = [System.Collections.Generic.List[object]]::new()
foreach ($manifestPath in @($migrationManifestPath, $extraManifestPath)) {
    $manifestPins.Add([pscustomobject]@{ Path = Get-AbsolutePath $manifestPath; Sha256 = Get-Sha256 $manifestPath; Label = 'deployment manifest' })
}
if (Test-Path -LiteralPath $steelReportPath -PathType Leaf) {
    $manifestPins.Add([pscustomobject]@{ Path = Get-AbsolutePath $steelReportPath; Sha256 = Get-Sha256 $steelReportPath; Label = 'steel-frame transform report' })
}

$protectedStates = [System.Collections.Generic.Dictionary[string, object]]::new([System.StringComparer]::OrdinalIgnoreCase)
function Add-ProtectedState {
    param([Parameter(Mandatory)][string] $Path)
    $full = Get-AbsolutePath $Path
    if (-not $protectedStates.ContainsKey($full)) {
        $protectedStates.Add($full, (Get-PinnedFileState $full))
    }
}
foreach ($path in @(
        $liveJar,
        $knownLivePaths.ledger,
        $knownLivePaths.default,
        $knownLivePaths.approved,
        $knownLivePaths.rejected,
        $knownLivePaths.disabled,
        $knownLivePaths.maybe,
        $knownLivePaths.deferred,
        $knownLivePaths.generatedScript,
        $knownLivePaths.quest
)) {
    Add-ProtectedState $path
}
foreach ($item in $installItems) { Add-ProtectedState $item.Destination }

function Assert-AllInputsCurrent {
    Assert-JavaStopped
    Assert-FileHash $builtJarPath $builtJarHash 'built full JAR'
    foreach ($pin in $sourcePins) { Assert-FileHash $pin.Path $pin.Sha256 $pin.Label }
    foreach ($pin in $manifestPins) { Assert-FileHash $pin.Path $pin.Sha256 $pin.Label }
    foreach ($item in $installItems) { Assert-FileHash $item.Source $item.SourceHash "$($item.Label) source" }
    foreach ($state in $protectedStates.Values) { Assert-PinnedFileState $state 'live destination' }
}

Assert-AllInputsCurrent

Write-Host 'Validated staged review deployment plan:' -ForegroundColor Cyan
Write-Host "  Live pack: $script:LiveRoot"
Write-Host "  Full JAR: $builtJarPath ($builtJarHash)"
Write-Host "  Review stage: $stagedRoot"
Write-Host "  Steel policy stage: $(if (Test-Path -LiteralPath $steelReportPath -PathType Leaf) { 'present' } else { 'not present' })"
foreach ($item in $installItems) {
    Write-Host "  INSTALL $($item.Label): $($item.Destination)"
}
if ($legacyMaybeExists) {
    Write-Host "  RETIRE legacy Maybe archive: $($knownLivePaths.maybe)"
}
Write-Host "  PROTECT generated KJSGen script: $($knownLivePaths.generatedScript)"
Write-Host "  PROTECT FTB quest file: $($knownLivePaths.quest)"

if ($PlanOnly) {
    Write-Host 'PlanOnly complete: all source, staged-output, and live-input hashes match; no files were changed.' -ForegroundColor Green
    return
}

$backupParent = Assert-DescendantPath $script:LiveRoot (Join-Path $script:LiveRoot '_industrial_colonies_backups') 'backup parent'
$lockPath = Assert-DescendantPath $script:LiveRoot (Join-Path $script:LiveRoot '.industrial_colonies_review_deploy.lock') 'deployment lock'
$lockStream = $null
$backupRoot = $null
$backupByLivePath = [System.Collections.Generic.Dictionary[string, string]]::new([System.StringComparer]::OrdinalIgnoreCase)
$committedItems = [System.Collections.Generic.List[object]]::new()
$legacyMaybeRetired = $false
$retiredMaybePath = $null
$transactionStarted = $false
$deploymentSucceeded = $false
$lockAcquired = $false

try {
    try {
        $lockStream = [System.IO.FileStream]::new(
            $lockPath,
            [System.IO.FileMode]::CreateNew,
            [System.IO.FileAccess]::ReadWrite,
            [System.IO.FileShare]::None,
            1,
            [System.IO.FileOptions]::DeleteOnClose
        )
        $lockAcquired = $true
    }
    catch {
        throw "Could not acquire the deployment lock at ${lockPath}: $($_.Exception.Message)"
    }

    Assert-AllInputsCurrent
    if (-not (Test-Path -LiteralPath $backupParent -PathType Container)) {
        New-Item -ItemType Directory -Path $backupParent | Out-Null
    }
    $backupRoot = Assert-DescendantPath $backupParent (
        Join-Path $backupParent ('review-migration-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
    ) 'deployment backup'
    New-Item -ItemType Directory -Path $backupRoot | Out-Null

    foreach ($state in $protectedStates.Values) {
        if (-not [bool] $state.Exists) { continue }
        $relative = [System.IO.Path]::GetRelativePath($script:LiveRoot, [string] $state.Path)
        $backupPath = Assert-DescendantPath $backupRoot (Join-Path (Join-Path $backupRoot 'snapshot') $relative) 'backup snapshot file'
        Copy-VerifiedFile ([string] $state.Path) $backupPath ([string] $state.Sha256)
        $backupByLivePath.Add([string] $state.Path, $backupPath)
    }

    $preinstallManifest = [ordered]@{
        schemaVersion = 1
        createdAt = (Get-Date).ToUniversalTime().ToString('o')
        livePack = $script:LiveRoot
        stagedDirectory = $stagedRoot
        builtFullJar = [ordered]@{ path = $builtJarPath; sha256 = $builtJarHash }
        protectedFiles = @($protectedStates.Values | ForEach-Object {
            [ordered]@{
                path = $_.Path
                existed = [bool] $_.Exists
                sha256 = $_.Sha256
                backup = if ($backupByLivePath.ContainsKey([string] $_.Path)) { $backupByLivePath[[string] $_.Path] } else { $null }
            }
        })
        plannedInstalls = @($installItems | ForEach-Object {
            [ordered]@{ label = $_.Label; source = $_.Source; sourceSha256 = $_.SourceHash; destination = $_.Destination }
        })
        retireLegacyMaybe = $legacyMaybeExists
    }
    $preinstallManifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $backupRoot 'preinstall_manifest.json') -Encoding utf8

    # Prepare every payload beside its destination before the first replacement.
    foreach ($item in $installItems) {
        $destinationParent = Split-Path -Parent $item.Destination
        if (-not (Test-Path -LiteralPath $destinationParent -PathType Container)) {
            throw "Destination directory is missing; refusing to create an unmanifested directory: $destinationParent"
        }
        $prepared = Assert-DescendantPath $script:LiveRoot (Join-Path $destinationParent (
            '.' + (Split-Path -Leaf $item.Destination) + '.deploying-' + [guid]::NewGuid().ToString('N')
        )) 'same-volume prepared file'
        Copy-VerifiedFile $item.Source $prepared $item.SourceHash
        $item.Prepared = $prepared
    }

    # Close the validation-to-commit race as far as a local multi-file update permits.
    Assert-AllInputsCurrent
    $transactionStarted = $true

    foreach ($item in $installItems) {
        Assert-JavaStopped
        Assert-FileHash $item.Source $item.SourceHash "$($item.Label) source"
        Assert-PinnedFileState $protectedStates[$item.Destination] "$($item.Label) destination"
        Install-AtomicPreparedFile $item.Prepared $item.Destination ([bool] $protectedStates[$item.Destination].Exists)
        $item.Prepared = $null
        $item.Committed = $true
        $committedItems.Add($item)
        Assert-FileHash $item.Destination $item.SourceHash "$($item.Label) installed output"
    }

    if ($legacyMaybeExists) {
        Assert-JavaStopped
        Assert-PinnedFileState $protectedStates[$knownLivePaths.maybe] 'legacy Maybe archive'
        $retiredMaybePath = Assert-DescendantPath $backupRoot (Join-Path $backupRoot 'retired\kjsgen\projects\maybe_recipes.json') 'retired Maybe archive'
        $retiredParent = Split-Path -Parent $retiredMaybePath
        if (-not (Test-Path -LiteralPath $retiredParent -PathType Container)) {
            New-Item -ItemType Directory -Path $retiredParent -Force | Out-Null
        }
        [System.IO.File]::Move($knownLivePaths.maybe, $retiredMaybePath)
        $legacyMaybeRetired = $true
        Assert-FileHash $retiredMaybePath $protectedStates[$knownLivePaths.maybe].Sha256 'retired legacy Maybe archive'
    }

    foreach ($item in $installItems) {
        Assert-FileHash $item.Destination $item.SourceHash "$($item.Label) post-install"
    }
    if ($legacyMaybeExists -and (Test-Path -LiteralPath $knownLivePaths.maybe)) {
        throw 'Legacy maybe_recipes.json remained active after retirement.'
    }
    Assert-FileHash $knownLivePaths.deferred $finalSources.deferred.Sha256 'active Deferred project'
    Assert-FileHash $knownLivePaths.generatedScript $protectedStates[$knownLivePaths.generatedScript].Sha256 'protected generated KJSGen script'

    $postinstallManifest = [ordered]@{
        schemaVersion = 1
        completedAt = (Get-Date).ToUniversalTime().ToString('o')
        livePack = $script:LiveRoot
        backup = $backupRoot
        installed = @($installItems | ForEach-Object {
            [ordered]@{ label = $_.Label; destination = $_.Destination; sha256 = Get-Sha256 $_.Destination }
        })
        retiredLegacyMaybe = if ($legacyMaybeRetired) {
            [ordered]@{ from = $knownLivePaths.maybe; to = $retiredMaybePath; sha256 = Get-Sha256 $retiredMaybePath }
        } else { $null }
    }
    $postinstallManifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $backupRoot 'postinstall_manifest.json') -Encoding utf8
    $deploymentSucceeded = $true
}
catch {
    $deploymentError = $_
    if ($transactionStarted) {
        Write-Warning "Deployment failed; rolling back every committed live file: $($deploymentError.Exception.Message)"
        $rollbackErrors = [System.Collections.Generic.List[string]]::new()

        if ($legacyMaybeRetired) {
            try {
                if (Test-Path -LiteralPath $knownLivePaths.maybe) {
                    throw "Cannot restore legacy Maybe archive because its live path is occupied: $($knownLivePaths.maybe)"
                }
                [System.IO.File]::Move($retiredMaybePath, $knownLivePaths.maybe)
            }
            catch { $rollbackErrors.Add($_.Exception.Message) }
        }

        for ($index = $committedItems.Count - 1; $index -ge 0; $index--) {
            $item = $committedItems[$index]
            try {
                $previous = $protectedStates[$item.Destination]
                $backupPath = if ($backupByLivePath.ContainsKey($item.Destination)) { $backupByLivePath[$item.Destination] } else { $null }
                Restore-AtomicFile $previous $backupPath $backupRoot
            }
            catch { $rollbackErrors.Add($_.Exception.Message) }
        }

        foreach ($state in $protectedStates.Values) {
            try { Assert-PinnedFileState $state 'post-rollback live file' }
            catch { $rollbackErrors.Add($_.Exception.Message) }
        }
        if ($rollbackErrors.Count -gt 0) {
            throw "Deployment failed and rollback was incomplete. Backup: $backupRoot. Cause: $($deploymentError.Exception.Message). Rollback errors: $($rollbackErrors -join ' | ')"
        }
        throw "Deployment failed and was completely rolled back. Backup retained at $backupRoot. Cause: $($deploymentError.Exception.Message)"
    }
    throw
}
finally {
    foreach ($item in $installItems) {
        if ($null -ne $item.Prepared -and (Test-Path -LiteralPath $item.Prepared -PathType Leaf)) {
            Remove-Item -LiteralPath $item.Prepared -Force -ErrorAction SilentlyContinue
        }
    }
    if ($null -ne $lockStream) { $lockStream.Dispose() }
    if ($lockAcquired -and (Test-Path -LiteralPath $lockPath -PathType Leaf)) {
        Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue
    }
}

if ($deploymentSucceeded) {
    Write-Host 'Deployment completed with staged/live SHA-256 parity verified.' -ForegroundColor Green
    Write-Host "Backup and recovery manifests: $backupRoot"
}
