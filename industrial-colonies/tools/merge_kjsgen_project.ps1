<#
.SYNOPSIS
Three-way merges project-owned KJSGen entries into an editable live project.

.DESCRIPTION
The managed source contains the version maintained by Industrial Colonies. The
baseline sidecar contains the managed source from the last successful deploy.
The live KJSGen project contains both those cards and user-authored content.

Entries are compared semantically by stable UID. A source-only change is
applied, a live-only change is preserved, and different changes on both sides
abort before any output is written. Unrelated live entries and all project
metadata are preserved. Dropping a UID from the managed source never deletes
the corresponding live entry. Deletion requires an explicit UID tombstone in
retiredRecipeUids or retiredRemovalUids. A tombstone only removes live content
that is still semantically identical to its deployment baseline; a user-edited
entry causes a merge conflict instead.

This deliberately operates on KJSGen's native JSON model. It does not parse the
generated kubejs/server_scripts/kjsgen_recipes.js export.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string] $ManagedSource,

    [Parameter(Mandatory)]
    [string] $ExistingBaseline,

    [Parameter(Mandatory)]
    [string] $ExistingProject,

    [Parameter(Mandatory)]
    [string] $OutputProject,

    [Parameter(Mandatory)]
    [string] $OutputBaseline
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Read-JsonHashtable {
    param(
        [Parameter(Mandatory)]
        [string] $Path,

        [Parameter(Mandatory)]
        [string] $Label
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label does not exist or is not a file: $Path"
    }

    try {
        return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 |
            ConvertFrom-Json -AsHashtable -Depth 100
    }
    catch {
        throw "$Label is not valid JSON: $Path. $($_.Exception.Message)"
    }
}

function Get-RequiredString {
    param(
        [Parameter(Mandatory)]
        [System.Collections.IDictionary] $Object,

        [Parameter(Mandatory)]
        [string] $Key,

        [Parameter(Mandatory)]
        [string] $Label
    )

    if (-not $Object.Contains($Key)) {
        throw "$Label is missing '$Key'."
    }
    $value = [string] $Object[$Key]
    if ([string]::IsNullOrWhiteSpace($value)) {
        throw "$Label has a blank '$Key'."
    }
    return $value
}

function Get-EntryArray {
    param(
        [Parameter(Mandatory)]
        [System.Collections.IDictionary] $Object,

        [Parameter(Mandatory)]
        [string] $Key,

        [Parameter(Mandatory)]
        [string] $Label
    )

    if (-not $Object.Contains($Key) -or $null -eq $Object[$Key]) {
        return @()
    }
    if ($Object[$Key] -is [string] -or $Object[$Key] -isnot [System.Collections.IEnumerable]) {
        throw "$Label '$Key' must be an array."
    }
    return @($Object[$Key])
}

function Get-UidArray {
    param(
        [Parameter(Mandatory)]
        [System.Collections.IDictionary] $Object,

        [Parameter(Mandatory)]
        [string] $Key,

        [Parameter(Mandatory)]
        [string] $Label
    )

    if (-not $Object.Contains($Key)) {
        return @()
    }
    if ($null -eq $Object[$Key] -or
        $Object[$Key] -is [string] -or
        $Object[$Key] -is [System.Collections.IDictionary] -or
        $Object[$Key] -isnot [System.Collections.IEnumerable]) {
        throw "$Label '$Key' must be an array of UUID strings."
    }

    $seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    $uids = [System.Collections.Generic.List[string]]::new()
    foreach ($value in @($Object[$Key])) {
        if ($value -isnot [string] -or [string]::IsNullOrWhiteSpace([string] $value)) {
            throw "$Label '$Key' entries must be non-blank UUID strings."
        }
        $uid = [string] $value
        $parsedUid = [guid]::Empty
        if (-not [guid]::TryParse($uid, [ref] $parsedUid)) {
            throw "$Label '$Key' entry is not a UUID: $uid"
        }
        if (-not $seen.Add($uid)) {
            throw "$Label '$Key' contains duplicate UID: $uid"
        }
        $uids.Add($uid)
    }
    return $uids.ToArray()
}

function Assert-UniqueUids {
    param(
        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [object[]] $Entries,

        [Parameter(Mandatory)]
        [string] $Label,

        [Parameter()]
        [switch] $RequireRecipeShape
    )

    $seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($entry in $Entries) {
        if ($entry -isnot [System.Collections.IDictionary]) {
            throw "$Label entries must be JSON objects."
        }
        $uid = Get-RequiredString -Object $entry -Key 'uid' -Label "$Label entry"
        $parsedUid = [guid]::Empty
        if (-not [guid]::TryParse($uid, [ref] $parsedUid)) {
            throw "$Label entry UID is not a UUID: $uid"
        }
        if (-not $seen.Add($uid)) {
            throw "$Label contains duplicate UID: $uid"
        }

        if ($RequireRecipeShape) {
            [void] (Get-RequiredString -Object $entry -Key 'type' -Label "$Label entry $uid")
            if (-not $entry.Contains('slots') -or $entry['slots'] -isnot [System.Collections.IDictionary]) {
                throw "$Label recipe $uid must contain a 'slots' object."
            }
            if (-not $entry.Contains('params') -or $entry['params'] -isnot [System.Collections.IDictionary]) {
                throw "$Label recipe $uid must contain a 'params' object."
            }
        }
    }
}

function Assert-NoCrossKindUidOverlap {
    param(
        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [object[]] $Recipes,

        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [object[]] $Removals,

        [Parameter(Mandatory)]
        [string] $Label
    )

    $recipeUids = [System.Collections.Generic.HashSet[string]]::new(
        [System.StringComparer]::OrdinalIgnoreCase
    )
    foreach ($recipe in $Recipes) {
        $uid = Get-RequiredString -Object $recipe -Key 'uid' -Label "$Label recipe"
        [void] $recipeUids.Add($uid)
    }
    foreach ($removal in $Removals) {
        $uid = Get-RequiredString -Object $removal -Key 'uid' -Label "$Label removal"
        if ($recipeUids.Contains($uid)) {
            throw "$Label reuses UID $uid across recipes and removals."
        }
    }
}

function Assert-ManagedFragment {
    param(
        [Parameter(Mandatory)]
        [System.Collections.IDictionary] $Fragment,

        [Parameter(Mandatory)]
        [string] $Label,

        [Parameter(Mandatory)]
        [string] $ExpectedProject
    )

    if (-not $Fragment.Contains('schema') -or [int] $Fragment['schema'] -ne 1) {
        throw "$Label must use schema 1."
    }
    $fragmentProject = Get-RequiredString -Object $Fragment -Key 'project' -Label $Label
    if (-not $fragmentProject.Equals($ExpectedProject, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "$Label project '$fragmentProject' does not match managed project '$ExpectedProject'."
    }
}

function Test-IsJsonNumber {
    param([object] $Value)

    return $Value -is [byte] -or
        $Value -is [sbyte] -or
        $Value -is [int16] -or
        $Value -is [uint16] -or
        $Value -is [int32] -or
        $Value -is [uint32] -or
        $Value -is [int64] -or
        $Value -is [uint64] -or
        $Value -is [single] -or
        $Value -is [double] -or
        $Value -is [decimal]
}

function Test-JsonEquivalent {
    param(
        [AllowNull()]
        [object] $Left,

        [AllowNull()]
        [object] $Right
    )

    if ($null -eq $Left -or $null -eq $Right) {
        return $null -eq $Left -and $null -eq $Right
    }

    if ($Left -is [System.Collections.IDictionary] -or $Right -is [System.Collections.IDictionary]) {
        if ($Left -isnot [System.Collections.IDictionary] -or $Right -isnot [System.Collections.IDictionary]) {
            return $false
        }
        if ($Left.Count -ne $Right.Count) {
            return $false
        }
        foreach ($key in $Left.Keys) {
            if (-not $Right.Contains($key)) {
                return $false
            }
            if (-not (Test-JsonEquivalent -Left $Left[$key] -Right $Right[$key])) {
                return $false
            }
        }
        return $true
    }

    $leftIsList = $Left -is [System.Collections.IEnumerable] -and $Left -isnot [string]
    $rightIsList = $Right -is [System.Collections.IEnumerable] -and $Right -isnot [string]
    if ($leftIsList -or $rightIsList) {
        if (-not $leftIsList -or -not $rightIsList) {
            return $false
        }
        $leftItems = @($Left)
        $rightItems = @($Right)
        if ($leftItems.Count -ne $rightItems.Count) {
            return $false
        }
        for ($index = 0; $index -lt $leftItems.Count; $index++) {
            if (-not (Test-JsonEquivalent -Left $leftItems[$index] -Right $rightItems[$index])) {
                return $false
            }
        }
        return $true
    }

    if ($Left -is [bool] -or $Right -is [bool]) {
        return $Left -is [bool] -and $Right -is [bool] -and $Left -eq $Right
    }
    if ((Test-IsJsonNumber -Value $Left) -or (Test-IsJsonNumber -Value $Right)) {
        if (-not (Test-IsJsonNumber -Value $Left) -or -not (Test-IsJsonNumber -Value $Right)) {
            return $false
        }
        return [decimal] $Left -eq [decimal] $Right
    }
    if ($Left -is [string] -or $Right -is [string]) {
        return $Left -is [string] -and
            $Right -is [string] -and
            [string]::Equals($Left, $Right, [System.StringComparison]::Ordinal)
    }
    return [object]::Equals($Left, $Right)
}

function Test-RecipeSlotJsonEquivalent {
    param(
        [AllowNull()]
        [object] $Left,

        [AllowNull()]
        [object] $Right
    )

    if ($null -eq $Left -or $null -eq $Right) {
        return $null -eq $Left -and $null -eq $Right
    }

    if ($Left -is [System.Collections.IDictionary] -or $Right -is [System.Collections.IDictionary]) {
        if ($Left -isnot [System.Collections.IDictionary] -or $Right -isnot [System.Collections.IDictionary]) {
            return $false
        }

        $keys = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
        foreach ($key in $Left.Keys) {
            [void] $keys.Add([string] $key)
        }
        foreach ($key in $Right.Keys) {
            [void] $keys.Add([string] $key)
        }
        foreach ($key in $keys) {
            $leftHasKey = $Left.Contains($key)
            $rightHasKey = $Right.Contains($key)
            if ($leftHasKey -ne $rightHasKey) {
                # KJSGen 2.0.5's native SlotContent serializer omits an item
                # count of 1 and a fluid amount of 1000 mB; its deserializer
                # restores those same defaults. These forms therefore describe
                # the same slot even when an editor round-trip omitted the key.
                $slotDefault = if ($key -eq 'count') {
                    [decimal] 1
                }
                elseif ($key -eq 'amount') {
                    [decimal] 1000
                }
                else {
                    $null
                }
                if ($null -ne $slotDefault) {
                    $presentValue = if ($leftHasKey) { $Left[$key] } else { $Right[$key] }
                    if ((Test-IsJsonNumber -Value $presentValue) -and [decimal] $presentValue -eq $slotDefault) {
                        continue
                    }
                }
                return $false
            }
            if (-not (Test-RecipeSlotJsonEquivalent -Left $Left[$key] -Right $Right[$key])) {
                return $false
            }
        }
        return $true
    }

    $leftIsList = $Left -is [System.Collections.IEnumerable] -and $Left -isnot [string]
    $rightIsList = $Right -is [System.Collections.IEnumerable] -and $Right -isnot [string]
    if ($leftIsList -or $rightIsList) {
        if (-not $leftIsList -or -not $rightIsList) {
            return $false
        }
        $leftItems = @($Left)
        $rightItems = @($Right)
        if ($leftItems.Count -ne $rightItems.Count) {
            return $false
        }
        for ($index = 0; $index -lt $leftItems.Count; $index++) {
            if (-not (Test-RecipeSlotJsonEquivalent -Left $leftItems[$index] -Right $rightItems[$index])) {
                return $false
            }
        }
        return $true
    }

    return Test-JsonEquivalent -Left $Left -Right $Right
}

function Test-RecipeEntryEquivalent {
    param(
        [Parameter(Mandatory)]
        [System.Collections.IDictionary] $Left,

        [Parameter(Mandatory)]
        [System.Collections.IDictionary] $Right,

        [Parameter()]
        [switch] $IgnoreComment
    )

    $keys = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($key in $Left.Keys) {
        if (-not ($IgnoreComment -and [string] $key -eq 'comment')) {
            [void] $keys.Add([string] $key)
        }
    }
    foreach ($key in $Right.Keys) {
        if (-not ($IgnoreComment -and [string] $key -eq 'comment')) {
            [void] $keys.Add([string] $key)
        }
    }

    foreach ($key in $keys) {
        if (-not $Left.Contains($key) -or -not $Right.Contains($key)) {
            return $false
        }
        $equivalent = if ($key -eq 'slots') {
            Test-RecipeSlotJsonEquivalent -Left $Left[$key] -Right $Right[$key]
        }
        else {
            Test-JsonEquivalent -Left $Left[$key] -Right $Right[$key]
        }
        if (-not $equivalent) {
            return $false
        }
    }
    return $true
}

function Test-MergeEntryEquivalent {
    param(
        [Parameter(Mandatory)]
        [System.Collections.IDictionary] $Left,

        [Parameter(Mandatory)]
        [System.Collections.IDictionary] $Right,

        [Parameter(Mandatory)]
        [string] $Kind
    )

    if ($Kind -eq 'recipe') {
        return Test-RecipeEntryEquivalent -Left $Left -Right $Right
    }
    return Test-JsonEquivalent -Left $Left -Right $Right
}

function New-UidMap {
    param(
        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [object[]] $Entries
    )

    $map = [System.Collections.Generic.Dictionary[string, object]]::new(
        [System.StringComparer]::OrdinalIgnoreCase
    )
    foreach ($entry in $Entries) {
        $map[[string] $entry['uid']] = $entry
    }
    return $map
}

function New-UidSet {
    param(
        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [string[]] $Uids
    )

    $set = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($uid in $Uids) {
        [void] $set.Add($uid)
    }
    # Prevent PowerShell from enumerating an empty HashSet into $null.
    return ,$set
}

function Assert-NoRetirementOverlap {
    param(
        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [object[]] $ActiveEntries,

        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [string[]] $RetiredUids,

        [Parameter(Mandatory)]
        [string] $Label
    )

    $activeByUid = New-UidMap -Entries $ActiveEntries
    foreach ($uid in $RetiredUids) {
        if ($activeByUid.ContainsKey($uid)) {
            throw "$Label retirement UID $uid overlaps an active managed entry."
        }
    }
}

function Assert-RetirementsHaveBaseline {
    param(
        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [string[]] $RetiredUids,

        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [object[]] $BaselineEntries,

        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [string[]] $BaselineRetiredUids,

        [Parameter(Mandatory)]
        [string] $Kind
    )

    $baselineByUid = New-UidMap -Entries $BaselineEntries
    $baselineRetired = New-UidSet -Uids $BaselineRetiredUids
    foreach ($uid in $RetiredUids) {
        if (-not $baselineByUid.ContainsKey($uid) -and -not $baselineRetired.Contains($uid)) {
            throw "Retired $Kind UID $uid is not present in the deployment baseline."
        }
    }
}

function Get-EntryDescription {
    param(
        [Parameter(Mandatory)]
        [System.Collections.IDictionary] $Entry
    )

    foreach ($key in @('comment', 'type', 'output', 'recipeId')) {
        if ($Entry.Contains($key) -and -not [string]::IsNullOrWhiteSpace([string] $Entry[$key])) {
            return [string] $Entry[$key]
        }
    }
    return 'unlabelled entry'
}

function Merge-EntriesThreeWay {
    param(
        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [object[]] $Existing,

        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [object[]] $Baseline,

        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [object[]] $Managed,

        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [string[]] $RetiredUids,

        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [string[]] $BaselineRetiredUids,

        [Parameter(Mandatory)]
        [string] $Kind
    )

    $existingByUid = New-UidMap -Entries $Existing
    $baselineByUid = New-UidMap -Entries $Baseline
    $managedByUid = New-UidMap -Entries $Managed
    $retired = New-UidSet -Uids $RetiredUids
    $baselineRetired = New-UidSet -Uids $BaselineRetiredUids
    $replacements = [System.Collections.Generic.Dictionary[string, object]]::new(
        [System.StringComparer]::OrdinalIgnoreCase
    )
    $deletions = [System.Collections.Generic.HashSet[string]]::new(
        [System.StringComparer]::OrdinalIgnoreCase
    )
    $additions = [System.Collections.Generic.List[object]]::new()
    $conflicts = [System.Collections.Generic.List[string]]::new()
    $sourceUpdates = 0
    $livePreserved = 0
    $identical = 0
    $retiredCount = 0

    foreach ($sourceEntry in $Managed) {
        $uid = [string] $sourceEntry['uid']
        $hasBaseline = $baselineByUid.ContainsKey($uid)
        $hasLive = $existingByUid.ContainsKey($uid)

        if (-not $hasBaseline) {
            if (-not $hasLive) {
                $additions.Add($sourceEntry)
                $sourceUpdates++
            }
            elseif (Test-MergeEntryEquivalent -Left $sourceEntry -Right $existingByUid[$uid] -Kind $Kind) {
                $identical++
            }
            else {
                $description = Get-EntryDescription -Entry $sourceEntry
                $conflicts.Add(
                    "$Kind UID $uid ($description) already exists live with different content and has no deployment baseline."
                )
            }
            continue
        }

        $baselineEntry = $baselineByUid[$uid]
        $sourceChanged = -not (Test-MergeEntryEquivalent -Left $sourceEntry -Right $baselineEntry -Kind $Kind)
        $liveChanged = -not $hasLive -or
            -not (Test-MergeEntryEquivalent -Left $existingByUid[$uid] -Right $baselineEntry -Kind $Kind)

        if (-not $sourceChanged) {
            # Source is still at the baseline, so every substantive live-only
            # edit (including a deliberate deletion) remains authoritative.
            # When KJSGen merely omitted serializer defaults while preserving
            # the recipe semantics, write the canonical source representation
            # back into the staged project so exact source-parity validation is
            # deterministic.
            if ($liveChanged) {
                $livePreserved++
            }
            elseif ($hasLive -and -not (Test-JsonEquivalent -Left $sourceEntry -Right $existingByUid[$uid])) {
                $replacements[$uid] = $sourceEntry
                $sourceUpdates++
            }
            else {
                $identical++
            }
            continue
        }

        if (-not $liveChanged) {
            $replacements[$uid] = $sourceEntry
            $sourceUpdates++
            continue
        }

        if ($hasLive -and (Test-MergeEntryEquivalent -Left $sourceEntry -Right $existingByUid[$uid] -Kind $Kind)) {
            # Both sides independently reached the same content.
            $identical++
            continue
        }

        if ($Kind -eq 'recipe' -and $hasLive -and
            (Test-RecipeEntryEquivalent -Left $sourceEntry -Right $existingByUid[$uid] -IgnoreComment)) {
            # The live editor and source independently reached the same recipe
            # design. Source-owned explanatory copy may have moved phases or
            # been rewritten; that is not a competing ingredient/machine edit.
            $replacements[$uid] = $sourceEntry
            $sourceUpdates++
            continue
        }

        $description = Get-EntryDescription -Entry $sourceEntry
        $liveState = if ($hasLive) { 'different content' } else { 'a live deletion' }
        $conflicts.Add(
            "$Kind UID $uid ($description) changed in managed source and has $liveState since the baseline."
        )
    }

    # UIDs that were in the old baseline but were dropped from the new source
    # are deliberately untouched unless the source also carries an explicit
    # retirement tombstone. A retired live entry is deleted only when it still
    # matches the baseline; live edits remain protected by a conflict.
    foreach ($baselineEntry in $Baseline) {
        $uid = [string] $baselineEntry['uid']
        if ($managedByUid.ContainsKey($uid)) {
            continue
        }
        if ($retired.Contains($uid)) {
            if (-not $existingByUid.ContainsKey($uid)) {
                # A prior run or the user already removed it. Do not recreate it.
                $identical++
            }
            elseif (Test-MergeEntryEquivalent -Left $existingByUid[$uid] -Right $baselineEntry -Kind $Kind) {
                [void] $deletions.Add($uid)
                $retiredCount++
            }
            else {
                $description = Get-EntryDescription -Entry $baselineEntry
                $conflicts.Add(
                    "$Kind UID $uid ($description) is retired in managed source but has different live content than its baseline."
                )
            }
        }
        elseif ($existingByUid.ContainsKey($uid)) {
            $livePreserved++
        }
    }

    # A tombstone retained across deployments is present in the baseline's own
    # retirement list instead of its active-entry array. A missing live UID is
    # the expected idempotent state. If it reappears, its content has no active
    # baseline to prove ownership against, so fail safely rather than delete it.
    foreach ($uid in $RetiredUids) {
        if (-not $baselineRetired.Contains($uid) -or $baselineByUid.ContainsKey($uid)) {
            continue
        }
        if ($existingByUid.ContainsKey($uid)) {
            $conflicts.Add(
                "$Kind UID $uid was already retired in the deployment baseline but has reappeared live."
            )
        }
        else {
            $identical++
        }
    }

    $merged = [System.Collections.Generic.List[object]]::new()
    foreach ($entry in $Existing) {
        $uid = [string] $entry['uid']
        if ($deletions.Contains($uid)) {
            continue
        }
        elseif ($replacements.ContainsKey($uid)) {
            $merged.Add($replacements[$uid])
        }
        else {
            $merged.Add($entry)
        }
    }
    foreach ($entry in $additions) {
        $merged.Add($entry)
    }

    return [pscustomobject]@{
        Entries = $merged.ToArray()
        Conflicts = $conflicts.ToArray()
        Changed = $replacements.Count -gt 0 -or $additions.Count -gt 0 -or $deletions.Count -gt 0
        SourceUpdates = $sourceUpdates
        LivePreserved = $livePreserved
        Identical = $identical
        Retired = $retiredCount
    }
}

function Write-JsonFile {
    param(
        [Parameter(Mandatory)]
        [object] $Value,

        [Parameter(Mandatory)]
        [string] $Path
    )

    $json = $Value | ConvertTo-Json -Depth 100
    $utf8WithoutBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($Path, $json + [Environment]::NewLine, $utf8WithoutBom)
}

$managedPath = [System.IO.Path]::GetFullPath($ManagedSource)
$baselinePath = [System.IO.Path]::GetFullPath($ExistingBaseline)
$existingPath = [System.IO.Path]::GetFullPath($ExistingProject)
$outputPath = [System.IO.Path]::GetFullPath($OutputProject)
$outputBaselinePath = [System.IO.Path]::GetFullPath($OutputBaseline)

if ($outputPath.Equals($outputBaselinePath, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'OutputProject and OutputBaseline must be different files.'
}

$managed = Read-JsonHashtable -Path $managedPath -Label 'Managed KJSGen fragment'
if ($managed -isnot [System.Collections.IDictionary]) {
    throw 'Managed KJSGen fragment root must be a JSON object.'
}
if (-not $managed.Contains('schema') -or [int] $managed['schema'] -ne 1) {
    throw 'Managed KJSGen fragment must use schema 1.'
}
$projectName = Get-RequiredString -Object $managed -Key 'project' -Label 'Managed KJSGen fragment'
$managedRecipes = @(Get-EntryArray -Object $managed -Key 'recipes' -Label 'Managed KJSGen fragment')
$managedRemovals = @(Get-EntryArray -Object $managed -Key 'removals' -Label 'Managed KJSGen fragment')
$managedRetiredRecipeUids = @(Get-UidArray -Object $managed -Key 'retiredRecipeUids' -Label 'Managed KJSGen fragment')
$managedRetiredRemovalUids = @(Get-UidArray -Object $managed -Key 'retiredRemovalUids' -Label 'Managed KJSGen fragment')
Assert-UniqueUids -Entries $managedRecipes -Label 'Managed recipes' -RequireRecipeShape
Assert-UniqueUids -Entries $managedRemovals -Label 'Managed removals'
Assert-NoCrossKindUidOverlap `
    -Recipes $managedRecipes `
    -Removals $managedRemovals `
    -Label 'Managed KJSGen fragment'
Assert-NoRetirementOverlap `
    -ActiveEntries $managedRecipes `
    -RetiredUids $managedRetiredRecipeUids `
    -Label 'Managed recipe'
Assert-NoRetirementOverlap `
    -ActiveEntries $managedRemovals `
    -RetiredUids $managedRetiredRemovalUids `
    -Label 'Managed removal'

if (Test-Path -LiteralPath $baselinePath -PathType Leaf) {
    $baseline = Read-JsonHashtable -Path $baselinePath -Label 'Existing KJSGen deployment baseline'
    if ($baseline -isnot [System.Collections.IDictionary]) {
        throw 'Existing KJSGen deployment baseline root must be a JSON object.'
    }
    Assert-ManagedFragment -Fragment $baseline -Label 'Existing KJSGen deployment baseline' -ExpectedProject $projectName
}
else {
    $baseline = [ordered]@{
        schema = 1
        project = $projectName
        recipes = @()
        removals = @()
    }
}
$baselineRecipes = @(Get-EntryArray -Object $baseline -Key 'recipes' -Label 'Existing KJSGen deployment baseline')
$baselineRemovals = @(Get-EntryArray -Object $baseline -Key 'removals' -Label 'Existing KJSGen deployment baseline')
$baselineRetiredRecipeUids = @(Get-UidArray -Object $baseline -Key 'retiredRecipeUids' -Label 'Existing KJSGen deployment baseline')
$baselineRetiredRemovalUids = @(Get-UidArray -Object $baseline -Key 'retiredRemovalUids' -Label 'Existing KJSGen deployment baseline')
Assert-UniqueUids -Entries $baselineRecipes -Label 'Baseline recipes' -RequireRecipeShape
Assert-UniqueUids -Entries $baselineRemovals -Label 'Baseline removals'
Assert-NoCrossKindUidOverlap `
    -Recipes $baselineRecipes `
    -Removals $baselineRemovals `
    -Label 'Existing KJSGen deployment baseline'
Assert-NoRetirementOverlap `
    -ActiveEntries $baselineRecipes `
    -RetiredUids $baselineRetiredRecipeUids `
    -Label 'Baseline recipe'
Assert-NoRetirementOverlap `
    -ActiveEntries $baselineRemovals `
    -RetiredUids $baselineRetiredRemovalUids `
    -Label 'Baseline removal'
Assert-RetirementsHaveBaseline `
    -RetiredUids $managedRetiredRecipeUids `
    -BaselineEntries $baselineRecipes `
    -BaselineRetiredUids $baselineRetiredRecipeUids `
    -Kind 'recipe'
Assert-RetirementsHaveBaseline `
    -RetiredUids $managedRetiredRemovalUids `
    -BaselineEntries $baselineRemovals `
    -BaselineRetiredUids $baselineRetiredRemovalUids `
    -Kind 'removal'

$existingProjectPresent = Test-Path -LiteralPath $existingPath -PathType Leaf
if ($existingProjectPresent) {
    $project = Read-JsonHashtable -Path $existingPath -Label 'Existing KJSGen project'
}
else {
    $project = [ordered]@{
        format = 1
        name = $projectName
        defaultTargetFile = 'kjsgen_recipes'
        exportComments = $true
        reloadOnExport = $false
        recipes = @()
        removals = @()
    }
}

if ($project -isnot [System.Collections.IDictionary]) {
    throw 'Existing KJSGen project root must be a JSON object.'
}
if (-not $project.Contains('format') -or [int] $project['format'] -ne 1) {
    throw 'Existing KJSGen project must use format 1.'
}
$existingName = Get-RequiredString -Object $project -Key 'name' -Label 'Existing KJSGen project'
if (-not $existingName.Equals($projectName, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Managed project '$projectName' cannot be merged into existing project '$existingName'."
}

$existingRecipes = @(Get-EntryArray -Object $project -Key 'recipes' -Label 'Existing KJSGen project')
$existingRemovals = @(Get-EntryArray -Object $project -Key 'removals' -Label 'Existing KJSGen project')
Assert-UniqueUids -Entries $existingRecipes -Label 'Existing recipes'
Assert-UniqueUids -Entries $existingRemovals -Label 'Existing removals'
Assert-NoCrossKindUidOverlap `
    -Recipes $existingRecipes `
    -Removals $existingRemovals `
    -Label 'Existing KJSGen project'

$recipeMerge = Merge-EntriesThreeWay `
    -Existing $existingRecipes `
    -Baseline $baselineRecipes `
    -Managed $managedRecipes `
    -RetiredUids $managedRetiredRecipeUids `
    -BaselineRetiredUids $baselineRetiredRecipeUids `
    -Kind 'recipe'
$removalMerge = Merge-EntriesThreeWay `
    -Existing $existingRemovals `
    -Baseline $baselineRemovals `
    -Managed $managedRemovals `
    -RetiredUids $managedRetiredRemovalUids `
    -BaselineRetiredUids $baselineRetiredRemovalUids `
    -Kind 'removal'

$conflicts = @($recipeMerge.Conflicts) + @($removalMerge.Conflicts)
if ($conflicts.Count -gt 0) {
    $details = ($conflicts | ForEach-Object { " - $_" }) -join [Environment]::NewLine
    throw @"
KJSGen managed-project merge conflict. No output was written.
$details
Resolve each UID by copying the intended live card into pack-kjsgen/default.managed.json,
or restore the live card to the last deployed baseline, then run deployment again.
"@
}

$project['recipes'] = @($recipeMerge.Entries)
$project['removals'] = @($removalMerge.Entries)

$outputParent = Split-Path -Parent $outputPath
$outputBaselineParent = Split-Path -Parent $outputBaselinePath
if ([string]::IsNullOrWhiteSpace($outputParent) -or [string]::IsNullOrWhiteSpace($outputBaselineParent)) {
    throw 'Both output files must have parent directories.'
}
New-Item -ItemType Directory -Path $outputParent -Force | Out-Null
New-Item -ItemType Directory -Path $outputBaselineParent -Force | Out-Null

$projectChanged = -not $existingProjectPresent -or $recipeMerge.Changed -or $removalMerge.Changed
if ($projectChanged) {
    Write-JsonFile -Value $project -Path $outputPath
}
else {
    # Keep all user formatting, key order, and unknown metadata byte-for-byte
    # when the three-way merge does not need to alter the project.
    Copy-Item -LiteralPath $existingPath -Destination $outputPath -Force
}

# The next baseline is the exact managed source used by this merge. It is
# staged beside the merged project and deployed only after the normal backup
# and SHA256-verified copy transaction succeeds.
Copy-Item -LiteralPath $managedPath -Destination $outputBaselinePath -Force

Write-Host (
    ('KJSGen three-way merge: {0} recipes and {1} removals maintained; ' +
    '{2} source updates, {3} explicit retirements, {4} live edits preserved, {5} identical; ' +
    'output has {6} recipes and {7} removals.') -f
    $managedRecipes.Count,
    $managedRemovals.Count,
    ($recipeMerge.SourceUpdates + $removalMerge.SourceUpdates),
    ($recipeMerge.Retired + $removalMerge.Retired),
    ($recipeMerge.LivePreserved + $removalMerge.LivePreserved),
    ($recipeMerge.Identical + $removalMerge.Identical),
    @($project['recipes']).Count,
    @($project['removals']).Count
)
