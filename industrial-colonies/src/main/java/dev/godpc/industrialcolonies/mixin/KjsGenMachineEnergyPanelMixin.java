package dev.godpc.industrialcolonies.mixin;

import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeRegistry;
import com.zizazr.kjsgen.ui.vanilla.VanillaEditorScreen;
import dev.godpc.industrialcolonies.KjsGenMachineEnergyInfo;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.network.chat.Component;
import net.neoforged.fml.loading.FMLPaths;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/** Native editable controls stay intact; energy type and derived facts are read-only. */
@Mixin(value = VanillaEditorScreen.class, remap = false)
public abstract class KjsGenMachineEnergyPanelMixin {
    @Shadow @Final private List<AbstractWidget> paramWidgets;
    @Shadow @Final private List<Component> paramLabels;
    @Shadow private int paramW;
    @Shadow abstract Optional<RecipeInstance> selectedRecipe();
    @Shadow private void layoutParamWidgets() { throw new AssertionError(); }
    @Shadow private void addParam(Component label, AbstractWidget widget) { throw new AssertionError(); }
    @Unique private final List<EditBox> industrialColonies$energyFields = new ArrayList<>();
    @Unique private KjsGenMachineEnergyInfo.Settings industrialColonies$energySettings;
    @Unique private long industrialColonies$nextEnergySettingsRead;

    @Unique private List<KjsGenMachineEnergyInfo.Row> industrialColonies$energyRows() {
        var selected = selectedRecipe();
        if (selected.isEmpty()) return List.of();
        var definition = RecipeTypeRegistry.get(selected.get().typeId());
        if (definition.isEmpty()) return List.of();
        long now = System.nanoTime();
        if (industrialColonies$energySettings == null || now >= industrialColonies$nextEnergySettingsRead) {
            industrialColonies$energySettings = KjsGenMachineEnergyInfo.loadSettings(FMLPaths.CONFIGDIR.get());
            industrialColonies$nextEnergySettingsRead = now + 5_000_000_000L;
        }
        return KjsGenMachineEnergyInfo.describe(selected.get(), definition.get(), industrialColonies$energySettings);
    }

    @Inject(method = "buildParamWidgets", at = @At("TAIL"))
    private void industrialColonies$addNativeEnergyFacts(CallbackInfo ci) {
        industrialColonies$energyFields.clear();
        var rows = industrialColonies$energyRows();
        if (rows.isEmpty()) return;
        int priorSize = paramWidgets.size();
        for (var row : rows) {
            var widget = new EditBox(Minecraft.getInstance().font, 0, 0, Math.max(20, paramW - 60), 16,
                Component.literal(row.label()));
            widget.setMaxLength(1024);
            widget.setEditable(false);
            widget.setTextColorUneditable(0xFFE0E0E0);
            widget.setValue(row.value());
            widget.setCursorPosition(0);
            widget.setHighlightPos(0);
            widget.setTooltip(Tooltip.create(Component.literal(row.value() + "\n" + row.explanation())));
            addParam(Component.literal(row.label()), widget);
            industrialColonies$energyFields.add(widget);
        }
        var widgets = new ArrayList<>(paramWidgets.subList(priorSize, paramWidgets.size()));
        var labels = new ArrayList<>(paramLabels.subList(priorSize, paramLabels.size()));
        paramWidgets.subList(priorSize, paramWidgets.size()).clear();
        paramLabels.subList(priorSize, paramLabels.size()).clear();
        paramWidgets.addAll(0, widgets);
        paramLabels.addAll(0, labels);
        layoutParamWidgets();
    }

    @Inject(method = "drawParams", at = @At("HEAD"))
    private void industrialColonies$refreshNativeEnergyFacts(GuiGraphics graphics, CallbackInfo ci) {
        if (industrialColonies$energyFields.isEmpty()) return;
        var rows = industrialColonies$energyRows();
        for (int i = 0; i < Math.min(rows.size(), industrialColonies$energyFields.size()); i++) {
            var widget = industrialColonies$energyFields.get(i);
            var row = rows.get(i);
            if (!widget.getValue().equals(row.value())) {
                widget.setValue(row.value());
                widget.setCursorPosition(0);
                widget.setHighlightPos(0);
            }
            widget.setEditable(false); // Native scrolling toggles active, never this read-only flag.
            widget.setTooltip(Tooltip.create(Component.literal(row.value() + "\n" + row.explanation())));
        }
    }
}
