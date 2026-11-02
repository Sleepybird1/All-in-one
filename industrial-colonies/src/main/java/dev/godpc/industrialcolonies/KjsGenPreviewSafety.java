package dev.godpc.industrialcolonies;

import java.util.function.Supplier;

/** Keeps expected draft-input failures inside the editor's non-executable preview. */
public final class KjsGenPreviewSafety {
    private KjsGenPreviewSafety() {}

    public record Result(String script, String diagnostic) {
        public boolean failed() {
            return diagnostic != null;
        }
    }

    public static Result preview(Supplier<String> generator) {
        try {
            return new Result(generator.get(), null);
        } catch (IllegalArgumentException invalid) {
            String detail = invalid.getMessage();
            if (detail == null || detail.isBlank()) {
                detail = "Incomplete or invalid recipe input";
            }
            // A diagnostic can contain line breaks. Never let it become executable JS.
            String comments = detail.replace("\r\n", "\n").replace('\r', '\n')
                    .replace('\u2028', '\n').replace('\u2029', '\n')
                    .replace("\n", "\n// ");
            return new Result("// Recipe preview unavailable: " + comments
                    + "\n// Correct this draft to regenerate the preview. Your edits are preserved.", detail);
        }
    }
}
