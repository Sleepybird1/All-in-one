param(
    [Parameter(Mandatory = $true)]
    [string]$BaseJar,

    [Parameter(Mandatory = $true)]
    [string]$FeatureJar,

    [Parameter(Mandatory = $true)]
    [string]$OutputJar
)

$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

function Read-ZipText {
    param(
        [Parameter(Mandatory = $true)]
        [System.IO.Compression.ZipArchive]$Archive,

        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    $entry = $Archive.GetEntry($Name)
    if ($null -eq $entry) {
        throw "Missing required JAR entry: $Name"
    }

    $reader = [System.IO.StreamReader]::new($entry.Open(), [System.Text.Encoding]::UTF8)
    try {
        return $reader.ReadToEnd()
    }
    finally {
        $reader.Dispose()
    }
}

function Write-ZipBytes {
    param(
        [Parameter(Mandatory = $true)]
        [System.IO.Compression.ZipArchive]$Archive,

        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [byte[]]$Bytes
    )

    $existing = $Archive.GetEntry($Name)
    if ($null -ne $existing) {
        $existing.Delete()
    }

    $entry = $Archive.CreateEntry($Name, [System.IO.Compression.CompressionLevel]::Optimal)
    $stream = $entry.Open()
    try {
        $stream.Write($Bytes, 0, $Bytes.Length)
    }
    finally {
        $stream.Dispose()
    }
}

function Write-ZipText {
    param(
        [Parameter(Mandatory = $true)]
        [System.IO.Compression.ZipArchive]$Archive,

        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string]$Text
    )

    $utf8WithoutBom = [System.Text.UTF8Encoding]::new($false)
    Write-ZipBytes -Archive $Archive -Name $Name -Bytes $utf8WithoutBom.GetBytes($Text)
}

function Read-ZipBytes {
    param(
        [Parameter(Mandatory = $true)]
        [System.IO.Compression.ZipArchive]$Archive,

        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    $entry = $Archive.GetEntry($Name)
    if ($null -eq $entry) {
        throw "Missing required feature JAR entry: $Name"
    }

    $memory = [System.IO.MemoryStream]::new()
    $stream = $entry.Open()
    try {
        $stream.CopyTo($memory)
        return $memory.ToArray()
    }
    finally {
        $stream.Dispose()
        $memory.Dispose()
    }
}

$basePath = [System.IO.Path]::GetFullPath($BaseJar)
$featurePath = [System.IO.Path]::GetFullPath($FeatureJar)
$outputPath = [System.IO.Path]::GetFullPath($OutputJar)

if (-not [System.IO.File]::Exists($basePath)) {
    throw "Base JAR does not exist: $basePath"
}
if (-not [System.IO.File]::Exists($featurePath)) {
    throw "Feature JAR does not exist: $featurePath"
}
if ($outputPath -eq $basePath -or $outputPath -eq $featurePath) {
    throw 'OutputJar must be different from BaseJar and FeatureJar.'
}

$outputDirectory = [System.IO.Path]::GetDirectoryName($outputPath)
[System.IO.Directory]::CreateDirectory($outputDirectory) | Out-Null
[System.IO.File]::Copy($basePath, $outputPath, $true)

$feature = [System.IO.Compression.ZipFile]::OpenRead($featurePath)
$output = [System.IO.Compression.ZipFile]::Open(
    $outputPath,
    [System.IO.Compression.ZipArchiveMode]::Update
)

try {
    $featureClassNames = @(
        'dev/godpc/industrialcolonies/KjsGenRecipeReviewStore.class',
        'dev/godpc/industrialcolonies/KjsGenRecipeReviewStore$ArchiveMutation.class',
        'dev/godpc/industrialcolonies/KjsGenRecipeReviewStore$Counts.class',
        'dev/godpc/industrialcolonies/KjsGenRecipeReviewStore$Review.class',
        'dev/godpc/industrialcolonies/KjsGenRecipeReviewStore$Status.class',
        'dev/godpc/industrialcolonies/KjsGenRecipeReviewStore$StoredReview.class',
        'dev/godpc/industrialcolonies/KjsGenRejectReasonScreen.class',
        'dev/godpc/industrialcolonies/KjsGenRejectReasonScreen$CommonReason.class',
        'dev/godpc/industrialcolonies/KjsGenRejectReasonScreen$DisableReason.class',
        'dev/godpc/industrialcolonies/KjsGenRejectReasonScreen$MachineChooserStep.class',
        'dev/godpc/industrialcolonies/KjsGenRejectReasonScreen$MachineEnvironment.class',
        'dev/godpc/industrialcolonies/KjsGenRecipeViewHistory.class',
        'dev/godpc/industrialcolonies/KjsGenRecipeHelp.class',
        'dev/godpc/industrialcolonies/KjsGenRecipeNotesScreen.class',
        'dev/godpc/industrialcolonies/KjsGenDisabledRecipeFilter.class',
        'dev/godpc/industrialcolonies/mixin/KjsGenRecipeReviewMixin.class',
        'dev/godpc/industrialcolonies/mixin/KjsGenRecipeReviewMixin$1.class',
        'dev/godpc/industrialcolonies/mixin/KjsGenS2CPayloadMixin.class',
        'dev/godpc/industrialcolonies/mixin/KjsGenServerProjectStoreAccessor.class',
        'dev/godpc/industrialcolonies/mixin/KjsGenScriptAssemblerMixin.class'
    )

    foreach ($name in $featureClassNames) {
        Write-ZipBytes -Archive $output -Name $name -Bytes (Read-ZipBytes -Archive $feature -Name $name)
    }

    $mixinConfigName = 'industrial_colonies.mixins.json'
    $mixinConfig = Read-ZipText -Archive $output -Name $mixinConfigName | ConvertFrom-Json
    $commonMixins = [System.Collections.Generic.List[string]]::new()
    foreach ($name in $mixinConfig.mixins) {
        $commonMixins.Add([string]$name)
    }
    foreach ($name in @('KjsGenS2CPayloadMixin')) {
        if (-not $commonMixins.Contains($name)) {
            $commonMixins.Add($name)
        }
    }
    $mixinConfig.mixins = @($commonMixins)
    $clientMixins = [System.Collections.Generic.List[string]]::new()
    foreach ($name in $mixinConfig.client) {
        $clientMixins.Add([string]$name)
    }
    foreach ($name in @('KjsGenRecipeReviewMixin', 'KjsGenServerProjectStoreAccessor')) {
        if (-not $clientMixins.Contains($name)) {
            $clientMixins.Add($name)
        }
    }
    $mixinConfig.client = @($clientMixins)
    $mixinJson = $mixinConfig | ConvertTo-Json -Depth 20
    Write-ZipText -Archive $output -Name $mixinConfigName -Text ($mixinJson + "`n")

    $languageName = 'assets/industrial_colonies/lang/en_us.json'
    $baseLanguage = Read-ZipText -Archive $output -Name $languageName | ConvertFrom-Json -AsHashtable
    $featureLanguage = Read-ZipText -Archive $feature -Name $languageName | ConvertFrom-Json -AsHashtable
    foreach ($entry in $featureLanguage.GetEnumerator()) {
        if ([string]$entry.Key -like 'industrial_colonies.kjsgen.review.*') {
            $baseLanguage[$entry.Key] = $entry.Value
        }
    }
    $languageJson = $baseLanguage | ConvertTo-Json -Depth 20
    Write-ZipText -Archive $output -Name $languageName -Text ($languageJson + "`n")

    $machineEnvironmentName = 'data/industrial_colonies/tier_recipe_environments.json'
    $reviewHelpName = 'data/industrial_colonies/recipe_review_help.json'
    Write-ZipBytes -Archive $output -Name $reviewHelpName -Bytes (Read-ZipBytes -Archive $feature -Name $reviewHelpName)
    Write-ZipBytes `
        -Archive $output `
        -Name $machineEnvironmentName `
        -Bytes (Read-ZipBytes -Archive $feature -Name $machineEnvironmentName)
}
finally {
    $output.Dispose()
    $feature.Dispose()
}

Write-Output $outputPath
