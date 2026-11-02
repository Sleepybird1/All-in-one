$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$before=[IO.Compression.ZipFile]::OpenRead((Join-Path $project 'isolated-runtime/mineshaft-01/mods/industrial_colonies-0.5.1.jar.previous'))
$after=[IO.Compression.ZipFile]::OpenRead((Join-Path $project 'build/libs/industrial_colonies-0.5.2.jar'))
function Read-Text($zip,$path){$r=[IO.StreamReader]::new($zip.GetEntry($path).Open());try{return $r.ReadToEnd()}finally{$r.Dispose()}}
try {
    $a=(Read-Text $before 'assets/industrial_colonies/lang/en_us.json') | ConvertFrom-Json -AsHashtable
    $b=(Read-Text $after 'assets/industrial_colonies/lang/en_us.json') | ConvertFrom-Json -AsHashtable
    foreach($key in (@($a.Keys)+@($b.Keys) | Sort-Object -Unique)) {
        if($a[$key] -cne $b[$key]){[pscustomobject]@{key=$key;old=$a[$key];new=$b[$key]}}
    }
    $audit=Get-Content (Join-Path $project 'build/mineshaft-archive-audit.json') -Raw | ConvertFrom-Json
    $equivalent=@()
    foreach($path in ($audit.changed | Where-Object {$_.EndsWith('.json') -and $_ -ne 'industrial_colonies.mixins.json'})) {
        $same=[System.Text.Json.Nodes.JsonNode]::DeepEquals([System.Text.Json.Nodes.JsonNode]::Parse((Read-Text $before $path)),[System.Text.Json.Nodes.JsonNode]::Parse((Read-Text $after $path)))
        if($same){$equivalent+=$path}else{Write-Output "Semantic resource difference: $path"}
    }
    $audit | Add-Member -Force -NotePropertyName jsonEquivalent -NotePropertyValue $equivalent
    $audit | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $project 'build/mineshaft-archive-audit.json')
    "Equivalent JSON resources: $($equivalent.Count)"
} finally {$before.Dispose();$after.Dispose()}
