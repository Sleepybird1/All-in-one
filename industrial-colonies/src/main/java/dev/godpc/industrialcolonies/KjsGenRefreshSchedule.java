package dev.godpc.industrialcolonies;
import java.util.*;
/** Cheap polling and retry policy; no filesystem or project serialization. */
public final class KjsGenRefreshSchedule {
 private long nextPoll;
 private final Map<String,String> seen=new HashMap<>();
 private final Map<String,Long> attempted=new HashMap<>();
 public boolean poll(long nanos){if(nanos<nextPoll)return false;nextPoll=nanos+1_000_000_000L;return true;}
 public boolean attempt(String key,String revision,long edits){
  if(revision==null)return false;
  if(revision.equals(seen.get(key))&&(Objects.equals(attempted.get(key),edits)||Objects.equals(attempted.get(key),Long.MIN_VALUE)))return false;
  seen.put(key,revision);attempted.put(key,edits);return true;
 }
 public void success(String key){attempted.put(key,Long.MIN_VALUE);}
 public void clear(){seen.clear();attempted.clear();nextPoll=0;}
}
