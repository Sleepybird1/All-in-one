[CmdletBinding()]
param(
    [string]$ProjectRoot=(Join-Path $PSScriptRoot '../..'),
    [string]$ServerStage='',
    [switch]$Stage
)
# Preparation only. No launch, network, accounts, existing worlds, or live-pack writes.
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$project=[IO.Path]::GetFullPath($ProjectRoot)
if (-not $ServerStage) {$ServerStage=Join-Path $project 'isolated-runtime/geology-gametest-20260909-001051-895'}
$server=(Resolve-Path -LiteralPath $ServerStage).Path
$allowed=[IO.Path]::GetFullPath((Join-Path $project 'isolated-runtime')).TrimEnd('\','/')+[IO.Path]::DirectorySeparatorChar
if (-not $server.StartsWith($allowed,[StringComparison]::OrdinalIgnoreCase)) {throw 'Source must be the isolated workspace stage'}
$candidate=Join-Path $server 'mods/industrial_colonies-0.4.0.jar'
$expectedCandidate='ABC9A4D5D168639A0E96A9D0FEBC6BFA8012CF46A0DC2C9C2DCBBE91DBD56546'
if ((Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash -ne $expectedCandidate) {throw 'Unexpected corrected candidate hash'}
$userdev=[IO.Path]::GetFullPath((Join-Path $project '../gradle-user-home/caches/modules-2/files-2.1/net.neoforged/neoforge/21.1.248/dab61062b17c39eb246328576ae1bcbd59ee780b/neoforge-21.1.248-userdev.jar'))
if ((Get-FileHash -LiteralPath $userdev -Algorithm SHA1).Hash -ne 'DAB61062B17C39EB246328576AE1BCBD59EE780B') {throw 'Wrong cached original userdev metadata'}
$groups=@('mods','excluded-rendering-mods','excluded-gametest-incompatible-mods')
$mods=@(foreach($group in $groups){Get-ChildItem -LiteralPath (Join-Path $server $group) -File -Filter '*.jar'})
if ($mods.Count -ne 239 -or @($mods.Name | Select-Object -Unique).Count -ne 239) {throw 'Expected exactly 239 unique original/candidate JARs after restoring held originals'}
$held=@($mods|Where-Object{$_.Directory.Name -ne 'mods'})
if ($held.Count -ne 6) {throw 'Expected the exact six held rendering/GameTest-incompatible JARs'}
$hashes=[ordered]@{
    jar='366ADC4E95AB9B32C8E33B9F449529C8937C6FC021EE0C6B25419EA2BB703740'
    pom='49BA05392F1BF4A513DA8CE72377230EEC261B6E13A019B6DF526DD22D2CBC30'
    module='30A811979EC04FCCBD1F78D4B1C387913ACD08C52EBD0C97F87DB08B0E61FDDC'
}
foreach($extension in $hashes.Keys){
    $path=Join-Path $server ('offline-maven/net/neoforged/DevLaunch/1.0.2/DevLaunch-1.0.2.'+$extension)
    if((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ne $hashes[$extension]){throw 'DevLaunch differs from approved official acquisition'}
}
$assetProperties=Get-Content -Raw -LiteralPath (Join-Path $server 'offline-assets.properties')
$assetPropertiesMap=ConvertFrom-StringData $assetProperties
$indexFile=Join-Path $assetPropertiesMap.assets_root ('indexes/'+$assetPropertiesMap.asset_index+'.json')
$index=Get-Content -Raw -LiteralPath $indexFile | ConvertFrom-Json -AsHashtable
foreach($value in $index.objects.Values){
    $asset=Join-Path $assetPropertiesMap.assets_root ('objects/'+$value.hash.Substring(0,2)+'/'+$value.hash)
    if(-not [IO.File]::Exists($asset) -or ([IO.FileInfo]::new($asset)).Length -ne $value.size){throw "Missing/corrupt installed asset; no download permitted: $asset"}
}
$folders=@('config','defaultconfigs','kubejs','kjsgen','data','datapacks','moonlight-global-datapacks','offline-maven')
$destination=Join-Path $project ('isolated-runtime/client-render-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$plan=[ordered]@{
    mode=if($Stage){'stage_only'}else{'read_only_plan'}
    sourceStage=$server; destination=$destination; candidateSha256=$expectedCandidate
    restoredHeldJars=@($held.Name); stagedJarCount=239
    assetsRoot=$assetPropertiesMap.assets_root; assetIndex=$assetPropertiesMap.asset_index
    assetsPresentWithExpectedSize=$index.objects.Count; userdevJar=$userdev
    noLaunch=$true; noAccountsOrSavesCopied=$true; noServerStageOrLiveWrites=$true
    network='No downloads. Gradle --offline is not a runtime firewall; any later full-client launch requires its own approved execution controls.'
}
if(-not $Stage){$plan|ConvertTo-Json -Depth 8;return}
$destination=[IO.Path]::GetFullPath($destination)
if(-not $destination.StartsWith($allowed,[StringComparison]::OrdinalIgnoreCase) -or (Test-Path -LiteralPath $destination)){throw 'Destination must be a new isolated workspace directory'}
[void][IO.Directory]::CreateDirectory((Join-Path $destination 'mods'))
$manifest=[Collections.Generic.List[object]]::new()
foreach($mod in $mods){
    $target=Join-Path $destination ('mods/'+$mod.Name)
    $hash=(Get-FileHash -LiteralPath $mod.FullName -Algorithm SHA256).Hash
    Copy-Item -LiteralPath $mod.FullName -Destination $target
    if((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $hash){throw "Copy hash mismatch: $($mod.Name)"}
    $manifest.Add([ordered]@{name=$mod.Name;source=$mod.FullName;sha256=$hash;bytes=$mod.Length;restoredHeld=($mod.Directory.Name -ne 'mods')})
}
foreach($folder in $folders){
    $source=Join-Path $server $folder
    if(-not(Test-Path -LiteralPath $source)){continue}
    $prefix=[IO.Path]::GetFullPath($source).TrimEnd('\','/')+[IO.Path]::DirectorySeparatorChar
    foreach($entry in Get-ChildItem -LiteralPath $source -Recurse -Force){
        if(($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw 'Refusing linked stage input'}
        if($entry.PSIsContainer){continue}
        $relative=$entry.FullName.Substring($prefix.Length)
        if($folder -eq 'config' -and $relative -match '^industrial_colonies[\\/]worldgen[\\/]'){continue}
        $target=Join-Path (Join-Path $destination $folder) $relative
        [void][IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($target))
        Copy-Item -LiteralPath $entry.FullName -Destination $target
    }
}
Copy-Item -LiteralPath (Join-Path $server 'offline-assets.properties') -Destination (Join-Path $destination 'offline-assets.properties')
$utf8=[Text.UTF8Encoding]::new($false)
$template=Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'client-smoke.init.gradle.template')
$init=$template.Replace('@STAGE@',$destination.Replace('\','/').Replace("'","\'")).Replace('@USERDEV@',$userdev.Replace('\','/').Replace("'","\'"))
$initPath=Join-Path $destination 'client-smoke.init.gradle'
[IO.File]::WriteAllText($initPath,$init,$utf8)
$plan['initScript']=$initPath
$plan['mods']=@($manifest)
$plan['prepareCommand']='.\gradlew.bat --offline --no-configuration-cache --console=plain -I "'+$initPath+'" prepareClientRun auditClientSmokeDependencies'
$plan['dryRunCommand']='.\gradlew.bat --offline --no-configuration-cache --console=plain -I "'+$initPath+'" runClient --dry-run'
$plan['launchCommandNotExecuted']='.\gradlew.bat --offline --no-configuration-cache --console=plain -I "'+$initPath+'" runClient'
[IO.File]::WriteAllText((Join-Path $destination 'client-preparation.json'),($plan|ConvertTo-Json -Depth 8)+[Environment]::NewLine,$utf8)
[pscustomobject]$plan|Select-Object * -ExcludeProperty mods|ConvertTo-Json -Depth 8
