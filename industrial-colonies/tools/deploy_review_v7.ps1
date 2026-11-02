$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$stage = Join-Path $projectRoot 'progression/review-batches/20260904/v7-staged'
$instance = 'C:\Users\GodPC\curseforge\minecraft\Instances\All in one'
if (Get-Process javaw -ErrorAction SilentlyContinue) { throw 'Minecraft is still running.' }
$inputs = Get-Content (Join-Path $stage 'deployment-input-hashes.json') -Raw | ConvertFrom-Json
foreach ($entry in $inputs.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath $entry.Name).Hash -ne $entry.Value) { throw "Live review data changed: $($entry.Name)" }
}
$files = @{
    'default.json' = 'kjsgen/projects/default.json'
    'rejected_recipes.json' = 'kjsgen/projects/rejected_recipes.json'
    'default.recipe_reviews.json' = 'kjsgen/industrial_colonies_sync/default.recipe_reviews.json'
    'default.managed.baseline.json' = 'kjsgen/industrial_colonies_sync/default.managed.baseline.json'
}
$backup = Join-Path $instance ('_industrial_colonies_backups/recipe-v7-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $backup | Out-Null
foreach ($entry in $files.GetEnumerator()) {
    Copy-Item -LiteralPath (Join-Path $instance $entry.Value) -Destination (Join-Path $backup $entry.Key)
}
$jarName = 'industrial_colonies-0.4.0.jar'
$jarSource = Join-Path $projectRoot "build/libs/$jarName"
$jarTarget = Join-Path $instance "mods/$jarName"
Copy-Item -LiteralPath $jarTarget -Destination (Join-Path $backup $jarName)
foreach ($entry in $files.GetEnumerator()) {
    $source = Join-Path $stage $entry.Key
    $target = Join-Path $instance $entry.Value
    Copy-Item -LiteralPath $source -Destination $target
    if ((Get-FileHash $source).Hash -ne (Get-FileHash $target).Hash) { throw "Copy verification failed: $target" }
}
Copy-Item -LiteralPath $jarSource -Destination $jarTarget
if ((Get-FileHash $jarSource).Hash -ne (Get-FileHash $jarTarget).Hash) { throw 'Jar verification failed.' }
foreach ($entry in $inputs.PSObject.Properties) {
    if ($entry.Name -match 'projects\\(approved_recipes|Deferred|disabled_recipes|maybe_recipes)\.json$') {
        if ((Get-FileHash -LiteralPath $entry.Name).Hash -ne $entry.Value) { throw "Protected project changed: $($entry.Name)" }
    }
}
Write-Output "Deployed four review JSON files and support JAR. Backup: $backup"
