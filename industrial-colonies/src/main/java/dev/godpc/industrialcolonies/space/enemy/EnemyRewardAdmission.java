package dev.godpc.industrialcolonies.space.enemy;

import java.util.*;

/** Read-only proposal: ALLOW_RESERVATION is not permission to create items.
 * Caller must verify durable destruction evidence and atomically reserve the
 * encounter (not player) before any grant. No rewards, storage or native hooks. */
public final class EnemyRewardAdmission {
 public enum Claim { NONE, PENDING, COMMITTED, UNKNOWN }
 public enum Decision { ALLOW_RESERVATION, HOLD, ALREADY_CLAIMED }
 public record Evidence(UUID encounter,UUID root,UUID currentOwner,UUID beneficiary,
       long observationTick,long now,long revision,boolean enabled,boolean completeCustody,
       Set<String> commissioned,Map<String,EnemyBossDefeat.Condition> conditions,
       String verifiedDestructionDigest,Claim claim){
  public Evidence {
   commissioned=Set.copyOf(Objects.requireNonNull(commissioned));
   conditions=Map.copyOf(Objects.requireNonNull(conditions));
  }
 }
 private EnemyRewardAdmission(){}
 public static Decision assess(Evidence e){
  if(e==null||e.encounter()==null||e.root()==null||e.beneficiary()==null
      ||!e.root().equals(e.currentOwner())||e.claim()==null)return Decision.HOLD;
  if(e.claim()==Claim.COMMITTED)return Decision.ALREADY_CLAIMED;
  if(e.claim()!=Claim.NONE||!e.enabled()||!e.completeCustody()||e.revision()<1
      ||e.observationTick()<0||e.now()<e.observationTick()||e.now()-e.observationTick()>1)
   return Decision.HOLD;
  if(e.commissioned().isEmpty()||e.commissioned().size()>128
      ||e.commissioned().stream().anyMatch(n->n.isBlank()||n.length()>128)
      ||!e.conditions().keySet().equals(e.commissioned())
      ||e.conditions().values().stream().anyMatch(c->c!=EnemyBossDefeat.Condition.DESTROYED))return Decision.HOLD;
  if(e.verifiedDestructionDigest()==null||!e.verifiedDestructionDigest().matches("[0-9a-f]{64}"))return Decision.HOLD;
  return Decision.ALLOW_RESERVATION;
 }
}
