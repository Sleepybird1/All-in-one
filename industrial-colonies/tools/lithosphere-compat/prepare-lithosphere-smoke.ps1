[CmdletBinding()]
param(
    [string]$ProjectRoot=(Join-Path $PSScriptRoot '../..'),
    [string]$PackRoot='C:\Users\GodPC\curseforge\minecraft\Instances\All in one',
    [string]$CandidateJar='',
    [switch]$ServerCompatibleSubset,
    [switch]$Stage
)
# Default is read-only. -Stage creates a NEW physical copy using the established
# offline preparator. Never invokes Gradle/Java/Minecraft or changes live configuration.
$ErrorActionPreference='Stop'
$project=[IO.Path]::GetFullPath($ProjectRoot)
$pack=[IO.Path]::GetFullPath($PackRoot)
if(-not $CandidateJar){
    $versionLine=@(Get-Content -LiteralPath (Join-Path $project 'gradle.properties')|Where-Object {$_ -match '^mod_version='})
    if($versionLine.Count -ne 1){throw 'Supply -CandidateJar or define exactly one mod_version in gradle.properties'}
    $version=$versionLine[0].Substring('mod_version='.Length).Trim()
    if($version -notmatch '^[A-Za-z0-9._+-]+$'){throw 'Unsafe mod_version; supply an explicit -CandidateJar'}
    $CandidateJar=Join-Path $project ('build/libs/industrial_colonies-'+$version+'.jar')
}
$candidate=[IO.Path]::GetFullPath($CandidateJar)
Add-Type -AssemblyName System.IO.Compression.FileSystem
$required=@('lithosphere 1.6 17.06.2025 (1.20.5 - 1.21.5).jar','wwoo-neoforge-2.6.7.jar','cristellib-neoforge-1.21.1-3.1.7.jar','regions-unexplored-0.6.2-neoforge-21.1.jar')
$sourceMods=@(Get-ChildItem -LiteralPath (Join-Path $pack 'mods') -File -Filter '*.jar')
foreach($name in $required){if($name -notin $sourceMods.Name){throw "Required compatibility artifact absent: $name"}}
if(@($sourceMods|Where-Object Name -like 'tectonic-*').Count){throw 'Remove the Tectonic/Lithosphere ambiguity before preparing this test; no mod is removed automatically'}
$wwooConfig=Get-Content -Raw -LiteralPath (Join-Path $pack 'config/wwoo/config.json5')
if($wwooConfig -notmatch '"removeOres"\s*:\s*true'){throw 'This exact compatibility test expects the audited WWOO removeOres=true input; never changes it automatically'}
$lithosphere=Join-Path $pack ('mods/'+$required[0])
$zip=[IO.Compression.ZipFile]::OpenRead($lithosphere)
try{
    $entry=$zip.GetEntry('data/minecraft/worldgen/noise_settings/overworld.json')
    if(-not $entry){throw 'Installed Lithosphere lacks expected vanilla-key noise settings'}
    $stream=$entry.Open();$buffer=[IO.MemoryStream]::new()
    try{$stream.CopyTo($buffer);$noiseBytes=$buffer.ToArray()}finally{$stream.Dispose();$buffer.Dispose()}
    $noiseHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($noiseBytes))
    $noise=[Text.Encoding]::UTF8.GetString($noiseBytes)|ConvertFrom-Json
    if($noise.noise.min_y -ne -64 -or $noise.noise.height -ne 576 -or $noise.default_block.Name -ne 'minecraft:stone'){throw 'Installed Lithosphere contract changed; re-audit before tests'}
}finally{$zip.Dispose()}
$zip=[IO.Compression.ZipFile]::OpenRead($candidate)
try{
    $ready=$null -ne $zip.GetEntry('data/industrial_colonies/tags/worldgen/placed_feature/geology/wwoo.json') -and $null -ne $zip.GetEntry('resourcepacks/ic_wwoo_decorative/source_manifest.json') -and $null -ne $zip.GetEntry('dev/godpc/industrialcolonies/geology/GeologyCompatibilityPacks.class')
}finally{$zip.Dispose()}
if($Stage -and -not $ready){throw 'Build the compatibility candidate first; refusing to stage an old candidate'}
$baseArguments=@{ProjectRoot=$project;PackRoot=$pack;CandidateJar=$candidate}
if($Stage){$baseArguments.Stage=$true}
$baseOutput=& (Join-Path $project 'tools/prepare_geology_gametest.ps1') @baseArguments
$base=($baseOutput -join [Environment]::NewLine)|ConvertFrom-Json
$result=[ordered]@{
    kind='lithosphere_wwoo_compatibility';mode=if($Stage){'stage_only'}else{'read_only_plan'}
    sourcePack=$pack;destination=$base.destination;candidateSha256=$base.candidateSha256;candidateFileName=[IO.Path]::GetFileName($candidate);candidateContainsCompatibility=$ready
    installedJarCount=$sourceMods.Count;noiseSourceJar=$required[0];noiseSourceSha256=(Get-FileHash -LiteralPath $lithosphere -Algorithm SHA256).Hash
    expectedNoiseSha256=$noiseHash;expectedMinY=-64;expectedHeight=576
    wwooConfigUnchanged=$true;removeOres=$true;decorativeRestoration='Conditional required candidate builtin pack, exactly 12 original decorative resources; lava untouched'
    requestedServerSubset=[bool]$ServerCompatibleSubset;noLaunch=$true;noLiveWrites=$true;noPriorStageWrites=$true
}
if($Stage){
    $stagePath=[IO.Path]::GetFullPath($base.destination)
    $allowed=[IO.Path]::GetFullPath((Join-Path $project 'isolated-runtime')).TrimEnd('\','/')+[IO.Path]::DirectorySeparatorChar
    if(-not $stagePath.StartsWith($allowed,[StringComparison]::OrdinalIgnoreCase)){throw 'Stage escaped workspace'}
    $held=@()
    if($ServerCompatibleSubset){
        # Same six independently diagnosed exclusions previously authorized for server GameTests.
        # Keep every copied artifact recoverable; no gameplay mod other than the approved DH exception.
        $names=@('sodium-neoforge-0.8.13+mc1.21.1.jar','iris-neoforge-1.8.14-beta.1+mc1.21.1.jar','entity_texture_features_1.21-neoforge-7.1.jar','entity_model_features-3.2.4-1.21-neoforge.jar','EuphoriaPatcher-1.9.3-r5.8.1-neoforge.jar','DistantHorizons-3.2.0-b-1.21.1-fabric-neoforge.jar')
        $known=Get-Content -Raw -LiteralPath (Join-Path $project 'isolated-runtime/client-render-20260909-030821-140/client-preparation.json')|ConvertFrom-Json
        $hold=Join-Path $stagePath 'excluded-server-test-only';[void][IO.Directory]::CreateDirectory($hold)
        foreach($name in $names){
            $source=[IO.Path]::GetFullPath((Join-Path $stagePath ('mods/'+$name)))
            $target=[IO.Path]::GetFullPath((Join-Path $hold $name))
            if(-not $source.StartsWith($stagePath+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase) -or -not $target.StartsWith($stagePath+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Exclusion target escaped fresh stage'}
            $prior=@($known.mods|Where-Object name -eq $name)
            if($prior.Count -ne 1 -or (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne $prior[0].sha256){throw "Previously approved server-incompatible artifact changed: $name"}
            Move-Item -LiteralPath $source -Destination $target
            $held+=[ordered]@{name=$name;sha256=$prior[0].sha256;location=('excluded-server-test-only/'+$name);reason=if($name -like 'DistantHorizons*'){'Previously approved dual-side GameTestServer cast incompatibility'}else{'Previously approved client rendering-only server incompatibility'}}
        }
    }
    $result['heldServerIncompatible']=$held
    $result['activeMods']=@(Get-ChildItem -LiteralPath (Join-Path $stagePath 'mods') -File -Filter '*.jar'|ForEach-Object {[ordered]@{name=$_.Name;bytes=$_.Length;sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash}})
    $result['activeJarCount']=$result.activeMods.Count
    $targetConfig=Join-Path $stagePath 'config/wwoo/config.json5'
    if((Get-FileHash -Algorithm SHA256 -LiteralPath $targetConfig).Hash -ne (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $pack 'config/wwoo/config.json5')).Hash){throw 'Staged WWOO config is not byte-identical'}
    $result['wwooConfigSha256']=(Get-FileHash -Algorithm SHA256 -LiteralPath $targetConfig).Hash
    $baseCommand='.\gradlew.bat --offline --no-configuration-cache --console=plain -I "'+(Join-Path $stagePath 'geology-smoke.init.gradle')+'" -I tools/lithosphere-compat/lithosphere-smoke.init.gradle -PcompatStage="'+$stagePath+'"'
    $result['commandsNotExecuted']=@(($baseCommand+' -PterrainOrder=a -PcompatRevision=r1 runGameTestServer'),($baseCommand+' -PterrainOrder=b -PcompatRevision=r1 runGameTestServer'))
    [IO.File]::WriteAllText((Join-Path $stagePath 'lithosphere-preparation.json'),($result|ConvertTo-Json -Depth 7)+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
}
$result|ConvertTo-Json -Depth 7
