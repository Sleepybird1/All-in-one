[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'deployment_hash_pinning.ps1')

$scratch = Join-Path ([System.IO.Path]::GetTempPath()) (
    'industrial-colonies-hash-pinning-' + [guid]::NewGuid().ToString('N')
)

function Assert-Throws {
    param(
        [Parameter(Mandatory)]
        [scriptblock] $Action,

        [Parameter(Mandatory)]
        [string] $Pattern,

        [Parameter(Mandatory)]
        [string] $Label
    )

    $matched = $false
    try {
        & $Action
    }
    catch {
        $matched = $_.Exception.Message -match $Pattern
    }
    if (-not $matched) {
        throw "$Label did not fail with message pattern '$Pattern'."
    }
}

try {
    New-Item -ItemType Directory -Path $scratch -Force | Out-Null
    $source = Join-Path $scratch 'source.txt'
    $destination = Join-Path $scratch 'destination.txt'
    $missing = Join-Path $scratch 'missing.txt'
    Set-Content -LiteralPath $source -Value 'source-v1' -NoNewline
    Set-Content -LiteralPath $destination -Value 'destination-v1' -NoNewline

    $sourceState = Get-PinnedFileState -Path $source
    $destinationState = Get-PinnedFileState -Path $destination
    $missingState = Get-PinnedFileState -Path $missing
    $plan = @([pscustomobject]@{
        Type = 'Copy'
        Source = $source
        Destination = $destination
        Reason = 'fixture'
        ExpectedSourceState = $sourceState
        ExpectedDestinationState = $destinationState
    })

    Assert-DeploymentPlanCurrent -Plan $plan

    $setStates = @(Get-PinnedFileSet -Paths @($source, $destination))
    Assert-PinnedFileSet `
        -Expected $setStates `
        -CurrentPaths @($destination, $source) `
        -Label 'fixture source set'
    Assert-Throws `
        -Action { Assert-PinnedFileSet -Expected $setStates -CurrentPaths @($source) -Label 'fixture source set' } `
        -Pattern 'file membership changed' `
        -Label 'Removed validated source'

    $guardPlan = @([pscustomobject]@{
        Type = 'GuardOnly'
        Source = $source
        Destination = $destination
        Reason = 'unchanged fixture'
        ExpectedSourceState = $sourceState
        ExpectedDestinationState = $destinationState
    })
    Set-Content -LiteralPath $destination -Value 'guard-drift' -NoNewline
    Assert-Throws `
        -Action { Assert-DeploymentPlanCurrent -Plan $guardPlan } `
        -Pattern 'unchanged fixture destination changed.*SHA256' `
        -Label 'Unchanged destination guard'
    Set-Content -LiteralPath $destination -Value 'destination-v1' -NoNewline

    Set-Content -LiteralPath $source -Value 'source-v2' -NoNewline
    Assert-Throws `
        -Action { Assert-DeploymentPlanCurrent -Plan $plan } `
        -Pattern 'fixture source changed.*SHA256' `
        -Label 'Mutated source'
    Set-Content -LiteralPath $source -Value 'source-v1' -NoNewline

    Set-Content -LiteralPath $destination -Value 'destination-v2' -NoNewline
    Assert-Throws `
        -Action { Assert-DeploymentPlanCurrent -Plan $plan } `
        -Pattern 'fixture destination changed.*SHA256' `
        -Label 'Mutated destination'
    Set-Content -LiteralPath $destination -Value 'destination-v1' -NoNewline
    Assert-DeploymentPlanCurrent -Plan $plan

    Set-Content -LiteralPath $missing -Value 'unexpected' -NoNewline
    Assert-Throws `
        -Action { Assert-PinnedFileState -Expected $missingState -Label 'missing fixture' } `
        -Pattern 'expected it to remain absent' `
        -Label 'Unexpected destination creation'
    Remove-Item -LiteralPath $missing -Force

    Remove-Item -LiteralPath $destination -Force
    Assert-Throws `
        -Action { Assert-PinnedFileState -Expected $destinationState -Label 'destination fixture' } `
        -Pattern 'expected it to exist' `
        -Label 'Unexpected destination deletion'

    # A race discovered before our atomic rename must leave the concurrent
    # editor's bytes intact. Only an action marked written may be rolled back.
    $rollbackDestination = Join-Path $scratch 'rollback-destination.txt'
    $rollbackBackup = Join-Path $scratch 'rollback-backup.txt'
    Set-Content -LiteralPath $rollbackDestination -Value 'planned-old-bytes' -NoNewline
    Copy-Item -LiteralPath $rollbackDestination -Destination $rollbackBackup
    Set-Content -LiteralPath $rollbackDestination -Value 'concurrent-user-edit' -NoNewline
    $pendingAction = [pscustomobject]@{
        Destination = $rollbackDestination
        Existed = $true
        Backup = $rollbackBackup
        DestinationWritten = $false
    }
    Restore-DeploymentCopyAction -Action $pendingAction
    if ((Get-Content -LiteralPath $rollbackDestination -Raw) -ne 'concurrent-user-edit') {
        throw 'A pre-rename rollback destroyed the concurrent destination edit.'
    }

    $pendingAction.DestinationWritten = $true
    Restore-DeploymentCopyAction -Action $pendingAction
    if ((Get-Content -LiteralPath $rollbackDestination -Raw) -ne 'planned-old-bytes') {
        throw 'A completed destination write did not restore its verified backup.'
    }

    $createdDuringRace = Join-Path $scratch 'created-during-race.txt'
    Set-Content -LiteralPath $createdDuringRace -Value 'external-file' -NoNewline
    Restore-DeploymentCopyAction -Action ([pscustomobject]@{
        Destination = $createdDuringRace
        Existed = $false
        Backup = $null
        DestinationWritten = $false
    })
    if ((Get-Content -LiteralPath $createdDuringRace -Raw) -ne 'external-file') {
        throw 'A pre-rename rollback deleted an externally created destination.'
    }

    $firstLock = Enter-DeploymentFileLock -LiveRoot $scratch
    try {
        Assert-Throws `
            -Action { $secondLock = Enter-DeploymentFileLock -LiveRoot $scratch; $secondLock.Dispose() } `
            -Pattern 'already owns the live-pack lock' `
            -Label 'Concurrent deployment lock'
    }
    finally {
        $firstLock.Dispose()
    }
    $releasedLock = Enter-DeploymentFileLock -LiveRoot $scratch
    $releasedLock.Dispose()

    Write-Host 'Deployment hash-pinning tests passed.'
}
finally {
    if (Test-Path -LiteralPath $scratch -PathType Container) {
        Remove-Item -LiteralPath $scratch -Recurse -Force
    }
}
