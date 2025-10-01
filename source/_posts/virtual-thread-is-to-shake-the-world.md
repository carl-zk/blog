---
title: virtual thread is to shake the world
date: 2025-09-30 18:08:17
category:
tags:
---
# virtual thread
## when sould you use virtual threads

Virtual threads (introduced in **Project Loom**, JDK 21 GA) are lightweight threads managed by the JVM rather than the OS. They shine in scenarios where you need to handle **lots of concurrent tasks that spend most of their time waiting (IO-bound workloads).**

Good use cases:

- Servers handling many concurrent connections
    e.g., HTTP servers, gRPC servers, WebSocket servers.

- High-concurrency clients
    e.g., calling many downstream services (DB, REST APIs, message queues).

- Asynchronous pipelines
    where tasks wait on external systems but you want code to look synchronous.

- Replacement for callback-heavy async code
    You can write blocking-style code, but still scale like async/reactive.

Not ideal:

- CPU-bound parallel computations
    Use platform threads (classic ForkJoinPool, parallel streams, or structured concurrency with platform threads). Virtual threads don’t give extra CPU, they just multiplex blocking tasks.

- Very short-lived tasks in huge numbers
    If the task just increments a counter, spawning millions of VTs gives no benefit and can be slower than batching work on a platform thread pool.

## does a "virtual thread pool" exist?
Strictly speaking: **NO, virtual threads don't use a traditional pool** like `Executors.newFixedThreadPool`.

Instead, each virtual threads is cheap to create (thousands to millions possible). The JVM schedules them onto a small pool of **carrier threads** (platform threads) behind the scenes.

That means:

- You can just create anew virtual thread per task (`Thread.ofVirtual().start(...)` or `Executors.newVirtualThreadPerTaskExecutor()`).
- No need to reuse them ------ they are disposable, unlike platform threads.
- The JVM maintains an internal scheduler that runs VTs on carrier threads.

So the pattern is:

```java
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 1_000_000).forEach(i ->
        executor.submit(() -> {
            // IO-bound task
            fetchFromDb(i);
        })
    );
}
```

Here, each task gets its own virtual thread. The JVM multiplexes them efficiently over a small number of OS threads.

## How to choose between pool of platform threads vs per-task virtual threads

- User **platform thread pools** when:
    - You want to bound concurrency for CPU-bound tasks (e.g., 8 threads for 8 CPU cores).
- User virtual threads when:
    - You want to scale IO-bound concurrency (e.g., 50k socket connections).
    - Thread creation overhead is a bottleneck.

# VTs or Reactor
## Reactor vs Virtual threads: different approaches
### Reactor
- Based on the **reactive streams model** (non-blocking, event-loop style).
- Forces you to compose async flows (Mono, Flux) to avoid blocking threads.
- Good for massive concurrency and **backpressure control**, but requires a different programming model.
### Virtual threads
- Keep the **blocking code style** (imperative, linear).
- You can just call `db.query()` or `httpClient.send()` inside a virtual thread without worring about blocking the OS thread.
- The scheduler multiplexes thousands of VTs on a few carriers.

In case you have some ideas like 
```java
Mono.fromCallable(() -> {
    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
        return executor.submit(() -> blockingDbQuery()).get();
    }
});
```
, you could question: ***why Reactor at all for IO-heavy workloads?***  
With VTs, you don't need reactive chains to achieve scalability ——— **a simple synchronous style in a VT can scale to tens of thousands of connections.**

---  

Reactor is still useful if:
- You need backpressure.
- You already have a large reactive codebase.
- You want integration with libraries that are natively reactive (R2DBC, reactive Kafka, etc.).

Hybrid using is fine, you can still integrates with existing Reactor ecosystem.
```java
Scheduler vtScheduler = Scheduler.fromExecutor(Executors.newVirtualThreadPerTaskExecutor());

Mono.fromCallable(() -> blockingApiCall())
    .subscribeOn(vtScheduler)
    .flatMap(result -> Mono.just(transform(result)));
```

---  

it's a Reactor way you handle IO-heavy request,

```java
Scheduler vtScheduler = Scheduler.fromExecutor(
    Executors.newVirtualThreadPerTaskExecutor()
);

Mono<String> service(String id) {
    return Mono.fromCallable(() -> blockingDbQuery(id))
               .subscribeOn(vtScheduler)
               .zipWith(
                   Mono.fromCallable(() -> blockingHttpCall(id))
                       .subscribeOn(vtScheduler)
               )
               .map(tuple -> "DB: " + tuple.getT1() + ", HTTP: " + tuple.getT2());
}
```

what does pure virtual threads looks like in IO-heavy tasks?

```java
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();

String service(String id) throws Exception {
    Future<String> future = executor.submit(() -> {
        var dbResult = blockingDbQuery(id);
        var httpResult = blockingHttpCall(id);
        return "DB: " + dbResult + ", HTTP: " + httpResult;
    });
    return future.get();
}
```

or with structured concurrency:

```java
String service(String id) throws Exception {
    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
        var dbFuture = scope.fork(() -> blockingDbQuery(id));
        var httpFuture = scope.fork(() -> blockingHttpCall(id));

        scope.join();           // wait for both
        scope.throwIfFailed();  // propagate exception

        return "DB: " + dbFuture.resultNow() + ", HTTP: " + httpFuture.resultNow();
    }
}
```

that's it, the blocking style comes back without loose high throughput.

If you're on Spring 6 / Spring boot 3 with Loom (JDK 21), you can drop WebFlux and use Spring MVC with virtual threads instead.
Each request gets its own VT, so blocking is cheap:

```java
@Configuration
class VirtualThreadConfig {

    @Bean
    ExecutorService applicationExecutor() {
        return Executors.newVirtualThreadPerTaskExecutor();
    }
}

@RestController
class MyController {

    @GetMapping("/service/{id}")
    public String service(@PathVariable String id) {
        // This method is blocking, but it’s OK — it runs on a virtual thread
        var dbResult = blockingDbQuery(id);
        var httpResult = blockingHttpCall(id);
        return "DB: " + dbResult + ", HTTP: " + httpResult;
    }

    private String blockingDbQuery(String id) {
        return "db-" + id;
    }

    private String blockingHttpCall(String id) {
        return "http-" + id;
    }
}
```

this is the "Loom Future": MVC simplicity + WebFlux scalability.

# VTs or Netty

**Virtual threads can replace the reason Netty exists**
Netty was designed because the **thread-per-connection model didn't scale** (too many OS threads).
With VTs, you can go back to simple thread-per-connection model:

```java
try (var listener = AsynchronousServerSocketChannel.open()) {
    listener.bind(new InetSocketAddress(8080));
    while (true) {
        var client = listener.accept().get(); // blocks
        Thread.ofVirtual().start(() -> handle(client));
    }
}
```

Each connection just runs on its own virtual thread ——— no event loop gymnastics.
> this eliminates the core scalability problem Netty solved in 2004.

Can VTs replace Netty?

Not now, Nety is not "just" about scaling connections. It also provides:
- Protocol implementations (HTTP, HTTP/2, HTTP/3, WebSockets, gRPC transport).
- Pipelines (handlers, encoders/decoders, SSL/TLS, compression).
- Zero-copy, pooled byte buffers for performance.
- Backpressure and flow control.

Virtual threads don't give you any of that ——— they just let you block without guilt.

What's a minimal blocking HTTP server with VTs looks like?

```java
import java.io.*;
import java.net.*;

public class SimpleHttpServer {

    public static void main(String[] args) throws IOException {
        try (var serverSocket = new ServerSocket(8080)) {
            System.out.println("Server listening on port 8080...");

            while (true) {
                Socket client = serverSocket.accept(); // blocks
                Thread.ofVirtual().start(() -> handleClient(client));
            }
        }
    }

    private static void handleClient(Socket client) {
        try (client;
             var reader = new BufferedReader(new InputStreamReader(client.getInputStream()));
             var writer = new BufferedWriter(new OutputStreamWriter(client.getOutputStream()))) {

            // Read the first request line (ignore headers for simplicity)
            String line = reader.readLine();
            System.out.println("Received: " + line);

            // Simple HTTP response
            writer.write("HTTP/1.1 200 OK\r\n");
            writer.write("Content-Type: text/plain\r\n");
            writer.write("Connection: close\r\n");
            writer.write("\r\n");
            writer.write("Hello from Virtual Threads!\n");
            writer.flush();

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

If you want non-blocking channels but still keep the simple style:

```java
import java.net.*;
import java.nio.*;
import java.nio.channels.*;

public class NioHttpServer {

    public static void main(String[] args) throws Exception {
        try (var server = ServerSocketChannel.open()) {
            server.bind(new InetSocketAddress(8080));

            System.out.println("NIO server listening on port 8080...");

            while (true) {
                SocketChannel client = server.accept(); // blocks
                Thread.ofVirtual().start(() -> handle(client));
            }
        }
    }

    private static void handle(SocketChannel client) {
        try (client) {
            ByteBuffer buffer = ByteBuffer.allocate(1024);
            client.read(buffer); // blocks
            buffer.flip();

            String response = """
                HTTP/1.1 200 OK\r
                Content-Type: text/plain\r
                Connection: close\r
                \r
                Hello from Virtual Threads with NIO!
                """;

            client.write(ByteBuffer.wrap(response.getBytes()));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

# VTs frameworks

Helidon Níma (Helidon 4)

Reactor Core (Spring Reactor / WebFlux)

Spring Boot 3.2

# Caveats, Limitations & Things to Watch

- **Blocking calls in third-party libraries**: If a library internally blocks in a way the JVM can’t detect (e.g. native sleep, synchronized locks), the benefit is diminished.
- **ThreadLocal usage**: Because you may have many virtual threads, ThreadLocal data may become an issue (memory, leakage). Scoped values or other strategies are recommended. 
- **Resource limits beyond threads**: Database connections, file descriptors, sockets, memory — you still need to manage these.
- **Performance & tuning**: The new runtime behaviors may reveal new performance bottlenecks, GC overheads, scheduling latency, etc.
- **Maturity & ecosystem**: Many frameworks, tools, APM agents, debuggers, etc., will need adaptation to fully embrace Loom.

ThreadLocals can blow up memory usage with millions of virtual threads.
Prefer Scoped Values (available in preview) or explicit context passing.

```java
ScopedValue<String> USER = ScopedValue.newInstance();

ScopedValue.where(USER, "carl")
           .run(() -> doWork(USER.get()));
```

Structured Concurrency (for Task Groups), Instead of manual `CompletableFuture` composition, use Loom’s structured concurrency API:

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var task1 = scope.fork(() -> fetchUser());
    var task2 = scope.fork(() -> fetchOrders());
    scope.join();
    scope.throwIfFailed();
    return combine(task1.resultNow(), task2.resultNow());
}
```

---

🗓 Project Loom Timeline / Roadmap
🔹 Early Days

2017: Project Loom was announced at OpenJDK (Brian Goetz & Ron Pressler leading).

2018–2020: Early prototypes with fibers and continuations. APIs unstable.

JDK 13–16: Some incubator APIs for continuations and structured concurrency experiments.

🔹 Key Milestones

JDK 19 (Sept 2022)

Virtual Threads introduced as a preview feature.

Structured Concurrency incubated.

JDK 20 (Mar 2023)

Virtual Threads previewed again with refinements.

Structured Concurrency incubator updated.

JDK 21 (Sept 2023, LTS release)

Virtual Threads finalized (no longer preview).

Structured Concurrency still incubating.

Scoped Values introduced in preview.

JDK 22 (Mar 2024)

Structured Concurrency (2nd incubator round).

Scoped Values (2nd preview).

JDK 23 (Sept 2024, not LTS)

Ongoing improvements in Structured Concurrency & Scoped Values.

Tooling support (debuggers, profilers) improving for virtual threads.

🔮 Near Future

JDK 25 (likely next LTS in 2026)

Expect Structured Concurrency and Scoped Values to become stable.

Virtual thread ecosystem maturity (Spring, Hibernate, Netty alternatives adapting).

JVM / JIT / GC optimizations specific to Loom workloads.