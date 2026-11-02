package dev.godpc.industrialcolonies.processing;

import com.simibubi.create.AllBlocks;
import com.simibubi.create.content.processing.recipe.*;
import com.simibubi.create.content.processing.sequenced.IAssemblyRecipe;
import com.simibubi.create.compat.jei.category.sequencedAssembly.SequencedAssemblySubCategory;
import dev.godpc.industrialcolonies.TieredRecipeTypeInfo;
import dev.godpc.industrialcolonies.TieredRecipeCatalog;
import dev.godpc.industrialcolonies.TieredRecipeBindings;
import dev.godpc.industrialcolonies.TieredRecipeSerializer;
import dev.godpc.industrialcolonies.client.jei.ExtendedAssemblyCategory;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.crafting.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ItemLike;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredRegister;
import java.util.*;
import java.util.function.Supplier;

/** Codec-backed nested recipes; these are assembly stages, not furnace recipe replacements. */
public final class AssemblyFanRecipes {
    private static final DeferredRegister<RecipeType<?>> TYPES = DeferredRegister.create(Registries.RECIPE_TYPE, "industrial_colonies");
    private static final DeferredRegister<RecipeSerializer<?>> SERIALIZERS = DeferredRegister.create(Registries.RECIPE_SERIALIZER, "industrial_colonies");
    private static final Map<String, TieredRecipeTypeInfo> INFO = new HashMap<>();
    public static void register(IEventBus bus) {
        for (String mode : List.of("smoking", "blasting", "splashing", "haunting")) {
            String name = "assembly_" + mode;
            var id = ResourceLocation.fromNamespaceAndPath("industrial_colonies", name);
            var type = TYPES.register(name, () -> RecipeType.simple(id));
            var serializer = SERIALIZERS.register(name, () -> new StandardProcessingRecipe.Serializer<>(p -> new FanRecipe(mode, p)));
            INFO.put(mode, new TieredRecipeTypeInfo(id, type::get, serializer::get));
            var family=TieredRecipeCatalog.load().recipeFamilies().stream()
                    .filter(f -> f.id().equals(mode.equals("haunting")?"haunting":"splashing")).findFirst().orElseThrow();
            for(var machine:family.machines())new BoundRegistration(mode,family,machine,serializer::get).register();
        }
        TYPES.register(bus); SERIALIZERS.register(bus);
    }
    private static final class BoundRegistration {
        final String mode; final TieredRecipeCatalog.RecipeFamily family; final TieredRecipeCatalog.Machine machine;
        final Supplier<RecipeSerializer<?>> delegate;
        net.neoforged.neoforge.registries.DeferredHolder<RecipeType<?>,RecipeType<?>> type;
        net.neoforged.neoforge.registries.DeferredHolder<RecipeSerializer<?>,RecipeSerializer<?>> serializer;
        TieredRecipeTypeInfo info;
        BoundRegistration(String mode,TieredRecipeCatalog.RecipeFamily family,TieredRecipeCatalog.Machine machine,Supplier<RecipeSerializer<?>> delegate) {
            this.mode=mode;this.family=family;this.machine=machine;this.delegate=delegate;
        }
        void register() {
            String name="assembly_"+mode+"_"+machine.id();
            var id=ResourceLocation.fromNamespaceAndPath("industrial_colonies",name);
            type=TYPES.register(name,()->RecipeType.simple(id));
            serializer=SERIALIZERS.register(name,()->new TieredRecipeSerializer(delegate,this::binding));
            info=new TieredRecipeTypeInfo(id,type::get,serializer::get);
        }
        TieredRecipeBindings.Binding binding() {return new TieredRecipeBindings.Binding(type.get(),serializer.get(),info,null,family,machine);}
    }
    public static final class FanRecipe extends StandardProcessingRecipe<SingleRecipeInput> implements IAssemblyRecipe {
        public final String mode;
        public FanRecipe(String mode, ProcessingRecipeParams params) { super(INFO.get(mode), params); this.mode = mode; }
        @Override public boolean matches(SingleRecipeInput input, Level level) { return !input.isEmpty() && ingredients.getFirst().test(input.item()); }
        @Override protected int getMaxInputCount() { return 1; }
        @Override protected int getMaxOutputCount() { return 1; }
        @Override protected boolean canSpecifyDuration() { return true; }
        @Override public Component getDescriptionForAssembly() { return Component.literal("Fan " + mode); }
        @Override public void addRequiredMachines(Set<ItemLike> machines) {
            var binding=TieredRecipeBindings.get(this);
            if(binding!=null && binding.machine()!=null)machines.add(net.minecraft.core.registries.BuiltInRegistries.ITEM.get(ResourceLocation.parse(binding.machine().item())));
            else machines.add(AllBlocks.ENCASED_FAN.get());
        }
        @Override public void addAssemblyIngredients(List<Ingredient> ingredients) {}
        @Override public Supplier<Supplier<SequencedAssemblySubCategory>> getJEISubCategory() { return () -> ExtendedAssemblyCategory::new; }
    }
}
