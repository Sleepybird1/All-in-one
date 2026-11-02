[CmdletBinding()]
param(
    [string]$ProjectRoot=(Join-Path $PSScriptRoot '../..'),
    [string]$MinecraftJar='',
    [switch]$Write
)
# Exact mechanical extraction only. Default validates; never launches or writes live files.
$ErrorActionPreference='Stop'
$project=[IO.Path]::GetFullPath($ProjectRoot)
if(-not $MinecraftJar){$MinecraftJar=Join-Path $project '../gradle-user-home/caches/neoformruntime/artifacts/minecraft_1.21.1_client.jar'}
$minecraft=[IO.Path]::GetFullPath($MinecraftJar)
$sourceSha1=(Get-FileHash -Algorithm SHA1 -LiteralPath $minecraft).Hash
if($sourceSha1 -ne '30C73B1C5DA787909B2F73340419FDF13B9DEF88'){throw 'Expected exact original Minecraft 1.21.1 client artifact'}
$root=Join-Path $project 'src/main/resources/resourcepacks/ic_wwoo_decorative'
$entries=@(
    'configured_feature/ore_andesite','configured_feature/ore_diorite',
    'configured_feature/ore_granite','configured_feature/ore_dirt','configured_feature/ore_gravel',
    'placed_feature/ore_andesite_lower','placed_feature/ore_andesite_upper',
    'placed_feature/ore_diorite_lower','placed_feature/ore_diorite_upper',
    'placed_feature/ore_granite_lower','placed_feature/ore_granite_upper','placed_feature/ore_dirt'
)
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip=[IO.Compression.ZipFile]::OpenRead($minecraft)
$records=@()
try{
    foreach($name in $entries){
        $path='data/minecraft/worldgen/'+$name+'.json'
        $entry=$zip.GetEntry($path)
        if(-not $entry){throw "Missing original entry: $path"}
        $buffer=[IO.MemoryStream]::new();$input=$entry.Open()
        try{$input.CopyTo($buffer);$bytes=$buffer.ToArray()}finally{$input.Dispose();$buffer.Dispose()}
        $hash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes))
        $target=Join-Path $root $path
        if($Write){[void][IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($target));[IO.File]::WriteAllBytes($target,$bytes)}
        if(-not(Test-Path -LiteralPath $target -PathType Leaf) -or (Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash -ne $hash){throw "Missing/changed vanilla decorative overlay: $target"}
        $records+=[ordered]@{resource=('minecraft:worldgen/'+$name+'.json');entry=$path;sha256=$hash;bytes=$bytes.Length}
    }
}finally{$zip.Dispose()}
$manifest=[ordered]@{source='Original Minecraft 1.21.1 client JAR';sourceSha1=$sourceSha1;resources=$records;scope='Exactly five configured and seven placed decorative definitions. No lava, economic ores, biomes, terrain noise, textures or rates.'}
$manifestPath=Join-Path $root 'source_manifest.json'
if($Write){[IO.File]::WriteAllText($manifestPath,($manifest|ConvertTo-Json -Depth 5)+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))}
else{
    $existing=Get-Content -Raw -LiteralPath $manifestPath|ConvertFrom-Json
    if($existing.sourceSha1 -ne $sourceSha1 -or ($existing.resources|ConvertTo-Json -Depth 5 -Compress) -cne ($records|ConvertTo-Json -Depth 5 -Compress)){throw 'Decorative source manifest differs'}
}
[pscustomobject]@{status='PASS';mode=if($Write){'mechanical_source_copy'}else{'read_only_validation'};files=$records.Count;sourceSha1=$sourceSha1;sourceAndOverlayBytesIdentical=$true}
