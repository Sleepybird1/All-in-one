package dev.godpc.industrialcolonies.geology.oil;

import java.io.IOException;
import net.minecraft.SharedConstants;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.level.storage.DimensionDataStorage;
import net.neoforged.neoforge.common.IOUtilities;

/** Native asynchronous publication plus independent disk equality check.
 * Caller owns the server thread and must block extraction until this returns.
 * This is not an OS/power-loss or multi-file transaction guarantee. */
public final class NativeOilPublication {
    private NativeOilPublication() {}
    public static CompoundTag publish(DimensionDataStorage storage,SavedData data,CompoundTag expected)throws IOException {
        var snapshot=expected.copy();
        data.setDirty();
        storage.save();
        IOUtilities.waitUntilIOWorkerComplete();
        var disk=storage.readTagFromDisk("tfmg_deposits",null,SharedConstants.getCurrentVersion().getDataVersion().getVersion());
        var actual=disk.getCompound("data");
        if(!snapshot.equals(actual))throw new IOException("Native oil disk readback differs from admitted state");
        return actual;
    }
}
