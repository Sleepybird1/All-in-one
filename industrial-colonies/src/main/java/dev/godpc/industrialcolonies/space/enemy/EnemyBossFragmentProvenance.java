package dev.godpc.industrialcolonies.space.enemy;
import java.util.UUID;
/** Direct native parent evidence is mandatory; copied tags alone are insufficient. */
public final class EnemyBossFragmentProvenance {
 private EnemyBossFragmentProvenance(){}
 public static boolean matches(UUID source,UUID destination,UUID nativeParent,
         UUID encounter,UUID root,boolean tagged,UUID taggedEncounter,UUID taggedRoot){
  if(source==null||destination==null||encounter==null||root==null||source.equals(destination)
       ||!source.equals(nativeParent))return false;
  return tagged ? encounter.equals(taggedEncounter)&&root.equals(taggedRoot)
       : taggedEncounter==null&&taggedRoot==null;
 }
}
