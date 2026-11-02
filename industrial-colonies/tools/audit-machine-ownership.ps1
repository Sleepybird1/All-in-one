param([string]$LiveProject='C:\Users\GodPC\curseforge\minecraft\Instances\All in one\kjsgen\projects\default.json')
$ErrorActionPreference='Stop'
$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$data=Get-Content -LiteralPath $LiveProject -Raw | ConvertFrom-Json
function Summarize($card) {
    $out=@($card.slots.PSObject.Properties | Where-Object {$_.Name -match '^output'} | ForEach-Object {$_.Value.id})
    $machines=@($card.slots.PSObject.Properties | Where-Object {$_.Name -like '__machine*'} | ForEach-Object {$_.Value.id} | Sort-Object -Unique)
    $ingredients=@($card.slots.PSObject.Properties | Where-Object {$_.Name -notmatch '^output|^transitional|^__machine'} | ForEach-Object {$_.Value.id} | Sort-Object -Unique)
    [ordered]@{id=$card.recipeId;type=$card.type;outputs=$out;machines=$machines;ingredients=$ingredients;gridW=$card.params.gridW;gridH=$card.params.gridH}
}
$selected=@($data.recipes | Where-Object {$_.recipeId -match 'manufacturing/(weathered_iron|industrial_iron)/|mekanism_pre_nuclear/crusher|electronics/circuit_board|factory.*crushing'} | ForEach-Object {Summarize $_})
$mechanical=@($data.recipes | Where-Object {$_.type -eq 'kjsgen:create_mechanical_crafting'})
$oversize=@($mechanical | Where-Object {[int]$_.params.gridW -gt 7 -or [int]$_.params.gridH -gt 7} | ForEach-Object {Summarize $_})
$missingDimensions=@($mechanical | Where-Object {-not $_.params.gridW -or -not $_.params.gridH} | ForEach-Object {$_.recipeId})
$snapshot=[ordered]@{
    recordedAt=(Get-Date).ToString('o');scope='Read-only KJSGen project and local processing policy; not effective runtime certification'
    input=$LiveProject;sha256=(Get-FileHash -LiteralPath $LiveProject).Hash;recipeCards=$data.recipes.Count
    mechanicalCrafterCards=$mechanical.Count;oversizeCards=$oversize;missingGridDimensions=$missingDimensions
    gridCounts=@($mechanical | Group-Object {"$($_.params.gridW)x$($_.params.gridH)"} | ForEach-Object {[ordered]@{grid=$_.Name;count=$_.Count}})
    selectedCards=$selected
}
$snapshot | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $project 'design/machine_ownership_snapshot.json') -Encoding utf8
"Read-only audit: $($data.recipes.Count) cards; $($mechanical.Count) mechanical recipes; $($oversize.Count) oversized; $($missingDimensions.Count) missing dimensions."
