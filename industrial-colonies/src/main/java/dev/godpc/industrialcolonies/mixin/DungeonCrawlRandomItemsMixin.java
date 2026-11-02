package dev.godpc.industrialcolonies.mixin;

import net.minecraft.core.RegistryAccess;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Keeps Dungeon Crawl's staged equipment finds without granting pristine tools.
 *
 * <p>Dungeon Crawl does not name most generated tools in its chest tables. Its
 * {@code dungeoncrawl:random_item} loot function selects from separate staged
 * treasure lists and returns a fresh, undamaged stack. Damage that stack at the
 * source so every chest using the function follows the same exploration-tool
 * contract. Deeper floors retain more durability and therefore remain more
 * rewarding.</p>
 */
@Pseudo
@Mixin(targets = "xiroc.dungeoncrawl.dungeon.treasure.RandomItems", remap = false)
public abstract class DungeonCrawlRandomItemsMixin {
    @Inject(method = "generate", at = @At("RETURN"), cancellable = true, remap = false)
    private static void industrialColonies$wearGeneratedDungeonEquipment(
            RandomSource random,
            int lootLevel,
            RegistryAccess registryAccess,
            CallbackInfoReturnable<ItemStack> callback
    ) {
        ItemStack stack = callback.getReturnValue();
        if (stack == null || stack.isEmpty() || !stack.isDamageableItem()) {
            return;
        }

        int boundedLevel = Math.max(0, Math.min(5, lootLevel));
        double minimumRemaining = 0.10D + (0.04D * boundedLevel);
        double maximumRemaining = 0.20D + (0.05D * boundedLevel);
        double remainingFraction = minimumRemaining
                + random.nextDouble() * (maximumRemaining - minimumRemaining);
        int remainingUses = Math.max(1, (int) Math.round(stack.getMaxDamage() * remainingFraction));
        stack.setDamageValue(Math.max(0, stack.getMaxDamage() - remainingUses));
        callback.setReturnValue(stack);
    }
}
