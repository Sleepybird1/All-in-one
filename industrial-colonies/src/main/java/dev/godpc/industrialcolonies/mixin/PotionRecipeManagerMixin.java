package dev.godpc.industrialcolonies.mixin;

import com.google.common.collect.ImmutableMultimap;
import dev.godpc.industrialcolonies.processing.PotionIdentityRuntime;
import dev.godpc.industrialcolonies.processing.PotionRecipeNormalizer;
import java.util.Map;
import net.minecraft.core.HolderLookup;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.crafting.*;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Unregistered by default; never enables producers before consumer publication. */
@Mixin(value=RecipeManager.class,priority=850)
public abstract class PotionRecipeManagerMixin {
    @Shadow @Final private HolderLookup.Provider registries;
    @Shadow private Map<ResourceLocation,RecipeHolder<?>> byName;
    @Shadow private com.google.common.collect.Multimap<RecipeType<?>,RecipeHolder<?>> byType;
    @Inject(method={"apply(Ljava/util/Map;Lnet/minecraft/server/packs/resources/ResourceManager;Lnet/minecraft/util/profiling/ProfilerFiller;)V","replaceRecipes"},at=@At("HEAD"))
    private void industrialColonies$holdPotionProducers(CallbackInfo ci) {
        PotionIdentityRuntime.invalidate((RecipeManager)(Object)this);
    }
    @Inject(method="apply(Ljava/util/Map;Lnet/minecraft/server/packs/resources/ResourceManager;Lnet/minecraft/util/profiling/ProfilerFiller;)V",at=@At("RETURN"))
    private void industrialColonies$publishPotionConsumers(CallbackInfo ci) {
        industrialColonies$normalizePotionConsumers();
    }
    @Inject(method="replaceRecipes",at=@At("RETURN"))
    private void industrialColonies$replaceServerPotionConsumers(CallbackInfo ci) {
        var server=net.neoforged.neoforge.server.ServerLifecycleHooks.getCurrentServer();
        if(server!=null&&server.isSameThread()) industrialColonies$normalizePotionConsumers();
    }
    @Unique private void industrialColonies$normalizePotionConsumers() {
        if(!PotionIdentityRuntime.enabled()) return;
        var manager=(RecipeManager)(Object)this;
        try {
            var rules=PotionIdentityRuntime.rules();
            var result=PotionRecipeNormalizer.normalize(byName,registries,rules);
            if(result.held()) return;
            if(result.changed()>0) {
                var types=ImmutableMultimap.<RecipeType<?>,RecipeHolder<?>>builder();
                result.recipes().values().forEach(h->types.put(h.value().getType(),h));
                byName=result.recipes();byType=types.build();
            }
            PotionIdentityRuntime.admit(manager,byName,rules);
        } catch(RuntimeException e) {
            PotionIdentityRuntime.invalidate(manager);
            org.slf4j.LoggerFactory.getLogger(PotionRecipeManagerMixin.class).warn("Potion identity conversion held",e);
        }
    }
}
