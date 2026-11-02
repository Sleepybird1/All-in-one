package dev.godpc.industrialcolonies;

import java.nio.charset.StandardCharsets;
import java.util.*;

/** Private stdin/stdout transport; field values can contain tabs, newlines and Unicode. */
public final class KjsGenDesktopProtocol {
    public static String encode(String... fields) {
        return String.join("\t",Arrays.stream(fields).map(s->Base64.getEncoder().encodeToString(s.getBytes(StandardCharsets.UTF_8))).toList());
    }
    public static String[] decode(String line) {
        if(line.length()>4*1024*1024)throw new IllegalArgumentException("Message too large");
        return Arrays.stream(line.split("\t",-1)).map(s->new String(Base64.getDecoder().decode(s),StandardCharsets.UTF_8)).toArray(String[]::new);
    }
}
