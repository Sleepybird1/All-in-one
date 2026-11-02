package dev.godpc.industrialcolonies.geology;

import java.security.MessageDigest;
import java.util.HexFormat;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/** Narrow guard for the installed ReTerraForged aquifer-height optimization. */
public final class ReTerraForgedAquiferCompatibility {
    private static final Logger LOGGER = LoggerFactory.getLogger(ReTerraForgedAquiferCompatibility.class);
    private static final String RESOURCE = "raccoonman/reterraforged/mixin/MixinNoiseChunk.class";
    private static final String REVIEWED_SHA256 = "2a4c655a65acbf5d4a170757abec2085b5444a1538a03121022ac2e72e4d538b";
    private static final boolean AFFECTED_BUILD = inspect();

    private ReTerraForgedAquiferCompatibility() {}

    public static boolean isAffectedBuild() {
        return AFFECTED_BUILD;
    }

    private static boolean inspect() {
        // Read original resource bytes without linking any optional ReTerraForged class.
        try (var input = ReTerraForgedAquiferCompatibility.class.getClassLoader().getResourceAsStream(RESOURCE)) {
            if (input == null) return false;
            String actual = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(input.readAllBytes()));
            if (!REVIEWED_SHA256.equals(actual)) {
                LOGGER.warn("ReTerraForged aquifer compatibility not applied: unreviewed implementation {}", actual);
                return false;
            }
            LOGGER.info("ReTerraForged aquifer compatibility enabled for the reviewed height-cap implementation");
            return true;
        } catch (Exception exception) {
            LOGGER.warn("Unable to inspect optional ReTerraForged aquifer compatibility; retaining existing behavior", exception);
            return false;
        }
    }
}
