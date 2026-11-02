package dev.godpc.industrialcolonies;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonNull;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.logging.LogUtils;
import com.zizazr.kjsgen.core.ProjectManager;
import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeProject;
import dev.godpc.industrialcolonies.mixin.KjsGenServerProjectStoreAccessor;
import net.minecraft.client.Minecraft;
import net.minecraft.server.MinecraftServer;
import net.neoforged.fml.loading.FMLPaths;
import org.slf4j.Logger;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.TreeMap;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;

/**
 * Durable review decisions for the managed recipes shown in KJSGen's default
 * project.
 *
 * <p>A decision belongs to a recipe design rather than merely its recipe ID.
 * The effective state therefore becomes {@link Status#STALE} whenever the
 * canonical design hash differs from the reviewed version. Stale approved or
 * rejected cards participate in Default's pending traversal; Maybe, Deferred,
 * and Disabled remain in their explicit archive queues until reclassified.</p>
 */
public final class KjsGenRecipeReviewStore {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static final Gson COMPACT_GSON =
            new GsonBuilder().disableHtmlEscaping().create();

    private static final int SCHEMA_VERSION = 2;
    private static final int LEGACY_SCHEMA_VERSION = 1;
    private static final String DEFAULT_PROJECT = "default";
    private static final String APPROVED_PROJECT = "approved recipes";
    private static final String REJECTED_PROJECT = "rejected recipes";
    private static final String DEFERRED_PROJECT = "Deferred";
    private static final String MAYBE_PROJECT = "maybe recipes";
    private static final String DISABLED_PROJECT = "disabled recipes";
    private static final List<String> REVIEW_ARCHIVE_PROJECTS = List.of(
            APPROVED_PROJECT,
            REJECTED_PROJECT,
            DEFERRED_PROJECT,
            MAYBE_PROJECT,
            DISABLED_PROJECT
    );
    private static final String REVIEW_FILE = "default.recipe_reviews.json";
    private static final String MANAGED_BASELINE_FILE = "default.managed.baseline.json";

    private static final Set<String> REJECTION_REASONS = Set.of(
            "manual",
            "default_recipe",
            "restore_default_recipe",
            "ring_of_items"
    );
    private static final Set<String> DISABLE_REASONS = Set.of(
            "redundant_mechanic",
            "duplicate_machine",
            "progression_bypass",
            "internal_unused",
            "manual"
    );
    private static final KjsGenRecipeReviewStore DEFAULT = new KjsGenRecipeReviewStore();

    private final Map<String, StoredReview> reviewsByRecipeId = new TreeMap<>();
    private final Set<String> managedUids = new HashSet<>();
    private RecipeProject project;

    private KjsGenRecipeReviewStore() {
    }

    /** Loads the durable ledger and managed baseline for the supplied project. */
    public static KjsGenRecipeReviewStore forProject(RecipeProject project) {
        return DEFAULT.refresh(project);
    }

    /**
     * Reloads review state from disk. Failures are logged and leave the store
     * empty rather than preventing the KJSGen editor from opening.
     */
    public synchronized KjsGenRecipeReviewStore refresh(RecipeProject project) {
        this.project = project;
        managedUids.clear();
        reviewsByRecipeId.clear();
        if (!isReviewProject(project)) {
            return this;
        }
        loadManagedBaseline();
        loadReviews();
        includeLedgerBackedArchiveUids(project);
        if (!projectNamed(project, DEFAULT_PROJECT) && !isArchiveProject(project)) {
            project.recipes().stream().filter(this::canReview).map(RecipeInstance::uid).forEach(managedUids::add);
        }
        return this;
    }

    public synchronized boolean isManaged(String uid) {
        return uid != null && managedUids.contains(uid);
    }

    /**
     * Returns whether the selected card can be adopted into the review ledger.
     * Newly created, duplicated, or formerly unmanaged cards are intentionally
     * reviewable as long as KJSGen has assigned both a UID and recipe ID.
     */
    public synchronized boolean canReview(RecipeInstance recipe) {
        return recipe != null
                && recipe.uid() != null
                && !recipe.uid().isBlank()
                && recipe.recipeId() != null
                && !recipe.recipeId().isBlank()
                && isReviewProject(project);
    }

    public synchronized List<RecipeInstance> managedRecipes() {
        return managedRecipes(project);
    }

    public synchronized List<RecipeInstance> managedRecipes(RecipeProject project) {
        if (!isReviewProject(project) || managedUids.isEmpty()) {
            return List.of();
        }
        return project.recipes().stream()
                .filter(recipe -> managedUids.contains(recipe.uid()))
                .toList();
    }

    /** Returns the effective state; stale decisions are never treated as reviewed. */
    public synchronized Status status(RecipeInstance recipe) {
        return review(recipe).effectiveStatus();
    }

    public synchronized Status effectiveStatus(RecipeInstance recipe) {
        return status(recipe);
    }

    /** Returns the state written in the ledger before design-staleness is applied. */
    public synchronized Status currentStatus(RecipeInstance recipe) {
        return review(recipe).currentStatus();
    }

    /**
     * Returns whether a card belongs in the currently open review queue.
     *
     * <p>Default remains the canonical KJSGen project used for editing and
     * export, but reviewed managed cards are projected out of its visible
     * queue. This prevents a completed card from being reviewed twice without
     * deleting the underlying recipe. Archive projects expose only cards whose
     * durable decision still matches that archive. Unmanaged cards remain
     * visible so KJSGen's normal add/edit workflow is unaffected.</p>
     */
    public synchronized boolean isVisibleInReviewQueue(
            RecipeProject project,
            RecipeInstance recipe
    ) {
        if (project == null || recipe == null || !isReviewProject(project)) {
            return true;
        }
        if (!managedUids.contains(recipe.uid())) {
            return true;
        }

        Review review = review(recipe);
        if (projectNamed(project, DEFAULT_PROJECT)) {
            return isPendingForProject(project, review);
        }
        if (projectNamed(project, APPROVED_PROJECT)) {
            return review.currentStatus() == Status.APPROVED;
        }
        if (projectNamed(project, REJECTED_PROJECT)) {
            return review.currentStatus() == Status.REJECTED;
        }
        if (projectNamed(project, DEFERRED_PROJECT)) {
            return review.currentStatus() == Status.DEFERRED;
        }
        if (projectNamed(project, MAYBE_PROJECT)) {
            return review.currentStatus() == Status.MAYBE;
        }
        if (projectNamed(project, DISABLED_PROJECT)) {
            return review.currentStatus() == Status.DISABLED;
        }
        return isPendingForProject(project, review);
    }

    /**
     * Snapshot projection used by KJSGen's recipe list. Callers cache this
     * result for the lifetime of one editor rebuild so hashing is never done
     * for every recipe row on every rendered frame.
     */
    public synchronized List<RecipeInstance> visibleRecipes(RecipeProject project) {
        if (project == null || !isReviewProject(project)) {
            return project == null ? List.of() : project.recipes();
        }
        return project.recipes().stream()
                .filter(recipe -> isVisibleInReviewQueue(project, recipe))
                .toList();
    }

    public synchronized Review review(RecipeInstance recipe) {
        if (recipe == null || recipe.recipeId() == null || recipe.recipeId().isBlank()) {
            return Review.pending();
        }

        StoredReview stored = reviewsByRecipeId.get(recipe.recipeId());
        if (stored == null) {
            return Review.pending();
        }

        Status current = switch (stored.status()) {
            case "approved" -> Status.APPROVED;
            case "rejected" -> Status.REJECTED;
            case "deferred" -> Status.DEFERRED;
            case "maybe" -> Status.MAYBE;
            case "disabled" -> Status.DISABLED;
            default -> Status.PENDING;
        };
        String currentHash = cardSha256(recipe);
        Status effective = stored.cardSha256().equals(currentHash)
                ? current
                : Status.STALE;
        return new Review(
                stored.uid(),
                current,
                effective,
                stored.reason(),
                stored.note(),
                stored.cardSha256()
        );
    }

    public synchronized String note(RecipeInstance recipe) {
        return review(recipe).note();
    }

    public synchronized Counts counts() {
        return counts(project);
    }

    public synchronized Counts counts(RecipeProject project) {
        int approved = 0;
        int rejected = 0;
        int deferred = 0;
        int maybe = 0;
        int disabled = 0;
        int pending = 0;
        int stale = 0;
        int queueRemaining = 0;
        List<RecipeInstance> managed = managedRecipes(project);

        for (RecipeInstance recipe : managed) {
            Review review = review(recipe);
            Status status = review.effectiveStatus();
            switch (status) {
                case APPROVED -> approved++;
                case REJECTED -> rejected++;
                case DEFERRED -> deferred++;
                case MAYBE -> maybe++;
                case DISABLED -> disabled++;
                case STALE -> stale++;
                case PENDING -> pending++;
            }
            if (isPendingForProject(project, review)) {
                queueRemaining++;
            }
        }
        return new Counts(
                managed.size(),
                approved,
                rejected,
                deferred,
                maybe,
                disabled,
                pending,
                stale,
                queueRemaining
        );
    }

    /**
     * Records approval and snapshots the exact card into the review-only
     * {@code approved recipes} KJSGen project.
     */
    public synchronized boolean approve(RecipeInstance recipe) {
        return recordDecision(recipe, "approved", "approved", "", APPROVED_PROJECT);
    }

    /** Alias retained for callers that prefer the ledger operation's full name. */
    public synchronized boolean recordApprove(RecipeInstance recipe) {
        return approve(recipe);
    }

    /**
     * Records a rejection. The code is one of {@code manual},
     * {@code default_recipe}, {@code restore_default_recipe}, or
     * {@code ring_of_items}; invalid codes safely fall back to {@code manual}.
     */
    public synchronized boolean reject(RecipeInstance recipe, String code, String note) {
        String normalizedCode = code == null ? "manual" : code.trim().toLowerCase();
        if (!REJECTION_REASONS.contains(normalizedCode)) {
            LOGGER.warn("Unknown KJSGen recipe rejection code '{}'; using 'manual'", code);
            normalizedCode = "manual";
        }
        String normalizedNote = note == null ? "" : note.trim();
        if (normalizedNote.isEmpty()) {
            normalizedNote = defaultRejectionNote(normalizedCode);
        }
        return recordDecision(
                recipe,
                "rejected",
                normalizedCode,
                normalizedNote,
                REJECTED_PROJECT
        );
    }

    public synchronized boolean recordReject(RecipeInstance recipe, String code, String note) {
        return reject(recipe, code, note);
    }

    /** Parks the exact card in the Maybe queue for a later judgment. */
    public synchronized boolean maybe(RecipeInstance recipe) {
        return maybe(recipe, "");
    }

    /** Parks the exact card in the Maybe queue with an optional reviewer note. */
    public synchronized boolean maybe(RecipeInstance recipe, String note) {
        String normalizedNote = note == null ? "" : note.trim();
        if (normalizedNote.isEmpty()) {
            normalizedNote = "Maybe—return for another judgment pass.";
        }
        return recordDecision(
                recipe,
                "maybe",
                "maybe",
                normalizedNote,
                MAYBE_PROJECT
        );
    }

    public synchronized boolean recordMaybe(RecipeInstance recipe) {
        return maybe(recipe);
    }

    public synchronized boolean recordMaybe(RecipeInstance recipe, String note) {
        return maybe(recipe, note);
    }

    /** Defers the exact card because its identity or function needs investigation. */
    public synchronized boolean defer(RecipeInstance recipe) {
        return defer(recipe, "");
    }

    /** Defers the exact card with an optional investigation note. */
    public synchronized boolean defer(RecipeInstance recipe, String note) {
        String normalizedNote = note == null ? "" : note.trim();
        if (normalizedNote.isEmpty()) {
            normalizedNote = "Deferred until its icon and function are clear.";
        }
        return recordDecision(
                recipe,
                "deferred",
                "deferred",
                normalizedNote,
                DEFERRED_PROJECT
        );
    }

    public synchronized boolean recordDefer(RecipeInstance recipe) {
        return defer(recipe);
    }

    public synchronized boolean recordDefer(RecipeInstance recipe, String note) {
        return defer(recipe, note);
    }

    /** Disables the exact card using the default manual disable reason. */
    public synchronized boolean disable(RecipeInstance recipe) {
        return disable(recipe, "manual", "");
    }

    /**
     * Archives a deliberately disabled card. Disable reasons are separate from
     * ordinary recipe-rejection reasons because the recipe must not return to
     * Default's review queue or export path.
     */
    public synchronized boolean disable(RecipeInstance recipe, String code, String note) {
        String normalizedCode = code == null ? "manual" : code.trim().toLowerCase();
        if (!DISABLE_REASONS.contains(normalizedCode)) {
            LOGGER.warn("Unknown KJSGen recipe disable code '{}'; using 'manual'", code);
            normalizedCode = "manual";
        }
        String normalizedNote = note == null ? "" : note.trim();
        if (normalizedNote.isEmpty()) {
            normalizedNote = defaultDisableNote(normalizedCode);
        }
        return recordDecision(
                recipe,
                "disabled",
                normalizedCode,
                normalizedNote,
                DISABLED_PROJECT
        );
    }

    public synchronized boolean recordDisable(
            RecipeInstance recipe,
            String code,
            String note
    ) {
        return disable(recipe, code, note);
    }

    /** Effective pending queue: new and stale cards, in project display order. */
    public synchronized List<RecipeInstance> pendingRecipes(RecipeProject project) {
        return managedRecipes(project).stream()
                .filter(recipe -> isPendingForProject(project, review(recipe)))
                .toList();
    }

    public synchronized Optional<RecipeInstance> nextPending(RecipeProject project, String currentUid) {
        return traversePending(project, currentUid, 1);
    }

    public synchronized Optional<RecipeInstance> previousPending(RecipeProject project, String currentUid) {
        return traversePending(project, currentUid, -1);
    }

    /** SHA-256 over canonical sorted-key JSON containing only type, recipeId, slots, and params. */
    public static String cardSha256(RecipeInstance recipe) {
        JsonObject source = recipe.toJson();
        JsonObject design = new JsonObject();
        design.add("type", copyOrNull(source, "type"));
        design.add("recipeId", copyOrNull(source, "recipeId"));
        design.add("slots", copyOrEmptyObject(source, "slots"));
        design.add("params", copyOrEmptyObject(source, "params"));

        String canonical = COMPACT_GSON.toJson(sortRecursively(design));
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256")
                    .digest(canonical.getBytes(StandardCharsets.UTF_8));
            return "sha256:" + HexFormat.of().formatHex(digest);
        } catch (NoSuchAlgorithmException exception) {
            throw new IllegalStateException("The JVM does not provide SHA-256", exception);
        }
    }

    private boolean reviewable(RecipeInstance recipe) {
        if (!canReview(recipe)) {
            LOGGER.warn("Refused to review a KJSGen card without a recipe ID");
            return false;
        }
        if (!managedUids.contains(recipe.uid())) {
            if (projectNamed(project, DEFAULT_PROJECT)
                    && !persistManagedBaselineRecipe(recipe)) {
                return false;
            }
            managedUids.add(recipe.uid());
            LOGGER.info(
                    "Adopted newly created or unmanaged KJSGen card '{}' ({}) into review",
                    recipe.recipeId(), recipe.uid());
        }
        return true;
    }

    private boolean persistManagedBaselineRecipe(RecipeInstance recipe) {
        Path path = syncDirectory().resolve(MANAGED_BASELINE_FILE);
        try {
            JsonObject root;
            if (Files.isRegularFile(path)) {
                root = JsonParser.parseString(Files.readString(path, StandardCharsets.UTF_8))
                        .getAsJsonObject();
            } else {
                root = new JsonObject();
                root.addProperty("schema", 1);
                root.addProperty("project", DEFAULT_PROJECT);
            }

            JsonArray recipes = root.has("recipes") && root.get("recipes").isJsonArray()
                    ? root.getAsJsonArray("recipes")
                    : new JsonArray();
            for (JsonElement element : recipes) {
                if (element.isJsonObject()
                        && element.getAsJsonObject().has("uid")
                        && recipe.uid().equals(element.getAsJsonObject().get("uid").getAsString())) {
                    return true;
                }
            }

            recipes.add(recipe.toJson().deepCopy());
            root.add("recipes", recipes);
            atomicWrite(path, GSON.toJson(root) + System.lineSeparator());
            return true;
        } catch (Exception exception) {
            LOGGER.error(
                    "Failed to adopt KJSGen card '{}' ({}) into managed baseline {}",
                    recipe.recipeId(), recipe.uid(), path, exception);
            return false;
        }
    }

    private boolean recordDecision(
            RecipeInstance recipe,
            String status,
            String reason,
            String note,
            String destinationProject
    ) {
        if (!reviewable(recipe)) {
            return false;
        }
        String recipeId = recipe.recipeId();
        StoredReview previous = reviewsByRecipeId.get(recipeId);
        if (!putAndSave(recipe, status, reason, note)) {
            return false;
        }
        if (moveReviewSnapshot(recipe, destinationProject)) {
            synchronizeActiveArchive(recipe, destinationProject);
            return true;
        }

        restoreReview(recipeId, previous);
        if (!saveReviews()) {
            LOGGER.error(
                    "Failed to roll back review ledger after archive transition failed for '{}'",
                    recipeId);
        }
        return false;
    }

    private void restoreReview(String recipeId, StoredReview previous) {
        if (previous == null) {
            reviewsByRecipeId.remove(recipeId);
        } else {
            reviewsByRecipeId.put(recipeId, previous);
        }
    }

    private boolean putAndSave(RecipeInstance recipe, String status, String reason, String note) {
        String recipeId = recipe.recipeId();
        StoredReview previous = reviewsByRecipeId.put(recipeId, new StoredReview(
                recipe.uid(),
                status,
                reason,
                note,
                cardSha256(recipe)
        ));
        if (saveReviews()) {
            return true;
        }
        if (previous == null) {
            reviewsByRecipeId.remove(recipeId);
        } else {
            reviewsByRecipeId.put(recipeId, previous);
        }
        return false;
    }

    private Optional<RecipeInstance> traversePending(
            RecipeProject project,
            String currentUid,
            int direction
    ) {
        List<RecipeInstance> managed = managedRecipes(project);
        if (managed.isEmpty()) {
            return Optional.empty();
        }

        int currentIndex = -1;
        for (int index = 0; index < managed.size(); index++) {
            if (managed.get(index).uid().equals(currentUid)) {
                currentIndex = index;
                break;
            }
        }
        for (int offset = 1; offset <= managed.size(); offset++) {
            int index = Math.floorMod(currentIndex + direction * offset, managed.size());
            RecipeInstance candidate = managed.get(index);
            if (isPendingForProject(project, review(candidate))) {
                return Optional.of(candidate);
            }
        }
        return Optional.empty();
    }

    private static boolean isPendingForProject(RecipeProject project, Review review) {
        if (projectNamed(project, DEFERRED_PROJECT)) {
            return review.currentStatus() == Status.DEFERRED;
        }
        if (projectNamed(project, MAYBE_PROJECT)) {
            return review.currentStatus() == Status.MAYBE;
        }
        if (!projectNamed(project, DEFAULT_PROJECT)) {
            return review.effectiveStatus() == Status.PENDING
                    || review.effectiveStatus() == Status.STALE;
        }
        // Maybe and Deferred decisions stay out of Default even if their
        // canonical cards subsequently change. Their archived snapshots remain
        // intentionally parked until explicitly reclassified.
        return review.currentStatus() != Status.DEFERRED
                && review.currentStatus() != Status.MAYBE
                && review.currentStatus() != Status.DISABLED
                && (review.effectiveStatus() == Status.PENDING
                || review.effectiveStatus() == Status.STALE);
    }

    private static boolean isReviewProject(RecipeProject project) {
        return project != null && project.name() != null && !project.name().isBlank();
    }

    private static boolean isArchiveProject(RecipeProject project) {
        return REVIEW_ARCHIVE_PROJECTS.stream().anyMatch(name -> projectNamed(project, name));
    }

    private static boolean projectNamed(RecipeProject project, String expected) {
        return project != null
                && project.name() != null
                && expected.equalsIgnoreCase(project.name().trim());
    }

    private void loadManagedBaseline() {
        Path path = syncDirectory().resolve(MANAGED_BASELINE_FILE);
        if (!Files.isRegularFile(path)) {
            LOGGER.warn(
                    "KJSGen managed recipe review is unavailable because {} does not exist",
                    path.toAbsolutePath().normalize());
            return;
        }

        try {
            JsonObject root = JsonParser.parseString(Files.readString(path, StandardCharsets.UTF_8))
                    .getAsJsonObject();
            JsonArray recipes = root.has("recipes") && root.get("recipes").isJsonArray()
                    ? root.getAsJsonArray("recipes")
                    : new JsonArray();
            for (JsonElement element : recipes) {
                if (!element.isJsonObject()) {
                    continue;
                }
                JsonObject recipe = element.getAsJsonObject();
                if (recipe.has("uid") && recipe.get("uid").isJsonPrimitive()) {
                    String uid = recipe.get("uid").getAsString();
                    if (!uid.isBlank()) {
                        managedUids.add(uid);
                    }
                }
            }
        } catch (Exception exception) {
            managedUids.clear();
            LOGGER.error("Failed to load KJSGen managed recipe baseline from {}", path, exception);
        }
    }

    private void loadReviews() {
        Path path = reviewPath();
        if (!Files.isRegularFile(path)) {
            return;
        }

        try {
            JsonObject root = JsonParser.parseString(Files.readString(path, StandardCharsets.UTF_8))
                    .getAsJsonObject();
            int schemaVersion = root.has("schemaVersion")
                    ? root.get("schemaVersion").getAsInt()
                    : -1;
            String projectName = root.has("project")
                    ? root.get("project").getAsString()
                    : "";
            if ((schemaVersion != SCHEMA_VERSION
                    && schemaVersion != LEGACY_SCHEMA_VERSION)
                    || !DEFAULT_PROJECT.equals(projectName)) {
                LOGGER.error(
                        "Ignored incompatible KJSGen review ledger {} (schema {}, project '{}')",
                        path, schemaVersion, projectName);
                return;
            }

            if (!root.has("reviews") || !root.get("reviews").isJsonObject()) {
                return;
            }
            JsonObject reviews = root.getAsJsonObject("reviews");
            for (Map.Entry<String, JsonElement> entry : reviews.entrySet()) {
                readStoredReview(entry.getKey(), entry.getValue(), schemaVersion)
                        .ifPresent(review ->
                        reviewsByRecipeId.put(entry.getKey(), review));
            }
        } catch (Exception exception) {
            reviewsByRecipeId.clear();
            LOGGER.error("Failed to load KJSGen recipe reviews from {}", path, exception);
        }
    }

    /**
     * Historical archive snapshots may use UIDs retired from the current
     * managed baseline. Keep Default strictly baseline-scoped, but allow an
     * archive card whose recipe ID is still backed by the durable ledger.
     */
    private void includeLedgerBackedArchiveUids(RecipeProject project) {
        if (!isArchiveProject(project)) {
            return;
        }
        project.recipes().stream()
                .filter(recipe -> recipe.recipeId() != null
                        && reviewsByRecipeId.containsKey(recipe.recipeId()))
                .map(RecipeInstance::uid)
                .filter(uid -> uid != null && !uid.isBlank())
                .forEach(managedUids::add);
    }

    private Optional<StoredReview> readStoredReview(
            String recipeId,
            JsonElement element,
            int schemaVersion
    ) {
        if (recipeId == null || recipeId.isBlank() || !element.isJsonObject()) {
            return Optional.empty();
        }
        try {
            JsonObject object = element.getAsJsonObject();
            String uid = requiredString(object, "uid");
            String status = requiredString(object, "status");
            String reason = requiredString(object, "reason");
            String note = object.has("note") ? object.get("note").getAsString() : "";
            String hash = requiredString(object, "cardSha256");

            // Version 1 had one button internally called Maybe but displayed and
            // archived it as Deferred. Preserve those decisions as Deferred when
            // upgrading instead of silently turning them into the new Maybe state.
            if (schemaVersion == LEGACY_SCHEMA_VERSION
                    && "maybe".equals(status)
                    && "maybe".equals(reason)) {
                status = "deferred";
                reason = "deferred";
            }

            boolean validApproval = "approved".equals(status) && "approved".equals(reason);
            boolean validRejection = "rejected".equals(status) && REJECTION_REASONS.contains(reason);
            boolean validDeferred = "deferred".equals(status) && "deferred".equals(reason);
            boolean validMaybe = "maybe".equals(status) && "maybe".equals(reason);
            boolean validDisable = "disabled".equals(status) && DISABLE_REASONS.contains(reason);
            boolean validRevision = "pending".equals(status) && "revised_for_review".equals(reason);
            if ((!validApproval && !validRejection && !validDeferred
                    && !validMaybe && !validDisable && !validRevision)
                    || !hash.matches("sha256:[0-9a-f]{64}")) {
                LOGGER.warn("Ignored invalid KJSGen review entry for '{}'", recipeId);
                return Optional.empty();
            }
            return Optional.of(new StoredReview(uid, status, reason, note, hash));
        } catch (RuntimeException exception) {
            LOGGER.warn("Ignored malformed KJSGen review entry for '{}'", recipeId, exception);
            return Optional.empty();
        }
    }

    private boolean saveReviews() {
        JsonObject root = new JsonObject();
        root.addProperty("schemaVersion", SCHEMA_VERSION);
        root.addProperty("project", DEFAULT_PROJECT);
        JsonObject reviews = new JsonObject();
        reviewsByRecipeId.forEach((recipeId, review) -> {
            JsonObject object = new JsonObject();
            object.addProperty("uid", review.uid());
            object.addProperty("status", review.status());
            object.addProperty("reason", review.reason());
            object.addProperty("note", review.note());
            object.addProperty("cardSha256", review.cardSha256());
            reviews.add(recipeId, object);
        });
        root.add("reviews", reviews);

        Path path = reviewPath();
        try {
            atomicWrite(path, GSON.toJson(root) + System.lineSeparator());
            return true;
        } catch (IOException exception) {
            LOGGER.error("Failed to save KJSGen recipe reviews to {}", path, exception);
            return false;
        }
    }

    /**
     * Moves an exact card snapshot between the review-only archive projects.
     *
     * <p>The disk files are updated as one best-effort transaction: every
     * original byte sequence is captured before the first write, changed files
     * are written atomically, and any failure restores all files already
     * touched. The integrated-server cache is changed only after every disk
     * write succeeds.</p>
     */
    private boolean moveReviewSnapshot(RecipeInstance recipe, String destinationProject) {
        if (!REVIEW_ARCHIVE_PROJECTS.contains(destinationProject)) {
            LOGGER.error("Refused to move KJSGen review card to unknown archive '{}'", destinationProject);
            return false;
        }
        RecipeInstance snapshot = RecipeInstance.fromJson(recipe.toJson().deepCopy());
        MinecraftServer integratedServer = Minecraft.getInstance().getSingleplayerServer();
        if (integratedServer == null || integratedServer.isSameThread()) {
            Map<String, RecipeProject> serverCache = integratedServer == null
                    ? null
                    : KjsGenServerProjectStoreAccessor.industrialColonies$loadedProjects();
            return moveReviewSnapshotOnCurrentThread(snapshot, destinationProject, serverCache);
        }

        CompletableFuture<Boolean> result = new CompletableFuture<>();
        try {
            integratedServer.execute(() -> {
                try {
                    result.complete(moveReviewSnapshotOnCurrentThread(
                            snapshot,
                            destinationProject,
                            KjsGenServerProjectStoreAccessor.industrialColonies$loadedProjects()
                    ));
                } catch (Throwable throwable) {
                    result.completeExceptionally(throwable);
                }
            });
            // Do not time out a queued server mutation. A timeout could report
            // failure and roll the ledger back while the task later changes an
            // archive, leaving the two stores contradictory.
            return result.get();
        } catch (InterruptedException exception) {
            Thread.currentThread().interrupt();
            LOGGER.error("Interrupted while moving a KJSGen review archive snapshot", exception);
            return false;
        } catch (ExecutionException | RuntimeException | LinkageError exception) {
            LOGGER.error("Failed to update the integrated-server KJSGen review archives", exception);
            return false;
        }
    }

    private boolean moveReviewSnapshotOnCurrentThread(
            RecipeInstance snapshot,
            String destinationProject,
            Map<String, RecipeProject> serverCache
    ) {
        List<ArchiveMutation> mutations = new ArrayList<>();
        try {
            for (String archiveProject : REVIEW_ARCHIVE_PROJECTS) {
                mutations.add(prepareArchiveMutation(
                        archiveProject,
                        destinationProject,
                        snapshot,
                        serverCache
                ));
            }
        } catch (Exception | LinkageError exception) {
            LOGGER.error(
                    "Failed to prepare KJSGen review archive transition for '{}'",
                    snapshot.recipeId(), exception);
            return false;
        }

        List<ArchiveMutation> written = new ArrayList<>();
        try {
            for (ArchiveMutation mutation : mutations) {
                if (!mutation.changed()) {
                    continue;
                }
                // Include the in-flight target in rollback as well. A failed
                // fallback move can leave the destination state uncertain.
                written.add(mutation);
                atomicWrite(mutation.file(), encodeProject(mutation.project()));
            }
        } catch (IOException exception) {
            LOGGER.error(
                    "Failed to persist KJSGen review archive transition for '{}'",
                    snapshot.recipeId(), exception);
            restoreArchiveFiles(written);
            return false;
        }

        if (serverCache != null) {
            Map<String, RecipeProject> priorCache = new LinkedHashMap<>(serverCache);
            try {
                for (ArchiveMutation mutation : mutations) {
                    if (mutation.project() == null) {
                        continue;
                    }
                    removeArchiveCacheAliases(serverCache, mutation.projectName());
                    serverCache.put(
                            ProjectManager.sanitizeName(mutation.projectName()),
                            mutation.project()
                    );
                }
            } catch (RuntimeException exception) {
                try {
                    serverCache.clear();
                    serverCache.putAll(priorCache);
                } catch (RuntimeException restoreException) {
                    exception.addSuppressed(restoreException);
                }
                restoreArchiveFiles(written);
                LOGGER.error(
                        "Failed to update the KJSGen server review cache for '{}'",
                        snapshot.recipeId(), exception);
                return false;
            }
        }
        return true;
    }

    private ArchiveMutation prepareArchiveMutation(
            String archiveProject,
            String destinationProject,
            RecipeInstance snapshot,
            Map<String, RecipeProject> serverCache
    ) throws IOException {
        Path file = resolveArchiveFile(archiveProject);
        if (Files.exists(file) && !Files.isRegularFile(file)) {
            throw new IOException("KJSGen review archive is not a regular file: " + file);
        }
        boolean fileExisted = Files.isRegularFile(file);
        byte[] originalBytes = fileExisted ? Files.readAllBytes(file) : null;

        RecipeProject working = cachedArchive(serverCache, archiveProject)
                .map(KjsGenRecipeReviewStore::copyProject)
                .orElseGet(() -> loadArchiveFromBytes(file, originalBytes).orElse(null));
        boolean destination = archiveProject.equals(destinationProject);
        if (working == null && destination) {
            working = new RecipeProject(archiveProject);
        }

        boolean changed = false;
        if (working != null) {
            int priorSize = working.recipes().size();
            working.recipes().removeIf(existing -> sameRecipe(existing, snapshot));
            changed = working.recipes().size() != priorSize;
            if (!archiveProject.equals(working.name())) {
                working.setName(archiveProject);
                changed = true;
            }
        }

        if (destination) {
            working.add(RecipeInstance.fromJson(snapshot.toJson().deepCopy()));
            // A same-destination decision intentionally refreshes the exact
            // archived card and its position, even when the design is equal.
            changed = true;
        }
        return new ArchiveMutation(
                archiveProject,
                file,
                fileExisted,
                originalBytes,
                working,
                changed
        );
    }

    private static Optional<RecipeProject> cachedArchive(
            Map<String, RecipeProject> serverCache,
            String archiveProject
    ) {
        if (serverCache == null) {
            return Optional.empty();
        }
        String canonicalKey = ProjectManager.sanitizeName(archiveProject);
        RecipeProject exact = serverCache.get(canonicalKey);
        if (exact != null) {
            return Optional.of(exact);
        }
        return serverCache.entrySet().stream()
                .filter(entry -> entry.getKey().equalsIgnoreCase(canonicalKey)
                        || projectNamed(entry.getValue(), archiveProject))
                .map(Map.Entry::getValue)
                .filter(Objects::nonNull)
                .findFirst();
    }

    private static Optional<RecipeProject> loadArchiveFromBytes(Path file, byte[] bytes) {
        if (bytes == null) {
            return Optional.empty();
        }
        try {
            JsonObject json = JsonParser.parseString(new String(bytes, StandardCharsets.UTF_8))
                    .getAsJsonObject();
            return Optional.of(RecipeProject.fromJson(json));
        } catch (RuntimeException exception) {
            throw new IllegalArgumentException("Unreadable KJSGen review archive " + file, exception);
        }
    }

    private static RecipeProject copyProject(RecipeProject source) {
        return RecipeProject.fromJson(source.toJson().deepCopy());
    }

    private static boolean sameRecipe(RecipeInstance first, RecipeInstance second) {
        return Objects.equals(first.recipeId(), second.recipeId())
                || Objects.equals(first.uid(), second.uid());
    }

    private static byte[] encodeProject(RecipeProject project) {
        return (GSON.toJson(project.toJson()) + System.lineSeparator())
                .getBytes(StandardCharsets.UTF_8);
    }

    /** Uses an existing case-variant filename instead of creating a duplicate. */
    private static Path resolveArchiveFile(String archiveProject) throws IOException {
        Path canonical = ProjectManager.fileFor(archiveProject);
        if (Files.exists(canonical)) {
            return canonical;
        }
        Path directory = ProjectManager.projectsDir();
        if (!Files.isDirectory(directory)) {
            return canonical;
        }
        String expected = canonical.getFileName().toString();
        List<Path> matches;
        try (var paths = Files.list(directory)) {
            matches = paths
                    .filter(path -> path.getFileName().toString().equalsIgnoreCase(expected))
                    .toList();
        }
        if (matches.size() > 1) {
            throw new IOException(
                    "Ambiguous case-variant KJSGen review archive filenames for " + expected);
        }
        return matches.isEmpty() ? canonical : matches.getFirst();
    }

    private static void removeArchiveCacheAliases(
            Map<String, RecipeProject> serverCache,
            String archiveProject
    ) {
        String canonicalKey = ProjectManager.sanitizeName(archiveProject);
        List<String> aliases = serverCache.entrySet().stream()
                .filter(entry -> entry.getKey().equalsIgnoreCase(canonicalKey)
                        || projectNamed(entry.getValue(), archiveProject))
                .map(Map.Entry::getKey)
                .toList();
        aliases.forEach(serverCache::remove);
    }

    private static void restoreArchiveFiles(List<ArchiveMutation> written) {
        for (int index = written.size() - 1; index >= 0; index--) {
            ArchiveMutation mutation = written.get(index);
            try {
                if (mutation.fileExisted()) {
                    atomicWrite(mutation.file(), mutation.originalBytes());
                } else {
                    Files.deleteIfExists(mutation.file());
                }
            } catch (IOException rollbackException) {
                LOGGER.error(
                        "Failed to roll back KJSGen review archive {}",
                        mutation.file(), rollbackException);
            }
        }
    }

    /** Mirrors a successful disk move into the currently open archive tab. */
    private void synchronizeActiveArchive(
            RecipeInstance recipe,
            String destinationProject
    ) {
        if (!isArchiveProject(project)) {
            return;
        }
        project.recipes().removeIf(existing -> sameRecipe(existing, recipe));
        if (projectNamed(project, destinationProject)) {
            project.add(RecipeInstance.fromJson(recipe.toJson().deepCopy()));
        }
    }

    private static Path syncDirectory() {
        return FMLPaths.GAMEDIR.get()
                .resolve("kjsgen")
                .resolve("industrial_colonies_sync");
    }

    private static Path reviewPath() {
        return syncDirectory().resolve(REVIEW_FILE);
    }

    private static void atomicWrite(Path target, String contents) throws IOException {
        atomicWrite(target, contents.getBytes(StandardCharsets.UTF_8));
    }

    private static void atomicWrite(Path target, byte[] contents) throws IOException {
        Path parent = target.toAbsolutePath().normalize().getParent();
        Files.createDirectories(parent);
        Path temporary = Files.createTempFile(parent, target.getFileName().toString(), ".tmp");
        try {
            Files.write(
                    temporary,
                    contents,
                    StandardOpenOption.TRUNCATE_EXISTING,
                    StandardOpenOption.WRITE
            );
            try {
                Files.move(
                        temporary,
                        target,
                        StandardCopyOption.ATOMIC_MOVE,
                        StandardCopyOption.REPLACE_EXISTING
                );
            } catch (AtomicMoveNotSupportedException exception) {
                Files.move(temporary, target, StandardCopyOption.REPLACE_EXISTING);
            }
        } finally {
            Files.deleteIfExists(temporary);
        }
    }

    private static String requiredString(JsonObject object, String key) {
        if (!object.has(key) || !object.get(key).isJsonPrimitive()) {
            throw new IllegalArgumentException("Missing string property " + key);
        }
        String value = object.get(key).getAsString();
        if (value.isBlank()) {
            throw new IllegalArgumentException("Blank string property " + key);
        }
        return value;
    }

    private static String defaultRejectionNote(String reason) {
        return switch (reason) {
            case "default_recipe" -> "Keep the default recipe.";
            case "restore_default_recipe" ->
                    "Restore the original mod recipe; remove this custom replacement.";
            case "ring_of_items" -> "Replace the ring-of-items layout with a functional design.";
            default -> "Rejected during manual recipe review.";
        };
    }

    private static String defaultDisableNote(String reason) {
        return switch (reason) {
            case "redundant_mechanic" -> "Disable this redundant mechanic.";
            case "duplicate_machine" -> "Disable this duplicate machine or recipe.";
            case "progression_bypass" -> "Disable this progression bypass.";
            case "internal_unused" -> "Disable this internal or unused recipe.";
            default -> "Disable this recipe.";
        };
    }

    private static JsonElement copyOrNull(JsonObject source, String key) {
        return source.has(key) ? source.get(key).deepCopy() : JsonNull.INSTANCE;
    }

    private static JsonElement copyOrEmptyObject(JsonObject source, String key) {
        return source.has(key) ? source.get(key).deepCopy() : new JsonObject();
    }

    private static JsonElement sortRecursively(JsonElement element) {
        if (element == null || element.isJsonNull() || element.isJsonPrimitive()) {
            return element == null ? JsonNull.INSTANCE : element.deepCopy();
        }
        if (element.isJsonArray()) {
            JsonArray sorted = new JsonArray();
            for (JsonElement child : element.getAsJsonArray()) {
                sorted.add(sortRecursively(child));
            }
            return sorted;
        }

        JsonObject sorted = new JsonObject();
        element.getAsJsonObject().entrySet().stream()
                .sorted(Map.Entry.comparingByKey())
                .forEach(entry -> sorted.add(entry.getKey(), sortRecursively(entry.getValue())));
        return sorted;
    }

    public enum Status {
        PENDING,
        APPROVED,
        REJECTED,
        DEFERRED,
        MAYBE,
        DISABLED,
        STALE
    }

    public record Review(
            String uid,
            Status currentStatus,
            Status effectiveStatus,
            String reason,
            String note,
            String cardSha256
    ) {
        private static Review pending() {
            return new Review("", Status.PENDING, Status.PENDING, "", "", "");
        }
    }

    public record Counts(
            int managed,
            int approved,
            int rejected,
            int deferred,
            int maybe,
            int disabled,
            int pending,
            int stale,
            int queueRemaining
    ) {
        public int remaining() {
            return queueRemaining;
        }
    }

    private record ArchiveMutation(
            String projectName,
            Path file,
            boolean fileExisted,
            byte[] originalBytes,
            RecipeProject project,
            boolean changed
    ) {
    }

    private record StoredReview(
            String uid,
            String status,
            String reason,
            String note,
            String cardSha256
    ) {
    }
}
