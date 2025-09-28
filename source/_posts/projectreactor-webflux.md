---
title: projectreactor & webflux
date: 2025-09-28 21:52:25
category:
tags:
---
# reactor
| Aspect             | `generate` (sync)                           | `push` (async, single thread)            | `create` (async, multi-thread)           |
| ------------------ | ------------------------------------------- | ---------------------------------------- | ---------------------------------------- |
| **Emission style** | **Pull** (one item per request)             | **Push** (producer pushes items)         | **Push** (producer pushes items)         |
| **Concurrency**    | Always single-threaded, synchronous         | Single-thread only                       | Multi-thread allowed                     |
| **Backpressure**   | Native: generator runs only on demand       | Needs overflow strategy if fast producer | Needs overflow strategy if fast producer |
| **Use case**       | Generate values step by step, state machine | Event listener, single-thread producer   | Multi-threaded sources, complex bridging |

```java

Flux<Integer> flux = Flux.generate(
    () -> 0,  // initial state
    (state, sink) -> {
        sink.next(state);
        if (state == 5) sink.complete();
        return state + 1; // next state
    }
);


Flux<String> flux = Flux.push(sink -> {
    someListener.onMessage(msg -> sink.next(msg));
});


Flux<String> flux = Flux.create(sink -> {
    new Thread(() -> {
        sink.next("A");
        sink.next("B");
        sink.complete();
    }).start();
}, FluxSink.OverflowStrategy.BUFFER);

```

> **Rule of Thumb**
> Use Flux.generate when you want a pull-based, synchronous generator (like a lazy sequence, state machine, or random number generator).
> Use Flux.push/create when you want to adapt to an external asynchronous source (like callbacks, listeners, or multiple threads producing data).



# webflux

🟢 Cold, synchronous sources (run on caller thread, usually the subscriber’s thread)

These methods execute inline on the same thread that subscribes, unless moved:

Mono.just(...), Flux.just(...)

Mono.empty(), Flux.empty()

Mono.error(...), Flux.error(...)

Flux.range(...), Flux.fromIterable(...), Flux.fromArray(...)

Mono.fromSupplier(...) (evaluates lazily but still on caller thread)

Mono.fromCallable(...)

Flux.defer(...), Mono.defer(...)

👉 By default: No background thread, execution happens immediately when subscribed.

## thread model
default WebFlux app on Netty:
- Boss threads: 1
- Worker (event loop) threads: 2 * cpu
- Reactor Scheduler available:
    - paraller: cpu
    - boundedElastic: 10 * cpu -> 1000+
    - timer: cpu (independent scheduler, never run user code directly, wraped a ScheduledExecutorService)
    - single: 1
    - immediate: 0 (just current thread)

**Best Practices**

- **Pure reactive stack (WebClient, R2DBC, reactive Mongo, etc.):**
    → stay on Netty event loop, no scheduler needed.

- **Blocking APIs (JDBC, legacy SDKs, file IO):**
    → wrap with Mono.fromCallable(...).subscribeOn(Schedulers.boundedElastic()).

- **Heavy CPU tasks (compression, JSON parsing, crypto):**
    → offload with publishOn(Schedulers.parallel()).

- **Global customization** (rarely needed): adjust Netty loop threads for connection-heavy apps, or override boundedElastic size for blocking-heavy apps.

why heavy cpu tasks, not io tasks, cauz netty born for heavy sockets tasks, it's non-block at all.

io tasks not to be block tasks for netty, don't equal to them. even if there's no io, it still could be a block task, e.g. `Thread.sleep(5000)` is a block task, forbidden running on event loop.

---

🟡 Asynchronous sources (use a Reactor scheduler by default)

These spawn work on an internal boundedElastic or parallel thread pool:

Mono.delay(Duration) → Schedulers.parallel()

Flux.interval(Duration) → Schedulers.parallel()

Mono.fromRunnable(...), Mono.fromFuture(...), Mono.fromCompletionStage(...)

If future already completed → current thread

If not → completion thread (depends on upstream executor/future, not Reactor itself)

👉 By default: don’t run on subscriber thread, Reactor chooses.

---

🔵 Blocking bridge operators (force boundedElastic by default)

Reactor assumes blocking I/O → runs on Schedulers.boundedElastic() unless you change:

Mono.fromCallable(blockingFn).subscribeOn(Schedulers.boundedElastic()) (best practice)

Mono.block() / Flux.blockFirst() / Flux.blockLast() (blocking the caller thread)

Operators like flatMap with blocking calls must be explicitly shifted to boundedElastic.

---

🔴 Thread-affecting operators (don’t run anything themselves but change execution)

publishOn(Scheduler) → switches downstream execution thread

subscribeOn(Scheduler) → changes the context where subscription and upstream happen

---

⚪ Context-dependent sources

Some methods inherit threads from external APIs:

Flux.create(...) or Mono.create(...) → depends on how you emit (`caller thread` or async callback thread)

Flux.push(...) → same, depends on emitter thread

Flux.generate(...) → runs on `subscriber thread` unless you schedule

> ✅ Quick rule of thumb
> "Pure data" operators (just, range, fromIterable) → run on subscriber thread.
> "Timed" operators (delay, interval) → run on Reactor’s parallel scheduler.
> "Bridges to blocking/async world" (fromCallable, fromFuture) → run on caller’s thread or boundedElastic/foreign executor, unless you move them.
> Schedulers (publishOn, subscribeOn) are the only way to force thread switch.

***caller thread = initiator of subscription, subscriber thread = executor of signals.***

```java
flux.publishOn(Schedulers.parallel())
    .subscribe(i -> System.out.println("sub: " + i + " on " + Thread.currentThread().getName()));
```

- caller thread = main
- subscriber thread = parallel-1
- Mapping still happens on 'parallel-1' because of `publishOn`

### think about
🔹 Two philosophies

1. Operators/methods decide their scheduler (local responsibility)

You sprinkle .subscribeOn(...) or .publishOn(...) inside every method that returns a Mono/Flux.

Pros:
The method guarantees safe execution (e.g., offloading a blocking call to boundedElastic).
Callers don’t need to know the implementation details (e.g., that it does blocking JDBC work).
Cons:
You lose flexibility: the caller cannot override your scheduler easily.
If multiple methods apply .subscribeOn(...), only the first one in the chain wins (because subscribeOn only affects upstream).
Can lead to confusion if one method hides threading decisions.

2. Caller decides (central responsibility)

Your methods just describe the pipeline (Mono.just, map, flatMap, etc.) with no scheduler hints.
The caller (e.g., controller or service entry point) applies subscribeOn / publishOn.

Pros:
Clean separation of concerns: methods remain pure, deterministic pipelines.
Caller has full control of threading policy.
Easy to test synchronously (no schedulers in unit tests unless you want them).
Cons:
Risk: if a method does blocking work (e.g., JDBC, file IO, legacy API), caller must remember to schedule it properly, or it will block Netty/event loop.

🔹 Rule of Thumb

👉 Don’t sprinkle subscribeOn everywhere.

If your method is purely non-blocking/reactive (using Reactor operators, R2DBC, WebClient, etc.):
❌ Do not configure a scheduler. Let the caller decide.

If your method wraps blocking code (JDBC, file IO, legacy API, etc.):
✅ Apply subscribeOn(Schedulers.boundedElastic()) inside the method — because you must protect the Netty event loop.

This way:

Non-blocking pipelines remain transparent and flexible.
Blocking bridges are safe by default, without relying on the caller’s discipline.

```java
// ✅ Non-blocking service, no scheduler
Mono<User> getUserReactive(String id) {
    return webClient.get()
        .uri("/users/{id}", id)
        .retrieve()
        .bodyToMono(User.class);
}

// ✅ Blocking service, safe by default
Mono<User> getUserBlocking(String id) {
    return Mono.fromCallable(() -> jdbcTemplate.queryForObject("...", User.class, id))
               .subscribeOn(Schedulers.boundedElastic());
}
```

Caller:
```java
// Controller - doesn't care about threading for reactive code
getUserReactive("123")
    .map(this::transform)
    .subscribe();

// Blocking call is already protected by boundedElastic internally
getUserBlocking("123")
    .map(this::transform)
    .subscribe();
```

✅ Best practice summary

Non-blocking methods: don’t set subscribeOn.
Blocking methods: always set subscribeOn(Schedulers.boundedElastic()) inside the method.
At the top level (controllers, pipelines): only add publishOn/subscribeOn when you need explicit control over where downstream operators run.

define custom schedulers
```java
import reactor.core.scheduler.Scheduler;
import reactor.core.scheduler.Schedulers;

import java.util.concurrent.Executors;
import java.util.concurrent.ThreadFactory;
import java.util.concurrent.ExecutorService;

public class CustomSchedulers {

    // CPU-heavy tasks: non-blocking, parallel computation
    public static final Scheduler CPU_SCHEDULER = Schedulers.newParallel(
            "cpu-pool",  // thread name prefix
            Runtime.getRuntime().availableProcessors()
    );

    // Blocking / IO-heavy tasks: e.g., DB, file I/O, network calls
    private static final int IO_POOL_SIZE = 50;  // adjust based on load
    private static final ExecutorService ioExecutor = Executors.newFixedThreadPool(
            IO_POOL_SIZE,
            new ThreadFactory() {
                private int count = 0;
                @Override
                public Thread newThread(Runnable r) {
                    return new Thread(r, "io-pool-" + count++);
                }
            }
    );
    public static final Scheduler IO_SCHEDULER = Schedulers.fromExecutorService(ioExecutor);

    // Cleanup on shutdown
    public static void shutdown() {
        CPU_SCHEDULER.dispose();
        IO_SCHEDULER.dispose();
        ioExecutor.shutdown();
    }
}
```

# methods usage
## defer & interval
`defer` is like a provider in spring, when inject a provider: () -> new Instance() instead a : new Instance() itself.
it **create a new Mono for every subscription** by invoking the supplier lazily.

say we need a loop call, 
```java
public Mono<String> pollUntilJson(String path) {
        return Mono.defer(() ->
                webClient.get()
                         .uri(path)
                         .retrieve()
                         .bodyToMono(String.class)
        ).flatMap(body -> {
            if (!body.isEmpty() && body.trim().startsWith("{")) {
                return Mono.just(body); // ✅ Got JSON, finish
            } else {
                return Mono.delay(Duration.ofSeconds(1)) // delay create a non-blocking timer, so reactor will schedules it on a reactor timer, not a thread sleep.
                           .then(pollUntilJson(path)); // each time, we make a fresh call, not reuse the first mono which we don't want to.
            }
        });
    } // since webclient is non-blocking, we don't need a subscribeOn(boundedElastic()).
```

alternatives to delay
```java
Flux.interval(Duration.ofSeconds(1))
    .flatMap(tick ->
        webClient.get().uri(path).retrieve().bodyToMono(String.class)
    )
    .filter(body -> isJson(body)) // 
    .next(); // take the first JSON result
```

or exponential backoff way
```java
Mono.defer(() -> webClient.get().uri(path).retrieve().bodyToMono(String.class))
    .filter(this::isJson)
    .retryWhen(Retry.backoff(10, Duration.ofSeconds(1)));
```




