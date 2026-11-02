package dev.godpc.industrialcolonies.space.enemy;
/** Optional native boundaries; absent hooks never admit autonomous rotation. */
public interface EnemyNativeTurretHooks {
 default boolean ic$enemyRotationReadGuard(){return false;}
 default boolean ic$enemyRotationWriteGuard(){return false;}
}
