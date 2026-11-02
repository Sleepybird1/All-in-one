package dev.godpc.industrialcolonies;

import com.zizazr.kjsgen.core.ContentKind;
import com.zizazr.kjsgen.core.SlotContent;
import mekanism.api.MekanismAPI;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.inventory.InventoryMenu;

/** Optional Mekanism chemical display; never converts chemicals into fluids. */
public final class KjsGenChemicalRendering {
    private KjsGenChemicalRendering() {}

    public static void draw(GuiGraphics graphics, int x, int y, SlotContent content) {
        var client = Minecraft.getInstance();
        var id = ResourceLocation.tryParse(content.id());
        var chemical = MekanismAPI.EMPTY_CHEMICAL;
        if (id != null) {
            chemical = content.kind() == ContentKind.CHEMICAL_TAG
                    ? MekanismAPI.CHEMICAL_REGISTRY.getTag(TagKey.create(MekanismAPI.CHEMICAL_REGISTRY_NAME, id))
                        .flatMap(tag -> tag.stream().findFirst()).map(holder -> holder.value())
                        .orElse(MekanismAPI.EMPTY_CHEMICAL)
                    : MekanismAPI.CHEMICAL_REGISTRY.get(id);
        }
        if (chemical == null || chemical.isEmptyType()) {
            graphics.fill(x + 1, y + 1, x + 17, y + 17, 0xff6b3248);
            graphics.drawString(client.font, "?", x + 6, y + 4, 0xffffffff, false);
        } else {
            var sprite = client.getTextureAtlas(InventoryMenu.BLOCK_ATLAS).apply(chemical.getIcon());
            int tint = chemical.getTint();
            graphics.setColor(((tint >> 16) & 255) / 255f, ((tint >> 8) & 255) / 255f,
                    (tint & 255) / 255f, 1);
            try {
                graphics.blit(x + 1, y + 1, 0, 16, 16, sprite);
            } finally {
                graphics.setColor(1, 1, 1, 1);
            }
        }
        String amount = Integer.toString(content.amount());
        float scale = Math.min(.65f, 16f / Math.max(1, client.font.width(amount)));
        graphics.pose().pushPose();
        graphics.pose().translate(x + 18, y + 11, 200);
        graphics.pose().scale(scale, scale, 1);
        graphics.drawString(client.font, amount, -client.font.width(amount), 0, 0xffffffff, true);
        graphics.pose().popPose();
        if (content.kind() == ContentKind.CHEMICAL_TAG)
            graphics.drawString(client.font, "#", x + 1, y + 1, 0xffffc857, true);
    }
}
