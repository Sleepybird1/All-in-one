package dev.godpc.industrialcolonies.mixin;

import com.zizazr.kjsgen.core.ContentKind;
import com.zizazr.kjsgen.ui.vanilla.VanillaSlotEditScreen;
import dev.godpc.industrialcolonies.KjsGenFluidRendering;
import net.minecraft.client.gui.GuiGraphics;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.gen.Accessor;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Coerce;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Fluid rows, quick picks and selected previews use actual fluid sprites, never a substitute bucket. */
@Mixin(value=VanillaSlotEditScreen.class,remap=false)
public abstract class KjsGenFluidIconMixin {
    @Shadow private ContentKind kind;

    @Inject(method="drawEntryIcon",at=@At("HEAD"),cancellable=true)
    private void industrialColonies$fluidSprite(GuiGraphics graphics,@Coerce Object entry,
                                               int x,int y,long cycle,CallbackInfo ci) {
        if(!KjsGenFluidRendering.isFluid(kind))return;
        KjsGenFluidRendering.drawPicker(graphics,x,y,kind,((EntryAccess)entry).industrialColonies$fluidId(),cycle);
        ci.cancel();
    }

    /** The native record is package-private; its exact field is accessed without reflection. */
    @Mixin(targets="com.zizazr.kjsgen.ui.vanilla.VanillaSlotEditScreen$Entry",remap=false)
    public interface EntryAccess {
        @Accessor("id") String industrialColonies$fluidId();
    }
}
