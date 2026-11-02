package dev.godpc.industrialcolonies.processing;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import dev.godpc.industrialcolonies.IndustrialColonies;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Consumer;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.material.Fluid;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.extensions.common.IClientFluidTypeExtensions;
import net.neoforged.neoforge.fluids.BaseFlowingFluid;
import net.neoforged.neoforge.fluids.FluidType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

/** Only missing process intermediates. No replacement geological blocks or texture edits. */
public final class ProcessingContent {
    private static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(IndustrialColonies.MOD_ID);
    private static final DeferredRegister<Fluid> FLUIDS = DeferredRegister.create(Registries.FLUID, IndustrialColonies.MOD_ID);
    private static final DeferredRegister<FluidType> TYPES = DeferredRegister.create(NeoForgeRegistries.FLUID_TYPES, IndustrialColonies.MOD_ID);
    private static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, IndustrialColonies.MOD_ID);
    private static final Map<String, DeferredItem<Item>> CONTENT = new LinkedHashMap<>();
    private static final JsonObject CATALOG = readCatalog();

    static {
        for (String name : CATALOG.getAsJsonObject("items").keySet()) {
            CONTENT.put(name, ITEMS.registerSimpleItem(name));
        }
        CATALOG.getAsJsonObject("fluids").entrySet().forEach(entry -> {
            String name = entry.getKey();
            int tint = (int) entry.getValue().getAsJsonObject().get("color").getAsLong();
            DeferredHolder<FluidType, FluidType> type = TYPES.register(name, () -> new FluidType(
                    FluidType.Properties.create().descriptionId("fluid.industrial_colonies." + name)
                            .canConvertToSource(false).density(1200).viscosity(1500)) {
                @Override
                public void initializeClient(Consumer<IClientFluidTypeExtensions> consumer) {
                    consumer.accept(new IClientFluidTypeExtensions() {
                        @Override public ResourceLocation getStillTexture() { return ResourceLocation.withDefaultNamespace("block/water_still"); }
                        @Override public ResourceLocation getFlowingTexture() { return ResourceLocation.withDefaultNamespace("block/water_flow"); }
                        @Override public int getTintColor() { return tint; }
                    });
                }
            });
            // Tank-only intermediates: no new world fluids, buckets or infinite sources.
            @SuppressWarnings("unchecked")
            DeferredHolder<Fluid, ? extends Fluid>[] pair = new DeferredHolder[2];
            pair[0] = FLUIDS.register(name, () -> new BaseFlowingFluid.Source(new BaseFlowingFluid.Properties(type, pair[0], pair[1])));
            pair[1] = FLUIDS.register("flowing_" + name, () -> new BaseFlowingFluid.Flowing(new BaseFlowingFluid.Properties(type, pair[0], pair[1])));
        });
        TABS.register("material_processing", () -> CreativeModeTab.builder()
                .title(Component.literal("Industrial Colonies — Material Processing"))
                .icon(() -> new ItemStack(CONTENT.get("roasted_cinnabar").get()))
                .displayItems((parameters, output) -> CONTENT.values().forEach(item -> output.accept(item.get())))
                .build());
    }

    private ProcessingContent() {}

    private static JsonObject readCatalog() {
        var stream = ProcessingContent.class.getResourceAsStream("/data/industrial_colonies/processing/content.json");
        if (stream == null) throw new IllegalStateException("Missing generated material-processing catalog");
        try (var reader = new InputStreamReader(stream, StandardCharsets.UTF_8)) {
            return new Gson().fromJson(reader, JsonObject.class);
        } catch (Exception e) {
            throw new IllegalStateException("Invalid material-processing catalog", e);
        }
    }

    public static void register(IEventBus bus) {
        ITEMS.register(bus); TYPES.register(bus); FLUIDS.register(bus); TABS.register(bus);
    }
}
