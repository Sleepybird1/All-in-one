package dev.godpc.industrialcolonies;

import com.zizazr.kjsgen.integration.jei.KjsgenJeiPlugin;
import mezz.jei.api.ingredients.*;
import mezz.jei.api.neoforge.NeoForgeTypes;
import mezz.jei.api.runtime.*;
import net.minecraft.client.Minecraft;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.neoforged.neoforge.fluids.FluidStack;
import java.util.*;

/** Shared JEI source for representable FLUID choices; saved/hidden fluid resolution stays registry based. */
public final class KjsGenJeiFluidCatalog {
    private KjsGenJeiFluidCatalog() { }
    public record Choice(String id,String label) {
        public Choice {
            if(id==null||!id.matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))throw new IllegalArgumentException("Actual fluid ID required");
            Objects.requireNonNull(label);
        }
    }
    public record Snapshot(long generation,List<Choice> fluids,Map<String,String> labels) {
        public static Snapshot index(long generation,List<Choice> rows) {
            Map<String,Choice> unique=new LinkedHashMap<>();
            rows.forEach(row -> unique.putIfAbsent(row.id(),row));
            List<Choice> sorted=unique.values().stream().sorted(Comparator.comparing(Choice::label,String.CASE_INSENSITIVE_ORDER).thenComparing(Choice::id)).toList();
            Map<String,String> names=new HashMap<>();sorted.forEach(row -> names.put(row.id(),row.label()));
            return new Snapshot(generation,sorted,Map.copyOf(names));
        }
        public List<String> search(String query) {
            String text=query.toLowerCase(Locale.ROOT).trim();
            return fluids.stream().filter(row -> row.id().contains(text)||row.label().toLowerCase(Locale.ROOT).contains(text)).map(Choice::id).toList();
        }
    }
    private static IJeiRuntime runtime;
    private static HolderLookup.Provider registries;
    private static String language="";
    private static volatile long invalidation;
    private static long observed=-1,generation;
    private static Snapshot cached;

    /** Lazy client-thread snapshot; no JEI filter/overlay query is read or changed. */
    public static Optional<Snapshot> snapshot() {
        Minecraft client=Minecraft.getInstance(); IJeiRuntime active=KjsgenJeiPlugin.runtime();
        HolderLookup.Provider access=client.level==null?null:client.level.registryAccess();
        String locale=client.getLanguageManager().getSelected();
        if(active!=runtime) {
            runtime=active;cached=null;observed=-1;invalidation++;
            if(active!=null)observe(active);
        }
        if(access!=registries||!locale.equals(language)) {registries=access;language=locale;cached=null;invalidation++;}
        if(active==null||access==null)return Optional.empty();
        if(cached!=null&&observed==invalidation)return Optional.of(cached);
        long revision=invalidation;
        var manager=active.getIngredientManager(); var helper=manager.getIngredientHelper(NeoForgeTypes.FLUID_STACK);
        var visibility=active.getJeiHelpers().getIngredientVisibility(); List<Choice> rows=new ArrayList<>();
        for(FluidStack original:manager.getAllIngredients(NeoForgeTypes.FLUID_STACK)) {
            // Native KJS Gen FLUID slots save only an ID and mB: never flatten potion/component variants.
            if(original==null||original.isEmpty()||!original.isComponentsPatchEmpty()
                ||!visibility.isIngredientVisible(NeoForgeTypes.FLUID_STACK,original))continue;
            FluidStack copy=original.copyWithAmount(1000);
            var id=BuiltInRegistries.FLUID.getKey(copy.getFluid());
            if(id!=null)rows.add(new Choice(id.toString(),helper.getDisplayName(copy)));
        }
        cached=Snapshot.index(++generation,rows);observed=revision;return Optional.of(cached);
    }
    private static void observe(IJeiRuntime owner) {
        owner.getIngredientManager().registerIngredientListener(new IIngredientManager.IIngredientListener() {
            @Override public <V> void onIngredientsAdded(IIngredientHelper<V> helper,Collection<ITypedIngredient<V>> items){if(runtime==owner)invalidation++;}
            @Override public <V> void onIngredientsRemoved(IIngredientHelper<V> helper,Collection<ITypedIngredient<V>> items){if(runtime==owner)invalidation++;}
        });
        owner.getJeiHelpers().getIngredientVisibility().registerListener(new IIngredientVisibility.IListener() {
            @Override public <V> void onIngredientVisibilityChanged(ITypedIngredient<V> ingredient,boolean visible){if(runtime==owner)invalidation++;}
        });
    }
    public static Optional<String> label(String actualFluidId) {
        return snapshot().map(snapshot -> snapshot.labels().get(actualFluidId));
    }
}
