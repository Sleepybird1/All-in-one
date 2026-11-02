// priority: -10000
// Supersedes six-only restriction. Preserve all other processing and exact yields.
ServerEvents.recipes(event => {
  const exclusions = [
  {
    "id": "mekanism:enriching/ice_shard_or_to_ice_shards",
    "output": "ad_astra:ice_shard",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "allthemodium:processing/allthemodium/dust/from_ore",
    "output": "allthemodium:allthemodium_dust",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "allthemodium:processing/allthemodium/dust/from_raw_block",
    "output": "allthemodium:allthemodium_dust",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "allthemodium:processing/allthemodium/dust/from_raw_ore",
    "output": "allthemodium:allthemodium_dust",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "allthemodium:processing/unobtainium/dust/from_ore",
    "output": "allthemodium:unobtainium_dust",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "allthemodium:processing/unobtainium/dust/from_raw_block",
    "output": "allthemodium:unobtainium_dust",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "allthemodium:processing/unobtainium/dust/from_raw_ore",
    "output": "allthemodium:unobtainium_dust",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "allthemodium:processing/vibranium/dust/from_ore",
    "output": "allthemodium:vibranium_dust",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "allthemodium:processing/vibranium/dust/from_raw_block",
    "output": "allthemodium:vibranium_dust",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "allthemodium:processing/vibranium/dust/from_raw_ore",
    "output": "allthemodium:vibranium_dust",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/brick_slabs_to_polished",
    "output": "deeperdarker:polished_gloomslate_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/brick_stairs_to_polished",
    "output": "deeperdarker:polished_gloomslate_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/brick_wall_to_polished",
    "output": "deeperdarker:polished_gloomslate_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/bricks_to_polished",
    "output": "deeperdarker:polished_gloomslate",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/cut_slabs_to_smooth",
    "output": "deeperdarker:smooth_gloomslate_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/cut_stairs_to_smooth",
    "output": "deeperdarker:smooth_gloomslate_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/cut_to_smooth",
    "output": "deeperdarker:smooth_gloomslate",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/cut_wall_to_smooth",
    "output": "deeperdarker:smooth_gloomslate_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/from_cobbled",
    "output": "deeperdarker:gloomslate",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/from_cobbled_slabs",
    "output": "deeperdarker:gloomslate_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/from_cobbled_stairs",
    "output": "deeperdarker:gloomslate_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/from_cobbled_wall",
    "output": "deeperdarker:gloomslate_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/polished_slabs_to_cut",
    "output": "deeperdarker:cut_gloomslate_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/polished_stairs_to_cut",
    "output": "deeperdarker:cut_gloomslate_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/polished_to_cut",
    "output": "deeperdarker:cut_gloomslate",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/polished_wall_to_cut",
    "output": "deeperdarker:cut_gloomslate_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/slabs_to_smooth",
    "output": "deeperdarker:smooth_gloomslate_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/stairs_to_smooth",
    "output": "deeperdarker:smooth_gloomslate_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/tile_slabs_to_brick",
    "output": "deeperdarker:gloomslate_brick_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/tile_stairs_to_brick",
    "output": "deeperdarker:gloomslate_brick_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/tile_wall_to_brick",
    "output": "deeperdarker:gloomslate_brick_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/tiles_to_bricks",
    "output": "deeperdarker:gloomslate_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/to_smooth",
    "output": "deeperdarker:smooth_gloomslate",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/gloomslate/wall_to_smooth",
    "output": "deeperdarker:smooth_gloomslate_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/brick_slabs_to_polished",
    "output": "deeperdarker:polished_sculk_stone_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/brick_stairs_to_polished",
    "output": "deeperdarker:polished_sculk_stone_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/brick_wall_to_polished",
    "output": "deeperdarker:polished_sculk_stone_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/bricks_to_polished",
    "output": "deeperdarker:polished_sculk_stone",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/cut_slabs_to_smooth",
    "output": "deeperdarker:smooth_sculk_stone_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/cut_stairs_to_smooth",
    "output": "deeperdarker:smooth_sculk_stone_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/cut_to_smooth",
    "output": "deeperdarker:smooth_sculk_stone",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/cut_wall_to_smooth",
    "output": "deeperdarker:smooth_sculk_stone_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/from_cobbled",
    "output": "deeperdarker:sculk_stone",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/from_cobbled_slabs",
    "output": "deeperdarker:sculk_stone_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/from_cobbled_stairs",
    "output": "deeperdarker:sculk_stone_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/from_cobbled_wall",
    "output": "deeperdarker:sculk_stone_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/polished_slabs_to_cut",
    "output": "deeperdarker:cut_sculk_stone_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/polished_stairs_to_cut",
    "output": "deeperdarker:cut_sculk_stone_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/polished_to_cut",
    "output": "deeperdarker:cut_sculk_stone",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/polished_wall_to_cut",
    "output": "deeperdarker:cut_sculk_stone_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/slabs_to_smooth",
    "output": "deeperdarker:smooth_sculk_stone_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/stairs_to_smooth",
    "output": "deeperdarker:smooth_sculk_stone_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/tile_slabs_to_brick",
    "output": "deeperdarker:sculk_stone_brick_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/tile_stairs_to_brick",
    "output": "deeperdarker:sculk_stone_brick_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/tile_wall_to_brick",
    "output": "deeperdarker:sculk_stone_brick_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/tiles_to_bricks",
    "output": "deeperdarker:sculk_stone_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/to_smooth",
    "output": "deeperdarker:smooth_sculk_stone",
    "reason": "decorative block conversion"
  },
  {
    "id": "deeperdarker:compatibility/mekanism/enriching/conversion/sculk_stone/wall_to_smooth",
    "output": "deeperdarker:smooth_sculk_stone_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/certus_quartz/enriching/block_to_pillar",
    "output": "ae2:quartz_pillar",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/certus_quartz/enriching/chiseled_block_to_block",
    "output": "ae2:quartz_block",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/certus_quartz/enriching/chiseled_slab_to_slab",
    "output": "ae2:quartz_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/certus_quartz/enriching/chiseled_stairs_to_stairs",
    "output": "ae2:quartz_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/certus_quartz/enriching/chiseled_wall_to_wall",
    "output": "ae2:quartz_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/certus_quartz/enriching/pillar_slab_to_chiseled_slab",
    "output": "ae2:chiseled_quartz_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/certus_quartz/enriching/pillar_stairs_to_chiseled_stairs",
    "output": "ae2:chiseled_quartz_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/certus_quartz/enriching/pillar_to_chiseled_block",
    "output": "ae2:chiseled_quartz_block",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/certus_quartz/enriching/pillar_wall_to_chiseled_wall",
    "output": "ae2:chiseled_quartz_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/certus_quartz/enriching/slab_to_pillar_slab",
    "output": "ae2:quartz_pillar_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/certus_quartz/enriching/stairs_to_pillar_stairs",
    "output": "ae2:quartz_pillar_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/certus_quartz/enriching/wall_to_pillar_wall",
    "output": "ae2:quartz_pillar_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/sky_stone/enriching/brick_slab_to_small_brick_slab",
    "output": "ae2:sky_stone_small_brick_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/sky_stone/enriching/brick_stairs_to_small_brick_stairs",
    "output": "ae2:sky_stone_small_brick_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/sky_stone/enriching/brick_to_small_brick",
    "output": "ae2:sky_stone_small_brick",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/sky_stone/enriching/brick_wall_to_small_brick_wall",
    "output": "ae2:sky_stone_small_brick_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/sky_stone/enriching/chest_to_smooth_chest",
    "output": "ae2:smooth_sky_stone_chest",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/sky_stone/enriching/slab_to_smooth_slab",
    "output": "ae2:smooth_sky_stone_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/sky_stone/enriching/smooth_slab_to_brick_slab",
    "output": "ae2:sky_stone_brick_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/sky_stone/enriching/smooth_stairs_to_brick_stairs",
    "output": "ae2:sky_stone_brick_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/sky_stone/enriching/smooth_to_brick",
    "output": "ae2:sky_stone_brick",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/sky_stone/enriching/smooth_wall_to_brick_wall",
    "output": "ae2:sky_stone_brick_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/sky_stone/enriching/stairs_to_smooth_stairs",
    "output": "ae2:smooth_sky_stone_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/ae2/decorative/sky_stone/enriching/wall_to_smooth_wall",
    "output": "ae2:smooth_sky_stone_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/conversion_chiseled_dacite_bricks",
    "output": "biomeswevegone:dacite_tiles",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/conversion_cracked_dacite_bricks",
    "output": "biomeswevegone:dacite_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/conversion_dacite",
    "output": "biomeswevegone:cracked_dacite_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/conversion_dacite_bricks",
    "output": "biomeswevegone:chiseled_dacite_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/conversion_dacite_cobblestone",
    "output": "biomeswevegone:dacite",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/conversion_dacite_tiles",
    "output": "biomeswevegone:dacite_cobblestone",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/slabs_conversion_chiseled_dacite_bricks",
    "output": "biomeswevegone:dacite_tile_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/slabs_conversion_cracked_dacite_bricks",
    "output": "biomeswevegone:dacite_brick_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/slabs_conversion_dacite",
    "output": "biomeswevegone:cracked_dacite_brick_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/slabs_conversion_dacite_bricks",
    "output": "biomeswevegone:chiseled_dacite_brick_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/slabs_conversion_dacite_cobblestone",
    "output": "biomeswevegone:dacite_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/slabs_conversion_dacite_tiles",
    "output": "biomeswevegone:dacite_cobblestone_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/stairs_conversion_chiseled_dacite_bricks",
    "output": "biomeswevegone:dacite_tile_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/stairs_conversion_cracked_dacite_bricks",
    "output": "biomeswevegone:dacite_brick_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/stairs_conversion_dacite",
    "output": "biomeswevegone:cracked_dacite_brick_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/stairs_conversion_dacite_bricks",
    "output": "biomeswevegone:chiseled_dacite_brick_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/stairs_conversion_dacite_cobblestone",
    "output": "biomeswevegone:dacite_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/stairs_conversion_dacite_tiles",
    "output": "biomeswevegone:dacite_cobblestone_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/walls_conversion_chiseled_dacite_bricks",
    "output": "biomeswevegone:dacite_tile_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/walls_conversion_cracked_dacite_bricks",
    "output": "biomeswevegone:dacite_brick_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/walls_conversion_dacite",
    "output": "biomeswevegone:cracked_dacite_brick_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/walls_conversion_dacite_bricks",
    "output": "biomeswevegone:chiseled_dacite_brick_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/walls_conversion_dacite_cobblestone",
    "output": "biomeswevegone:dacite_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/dacite/walls_conversion_dacite_tiles",
    "output": "biomeswevegone:dacite_cobblestone_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/mossy_stone/conversion_mossy_stone",
    "output": "minecraft:stone",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/mossy_stone/slabs_conversion_mossy_stone",
    "output": "minecraft:stone_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/mossy_stone/stairs_conversion_mossy_stone",
    "output": "minecraft:stone_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/conversion_chiseled_red_rock_bricks",
    "output": "biomeswevegone:red_rock_tiles",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/conversion_cracked_red_rock_bricks",
    "output": "biomeswevegone:red_rock_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/conversion_mossy_red_rock_bricks",
    "output": "biomeswevegone:red_rock_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/conversion_polished_red_rock",
    "output": "biomeswevegone:cracked_red_rock_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/conversion_red_rock",
    "output": "biomeswevegone:polished_red_rock",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/conversion_red_rock_bricks",
    "output": "biomeswevegone:chiseled_red_rock_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/conversion_red_rock_tiles",
    "output": "biomeswevegone:red_rock",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/slabs_conversion_chiseled_red_rock_bricks",
    "output": "biomeswevegone:red_rock_tile_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/slabs_conversion_cracked_red_rock_bricks",
    "output": "biomeswevegone:red_rock_brick_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/slabs_conversion_mossy_red_rock_bricks",
    "output": "biomeswevegone:red_rock_brick_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/slabs_conversion_polished_red_rock",
    "output": "biomeswevegone:cracked_red_rock_brick_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/slabs_conversion_red_rock",
    "output": "biomeswevegone:polished_red_rock_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/slabs_conversion_red_rock_bricks",
    "output": "biomeswevegone:chiseled_red_rock_brick_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/slabs_conversion_red_rock_tiles",
    "output": "biomeswevegone:red_rock_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/stairs_conversion_chiseled_red_rock_bricks",
    "output": "biomeswevegone:red_rock_tile_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/stairs_conversion_cracked_red_rock_bricks",
    "output": "biomeswevegone:red_rock_brick_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/stairs_conversion_mossy_red_rock_bricks",
    "output": "biomeswevegone:red_rock_brick_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/stairs_conversion_polished_red_rock",
    "output": "biomeswevegone:cracked_red_rock_brick_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/stairs_conversion_red_rock",
    "output": "biomeswevegone:polished_red_rock_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/stairs_conversion_red_rock_bricks",
    "output": "biomeswevegone:chiseled_red_rock_brick_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/stairs_conversion_red_rock_tiles",
    "output": "biomeswevegone:red_rock_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/walls_conversion_chiseled_red_rock_bricks",
    "output": "biomeswevegone:red_rock_tile_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/walls_conversion_cracked_red_rock_bricks",
    "output": "biomeswevegone:red_rock_brick_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/walls_conversion_mossy_red_rock_bricks",
    "output": "biomeswevegone:red_rock_brick_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/walls_conversion_polished_red_rock",
    "output": "biomeswevegone:cracked_red_rock_brick_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/walls_conversion_red_rock",
    "output": "biomeswevegone:polished_red_rock_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/walls_conversion_red_rock_bricks",
    "output": "biomeswevegone:chiseled_red_rock_brick_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/red_rock/walls_conversion_red_rock_tiles",
    "output": "biomeswevegone:red_rock_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/conversion_chiseled_white_dacite_bricks",
    "output": "biomeswevegone:white_dacite_tiles",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/conversion_cracked_white_dacite_bricks",
    "output": "biomeswevegone:white_dacite_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/conversion_white_dacite",
    "output": "biomeswevegone:cracked_white_dacite_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/conversion_white_dacite_bricks",
    "output": "biomeswevegone:chiseled_white_dacite_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/conversion_white_dacite_cobblestone",
    "output": "biomeswevegone:white_dacite",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/conversion_white_dacite_tiles",
    "output": "biomeswevegone:white_dacite_cobblestone",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/slabs_conversion_chiseled_white_dacite_bricks",
    "output": "biomeswevegone:white_dacite_tile_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/slabs_conversion_cracked_white_dacite_bricks",
    "output": "biomeswevegone:white_dacite_brick_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/slabs_conversion_white_dacite",
    "output": "biomeswevegone:cracked_white_dacite_brick_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/slabs_conversion_white_dacite_bricks",
    "output": "biomeswevegone:chiseled_white_dacite_brick_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/slabs_conversion_white_dacite_cobblestone",
    "output": "biomeswevegone:white_dacite_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/slabs_conversion_white_dacite_tiles",
    "output": "biomeswevegone:white_dacite_cobblestone_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/stairs_conversion_chiseled_white_dacite_bricks",
    "output": "biomeswevegone:white_dacite_tile_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/stairs_conversion_cracked_white_dacite_bricks",
    "output": "biomeswevegone:white_dacite_brick_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/stairs_conversion_white_dacite",
    "output": "biomeswevegone:cracked_white_dacite_brick_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/stairs_conversion_white_dacite_bricks",
    "output": "biomeswevegone:chiseled_white_dacite_brick_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/stairs_conversion_white_dacite_cobblestone",
    "output": "biomeswevegone:white_dacite_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/stairs_conversion_white_dacite_tiles",
    "output": "biomeswevegone:white_dacite_cobblestone_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/walls_conversion_chiseled_white_dacite_bricks",
    "output": "biomeswevegone:white_dacite_tile_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/walls_conversion_cracked_white_dacite_bricks",
    "output": "biomeswevegone:white_dacite_brick_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/walls_conversion_white_dacite",
    "output": "biomeswevegone:cracked_white_dacite_brick_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/walls_conversion_white_dacite_bricks",
    "output": "biomeswevegone:chiseled_white_dacite_brick_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/walls_conversion_white_dacite_cobblestone",
    "output": "biomeswevegone:white_dacite_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:compat/biomeswevegone/enriching/white_dacite/walls_conversion_white_dacite_tiles",
    "output": "biomeswevegone:white_dacite_cobblestone_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/basalt_or_smooth_to_polished_basalt",
    "output": "minecraft:polished_basalt",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/cracked_nether_bricks_to_nether_bricks",
    "output": "minecraft:nether_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/nether_bricks_to_chiseled_nether_bricks",
    "output": "minecraft:chiseled_nether_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/purpur_pillar_from_block",
    "output": "minecraft:purpur_pillar",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/andesite/slab_to_polished_slab",
    "output": "minecraft:polished_andesite_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/andesite/stairs_to_polished_stairs",
    "output": "minecraft:polished_andesite_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/andesite/to_polished",
    "output": "minecraft:polished_andesite",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/blackstone/bricks_to_chiseled_bricks",
    "output": "minecraft:chiseled_polished_blackstone",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/blackstone/cracked_bricks_to_bricks",
    "output": "minecraft:polished_blackstone_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/blackstone/to_cracked_bricks",
    "output": "minecraft:cracked_polished_blackstone_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/deepslate/chiseled_to_cracked_tile",
    "output": "minecraft:cracked_deepslate_tiles",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/deepslate/cobbled_slabs_to_polished",
    "output": "minecraft:polished_deepslate_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/deepslate/cobbled_stairs_to_polished",
    "output": "minecraft:polished_deepslate_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/deepslate/cobbled_wall_to_polished",
    "output": "minecraft:polished_deepslate_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/deepslate/cracked_bricks_to_bricks",
    "output": "minecraft:deepslate_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/deepslate/cracked_tile_to_tile",
    "output": "minecraft:deepslate_tiles",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/deepslate/from_cobbled",
    "output": "minecraft:deepslate",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/deepslate/polished_chiseled",
    "output": "minecraft:chiseled_deepslate",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/deepslate/polished_slabs_to_tile",
    "output": "minecraft:deepslate_tile_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/deepslate/polished_stairs_to_tile",
    "output": "minecraft:deepslate_tile_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/deepslate/polished_wall_to_tile",
    "output": "minecraft:deepslate_tile_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/deepslate/tile_slabs_to_brick",
    "output": "minecraft:deepslate_brick_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/deepslate/tile_stairs_to_brick",
    "output": "minecraft:deepslate_brick_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/deepslate/tile_wall_to_brick",
    "output": "minecraft:deepslate_brick_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/deepslate/tiles_to_cracked_bricks",
    "output": "minecraft:cracked_deepslate_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/deepslate/to_polished",
    "output": "minecraft:polished_deepslate",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/diorite/slab_to_polished_slab",
    "output": "minecraft:polished_diorite_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/diorite/stairs_to_polished_stairs",
    "output": "minecraft:polished_diorite_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/diorite/to_polished",
    "output": "minecraft:polished_diorite",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/granite/slab_to_polished_slab",
    "output": "minecraft:polished_granite_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/granite/stairs_to_polished_stairs",
    "output": "minecraft:polished_granite_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/granite/to_polished",
    "output": "minecraft:polished_granite",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/mossy/cobblestone",
    "output": "minecraft:cobblestone",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/mossy/cobblestone_slabs",
    "output": "minecraft:cobblestone_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/mossy/cobblestone_stairs",
    "output": "minecraft:cobblestone_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/mossy/cobblestone_walls",
    "output": "minecraft:cobblestone_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/mossy/stone_brick_slabs",
    "output": "minecraft:stone_brick_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/mossy/stone_brick_stairs",
    "output": "minecraft:stone_brick_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/mossy/stone_brick_walls",
    "output": "minecraft:stone_brick_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/mossy/stone_bricks",
    "output": "minecraft:stone_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/mud/packed_to_bricks",
    "output": "minecraft:mud_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/quartz/from_smooth_quartz",
    "output": "minecraft:quartz_block",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/quartz/smooth_slab_to_slab",
    "output": "minecraft:quartz_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/quartz/smooth_stairs_to_stairs",
    "output": "minecraft:quartz_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/stone/bricks_to_chiseled_bricks",
    "output": "minecraft:chiseled_stone_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/stone/cracked_bricks_to_bricks",
    "output": "minecraft:stone_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/stone/to_cracked_bricks",
    "output": "minecraft:cracked_stone_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/tuff/brick_to_chiseled",
    "output": "minecraft:chiseled_tuff",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/tuff/from_chiseled",
    "output": "minecraft:tuff",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/tuff/polished_slabs_to_brick",
    "output": "minecraft:tuff_brick_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/tuff/polished_stairs_to_brick",
    "output": "minecraft:tuff_brick_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/tuff/polished_to_brick",
    "output": "minecraft:tuff_bricks",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/tuff/polished_wall_to_brick",
    "output": "minecraft:tuff_brick_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/tuff/slab_from_brick",
    "output": "minecraft:tuff_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/tuff/slabs_to_polished",
    "output": "minecraft:polished_tuff_slab",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/tuff/stairs_from_brick",
    "output": "minecraft:tuff_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/tuff/stairs_to_polished",
    "output": "minecraft:polished_tuff_stairs",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/tuff/to_polished",
    "output": "minecraft:polished_tuff",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/tuff/wall_from_brick",
    "output": "minecraft:tuff_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:enriching/conversion/tuff/wall_to_polished",
    "output": "minecraft:polished_tuff_wall",
    "reason": "decorative block conversion"
  },
  {
    "id": "mekanism:processing/coal/from_ore",
    "output": "minecraft:coal",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/copper/dust/from_ore",
    "output": "mekanism:dust_copper",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/copper/dust/from_raw_block",
    "output": "mekanism:dust_copper",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/copper/dust/from_raw_ore",
    "output": "mekanism:dust_copper",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/diamond/from_ore",
    "output": "minecraft:diamond",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/emerald/from_ore",
    "output": "minecraft:emerald",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/fluorite/from_ore",
    "output": "mekanism:fluorite_gem",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/gold/dust/from_ore",
    "output": "mekanism:dust_gold",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/gold/dust/from_raw_block",
    "output": "mekanism:dust_gold",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/gold/dust/from_raw_ore",
    "output": "mekanism:dust_gold",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/iron/dust/from_ore",
    "output": "mekanism:dust_iron",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/iron/dust/from_raw_block",
    "output": "mekanism:dust_iron",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/iron/dust/from_raw_ore",
    "output": "mekanism:dust_iron",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/lapis_lazuli/from_ore",
    "output": "minecraft:lapis_lazuli",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/lead/dust/from_ore",
    "output": "mekanism:dust_lead",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/lead/dust/from_raw_block",
    "output": "mekanism:dust_lead",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/lead/dust/from_raw_ore",
    "output": "mekanism:dust_lead",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/netherite/ancient_debris_to_scrap",
    "output": "minecraft:netherite_scrap",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/osmium/dust/from_ore",
    "output": "mekanism:dust_osmium",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/osmium/dust/from_raw_block",
    "output": "mekanism:dust_osmium",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/osmium/dust/from_raw_ore",
    "output": "mekanism:dust_osmium",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/quartz/from_ore",
    "output": "minecraft:quartz",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/redstone/from_ore",
    "output": "minecraft:redstone",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/tin/dust/from_ore",
    "output": "mekanism:dust_tin",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/tin/dust/from_raw_block",
    "output": "mekanism:dust_tin",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/tin/dust/from_raw_ore",
    "output": "mekanism:dust_tin",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/uranium/dust/from_ore",
    "output": "mekanism:dust_uranium",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/uranium/dust/from_raw_block",
    "output": "mekanism:dust_uranium",
    "reason": "ore/raw multiplication"
  },
  {
    "id": "mekanism:processing/uranium/dust/from_raw_ore",
    "output": "mekanism:dust_uranium",
    "reason": "ore/raw multiplication"
  }
];
  exclusions.forEach(r => event.remove({id:r.id,type:"mekanism:enriching",output:r.output}));
  console.info("[Industrial Colonies] Targeted Enrichment ore/raw and decorative exclusions registered.");
});
