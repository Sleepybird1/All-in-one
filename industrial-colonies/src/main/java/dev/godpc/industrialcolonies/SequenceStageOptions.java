package dev.godpc.industrialcolonies;
import com.zizazr.kjsgen.core.*;
import java.util.*;

public final class SequenceStageOptions {
    public static final Set<String> FANS=Set.of("smoking","blasting","splashing","haunting");
    public static boolean basin(String family) { return family.equals("mixing") || family.equals("compacting"); }
    public static boolean configurable(String family) { return basin(family) || FANS.contains(family) || family.equals("cutting") || family.equals("deploying"); }
    public static String key(int stage,String field) { return "icSeq"+stage+field; }
    public static String heat(RecipeInstance recipe, RecipeTypeDefinition type,int stage) {
        String value=recipe.param(type,key(stage,"Heat"));return value.isEmpty()?"none":value;
    }
    public static int ticks(RecipeInstance recipe, RecipeTypeDefinition type,int stage) {
        String value=recipe.param(type,key(stage,"Ticks"));
        try { int ticks=value.isEmpty()?100:Integer.parseInt(value); if(ticks>0)return ticks; }
        catch(NumberFormatException ignored) {}
        throw new IllegalArgumentException("Stage "+(stage+1)+" time must be a positive whole number of ticks");
    }
    private record Saved(String heat,String ticks,String toolUse,String toolDamage,List<SlotContent> extras) {}
    private static List<Saved> capture(RecipeInstance recipe,RecipeTypeDefinition type) {
        var all=new ArrayList<Saved>();
        for(int i=0;i<CreateSpecialModel.seqLen(recipe,type);i++) {
            var slots=new ArrayList<SlotContent>();for(int n=0;n<4;n++)slots.add(recipe.slot(key(i,"Extra"+n)));
            all.add(new Saved(recipe.param(type,key(i,"Heat")),recipe.param(type,key(i,"Ticks")),recipe.param(type,key(i,"ToolUse")),recipe.param(type,key(i,"ToolDamage")),slots));
        }
        return all;
    }
    public static void clear(RecipeInstance recipe,int index) {
        recipe.setParam(key(index,"Heat"),"");recipe.setParam(key(index,"Ticks"),"");
        recipe.setParam(key(index,"ToolUse"),"");recipe.setParam(key(index,"ToolDamage"),"");
        for(int n=0;n<4;n++)recipe.setSlot(key(index,"Extra"+n),SlotContent.EMPTY);
    }
    private static void write(RecipeInstance recipe,List<Saved> all,int oldSize) {
        for(int i=0;i<oldSize;i++)clear(recipe,i);
        for(int i=0;i<all.size();i++) {
            var saved=all.get(i);recipe.setParam(key(i,"Heat"),saved.heat());recipe.setParam(key(i,"Ticks"),saved.ticks());
            recipe.setParam(key(i,"ToolUse"),saved.toolUse());recipe.setParam(key(i,"ToolDamage"),saved.toolDamage());
            for(int n=0;n<4;n++)recipe.setSlot(key(i,"Extra"+n),saved.extras().get(n));
        }
    }
    public static void move(RecipeInstance recipe,RecipeTypeDefinition type,int from,int to) {
        var all=capture(recipe,type);int size=all.size();
        if(from<0||to<0||from>=size||to>=size||from==to)return;
        all.add(to,all.remove(from));write(recipe,all,size);
    }
    public static void remove(RecipeInstance recipe,RecipeTypeDefinition type,int index) {
        var all=capture(recipe,type);int size=all.size();
        if(index<0||index>=size)return;all.remove(index);write(recipe,all,size);
    }
}
