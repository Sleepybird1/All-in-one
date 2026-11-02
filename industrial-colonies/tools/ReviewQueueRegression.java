import dev.godpc.industrialcolonies.KjsGenRecipeReviewStore;
import com.zizazr.kjsgen.core.*;
import java.util.*;
public class ReviewQueueRegression {
 static int checks;
 static void check(boolean b,String m){checks++;if(!b)throw new AssertionError(m);}
 public static void main(String[] args)throws Exception{
  Class<?> cls=KjsGenRecipeReviewStore.class;
  var ctor=cls.getDeclaredConstructor();ctor.setAccessible(true);
  var store=(KjsGenRecipeReviewStore)ctor.newInstance();
  var pf=cls.getDeclaredField("project");pf.setAccessible(true);
  var mf=cls.getDeclaredField("managedUids");mf.setAccessible(true);
  var rf=cls.getDeclaredField("reviewsByRecipeId");rf.setAccessible(true);
  var rc=Class.forName(cls.getName()+"$StoredReview").getDeclaredConstructors()[0];rc.setAccessible(true);
  var card=new RecipeInstance("minecraft:crafting_shaped");card.setRecipeId("test:card");
  ((Set<String>)mf.get(store)).add(card.uid());
  var ledger=(Map<String,Object>)rf.get(store);
  String[] states={"approved","rejected","maybe","deferred","disabled"};
  String[] archives={"approved recipes","rejected recipes","maybe recipes","Deferred","disabled recipes"};
  for(int i=0;i<states.length;i++){
   ledger.put(card.recipeId(),rc.newInstance(card.uid(),states[i],"test","note",KjsGenRecipeReviewStore.cardSha256(card)));
   for(String name:List.of("Progression Review","default","Other Review")){
    var p=new RecipeProject(name);p.add(card);pf.set(store,p);
    check(store.visibleRecipes(p).isEmpty(),states[i]+" stayed in "+name);
    check(p.recipes().size()==1,"source data deleted");
   }
   for(int j=0;j<archives.length;j++){
    var p=new RecipeProject(archives[j]);p.add(card);pf.set(store,p);
    check(store.visibleRecipes(p).size()==(i==j?1:0),"wrong archive "+states[i]);
   }
  }
  ledger.clear();var p=new RecipeProject("Progression Review");p.add(card);pf.set(store,p);
  check(store.visibleRecipes(p).size()==1,"pending hidden");
  ledger.put(card.recipeId(),rc.newInstance(card.uid(),"approved","","","sha256:old"));
  check(store.visibleRecipes(p).size()==1,"edited card cannot be re-reviewed");
  ((Set<String>)mf.get(store)).clear();check(store.visibleRecipes(p).size()==1,"unmanaged hidden");
  System.out.println("PASS "+checks+" actual-store queue checks");
 }
}
