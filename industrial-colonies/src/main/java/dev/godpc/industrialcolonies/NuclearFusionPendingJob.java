package dev.godpc.industrialcolonies;

import java.lang.reflect.Field;
import java.util.List;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtOps;
import net.minecraft.resources.RegistryOps;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.neoforged.neoforge.fluids.FluidStack;

/** Keeps a consumed batch tied to the exact registered recipe that consumed it.
 * Unknown legacy or changed recipes remain held; no guessed refunds or rematching.
 */
public final class NuclearFusionPendingJob {
    public static final String KEY="IndustrialColoniesPendingFusion";
    private CompoundTag identity;
    private boolean idlePending;
    private double idleProgress;
    private Object idleRecipe;

    private static Field field(Object reaction,String name) {
        try { var f=reaction.getClass().getDeclaredField(name);f.setAccessible(true);return f; }
        catch(ReflectiveOperationException e){throw new IllegalStateException("Unsupported fusion reaction field "+name,e);}
    }
    private static Object get(Object reaction,String name) {
        try{return field(reaction,name).get(reaction);}
        catch(IllegalAccessException e){throw new IllegalStateException(e);}
    }
    private static void set(Object reaction,String name,Object value) {
        try{field(reaction,name).set(reaction,value);}
        catch(IllegalAccessException e){throw new IllegalStateException(e);}
    }
    public static boolean pending(Object reaction){return Boolean.TRUE.equals(get(reaction,"fuelConsumed"));}

    private static CompoundTag fingerprint(BlockEntity controller,Recipe<?> recipe,ResourceLocation id) throws ReflectiveOperationException {
        var level=controller.getLevel();
        if(level==null)throw new IllegalStateException("No recipe registry");
        var tag=new CompoundTag();tag.putInt("version",1);tag.putString("id",id.toString());
        tag.put("recipe",Recipe.CODEC.encodeStart(RegistryOps.create(NbtOps.INSTANCE,level.registryAccess()),recipe).getOrThrow());
        var outputs=new ListTag();
        for(Object output:(List<?>)recipe.getClass().getMethod("outputs").invoke(recipe)) {
            var fluid=(FluidStack)output.getClass().getMethod("resolve").invoke(output);
            if(fluid.isEmpty())throw new IllegalStateException("Unresolved fusion product");
            outputs.add(fluid.save(level.registryAccess()));
        }
        tag.put("resolvedOutputs",outputs);return tag;
    }

    /** Runs before native fuel draining. Only recipes actually registered in this level qualify. */
    public boolean prepare(Object controller,Object value) {
        identity=null;
        if(!(controller instanceof BlockEntity core)||core.getLevel()==null||!(value instanceof Recipe<?> recipe))return false;
        try {
            for(var holder:core.getLevel().getRecipeManager().getRecipes()) {
                if(holder.value()==recipe) {identity=fingerprint(core,recipe,holder.id());return true;}
            }
        } catch(ReflectiveOperationException|RuntimeException failure){identity=null;}
        return false;
    }

    /** Clear first, then restore only an exact current-registry match. Native cooling still runs. */
    public void beforeTick(Object reaction,Object controller) {
        if(!pending(reaction)){identity=null;return;}
        set(reaction,"currentRecipe",null);
        double progress=((Number)get(reaction,"ticksProcessed")).doubleValue();
        if(!Double.isFinite(progress)||progress<0||identity==null||identity.getInt("version")!=1)return;
        if(!(controller instanceof BlockEntity core)||core.getLevel()==null)return;
        try {
            var id=ResourceLocation.tryParse(identity.getString("id"));if(id==null)return;
            var holder=core.getLevel().getRecipeManager().byKey(id).orElse(null);
            if(holder!=null&&identity.equals(fingerprint(core,holder.value(),id)))set(reaction,"currentRecipe",holder.value());
        } catch(ReflectiveOperationException|RuntimeException failure){/* Preserve the unresolved pending job. */}
    }

    public void save(Object reaction,CompoundTag tag) {
        tag.remove(KEY);
        if(pending(reaction)&&identity!=null)tag.put(KEY,identity.copy());
    }
    public void load(Object reaction,CompoundTag tag) {
        identity=pending(reaction)&&tag.contains(KEY,10)?tag.getCompound(KEY).copy():null;
        set(reaction,"currentRecipe",null);
        idlePending=false;idleRecipe=null;
    }
    public void beforeIdle(Object reaction) {
        idlePending=pending(reaction);
        if(idlePending){idleProgress=((Number)get(reaction,"ticksProcessed")).doubleValue();idleRecipe=get(reaction,"currentRecipe");}
    }
    public void afterIdle(Object reaction) {
        if(idlePending){set(reaction,"fuelConsumed",true);set(reaction,"ticksProcessed",idleProgress);set(reaction,"currentRecipe",idleRecipe);}
        idlePending=false;idleRecipe=null;
    }
}
