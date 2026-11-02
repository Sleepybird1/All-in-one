package dev.godpc.industrialcolonies.mixin;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.StructureManager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;
@Mixin(StructureManager.class)
public interface GeologyStructureManagerAccessor {
    @Accessor("level") LevelAccessor industrialColonies$level();
}
