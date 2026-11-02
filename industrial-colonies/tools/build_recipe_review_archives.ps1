[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Reviews,
    [Parameter(Mandatory = $true)][string]$DefaultProject,
    [Parameter(Mandatory = $true)][string]$Acceptance,
    [string]$ExistingRejected,
    [string]$ExistingMaybe,
    [string]$ExistingDisabled,
    [Parameter(Mandatory = $true)][string]$OutputRejected,
    [Parameter(Mandatory = $true)][string]$OutputMaybe,
    [string]$OutputDisabled,
    [string]$Report,
    [switch]$Check
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$workspaceRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
Import-Module (Join-Path $PSScriptRoot 'RecipeReviewArchiveBackfill.psm1') -Force

function Resolve-InputPath {
    param([Parameter(Mandatory = $true)][string]$Path, [string]$Label)
    $full = [IO.Path]::GetFullPath($Path)
    if (-not [IO.File]::Exists($full)) {
        throw "$Label does not exist: $full"
    }
    return $full
}

function Resolve-WorkspaceOutput {
    param([Parameter(Mandatory = $true)][string]$Path, [string]$Label)
    $candidate = if ([IO.Path]::IsPathRooted($Path)) {
        [IO.Path]::GetFullPath($Path)
    }
    else {
        [IO.Path]::GetFullPath((Join-Path $workspaceRoot $Path))
    }
    $prefix = $workspaceRoot.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    if (-not $candidate.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "$Label must stay inside the project workspace: $candidate"
    }
    return $candidate
}

function Read-JsonDocument {
    param([Parameter(Mandatory = $true)][string]$Path, [string]$Label)
    try {
        $value = Get-Content -LiteralPath $Path -Raw -Encoding UTF8 |
                ConvertFrom-Json -AsHashtable -Depth 100
    }
    catch {
        throw "cannot read $Label JSON '$Path': $($_.Exception.Message)"
    }
    if ($value -isnot [Collections.IDictionary]) {
        throw "$Label must contain a JSON object"
    }
    return $value
}

function ConvertTo-ArchiveBytes {
    param([Parameter(Mandatory = $true)]$Document)
    $text = ($Document | ConvertTo-Json -Depth 100) + "`n"
    return ,([Text.UTF8Encoding]::new($false).GetBytes($text))
}

function Test-EqualBytes {
    param([byte[]]$First, [byte[]]$Second)
    if ($First.Length -ne $Second.Length) { return $false }
    for ($index = 0; $index -lt $First.Length; $index++) {
        if ($First[$index] -ne $Second[$index]) { return $false }
    }
    return $true
}

function Write-AtomicBytes {
    param([Parameter(Mandatory = $true)][string]$Path, [byte[]]$Bytes)
    $directory = [IO.Path]::GetDirectoryName($Path)
    [IO.Directory]::CreateDirectory($directory) | Out-Null
    $temporary = Join-Path $directory ('.' + [IO.Path]::GetFileName($Path) +
            '.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    try {
        [IO.File]::WriteAllBytes($temporary, $Bytes)
        [IO.File]::Move($temporary, $Path, $true)
    }
    finally {
        if ([IO.File]::Exists($temporary)) {
            [IO.File]::Delete($temporary)
        }
    }
}

$reviewPath = Resolve-InputPath $Reviews 'review ledger'
$defaultPath = Resolve-InputPath $DefaultProject 'current Default project'
$acceptancePath = Resolve-InputPath $Acceptance 'frozen acceptance'
$rejectedOutput = Resolve-WorkspaceOutput $OutputRejected 'Rejected archive output'
$maybeOutput = Resolve-WorkspaceOutput $OutputMaybe 'Deferred archive output'
if ([IO.Path]::GetFileName($rejectedOutput) -cne 'Rejected_Recipes.json') {
    throw 'Rejected archive output filename must be Rejected_Recipes.json'
}
if ([IO.Path]::GetFileName($maybeOutput) -cne 'Deferred.json') {
    throw 'Deferred archive output filename must be Deferred.json'
}
if ($rejectedOutput -ceq $maybeOutput) {
    throw 'Rejected and Deferred archive outputs must be different files'
}
$disabledOutput = if ($OutputDisabled) {
    Resolve-WorkspaceOutput $OutputDisabled 'Disabled archive output'
}
else { $null }
if ($disabledOutput -and
        [IO.Path]::GetFileName($disabledOutput) -cne 'Disabled_Recipes.json') {
    throw 'Disabled archive output filename must be Disabled_Recipes.json'
}
if ($disabledOutput -and $disabledOutput -in @($rejectedOutput, $maybeOutput)) {
    throw 'Disabled archive output must be different from Rejected and Deferred outputs'
}

$rejectedInput = if ($ExistingRejected) {
    Resolve-InputPath $ExistingRejected 'existing Rejected archive'
}
elseif ([IO.File]::Exists($rejectedOutput)) {
    $rejectedOutput
}
else { $null }
$disabledInput = if ($ExistingDisabled) {
    Resolve-InputPath $ExistingDisabled 'existing Disabled archive'
}
elseif ($disabledOutput -and [IO.File]::Exists($disabledOutput)) {
    $disabledOutput
}
else { $null }
$maybeInput = if ($ExistingMaybe) {
    Resolve-InputPath $ExistingMaybe 'existing Deferred archive'
}
elseif ([IO.File]::Exists($maybeOutput)) {
    $maybeOutput
}
else { $null }

$ledger = Read-JsonDocument $reviewPath 'review ledger'
$current = Read-JsonDocument $defaultPath 'current Default project'
$frozen = Read-JsonDocument $acceptancePath 'frozen acceptance'
$existingRejectedDocument = if ($rejectedInput) {
    Read-JsonDocument $rejectedInput 'existing Rejected archive'
}
$existingMaybeDocument = if ($maybeInput) {
    Read-JsonDocument $maybeInput 'existing Deferred archive'
}
$existingDisabledDocument = if ($disabledInput) {
    Read-JsonDocument $disabledInput 'existing Disabled archive'
}

# Resolve every ledger-backed snapshot before opening or replacing any output.
$result = Build-RecipeReviewArchives `
        -Ledger $ledger `
        -CurrentDefault $current `
        -FrozenAcceptance $frozen `
        -ExistingRejected $existingRejectedDocument `
        -ExistingMaybe $existingMaybeDocument `
        -ExistingDisabled $existingDisabledDocument

if ($result.Report.disabled -gt 0 -and -not $disabledOutput) {
    throw 'The ledger contains disabled decisions; specify -OutputDisabled to build Disabled_Recipes.json'
}

$outputs = [ordered]@{
    $rejectedOutput = ConvertTo-ArchiveBytes $result.Rejected
    $maybeOutput = ConvertTo-ArchiveBytes $result.Maybe
}
if ($disabledOutput) {
    $outputs[$disabledOutput] = ConvertTo-ArchiveBytes $result.Disabled
}
$reportOutput = if ($Report) {
    Resolve-WorkspaceOutput $Report 'Backfill report output'
}
else { $null }
if ($reportOutput) {
    $outputs[$reportOutput] = ConvertTo-ArchiveBytes $result.Report
}

if ($Check) {
    $stale = foreach ($item in $outputs.GetEnumerator()) {
        if (-not [IO.File]::Exists($item.Key) -or
                -not (Test-EqualBytes ([IO.File]::ReadAllBytes($item.Key)) $item.Value)) {
            $item.Key
        }
    }
    if ($stale) {
        throw 'Recipe review archives are stale or missing: ' + ($stale -join ', ')
    }
}
else {
    foreach ($item in $outputs.GetEnumerator()) {
        Write-AtomicBytes $item.Key $item.Value
    }
}

Write-Output (
    ("Recipe review archives are current: {0} rejected, {1} deferred, {2} disabled " +
    "(existing rejected {3}, existing deferred {4}, existing disabled {5}, frozen acceptance {6}, current Default {7}).") -f
    $result.Report.rejected,
    $result.Report.maybe,
    $result.Report.disabled,
    $result.Report.sources.existingRejected,
    $result.Report.sources.existingMaybe,
    $result.Report.sources.existingDisabled,
    $result.Report.sources.frozenAcceptance,
    $result.Report.sources.currentDefault
)
