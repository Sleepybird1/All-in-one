param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$project = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$pack = 'C:\Users\GodPC\curseforge\minecraft\Instances\All in one'
$candidate = Join-Path $project 'build\libs\industrial_colonies-0.5.1.jar'
$expected = '7219C29073CF45918E4BD8A64127E4D83147CC277120E334BE10242882078749'
if ((Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash -ne $expected) { throw 'Candidate hash changed' }
$old = Join-Path $pack 'mods\industrial_colonies-0.5.0.jar'
$target = Join-Path $pack 'mods\industrial_colonies-0.5.1.jar'
$oldHash = (Get-FileHash -LiteralPath $old -Algorithm SHA256).Hash
if ($oldHash -ne '8DF80E5C7E4B447F651696A9383A1487B26F557A67D6263DEAFA3805BC675D91') { throw 'Installed base differs from the audited 0.5.0 JAR' }
$log = Join-Path $project 'isolated-runtime\cave-traces-01\launch-surface-r2.log'
$evidence = Get-Content -LiteralPath $log -Raw
foreach ($marker in @('CAVE_NATIVE_PLACEMENT_PASS','CAVE_NATURAL_SURVEY_PASS','SURFACE_ROCK_PICKUP_PASS','SURFACE_ROCK_NATURAL_PASS','All 8 required tests passed','BUILD SUCCESSFUL')) {
    if (-not $evidence.Contains($marker)) { throw "Missing native acceptance: $marker" }
}
$clientLog = Get-Content -LiteralPath (Join-Path $project 'isolated-runtime\surface-client-02\launch.log') -Raw
if (-not $clientLog.Contains('SURFACE_CLIENT_PASS models=21') -or -not $clientLog.Contains('BUILD SUCCESSFUL')) { throw 'Missing client render acceptance' }
if (Test-Path -LiteralPath $target) { throw 'Target already exists; inspect current installation first' }
$active = @(Get-ChildItem -LiteralPath (Join-Path $pack 'mods') -File -Filter 'industrial_colonies-*.jar')
if ($active.Count -ne 1 -or $active[0].FullName -ne $old) { throw 'Unexpected active Industrial Colonies JAR set' }
if (-not $Apply) { [ordered]@{candidate=$candidate;sha256=$expected;replace=$old;oldSha256=$oldHash;target=$target;scope='Only the Industrial Colonies JAR; automatic new config on next world generation'} | ConvertTo-Json; return }
$running = @(Get-CimInstance Win32_Process -Filter "Name = 'java.exe' OR Name = 'javaw.exe'" | Where-Object { $_.CommandLine -like '*All in one*' })
if ($running.Count) { throw 'Live pack is running; close Minecraft before applying' }
$backup = Join-Path $pack ('_industrial_colonies_backups\cave-traces-0.5.1-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
$backup = [IO.Path]::GetFullPath($backup)
if (-not $backup.StartsWith($pack + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Backup escapes named instance' }
New-Item -ItemType Directory -Path $backup | Out-Null
$backupJar = Join-Path $backup 'industrial_colonies-0.5.0.jar'
Copy-Item -LiteralPath $old -Destination $backupJar
if ((Get-FileHash -LiteralPath $backupJar -Algorithm SHA256).Hash -ne $oldHash) { throw 'Backup verification failed' }
$retired = Join-Path $backup 'industrial_colonies-0.5.0.jar.retired'
Move-Item -LiteralPath $old -Destination $retired
try {
    Copy-Item -LiteralPath $candidate -Destination $target
    if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $expected) { throw 'Installed hash mismatch' }
} catch {
    if (Test-Path -LiteralPath $target) { Move-Item -LiteralPath $target -Destination (Join-Path $backup 'failed-0.5.1.jar') }
    Copy-Item -LiteralPath $backupJar -Destination $old
    throw
}
$receipt = [ordered]@{status='APPLIED';version='0.5.1';sha256=$expected;installed=$target;backup=$backupJar;previousSha256=$oldHash;appliedAt=(Get-Date).ToString('o');savesTouched=$false;recipesTouched=$false}
$receipt | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $backup 'deployment.json') -Encoding utf8
$receipt | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $project 'build\cave-deployment.json') -Encoding utf8
$receipt | ConvertTo-Json
