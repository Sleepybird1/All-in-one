package dev.godpc.industrialcolonies.mixin;

import dev.latvian.mods.kubejs.recipe.schema.RecipeSchemaRegistry;
import net.minecraft.resources.ResourceLocation;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** CM registers Java schemas after JSON loading; replace only its incompatible entity alias. */
@Pseudo
@Mixin(targets="fr.lucreeper74.createmetallurgy.compat.kubejs.CreateMetallurgyKJS",remap=false)
public abstract class MetallurgyEntitySchemaMixin {
    @Inject(method="registerRecipeSchemas",at=@At("TAIL"))
    private void industrialColonies$emptyEntityInputs(RecipeSchemaRegistry registry,CallbackInfo ci) {
        registry.namespace("createmetallurgy").withExistingParent("entity_melting",
                ResourceLocation.parse("industrial_colonies:metallurgy_entity_melting"));
    }
}
