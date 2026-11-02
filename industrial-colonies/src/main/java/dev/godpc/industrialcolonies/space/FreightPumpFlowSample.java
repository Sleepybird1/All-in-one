package dev.godpc.industrialcolonies.space;

import java.io.IOException;
import java.util.Set;
import net.minecraft.nbt.*;

/** Create 6.0.10 completed pump-flow samples are one-unit SIMULATE queries,
 * not stored fluid. Only this explicit recovery profile omits them from a
 * newly captured digest. Tanks, pressure, power and every other field stay exact. */
final class FreightPumpFlowSample {
 private FreightPumpFlowSample(){}
 static void normalize(CompoundTag saved)throws IOException{
  if(!saved.getString("id").equals("create:mechanical_pump"))throw new IOException("Exact pump schema required");
  for(String side:Set.of("down","up","north","south","west","east")){
   if(!saved.contains(side))continue;
   if(!saved.contains(side,Tag.TAG_COMPOUND))throw new IOException("Pump side must be compound");
   var connection=saved.getCompound(side);
   // Open ends can own real fluid; this bounded profile refuses them entirely.
   if(connection.contains("OpenEnd"))throw new IOException("Open-ended pump not qualified");
   if(!connection.contains("Flow"))continue;
   if(!connection.contains("Flow",Tag.TAG_COMPOUND))throw new IOException("Flow sample must be compound");
   var flow=connection.getCompound("Flow");
   if(!flow.getAllKeys().equals(Set.of("Fluid","In"))||!flow.contains("In",Tag.TAG_BYTE)||flow.getByte("In")<0||flow.getByte("In")>1||!flow.contains("Fluid",Tag.TAG_COMPOUND))throw new IOException("Only complete standard flow samples qualified");
   var fluid=flow.getCompound("Fluid");
   if(!fluid.getAllKeys().equals(Set.of("id","amount"))||!fluid.contains("id",Tag.TAG_STRING)||!fluid.contains("amount",Tag.TAG_INT)||fluid.getInt("amount")!=1||!fluid.getString("id").matches("[a-z0-9_.-]+:[a-z0-9/._-]+")||fluid.getString("id").equals("minecraft:empty"))throw new IOException("Only one-unit component-free simulated flow samples qualified");
   connection.remove("Flow");
  }
 }
}
