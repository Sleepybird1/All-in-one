package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.geology.GeologyConfig;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.levelgen.feature.FossilFeature;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructurePlaceSettings;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** Keeps the bone skeleton but skips the second (coal/diamond) fossil template. */
@Mixin(FossilFeature.class)
public abstract class GeologyFossilOverlayMixin {
    @Redirect(
            method = "place",
            at = @At(value = "INVOKE",
                    target = "Lnet/minecraft/world/level/levelgen/structure/templatesystem/StructureTemplate;"
                            + "placeInWorld(Lnet/minecraft/world/level/ServerLevelAccessor;"
                            + "Lnet/minecraft/core/BlockPos;Lnet/minecraft/core/BlockPos;"
                            + "Lnet/minecraft/world/level/levelgen/structure/templatesystem/StructurePlaceSettings;"
                            + "Lnet/minecraft/util/RandomSource;I)Z",
                    ordinal = 1),
            require = 1
    )
    private boolean industrialColonies$preserveBonesWithoutOreOverlay(
            StructureTemplate overlay,
            ServerLevelAccessor world,
            BlockPos origin,
            BlockPos pivot,
            StructurePlaceSettings settings,
            RandomSource random,
            int flags
    ) {
        if (GeologyConfig.suppressDefaultOres() && world.getLevel().dimension() == Level.OVERWORLD) {
            return true;
        }
        return overlay.placeInWorld(world, origin, pivot, settings, random, flags);
    }
}
