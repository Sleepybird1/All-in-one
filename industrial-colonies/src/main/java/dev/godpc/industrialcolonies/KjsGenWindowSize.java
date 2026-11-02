package dev.godpc.industrialcolonies;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.neoforged.fml.loading.FMLPaths;
import java.nio.file.Files;
import java.nio.file.Path;
import java.io.IOException;

/** Editor window dimensions only; never changes Minecraft's GUI scale. */
public final class KjsGenWindowSize {
    private static double width = .9, height = .9;
    private static boolean loaded;
    private KjsGenWindowSize() {}
    public static double clamp(double value) {return Double.isFinite(value)?Math.max(.5,Math.min(1,value)):.9;}
    public static int dimension(int screen, int preferredMinimum, double fraction) {
        int available=Math.max(1,screen-16);
        return Math.max(Math.min(preferredMinimum,available),Math.min(available,(int)Math.round(available*clamp(fraction))));
    }
    private static Path file(){return FMLPaths.CONFIGDIR.get().resolve("industrial-colonies-kjsgen-window.json");}
    private static void load() {
        if(loaded)return;loaded=true;
        try {
            if(!Files.isRegularFile(file()))return;
            var json=JsonParser.parseString(Files.readString(file())).getAsJsonObject();
            width=clamp(json.get("width").getAsDouble());height=clamp(json.get("height").getAsDouble());
        }catch(Exception ignored){width=.9;height=.9;}
    }
    public static double width(){load();return width;}
    public static double height(){load();return height;}
    public static void save(double w,double h) throws IOException {
        var json=new JsonObject();json.addProperty("width",clamp(w));json.addProperty("height",clamp(h));
        Files.createDirectories(file().getParent());Files.writeString(file(),json.toString()+"\n");
        width=clamp(w);height=clamp(h);loaded=true;
    }
}
