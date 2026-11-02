// priority: -10001
// Mining-derived inputs only. Preserve dust cleaning, ingots and machine synthesis.
ServerEvents.recipes(event => {
  const miningInputs = [
  "allthemodium:allthemodium_ore",
  "allthemodium:allthemodium_slate_ore",
  "allthemodium:vibranium_ore",
  "allthemodium:other_vibranium_ore",
  "allthemodium:unobtainium_ore",
  "allthemodium:raw_allthemodium",
  "allthemodium:raw_allthemodium_block",
  "#c:ores/allthemodium",
  "#c:raw_materials/allthemodium",
  "#c:storage_blocks/raw_allthemodium",
  "allthemodium:raw_vibranium",
  "allthemodium:raw_vibranium_block",
  "#c:ores/vibranium",
  "#c:raw_materials/vibranium",
  "#c:storage_blocks/raw_vibranium",
  "allthemodium:raw_unobtainium",
  "allthemodium:raw_unobtainium_block",
  "#c:ores/unobtainium",
  "#c:raw_materials/unobtainium",
  "#c:storage_blocks/raw_unobtainium"
];
  miningInputs.forEach(input => event.remove({input:input}));
  console.info("[Industrial Colonies] Allthemodium ore/raw input exclusions registered; dust processing preserved.");
});
