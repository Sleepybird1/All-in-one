// priority: -20000
// Retired Neptunium suppliers leave these native crafting ingredients empty.
// Exact recipe IDs only: preserve items and all other acquisition routes.
ServerEvents.recipes(event => {
  event.remove({ id: 'aquaculture:neptunium_chestplate' })
  event.remove({ id: 'aquaculture:neptunium_axe' })
  event.remove({ id: 'aquaculture:neptunium_shovel' })
  event.remove({ id: 'aquaculture:neptunium_leggings' })
  event.remove({ id: 'aquaculture:neptunium_boots' })
  event.remove({ id: 'aquaculture:neptunium_bow' })
  event.remove({ id: 'aquaculture:neptunium_sword' })
  event.remove({ id: 'aquaculture:neptunium_fishing_rod' })
  event.remove({ id: 'aquaculture:neptunium_hoe' })
  event.remove({ id: 'aquaculture:neptunium_fillet_knife' })
  event.remove({ id: 'aquaculture:neptunium_helmet' })
  event.remove({ id: 'aquaculture:neptunes_bounty' })
  event.remove({ id: 'aquaculture:neptunium_pickaxe' })
})
