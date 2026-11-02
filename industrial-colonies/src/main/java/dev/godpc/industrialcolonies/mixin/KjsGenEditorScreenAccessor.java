package dev.godpc.industrialcolonies.mixin;

import com.zizazr.kjsgen.core.SlotContent;
import com.zizazr.kjsgen.ui.vanilla.VanillaEditorScreen;
import net.minecraft.client.gui.GuiGraphics;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/** Package-bound editor drawing and dirty-state calls used by the sequence panel mixin. */
@Mixin(value = VanillaEditorScreen.class, remap = false)
public interface KjsGenEditorScreenAccessor {
    @Invoker("setProject")
    void industrialColonies$setProject(com.zizazr.kjsgen.core.RecipeProject project);
    @Invoker("drawSlotContent")
    void industrialColonies$drawSlotContent(
            GuiGraphics graphics,
            int x,
            int y,
            SlotContent content
    );

    @Invoker("markDirty")
    void industrialColonies$markDirty();
}
