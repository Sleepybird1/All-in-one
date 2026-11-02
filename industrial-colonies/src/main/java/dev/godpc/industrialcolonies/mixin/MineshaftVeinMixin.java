package dev.godpc.industrialcolonies.mixin;

import java.util.Optional;
import dev.godpc.industrialcolonies.geology.MineshaftVeins;
import dev.godpc.industrialcolonies.geology.*;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.structures.MineshaftStructure;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(MineshaftStructure.class)
public abstract class MineshaftVeinMixin {
    @Shadow @Final private MineshaftStructure.Type type;
    @Inject(method="findGenerationPoint",at=@At("RETURN"),cancellable=true)
    private void industrialColonies$connectOreWorking(Structure.GenerationContext context,CallbackInfoReturnable<Optional<Structure.GenerationStub>> result){
        var admitted=ContinentMineContext.current(context);
        if(admitted.isPresent()){
            if(WorldStartMinePolicy.enabled(GeologyConfig.get().settings())&&!ContinentMineContext.scheduled(context)){
                // A vanilla structure-set roll must not create an additional mine for a vein.
                result.setReturnValue(Optional.empty());return;
            }
            if(result.getReturnValue().isPresent()&&!ContinentMineshafts.attach(context,result.getReturnValue().get(),admitted.get(),type))result.setReturnValue(Optional.empty());
            return;
        }
        if(GeologyConfig.enabled()&&MassiveDeposits.enabled(GeologyConfig.get())){
            var world=GeologyWorld.forGeneration(context.randomState());
            if(world.overworld()){
                if(result.getReturnValue().isPresent()&&!MassiveMineshafts.attach(context,result.getReturnValue().get(),world))result.setReturnValue(Optional.empty());
                return;
            }
        }
        result.getReturnValue().ifPresent(stub->MineshaftVeins.attach(context,stub,type));
    }
}
