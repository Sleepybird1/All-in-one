package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.geology.*;
import net.minecraft.core.RegistryAccess;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.WorldGenRegion;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.chunk.*;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplateManager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Registers dimension identity before starts, including dimensions with no usable level-load event. */
@Mixin(ChunkGenerator.class)
public abstract class GeologyStructureContextMixin {
    @Inject(method="createStructures",at=@At("HEAD"))
    private void industrialColonies$registerGeologyContext(RegistryAccess registries,ChunkGeneratorStructureState state,
            StructureManager structures,ChunkAccess chunk,StructureTemplateManager templates,CallbackInfo ci){
        if(!GeologyConfig.enabled()||!MassiveDeposits.enabled(GeologyConfig.get()))return;
        LevelAccessor accessor=((GeologyStructureManagerAccessor)structures).industrialColonies$level();
        ServerLevel level=accessor instanceof ServerLevel server?server:accessor instanceof WorldGenRegion region?region.getLevel():null;
        if(level==null)throw new IllegalStateException("Massive geology requires a server structure-generation context");
        GeologyWorld.of(level);
    }
}
