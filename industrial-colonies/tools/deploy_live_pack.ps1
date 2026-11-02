<#
.SYNOPSIS
Safely deploys the built Industrial Colonies mod and owned pack files to the live CurseForge instance.

.DESCRIPTION
Refuses to run while the live Minecraft instance or CurseForge Minecraft Java runtime appears active.
Before constructing a live-file plan, rebuilds stale raw managed-recipe artifacts, reconciles the
reviewed KJSGen deployment fragment, and validates the manifest, compiler output, installed item
registry, canonical materials, nuclear
chemistry boundaries, and the post-Star orbital-entry/ambient-kinetic contracts. Any failed check aborts before
the live instance is modified.
Changed live files are preserved below _industrial_colonies_backups before replacement. The script
copies only project-owned KubeJS files, so default and unrelated scripts remain untouched. If an
operation or SHA256 check fails, the script attempts to restore the complete pre-deployment state.
Reviewed source-managed visual recipes are three-way merged by UID into KJSGen's default project. A
sidecar baseline preserves unrelated live content and prevents managed cards edited in KJSGen
from being silently overwritten.

.EXAMPLE
.\tools\deploy_live_pack.ps1 -PlanOnly

Runs all path/process preflight checks and prints the pending changes without writing to the live pack.

.EXAMPLE
.\tools\deploy_live_pack.ps1

Deploys, verifies SHA256 parity, and prints the in-game acceptance checklist.
#>
[CmdletBinding()]
param(
    [Parameter()]
    [string] $ProjectRoot = 'C:\Users\GodPC\Documents\Codex\2026-08-16\ok\work\industrial-colonies',

    [Parameter()]
    [string] $LivePackRoot = 'C:\Users\GodPC\curseforge\minecraft\Instances\All in one',

    [Parameter()]
    [string] $ProjectJar = 'C:\Users\GodPC\Documents\Codex\2026-08-16\ok\work\industrial-colonies\build\libs\industrial_colonies-0.4.0.jar',

    [Parameter()]
    [string] $PythonExecutable = '',

    [Parameter()]
    [string] $RecipeCatalog = '',

    [Parameter()]
    [string] $RuntimeItemCatalog = '',

    [Parameter()]
    [switch] $PlanOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'deployment_hash_pinning.ps1')

function Resolve-ExistingDirectory {
    param(
        [Parameter(Mandatory)]
        [string] $Path,

        [Parameter(Mandatory)]
        [string] $Label
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        throw "$Label does not exist or is not a directory: $Path"
    }

    return [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $Path).ProviderPath).TrimEnd('\')
}

function Resolve-ExistingFile {
    param(
        [Parameter(Mandatory)]
        [string] $Path,

        [Parameter(Mandatory)]
        [string] $Label
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label does not exist or is not a file: $Path"
    }

    return [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $Path).ProviderPath)
}

function Test-ChildPath {
    param(
        [Parameter(Mandatory)]
        [string] $Parent,

        [Parameter(Mandatory)]
        [string] $Child
    )

    $parentPrefix = [System.IO.Path]::GetFullPath($Parent).TrimEnd('\') + '\'
    $childFull = [System.IO.Path]::GetFullPath($Child)
    return $childFull.StartsWith($parentPrefix, [System.StringComparison]::OrdinalIgnoreCase)
}

function Assert-ChildPath {
    param(
        [Parameter(Mandatory)]
        [string] $Parent,

        [Parameter(Mandatory)]
        [string] $Child,

        [Parameter(Mandatory)]
        [string] $Label
    )

    if (-not (Test-ChildPath -Parent $Parent -Child $Child)) {
        throw "$Label must remain inside '$Parent': $Child"
    }
}

function Get-RelativeChildPath {
    param(
        [Parameter(Mandatory)]
        [string] $Parent,

        [Parameter(Mandatory)]
        [string] $Child
    )

    Assert-ChildPath -Parent $Parent -Child $Child -Label 'Relative path target'
    $parentPrefix = [System.IO.Path]::GetFullPath($Parent).TrimEnd('\') + '\'
    return [System.IO.Path]::GetFullPath($Child).Substring($parentPrefix.Length)
}

function Get-Sha256 {
    param(
        [Parameter(Mandatory)]
        [string] $Path
    )

    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()
}

function Test-SameFileContent {
    param(
        [Parameter(Mandatory)]
        [string] $Left,

        [Parameter(Mandatory)]
        [string] $Right
    )

    if (-not (Test-Path -LiteralPath $Left -PathType Leaf)) {
        return $false
    }
    if (-not (Test-Path -LiteralPath $Right -PathType Leaf)) {
        return $false
    }

    $leftInfo = Get-Item -LiteralPath $Left
    $rightInfo = Get-Item -LiteralPath $Right
    if ($leftInfo.Length -ne $rightInfo.Length) {
        return $false
    }

    return (Get-Sha256 -Path $Left) -eq (Get-Sha256 -Path $Right)
}

function Test-ExclusiveFileAccess {
    param(
        [Parameter(Mandatory)]
        [string] $Path
    )

    try {
        $stream = [System.IO.File]::Open(
            $Path,
            [System.IO.FileMode]::Open,
            [System.IO.FileAccess]::Read,
            [System.IO.FileShare]::None
        )
        $stream.Dispose()
        return $true
    }
    catch [System.IO.IOException] {
        return $false
    }
    catch [System.UnauthorizedAccessException] {
        return $false
    }
}

function Assert-MinecraftStopped {
    param(
        [Parameter(Mandatory)]
        [string] $LiveRoot
    )

    $blockingReasons = [System.Collections.Generic.List[string]]::new()
    $javaProcesses = @(Get-Process -Name 'java', 'javaw' -ErrorAction SilentlyContinue)

    $instancesRoot = Split-Path -Parent $LiveRoot
    $curseForgeMinecraftRoot = Split-Path -Parent $instancesRoot
    $curseForgeRuntimeRoot = [System.IO.Path]::GetFullPath(
        (Join-Path $curseForgeMinecraftRoot 'Install\java')
    ).TrimEnd('\')

    $commandLinesInspected = $false
    if ($javaProcesses.Count -gt 0) {
        try {
            $javaRows = @(
                Get-CimInstance Win32_Process -Filter "Name = 'java.exe' OR Name = 'javaw.exe'" -ErrorAction Stop
            )
            $commandLinesInspected = $true
            $liveBackslash = $LiveRoot.ToLowerInvariant()
            $liveForward = $LiveRoot.Replace('\', '/').ToLowerInvariant()

            foreach ($row in $javaRows) {
                $commandLine = [string] $row.CommandLine
                if ([string]::IsNullOrWhiteSpace($commandLine)) {
                    continue
                }

                $normalizedCommandLine = $commandLine.ToLowerInvariant()
                if (
                    $normalizedCommandLine.Contains($liveBackslash) -or
                    $normalizedCommandLine.Contains($liveForward)
                ) {
                    $blockingReasons.Add(
                        "PID $($row.ProcessId) command line references the live instance"
                    )
                }
            }
        }
        catch {
            Write-Warning "Could not inspect Java command lines: $($_.Exception.Message)"
        }
    }

    foreach ($process in $javaProcesses) {
        try {
            $executablePath = [System.IO.Path]::GetFullPath([string] $process.Path)
            if (Test-ChildPath -Parent $curseForgeRuntimeRoot -Child $executablePath) {
                $blockingReasons.Add(
                    "PID $($process.Id) uses the CurseForge Minecraft Java runtime"
                )
            }
        }
        catch {
            if ((-not $commandLinesInspected) -and $process.ProcessName -eq 'javaw') {
                $blockingReasons.Add(
                    "PID $($process.Id) is an uninspectable javaw process"
                )
            }
        }
    }

    $savesRoot = Join-Path $LiveRoot 'saves'
    if (Test-Path -LiteralPath $savesRoot -PathType Container) {
        foreach ($sessionLock in @(Get-ChildItem -LiteralPath $savesRoot -Filter 'session.lock' -File -Recurse -ErrorAction SilentlyContinue)) {
            if (-not (Test-ExclusiveFileAccess -Path $sessionLock.FullName)) {
                $worldName = Split-Path -Leaf (Split-Path -Parent $sessionLock.FullName)
                $blockingReasons.Add("world '$worldName' has a locked session.lock")
            }
        }
    }

    $uniqueReasons = @($blockingReasons | Sort-Object -Unique)
    if ($uniqueReasons.Count -gt 0) {
        $details = $uniqueReasons -join [Environment]::NewLine
        throw @"
Minecraft may still be using the live pack. Deployment was refused before any live files were changed.
$details
Save and Quit, close Minecraft completely, and run this script again.
"@
    }
}

function Resolve-PythonCommand {
    param(
        [Parameter()]
        [string] $RequestedExecutable
    )

    if (-not [string]::IsNullOrWhiteSpace($RequestedExecutable)) {
        $resolved = Resolve-ExistingFile -Path $RequestedExecutable -Label 'Python executable'
        $version = & $resolved --version 2>&1
        if ($LASTEXITCODE -ne 0 -or ([string] ($version -join ' ')) -notmatch '^Python 3\.') {
            throw "The requested Python executable is not a working Python 3 runtime: $resolved"
        }
        return [pscustomobject]@{
            Executable = $resolved
            PrefixArguments = @()
            DisplayName = $resolved
        }
    }

    foreach ($candidate in @(
        [pscustomobject]@{ Name = 'python'; PrefixArguments = @() },
        [pscustomobject]@{ Name = 'python3'; PrefixArguments = @() },
        [pscustomobject]@{ Name = 'py'; PrefixArguments = @('-3') }
    )) {
        $command = Get-Command -Name $candidate.Name -CommandType Application -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($null -eq $command) {
            continue
        }

        try {
            $probeArguments = @($candidate.PrefixArguments) + @('--version')
            $version = & $command.Source @probeArguments 2>&1
            if (
                $LASTEXITCODE -eq 0 -and
                ([string] ($version -join ' ')) -match '^Python 3\.'
            ) {
                return [pscustomobject]@{
                    Executable = [System.IO.Path]::GetFullPath($command.Source)
                    PrefixArguments = @($candidate.PrefixArguments)
                    DisplayName = "$($command.Source) $($candidate.PrefixArguments -join ' ')".Trim()
                }
            }
        }
        catch {
            continue
        }
    }

    throw @'
Python 3 was not found on PATH. Pass -PythonExecutable with the full path to python.exe.
The deployment stopped before any live-pack file was changed.
'@
}

function Find-UpwardChildPath {
    param(
        [Parameter(Mandatory)]
        [string] $StartDirectory,

        [Parameter(Mandatory)]
        [string[]] $RelativeCandidates,

        [Parameter(Mandatory)]
        [ValidateSet('File', 'Directory')]
        [string] $ExpectedType
    )

    $cursor = [System.IO.Path]::GetFullPath($StartDirectory).TrimEnd('\')
    for ($depth = 0; $depth -le 5; $depth++) {
        foreach ($relative in $RelativeCandidates) {
            $candidate = [System.IO.Path]::GetFullPath((Join-Path $cursor $relative))
            $pathType = if ($ExpectedType -eq 'File') { 'Leaf' } else { 'Container' }
            if (Test-Path -LiteralPath $candidate -PathType $pathType) {
                return $candidate
            }
        }

        $parent = Split-Path -Parent $cursor
        if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $cursor) {
            break
        }
        $cursor = $parent
    }
    return $null
}

function Resolve-RecipeCatalogDirectory {
    param(
        [Parameter(Mandatory)]
        [string] $Root,

        [Parameter()]
        [string] $RequestedPath
    )

    if ([string]::IsNullOrWhiteSpace($RequestedPath)) {
        $RequestedPath = Find-UpwardChildPath `
            -StartDirectory $Root `
            -RelativeCandidates @('outputs\recipe-catalog-current', 'recipe-catalog-current') `
            -ExpectedType Directory
    }
    if ([string]::IsNullOrWhiteSpace($RequestedPath)) {
        throw 'Recipe catalog was not found. Pass -RecipeCatalog with the recipe-catalog-current directory.'
    }

    $resolved = Resolve-ExistingDirectory -Path $RequestedPath -Label 'Recipe catalog'
    Resolve-ExistingFile -Path (Join-Path $resolved 'recipes.csv') -Label 'Recipe catalog recipes.csv' | Out-Null
    Resolve-ExistingFile -Path (Join-Path $resolved 'recipe_refs.csv') -Label 'Recipe catalog recipe_refs.csv' | Out-Null
    return $resolved
}

function Resolve-RuntimeItemCatalogFile {
    param(
        [Parameter(Mandatory)]
        [string] $Root,

        [Parameter()]
        [string] $RequestedPath
    )

    if ([string]::IsNullOrWhiteSpace($RequestedPath)) {
        $RequestedPath = Find-UpwardChildPath `
            -StartDirectory $Root `
            -RelativeCandidates @(
                'exports\ALL_IN_ONE_MODS_ITEMS_BLOCKS.txt',
                'outputs\ALL_IN_ONE_MODS_ITEMS_BLOCKS.txt',
                'ALL_IN_ONE_MODS_ITEMS_BLOCKS.txt'
            ) `
            -ExpectedType File
    }
    if ([string]::IsNullOrWhiteSpace($RequestedPath)) {
        throw 'Runtime item catalog was not found. Pass -RuntimeItemCatalog with ALL_IN_ONE_MODS_ITEMS_BLOCKS.txt.'
    }
    return Resolve-ExistingFile -Path $RequestedPath -Label 'Runtime item catalog'
}

function Invoke-PythonTool {
    param(
        [Parameter(Mandatory)]
        [object] $Python,

        [Parameter(Mandatory)]
        [string] $Script,

        [Parameter()]
        [string[]] $Arguments = @(),

        [Parameter()]
        [int[]] $AllowedExitCodes = @(0),

        [Parameter(Mandatory)]
        [string] $Label
    )

    $scriptResolved = Resolve-ExistingFile -Path $Script -Label "$Label script"
    $commandArguments = @($Python.PrefixArguments) + @($scriptResolved) + @($Arguments)
    Write-Host "[preflight] $Label"
    & $Python.Executable @commandArguments | Out-Host
    $exitCode = $LASTEXITCODE
    if ($AllowedExitCodes -notcontains $exitCode) {
        throw "$Label failed with exit code $exitCode. No live-pack files were changed."
    }
    return $exitCode
}

function Invoke-ManagedRecipePreflight {
    param(
        [Parameter(Mandatory)]
        [string] $Root,

        [Parameter(Mandatory)]
        [string] $LiveRoot,

        [Parameter(Mandatory)]
        [string] $ModsRoot,

        [Parameter(Mandatory)]
        [string] $ProjectJarPath,

        [Parameter(Mandatory)]
        [object] $Python,

        [Parameter(Mandatory)]
        [string] $RecipeCatalogPath,

        [Parameter(Mandatory)]
        [string] $RuntimeItemCatalogPath
    )

    $builder = Join-Path $Root 'tools\build_managed_recipe_manifest.py'
    $generator = Join-Path $Root 'tools\generate_managed_recipe_overhaul.py'
    $reviewAcceptanceReconciler = Join-Path $Root 'tools\apply_recipe_review_acceptance.py'
    $recipeFormPolicyAudit = Join-Path $Root 'tools\audit_recipe_form_policy.py'
    $defaultRestorationValidator = Join-Path $Root 'tools\validate_default_recipe_restoration.py'
    $defaultRestorationTests = Join-Path $Root 'tools\test_default_recipe_restoration.py'
    $rejectedResolutionCoverageTests = Join-Path $Root 'tools\test_rejected_recipe_resolution_coverage.py'
    $v3SteelFrameTests = Join-Path $Root 'tools\test_recipe_design_v3_mekanism_steel_frame.py'
    $v3SourcePolicyAudit = Join-Path $Root 'tools\audit_recipe_design_v3_policy.py'
    $recipeDesignV4Tests = @(
        'test_recipe_design_v4_ae2_electronics_depth.py'
        'test_recipe_design_v4_ae2_remaining_depth.py'
        'test_recipe_design_v4_bigreactors_rejected.py'
        'test_recipe_design_v4_digital_machine_corrections.py'
        'test_recipe_design_v4_electronics_primitives.py'
        'test_recipe_design_v4_machine_family_corrections.py'
        'test_recipe_design_v4_manual_rejections.py'
        'test_recipe_design_v4_manufacturing_rejects.py'
        'test_recipe_design_v4_mega_storage_depth.py'
        'test_recipe_design_v4_rejected_redesigns.py'
        'test_recipe_design_v4_space_electronics.py'
        'test_recipe_design_v4_space_hardware_depth.py'
        'test_recipe_design_v4_stress_storage_depth.py'
        'test_recipe_design_v5_pumpjack_manufacturing.py'
        'test_recipe_design_v5_digital_transmission.py'
        'test_recipe_design_v5_nuclear_hardware.py'
        'test_recipe_design_v5_remaining_rejections.py'
    ) | ForEach-Object { Join-Path $Root "tools\$_" }
    $overhaulValidator = Join-Path $Root 'tools\validate_managed_recipe_overhaul.py'
    $kjsGenMergeTests = Join-Path $Root 'tools\test_merge_kjsgen_project.ps1'
    $orphanRetirementTests = Join-Path $Root 'tools\test_sanitize_kjsgen_orphans.py'
    $autoExportValidator = Join-Path $Root 'tools\validate_kjsgen_auto_export.py'
    $mekanismInfusingCodegenValidator = Join-Path $Root 'tools\validate_kjsgen_mekanism_infusing_codegen.py'
    $mekanismInfusingCodegenTests = Join-Path $Root 'tools\test_validate_kjsgen_mekanism_infusing_codegen.py'
    $tfmgChemicalVatValidator = Join-Path $Root 'tools\validate_kjsgen_tfmg_chemical_vat.py'
    $tfmgChemicalVatTests = Join-Path $Root 'tools\test_validate_kjsgen_tfmg_chemical_vat.py'
    $canonicalValidator = Join-Path $Root 'tools\validate_canonicalization.py'
    $allthemodiumValidator = Join-Path $Root 'tools\validate_allthemodium_currency.py'
    $spaceEntryValidator = Join-Path $Root 'tools\validate_space_entry_boundary.py'
    $spaceEntryTests = Join-Path $Root 'tools\test_validate_space_entry_boundary.py'
    $spaceDestinationValidator = Join-Path $Root 'tools\validate_space_destination_bridge.py'
    $spaceDestinationTests = Join-Path $Root 'tools\test_validate_space_destination_bridge.py'
    $orbitalFlightGateValidator = Join-Path $Root 'tools\validate_orbital_flight_gate.py'
    $orbitalFlightGateTests = Join-Path $Root 'tools\test_validate_orbital_flight_gate.py'
    $orbitalAmbientKineticsValidator = Join-Path $Root 'tools\validate_orbital_ambient_kinetics.py'
    $orbitalAmbientKineticsTests = Join-Path $Root 'tools\test_validate_orbital_ambient_kinetics.py'
    $planetaryFreightGateValidator = Join-Path $Root 'tools\validate_planetary_freight_gates.py'
    $planetaryFreightGateTests = Join-Path $Root 'tools\test_validate_planetary_freight_gates.py'
    $planetaryStructureBuilder = Join-Path $Root 'tools\build_planetary_structure_overrides.py'
    $tieredMegaprojectSequenceTests = Join-Path $Root 'tools\test_validate_tiered_megaproject_sequences.py'
    $nuclearValidator = Join-Path $Root 'tools\validate_nuclear_chemistry_boundaries.py'
    $capstoneReachabilityValidator = Join-Path $Root 'tools\validate_capstone_reachability.py'
    $capstoneReachabilityTests = Join-Path $Root 'tools\test_validate_capstone_reachability.py'
    $foodDiversityValidator = Join-Path $Root 'tools\validate_food_diversity_progression.py'
    $ae2TransformValidator = Join-Path $Root 'tools\validate_ae2_transform_hardening.py'
    $bypassRetirementValidator = Join-Path $Root 'tools\validate_progression_bypass_retirement.py'
    $primitiveToolValidator = Join-Path $Root 'tools\validate_primitive_tool_progression.py'
    $dungeonToolLootValidator = Join-Path $Root 'tools\validate_dungeon_tool_loot.py'
    $dungeonExplorationValidator = Join-Path $Root 'tools\validate_dungeon_exploration_audit.py'
    $regionalOilValidator = Join-Path $Root 'tools\validate_regional_finite_oil_fields.py'
    $questGenerator = Join-Path $Root 'tools\generate_ftbquests_native.py'
    $questValidator = Join-Path $Root 'tools\validate_ftbquests_native.py'
    $postDieselQuestValidator = Join-Path $Root 'tools\validate_ftb_post_diesel_guidance_audit.py'

    $builderArguments = @('--catalog', $RecipeCatalogPath, '--mods', $ModsRoot)
    $builderCheck = Invoke-PythonTool `
        -Python $Python `
        -Script $builder `
        -Arguments ($builderArguments + @('--check')) `
        -AllowedExitCodes @(0, 1) `
        -Label 'Check assembled managed-recipe manifest'
    if ($builderCheck -eq 1) {
        Write-Host '[preflight] The assembled manifest is stale; rebuilding deterministic artifacts.' -ForegroundColor Yellow
        Invoke-PythonTool `
            -Python $Python `
            -Script $builder `
            -Arguments $builderArguments `
            -Label 'Rebuild assembled managed-recipe manifest' | Out-Null
    }
    Invoke-PythonTool `
        -Python $Python `
        -Script $builder `
        -Arguments ($builderArguments + @('--check')) `
        -Label 'Recheck assembled managed-recipe manifest' | Out-Null

    $generatedCheck = Invoke-PythonTool `
        -Python $Python `
        -Script $generator `
        -Arguments @('--check') `
        -AllowedExitCodes @(0, 1) `
        -Label 'Check generated KJSGen managed project'
    if ($generatedCheck -eq 1) {
        Write-Host '[preflight] The generated KJSGen project is stale; rebuilding it.' -ForegroundColor Yellow
        Invoke-PythonTool `
            -Python $Python `
            -Script $generator `
            -Label 'Generate KJSGen managed project' | Out-Null
    }
    Invoke-PythonTool `
        -Python $Python `
        -Script $generator `
        -Arguments @('--check') `
        -Label 'Recheck generated KJSGen managed project' | Out-Null

    Invoke-PythonTool `
        -Python $Python `
        -Script $recipeFormPolicyAudit `
        -Arguments @('--catalog', $RuntimeItemCatalogPath, '--check') `
        -Label 'Validate functional-block versus component recipe-form policy' | Out-Null

    # Keep the complete manifest/compiler pair authoritative for design and
    # dependency validation, then derive the deployable fragment through the
    # frozen review acceptance.  Unchanged rejected cards must never leak back
    # into the live project merely because the raw compiler still emits them.
    $reviewAcceptanceArguments = @(
        '--acceptance', (Join-Path $Root 'progression\recipe_review_acceptance.json'),
        '--previous-reviewed', (Join-Path $Root 'pack-kjsgen\default.reviewed.managed.json'),
        '--next-managed', (Join-Path $Root 'pack-kjsgen\default.managed.json'),
        '--next-manifest', (Join-Path $Root 'progression\managed_recipe_overhaul.json'),
        '--output-reviewed', (Join-Path $Root 'pack-kjsgen\default.reviewed.managed.json'),
        '--output-ownership-manifest', (Join-Path $Root 'progression\reviewed_ownership_manifest.json'),
        '--report', (Join-Path $Root 'progression\recipe_review_reconciliation_report.json')
    )
    $reviewedCheck = Invoke-PythonTool `
        -Python $Python `
        -Script $reviewAcceptanceReconciler `
        -Arguments ($reviewAcceptanceArguments + @('--check')) `
        -AllowedExitCodes @(0, 1) `
        -Label 'Check reconciled reviewed KJSGen deployment fragment'
    if ($reviewedCheck -eq 1) {
        Write-Host '[preflight] The reviewed KJSGen deployment fragment is stale; rebuilding it from the frozen acceptance.' -ForegroundColor Yellow
        Invoke-PythonTool `
            -Python $Python `
            -Script $reviewAcceptanceReconciler `
            -Arguments $reviewAcceptanceArguments `
            -Label 'Reconcile reviewed KJSGen deployment fragment' | Out-Null
    }
    Invoke-PythonTool `
        -Python $Python `
        -Script $reviewAcceptanceReconciler `
        -Arguments ($reviewAcceptanceArguments + @('--check')) `
        -Label 'Recheck reconciled reviewed KJSGen deployment fragment' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $defaultRestorationValidator `
        -Label 'Validate reviewed default-recipe restoration and ownership parity' | Out-Null

    # Current recipe-review profile.  These tests audit the redesign modules
    # and complete rejected-card disposition rather than freezing superseded
    # intermediate recipe shapes from earlier phases.
    foreach ($testScript in $recipeDesignV4Tests) {
        Invoke-PythonTool `
            -Python $Python `
            -Script $testScript `
            -Label "Run current recipe-design v4 contract: $(Split-Path -Leaf $testScript)" | Out-Null
    }
    Invoke-PythonTool `
        -Python $Python `
        -Script $rejectedResolutionCoverageTests `
        -Label 'Validate complete rejected-recipe resolution coverage' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $defaultRestorationTests `
        -Label 'Mutation-test exact reviewed default-recipe restoration' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $v3SteelFrameTests `
        -Label 'Validate canonical TFMG steel-frame policy' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $v3SourcePolicyAudit `
        -Arguments @('--seed', (Join-Path $Root 'progression\managed_recipe_overhaul.seed.json'), '--catalog', (Join-Path $RecipeCatalogPath 'recipe_catalog.sqlite')) `
        -Label 'Audit the current strict v3 source policy' | Out-Null

    $questCheck = Invoke-PythonTool `
        -Python $Python `
        -Script $questGenerator `
        -Arguments @('--check') `
        -AllowedExitCodes @(0, 1) `
        -Label 'Check generated FTB Quests guidance campaign'
    if ($questCheck -eq 1) {
        Write-Host '[preflight] The generated FTB Quests campaign is stale; rebuilding it.' -ForegroundColor Yellow
        Invoke-PythonTool `
            -Python $Python `
            -Script $questGenerator `
            -Label 'Generate FTB Quests guidance campaign' | Out-Null
    }
    Invoke-PythonTool `
        -Python $Python `
        -Script $questGenerator `
        -Arguments @('--check') `
        -Label 'Recheck generated FTB Quests guidance campaign' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $questValidator `
        -Arguments @('--item-catalog', $RuntimeItemCatalogPath, '--recipe-catalog', $RecipeCatalogPath, '--instance', $LiveRoot) `
        -Label 'Validate FTB Quests item guidance and capstone identity' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $postDieselQuestValidator `
        -Arguments @('--manifest', (Join-Path $Root 'progression\managed_recipe_overhaul.json'), '--items', $RuntimeItemCatalogPath, '--recipes', (Join-Path $RecipeCatalogPath 'recipes.csv')) `
        -Label 'Validate the post-Diesel factory-guidance campaign and cross-chapter DAG' | Out-Null

    Invoke-PythonTool `
        -Python $Python `
        -Script $overhaulValidator `
        -Label 'Validate managed-recipe schema, compiler parity, and dependency graph' | Out-Null
    Write-Host '[preflight] Mutation-test KJSGen three-way merge and native slot-default normalization'
    & (Resolve-ExistingFile -Path $kjsGenMergeTests -Label 'KJSGen merge tests script') | Out-Host
    Invoke-PythonTool `
        -Python $Python `
        -Script $orphanRetirementTests `
        -Label 'Mutation-test fail-closed KJSGen orphan retirement and user-card preservation' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $autoExportValidator `
        -Label 'Validate unattended marker-safe KJSGen export' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $mekanismInfusingCodegenValidator `
        -Label 'Validate Mekanism metallurgic-infusing KJSGen code generation' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $mekanismInfusingCodegenTests `
        -Label 'Mutation-test explicit Mekanism metallurgic-infusing recipe IDs' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $tfmgChemicalVatValidator `
        -Arguments @('--project', $Root, '--mods', $ModsRoot, '--project-jar', $ProjectJarPath) `
        -Label 'Validate the KJSGen TFMG Chemical Vat editor and compiler' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $tfmgChemicalVatTests `
        -Label 'Mutation-test the KJSGen TFMG Chemical Vat contract' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $canonicalValidator `
        -Arguments @($LiveRoot, '--project', $Root, '--skip-installed-parity') `
        -Label 'Validate TFMG-first canonical materials and fuels' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $allthemodiumValidator `
        -Label 'Validate manufactured Allthemodium currency and physical consumer closure' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $spaceEntryValidator `
        -Arguments @('--project', $Root, '--catalog', $RecipeCatalogPath) `
        -Label 'Validate the post-Star space-entry and canonical-propellant boundary' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $spaceEntryTests `
        -Label 'Mutation-test the post-Star space-entry boundary' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $spaceDestinationValidator `
        -Arguments @('--project', $Root, '--mods', $ModsRoot) `
        -Label 'Validate canonical Moon/Mars destinations, ship physics, and installed textures' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $spaceDestinationTests `
        -Label 'Mutation-test the canonical Moon/Mars destination bridge' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $orbitalFlightGateValidator `
        -Arguments @('--project', $Root, '--mods', $ModsRoot, '--project-jar', $ProjectJarPath) `
        -Label 'Validate the physical Orbital Flight Computer gate and deployment JAR assets' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $orbitalFlightGateTests `
        -Label 'Mutation-test the physical Orbital Flight Computer gate' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $orbitalAmbientKineticsValidator `
        -Arguments @('--project', $Root, '--mods', $ModsRoot, '--project-jar', $ProjectJarPath) `
        -Label 'Validate dimension-scoped orbital wind and water suppression' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $orbitalAmbientKineticsTests `
        -Label 'Mutation-test the orbital ambient-kinetic boundary' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $planetaryFreightGateValidator `
        -Arguments @('--project', $Root, '--mods', $ModsRoot, '--project-jar', $ProjectJarPath) `
        -Label 'Validate the Mars route-computer and offworld Ender Chest freight gates' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $planetaryFreightGateTests `
        -Label 'Mutation-test the planetary freight gates' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $planetaryStructureBuilder `
        -Arguments @('--mods', $ModsRoot, '--check') `
        -Label 'Verify deterministic Desh/Ostrum structure bypass overrides' | Out-Null

    # Late-slice validators that freeze superseded recipe shapes are deliberately
    # omitted. Reviewed reconciliation, the v4 recipe suites, and generic
    # manifest/compiler validation are authoritative for current recipe cards.
    Invoke-PythonTool `
        -Python $Python `
        -Script $tieredMegaprojectSequenceTests `
        -Label 'Mutation-test exact-machine routing in tiered megaproject sequences' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $nuclearValidator `
        -Arguments @($LiveRoot, '--project', $Root) `
        -Label 'Validate nuclear chemistry boundaries' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $capstoneReachabilityValidator `
        -Arguments @('--project', $Root, '--catalog', $RecipeCatalogPath, '--mods', $ModsRoot) `
        -Label 'Validate physical actinide-to-capstone reachability' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $capstoneReachabilityTests `
        -Label 'Mutation-test the actinide-to-capstone reachability boundary' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $foodDiversityValidator `
        -Label 'Validate bounded persistent food-diversity progression' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $ae2TransformValidator `
        -Label 'Validate AE2 and AppMek transform hardening' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $bypassRetirementValidator `
        -Label 'Validate exact retirement of confirmed progression bypasses' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $primitiveToolValidator `
        -Label 'Validate primitive and modular tool progression' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $dungeonToolLootValidator `
        -Arguments @('--instance', $LiveRoot) `
        -Label 'Validate dungeon tool-loot progression' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $dungeonExplorationValidator `
        -Arguments @('--instance', $LiveRoot) `
        -Label 'Validate optional dungeon structures and non-gating exploration routes' | Out-Null
    Invoke-PythonTool `
        -Python $Python `
        -Script $regionalOilValidator `
        -Arguments @('--project', $Root, '--instance', $LiveRoot) `
        -Label 'Validate regional finite TFMG oil and duplicate-extractor retirement' | Out-Null

    Write-Host '[preflight] Managed-recipe pipeline passed.' -ForegroundColor Green
}

function Add-CopyPlanItem {
    param(
        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [System.Collections.Generic.List[object]] $Plan,

        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [System.Collections.Generic.HashSet[string]] $Destinations,

        [Parameter(Mandatory)]
        [string] $Source,

        [Parameter(Mandatory)]
        [string] $Destination,

        [Parameter(Mandatory)]
        [string] $Reason,

        [Parameter()]
        [object] $ExpectedSourceState,

        [Parameter()]
        [object] $ExpectedDestinationState
    )

    $sourceFull = Resolve-ExistingFile -Path $Source -Label "$Reason source"
    $destinationFull = [System.IO.Path]::GetFullPath($Destination)
    if (-not $Destinations.Add($destinationFull)) {
        throw "Deployment plan contains duplicate destination: $destinationFull"
    }

    if ($null -eq $ExpectedSourceState) {
        $ExpectedSourceState = Get-PinnedFileState -Path $sourceFull
    }
    if ($null -eq $ExpectedDestinationState) {
        $ExpectedDestinationState = Get-PinnedFileState -Path $destinationFull
    }
    Assert-PinnedFileState -Expected $ExpectedSourceState -Label "$Reason source"
    Assert-PinnedFileState -Expected $ExpectedDestinationState -Label "$Reason destination"

    $type = if (Test-SameFileContent -Left $sourceFull -Right $destinationFull) {
        'GuardOnly'
    }
    else {
        'Copy'
    }
    $Plan.Add([pscustomobject]@{
        Type = $type
        Source = $sourceFull
        Destination = $destinationFull
        Reason = $Reason
        ExpectedSourceState = $ExpectedSourceState
        ExpectedDestinationState = $ExpectedDestinationState
    })
}

function Get-OrdinaryDeploymentSourcePaths {
    param(
        [Parameter(Mandatory)]
        [string] $ProjectJarPath,

        [Parameter(Mandatory)]
        [string] $ServerRoot,

        [Parameter(Mandatory)]
        [string] $ClientRoot,

        [Parameter(Mandatory)]
        [string[]] $ConfigFiles,

        [Parameter()]
        [AllowNull()]
        [string] $QuestRoot
    )

    $paths = [System.Collections.Generic.List[string]]::new()
    $paths.Add([System.IO.Path]::GetFullPath($ProjectJarPath))
    foreach ($path in $ConfigFiles) {
        $paths.Add([System.IO.Path]::GetFullPath($path))
    }
    foreach ($file in Get-ChildItem -LiteralPath $ServerRoot -File -Recurse) {
        $paths.Add($file.FullName)
    }
    foreach ($file in Get-ChildItem -LiteralPath $ClientRoot -File -Recurse) {
        $paths.Add($file.FullName)
    }
    if (-not [string]::IsNullOrWhiteSpace($QuestRoot) -and
        (Test-Path -LiteralPath $QuestRoot -PathType Container)) {
        foreach ($file in Get-ChildItem -LiteralPath $QuestRoot -File -Recurse) {
            $paths.Add($file.FullName)
        }
    }
    return @($paths | Sort-Object)
}

function Write-AcceptanceChecklist {
    param(
        [Parameter(Mandatory)]
        [int] $ServerScriptCount,

        [Parameter(Mandatory)]
        [int] $ClientScriptCount,

        [Parameter(Mandatory)]
        [int] $QuestFileCount,

        [Parameter()]
        [Nullable[int]] $RecipeStageCount
    )

    Write-Host ''
    Write-Host 'Runtime acceptance checklist:' -ForegroundColor Cyan
    Write-Host '[ ] Launch the CurseForge profile and load Industrial Colonies Runtime Test (not the old New World).'
    Write-Host '[ ] MineColonies University research does not lock, hide, or authorize any factory recipe.'
    Write-Host "[ ] FTB Quests contains 70 physical-guidance quests across six factory chapters, the preserved three-item capstone chain, the 12-quest optional Dungeon Expeditions chapter, ten post-Star Orbital Engineering observations, and 29 Planetary Industry observations ($QuestFileCount deployed quest files)."
    Write-Host "[ ] KubeJS loads with zero script errors/warnings ($ServerScriptCount owned server scripts; $ClientScriptCount owned client scripts)."
    Write-Host '[ ] Industrial Colonies initializes without research-stage synchronization or recipe-gate errors.'
    Write-Host '[ ] No BetterChunkLoading/C2ME mixin exception appears.'
    Write-Host '[ ] Managed AE2, ComputerCraft, Mekanism, TFMG, and reactor items show their new factory recipes without duplicate stock paths.'
    Write-Host '[ ] The Crystal Resonance Generator has no recipe; Chunk Controller and Dimensional Stabilizer show only their powered 5x5 builds.'
    Write-Host '[ ] FTB Chunks land claiming/protection still works, but ordinary teams have zero free force-loaded chunks.'
    Write-Host '[ ] The existing kubejs/server_scripts/kjsgen_recipes.js still contains the user-authored recipes.'
    Write-Host '[ ] KJSGen Project > default still contains every user-authored recipe/removal plus any source-managed visual recipes.'
    Write-Host '[ ] KJSGen Project > default contains exactly one managed card each for Hose Anchor, Engine Cycle Pipes, Engine Nozzle, and Thruster Mount.'
    Write-Host '[ ] JEI shows those four modular propulsion recipes while the stock Rocket Thruster, Booster Thruster, Jetpack, and Physics Assembler recipes remain absent.'
    Write-Host '[ ] KJSGen Project > default contains exactly one managed 5x5 card each for Fan, Gas Tank, Large Gas Tank, Oxygen Gear, Oxygen Loader, Oxygen Distributor, Oxygen Sensor, Vent, and Airlock.'
    Write-Host '[ ] JEI shows only the managed recipes for those nine Ad Astra life-support outputs; Mekanism oxygen loads successfully while direct Ad Astra water-to-oxygen loading remains absent.'
    Write-Host '[ ] KJSGen Project > default contains three Refined Radiance Deployer certification cards with Keep Held Item enabled and one 5x5 Physics Assembler card.'
    Write-Host '[ ] The Orbital Flight Computer, Thruster Mount, and Airlock remain after certification; JEI shows only the authored Contraption Diagram and Physics Assembler routes.'
    Write-Host '[ ] Runtime debug.log shows SpaceTransitionHandlerMixin and DeepSpaceInstanceMixin applied to their exact Cosmonautics targets and both ambient-kinetic Mixins applied to the exact Create 6.0.10 targets, with no owned Mixin failure.'
    Write-Host '[ ] In every denied Ad Astra surface/orbit dimension and Rocketnautics deep space, Create water wheels and windmill bearings produce 0 RPM; the same generators still work in minecraft:overworld, including on terrestrial Sable vehicles.'
    Write-Host '[ ] Ender Chests open normally on Earth but cannot open in any managed Ad Astra surface/orbit or Rocketnautics deep-space dimension, including an inherited menu carried through a transition.'
    Write-Host '[ ] Moon descent remains unchanged; Mars descent fails without a placed Mars Navigation Computer on every occupied ship and succeeds once every occupied ship carries one.'
    Write-Host '[ ] JEI shows only the managed Desh/Ostrum grit, enrichment, vat reduction, Refined Radiance plate, and Mars Navigation Computer routes; direct ore/raw smelting and alternate plate presses remain absent.'
    Write-Host '[ ] KJSGen Project > default contains exactly one managed 5x5 card each for the four-panel Solar Array batch, Water Pump, Gravity Normalizer, Energizer, and Nutritional Liquifier.'
    Write-Host '[ ] FTB Quests Planetary Industry observes Moon/Mars arrival, both metallurgy lines, the Desh utility array, the joined Ostrum service reserve, and closed-loop rations without consuming items or granting rewards/stages.'
    Write-Host '[ ] Venus descent fails without a placed Venus Navigation Computer on every occupied ship or when any associated player lacks correctly slotted heat-resistant head, chest, leg, or foot armor; Venus authority also satisfies the earlier Mars route check.'
    Write-Host '[ ] JEI shows only the managed Netherite Space Suit fabrication and Calorite grit, enrichment, firebrick-vat acid leaching, superheated two-electrode reduction, and Refined Radiance plate routes; all 20 audited stock/alternate shortcuts remain absent.'
    Write-Host '[ ] Mercury descent fails without a placed Mercury Navigation Computer on every occupied loaded ship and succeeds once each occupied ship carries one; Mercury authority satisfies Mars/Venus routes while Venus heat-suit checks remain active.'
    Write-Host '[ ] Rocketnautics asteroids spawn only in canonical rocketnautics:deep_space through DeepSpaceHelper.isDeepSpace; high-Y non-deep-space locations no longer qualify.'
    Write-Host '[ ] FTB Quests Planetary Industry ends with Mercury arrival, returned Mercury Iron Ore, first asteroid Titanium Ore, and the retained five-ore bulk freight reserve; all observations consume nothing and grant no rewards/stages.'
    Write-Host '[ ] The titanium washing-to-Netherite Scrap shortcut remains absent; Create crushing for Mercury Iron Ore and asteroid Titanium Ore remains available.'
    Write-Host '[ ] The exact 35-ID post-Star space boundary remains active; managed Sputnik ownership has no second boundary removal and no broad Ad Astra, Cosmonautics, Simulated, or Cosmowarp recipe wipe is present.'
    Write-Host '[ ] KJSGen shows one editor entry per supported Create process, not the former 170 tier/process entries.'
    Write-Host '[ ] Create Pressing opens with an actual compatible press selector at the upper-left of the recipe canvas.'
    Write-Host '[ ] The selected press is routing metadata: it is absent from the ingredient list and is not consumed.'
    Write-Host '[ ] A Copper Press recipe runs only in createcasing:copper_press, not the normal press or another encased press.'
    Write-Host '[ ] A recipe explicitly assigned to the normal Mechanical Press runs only in that base press.'
    Write-Host '[ ] JEI shows the Copper Press/Deployer model and required-machine cue for a recipe bound to that exact machine.'
    Write-Host '[ ] JEI still shows the normal Create machine for native recipes that have no exact-machine binding.'
    Write-Host '[ ] Native stock Create processing recipes remain usable in their normal machines.'
    Write-Host '[ ] New dry-biome TFMG oil fields are finite; CDG engines remain usable but its duplicate Pumpjack finds no independent oil reserve.'
    Write-Host '[ ] Dungeon Crawl and other early dungeon tools appear as worn exploration finds rather than pristine progression skips.'
    Write-Host '[ ] Only managed exact-ID replacements plus retained canonicalization, compatibility, currency, and capstone rules alter the stock baseline; no broad wipe is active.'
    Write-Host '[ ] /give @s industrial_colonies:yellorium_compound succeeds.'
    Write-Host '[ ] Yellorite/raw Yellorium has no furnace or blast-furnace route to Mekanism uranium.'
    Write-Host '[ ] No uranium or finished reactor-fuel recipe converts backward into Yellorium.'
    Write-Host '[ ] FTB Quests opens normally with ten chapters and 124 total quests (70 factory guidance, three capstones, 12 optional dungeon expeditions, ten Orbital Engineering observations, and 29 Planetary Industry observations), without a research-tree mirror.'
    Write-Host '[ ] A Sable SHIP and STATION each require 600 continuous powered, TFMG-cooled, oxygen-covered ticks before commissioning; breaking or unloading the sole controller decommissions immediately.'
    Write-Host '[ ] Only a commissioned STATION in the verified gas-giant CUBE shell produces one bucket of condensate per uninterrupted 400-tick powered/cooled cycle.'
    Write-Host '[ ] Gas-Giant Condensate has no crafting shortcut; eight physically returned buckets are consumed by the 5x5 Warp Charge Precursor recipe.'
    Write-Host '[ ] Proxima Centauri owns exactly one Glacio surface bridge, ad_astra:glacio_orbit remains unlinked, and canonical lunar wastelands generate the source-owned Moon Crystal ore without replacing Cosmowarp stock worldgen.'
    Write-Host '[ ] JEI/KJSGen shows exactly the five reviewed interstellar routes: Moon Crystal polishing, two 5x5 computers/crystals, the 5x5 Warp Drive, and the two-loop physical Warp Charge sequence; only the three exact stock recipes are removed.'
    Write-Host '[ ] A placed Interstellar Navigation Computer signs only the exact immutable Sol-Glacio route; stock registration, copies, cards, arbitrary points, unsigned crystals, and ordinary deep-space Glacio descent grant no travel authority.'
    Write-Host '[ ] Warp START works only for the exact authorized onboard sender on one commissioned/live Sable SHIP with one drive, one physical computer, the exact occupants, no active contraptions or non-player cargo, a clear destination, and correctly slotted freeze armor inbound to Glacio.'
    Write-Host '[ ] Route/crystal/passenger/metadata/resource/destination changes during charge abort before copy; every cached crystal capability remains frozen, and exactly one factory Warp Charge is consumed only after stock beginWarp succeeds.'
    Write-Host '[ ] Before stock WarpSubLevel, destination IDs are snapshotted under a fail-closed guard and the removal scope starts; a copy exception is logged before source identity is probed, any probe failure leaves rollback disabled, and destination cleanup plus independent crew restoration occur only inside the proven-pristine branch. The scope always clears in finally and successful copy preserves the complete unrelated Sable user-data root.'
    Write-Host '[ ] Planetary Industry ends with exactly seven observation-only interstellar quests through Glacio arrival and returned Glacio ore; none grants rewards, stages, recipes, consumption, prefab spawning, or teleport authority.'
    Write-Host '[ ] The fresh world saves cleanly.'
}

$projectRootResolved = Resolve-ExistingDirectory -Path $ProjectRoot -Label 'Project root'
$liveRootResolved = Resolve-ExistingDirectory -Path $LivePackRoot -Label 'Live pack root'
$projectJarResolved = Resolve-ExistingFile -Path $ProjectJar -Label 'Project JAR'

if ($projectRootResolved.Equals($liveRootResolved, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Project root and live pack root must be different directories.'
}
Assert-ChildPath -Parent $projectRootResolved -Child $projectJarResolved -Label 'Project JAR'
if ([System.IO.Path]::GetExtension($projectJarResolved) -ne '.jar') {
    throw "Project JAR does not end in .jar: $projectJarResolved"
}

$serverSourceRoot = Resolve-ExistingDirectory -Path (Join-Path $projectRootResolved 'pack-scripts\server_scripts') -Label 'Server script source'
$clientSourceRoot = Resolve-ExistingDirectory -Path (Join-Path $projectRootResolved 'pack-scripts\client_scripts') -Label 'Client script source'
$kjsGenMergeTool = Resolve-ExistingFile -Path (Join-Path $projectRootResolved 'tools\merge_kjsgen_project.ps1') -Label 'KJSGen project merge tool'
$extremeReactorsSource = Resolve-ExistingFile -Path (Join-Path $projectRootResolved 'pack-config-overrides\ExtremeReactors\modpack_api.json') -Label 'Extreme Reactors modpack API source'
$createAppliedKineticsSource = Resolve-ExistingFile -Path (Join-Path $projectRootResolved 'pack-config-overrides\createappliedkinetics-common.toml') -Label 'Create Applied Kinetics config source'
$ftbChunksSource = Resolve-ExistingFile -Path (Join-Path $projectRootResolved 'pack-config-overrides\ftbchunks-world.snbt') -Label 'FTB Chunks modpack-default source'
$questSourceCandidate = [System.IO.Path]::GetFullPath((Join-Path $projectRootResolved 'pack-config-overrides\ftbquests\quests'))
$questSourceRoot = $null
if (Test-Path -LiteralPath $questSourceCandidate -PathType Container) {
    $questSourceRoot = Resolve-ExistingDirectory -Path $questSourceCandidate -Label 'FTB Quests source tree'
}

$modsRoot = Resolve-ExistingDirectory -Path (Join-Path $liveRootResolved 'mods') -Label 'Live mods directory'
$kubeJsRoot = Resolve-ExistingDirectory -Path (Join-Path $liveRootResolved 'kubejs') -Label 'Live KubeJS directory'
$configRoot = Resolve-ExistingDirectory -Path (Join-Path $liveRootResolved 'config') -Label 'Live config directory'
$serverDestinationRoot = [System.IO.Path]::GetFullPath((Join-Path $kubeJsRoot 'server_scripts'))
$clientDestinationRoot = [System.IO.Path]::GetFullPath((Join-Path $kubeJsRoot 'client_scripts'))
$extremeReactorsDestination = [System.IO.Path]::GetFullPath((Join-Path $configRoot 'extremereactors\modpack_api.json'))
$createAppliedKineticsDestination = [System.IO.Path]::GetFullPath((Join-Path $configRoot 'createappliedkinetics-common.toml'))
$ftbChunksDestination = [System.IO.Path]::GetFullPath((Join-Path $configRoot 'ftbchunks-world.snbt'))
$questDestinationRoot = [System.IO.Path]::GetFullPath((Join-Path $configRoot 'ftbquests\quests'))
$kjsGenProjectDestination = [System.IO.Path]::GetFullPath((Join-Path $liveRootResolved 'kjsgen\projects\default.json'))
$kjsGenBaselineDestination = [System.IO.Path]::GetFullPath((
    Join-Path $liveRootResolved 'kjsgen\industrial_colonies_sync\default.managed.baseline.json'
))
$destinationJar = [System.IO.Path]::GetFullPath((Join-Path $modsRoot (Split-Path -Leaf $projectJarResolved)))

foreach ($target in @($serverDestinationRoot, $clientDestinationRoot, $extremeReactorsDestination, $createAppliedKineticsDestination, $ftbChunksDestination, $questDestinationRoot, $kjsGenProjectDestination, $kjsGenBaselineDestination, $destinationJar)) {
    Assert-ChildPath -Parent $liveRootResolved -Child $target -Label 'Live deployment target'
}

Assert-MinecraftStopped -LiveRoot $liveRootResolved

$pythonCommand = Resolve-PythonCommand -RequestedExecutable $PythonExecutable
$recipeCatalogResolved = Resolve-RecipeCatalogDirectory `
    -Root $projectRootResolved `
    -RequestedPath $RecipeCatalog
$runtimeItemCatalogResolved = Resolve-RuntimeItemCatalogFile `
    -Root $projectRootResolved `
    -RequestedPath $RuntimeItemCatalog
Write-Host "Python preflight runtime: $($pythonCommand.DisplayName)"
Write-Host "Static recipe catalog: $recipeCatalogResolved"
Write-Host "Runtime item catalog: $runtimeItemCatalogResolved"
$ordinarySourceParameters = @{
    ProjectJarPath = $projectJarResolved
    ServerRoot = $serverSourceRoot
    ClientRoot = $clientSourceRoot
    ConfigFiles = @($extremeReactorsSource, $createAppliedKineticsSource, $ftbChunksSource)
    QuestRoot = $questSourceRoot
}
$ordinarySourcePaths = @(Get-OrdinaryDeploymentSourcePaths @ordinarySourceParameters)
$validatedOrdinarySourceStates = @(Get-PinnedFileSet -Paths $ordinarySourcePaths)
$runManagedPreflight = {
    Invoke-ManagedRecipePreflight `
        -Root $projectRootResolved `
        -LiveRoot $liveRootResolved `
        -ModsRoot $modsRoot `
        -ProjectJarPath $projectJarResolved `
        -Python $pythonCommand `
        -RecipeCatalogPath $recipeCatalogResolved `
        -RuntimeItemCatalogPath $runtimeItemCatalogResolved
}
& $runManagedPreflight

$preflightRegeneratedSources = $false
try {
    Assert-PinnedFileSet `
        -Expected $validatedOrdinarySourceStates `
        -CurrentPaths @(Get-OrdinaryDeploymentSourcePaths @ordinarySourceParameters) `
        -Label 'Ordinary deployment source validated by preflight'
}
catch {
    $preflightRegeneratedSources = $true
    Write-Host (
        '[preflight] A generated deployable source changed during the first validation pass; ' +
        'rerunning the complete preflight against its final bytes.'
    ) -ForegroundColor Yellow
}
if ($preflightRegeneratedSources) {
    $ordinarySourcePaths = @(Get-OrdinaryDeploymentSourcePaths @ordinarySourceParameters)
    $validatedOrdinarySourceStates = @(Get-PinnedFileSet -Paths $ordinarySourcePaths)
    & $runManagedPreflight
    Assert-PinnedFileSet `
        -Expected $validatedOrdinarySourceStates `
        -CurrentPaths @(Get-OrdinaryDeploymentSourcePaths @ordinarySourceParameters) `
        -Label 'Ordinary deployment source validated by stable preflight'
}
$validatedOrdinaryStateByPath = [System.Collections.Generic.Dictionary[string, object]]::new(
    [System.StringComparer]::OrdinalIgnoreCase
)
foreach ($state in $validatedOrdinarySourceStates) {
    if (-not $validatedOrdinaryStateByPath.TryAdd([string] $state.Path, $state)) {
        throw "Validated ordinary deployment source repeats path: $($state.Path)"
    }
}

# Resolve this reviewed source only after the fail-closed raw compiler and
# review-reconciliation pipelines have rebuilt it when necessary and verified
# deterministic parity.
$kjsGenManagedSource = Resolve-ExistingFile `
    -Path (Join-Path $projectRootResolved 'pack-kjsgen\default.reviewed.managed.json') `
    -Label 'Reviewed managed KJSGen project fragment'
$managedRecipeManifestPath = Resolve-ExistingFile `
    -Path (Join-Path $projectRootResolved 'progression\managed_recipe_overhaul.json') `
    -Label 'Raw managed recipe manifest'
$reviewedOwnershipManifestPath = Resolve-ExistingFile `
    -Path (Join-Path $projectRootResolved 'progression\reviewed_ownership_manifest.json') `
    -Label 'Reviewed KJSGen ownership manifest'
$kjsGenRetirementLedgerPath = Resolve-ExistingFile `
    -Path (Join-Path $projectRootResolved 'progression\kjsgen_orphan_retirement_ledger.json') `
    -Label 'KJSGen orphan-retirement ledger'
$kjsGenManagedValidatedState = Get-PinnedFileState -Path $kjsGenManagedSource
$managedRecipeManifestValidatedState = Get-PinnedFileState -Path $managedRecipeManifestPath
$reviewedOwnershipManifestValidatedState = Get-PinnedFileState -Path $reviewedOwnershipManifestPath
$kjsGenRetirementLedgerValidatedState = Get-PinnedFileState -Path $kjsGenRetirementLedgerPath

$kjsGenMergedSource = [System.IO.Path]::GetFullPath(
    (Join-Path $projectRootResolved 'build\generated\kjsgen\default.json')
)
$kjsGenNextBaselineSource = [System.IO.Path]::GetFullPath(
    (Join-Path $projectRootResolved 'build\generated\kjsgen\default.managed.baseline.json')
)
$kjsGenOrphanAuditSource = [System.IO.Path]::GetFullPath(
    (Join-Path $projectRootResolved 'build\generated\kjsgen\orphan-retirement-audit.json')
)
Assert-ChildPath -Parent $projectRootResolved -Child $kjsGenMergedSource -Label 'Generated KJSGen merge output'
Assert-ChildPath -Parent $projectRootResolved -Child $kjsGenNextBaselineSource -Label 'Generated KJSGen baseline output'
Assert-ChildPath -Parent $projectRootResolved -Child $kjsGenOrphanAuditSource -Label 'Generated KJSGen orphan-retirement audit'
$kjsGenProjectMergeInputState = Get-PinnedFileState -Path $kjsGenProjectDestination
$kjsGenBaselineMergeInputState = Get-PinnedFileState -Path $kjsGenBaselineDestination
Assert-PinnedFileState -Expected $kjsGenManagedValidatedState -Label 'Validated reviewed KJSGen fragment'
& $kjsGenMergeTool `
    -ManagedSource $kjsGenManagedSource `
    -ExistingBaseline $kjsGenBaselineDestination `
    -ExistingProject $kjsGenProjectDestination `
    -OutputProject $kjsGenMergedSource `
    -OutputBaseline $kjsGenNextBaselineSource
Assert-PinnedFileState `
    -Expected $kjsGenProjectMergeInputState `
    -Label 'Live KJSGen project used as the merge input'
Assert-PinnedFileState `
    -Expected $kjsGenBaselineMergeInputState `
    -Label 'Live KJSGen baseline used as the merge input'
if ((Get-Sha256 -Path $kjsGenNextBaselineSource) -ne (Get-Sha256 -Path $kjsGenManagedSource)) {
    throw 'Generated KJSGen next baseline is not byte-identical to the validated reviewed source.'
}
$kjsGenNextBaselineValidatedState = Get-PinnedFileState -Path $kjsGenNextBaselineSource

# Earlier deployment baselines did not carry tombstones for several generations
# of source-authored cards. Retire only the complete, hash-matched cards proven
# by the immutable migration ledger; any live edit blocks deployment before a
# live file is touched.
Invoke-PythonTool `
    -Python $pythonCommand `
    -Script (Join-Path $projectRootResolved 'tools\sanitize_kjsgen_orphans.py') `
    -Arguments @('--staged', $kjsGenMergedSource, '--managed', $kjsGenManagedSource, '--ledger', $kjsGenRetirementLedgerPath, '--require-reviewed-ledger', '--report', $kjsGenOrphanAuditSource) `
    -Label 'Retire only ledger-proven obsolete reviewed-managed KJSGen cards from the staged project' | Out-Null
$kjsGenMergedValidatedState = Get-PinnedFileState -Path $kjsGenMergedSource

# The merge deliberately preserves user-authored cards, so verify the actual
# staged project against the reviewed deployment ownership rather than against
# the larger raw compiler manifest.
Invoke-PythonTool `
    -Python $pythonCommand `
    -Script (Join-Path $projectRootResolved 'tools\validate_staged_kjsgen_project.py') `
    -Arguments @('--managed', $kjsGenManagedSource, '--staged', $kjsGenMergedSource, '--manifest', $reviewedOwnershipManifestPath) `
    -Label 'Protect active reviewed ownership while preserving user KJSGen cards in the staged project' | Out-Null

# The generic staged validator above checks the reconciled reviewed ownership.
# Re-running superseded late-slice shape contracts here would reject approved
# cards after a correct three-way merge.
Assert-PinnedFileState `
    -Expected $kjsGenMergedValidatedState `
    -Label 'Validated merged KJSGen project'
Assert-PinnedFileState `
    -Expected $kjsGenNextBaselineValidatedState `
    -Label 'Validated KJSGen next baseline'
Assert-PinnedFileState `
    -Expected $kjsGenManagedValidatedState `
    -Label 'Validated reviewed KJSGen fragment'
Assert-PinnedFileState `
    -Expected $managedRecipeManifestValidatedState `
    -Label 'Validated raw managed recipe manifest'
Assert-PinnedFileState `
    -Expected $reviewedOwnershipManifestValidatedState `
    -Label 'Validated reviewed KJSGen ownership manifest'
Assert-PinnedFileState `
    -Expected $kjsGenRetirementLedgerValidatedState `
    -Label 'Validated KJSGen orphan-retirement ledger'
Assert-PinnedFileSet `
    -Expected $validatedOrdinarySourceStates `
    -CurrentPaths @(Get-OrdinaryDeploymentSourcePaths @ordinarySourceParameters) `
    -Label 'Ordinary deployment source after staged KJSGen validation'

$serverSources = @(Get-ChildItem -LiteralPath $serverSourceRoot -File -Recurse | Sort-Object FullName)
$clientSources = @(Get-ChildItem -LiteralPath $clientSourceRoot -File -Recurse | Sort-Object FullName)
$questSources = @()
if ($null -ne $questSourceRoot) {
    $questSources = @(Get-ChildItem -LiteralPath $questSourceRoot -File -Recurse | Sort-Object FullName)
}
if ($serverSources.Count -eq 0) {
    throw 'No project server scripts were found.'
}
if ($clientSources.Count -eq 0) {
    throw 'No project client scripts were found.'
}

$plan = [System.Collections.Generic.List[object]]::new()
$plannedDestinations = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

Add-CopyPlanItem `
    -Plan $plan `
    -Destinations $plannedDestinations `
    -Source $projectJarResolved `
    -Destination $destinationJar `
    -Reason 'Industrial Colonies mod JAR' `
    -ExpectedSourceState $validatedOrdinaryStateByPath[$projectJarResolved]
Add-CopyPlanItem `
    -Plan $plan `
    -Destinations $plannedDestinations `
    -Source $kjsGenMergedSource `
    -Destination $kjsGenProjectDestination `
    -Reason 'Merged KJSGen default project' `
    -ExpectedSourceState $kjsGenMergedValidatedState `
    -ExpectedDestinationState $kjsGenProjectMergeInputState
Add-CopyPlanItem `
    -Plan $plan `
    -Destinations $plannedDestinations `
    -Source $kjsGenNextBaselineSource `
    -Destination $kjsGenBaselineDestination `
    -Reason 'KJSGen managed-project merge baseline' `
    -ExpectedSourceState $kjsGenNextBaselineValidatedState `
    -ExpectedDestinationState $kjsGenBaselineMergeInputState

foreach ($sourceFile in $serverSources) {
    $relative = Get-RelativeChildPath -Parent $serverSourceRoot -Child $sourceFile.FullName
    $destination = [System.IO.Path]::GetFullPath((Join-Path $serverDestinationRoot $relative))
    Assert-ChildPath -Parent $serverDestinationRoot -Child $destination -Label 'Server script destination'
    Add-CopyPlanItem `
        -Plan $plan `
        -Destinations $plannedDestinations `
        -Source $sourceFile.FullName `
        -Destination $destination `
        -Reason 'KubeJS server script' `
        -ExpectedSourceState $validatedOrdinaryStateByPath[$sourceFile.FullName]
}

foreach ($sourceFile in $clientSources) {
    $relative = Get-RelativeChildPath -Parent $clientSourceRoot -Child $sourceFile.FullName
    $destination = [System.IO.Path]::GetFullPath((Join-Path $clientDestinationRoot $relative))
    Assert-ChildPath -Parent $clientDestinationRoot -Child $destination -Label 'Client script destination'
    Add-CopyPlanItem `
        -Plan $plan `
        -Destinations $plannedDestinations `
        -Source $sourceFile.FullName `
        -Destination $destination `
        -Reason 'KubeJS client script' `
        -ExpectedSourceState $validatedOrdinaryStateByPath[$sourceFile.FullName]
}

Add-CopyPlanItem -Plan $plan -Destinations $plannedDestinations -Source $extremeReactorsSource -Destination $extremeReactorsDestination -Reason 'Extreme Reactors modpack_api.json' -ExpectedSourceState $validatedOrdinaryStateByPath[$extremeReactorsSource]
Add-CopyPlanItem -Plan $plan -Destinations $plannedDestinations -Source $createAppliedKineticsSource -Destination $createAppliedKineticsDestination -Reason 'Create Applied Kinetics Inscriber compatibility config' -ExpectedSourceState $validatedOrdinaryStateByPath[$createAppliedKineticsSource]
Add-CopyPlanItem -Plan $plan -Destinations $plannedDestinations -Source $ftbChunksSource -Destination $ftbChunksDestination -Reason 'FTB Chunks claims-enabled zero-force-load pack defaults' -ExpectedSourceState $validatedOrdinaryStateByPath[$ftbChunksSource]

foreach ($sourceFile in $questSources) {
    $relative = Get-RelativeChildPath -Parent $questSourceRoot -Child $sourceFile.FullName
    $destination = [System.IO.Path]::GetFullPath((Join-Path $questDestinationRoot $relative))
    Assert-ChildPath -Parent $questDestinationRoot -Child $destination -Label 'FTB Quests destination'
    Add-CopyPlanItem `
        -Plan $plan `
        -Destinations $plannedDestinations `
        -Source $sourceFile.FullName `
        -Destination $destination `
        -Reason 'FTB Quests factory-guidance data' `
        -ExpectedSourceState $validatedOrdinaryStateByPath[$sourceFile.FullName]
}

$activeIndustrialJars = @(
    Get-ChildItem -LiteralPath $modsRoot -File |
        Where-Object { $_.Name -match '(?i)^industrial_colonies-.+\.jar$' }
)
foreach ($activeJar in $activeIndustrialJars) {
    if (-not $activeJar.FullName.Equals($destinationJar, [System.StringComparison]::OrdinalIgnoreCase)) {
        $plan.Add([pscustomobject]@{
            Type = 'MoveToBackup'
            Source = $activeJar.FullName
            Destination = $null
            Reason = 'Retire duplicate active Industrial Colonies JAR'
            ExpectedSourceState = Get-PinnedFileState -Path $activeJar.FullName
            ExpectedDestinationState = $null
        })
    }
}

$activeC2meJars = @(
    Get-ChildItem -LiteralPath $modsRoot -File |
        Where-Object { $_.Name -match '(?i)^c2me.*\.jar$' }
)
$activeBetterChunkLoadingJars = @(
    Get-ChildItem -LiteralPath $modsRoot -File |
        Where-Object { $_.Name -match '(?i)^betterchunkloading.*\.jar$' }
)
if ($activeC2meJars.Count -gt 0 -and $activeBetterChunkLoadingJars.Count -gt 0) {
    foreach ($activeJar in $activeBetterChunkLoadingJars) {
        $plan.Add([pscustomobject]@{
            Type = 'MoveToBackup'
            Source = $activeJar.FullName
            Destination = $null
            Reason = 'Disable BetterChunkLoading because C2ME is active'
            ExpectedSourceState = Get-PinnedFileState -Path $activeJar.FullName
            ExpectedDestinationState = $null
        })
    }
}

$spaceBoundaryDestination = [System.IO.Path]::GetFullPath((
    Join-Path $serverDestinationRoot 'industrial_space_entry_deferred.js'
))
$requiredOrbitalPlanDestinations = @(
    $destinationJar,
    $kjsGenProjectDestination,
    $spaceBoundaryDestination
)
foreach ($requiredDestination in $requiredOrbitalPlanDestinations) {
    if (-not $plannedDestinations.Contains($requiredDestination)) {
        throw "Deployment plan omitted a required orbital-entry artifact: $requiredDestination"
    }
}

$recipeStageCount = $null
$recipeStageManifest = Join-Path $projectRootResolved 'build\generated\recipeStages\data\industrial_colonies\progression\recipe_stages.json'
if (Test-Path -LiteralPath $recipeStageManifest -PathType Leaf) {
    try {
        $stageData = Get-Content -LiteralPath $recipeStageManifest -Raw | ConvertFrom-Json
        $recipeStageCount = @($stageData.recipes.psobject.Properties).Count
    }
    catch {
        Write-Warning "Could not read generated recipe-stage count: $($_.Exception.Message)"
    }
}

Write-Host "Project JAR SHA256: $(Get-Sha256 -Path $projectJarResolved)"
Write-Host "Owned scripts: $($serverSources.Count) server, $($clientSources.Count) client"
Write-Host "Owned FTB Quests files to deploy: $($questSources.Count) (six factory chapters, optional dungeon guidance, preserved capstone, Orbital Engineering, and Planetary Industry)"
$writePlan = @($plan | Where-Object { $_.Type -ne 'GuardOnly' })
$guardPlan = @($plan | Where-Object { $_.Type -eq 'GuardOnly' })
Assert-DeploymentPlanCurrent -Plan @($plan)
Write-Host "Planned live changes: $($writePlan.Count)"
Write-Host "Guarded unchanged validated files: $($guardPlan.Count)"
foreach ($item in $plan) {
    if ($item.Type -eq 'Copy') {
        Write-Host "  COPY $($item.Reason): $($item.Destination)"
    }
    elseif ($item.Type -eq 'GuardOnly') {
        Write-Host "  GUARD $($item.Reason): $($item.Destination)"
    }
    else {
        Write-Host "  MOVE $($item.Reason): $($item.Source)"
    }
}

if ($PlanOnly) {
    Write-Host 'Plan-only mode: no live files were changed.' -ForegroundColor Yellow
    Write-AcceptanceChecklist -ServerScriptCount $serverSources.Count -ClientScriptCount $clientSources.Count -QuestFileCount $questSources.Count -RecipeStageCount $recipeStageCount
    return
}

if ($writePlan.Count -eq 0) {
    Write-Host 'Live pack is already synchronized; no backup or file write was needed.' -ForegroundColor Green
    Write-AcceptanceChecklist -ServerScriptCount $serverSources.Count -ClientScriptCount $clientSources.Count -QuestFileCount $questSources.Count -RecipeStageCount $recipeStageCount
    return
}

$backupParent = [System.IO.Path]::GetFullPath((Join-Path $liveRootResolved '_industrial_colonies_backups'))
Assert-ChildPath -Parent $liveRootResolved -Child $backupParent -Label 'Backup parent'
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$backupRoot = [System.IO.Path]::GetFullPath((Join-Path $backupParent "deployment-$timestamp"))
Assert-ChildPath -Parent $backupParent -Child $backupRoot -Label 'Deployment backup'

$rollbackActions = [System.Collections.Generic.List[object]]::new()
$verificationRows = [System.Collections.Generic.List[object]]::new()
$temporaryFiles = [System.Collections.Generic.List[string]]::new()
$deploymentSucceeded = $false
$transactionStarted = $false
$deploymentLock = $null

try {
    $deploymentLock = Enter-DeploymentFileLock -LiveRoot $liveRootResolved
    # Close the race between validation/hash planning and the first live write.
    Assert-MinecraftStopped -LiveRoot $liveRootResolved
    Assert-DeploymentPlanCurrent -Plan @($plan)
    $transactionStarted = $true
    New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null

    foreach ($item in $plan) {
        Assert-PinnedFileState `
            -Expected $item.ExpectedSourceState `
            -Label "$($item.Reason) source"
        if ($item.Type -eq 'GuardOnly') {
            Assert-PinnedFileState `
                -Expected $item.ExpectedDestinationState `
                -Label "$($item.Reason) destination"
            continue
        }
        if ($item.Type -eq 'MoveToBackup') {
            $relativeSource = Get-RelativeChildPath -Parent $liveRootResolved -Child $item.Source
            $archivedPath = [System.IO.Path]::GetFullPath((Join-Path (Join-Path $backupRoot 'disabled-or-retired') $relativeSource))
            Assert-ChildPath -Parent $backupRoot -Child $archivedPath -Label 'Archived mod JAR'
            New-Item -ItemType Directory -Path (Split-Path -Parent $archivedPath) -Force | Out-Null

            $sourceHash = [string] $item.ExpectedSourceState.Sha256
            $rollbackActions.Add([pscustomobject]@{
                Type = 'MoveBack'
                Original = $item.Source
                Archived = $archivedPath
            })
            Move-Item -LiteralPath $item.Source -Destination $archivedPath
            if ((Get-Sha256 -Path $archivedPath) -ne $sourceHash) {
                throw "Archived JAR hash mismatch: $($item.Source)"
            }

            $verificationRows.Add([pscustomobject]@{
                Action = $item.Reason
                Source = $item.Source
                Destination = $archivedPath
                Sha256 = $sourceHash
            })
            continue
        }

        Assert-PinnedFileState `
            -Expected $item.ExpectedDestinationState `
            -Label "$($item.Reason) destination"
        $destinationExists = [bool] $item.ExpectedDestinationState.Exists
        $backupPath = $null
        if ($destinationExists) {
            $relativeDestination = Get-RelativeChildPath -Parent $liveRootResolved -Child $item.Destination
            $backupPath = [System.IO.Path]::GetFullPath((Join-Path (Join-Path $backupRoot 'overwritten') $relativeDestination))
            Assert-ChildPath -Parent $backupRoot -Child $backupPath -Label 'Overwritten-file backup'
            New-Item -ItemType Directory -Path (Split-Path -Parent $backupPath) -Force | Out-Null

            $oldHash = [string] $item.ExpectedDestinationState.Sha256
            Copy-Item -LiteralPath $item.Destination -Destination $backupPath
            if ((Get-Sha256 -Path $backupPath) -ne $oldHash) {
                throw "Backup hash mismatch for $($item.Destination)"
            }
        }

        $rollbackAction = [pscustomobject]@{
            Type = 'RestoreCopy'
            Destination = $item.Destination
            Existed = $destinationExists
            Backup = $backupPath
            DestinationWritten = $false
        }
        $rollbackActions.Add($rollbackAction)

        $destinationParent = Split-Path -Parent $item.Destination
        New-Item -ItemType Directory -Path $destinationParent -Force | Out-Null
        $temporaryPath = Join-Path $destinationParent ('.' + (Split-Path -Leaf $item.Destination) + '.deploying-' + [guid]::NewGuid().ToString('N'))
        Assert-ChildPath -Parent $liveRootResolved -Child $temporaryPath -Label 'Temporary deployment file'
        $temporaryFiles.Add($temporaryPath)

        Assert-PinnedFileState `
            -Expected $item.ExpectedSourceState `
            -Label "$($item.Reason) source"
        Assert-PinnedFileState `
            -Expected $item.ExpectedDestinationState `
            -Label "$($item.Reason) destination"
        $sourceHash = [string] $item.ExpectedSourceState.Sha256
        Copy-Item -LiteralPath $item.Source -Destination $temporaryPath
        if ((Get-Sha256 -Path $temporaryPath) -ne $sourceHash) {
            throw "Temporary copy hash mismatch for $($item.Source)"
        }
        Assert-PinnedFileState `
            -Expected $item.ExpectedSourceState `
            -Label "$($item.Reason) source"
        Assert-PinnedFileState `
            -Expected $item.ExpectedDestinationState `
            -Label "$($item.Reason) destination"

        if ($destinationExists) {
            # The temporary file lives beside the destination, so this is a
            # same-volume atomic rename. The Boolean overload avoids
            # File.Replace's nullable-backup-path incompatibility on Windows;
            # the verified rollback copy above remains authoritative.
            [System.IO.File]::Move($temporaryPath, $item.Destination, $true)
        }
        else {
            [System.IO.File]::Move($temporaryPath, $item.Destination)
        }
        $rollbackAction.DestinationWritten = $true
        if ((Get-Sha256 -Path $item.Destination) -ne $sourceHash) {
            throw "Installed file hash mismatch for $($item.Destination)"
        }

        $verificationRows.Add([pscustomobject]@{
            Action = $item.Reason
            Source = $item.Source
            Destination = $item.Destination
            Sha256 = $sourceHash
        })
    }

    foreach ($sourceFile in $serverSources) {
        $relative = Get-RelativeChildPath -Parent $serverSourceRoot -Child $sourceFile.FullName
        $destination = Join-Path $serverDestinationRoot $relative
        if (-not (Test-SameFileContent -Left $sourceFile.FullName -Right $destination)) {
            throw "Post-deployment parity failed for server script: $relative"
        }
    }
    foreach ($sourceFile in $clientSources) {
        $relative = Get-RelativeChildPath -Parent $clientSourceRoot -Child $sourceFile.FullName
        $destination = Join-Path $clientDestinationRoot $relative
        if (-not (Test-SameFileContent -Left $sourceFile.FullName -Right $destination)) {
            throw "Post-deployment parity failed for client script: $relative"
        }
    }
    if (-not (Test-SameFileContent -Left $projectJarResolved -Right $destinationJar)) {
        throw 'Post-deployment parity failed for the Industrial Colonies JAR.'
    }
    if (-not (Test-SameFileContent -Left $kjsGenMergedSource -Right $kjsGenProjectDestination)) {
        throw 'Post-deployment parity failed for the merged KJSGen default project.'
    }
    if (-not (Test-SameFileContent -Left $kjsGenNextBaselineSource -Right $kjsGenBaselineDestination)) {
        throw 'Post-deployment parity failed for the KJSGen managed-project merge baseline.'
    }
    if (-not (Test-SameFileContent -Left $extremeReactorsSource -Right $extremeReactorsDestination)) {
        throw 'Post-deployment parity failed for Extreme Reactors modpack_api.json.'
    }
    if (-not (Test-SameFileContent -Left $createAppliedKineticsSource -Right $createAppliedKineticsDestination)) {
        throw 'Post-deployment parity failed for Create Applied Kinetics config.'
    }
    foreach ($sourceFile in $questSources) {
        $relative = Get-RelativeChildPath -Parent $questSourceRoot -Child $sourceFile.FullName
        $destination = Join-Path $questDestinationRoot $relative
        if (-not (Test-SameFileContent -Left $sourceFile.FullName -Right $destination)) {
            throw "Post-deployment parity failed for FTB Quests data: $relative"
        }
    }

    $remainingIndustrialJars = @(
        Get-ChildItem -LiteralPath $modsRoot -File |
            Where-Object { $_.Name -match '(?i)^industrial_colonies-.+\.jar$' }
    )
    if ($remainingIndustrialJars.Count -ne 1 -or -not $remainingIndustrialJars[0].FullName.Equals($destinationJar, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'Exactly one active Industrial Colonies JAR was not present after deployment.'
    }

    $remainingC2me = @(
        Get-ChildItem -LiteralPath $modsRoot -File |
            Where-Object { $_.Name -match '(?i)^c2me.*\.jar$' }
    )
    $remainingBetterChunkLoading = @(
        Get-ChildItem -LiteralPath $modsRoot -File |
            Where-Object { $_.Name -match '(?i)^betterchunkloading.*\.jar$' }
    )
    if ($remainingC2me.Count -gt 0 -and $remainingBetterChunkLoading.Count -gt 0) {
        throw 'C2ME and BetterChunkLoading are still simultaneously active after deployment.'
    }

    # Unchanged validated destinations participate as guards for the complete
    # transaction, not only at planning time.
    Assert-DeploymentPlanCurrent -Plan @($guardPlan)

    $manifest = [ordered]@{
        schema = 1
        completed_at = (Get-Date).ToString('o')
        project_root = $projectRootResolved
        live_pack_root = $liveRootResolved
        project_jar_sha256 = Get-Sha256 -Path $projectJarResolved
        owned_server_scripts = $serverSources.Count
        owned_client_scripts = $clientSources.Count
        owned_ftbquests_files = $questSources.Count
        recipe_stage_mappings = $recipeStageCount
        changes = @($verificationRows)
    }
    $manifestPath = Join-Path $backupRoot 'deployment-manifest.json'
    $manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
    $deploymentSucceeded = $true
}
catch {
    if (-not $transactionStarted) {
        throw
    }
    $deploymentError = $_
    Write-Warning "Deployment failed; restoring the previous live-pack state: $($deploymentError.Exception.Message)"
    $rollbackErrors = [System.Collections.Generic.List[string]]::new()

    for ($index = $rollbackActions.Count - 1; $index -ge 0; $index--) {
        $action = $rollbackActions[$index]
        try {
            if ($action.Type -eq 'MoveBack') {
                if (Test-Path -LiteralPath $action.Archived -PathType Leaf) {
                    New-Item -ItemType Directory -Path (Split-Path -Parent $action.Original) -Force | Out-Null
                    Move-Item -LiteralPath $action.Archived -Destination $action.Original -Force
                }
                continue
            }

            Restore-DeploymentCopyAction -Action $action
        }
        catch {
            $rollbackErrors.Add($_.Exception.Message)
        }
    }

    foreach ($temporaryPath in $temporaryFiles) {
        try {
            if (Test-Path -LiteralPath $temporaryPath -PathType Leaf) {
                Remove-Item -LiteralPath $temporaryPath -Force
            }
        }
        catch {
            $rollbackErrors.Add($_.Exception.Message)
        }
    }

    if ($rollbackErrors.Count -gt 0) {
        throw "Deployment failed and rollback was incomplete. Backup: $backupRoot. Errors: $($rollbackErrors -join ' | ')"
    }
    throw "Deployment failed and was rolled back. Backup retained at: $backupRoot. Cause: $($deploymentError.Exception.Message)"
}
finally {
    foreach ($temporaryPath in $temporaryFiles) {
        if (Test-Path -LiteralPath $temporaryPath -PathType Leaf) {
            Remove-Item -LiteralPath $temporaryPath -Force -ErrorAction SilentlyContinue
        }
    }
    if ($null -ne $deploymentLock) {
        $deploymentLock.Dispose()
    }
}

if ($deploymentSucceeded) {
    Write-Host ''
    Write-Host 'Deployment completed with SHA256 parity verified.' -ForegroundColor Green
    Write-Host "Backup and deployment manifest: $backupRoot"
    Write-AcceptanceChecklist -ServerScriptCount $serverSources.Count -ClientScriptCount $clientSources.Count -QuestFileCount $questSources.Count -RecipeStageCount $recipeStageCount
}
