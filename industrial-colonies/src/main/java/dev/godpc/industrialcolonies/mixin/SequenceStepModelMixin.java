package dev.godpc.industrialcolonies.mixin;
import com.zizazr.kjsgen.core.*;
import dev.godpc.industrialcolonies.SequenceStageOptions;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import java.util.*;

@Mixin(value=CreateSpecialModel.class,remap=false)
public abstract class SequenceStepModelMixin {
    @Shadow @Final @Mutable public static List<CreateSpecialModel.StepType> STEP_TYPES;
    @Inject(method="<clinit>",at=@At("TAIL"))
    private static void industrialColonies$extend(CallbackInfo ci) {
        var types=new ArrayList<>(STEP_TYPES);
        for(String id:List.of("mixing","compacting","smoking","blasting","splashing","haunting"))
            types.add(new CreateSpecialModel.StepType(id,false,false));
        STEP_TYPES=List.copyOf(types);
    }
    @Inject(method="moveStep",at=@At("HEAD"))
    private static void industrialColonies$move(RecipeInstance recipe,RecipeTypeDefinition type,int from,int to,CallbackInfo ci) { SequenceStageOptions.move(recipe,type,from,to); }
    @Inject(method="removeStep",at=@At("HEAD"))
    private static void industrialColonies$remove(RecipeInstance recipe,RecipeTypeDefinition type,int index,CallbackInfo ci) { SequenceStageOptions.remove(recipe,type,index); }
    @Inject(method="setStepType",at=@At("HEAD"))
    private static void industrialColonies$clear(RecipeInstance recipe,int index,String operation,CallbackInfo ci) { SequenceStageOptions.clear(recipe,index); }
}
