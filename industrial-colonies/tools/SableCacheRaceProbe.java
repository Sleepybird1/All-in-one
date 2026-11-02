import it.unimi.dsi.fastutil.ints.Int2BooleanOpenHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicReference;

// Isolated diagnostic: same map and operation as installed Sable 2.0.3.
// Does not read or change Minecraft data.
public class SableCacheRaceProbe {
    public static void main(String[] args) throws Exception {
        boolean locked = args.length > 0 && args[0].equals("locked");
        for (int round = 0; round < 20; round++) {
            var map = new Int2BooleanOpenHashMap();
            var start = new CountDownLatch(1);
            var done = new CountDownLatch(8);
            var failure = new AtomicReference<Throwable>();
            for (int worker = 0; worker < 8; worker++) {
                final int offset = worker * 10000;
                Thread thread = new Thread(() -> {
                    try {
                        start.await();
                        for (int j = 1; j <= 10000; j++) {
                            int key = offset + j;
                            if (locked) {
                                synchronized (map) { map.computeIfAbsent(key, (int k) -> (k & 1) == 0); }
                            } else { map.computeIfAbsent(key, (int k) -> (k & 1) == 0); }
                        }
                    } catch (Throwable ex) { failure.compareAndSet(null, ex); }
                    finally { done.countDown(); }
                });
                thread.setDaemon(true);
                thread.start();
            }
            start.countDown();
            if (!done.await(3, java.util.concurrent.TimeUnit.SECONDS)) {
                System.out.println("HANG: round " + round + ", locked=" + locked);
                if (failure.get() != null) failure.get().printStackTrace(System.out);
                System.exit(2);
            }
            if (failure.get() != null) {
                failure.get().printStackTrace(System.out);
                System.exit(3);
            }
            if (map.size() != 80000) {
                System.out.println("CORRUPTION: size=" + map.size() + ", expected=80000");
                System.exit(4);
            }
        }
        System.out.println("PASS: 20 rounds, 1,600,000 insertions; locked=" + locked);
    }
}
