package dev.godpc.industrialcolonies.mixin;
import com.zizazr.kjsgen.core.*;
import dev.godpc.industrialcolonies.KjsGenVatCompatibility;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.*;
import java.util.Map;
@Mixin(value=RecipeInstance.class,remap=false)
public abstract class KjsGenVatCompatibilityMixin {
 @Shadow private String typeId;
 @Shadow @Final private Map<String,SlotContent> slots;
 @Inject(method="slot",at=@At("HEAD"),cancellable=true)
 private void industrialColonies$read(String key,CallbackInfoReturnable<SlotContent> ci){
  String alias=KjsGenVatCompatibility.alias(typeId,slots,key);
  if(alias!=null)ci.setReturnValue(slots.getOrDefault(alias,SlotContent.EMPTY));
 }
 @Inject(method="setSlot",at=@At("HEAD"),cancellable=true)
 private void industrialColonies$write(String key,SlotContent content,CallbackInfo ci){
  String alias=KjsGenVatCompatibility.alias(typeId,slots,key);
  if(alias!=null){((RecipeInstance)(Object)this).setSlot(alias,content);ci.cancel();}
 }
 @Inject(method="param",at=@At("HEAD"),cancellable=true)
 private void industrialColonies$parameter(RecipeTypeDefinition type,String key,CallbackInfoReturnable<String> ci){
  String legacy=KjsGenVatCompatibility.legacyParameter((RecipeInstance)(Object)this,key);
  if(legacy!=null)ci.setReturnValue(legacy);
 }
}
