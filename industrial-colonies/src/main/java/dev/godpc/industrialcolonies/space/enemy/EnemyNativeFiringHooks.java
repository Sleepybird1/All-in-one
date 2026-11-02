package dev.godpc.industrialcolonies.space.enemy;

/** Optional native guard capability. Every absent hook defaults to refusal.
 * Implementations are supplied by the staged, independently qualified mixins. */
public interface EnemyNativeFiringHooks {
    default boolean ic$enemyShotGuard(){return false;}
    default boolean ic$enemyEmissionGuard(){return false;}
    default boolean ic$enemyCasingGuard(){return false;}
    default boolean ic$enemyRateGuard(){return false;}
    default boolean ic$enemyTickGuard(){return false;}
    default boolean ic$enemyBlockGuard(){return false;}
    default boolean ic$enemyEntityGuard(){return false;}
    default boolean ic$enemyImpactGuard(){return false;}
    default boolean ic$enemyProjectileGuards(){return ic$enemyTickGuard()&&ic$enemyBlockGuard()&&ic$enemyEntityGuard()&&ic$enemyImpactGuard();}
}
