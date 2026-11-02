package dev.godpc.industrialcolonies.geology;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.Objects;

/** Scope and commissioning intent for a per-level coordinator root. Never repairs missing journals. */
public final class ContinentCoordinatorDirectory {
 public record Entry(Path path,boolean existing){}
 public record PolicyEntry(Entry entry,boolean rollout){}
 private final Path root;private final String identity;
 private ContinentCoordinatorDirectory(Path root,String identity){
  this.root=Objects.requireNonNull(root).toAbsolutePath().normalize();this.identity=Objects.requireNonNull(identity);
  if(identity.isEmpty()||identity.getBytes(StandardCharsets.UTF_8).length>1024)throw new IllegalArgumentException("Bounded runtime identity required");
 }
 public static ContinentCoordinatorDirectory create(Path root,String identity)throws IOException{
  var directory=new ContinentCoordinatorDirectory(root,identity);Files.createDirectory(directory.root);
  Files.writeString(directory.root.resolve("runtime.scope"),identity,StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);
  return directory;
 }
 public static ContinentCoordinatorDirectory open(Path root,String identity)throws IOException{
  var directory=new ContinentCoordinatorDirectory(root,identity);directory.check();return directory;
 }
 public void check()throws IOException{
  Path file=root.resolve("runtime.scope");
  if(!Files.isDirectory(root,LinkOption.NOFOLLOW_LINKS)||!Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS)||Files.size(file)>1024||!Files.readString(file,StandardCharsets.UTF_8).equals(identity))throw new IOException("Missing or changed continent runtime identity");
 }
 /** New entry intent is written first; caller creates journals exactly once or holds the failed intent. */
 public Entry commission(String name)throws IOException{
  return commissionInternal(name,false);
 }
 private Entry commissionInternal(String name,boolean policyAdmitted)throws IOException{
  check();if(name==null||!name.matches("continent-[a-f0-9]{8}-[a-f0-9]{8}-[a-f0-9]{8}"))throw new IllegalArgumentException("Exact native continent key required");
  Path path=root.resolve(name),intent=root.resolve(name+".started");
  if(!policyAdmitted&&Files.exists(root.resolve(name+".policy"),LinkOption.NOFOLLOW_LINKS))throw new IOException("Versioned continent requires its recorded policy");
  if(Files.exists(intent,LinkOption.NOFOLLOW_LINKS)){
   if(!Files.isRegularFile(intent,LinkOption.NOFOLLOW_LINKS)||Files.size(intent)!=0||!Files.isDirectory(path,LinkOption.NOFOLLOW_LINKS))throw new IOException("Incomplete saved continent commissioning");
   return new Entry(path,true);
  }
  if(Files.exists(path,LinkOption.NOFOLLOW_LINKS))throw new IOException("Uncommissioned continent directory must not be adopted");
  Files.createFile(intent);return new Entry(path,false);
 }
 /** Existing commissioning always retains its original policy. A durable marker precedes any new
  * rollout intent; interrupted markers hold instead of falling back or silently rerolling. */
 public PolicyEntry commission(String name,String rolloutPolicy)throws IOException{
  check();
  if(name==null||!name.matches("continent-[a-f0-9]{8}-[a-f0-9]{8}-[a-f0-9]{8}")
      ||rolloutPolicy==null||!rolloutPolicy.matches("[a-f0-9]{64}"))throw new IllegalArgumentException("Exact continent and policy required");
  Path marker=root.resolve(name+".policy"),intent=root.resolve(name+".started"),path=root.resolve(name);
  if(Files.exists(marker,LinkOption.NOFOLLOW_LINKS)){
   if(!Files.isRegularFile(marker,LinkOption.NOFOLLOW_LINKS)||Files.size(marker)!=64
       ||!Files.readString(marker,StandardCharsets.UTF_8).equals(rolloutPolicy))throw new IOException("Unknown or changed continent policy");
   if(!Files.exists(intent,LinkOption.NOFOLLOW_LINKS))throw new IOException("Interrupted continent policy claim requires explicit recovery");
   return new PolicyEntry(commissionInternal(name,true),true);
  }
  if(Files.exists(intent,LinkOption.NOFOLLOW_LINKS)||Files.exists(path,LinkOption.NOFOLLOW_LINKS))
   return new PolicyEntry(commissionInternal(name,false),false);
  try(var channel=java.nio.channels.FileChannel.open(marker,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)){
   var bytes=java.nio.ByteBuffer.wrap(rolloutPolicy.getBytes(StandardCharsets.UTF_8));
   while(bytes.hasRemaining())channel.write(bytes);channel.force(true);
  }
  return new PolicyEntry(commissionInternal(name,true),true);
 }

}
