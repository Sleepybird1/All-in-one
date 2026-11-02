package dev.godpc.industrialcolonies.geology;

import com.google.gson.*;
import java.io.*;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;

/** Separate guaranteed-supply request policy. No optional presence roll, terrain reads or writes.
 * A request is NOT proof that deposits fit or contain the requested recoverable coal.
 * The unresolved extra-small minimum is mandatory configuration, never an implicit default. */
public final class CoalLayoutPolicy {
    public enum Minimum { ADD_SMALL, REPLACED_BY_NON_SMALL }
    public enum Layout { SMALL_GROUP, TWO_MEDIUM, ONE_LARGE }
    public enum Size { SMALL, MEDIUM, LARGE }
    public record Deposit(String slot,Size size,int oreBlocks,long shapeSalt) {}
    public record Plan(String identity,String policySha256,Layout layout,Minimum minimum,
                       List<Deposit> deposits,int requestedTotal) {
        public Plan {deposits=List.copyOf(deposits);}
    }
    private static final Set<String> FIELDS=Set.of("schema","status","sourceChartSHA256",
            "oreBlocks","layoutWeights","smallCounts","smallCountSelection","nonSmallMinimum");
    private final int small,medium,large,smallWeight,mediumWeight,minSmall,maxSmall;
    private final Minimum minimum;
    private final String fingerprint;
    private CoalLayoutPolicy(int[] sizes,int[] weights,int[] counts,Minimum minimum,String fingerprint){
        small=sizes[0];medium=sizes[1];large=sizes[2];smallWeight=weights[0];mediumWeight=weights[1];
        minSmall=counts[0];maxSmall=counts[1];this.minimum=minimum;this.fingerprint=fingerprint;
    }
    /** Exact source bytes bind the policy; changed configuration must not reopen an old allocation. */
    public static CoalLayoutPolicy read(byte[] source){
        if(source==null||source.length==0||source.length>16384)throw new IllegalArgumentException("Bounded coal policy required");
        try{
            JsonObject root=JsonParser.parseString(new String(source,StandardCharsets.UTF_8)).getAsJsonObject();
            if(!root.keySet().equals(FIELDS)||!text(root,"schema").equals("continent-coal-layout-v1")
                    ||!text(root,"status").equals("PROPOSAL_NOT_INSTALLED")
                    ||!text(root,"sourceChartSHA256").matches("[a-f0-9]{64}")
                    ||!text(root,"smallCountSelection").equals("UNIFORM_INCLUSIVE"))
                throw new IllegalArgumentException("Explicit supported coal policy required");
            int[] sizes=ints(root,"oreBlocks",3),weights=ints(root,"layoutWeights",3),counts=ints(root,"smallCounts",2);
            if(sizes[0]<1||sizes[0]>=sizes[1]||sizes[1]>=sizes[2]||sizes[2]>FiniteOreLimits.MAX_BLOCKS
                    ||Arrays.stream(weights).anyMatch(v->v<0||v>100)||Arrays.stream(weights).sum()!=100
                    ||counts[0]<1||counts[0]>counts[1]||counts[1]>6)
                throw new IllegalArgumentException("Coal size, weight or small-count bounds");
            Minimum minimum=Minimum.valueOf(text(root,"nonSmallMinimum"));
            return new CoalLayoutPolicy(sizes,weights,counts,minimum,hex(hash(source)));
        }catch(JsonParseException|IllegalStateException|ArithmeticException e){
            throw new IllegalArgumentException("Invalid coal policy",e);
        }
    }
    private static String text(JsonObject root,String key){
        var value=root.get(key);
        if(value==null||!value.isJsonPrimitive()||!value.getAsJsonPrimitive().isString())throw new IllegalArgumentException("String required: "+key);
        return value.getAsString();
    }
    private static int[] ints(JsonObject root,String key,int size){
        var value=root.get(key);if(value==null||!value.isJsonArray()||value.getAsJsonArray().size()!=size)throw new IllegalArgumentException("Array required: "+key);
        int[] result=new int[size];int i=0;
        for(var n:value.getAsJsonArray()){
            if(!n.isJsonPrimitive()||!n.getAsJsonPrimitive().isNumber())throw new IllegalArgumentException("Integer required: "+key);
            result[i++]=n.getAsBigDecimal().intValueExact();
        }
        return result;
    }
    public String fingerprint(){return fingerprint;}
    /** Scope excludes chunk and query order. Different continents have independent layout draws.
     * No automatic replacement is attempted if a selected deposit cannot fit. */
    public Plan select(ContinentResourceDecision.Scope scope,ReTerraForgedGeography.ContinentKey continent){
        Objects.requireNonNull(scope);Objects.requireNonNull(continent);
        byte[] scopeBytes=scopeBytes(scope,continent);
        int ticket=random(scopeBytes,"layout").nextInt(100);
        Layout layout=ticket<smallWeight?Layout.SMALL_GROUP:ticket<smallWeight+mediumWeight?Layout.TWO_MEDIUM:Layout.ONE_LARGE;
        var deposits=new ArrayList<Deposit>();
        if(layout==Layout.SMALL_GROUP){
            int count=random(scopeBytes,"small-count").nextInt(minSmall,maxSmall+1);
            for(int i=0;i<count;i++)deposits.add(deposit(scopeBytes,"small_"+i,Size.SMALL,small));
        }else{
            Size size=layout==Layout.TWO_MEDIUM?Size.MEDIUM:Size.LARGE;
            for(int i=0;i<(size==Size.MEDIUM?2:1);i++)deposits.add(deposit(scopeBytes,size.name().toLowerCase(Locale.ROOT)+"_"+i,size,size==Size.MEDIUM?medium:large));
            if(minimum==Minimum.ADD_SMALL)deposits.add(deposit(scopeBytes,"minimum_small",Size.SMALL,small));
        }
        return new Plan(hex(hash(scopeBytes)),fingerprint,layout,minimum,deposits,deposits.stream().mapToInt(Deposit::oreBlocks).sum());
    }
    /** Call before using a previously saved request; never silently redraw under changed inputs. */
    public void verify(ContinentResourceDecision.Scope scope,ReTerraForgedGeography.ContinentKey continent,Plan saved){
        if(!select(scope,continent).equals(saved))throw new IllegalStateException("Coal allocation changed; explicit review required");
    }
    private Deposit deposit(byte[] scope,String slot,Size size,int blocks){return new Deposit(slot,size,blocks,random(scope,"shape/"+slot).nextLong());}
    private byte[] scopeBytes(ContinentResourceDecision.Scope scope,ReTerraForgedGeography.ContinentKey continent){
        try{
            var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
            out.writeUTF("industrial-colonies/coal-layout/v1");out.writeLong(scope.worldSeed());out.writeUTF(scope.dimension());out.writeUTF(scope.presetSha256());
            out.writeInt(continent.centerX());out.writeInt(continent.centerZ());out.writeInt(continent.identityBits());out.writeUTF(fingerprint);out.flush();return bytes.toByteArray();
        }catch(IOException e){throw new AssertionError(e);}
    }
    private static SplittableRandom random(byte[] scope,String domain){
        try{
            var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
            out.writeInt(scope.length);out.write(scope);out.writeUTF(domain);out.flush();
            return new SplittableRandom(ByteBuffer.wrap(hash(bytes.toByteArray())).getLong());
        }catch(IOException e){throw new AssertionError(e);}
    }
    private static byte[] hash(byte[] value){try{return MessageDigest.getInstance("SHA-256").digest(value);}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
    private static String hex(byte[] bytes){return HexFormat.of().formatHex(bytes);}
}
