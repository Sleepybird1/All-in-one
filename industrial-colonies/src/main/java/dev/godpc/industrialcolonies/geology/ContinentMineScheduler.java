package dev.godpc.industrialcolonies.geology;

import java.util.*;
import com.google.gson.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.structures.MineshaftStructure;

/** Fresh native structure starts only: one deterministic anchor per selected existing vein.
 * No new reserve, distance exclusion, saved-start retrofit or retry-based occurrence roll. */
public final class ContinentMineScheduler {
 public record Layout(List<StructurePiece> pieces,MassiveMinePiece marker){
  public Layout{pieces=List.copyOf(pieces);Objects.requireNonNull(marker);}
 }
 private ContinentMineScheduler(){}
 public static ChunkPos anchor(MiningScanScope scope){
  if(!scope.isContinent())throw new IllegalArgumentException("Existing finite mineral/seam reservation required");
  var c=scope.reservedCandidate();return new ChunkPos(c.x()>>4,c.z()>>4);
 }
 private static com.google.gson.JsonObject definition(String family){
  return GeologyConfig.get().deposits().getAsJsonArray("deposits").asList().stream().map(com.google.gson.JsonElement::getAsJsonObject)
      .filter(d->d.get("id").getAsString().equals(family)).findFirst().orElseThrow();
 }
 public static void starts(ServerLevel level,ChunkAccess owner,List<MiningScanScope> admitted){
  var settings=GeologyConfig.get().settings();if(!WorldStartMinePolicy.enabled(settings))return;
  if(!level.getServer().isSameThread()||owner.isUpgrading()||!owner.getPersistedStatus().isBefore(net.minecraft.world.level.chunk.status.ChunkStatus.STRUCTURE_STARTS))throw new IllegalStateException("Fresh native structure owner required");
  var selected=new ArrayList<MiningScanScope>();
  for(var scope:ContinentMineshafts.validatedAcrossContinents(admitted,level.getSeed(),level.getMinBuildHeight(),level.getMaxBuildHeight())){
   if(!anchor(scope).equals(owner.getPos()))continue;
   var allocation=new WorldStartAllocation.Scope(scope.worldSeed(),scope.dimension(),scope.presetSha256(),scope.continentKey());
   if(WorldStartMinePolicy.allows(settings,definition(scope.family()),allocation,scope.key()))selected.add(scope);
  }
  if(selected.isEmpty())return;
  // Existing finite bodies cannot overlap; an unexpected anchor collision holds rather than
  // dropping one selected vein or placing two starts under the same native structure key.
  if(selected.size()!=1)throw new IllegalStateException("Distinct selected veins share one native mine anchor");
  var scope=selected.getFirst();
  var structure=level.registryAccess().registryOrThrow(Registries.STRUCTURE).get(ResourceLocation.withDefaultNamespace("mineshaft"));
  if(!(structure instanceof MineshaftStructure))throw new IllegalStateException("Native mineshaft definition required");
  if(owner.getStartForStructure(structure)!=null&&owner.getStartForStructure(structure).isValid())throw new IllegalStateException("Existing native mine start cannot be replaced");
  var source=level.getChunkSource();var generator=source.getGenerator();
  var start=ContinentMineContext.scheduled(level,scope,()->structure.generate(level.registryAccess(),generator,generator.getBiomeSource(),source.randomState(),level.getStructureManager(),level.getSeed(),owner.getPos(),0,level,biome->true));
  long markers=start.getPieces().stream().filter(p->p instanceof MassiveMinePiece).count();
  if(!start.isValid()||markers!=1)throw new IllegalStateException("Selected finite mine did not form; preserve selected occurrence and hold: scope="+scope.key()+", valid="+start.isValid()+", pieces="+start.getPieces().size()+", markers="+markers);
  owner.setStartForStructure(structure,start);owner.setUnsaved(true);
 }
 /** Connect the complete native mine to the original finite vein; tunnels may extend beyond it. */
 static Layout fit(List<StructurePiece> original,StructurePiece room,MiningScanScope scope,MineshaftStructure.Type type){
  if(original.isEmpty()||!original.contains(room))throw new IllegalArgumentException("Original native room/pieces required");
  var b=room.getBoundingBox();
  var placement=VeinMineSiting.site(scope,new MassiveDepositGeometry.Bounds(b.minX(),b.minY(),b.minZ(),b.maxX(),b.maxY(),b.maxZ()));
  for(var piece:original)piece.move(placement.dx(),placement.dy(),placement.dz());
  var moved=room.getBoundingBox();
  if(moved.getCenter().getX()!=placement.nodeX()||moved.minY()+1!=placement.nodeY()||moved.getCenter().getZ()!=placement.nodeZ())
   throw new IllegalStateException("Native room/node siting differs from admitted vein connection");
  return new Layout(List.copyOf(original),new MassiveMinePiece(moved,scope));
 }
}
