package dev.godpc.industrialcolonies.processing;

import com.google.gson.JsonParser;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.crafting.*;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.server.ServerLifecycleHooks;

/** Opt-in staged bridge. A server recipe snapshot, never a saved flag, admits production. */
public final class PotionIdentityRuntime {
    private static volatile java.util.function.Supplier<RecipeManager> clientManager = () -> null;
    private static final Map<RecipeManager,Map<ResourceLocation,RecipeHolder<?>>> READY =
            Collections.synchronizedMap(new WeakHashMap<>());

    public static boolean enabled() { return Boolean.getBoolean("industrial_colonies.canonicalPotions"); }
    public static List<PotionRecipeNormalizer.Rule> rules() {
        try (var stream=PotionIdentityRuntime.class.getResourceAsStream("/industrial_colonies/potion-consumer-rules.json")) {
            if (stream==null) throw new IllegalStateException("Missing pinned potion consumers");
            var list=new ArrayList<PotionRecipeNormalizer.Rule>();
            var ids=new HashSet<ResourceLocation>();
            for (var e:JsonParser.parseReader(new InputStreamReader(stream,StandardCharsets.UTF_8)).getAsJsonArray()) {
                var row=e.getAsJsonObject();var id=ResourceLocation.parse(row.get("id").getAsString());
                String before=row.get("beforeSHA256").getAsString(), after=row.get("afterSHA256").getAsString();
                if (!ids.add(id)||!before.matches("[0-9a-f]{64}")||!after.matches("[0-9a-f]{64}"))
                    throw new IllegalStateException("Invalid pinned potion consumer");
                list.add(new PotionRecipeNormalizer.Rule(id,before,after));
            }
            if(list.size()!=6) throw new IllegalStateException("Incomplete pinned potion consumer set");
            return List.copyOf(list);
        } catch (Exception e) { throw new IllegalStateException("Cannot load pinned potion consumers",e); }
    }
    public static void invalidate(RecipeManager manager) { READY.remove(manager); }
    /** The client supplies a thread- and connection-bound lookup; common code never loads client classes. */
    public static void bindClient(java.util.function.Supplier<RecipeManager> current) { clientManager = current; }
    public static boolean admitClient(RecipeManager manager, net.minecraft.core.HolderLookup.Provider registries) {
        invalidate(manager);
        if (!enabled()) return false;
        var rules = rules();
        var snapshot = new LinkedHashMap<ResourceLocation,RecipeHolder<?>>();
        int present = 0;
        for (var rule : rules) {
            var holder = manager.byKey(rule.id()).orElse(null);
            if (holder == null) continue;
            String hash = clientFingerprint(holder, registries);
            if (!hash.equals(rule.afterSHA256())) return false;
            snapshot.put(rule.id(), holder); present++;
        }
        if (present == 0) return false;
        admit(manager, snapshot, rules);
        return true;
    }
    /** IE's wire codec expands this one tag; qualify every member before restoring its pinned form. */
    public static String clientFingerprint(RecipeHolder<?> holder, net.minecraft.core.HolderLookup.Provider registries) {
        var ops=net.minecraft.resources.RegistryOps.create(com.mojang.serialization.JsonOps.INSTANCE,registries);
        var json=Recipe.CODEC.encodeStart(ops,holder.value()).getOrThrow().getAsJsonObject().deepCopy();
        if(holder.id().toString().equals("immersiveengineering:refinery/high_power_biodiesel")) {
            var input=json.getAsJsonObject("input0");
            if(input!=null&&input.has("children")) {
                if(!input.keySet().equals(Set.of("children","type","amount"))
                        ||!input.get("type").getAsString().equals("neoforge:compound"))
                    throw new IllegalArgumentException("Unknown refinery wire ingredient");
                var actual=new HashSet<ResourceLocation>();
                for(var child:input.getAsJsonArray("children")) {
                    var object=child.getAsJsonObject();
                    if(!object.keySet().equals(Set.of("fluid"))||!actual.add(ResourceLocation.parse(object.get("fluid").getAsString())))
                        throw new IllegalArgumentException("Non-exact refinery wire membership");
                }
                var tag=net.minecraft.tags.TagKey.create(net.minecraft.core.registries.Registries.FLUID,ResourceLocation.parse("c:biodiesel"));
                var expected=new HashSet<ResourceLocation>();
                registries.lookupOrThrow(net.minecraft.core.registries.Registries.FLUID).getOrThrow(tag)
                        .forEach(fluid->expected.add(fluid.unwrapKey().orElseThrow().location()));
                if(expected.isEmpty()||!actual.equals(expected)) throw new IllegalArgumentException("Changed refinery wire members");
                var restored=new com.google.gson.JsonObject();restored.addProperty("tag","c:biodiesel");
                restored.add("amount",input.get("amount"));json.add("input0",restored);
            }
        }
        return EffectiveFluidNormalizer.fingerprint(json);
    }
    public static void admit(RecipeManager manager, Map<ResourceLocation,RecipeHolder<?>> applied,
                             List<PotionRecipeNormalizer.Rule> rules) {
        var snapshot=new LinkedHashMap<ResourceLocation,RecipeHolder<?>>();
        for(var rule:rules) snapshot.put(rule.id(),applied.get(rule.id()));
        READY.put(manager,Collections.unmodifiableMap(snapshot));
    }
    public static boolean ready(RecipeManager manager) {
        if(!enabled()) return false;
        var snapshot=READY.get(manager);
        if(snapshot==null) return false;
        for(var entry:snapshot.entrySet())
            if(manager.byKey(entry.getKey()).orElse(null)!=entry.getValue()) { invalidate(manager);return false; }
        return true;
    }
    public static FluidStack produced(FluidStack original) {
        var server=ServerLifecycleHooks.getCurrentServer();
        var manager=server!=null&&server.isSameThread()?server.getRecipeManager():clientManager.get();
        if(manager==null||!ready(manager)) return original;
        var projection=PotionCanonicalizer.project(original);
        return projection.status().equals("CANONICAL")?projection.fluid():original;
    }

    /** Batch-local query translation; never changes tank contents or external capabilities. */
    public static FluidStack storedQuery(net.neoforged.neoforge.fluids.capability.IFluidHandler handler,
                                        FluidStack requested, int required) {
        var server=ServerLifecycleHooks.getCurrentServer();
        if(required<=0||server==null||!server.isSameThread()||!ready(server.getRecipeManager())) return requested;
        var target=PotionCanonicalizer.project(requested);
        if(!target.status().equals("CANONICAL")) return requested;
        for(int i=0;i<handler.getTanks();i++) {
            var stored=handler.getFluidInTank(i);
            if(stored.getAmount()<required) continue;
            var candidate=PotionCanonicalizer.project(stored);
            if(candidate.status().equals("CANONICAL")
                    &&FluidStack.isSameFluidSameComponents(candidate.fluid(),target.fluid()))
                return stored.copyWithAmount(requested.getAmount());
        }
        return requested;
    }
}
