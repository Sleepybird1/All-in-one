package dev.godpc.industrialcolonies.space.enemy;
import dev.godpc.industrialcolonies.space.OrbitalBodyCustody;
import dev.ryanhcode.sable.api.sublevel.SubLevelContainer;
import net.minecraft.server.level.ServerLevel;
import java.util.*;

/** Restore against an externally persisted, complete commissioned NPC roster.
 * All registered survivors must be loaded and match native metadata. Unknown NPC
 * tags refuse restoration. Never treats an empty runtime map as an empty world.
 * Roster creation/removal and spawn authority remain separate operations. */
public final class EnemyNativeBudget {
 private EnemyNativeBudget(){}
 public static void restore(ServerLevel level,Map<UUID,UUID> commissionedBodies,EnemyEncounterBudget budget)throws java.io.IOException{
  if(!level.getServer().isSameThread()||commissionedBodies==null||commissionedBodies.isEmpty()||commissionedBodies.size()>4096)
   throw new IllegalStateException("Complete bounded persisted NPC roster required");
  var expected=Map.copyOf(commissionedBodies);var found=new HashSet<UUID>();var grouped=new HashMap<UUID,Long>();int scanned=0;
  for(var body:SubLevelContainer.getContainer(level).getAllSubLevels()){
   if(++scanned>4096)throw new IllegalStateException("Native body scan budget exceeded");
   var tag=body.getUserDataTag();boolean marked=tag!=null&&tag.contains(EnemyHullIdentity.KEY);
   if(!marked){if(expected.containsKey(body.getUniqueId()))throw new IllegalStateException("Registered NPC lost identity");continue;}
   var identity=EnemyHullIdentity.read(body);var bound=expected.get(body.getUniqueId());
   if(bound==null||!bound.equals(identity.encounter())||!found.add(body.getUniqueId()))throw new IllegalStateException("Unknown or changed native NPC identity");
   var custody=OrbitalBodyCustody.read(body);if(custody.blocks()<1)throw new IllegalStateException("Empty surviving NPC body");
   // CBC assembly moves gun blocks out of the Sable body into a separately
   // registered native entity. They still consume the encounter's block cap.
   // Audit held custody before changing any reservation; armed/unknown mounts
   // must not restore a spawn budget or be treated as zero external blocks.
   long blocks=custody.blocks();
   for(var attachment:EnemyMountedCannonCustody.readHeld(body).attachments())blocks=Math.addExact(blocks,attachment.blocks());
   grouped.merge(bound,blocks,Math::addExact);
  }
  if(!found.equals(expected.keySet()))throw new IllegalStateException("Registered NPC survivor is not loaded");
  if(!budget.restore(grouped))throw new IllegalStateException("Native survivor budget exceeds limits");
 }
}
