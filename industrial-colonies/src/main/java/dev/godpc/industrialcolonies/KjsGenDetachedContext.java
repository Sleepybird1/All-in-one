package dev.godpc.industrialcolonies;
import java.util.function.*;
/** Scoped editor execution always restores the playable game's active screen. */
public final class KjsGenDetachedContext {
 private static int depth;
 public static boolean active(){return depth>0;}
 public static <T> void run(Supplier<T> get,Consumer<T> set,T editor,Runnable action){
  T previous=get.get();depth++;
  try{set.accept(editor);action.run();}finally{try{set.accept(previous);}finally{depth--;}}
 }
}
