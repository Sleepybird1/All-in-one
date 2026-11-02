package dev.godpc.industrialcolonies.mixin;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.companion.math.BoundingBox3d;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.AABB;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;
/** Keep both bounds in world coordinates during a client riding transition from a ship plot. */
@Mixin(value=Player.class,priority=900)
public abstract class SableRidingBoundsMixin {
 @ModifyArg(method="aiStep",at=@At(value="INVOKE",target="Lnet/minecraft/world/level/Level;getEntities(Lnet/minecraft/world/entity/Entity;Lnet/minecraft/world/phys/AABB;)Ljava/util/List;"),index=1,require=1)
 private AABB industrialColonies$alignPlayerBounds(AABB box) {
  var player=(Player)(Object)this;
  if(!player.level().isClientSide || !net.neoforged.fml.ModList.get().isLoaded("sable"))return box;
  var vehicle=player.getVehicle();if(vehicle==null)return box;
  var body=Sable.HELPER.getContaining(vehicle);
  if(body==null||Sable.HELPER.getContaining(player)!=body)return box;
  var rider=new BoundingBox3d(player.getBoundingBox());
  var seat=new BoundingBox3d(vehicle.getBoundingBox());
  var riderWorld=rider.transform(body.logicalPose(),rider).toMojang();
  var seatWorld=seat.transform(body.logicalPose(),seat).toMojang();
  return riderWorld.minmax(seatWorld).inflate(1.0,0.0,1.0);
 }
}
