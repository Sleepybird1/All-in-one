package dev.godpc.industrialcolonies.materialcheck;

import blusunrize.immersiveengineering.api.crafting.ArcFurnaceRecipe;
import com.drmangotea.tfmg.TFMGRegistries;
import com.drmangotea.tfmg.content.machinery.vat.electrode_holder.ElectrodeHolderBlockEntity;
import com.drmangotea.tfmg.recipes.VatMachineRecipe;
import com.google.gson.*;
import com.mojang.logging.LogUtils;
import com.mojang.serialization.JsonOps;
import com.simibubi.create.AllRecipeTypes;
import com.simibubi.create.content.kinetics.belt.behaviour.TransportedItemStackHandlerBehaviour.TransportedResult;
import com.simibubi.create.content.kinetics.belt.transport.TransportedItemStack;
import com.simibubi.create.content.kinetics.fan.processing.AllFanProcessingTypes;
import com.simibubi.create.content.kinetics.fan.processing.FanProcessing;
import com.simibubi.create.content.processing.recipe.HeatCondition;
import com.simibubi.create.content.processing.recipe.ProcessingRecipe;
import dev.godpc.industrialcolonies.CreateMachineContext;
import dev.godpc.industrialcolonies.CreateRecipeStageGate;
import dev.godpc.industrialcolonies.processing.ExclusiveMillingRecipe;
import dev.godpc.industrialcolonies.processing.FanRecipeCache;
import dev.godpc.industrialcolonies.processing.ManualCinnabarConfig;
import io.netty.buffer.Unpooled;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.NonNullList;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.resources.RegistryOps;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.*;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

/** Native runtime/API acceptance fixture; not a powered factory, real-player or throughput survey. */
@GameTestHolder("ic_material_smoke")
@PrefixGameTestTemplate(false)
public final class MaterialGameTests {
    private MaterialGameTests() { }

    @GameTest(templateNamespace="ic_material_smoke", template="geology_smoke_empty", timeoutTicks=2400)
    public static void loadedMaterialProcessingAcceptance(GameTestHelper helper) {
        new Run(helper).run();
    }

    @FunctionalInterface private interface Checked { void run() throws Exception; }
    private static final class Run {
        final GameTestHelper helper;
        final ServerLevel level;
        final JsonObject report=new JsonObject(), sections=new JsonObject();
        final JsonArray failures=new JsonArray();
        final long started=System.nanoTime();
        JsonObject recipes;
        RegistryOps<JsonElement> ops;
        Path output;
        int assertions;

        Run(GameTestHelper helper) { this.helper=helper; level=helper.getLevel(); }
        void check(boolean condition,String message) {
            assertions++; if(!condition)throw new IllegalStateException(message);
        }
        void section(String name,Checked action) {
            int before=assertions;
            try { action.run(); sections.addProperty(name,"PASS ("+(assertions-before)+" assertions)"); }
            catch(Exception failure) {
                sections.addProperty(name,"FAIL"); failures.add(name+": "+failure);
                LogUtils.getLogger().error("MATERIAL_PROCESSING_SMOKE section={} FAIL",name,failure);
            }
        }
        void run() {
            try {
                initialize();
                section("loadedCatalogAndRegistryReferences",this::catalog);
                section("noModernFoundryAlloy",this::noFoundryAlloy);
                section("retainedElectronicsBootstrap",this::electronicsBootstrap);
                section("nativeExclusiveMilling",this::exclusiveMilling);
                section("exactFanAndNegativeCacheRetry",this::fans);
                section("nativeElectricalVatAndTungstenArc",this::chemistry);
                section("manualConfigAndNoHeatCinnabar",this::manual);
                report.add("sections",sections); report.add("failures",failures);
                report.addProperty("assertions",assertions);
                report.addProperty("elapsedMilliseconds",(System.nanoTime()-started)/1_000_000);
                report.addProperty("status",failures.isEmpty()?"PASS":"FAIL");
                save();
                if(!failures.isEmpty())throw new IllegalStateException(failures.toString());
                LogUtils.getLogger().info("MATERIAL_PROCESSING_SMOKE PASS recipes={} assertions={} report={}",recipes.size(),assertions,output);
                helper.succeed();
            } catch(Exception failure) {
                report.addProperty("status","FAIL"); report.addProperty("fatal",failure.toString());
                try { save(); } catch(Exception writeFailure) { failure.addSuppressed(writeFailure); }
                LogUtils.getLogger().error("MATERIAL_PROCESSING_SMOKE FAIL",failure);
                helper.fail(failure.toString());
            }
        }
        void initialize() throws Exception {
            check(level.getServer().isSameThread(),"Fixture must run on the server thread");
            Path stage=Path.of(System.getProperty("user.dir")).toAbsolutePath().normalize();
            output=requiredPath("ic.material.report");
            check(output.startsWith(stage)&&!output.equals(stage),"Report must remain inside disposable stage");
            check(!Files.exists(output),"Refusing to overwrite an existing report");
            Path catalog=requiredPath("ic.material.catalog"), candidate=requiredPath("ic.material.candidate");
            check(candidate.startsWith(stage.resolve("mods")),"Candidate must be a staged mod, not live pack/source outputs");
            String catalogHash=sha(catalog), candidateHash=sha(candidate);
            check(catalogHash.equalsIgnoreCase(System.getProperty("ic.material.catalogSha256","")),"Catalog changed after launcher configuration");
            check(candidateHash.equalsIgnoreCase(System.getProperty("ic.material.candidateSha256","")),"Staged candidate changed after launcher configuration");
            report.addProperty("catalog",catalog.toString()); report.addProperty("catalogSha256",catalogHash);
            report.addProperty("candidate",candidate.toString()); report.addProperty("candidateSha256",candidateHash);
            report.add("preScriptProjectExport",StageProjectExport.verifiedEvidence());
            report.addProperty("scope","Actual loaded recipe manager, native codecs, direct fan/cache and milling APIs; no powered factory, real-player manual interaction or distribution claim");
            recipes=JsonParser.parseString(Files.readString(catalog)).getAsJsonObject().getAsJsonObject("recipes");
            check(recipes!=null&&!recipes.isEmpty(),"Generated catalog recipes object is empty");
            report.addProperty("expectedRecipes",recipes.size());
            ops=RegistryOps.create(JsonOps.INSTANCE,level.registryAccess());
        }
        Path requiredPath(String name) {
            String value=System.getProperty(name);
            check(value!=null&&!value.isBlank(),"Missing JVM property "+name);
            return Path.of(value).toAbsolutePath().normalize();
        }
        static String sha(Path path) throws Exception {
            return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(path)));
        }
        void save() throws Exception {
            if(output==null)return;
            Files.createDirectories(output.getParent());
            Files.writeString(output,new GsonBuilder().setPrettyPrinting().create().toJson(report)+"\n",StandardCharsets.UTF_8);
        }
        Recipe<?> recipe(String id) {
            return level.getRecipeManager().byKey(ResourceLocation.parse(id))
                    .orElseThrow(()->new IllegalStateException("Missing loaded recipe: "+id)).value();
        }
        JsonObject body(String id) {
            check(recipes.has(id),"Missing generated catalog recipe: "+id);
            return recipes.getAsJsonObject(id);
        }
        @SuppressWarnings({"rawtypes","unchecked"})
        Recipe<?> decode(JsonObject body) {
            ResourceLocation type=ResourceLocation.parse(body.get("type").getAsString());
            check(BuiltInRegistries.RECIPE_SERIALIZER.containsKey(type),"Unregistered recipe serializer "+type);
            RecipeSerializer serializer=BuiltInRegistries.RECIPE_SERIALIZER.get(type);
            return (Recipe<?>)serializer.codec().codec().parse(ops,body).getOrThrow();
        }
        @SuppressWarnings({"rawtypes","unchecked"})
        JsonElement encode(Recipe<?> recipe) {
            RecipeSerializer serializer=recipe.getSerializer();
            return (JsonElement)serializer.codec().codec().encodeStart(ops,recipe).getOrThrow();
        }
        void catalog() {
            JsonArray problems=new JsonArray(),encodedMismatches=new JsonArray(),noMoldSentinels=new JsonArray(); int loaded=0;
            for(var entry:recipes.entrySet()) {
                try {
                    String id=entry.getKey(); JsonObject expected=entry.getValue().getAsJsonObject();
                    Recipe<?> actual=recipe(id), decoded=decode(expected);
                    ResourceLocation expectedSerializer=ResourceLocation.parse(expected.get("type").getAsString());
                    ResourceLocation actualSerializer=BuiltInRegistries.RECIPE_SERIALIZER.getKey(actual.getSerializer());
                    check(expectedSerializer.equals(actualSerializer),"Serializer mismatch "+id);
                    JsonElement actualEncoded=encode(actual),expectedEncoded=encode(decoded);
                    boolean equivalent=actualEncoded.equals(expectedEncoded);
                    if(!equivalent) {
                        JsonObject mismatch=new JsonObject(); mismatch.addProperty("recipe",id);
                        mismatch.add("expectedSource",expected.deepCopy());
                        mismatch.add("expectedEncoded",expectedEncoded); mismatch.add("actualEncoded",actualEncoded);
                        encodedMismatches.add(mismatch);
                    }
                    check(equivalent,"Loaded recipe differs from generated catalog: "+id);
                    references(expected,id,true);
                    for(Ingredient ingredient:actual.getIngredients()) {
                        // MF basin block casts deliberately expose EMPTY as the absent mold.
                        // Identity is required: an ingredient backed by an empty tag is never exempt.
                        if(ResourceLocation.parse("modernfoundry:casting_basin").equals(actualSerializer)
                                &&!expected.has("cast")&&ingredient==Ingredient.EMPTY) {
                            noMoldSentinels.add(id); continue;
                        }
                        check(ingredient.getItems().length>0,"Empty loaded ingredient/tag: "+id);
                        for(ItemStack stack:ingredient.getItems())check(!stack.isEmpty(),"Air ingredient: "+id);
                    }
                    if(actual instanceof ProcessingRecipe<?,?> processing) {
                        check(processing.validate().isEmpty(),"Native Create validation failed: "+id+" "+processing.validate());
                        for(var input:processing.getFluidIngredients()) {
                            check(input.amount()>0&&input.getFluids().length>0,"Empty loaded fluid ingredient: "+id);
                            for(var fluid:input.getFluids())check(!fluid.isEmpty(),"Empty matching fluid: "+id);
                        }
                        for(var result:processing.getRollableResults())check(!result.getStack().isEmpty(),"Empty Create item output: "+id);
                        for(var result:processing.getFluidResults())check(!result.isEmpty(),"Empty Create fluid output: "+id);
                    }
                    loaded++;
                } catch(Exception failure) { problems.add(entry.getKey()+": "+failure.getMessage()); }
            }
            report.addProperty("loadedAndVerifiedRecipes",loaded); report.add("catalogProblems",problems);
            report.add("catalogEncodedMismatches",encodedMismatches);
            report.add("nativeBasinNoMoldSentinels",noMoldSentinels);
            check(problems.isEmpty(),problems.size()+" catalog recipe problems (see report catalogProblems)");
        }
        void references(JsonElement value,String path,boolean top) {
            if(value.isJsonArray()) { for(JsonElement child:value.getAsJsonArray())references(child,path,false); return; }
            if(!value.isJsonObject())return;
            JsonObject object=value.getAsJsonObject();
            boolean fluid=object.has("amount")||object.has("fluid")||
                    (object.has("type")&&object.get("type").getAsString().startsWith("neoforge:"));
            for(var e:object.entrySet()) {
                String key=e.getKey(); JsonElement child=e.getValue();
                if(child.isJsonPrimitive()&&child.getAsJsonPrimitive().isString()) {
                    String id=child.getAsString();
                    if(key.equals("item")||(!top&&key.equals("id")&&!fluid))checkItem(id,path);
                    if(key.equals("fluid")||(!top&&key.equals("id")&&fluid))checkFluid(id,path);
                    if(key.equals("tag")) {
                        ResourceLocation name=ResourceLocation.parse(id);
                        boolean exists=fluid
                                ? BuiltInRegistries.FLUID.getTag(TagKey.create(Registries.FLUID,name)).map(set->set.iterator().hasNext()).orElse(false)
                                : BuiltInRegistries.ITEM.getTag(TagKey.create(Registries.ITEM,name)).map(set->set.iterator().hasNext()).orElse(false);
                        check(exists,"Missing/empty "+(fluid?"fluid":"item")+" tag "+id+" in "+path);
                    }
                }
                references(child,path+"/"+key,false);
            }
        }
        void checkItem(String id,String path) {
            ResourceLocation name=ResourceLocation.parse(id);
            check(BuiltInRegistries.ITEM.containsKey(name)&&!new ItemStack(BuiltInRegistries.ITEM.get(name)).isEmpty(),"Missing/air item "+id+" in "+path);
        }
        void checkFluid(String id,String path) {
            ResourceLocation name=ResourceLocation.parse(id);
            check(BuiltInRegistries.FLUID.containsKey(name)&&BuiltInRegistries.FLUID.get(name)!=Fluids.EMPTY,"Missing/empty fluid "+id+" in "+path);
        }
        void noFoundryAlloy() {
            // Installed MF has an "alloy" serializer but an "alloying" native RecipeType.
            // Other installed mods also expose synthetic recipes with no registered type key.
            ResourceLocation alloySerializer=ResourceLocation.parse("modernfoundry:alloy");
            ResourceLocation alloyType=ResourceLocation.parse("modernfoundry:alloying");
            JsonObject registration=new JsonObject();
            registration.addProperty("serializer",alloySerializer.toString());
            registration.addProperty("recipeType",alloyType.toString());
            registration.addProperty("serializerRegistered",BuiltInRegistries.RECIPE_SERIALIZER.containsKey(alloySerializer));
            registration.addProperty("recipeTypeRegistered",BuiltInRegistries.RECIPE_TYPE.containsKey(alloyType));
            report.add("modernFoundryAlloyRegistration",registration);
            check(registration.get("serializerRegistered").getAsBoolean(),"Expected installed Modern Foundry alloy serializer is not registered");
            check(registration.get("recipeTypeRegistered").getAsBoolean(),"Expected installed Modern Foundry alloying recipe type is not registered");
            JsonArray found=new JsonArray(),unregistered=new JsonArray();
            for(RecipeHolder<?> holder:level.getRecipeManager().getRecipes()) {
                RecipeSerializer<?> serializerObject=holder.value().getSerializer();
                RecipeType<?> typeObject=holder.value().getType();
                ResourceLocation serializer=BuiltInRegistries.RECIPE_SERIALIZER.getKey(serializerObject);
                ResourceLocation type=BuiltInRegistries.RECIPE_TYPE.getKey(typeObject);
                if(serializer==null||type==null) {
                    JsonObject row=new JsonObject();row.addProperty("recipe",holder.id().toString());
                    row.addProperty("recipeClass",holder.value().getClass().getName());
                    row.addProperty("serializerKey",serializer==null?null:serializer.toString());
                    row.addProperty("recipeTypeKey",type==null?null:type.toString());
                    row.addProperty("serializerClass",serializerObject==null?null:serializerObject.getClass().getName());
                    row.addProperty("recipeTypeClass",typeObject==null?null:typeObject.getClass().getName());
                    unregistered.add(row);
                }
                if(alloySerializer.equals(serializer)||alloyType.equals(type))found.add(holder.id().toString());
            }
            report.add("remainingModernFoundryAlloys",found);
            report.add("unregisteredRecipeIdentities",unregistered);
            report.addProperty("unregisteredRecipeIdentityCount",unregistered.size());
            check(found.isEmpty(),"Modern Foundry alloy recipes remain loaded: "+found);
        }
        void electronicsBootstrap() {
            Map<String,String> retained=Map.of(
                    "industrial_colonies:electronics/n_semiconductor","tfmg:n_semiconductor",
                    "industrial_colonies:electronics/p_semiconductor","tfmg:p_semiconductor",
                    "industrial_colonies:electronics/prepared_silicon_wafer","industrial_colonies:prepared_silicon_wafer");
            JsonArray rows=new JsonArray();
            for(var entry:new TreeMap<>(retained).entrySet()) {
                Recipe<?> recipe=recipe(entry.getKey());
                check(recipe.getType()==AllRecipeTypes.SEQUENCED_ASSEMBLY.getType(),"Bootstrap electronics lost native sequenced assembly: "+entry.getKey());
                ItemStack output=recipe.getResultItem(level.registryAccess());
                check(!output.isEmpty()&&BuiltInRegistries.ITEM.getKey(output.getItem()).toString().equals(entry.getValue()),"Bootstrap recipe no longer produces its canonical component: "+entry.getKey());
                JsonObject row=new JsonObject();row.addProperty("recipe",entry.getKey());row.addProperty("output",entry.getValue());row.addProperty("count",output.getCount());rows.add(row);
            }
            report.add("retainedElectronicsBootstrap",rows);
        }
        void exclusiveMilling() {
            String id="industrial_colonies:processing/pgm/crude_exclusive";
            check(recipe(id) instanceof ExclusiveMillingRecipe,"Crude PGM is not native ExclusiveMillingRecipe");
            ExclusiveMillingRecipe recipe=(ExclusiveMillingRecipe)recipe(id);
            check(recipe.getType()==AllRecipeTypes.MILLING.getType(),"Crude PGM must remain in native MILLING, not industrial CRUSHING");
            check(recipe.matches(new SingleRecipeInput(stack("industrial_colonies:ultramafic_rock")),level),"Native millstone input does not match ultramafic rock");
            int samples=100000,recovered=0; int[] counts=new int[3];
            List<String> ids=recipe.getRollableResults().stream().map(r->BuiltInRegistries.ITEM.getKey(r.getStack().getItem()).toString()).toList();
            check(ids.equals(List.of("mekanism:nugget_osmium","industrial_colonies:platinum_trace_fragment","industrial_colonies:iridium_trace_fragment")),"Unexpected exclusive PGM output identities/order");
            RandomSource random=RandomSource.create(0x4d4154455249414cL);
            for(int i=0;i<samples;i++) {
                List<ItemStack> outputs=recipe.rollResults(random);
                check(outputs.size()<=1,"Exclusive native roll produced multiple materials");
                if(outputs.isEmpty())continue;
                ItemStack result=outputs.getFirst();
                check(!result.isEmpty()&&result.getCount()==1,"Exclusive native output count is not exactly one");
                int at=ids.indexOf(BuiltInRegistries.ITEM.getKey(result.getItem()).toString());
                check(at>=0,"Unexpected exclusive output item"); counts[at]++; recovered++;
            }
            check(Math.abs(recovered/(double)samples-recipe.recoveryChance())<.015,"Native recovery frequency outside fixed-seed tolerance");
            check(recovered>0,"No successful native PGM recoveries");
            for(int i=0;i<3;i++)check(Math.abs(counts[i]/(double)recovered-recipe.getRollableResults().get(i).getChance())<.015,"Conditional PGM share outside tolerance at "+i);
            JsonObject stats=new JsonObject(); stats.addProperty("samples",samples); stats.addProperty("recovered",recovered);
            stats.add("countsOsPtIr",new Gson().toJsonTree(counts)); report.add("nativeExclusiveMilling",stats);
            var serializer=new ExclusiveMillingRecipe.Serializer();
            RegistryFriendlyByteBuf buffer=new RegistryFriendlyByteBuf(Unpooled.buffer(),level.registryAccess());
            try {
                serializer.streamCodec().encode(buffer,recipe);
                ExclusiveMillingRecipe copy=serializer.streamCodec().decode(buffer);
                check(buffer.readableBytes()==0,"PGM stream codec left unread data");
                check(copy.recoveryChance()==recipe.recoveryChance()&&encode(copy).equals(encode(recipe)),"PGM registry-aware network round trip changed recipe");
            } finally { buffer.release(); }
            JsonObject invalid=body(id).deepCopy(); invalid.getAsJsonArray("results").get(0).getAsJsonObject().addProperty("count",2);
            check(serializer.codec().codec().parse(ops,invalid).error().isPresent(),"PGM codec accepted count=2");
            invalid=body(id).deepCopy(); invalid.remove("recovery_chance");
            check(serializer.codec().codec().parse(ops,invalid).error().isPresent(),"PGM codec accepted missing recovery chance");
            invalid=body(id).deepCopy(); invalid.getAsJsonArray("results").get(0).getAsJsonObject().addProperty("chance",.9);
            check(serializer.codec().codec().parse(ops,invalid).error().isPresent(),"PGM codec accepted non-normalized weights");
            for(int rate=0;rate<=1;rate++) {
                JsonObject boundary=body(id).deepCopy(); boundary.addProperty("recovery_chance",rate);
                ExclusiveMillingRecipe boundaryRecipe=(ExclusiveMillingRecipe)decode(boundary);
                for(int i=0;i<1000;i++)check(boundaryRecipe.rollResults(random).size()==rate,"Native recovery endpoint "+rate+" failed");
            }
        }
        ItemStack stack(String id) { checkItem(id,"fixture"); return new ItemStack(BuiltInRegistries.ITEM.get(ResourceLocation.parse(id))); }
        BlockEntity machine(String id) {
            ResourceLocation key=ResourceLocation.parse(id);
            check(BuiltInRegistries.BLOCK.containsKey(key),"Missing machine block "+id);
            var block=BuiltInRegistries.BLOCK.get(key);
            check(block instanceof EntityBlock,"Machine is not an EntityBlock: "+id);
            BlockEntity entity=((EntityBlock)block).newBlockEntity(helper.absolutePos(BlockPos.ZERO),block.defaultBlockState());
            check(entity!=null,"No native block entity for "+id); entity.setLevel(level); return entity;
        }
        void negativeCache(ItemEntity entity) {
            CompoundTag processing=new CompoundTag(); processing.putString("Type","create:splashing"); processing.putInt("Time",-1);
            CompoundTag create=new CompoundTag(); create.put("Processing",processing); entity.getPersistentData().put("CreateData",create);
        }
        void fans() {
            String id="industrial_colonies:processing/chromium/industrial_iron_separation";
            body(id); Recipe<?> recipe=recipe(id);
            check(!recipe.getIngredients().isEmpty(),"Industrial fan has no input");
            ItemStack input=recipe.getIngredients().getFirst().getItems()[0].copy(); input.setCount(1);
            check(FanRecipeCache.tierSensitive(input,level),"Exact fan input absent from scoped cache index");
            BlockEntity normal=machine("create:encased_fan"), weathered=machine("createcasing:weathered_iron_encased_fan"), industrial=machine("createcasing:industrial_iron_encased_fan");
            check(!CreateRecipeStageGate.machineMatches(recipe,normal),"Normal fan accepted industrial separation");
            check(!CreateRecipeStageGate.machineMatches(recipe,weathered),"Weathered fan accepted industrial separation");
            check(CreateRecipeStageGate.machineMatches(recipe,industrial),"Industrial Iron fan rejected its separation");
            ItemEntity entity=new ItemEntity(level,0,0,0,input.copy());
            for(BlockEntity low:List.of(normal,weathered))try(var ignored=CreateMachineContext.enter(low)) {
                negativeCache(entity);
                check(!AllFanProcessingTypes.SPLASHING.canProcess(input,level),"Native low-tier lookup bypassed exact fan gate");
                check(!FanProcessing.canProcess(entity,AllFanProcessingTypes.SPLASHING),"Dropped-item cache bypassed exact fan gate");
                TransportedItemStack transported=new TransportedItemStack(input.copy());
                transported.processedBy=AllFanProcessingTypes.SPLASHING; transported.processingTime=1;
                check(FanProcessing.applyProcessing(transported,level,AllFanProcessingTypes.SPLASHING).doesNothing(),"Wrong fan completed nearly-finished belt processing");
            }
            try(var ignored=CreateMachineContext.enter(industrial)) {
                negativeCache(entity);
                check(AllFanProcessingTypes.SPLASHING.canProcess(input,level),"Native industrial fan lookup failed");
                check(FanProcessing.canProcess(entity,AllFanProcessingTypes.SPLASHING),"Industrial fan could not retry dropped item after negative cache");
                check(!entity.getPersistentData().getCompound("CreateData").contains("Processing"),"Negative dropped-item cache was not cleared");
                TransportedItemStack transported=new TransportedItemStack(input.copy());
                transported.processedBy=AllFanProcessingTypes.SPLASHING; transported.processingTime=-1;
                TransportedResult result=TransportedResult.doNothing(); int calls=0;
                while(result.doesNothing()&&calls++<4096)result=FanProcessing.applyProcessing(transported,level,AllFanProcessingTypes.SPLASHING);
                check(!result.doesNothing(),"Industrial fan belt negative-cache retry did not complete within 4096 direct processing calls");
                check(result.getOutputs()!=null&&result.getOutputs().stream().anyMatch(s->s.stack.is(BuiltInRegistries.ITEM.get(ResourceLocation.parse("industrial_colonies:chromium_bearing_fraction")))) ,"Industrial fan returned no chromium fraction");
                report.addProperty("industrialFanDirectProcessingCalls",calls);
            }
            // Native, ungated copper washing must still work for all three physical fan variants.
            var nativeEntry=recipes.entrySet().stream().filter(e->e.getValue().getAsJsonObject().get("type").getAsString().equals("create:splashing")).findFirst().orElseThrow();
            Recipe<?> universal=recipe(nativeEntry.getKey()); ItemStack ordinary=universal.getIngredients().getFirst().getItems()[0].copy(); ordinary.setCount(1);
            check(!FanRecipeCache.tierSensitive(ordinary,level),"Ordinary washing was incorrectly included in exact-fan cache repair");
            for(BlockEntity fan:List.of(normal,weathered,industrial))try(var ignored=CreateMachineContext.enter(fan)) {
                check(CreateRecipeStageGate.machineMatches(universal,fan),"Universal recipe unexpectedly machine-bound");
                check(AllFanProcessingTypes.SPLASHING.canProcess(ordinary,level),"Ordinary washing broken for "+BuiltInRegistries.BLOCK.getKey(fan.getBlockState().getBlock()));
            }
            check(CreateMachineContext.current()==null,"Fan scope leaked after test");
            report.addProperty("fanFixture","Detached native block entities; no world blocks changed. Direct lookup/belt processing exercised, not airflow geometry.");
        }
        void chemistry() {
            JsonArray electrical=new JsonArray(); Set<String> nativeOperations=new HashSet<>();
            TFMGRegistries.ELECTRODE_REGISTRY.stream().forEach(e->nativeOperations.add(e.getOperationId()));
            check(nativeOperations.contains("tfmg:electrode"),"Native TFMG electrode registry does not implement recipe operation tfmg:electrode");
            for(var entry:recipes.entrySet()) {
                JsonObject json=entry.getValue().getAsJsonObject();
                if(!json.get("type").getAsString().equals("tfmg:vat_machine_recipe"))continue;
                List<String> machines=json.getAsJsonArray("machines").asList().stream().map(JsonElement::getAsString).toList();
                if(machines.stream().noneMatch(s->s.contains("electrode")))continue;
                check(recipe(entry.getKey()) instanceof VatMachineRecipe,"Electrical recipe not decoded as native TFMG vat recipe");
                VatMachineRecipe vat=(VatMachineRecipe)recipe(entry.getKey());
                check(vat.machines.equals(machines),"Electrical operations changed after decoding: "+entry.getKey());
                check(vat.machines.stream().filter(s->s.equals("tfmg:electrode")).count()>=2,"Electrical process requires fewer than two native electrode operations");
                check(vat.minSize==json.get("min_size").getAsInt(),"Vat minimum size changed");
                check(vat.allowedVatTypes.equals(json.getAsJsonArray("allowed_vat_types").asList().stream().map(JsonElement::getAsString).toList()),"Vat lining constraints changed");
                check(vat.getProcessingDuration()==json.get("processing_time").getAsInt(),"Vat processing duration changed");
                electrical.add(entry.getKey());
            }
            check(electrical.size()>=3,"Expected Aluminum, Magnesium and Lithium powered electrical routes");
            for(String material:List.of("aluminum/","magnesium/","lithium/"))check(electrical.asList().stream().anyMatch(e->e.getAsString().contains(material)),"Missing native electrical route for "+material);
            BlockEntity machine=machine("tfmg:electrode_holder");
            check(machine instanceof ElectrodeHolderBlockEntity,"Electrode holder has wrong native block entity");
            check(!((ElectrodeHolderBlockEntity)machine).canOperate(null),"Unpowered native electrode holder reported operational");
            report.add("nativeElectricalRecipes",electrical);
            String id="industrial_colonies:processing/tungsten/sinter"; JsonObject json=body(id);
            check(recipe(id) instanceof ArcFurnaceRecipe,"Tungsten sintering is not native IE arc furnace processing");
            ArcFurnaceRecipe arc=(ArcFurnaceRecipe)recipe(id);
            check(arc.getBaseTime()==json.get("time").getAsInt()&&arc.getBaseEnergy()==json.get("energy").getAsInt(),"Native arc furnace time/total-energy decoding changed");
            check(arc.input.getCount()==json.getAsJsonObject("input").get("count").getAsInt(),"Tungsten powder quantity was lost during native sized ingredient decoding");
            ItemStack powder=stack("nuclearcraft:tungsten_dust"); powder.setCount(arc.input.getCount());
            check(arc.matches(powder,NonNullList.create()),"Native tungsten arc recipe does not match its configured full powder input");
            ItemStack shortPowder=powder.copy(); shortPowder.shrink(1);
            check(!arc.matches(shortPowder,NonNullList.create()),"Native tungsten arc recipe accepts insufficient powder");
            check(arc.getBaseOutputs().stream().anyMatch(s->s.is(BuiltInRegistries.ITEM.get(ResourceLocation.parse("nuclearcraft:tungsten_ingot")))&&s.getCount()==1),"Native tungsten arc output is not one canonical ingot");
            var selected=ArcFurnaceRecipe.findRecipe(level,powder,NonNullList.create());
            check(selected!=null&&selected.id().toString().equals(id),"Native arc recipe cache selected a conflicting Tungsten shortcut");
            report.addProperty("nativeArcBaseTime",arc.getBaseTime()); report.addProperty("nativeArcBaseTotalEnergy",arc.getBaseEnergy());
        }
        void manual() {
            ManualCinnabarConfig config=ManualCinnabarConfig.get();
            check(config.enabled(),"Manual Cinnabar route disabled in stage");
            check(config.manualNoBatch(),"Manual no-batch guard disabled");
            check(config.heatingTicks()>=20&&config.heatingTicks()<=72000,"Invalid manual heating duration");
            check(config.hammerCooldownTicks()>0&&config.hammerDamage()>0,"Manual hammer delay/damage missing");
            check(config.reach()>=1&&config.reach()<=5,"Manual reach out of bounds");
            check(stack("immersiveengineering:hammer").isDamageableItem(),"Canonical IE hammer is not damageable");
            stack("industrial_colonies:roasted_cinnabar");
            JsonObject decoded=new Gson().toJsonTree(config).getAsJsonObject();
            check(ManualCinnabarConfig.fromJson(decoded).equals(config),"Manual settings did not round-trip");
            decoded.addProperty("manualNoBatch",false); boolean rejected=false;
            try { ManualCinnabarConfig.fromJson(decoded); } catch(IllegalArgumentException expected) { rejected=true; }
            check(rejected,"Manual config accepted automation/batching bypass");
            Recipe<?> batch=recipe("industrial_colonies:processing/cinnabar/batch_redstone");
            check(batch instanceof ProcessingRecipe<?,?>,"Batch Cinnabar is not native Create processing");
            check(batch.getType()==AllRecipeTypes.MIXING.getType(),"Batch Cinnabar uses the wrong native processing family");
            check(((ProcessingRecipe<?,?>)batch).getRequiredHeat()==HeatCondition.NONE,"Batch Cinnabar mistakenly requires extra heat");
            report.add("manualConfig",new Gson().toJsonTree(config));
            report.addProperty("manualScope","Config, registered damageable hammer and no-heat batch recipe checked; a real-player 60-second interaction was not simulated by this addon.");
        }
    }
}
