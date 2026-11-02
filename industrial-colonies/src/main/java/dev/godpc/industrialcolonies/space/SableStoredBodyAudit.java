package dev.godpc.industrialcolonies.space;

import dev.ryanhcode.sable.api.sublevel.SubLevelContainer;
import java.io.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import net.minecraft.nbt.*;
import net.minecraft.server.MinecraftServer;

/** Read-only native holding-pointer/body inventory. Any unsupported stream or changing file aborts. */
public final class SableStoredBodyAudit {
 public record Body(String dimension,UUID id,Map<UUID,Optional<UUID>> transponders,boolean referenced,String record){
  public Body{transponders=Map.copyOf(transponders);}
 }
 public record Audit(List<Body> bodies,Map<String,String> hashes){
  public Audit{bodies=List.copyOf(bodies);hashes=Map.copyOf(hashes);}
 }
 private record Raw(String dimension,Path file,int slot,CompoundTag tag){}
 private SableStoredBodyAudit(){}
 private static void require(boolean result,String text)throws IOException{if(!result)throw new IOException(text);}
 private static List<Path> files(Path folder)throws IOException{
  if(Files.notExists(folder))return List.of();require(Files.isDirectory(folder,LinkOption.NOFOLLOW_LINKS),"Invalid native storage directory");
  try(var stream=Files.list(folder)){
   var entries=stream.limit(4097).sorted().toList();require(entries.size()<=4096,"Native audit file budget exceeded");var files=new ArrayList<Path>();
   for(Path file:entries){
    String name=file.getFileName().toString();
    if(Files.isDirectory(file,LinkOption.NOFOLLOW_LINKS)&&name.matches("r\\.-?\\d+\\.-?\\d+(\\.\\d+)?\\.[rs]")){
     try(var children=Files.list(file)){require(children.findAny().isEmpty(),"Native external streams require separate validation: "+name);}continue;
    }
    require(Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS)&&name.matches("r\\.-?\\d+\\.-?\\d+(\\.\\d+)?\\.slvl[rs]"),"Unsupported entry in native storage: "+name);files.add(file);
   }
   return List.copyOf(files);
  }
 }
 public static Audit inspect(MinecraftServer server)throws IOException{
  require(server.isSameThread(),"Native audit requires server thread");var folders=new TreeMap<String,Path>();
  for(var level:server.getAllLevels()){
   var container=SubLevelContainer.getContainer(level);if(container==null)continue;
   folders.put(level.dimension().location().toString(),container.getHoldingChunkMap().getStorage().getFolder());
  }
  return inspectFolders(folders);
 }
 public static Audit inspectFolders(Map<String,Path> folders)throws IOException{
  var records=new ArrayList<Raw>();var hashes=new TreeMap<String,String>();var directories=new LinkedHashMap<Path,List<Path>>();long fileBytes=0,nbtBytes=0;
  for(var dimension:folders.entrySet()){
   Path folder=dimension.getValue();var files=files(folder);directories.put(folder,files);
   for(Path file:files){
    fileBytes+=Files.size(file);require(fileBytes<=256L*1024*1024&&hashes.size()<4096,"Native audit input budget exceeded");
    String before=sha(file);hashes.put(file.toString(),before);
    for(var record:SableStorageReader.read(file)){
     byte[] bytes=record.nbt();nbtBytes+=bytes.length;require(nbtBytes<=256L*1024*1024&&records.size()<4096,"Native audit decoded budget exceeded");var input=new DataInputStream(new ByteArrayInputStream(bytes));var tag=NbtIo.read(input,NbtAccounter.create(32L*1024*1024));
     require(input.available()==0,"Trailing native NBT bytes");records.add(new Raw(dimension.getKey(),file,record.slot(),tag));
    }
    require(before.equals(sha(file)),"Native storage changed during read");
   }
  }
  var indexed=new HashMap<String,Raw>();for(var r:records)require(indexed.put(key(r.file(),r.slot()),r)==null,"Duplicate storage record");
  var references=new HashSet<String>();
  for(var r:records)if(r.file().toString().endsWith(".slvlr")){
   require(r.tag().contains("pointers",Tag.TAG_INT_ARRAY),"Malformed native holding pointer list");
   var name=r.file().getFileName().toString();String stem=name.substring(0,name.length()-6);
   for(int pointer:r.tag().getIntArray("pointers")){
    int storage=(short)(pointer>>16),slot=(short)pointer;require(storage>=0&&slot>=0&&slot<1024,"Invalid native holding pointer");
    Path target=r.file().resolveSibling(stem+'.'+storage+".slvls");String key=key(target,slot);
    require(indexed.containsKey(key),"Holding pointer references missing native body");require(references.add(key),"Multiple native holding pointers reference same body");
   }
  }
  var bodies=new ArrayList<Body>();var ids=new HashSet<UUID>();
  for(var r:records)if(r.file().toString().endsWith(".slvls")){
   var tag=r.tag();require(tag.hasUUID("uuid")&&tag.contains("plot",Tag.TAG_COMPOUND),"Malformed native body identity/plot");UUID id=tag.getUUID("uuid");require(ids.add(id),"Duplicate stored native body identity");
   var plot=tag.getCompound("plot");require(plot.contains("chunks",Tag.TAG_COMPOUND),"Malformed stored plot chunks");var transponders=new HashMap<UUID,Optional<UUID>>();var chunks=plot.getCompound("chunks");
   for(String chunkKey:chunks.getAllKeys()){
    require(chunks.contains(chunkKey,Tag.TAG_COMPOUND),"Malformed native plot chunk");var chunk=chunks.getCompound(chunkKey);
    if(!chunk.contains("block_entities"))continue;require(chunk.contains("block_entities",Tag.TAG_LIST),"Malformed native block-entity list");
    var raw=(ListTag)chunk.get("block_entities");require(raw.isEmpty()||raw.getElementType()==Tag.TAG_COMPOUND,"Malformed native block entity");
    for(Tag value:raw){var be=(CompoundTag)value;String type=be.getString("id");
     if(type.equals("create_aeronautics_automated_logistics:ship_transponder")||type.equals("create_aeronautics_automated_logistics:advanced_transponder")){
      require(be.hasUUID("transponderId")&&(!be.contains("ownerId")||be.hasUUID("ownerId")),"Malformed stored transponder identity/owner");require(transponders.put(be.getUUID("transponderId"),be.hasUUID("ownerId")?Optional.of(be.getUUID("ownerId")):Optional.empty())==null,"Duplicate transponder within stored body");
     }
    }
   }
   bodies.add(new Body(r.dimension(),id,transponders,references.contains(key(r.file(),r.slot())),key(r.file(),r.slot())));
  }
  for(var e:directories.entrySet())require(files(e.getKey()).equals(e.getValue()),"Native storage membership changed during audit");
  for(var e:hashes.entrySet())require(sha(Path.of(e.getKey())).equals(e.getValue()),"Native storage bytes changed during audit");
  return new Audit(bodies,hashes);
 }
 private static String key(Path file,int slot){return file.toAbsolutePath().normalize()+"#"+slot;}
 private static String sha(Path file)throws IOException{
  try(var input=Files.newInputStream(file)){var digest=MessageDigest.getInstance("SHA-256");byte[] buffer=new byte[8192];int read;while((read=input.read(buffer))>=0)digest.update(buffer,0,read);return HexFormat.of().formatHex(digest.digest());}
  catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
 }
}
