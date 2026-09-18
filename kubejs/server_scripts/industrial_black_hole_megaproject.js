// Industrial Colonies - post-nuclear Black Hole megaproject
//
// Each input is the highest (9x) AllTheCompressed tier of a factory-renewable
// bulk material. The recipe intentionally stays a normal 3x3 crafting grid:
// the difficulty is producing the mass, not finding a special workstation.

ServerEvents.recipes(event => {
  event.shaped(
    Item.of('industrial_colonies:black_hole'),
    [
      'CSG',
      'DBK',
      'LOP'
    ],
    {
      C: 'allthecompressed:cobblestone_9x',
      S: 'allthecompressed:stone_9x',
      G: 'allthecompressed:gravel_9x',
      D: 'allthecompressed:dirt_9x',
      B: 'allthecompressed:basalt_9x',
      K: 'allthecompressed:blackstone_9x',
      L: 'allthecompressed:oak_log_9x',
      O: 'allthecompressed:sand_9x',
      P: 'allthecompressed:oak_planks_9x'
    }
  ).id('industrial_colonies:megaproject/black_hole')

  console.info('[Industrial Colonies] Registered the staged 9x-compressed Black Hole megaproject recipe.')
})
