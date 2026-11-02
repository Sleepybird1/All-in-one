package dev.godpc.industrialcolonies.mixin;
import com.simibubi.create.content.kinetics.deployer.ItemApplicationRecipeParams;
import com.mojang.serialization.*;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import dev.godpc.industrialcolonies.DeployerToolDamage;
import net.minecraft.network.RegistryFriendlyByteBuf;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(value=ItemApplicationRecipeParams.class,remap=false)
public abstract class DeployerToolDamageParamsMixin implements DeployerToolDamage {
 @Shadow public static MapCodec<ItemApplicationRecipeParams> CODEC;
 @Unique private int industrialColonies$damage=1;
 public int industrialColonies$damage(){return industrialColonies$damage;}
 public void industrialColonies$damage(int value){if(value<1)throw new IllegalArgumentException("Tool damage must be positive");industrialColonies$damage=value;}
 @Inject(method="<clinit>",at=@At("TAIL"))
 private static void industrialColonies$codec(CallbackInfo ci) {
  var original=CODEC;
  CODEC=RecordCodecBuilder.mapCodec(instance->instance.group(
   original.forGetter((ItemApplicationRecipeParams p)->p),
   Codec.intRange(1,Integer.MAX_VALUE).optionalFieldOf("industrial_tool_damage",1).forGetter(p->((DeployerToolDamage)p).industrialColonies$damage())
  ).apply(instance,(p,damage)->{((DeployerToolDamage)p).industrialColonies$damage(damage);return p;}));
 }
 @Inject(method="encode",at=@At("TAIL"))
 private void industrialColonies$write(RegistryFriendlyByteBuf buffer,CallbackInfo ci){buffer.writeVarInt(industrialColonies$damage);}
 @Inject(method="decode",at=@At("TAIL"))
 private void industrialColonies$read(RegistryFriendlyByteBuf buffer,CallbackInfo ci){industrialColonies$damage(buffer.readVarInt());}
}
