package dev.godpc.industrialcolonies.geology;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import java.util.function.BooleanSupplier;

/** Resolve an observed natural-owner hash against existing checksummed decisions, without commissioning. */
public final class RecordedVeinScopeLookup {
 private RecordedVeinScopeLookup(){}
 @FunctionalInterface public interface Reader {Collection<ContinentOccurrenceLedger.Entry> read(Path file)throws IOException;}
 public static Optional<ContinentOccurrenceLedger.Request> find(Path root,String owner,BooleanSupplier cancelled,Reader reader)throws IOException{
  if(owner==null||!owner.matches("[a-f0-9]{64}"))throw new IllegalArgumentException("Natural owner key");
  if(!Files.isDirectory(root,LinkOption.NOFOLLOW_LINKS)||Files.isSymbolicLink(root))throw new IOException("Saved vein directory unavailable");
  ContinentOccurrenceLedger.Request match=null;int visited=0;
  try(var directories=Files.newDirectoryStream(root,"continent-*")){
   for(var directory:directories){
    if(cancelled.getAsBoolean())throw new java.util.concurrent.CancellationException();
    if(++visited>4096)throw new IOException("Saved vein directory limit");
    if(directory.getFileName().toString().matches("continent-[0-9a-f]{8}-[0-9a-f]{8}-[0-9a-f]{8}\\.started")){
     String name=directory.getFileName().toString();var paired=root.resolve(name.substring(0,name.length()-8));
     if(Files.isSymbolicLink(directory)||!Files.isRegularFile(directory,LinkOption.NOFOLLOW_LINKS)||Files.size(directory)!=0||Files.isSymbolicLink(paired)||!Files.isDirectory(paired,LinkOption.NOFOLLOW_LINKS))throw new IOException("Incomplete continent commissioning marker");
     continue;
    }
    if(!directory.getFileName().toString().matches("continent-[0-9a-f]{8}-[0-9a-f]{8}-[0-9a-f]{8}")||Files.isSymbolicLink(directory)||!Files.isDirectory(directory,LinkOption.NOFOLLOW_LINKS))throw new IOException("Invalid saved vein directory");
    var file=directory.resolve("occurrences.bin");if(!Files.exists(file,LinkOption.NOFOLLOW_LINKS))continue;
    if(!Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS)||Files.isSymbolicLink(file))throw new IOException("Invalid saved vein record");
    for(var entry:reader.read(file))if(entry.present()&&ContinentOreProvenance.key(entry.request()).equals(owner)){
     if(match!=null)throw new IOException("Duplicate saved natural-owner authority");match=entry.request();
    }
   }
  }
  return Optional.ofNullable(match);
 }
}
