package dev.godpc.industrialcolonies;

import com.simibubi.create.content.processing.sequenced.SequencedAssemblyItem;
import com.zizazr.kjsgen.codegen.JsUtil;
import com.zizazr.kjsgen.core.*;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;

/** Export-only adaptation: never changes the user's project or its visible middle slot. */
public final class AssemblyWorkpieceCodegen {
    public static String generate(RecipeInstance source, RecipeTypeDefinition type) {
        var prepared = prepare(source);
        return prepared.finish(ExtendedSequenceCodegen.generate(prepared.recipe(), type));
    }
    public record Prepared(RecipeInstance recipe, String appearance) {
        public String finish(String code) {
            if (appearance == null) return code;
            String old = ".transitionalItem(" + JsUtil.quote(AssemblyWorkpieceItem.ID) + ")";
            String value = "Item.of(" + JsUtil.quote(AssemblyWorkpieceItem.ID)
                    + ", {'minecraft:custom_data': {" + JsUtil.quote(AssemblyWorkpieceItem.APPEARANCE)
                    + ": " + JsUtil.quote(appearance) + "}})";
            if (!code.contains(old)) throw new IllegalStateException("Assembly transition exporter changed; refusing incomplete export");
            return code.replace(old, ".transitionalItem(" + value + ")");
        }
    }

    public static Prepared prepare(RecipeInstance source) {
        var selected = source.slot("transitional");
        if (selected.isEmpty()) return new Prepared(source, null);
        if (selected.kind() != ContentKind.ITEM) throw new IllegalArgumentException("Workpiece appearance must be one concrete item");
        if (selected.id().equals(AssemblyWorkpieceItem.ID)) throw new IllegalArgumentException("Select a finished item as the workpiece appearance");
        var id = ResourceLocation.tryParse(selected.id());
        if (id == null || !BuiltInRegistries.ITEM.containsKey(id)) throw new IllegalArgumentException("Unknown workpiece appearance: " + selected.id());
        // Preserve legacy explicitly unfinished items and their existing exported identity.
        var item = BuiltInRegistries.ITEM.get(id);
        if (item instanceof SequencedAssemblyItem || (id.getNamespace().equals("industrial_colonies")
                && id.getPath().startsWith("unfinished_"))) return new Prepared(source, null);
        var copy = RecipeInstance.fromJson(source.toJson().deepCopy());
        copy.setSlot("transitional", SlotContent.item(AssemblyWorkpieceItem.ID, 1));
        return new Prepared(copy, selected.id());
    }
}
