package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;

/** Durable start intent for the coal stage inside an already commissioned continent. */
public final class CoalRuntimeCommission {
    public record Admission(CoalAllocationJournal allocation,Path searchDirectory,boolean existing){}
    private final Path base;
    private final CoalRuntimePolicy policy;
    private final ContinentResourceDecision.Scope scope;
    private final ReTerraForgedGeography.ContinentKey key;
    private final ContinentCoordinatorManifest manifest;
    private CoalRuntimeCommission(boolean create,Path base,CoalRuntimePolicy policy,ContinentResourceDecision.Scope scope,
            ReTerraForgedGeography.ContinentKey key)throws IOException {
        this.base=base.toAbsolutePath().normalize();this.policy=Objects.requireNonNull(policy);this.scope=Objects.requireNonNull(scope);this.key=Objects.requireNonNull(key);
        String identity;
        try{identity=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(("IC_COAL_COMMISSION_V1\n"+scope+"\n"+key+"\n"+policy.fingerprint()).getBytes(StandardCharsets.UTF_8)));}
        catch(NoSuchAlgorithmException e){throw new AssertionError(e);}
        Path file=this.base.resolve("coal-commissioning.bin");
        manifest=create?ContinentCoordinatorManifest.create(file,identity,1):ContinentCoordinatorManifest.open(file,identity,1);
    }
    public static CoalRuntimeCommission create(Path base,CoalRuntimePolicy policy,ContinentResourceDecision.Scope scope,ReTerraForgedGeography.ContinentKey key)throws IOException {return new CoalRuntimeCommission(true,base,policy,scope,key);}
    public static CoalRuntimeCommission open(Path base,CoalRuntimePolicy policy,ContinentResourceDecision.Scope scope,ReTerraForgedGeography.ContinentKey key)throws IOException {return new CoalRuntimeCommission(false,base,policy,scope,key);}
    public int started()throws IOException{return manifest.started();}
    public Admission admit()throws IOException {
        boolean existing=manifest.started()==1;Path root=base.resolve("coal");
        if(!existing){manifest.start(0);Files.createDirectory(root);}
        var allocation=existing?CoalAllocationJournal.open(root.resolve("allocation.bin"),policy.layout(),scope,key)
                :CoalAllocationJournal.create(root.resolve("allocation.bin"),policy.layout(),scope,key);
        return new Admission(allocation,root.resolve("search"),existing);
    }
}
