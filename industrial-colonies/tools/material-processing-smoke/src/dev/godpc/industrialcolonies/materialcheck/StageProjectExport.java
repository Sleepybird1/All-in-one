package dev.godpc.industrialcolonies.materialcheck;

import com.google.gson.*;
import com.mojang.logging.LogUtils;
import com.zizazr.kjsgen.codegen.CodegenRegistry;
import com.zizazr.kjsgen.core.ProjectManager;
import com.zizazr.kjsgen.core.RecipeProject;
import com.zizazr.kjsgen.core.RecipeTypeDefinition;
import com.zizazr.kjsgen.core.RecipeTypeRegistry;
import com.zizazr.kjsgen.integration.kubejs.KubeJsExporter;
import dev.godpc.industrialcolonies.KjsGenIntegration;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.event.lifecycle.FMLLoadCompleteEvent;
import net.neoforged.fml.loading.FMLPaths;
import net.neoforged.neoforge.server.ServerLifecycleHooks;

/** Test-only, fail-closed export; no client-only classes and no live-instance fallback. */
final class StageProjectExport {
    private static JsonObject completed;
    private static Path stage, project;
    private static String projectHash;
    private static final Map<Path,String> exportedHashes=new LinkedHashMap<>();
    private StageProjectExport() { }

    static void register(IEventBus modBus) { modBus.addListener(StageProjectExport::loadComplete); }

    private static void loadComplete(FMLLoadCompleteEvent event) {
        // KJSGen's common setup is finished by this phase. ServerModLoader.load() waits for
        // this deferred work before Main creates any GameTest world/server resource packs.
        // KubeJS reads server_scripts in ServerScriptManager.createPackResources()->reload().
        event.enqueueWork(StageProjectExport::export);
    }

    private static synchronized void export() {
        if(completed!=null)throw new IllegalStateException("Duplicate material stage export lifecycle call");
        try {
            require(Boolean.getBoolean("neoforge.gameTestServer"),"Exporter is limited to the disposable GameTest server");
            stage=requiredPath("ic.material.requireStageRoot").toRealPath();
            require(FMLPaths.GAMEDIR.get().toRealPath().equals(stage),"FML game directory differs from required stage root");
            require(Path.of(System.getProperty("user.dir")).toRealPath().equals(stage),"Process directory differs from required stage root");
            require(ServerLifecycleHooks.getCurrentServer()==null,"Export is too late: a server already exists");
            require(Files.isDirectory(stage.resolve("mods")),"Required stage has no mods directory");
            Path scripts=guard(KubeJsExporter.serverScriptsDir());
            require(scripts.equals(stage.resolve("kubejs/server_scripts")),"KJSGen resolved an unexpected server_scripts directory");
            project=guard(ProjectManager.fileFor("default"));
            require(project.equals(stage.resolve("kjsgen/projects/default.json")),"KJSGen resolved an unexpected project path");
            require(Files.isRegularFile(project),"Merged staged default project does not exist");
            projectHash=sha(project);
            require(projectHash.equalsIgnoreCase(System.getProperty("ic.material.projectSha256","")),"Merged project changed after launcher configuration");
            Path report=guard(requiredPath("ic.material.exportReport"));
            require(!Files.exists(report),"Refusing to overwrite an earlier export report");

            JsonObject vatLayout=loadCandidateVatLayout();
            KjsGenIntegration.installMachineCentricDefinitions();
            require(RecipeTypeRegistry.get("kjsgen:shaped").isPresent()
                    &&RecipeTypeRegistry.get("kjsgen:create_pressing").isPresent()
                    &&CodegenRegistry.get(KjsGenIntegration.MACHINE_TEMPLATE_CODEGEN).isPresent()
                    &&CodegenRegistry.get("kjsgen:create_sequenced_assembly").isPresent(),
                    "Common KJSGen definitions/code generators are not ready at load-complete");
            JsonObject raw=JsonParser.parseString(Files.readString(project)).getAsJsonObject();
            RecipeProject merged=ProjectManager.load("default").orElseThrow(()->new IllegalStateException("Cannot load merged staged project"));
            require(ProjectManager.sanitizeName(merged.name()).equals("default"),"Expected only the merged default project");
            List<String> rawUids=raw.getAsJsonArray("recipes").asList().stream()
                    .map(e->e.getAsJsonObject().get("uid").getAsString()).sorted().toList();
            List<String> loadedUids=merged.recipes().stream().map(r->r.uid()).sorted().toList();
            require(rawUids.equals(loadedUids),"Loading changed/dropped/duplicated merged project cards");
            require(!loadedUids.isEmpty(),"Merged project has no recipe cards");
            require(merged.removals().size()==raw.getAsJsonArray("removals").size(),"Loading changed the project removal-rule count");
            for(var card:merged.recipes()) {
                var definition=RecipeTypeRegistry.get(card.typeId()).orElseThrow(()->new IllegalStateException("No registered layout for card "+card.uid()+" type "+card.typeId()));
                require(CodegenRegistry.get(definition.codegenId()).isPresent(),"No registered code generator for "+card.uid()+" type "+card.typeId());
            }
            // Resolve and validate EVERY destination before allowing the native exporter to write.
            Map<Path,String> previous=new LinkedHashMap<>();
            Set<Path> destinations=new HashSet<>();
            for(String file:merged.recipesByTargetFile().keySet()) {
                Path path=guard(KubeJsExporter.resolveScriptFile(file));
                require(path.getParent().equals(scripts),"Export destination is not directly in staged server_scripts");
                require(destinations.add(path),"Two project target names sanitize to the same script path");
                previous.put(path,Files.exists(path)?Files.readString(path):"");
            }
            ProjectManager.setCurrent(merged); // In-memory only; deliberately never save or rewrite the project JSON.
            KubeJsExporter.ExportResult result=KubeJsExporter.exportProject(merged);
            require(result.files().stream().mapToInt(KubeJsExporter.FileResult::recipeCount).sum()==loadedUids.size(),"Native exporter omitted merged recipe cards");
            require(result.files().size()==destinations.size(),"Native exporter returned an unexpected script count");
            require(sha(project).equals(projectHash),"Native export modified the merged project JSON");
            JsonObject evidence=new JsonObject(); JsonArray files=new JsonArray(), warnings=new JsonArray();
            evidence.addProperty("status","PASS"); evidence.addProperty("phase","FMLLoadCompleteEvent.enqueueWork (before GameTest world packs / KubeJS server script parse)");
            evidence.addProperty("stage",stage.toString()); evidence.addProperty("project",project.toString());
            evidence.addProperty("projectSha256",projectHash); evidence.addProperty("recipeCards",loadedUids.size());
            evidence.addProperty("removalRules",merged.removals().size());
            evidence.addProperty("allMergedCardUidsRetained",true);
            evidence.add("candidateBundledVatLayout",vatLayout);
            for(var file:result.files()) {
                Path path=guard(file.path()); require(destinations.contains(path),"Exporter wrote an unanticipated destination");
                String content=Files.readString(path), before=previous.get(path);
                require(outsideDefaultBlock(before).equals(outsideDefaultBlock(content)),"Content outside default project markers changed: "+path);
                String hash=sha(path); exportedHashes.put(path,hash);
                JsonObject row=new JsonObject(); row.addProperty("path",path.toString()); row.addProperty("sha256",hash);
                row.addProperty("bytes",Files.size(path)); row.addProperty("recipeCards",file.recipeCount());
                row.addProperty("previousSha256",sha(before.getBytes(StandardCharsets.UTF_8)));
                row.addProperty("outsideMarkerContentPreservedIgnoringBoundaryWhitespace",true); files.add(row);
                LogUtils.getLogger().info("MATERIAL_STAGE_EXPORT script={} cards={} sha256={}",path,file.recipeCount(),hash);
            }
            for(String warning:result.warnings()) { warnings.add(warning); LogUtils.getLogger().warn("MATERIAL_STAGE_EXPORT warning={}",warning); }
            evidence.add("scripts",files); evidence.add("warnings",warnings);
            Files.writeString(report,new GsonBuilder().setPrettyPrinting().create().toJson(evidence)+"\n",StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);
            completed=evidence;
            LogUtils.getLogger().info("MATERIAL_STAGE_EXPORT PASS cards={} files={} projectSha256={} report={}",loadedUids.size(),files.size(),projectHash,report);
        } catch(Exception failure) {
            LogUtils.getLogger().error("MATERIAL_STAGE_EXPORT FAIL; aborting before server scripts can be used",failure);
            throw new IllegalStateException("Test-only staged KJSGen export failed",failure);
        }
    }

    private static JsonObject loadCandidateVatLayout() throws Exception {
        // KJSGen 2.0.5 loadBundled() scans only its own assets/kjsgen namespace.
        // Its resource-reload loader discovers this existing candidate asset on
        // the client, but no such client reload occurs in a dedicated GameTest.
        // Use the same public fromJson/register APIs as both native loaders;
        // never synthesize a layout, change a card, or substitute its codegen.
        String resource="/assets/industrial_colonies/kjsgen_layouts/tfmg_chemical_vat.json";
        byte[] bytes;
        try(var input=KjsGenIntegration.class.getResourceAsStream(resource)) {
            require(input!=null,"Candidate lacks its bundled TFMG vat layout: "+resource);
            bytes=input.readAllBytes();
        }
        var definition=RecipeTypeDefinition.fromJson(JsonParser.parseString(
                new String(bytes,StandardCharsets.UTF_8)).getAsJsonObject());
        require(definition.id().equals(KjsGenIntegration.TFMG_CHEMICAL_VAT_CODEGEN)
                &&definition.codegenId().equals(KjsGenIntegration.TFMG_CHEMICAL_VAT_CODEGEN),
                "Candidate bundled vat layout changed its type/code-generator identity");
        require(CodegenRegistry.get(definition.codegenId()).isPresent(),
                "Candidate's native TFMG vat code generator is not registered");
        var existing=RecipeTypeRegistry.get(definition.id());
        if(existing.isPresent()) {
            require(existing.get().toJson().equals(definition.toJson()),
                    "Already registered vat layout differs from the candidate bundled asset");
        } else {
            RecipeTypeRegistry.register(definition);
        }
        require(RecipeTypeRegistry.get(definition.id()).isPresent(),"Bundled vat layout registration failed");
        JsonObject evidence=new JsonObject();
        evidence.addProperty("resource",resource);
        evidence.addProperty("sha256",sha(bytes));
        evidence.addProperty("registeredByTestHarness",existing.isEmpty());
        evidence.addProperty("nativeParser","RecipeTypeDefinition.fromJson");
        evidence.addProperty("codegen",definition.codegenId());
        LogUtils.getLogger().info("MATERIAL_STAGE_EXPORT candidateLayout={} sha256={} registered={}",
                resource,sha(bytes),existing.isEmpty());
        return evidence;
    }

    static synchronized JsonObject verifiedEvidence() throws Exception {
        require(completed!=null,"Staged project export did not finish before GameTest execution");
        require(sha(project).equals(projectHash),"Staged project changed after export");
        for(var entry:exportedHashes.entrySet())require(sha(entry.getKey()).equals(entry.getValue()),"Exported script changed after export: "+entry.getKey());
        return completed.deepCopy();
    }
    private static Path requiredPath(String key) {
        String value=System.getProperty(key); require(value!=null&&!value.isBlank(),"Required guard JVM property missing: "+key);
        return Path.of(value).toAbsolutePath().normalize();
    }
    private static Path guard(Path input) throws IOException {
        Path path=input.toAbsolutePath().normalize();
        require(path.startsWith(stage)&&!path.equals(stage),"Path escaped required disposable stage: "+path);
        for(Path part=path;part!=null&&part.startsWith(stage);part=part.getParent()) {
            require(!Files.isSymbolicLink(part),"Stage export path contains a symbolic link: "+part);
            if(Files.exists(part))require(part.toRealPath().startsWith(stage),"Stage export path resolves outside stage: "+part);
        }
        return path;
    }
    private static String outsideDefaultBlock(String text) {
        // Native marker merging normalizes line endings; preserve all other project/user text.
        String normalized=text.replace("\r\n","\n");
        return normalized.replaceFirst("(?ms)^// kjsgen:start default\\h*$.*?^// kjsgen:end default\\h*$","").strip();
    }
    private static String sha(Path path) throws Exception { return sha(Files.readAllBytes(path)); }
    private static String sha(byte[] bytes) throws Exception { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes)); }
    private static void require(boolean value,String message) { if(!value)throw new IllegalStateException(message); }
}
