// Original recipe review: registrations retained below, temporarily inactive.
function IC_originalRecipeReview_skip() {}
// priority: -10000
// STAGED ONLY. User owns replacement recipes in approved_recipes.json.
IC_originalRecipeReview_skip(event => {
  function reject(recipe) {
    // Inspect content so a user's zinc replacement using a stock ID survives.
    recipe.serialize();
    var data = JSON.parse(String(recipe.json));
    var outputs = JSON.stringify(data.results || data.result || data.output || {});
    var inputs = JSON.stringify(data.ingredients || data.key || data.input || {});
    return outputs.indexOf('create:andesite_alloy"') >= 0 &&
      /"(?:minecraft:iron_nugget|c:nuggets\/iron|forge:nuggets\/iron)"/.test(inputs);
  }
  event.forEachRecipe({}, recipe => { if (reject(recipe)) recipe.remove(); });
  event.addedRecipes.removeIf(recipe => reject(recipe));
});
