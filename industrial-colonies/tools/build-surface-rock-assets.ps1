$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\src\main\resources'))
$materials=@('hematite','magnetite','chalcopyrite','sphalerite','galena','pentlandite','bauxite','spodumene_rock','argentite','wolframite_rock','dolomite','graphite_rock','phosphate_rock','ultramafic_rock','ilmenite','bertrandite','borax_rock','cassiterite','chromite','cinnabar','coal')
function Save-Json($relative,$value) {
    $path=Join-Path $root $relative
    New-Item -ItemType Directory -Force -Path (Split-Path $path -Parent) | Out-Null
    $value | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $path -Encoding utf8
}
$langPath=Join-Path $root 'assets\industrial_colonies\lang\en_us.json'
$lang=Get-Content -LiteralPath $langPath -Raw | ConvertFrom-Json -AsHashtable
foreach ($material in $materials) {
    $id='loose_'+$material
    $texture=if($material -eq 'coal') {'minecraft:block/coal_block'} elseif($material -eq 'spodumene_rock') {'industrial_colonies:block/geology/spodumene_rock_side'} else {'industrial_colonies:block/geology/'+$material}
    $elements=@()
    foreach ($box in @(@(4,0,5,11,3,12),@(8,0,3,13,2,8))) {
        $faces=[ordered]@{}
        foreach ($face in @('north','east','south','west','up','down')) { $faces[$face]=@{texture='#rock';uv=@(0,0,16,16)} }
        $elements+=@{from=@($box[0],$box[1],$box[2]);to=@($box[3],$box[4],$box[5]);faces=$faces}
    }
    Save-Json ('assets\industrial_colonies\models\block\'+$id+'.json') ([ordered]@{parent='minecraft:block/block';textures=@{particle=$texture;rock=$texture};elements=$elements})
    Save-Json ('assets\industrial_colonies\models\item\'+$id+'.json') @{parent='industrial_colonies:block/'+$id}
    Save-Json ('assets\industrial_colonies\blockstates\'+$id+'.json') @{variants=@{''=@{model='industrial_colonies:block/'+$id}}}
    $drop=if($material -eq 'coal') {'minecraft:coal'} else {'industrial_colonies:'+$material}
    Save-Json ('data\industrial_colonies\loot_table\blocks\'+$id+'.json') @{type='minecraft:block';pools=@(@{rolls=1;entries=@(@{type='minecraft:item';name=$drop});conditions=@(@{condition='minecraft:survives_explosion'})})}
    $display=(Get-Culture).TextInfo.ToTitleCase($material.Replace('_',' '))
    $lang['block.industrial_colonies.'+$id]='Loose '+$display+$(if($display.EndsWith(' Rock')){''}else{' Rock'})
}
$lang['tooltip.industrial_colonies.surface_rock']='A prospecting clue: matching deposits are usually nearby, but not guaranteed. Collect by hand.'
Save-Json 'assets\industrial_colonies\lang\en_us.json' $lang
Write-Output 'Generated 21 ground-rock models, items, blockstates, loot tables and translations; existing textures unchanged.'
