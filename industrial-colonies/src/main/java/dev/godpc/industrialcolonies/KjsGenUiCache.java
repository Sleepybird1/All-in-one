package dev.godpc.industrialcolonies;
import java.util.function.Supplier;
/** Cache only UI summaries; authoritative review decisions remain uncached. */
public final class KjsGenUiCache<T> {
 private Object owner;private int size;private long expires;private T value;
 public T get(Object project,int count,long now,Supplier<T> compute){
  if(value==null||owner!=project||size!=count||now>=expires){value=compute.get();owner=project;size=count;expires=now+500_000_000L;}return value;
 }
 public void invalidate(){value=null;}
}
