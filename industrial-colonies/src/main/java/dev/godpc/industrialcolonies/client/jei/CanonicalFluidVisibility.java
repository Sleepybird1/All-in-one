package dev.godpc.industrialcolonies.client.jei;

import com.google.gson.*;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import dev.godpc.industrialcolonies.processing.EffectiveFluidNormalizer;
import java.util.*;
import mezz.jei.api.IModPlugin;
import mezz.jei.api.JeiPlugin;
import mezz.jei.api.constants.VanillaTypes;
import mezz.jei.api.ingredients.subtypes.UidContext;
import mezz.jei.api.neoforge.NeoForgeTypes;
import mezz.jei.api.runtime.IJeiRuntime;
import net.minecraft.client.Minecraft;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.*;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.material.*;
import net.neoforged.neoforge.fluids.*;

/** Optional ingredient-list cleanup; recipe displays and registry identities are retained. */
@JeiPlugin
public final class CanonicalFluidVisibility implements IModPlugin {
    private static IJeiRuntime runtime;
    private static JsonObject report=new JsonObject();
    private static JsonObject packets;
    public static IJeiRuntime runtime(){return runtime;}
    public static JsonObject report(){return report.deepCopy();}
    /** Families already canonical in recipes still need duplicate-list cleanup. */
    public static JsonArray boundaryPolicies(){
        try(var in=CanonicalFluidVisibility.class.getResourceAsStream("/industrial_colonies/fluid-visibility-boundaries.json")){
            if(in==null)throw new IllegalStateException("Missing fluid visibility boundaries");
            return JsonParser.parseReader(new InputStreamReader(in,StandardCharsets.UTF_8)).getAsJsonArray();
        }catch(Exception e){throw new IllegalStateException("Invalid fluid visibility boundaries",e);}
    }
    /** Read-only admission: absent recipes stay absent, changed recipes hold the family. */
    public static String boundaryAdmission(Level level,JsonArray references){
        boolean present=false;
        var ops=net.minecraft.resources.RegistryOps.create(com.mojang.serialization.JsonOps.INSTANCE,level.registryAccess());
        for(var value:references){
            var row=value.getAsJsonObject();String id=row.get("id").getAsString();
            var holder=level.getRecipeManager().byKey(ResourceLocation.parse(id));
            if(holder.isEmpty())continue;
            present=true;
            try{
                var recipe=holder.get().value();
                if(!recipe.getClass().getName().equals(row.get("class").getAsString()))return "HELD_CLASS: "+id;
                if(row.has("packetSHA256")){
                    if(!BuiltInRegistries.RECIPE_SERIALIZER.getKey(recipe.getSerializer()).toString().equals(row.get("serializer").getAsString()))return "HELD_SERIALIZER: "+id;
                    if(!packetHash(level,holder.get()).equals(row.get("packetSHA256").getAsString()))return "HELD_PAYLOAD: "+id;
                    continue;
                }
                var data=net.minecraft.world.item.crafting.Recipe.CODEC.encodeStart(ops,recipe).getOrThrow();
                if(!EffectiveFluidNormalizer.fingerprint(data).equals(row.get("sha256").getAsString()))return "HELD_PAYLOAD: "+id;
            }catch(RuntimeException e){return "HELD_ENCODING: "+id;}
        }
        return present?"QUALIFIED":"HELD_NO_RECIPES";
    }
    /** Exact native payload fallback for client-only JSON representation differences. */
    @SuppressWarnings({"rawtypes","unchecked"})
    private static String packetHash(Level level,RecipeHolder<?> holder){
        var buffer=new net.minecraft.network.RegistryFriendlyByteBuf(io.netty.buffer.Unpooled.buffer(),level.registryAccess());
        try{
            ((net.minecraft.network.codec.StreamCodec)holder.value().getSerializer().streamCodec()).encode(buffer,holder.value());
            byte[] bytes=new byte[buffer.readableBytes()];buffer.readBytes(bytes);
            return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
        }catch(java.security.NoSuchAlgorithmException e){throw new IllegalStateException(e);}
        finally{buffer.release();}
    }
    public static boolean packetQualified(Level level,RecipeHolder<?> holder){
        try{
            if(packets==null){try(var in=CanonicalFluidVisibility.class.getResourceAsStream("/industrial_colonies/visibility-packet-fingerprints.json")){
                if(in==null)return false;
                packets=JsonParser.parseReader(new InputStreamReader(in,StandardCharsets.UTF_8)).getAsJsonObject();
            }}
            var row=packets.getAsJsonObject(holder.id().toString());if(row==null)return false;
            var recipe=holder.value();
            if(!recipe.getClass().getName().equals(row.get("recipeClass").getAsString()))return false;
            if(!BuiltInRegistries.RECIPE_SERIALIZER.getKey(recipe.getSerializer()).toString().equals(row.get("serializer").getAsString()))return false;
            return packetHash(level,holder).equals(row.get("sha256").getAsString());
        }catch(Exception e){return false;}
    }
    @Override public ResourceLocation getPluginUid(){return ResourceLocation.parse("industrial_colonies:canonical_fluid_visibility");}
    @Override public void onRuntimeUnavailable(){runtime=null;report=new JsonObject();}
    @Override public void onRuntimeAvailable(IJeiRuntime value){
        runtime=value;report=new JsonObject();
        if(!Boolean.getBoolean("industrial_colonies.canonicalFluidVisibility")){report.addProperty("status","DISABLED");return;}
        var level=Minecraft.getInstance().level;
        if(level==null){report.addProperty("status","HELD_NO_LEVEL");return;}
        var statuses=EffectiveFluidNormalizer.report(level.getRecipeManager());
        var packetAdmission=new HashMap<String,Boolean>();int admittedByPacket=0;
        var pairs=new TreeMap<String,String>();var required=new TreeMap<String,Set<String>>();
        for(var e:EffectiveFluidNormalizer.rules()){
            var rule=e.getAsJsonObject();String id=rule.get("id").getAsString();
            for(var v:rule.getAsJsonArray("changes")){
                var c=v.getAsJsonObject();String old=c.get("before").getAsString(),preferred=c.get("after").getAsString();
                String prior=pairs.putIfAbsent(old,preferred);
                if(prior!=null&&!prior.equals(preferred)){report.addProperty("status","HELD_CONFLICTING_POLICY");return;}
                required.computeIfAbsent(old,k->new TreeSet<>()).add(id);
            }
        }
        var boundaries=new HashMap<String,JsonArray>();
        for(var entry:boundaryPolicies()){
            var row=entry.getAsJsonObject();String alias=row.get("alias").getAsString(),preferred=row.get("preferred").getAsString();
            if(pairs.putIfAbsent(alias,preferred)!=null){report.addProperty("status","HELD_CONFLICTING_POLICY");return;}
            boundaries.put(alias,row.getAsJsonArray("references"));required.put(alias,Set.of());
        }
        var ingredients=value.getIngredientManager();var visibility=value.getIngredientVisibility();
        var fluids=new ArrayList<>(ingredients.getAllIngredients(NeoForgeTypes.FLUID_STACK));
        var items=new ArrayList<>(ingredients.getAllItemStacks());var rows=new JsonArray();int hidden=0;
        report.addProperty("registeredFluidsBefore",fluids.size());report.addProperty("registeredItemsBefore",items.size());
        for(var e:pairs.entrySet()){
            var row=new JsonObject();row.addProperty("alias",e.getKey());row.addProperty("preferred",e.getValue());
            var failures=new JsonArray();boolean present=false;
            if(boundaries.containsKey(e.getKey())){
                String admission=boundaryAdmission(level,boundaries.get(e.getKey()));
                row.addProperty("boundaryAdmission",admission);
                if(admission.equals("QUALIFIED"))present=true;else failures.add(admission);
            }
            for(String id:required.get(e.getKey())){
                String status=statuses.getOrDefault(id,"UNQUALIFIED");
                if(status.equals("CHANGED")||status.equals("ALREADY_CANONICAL"))present=true;
                else if(!status.equals("ABSENT")){
                    boolean qualified=packetAdmission.computeIfAbsent(id,k->level.getRecipeManager().byKey(ResourceLocation.parse(k)).map(h->packetQualified(level,h)).orElse(false));
                    if(qualified){present=true;admittedByPacket++;}else failures.add(id+": "+status);
                }
            }
            if(!present||!failures.isEmpty()){
                row.addProperty("status","HELD_RECIPE_CONTEXT");row.add("reasons",failures);rows.add(row);continue;
            }
            var preferredId=ResourceLocation.parse(e.getValue());var aliasId=ResourceLocation.parse(e.getKey());
            if(!BuiltInRegistries.FLUID.containsKey(preferredId)||!BuiltInRegistries.FLUID.containsKey(aliasId)){
                row.addProperty("status","HELD_MISSING_FLUID");rows.add(row);continue;
            }
            var preferred=BuiltInRegistries.FLUID.get(preferredId);var alias=BuiltInRegistries.FLUID.get(aliasId);
            boolean canonicalVisible=fluids.stream().anyMatch(f->f.getFluid()==preferred&&f.getComponentsPatch().isEmpty()&&visibility.isIngredientVisible(NeoForgeTypes.FLUID_STACK,f,UidContext.Ingredient));
            if(!canonicalVisible){row.addProperty("status","HELD_PREFERRED_NOT_VISIBLE");rows.add(row);continue;}
            var acceptedAliases=Collections.newSetFromMap(new IdentityHashMap<Fluid,Boolean>());acceptedAliases.add(alias);
            if(alias instanceof FlowingFluid flowing){acceptedAliases.add(flowing.getSource());acceptedAliases.add(flowing.getFlowing());}
            if(acceptedAliases.contains(preferred)){row.addProperty("status","HELD_SAME_FAMILY");rows.add(row);continue;}
            var hideFluids=fluids.stream().filter(f->acceptedAliases.contains(f.getFluid())&&f.getComponentsPatch().isEmpty()&&visibility.isIngredientVisible(NeoForgeTypes.FLUID_STACK,f,UidContext.Ingredient)).toList();
            boolean canonicalBucketVisible=items.stream().anyMatch(s->s.getItem() instanceof BucketItem&&s.getComponentsPatch().isEmpty()&&FluidUtil.getFluidContained(s).filter(f->f.getFluid()==preferred&&f.getAmount()==1000&&f.getComponentsPatch().isEmpty()).isPresent()&&visibility.isIngredientVisible(VanillaTypes.ITEM_STACK,s,UidContext.Ingredient));
            var hideItems=canonicalBucketVisible?items.stream().filter(s->s.getItem() instanceof BucketItem&&s.getComponentsPatch().isEmpty()&&FluidUtil.getFluidContained(s).filter(f->acceptedAliases.contains(f.getFluid())&&f.getAmount()==1000&&f.getComponentsPatch().isEmpty()).isPresent()&&visibility.isIngredientVisible(VanillaTypes.ITEM_STACK,s,UidContext.Ingredient)).toList():List.<ItemStack>of();
            // Hide only ingredient-list identities. Legacy recipe lookup stays available.
            var details=new JsonArray();
            for(var f:hideFluids){var d=new JsonObject();d.addProperty("kind","fluid");d.addProperty("id",BuiltInRegistries.FLUID.getKey(f.getFluid()).toString());d.addProperty("recipeVisibleBefore",visibility.isIngredientVisible(NeoForgeTypes.FLUID_STACK,f,UidContext.Recipe));details.add(d);}
            for(var s:hideItems){var d=new JsonObject();d.addProperty("kind","item");d.addProperty("id",BuiltInRegistries.ITEM.getKey(s.getItem()).toString());d.addProperty("recipeVisibleBefore",visibility.isIngredientVisible(VanillaTypes.ITEM_STACK,s,UidContext.Recipe));details.add(d);}
            // JEI rejects empty collections, including an already-applied cleanup.
            if(!hideFluids.isEmpty())visibility.hideIngredients(NeoForgeTypes.FLUID_STACK,hideFluids,List.of(UidContext.Ingredient));
            if(!hideItems.isEmpty())visibility.hideIngredients(VanillaTypes.ITEM_STACK,hideItems,List.of(UidContext.Ingredient));
            row.add("hidden",details);row.addProperty("status","APPLIED");row.addProperty("hiddenFluids",hideFluids.size());row.addProperty("hiddenBuckets",hideItems.size());hidden+=hideFluids.size()+hideItems.size();rows.add(row);
        }
        report.addProperty("registeredFluidsAfter",ingredients.getAllIngredients(NeoForgeTypes.FLUID_STACK).size());report.addProperty("registeredItemsAfter",ingredients.getAllItemStacks().size());
        report.addProperty("packetAdmissionReferences",admittedByPacket);
        report.addProperty("status","APPLIED_QUALIFIED_FAMILIES");report.addProperty("hiddenEntries",hidden);report.add("families",rows);
    }
}
