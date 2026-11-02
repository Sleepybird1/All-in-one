package dev.godpc.industrialcolonies.mixin;

import com.zizazr.kjsgen.core.RecipeTypeDefinition;
import com.zizazr.kjsgen.core.RecipeTypeRegistry;
import com.zizazr.kjsgen.ui.vanilla.VanillaTypePickerScreen;
import dev.godpc.industrialcolonies.RecipeTypeFolders;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyArg;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.ArrayList;
import java.util.List;

/** Mod folders beside the existing recipe grid. No saved recipes or type IDs are rewritten. */
@Mixin(value = VanillaTypePickerScreen.class, remap = false)
public abstract class KjsGenTypeFolderMixin extends Screen {
    @Shadow @Final private List<RecipeTypeDefinition> filtered;
    @Shadow private String query;
    @Shadow private int scroll;
    @Shadow private int gridX;
    @Shadow private int gridY;
    @Shadow private int gridW;
    @Shadow private int gridH;
    @Shadow private int cols;
    @Shadow private void refilter() { throw new AssertionError(); }

    @Unique private String industrialColonies$folder = RecipeTypeFolders.ALL;
    @Unique private int industrialColonies$folderOffset;
    @Unique private int industrialColonies$railX;
    @Unique private int industrialColonies$railRows;
    @Unique private boolean industrialColonies$ready;
    @Unique private final List<Button> industrialColonies$folderButtons = new ArrayList<>();
    @Unique private Button industrialColonies$previous;
    @Unique private Button industrialColonies$next;
    @Unique private List<RecipeTypeFolders.Folder> industrialColonies$folders = List.of();
    @Unique private static final int industrialColonies$RAIL_WIDTH = 104;

    protected KjsGenTypeFolderMixin(Component title) { super(title); }

    @ModifyArg(method = "init", at = @At(value = "INVOKE",
            target = "Lcom/zizazr/kjsgen/ui/vanilla/VanillaTypePickerScreen;centerDialog(II)V"), index = 0)
    private int industrialColonies$widerPicker(int originalWidth) {
        return Math.max(originalWidth, Math.min(460, width - 16));
    }

    @Inject(method = "init", at = @At("HEAD"))
    private void industrialColonies$prepareResize(CallbackInfo callback) {
        industrialColonies$ready = false;
        industrialColonies$folderButtons.clear();
    }

    @Inject(method = "init", at = @At("TAIL"))
    private void industrialColonies$addFolders(CallbackInfo callback) {
        industrialColonies$railX = gridX;
        gridX += industrialColonies$RAIL_WIDTH;
        gridW -= industrialColonies$RAIL_WIDTH;
        cols = Math.max(1, (gridW + 4) / 62);
        industrialColonies$railRows = Math.max(1, (gridH - 22) / 20);
        for (int row = 0; row < industrialColonies$railRows; row++) {
            final int visibleRow = row;
            Button button = Button.builder(Component.empty(), ignored -> industrialColonies$chooseFolder(visibleRow))
                    .bounds(industrialColonies$railX, gridY + row * 20, industrialColonies$RAIL_WIDTH - 6, 18).build();
            industrialColonies$folderButtons.add(addRenderableWidget(button));
        }
        industrialColonies$previous = addRenderableWidget(Button.builder(Component.literal("Previous"), ignored ->
                        industrialColonies$scrollFolders(-industrialColonies$railRows))
                .bounds(industrialColonies$railX, gridY + gridH - 20, 47, 18).build());
        industrialColonies$next = addRenderableWidget(Button.builder(Component.literal("Next"), ignored ->
                        industrialColonies$scrollFolders(industrialColonies$railRows))
                .bounds(industrialColonies$railX + 49, gridY + gridH - 20, 49, 18).build());
        industrialColonies$ready = true;
        refilter();
    }

    @Inject(method = "refilter", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$filterFolder(CallbackInfo callback) {
        List<RecipeTypeDefinition> available = RecipeTypeRegistry.all().stream()
                .filter(RecipeTypeDefinition::isAvailable)
                .filter(type -> RecipeTypeFolders.visibleInPicker(industrialColonies$entry(type))).toList();
        industrialColonies$folders = RecipeTypeFolders.folders(available.stream()
                .map(KjsGenTypeFolderMixin::industrialColonies$entry).toList(), query);
        filtered.clear();
        available.stream().filter(type -> RecipeTypeFolders.inFolder(industrialColonies$entry(type),
                industrialColonies$folder, query)).forEach(filtered::add);
        scroll = 0;
        if (industrialColonies$ready) industrialColonies$updateButtons();
        callback.cancel();
    }

    @Unique private static RecipeTypeFolders.Entry industrialColonies$entry(RecipeTypeDefinition type) {
        // The installed typeName method is package-private. Mirror its translation/fallback rule.
        String path = type.id().substring(type.id().indexOf(':') + 1);
        String fallback = path.isEmpty() ? type.id()
                : Character.toUpperCase(path.charAt(0)) + path.substring(1).replace('_', ' ');
        String name = Component.translatableWithFallback(type.translationKey(), fallback).getString();
        return new RecipeTypeFolders.Entry(type.id(), type.modId(), type.requiresMod(), type.iconItem(),
                name);
    }

    @Unique private void industrialColonies$chooseFolder(int visibleRow) {
        int index = industrialColonies$folderOffset + visibleRow;
        if (index >= industrialColonies$folders.size()) return;
        industrialColonies$folder = industrialColonies$folders.get(index).id();
        refilter();
    }

    @Unique private void industrialColonies$scrollFolders(int amount) {
        industrialColonies$folderOffset = RecipeTypeFolders.clampOffset(industrialColonies$folderOffset + amount,
                industrialColonies$folders.size(), industrialColonies$railRows);
        industrialColonies$updateButtons();
    }

    @Unique private void industrialColonies$updateButtons() {
        industrialColonies$folderOffset = RecipeTypeFolders.clampOffset(industrialColonies$folderOffset,
                industrialColonies$folders.size(), industrialColonies$railRows);
        for (int row = 0; row < industrialColonies$folderButtons.size(); row++) {
            Button button = industrialColonies$folderButtons.get(row);
            int index = industrialColonies$folderOffset + row;
            button.visible = index < industrialColonies$folders.size();
            if (!button.visible) continue;
            RecipeTypeFolders.Folder folder = industrialColonies$folders.get(index);
            String marker = folder.id().equals(industrialColonies$folder) ? "> " : "";
            // The complete folder name and count remain in the narration and tooltip.
            button.setMessage(Component.literal(marker + folder.label() + " (" + folder.matches() + ")"));
            button.setTooltip(Tooltip.create(Component.literal(folder.label() + ": " + folder.matches() + " matching recipe types")));
        }
        industrialColonies$previous.active = industrialColonies$folderOffset > 0;
        industrialColonies$next.active = industrialColonies$folderOffset < RecipeTypeFolders.maxOffset(
                industrialColonies$folders.size(), industrialColonies$railRows);
    }

    /** The rail has its own scroll; the original machine grid and search keep their existing handling. */
    @Inject(method = "mouseScrolled", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$scrollRail(double mouseX, double mouseY, double horizontal, double vertical,
                                               CallbackInfoReturnable<Boolean> callback) {
        if (industrialColonies$ready && mouseX >= industrialColonies$railX && mouseX < gridX - 4
                && mouseY >= gridY && mouseY < gridY + gridH) {
            if (vertical != 0) industrialColonies$scrollFolders(vertical > 0 ? -1 : 1);
            callback.setReturnValue(true);
        }
    }
}
