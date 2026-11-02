package dev.godpc.industrialcolonies.geology;

import java.io.IOException;
import java.util.*;
import java.util.function.BooleanSupplier;

/** Bounded, thread-confined residency, never a replacement for durable coordinator journals. */
public final class ContinentCoordinatorCache<K,V> implements AutoCloseable {
 public static final class Busy extends IllegalStateException { public Busy(){super("All resident coordinators are leased");} }
 @FunctionalInterface public interface Loader<K,V> { V load(K key) throws IOException; }
 private final int capacity;
 private final BooleanSupplier correctThread;
 private final Loader<K,V> loader;
 private final LinkedHashMap<K,Entry> entries=new LinkedHashMap<>(16,.75f,true);
 private boolean closed,loading;
 private final class Entry { final V value;int leases;Entry(V value){this.value=value;} }
 public ContinentCoordinatorCache(int capacity,BooleanSupplier correctThread,Loader<K,V> loader){
  if(capacity<1||capacity>64)throw new IllegalArgumentException("Coordinator capacity1..64");
  this.capacity=capacity;this.correctThread=Objects.requireNonNull(correctThread);this.loader=Objects.requireNonNull(loader);
 }
 private void thread(){if(!correctThread.getAsBoolean())throw new IllegalStateException("Coordinator owner thread required");}
 private void live(){thread();if(closed)throw new IllegalStateException("Coordinator cache closed");}
 public Lease acquire(K key)throws IOException{
  live();Objects.requireNonNull(key);
  if(loading)throw new IllegalStateException("Reentrant coordinator loading");
  Entry entry=entries.get(key);
  if(entry==null){
   if(entries.size()==capacity){
    var iterator=entries.entrySet().iterator();boolean removed=false;
    while(iterator.hasNext()){if(iterator.next().getValue().leases==0){iterator.remove();removed=true;break;}}
    if(!removed)throw new Busy();
   }
   // Eviction never deletes saved state. A failed load leaves room for a later explicit retry.
   loading=true;try{entry=new Entry(Objects.requireNonNull(loader.load(key)));}finally{loading=false;}
   entries.put(key,entry);
  }
  entry.leases++;return new Lease(entry);
 }
 public int residentCount(){live();return entries.size();}
 public final class Lease implements AutoCloseable {
  private final Entry entry;private boolean released;
  private Lease(Entry entry){this.entry=entry;}
  public V value(){live();if(released)throw new IllegalStateException("Coordinator lease released");return entry.value;}
  @Override public void close(){thread();if(!released){released=true;entry.leases--;}}
 }
 @Override public void close(){thread();if(loading)throw new IllegalStateException("Close during coordinator loading");closed=true;entries.clear();}
}
