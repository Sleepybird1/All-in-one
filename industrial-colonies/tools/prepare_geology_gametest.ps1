[CmdletBinding()]
param(
    [string]$ProjectRoot=(Join-Path $PSScriptRoot '..'),
    [string]$PackRoot='C:\Users\GodPC\curseforge\minecraft\Instances\All in one',
    [string]$CandidateJar='',
    [string]$UserDevJar='',
    [string]$DevLaunchSourceDirectory='',
    [string]$AssetsRoot='C:\Users\GodPC\curseforge\minecraft\Install\assets',
    [string]$AssetIndex='17',
    [switch]$Stage
)
# Default: read-only plan. -Stage copies inputs to a NEW workspace-only directory.
# NEVER starts Gradle/Java/Minecraft, writes an EULA, downloads, or copies saves.
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$project=[System.IO.Path]::GetFullPath($ProjectRoot)
$pack=[System.IO.Path]::GetFullPath($PackRoot)
if(-not(Test-Path -LiteralPath (Join-Path $project 'build.gradle'))){throw 'Not the source project'}
if(-not $CandidateJar){$CandidateJar=Join-Path $project 'build/libs/industrial_colonies-0.4.0.jar'}
$candidate=[System.IO.Path]::GetFullPath($CandidateJar)
if(-not(Test-Path -LiteralPath $candidate)){throw "Build the candidate first: $candidate"}
if(-not $UserDevJar){$UserDevJar=Join-Path $project '../gradle-user-home/caches/modules-2/files-2.1/net.neoforged/neoforge/21.1.248/dab61062b17c39eb246328576ae1bcbd59ee780b/neoforge-21.1.248-userdev.jar'}
$userdev=[System.IO.Path]::GetFullPath($UserDevJar)
if(-not(Test-Path -LiteralPath $userdev -PathType Leaf)){throw "Exact cached userdev JAR is absent; no download permitted: $userdev"}
$userdevSha1=(Get-FileHash -LiteralPath $userdev -Algorithm SHA1).Hash
if($userdevSha1 -ne 'DAB61062B17C39EB246328576AE1BCBD59EE780B'){throw 'Unexpected userdev artifact; this harness targets exact NeoForge 21.1.248 metadata'}
$userdevArchive=[System.IO.Compression.ZipFile]::OpenRead($userdev)
try{
    $userdevEntry=$userdevArchive.GetEntry('config.json')
    if(-not $userdevEntry){throw 'Cached userdev JAR has no original config.json'}
    $userdevReader=[System.IO.StreamReader]::new($userdevEntry.Open())
    try{$userdevConfig=$userdevReader.ReadToEnd()|ConvertFrom-Json -AsHashtable}finally{$userdevReader.Dispose()}
    if(-not $userdevConfig.runs.gameTestServer -or -not $userdevConfig.runs.gameTestServer.server){throw 'Cached userdev metadata lacks the server GameTest run'}
}finally{$userdevArchive.Dispose()}
if(-not $DevLaunchSourceDirectory){$DevLaunchSourceDirectory=Join-Path $project 'isolated-runtime/geology-gametest-20260909-001051-895/offline-maven/net/neoforged/DevLaunch/1.0.2'}
$devLaunchSource=[System.IO.Path]::GetFullPath($DevLaunchSourceDirectory)
$devLaunchArtifacts=[System.Collections.Generic.List[object]]::new()
$approvedDevLaunchHashes=@{
    jar='366ADC4E95AB9B32C8E33B9F449529C8937C6FC021EE0C6B25419EA2BB703740'
    pom='49BA05392F1BF4A513DA8CE72377230EEC261B6E13A019B6DF526DD22D2CBC30'
    module='30A811979EC04FCCBD1F78D4B1C387913ACD08C52EBD0C97F87DB08B0E61FDDC'
}
foreach($extension in @('jar','pom','module')){
    $artifactName='DevLaunch-1.0.2.'+$extension
    $artifactPath=Join-Path $devLaunchSource $artifactName
    $checksumPath=$artifactPath+'.sha256'
    if(-not(Test-Path -LiteralPath $artifactPath -PathType Leaf) -or -not(Test-Path -LiteralPath $checksumPath -PathType Leaf)){
        throw "Missing checksum-verified local DevLaunch artifact: $artifactName. Obtain the exact official 1.0.2 artifact and SHA-256 separately with approval, then supply -DevLaunchSourceDirectory. This preparation script never downloads."
    }
    $checksumText=(Get-Content -LiteralPath $checksumPath -Raw).Trim()
    if($checksumText -notmatch '^([0-9a-fA-F]{64})(?:\s|$)'){throw "Invalid SHA-256 sidecar: $checksumPath"}
    $expectedChecksum=$Matches[1].ToUpperInvariant()
    if($expectedChecksum -ne $approvedDevLaunchHashes[$extension]){throw "DevLaunch sidecar differs from approved official acquisition: $artifactName"}
    $actualChecksum=(Get-FileHash -LiteralPath $artifactPath -Algorithm SHA256).Hash
    if($actualChecksum -ne $expectedChecksum){throw "DevLaunch checksum mismatch: $artifactName"}
    $devLaunchArtifacts.Add([ordered]@{name=$artifactName;source=$artifactPath;sha256=$actualChecksum;bytes=(Get-Item -LiteralPath $artifactPath).Length})
}
$devLaunchModule=Get-Content -LiteralPath (Join-Path $devLaunchSource 'DevLaunch-1.0.2.module') -Raw|ConvertFrom-Json -AsHashtable
if($devLaunchModule.component.group -ne 'net.neoforged' -or $devLaunchModule.component.module -ne 'DevLaunch' -or $devLaunchModule.component.version -ne '1.0.2'){throw 'Unexpected DevLaunch module coordinates'}
$devLaunchArchive=[System.IO.Compression.ZipFile]::OpenRead((Join-Path $devLaunchSource 'DevLaunch-1.0.2.jar'))
try{if(-not $devLaunchArchive.GetEntry('net/neoforged/devlaunch/Main.class')){throw 'Exact DevLaunch entry point absent'}}finally{$devLaunchArchive.Dispose()}
$assets=[System.IO.Path]::GetFullPath($AssetsRoot)
if($AssetIndex -notmatch '^[a-zA-Z0-9_.-]+$'){throw 'Invalid local asset index ID'}
$assetIndexFile=Join-Path $assets ('indexes/'+$AssetIndex+'.json')
if(-not(Test-Path -LiteralPath $assetIndexFile -PathType Leaf)){throw "Required installed asset index is absent: $assetIndexFile"}
$assetIndexData=Get-Content -LiteralPath $assetIndexFile -Raw | ConvertFrom-Json -AsHashtable
if(-not $assetIndexData.objects -or $assetIndexData.objects.Count -eq 0){throw 'Installed asset index has no objects'}
foreach($assetEntry in $assetIndexData.objects.GetEnumerator()){
    $hash=[string]$assetEntry.Value.hash
    if($hash -notmatch '^[0-9a-f]{40}$'){throw "Invalid indexed asset hash: $($assetEntry.Key)"}
    $assetFile=Join-Path $assets ('objects/'+$hash.Substring(0,2)+'/'+$hash)
    if(-not [System.IO.File]::Exists($assetFile)){throw "Missing installed asset; no download permitted: $($assetEntry.Key)"}
    if(([System.IO.FileInfo]::new($assetFile)).Length -ne $assetEntry.Value.size){throw "Installed asset size mismatch: $($assetEntry.Key)"}
}
$zip=[System.IO.Compression.ZipFile]::OpenRead($candidate)
try{
foreach($entry in @(
'dev/godpc/industrialcolonies/geology/GeologyBlocks.class',
'dev/godpc/industrialcolonies/geology/GeologyGameTests.class',
'data/industrial_colonies/structure/geology_smoke_empty.nbt',
'data/industrial_colonies/geology/deposit_families.json',
'industrial_colonies.mixins.json'
)){if(-not $zip.GetEntry($entry)){throw "Candidate requires rebuild; missing $entry"}}
}finally{$zip.Dispose()}
$mods=@(Get-ChildItem -LiteralPath (Join-Path $pack 'mods') -File -Filter '*.jar')
$installedOwned=[System.Collections.Generic.List[string]]::new()
foreach($mod in $mods){
$zip=[System.IO.Compression.ZipFile]::OpenRead($mod.FullName)
try{
$entry=$zip.GetEntry('META-INF/neoforge.mods.toml')
if(-not $entry){$entry=$zip.GetEntry('META-INF/mods.toml')}
if($entry){
$reader=[System.IO.StreamReader]::new($entry.Open())
try{$metadata=$reader.ReadToEnd()}finally{$reader.Dispose()}
if($metadata -match '(?m)^\s*modId\s*=\s*["'']industrial_colonies["'']'){$installedOwned.Add($mod.FullName)}
}
}finally{$zip.Dispose()}
}
if($installedOwned.Count -gt 1){throw 'Multiple installed Industrial Colonies jars; resolve ambiguity first'}
$copiedMods=@($mods|Where-Object {$_.FullName -notin $installedOwned})
$folders=@('config','defaultconfigs','kubejs','kjsgen','data','datapacks','moonlight-global-datapacks')
$destination=Join-Path $project ('isolated-runtime/geology-gametest-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$plan=[ordered]@{
mode=if($Stage){'stage_only'}else{'read_only_plan'}
candidate=$candidate
candidateSha256=(Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash
installedJarCount=$mods.Count
copiedInstalledJars=$copiedMods.Count
excludedInstalledOwnedJars=@($installedOwned)
stagedJarCount=$copiedMods.Count+1
modBytes=@($copiedMods|Measure-Object Length -Sum)[0].Sum+(Get-Item -LiteralPath $candidate).Length
inputFolders=@($folders|Where-Object {Test-Path -LiteralPath (Join-Path $pack $_)})
destination=$destination
noSavesCopied=$true
noLinksCreated=$true
noLaunch=$true
noEulaWritten=$true
localAssets=[ordered]@{root=$assets;index=$AssetIndex;indexSha1=(Get-FileHash -LiteralPath $assetIndexFile -Algorithm SHA1).Hash;objectsPresentWithExpectedSize=$assetIndexData.objects.Count;objectHashesRecomputed=$false;downloadAssetsDisabled=$true;liveAssetsReadOnly=$true}
localRunTemplates=[ordered]@{userdevJar=$userdev;sha1=$userdevSha1;archiveEntry='config.json';metadataModified=$false;standaloneModdevConfigNotRequired=$true}
localDevLaunch=[ordered]@{sourceDirectory=$devLaunchSource;artifacts=@($devLaunchArtifacts);remoteChecksumSidecarsVerified=$true;automaticNetwork=$false}
networkRequirement='Run later only with enforced outbound-network denial; Gradle --offline alone does not block mod traffic.'
}
if(-not $Stage){$plan|ConvertTo-Json -Depth 6;return}
$stageRoot=[System.IO.Path]::GetFullPath($destination)
$allowedRoot=[System.IO.Path]::GetFullPath((Join-Path $project 'isolated-runtime')).TrimEnd('\','/')+[System.IO.Path]::DirectorySeparatorChar
if(-not $stageRoot.StartsWith($allowedRoot,[StringComparison]::OrdinalIgnoreCase)){throw 'Destination escaped the project'}
if(Test-Path -LiteralPath $stageRoot){throw 'Refusing to overwrite an existing smoke directory'}
[void][System.IO.Directory]::CreateDirectory((Join-Path $stageRoot 'mods'))
foreach($mod in $copiedMods){Copy-Item -LiteralPath $mod.FullName -Destination (Join-Path $stageRoot ('mods/'+$mod.Name))}
Copy-Item -LiteralPath $candidate -Destination (Join-Path $stageRoot ('mods/'+[System.IO.Path]::GetFileName($candidate)))
foreach($folder in $folders){
$sourceFolder=Join-Path $pack $folder
if(-not(Test-Path -LiteralPath $sourceFolder)){continue}
$sourcePrefix=[System.IO.Path]::GetFullPath($sourceFolder).TrimEnd('\','/')+[System.IO.Path]::DirectorySeparatorChar
foreach($file in Get-ChildItem -LiteralPath $sourceFolder -File -Recurse){
if(($file.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0){throw "Refusing linked input: $($file.FullName)"}
$relative=$file.FullName.Substring($sourcePrefix.Length)
# Test candidate master defaults, not a stale external geology override.
if($folder -eq 'config' -and $relative -match '^industrial_colonies[\\/]worldgen[\\/]'){continue}
$target=Join-Path (Join-Path $stageRoot $folder) $relative
[void][System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($target))
Copy-Item -LiteralPath $file.FullName -Destination $target
}
}
$utf8=[System.Text.UTF8Encoding]::new($false)
$plan['offlineEpollRepository']=& (Join-Path $PSScriptRoot 'prepare_offline_epoll_repo.ps1') -StageRoot $stageRoot -ProjectRoot $project
$devLaunchTarget=Join-Path $stageRoot 'offline-maven/net/neoforged/DevLaunch/1.0.2'
[void][System.IO.Directory]::CreateDirectory($devLaunchTarget)
foreach($artifact in $devLaunchArtifacts){
    Copy-Item -LiteralPath $artifact.source -Destination (Join-Path $devLaunchTarget $artifact.name)
    Copy-Item -LiteralPath ($artifact.source+'.sha256') -Destination (Join-Path $devLaunchTarget ($artifact.name+'.sha256'))
    if((Get-FileHash -LiteralPath (Join-Path $devLaunchTarget $artifact.name) -Algorithm SHA256).Hash -ne $artifact.sha256){throw 'Staged DevLaunch copy failed hash verification'}
}
$groovyDirectory=$stageRoot.Replace('\','/').Replace("'","\'")
$groovyUserDev=$userdev.Replace('\','/').Replace("'","\'")
$assetPropertiesFile=Join-Path $stageRoot 'offline-assets.properties'
# Forward slashes avoid Java Properties interpreting Windows backslashes as escapes.
$assetProperties=('assets_root={0}{2}asset_index={1}{2}' -f $assets.Replace('\','/'),$AssetIndex,[Environment]::NewLine)
[System.IO.File]::WriteAllText($assetPropertiesFile,$assetProperties,$utf8)
$init=@"
gradle.projectsEvaluated {
    def p = gradle.rootProject
    p.repositories.maven {
        name = 'isolatedBundledNettyEpoll'
        url = p.uri('$groovyDirectory/offline-maven')
        content { includeModule('io.netty', 'netty-transport-native-epoll') }
        metadataSources { mavenPom(); artifact() }
    }
    p.repositories.maven {
        name = 'isolatedOfficialDevLaunch'
        url = p.uri('$groovyDirectory/offline-maven')
        content { includeModule('net.neoforged', 'DevLaunch') }
        metadataSources { gradleMetadata(); mavenPom(); artifact() }
    }
    // ModDevGradle reads these two properties even for a headless server run.
    // Supply the installed local assets explicitly; NeoForm's downloader does not obey --offline.
    def localAssets = p.file('$groovyDirectory/offline-assets.properties')
    if (!localAssets.isFile()) throw new GradleException('Missing staged offline asset reference')
    p.tasks.named('downloadAssets') { enabled = false }
    // Supported ModDevGradle input: a userdev JAR is read directly via its original config.json.
    def localUserDev = p.file('$groovyUserDev')
    if (!localUserDev.isFile()) throw new GradleException('Missing exact cached NeoForge userdev JAR')
    p.tasks.named('prepareGameTestServerRun') {
        assetProperties.set(localAssets)
        runTypeTemplatesSource.setFrom(localUserDev)
    }
    def run = p.extensions.getByName('neoForge').runs.getByName('gameTestServer')
    run.gameDirectory.set(p.file('$groovyDirectory'))
    // Use the compiled candidate in isolated mods, not Gradle project-class mod folders.
    run.loadedMods.set([])
    run.systemProperty('neoforge.gameTestServer', 'true')
    run.systemProperty('neoforge.enabledGameTestNamespaces', 'industrial_colonies')
    run.systemProperty('java.awt.headless', 'true')
    run.systemProperty('mixin.debug.verbose', 'true')
    run.systemProperty('bsl.debug', 'true')
    run.jvmArgument('-Xmx6G')
    run.programArguments.set([
        '--nogui', '--allowUpdates', 'false',
        '--universe', '$groovyDirectory/worlds',
        '--world', 'geology-smoke-world'
    ])
}
"@
$initFile=Join-Path $stageRoot 'geology-smoke.init.gradle'
[System.IO.File]::WriteAllText($initFile,$init,$utf8)
$properties=@'
server-ip=127.0.0.1
server-port=0
online-mode=false
enable-status=false
enable-query=false
enable-rcon=false
broadcast-console-to-ops=false
level-name=geology-smoke-world
level-seed=812734921
view-distance=2
simulation-distance=2
spawn-protection=0
generate-structures=false
sync-chunk-writes=true
'@
[System.IO.File]::WriteAllText((Join-Path $stageRoot 'server.properties'),$properties,$utf8)
$plan['initScript']=$initFile
$plan['commands']=@(
('.\gradlew.bat --offline --no-configuration-cache --console=plain -I "{0}" runGameTestServer --dry-run' -f $initFile),
('.\gradlew.bat --offline --no-configuration-cache --console=plain -I "{0}" runGameTestServer' -f $initFile)
)
$plan['stagedInputs']='Physical copies only. No saves, account/launcher files, options, logs, resourcepacks or natives. External config/industrial_colonies/worldgen overrides excluded so candidate defaults are tested.'
[System.IO.File]::WriteAllText((Join-Path $stageRoot 'preparation.json'),($plan|ConvertTo-Json -Depth 6)+[Environment]::NewLine,$utf8)
$plan|ConvertTo-Json -Depth 6
