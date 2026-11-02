package net.neoforged.fml.loading;

import java.nio.file.Path;

/** Compile-only standalone planner-test shim; never included in the mod source set or JAR. */
public enum FMLPaths {
    CONFIGDIR;
    public Path get() { return Path.of(System.getProperty("geology.test.config", "build/geology-planner-test/config")); }
}
