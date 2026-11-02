[CmdletBinding()]
param(
    [string] $ProjectRoot = '',
    [string] $LiveRoot = 'C:\Users\GodPC\curseforge\minecraft\Instances\All in one',
    [string] $StagedRoot = '',
    [string] $PredecessorRoot = '',
    [switch] $PlanOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $scriptRoot
}
if ([string]::IsNullOrWhiteSpace($StagedRoot)) {
    $StagedRoot = Join-Path $ProjectRoot 'progression\review-batches\20260902\staged'
}
if ([string]::IsNullOrWhiteSpace($PredecessorRoot)) {
    $PredecessorRoot = Join-Path $ProjectRoot 'progression\review-batches\20260902\predecessor'
}

function Get-FullPath {
    param([Parameter(Mandatory)][string] $Path)
    return [System.IO.Path]::GetFullPath($Path)
}

function Assert-ChildPath {
    param(
        [Parameter(Mandatory)][string] $Parent,
        [Parameter(Mandatory)][string] $Child,
        [Parameter(Mandatory)][string] $Label
    )
    $parentFull = (Get-FullPath $Parent).TrimEnd('\') + '\'
    $childFull = Get-FullPath $Child
    if (-not $childFull.StartsWith($parentFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "$Label escapes its required parent: $childFull"
    }
    return $childFull
}

function Get-Sha256 {
    param([Parameter(Mandatory)][string] $Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()
}

function Assert-Hash {
    param(
        [Parameter(Mandatory)][string] $Path,
        [Parameter(Mandatory)][string] $Expected,
        [Parameter(Mandatory)][string] $Label
    )
    $actual = Get-Sha256 $Path
    if ($actual -ne $Expected.ToUpperInvariant()) {
        throw "$Label changed after review reconciliation. Expected $Expected, found $actual at $Path"
    }
}

function Assert-UniqueField {
    param(
        [Parameter(Mandatory)][object[]] $Entries,
        [Parameter(Mandatory)][string] $Field,
        [Parameter(Mandatory)][string] $Label
    )
    $values = @($Entries | ForEach-Object { $_.$Field })
    if ($values.Count -ne (@($values | Where-Object { $_ -is [string] -and $_.Length -gt 0 })).Count) {
        throw "$Label contains a blank $Field."
    }
    $duplicates = @($values | Group-Object | Where-Object Count -gt 1 | Select-Object -ExpandProperty Name)
    if ($duplicates.Count -gt 0) {
        throw "$Label contains duplicate ${Field}: $($duplicates -join ', ')"
    }
}

function Install-AtomicFile {
    param(
        [Parameter(Mandatory)][string] $Source,
        [Parameter(Mandatory)][string] $Destination
    )
    $destinationDirectory = Split-Path -Parent $Destination
    $temporary = Join-Path $destinationDirectory ('.' + [System.IO.Path]::GetFileName($Destination) + '.' + [guid]::NewGuid().ToString('N') + '.tmp')
    $replaceBackup = Join-Path $destinationDirectory ('.' + [System.IO.Path]::GetFileName($Destination) + '.' + [guid]::NewGuid().ToString('N') + '.replace.bak')
    try {
        Copy-Item -LiteralPath $Source -Destination $temporary
        if ((Get-Sha256 $temporary) -ne (Get-Sha256 $Source)) {
            throw "Temporary copy hash mismatch for $Destination"
        }
        [System.IO.File]::Replace($temporary, $Destination, $replaceBackup, $true)
        if (Test-Path -LiteralPath $replaceBackup) {
            Remove-Item -LiteralPath $replaceBackup -Force
        }
    }
    finally {
        if (Test-Path -LiteralPath $temporary) {
            Remove-Item -LiteralPath $temporary -Force
        }
    }
}

$project = Get-FullPath $ProjectRoot
$live = Get-FullPath $LiveRoot
$staged = Get-FullPath $StagedRoot
$predecessor = Get-FullPath $PredecessorRoot
$batchRoot = Get-FullPath (Split-Path -Parent $staged)
if (-not (Get-FullPath (Split-Path -Parent $predecessor)).Equals(
        $batchRoot,
        [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Staged and predecessor snapshots must belong to the same durable review batch.'
}
$expectedLive = Get-FullPath 'C:\Users\GodPC\curseforge\minecraft\Instances\All in one'
if (-not $live.Equals($expectedLive, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "This one-time migration is pinned to the All in one instance: $expectedLive"
}
if (-not (Test-Path -LiteralPath (Join-Path $live 'minecraftinstance.json') -PathType Leaf)) {
    throw "The target is not the expected CurseForge instance: $live"
}

$paths = [ordered]@{
    LiveProject = Assert-ChildPath $live (Join-Path $live 'kjsgen\projects\default.json') 'live project'
    LiveApproved = Assert-ChildPath $live (Join-Path $live 'kjsgen\projects\Approved_Recipes.json') 'approved project'
    LiveBaseline = Assert-ChildPath $live (Join-Path $live 'kjsgen\industrial_colonies_sync\default.managed.baseline.json') 'live baseline'
    LiveReviews = Assert-ChildPath $live (Join-Path $live 'kjsgen\industrial_colonies_sync\default.recipe_reviews.json') 'review ledger'
    LiveScript = Assert-ChildPath $live (Join-Path $live 'kubejs\server_scripts\kjsgen_recipes.js') 'KJSGen export'
    StagedProject = Assert-ChildPath $staged (Join-Path $staged 'default.json') 'staged project'
    StagedApproved = Assert-ChildPath $staged (Join-Path $staged 'Approved_Recipes.json') 'staged approved project'
    StagedBaseline = Assert-ChildPath $staged (Join-Path $staged 'default.managed.baseline.json') 'staged baseline'
    StagedManaged = Assert-ChildPath $staged (Join-Path $staged 'default.reviewed.managed.json') 'staged managed source'
    Acceptance = Assert-ChildPath $staged (Join-Path $staged 'recipe_review_acceptance.json') 'acceptance snapshot'
    Report = Assert-ChildPath $staged (Join-Path $staged 'reconciliation_report.json') 'reconciliation report'
    Ownership = Assert-ChildPath $staged (Join-Path $staged 'reviewed_ownership_manifest.json') 'reviewed ownership manifest'
    RawManaged = Assert-ChildPath $project (Join-Path $project 'pack-kjsgen\default.managed.json') 'raw managed source'
    RawManifest = Assert-ChildPath $project (Join-Path $project 'progression\managed_recipe_overhaul.json') 'raw manifest'
    CanonicalReviewedManaged = Assert-ChildPath $project (Join-Path $project 'pack-kjsgen\default.reviewed.managed.json') 'canonical reviewed managed source'
    CanonicalAcceptance = Assert-ChildPath $project (Join-Path $project 'progression\recipe_review_acceptance.json') 'canonical acceptance snapshot'
    CanonicalReport = Assert-ChildPath $project (Join-Path $project 'progression\recipe_review_reconciliation_report.json') 'canonical reconciliation report'
    CanonicalOwnership = Assert-ChildPath $project (Join-Path $project 'progression\reviewed_ownership_manifest.json') 'canonical reviewed ownership manifest'
    PredecessorProject = Assert-ChildPath $predecessor (Join-Path $predecessor 'default.json') 'predecessor project'
    PredecessorApproved = Assert-ChildPath $predecessor (Join-Path $predecessor 'Approved_Recipes.json') 'predecessor approved project'
    PredecessorBaseline = Assert-ChildPath $predecessor (Join-Path $predecessor 'default.managed.baseline.json') 'predecessor baseline'
    PredecessorManaged = Assert-ChildPath $predecessor (Join-Path $predecessor 'default.reviewed.managed.json') 'predecessor managed source'
    BatchManifest = Assert-ChildPath $batchRoot (Join-Path $batchRoot 'batch_manifest.json') 'review batch manifest'
}
foreach ($entry in $paths.GetEnumerator()) {
    if ($entry.Key -eq 'LiveScript') { continue }
    if (-not (Test-Path -LiteralPath $entry.Value -PathType Leaf)) {
        throw "Missing required $($entry.Key): $($entry.Value)"
    }
}

$batchManifest = Get-Content -LiteralPath $paths.BatchManifest -Raw | ConvertFrom-Json
if ($batchManifest.schemaVersion -ne 1 -or $batchManifest.batch -ne '20260902') {
    throw 'The durable review-batch manifest has an unexpected identity or schema.'
}
foreach ($property in $batchManifest.files.PSObject.Properties) {
    $relative = [string] $property.Name
    $expectedHash = ([string] $property.Value) -replace '^sha256:', ''
    if ($expectedHash -notmatch '^[0-9A-Fa-f]{64}$') {
        throw "Invalid pinned SHA-256 for $relative in the review-batch manifest."
    }
    $artifact = Assert-ChildPath $batchRoot (Join-Path $batchRoot $relative) "review batch artifact $relative"
    if (-not (Test-Path -LiteralPath $artifact -PathType Leaf)) {
        throw "Missing review batch artifact: $artifact"
    }
    Assert-Hash $artifact $expectedHash "review batch artifact $relative"
}

$report = Get-Content -LiteralPath $paths.Report -Raw | ConvertFrom-Json
$acceptance = Get-Content -LiteralPath $paths.Acceptance -Raw | ConvertFrom-Json
$stagedProject = Get-Content -LiteralPath $paths.StagedProject -Raw | ConvertFrom-Json
$stagedApproved = Get-Content -LiteralPath $paths.StagedApproved -Raw | ConvertFrom-Json
$stagedBaseline = Get-Content -LiteralPath $paths.StagedBaseline -Raw | ConvertFrom-Json

foreach ($pair in @(
        @($paths.StagedManaged, $paths.CanonicalReviewedManaged, 'reviewed managed source'),
        @($paths.Acceptance, $paths.CanonicalAcceptance, 'acceptance snapshot'),
        @($paths.Report, $paths.CanonicalReport, 'reconciliation report'),
        @($paths.Ownership, $paths.CanonicalOwnership, 'reviewed ownership manifest')
)) {
    if ((Get-Sha256 $pair[0]) -ne (Get-Sha256 $pair[1])) {
        throw "The staged $($pair[2]) is not byte-identical to its canonical source."
    }
}
$acceptanceInputs = $acceptance.inputSha256 | ConvertTo-Json -Depth 20 -Compress
$reportInputs = $report.inputSha256 | ConvertTo-Json -Depth 20 -Compress
if ($acceptanceInputs -ne $reportInputs) {
    throw 'Acceptance and reconciliation report do not pin the same audited inputs.'
}

if ($report.nextManaged -ne 813 -or $report.nextPending -ne 672 -or $report.nextUnmanaged -ne 0 -or $report.nextRemovals -ne 1224) {
    throw 'The staged reconciliation report does not contain the audited 813/672/0/1224 counts.'
}
if ($report.approved -ne 141 -or $report.rejected -ne 240 -or $report.draftsRemoved -ne 6) {
    throw 'The staged reconciliation report no longer matches the completed review ledger.'
}
if ($report.reviewUiCounts.approved -ne 141 -or $report.reviewUiCounts.rejected -ne 0 -or $report.reviewUiCounts.stale -ne 141 -or $report.reviewUiCounts.unreviewed -ne 531) {
    throw 'The staged review-UI counts are not the audited 141 approved / 141 stale / 531 pending state.'
}
if ($report.predecessorRecipeUidsRetired -ne 6 -or $report.predecessorRemovalUidsRetired -ne 6) {
    throw 'The six absent optional slicer cards and removals were not retired from the predecessor batch.'
}
if ($acceptance.reviewed -ne 381 -or $acceptance.approved -ne 141 -or $acceptance.rejected -ne 240 -or $acceptance.entries.Count -ne 381) {
    throw 'The durable acceptance snapshot is incomplete.'
}
if ($stagedProject.recipes.Count -ne 813 -or $stagedProject.removals.Count -ne 1224) {
    throw 'The staged KJSGen project has unexpected recipe/removal counts.'
}
if ($stagedBaseline.recipes.Count -ne 813 -or $stagedBaseline.removals.Count -ne 1224) {
    throw 'The staged baseline has unexpected recipe/removal counts.'
}
if ($stagedApproved.recipes.Count -ne 141 -or $stagedApproved.removals.Count -ne 0) {
    throw 'The staged approved project is not the exact 141-card approval set.'
}
Assert-UniqueField @($stagedProject.recipes) 'uid' 'staged recipes'
Assert-UniqueField @($stagedProject.recipes) 'recipeId' 'staged recipes'
Assert-UniqueField @($stagedProject.removals) 'uid' 'staged removals'
Assert-UniqueField @($stagedProject.removals) 'recipeId' 'staged removals'
if ((Get-Sha256 $paths.StagedBaseline) -ne (Get-Sha256 $paths.StagedManaged)) {
    throw 'The staged baseline and durable reviewed managed source are not byte-identical.'
}
$projectRecipes = $stagedProject.recipes | ConvertTo-Json -Depth 100 -Compress
$baselineRecipes = $stagedBaseline.recipes | ConvertTo-Json -Depth 100 -Compress
$projectRemovals = $stagedProject.removals | ConvertTo-Json -Depth 100 -Compress
$baselineRemovals = $stagedBaseline.removals | ConvertTo-Json -Depth 100 -Compress
if ($projectRecipes -ne $baselineRecipes -or $projectRemovals -ne $baselineRemovals) {
    throw 'The staged project and baseline do not own the same exact cards.'
}

$alreadyDeployed = (
    (Get-Sha256 $paths.LiveProject) -eq (Get-Sha256 $paths.StagedProject) -and
    (Get-Sha256 $paths.LiveApproved) -eq (Get-Sha256 $paths.StagedApproved) -and
    (Get-Sha256 $paths.LiveBaseline) -eq (Get-Sha256 $paths.StagedBaseline)
)
if ($alreadyDeployed) {
    Assert-Hash $paths.LiveReviews $report.inputSha256.reviewLedger 'preserved review ledger'
    Write-Host 'The reconciled review batch is already deployed and hash-identical.' -ForegroundColor Green
    return
}

Assert-Hash $paths.PredecessorManaged $report.inputSha256.previousReviewed 'predecessor reviewed source'
$predecessorMatches = (
    (Get-Sha256 $paths.LiveProject) -eq (Get-Sha256 $paths.PredecessorProject) -and
    (Get-Sha256 $paths.LiveBaseline) -eq (Get-Sha256 $paths.PredecessorBaseline) -and
    (Get-Sha256 $paths.LiveApproved) -eq (Get-Sha256 $paths.PredecessorApproved)
)
$originalInputsMatch = (
    (Get-Sha256 $paths.LiveProject) -eq $report.inputSha256.liveProject -and
    (Get-Sha256 $paths.LiveBaseline) -eq $report.inputSha256.oldBaseline -and
    (Get-Sha256 $paths.LiveApproved) -eq $report.inputSha256.approvedProject
)
if (-not $predecessorMatches -and -not $originalInputsMatch) {
    throw 'Live KJSGen files match neither the original review inputs nor the audited predecessor deployment.'
}
Assert-Hash $paths.LiveReviews $report.inputSha256.reviewLedger 'live review ledger'
Assert-Hash $paths.RawManaged $report.inputSha256.nextManagedSource 'raw managed source'
Assert-Hash $paths.RawManifest $report.inputSha256.nextManifest 'raw recipe manifest'

$javaProcesses = @(Get-Process java, javaw -ErrorAction SilentlyContinue)
if ($javaProcesses.Count -gt 0) {
    throw "Minecraft/Java must be fully closed before deployment. Running process IDs: $($javaProcesses.Id -join ', ')"
}
if ($PlanOnly) {
    Write-Host 'PASS: reconciliation inputs, staged artifacts, target hashes, and closed-game state are safe for deployment.' -ForegroundColor Green
    return
}

$backupRoot = Assert-ChildPath $live (Join-Path $live '_industrial_colonies_backups') 'backup root'
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupDirectory = Assert-ChildPath $backupRoot (Join-Path $backupRoot "review-batch-reconcile-$timestamp") 'backup directory'
New-Item -ItemType Directory -Path $backupDirectory | Out-Null

$backupMap = [ordered]@{
    $paths.LiveProject = Join-Path $backupDirectory 'default.json'
    $paths.LiveApproved = Join-Path $backupDirectory 'Approved_Recipes.json'
    $paths.LiveBaseline = Join-Path $backupDirectory 'default.managed.baseline.json'
    $paths.LiveReviews = Join-Path $backupDirectory 'default.recipe_reviews.json'
}
if (Test-Path -LiteralPath $paths.LiveScript -PathType Leaf) {
    $backupMap[$paths.LiveScript] = Join-Path $backupDirectory 'kjsgen_recipes.js'
}
foreach ($source in $backupMap.Keys) {
    Copy-Item -LiteralPath $source -Destination $backupMap[$source]
    if ((Get-Sha256 $source) -ne (Get-Sha256 $backupMap[$source])) {
        throw "Backup hash mismatch for $source"
    }
}

$backupManifest = [ordered]@{
    createdAt = (Get-Date).ToUniversalTime().ToString('o')
    liveRoot = $live
    files = @($backupMap.Keys | ForEach-Object {
        [ordered]@{ source = $_; backup = $backupMap[$_]; sha256 = Get-Sha256 $_ }
    })
}
$backupManifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $backupDirectory 'backup_manifest.json') -Encoding utf8

$installMap = [ordered]@{
    $paths.StagedBaseline = $paths.LiveBaseline
    $paths.StagedApproved = $paths.LiveApproved
    $paths.StagedProject = $paths.LiveProject
}
try {
    foreach ($source in $installMap.Keys) {
        Install-AtomicFile -Source $source -Destination $installMap[$source]
    }
    if ((Get-Sha256 $paths.LiveBaseline) -ne (Get-Sha256 $paths.StagedBaseline) -or
        (Get-Sha256 $paths.LiveApproved) -ne (Get-Sha256 $paths.StagedApproved) -or
        (Get-Sha256 $paths.LiveProject) -ne (Get-Sha256 $paths.StagedProject)) {
        throw 'Post-deployment hash verification failed.'
    }
    Assert-Hash $paths.LiveReviews $report.inputSha256.reviewLedger 'preserved review ledger'
}
catch {
    foreach ($destination in @($paths.LiveBaseline, $paths.LiveApproved, $paths.LiveProject)) {
        $backup = $backupMap[$destination]
        if (Test-Path -LiteralPath $backup -PathType Leaf) {
            Install-AtomicFile -Source $backup -Destination $destination
        }
    }
    throw
}

Write-Host "Deployed the reconciled 813-card review batch with zero unmanaged cards." -ForegroundColor Green
Write-Host "Backup: $backupDirectory"
