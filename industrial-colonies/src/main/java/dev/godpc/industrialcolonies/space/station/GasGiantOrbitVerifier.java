package dev.godpc.industrialcolonies.space.station;

import dev.devce.rocketnautics.content.orbit.DeepSpaceData;
import dev.devce.rocketnautics.content.orbit.DeepSpaceInstance;
import dev.devce.rocketnautics.api.orbit.DeepSpaceHelper;
import dev.devce.rocketnautics.content.orbit.universe.CubePlanet;
import dev.devce.rocketnautics.content.orbit.universe.DeepSpacePosition;
import dev.devce.rocketnautics.content.orbit.universe.UniverseDefinition;
import dev.devce.rocketnautics.shaded.hipparchus.geometry.euclidean.threed.Vector3D;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import java.util.OptionalDouble;
import java.util.OptionalInt;
import org.joml.Vector3dc;

/** Fail-closed verifier for the installed Rocketnautics gas-giant frame. */
public final class GasGiantOrbitVerifier {
    public static final String GAS_GIANT_FRAME = "gas_giant";
    public static final double MIN_EXTRACTION_ALTITUDE = 250_000.0D;
    public static final double MAX_EXTRACTION_ALTITUDE = 2_500_000.0D;

    private GasGiantOrbitVerifier() {
    }

    public static OptionalDouble verifiedAltitude(ServerSubLevel station) {
        if (station.isRemoved() || !StationLifeSupport.DEEP_SPACE.equals(station.getLevel().dimension())) {
            return OptionalDouble.empty();
        }
        Vector3dc pose = station.logicalPose().position();
        DeepSpaceData data;
        try {
            data = DeepSpaceData.getInstance(station.getLevel().getServer());
        } catch (RuntimeException ignored) {
            return OptionalDouble.empty();
        }
        DeepSpaceInstance instance = data.getInstanceForPos(
                (int) pose.x(),
                (int) pose.z());
        if (instance == null
                || instance.isCorrupted()
                || !instance.boundingBox().contains(pose.x(), pose.y(), pose.z())) {
            return OptionalDouble.empty();
        }

        UniverseDefinition universe = data.getUniverse();
        OptionalInt gasGiantId = universe.getIDByFrameName(GAS_GIANT_FRAME);
        if (gasGiantId.isEmpty()) {
            return OptionalDouble.empty();
        }
        CubePlanet gasGiant = universe.getPlanetById(gasGiantId.getAsInt());
        DeepSpacePosition position = instance.getPosition();
        if (gasGiant == null
                || position.getFrame() != gasGiant.orekitFrame()
                || !GAS_GIANT_FRAME.equals(position.getFrame().getName())
                || DeepSpaceHelper.isSphereShape()) {
            return OptionalDouble.empty();
        }
        Vector3D bodyPosition = gasGiant.getRotationAtTime(position.getLocalUniverseTime())
                .applyInverseTo(position.getPosition(gasGiant.orekitFrame()));
        double dx = Math.max(0.0D, Math.abs(bodyPosition.getX()) - gasGiant.radius());
        double dy = Math.max(0.0D, Math.abs(bodyPosition.getY()) - gasGiant.radius());
        double dz = Math.max(0.0D, Math.abs(bodyPosition.getZ()) - gasGiant.radius());
        double altitude = Math.sqrt(dx * dx + dy * dy + dz * dz);
        if (!Double.isFinite(altitude)
                || altitude < MIN_EXTRACTION_ALTITUDE
                || altitude > MAX_EXTRACTION_ALTITUDE) {
            return OptionalDouble.empty();
        }
        return OptionalDouble.of(altitude);
    }

    public static boolean isInExtractionBand(ServerSubLevel station) {
        return verifiedAltitude(station).isPresent();
    }
}
