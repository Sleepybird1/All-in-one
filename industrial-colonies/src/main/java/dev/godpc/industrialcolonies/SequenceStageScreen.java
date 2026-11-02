package dev.godpc.industrialcolonies;
import com.zizazr.kjsgen.core.*;
import com.zizazr.kjsgen.ui.vanilla.VanillaSlotEditScreen;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.*;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.neoforged.fml.ModList;
import java.util.*;

public final class SequenceStageScreen extends Screen {
    private final Screen parent;
    private final RecipeInstance recipe, draft;
    private final RecipeTypeDefinition type;
    private final int index;
    private final Runnable changed;
    private EditBox time;
    private String timeText;
    private String damageText;
    private String error="";
    public SequenceStageScreen(Screen parent,RecipeInstance recipe,RecipeTypeDefinition type,int index,Runnable changed) {
        super(Component.literal("Assembly stage "+(index+1)));
        this.parent=parent;this.recipe=recipe;this.type=type;this.index=index;this.changed=changed;
        draft=RecipeInstance.fromJson(recipe.toJson().deepCopy());timeText=recipe.param(type,SequenceStageOptions.key(index,"Ticks"));
        damageText=recipe.param(type,SequenceStageOptions.key(index,"ToolDamage"));if(damageText.isBlank())damageText="1";
        if(timeText.isEmpty())timeText="100";
    }
    @Override protected void init() {
        int x=width/2-120,y=height/2-105;
        time=new EditBox(font,x+100,y+25,135,20,Component.literal("Processing ticks"));
        time.setMaxLength(10);time.setValue(timeText);time.setResponder(value->timeText=value);addRenderableWidget(time);
        String operation=CreateSpecialModel.stepTypeId(recipe,type,index);
        if(operation.equals("deploying")) {
            time.visible=false;time.active=false;
            var damage=new EditBox(font,x+120,y+52,115,20,Component.literal("Damage per use"));damage.setMaxLength(10);damage.setValue(damageText);damage.setResponder(value->damageText=value);addRenderableWidget(damage);
            String key=SequenceStageOptions.key(index,"ToolUse");
            addRenderableWidget(Button.builder(Component.literal("Tool: "+ToolUseOptions.mode(draft,type,key)),button->{
                var modes=ToolUseOptions.DEPLOY_MODES;
                String next=modes.get((modes.indexOf(ToolUseOptions.mode(draft,type,key))+1)%modes.size());
                draft.setParam(key,next);button.setMessage(Component.literal("Tool: "+next));
            }).bounds(x,y+25,235,20).build());
        }
        if(SequenceStageOptions.basin(operation)) {
            var heats=new ArrayList<>(List.of("none","heated","superheated"));
            if(ModList.get().isLoaded("createlowheated"))heats.add(1,"lowheated");
            addRenderableWidget(Button.builder(Component.literal("Heat: "+SequenceStageOptions.heat(draft,type,index)),button->{
                String next=heats.get((heats.indexOf(SequenceStageOptions.heat(draft,type,index))+1)%heats.size());
                draft.setParam(SequenceStageOptions.key(index,"Heat"),next);button.setMessage(Component.literal("Heat: "+next));
            }).bounds(x,y+52,235,20).build());
            for(int n=0;n<4;n++) {
                final int slot=n;String key=SequenceStageOptions.key(index,"Extra"+n);
                var content=draft.slot(key);
                addRenderableWidget(Button.builder(Component.literal("Input "+(n+1)+": "+(content.isEmpty()?"Add item/fluid":content.id())),button->{
                    var definition=new SlotDefinition(key,SlotRole.INPUT,0,0,false,true,true,true,false,true,false,false);
                    minecraft.setScreen(new VanillaSlotEditScreen(this,definition,"Stage input "+(slot+1),draft.slot(key),value->draft.setSlot(key,value)));
                }).bounds(x,y+77+n*23,235,20).build());
            }
        }
        addRenderableWidget(Button.builder(Component.literal("Save"),button->{
            try {
                if(operation.equals("deploying")) {
                    String key=SequenceStageOptions.key(index,"ToolUse");
                    draft.setParam(SequenceStageOptions.key(index,"ToolDamage"),damageText);
                    int damage=ToolUseOptions.damage(draft,type,SequenceStageOptions.key(index,"ToolDamage"));
                    ToolUseOptions.deploySuffix(ToolUseOptions.mode(draft,type,key),CreateSpecialModel.stepItem(draft,index),damage);
                    recipe.setParam(SequenceStageOptions.key(index,"ToolDamage"),Integer.toString(damage));
                    recipe.setParam(key,ToolUseOptions.mode(draft,type,key));
                    changed.run();minecraft.setScreen(parent);return;
                }
                draft.setParam(SequenceStageOptions.key(index,"Ticks"),timeText);
                SequenceStageOptions.ticks(draft,type,index);
                recipe.setParam(SequenceStageOptions.key(index,"Ticks"),timeText);
                recipe.setParam(SequenceStageOptions.key(index,"Heat"),SequenceStageOptions.heat(draft,type,index));
                for(int n=0;n<4;n++)recipe.setSlot(SequenceStageOptions.key(index,"Extra"+n),draft.slot(SequenceStageOptions.key(index,"Extra"+n)));
                changed.run();minecraft.setScreen(parent);
            } catch(IllegalArgumentException ex) {error=ex.getMessage();}
        }).bounds(x,y+178,112,20).build());
        addRenderableWidget(Button.builder(Component.literal("Cancel"),button->onClose()).bounds(x+123,y+178,112,20).build());
    }
    @Override public void render(GuiGraphics graphics,int mouseX,int mouseY,float partial) {
        renderBackground(graphics,mouseX,mouseY,partial);super.render(graphics,mouseX,mouseY,partial);
        int x=width/2-120,y=height/2-105;
        graphics.drawString(font,title,x,y,0xFFFFFFFF);
        if(CreateSpecialModel.stepTypeId(recipe,type,index).equals("deploying")) {
            graphics.drawString(font,"Damage per use",x,y+57,0xFFFFFFFF);
            graphics.drawString(font,"Applies each time this step runs",x,y+82,0xFFFFFFFF);
            graphics.drawString(font,"Keep: no wear. Native: default wear.",x,y+97,0xFFFFFFFF);
        } else graphics.drawString(font,"Time (ticks)",x,y+31,0xFFFFFFFF);
        graphics.drawString(font,error,x,y+204,0xFFFF8888);
    }
    @Override public void onClose() { minecraft.setScreen(parent); }
}
