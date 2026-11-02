package dev.godpc.industrialcolonies.geology;

import java.util.Objects;

/** One bounded generation step. No lease survives a yield, success or failure.
 * Only acquisition contention retries; a failure after admission is terminal and never replays writes. */
public final class ContinentGenerationSlice<L extends AutoCloseable,R> {
 @FunctionalInterface public interface Acquire<L>{L get()throws Exception;}
 @FunctionalInterface public interface Advance<L>{boolean ready(L lease)throws Exception;}
 @FunctionalInterface public interface Finish<L,R>{R apply(L lease)throws Exception;}
 private final Acquire<L> acquire;private final Advance<L> advance;private final Finish<L,R> finish;
 private boolean running,done,failed;private R result;
 public ContinentGenerationSlice(Acquire<L> acquire,Advance<L> advance,Finish<L,R> finish){this.acquire=Objects.requireNonNull(acquire);this.advance=Objects.requireNonNull(advance);this.finish=Objects.requireNonNull(finish);}
 public boolean advance()throws Exception{
  if(running||done||failed)throw new IllegalStateException("Generation slice is already running or terminal");
  running=true;
  try{
   L lease;
   try{lease=Objects.requireNonNull(acquire.get());}catch(ContinentCoordinatorCache.Busy busy){return false;}
   R candidate;
   try(lease){if(!advance.ready(lease))return false;candidate=Objects.requireNonNull(finish.apply(lease));}
   result=candidate;done=true;return true;
  }catch(NativeTerrainYield.Pending pending){throw pending;}
  catch(Exception|Error failure){failed=true;throw failure;}
  finally{running=false;}
 }
 public R result(){if(!done)throw new IllegalStateException("Generation result not committed");return result;}
}
