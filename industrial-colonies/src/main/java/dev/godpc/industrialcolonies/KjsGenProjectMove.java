package dev.godpc.industrialcolonies;

import com.google.gson.*;
import com.zizazr.kjsgen.core.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.io.IOException;
import java.util.*;

/** Two-project move with collision checks, durable backups and rollback. No export or recipe rewriting. */
public final class KjsGenProjectMove {
    private static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
    private static String key(String name) { return ProjectManager.sanitizeName(name).toLowerCase(Locale.ROOT); }
    public static boolean archive(String name) {
        return Set.of("approved_recipes","rejected_recipes","maybe_recipes","deferred","disabled_recipes").contains(key(name));
    }
    public static RecipeProject copy(RecipeProject project) {return RecipeProject.fromJson(project.toJson().deepCopy());}
    private static Path file(Path root,String name) throws IOException {
        String wanted=key(name)+".json";
        try(var files=Files.list(root)) {
            var matches=files.filter(p->p.getFileName().toString().equalsIgnoreCase(wanted)).toList();
            if(matches.size()!=1)throw new IOException("Project is missing or ambiguous: "+name);
            Path p=matches.getFirst();
            if(!Files.isRegularFile(p,LinkOption.NOFOLLOW_LINKS))throw new IOException("Project is not a regular file");
            return p;
        }
    }
    private static RecipeProject latest(Path path,String name,Map<String,RecipeProject> cache) throws IOException {
        if(cache!=null)for(var entry:cache.entrySet())
            if(key(entry.getKey()).equals(key(name)) || key(entry.getValue().name()).equals(key(name)))return copy(entry.getValue());
        try {return RecipeProject.fromJson(JsonParser.parseString(Files.readString(path)).getAsJsonObject());}
        catch(RuntimeException e){throw new IOException("Cannot read project: "+name,e);}
    }
    private static void write(Path path,byte[] bytes) throws IOException {
        Path temp=Files.createTempFile(path.getParent(),".ic-move-",".tmp");
        try {
            Files.write(temp,bytes);
            try {Files.move(temp,path,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);}
            catch(AtomicMoveNotSupportedException e){Files.move(temp,path,StandardCopyOption.REPLACE_EXISTING);}
        }finally{Files.deleteIfExists(temp);}
    }
    private static byte[] bytes(RecipeProject project){return JSON.toJson(project.toJson()).getBytes(StandardCharsets.UTF_8);}
    private static void cache(Map<String,RecipeProject> cache,RecipeProject project) {
        cache.entrySet().removeIf(e->key(e.getKey()).equals(key(project.name())) || key(e.getValue().name()).equals(key(project.name())));
        cache.put(ProjectManager.sanitizeName(project.name()),project);
    }
    public static RecipeProject move(Path root,Map<String,RecipeProject> cache,RecipeProject source,RecipeInstance card,String destination) throws IOException {
        if((archive(source.name()) && !key(source.name()).equals("approved_recipes")) || archive(destination))
            throw new IOException("Move from a regular project or Approved Recipes into a regular project. Use review controls to change a decision.");
        if(key(source.name()).equals(key(destination)))throw new IOException("Choose a different project.");
        if(source.recipeByUid(card.uid()).isEmpty())throw new IOException("The selected recipe no longer exists.");
        Path from=file(root,source.name()),to=file(root,destination);
        KjsGenProjectRefresh.requireUnchangedIfTracked(from);
        KjsGenProjectRefresh.requireUnchangedIfTracked(to);
        byte[] beforeFrom=Files.readAllBytes(from),beforeTo=Files.readAllBytes(to);
        var fromProject=cache==null?copy(source):latest(from,source.name(),cache);
        var toProject=latest(to,destination,cache);
        for(var existing:toProject.recipes()) {
            if(Objects.equals(existing.uid(),card.uid()) || (!card.recipeId().isBlank() && Objects.equals(existing.recipeId(),card.recipeId())))
                throw new IOException("Destination already contains this UID or recipe ID. Nothing was moved.");
        }
        fromProject.recipes().removeIf(r->r.uid().equals(card.uid()));
        toProject.add(RecipeInstance.fromJson(card.toJson().deepCopy()));
        Path backup=root.getParent().resolve("industrial_colonies_sync/project-moves").resolve(UUID.randomUUID().toString());
        Files.createDirectories(backup);
        Files.write(backup.resolve("source.json"),beforeFrom);Files.write(backup.resolve("destination.json"),beforeTo);
        Files.writeString(backup.resolve("move.json"),JSON.toJson(Map.of("source",from.toString(),"destination",to.toString(),"uid",card.uid(),"status","IN_PROGRESS")));
        var oldCache=cache==null?null:new LinkedHashMap<>(cache);
        try {
            write(to,bytes(toProject));write(from,bytes(fromProject));
            if(cache!=null){cache(cache,fromProject);cache(cache,toProject);}
            if(!archive(fromProject.name()))KjsGenProjectRefresh.acceptOwnWrite(from,fromProject);
            KjsGenProjectRefresh.acceptOwnWrite(to,toProject);
            Files.writeString(backup.resolve("status.txt"),"APPLIED");
        }catch(Exception error) {
            try {write(from,beforeFrom);write(to,beforeTo);if(cache!=null){cache.clear();cache.putAll(oldCache);}}
            catch(Exception rollback){error.addSuppressed(rollback);}
            try {
                if(!archive(fromProject.name()))KjsGenProjectRefresh.acceptOwnWrite(from,RecipeProject.fromJson(JsonParser.parseString(new String(beforeFrom,StandardCharsets.UTF_8)).getAsJsonObject()));
                KjsGenProjectRefresh.acceptOwnWrite(to,RecipeProject.fromJson(JsonParser.parseString(new String(beforeTo,StandardCharsets.UTF_8)).getAsJsonObject()));
            }catch(Exception rollback){error.addSuppressed(rollback);}
            Files.writeString(backup.resolve("status.txt"),"FAILED: "+error);
            throw new IOException("Move failed: "+error.getMessage()+" Backups: "+backup,error);
        }
        return copy(fromProject);
    }
}
