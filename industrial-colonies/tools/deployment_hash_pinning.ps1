Set-StrictMode -Version Latest

function Get-PinnedFileState {
    param(
        [Parameter(Mandatory)]
        [string] $Path
    )

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $exists = Test-Path -LiteralPath $fullPath -PathType Leaf
    return [pscustomobject]@{
        Path = $fullPath
        Exists = $exists
        Sha256 = if ($exists) {
            (Get-FileHash -LiteralPath $fullPath -Algorithm SHA256).Hash.ToUpperInvariant()
        }
        else {
            $null
        }
    }
}

function Get-PinnedFileSet {
    param(
        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [string[]] $Paths
    )

    $seen = [System.Collections.Generic.HashSet[string]]::new(
        [System.StringComparer]::OrdinalIgnoreCase
    )
    $states = [System.Collections.Generic.List[object]]::new()
    foreach ($path in $Paths) {
        $state = Get-PinnedFileState -Path $path
        if (-not $state.Exists) {
            throw "Validated deployment source is missing: $($state.Path)"
        }
        if (-not $seen.Add([string] $state.Path)) {
            throw "Validated deployment source is listed more than once: $($state.Path)"
        }
        $states.Add($state)
    }
    return $states.ToArray()
}

function Assert-PinnedFileSet {
    param(
        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [object[]] $Expected,

        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [string[]] $CurrentPaths,

        [Parameter(Mandatory)]
        [string] $Label
    )

    $expectedByPath = [System.Collections.Generic.Dictionary[string, object]]::new(
        [System.StringComparer]::OrdinalIgnoreCase
    )
    foreach ($state in $Expected) {
        if (-not $expectedByPath.TryAdd([string] $state.Path, $state)) {
            throw "$Label expected set repeats path: $($state.Path)"
        }
    }

    $current = @(Get-PinnedFileSet -Paths $CurrentPaths)
    $currentPathsSeen = [System.Collections.Generic.HashSet[string]]::new(
        [System.StringComparer]::OrdinalIgnoreCase
    )
    foreach ($state in $current) {
        [void] $currentPathsSeen.Add([string] $state.Path)
    }
    $expectedPaths = [System.Collections.Generic.HashSet[string]]::new(
        $expectedByPath.Keys,
        [System.StringComparer]::OrdinalIgnoreCase
    )
    if (-not $expectedPaths.SetEquals($currentPathsSeen)) {
        $added = @($currentPathsSeen | Where-Object { -not $expectedPaths.Contains($_) })
        $removed = @($expectedPaths | Where-Object { -not $currentPathsSeen.Contains($_) })
        throw (
            "$Label file membership changed after validation; " +
            "added=[$($added -join ', ')], removed=[$($removed -join ', ')]"
        )
    }
    foreach ($state in $Expected) {
        Assert-PinnedFileState -Expected $state -Label $Label
    }
}

function Enter-DeploymentFileLock {
    param(
        [Parameter(Mandatory)]
        [string] $LiveRoot
    )

    $normalized = [System.IO.Path]::GetFullPath($LiveRoot).TrimEnd('\').ToLowerInvariant()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($normalized)
    $sha = [System.Security.Cryptography.SHA256]::HashData($bytes)
    $key = [System.Convert]::ToHexString($sha)
    $lockPath = Join-Path ([System.IO.Path]::GetTempPath()) (
        "industrial-colonies-deploy-$key.lock"
    )
    try {
        return [System.IO.File]::Open(
            $lockPath,
            [System.IO.FileMode]::OpenOrCreate,
            [System.IO.FileAccess]::ReadWrite,
            [System.IO.FileShare]::None
        )
    }
    catch [System.IO.IOException] {
        throw "Another Industrial Colonies deployment already owns the live-pack lock for: $normalized"
    }
}

function Assert-PinnedFileState {
    param(
        [Parameter(Mandatory)]
        [object] $Expected,

        [Parameter(Mandatory)]
        [string] $Label
    )

    $actual = Get-PinnedFileState -Path ([string] $Expected.Path)
    if ([bool] $actual.Exists -ne [bool] $Expected.Exists) {
        $expectedDescription = if ($Expected.Exists) { 'exist' } else { 'remain absent' }
        throw "$Label changed after it was validated/planned: expected it to ${expectedDescription}: $($Expected.Path)"
    }
    if ($actual.Exists -and
        -not ([string] $actual.Sha256).Equals(
            [string] $Expected.Sha256,
            [System.StringComparison]::OrdinalIgnoreCase
        )) {
        throw (
            "$Label changed after it was validated/planned: $($Expected.Path) " +
            "(expected SHA256 $($Expected.Sha256), found $($actual.Sha256))"
        )
    }
}

function Assert-DeploymentPlanCurrent {
    param(
        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [object[]] $Plan
    )

    foreach ($item in $Plan) {
        Assert-PinnedFileState `
            -Expected $item.ExpectedSourceState `
            -Label "$($item.Reason) source"
        if ($item.Type -in @('Copy', 'GuardOnly')) {
            Assert-PinnedFileState `
                -Expected $item.ExpectedDestinationState `
                -Label "$($item.Reason) destination"
        }
    }
}

function Restore-DeploymentCopyAction {
    param(
        [Parameter(Mandatory)]
        [object] $Action
    )

    # A failed pin check can occur after a backup was captured but before this
    # deployment replaced the destination. In that case the current bytes may
    # belong to a concurrent editor and must not be deleted or rolled back.
    if (-not [bool] $Action.DestinationWritten) {
        return
    }

    if (Test-Path -LiteralPath $Action.Destination -PathType Leaf) {
        Remove-Item -LiteralPath $Action.Destination -Force
    }
    if ([bool] $Action.Existed -and
        (Test-Path -LiteralPath $Action.Backup -PathType Leaf)) {
        New-Item -ItemType Directory -Path (Split-Path -Parent $Action.Destination) -Force | Out-Null
        Copy-Item -LiteralPath $Action.Backup -Destination $Action.Destination
    }
}
