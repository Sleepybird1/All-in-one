param(
    [string]$ProjectRoot = (Split-Path $PSScriptRoot -Parent),
    [string]$JavaDirectory = 'C:/Users/GodPC/.gradle/jdks/eclipse_adoptium-21-amd64-windows.2/bin',
    [string]$GsonJar = 'C:/Users/GodPC/.gradle/caches/modules-2/files-2.1/com.google.code.gson/gson/2.10.1/b3add478d4382b78ea20b1671390a858002feb6c/gson-2.10.1.jar'
)
$ErrorActionPreference='Stop'
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$classes = Join-Path $ProjectRoot 'build/geology-planner-test/classes'
New-Item -ItemType Directory -Force -Path $classes | Out-Null
# Use the exact installed Gson dependency; no dependency download or production config writes.
$source = Join-Path $ProjectRoot 'src/main/java/dev/godpc/industrialcolonies/geology'
$sources = @(
    (Join-Path $source 'GeologyConfig.java'),
    (Join-Path $source 'GeologyMath.java'),
    (Join-Path $source 'GeologyPlanner.java'),
    (Join-Path $source 'MassiveDeposits.java'),
    (Join-Path $source 'MassiveDepositGeometry.java'),
    (Join-Path $ProjectRoot 'tools/test-support/net/neoforged/fml/loading/FMLPaths.java'),
    (Join-Path $ProjectRoot 'tools/GeologyPlannerSelfTest.java')
)
& (Join-Path $JavaDirectory 'javac.exe') -encoding UTF-8 -cp $GsonJar -d $classes @sources
if ($LASTEXITCODE -ne 0) { throw "Planner self-test compilation failed ($LASTEXITCODE)" }
& (Join-Path $JavaDirectory 'java.exe') -Xmx512m -cp "$classes;$GsonJar" dev.godpc.industrialcolonies.geology.GeologyPlannerSelfTest $ProjectRoot
if ($LASTEXITCODE -ne 0) { throw "Planner self-test failed ($LASTEXITCODE)" }
