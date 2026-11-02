package dev.godpc.industrialcolonies;

import com.google.gson.*;
import com.zizazr.kjsgen.core.*;
import com.zizazr.kjsgen.integration.net.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

/** One small marker poll per second off-thread; project serialization only after an external update. */
public final class KjsGenAutomaticRefresh {
    public interface View {
        void industrialColonies$applyAutomatic(RecipeProject project);
    }
    private static final ExecutorService IO=Executors.newSingleThreadExecutor(r->{var t=new Thread(r,"KJSGen external changes");t.setDaemon(true);return t;});
    private static final AtomicBoolean polling=new AtomicBoolean();
    private static final KjsGenRefreshSchedule schedule=new KjsGenRefreshSchedule();
    private static final Map<String,String> available=new HashMap<>();
    private static Pending pending;
    private static boolean forwarding;
    private static final class Pending {
        final String key,token,revision;
        final RecipeProject live;
        final JsonObject before;
        JsonObject result;
        boolean conflictNotified;
        long lastAttempt=Long.MIN_VALUE;
        Pending(String key,String revision,RecipeProject project){this.key=key;this.revision=revision;live=project;before=project.toJson().deepCopy();token=UUID.randomUUID().toString();}
    }
    private static String key(RecipeProject p){return ProjectManager.sanitizeName(p.name());}
    private static void say(String text){var mc=Minecraft.getInstance();if(mc.player!=null)mc.player.displayClientMessage(Component.literal(text),false);}
    public static boolean busy(String name){return pending!=null&&pending.key.equals(ProjectManager.sanitizeName(name));}
    public static boolean holdPush(){return !forwarding&&pending!=null&&pending.key.equals(key(ClientEditSession.project()));}
    public static void tick(Screen screen,RecipeProject project,boolean safe,long editRevision){
        var mc=Minecraft.getInstance();
        if(!mc.hasSingleplayerServer() || !ClientEditSession.isRemote() || KjsGenProjectMove.archive(project.name()))return;
        String key=key(project);
        if(pending!=null){
            long revision=pending.key.equals(key)?editRevision:-1;
            if(pending.result!=null&&(!pending.key.equals(key)||safe)&&pending.lastAttempt!=revision){
                pending.lastAttempt=revision;finish(pending.key.equals(key)?screen:null,pending.key.equals(key)?project:pending.live);
            }
            return;
        }
        long now=System.nanoTime();
        if(!polling.get()&&schedule.poll(now)&&polling.compareAndSet(false,true)){
            Path projectFile=ProjectManager.fileFor(project.name());
            Path marker=KjsGenProjectRefresh.stateRoot(projectFile).resolve("signals/"+key+".json");
            IO.execute(()->{
                String revision=null;
                try{revision=KjsGenRefreshMarker.readRevision(projectFile,marker);}
                catch(Exception ignored){}finally{polling.set(false);}
                String found=revision;
                mc.execute(()->KjsGenRefreshMarker.record(available,key,found));
            });
        }
        String revision=available.get(key);
        if(!safe||!schedule.attempt(key,revision,editRevision))return;
        pending=new Pending(key,revision,project);
        JsonObject request=new JsonObject();request.addProperty("project",project.name());request.addProperty("expected",KjsGenProjectRefresh.fingerprint(project));request.addProperty("token",pending.token);
        KjsGenNet.toServer("ic_refresh",request.toString());
    }
    public static boolean result(String text){
        if(pending==null)return false;
        JsonObject result=JsonParser.parseString(text).getAsJsonObject();
        if(!result.has("token")||!pending.token.equals(result.get("token").getAsString()))return false;
        pending.result=result;return true;
    }
    private static void finish(Screen screen,RecipeProject current){
        Pending p=pending;
        // A server snapshot/project switch must not silently replace the captured editor branch.
        if(current!=p.live){recover(p,"Editor project changed during automatic refresh");pending=null;say("Automatic refresh paused: project switched; editor recovery saved locally.");return;}
        if(p.result.has("error")){
            String error=p.result.get("error").getAsString();
            pending=null;
            // Flush edits made after the request into the old cache; the disk guard keeps
            // the external branch intact. Retry only after a new edit or external revision.
            forward(p.live.name(),p.before,p.live.toJson());
            say("Automatic project refresh paused ("+p.live.name()+"): "+error);return;
        }
        JsonObject refreshed=p.result.getAsJsonObject("project"), combined;
        try{combined=KjsGenProjectRefresh.merge(p.before,p.live.toJson(),refreshed);}
        catch(Exception error){
            if(!p.conflictNotified){recover(p,error.getMessage());say("Automatic refresh conflict: "+error.getMessage()+" Your edits are retained; resolve the field or ask for help.");p.conflictNotified=true;}
            return;
        }
        RecipeProject merged=RecipeProject.fromJson(combined);
        boolean changed=!p.live.toJson().equals(combined);
        pending=null;schedule.success(p.key);
        forward(merged.name(),refreshed,combined);
        // No rebuild when external data was semantically unchanged.
        if(changed&&screen!=null)((View)screen).industrialColonies$applyAutomatic(merged);
        else if(key(ClientEditSession.project()).equals(p.key))ClientEditSession.setLocalProject(changed?merged:current);
        say("Project updated automatically. Game recipes unchanged.");
    }
    /** Replay only actual post-request deltas; never export or issue a game reload. */
    private static void forward(String name,JsonObject base,JsonObject updated){
        forwarding=true;
        try{
            for(String field:List.of("recipes","removals")){
                Map<String,JsonObject> before=rows(base,field),after=rows(updated,field);
                for(var e:after.entrySet())if(!e.getValue().equals(before.get(e.getKey()))){
                    JsonObject body=new JsonObject();body.addProperty("project",name);body.add(field.equals("recipes")?"recipe":"removal",e.getValue());
                    KjsGenNet.toServer(field.equals("recipes")?"upsertRecipe":"upsertRemoval",body.toString());
                }
                for(String uid:before.keySet())if(!after.containsKey(uid)){
                    JsonObject body=new JsonObject();body.addProperty("project",name);body.addProperty("uid",uid);
                    KjsGenNet.toServer(field.equals("recipes")?"removeRecipe":"removeRemoval",body.toString());
                }
            }
            JsonObject meta=new JsonObject();
            for(String field:List.of("name","defaultTargetFile","exportComments","reloadOnExport"))if(!Objects.equals(base.get(field),updated.get(field)))meta.add(field,updated.get(field));
            if(!meta.isEmpty()){JsonObject body=new JsonObject();body.addProperty("project",name);body.add("meta",meta);KjsGenNet.toServer("meta",body.toString());}
        }finally{forwarding=false;}
    }
    private static Map<String,JsonObject> rows(JsonObject p,String field){
        Map<String,JsonObject> rows=new LinkedHashMap<>();for(JsonElement row:p.getAsJsonArray(field))rows.put(row.getAsJsonObject().get("uid").getAsString(),row.getAsJsonObject());return rows;
    }
    private static void recover(Pending p,String reason){
        JsonObject memory=p.live.toJson().deepCopy(),before=p.before.deepCopy(),result=p.result==null?new JsonObject():p.result.deepCopy();
        Path dir=KjsGenProjectRefresh.stateRoot(ProjectManager.fileFor(p.live.name())).resolve("automatic-recovery/"+p.token);
        IO.execute(()->{try{Files.createDirectories(dir);Files.writeString(dir.resolve("memory.json"),memory.toString());Files.writeString(dir.resolve("before.json"),before.toString());Files.writeString(dir.resolve("result.json"),result.toString());Files.writeString(dir.resolve("reason.txt"),reason);}catch(Exception e){com.mojang.logging.LogUtils.getLogger().error("Could not preserve automatic refresh recovery",e);}});
    }
    public static void reset(){if(pending!=null)recover(pending,"Session ended during automatic refresh");pending=null;schedule.clear();available.clear();}
}
