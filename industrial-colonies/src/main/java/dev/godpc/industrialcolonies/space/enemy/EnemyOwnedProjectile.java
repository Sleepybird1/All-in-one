package dev.godpc.industrialcolonies.space.enemy;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import java.util.*;

/** Staged exact-projectile custody, with no firing permission or automatic
 * registration. Only a trusted emitter in this package may bind its freshly
 * emitted stock bullet. Persistent markers never restore runtime authority:
 * marked orphans stop, while unrelated unmarked manual projectiles pass through.
 * Native hooks must guard tick, penetration, entity damage and impact force. */
public final class EnemyOwnedProjectile {
    public static final String KEY="IndustrialColoniesNpcProjectileV1";
    private record Owner(Entity projectile,EnemyCannonHold cannon,
            EnemyImpactAuthority authority,UUID nonce,long created,int lifetime) {}
    private static final Map<UUID,Owner> OWNERS=new HashMap<>();
    private EnemyOwnedProjectile() {}
    /** Runtime ownership must not retain a stopped server or its level. Markers
     * remain on discarded entities so a later native reload still refuses them. */
    static void releaseServer(net.minecraft.server.MinecraftServer server) {
        if(!server.isSameThread())throw new IllegalStateException("Server-thread projectile cleanup required");
        for(var owner:List.copyOf(OWNERS.values()))
            if(owner.projectile().level().getServer()==server)stop(owner.projectile());
    }
    /** Not an adoption API. Caller must prove this is its one actual emission. */
    static boolean bind(Entity projectile,EnemyCannonHold cannon,
            EnemyImpactAuthority authority,int lifetime) {
        if(projectile==null||cannon==null||authority==null||lifetime<1||lifetime>20
                ||!(projectile.level() instanceof ServerLevel level)
                ||!level.getServer().isSameThread()||projectile.isRemoved()
                ||projectile.tickCount!=0||projectile.level()!=authority.source().getLevel()
                ||!BuiltInRegistries.ENTITY_TYPE.getKey(projectile.getType()).toString()
                    .equals("createbigcannons:machine_gun_bullet"))return false;
        // Discarded entities need no retained runtime authority. Do not delete
        // markers: a later reload must still refuse the original orphan.
        OWNERS.entrySet().removeIf(e->e.getValue().projectile().level().getServer()==level.getServer()
                &&e.getValue().projectile().isRemoved());
        if(OWNERS.size()>=128||OWNERS.containsKey(projectile.getUUID())
                ||projectile.getPersistentData().contains(KEY)
                ||!cannon.owns(authority.source(),authority.hull())
                ||!authority.flight().allowed())return false;
        var nonce=UUID.randomUUID();var marker=new CompoundTag();
        marker.putInt("Format",1);marker.putUUID("Projectile",projectile.getUUID());
        marker.putUUID("Nonce",nonce);
        projectile.getPersistentData().put(KEY,marker);
        OWNERS.put(projectile.getUUID(),new Owner(projectile,cannon,authority,nonce,
                level.getGameTime(),lifetime));return true;
    }
    private static boolean marked(Entity projectile){return projectile.getPersistentData().contains(KEY);}
    private static boolean tracked(Entity projectile) {
        if(!(projectile.level() instanceof ServerLevel level)||!level.getServer().isSameThread())
            throw new IllegalStateException("Server-thread owned projectile required");
        // Removing the marker cannot turn an already owned projectile into an
        // unrestricted manual shot within this runtime.
        return marked(projectile)||OWNERS.containsKey(projectile.getUUID());
    }
    private static Owner owner(Entity projectile) {
        if(!(projectile.level() instanceof ServerLevel level)||!level.getServer().isSameThread())
            throw new IllegalStateException("Server-thread owned projectile required");
        try {
            var owner=OWNERS.get(projectile.getUUID());
            if(owner==null||owner.projectile()!=projectile||projectile.isRemoved()
                    ||!projectile.getPersistentData().contains(KEY,Tag.TAG_COMPOUND))return null;
            var marker=projectile.getPersistentData().getCompound(KEY);
            long now=level.getGameTime();
            if(marker.getAllKeys().size()!=3||!marker.contains("Format",Tag.TAG_INT)
                    ||marker.getInt("Format")!=1||!marker.hasUUID("Projectile")
                    ||!marker.getUUID("Projectile").equals(projectile.getUUID())
                    ||!marker.hasUUID("Nonce")||!marker.getUUID("Nonce").equals(owner.nonce())
                    ||now<owner.created()||now-owner.created()>=owner.lifetime()
                    ||!owner.cannon().owns(owner.authority().source(),owner.authority().hull())
                    ||!owner.authority().flight().allowed())return null;
            return owner;
        }catch(RuntimeException unavailable){return null;}
    }
    private static boolean stop(Entity projectile) {
        var owned=OWNERS.get(projectile.getUUID());
        if(owned!=null&&owned.projectile()==projectile)OWNERS.remove(projectile.getUUID());
        projectile.discard();return false;
    }
    /** Marked orphan or invalid/expired authority cannot take another native tick. */
    public static boolean beforeTick(Entity projectile) {
        if(projectile.level().isClientSide||!tracked(projectile))return true;
        return owner(projectile)!=null||stop(projectile);
    }
    public static boolean beforeBlock(Entity projectile,BlockHitResult hit) {
        if(projectile.level().isClientSide||!tracked(projectile))return true;
        var owner=owner(projectile);
        return owner!=null&&owner.authority().block(hit).allowed()||stop(projectile);
    }
    public static boolean beforeEntity(Entity projectile) {
        if(projectile.level().isClientSide||!tracked(projectile))return true;
        var owner=owner(projectile);
        return owner!=null&&owner.authority().entity().allowed()||stop(projectile);
    }
    /** Recheck at native impact-force entry even after an allowed penetration. */
    public static boolean beforeImpact(Entity projectile,HitResult hit) {
        if(projectile.level().isClientSide||!tracked(projectile))return true;
        if(hit instanceof BlockHitResult block)return beforeBlock(projectile,block);
        return beforeEntity(projectile);
    }
}
