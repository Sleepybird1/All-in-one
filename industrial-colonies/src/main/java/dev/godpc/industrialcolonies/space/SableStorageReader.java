package dev.godpc.industrialcolonies.space;

import java.io.*;
import java.nio.*;
import java.nio.file.*;
import java.util.*;
import java.util.zip.GZIPInputStream;

/** Read-only exact Sable 2.0.3 framing. Unsupported or incomplete storage is an error, never absence. */
public final class SableStorageReader {
 public record Record(int slot,byte[] nbt) {
  public Record {nbt=nbt.clone();}
  @Override public byte[] nbt(){return nbt.clone();}
 }
 private static final int HEADER=4096,MAX_FILE=64*1024*1024,MAX_PAYLOAD=32*1024*1024;
 private SableStorageReader(){}
 public static List<Record> read(Path path)throws IOException{
  if(!Files.isRegularFile(path,LinkOption.NOFOLLOW_LINKS)||Files.size(path)>MAX_FILE)throw new IOException("Unsupported native storage file");
  String name=path.getFileName().toString();
  int sector=name.matches("r\\.-?\\d+\\.-?\\d+\\.slvlr")?128:name.matches("r\\.-?\\d+\\.-?\\d+\\.\\d+\\.slvls")?4096:0;
  if(sector==0)throw new IOException("Unsupported native storage name/external stream");
  byte[] bytes=Files.readAllBytes(path);
  // Sable 2.0.3 opens holding maps with CREATE and a zero-initialized in-memory
  // header. EOF (-1) is an empty new map; no header is written until mutation
  // or close. Accept ONLY that exact named empty holding map, never a partial
  // header or an empty body store. The caller must still audit all references.
  if(sector==128&&bytes.length==0)return List.of();
  return decode(bytes,sector);
 }
 public static List<Record> decode(byte[] bytes,int sector)throws IOException{
  if((sector!=128&&sector!=4096)||bytes.length<HEADER||bytes.length>MAX_FILE)throw new IOException("Truncated/unsupported native storage framing");
  // Native write/flush persists the actual compressed bytes; only close pads
  // the last allocated sector. Missing padding is not missing record data.
  int sectors=(bytes.length+sector-1)/sector;
  var buffer=ByteBuffer.wrap(bytes).order(ByteOrder.BIG_ENDIAN);var used=new BitSet(sectors);used.set(0,HEADER/sector);var result=new ArrayList<Record>();long totalPayload=0;
  for(int slot=0;slot<1024;slot++){
   int span=buffer.getInt(slot*4);if(span==0)continue;int first=span>>>8,count=span&255;
   long start=(long)first*sector,end=(long)(first+count)*sector;
   if(count==0||start<HEADER||start+5>bytes.length||end>(long)sectors*sector||used.nextSetBit(first)>=0&&used.nextSetBit(first)<first+count)throw new IOException("Invalid/overlapping native storage span at "+slot);
   used.set(first,first+count);int offset=(int)start,size=buffer.getInt(offset),flags=Byte.toUnsignedInt(bytes[offset+4]);
   if(flags!=0)throw new IOException("External/unknown native stream flags at "+slot);
   if(size<=1||size>(end-start)-4||start+4L+size>bytes.length)throw new IOException("Truncated native storage payload at "+slot);
   byte[] payload;
   try(var stream=new GZIPInputStream(new ByteArrayInputStream(bytes,offset+5,size-1))){payload=stream.readNBytes(MAX_PAYLOAD+1);if(payload.length>MAX_PAYLOAD)throw new IOException("Native NBT payload too large");}
   if(payload.length<4||payload[0]!=10)throw new IOException("Native payload is not a compound NBT root");
   totalPayload+=payload.length;if(totalPayload>MAX_FILE)throw new IOException("Native decoded file exceeds audit budget");
   result.add(new Record(slot,payload));
  }
  return List.copyOf(result);
 }
}
