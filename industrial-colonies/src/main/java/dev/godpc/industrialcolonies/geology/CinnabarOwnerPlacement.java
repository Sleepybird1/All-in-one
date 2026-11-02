package dev.godpc.industrialcolonies.geology;

import java.io.IOException;
import java.util.*;
import static dev.godpc.industrialcolonies.geology.GeologyMath.Voxel;

/** Shared-ledger owner transaction. Caller validates native stage and saved selection authority. */
public final class CinnabarOwnerPlacement {
    public enum Material { REPLACEABLE, CINNABAR, OTHER }
    public enum Status { WRITTEN, HELD_SURFACE, HELD_WRITE }
    public record Result(Status status,int expected,int written) {}
    public record Intent(int chunkX,int chunkZ,String identity,Map<Voxel,String> targets){
        public Intent {
            targets=Map.copyOf(targets);
            if(identity==null||!identity.matches("[a-f0-9]{64}")||targets.entrySet().stream().anyMatch(e->!owns(chunkX,chunkZ,e.getKey())||!e.getValue().matches("[a-f0-9]{64}")))throw new IllegalArgumentException("Invalid surface owner intent");
        }
        public Set<String> provenanceKeys(){return Set.copyOf(targets.values());}
    }
    /** Full saved selection identity and exact local reservations, before underground owner writes. */
    public static Intent intent(int chunkX,int chunkZ,List<CinnabarConcentrations.Selection> selections){
        if(selections.isEmpty())throw new IllegalArgumentException("Explicit saved surface selections required");
        var hashes=new TreeSet<String>();var targets=new HashMap<Voxel,String>();
        for(var selection:selections){
            if(!selection.geometry().admitted())throw new IllegalArgumentException("Selected admitted geometry required");
            String key=CinnabarSelectionJournal.geometryHash(selection);if(!hashes.add(key))throw new IllegalArgumentException("Duplicate surface selection");
            for(var voxel:selection.geometry().blocks())if(owns(chunkX,chunkZ,voxel)&&targets.putIfAbsent(voxel,key)!=null)throw new IllegalArgumentException("Overlapping surface reservations");
        }
        String text="IC_SURFACE_OWNER_V1\n"+chunkX+":"+chunkZ+"\n"+String.join("\n",hashes);
        try{return new Intent(chunkX,chunkZ,HexFormat.of().formatHex(java.security.MessageDigest.getInstance("SHA-256").digest(text.getBytes(java.nio.charset.StandardCharsets.UTF_8))),targets);}
        catch(java.security.NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
    }
    public interface Access {
        Material material(Voxel position)throws IOException;
        boolean exterior(CinnabarSurfaceGeometry.Face face)throws IOException;
        boolean write(Voxel position)throws IOException;
        void record(String key,Voxel position)throws IOException;
        void abort()throws IOException;
    }
    private CinnabarOwnerPlacement(){}
    public static Result place(int chunkX,int chunkZ,List<CinnabarConcentrations.Selection> selections,Access access)throws IOException{
        Objects.requireNonNull(selections);Objects.requireNonNull(access);
        var targets=new TreeMap<Voxel,String>(Comparator.comparingInt(Voxel::x).thenComparingInt(Voxel::y).thenComparingInt(Voxel::z));
        var relevant=new ArrayList<CinnabarSurfaceGeometry.Stroke>();
        for(var selection:selections){
            if(!selection.geometry().admitted())throw new IllegalArgumentException("Selected admitted geometry required");
            String key=CinnabarSelectionJournal.geometryHash(selection);
            for(var voxel:selection.geometry().blocks())if(owns(chunkX,chunkZ,voxel)&&targets.putIfAbsent(voxel,key)!=null)throw new IllegalArgumentException("Overlapping concentration ownership");
            for(var stroke:selection.geometry().strokes())if(stroke.blocks().stream().anyMatch(v->owns(chunkX,chunkZ,v)))relevant.add(stroke);
        }
        int written=0;
        try{
            // Validate the complete local request before the first write. Foreign stroke prefixes may
            // already be natural ore, but preexisting local ore never becomes newly claimed reserve.
            for(var stroke:relevant){
                var front=access.material(stroke.face().front());
                if(front==Material.OTHER||!access.exterior(stroke.face())){access.abort();return new Result(Status.HELD_SURFACE,targets.size(),0);}
                int last=-1;for(int i=0;i<stroke.blocks().size();i++)if(owns(chunkX,chunkZ,stroke.blocks().get(i)))last=i;
                for(int i=0;i<=last;i++)if(access.material(stroke.blocks().get(i))==Material.OTHER){access.abort();return new Result(Status.HELD_SURFACE,targets.size(),0);}
            }
            for(var position:targets.keySet())if(access.material(position)!=Material.REPLACEABLE){access.abort();return new Result(Status.HELD_SURFACE,targets.size(),0);}
            for(var entry:targets.entrySet()){
                Voxel position=entry.getKey();
                if(access.material(position)!=Material.REPLACEABLE||!access.write(position)||access.material(position)!=Material.CINNABAR){access.abort();return new Result(Status.HELD_WRITE,targets.size(),written);}
                written++;access.record(entry.getValue(),position);
            }
            return new Result(Status.WRITTEN,targets.size(),written);
        }catch(IOException|RuntimeException|Error failure){
            try{access.abort();}catch(IOException|RuntimeException abort){failure.addSuppressed(abort);}throw failure;
        }
    }
    private static boolean owns(int x,int z,Voxel position){return(position.x()>>4)==x&&(position.z()>>4)==z;}
}
