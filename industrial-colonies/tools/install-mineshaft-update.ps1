param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$project = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$pack = 'C:\Users\GodPC\curseforge\minecraft\Instances\All in one'
$candidate = Join-Path $project 'build\libs\industrial_colonies-0.5.2.jar'
$expected = 'D1A60CE6F8869B7C1197EAE9D0D2879B8599A38BC34C064D878475E8594EFA2E'
if ((Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash -ne $expected) { throw 'Candidate hash changed' }
$old = Join-Path $pack 'mods\industrial_colonies-0.5.1.jar'
$target = Join-Path $pack 'mods\industrial_colonies-0.5.2.jar'
$oldHash = (Get-FileHash -LiteralPath $old -Algorithm SHA256).Hash
if ($oldHash -ne '7219C29073CF45918E4BD8A64127E4D83147CC277120E334BE10242882078749') { throw 'Installed base differs from the audited 0.5.1 JAR' }
$log = Join-Path $project 'isolated-runtime\mineshaft-01\launch-r1.log'
$evidence = Get-Content -LiteralPath $log -Raw
foreach ($marker in @('MINESHAFT_VANILLA_PARITY_PASS samples=128','MINESHAFT_CONNECTION_PASS','All 6 required tests passed','BUILD SUCCESSFUL')) {
    if (-not $evidence.Contains($marker)) { throw "Missing native acceptance: $marker" }
}
if (Test-Path -LiteralPath $target) { throw 'Target already exists; inspect current installation first' }
$active = @(Get-ChildItem -LiteralPath (Join-Path $pack 'mods') -File -Filter 'industrial_colonies-*.jar')
if ($active.Count -ne 1 -or $active[0].FullName -ne $old) { throw 'Unexpected active Industrial Colonies JAR set' }
if (-not $Apply) { [ordered]@{candidate=$candidate;sha256=$expected;replace=$old;oldSha256=$oldHash;target=$target;scope='Only the Industrial Colonies JAR; ore workings on newly generated mineshafts'} | ConvertTo-Json; return }
$running = @(Get-CimInstance Win32_Process -Filter "Name = 'java.exe' OR Name = 'javaw.exe'" | Where-Object { $_.CommandLine -like '*All in one*' })
if ($running.Count) { throw 'Live pack is running; close Minecraft before applying' }
$backup = Join-Path $pack ('_industrial_colonies_backups\mineshaft-veins-0.5.2-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
$backup = [IO.Path]::GetFullPath($backup)
if (-not $backup.StartsWith($pack + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Backup escapes named instance' }
New-Item -ItemType Directory -Path $backup | Out-Null
$backupJar = Join-Path $backup 'industrial_colonies-0.5.1.jar'
Copy-Item -LiteralPath $old -Destination $backupJar
if ((Get-FileHash -LiteralPath $backupJar -Algorithm SHA256).Hash -ne $oldHash) { throw 'Backup verification failed' }
$retired = Join-Path $backup 'industrial_colonies-0.5.1.jar.retired'
Move-Item -LiteralPath $old -Destination $retired
try {
    Copy-Item -LiteralPath $candidate -Destination $target
    if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $expected) { throw 'Installed hash mismatch' }
} catch {
    if (Test-Path -LiteralPath $target) { Move-Item -LiteralPath $target -Destination (Join-Path $backup 'failed-0.5.2.jar') }
    Copy-Item -LiteralPath $backupJar -Destination $old
    throw
}
$receipt = [ordered]@{status='APPLIED';version='0.5.2';sha256=$expected;installed=$target;backup=$backupJar;previousSha256=$oldHash;appliedAt=(Get-Date).ToString('o');savesTouched=$false;recipesTouched=$false}
$receipt | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $backup 'deployment.json') -Encoding utf8
$receipt | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $project 'build\mineshaft-deployment.json') -Encoding utf8
$receipt | ConvertTo-Json

