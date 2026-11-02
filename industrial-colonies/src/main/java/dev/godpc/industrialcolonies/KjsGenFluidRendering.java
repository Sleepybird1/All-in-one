package dev.godpc.industrialcolonies;

import com.zizazr.kjsgen.core.ContentKind;
import com.zizazr.kjsgen.core.SlotContent;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.neoforge.client.extensions.common.IClientFluidTypeExtensions;
import net.neoforged.neoforge.fluids.FluidStack;

/** Fluid ingredients are fluid sprites, including fluids with no bucket item. */
public final class KjsGenFluidRendering {
    private KjsGenFluidRendering() {}
    public static boolean isFluid(SlotContent content) {
        return isFluid(content.kind());
    }
    public static boolean isFluid(ContentKind kind) {
        return kind==ContentKind.FLUID || kind==ContentKind.FLUID_TAG;
    }
    public static Fluid resolve(SlotContent content) {
        return resolve(content.kind(),content.id(),0);
    }
    private static Fluid resolve(ContentKind kind,String value,long cycle) {
        var id=ResourceLocation.tryParse(value);
        if(id==null)return Fluids.EMPTY;
        if(kind==ContentKind.FLUID_TAG)
            return BuiltInRegistries.FLUID.getTag(TagKey.create(Registries.FLUID,id))
                    .map(set->set.size()==0?Fluids.EMPTY:set.get(cycleMemberIndex(cycle,set.size())).value()).orElse(Fluids.EMPTY);
        return BuiltInRegistries.FLUID.get(id);
    }
    static int cycleMemberIndex(long cycle,int size) {
        if(size<=0)throw new IllegalArgumentException("Fluid tag must have a member before cycling");
        return (int)Math.floorMod(cycle,(long)size);
    }
    static int normalizedTint(int tint) {
        // Match JEI's native handling of mods that return RGB without an alpha byte.
        return (tint&0xff000000)==0?tint|0xff000000:tint;
    }
    /** Same 16-pixel region as the native picker icon; no amount or authored state changes. */
    public static void drawPicker(GuiGraphics g,int x,int y,ContentKind kind,String id,long cycle) {
        if(!isFluid(kind))return;
        drawSprite(g,x,y,resolve(kind,id,cycle),1000);
        if(kind==ContentKind.FLUID_TAG)g.drawString(Minecraft.getInstance().font,"#",x,y,0xffffc857,true);
    }
    public static void draw(GuiGraphics g,int x,int y,SlotContent content) {
        var mc=Minecraft.getInstance();
        drawSprite(g,x+1,y+1,resolve(content),Math.max(1,content.amount()));
        String amount=Integer.toString(content.amount());
        g.pose().pushPose();
        try {
            g.pose().translate(x+18,y+11,200);g.pose().scale(.65f,.65f,1);
            g.drawString(mc.font,amount,-mc.font.width(amount),0,0xffffffff,true);
        } finally {g.pose().popPose();}
        if(content.kind()==ContentKind.FLUID_TAG)g.drawString(mc.font,"#",x+1,y+1,0xffffc857,true);
    }
    private static void drawSprite(GuiGraphics g,int x,int y,Fluid fluid,int amount) {
        var mc=Minecraft.getInstance();
        if(fluid==Fluids.EMPTY) {
            g.fill(x,y,x+16,y+16,0xff6b3248);
            g.drawString(mc.font,"?",x+5,y+3,0xffffffff,false);
        } else {
            var stack=new FluidStack(fluid,amount);
            var extension=IClientFluidTypeExtensions.of(fluid);
            var texture=extension.getStillTexture(stack);
            var sprite=mc.getTextureAtlas(InventoryMenu.BLOCK_ATLAS).apply(texture==null
                    ?ResourceLocation.withDefaultNamespace("missingno"):texture);
            int tint=normalizedTint(extension.getTintColor(stack));
            g.setColor(((tint>>16)&255)/255f,((tint>>8)&255)/255f,(tint&255)/255f,((tint>>>24)&255)/255f);
            try {g.blit(x,y,0,16,16,sprite);} finally {g.setColor(1,1,1,1);}
        }
    }
}
