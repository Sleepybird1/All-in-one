package dev.godpc.industrialcolonies;

import com.google.gson.*;
import com.mojang.logging.LogUtils;
import com.mojang.serialization.JsonOps;
import com.zizazr.kjsgen.integration.jei.KjsgenJeiPlugin;
import mezz.jei.api.constants.VanillaTypes;
import mezz.jei.api.ingredients.*;
import mezz.jei.api.runtime.*;
import net.minecraft.client.Minecraft;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.RegistryOps;
import net.minecraft.world.item.ItemStack;
import java.util.*;

/** Authoring catalog: full JEI identities plus omitted registry defaults; never changes JEI visibility/search. */
public final class KjsGenJeiItemCatalog {
    private KjsGenJeiItemCatalog() { }
    public static final class Choice {
        private final String key, id, label, components, search;
        private final ItemStack stack;
        private Choice(String id, String label, String components, ItemStack stack) {
            this.id=id; this.label=label; this.components=components; this.stack=stack.copyWithCount(1);
            this.key=KjsGenItemReference.key(id,components);
            this.search=(id+" "+label+" "+components).toLowerCase(Locale.ROOT);
        }
        public String key(){return key;} public String id(){return id;} public String label(){return label;}
        public String components(){return components;} public ItemStack stack(){return stack.copy();}
        public boolean matches(String query){return search.contains(query);}
    }
    public record Snapshot(long generation, List<Choice> items, Map<String,Choice> byKey) {
        public List<String> search(String query) {
            String text=query.toLowerCase(Locale.ROOT).trim();
            return items.stream().filter(choice -> choice.matches(text)).map(Choice::key).toList();
        }
    }
    private static IJeiRuntime runtime;
    private static HolderLookup.Provider registries;
    private static String language="";
    private static volatile long invalidation;
    private static long observed=-1, generation;
    private static Snapshot cached;
    private static final Map<String,Choice> decodedHistory = new LinkedHashMap<>(128,.75f,true) {
        @Override protected boolean removeEldestEntry(Map.Entry<String,Choice> entry){return size()>128;}
    };
    /** Called on the client thread; cached rendering performs no component serialization. */
    public static Optional<Snapshot> snapshot() {
        Minecraft client=Minecraft.getInstance();
        IJeiRuntime active=KjsgenJeiPlugin.runtime();
        HolderLookup.Provider access=client.level==null?null:client.level.registryAccess();
        String locale=client.getLanguageManager().getSelected();
        if(active!=runtime) {
            runtime=active; cached=null; observed=-1; decodedHistory.clear(); invalidation++;
            if(active!=null) observe(active);
        }
        if(access!=registries||!locale.equals(language)) {
            registries=access; language=locale; cached=null; decodedHistory.clear(); invalidation++;
        }
        if(active==null||access==null)return Optional.empty();
        if(cached!=null&&observed==invalidation)return Optional.of(cached);
        long revision=invalidation;
        var coverage=new KjsGenItemCatalogCoverage<Choice>(Choice::key);
        var manager=active.getIngredientManager(); var helper=manager.getIngredientHelper(VanillaTypes.ITEM_STACK);
        RegistryOps<JsonElement> ops=access.createSerializationContext(JsonOps.INSTANCE);
        for(ItemStack stack:manager.getAllItemStacks()) {
            if(stack==null||stack.isEmpty())continue;
            String id=BuiltInRegistries.ITEM.getKey(stack.getItem()).toString();
            // Hidden ingredients remain usable in this authoring tool; JEI itself stays unchanged.
            coverage.addJei(id,()->fromStack(stack,helper.getDisplayName(stack),ops));
        }
        for(var item:BuiltInRegistries.ITEM) {
            String id=BuiltInRegistries.ITEM.getKey(item).toString();
            coverage.addRegistered(id,()->{
                ItemStack stack=item.getDefaultInstance();
                if(stack.isEmpty())throw new IllegalArgumentException("Empty registered item");
                return fromStack(stack,stack.getHoverName().getString(),ops);
            });
        }
        Map<String,Choice> choices=coverage.choices();
        if(coverage.refused()>0)LogUtils.getLogger().warn("KubeJS Gen refused {} item variants that cannot round-trip their complete component patch",coverage.refused());
        List<Choice> ordered=choices.values().stream().sorted(Comparator.comparing(Choice::label,String.CASE_INSENSITIVE_ORDER).thenComparing(Choice::key)).toList();
        cached=new Snapshot(++generation,ordered,Map.copyOf(choices)); observed=revision; decodedHistory.clear();
        return Optional.of(cached);
    }
    private static void observe(IJeiRuntime owner) {
        owner.getIngredientManager().registerIngredientListener(new IIngredientManager.IIngredientListener() {
            @Override public <V> void onIngredientsAdded(IIngredientHelper<V> helper,Collection<ITypedIngredient<V>> items){if(runtime==owner)invalidation++;}
            @Override public <V> void onIngredientsRemoved(IIngredientHelper<V> helper,Collection<ITypedIngredient<V>> items){if(runtime==owner)invalidation++;}
        });
        owner.getJeiHelpers().getIngredientVisibility().registerListener(new IIngredientVisibility.IListener() {
            @Override public <V> void onIngredientVisibilityChanged(ITypedIngredient<V> item,boolean visible){if(runtime==owner)invalidation++;}
        });
    }
    private static Choice fromStack(ItemStack original,String label,RegistryOps<JsonElement> ops) {
        ItemStack stack=original.copyWithCount(1);
        JsonObject json=ItemStack.CODEC.encodeStart(ops,stack).getOrThrow().getAsJsonObject();
        ItemStack restored=ItemStack.CODEC.parse(ops,json).getOrThrow();
        if(!ItemStack.isSameItemSameComponents(stack,restored)||!stack.getComponentsPatch().equals(restored.getComponentsPatch()))
            throw new IllegalArgumentException("Incomplete component codec");
        String id=json.get("id").getAsString();
        String components=json.has("components")?KjsGenItemReference.canonical(json.get("components")):"";
        return new Choice(id,label,components,stack);
    }
    /** Resolve persisted global quick-picks and an existing card even if it is currently hidden in JEI. */
    public static Optional<Choice> resolve(String key) {
        var snapshot=snapshot();
        Choice current=snapshot.map(value -> value.byKey().get(key)).orElse(null); if(current!=null)return Optional.of(current);
        if(!KjsGenItemReference.isReference(key))return Optional.empty();
        if(registries==null)return Optional.empty();
        Choice previous=decodedHistory.get(key); if(previous!=null)return Optional.of(previous);
        var encoded=KjsGenItemReference.decode(key);if(encoded.isEmpty())return Optional.empty();
        try {
            JsonObject item=new JsonObject();item.addProperty("id",encoded.get().id());item.addProperty("count",1);
            item.add("components",JsonParser.parseString(encoded.get().components()));
            var ops=registries.createSerializationContext(JsonOps.INSTANCE);
            ItemStack stack=ItemStack.CODEC.parse(ops,item).getOrThrow();
            String name=runtime==null?stack.getHoverName().getString():runtime.getIngredientManager().getIngredientHelper(VanillaTypes.ITEM_STACK).getDisplayName(stack);
            Choice choice=fromStack(stack,name,ops);
            if(!choice.key().equals(key))return Optional.empty();
            decodedHistory.put(key,choice);return Optional.of(choice);
        } catch(RuntimeException invalid){return Optional.empty();}
    }
    public static boolean visibleQuickPick(String key) {
        var current=snapshot();
        if(current.isPresent())return current.get().byKey().containsKey(key);
        return !KjsGenItemReference.isReference(key)||resolve(key).isPresent();
    }
}
