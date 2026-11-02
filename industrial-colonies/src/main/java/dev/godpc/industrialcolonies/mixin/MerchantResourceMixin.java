package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.ResourceCanonicalization;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.trading.ItemCost;
import net.minecraft.world.item.trading.MerchantOffer;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import java.util.Optional;

/** Applies to generated and loaded offers; preserves prices, components, demand and stock fields. */
@Mixin(MerchantOffer.class)
public abstract class MerchantResourceMixin {
    @Shadow @Final @Mutable private ItemCost baseCostA;
    @Shadow @Final @Mutable private Optional<ItemCost> costB;
    @Shadow @Final @Mutable private ItemStack result;
    @Inject(method="<init>",at=@At("RETURN"))
    private void industrialColonies$canonicalResources(CallbackInfo ci) {
        if(ResourceCanonicalization.retired(result) || ResourceCanonicalization.blockedTradeResult(result) || ResourceCanonicalization.retired(baseCostA.itemStack())
                || costB.map(c->ResourceCanonicalization.retired(c.itemStack())).orElse(false)) {
            result=ItemStack.EMPTY; // Inert retired offer; never charge for a substitute reward.
            return;
        }
        baseCostA=ResourceCanonicalization.canonical(baseCostA);
        costB=costB.map(ResourceCanonicalization::canonical);
        result=ResourceCanonicalization.canonical(result);
    }
}
