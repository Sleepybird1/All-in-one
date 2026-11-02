package dev.godpc.industrialcolonies.geology;

import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.repository.Pack;
import net.minecraft.server.packs.repository.PackSource;
import net.neoforged.fml.ModList;
import net.neoforged.neoforge.event.AddPackFindersEvent;

/** Restore only WWOO's disabled decorative blobs; never replace its lava or landscape features. */
public final class GeologyCompatibilityPacks {
    private GeologyCompatibilityPacks() {}

    public static void registerPacks(AddPackFindersEvent event) {
        if(event.getPackType()!=PackType.SERVER_DATA||!ModList.get().isLoaded("wwoo"))return;
        event.addPackFinders(ResourceLocation.fromNamespaceAndPath("industrial_colonies","resourcepacks/ic_wwoo_decorative"),
                PackType.SERVER_DATA,Component.literal("Industrial Colonies - WWOO Decorative Geology"),
                PackSource.BUILT_IN,true,Pack.Position.TOP);
    }
}
