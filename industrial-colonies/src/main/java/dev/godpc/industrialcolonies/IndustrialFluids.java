package dev.godpc.industrialcolonies;

import java.util.function.Consumer;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.level.material.FlowingFluid;
import net.minecraft.world.level.material.Fluid;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.extensions.common.IClientFluidTypeExtensions;
import net.neoforged.neoforge.common.SoundActions;
import net.neoforged.neoforge.fluids.BaseFlowingFluid;
import net.neoforged.neoforge.fluids.FluidType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

/** Source-owned fluid extracted only by a commissioned gas-giant station. */
public final class IndustrialFluids {
    private static final DeferredRegister<FluidType> FLUID_TYPES =
            DeferredRegister.create(NeoForgeRegistries.FLUID_TYPES, IndustrialColonies.MOD_ID);
    private static final DeferredRegister<Fluid> FLUIDS =
            DeferredRegister.create(BuiltInRegistries.FLUID, IndustrialColonies.MOD_ID);

    public static final DeferredHolder<FluidType, FluidType> GAS_GIANT_CONDENSATE_TYPE =
            FLUID_TYPES.register("gas_giant_condensate", () -> new FluidType(
                    FluidType.Properties.create()
                            .descriptionId("fluid.industrial_colonies.gas_giant_condensate")
                            .density(720)
                            .temperature(90)
                            .viscosity(1_600)
                            .canConvertToSource(false)
                            .rarity(Rarity.RARE)
                            .sound(SoundActions.BUCKET_FILL, SoundEvents.BUCKET_FILL)
                            .sound(SoundActions.BUCKET_EMPTY, SoundEvents.BUCKET_EMPTY)) {
                @Override
                public void initializeClient(Consumer<IClientFluidTypeExtensions> consumer) {
                    consumer.accept(new IClientFluidTypeExtensions() {
                        private static final ResourceLocation STILL =
                                ResourceLocation.withDefaultNamespace("block/water_still");
                        private static final ResourceLocation FLOWING =
                                ResourceLocation.withDefaultNamespace("block/water_flow");

                        @Override
                        public ResourceLocation getStillTexture() {
                            return STILL;
                        }

                        @Override
                        public ResourceLocation getFlowingTexture() {
                            return FLOWING;
                        }

                        @Override
                        public int getTintColor() {
                            return 0xFF7656E8;
                        }
                    });
                }
            });

    public static final DeferredHolder<Fluid, FlowingFluid> GAS_GIANT_CONDENSATE =
            FLUIDS.register(
                    "gas_giant_condensate",
                    () -> new BaseFlowingFluid.Source(properties()));
    public static final DeferredHolder<Fluid, FlowingFluid> FLOWING_GAS_GIANT_CONDENSATE =
            FLUIDS.register(
                    "flowing_gas_giant_condensate",
                    () -> new BaseFlowingFluid.Flowing(properties()));

    private IndustrialFluids() {
    }

    private static BaseFlowingFluid.Properties properties() {
        return new BaseFlowingFluid.Properties(
                GAS_GIANT_CONDENSATE_TYPE,
                GAS_GIANT_CONDENSATE,
                FLOWING_GAS_GIANT_CONDENSATE)
                .bucket(IndustrialItems.GAS_GIANT_CONDENSATE_BUCKET)
                .block(IndustrialBlocks.GAS_GIANT_CONDENSATE)
                .slopeFindDistance(2)
                .levelDecreasePerBlock(2)
                .tickRate(10)
                .explosionResistance(100.0F);
    }

    public static void register(IEventBus modEventBus) {
        FLUID_TYPES.register(modEventBus);
        FLUIDS.register(modEventBus);
    }
}
