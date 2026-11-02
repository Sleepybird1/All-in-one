package dev.godpc.industrialcolonies.space.enemy;

import java.io.IOException;
import java.util.*;

/** Consistency check for a trusted live observer. Supplied values alone never
 * establish native destruction or authorize a reward. */
public final class EnemyDestructionBinding {
 private EnemyDestructionBinding(){}
 public static void require(EnemyBossDestructionJournal.CommittedObservation saved,
     UUID encounter,UUID root,long revision,Set<String> manifest,Set<String> destroyed,
     String currentStructure)throws IOException {
  if(saved==null||!saved.encounter().equals(encounter)||!saved.authority().equals(root)
      ||manifest==null||manifest.isEmpty()||manifest.size()>128||destroyed==null
      ||destroyed.isEmpty()||!manifest.containsAll(destroyed)||revision<1
      ||saved.entries().size()!=revision)
   throw new IOException("Destruction authority, manifest or revision mismatch");
  var union=new HashSet<String>();long expected=1;String previous=null;
  for(var entry:saved.entries()){
   if(!entry.committed()||entry.revision()!=expected++
       ||previous!=null&&!previous.equals(entry.before()))
    throw new IOException("Incomplete destruction chain");
   for(var name:entry.candidates()){
    if(!manifest.contains(name)||union.contains(name))
     throw new IOException("Unknown or previously destroyed constituent");
    if(entry.kind()==EnemyBossDestructionJournal.Kind.DESTROY)union.add(name);
   }
   previous=entry.after();
  }
  if(!union.equals(destroyed)||!Objects.equals(previous,currentStructure))
   throw new IOException("Live destruction observation differs from receipt");
 }
}
