package dev.godpc.industrialcolonies.space;

import java.util.*;
import dev.devce.rocketnautics.content.orbit.DeepSpaceData;
import net.minecraft.server.MinecraftServer;

/** Read-only native instance registries, not a persisted holding-storage audit.
 * A loaded body list alone cannot establish exclusive custody after a restart.
 */
public record OrbitalInstanceMembership(long instance,long serverTick,Set<UUID> loadedBodies,
                                      Set<UUID> unloadedBodies,Set<UUID> onlinePlayers,
                                      Set<UUID> offlinePlayers) {
 public OrbitalInstanceMembership {
  loadedBodies=Set.copyOf(loadedBodies);unloadedBodies=Set.copyOf(unloadedBodies);
  onlinePlayers=Set.copyOf(onlinePlayers);offlinePlayers=Set.copyOf(offlinePlayers);
  if(serverTick<0)throw new IllegalArgumentException("Invalid observation clock");
  if(!Collections.disjoint(loadedBodies,unloadedBodies)||!Collections.disjoint(onlinePlayers,offlinePlayers))
   throw new IllegalArgumentException("Conflicting native membership");
 }
 /** Necessary but insufficient for rebase: no cargo, ownership, entity, lease,
  * collision or persisted storage claim follows from this registry observation. */
 public boolean soleLoadedBodyWithoutPlayers(UUID body) {
  return loadedBodies.equals(Set.of(body))&&unloadedBodies.isEmpty()&&onlinePlayers.isEmpty()&&offlinePlayers.isEmpty();
 }
 public static OrbitalInstanceMembership read(MinecraftServer server,OrbitalEndpoint endpoint) {
  if(!server.isSameThread()||endpoint.serverTick()!=server.getTickCount())throw new IllegalStateException("Fresh server-thread endpoint required");
  var nativeInstance=DeepSpaceData.getInstance(server).getInstance(endpoint.instance());
  if(nativeInstance==null||nativeInstance.isCorrupted()||nativeInstance.getPosition().getLocalUniverseTicks()!=endpoint.universeTick())
   throw new IllegalStateException("Native instance changed since endpoint observation");
  var loaded=new HashSet<UUID>();var online=new HashSet<UUID>();
  nativeInstance.collectLoadedSublevels(server,b->{if(b.isRemoved()||!loaded.add(b.getUniqueId()))throw new IllegalStateException("Invalid loaded body membership");});
  nativeInstance.collectOnlinePlayers(server,p->{if(!online.add(p.getUUID()))throw new IllegalStateException("Duplicate online player membership");});
  var result=new OrbitalInstanceMembership(endpoint.instance(),server.getTickCount(),loaded,nativeInstance.getUnloadedSublevels().keySet(),online,nativeInstance.getOfflinePlayers().keySet());
  if(!result.loadedBodies().contains(endpoint.body()))throw new IllegalStateException("Endpoint body is no longer a member");
  return result;
 }
}
