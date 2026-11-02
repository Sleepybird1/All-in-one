package dev.godpc.industrialcolonies.mixin;

import com.zizazr.kjsgen.integration.net.KjsGenS2CPayload;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.Constant;
import org.spongepowered.asm.mixin.injection.ModifyConstant;

/**
 * Allows KJSGen to synchronize projects whose serialized snapshot is larger
 * than its built-in one-megabyte string codec limit.
 *
 * <p>KJSGen uses the received snapshot to mark its client edit session as
 * remote. If encoding the initial snapshot fails, even an integrated-server
 * session falls back to local-only behavior and newly created projects are
 * never persisted. Architectury handles payload aggregation; this limit is
 * the per-string guard selected by KJSGen's S2C codec.</p>
 */
@Mixin(value = KjsGenS2CPayload.class, remap = false)
public abstract class KjsGenS2CPayloadMixin {
    private static final int INDUSTRIAL_COLONIES_MAX_SNAPSHOT_CHARS =
            8 * 1024 * 1024;

    @ModifyConstant(
            method = "<clinit>",
            constant = @Constant(intValue = 1024 * 1024),
            require = 1
    )
    private static int industrialColonies$raiseSnapshotStringLimit(int originalLimit) {
        return INDUSTRIAL_COLONIES_MAX_SNAPSHOT_CHARS;
    }
}
