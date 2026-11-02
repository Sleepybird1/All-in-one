package dev.godpc.industrialcolonies;

import net.minecraft.world.level.block.entity.BlockEntity;

import java.util.ArrayDeque;
import java.util.Deque;

/** Nested, exception-safe processing-machine context for Create recipe lookups. */
public final class CreateMachineContext {
    private static final ThreadLocal<Deque<BlockEntity>> CURRENT =
            ThreadLocal.withInitial(ArrayDeque::new);

    private CreateMachineContext() {
    }

    public static Scope enter(BlockEntity blockEntity) {
        CURRENT.get().push(blockEntity);
        return new Scope(blockEntity);
    }

    public static BlockEntity current() {
        return CURRENT.get().peek();
    }

    public static final class Scope implements AutoCloseable {
        private final BlockEntity blockEntity;
        private boolean closed;

        private Scope(BlockEntity blockEntity) {
            this.blockEntity = blockEntity;
        }

        @Override
        public void close() {
            if (closed) {
                return;
            }
            closed = true;

            Deque<BlockEntity> stack = CURRENT.get();
            BlockEntity current = stack.poll();
            if (current != blockEntity) {
                stack.clear();
                CURRENT.remove();
                throw new IllegalStateException("Create machine context closed out of order");
            }
            if (stack.isEmpty()) {
                CURRENT.remove();
            }
        }
    }
}
