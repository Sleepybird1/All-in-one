package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.content.kinetics.belt.behaviour.BeltProcessingBehaviour;
import com.simibubi.create.content.kinetics.belt.behaviour.TransportedItemStackHandlerBehaviour;
import com.simibubi.create.content.kinetics.belt.transport.TransportedItemStack;
import dev.godpc.industrialcolonies.CreateMachineContext;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** Replaces belt/depot context with the processing machine that owns the callback. */
@Mixin(BeltProcessingBehaviour.class)
public abstract class BeltProcessingBehaviourMixin {
    @Redirect(
            method = {
                    "handleReceivedItem(Lcom/simibubi/create/content/kinetics/belt/transport/TransportedItemStack;"
                            + "Lcom/simibubi/create/content/kinetics/belt/behaviour/"
                            + "TransportedItemStackHandlerBehaviour;)"
                            + "Lcom/simibubi/create/content/kinetics/belt/behaviour/"
                            + "BeltProcessingBehaviour$ProcessingResult;",
                    "handleHeldItem(Lcom/simibubi/create/content/kinetics/belt/transport/TransportedItemStack;"
                            + "Lcom/simibubi/create/content/kinetics/belt/behaviour/"
                            + "TransportedItemStackHandlerBehaviour;)"
                            + "Lcom/simibubi/create/content/kinetics/belt/behaviour/"
                            + "BeltProcessingBehaviour$ProcessingResult;"
            },
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/simibubi/create/content/kinetics/belt/behaviour/"
                            + "BeltProcessingBehaviour$ProcessingCallback;apply("
                            + "Lcom/simibubi/create/content/kinetics/belt/transport/TransportedItemStack;"
                            + "Lcom/simibubi/create/content/kinetics/belt/behaviour/"
                            + "TransportedItemStackHandlerBehaviour;)"
                            + "Lcom/simibubi/create/content/kinetics/belt/behaviour/"
                            + "BeltProcessingBehaviour$ProcessingResult;"
            )
    )
    private BeltProcessingBehaviour.ProcessingResult industrialColonies$useProcessingMachine(
            BeltProcessingBehaviour.ProcessingCallback callback,
            TransportedItemStack transported,
            TransportedItemStackHandlerBehaviour handler
    ) {
        BeltProcessingBehaviour behaviour = (BeltProcessingBehaviour) (Object) this;
        try (CreateMachineContext.Scope ignored = CreateMachineContext.enter(behaviour.blockEntity)) {
            return callback.apply(transported, handler);
        }
    }
}
