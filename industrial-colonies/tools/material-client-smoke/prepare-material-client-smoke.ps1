[CmdletBinding()]
param(
    [string]$ProjectRoot=(Join-Path $PSScriptRoot '../..'),
    [Parameter(Mandatory=$true)][string]$ServerStage,
    [string]$CandidateJar='',
    [switch]$Stage
)
# Read-only by default. -Stage only creates a NEW physical client copy.
# Never launches Gradle/Java/Minecraft, downloads, connects, copies saves/accounts or alters source stages.
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
Add-Type -AssemblyName System.IO.Compression.FileSystem
$project=[IO.Path]::GetFullPath($ProjectRoot)
$server=(Resolve-Path -LiteralPath $ServerStage).Path
$isolated=[IO.Path]::GetFullPath((Join-Path $project 'isolated-runtime')).TrimEnd('\','/')+[IO.Path]::DirectorySeparatorChar
if(-not $server.StartsWith($isolated,[StringComparison]::OrdinalIgnoreCase)){throw 'ServerStage must be an existing isolated workspace stage'}
if(-not $CandidateJar){
    $versions=@(Get-Content -LiteralPath (Join-Path $project 'gradle.properties')|Where-Object{$_ -match '^mod_version='})
    if($versions.Count -ne 1){throw 'Expected one mod_version or explicit CandidateJar'}
    $version=$versions[0].Substring('mod_version='.Length).Trim()
    if($version -notmatch '^[A-Za-z0-9._+-]+$'){throw 'Unsafe candidate version'}
    $CandidateJar=Join-Path $project ('build/libs/industrial_colonies-'+$version+'.jar')
}
$candidate=(Resolve-Path -LiteralPath $CandidateJar).Path
$candidateHash=(Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash
$groups=@('mods','excluded-server-test-only','excluded-rendering-mods','excluded-gametest-incompatible-mods')
$mods=@(foreach($group in $groups){$folder=Join-Path $server $group;if(Test-Path -LiteralPath $folder){Get-ChildItem -LiteralPath $folder -File -Filter '*.jar'}})
if($mods.Count -ne 241 -or @($mods.Name|Select-Object -Unique).Count -ne 241){throw 'Expected exactly 241 unique physical full-client input JARs after restoring every held server exclusion'}
$owned=@($mods|Where-Object Name -like 'industrial_colonies-*.jar')
if($owned.Count -ne 1 -or $owned[0].Name -ne [IO.Path]::GetFileName($candidate) -or (Get-FileHash -LiteralPath $owned[0].FullName -Algorithm SHA256).Hash -ne $candidateHash){throw 'Prepared server stage must contain the exact current candidate'}
foreach($required in @('lithosphere 1.6 17.06.2025 (1.20.5 - 1.21.5).jar','wwoo-neoforge-2.6.7.jar','cristellib-neoforge-1.21.1-3.1.7.jar')){if($required -notin $mods.Name){throw "Current full pack is missing $required"}}
if(@($mods|Where-Object Name -like 'tectonic-*').Count){throw 'Unexpected stale Tectonic input; no automatic mod removal is permitted'}
$held=@($mods|Where-Object{$_.Directory.Name -ne 'mods'})
$approvedHeld=@('sodium-neoforge-0.8.13+mc1.21.1.jar','iris-neoforge-1.8.14-beta.1+mc1.21.1.jar','entity_texture_features_1.21-neoforge-7.1.jar','entity_model_features-3.2.4-1.21-neoforge.jar','EuphoriaPatcher-1.9.3-r5.8.1-neoforge.jar','DistantHorizons-3.2.0-b-1.21.1-fabric-neoforge.jar')
if($held.Count -notin @(0,6) -or @($held|Where-Object{$_.Name -notin $approvedHeld}).Count){throw 'Unexpected held-mod set; re-audit rather than silently changing the full roster'}
$content=Join-Path $project 'src/main/resources/data/industrial_colonies/processing/content.json'
$catalog=Join-Path $project 'processing/material_processing_catalog.json'
$contentData=Get-Content -LiteralPath $content -Raw|ConvertFrom-Json -AsHashtable
if($contentData.items.Count -ne 74 -or $contentData.fluids.Count -ne 25){throw 'Expected 74 material items and 25 tank-only fluids; update the coverage contract deliberately if scope changed'}
$contentHash=(Get-FileHash -LiteralPath $content -Algorithm SHA256).Hash
$catalogHash=(Get-FileHash -LiteralPath $catalog -Algorithm SHA256).Hash
$initialOptions='onboardAccessibility:false'+[char]10
$initialOptionsHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($initialOptions)))
$patchPath=Join-Path $server 'material-stage-patch.json'
if(-not(Test-Path -LiteralPath $patchPath -PathType Leaf)){throw 'Apply and verify the scoped material stage patch before preparing the client copy'}
$patch=Get-Content -LiteralPath $patchPath -Raw|ConvertFrom-Json
if($patch.catalogSha256 -ne $catalogHash -or $patch.newProjectSha256 -ne (Get-FileHash -LiteralPath (Join-Path $server 'kjsgen/projects/default.json') -Algorithm SHA256).Hash -or $patch.scriptSha256 -ne (Get-FileHash -LiteralPath (Join-Path $server 'kubejs/server_scripts/zz_industrial_material_processing.js') -Algorithm SHA256).Hash){throw 'Material stage patch identities differ from the current staged project/script/source catalog'}
$zip=[IO.Compression.ZipFile]::OpenRead($candidate)
try {
    foreach($name in @('dev/godpc/industrialcolonies/processing/ProcessingContent.class','dev/godpc/industrialcolonies/mixin/ProcessingRadianceConversionMixin.class','data/industrial_colonies/processing/content.json','industrial_colonies.mixins.json')){if(-not $zip.GetEntry($name)){throw "Candidate lacks $name"}}
    $reader=[IO.StreamReader]::new($zip.GetEntry('industrial_colonies.mixins.json').Open())
    try {$mixinConfig=$reader.ReadToEnd()|ConvertFrom-Json}finally{$reader.Dispose()}
    if('ProcessingRadianceConversionMixin' -notin $mixinConfig.mixins){throw 'Radiance conversion mixin is not in the common runtime configuration'}
    $stream=$zip.GetEntry('data/industrial_colonies/processing/content.json').Open();$buffer=[IO.MemoryStream]::new()
    try {$stream.CopyTo($buffer);$bundledHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($buffer.ToArray()))}finally{$stream.Dispose();$buffer.Dispose()}
    if($bundledHash -ne $contentHash){throw 'Candidate content manifest is stale relative to current source'}
    if(@($zip.Entries.FullName|Where-Object{$_ -match '(^|/)(clientcheck|materialclientcheck|materialcheck|oilcheck|terraincheck)/'}).Count){throw 'A development-only smoke addon leaked into the candidate'}
}finally{$zip.Dispose()}
$userdev=[IO.Path]::GetFullPath((Join-Path $project '../gradle-user-home/caches/modules-2/files-2.1/net.neoforged/neoforge/21.1.248/dab61062b17c39eb246328576ae1bcbd59ee780b/neoforge-21.1.248-userdev.jar'))
if((Get-FileHash -LiteralPath $userdev -Algorithm SHA1).Hash -ne 'DAB61062B17C39EB246328576AE1BCBD59EE780B'){throw 'Unexpected NeoForge userdev metadata'}
$devHashes=@{jar='366ADC4E95AB9B32C8E33B9F449529C8937C6FC021EE0C6B25419EA2BB703740';pom='49BA05392F1BF4A513DA8CE72377230EEC261B6E13A019B6DF526DD22D2CBC30';module='30A811979EC04FCCBD1F78D4B1C387913ACD08C52EBD0C97F87DB08B0E61FDDC'}
foreach($ext in $devHashes.Keys){if((Get-FileHash -LiteralPath (Join-Path $server ('offline-maven/net/neoforged/DevLaunch/1.0.2/DevLaunch-1.0.2.'+$ext)) -Algorithm SHA256).Hash -ne $devHashes[$ext]){throw 'DevLaunch is not the previously verified official artifact'}}
$assets=ConvertFrom-StringData (Get-Content -LiteralPath (Join-Path $server 'offline-assets.properties') -Raw)
$index=Get-Content -LiteralPath (Join-Path $assets.assets_root ('indexes/'+$assets.asset_index+'.json')) -Raw|ConvertFrom-Json -AsHashtable
foreach($value in $index.objects.Values){$file=Join-Path $assets.assets_root ('objects/'+$value.hash.Substring(0,2)+'/'+$value.hash);if(-not [IO.File]::Exists($file) -or ([IO.FileInfo]::new($file)).Length -ne $value.size){throw "Missing or size-mismatched installed asset (no downloads): $file"}}
$destination=Join-Path $project ('isolated-runtime/material-client-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$plan=[ordered]@{mode=if($Stage){'stage_only'}else{'read_only_plan'};sourceStage=$server;destination=$destination;candidateFileName=[IO.Path]::GetFileName($candidate);candidateSha256=$candidateHash;sourceContent=$content;contentSha256=$contentHash;sourceCatalog=$catalog;catalogSha256=$catalogHash;stagedJarCount=241;restoredHeldJars=@($held.Name);materialItems=74;tankFluids=25;geologyBlocks=41;expectedGeologyQuads=258;assetsPresentWithExpectedSize=$index.objects.Count;noLaunch=$true;noSavesOrAccountsCopied=$true;noLiveOrPriorStageWrites=$true;network='No download. Later full-client launch requires approved execution; Gradle --offline is not a runtime firewall.'}
$plan['materialStagePatchSha256']=(Get-FileHash -LiteralPath $patchPath -Algorithm SHA256).Hash
$plan['mergedProjectSha256']=$patch.newProjectSha256
$plan['initialOptions']=[ordered]@{file='options.txt';content=$initialOptions;sha256=$initialOptionsHash;purpose='Skip only native first-launch accessibility orientation in this new disposable profile';otherOptions='Unspecified; native defaults. No live options copied and no authentication/privacy preferences changed.';verifiedMinecraftSha256='BC811B3368CA4E056672AB7425682247A68AB72210F14B0BA68B91EEAE040CE3'}
if(-not $Stage){$plan|ConvertTo-Json -Depth 8;return}
$destination=[IO.Path]::GetFullPath($destination)
if(-not $destination.StartsWith($isolated,[StringComparison]::OrdinalIgnoreCase) -or (Test-Path -LiteralPath $destination)){throw 'Destination must be a NEW isolated workspace directory'}
[void][IO.Directory]::CreateDirectory((Join-Path $destination 'mods'))
$manifest=[Collections.Generic.List[object]]::new()
foreach($mod in $mods){
    if(($mod.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw 'Refusing a linked mod input'}
    $target=Join-Path $destination ('mods/'+$mod.Name);$hash=(Get-FileHash -LiteralPath $mod.FullName -Algorithm SHA256).Hash
    Copy-Item -LiteralPath $mod.FullName -Destination $target
    if((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $hash){throw "Mod copy hash mismatch: $($mod.Name)"}
    $manifest.Add([ordered]@{name=$mod.Name;source=$mod.FullName;sha256=$hash;bytes=$mod.Length;restoredHeld=($mod.Directory.Name -ne 'mods')})
}
foreach($folder in @('config','defaultconfigs','kubejs','kjsgen','data','datapacks','moonlight-global-datapacks','offline-maven')){
    $source=Join-Path $server $folder;if(-not(Test-Path -LiteralPath $source)){continue}
    $prefix=[IO.Path]::GetFullPath($source).TrimEnd('\','/')+[IO.Path]::DirectorySeparatorChar
    foreach($entry in Get-ChildItem -LiteralPath $source -Recurse -Force){
        if(($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw "Refusing linked stage input: $($entry.FullName)"}
        if($entry.PSIsContainer){continue}
        if($entry.Name -in @('launcher_accounts.json','accounts.json','usercache.json','servers.dat','options.txt')){continue}
        $target=Join-Path (Join-Path $destination $folder) $entry.FullName.Substring($prefix.Length)
        [void][IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($target));Copy-Item -LiteralPath $entry.FullName -Destination $target
    }
}
Copy-Item -LiteralPath (Join-Path $server 'offline-assets.properties') -Destination (Join-Path $destination 'offline-assets.properties')
[void][IO.Directory]::CreateDirectory((Join-Path $destination 'material-client-inputs'))
Copy-Item -LiteralPath $content -Destination (Join-Path $destination 'material-client-inputs/content.json')
Copy-Item -LiteralPath $catalog -Destination (Join-Path $destination 'material-client-inputs/catalog.json')
if((Get-FileHash -LiteralPath (Join-Path $destination 'material-client-inputs/content.json') -Algorithm SHA256).Hash -ne $contentHash -or (Get-FileHash -LiteralPath (Join-Path $destination 'material-client-inputs/catalog.json') -Algorithm SHA256).Hash -ne $catalogHash){throw 'Source manifest copy mismatch'}
$utf8=[Text.UTF8Encoding]::new($false)
$optionsPath=Join-Path $destination 'options.txt'
if(Test-Path -LiteralPath $optionsPath){throw 'Refusing to replace existing profile options'}
[IO.File]::WriteAllText($optionsPath,$initialOptions,$utf8)
if((Get-FileHash -LiteralPath $optionsPath -Algorithm SHA256).Hash -ne $initialOptionsHash){throw 'Initial orientation-only options seed differs from its manifest'}
$template=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'material-client-smoke.init.gradle.template') -Raw
$init=$template.Replace('@STAGE@',$destination.Replace('\','/').Replace("'","\'")).Replace('@USERDEV@',$userdev.Replace('\','/').Replace("'","\'"))
$initPath=Join-Path $destination 'material-client-smoke.init.gradle'
[IO.File]::WriteAllText($initPath,$init,$utf8)
$plan['mods']=@($manifest);$plan['initScript']=$initPath
$command='.\gradlew.bat --offline --no-daemon --no-configuration-cache --console=plain -I "'+$initPath+'"'
$plan['prepareCommandNotExecuted']=$command+' compileMaterialClientSmokeJava processMaterialClientSmokeResources prepareClientRun auditMaterialClientSmokeDependencies'
$plan['launchCommandNotExecuted']=$command+' runClient'
[IO.File]::WriteAllText((Join-Path $destination 'material-client-preparation.json'),($plan|ConvertTo-Json -Depth 8)+[Environment]::NewLine,$utf8)
[pscustomobject]$plan|Select-Object * -ExcludeProperty mods|ConvertTo-Json -Depth 8
