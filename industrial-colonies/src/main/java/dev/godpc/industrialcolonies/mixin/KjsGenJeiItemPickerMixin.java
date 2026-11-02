package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.zizazr.kjsgen.core.*;
import com.zizazr.kjsgen.ui.vanilla.VanillaSlotEditScreen;
import dev.godpc.industrialcolonies.*;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.CycleButton;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
import java.util.*;

/** ITEM mode only: native entry/window/render/history remains, with reversible JEI stack identities. */
@Mixin(value=VanillaSlotEditScreen.class,remap=false)
public abstract class KjsGenJeiItemPickerMixin {
    @Shadow @Final private SlotDefinition slotDef;
    @Shadow @Final private List<String> matchedIds;
    @Shadow private ContentKind kind;
    @Shadow private String id;
    @Shadow private String components;
    @Shadow private String searchQuery;
    @Shadow private int resultScroll;
    @Shadow private EditBox idField;
    @Shadow private void loadWindow(int first){throw new AssertionError();}
    @Shadow private void runSearch(String query){throw new AssertionError();}
    @Unique private long industrialColonies$catalogGeneration=-1;
    @Unique private String industrialColonies$beforeId="",industrialColonies$beforeComponents="";
    @Unique private String industrialColonies$selectedKey="";
    @Unique private String industrialColonies$previewId="",industrialColonies$previewComponents="",industrialColonies$previewKey="";
    @Unique private EditBox industrialColonies$componentField;

    @Inject(method="buildLeftColumn",at=@At("HEAD"))
    private void industrialColonies$resetComponentBox(CallbackInfo ci){industrialColonies$componentField=null;}
    @WrapOperation(method="buildLeftColumn",at=@At(value="INVOKE",target="Lnet/minecraft/client/gui/components/EditBox;setMaxLength(I)V",ordinal=1))
    private void industrialColonies$componentBox(EditBox box,int maximum,Operation<Void> original) {
        industrialColonies$componentField=box;original.call(box,Math.max(maximum,KjsGenItemReference.MAX_REFERENCE_LENGTH));
    }

    @Inject(method="runSearch",at=@At("HEAD"),cancellable=true)
    private void industrialColonies$jeiSearch(String query,CallbackInfo ci) {
        if(kind!=ContentKind.ITEM)return;
        var snapshot=KjsGenJeiItemCatalog.snapshot(); if(snapshot.isEmpty())return;
        searchQuery=query; resultScroll=0; matchedIds.clear();
        Set<String> allowed=MachineRecipeRouting.allowedMachineItems(slotDef);
        snapshot.get().search(query).stream()
            .filter(key -> !SheetCanonicalization.isDeprecated(KjsGenItemReference.baseId(key)))
            .filter(key -> allowed.isEmpty()||allowed.contains(KjsGenItemReference.baseId(key)))
            .forEach(matchedIds::add);
        industrialColonies$catalogGeneration=snapshot.get().generation(); loadWindow(0); ci.cancel();
    }
    @Inject(method="renderContent",at=@At("HEAD"))
    private void industrialColonies$refreshCatalog(GuiGraphics graphics,int mouseX,int mouseY,float partial,CallbackInfo ci) {
        if(kind!=ContentKind.ITEM)return;
        long generation=KjsGenJeiItemCatalog.snapshot().map(KjsGenJeiItemCatalog.Snapshot::generation).orElse(-1L);
        if(generation!=industrialColonies$catalogGeneration) {
            industrialColonies$catalogGeneration=generation;runSearch(searchQuery);
        }
    }
    @WrapOperation(method="makeEntry",at=@At(value="INVOKE",target="Lcom/zizazr/kjsgen/ui/vanilla/VanillaSlotEditScreen;itemName(Ljava/lang/String;)Ljava/lang/String;"))
    private String industrialColonies$variantName(String key,Operation<String> original) {
        if(!KjsGenItemReference.isReference(key))return original.call(key);
        return KjsGenJeiItemCatalog.resolve(key).map(KjsGenJeiItemCatalog.Choice::label).orElse("Unavailable item variant");
    }
    @WrapOperation(method="makeEntry",at=@At(value="INVOKE",target="Lcom/zizazr/kjsgen/ui/vanilla/VanillaTheme;itemStack(Ljava/lang/String;)Lnet/minecraft/world/item/ItemStack;"))
    private ItemStack industrialColonies$variantIcon(String key,Operation<ItemStack> original) {
        if(!KjsGenItemReference.isReference(key))return original.call(key);
        return KjsGenJeiItemCatalog.resolve(key).map(KjsGenJeiItemCatalog.Choice::stack).orElse(ItemStack.EMPTY);
    }
    @Inject(method="select",at=@At("HEAD"))
    private void industrialColonies$rememberSelection(CallbackInfo ci) {
        industrialColonies$beforeId=id;industrialColonies$beforeComponents=components;
    }
    @WrapOperation(method="select",at=@At(value="INVOKE",target="Lcom/zizazr/kjsgen/ui/vanilla/VanillaSlotEditScreen$Entry;id()Ljava/lang/String;"))
    private String industrialColonies$captureFullReference(@Coerce Object entry,Operation<String> original) {
        industrialColonies$selectedKey=original.call(entry);
        // The ID EditBox is length-limited: never send the component/history token through it.
        return kind==ContentKind.ITEM?KjsGenItemReference.baseId(industrialColonies$selectedKey):industrialColonies$selectedKey;
    }
    @Inject(method="select",at=@At("TAIL"))
    private void industrialColonies$selectFullStack(CallbackInfo ci) {
        if(kind!=ContentKind.ITEM)return;
        String patch="";
        if(KjsGenItemReference.isReference(industrialColonies$selectedKey)) {
            var selected=KjsGenJeiItemCatalog.resolve(industrialColonies$selectedKey);
            if(selected.isPresent()) {id=selected.get().id();patch=selected.get().components();}
            else {id=industrialColonies$beforeId;patch=industrialColonies$beforeComponents;}
        }
        if(idField!=null)idField.setValue(id);
        if(industrialColonies$componentField!=null)industrialColonies$componentField.setValue(patch);
        components=patch;
    }
    @Inject(method="lambda$buildLeftColumn$3",at=@At("HEAD"))
    private void industrialColonies$clearOldComponents(String edited,CallbackInfo ci) {
        if(kind==ContentKind.ITEM&&!edited.trim().equals(id)) {
            if(industrialColonies$componentField!=null)industrialColonies$componentField.setValue("");
            components="";
        }
    }
    @Inject(method="lambda$buildLeftColumn$2",at=@At("HEAD"))
    private void industrialColonies$clearChangedKind(CycleButton<?> selector,ContentKind selected,CallbackInfo ci) {
        if(selected!=kind)components="";
    }
    @ModifyArg(method="drawSelectedPreview",at=@At(value="INVOKE",target="Lcom/zizazr/kjsgen/ui/vanilla/VanillaSlotEditScreen;makeEntry(Ljava/lang/String;)Lcom/zizazr/kjsgen/ui/vanilla/VanillaSlotEditScreen$Entry;"),index=0)
    private String industrialColonies$selectedVariantPreview(String selected) {return industrialColonies$historyKey(selected);}
    @ModifyArg(method="commit",at=@At(value="INVOKE",target="Lcom/zizazr/kjsgen/ui/vanilla/SlotPicks;addRecent(Lcom/zizazr/kjsgen/core/ContentKind;Ljava/lang/String;)V"),index=1)
    private String industrialColonies$recentVariant(String selected) {return industrialColonies$historyKey(selected);}
    @Unique private String industrialColonies$historyKey(String selected) {
        if(kind!=ContentKind.ITEM||components==null||components.isBlank()||!selected.equals(id))return selected;
        if(selected.equals(industrialColonies$previewId)&&components.equals(industrialColonies$previewComponents))return industrialColonies$previewKey;
        try {
            String key=KjsGenItemReference.key(selected,components);
            industrialColonies$previewId=selected;industrialColonies$previewComponents=components;industrialColonies$previewKey=key;
            return key;
        }catch(RuntimeException invalid){return "@kjsgen-item:unavailable";}
    }
    @Inject(method="commit",at=@At("HEAD"),cancellable=true)
    private void industrialColonies$neverAuthorReference(CallbackInfo ci) {
        if(KjsGenItemReference.isReference(id))ci.cancel();
    }
}
