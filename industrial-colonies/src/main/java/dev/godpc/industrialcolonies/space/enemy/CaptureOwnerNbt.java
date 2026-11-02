package dev.godpc.industrialcolonies.space.enemy;
import net.minecraft.nbt.*;
import java.io.IOException;
import java.util.*;
/** Exact two-field comparison allowance, never a live NBT mutation. */
public final class CaptureOwnerNbt {
 private CaptureOwnerNbt(){}
 public static CompoundTag comparisonCopy(CompoundTag saved,UUID transponder,Optional<UUID> owner,String name)throws IOException{
  Objects.requireNonNull(transponder);Objects.requireNonNull(owner);Objects.requireNonNull(name);
  if(!saved.getString("id").equals("create_aeronautics_automated_logistics:ship_transponder")
      ||!saved.contains("dataVersion",Tag.TAG_INT)||saved.getInt("dataVersion")!=1
      ||!saved.hasUUID("transponderId")||!saved.getUUID("transponderId").equals(transponder)
      ||!saved.contains("ownerName",Tag.TAG_STRING)||!saved.getString("ownerName").equals(name)
      ||(owner.isPresent()?(!saved.hasUUID("ownerId")||!saved.getUUID("ownerId").equals(owner.get())):saved.contains("ownerId")))
   throw new IOException("Capture owner comparison identity/schema mismatch");
  var copy=saved.copy();copy.remove("ownerId");copy.remove("ownerName");return copy;
 }
}
