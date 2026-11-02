param(
    [Parameter(Mandatory)][string]$Stage,
    [ValidatePattern('^[a-z0-9-]*$')][string]$Revision = '',
    [string]$OutputPath
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$stagePath = (Resolve-Path -LiteralPath $Stage).Path
$reportSuffix = if ($Revision) { '-' + $Revision } else { '' }
$a = Get-Content -LiteralPath (Join-Path $stagePath "terrain-report-a$reportSuffix.json") -Raw | ConvertFrom-Json
$b = Get-Content -LiteralPath (Join-Path $stagePath "terrain-report-b$reportSuffix.json") -Raw | ConvertFrom-Json
function Require([bool]$Condition, [string]$Message) { if (-not $Condition) { throw $Message } }
function Canonical($Value) { return ConvertTo-Json -InputObject $Value -Depth 32 -Compress }
Require ($a.status -eq 'PASS' -and $b.status -eq 'PASS') 'Both natural-terrain runs must independently pass.'
Require (-not $a.reverseRequests -and $b.reverseRequests) 'Runs must use forward and reverse request order.'
foreach ($field in @('worldSeed','generator','noiseSettingsKey','noiseSettingsSourcePack','minimumBuildHeight','maximumBuildHeight','regionSize','selectedRequestedChunks','selectedFamilies')) {
    Require ($a.$field -ceq $b.$field) "Different terrain/config field: $field"
}
Require ((Canonical $a.configSha256) -ceq (Canonical $b.configSha256)) 'Configuration hashes differ.'
Require ((Canonical $a.selectedPlans) -ceq (Canonical $b.selectedPlans)) 'Selected natural formations differ.'
Require ($a.plans.Count -eq 3 -and $b.plans.Count -eq 3) 'Exactly three completed formation scans are required.'
Require ($a.requestOrder.Count -eq $b.requestOrder.Count -and $a.requestOrder.Count -le 60) 'Request count differs or exceeds cap.'
for ($i=0; $i -lt $a.requestOrder.Count; $i++) {
    $forward=$a.requestOrder[$i]; $backward=$b.requestOrder[$b.requestOrder.Count-1-$i]
    Require ($forward.x -eq $backward.x -and $forward.z -eq $backward.z) "Chunk requests are not exactly reversed at index $i."
}
$comparisons = foreach ($left in $a.plans) {
    $right = @($b.plans | Where-Object { $_.id -eq $left.id -and $_.regionX -eq $left.regionX -and $_.regionZ -eq $left.regionZ })
    Require ($right.Count -eq 1) "No unique counterpart for $($left.id)."
    Require ((Canonical $left) -ceq (Canonical $right[0])) "Formation counts/state hashes/biome metadata differ for $($left.id)."
    [ordered]@{
        id=$left.id; intended=$left.intendedSize; actualHostBeforeRich=$left.actualHostBeforeRich
        finalGeologyCounts=$left.finalGeologyCounts; nonemptyChunks=$left.nonemptyChunks
        retainedCrossChunkNeighborBonds=$left.retainedCrossChunkNeighborBonds
        shapeStateSha256=$left.shapeStateSha256; retainedGeologySha256=$left.retainedGeologySha256
    }
}
$result = [ordered]@{
    status='PASS'; checkedUtc=[DateTime]::UtcNow.ToString('o'); seed=$a.worldSeed
    requestedChunksPerWorld=$a.requestOrder.Count; selectedFamilies=$a.selectedFamilies
    exactReverseOrder=$true; allShapeStatesAndCountsIdentical=$true
    noiseSettingsSourcePack=$a.noiseSettingsSourcePack
    regionsUnexploredActualObserved=($a.regionsUnexploredActualObserved -and $b.regionsUnexploredActualObserved)
    formations=@($comparisons)
    limits='Three bounded selected formations and one seed; not whole-world distribution, client rendering, oil or survival-economy acceptance. Minecraft dependency-halo generation order is not fully controlled.'
}
$json = $result | ConvertTo-Json -Depth 32
if ($OutputPath) {
    $full = [IO.Path]::GetFullPath($OutputPath)
    Require ($full.StartsWith($stagePath + [IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) 'Output must stay within the disposable stage.'
    [IO.File]::WriteAllText($full,$json + [Environment]::NewLine,[Text.UTF8Encoding]::new($false))
}
$json
