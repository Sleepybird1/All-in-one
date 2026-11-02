package dev.godpc.industrialcolonies.mixin;

import com.zizazr.kjsgen.core.SlotDefinition;
import com.zizazr.kjsgen.core.ContentKind;
import com.zizazr.kjsgen.ui.vanilla.VanillaSlotEditScreen;
import dev.godpc.industrialcolonies.MachineRecipeRouting;
import dev.godpc.industrialcolonies.SheetCanonicalization;
import dev.godpc.industrialcolonies.KjsGenItemReference;
import dev.godpc.industrialcolonies.KjsGenJeiItemCatalog;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.List;
import java.util.Set;

/** Turns the normal item search dialog into a compatible-machine picker for routing slots. */
@Mixin(value = VanillaSlotEditScreen.class, remap = false)
public abstract class KjsGenMachineSearchMixin {
    @Shadow
    @Final
    private SlotDefinition slotDef;
    @Shadow private ContentKind kind;

    @Shadow
    @Final
    private List<String> matchedIds;

    @Inject(
            method = "runSearch",
            at = @At(value = "INVOKE", target = "Lcom/zizazr/kjsgen/ui/vanilla/VanillaSlotEditScreen;loadWindow(I)V")
    )
    private void industrialColonies$onlyCompatibleMachines(String query, CallbackInfo ci) {
        matchedIds.removeIf(id -> SheetCanonicalization.isDeprecated(KjsGenItemReference.baseId(id)));
        Set<String> allowed = MachineRecipeRouting.allowedMachineItems(slotDef);
        if (!allowed.isEmpty()) {
            matchedIds.removeIf(id -> !allowed.contains(KjsGenItemReference.baseId(id)));
        }
    }

    /** Recent and favorite picks share a global item history; hide non-machines here too. */
    @ModifyVariable(method = "entriesFor", at = @At("HEAD"), argsOnly = true)
    private List<String> industrialColonies$onlyCompatibleQuickPicks(List<String> ids) {
        Set<String> allowed = MachineRecipeRouting.allowedMachineItems(slotDef);
        return ids.stream().filter(id -> !SheetCanonicalization.isDeprecated(KjsGenItemReference.baseId(id)))
                .filter(id -> allowed.isEmpty() || allowed.contains(KjsGenItemReference.baseId(id)))
                .filter(id -> kind!=ContentKind.ITEM||KjsGenJeiItemCatalog.visibleQuickPick(id)).toList();
    }
}
