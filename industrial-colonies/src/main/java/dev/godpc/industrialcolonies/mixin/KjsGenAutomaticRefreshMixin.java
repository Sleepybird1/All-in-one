package dev.godpc.industrialcolonies.mixin;
import com.zizazr.kjsgen.core.*;
import com.zizazr.kjsgen.ui.vanilla.VanillaEditorScreen;
import com.zizazr.kjsgen.integration.net.ClientEditSession;
import dev.godpc.industrialcolonies.*;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(value=VanillaEditorScreen.class,remap=false)
public abstract class KjsGenAutomaticRefreshMixin extends Screen implements KjsGenAutomaticRefresh.View {
 protected KjsGenAutomaticRefreshMixin(Component title){super(title);}
 @Shadow private RecipeProject project;
 @Shadow private String selectedUid,recipePushUid;
 @Shadow private int listScroll,paramScroll,previewScroll;
 @Shadow private boolean metaPushDue,menuOpen;
 @Shadow @Final private UndoStack undoStack;
 @Shadow @Final private java.util.List<net.minecraft.client.gui.components.AbstractWidget> paramWidgets;
 @Shadow @Final private java.util.List<Component> paramLabels;
 @Shadow private SlotContent heldItem;
 @Unique private long industrialColonies$editedAt,industrialColonies$revision;
 @Inject(method={"markDirty","scheduleMetaPush"},at=@At("HEAD"))
 private void industrialColonies$edit(CallbackInfo ci){industrialColonies$editedAt=System.nanoTime();industrialColonies$revision++;}
 @Inject(method="tick",at=@At("TAIL"))
 private void industrialColonies$automatic(CallbackInfo ci){
   boolean safe=recipePushUid==null&&!metaPushDue&&!menuOpen&&!isDragging()&&heldItem.isEmpty()
      &&(!(getFocused() instanceof EditBox)||KjsGenDesktopBridge.editorUnfocused())&&System.nanoTime()-industrialColonies$editedAt>=750_000_000L;
   KjsGenAutomaticRefresh.tick(this,project,safe,industrialColonies$revision);
 }
 @Override public void industrialColonies$applyAutomatic(RecipeProject updated){
   int focused=paramWidgets.indexOf(getFocused());
   String label=focused>=0&&focused<paramLabels.size()?paramLabels.get(focused).getString():null;
   int cursor=getFocused() instanceof EditBox box?box.getCursorPosition():0;
   project=updated;ClientEditSession.setLocalProject(updated);undoStack.clear();
   if(selectedUid!=null&&updated.recipeByUid(selectedUid).isEmpty())selectedUid=updated.recipes().isEmpty()?null:updated.recipes().getFirst().uid();
   // Keep scroll coordinates and rebuild once, only after actual data changed.
   rebuildWidgets();
   if(label!=null&&focused<paramWidgets.size()&&focused<paramLabels.size()&&label.equals(paramLabels.get(focused).getString())){
     var widget=paramWidgets.get(focused);setFocused(widget);
     if(widget instanceof EditBox box)box.setCursorPosition(Math.min(cursor,box.getValue().length()));
   }
 }
}
