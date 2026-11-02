$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$module = Join-Path $PSScriptRoot 'RecipeReviewArchiveBackfill.psm1'
$tool = Join-Path $PSScriptRoot 'build_recipe_review_archives.ps1'
Import-Module $module -Force

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw "ASSERTION FAILED: $Message" }
}

function Test-EqualBytes {
    param([byte[]]$First, [byte[]]$Second)
    if ($First.Length -ne $Second.Length) { return $false }
    for ($index = 0; $index -lt $First.Length; $index++) {
        if ($First[$index] -ne $Second[$index]) { return $false }
    }
    return $true
}

function New-TestCard {
    param([string]$Uid, [string]$RecipeId, [string]$Ingredient, [string]$Comment)
    return [ordered]@{
        uid = $Uid
        type = 'kjsgen:shaped'
        recipeId = $RecipeId
        comment = $Comment
        replaceRecipe = $false
        slots = [ordered]@{
            input = [ordered]@{ kind = 'ITEM'; id = $Ingredient }
            output = [ordered]@{ kind = 'ITEM'; id = 'test:output' }
        }
        params = [ordered]@{}
    }
}

function New-Project {
    param([string]$Name, [object[]]$Cards)
    return [ordered]@{
        format = 1
        name = $Name
        defaultTargetFile = 'kjsgen_recipes'
        exportComments = $true
        reloadOnExport = $false
        recipes = $Cards
        removals = @()
    }
}

function New-Decision {
    param($Card, [string]$Status, [string]$Uid = $Card.uid)
    return [ordered]@{
        uid = $Uid
        status = $Status
        reason = $(if ($Status -eq 'maybe') { 'maybe' } else { 'manual' })
        note = 'test'
        cardSha256 = Get-RecipeReviewDesignHash $Card
    }
}

$archiveCard = New-TestCard 'old-a' 'test:archive' 'minecraft:iron_ingot' 'preserve existing'
$frozenCard = New-TestCard 'old-b' 'test:frozen' 'minecraft:copper_ingot' 'preserve frozen'
$currentCard = New-TestCard 'current-c' 'test:current' 'minecraft:gold_ingot' 'use current'
$movedCard = New-TestCard 'old-d' 'test:moved' 'minecraft:diamond' 'move existing snapshot'
$extraCard = New-TestCard 'extra' 'test:extra' 'minecraft:coal' 'must not survive'
$disabledCard = New-TestCard 'disabled-e' 'test:disabled' 'minecraft:redstone' 'disabled current'

$ledger = [ordered]@{
    schemaVersion = 1
    project = 'default'
    reviews = [ordered]@{
        'test:archive' = New-Decision $archiveCard 'rejected' 'new-ledger-a'
        'test:frozen' = New-Decision $frozenCard 'rejected' 'new-ledger-b'
        'test:current' = New-Decision $currentCard 'rejected'
        'test:moved' = New-Decision $movedCard 'maybe' 'new-ledger-d'
        'test:disabled' = New-Decision $disabledCard 'disabled'
    }
}
$acceptance = [ordered]@{
    schemaVersion = 1
    project = 'default'
    reviewed = 1
    approved = 0
    rejected = 1
    entries = @([ordered]@{
        recipeId = 'test:frozen'
        decision = New-Decision $frozenCard 'rejected'
        card = $frozenCard
    })
}
$current = New-Project 'default' @(
    (New-TestCard 'different-a' 'test:archive' 'minecraft:iron_ingot' 'current loses'),
    (New-TestCard 'different-b' 'test:frozen' 'minecraft:copper_ingot' 'current loses'),
    $currentCard,
    (New-TestCard 'different-d' 'test:moved' 'minecraft:diamond' 'current loses'),
    $disabledCard
)
$existingRejected = New-Project 'rejected recipes' @($archiveCard, $movedCard, $extraCard)
$existingMaybe = New-Project 'Deferred' @()

$result = Build-RecipeReviewArchives `
        -Ledger $ledger `
        -CurrentDefault $current `
        -FrozenAcceptance $acceptance `
        -ExistingRejected $existingRejected `
        -ExistingMaybe $existingMaybe

Assert-True ($result.Report.rejected -eq 3) 'three rejected cards expected'
Assert-True ($result.Report.maybe -eq 1) 'one deferred card expected'
Assert-True ($result.Report.disabled -eq 1) 'one disabled card expected'
Assert-True ($result.Maybe.name -ceq 'Deferred') 'deferred archive project name must preserve exact requested case'
Assert-True ($result.Report.sources.existingRejected -eq 2) 'existing snapshots take precedence and may move archives'
Assert-True ($result.Report.sources.frozenAcceptance -eq 1) 'frozen acceptance supplies historical exact card'
Assert-True ($result.Report.sources.currentDefault -eq 2) 'current Default is the final fallback'
Assert-True ($result.Rejected.recipes[0].comment -eq 'preserve existing') 'existing archive card must be preserved verbatim'
Assert-True ($result.Rejected.recipes[1].comment -eq 'use current') 'current fallback card expected'
Assert-True ($result.Rejected.recipes[2].comment -eq 'preserve frozen') 'frozen card expected'
Assert-True ($result.Maybe.recipes[0].comment -eq 'move existing snapshot') 'matching cross-archive card must be preserved'
Assert-True ($result.Disabled.recipes[0].comment -eq 'disabled current') 'disabled archive must use the same fail-closed resolution'
Assert-True ('test:extra' -notin @($result.Rejected.recipes.recipeId)) 'archive extras must not be copied'

$badLedger = $ledger | ConvertTo-Json -Depth 100 | ConvertFrom-Json -AsHashtable -Depth 100
$badLedger.reviews['test:current'].uid = 'wrong-current-uid'
try {
    Build-RecipeReviewArchives `
            -Ledger $badLedger `
            -CurrentDefault $current `
            -FrozenAcceptance $acceptance `
            -ExistingRejected $existingRejected `
            -ExistingMaybe $existingMaybe | Out-Null
    throw 'expected current UID mismatch to fail closed'
}
catch {
    Assert-True ($_.Exception.Message -like "*current Default UID/hash does not match*") 'mismatch failure should identify current Default'
}

$badDisabledReason = $ledger | ConvertTo-Json -Depth 100 |
        ConvertFrom-Json -AsHashtable -Depth 100
$badDisabledReason.reviews['test:disabled'].reason = 'freeform_code'
try {
    Build-RecipeReviewArchives `
            -Ledger $badDisabledReason `
            -CurrentDefault $current `
            -FrozenAcceptance $acceptance `
            -ExistingRejected $existingRejected `
            -ExistingMaybe $existingMaybe | Out-Null
    throw 'expected unknown disabled code to fail closed'
}
catch {
    Assert-True ($_.Exception.Message -like '*invalid disabled reason*') 'disabled decisions must use an exact supported code'
}

$testRoot = Join-Path $projectRoot ('build\tmp\archive-backfill-test\' + [Guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($testRoot) | Out-Null
$ledgerPath = Join-Path $testRoot 'ledger.json'
$defaultPath = Join-Path $testRoot 'default.json'
$acceptancePath = Join-Path $testRoot 'acceptance.json'
$existingRejectedPath = Join-Path $testRoot 'existing-rejected.json'
$rejectedPath = Join-Path $testRoot 'Rejected_Recipes.json'
$maybePath = Join-Path $testRoot 'Deferred.json'
$disabledPath = Join-Path $testRoot 'Disabled_Recipes.json'
foreach ($item in @(
    @($ledgerPath, $ledger),
    @($defaultPath, $current),
    @($acceptancePath, $acceptance),
    @($existingRejectedPath, $existingRejected)
)) {
    [IO.File]::WriteAllText(
            $item[0],
            (($item[1] | ConvertTo-Json -Depth 100) + "`n"),
            [Text.UTF8Encoding]::new($false))
}

& $tool `
        -Reviews $ledgerPath `
        -DefaultProject $defaultPath `
        -Acceptance $acceptancePath `
        -ExistingRejected $existingRejectedPath `
        -OutputRejected $rejectedPath `
        -OutputMaybe $maybePath `
        -OutputDisabled $disabledPath | Out-Null
Assert-True ([IO.File]::Exists($rejectedPath)) 'CLI must write Rejected_Recipes.json inside workspace'
Assert-True ([IO.File]::Exists($maybePath)) 'CLI must write Deferred.json inside workspace'
Assert-True ([IO.File]::Exists($disabledPath)) 'CLI must write optional Disabled_Recipes.json inside workspace'
& $tool `
        -Reviews $ledgerPath `
        -DefaultProject $defaultPath `
        -Acceptance $acceptancePath `
        -ExistingRejected $rejectedPath `
        -ExistingMaybe $maybePath `
        -OutputRejected $rejectedPath `
        -OutputMaybe $maybePath `
        -OutputDisabled $disabledPath `
        -Check | Out-Null

$sentinel = [Text.Encoding]::UTF8.GetBytes('sentinel')
[IO.File]::WriteAllBytes($rejectedPath, $sentinel)
$badLedgerPath = Join-Path $testRoot 'bad-ledger.json'
[IO.File]::WriteAllText(
        $badLedgerPath,
        (($badLedger | ConvertTo-Json -Depth 100) + "`n"),
        [Text.UTF8Encoding]::new($false))
try {
    & $tool `
            -Reviews $badLedgerPath `
            -DefaultProject $defaultPath `
            -Acceptance $acceptancePath `
            -ExistingRejected $existingRejectedPath `
            -OutputRejected $rejectedPath `
            -OutputMaybe $maybePath `
            -OutputDisabled $disabledPath | Out-Null
    throw 'expected CLI mismatch to fail closed'
}
catch {
    Assert-True (Test-EqualBytes ([IO.File]::ReadAllBytes($rejectedPath)) $sentinel) 'failed backfill must not replace an existing output'
}

Write-Output 'PASS recipe review archive backfill tests'
