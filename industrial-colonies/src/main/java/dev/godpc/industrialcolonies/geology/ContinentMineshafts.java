package dev.godpc.industrialcolonies.geology;

import java.util.*;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.structures.MineshaftPieces;

/** Opt-in adapter for an already resolved, immutable continent snapshot. Never starts a search. */
public final class ContinentMineshafts {
 private ContinentMineshafts(){}
 /** Caller must supply the current coordinator snapshot before structure admission; no legacy fallback. */
 public static boolean attach(Structure.GenerationContext context,Structure.GenerationStub stub,List<MiningScanScope> admitted){
  return attach(context,stub,admitted,net.minecraft.world.level.levelgen.structure.structures.MineshaftStructure.Type.NORMAL);
 }
 public static boolean attach(Structure.GenerationContext context,Structure.GenerationStub stub,List<MiningScanScope> admitted,net.minecraft.world.level.levelgen.structure.structures.MineshaftStructure.Type type){
  var scopes=validatedAcrossContinents(admitted,context.seed(),context.heightAccessor().getMinBuildHeight(),context.heightAccessor().getMaxBuildHeight());
  var builder=stub.getPiecesBuilder();var original=builder.build().pieces();
  var existing=original.stream().filter(p->p instanceof MassiveMinePiece).map(p->(MassiveMinePiece)p).toList();
  if(!existing.isEmpty())throw new IllegalStateException("Mine already has a saved deposit association");
  if(original.stream().anyMatch(p->p instanceof MineshaftVeinPiece))throw new IllegalStateException("Legacy ore-generating mine cannot acquire a second reserve");
  var rooms=original.stream().filter(p->p instanceof MineshaftPieces.MineShaftRoom).toList();
  if(rooms.size()!=1)return false;var room=rooms.getFirst();
  for(var scope:scopes){
   var config=GeologyConfig.get();
   var definition=GeologyConfig.array(config.deposits(),"deposits").asList().stream()
       .map(e->e.getAsJsonObject()).filter(d->d.get("id").getAsString().equals(scope.family()))
       .findFirst().orElseThrow(()->new IllegalStateException("Missing finite mine family"));
   var allocation=new WorldStartAllocation.Scope(scope.worldSeed(),scope.dimension(),scope.presetSha256(),scope.continentKey());
   if(!WorldStartMinePolicy.allows(config.settings(),definition,allocation,scope.key()))continue;
   if(WorldStartMinePolicy.enabled(config.settings())&&ContinentMineContext.scheduled(context)){
    var layout=ContinentMineScheduler.fit(original,room,scope,type);
    builder.clear();layout.pieces().forEach(builder::addPiece);builder.addPiece(layout.marker());return true;
   }
   var retained=MassiveMineshafts.fit(original,room,scope);
   if(retained.isEmpty())continue;
   var marker=new MassiveMinePiece(room.getBoundingBox(),scope);
   // All validation precedes mutation; existing vanilla piece coordinates are retained.
   builder.clear();retained.forEach(builder::addPiece);builder.addPiece(marker);return true;
  }
  return false;
 }
 /** Pure input admission shared by native bridge and offline tests. */
 public static List<MiningScanScope> validated(List<MiningScanScope> admitted,long seed,int minY,int maxY){
  var result=validatedAcrossContinents(admitted,seed,minY,maxY);
  if(result.stream().map(MiningScanScope::continentKey).distinct().count()>1)throw new IllegalArgumentException("Single continent required");
  return result;
 }
 /** Explicit border admission permits different continents, but never two outcomes for one family/key. */
 public static List<MiningScanScope> validatedAcrossContinents(List<MiningScanScope> admitted,long seed,int minY,int maxY){
  Objects.requireNonNull(admitted);if(admitted.size()>128)throw new IllegalArgumentException("Bounded continent scope list required");
  var scopes=new ArrayList<MiningScanScope>();var seen=new HashSet<String>();String preset=null;
  for(var s:admitted){
   Objects.requireNonNull(s);if(!s.isContinent()||s.worldSeed()!=seed||!s.dimension().equals("minecraft:overworld")||s.minBuildY()!=minY||s.maxBuildYExclusive()!=maxY)throw new IllegalArgumentException("Mine scope world/build identity mismatch");
   if(preset==null)preset=s.presetSha256();
   if(!preset.equals(s.presetSha256())||!seen.add(s.continentKey()+"/"+s.depositSlot()))throw new IllegalArgumentException("Mixed preset or duplicate continent/deposit mine scope");
   scopes.add(s);
  }
  scopes.sort(Comparator.comparing(MiningScanScope::key));return List.copyOf(scopes);
 }
}
