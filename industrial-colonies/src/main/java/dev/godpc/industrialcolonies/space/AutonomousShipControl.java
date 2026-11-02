package dev.godpc.industrialcolonies.space;

import java.util.*;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.*;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
import net.sprocketgames.create_aeronautics_automated_logistics.identity.ShipTransponderRegistry;
import net.sprocketgames.create_aeronautics_automated_logistics.route.Route;

/** Server-wide administrative switches keyed by persistent transponder identity. */
public final class AutonomousShipControl extends SavedData {
 public static final String FILE="industrial_colonies_ship_controls";
 public static final Factory<AutonomousShipControl> FACTORY=new Factory<>(AutonomousShipControl::new,AutonomousShipControl::load);
 private boolean allDisabled,invalid;
 private long chemicalDockRevision;
 public long chemicalDockRevision(){return chemicalDockRevision;}
 private CompoundTag rejected;
 private final Set<UUID> disabled=new HashSet<>();
 public static AutonomousShipControl get(MinecraftServer server){return server.overworld().getDataStorage().computeIfAbsent(FACTORY,FILE);}
 public boolean allDisabled(){return allDisabled||invalid;}
 public boolean disabled(UUID id){return allDisabled()||disabled.contains(id);}
 public Set<UUID> individuallyDisabled(){return Set.copyOf(disabled);}
 public void setAllDisabled(boolean value){requireValid();allDisabled=value;chemicalDockRevision++;setDirty();}
 public void setDisabled(UUID id,boolean value){requireValid();if(value)disabled.add(id);else disabled.remove(id);chemicalDockRevision++;setDirty();}
 private void requireValid(){if(invalid)throw new IllegalStateException("Ship controls contain invalid saved data; preserved and held disabled.");}
 public static AutonomousShipControl load(CompoundTag tag,HolderLookup.Provider registries){
  var result=new AutonomousShipControl();
  try{
   if(!tag.contains("format",Tag.TAG_INT)||tag.getInt("format")!=1||!tag.contains("allDisabled",Tag.TAG_BYTE)||!tag.contains("disabled",Tag.TAG_LIST))throw new IllegalArgumentException("Invalid ship-control schema");
   var list=tag.getList("disabled",Tag.TAG_STRING);if(list.size()!=((ListTag)tag.get("disabled")).size())throw new IllegalArgumentException("Invalid identity list");
   for(Tag entry:list)if(!result.disabled.add(UUID.fromString(entry.getAsString())))throw new IllegalArgumentException("Duplicate identity");
   result.allDisabled=tag.getBoolean("allDisabled");
  }catch(RuntimeException failure){result.invalid=true;result.rejected=tag.copy();}
  return result;
 }
 @Override public CompoundTag save(CompoundTag tag,HolderLookup.Provider registries){
  if(invalid)return rejected.copy();
  tag.putInt("format",1);tag.putBoolean("allDisabled",allDisabled);var ids=new ListTag();disabled.stream().map(UUID::toString).sorted().forEach(id->ids.add(StringTag.valueOf(id)));tag.put("disabled",ids);return tag;
 }
 public static boolean blocksRoute(MinecraftServer server,Route route){
  var control=get(server);if(control.allDisabled())return true;
  if(route.linkedController().vehicleId().filter(id->blocksVehicle(server,route.dimension(),id)).isPresent())return true;
  // Native persistent transponder records retain the body association through unload.
  return ShipTransponderRegistry.allShips().stream().anyMatch(s->control.disabled(s.transponderId())&&
   (s.controllerRef().filter(ref->ref.matches(route.linkedController())).isPresent()||
    s.runtimeShipId().isPresent()&&s.runtimeShipId().equals(route.linkedController().vehicleId())));
 }
 public static boolean blocksVehicle(MinecraftServer server,net.minecraft.resources.ResourceKey<net.minecraft.world.level.Level> dimension,UUID id){
  var level=server.getLevel(dimension);if(level==null)return false;
  var container=dev.ryanhcode.sable.api.sublevel.SubLevelContainer.getContainer(level);if(container==null)return false;
  var body=container.getSubLevel(id);
  return body instanceof dev.ryanhcode.sable.sublevel.ServerSubLevel ship && SpaceflightAuthorization.automationDisabled(ship);
 }
}
