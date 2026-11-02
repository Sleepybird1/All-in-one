[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Stage,
    [Parameter(Mandatory)][ValidatePattern('^[a-z0-9][a-z0-9-]*$')][string]$Revision,
    [string]$CandidateJar='',
    [string]$OutputPath=''
)
# Current scoped acceptance only. Historical comparator and reports remain untouched.
# No launch, downloads, source changes or live-pack reads/writes. Read-only unless OutputPath is supplied.
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
Add-Type -AssemblyName System.IO.Compression.FileSystem
$script:checks=0
function Require([bool]$Condition,[string]$Message) {
    $script:checks++
    if(-not $Condition){throw $Message}
}
function ReadJson([string]$Path) { Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json }
function Hash([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash }
function ZipBytes($Zip,[string]$Name) {
    $entry=$Zip.GetEntry($Name)
    Require ($null -ne $entry) "Missing archived resource: $Name"
    $stream=$entry.Open();$buffer=[IO.MemoryStream]::new()
    try {$stream.CopyTo($buffer);return ,$buffer.ToArray()}finally{$stream.Dispose();$buffer.Dispose()}
}
$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$stagePath=(Resolve-Path -LiteralPath $Stage).Path.TrimEnd('\','/')
$isolated=[IO.Path]::GetFullPath((Join-Path $project 'isolated-runtime')).TrimEnd('\','/')+[IO.Path]::DirectorySeparatorChar
Require ($stagePath.StartsWith($isolated,[StringComparison]::OrdinalIgnoreCase)) 'Only a current isolated workspace stage may be validated.'
$metadataPath=Join-Path $stagePath 'lithosphere-preparation.json'
$basePath=Join-Path $stagePath 'preparation.json'
$metadata=ReadJson $metadataPath;$base=ReadJson $basePath
Require ($metadata.kind -eq 'lithosphere_wwoo_compatibility' -and $metadata.candidateContainsCompatibility) 'Stage was not prepared for current Lithosphere compatibility.'
Require ($metadata.requestedServerSubset -and $metadata.installedJarCount -eq 241 -and $metadata.activeJarCount -eq 235) 'Expected current 241-input/235-active isolated server contract.'
Require ($metadata.candidateFileName -cmatch '^industrial_colonies-[A-Za-z0-9._+-]+\.jar$') 'Unsafe candidate filename.'
Require ($metadata.candidateSha256 -eq $base.candidateSha256) 'Base and Lithosphere candidate preparation identities disagree.'
Require ($metadata.expectedMinY -eq -64 -and $metadata.expectedHeight -eq 576) 'Current Lithosphere height contract changed.'
$candidate=Join-Path $stagePath ('mods/'+$metadata.candidateFileName)
$stagedHash=Hash $candidate
Require ($stagedHash -eq $metadata.candidateSha256) 'Staged candidate differs from launch-guard preparation identity.'
if(-not $CandidateJar){$CandidateJar=$base.candidate}
$source=(Resolve-Path -LiteralPath $CandidateJar).Path
$sourceHash=Hash $source
Require ($sourceHash -eq $stagedHash) 'Source/delivery candidate differs from the staged acceptance candidate; do not relabel historical evidence.'
Require (@(Get-ChildItem -LiteralPath (Join-Path $stagePath 'mods') -File -Filter 'industrial_colonies-*.jar').Count -eq 1) 'Multiple production candidates are present.'
Require (@(Get-ChildItem -LiteralPath (Join-Path $stagePath 'mods') -File -Filter 'tectonic-*.jar').Count -eq 0) 'Tectonic is present in a Lithosphere acceptance stage.'
Require ([IO.Path]::GetFileName($metadata.noiseSourceJar) -ceq $metadata.noiseSourceJar) 'Unsafe noise source filename.'
$noiseJar=Join-Path $stagePath ('mods/'+$metadata.noiseSourceJar)
Require ((Hash $noiseJar) -eq $metadata.noiseSourceSha256) 'Staged Lithosphere JAR differs from its prepared source.'
$zip=[IO.Compression.ZipFile]::OpenRead($noiseJar)
try {
    $noiseBytes=ZipBytes $zip 'data/minecraft/worldgen/noise_settings/overworld.json'
    $noiseHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($noiseBytes))
    Require ($noiseHash -eq $metadata.expectedNoiseSha256) 'Prepared noise SHA differs from the actual staged Lithosphere resource.'
}finally{$zip.Dispose()}

# Preserve every historical comparison criterion. No OutputPath means this invocation writes nothing.
$comparisonText=& (Join-Path $project 'tools/terrain-smoke/compare-terrain-reports.ps1') -Stage $stagePath -Revision ('lithosphere-'+$Revision)
$comparison=($comparisonText -join [Environment]::NewLine)|ConvertFrom-Json
Require ($comparison.status -eq 'PASS') 'Generic natural A/B comparison did not pass.'
$evidence=@()
foreach($order in @('a','b')) {
    $terrainPath=Join-Path $stagePath ('terrain-report-'+$order+'-lithosphere-'+$Revision+'.json')
    $compatPath=Join-Path $stagePath ('compatibility-report-'+$order+'-lithosphere-'+$Revision+'.json')
    $terrain=ReadJson $terrainPath;$compat=ReadJson $compatPath
    Require ($terrain.status -eq 'PASS' -and $compat.status -eq 'PASS') "Order $order lacks passing terrain and native compatibility reports."
    Require ($terrain.expectedTerrainMod -ceq 'mr_lithosphere') "Order $order is not actual Lithosphere evidence."
    Require ($terrain.noiseSettingsKey -ceq 'minecraft:overworld') "Order $order used another noise-settings key."
    Require ($terrain.noiseSettingsSourcePack -match '(?i)lithosphere') "Order $order did not load Lithosphere's effective noise resource."
    Require ($terrain.noiseSettingsSha256 -eq $noiseHash) "Order $order effective noise SHA differs from staged/prepared Lithosphere."
    Require ($terrain.minimumBuildHeight -eq $metadata.expectedMinY -and $terrain.maximumBuildHeight -eq ($metadata.expectedMinY+$metadata.expectedHeight)) "Order $order terrain heights differ from preparation."
    Require ($compat.minimumBuildHeight -eq $metadata.expectedMinY -and $compat.maximumBuildHeight -eq ($metadata.expectedMinY+$metadata.expectedHeight)) "Order $order compatibility heights differ from preparation."
    Require ($compat.economicFeaturesChecked -eq 5 -and $compat.directGuardCalls -eq 10 -and $compat.overworldBiomesInspected -gt 0) "Order $order lacks complete native WWOO guard/biome-removal checks."
    Require ($compat.lavaFeatureRetained -and $compat.wwooLavaSpringPolicyPreserved) "Order $order changed preserved lava policy."
    Require ($compat.paleGardenFamily -ceq 'ordinary_forest') "Order $order changed the Pale Garden mapping."
    Require ($compat.decorativeResourcePriority.Count -eq 12) "Order $order did not check all 12 decorative resources."
    $evidence += [ordered]@{order=$order;terrainReport=$terrainPath;terrainReportSha256=(Hash $terrainPath);compatibilityReport=$compatPath;compatibilityReportSha256=(Hash $compatPath);noiseSettingsSha256=$terrain.noiseSettingsSha256;overworldBiomesInspected=$compat.overworldBiomesInspected}
}
$result=[ordered]@{
    status='PASS';checkedUtc=[DateTime]::UtcNow.ToString('o');wrapperAssertions=$script:checks
    stage=$stagePath;revision=$Revision;candidate=$candidate;candidateSha256=$stagedHash
    sourceCandidate=$source;sourceCandidateSha256=$sourceHash
    preparationSha256=(Hash $metadataPath);basePreparationSha256=(Hash $basePath)
    expectedTerrainMod='mr_lithosphere';minimumBuildHeight=-64;maximumBuildHeight=512
    noiseSettingsSha256=$noiseHash;reports=$evidence;nativeABComparison=$comparison
    identityScope='Current source/staged bytes agree with launch-guard preparation; terrain reports do not embed a candidate hash. Preserve matching launch logs and preparation provenance.'
    limits='Three bounded formations, reversed direct requests, native WWOO compatibility; not world-wide frequencies, manual processing, powered factories, full-client rendering or completed placer selection.'
}
$json=$result|ConvertTo-Json -Depth 40
if($OutputPath){
    $output=[IO.Path]::GetFullPath($OutputPath)
    Require ($output.StartsWith($stagePath+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) 'Output must remain inside the disposable stage.'
    Require (-not(Test-Path -LiteralPath $output)) 'Refusing to overwrite acceptance evidence.'
    [IO.File]::WriteAllText($output,$json+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
}
$json
