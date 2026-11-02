package dev.godpc.industrialcolonies.mixin;

import com.zizazr.kjsgen.core.CreateSpecialModel;
import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeDefinition;
import com.zizazr.kjsgen.core.SlotContent;
import com.zizazr.kjsgen.core.SlotDefinition;
import com.zizazr.kjsgen.ui.vanilla.VanillaEditorScreen;
import com.zizazr.kjsgen.ui.vanilla.VanillaSlotEditScreen;
import dev.godpc.industrialcolonies.MachineRecipeRouting;
import dev.godpc.industrialcolonies.TieredRecipeCatalog;
import dev.godpc.industrialcolonies.SequenceStageOptions;
import dev.godpc.industrialcolonies.SequenceStageScreen;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyArg;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Exposes the exact Press, Deployer, Saw, or Spout beside each corresponding
 * operation in KJSGen's Sequenced Assembly panel. Machine metadata follows a
 * row when it is moved and is cleared when that row changes operation type.
 */
@Mixin(targets = "com.zizazr.kjsgen.ui.vanilla.VanillaSequencePanel", remap = false)
public abstract class KjsGenSequencePanelMixin {
    private static final int MACHINE_SLOT_SIZE = 18;
    private static final int MACHINE_SLOT_GAP = 2;

    @Shadow
    private int rx;

    @Shadow
    private int rw;

    @Shadow
    private int listTop;

    @Shadow
    private int listBottom;

    @Shadow
    private int scroll;

    @ModifyArg(
            method = "drawRow",
            at = @At(
                    value = "INVOKE",
                    target = "Lnet/minecraft/client/gui/Font;plainSubstrByWidth(Ljava/lang/String;I)Ljava/lang/String;"
            ),
            index = 1
    )
    private int industrialColonies$reserveMachineSlot(int width) {
        return Math.max(0, width - 2 * (MACHINE_SLOT_SIZE + MACHINE_SLOT_GAP));
    }

    @Inject(method = "drawRow", at = @At("TAIL"))
    private void industrialColonies$drawStepMachineSelector(
            GuiGraphics graphics,
            VanillaEditorScreen editor,
            Font font,
            RecipeInstance recipe,
            RecipeTypeDefinition type,
            int index,
            int rowX,
            int rowY,
            int rowWidth,
            int mouseX,
            int mouseY,
            boolean dragging,
            CallbackInfo ci
    ) {
        if (SequenceStageOptions.configurable(CreateSpecialModel.stepTypeId(recipe,type,index))) {
            int settingsX=machineSlotX(rowX,rowWidth)-20;
            drawSlot(graphics,settingsX,rowY+1,false);
            graphics.drawString(font,"...",settingsX+2,rowY+5,0xFFFFFFFF,false);
        }
        TieredRecipeCatalog.RecipeFamily family = selectableStepFamily(recipe, type, index);
        if (family == null) {
            return;
        }

        int machineX = machineSlotX(rowX, rowWidth);
        int machineY = rowY + 1;
        boolean hovered = !dragging
                && industrialColonies$machineSlotHit(mouseX, mouseY, machineX, machineY);
        drawSlot(graphics, machineX, machineY, hovered);

        String key = MachineRecipeRouting.stepSlotKey(index, family);
        SlotContent selected = recipe.slot(key);
        if (selected.isEmpty() && SequenceStageOptions.FANS.contains(CreateSpecialModel.stepTypeId(recipe,type,index))) {
            graphics.drawString(font,"Any",machineX+1,machineY+5,0xFFFFFFFF,false);
            return;
        }
        if (selected.isEmpty()) {
            TieredRecipeCatalog.Machine base = family.baseMachine();
            if (base != null) {
                selected = SlotContent.item(base.item(), 1);
            }
        }
        ((KjsGenEditorScreenAccessor) editor)
                .industrialColonies$drawSlotContent(graphics, machineX, machineY, selected);
    }

    @Inject(method = "mouseClicked", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$editStepMachineSelector(
            VanillaEditorScreen editor,
            RecipeInstance recipe,
            RecipeTypeDefinition type,
            double mouseX,
            double mouseY,
            int button,
            CallbackInfoReturnable<Boolean> cir
    ) {
        if (mouseY < listTop || mouseY > listBottom) {
            return;
        }

        int index = (int) ((mouseY - listTop + scroll) / 20.0D);
        int length = CreateSpecialModel.seqLen(recipe, type);
        if (index < 0 || index >= length) {
            return;
        }

        int settingsX=machineSlotX(rx+4,rw-8)-20;
        int settingsY=listTop+index*20-scroll+1;
        if (SequenceStageOptions.configurable(CreateSpecialModel.stepTypeId(recipe,type,index))
                && industrialColonies$machineSlotHit(mouseX,mouseY,settingsX,settingsY)) {
            Minecraft.getInstance().setScreen(new SequenceStageScreen(editor,recipe,type,index,
                    () -> ((KjsGenEditorScreenAccessor)editor).industrialColonies$markDirty()));
            cir.setReturnValue(true);return;
        }
        TieredRecipeCatalog.RecipeFamily family = selectableStepFamily(recipe, type, index);
        if (family == null) {
            return;
        }

        int rowX = rx + 4;
        int rowY = listTop + index * 20 - scroll;
        int machineX = machineSlotX(rowX, rw - 8);
        int machineY = rowY + 1;
        if (!industrialColonies$machineSlotHit(mouseX, mouseY, machineX, machineY)) {
            return;
        }

        KjsGenEditorScreenAccessor access = (KjsGenEditorScreenAccessor) editor;
        if (button == 1) {
            recipe.setSlot(MachineRecipeRouting.stepSlotKey(index, family), SlotContent.EMPTY);
            access.industrialColonies$markDirty();
        } else {
            openMachineEditor(editor, access, recipe, index, family);
        }
        cir.setReturnValue(true);
    }

    @Inject(method = "cycleStepType", at = @At("HEAD"))
    private void industrialColonies$clearChangedStepMachine(
            RecipeInstance recipe,
            int index,
            CreateSpecialModel.StepType current,
            int button,
            CallbackInfo ci
    ) {
        MachineRecipeRouting.clearSequenceStepMachine(recipe, index);
    }

    /** KJSGen 2.0.5 hardcodes new stages to STEP_TYPES[1] (Pressing). */
    @Redirect(
            method = "mouseClicked",
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/zizazr/kjsgen/core/CreateSpecialModel;addStep(Lcom/zizazr/kjsgen/core/RecipeInstance;Lcom/zizazr/kjsgen/core/RecipeTypeDefinition;Ljava/lang/String;)V"
            )
    )
    private void industrialColonies$addVisibleDeployingStep(
            RecipeInstance recipe,
            RecipeTypeDefinition type,
            String ignoredPressingDefault
    ) {
        CreateSpecialModel.addStep(recipe, type, "deploying");
    }

    @Redirect(
            method = "mouseClicked",
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/zizazr/kjsgen/core/CreateSpecialModel;removeStep(Lcom/zizazr/kjsgen/core/RecipeInstance;Lcom/zizazr/kjsgen/core/RecipeTypeDefinition;I)V"
            )
    )
    private void industrialColonies$removeStepAndMachine(
            RecipeInstance recipe,
            RecipeTypeDefinition type,
            int removedIndex
    ) {
        MachineRecipeRouting.removeSequenceStep(recipe, type, removedIndex);
        CreateSpecialModel.removeStep(recipe, type, removedIndex);
    }

    @Redirect(
            method = "mouseReleased",
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/zizazr/kjsgen/core/CreateSpecialModel;moveStep(Lcom/zizazr/kjsgen/core/RecipeInstance;Lcom/zizazr/kjsgen/core/RecipeTypeDefinition;II)V"
            )
    )
    private void industrialColonies$moveStepAndMachine(
            RecipeInstance recipe,
            RecipeTypeDefinition type,
            int from,
            int to
    ) {
        MachineRecipeRouting.moveSequenceStep(recipe, type, from, to);
        CreateSpecialModel.moveStep(recipe, type, from, to);
    }

    private static TieredRecipeCatalog.RecipeFamily selectableStepFamily(
            RecipeInstance recipe,
            RecipeTypeDefinition type,
            int index
    ) {
        String familyId = CreateSpecialModel.stepTypeId(recipe, type, index);
        if (!"deploying".equals(familyId)
                && !"pressing".equals(familyId)
                && !"cutting".equals(familyId)
                && !"mixing".equals(familyId)
                && !"compacting".equals(familyId)
                && !SequenceStageOptions.FANS.contains(familyId)
                && !"filling".equals(familyId)) {
            return null;
        }
        return MachineRecipeRouting.sequenceFamily(familyId)
                .filter(TieredRecipeCatalog.RecipeFamily::supportsMachineSelection)
                .orElse(null);
    }

    private static void openMachineEditor(
            VanillaEditorScreen editor,
            KjsGenEditorScreenAccessor access,
            RecipeInstance recipe,
            int index,
            TieredRecipeCatalog.RecipeFamily family
    ) {
        SlotDefinition slot = MachineRecipeRouting.stepMachineSlot(index, family);
        SlotContent initial = recipe.slot(slot.key());
        if (initial.isEmpty() && family.baseMachine() != null) {
            initial = SlotContent.item(family.baseMachine().item(), 1);
        }
        Minecraft.getInstance().setScreen(new VanillaSlotEditScreen(
                editor,
                slot,
                family.displayName() + " machine #" + (index + 1),
                initial,
                content -> {
                    recipe.setSlot(slot.key(), content);
                    access.industrialColonies$markDirty();
                }));
    }

    private static int machineSlotX(int rowX, int rowWidth) {
        int gripX = rowX + rowWidth - 10;
        int deleteX = gripX - 14;
        return deleteX - MACHINE_SLOT_GAP - MACHINE_SLOT_SIZE;
    }

    private static void drawSlot(GuiGraphics graphics, int x, int y, boolean hovered) {
        graphics.fill(x, y, x + MACHINE_SLOT_SIZE, y + MACHINE_SLOT_SIZE, -15921903);
        graphics.renderOutline(
                x, y, MACHINE_SLOT_SIZE, MACHINE_SLOT_SIZE,
                hovered ? -8612865 : -11908521);
    }

    @Unique
    private static boolean industrialColonies$machineSlotHit(
            double mouseX,
            double mouseY,
            int x,
            int y
    ) {
        return mouseX >= x && mouseX < x + MACHINE_SLOT_SIZE
                && mouseY >= y && mouseY < y + MACHINE_SLOT_SIZE;
    }
}
