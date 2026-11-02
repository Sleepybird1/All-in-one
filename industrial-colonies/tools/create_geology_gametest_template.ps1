[CmdletBinding()]
param([string]$ProjectRoot=(Join-Path $PSScriptRoot '..'))
$ErrorActionPreference='Stop'
$project=[System.IO.Path]::GetFullPath($ProjectRoot)
if(-not(Test-Path -LiteralPath (Join-Path $project 'build.gradle'))){throw 'Not the source project'}
# Empty 3x3x3 vanilla structure NBT; no blocks/entities and an air palette.
# Root compound; size int-list; entities/blocks compound-lists; palette; DataVersion=3955.
$hex='0A000009000473697A650300000003000000030000000300000003090008656E7469746965730A00000000090006626C6F636B730A0000000009000770616C657474650A000000010800044E616D65000D6D696E6563726166743A6169720003000B4461746156657273696F6E00000F7300'
$raw=[Convert]::FromHexString($hex)
$memory=[System.IO.MemoryStream]::new()
$gzip=[System.IO.Compression.GZipStream]::new($memory,[System.IO.Compression.CompressionLevel]::Optimal,$true)
try{$gzip.Write($raw,0,$raw.Length)}finally{$gzip.Dispose()}
$bytes=$memory.ToArray();$memory.Dispose()
$target=Join-Path $project 'src/main/resources/data/industrial_colonies/structure/geology_smoke_empty.nbt'
if(Test-Path -LiteralPath $target){
    $existing=[System.IO.File]::ReadAllBytes($target)
    if([Convert]::ToBase64String($existing) -cne [Convert]::ToBase64String($bytes)){throw 'Existing test template differs; manual review required.'}
}else{
    [void][System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($target))
    [System.IO.File]::WriteAllBytes($target,$bytes)
}
Get-FileHash -LiteralPath $target -Algorithm SHA256|Select-Object Path,Hash|ConvertTo-Json

