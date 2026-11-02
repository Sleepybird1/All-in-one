[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$mergeTool = Join-Path $PSScriptRoot 'merge_kjsgen_project.ps1'
$scratch = Join-Path ([System.IO.Path]::GetTempPath()) ('industrial-colonies-kjsgen-test-' + [guid]::NewGuid().ToString('N'))

function Assert-MergeFails {
    param(
        [Parameter(Mandatory)]
        [string] $ManagedPath,

        [Parameter(Mandatory)]
        [string] $BaselinePath,

        [Parameter(Mandatory)]
        [string] $ProjectPath,

        [Parameter(Mandatory)]
        [string] $ExpectedPattern,

        [Parameter(Mandatory)]
        [string] $Label
    )

    $caseId = [guid]::NewGuid().ToString('N')
    $caseOutput = Join-Path $scratch "$caseId-output.json"
    $caseBaselineOutput = Join-Path $scratch "$caseId-baseline.json"
    $failedAsExpected = $false
    try {
        & $mergeTool `
            -ManagedSource $ManagedPath `
            -ExistingBaseline $BaselinePath `
            -ExistingProject $ProjectPath `
            -OutputProject $caseOutput `
            -OutputBaseline $caseBaselineOutput
    }
    catch {
        $failedAsExpected = $_.Exception.Message -match $ExpectedPattern
    }
    if (-not $failedAsExpected) {
        throw "$Label did not fail with the expected message pattern '$ExpectedPattern'."
    }
    if ((Test-Path -LiteralPath $caseOutput) -or (Test-Path -LiteralPath $caseBaselineOutput)) {
        throw "$Label wrote an output file despite failing."
    }
}

try {
    New-Item -ItemType Directory -Path $scratch -Force | Out-Null
    $existing = Join-Path $scratch 'existing.json'
    $managed = Join-Path $scratch 'managed.json'
    $baseline = Join-Path $scratch 'baseline.json'
    $output = Join-Path $scratch 'output.json'
    $baselineOutput = Join-Path $scratch 'baseline-output.json'

    @'
{
  "format": 1,
  "name": "default",
  "defaultTargetFile": "my_user_file",
  "exportComments": false,
  "reloadOnExport": true,
  "futureMetadata": { "preserveMe": true },
  "recipes": [
    {
      "uid": "11111111-1111-1111-1111-111111111111",
      "type": "kjsgen:shaped",
      "slots": { "output": { "kind": "ITEM", "id": "minecraft:stick" } },
      "params": { "user": "untouched" }
    },
    {
      "uid": "22222222-2222-2222-2222-222222222222",
      "type": "kjsgen:shaped",
      "slots": { "output": { "kind": "ITEM", "id": "minecraft:dirt" } },
      "params": {}
    }
  ],
  "removals": [
    {
      "uid": "44444444-4444-4444-4444-444444444444",
      "output": "minecraft:diamond",
      "input": "",
      "mod": "",
      "recipeId": ""
    }
  ]
}
'@ | Set-Content -LiteralPath $existing -Encoding UTF8

    @'
{
  "schema": 1,
  "project": "default",
  "recipes": [
    {
      "uid": "22222222-2222-2222-2222-222222222222",
      "type": "kjsgen:shaped",
      "comment": "managed update",
      "slots": { "output": { "kind": "ITEM", "id": "minecraft:stone" } },
      "params": {}
    },
    {
      "uid": "33333333-3333-3333-3333-333333333333",
      "type": "kjsgen:shapeless",
      "slots": { "output": { "kind": "ITEM", "id": "minecraft:paper" } },
      "params": {}
    }
  ],
  "removals": []
}
'@ | Set-Content -LiteralPath $managed -Encoding UTF8

    @'
{
  "schema": 1,
  "project": "default",
  "recipes": [
    {
      "uid": "22222222-2222-2222-2222-222222222222",
      "type": "kjsgen:shaped",
      "slots": { "output": { "kind": "ITEM", "id": "minecraft:dirt" } },
      "params": {}
    }
  ],
  "removals": []
}
'@ | Set-Content -LiteralPath $baseline -Encoding UTF8

    & $mergeTool `
        -ManagedSource $managed `
        -ExistingBaseline $baseline `
        -ExistingProject $existing `
        -OutputProject $output `
        -OutputBaseline $baselineOutput
    $result = Get-Content -LiteralPath $output -Raw | ConvertFrom-Json -AsHashtable -Depth 100

    if ($result['defaultTargetFile'] -ne 'my_user_file') {
        throw 'Existing project metadata was not preserved.'
    }
    if (-not [bool] $result['futureMetadata']['preserveMe']) {
        throw 'Unknown future metadata was not preserved.'
    }
    if (@($result['recipes']).Count -ne 3) {
        throw 'Expected three merged recipes.'
    }
    if ($result['recipes'][0]['params']['user'] -ne 'untouched') {
        throw 'Unmanaged user recipe was modified.'
    }
    if ($result['recipes'][1]['slots']['output']['id'] -ne 'minecraft:stone') {
        throw 'Managed recipe was not updated in place.'
    }
    if ($result['recipes'][2]['slots']['output']['id'] -ne 'minecraft:paper') {
        throw 'New managed recipe was not appended.'
    }
    if (@($result['removals']).Count -ne 1) {
        throw 'Unmanaged removal was not preserved.'
    }

    $committedOutput = Join-Path $scratch 'committed-output.json'
    $committedBaseline = Join-Path $scratch 'committed-baseline.json'
    $committedManagedPath = Join-Path $projectRoot 'pack-kjsgen\default.managed.json'
    $committedManaged = Get-Content -LiteralPath $committedManagedPath -Raw |
        ConvertFrom-Json -AsHashtable -Depth 100
    # Treat any long-lived retirement tombstones in the committed fragment as
    # already deployed. First-deploy behavior for active cards is still tested,
    # without fabricating baseline-owned content that would be unsafe to delete.
    $committedPriorBaseline = Join-Path $scratch 'committed-prior-baseline.json'
    $committedRetiredRecipeUids = @(
        if ($committedManaged.Contains('retiredRecipeUids')) {
            @($committedManaged['retiredRecipeUids'])
        }
    )
    $committedRetiredRemovalUids = @(
        if ($committedManaged.Contains('retiredRemovalUids')) {
            @($committedManaged['retiredRemovalUids'])
        }
    )
    [ordered]@{
        schema = 1
        project = [string] $committedManaged['project']
        recipes = @()
        removals = @()
        retiredRecipeUids = $committedRetiredRecipeUids
        retiredRemovalUids = $committedRetiredRemovalUids
    } | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $committedPriorBaseline -Encoding UTF8
    & $mergeTool `
        -ManagedSource $committedManagedPath `
        -ExistingBaseline $committedPriorBaseline `
        -ExistingProject $existing `
        -OutputProject $committedOutput `
        -OutputBaseline $committedBaseline
    $committedResult = Get-Content -LiteralPath $committedOutput -Raw |
        ConvertFrom-Json -AsHashtable -Depth 100
    $managedRecipeCount = @($committedManaged['recipes']).Count
    $managedRemovalCount = @($committedManaged['removals']).Count
    if (@($committedResult['recipes']).Count -ne (2 + $managedRecipeCount)) {
        throw 'The committed visual recipes did not append to both existing user recipes.'
    }
    if (@($committedResult['removals']).Count -ne (1 + $managedRemovalCount)) {
        throw 'The committed exact-ID removals did not append beside the existing user removal.'
    }
    if ($committedResult['recipes'][0]['params']['user'] -ne 'untouched') {
        throw 'Committed visual recipe merge modified an existing user recipe.'
    }
    $managedTypes = @($committedResult['recipes'] | Select-Object -Skip 2 | ForEach-Object { $_['type'] })
    if ($managedTypes -notcontains 'kjsgen:create_compacting') {
        throw 'Committed project is missing its editable exact-machine compacting card.'
    }
    if ($managedTypes -notcontains 'kjsgen:create_deploying') {
        throw 'Committed project is missing its editable exact-machine deploying card.'
    }
    if ($managedTypes -notcontains 'kjsgen:create_sequenced_assembly') {
        throw 'Committed project is missing its editable sequenced-assembly cards.'
    }

    # Canonical native slot keys: compacting input is a list (in0), its output
    # is singular (output), shaped output is singular, and sequenced output is
    # a list (output0).
    $managedRecipeIds = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($recipe in @($committedManaged['recipes'])) {
        $slots = $recipe['slots']
        if ([string]::IsNullOrWhiteSpace([string] $recipe['recipeId'])) {
            throw "Managed card is missing a stable recipeId: $($recipe['uid'])"
        }
        if (-not $managedRecipeIds.Add([string] $recipe['recipeId'])) {
            throw "Managed cards duplicate recipeId: $($recipe['recipeId'])"
        }
        if ([bool] $recipe['replaceRecipe']) {
            throw "Managed card still requests a broad output replacement: $($recipe['recipeId'])"
        }
        if ($recipe['type'] -eq 'kjsgen:create_compacting') {
            if (-not $slots.Contains('in0') -or -not $slots.Contains('output') -or $slots.Contains('output0')) {
                throw 'Compacting managed card does not use KJSGen native list/singular slot keys.'
            }
        }
        elseif ($recipe['type'] -eq 'kjsgen:shaped') {
            if (-not $slots.Contains('output') -or $slots.Contains('output0')) {
                throw 'Shaped managed card does not use KJSGen native output slot key.'
            }
        }
        elseif ($recipe['type'] -eq 'kjsgen:create_sequenced_assembly') {
            if (-not $slots.Contains('output0') -or $slots.Contains('output')) {
                throw 'Sequenced managed card does not use KJSGen native list output slot key.'
            }
        }
    }
    foreach ($removal in @($committedManaged['removals'])) {
        if ([string]::IsNullOrWhiteSpace([string] $removal['recipeId'])) {
            throw "Managed removal is not exact-ID based: $($removal['uid'])"
        }
        if (-not [string]::IsNullOrWhiteSpace([string] $removal['output']) -or
            -not [string]::IsNullOrWhiteSpace([string] $removal['input']) -or
            -not [string]::IsNullOrWhiteSpace([string] $removal['mod'])) {
            throw "Managed removal mixes broad filters with an exact recipe ID: $($removal['uid'])"
        }
    }

    # An empty fragment must be an exact no-op against an existing project,
    # including whitespace and property order.
    $emptyOutput = Join-Path $scratch 'empty-output.json'
    $emptyManaged = Join-Path $scratch 'empty-managed.json'
    @'
{
  "schema": 1,
  "project": "default",
  "recipes": [],
  "removals": []
}
'@ | Set-Content -LiteralPath $emptyManaged -Encoding UTF8
    $emptyMergeArguments = @{
        ManagedSource = $emptyManaged
        ExistingBaseline = $baseline
        ExistingProject = $existing
        OutputProject = $emptyOutput
        OutputBaseline = (Join-Path $scratch 'empty-baseline-output.json')
    }
    & $mergeTool @emptyMergeArguments
    $existingHash = (Get-FileHash -LiteralPath $existing -Algorithm SHA256).Hash
    $emptyHash = (Get-FileHash -LiteralPath $emptyOutput -Algorithm SHA256).Hash
    if ($existingHash -ne $emptyHash) {
        throw 'Empty managed fragment did not preserve the existing project byte-for-byte.'
    }

    # Explicit retirement deletes only baseline-owned entries whose live
    # content is still semantically unchanged. Unrelated user content remains.
    $retirementExisting = Join-Path $scratch 'retirement-existing.json'
    $retirementBaseline = Join-Path $scratch 'retirement-baseline.json'
    $retirementManaged = Join-Path $scratch 'retirement-managed.json'
    $retirementOutput = Join-Path $scratch 'retirement-output.json'
    $retirementBaselineOutput = Join-Path $scratch 'retirement-baseline-output.json'
    @'
{
  "format": 1,
  "name": "default",
  "defaultTargetFile": "retirement_test",
  "exportComments": true,
  "reloadOnExport": false,
  "recipes": [
    {
      "uid": "55555555-5555-5555-5555-555555555555",
      "type": "kjsgen:shaped",
      "slots": { "output": { "kind": "ITEM", "id": "minecraft:stone" } },
      "params": {}
    },
    {
      "uid": "77777777-7777-7777-7777-777777777777",
      "type": "kjsgen:shapeless",
      "slots": { "output": { "kind": "ITEM", "id": "minecraft:diamond" } },
      "params": { "userOwned": true }
    }
  ],
  "removals": [
    {
      "uid": "66666666-6666-6666-6666-666666666666",
      "output": "",
      "input": "",
      "mod": "",
      "recipeId": "minecraft:old_managed_recipe"
    },
    {
      "uid": "88888888-8888-8888-8888-888888888888",
      "output": "minecraft:emerald",
      "input": "",
      "mod": "",
      "recipeId": ""
    }
  ]
}
'@ | Set-Content -LiteralPath $retirementExisting -Encoding UTF8
    @'
{
  "schema": 1,
  "project": "default",
  "recipes": [
    {
      "uid": "55555555-5555-5555-5555-555555555555",
      "type": "kjsgen:shaped",
      "slots": { "output": { "kind": "ITEM", "id": "minecraft:stone" } },
      "params": {}
    }
  ],
  "removals": [
    {
      "uid": "66666666-6666-6666-6666-666666666666",
      "output": "",
      "input": "",
      "mod": "",
      "recipeId": "minecraft:old_managed_recipe"
    }
  ]
}
'@ | Set-Content -LiteralPath $retirementBaseline -Encoding UTF8
    @'
{
  "schema": 1,
  "project": "default",
  "recipes": [],
  "removals": [],
  "retiredRecipeUids": ["55555555-5555-5555-5555-555555555555"],
  "retiredRemovalUids": ["66666666-6666-6666-6666-666666666666"]
}
'@ | Set-Content -LiteralPath $retirementManaged -Encoding UTF8
    & $mergeTool `
        -ManagedSource $retirementManaged `
        -ExistingBaseline $retirementBaseline `
        -ExistingProject $retirementExisting `
        -OutputProject $retirementOutput `
        -OutputBaseline $retirementBaselineOutput
    $retiredResult = Get-Content -LiteralPath $retirementOutput -Raw |
        ConvertFrom-Json -AsHashtable -Depth 100
    if (@($retiredResult['recipes']).Count -ne 1 -or
        $retiredResult['recipes'][0]['uid'] -ne '77777777-7777-7777-7777-777777777777') {
        throw 'Explicit recipe retirement did not remove only the unchanged baseline-owned recipe.'
    }
    if (@($retiredResult['removals']).Count -ne 1 -or
        $retiredResult['removals'][0]['uid'] -ne '88888888-8888-8888-8888-888888888888') {
        throw 'Explicit removal retirement did not remove only the unchanged baseline-owned removal.'
    }
    if ((Get-FileHash -LiteralPath $retirementManaged -Algorithm SHA256).Hash -ne
        (Get-FileHash -LiteralPath $retirementBaselineOutput -Algorithm SHA256).Hash) {
        throw 'Retirement merge did not stage the managed source as the exact next baseline.'
    }

    # A missing live entry is preserved as missing. The same tombstone can be
    # deployed repeatedly after it moves into the prior baseline.
    $missingRetirementOutput = Join-Path $scratch 'missing-retirement-output.json'
    & $mergeTool `
        -ManagedSource $retirementManaged `
        -ExistingBaseline $retirementBaseline `
        -ExistingProject $retirementOutput `
        -OutputProject $missingRetirementOutput `
        -OutputBaseline (Join-Path $scratch 'missing-retirement-baseline.json')
    if ((Get-FileHash -LiteralPath $retirementOutput -Algorithm SHA256).Hash -ne
        (Get-FileHash -LiteralPath $missingRetirementOutput -Algorithm SHA256).Hash) {
        throw 'A retirement for an already-missing live UID changed the project.'
    }

    $idempotentRetirementOutput = Join-Path $scratch 'idempotent-retirement-output.json'
    & $mergeTool `
        -ManagedSource $retirementManaged `
        -ExistingBaseline $retirementBaselineOutput `
        -ExistingProject $retirementOutput `
        -OutputProject $idempotentRetirementOutput `
        -OutputBaseline (Join-Path $scratch 'idempotent-retirement-baseline.json')
    if ((Get-FileHash -LiteralPath $retirementOutput -Algorithm SHA256).Hash -ne
        (Get-FileHash -LiteralPath $idempotentRetirementOutput -Algorithm SHA256).Hash) {
        throw 'An idempotent retirement redeploy changed the project.'
    }

    # A changed live card must conflict instead of being destroyed.
    $editedRetirementProject = Join-Path $scratch 'edited-retirement-project.json'
    (Get-Content -LiteralPath $retirementExisting -Raw).Replace('minecraft:stone', 'minecraft:gold_block') |
        Set-Content -LiteralPath $editedRetirementProject -Encoding UTF8
    Assert-MergeFails `
        -ManagedPath $retirementManaged `
        -BaselinePath $retirementBaseline `
        -ProjectPath $editedRetirementProject `
        -ExpectedPattern 'retired.*different live content' `
        -Label 'Edited recipe retirement'

    $editedRemovalProject = Join-Path $scratch 'edited-removal-project.json'
    (Get-Content -LiteralPath $retirementExisting -Raw).Replace(
        'minecraft:old_managed_recipe',
        'minecraft:user_changed_recipe'
    ) | Set-Content -LiteralPath $editedRemovalProject -Encoding UTF8
    Assert-MergeFails `
        -ManagedPath $retirementManaged `
        -BaselinePath $retirementBaseline `
        -ProjectPath $editedRemovalProject `
        -ExpectedPattern 'retired.*different live content' `
        -Label 'Edited removal retirement'

    # Once a tombstone is in the baseline, a live entry reusing that UID is
    # treated as user content and conflicts rather than being silently deleted.
    Assert-MergeFails `
        -ManagedPath $retirementManaged `
        -BaselinePath $retirementBaselineOutput `
        -ProjectPath $retirementExisting `
        -ExpectedPattern 'already retired.*reappeared' `
        -Label 'Reappeared retired UID'

    # Retirement declarations are strict UUID sets, cannot overlap active
    # managed entries, and must be traceable to the prior baseline.
    $invalidRetirement = Join-Path $scratch 'invalid-retirement.json'
    @'
{"schema":1,"project":"default","recipes":[],"removals":[],"retiredRecipeUids":["not-a-uuid"]}
'@ | Set-Content -LiteralPath $invalidRetirement -Encoding UTF8
    Assert-MergeFails `
        -ManagedPath $invalidRetirement `
        -BaselinePath $retirementBaseline `
        -ProjectPath $retirementExisting `
        -ExpectedPattern 'not a UUID' `
        -Label 'Invalid retirement UUID'

    $duplicateRetirement = Join-Path $scratch 'duplicate-retirement.json'
    @'
{"schema":1,"project":"default","recipes":[],"removals":[],"retiredRecipeUids":["55555555-5555-5555-5555-555555555555","55555555-5555-5555-5555-555555555555"]}
'@ | Set-Content -LiteralPath $duplicateRetirement -Encoding UTF8
    Assert-MergeFails `
        -ManagedPath $duplicateRetirement `
        -BaselinePath $retirementBaseline `
        -ProjectPath $retirementExisting `
        -ExpectedPattern 'duplicate UID' `
        -Label 'Duplicate retirement UUID'

    $overlapRetirement = Join-Path $scratch 'overlap-retirement.json'
    @'
{
  "schema": 1,
  "project": "default",
  "recipes": [{
    "uid": "55555555-5555-5555-5555-555555555555",
    "type": "kjsgen:shaped",
    "slots": {"output":{"kind":"ITEM","id":"minecraft:stone"}},
    "params": {}
  }],
  "removals": [],
  "retiredRecipeUids": ["55555555-5555-5555-5555-555555555555"]
}
'@ | Set-Content -LiteralPath $overlapRetirement -Encoding UTF8
    Assert-MergeFails `
        -ManagedPath $overlapRetirement `
        -BaselinePath $retirementBaseline `
        -ProjectPath $retirementExisting `
        -ExpectedPattern 'overlaps an active managed entry' `
        -Label 'Active/retired UID overlap'

    $unknownRetirement = Join-Path $scratch 'unknown-retirement.json'
    @'
{"schema":1,"project":"default","recipes":[],"removals":[],"retiredRecipeUids":["99999999-9999-9999-9999-999999999999"]}
'@ | Set-Content -LiteralPath $unknownRetirement -Encoding UTF8
    Assert-MergeFails `
        -ManagedPath $unknownRetirement `
        -BaselinePath $retirementBaseline `
        -ProjectPath $retirementExisting `
        -ExpectedPattern 'not present in the deployment baseline' `
        -Label 'Unknown retirement UID'

    # A UID identifies one card globally, not one card per array. Case-only
    # recipe/removal reuse must fail before either staged output is written.
    $crossKindManaged = Join-Path $scratch 'cross-kind-managed.json'
    @'
{
  "schema": 1,
  "project": "default",
  "recipes": [{
    "uid": "99999999-aaaa-bbbb-cccc-dddddddddddd",
    "type": "kjsgen:shaped",
    "slots": {"output":{"kind":"ITEM","id":"minecraft:stone"}},
    "params": {}
  }],
  "removals": [{
    "uid": "99999999-AAAA-BBBB-CCCC-DDDDDDDDDDDD",
    "output": "minecraft:stone",
    "input": "",
    "mod": "",
    "recipeId": "minecraft:stone"
  }]
}
'@ | Set-Content -LiteralPath $crossKindManaged -Encoding UTF8
    Assert-MergeFails `
        -ManagedPath $crossKindManaged `
        -BaselinePath $retirementBaseline `
        -ProjectPath $retirementExisting `
        -ExpectedPattern 'reuses UID.*across recipes and removals' `
        -Label 'Cross-kind managed UID collision'

    # Live-only changes to managed cards are preserved when source is still at
    # baseline. Different simultaneous changes abort without producing output.
    $liveEdited = Join-Path $scratch 'live-edited.json'
    $sourceUnchanged = Join-Path $scratch 'source-unchanged.json'
    $preservedOutput = Join-Path $scratch 'preserved-output.json'
    $preservedBaseline = Join-Path $scratch 'preserved-baseline.json'
    (Get-Content -LiteralPath $existing -Raw).Replace('minecraft:dirt', 'minecraft:gold_ingot') |
        Set-Content -LiteralPath $liveEdited -Encoding UTF8
    Copy-Item -LiteralPath $baseline -Destination $sourceUnchanged
    & $mergeTool `
        -ManagedSource $sourceUnchanged `
        -ExistingBaseline $baseline `
        -ExistingProject $liveEdited `
        -OutputProject $preservedOutput `
        -OutputBaseline $preservedBaseline
    $preserved = Get-Content -LiteralPath $preservedOutput -Raw | ConvertFrom-Json -AsHashtable -Depth 100
    if ($preserved['recipes'][1]['slots']['output']['id'] -ne 'minecraft:gold_ingot') {
        throw 'A live-only managed-card edit was not preserved.'
    }

    # KJSGen omits an item count of 1 and a fluid amount of 1000 mB when saving.
    # Those serialization-only differences must not block a real source update,
    # and an otherwise unchanged source must restore the explicit canonical
    # defaults in staged output. When live and source independently converge on
    # the same recipe design, source explanatory text also wins without being
    # treated as an ingredient edit.
    $canonicalExisting = Join-Path $scratch 'canonical-existing.json'
    $canonicalBaseline = Join-Path $scratch 'canonical-baseline.json'
    $canonicalManaged = Join-Path $scratch 'canonical-managed.json'
    $canonicalOutput = Join-Path $scratch 'canonical-output.json'
    @'
{
  "format": 1,
  "name": "default",
  "recipes": [
    {
      "uid": "aaaaaaaa-1111-1111-1111-111111111111",
      "type": "kjsgen:create_mixing",
      "comment": "old fluid comment",
      "recipeId": "industrial_colonies:test/fluid_default",
      "slots": {
        "in0": {"kind":"FLUID","id":"minecraft:lava"},
        "output": {"kind":"ITEM","id":"minecraft:stone"}
      },
      "params": {"machineId":"createcasing:weathered_iron_mixer"}
    },
    {
      "uid": "bbbbbbbb-2222-2222-2222-222222222222",
      "type": "kjsgen:shaped",
      "comment": "live wording",
      "recipeId": "industrial_colonies:test/comment_merge",
      "slots": {"output":{"kind":"ITEM","id":"minecraft:gold_ingot"}},
      "params": {}
    },
    {
      "uid": "cccccccc-3333-3333-3333-333333333333",
      "type": "kjsgen:create_mixing",
      "comment": "canonical omitted defaults",
      "recipeId": "industrial_colonies:test/canonical_defaults",
      "slots": {
        "in0": {"kind":"ITEM","id":"minecraft:cobblestone"},
        "in1": {"kind":"FLUID","id":"minecraft:water"},
        "output": {"kind":"ITEM","id":"minecraft:stone"}
      },
      "params": {"machineId":"createcasing:weathered_iron_mixer"}
    }
  ],
  "removals": []
}
'@ | Set-Content -LiteralPath $canonicalExisting -Encoding UTF8
    @'
{
  "schema": 1,
  "project": "default",
  "recipes": [
    {
      "uid": "aaaaaaaa-1111-1111-1111-111111111111",
      "type": "kjsgen:create_mixing",
      "comment": "old fluid comment",
      "recipeId": "industrial_colonies:test/fluid_default",
      "slots": {
        "in0": {"kind":"FLUID","id":"minecraft:lava","amount":1000},
        "output": {"kind":"ITEM","id":"minecraft:stone"}
      },
      "params": {"machineId":"createcasing:weathered_iron_mixer"}
    },
    {
      "uid": "bbbbbbbb-2222-2222-2222-222222222222",
      "type": "kjsgen:shaped",
      "comment": "baseline wording",
      "recipeId": "industrial_colonies:test/comment_merge",
      "slots": {"output":{"kind":"ITEM","id":"minecraft:iron_ingot"}},
      "params": {}
    },
    {
      "uid": "cccccccc-3333-3333-3333-333333333333",
      "type": "kjsgen:create_mixing",
      "comment": "canonical omitted defaults",
      "recipeId": "industrial_colonies:test/canonical_defaults",
      "slots": {
        "in0": {"kind":"ITEM","id":"minecraft:cobblestone","count":1},
        "in1": {"kind":"FLUID","id":"minecraft:water","amount":1000},
        "output": {"kind":"ITEM","id":"minecraft:stone","count":1}
      },
      "params": {"machineId":"createcasing:weathered_iron_mixer"}
    }
  ],
  "removals": []
}
'@ | Set-Content -LiteralPath $canonicalBaseline -Encoding UTF8
    @'
{
  "schema": 1,
  "project": "default",
  "recipes": [
    {
      "uid": "aaaaaaaa-1111-1111-1111-111111111111",
      "type": "kjsgen:create_mixing",
      "comment": "new source fluid comment",
      "recipeId": "industrial_colonies:test/fluid_default",
      "slots": {
        "in0": {"kind":"FLUID","id":"minecraft:lava","amount":1000},
        "output": {"kind":"ITEM","id":"minecraft:stone"}
      },
      "params": {"machineId":"createcasing:industrial_iron_mixer"}
    },
    {
      "uid": "bbbbbbbb-2222-2222-2222-222222222222",
      "type": "kjsgen:shaped",
      "comment": "source wording",
      "recipeId": "industrial_colonies:test/comment_merge",
      "slots": {"output":{"kind":"ITEM","id":"minecraft:gold_ingot"}},
      "params": {}
    },
    {
      "uid": "cccccccc-3333-3333-3333-333333333333",
      "type": "kjsgen:create_mixing",
      "comment": "canonical omitted defaults",
      "recipeId": "industrial_colonies:test/canonical_defaults",
      "slots": {
        "in0": {"kind":"ITEM","id":"minecraft:cobblestone","count":1},
        "in1": {"kind":"FLUID","id":"minecraft:water","amount":1000},
        "output": {"kind":"ITEM","id":"minecraft:stone","count":1}
      },
      "params": {"machineId":"createcasing:weathered_iron_mixer"}
    }
  ],
  "removals": []
}
'@ | Set-Content -LiteralPath $canonicalManaged -Encoding UTF8
    & $mergeTool `
        -ManagedSource $canonicalManaged `
        -ExistingBaseline $canonicalBaseline `
        -ExistingProject $canonicalExisting `
        -OutputProject $canonicalOutput `
        -OutputBaseline (Join-Path $scratch 'canonical-baseline-output.json')
    $canonical = Get-Content -LiteralPath $canonicalOutput -Raw |
        ConvertFrom-Json -AsHashtable -Depth 100
    if ($canonical['recipes'][0]['params']['machineId'] -ne 'createcasing:industrial_iron_mixer') {
        throw 'An omitted default 1000 mB amount was misclassified as a live recipe edit.'
    }
    if ($canonical['recipes'][1]['comment'] -ne 'source wording') {
        throw 'Converged live/source recipe designs did not accept source-owned explanatory text.'
    }
    if (
        $canonical['recipes'][2]['slots']['in0']['count'] -ne 1 -or
        $canonical['recipes'][2]['slots']['in1']['amount'] -ne 1000 -or
        $canonical['recipes'][2]['slots']['output']['count'] -ne 1
    ) {
        throw 'Semantically default KJSGen slot omissions were not restored to canonical source JSON.'
    }

    $conflictOutput = Join-Path $scratch 'conflict-output.json'
    $conflictBaselineOutput = Join-Path $scratch 'conflict-baseline-output.json'
    $conflicted = $false
    try {
        & $mergeTool `
            -ManagedSource $managed `
            -ExistingBaseline $baseline `
            -ExistingProject $liveEdited `
            -OutputProject $conflictOutput `
            -OutputBaseline $conflictBaselineOutput
    }
    catch {
        $conflicted = $_.Exception.Message -match 'merge conflict' -and
            $_.Exception.Message -match '22222222-2222-2222-2222-222222222222'
    }
    if (-not $conflicted) {
        throw 'Different simultaneous source/live changes did not report a UID conflict.'
    }
    if ((Test-Path -LiteralPath $conflictOutput) -or (Test-Path -LiteralPath $conflictBaselineOutput)) {
        throw 'Conflict handling wrote an output file.'
    }

    $managedHash = (Get-FileHash -LiteralPath $managed -Algorithm SHA256).Hash
    $nextBaselineHash = (Get-FileHash -LiteralPath $baselineOutput -Algorithm SHA256).Hash
    if ($managedHash -ne $nextBaselineHash) {
        throw 'The staged next baseline is not an exact copy of the managed source.'
    }

    Write-Host 'KJSGen project merge tests passed.' -ForegroundColor Green
}
finally {
    if (Test-Path -LiteralPath $scratch -PathType Container) {
        Remove-Item -LiteralPath $scratch -Recurse -Force
    }
}
