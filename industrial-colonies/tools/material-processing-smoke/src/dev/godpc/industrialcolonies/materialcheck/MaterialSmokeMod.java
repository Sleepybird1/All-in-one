package dev.godpc.industrialcolonies.materialcheck;

import net.neoforged.fml.common.Mod;
import net.neoforged.bus.api.IEventBus;

@Mod("ic_material_smoke")
public final class MaterialSmokeMod {
    public MaterialSmokeMod(IEventBus modBus) { StageProjectExport.register(modBus); }
}
