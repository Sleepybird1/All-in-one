param(
    [string]$ProjectRoot = (Split-Path $PSScriptRoot -Parent),
    [string]$JavaDirectory = 'C:/Program Files/Java/jdk-21/bin',
    [string]$GsonJar = 'C:/Users/GodPC/Documents/Codex/2026-08-16/ok/work/gradle-user-home/caches/modules-2/files-2.1/com.google.code.gson/gson/2.10.1/b3add478d4382b78ea20b1671390a858002feb6c/gson-2.10.1.jar'
)
$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$classes = Join-Path $ProjectRoot 'build/processing-runtime-test/classes'
New-Item -ItemType Directory -Force -Path $classes | Out-Null
$source = Join-Path $ProjectRoot 'src/main/java/dev/godpc/industrialcolonies/processing'
$sources = @(
    (Join-Path $source 'ManualWorkSessions.java'),
    (Join-Path $source 'ManualCinnabarConfig.java'),
    (Join-Path $source 'ExclusiveRecovery.java'),
    (Join-Path $ProjectRoot 'tools/test-support/net/neoforged/fml/loading/FMLPaths.java'),
    (Join-Path $ProjectRoot 'tools/java/dev/godpc/industrialcolonies/processing/ProcessingRuntimeSelfTest.java')
)
# Pure test: no game bootstrap, world generation, dependency downloads, or production config access.
& (Join-Path $JavaDirectory 'javac.exe') -encoding UTF-8 -cp $GsonJar -d $classes @sources
if ($LASTEXITCODE -ne 0) { throw "Processing runtime self-test compilation failed ($LASTEXITCODE)" }
& (Join-Path $JavaDirectory 'java.exe') -Xmx256m -cp "$classes;$GsonJar" dev.godpc.industrialcolonies.processing.ProcessingRuntimeSelfTest
if ($LASTEXITCODE -ne 0) { throw "Processing runtime self-test failed ($LASTEXITCODE)" }
