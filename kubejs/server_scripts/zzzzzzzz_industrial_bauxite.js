// priority: -10004
// Approved existing yields; no project export or broad script reactivation.
ServerEvents.recipes(event => {
  event.remove({id:"industrial_colonies:processing/aluminum/crush_bauxite"});
  event.custom({"type": "create:crushing", "ingredients": [{"item": "industrial_colonies:bauxite"}], "results": [{"id": "tfmg:bauxite_powder", "count": 4}], "processing_time": 250}).id("industrial_colonies:processing/aluminum/crush_bauxite");
  event.remove({id:"industrial_colonies:processing/aluminum/crush_rich_bauxite"});
  event.custom({"type": "create:crushing", "ingredients": [{"item": "industrial_colonies:rich_bauxite"}], "results": [{"id": "tfmg:bauxite_powder", "count": 8}], "processing_time": 250}).id("industrial_colonies:processing/aluminum/crush_rich_bauxite");
});
