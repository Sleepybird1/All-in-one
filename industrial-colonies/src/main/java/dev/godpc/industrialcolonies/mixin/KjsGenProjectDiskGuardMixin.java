package dev.godpc.industrialcolonies.mixin;
import com.zizazr.kjsgen.core.*;
import dev.godpc.industrialcolonies.KjsGenProjectRefresh;
import java.io.IOException;
import java.util.Optional;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;

@Mixin(value=ProjectManager.class,remap=false)
public abstract class KjsGenProjectDiskGuardMixin {
    @Inject(method="load",at=@At("RETURN"))
    private static void industrialColonies$baseline(String name,CallbackInfoReturnable<Optional<RecipeProject>> cir) throws IOException {
        if(!dev.godpc.industrialcolonies.KjsGenProjectMove.archive(name) && cir.getReturnValue().isPresent()) KjsGenProjectRefresh.loaded(ProjectManager.fileFor(name),cir.getReturnValue().get());
    }
    @Inject(method="save",at=@At("HEAD"),cancellable=true)
    private static void industrialColonies$guard(RecipeProject project,CallbackInfo ci) throws IOException {
        if(!dev.godpc.industrialcolonies.KjsGenProjectMove.archive(project.name())) {
            KjsGenProjectRefresh.save(ProjectManager.fileFor(project.name()),project); ci.cancel();
        }
    }
}
