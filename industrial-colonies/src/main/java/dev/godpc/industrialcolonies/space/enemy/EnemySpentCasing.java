package dev.godpc.industrialcolonies.space.enemy;

import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import java.util.*;

/** Exact native byproduct provenance, not an item-type exemption or adoption
 * API. Physical outputs are never discarded/refunded by this registry. Marked
 * copies, changed/merged stacks, expired records and restart orphans receive no
 * movement recognition. No automatic registration or resource reconstruction. */
public final class EnemySpentCasing {
    public static final String KEY="IndustrialColoniesNpcCasingV1";
    private record Owner(ItemEntity entity,ServerSubLevel source,NativeEnemyHull hull,
                         ItemStack original,UUID nonce,long created) {}
    private static final Map<UUID,Owner> OWNERS=new HashMap<>();
    private EnemySpentCasing() {}
    static boolean bind(Entity candidate,ServerSubLevel source,NativeEnemyHull hull) {
        if(!(candidate instanceof ItemEntity entity)||source==null||hull==null
                ||entity.level()!=source.getLevel()||!source.getLevel().getServer().isSameThread()
                ||entity.isRemoved()||entity.tickCount!=0||source.getLevel().getEntity(entity.getUUID())!=null
                ||entity.getPersistentData().contains(KEY)||!hull.belongsTo(source))return false;
        ItemStack stack=entity.getItem();
        if(stack.getCount()!=1||!BuiltInRegistries.ITEM.getKey(stack.getItem()).toString().equals("createbigcannons:empty_machine_gun_round")
                ||!ItemStack.isSameItemSameComponents(stack,new ItemStack(stack.getItem())))return false;
        long now=source.getLevel().getGameTime();
        OWNERS.entrySet().removeIf(e->e.getValue().entity().isRemoved()
                ||e.getValue().entity().level()==source.getLevel()&&now-e.getValue().created()>=600);
        if(OWNERS.size()>=128||OWNERS.containsKey(entity.getUUID()))return false;
        UUID nonce=UUID.randomUUID();CompoundTag tag=new CompoundTag();
        tag.putInt("Format",1);tag.putUUID("Entity",entity.getUUID());tag.putUUID("Source",source.getUniqueId());tag.putUUID("Nonce",nonce);
        entity.getPersistentData().put(KEY,tag);
        OWNERS.put(entity.getUUID(),new Owner(entity,source,hull,stack.copy(),nonce,now));return true;
    }
    static void admissionFailed(Entity entity) {
        var owner=OWNERS.get(entity.getUUID());if(owner!=null&&owner.entity()==entity)OWNERS.remove(entity.getUUID());
    }
    static void releaseServer(net.minecraft.server.MinecraftServer server) {
        if(!server.isSameThread())throw new IllegalStateException("Server-thread casing cleanup required");
        OWNERS.entrySet().removeIf(e->e.getValue().source().getLevel().getServer()==server);
    }
    public static boolean ownedBy(ServerSubLevel source,Entity candidate) {
        if(source==null||candidate==null||!(candidate.level() instanceof ServerLevel level)
                ||!level.getServer().isSameThread())return false;
        var owner=OWNERS.get(candidate.getUUID());
        if(owner==null||owner.entity()!=candidate||owner.source()!=source||candidate.isRemoved()
                ||level!=source.getLevel()||level.getEntity(candidate.getUUID())!=candidate
                ||!candidate.getPersistentData().contains(KEY,Tag.TAG_COMPOUND))return false;
        var tag=candidate.getPersistentData().getCompound(KEY);long now=level.getGameTime();
        if(tag.getAllKeys().size()!=4||!tag.contains("Format",Tag.TAG_INT)||tag.getInt("Format")!=1
                ||!tag.hasUUID("Entity")||!tag.getUUID("Entity").equals(candidate.getUUID())
                ||!tag.hasUUID("Source")||!tag.getUUID("Source").equals(source.getUniqueId())
                ||!tag.hasUUID("Nonce")||!tag.getUUID("Nonce").equals(owner.nonce())
                ||now<owner.created()||now-owner.created()>=600)return false;
        var stack=owner.entity().getItem();
        return stack.getCount()==owner.original().getCount()&&ItemStack.isSameItemSameComponents(stack,owner.original())
                &&EnemyTargetSelector.mayControlSource(source,owner.hull())
                &&EnemyNativeFrame.contains(source,candidate.getBoundingBox());
    }
}
