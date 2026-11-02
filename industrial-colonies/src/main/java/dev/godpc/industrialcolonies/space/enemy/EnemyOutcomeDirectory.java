package dev.godpc.industrialcolonies.space.enemy;

import java.nio.file.*;
import java.io.IOException;

/** Filesystem policy only. Native adapters supply the actual server save root.
 * No arbitrary alternate capture/reward directory and no implicit migration. */
final class EnemyOutcomeDirectory {
 private EnemyOutcomeDirectory(){}
 static Path expected(Path world)throws IOException{
  if(!Files.isDirectory(world,LinkOption.NOFOLLOW_LINKS)||Files.isSymbolicLink(world))throw new IOException("Existing native world directory required");
  return world.toRealPath().resolve("data").resolve("industrial_colonies_enemy_outcomes");
 }
 static Path require(Path world,Path requested,boolean create)throws IOException{
  var expected=expected(world);
  if(requested==null||!expected.equals(requested.toAbsolutePath().normalize()))throw new IOException("Capture and rewards require the same native world outcome directory");
  for(var path:new Path[]{expected.getParent(),expected}){
   if(create&&Files.notExists(path,LinkOption.NOFOLLOW_LINKS)){
    try{Files.createDirectory(path);}catch(FileAlreadyExistsException race){/* Inspect raced entry below. */}
   }
   if(!Files.isDirectory(path,LinkOption.NOFOLLOW_LINKS)||Files.isSymbolicLink(path)||!path.toRealPath().equals(path))throw new IOException("Missing or redirected native outcome directory");
  }
  return expected;
 }
}
