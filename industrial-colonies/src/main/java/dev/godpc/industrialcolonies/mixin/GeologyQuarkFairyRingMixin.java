package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.geology.GeologyConfig;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** Quark bypasses placed features when it hides diamonds under fairy rings. */
@Pseudo
@Mixin(targets = "org.violetmoon.quark.content.world.gen.FairyRingGenerator", remap = false)
public abstract class GeologyQuarkFairyRingMixin {
    @Redirect(
            method = "spawnFairyRing",
            at = @At(value = "INVOKE",
                    target = "Lnet/minecraft/world/level/WorldGenLevel;"
                            + "setBlock(Lnet/minecraft/core/BlockPos;"
                            + "Lnet/minecraft/world/level/block/state/BlockState;I)Z",
                    remap = false),
            remap = false,
            require = 1
    )
    private static boolean industrialColonies$keepFlowersAndEmeralds(
            WorldGenLevel world, BlockPos pos, BlockState state, int flags
    ) {
        if (GeologyConfig.suppressDefaultOres()
                && world.getLevel().dimension() == Level.OVERWORLD
                && (state.is(Blocks.DIAMOND_ORE) || state.is(Blocks.DEEPSLATE_DIAMOND_ORE))) {
            // Leave existing host stone untouched; don't turn a rejected diamond roll into more emerald.
            return false;
        }
        return world.setBlock(pos, state, flags);
    }
}
