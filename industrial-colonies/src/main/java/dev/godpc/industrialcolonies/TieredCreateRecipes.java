package dev.godpc.industrialcolonies;

import com.simibubi.create.AllRecipeTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.RecipeType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.ArrayList;
import java.util.List;

/**
 * Registers hidden runtime identities for exact-machine recipes while retaining
 * every old tier/family identifier so existing KubeJS exports and worlds load.
 * The in-game editor exposes processes and machines, not this compatibility
 * matrix.
 */
public final class TieredCreateRecipes {
    private static final DeferredRegister<RecipeSerializer<?>> SERIALIZERS =
            DeferredRegister.create(Registries.RECIPE_SERIALIZER, IndustrialColonies.MOD_ID);
    private static final DeferredRegister<RecipeType<?>> TYPES =
            DeferredRegister.create(Registries.RECIPE_TYPE, IndustrialColonies.MOD_ID);
    private static final TieredRecipeCatalog CATALOG = TieredRecipeCatalog.load();
    private static final List<Registration> REGISTRATIONS = new ArrayList<>();
    private static boolean initialized;

    private TieredCreateRecipes() {
    }

    public static void register(IEventBus modEventBus) {
        if (initialized) {
            return;
        }
        initialized = true;

        // A native Create recipe remains universal for compatibility. Recipes
        // explicitly authored for the base machine use base_<family>, allowing
        // them to reject every Encased variant just like any other selection.
        for (TieredRecipeCatalog.RecipeFamily family : CATALOG.recipeFamilies()) {
            if (family.supportsMachineSelection()) {
                register("base_" + family.id(), null, family, family.baseMachine());
            }
        }

        // Preserve the original 10 × 17 identifiers. Valid pairs bind to the
        // exact Encased block; impossible old pairs alias to the base machine.
        for (TieredRecipeCatalog.Tier tier : CATALOG.tiers()) {
            for (TieredRecipeCatalog.RecipeFamily family : CATALOG.recipeFamilies()) {
                register(tier.id() + "_" + family.id(), tier, family, family.machineForLegacyTier(tier));
            }
        }

        TYPES.register(modEventBus);
        SERIALIZERS.register(modEventBus);
    }

    private static void register(
            String path,
            TieredRecipeCatalog.Tier tier,
            TieredRecipeCatalog.RecipeFamily family,
            TieredRecipeCatalog.Machine machine
    ) {
        ResourceLocation id = ResourceLocation.fromNamespaceAndPath(IndustrialColonies.MOD_ID, path);
        Registration registration = new Registration(id, tier, family, machine);

        registration.type = TYPES.register(path, () -> RecipeType.simple(id));
        registration.serializer = SERIALIZERS.register(path, () -> new TieredRecipeSerializer(
                () -> family.baseType().getSerializer(), registration::binding));
        REGISTRATIONS.add(registration);
    }

    public static int environmentCount() {
        return REGISTRATIONS.size();
    }

    public static List<ResourceLocation> ids() {
        return REGISTRATIONS.stream().map(registration -> registration.id).toList();
    }

    /** Runtime recipe lookup types for one native Create family, in catalog order. */
    public static List<RecipeType<?>> typesFor(AllRecipeTypes baseType) {
        return REGISTRATIONS.stream()
                .filter(registration -> registration.family.baseType() == baseType)
                .<RecipeType<?>>map(registration -> registration.type.get())
                .toList();
    }

    private static final class Registration {
        private final ResourceLocation id;
        private final TieredRecipeCatalog.Tier tier;
        private final TieredRecipeCatalog.RecipeFamily family;
        private final TieredRecipeCatalog.Machine machine;
        private DeferredHolder<RecipeType<?>, RecipeType<?>> type;
        private DeferredHolder<RecipeSerializer<?>, RecipeSerializer<?>> serializer;
        private TieredRecipeTypeInfo typeInfo;

        private Registration(
                ResourceLocation id,
                TieredRecipeCatalog.Tier tier,
                TieredRecipeCatalog.RecipeFamily family,
                TieredRecipeCatalog.Machine machine
        ) {
            this.id = id;
            this.tier = tier;
            this.family = family;
            this.machine = machine;
        }

        private TieredRecipeBindings.Binding binding() {
            if (typeInfo == null) {
                typeInfo = new TieredRecipeTypeInfo(id, type::get, serializer::get);
            }
            return new TieredRecipeBindings.Binding(type.get(), serializer.get(), typeInfo, tier, family, machine);
        }
    }
}
