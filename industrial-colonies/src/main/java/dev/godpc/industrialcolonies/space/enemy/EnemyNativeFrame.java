package dev.godpc.industrialcolonies.space.enemy;
import dev.devce.rocketnautics.content.orbit.DeepSpaceData;
import dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import org.joml.Vector3d;
import java.util.Optional;
/** Fresh native frame identity only; never propulsion or encounter authority. */
public final class EnemyNativeFrame {
    public record Key(String dimension,long instance) {}
    private EnemyNativeFrame() {}
    public static Optional<Key> read(ServerSubLevel body) {
        if(body==null||body.isRemoved()||!body.getLevel().getServer().isSameThread())return Optional.empty();
        try {
            if(!RigidBodyHandle.of(body).isValid())return Optional.empty();
            String dimension=body.getLevel().dimension().location().toString();
            if(!dimension.equals("rocketnautics:deep_space"))return Optional.of(new Key(dimension,-1));
            var p=body.logicalPose().transformPosition(new Vector3d(body.getMassTracker().getCenterOfMass()));
            if(!p.isFinite()||p.x<Integer.MIN_VALUE||p.x>Integer.MAX_VALUE||p.z<Integer.MIN_VALUE||p.z>Integer.MAX_VALUE)return Optional.empty();
            var instance=DeepSpaceData.getInstance(body.getLevel().getServer()).getInstanceForPos((int)Math.floor(p.x),(int)Math.floor(p.z));
            if(instance==null||instance.isCorrupted()||instance.getPosition()==null||instance.getPosition().isCorrupted()
                    ||!instance.boundingBox().contains(p.x,p.y,p.z))return Optional.empty();
            var bounds=body.boundingBox().toMojang();
            for(double x:new double[]{bounds.minX,bounds.maxX})for(double y:new double[]{bounds.minY,bounds.maxY})for(double z:new double[]{bounds.minZ,bounds.maxZ})
                if(!Double.isFinite(x)||!Double.isFinite(y)||!Double.isFinite(z)||!instance.boundingBox().contains(x,y,z))return Optional.empty();
            return Optional.of(new Key(dimension,instance.getId()));
        }catch(RuntimeException unavailable){return Optional.empty();}
    }
    public static boolean common(ServerSubLevel source,ServerSubLevel target) {
        if(source==null||target==null||source.getLevel()!=target.getLevel())return false;
        var a=read(source);return a.isPresent()&&a.equals(read(target));
    }
    /** Complete physical volume containment, not just containing COM. Orbital
     * entities live in native cells above the ordinary block-building range. */
    public static boolean contains(ServerSubLevel body,net.minecraft.world.phys.AABB bounds) {
        if(bounds==null)return false;
        var key=read(body);if(key.isEmpty())return false;
        try {
            for(double x:new double[]{bounds.minX,bounds.maxX})for(double y:new double[]{bounds.minY,bounds.maxY})for(double z:new double[]{bounds.minZ,bounds.maxZ})
                if(!Double.isFinite(x)||!Double.isFinite(y)||!Double.isFinite(z))return false;
            if(!key.get().dimension().equals("rocketnautics:deep_space"))return true;
            var instance=DeepSpaceData.getInstance(body.getLevel().getServer()).getInstance(key.get().instance());
            if(instance==null||instance.isCorrupted()||instance.getPosition()==null||instance.getPosition().isCorrupted())return false;
            for(double x:new double[]{bounds.minX,bounds.maxX})for(double y:new double[]{bounds.minY,bounds.maxY})for(double z:new double[]{bounds.minZ,bounds.maxZ})
                if(!instance.boundingBox().contains(x,y,z))return false;
            return true;
        }catch(RuntimeException unavailable){return false;}
    }
}
