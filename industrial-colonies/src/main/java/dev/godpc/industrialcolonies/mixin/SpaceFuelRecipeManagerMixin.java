package dev.godpc.industrialcolonies.mixin;

import com.google.common.collect.ImmutableMultimap;
import dev.godpc.industrialcolonies.processing.SpaceFuelRecipeNormalizer;
import java.util.Map;
import net.minecraft.core.HolderLookup;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.crafting.*;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Staged opt-in server publication; client packets are consumed without rewriting them. */
@Mixin(value=RecipeManager.class,priority=800)
public abstract class SpaceFuelRecipeManagerMixin {
    @Shadow @Final private HolderLookup.Provider registries;
    @Shadow private Map<ResourceLocation,RecipeHolder<?>> byName;
    @Shadow private com.google.common.collect.Multimap<RecipeType<?>,RecipeHolder<?>> byType;
    @Inject(method="apply(Ljava/util/Map;Lnet/minecraft/server/packs/resources/ResourceManager;Lnet/minecraft/util/profiling/ProfilerFiller;)V",at=@At("RETURN"))
    private void industrialColonies$applySpaceFuel(CallbackInfo ci){industrialColonies$publishSpaceFuel();}
    @Inject(method="replaceRecipes",at=@At("RETURN"))
    private void industrialColonies$replaceServerSpaceFuel(CallbackInfo ci){
        var server=net.neoforged.neoforge.server.ServerLifecycleHooks.getCurrentServer();
        if(server!=null&&server.isSameThread())industrialColonies$publishSpaceFuel();
    }
    @Unique private void industrialColonies$publishSpaceFuel(){
        if(!SpaceFuelRecipeNormalizer.enabled())return;
        var result=SpaceFuelRecipeNormalizer.normalize(byName,registries);
        if(result.held()){
            org.slf4j.LoggerFactory.getLogger(SpaceFuelRecipeManagerMixin.class).warn("Space fuel identities held: {}",result.status());return;
        }
        if(result.changed()==0)return;
        var types=ImmutableMultimap.<RecipeType<?>,RecipeHolder<?>>builder();
        result.recipes().values().forEach(h->types.put(h.value().getType(),h));
        byName=result.recipes();byType=types.build();
    }
}
