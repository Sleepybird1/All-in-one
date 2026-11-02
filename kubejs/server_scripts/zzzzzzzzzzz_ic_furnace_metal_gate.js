// priority: -22000
// User rule: metals require retained processing machines, not ordinary cooking.
ServerEvents.recipes(event => {
  const metals = ["ad_astra:calorite_ingot", "ad_astra:desh_ingot", "ad_astra:ostrum_ingot", "ad_astra:steel_ingot", "advanced_ae:quantum_alloy", "allthemodium:allthemodium_ingot", "allthemodium:unobtainium_allthemodium_alloy_ingot", "allthemodium:unobtainium_ingot", "allthemodium:unobtainium_vibranium_alloy_ingot", "allthemodium:vibranium_allthemodium_alloy_ingot", "allthemodium:vibranium_ingot", "aquaculture:neptunium_ingot", "bigreactors:blutonium_ingot", "bigreactors:cyanite_ingot", "bigreactors:graphite_ingot", "bigreactors:inanite_ingot", "bigreactors:insanite_ingot", "bigreactors:ludicrite_ingot", "bigreactors:magentite_ingot", "bigreactors:ridiculite_ingot", "bigreactors:yellorium_ingot", "create:andesite_alloy", "create:brass_ingot", "create:zinc_ingot", "createaddition:electrum_ingot", "createbigcannons:bronze_ingot", "createbigcannons:cast_iron_ingot", "createbigcannons:nethersteel_ingot", "createbigcannons:steel_ingot", "createmechanisms:bronze", "createmetallurgy:obdurium_ingot", "createmetallurgy:steel_ingot", "createmetallurgy:tungsten_ingot", "extendedae:entro_ingot", "i_architecture:industrial_iron_ingot", "iceandfire:dragonsteel_fire_ingot", "iceandfire:dragonsteel_ice_ingot", "iceandfire:dragonsteel_lightning_ingot", "iceandfire:ghost_ingot", "iceandfire:silver_ingot", "immersiveengineering:ingot_aluminum", "immersiveengineering:ingot_constantan", "immersiveengineering:ingot_electrum", "immersiveengineering:ingot_hop_graphite", "immersiveengineering:ingot_lead", "immersiveengineering:ingot_nickel", "immersiveengineering:ingot_silver", "immersiveengineering:ingot_steel", "immersiveengineering:ingot_uranium", "irons_spellbooks:arcane_ingot", "irons_spellbooks:mithril_ingot", "irons_spellbooks:pyrium_ingot", "megacells:sky_bronze_ingot", "megacells:sky_osmium_ingot", "megacells:sky_steel_ingot", "mekanism:ingot_bronze", "mekanism:ingot_lead", "mekanism:ingot_osmium", "mekanism:ingot_refined_glowstone", "mekanism:ingot_refined_obsidian", "mekanism:ingot_steel", "mekanism:ingot_tin", "mekanism:ingot_uranium", "minecraft:copper_ingot", "minecraft:gold_ingot", "minecraft:iron_ingot", "minecraft:netherite_ingot", "minecraft:netherite_scrap", "modernfoundry:amethyst_bronze_ingot", "modernfoundry:cinderslime_ingot", "modernfoundry:cobalt_ingot", "modernfoundry:fake_ingot", "modernfoundry:hepatizon_ingot", "modernfoundry:knightmetal_ingot", "modernfoundry:knightslime_ingot", "modernfoundry:manyullyn_ingot", "modernfoundry:pig_iron_ingot", "modernfoundry:queens_slime_ingot", "modernfoundry:rose_gold_ingot", "modernfoundry:scorched_brick", "modernfoundry:seared_brick", "modernfoundry:slimesteel_ingot", "modernfoundry:soulsteel_ingot", "modernfoundry:steel_ingot", "nuclearcraft:aluminum_ingot", "nuclearcraft:baratol_ingot", "nuclearcraft:beryllium_ingot", "nuclearcraft:boron_ingot", "nuclearcraft:bronze_ingot", "nuclearcraft:calcium_ingot", "nuclearcraft:carbon_manganese_ingot", "nuclearcraft:chromium_ingot", "nuclearcraft:cobalt_ingot", "nuclearcraft:electrum_ingot", "nuclearcraft:extreme_ingot", "nuclearcraft:ferroboron_ingot", "nuclearcraft:graphite_ingot", "nuclearcraft:hafnium_ingot", "nuclearcraft:hard_carbon_ingot", "nuclearcraft:hsla_steel_ingot", "nuclearcraft:iridium_ingot", "nuclearcraft:lead_ingot", "nuclearcraft:lead_platinum_ingot", "nuclearcraft:lithium_ingot", "nuclearcraft:lithium_manganese_dioxide_ingot", "nuclearcraft:magnesium_diboride_ingot", "nuclearcraft:magnesium_ingot", "nuclearcraft:manganese_dioxide_ingot", "nuclearcraft:manganese_ingot", "nuclearcraft:manganese_oxide_ingot", "nuclearcraft:neutronium_ingot", "nuclearcraft:nichrome_ingot", "nuclearcraft:niobium_ingot", "nuclearcraft:niobium_tin_ingot", "nuclearcraft:niobium_titanium_ingot", "nuclearcraft:osmiridium_ingot", "nuclearcraft:osmium_ingot", "nuclearcraft:palladium_ingot", "nuclearcraft:platinum_ingot", "nuclearcraft:potassium_ingot", "nuclearcraft:pyrolitic_carbon_ingot", "nuclearcraft:shibuichi_ingot", "nuclearcraft:sic_sic_cmc_ingot", "nuclearcraft:silicon_carbide_ingot", "nuclearcraft:silver_ingot", "nuclearcraft:sodium_ingot", "nuclearcraft:stainless_steel_ingot", "nuclearcraft:steel_ingot", "nuclearcraft:strontium_ingot", "nuclearcraft:super_alloy_ingot", "nuclearcraft:thermoconducting_ingot", "nuclearcraft:thorium_ingot", "nuclearcraft:tin_ingot", "nuclearcraft:tin_silver_ingot", "nuclearcraft:titanium_ingot", "nuclearcraft:tough_alloy_ingot", "nuclearcraft:tungsten_carbide_ingot", "nuclearcraft:tungsten_ingot", "nuclearcraft:uranium_ingot", "nuclearcraft:yttrium_ingot", "nuclearcraft:zinc_ingot", "nuclearcraft:zircaloy_ingot", "nuclearcraft:zirconium_ingot", "nuclearcraft:zirconium_molybdenum_ingot", "rocketnautics:titanium_alloy", "rocketnautics:titanium_ingot", "stellaris:desh_ingot", "stellaris:heavy_metal_ingot", "stellaris:neptunium_ingot", "stellaris:plutonium_ingot", "stellaris:steel_ingot", "stellaris:uranium_ingot", "tfmg:aluminum_ingot", "tfmg:cast_iron_ingot", "tfmg:constantan_ingot", "tfmg:lead_ingot", "tfmg:lithium_ingot", "tfmg:nickel_ingot", "tfmg:plastic_sheet", "tfmg:rubber_sheet", "tfmg:silicon_ingot", "tfmg:steel_ingot"];
  const types = ["minecraft:smelting", "minecraft:blasting", "minecraft:smoking", "minecraft:campfire_cooking"];
  metals.forEach(item => {
    if (!Item.exists(item)) return;
    types.forEach(type => event.remove({type: type, output: item}));
  });

  // Crushed ores require retained machine processing; default fan washing must not yield metal.
  event.remove({id: "create:splashing/crushed_raw_copper"});
  event.remove({id: "create:splashing/crushed_raw_gold"});
  event.remove({id: "create:splashing/crushed_raw_iron"});
  event.remove({id: "create:splashing/crushed_raw_zinc"});
  event.remove({id: "create:splashing/galosphere/crushed_raw_silver"});
  event.remove({id: "create:splashing/iceandfire/crushed_raw_silver"});
  event.remove({id: "create:splashing/oreganized/crushed_raw_lead"});
  event.remove({id: "create:splashing/oreganized/crushed_raw_silver"});
  event.remove({id: "create:splashing/thermal/crushed_raw_lead"});
  event.remove({id: "create:splashing/thermal/crushed_raw_nickel"});
  event.remove({id: "create:splashing/thermal/crushed_raw_silver"});
  event.remove({id: "create:splashing/thermal/crushed_raw_tin"});
  if (Item.exists("create:crushed_raw_copper")) {
    event.remove({type: "minecraft:smelting", input: "create:crushed_raw_copper"});
    event.remove({type: "minecraft:blasting", input: "create:crushed_raw_copper"});
    event.remove({type: "minecraft:smoking", input: "create:crushed_raw_copper"});
    event.remove({type: "minecraft:campfire_cooking", input: "create:crushed_raw_copper"});
  }
  if (Item.exists("create:crushed_raw_gold")) {
    event.remove({type: "minecraft:smelting", input: "create:crushed_raw_gold"});
    event.remove({type: "minecraft:blasting", input: "create:crushed_raw_gold"});
    event.remove({type: "minecraft:smoking", input: "create:crushed_raw_gold"});
    event.remove({type: "minecraft:campfire_cooking", input: "create:crushed_raw_gold"});
  }
  if (Item.exists("create:crushed_raw_iron")) {
    event.remove({type: "minecraft:smelting", input: "create:crushed_raw_iron"});
    event.remove({type: "minecraft:blasting", input: "create:crushed_raw_iron"});
    event.remove({type: "minecraft:smoking", input: "create:crushed_raw_iron"});
    event.remove({type: "minecraft:campfire_cooking", input: "create:crushed_raw_iron"});
  }
  if (Item.exists("create:crushed_raw_lead")) {
    event.remove({type: "minecraft:smelting", input: "create:crushed_raw_lead"});
    event.remove({type: "minecraft:blasting", input: "create:crushed_raw_lead"});
    event.remove({type: "minecraft:smoking", input: "create:crushed_raw_lead"});
    event.remove({type: "minecraft:campfire_cooking", input: "create:crushed_raw_lead"});
  }
  if (Item.exists("create:crushed_raw_nickel")) {
    event.remove({type: "minecraft:smelting", input: "create:crushed_raw_nickel"});
    event.remove({type: "minecraft:blasting", input: "create:crushed_raw_nickel"});
    event.remove({type: "minecraft:smoking", input: "create:crushed_raw_nickel"});
    event.remove({type: "minecraft:campfire_cooking", input: "create:crushed_raw_nickel"});
  }
  if (Item.exists("create:crushed_raw_silver")) {
    event.remove({type: "minecraft:smelting", input: "create:crushed_raw_silver"});
    event.remove({type: "minecraft:blasting", input: "create:crushed_raw_silver"});
    event.remove({type: "minecraft:smoking", input: "create:crushed_raw_silver"});
    event.remove({type: "minecraft:campfire_cooking", input: "create:crushed_raw_silver"});
  }
  if (Item.exists("create:crushed_raw_tin")) {
    event.remove({type: "minecraft:smelting", input: "create:crushed_raw_tin"});
    event.remove({type: "minecraft:blasting", input: "create:crushed_raw_tin"});
    event.remove({type: "minecraft:smoking", input: "create:crushed_raw_tin"});
    event.remove({type: "minecraft:campfire_cooking", input: "create:crushed_raw_tin"});
  }
  if (Item.exists("create:crushed_raw_zinc")) {
    event.remove({type: "minecraft:smelting", input: "create:crushed_raw_zinc"});
    event.remove({type: "minecraft:blasting", input: "create:crushed_raw_zinc"});
    event.remove({type: "minecraft:smoking", input: "create:crushed_raw_zinc"});
    event.remove({type: "minecraft:campfire_cooking", input: "create:crushed_raw_zinc"});
  }
  if (Item.exists("create:crushed_raw_aluminum")) {
    event.remove({type: "minecraft:smelting", input: "create:crushed_raw_aluminum"});
    event.remove({type: "minecraft:blasting", input: "create:crushed_raw_aluminum"});
    event.remove({type: "minecraft:smoking", input: "create:crushed_raw_aluminum"});
    event.remove({type: "minecraft:campfire_cooking", input: "create:crushed_raw_aluminum"});
  }
  if (Item.exists("create:crushed_raw_osmium")) {
    event.remove({type: "minecraft:smelting", input: "create:crushed_raw_osmium"});
    event.remove({type: "minecraft:blasting", input: "create:crushed_raw_osmium"});
    event.remove({type: "minecraft:smoking", input: "create:crushed_raw_osmium"});
    event.remove({type: "minecraft:campfire_cooking", input: "create:crushed_raw_osmium"});
  }
  if (Item.exists("create:crushed_raw_platinum")) {
    event.remove({type: "minecraft:smelting", input: "create:crushed_raw_platinum"});
    event.remove({type: "minecraft:blasting", input: "create:crushed_raw_platinum"});
    event.remove({type: "minecraft:smoking", input: "create:crushed_raw_platinum"});
    event.remove({type: "minecraft:campfire_cooking", input: "create:crushed_raw_platinum"});
  }
  if (Item.exists("create:crushed_raw_quicksilver")) {
    event.remove({type: "minecraft:smelting", input: "create:crushed_raw_quicksilver"});
    event.remove({type: "minecraft:blasting", input: "create:crushed_raw_quicksilver"});
    event.remove({type: "minecraft:smoking", input: "create:crushed_raw_quicksilver"});
    event.remove({type: "minecraft:campfire_cooking", input: "create:crushed_raw_quicksilver"});
  }
  if (Item.exists("create:crushed_raw_uranium")) {
    event.remove({type: "minecraft:smelting", input: "create:crushed_raw_uranium"});
    event.remove({type: "minecraft:blasting", input: "create:crushed_raw_uranium"});
    event.remove({type: "minecraft:smoking", input: "create:crushed_raw_uranium"});
    event.remove({type: "minecraft:campfire_cooking", input: "create:crushed_raw_uranium"});
  }
});
