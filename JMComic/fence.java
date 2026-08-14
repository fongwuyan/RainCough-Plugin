import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
public class FenceTask {
    public final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final List futureList = new ArrayList();
    public void submit(Runnable runnable){
        Future future = executor.submit(runnable);
        futureList.add(future);
    }
    public void block(Runnable runnable){
        synchronized (futureList) {
            for (Object o : futureList) {
                Future future = (Future) o;
                try {
                    future.get();
                } catch (Exception e) {
                log(e.getMessage());
                }
            }
            runnable.run();
        }
    }
}
