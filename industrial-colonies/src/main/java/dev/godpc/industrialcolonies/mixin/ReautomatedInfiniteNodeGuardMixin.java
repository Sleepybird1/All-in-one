package dev.godpc.industrialcolonies.mixin;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Retain saved blocks, but disable extraction from the six retired infinite nodes. */
@Pseudo
@Mixin(targets = "com.github.zgraund.createreautomated.block.extractor.ExtractorBlockEntity", remap = false)
public abstract class ReautomatedInfiniteNodeGuardMixin {
    @Shadow public abstract BlockState getNode();

    @Inject(method = "failPreConditions", at = @At("HEAD"), cancellable = true, require = 1)
    private void industrialColonies$rejectInfiniteNodes(CallbackInfoReturnable<Boolean> callback) {
        var id = BuiltInRegistries.BLOCK.getKey(getNode().getBlock());
        if (!id.getNamespace().equals("createreautomated")) return;
        switch (id.getPath()) {
            case "infinite_copper_node", "infinite_iron_node", "infinite_gold_node",
                 "infinite_zinc_node", "infinite_diamond_node", "infinite_quartz_node" -> callback.setReturnValue(true);
            default -> { }
        }
    }
}
