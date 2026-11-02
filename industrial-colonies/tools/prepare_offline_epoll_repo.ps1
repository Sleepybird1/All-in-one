[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$StageRoot,
    [string]$ProjectRoot=(Join-Path $PSScriptRoot '..'),
    [string]$ServerJar=''
)
# Copy exact bundled Netty native artifacts to a workspace-only Maven repository.
# No downloads, launches, substitutions, cache edits, or live installation writes.
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$project=[IO.Path]::GetFullPath($ProjectRoot)
$stage=[IO.Path]::GetFullPath($StageRoot)
$allowed=[IO.Path]::GetFullPath((Join-Path $project 'isolated-runtime')).TrimEnd('\','/')+[IO.Path]::DirectorySeparatorChar
if(-not $stage.StartsWith($allowed,[StringComparison]::OrdinalIgnoreCase)){throw 'Stage must be inside project isolated-runtime'}
if(-not (Test-Path -LiteralPath $stage -PathType Container)){throw 'Stage directory must already exist'}
if(-not $ServerJar){$ServerJar=Join-Path $project '../gradle-user-home/caches/neoformruntime/artifacts/minecraft_1.21.1_server.jar'}
$source=[IO.Path]::GetFullPath($ServerJar)
$repo=Join-Path $stage 'offline-maven'
$relative='io/netty/netty-transport-native-epoll/4.1.97.Final/'
$targetDirectory=Join-Path $repo $relative
[void][IO.Directory]::CreateDirectory($targetDirectory)
$expected=[ordered]@{
    'linux-x86_64'='54188f271e388e7f313aea995e82f58ce2cdb809'
    'linux-aarch_64'='5514744c588190ffda076b35a9b8c9f24946a960'
}
$report=[System.Collections.Generic.List[object]]::new()
$pomBytes=$null
$archive=[IO.Compression.ZipFile]::OpenRead($source)
try{
    foreach($classifier in $expected.Keys){
        $name='netty-transport-native-epoll-4.1.97.Final-'+$classifier+'.jar'
        $entryPath='META-INF/libraries/'+$relative+$name
        $entry=$archive.GetEntry($entryPath)
        if(-not $entry){throw "Exact bundled artifact absent: $entryPath"}
        $buffer=[IO.MemoryStream]::new()
        $inputStream=$entry.Open()
        try{$inputStream.CopyTo($buffer)}finally{$inputStream.Dispose()}
        $bytes=$buffer.ToArray()
        $actual=[Convert]::ToHexString([Security.Cryptography.SHA1]::HashData($bytes)).ToLowerInvariant()
        if($actual -ne $expected[$classifier]){throw "Bundled artifact differs from Minecraft manifest: $name"}
        $buffer.Position=0
        $nested=[IO.Compression.ZipArchive]::new($buffer,[IO.Compression.ZipArchiveMode]::Read)
        try{
            if(@($nested.Entries|Where-Object {$_.FullName -like '*.class'}).Count -ne 0){throw 'Unexpected Java classes in native-only classifier'}
            $pomEntry=$nested.GetEntry('META-INF/maven/io.netty/netty-transport-native-epoll/pom.xml')
            if(-not $pomEntry){throw 'Bundled Maven POM is absent'}
            $pomBuffer=[IO.MemoryStream]::new();$pomInput=$pomEntry.Open()
            try{$pomInput.CopyTo($pomBuffer);$currentPom=$pomBuffer.ToArray()}finally{$pomInput.Dispose();$pomBuffer.Dispose()}
            if($null -ne $pomBytes -and [Convert]::ToBase64String($pomBytes) -ne [Convert]::ToBase64String($currentPom)){throw 'Classifier POMs differ'}
            $pomBytes=$currentPom
        }finally{$nested.Dispose();$buffer.Dispose()}
        $target=Join-Path $targetDirectory $name
        if([IO.File]::Exists($target)){
            if((Get-FileHash -LiteralPath $target -Algorithm SHA1).Hash.ToLowerInvariant() -ne $actual){throw "Refusing different existing artifact: $target"}
        }else{[IO.File]::WriteAllBytes($target,$bytes)}
        $report.Add([ordered]@{classifier=$classifier;sourceEntry=$entryPath;sha1=$actual;bytes=$bytes.Length;target=$target})
    }
}finally{$archive.Dispose()}
$pomTarget=Join-Path $targetDirectory 'netty-transport-native-epoll-4.1.97.Final.pom'
if([IO.File]::Exists($pomTarget)){
    if([Convert]::ToBase64String([IO.File]::ReadAllBytes($pomTarget)) -ne [Convert]::ToBase64String($pomBytes)){throw 'Refusing different existing POM'}
}else{[IO.File]::WriteAllBytes($pomTarget,$pomBytes)}
[ordered]@{repository=$repo;source=$source;sourceSha256=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash;artifacts=@($report);pom='Exact embedded upstream POM, not synthetic metadata';noRuntimeClassesDropped=$true;noLaunch=$true}
