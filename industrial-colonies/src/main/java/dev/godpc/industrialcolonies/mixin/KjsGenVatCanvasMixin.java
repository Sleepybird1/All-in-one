package dev.godpc.industrialcolonies.mixin;
import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeRegistry;
import com.zizazr.kjsgen.core.SlotDefinition;
import com.zizazr.kjsgen.core.SlotContent;
import com.zizazr.kjsgen.ui.vanilla.VanillaEditorScreen;
import com.drmangotea.tfmg.registry.TFMGGuiTextures;
import dev.godpc.industrialcolonies.KjsGenVatCanvasModel;
import dev.godpc.industrialcolonies.KjsGenVatCompatibility;
import com.drmangotea.tfmg.recipes.jei.machines.BlastFurnace;
import com.simibubi.create.foundation.gui.AllGuiTextures;
import net.minecraft.world.item.ItemStack;
import com.drmangotea.tfmg.registry.TFMGItems;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import java.util.*;

/** Draw behind native editable slots so item/fluid/count/chance editing keeps its real hitboxes. */
@Mixin(value=VanillaEditorScreen.class,remap=false)
public abstract class KjsGenVatCanvasMixin {
 @Shadow private int canvasOriginX,canvasOriginY;
 @Shadow private List<Component> hoverTooltip;
 @Shadow abstract Optional<RecipeInstance> selectedRecipe();
 @Inject(method="listEntryX",at=@At("HEAD"),cancellable=true)
 private void industrialColonies$feedX(SlotDefinition slot,int index,CallbackInfoReturnable<Integer> callback){
  if(industrialColonies$extraFeed(slot))callback.setReturnValue(industrialColonies$feedSlotX(slot,index));
 }
 @Inject(method="listEntryY",at=@At("HEAD"),cancellable=true)
 private void industrialColonies$feedY(SlotDefinition slot,int index,CallbackInfoReturnable<Integer> callback){
  if(industrialColonies$extraFeed(slot))callback.setReturnValue(industrialColonies$feedSlotY(slot,index));
 }
 private boolean industrialColonies$enlargedBowl(){
  return selectedRecipe().flatMap(recipe->RecipeTypeRegistry.get(recipe.typeId()))
   .filter(type->type.canvasHeight()>=KjsGenVatCanvasModel.BOWL_CANVAS_HEIGHT)
   .flatMap(type->type.slot("additionalIngredients"))
   .filter(slot->slot.x()==KjsGenVatCanvasModel.BOWL_INPUT_X&&slot.y()==KjsGenVatCanvasModel.BOWL_INPUT_Y).isPresent();
 }
 private int industrialColonies$feedSlotX(SlotDefinition slot,int index){
  return KjsGenVatCanvasModel.extraInputX(canvasOriginX+slot.x(),index+(industrialColonies$enlargedBowl()?4:0));
 }
 private int industrialColonies$feedSlotY(SlotDefinition slot,int index){
  return KjsGenVatCanvasModel.extraInputY(canvasOriginY+slot.y(),index+(industrialColonies$enlargedBowl()?4:0));
 }
 private boolean industrialColonies$extraFeed(SlotDefinition slot){
  return slot.list()&&slot.key().equals("additionalIngredients")
   &&selectedRecipe().map(r->KjsGenVatCompatibility.vat(r.typeId())).orElse(false);
 }
 @Inject(method="clickListSlot",at=@At("HEAD"),cancellable=true)
 private void industrialColonies$boundedFeed(double mouseX,double mouseY,int button,RecipeInstance recipe,SlotDefinition slot,CallbackInfoReturnable<Boolean> callback){
  if(!industrialColonies$extraFeed(slot))return;
  int count=Math.max(1,recipe.listSlots(slot.key()).size());
  if(KjsGenVatCanvasModel.mayAppendExtraInput(count))return;
  int x=industrialColonies$feedSlotX(slot,count);
  int y=industrialColonies$feedSlotY(slot,count);
  if(mouseX>=x&&mouseX<x+18&&mouseY>=y&&mouseY<y+18)callback.setReturnValue(true);
 }
 @Inject(method="drawPlusButton",at=@At("HEAD"),cancellable=true)
 private void industrialColonies$feedLimit(GuiGraphics graphics,int x,int y,boolean hovered,CallbackInfo callback){
  var selected=selectedRecipe();if(selected.isEmpty()||!KjsGenVatCompatibility.vat(selected.get().typeId()))return;
  var type=RecipeTypeRegistry.get(selected.get().typeId()).orElse(null);if(type==null)return;
  var slot=type.slot("additionalIngredients").orElse(null);if(slot==null)return;
  int count=Math.max(1,selected.get().listSlots(slot.key()).size());
  if(KjsGenVatCanvasModel.mayAppendExtraInput(count)
   ||x!=industrialColonies$feedSlotX(slot,count)
   ||y!=industrialColonies$feedSlotY(slot,count))return;
  if(!industrialColonies$enlargedBowl())graphics.fill(x+1,y+1,x+17,y+17,0xFF303030);
  if(hovered)hoverTooltip=List.of(Component.literal("Maximum 24 direct feed rows (4 base + 20 additional)"));
  callback.cancel();
 }
 @Inject(method="drawListSlot",at=@At("TAIL"))
 private void industrialColonies$feedLimitTooltip(GuiGraphics graphics,SlotDefinition slot,RecipeInstance recipe,int mouseX,int mouseY,CallbackInfo callback){
  if(!industrialColonies$extraFeed(slot))return;
  int count=Math.max(1,recipe.listSlots(slot.key()).size());
  if(KjsGenVatCanvasModel.mayAppendExtraInput(count))return;
  int x=industrialColonies$feedSlotX(slot,count);
  int y=industrialColonies$feedSlotY(slot,count);
  // Native drawListSlot writes its generic 'Add' tooltip after drawPlusButton.
  if(mouseX>=x&&mouseX<x+18&&mouseY>=y&&mouseY<y+18)
   hoverTooltip=List.of(Component.literal("Maximum 24 direct feed rows (4 base + 20 additional)"));
 }
 @Inject(method="drawCanvas",at=@At(value="INVOKE",target="Lcom/zizazr/kjsgen/core/RecipeTypeDefinition;decorations()Ljava/util/List;",shift=At.Shift.BEFORE))
 private void industrialColonies$vat(GuiGraphics graphics,int mouseX,int mouseY,CallbackInfo ci){
  var selected=selectedRecipe();if(selected.isEmpty())return;var recipe=selected.get();
  String id=recipe.typeId().toString();
  if(id.equals("industrial_colonies:tfmg_industrial_blasting")){
   var type=RecipeTypeRegistry.get(recipe.typeId()).orElseThrow();
   if(type.canvasHeight()<170)return; // Preserve old short layouts until matching assets are loaded.
   int x=canvasOriginX,y=canvasOriginY;
   new BlastFurnace().draw(graphics,x+50,y+135);
   AllGuiTextures.JEI_ARROW.render(graphics,x+96,y+121);
   AllGuiTextures.JEI_DOWN_ARROW.render(graphics,x+45,y+15);
   AllGuiTextures.JEI_SLOT.render(graphics,x+69,y+12);
   graphics.renderItem(new ItemStack(TFMGItems.COAL_COKE_DUST.get()),x+70,y+13);
   if(mouseX>=x+69&&mouseX<x+87&&mouseY>=y+12&&mouseY<y+30)
    hoverTooltip=List.of(Component.literal("Coal coke dust: furnace fuel"),Component.literal("Shown as in JEI; not an extra recipe ingredient"));
   return;
  }
  if(!KjsGenVatCompatibility.vat(id))return;
  var type=RecipeTypeRegistry.get(recipe.typeId()).orElseThrow();
  // Only the matching layout revision has slots inside this chamber.
  if(type.parameter("allowedVatTypes").isEmpty())return;
  int x=canvasOriginX,y=canvasOriginY;
  boolean enlarged=industrialColonies$enlargedBowl();
  String named=KjsGenVatCanvasModel.namedVat(id);
  String legacyAllowed=KjsGenVatCompatibility.legacyParameter(recipe,"allowedVatTypes");
  String allowed=named!=null?named:legacyAllowed!=null?legacyAllowed:recipe.param(type,"allowedVatTypes");
  // Scale only the vessel artwork. Native 18px slots and their click regions stay unscaled.
  graphics.pose().pushPose();
  try{
   graphics.pose().translate(x,y+24,0);
   if(enlarged)graphics.pose().scale(2,1.5f,1);
   TFMGGuiTextures.VAT.render(graphics,0,0);
   switch(KjsGenVatCanvasModel.lining(allowed)){
    case "tfmg:firebrick_lined_vat" -> TFMGGuiTextures.FIREPROOF_BRICK_OVERLAY.render(graphics,7,8);
    case "tfmg:cast_iron_vat" -> TFMGGuiTextures.CAST_IRON_VAT_OVERLAY.render(graphics,0,0);
   }
  }finally{graphics.pose().popPose();}
  if(mouseX>=x&&mouseX<x+(enlarged?220:110)&&mouseY>=y+24&&mouseY<y+(enlarged?150:109))
   hoverTooltip=List.of(Component.literal("Allowed vats: "+String.join(", ",KjsGenVatCanvasModel.values(allowed))));
  String setup=type.parameter("machineSetup").isPresent()?recipe.param(type,"machineSetup"):"";
  String legacySetup=KjsGenVatCompatibility.legacyParameter(recipe,"machineSetup");
  if(legacySetup!=null)setup=legacySetup;
  if(type.parameter("attachmentDrive").isPresent()){
   try{setup=KjsGenVatCanvasModel.selectedMachines(recipe.param(type,"attachmentDrive"),recipe.param(type,"electrodeType"),recipe.paramInt(type,"electrodeCount",0));}
   catch(IllegalArgumentException invalid){
    graphics.drawString(net.minecraft.client.Minecraft.getInstance().font,"Invalid attachment combination",x,y+(enlarged?4:120),0xFF6666,false);
    setup="none";
   }
  }
  for(var attachment:KjsGenVatCanvasModel.attachments(setup)){
   int ax=x+(enlarged?KjsGenVatCanvasModel.bowlAttachmentX(attachment.x()):attachment.x());TFMGGuiTextures.VAT_MACHINE.render(graphics,ax,y);
   switch(attachment.id()){
    case "tfmg:mixing" -> TFMGGuiTextures.MIXER.render(graphics,ax-7,y+32);
    case "tfmg:centrifuge" -> TFMGGuiTextures.CENTRIFUGE.render(graphics,ax,y+32);
    case "tfmg:electrode" -> TFMGGuiTextures.ELECTRODE.render(graphics,ax+9,y+32);
    case "tfmg:graphite_electrode" -> TFMGGuiTextures.GRAPHITE_ELECTRODE.render(graphics,ax+8,y+32);
   }
   if(mouseX>=ax&&mouseX<ax+24&&mouseY>=y&&mouseY<y+62)
    hoverTooltip=List.of(Component.literal("Required attachment: "+attachment.label()),Component.literal("Choose attachments in Parameters"));
  }
  switch(recipe.param(type,"heat")){
   case "heated" -> TFMGGuiTextures.VAT_HEATER.render(graphics,x+(enlarged?100:45),y+(enlarged?151:109));
   case "superheated" -> TFMGGuiTextures.VAT_SUPERHEATER.render(graphics,x+(enlarged?100:45),y+(enlarged?151:109));
  }
 }
}
