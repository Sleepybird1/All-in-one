package dev.godpc.industrialcolonies.space.enemy;

import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3d;
import java.util.*;

/** Read-only same-tick complete owned cannon geometry. Native CBC attachment
 * AABBs and toGlobalVector results are plot coordinates, not physical space.
 * Each gun reserves its full pivot-centred rotation sphere, so future turret
 * motion cannot escape the admitted assembly bounds. Unknown entities are not
 * adopted. Private construction prevents caller-supplied exclusion lists. */
public final class EnemyMountedAssembly {
    private record Part(Entity entity,AABB raw,AABB physical,AABB allRotation) {}
    private final ServerSubLevel body;
    private final long tick;
    private final EnemyMountedCannonCustody.Snapshot custody;
    private final Map<UUID,Part> parts;
    private final AABB bounds;
    private EnemyMountedAssembly(ServerSubLevel body,EnemyMountedCannonCustody.Snapshot custody,
            Map<UUID,Part> parts,AABB bounds) {
        this.body=body;this.custody=custody;this.parts=Map.copyOf(parts);this.bounds=bounds;
        tick=body.getLevel().getGameTime();
    }
    public static Optional<EnemyMountedAssembly> sample(ServerSubLevel body) {
        if(body==null||body.isRemoved()||!body.getLevel().getServer().isSameThread())return Optional.empty();
        try {
            var custody=EnemyMountedCannonCustody.readHeld(body);
            var parts=new HashMap<UUID,Part>();AABB bounds=body.boundingBox().toMojang();
            if(!finite(bounds))return Optional.empty();
            // Native cached hull bounds can refresh after a server sample.
            // Preserve them and include every current logical-pose voxel corner.
            var plot=body.getPlot().getBoundingBox();if(plot==null)return Optional.empty();
            bounds=bounds.minmax(transformBox(body,new AABB(plot.minX(),plot.minY(),plot.minZ(),
                    (double)plot.maxX()+1,(double)plot.maxY()+1,(double)plot.maxZ()+1)));
            if(custody.attachments().isEmpty())return Optional.of(new EnemyMountedAssembly(body,custody,parts,bounds));
            for(var attachment:custody.attachments()) {
                Entity entity=body.getLevel().getEntity(attachment.entity());
                if(entity==null||entity.isRemoved())return Optional.empty();
                AABB raw=entity.getBoundingBox();if(!finite(raw))return Optional.empty();
                var transform=entity.getClass().getMethod("toGlobalVector",Vec3.class,float.class);
                Vec3 pivot=(Vec3)transform.invoke(entity,Vec3.atCenterOf(BlockPos.ZERO),0f);
                if(!finite(pivot))return Optional.empty();
                Object contraption=entity.getClass().getMethod("getContraption").invoke(entity);
                var blocks=(Map<?,?>)contraption.getClass().getMethod("getBlocks").invoke(contraption);
                if(blocks.size()!=attachment.blocks())return Optional.empty();
                double radius=0;
                // Every complete owned block corner must be represented in the
                // actual native attachment AABB before deriving a rotation reserve.
                for(Object key:blocks.keySet()) {
                    if(!(key instanceof BlockPos p))return Optional.empty();
                    for(int x=0;x<=1;x++)for(int y=0;y<=1;y++)for(int z=0;z<=1;z++) {
                        Vec3 point=(Vec3)transform.invoke(entity,new Vec3(p.getX()+x,p.getY()+y,p.getZ()+z),0f);
                        if(!finite(point)||!raw.inflate(.002).contains(point))return Optional.empty();
                        radius=Math.max(radius,pivot.distanceTo(point));
                    }
                }
                // The raw native box can include additional collision padding.
                for(Vec3 point:corners(raw))radius=Math.max(radius,pivot.distanceTo(point));
                if(!Double.isFinite(radius)||radius<=0||radius>16)return Optional.empty();
                var physical=transformBox(body,raw);var center=body.logicalPose().transformPosition(new Vector3d(pivot.x,pivot.y,pivot.z));
                if(!center.isFinite()||!finite(physical))return Optional.empty();
                var rotation=new AABB(center.x-radius,center.y-radius,center.z-radius,
                        center.x+radius,center.y+radius,center.z+radius).inflate(.002);
                if(!finite(rotation)||!contains(rotation,physical))return Optional.empty();
                parts.put(entity.getUUID(),new Part(entity,raw,physical,rotation));bounds=bounds.minmax(rotation);
            }
            if(!custody.equals(EnemyMountedCannonCustody.readHeld(body)))return Optional.empty();
            if(!finite(bounds)||bounds.getXsize()>48||bounds.getYsize()>48||bounds.getZsize()>48)return Optional.empty();
            return Optional.of(new EnemyMountedAssembly(body,custody,parts,bounds));
        }catch(ReflectiveOperationException|java.io.IOException|RuntimeException unavailable){return Optional.empty();}
    }
    public boolean current(ServerSubLevel candidate) {
        if(candidate!=body||body.getLevel().getGameTime()!=tick)return false;
        return sample(body).filter(fresh->custody.equals(fresh.custody)&&parts.equals(fresh.parts)&&bounds.equals(fresh.bounds)).isPresent();
    }
    public boolean owns(Entity entity){var part=entity==null?null:parts.get(entity.getUUID());return part!=null&&part.entity()==entity;}
    public AABB bounds(){return bounds;}
    public int attachments(){return parts.size();}
    public Map<UUID,AABB> physicalAttachments(){var result=new HashMap<UUID,AABB>();parts.forEach((id,part)->result.put(id,part.physical()));return Map.copyOf(result);}
    public Map<UUID,AABB> rotationReserves(){var result=new HashMap<UUID,AABB>();parts.forEach((id,part)->result.put(id,part.allRotation()));return Map.copyOf(result);}
    private static AABB transformBox(ServerSubLevel body,AABB raw) {
        double minX=Double.POSITIVE_INFINITY,minY=minX,minZ=minX,maxX=Double.NEGATIVE_INFINITY,maxY=maxX,maxZ=maxX;
        for(Vec3 point:corners(raw)){
            var p=body.logicalPose().transformPosition(new Vector3d(point.x,point.y,point.z));
            minX=Math.min(minX,p.x);minY=Math.min(minY,p.y);minZ=Math.min(minZ,p.z);
            maxX=Math.max(maxX,p.x);maxY=Math.max(maxY,p.y);maxZ=Math.max(maxZ,p.z);
        }
        return new AABB(minX,minY,minZ,maxX,maxY,maxZ);
    }
    private static List<Vec3> corners(AABB b){var out=new ArrayList<Vec3>();for(double x:new double[]{b.minX,b.maxX})for(double y:new double[]{b.minY,b.maxY})for(double z:new double[]{b.minZ,b.maxZ})out.add(new Vec3(x,y,z));return out;}
    private static boolean finite(Vec3 p){return Double.isFinite(p.x)&&Double.isFinite(p.y)&&Double.isFinite(p.z);}
    private static boolean finite(AABB b){return finite(new Vec3(b.minX,b.minY,b.minZ))&&finite(new Vec3(b.maxX,b.maxY,b.maxZ))&&Math.abs(b.minX)<30000000&&Math.abs(b.maxX)<30000000&&Math.abs(b.minZ)<30000000&&Math.abs(b.maxZ)<30000000;}
    private static boolean contains(AABB outer,AABB inner){return inner.minX>=outer.minX&&inner.maxX<=outer.maxX&&inner.minY>=outer.minY&&inner.maxY<=outer.maxY&&inner.minZ>=outer.minZ&&inner.maxZ<=outer.maxZ;}
}
