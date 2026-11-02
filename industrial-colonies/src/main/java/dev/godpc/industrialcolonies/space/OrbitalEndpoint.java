package dev.godpc.industrialcolonies.space;

import java.util.*;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;

/** Read-only endpoint evidence. Native instance center and local body motion stay
 * separate until an adapter has verified their coordinate conversion. */
public record OrbitalEndpoint(UUID body,String dimension,long instance,String frame,long serverTick,
                              long universeTick,int timescale,V celestialPosition,V celestialVelocity,
                              V localOffset,V localVelocity,double mu,double planetRadius,
                              boolean sphere,double surfaceDistance,double transitionHeight) {
 public OrbitalEndpoint {
  Objects.requireNonNull(body);
  if(dimension==null||dimension.isBlank()||frame==null||frame.isBlank()||serverTick<0||universeTick<0||timescale<1)throw new IllegalArgumentException("Invalid endpoint identity or clock");
  for(V vector:List.of(celestialPosition,celestialVelocity,localOffset,localVelocity))if(!vector.finite()||!Double.isFinite(vector.length()))throw new IllegalArgumentException("Nonfinite endpoint vector");
  for(double value:new double[]{mu,planetRadius,transitionHeight})if(!Double.isFinite(value)||value<=0)throw new IllegalArgumentException("Invalid native planet geometry");
  if(celestialPosition.length()<=0||!Double.isFinite(surfaceDistance)||surfaceDistance<0)throw new IllegalArgumentException("Invalid native orbital position");
 }
 public enum Relation { SHARED_NATIVE_INSTANCE, INDEPENDENT_NATIVE_INSTANCES }
 public record Pair(OrbitalEndpoint ship,OrbitalEndpoint destination,Relation relation){}
 public static Pair pair(OrbitalEndpoint ship,OrbitalEndpoint destination){
  Objects.requireNonNull(ship);Objects.requireNonNull(destination);
  if(ship.body.equals(destination.body))throw new IllegalArgumentException("Distinct physical destination required");
  if(!ship.dimension.equals(destination.dimension)||!ship.frame.equals(destination.frame)||ship.mu!=destination.mu||ship.planetRadius!=destination.planetRadius||ship.sphere!=destination.sphere||ship.transitionHeight!=destination.transitionHeight)throw new IllegalArgumentException("Endpoint frames or planet definitions differ");
  if(ship.serverTick!=destination.serverTick||ship.universeTick!=destination.universeTick||ship.timescale!=1||destination.timescale!=1)throw new IllegalArgumentException("Endpoints require one synchronized ordinary-time observation");
  boolean shared=ship.instance==destination.instance;
  if(shared&&(!ship.celestialPosition.equals(destination.celestialPosition)||!ship.celestialVelocity.equals(destination.celestialVelocity)))throw new IllegalArgumentException("Shared instance reported inconsistent celestial state");
  return new Pair(ship,destination,shared?Relation.SHARED_NATIVE_INSTANCE:Relation.INDEPENDENT_NATIVE_INSTANCES);
 }
}
