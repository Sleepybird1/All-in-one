package dev.godpc.industrialcolonies.space;

import java.util.*;

/** Preserve recorded linear motion only for an unambiguous unfinished freight
 * commitment. This grants no permit and does not restore actuator/controller state. */
public final class FreightMotionPersistence {
 private FreightMotionPersistence(){}
 public static boolean preserves(FreightJourneyJournal journal,String dimension,UUID body){
  if(!journal.fault().isEmpty())return false;
  var owners=new HashSet<UUID>();int currentBodies=0;
  for(var entry:journal.entries()){
   if(entry.phase().terminal())continue;var p=entry.plan();
   String currentDimension=entry.phase().ordinal()<=FreightJourneyJournal.Phase.HANDOFF.ordinal()?p.sourceDimension():p.destinationDimension();
   if(entry.body().equals(body)&&currentDimension.equals(dimension)){owners.add(p.owner());currentBodies++;}
   if(p.destinationRoute().startsWith("icdock1:")){
    try{var ref=FreightDestinationReference.decode(p.destinationRoute());ref.requirePlan(p);
     if(ref.body().equals(body)&&ref.dimension().equals(dimension))owners.add(ref.owner());
    }catch(IllegalArgumentException invalid){/* An invalid reference authorizes no persistence override. */}
   }
  }
  return currentBodies<=1&&owners.size()==1;
 }
}
