package dev.godpc.industrialcolonies.geology;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;
import java.util.function.IntPredicate;

/** Pure location intent and enclosed-cavity search; never rolls ore presence or edits terrain. */
public final class CaveDirectedLocations {
 private CaveDirectedLocations(){}
 public interface Column { boolean air(int y); boolean solid(int y); }
 /** Bound to the saved search/slot, never to successive candidate coordinates. */
 public static boolean directed(String identity){
  Objects.requireNonNull(identity);if(identity.isBlank())throw new IllegalArgumentException("Saved search identity required");
  try{
   byte[] digest=MessageDigest.getInstance("SHA-256").digest(("IC_CAVE_LOCATION_V1\n"+identity).getBytes(StandardCharsets.UTF_8));
   return (ByteBuffer.wrap(digest).getLong()>>>11)*0x1.0p-53<.25;
  }catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
 }
 /** Nearest admissible floor first; an empty result is never replaced with a buried default.
  * At least two dry air cells and a solid roof within32blocks distinguish enclosed caves.
  * The requested formation center is two blocks below its existing cave floor. */
 public static OptionalInt fit(Column column,int minY,int maxY,int preferredCenter,IntPredicate formationFits){
  Objects.requireNonNull(column);Objects.requireNonNull(formationFits);
  if((long)maxY-minY>4096||minY>maxY)throw new IllegalArgumentException("Bounded underground column required");
  var floors=new ArrayList<Integer>();
  for(int floor=minY+2;floor<=maxY-3;floor++){
   if(!column.solid(floor)||!column.air(floor+1)||!column.air(floor+2))continue;
   boolean roof=false;
   for(int y=floor+3;y<=Math.min((long)maxY,(long)floor+32);y++){
    if(column.solid(y)){roof=true;break;}
    if(!column.air(y))break; // Fluids and unknown materials never certify a dry cavity.
   }
   if(roof)floors.add(floor);
  }
  floors.sort(Comparator.<Integer>comparingLong(y->Math.abs((long)y-2-preferredCenter)).thenComparingInt(Integer::intValue));
  for(int floor:floors)if(formationFits.test(floor-2))return OptionalInt.of(floor-2);
  return OptionalInt.empty();
 }
}
