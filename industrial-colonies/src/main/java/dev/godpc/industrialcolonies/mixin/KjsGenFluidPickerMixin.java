package dev.godpc.industrialcolonies.mixin;
import com.zizazr.kjsgen.core.*;
import com.zizazr.kjsgen.ui.vanilla.VanillaSlotEditScreen;
import dev.godpc.industrialcolonies.KjsGenFluidChoice;
import dev.godpc.industrialcolonies.KjsGenJeiFluidCatalog;
import dev.godpc.industrialcolonies.MachineRecipeRouting;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.*;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;

/** Keeps the native amount editor, validation and save path; makes fluid mode a direct action. */
@Mixin(value=VanillaSlotEditScreen.class,remap=false)
public abstract class KjsGenFluidPickerMixin extends Screen {
 @Shadow @Final private SlotDefinition slotDef;
 @Shadow private ContentKind kind;
 @Shadow private String id;
 @Shadow private int amount;
 @Shadow private int resultScroll;
 @Shadow private int favScroll;
 @Shadow @Final private java.util.List<String> matchedIds;
 @Shadow private String searchQuery;
 @Shadow private void loadWindow(int first){throw new AssertionError();}
 @Shadow private void runSearch(String query){throw new AssertionError();}
 @Unique private long industrialColonies$fluidCatalogGeneration=-1;
 protected KjsGenFluidPickerMixin(Component title){super(title);}

 @Inject(method="runSearch",at=@At("HEAD"),cancellable=true)
 private void industrialColonies$jeiFluidSearch(String query,CallbackInfo ci) {
  if(kind!=ContentKind.FLUID)return;
  if(!MachineRecipeRouting.allowedMachineItems(slotDef).isEmpty())return;
  var snapshot=KjsGenJeiFluidCatalog.snapshot();if(snapshot.isEmpty())return;
  searchQuery=query;resultScroll=0;matchedIds.clear();matchedIds.addAll(snapshot.get().search(query));
  industrialColonies$fluidCatalogGeneration=snapshot.get().generation();loadWindow(0);ci.cancel();
 }
 @Inject(method="renderContent",at=@At("HEAD"))
 private void industrialColonies$refreshFluidCatalog(GuiGraphics graphics,int mouseX,int mouseY,float partial,CallbackInfo ci) {
  if(kind!=ContentKind.FLUID)return;
  long generation=KjsGenJeiFluidCatalog.snapshot().map(KjsGenJeiFluidCatalog.Snapshot::generation).orElse(-1L);
  if(generation!=industrialColonies$fluidCatalogGeneration) {
   industrialColonies$fluidCatalogGeneration=generation;runSearch(searchQuery);
  }
 }
 @WrapOperation(method="makeEntry",at=@At(value="INVOKE",target="Lcom/zizazr/kjsgen/ui/vanilla/VanillaSlotEditScreen;fluidName(Ljava/lang/String;)Ljava/lang/String;"))
 private String industrialColonies$jeiFluidName(String actualId,Operation<String> original) {
  return KjsGenJeiFluidCatalog.label(actualId).orElseGet(() -> original.call(actualId));
 }

 @Inject(method="buildLeftColumn",at=@At("TAIL"))
 private void industrialColonies$fluidShortcut(CallbackInfo ci) {
  if(!slotDef.allowsFluid())return;
  for(var child:java.util.List.copyOf(children())) {
   if(!(child instanceof CycleButton<?> selector) || !(selector.getValue() instanceof ContentKind))continue;
   int width=selector.getWidth();int actionWidth=Math.min(66,width/2);
   selector.setWidth(width-actionWidth-2);
   var action=Button.builder(Component.literal("Fluid mB"),button->{
    var selected=KjsGenFluidChoice.chooseFluid(slotDef,kind,id,amount);
    kind=ContentKind.FLUID;id=selected.id();amount=selected.amount();resultScroll=0;favScroll=0;
    rebuildWidgets();
   }).bounds(selector.getX()+width-actionWidth,selector.getY(),actionWidth,selector.getHeight()).build();
   action.setTooltip(Tooltip.create(Component.literal("Choose actual fluid and edit its mB amount. A bucket item is a separate ingredient.")));
   action.active=kind!=ContentKind.FLUID;
   addRenderableWidget(action);break;
  }
 }
 @Inject(method="kindLabel",at=@At("HEAD"),cancellable=true)
 private static void industrialColonies$clearKind(ContentKind kind,CallbackInfoReturnable<String> cir) {
  if(kind==ContentKind.ITEM)cir.setReturnValue("Item / bucket");
  else if(kind==ContentKind.FLUID)cir.setReturnValue("Fluid (mB)");
  else if(kind==ContentKind.FLUID_TAG)cir.setReturnValue("Fluid tag (mB)");
 }
}
