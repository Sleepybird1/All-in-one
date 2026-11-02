package dev.godpc.industrialcolonies.mixin;

import it.zerono.mods.extremereactors.gamecontent.multiblock.reactor.part.ReactorSolidAccessPortEntity;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Keeps Mekanism plutonium pellets in the reinforced Extreme Reactors tier.
 */
@Mixin(value = ReactorSolidAccessPortEntity.class, remap = false)
public abstract class ReactorSolidAccessPortEntityMixin {
    private static final ResourceLocation PLUTONIUM_PELLET = ResourceLocation.fromNamespaceAndPath(
            "mekanism", "pellet_plutonium");
    private static final ResourceLocation BASIC_SOLID_ACCESS_PORT = ResourceLocation.fromNamespaceAndPath(
            "bigreactors", "basic_reactorsolidaccessport");

    @Inject(
            method = "consumeFuelSource(Lnet/minecraft/world/item/ItemStack;)Lnet/minecraft/world/item/ItemStack;",
            at = @At("HEAD"),
            cancellable = true,
            remap = false
    )
    private void industrialColonies$requireReinforcedPortForPlutonium(
            ItemStack requestedFuel, CallbackInfoReturnable<ItemStack> callback) {
        if (requestedFuel.isEmpty()
                || !PLUTONIUM_PELLET.equals(BuiltInRegistries.ITEM.getKey(requestedFuel.getItem()))) {
            return;
        }

        ReactorSolidAccessPortEntity accessPort = (ReactorSolidAccessPortEntity) (Object) this;
        BlockState accessPortState = accessPort.getBlockState();
        if (BASIC_SOLID_ACCESS_PORT.equals(BuiltInRegistries.BLOCK.getKey(accessPortState.getBlock()))) {
            callback.setReturnValue(ItemStack.EMPTY);
        }
    }
}
