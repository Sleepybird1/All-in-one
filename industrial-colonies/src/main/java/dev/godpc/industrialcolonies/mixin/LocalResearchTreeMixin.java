package dev.godpc.industrialcolonies.mixin;

import com.minecolonies.api.colony.IColony;
import com.minecolonies.api.research.IGlobalResearch;
import com.minecolonies.api.research.IGlobalResearchTree;
import com.minecolonies.api.research.ILocalResearch;
import com.minecolonies.api.research.ILocalResearchTree;
import com.minecolonies.api.research.IResearchEffectManager;
import com.minecolonies.api.research.util.ResearchState;
import com.minecolonies.core.colony.buildings.workerbuildings.BuildingUniversity;
import com.minecolonies.core.research.LocalResearchTree;
import dev.godpc.industrialcolonies.research.IndustrialResearchIds;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.HashMap;
import java.util.Map;

/**
 * Removes MineColonies' one-depth-six-research limit for the pack's single
 * research tab and safely folds saves from the former eleven tabs into it.
 */
@Mixin(value = LocalResearchTree.class, remap = false)
public abstract class LocalResearchTreeMixin {
    private static final String RESEARCH_TREE_TAG = "researchTree";
    private static final String FACTORY_DATA_TAG = "Data";
    private static final String BRANCH_TAG = "branch";
    private static final String RESEARCH_ID_TAG = "id";
    private static final String DEPTH_TAG = "depth";
    private static final String STATE_TAG = "state";
    private static final String PROGRESS_TAG = "progress";

    @Inject(method = "branchFinishedHighestLevel", at = @At("HEAD"), cancellable = true, remap = false)
    private void industrialColonies$allowEveryTechTreeLeaf(
            ResourceLocation branch,
            CallbackInfoReturnable<Boolean> callback
    ) {
        if (IndustrialResearchIds.isTechTree(branch)) {
            callback.setReturnValue(false);
        }
    }

    /**
     * Creative authors can deliberately force-complete any unfinished Tech
     * Tree research. Every non-Creative request is still checked against both
     * the structural parent and every explicit AND requirement at the
     * authoritative server start point.
     */
    @Inject(method = "attemptBeginResearch", at = @At("HEAD"), cancellable = true, remap = false)
    private void industrialColonies$enforceTechTreePrerequisites(
            Player player,
            IColony colony,
            BuildingUniversity university,
            IGlobalResearch globalResearch,
            CallbackInfo callback
    ) {
        if (globalResearch == null || colony == null
                || !IndustrialResearchIds.isTechTree(globalResearch.getBranch())) {
            return;
        }

        // Handle the one stock TryResearchMessage completely here. This avoids
        // re-entering MineColonies' normal cost/level/slot path and makes the
        // Tech Tree authoring action independent of its Creative-completion
        // config, without sending or requiring a second client message.
        if (player != null && player.isCreative()) {
            industrialColonies$forceCompleteCreativeResearch(colony, globalResearch);
            callback.cancel();
            return;
        }

        ILocalResearchTree localTree = colony.getResearchManager().getResearchTree();
        ILocalResearch existing = localTree.getResearch(globalResearch.getBranch(), globalResearch.getId());
        if (existing == null && !globalResearch.canResearch(university, localTree)) {
            industrialColonies$rejectOutOfOrderResearch(player, callback);
            return;
        }

        ResourceLocation parent = globalResearch.getParent();
        if (parent != null && !localTree.hasCompletedResearch(parent)) {
            industrialColonies$rejectOutOfOrderResearch(player, callback);
            return;
        }

        if (!IGlobalResearchTree.getInstance().isResearchRequirementsFulfilled(
                globalResearch.getResearchRequirements(), colony)) {
            industrialColonies$rejectOutOfOrderResearch(player, callback);
        }
    }

    private static void industrialColonies$forceCompleteCreativeResearch(
            IColony colony,
            IGlobalResearch globalResearch
    ) {
        ILocalResearchTree localTree = colony.getResearchManager().getResearchTree();
        ILocalResearch localResearch = localTree.getResearch(globalResearch.getBranch(), globalResearch.getId());
        if (localResearch == null) {
            globalResearch.startResearch(localTree);
            localResearch = localTree.getResearch(globalResearch.getBranch(), globalResearch.getId());
        }

        if (localResearch == null || localResearch.getState() == ResearchState.FINISHED) {
            return;
        }

        int baseTime = IGlobalResearchTree.getInstance()
                .getBranchData(globalResearch.getBranch())
                .getBaseTime(globalResearch.getDepth());
        localResearch.setState(ResearchState.IN_PROGRESS);
        localResearch.setProgress(Math.max(0, baseTime - 1));
        localResearch.research(colony.getResearchManager().getResearchEffects(), localTree);
        colony.getResearchManager().markDirty();
        colony.markDirty();
    }

    @Inject(method = "attemptResetResearch", at = @At("HEAD"), cancellable = true, remap = false)
    private void industrialColonies$protectImmutableTechResearch(
            Player player,
            IColony colony,
            ILocalResearch localResearch,
            CallbackInfo callback
    ) {
        if (localResearch == null || !IndustrialResearchIds.isTechTree(localResearch.getBranch())) {
            return;
        }

        IGlobalResearchTree globalTree = IGlobalResearchTree.getInstance();
        if (!globalTree.hasResearch(IndustrialResearchIds.TECH_TREE, localResearch.getId())) {
            return;
        }

        IGlobalResearch globalResearch = globalTree.getResearch(
                IndustrialResearchIds.TECH_TREE, localResearch.getId());
        if (globalResearch != null && globalResearch.isImmutable()) {
            callback.cancel();
        }
    }

    @Inject(method = "readFromNBT", at = @At("HEAD"), remap = false)
    private void industrialColonies$migrateLegacyResearchBranches(
            HolderLookup.Provider provider,
            CompoundTag colonyResearch,
            IResearchEffectManager effects,
            CallbackInfo callback
    ) {
        ListTag serializedResearch = colonyResearch.getList(RESEARCH_TREE_TAG, Tag.TAG_COMPOUND);
        IGlobalResearchTree globalTree = IGlobalResearchTree.getInstance();
        Map<ResourceLocation, CompoundTag> migratedByResearchId = new HashMap<>();
        for (int index = 0; index < serializedResearch.size();) {
            CompoundTag factoryEntry = serializedResearch.getCompound(index);
            if (!factoryEntry.contains(FACTORY_DATA_TAG, Tag.TAG_COMPOUND)) {
                index++;
                continue;
            }

            CompoundTag researchData = factoryEntry.getCompound(FACTORY_DATA_TAG);
            ResourceLocation oldBranch = ResourceLocation.tryParse(researchData.getString(BRANCH_TAG));
            ResourceLocation researchId = ResourceLocation.tryParse(researchData.getString(RESEARCH_ID_TAG));
            if (oldBranch == null || researchId == null) {
                index++;
                continue;
            }

            boolean isLegacyBranch = IndustrialResearchIds.LEGACY_BRANCHES.contains(oldBranch);
            if (isLegacyBranch && !globalTree.hasResearch(IndustrialResearchIds.TECH_TREE, researchId)) {
                index++;
                continue;
            }

            if (isLegacyBranch) {
                researchData.putString(BRANCH_TAG, IndustrialResearchIds.TECH_TREE.toString());
                oldBranch = IndustrialResearchIds.TECH_TREE;
            }

            if (!IndustrialResearchIds.isTechTree(oldBranch)) {
                index++;
                continue;
            }

            // State and progress remain intact. Updating only the structural
            // depth makes an in-progress legacy research use the current node's
            // timing and University-level rules after migration.
            if (!globalTree.hasResearch(IndustrialResearchIds.TECH_TREE, researchId)) {
                index++;
                continue;
            }

            IGlobalResearch currentResearch = globalTree.getResearch(
                    IndustrialResearchIds.TECH_TREE, researchId);
            if (currentResearch != null) {
                researchData.putInt(DEPTH_TAG, currentResearch.getDepth());
            }

            CompoundTag existing = migratedByResearchId.putIfAbsent(researchId, researchData);
            if (existing == null) {
                index++;
                continue;
            }

            // A partially tested pack may contain the same stable research ID
            // in both a legacy branch and the new tab. Collapse that safely:
            // FINISHED beats IN_PROGRESS beats NOT_STARTED, and no progress is
            // lost. The stock loader then applies effects exactly once.
            existing.putInt(STATE_TAG, Math.max(validState(existing), validState(researchData)));
            existing.putInt(PROGRESS_TAG, Math.max(
                    Math.max(0, existing.getInt(PROGRESS_TAG)),
                    Math.max(0, researchData.getInt(PROGRESS_TAG))));
            serializedResearch.remove(index);
        }
    }

    private static int validState(CompoundTag researchData) {
        return Math.max(0, Math.min(2, researchData.getInt(STATE_TAG)));
    }

    private static void industrialColonies$rejectOutOfOrderResearch(Player player, CallbackInfo callback) {
        if (player != null) {
            player.displayClientMessage(
                    Component.translatable("com.minecolonies.coremod.research.requirementnotmet"), false);
        }
        callback.cancel();
    }
}
