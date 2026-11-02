package dev.godpc.industrialcolonies.space;

import java.util.*;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.*;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

/** Human-readable names point to immutable references; journeys store the reference itself. */
public final class FreightDestinationBook extends SavedData {
 public static final String FILE="industrial_colonies_freight_destinations";
 public static final Factory<FreightDestinationBook> FACTORY=new Factory<>(FreightDestinationBook::new,FreightDestinationBook::load);
 private final Map<String,FreightDestinationReference> entries=new TreeMap<>();
 private CompoundTag rejected;
 public static FreightDestinationBook get(MinecraftServer server){
  if(!server.isSameThread())throw new IllegalStateException("Destination directory requires server thread");
  return server.overworld().getDataStorage().computeIfAbsent(FACTORY,FILE);
 }
 public static void name(String name){if(name==null||!name.matches("[a-z0-9][a-z0-9_-]{0,47}"))throw new IllegalArgumentException("Destination name must be 1-48 lowercase letters, digits, underscores or hyphens");}
 private void healthy(){if(rejected!=null)throw new IllegalStateException("Invalid destination directory retained; new binding refused");}
 public Optional<FreightDestinationReference> find(String name){healthy();name(name);return Optional.ofNullable(entries.get(name));}
 public Map<String,FreightDestinationReference> entries(){healthy();return Collections.unmodifiableMap(new TreeMap<>(entries));}
 public void bind(String name,FreightDestinationReference reference){
  healthy();name(name);Objects.requireNonNull(reference);var old=entries.get(name);
  if(old!=null&&!old.equals(reference))throw new IllegalStateException("Destination name already identifies another dock; explicit forgetting is required");
  if(old==null){entries.put(name,reference);setDirty();}
 }
 public void forget(String name,UUID owner,FreightJourneyJournal journal){
  var ref=find(name).orElseThrow(()->new IllegalArgumentException("Unknown destination"));
  if(!ref.owner().equals(owner))throw new IllegalStateException("Destination belongs to another owner");
  if(!journal.fault().isEmpty()||journal.entries().stream().anyMatch(e->!e.phase().terminal()&&e.plan().destinationRoute().equals(ref.encode())))throw new IllegalStateException("An unfinished journey still commits this destination");
  entries.remove(name);setDirty();
 }
 public static FreightDestinationBook load(CompoundTag tag,HolderLookup.Provider registries){
  var book=new FreightDestinationBook();
  try{
   if(!tag.contains("format",Tag.TAG_INT)||tag.getInt("format")!=1||!tag.contains("destinations",Tag.TAG_LIST))throw new IllegalArgumentException("Unknown destination directory schema");
   var list=tag.getList("destinations",Tag.TAG_COMPOUND);if(list.size()!=((ListTag)tag.get("destinations")).size())throw new IllegalArgumentException("Invalid destination entries");
   for(Tag entry:list){var row=(CompoundTag)entry;if(!row.contains("name",Tag.TAG_STRING)||!row.contains("reference",Tag.TAG_STRING))throw new IllegalArgumentException("Incomplete destination entry");
    String name=row.getString("name");name(name);var ref=FreightDestinationReference.decode(row.getString("reference"));if(book.entries.putIfAbsent(name,ref)!=null)throw new IllegalArgumentException("Duplicate destination name");
   }
  }catch(RuntimeException failure){book.rejected=tag.copy();book.entries.clear();}
  return book;
 }
 @Override public CompoundTag save(CompoundTag tag,HolderLookup.Provider registries){
  if(rejected!=null)return rejected.copy();tag.putInt("format",1);var list=new ListTag();
  entries.forEach((name,ref)->{var row=new CompoundTag();row.putString("name",name);row.putString("reference",ref.encode());list.add(row);});tag.put("destinations",list);return tag;
 }
}
