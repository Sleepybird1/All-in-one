package dev.godpc.industrialcolonies.mixin;

import com.zizazr.kjsgen.core.RecipeProject;
import com.zizazr.kjsgen.integration.net.ServerProjectStore;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

import java.util.Map;

/** Integrated-server cache bridge for the local approved-recipe archive. */
@Mixin(value = ServerProjectStore.class, remap = false)
public interface KjsGenServerProjectStoreAccessor {
    @Accessor("loaded")
    static Map<String, RecipeProject> industrialColonies$loadedProjects() {
        throw new AssertionError("mixin accessor");
    }
}
