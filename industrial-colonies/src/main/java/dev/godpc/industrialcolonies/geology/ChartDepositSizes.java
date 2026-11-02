package dev.godpc.industrialcolonies.geology;

import static dev.godpc.industrialcolonies.geology.GeologyMath.*;

/** Earth resource chart: counts are ore blocks, never quality-scaled formation volumes. */
public final class ChartDepositSizes {
 private ChartDepositSizes(){}
 public static int coal(long seed){return tier(unit(seed),8000,35000,100000);}
 public static int cinnabar(long seed){return tier(unit(seed),1000,5000,15000);}
 static int tier(double roll,int small,int medium,int large){
  if(!Double.isFinite(roll)||roll<0||roll>=1)throw new IllegalArgumentException("Unit tier roll required");
  return roll<.80?small:roll<.98?medium:large;
 }
}
