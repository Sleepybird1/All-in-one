package dev.godpc.industrialcolonies.space;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;

/** Immutable commissioned dock identity, suitable for Plan.destinationRoute.
 * This identifies a destination; it is not a trajectory or permission to move. */
public record FreightDestinationReference(UUID endpoint,UUID owner,UUID body,String dimension,
                                          int x,int y,int z,Face facing,Face up) {
 public enum Face {
  DOWN(1),UP(1),NORTH(2),SOUTH(2),WEST(0),EAST(0);
  final int axis;Face(int axis){this.axis=axis;}
 }
 private static final String PREFIX="icdock1:";
 public FreightDestinationReference {
  for(var id:List.of(endpoint,owner,body))if(id.equals(new UUID(0,0)))throw new IllegalArgumentException("Nonzero destination identity required");
  if(dimension==null||dimension.length()>256||!dimension.matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))throw new IllegalArgumentException("Invalid destination dimension");
  Objects.requireNonNull(facing);Objects.requireNonNull(up);
  if(facing.axis==up.axis)throw new IllegalArgumentException("Dock facing and up must be perpendicular");
 }
 public String encode(){
  try{
   var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);out.writeInt(0x49434431);
   for(var id:List.of(endpoint,owner,body)){out.writeLong(id.getMostSignificantBits());out.writeLong(id.getLeastSignificantBits());}
   out.writeUTF(dimension);out.writeInt(x);out.writeInt(y);out.writeInt(z);out.writeByte(facing.ordinal());out.writeByte(up.ordinal());out.flush();
   return PREFIX+Base64.getUrlEncoder().withoutPadding().encodeToString(bytes.toByteArray());
  }catch(IOException impossible){throw new AssertionError(impossible);}
 }
 public static FreightDestinationReference decode(String text){
  if(text==null||text.length()>1024||!text.startsWith(PREFIX))throw new IllegalArgumentException("Expected canonical physical dock reference");
  try{
   var in=new DataInputStream(new ByteArrayInputStream(Base64.getUrlDecoder().decode(text.substring(PREFIX.length()))));
   if(in.readInt()!=0x49434431)throw new IllegalArgumentException("Unknown physical dock reference format");
   UUID endpoint=new UUID(in.readLong(),in.readLong()),owner=new UUID(in.readLong(),in.readLong()),body=new UUID(in.readLong(),in.readLong());
   String dimension=in.readUTF();int x=in.readInt(),y=in.readInt(),z=in.readInt(),facing=in.readUnsignedByte(),up=in.readUnsignedByte();
   if(facing>=Face.values().length||up>=Face.values().length||in.available()!=0)throw new IllegalArgumentException("Invalid physical dock reference payload");
   var result=new FreightDestinationReference(endpoint,owner,body,dimension,x,y,z,Face.values()[facing],Face.values()[up]);
   if(!result.encode().equals(text))throw new IllegalArgumentException("Noncanonical physical dock reference");return result;
  }catch(IOException|IllegalArgumentException failure){throw new IllegalArgumentException("Invalid physical dock reference",failure);}
 }
 public String digest(){
  try{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(encode().getBytes(StandardCharsets.UTF_8)));}
  catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
 }
 public void requirePlan(FreightJourneyJournal.Plan plan){
  if(body.equals(plan.sourceBody())||!owner.equals(plan.owner())||!dimension.equals(plan.destinationDimension())||!encode().equals(plan.destinationRoute()))throw new IllegalArgumentException("Journey does not commit this exact distinct owned destination");
 }
}
