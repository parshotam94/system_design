import json
from pathlib import Path

content_dir = Path("content")
content_dir.mkdir(exist_ok=True)

def write_module(mod_data):
    mod_id = mod_data["module_id"]
    path = content_dir / f"module_{mod_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mod_data, f, indent=2)
    print(f"Generated module_{mod_id}.json with {len(mod_data['topics'])} topics")

def make_18_step_topic(topic_id, title, desc, what_is, why_need, core_idea, how_works, visual_dict, code_filename, code_content, walkthrough, real_world, when_use, when_not_use, advantages, disadvantages, variations, mistakes, q_text, a_text, practice_title, practice_stmt, practice_code):
    sections = [
        {"step_number": 1, "title": "1. What is it?", "content": f"<p>{what_is}</p>"},
        {"step_number": 2, "title": "2. Why do we need it?", "content": f"<p>{why_need}</p>"},
        {"step_number": 3, "title": "3. Core idea", "content": f"<p>{core_idea}</p>"},
        {"step_number": 4, "title": "4. How it works", "content": f"<p>{how_works}</p>"}
    ]
    sec_5 = {"step_number": 5, "title": "5. Visual explanation", "content": "<p>Visual Architecture & Mechanics:</p>"}
    if "diagram" in visual_dict: sec_5["diagram"] = visual_dict["diagram"]
    elif "comparison" in visual_dict: sec_5["comparison"] = visual_dict["comparison"]
    elif "callout" in visual_dict: sec_5["callout"] = visual_dict["callout"]
    elif "animation" in visual_dict: sec_5["animation"] = visual_dict["animation"]
    sections.append(sec_5)
    sections.append({"step_number": 6, "title": "6. C++ implementation", "content": "<p>Complete Production C++20 Implementation:</p>", "code_example": {"filename": code_filename, "code": code_content}})
    sections.append({"step_number": 7, "title": "7. Code walkthrough", "content": f"<p>{walkthrough}</p>"})
    sections.append({"step_number": 8, "title": "8. Real-world example", "content": f"<p>{real_world}</p>"})
    sections.append({"step_number": 9, "title": "9. When to use", "content": f"<p>{when_use}</p>"})
    sections.append({"step_number": 10, "title": "10. When NOT to use", "content": f"<p>{when_not_use}</p>"})
    sections.append({"step_number": 11, "title": "11. Advantages", "content": f"<p>{advantages}</p>"})
    sections.append({"step_number": 12, "title": "12. Disadvantages", "content": f"<p>{disadvantages}</p>"})
    sections.append({"step_number": 13, "title": "13. Variations / Types", "content": f"<p>{variations}</p>"})
    sections.append({"step_number": 14, "title": "14. Common mistakes", "content": f"<p>{mistakes}</p>"})
    sections.append({"step_number": 15, "title": "15. Interview questions", "content": f"<p><strong>Q:</strong> {q_text}</p>"})
    sections.append({"step_number": 16, "title": "16. Interview answer", "content": f"<p><strong>Answer:</strong> {a_text}</p>"})
    sections.append({
        "step_number": 17, "title": "17. Practice problem", "content": f"<p>{practice_stmt}</p>",
        "practice": {
            "title": practice_title, "problemStatement": practice_stmt,
            "requirements": ["Production C++20 code", "Proper resource management"],
            "constraints": ["Zero memory leaks"], "hint": "Follow standard C++ idioms.",
            "expectedEntities": [{"name": practice_title, "responsibility": "Idiom implementation."}],
            "referenceCode": {"filename": "practice_sol.cpp", "code": practice_code}
        }
    })
    sections.append({"step_number": 18, "title": "18. Summary", "content": f"<p>Mastering {title} is essential for advanced C++ systems design.</p>"})
    return {"id": topic_id, "title": title, "description": desc, "sections": sections}

# ==============================================================================
# MODULE 12: C++ Design Techniques
# ==============================================================================
mod_12 = {
    "module_id": "12",
    "title": "C++ Idioms & Advanced Design Techniques",
    "level": "Advanced",
    "category": "C++ Idioms",
    "description": "PImpl Idiom (Compilation Firewalls), CRTP (Static Polymorphism), Type Erasure (std::function), and Callback Architectures.",
    "topics": [
        make_18_step_topic(
            "pimpl-idiom", "PImpl Idiom (Pointer to Implementation)",
            "Hiding private implementation details and third-party headers behind an opaque pointer to speed up compilation.",
            "The <strong>PImpl Idiom</strong> (Pointer to Implementation / Compilation Firewall) moves private data and methods into an internal struct defined only in the <code>.cpp</code> file.",
            "Changing a private member in a header file forces every file that includes that header to recompile. PImpl eliminates compilation cascades and provides ABI stability.",
            "Header declares <code>struct Impl; std::unique_ptr&lt;Impl&gt; pImpl;</code>. Definition lives in <code>.cpp</code>.",
            "Client only includes the lightweight header; the heavy implementation and dependencies are isolated in the <code>.cpp</code> translation unit.",
            {"callout": {"type": "tip", "title": "Compilation Firewall", "text": "Header.hpp: struct Impl; unique_ptr<Impl> pImpl; (Zero 3rd-party includes!)\\nHeader.cpp: struct Impl { HeavyWindowsSdk sdk; }; (Only this .cpp recompiles!)"}},
            "pimpl_demo.cpp",
            """#include <iostream>
#include <memory>
#include <string>

// --- Public Header File (widget.hpp) ---
class Widget {
public:
    Widget();
    ~Widget(); // MUST be declared in header and defined in .cpp for unique_ptr<Impl>!
    Widget(Widget&&) noexcept;
    Widget& operator=(Widget&&) noexcept;

    void doHeavyOperation();

private:
    struct Impl; // Forward declared opaque struct
    std::unique_ptr<Impl> pImpl;
};

// --- Private Source File (widget.cpp) ---
struct Widget::Impl {
    std::string internalBuffer;
    void performInternalTask() {
        std::cout << "[PImpl] Executed heavy internal task with buffer: " << internalBuffer << "\\n";
    }
};

Widget::Widget() : pImpl(std::make_unique<Impl>()) {
    pImpl->internalBuffer = "Allocated 64MB buffer";
}

Widget::~Widget() = default; // Defined where Impl is complete!
Widget::Widget(Widget&&) noexcept = default;
Widget& Widget::operator=(Widget&&) noexcept = default;

void Widget::doHeavyOperation() {
    pImpl->performInternalTask();
}

int main() {
    Widget w;
    w.doHeavyOperation();
    return 0;
}""",
            "Widget delegates private operations to opaque struct Impl via std::unique_ptr.",
            "Qt Framework (Q_D pointer), Windows API SDKs, Proprietary Closed-Source C++ SDK distributions.",
            "Use in public library headers to preserve ABI compatibility and minimize client compilation times.",
            "Do not use for small, performance-critical math structs where heap allocation overhead is unacceptable.",
            "Fast build times; true encapsulation of private dependencies; stable binary ABI.",
            "Extra heap allocation for Impl and pointer indirection overhead per call.",
            "PImpl with std::unique_ptr, Fast PImpl (placement new in fixed stack buffer).",
            "Defining ~Widget() in the header file (causes compile error: cannot delete incomplete type Impl).",
            "Why must the destructor of a PImpl class be defined in the .cpp file?",
            "Because <code>std::unique_ptr&lt;Impl&gt;</code> requires <code>sizeof(Impl)</code> to generate its default deleter. In the header, <code>Impl</code> is an incomplete type; defining the destructor in the <code>.cpp</code> file ensures <code>Impl</code> is fully defined.",
            "DatabaseClient PImpl",
            "Wrap a heavy DatabaseClient using the PImpl idiom.",
            "class DbClient { struct Impl; std::unique_ptr<Impl> pImpl; public: DbClient(); ~DbClient(); };"
        ),
        make_18_step_topic(
            "crtp-static-polymorphism", "CRTP (Curiously Recurring Template Pattern)",
            "Achieving compile-time static polymorphism without VTable and VPTR runtime overhead.",
            "<strong>CRTP</strong> is a C++ idiom where a class derives from a template base class instantiated with the derived class itself (<code>class Derived : public Base&lt;Derived&gt;</code>).",
            "Allows static polymorphism with method overriding that is 100% inlined at compile time with zero VTable overhead.",
            "Base class casts <code>this</code> to <code>Derived*</code> (<code>static_cast&lt;Derived*&gt;(this)</code>) and calls derived methods statically.",
            "Zero indirect function pointer lookups; maximum performance in tight loops.",
            {"callout": {"type": "tip", "title": "CRTP Static Dispatch", "text": "template <typename Derived> class Base { public: void speak() { static_cast<Derived*>(this)->speakImpl(); } };"}},
            "crtp_static_poly.cpp",
            """#include <iostream>

// CRTP Base Class (Static Polymorphism)
template <typename Derived>
class BaseProcessor {
public:
    void process() {
        // Static dispatch resolved at compile time with zero VTable lookup!
        static_cast<Derived*>(this)->executeStep();
    }
};

class FastAudioProcessor : public BaseProcessor<FastAudioProcessor> {
public:
    void executeStep() {
        std::cout << "[CRTP] FastAudioProcessor: Executing inlined DSP cycle.\\n";
    }
};

template <typename T>
void runProcessingLoop(BaseProcessor<T>& proc) {
    proc.process(); // Fully inlinable!
}

int main() {
    FastAudioProcessor audio;
    runProcessingLoop(audio);
    return 0;
}""",
            "BaseProcessor dispatches statically to FastAudioProcessor without virtual functions.",
            "High-Frequency Trading (HFT) matching engines, Eigen matrix math library, PyBind11 bindings.",
            "Use in performance-critical code where virtual dispatch overhead or cache misses are bottlenecks.",
            "Do not use if you need runtime heterogeneous collections (e.g. vector of mixed objects).",
            "Zero runtime overhead; allows complete compiler inlining.",
            "Complex template compiler error messages.",
            "CRTP Mixins, CRTP Static Interfaces, CRTP Object Counters.",
            "Forgetting to mark derived methods public or friend with the base class.",
            "How does CRTP differ from standard runtime polymorphism?",
            "CRTP resolves method binding at <strong>compile time</strong> via template instantiation (zero runtime cost, inlinable), whereas runtime polymorphism resolves methods at <strong>runtime</strong> via a VTable lookup (indirect branch).",
            "CRTP Cloneable Mixin",
            "Implement a generic CRTP Cloneable mixin that automatically provides clone().",
            "template<class D> struct Cloneable { std::unique_ptr<D> clone() const { return std::make_unique<D>(*static_cast<const D*>(this)); } };"
        ),
        make_18_step_topic(
            "type-erasure", "Type Erasure (std::function & Custom Erasures)",
            "Encapsulating objects of any type that support a given interface without requiring a common inheritance hierarchy.",
            "<strong>Type Erasure</strong> is a technique that provides a unified, polymorphic interface to unrelated concrete types without forcing them to inherit from a common base class.",
            "Allows storing function pointers, lambdas with captures, and custom function objects uniformly in <code>std::function</code>.",
            "Combines templates (compile time) with inheritance and virtual functions (runtime) hidden inside an internal bridge wrapper.",
            "<code>std::function&lt;void()&gt;</code> can hold any callable: free function, lambda, or member function bind.",
            {"callout": {"type": "tip", "title": "Type Erasure Anatomy", "text": "std::function / std::any / custom erasures store a template Concept<T> inside an opaque non-template interface!"}},
            "type_erasure_demo.cpp",
            """#include <iostream>
#include <functional>
#include <vector>

// Type-Erased Event Dispatcher using std::function
class EventDispatcher {
private:
    std::vector<std::function<void(int)>> listeners;
public:
    void subscribe(std::function<void(int)> listener) {
        listeners.push_back(std::move(listener));
    }

    void emit(int eventData) {
        for (const auto& fn : listeners) fn(eventData);
    }
};

void freeFunctionListener(int x) { std::cout << "Free function received: " << x << "\\n"; }

int main() {
    EventDispatcher dispatcher;

    // 1. Subscribe free function
    dispatcher.subscribe(freeFunctionListener);

    // 2. Subscribe lambda with state capture
    int multiplier = 10;
    dispatcher.subscribe([multiplier](int x) {
        std::cout << "Lambda received: " << x * multiplier << "\\n";
    });

    dispatcher.emit(42);
    return 0;
}""",
            "EventDispatcher stores free functions and stateful lambdas uniformly via type-erased std::function.",
            "<code>std::function</code>, <code>std::any</code>, <code>std::move_only_function</code> (C++23), Adobe Type Erasure library.",
            "Use when you want duck-typing flexibility in C++ without rigid inheritance coupling.",
            "Do not use when template generics or standard interfaces suffice with less boilerplate.",
            "Duck-typing in strongly typed C++; callers don't need to inherit from base classes.",
            "Minor dynamic memory allocation and indirect call overhead in std::function.",
            "std::function, std::any, Custom Value-Semantic Type Erasure.",
            "Excessive dynamic allocations when passing small lambdas (mitigated by Small Buffer Optimization - SBO).",
            "How does std::function implement Type Erasure internally?",
            "It holds a pointer to an internal abstract <code>CallableBase</code> and template derived <code>CallableImpl&lt;Functor&gt;</code> that stores and invokes the actual callable.",
            "Type-Erased Printable Container",
            "Build a type-erased container that prints any object with operator<<.",
            "class AnyPrintable { struct Concept { virtual void print() = 0; }; /* template Model<T> */ };"
        ),
        make_18_step_topic(
            "function-objects-lambdas", "Function Objects, Lambdas & Callback Architecture",
            "Modern event-driven design using lambdas, closures, std::bind, and asynchronous callbacks.",
            "<strong>Function Objects (Functors)</strong> and <strong>Lambdas</strong> are objects that can be called like functions using <code>operator()</code>.",
            "Enables clean callback-driven architectures (e.g. Button click handlers, asynchronous network response callbacks) without rigid inheritance.",
            "Lambdas generate anonymous compiler structs with captured variables stored as member fields.",
            "Pass <code>std::function&lt;void(const Response&)&gt;</code> as callback handlers.",
            {"callout": {"type": "tip", "title": "Lambda Capture Semantics", "text": "[=] captures by value (copy); [&] captures by reference (watch out for dangling stack references!); [this] captures member pointer."}},
            "callbacks_async.cpp",
            """#include <iostream>
#include <functional>
#include <string>

class AsyncHttpClient {
public:
    using Callback = std::function<void(int statusCode, const std::string& body)>;

    void get(const std::string& url, Callback onComplete) {
        std::cout << "[HTTP] Fetching " << url << "...\\n";
        // Simulate network completion
        onComplete(200, "{\\"status\\": \\"success\\"}");
    }
};

int main() {
    AsyncHttpClient client;
    std::string userContext = "Session_9921";

    // Lambda capturing local context
    client.get("https://api.system.org/v1/user", [userContext](int code, const std::string& data) {
        std::cout << "Callback executed for [" << userContext << "] - Code: " << code << ", Body: " << data << "\\n";
    });
    return 0;
}""",
            "AsyncHttpClient executes modern lambda callback with captured local session context.",
            "Asynchronous I/O (Boost.Asio, libuv), GUI button listeners, threading task delegations.",
            "Use for event callbacks, custom container sorting comparators, and filter predicates.",
            "Do not capture local references <code>[&]</code> in asynchronous callbacks that outlive the stack frame (dangling reference bug).",
            "Concise, expressive, inline callback definitions.",
            "Capturing large state by value incurs copy overhead.",
            "Stateless Lambdas, Stateful Closures, Generic Lambdas (C++14), Template Lambdas (C++20).",
            "Capturing local variables by reference in asynchronous background tasks.",
            "What is a dangling reference bug in C++ lambda captures?",
            "If a lambda captures a local stack variable by reference (<code>[&x]</code>) and the lambda executes asynchronously after the enclosing function has returned, accessing <code>x</code> causes undefined behavior / crash.",
            "Timer Callback Handler",
            "Build a Timer utility accepting std::function callback executed on tick.",
            "class Timer { public: void onTick(std::function<void()> cb) { cb(); } };"
        )
    ]
}

# ==============================================================================
# MODULE 13: Concurrency & Thread Safety
# ==============================================================================
mod_13 = {
    "module_id": "13",
    "title": "Concurrency & Thread Safety in LLD",
    "level": "Advanced",
    "category": "Systems",
    "description": "Threads, mutexes, lock_guard, unique_lock, shared_mutex, deadlocks, condition variables, atomic operations, and lock-free design in C++.",
    "topics": [
        make_18_step_topic(
            "threads-and-race-conditions", "Threads, Data Races & Memory Safety",
            "Understanding multi-threaded execution, data races, race conditions, and memory visibility in modern C++.",
            "A <strong>Data Race</strong> occurs when two concurrent threads access the same memory location simultaneously, at least one access is a write, and there is no synchronization. A data race is <strong>Undefined Behavior (UB)</strong> in C++.",
            "Multi-core CPUs execute threads concurrently; unsynchronized writes cause corrupted state, silent calculation bugs, and memory crashes.",
            "Coordinate access to shared mutable state using synchronization primitives (Mutex, Atomics, Lock Guards).",
            "<code>std::jthread</code> (C++20) provides RAII thread joining on scope exit.",
            {"callout": {"type": "trap", "title": "Data Race = Undefined Behavior", "text": "Two threads executing counter++ without synchronization causes lost increments and hardware cache inconsistency. In C++, data race is strict UB!"}},
            "threads_race_demo.cpp",
            """#include <iostream>
#include <thread>
#include <vector>
#include <mutex>

class ThreadSafeCounter {
private:
    int count{0};
    mutable std::mutex mtx; // Protects count from data races

public:
    void increment() {
        std::lock_guard<std::mutex> lock(mtx); // RAII Lock
        ++count;
    }

    [[nodiscard]] int get() const {
        std::lock_guard<std::mutex> lock(mtx);
        return count;
    }
};

int main() {
    ThreadSafeCounter counter;
    std::vector<std::thread> threads;

    for (int i = 0; i < 10; ++i) {
        threads.emplace_back([&counter]() {
            for (int j = 0; j < 1000; ++j) counter.increment();
        });
    }

    for (auto& t : threads) t.join();
    std::cout << "Final Safe Count: " << counter.get() << " (Expected: 10000)\\n";
    return 0;
}""",
            "std::lock_guard guarantees mutual exclusion across 10 threads incrementing count.",
            "Thread pools, concurrent order books, real-time gaming state sync.",
            "Use synchronization whenever mutable state is shared across threads.",
            "Do not share mutable state if message passing (actor model) or thread-local storage suffices.",
            "Thread-safe predictable execution.",
            "Lock contention overhead.",
            "std::thread (C++11), std::jthread with auto-join (C++20).",
            "Forgetting to join or detach a std::thread before destruction, triggering std::terminate().",
            "What is the difference between a Data Race and a Race Condition?",
            "A <strong>Data Race</strong> is unsynchronized concurrent memory access (strictly Undefined Behavior in C++). A <strong>Race Condition</strong> is a semantic timing flaw where output depends on non-deterministic thread execution order.",
            "Thread Safe Accumulator",
            "Build an accumulator summing numbers from 4 worker threads.",
            "class Accumulator { double total{0}; mutex m; public: void add(double v) { lock_guard<mutex> l(m); total += v; } };"
        ),
        make_18_step_topic(
            "mutexes-and-lock-guards", "std::mutex, std::lock_guard & std::unique_lock",
            "RAII-based mutual exclusion locking in C++.",
            "<code>std::mutex</code> provides mutual exclusion. <code>std::lock_guard</code> is an immovable RAII wrapper. <code>std::unique_lock</code> is a movable, flexible lock supporting manual unlock and condition variables.",
            "Manually calling <code>mtx.lock()</code> and <code>mtx.unlock()</code> leaks locks when exceptions or early returns occur, causing permanent deadlocks.",
            "Always wrap mutexes in RAII lock objects on the stack.",
            "<code>std::lock_guard&lt;std::mutex&gt; lock(mtx);</code> locks on creation and unlocks on destruction automatically.",
            {"callout": {"type": "tip", "title": "lock_guard vs unique_lock", "text": "Default to std::lock_guard (or std::scoped_lock in C++17). Use std::unique_lock ONLY when you need deferred locking, manual unlocking, or std::condition_variable!"}},
            "mutex_raii_demo.cpp",
            """#include <iostream>
#include <mutex>
#include <stdexcept>

class BankVault {
private:
    double goldReserves{1000.0};
    mutable std::mutex vaultMutex;

public:
    void transferGold(double amount) {
        std::lock_guard<std::mutex> lock(vaultMutex); // Locks mutex via RAII
        if (amount > goldReserves) {
            throw std::runtime_error("Insufficient reserves"); // Unlocks automatically during stack unwinding!
        }
        goldReserves -= amount;
        std::cout << "Transferred " << amount << " gold. Remaining: " << goldReserves << "\\n";
    }
};""",
            "std::lock_guard automatically releases vaultMutex even if an exception is thrown.",
            "Banking ledgers, hardware controllers, memory allocators.",
            "Use lock_guard for standard critical sections. Use unique_lock with condition variables.",
            "Do not hold locks during slow I/O or network requests.",
            "Exception-safe locking; zero deadlock risk from forgotten unlocks.",
            "Coarse locking reduces concurrency throughput.",
            "std::lock_guard, std::unique_lock, std::scoped_lock (C++17).",
            "Calling mtx.lock() without RAII wrapper.",
            "Why is std::lock_guard preferred over manual mutex.lock()?",
            "Because std::lock_guard is an RAII class that guarantees the mutex will be unlocked when exiting scope, even in the presence of early returns or thrown exceptions.",
            "Thread-Safe Bank Transfer",
            "Implement transfer between two accounts using std::scoped_lock.",
            "void transfer(Account& from, Account& to, double amt) { std::scoped_lock lock(from.m, to.m); from.bal -= amt; to.bal += amt; }"
        ),
        make_18_step_topic(
            "read-write-locks", "Read-Write Locks (std::shared_mutex)",
            "Optimizing read-heavy workloads with multiple concurrent readers and exclusive single writers.",
            "<code>std::shared_mutex</code> (C++17) allows multiple threads to acquire shared read access simultaneously (<code>std::shared_lock</code>) while granting exclusive access to a single writer (<code>std::unique_lock</code>).",
            "In read-heavy systems (e.g. 99% reads, 1% writes like DNS lookups or product catalog queries), standard mutexes serialize all readers, killing throughput.",
            "Readers acquire <code>std::shared_lock</code> concurrently. Writers acquire <code>std::unique_lock</code> exclusively.",
            "Multiple reader threads execute in parallel; writer thread blocks until all active readers finish.",
            {"comparison": {
                "title": "std::mutex vs std::shared_mutex",
                "columns": ["Feature", "std::mutex", "std::shared_mutex"],
                "rows": [
                    ["Concurrent Readers", "1 reader at a time", "Unlimited parallel readers (shared_lock)"],
                    ["Writer", "Exclusive (lock_guard)", "Exclusive (unique_lock)"],
                    ["Best For", "Balanced Read/Write", "Read-Heavy Workloads (>90% reads)"]
                ]
            }},
            "shared_mutex_cache.cpp",
            """#include <iostream>
#include <unordered_map>
#include <string>
#include <shared_mutex>
#include <mutex>

class ThreadSafeCache {
private:
    std::unordered_map<std::string, std::string> cache;
    mutable std::shared_mutex rwMutex; // C++17 Read-Write Mutex

public:
    // READ: Multiple threads can read concurrently!
    std::string get(const std::string& key) const {
        std::shared_lock<std::shared_mutex> readLock(rwMutex);
        auto it = cache.find(key);
        return (it != cache.end()) ? it->second : "";
    }

    // WRITE: Exclusive access; blocks all readers & writers
    void set(const std::string& key, std::string value) {
        std::unique_lock<std::shared_mutex> writeLock(rwMutex);
        cache[key] = std::move(value);
    }
};""",
            "ThreadSafeCache enables concurrent read locks while guarding exclusive writes with unique_lock.",
            "DNS resolver cache, Stock symbol metadata lookup, Web server routing tables.",
            "Use when read operations vastly outnumber write operations (>10:1 ratio).",
            "Do not use if writes are frequent (shared_mutex has higher atomic overhead than standard mutex).",
            "Massive throughput scaling for read-heavy workloads.",
            "Risk of writer starvation if readers continuously hold shared locks.",
            "std::shared_mutex, std::shared_timed_mutex.",
            "Acquiring unique_lock inside getter methods.",
            "When should you choose std::shared_mutex over std::mutex?",
            "When the workload is read-heavy (>90% reads). Multiple readers acquire shared_lock simultaneously without blocking each other.",
            "Read-Heavy User Registry",
            "Implement UserRegistry with concurrent get() and exclusive registerUser().",
            "class Registry { std::shared_mutex rw; public: void read() { std::shared_lock l(rw); } void write() { std::unique_lock l(rw); } };"
        ),
        make_18_step_topic(
            "deadlock-prevention", "Deadlock Prevention & std::scoped_lock",
            "Preventing deadly mutual exclusion deadlocks using lock ordering, lock hierarchies, and std::scoped_lock.",
            "A <strong>Deadlock</strong> occurs when two or more threads are permanently blocked, each holding a lock the other thread needs (Circular Wait: Thread 1 holds Mutex A and waits for B; Thread 2 holds Mutex B and waits for A).",
            "Deadlocks freeze production systems, causing complete service outages requiring process restarts.",
            "Coffman conditions: Eliminate Circular Wait by acquiring multiple mutexes in a globally consistent order.",
            "C++17 <code>std::scoped_lock lock(mutexA, mutexB);</code> uses a deadlock-avoidance algorithm (via <code>std::lock</code>) to lock all mutexes safely.",
            {"callout": {"type": "important", "title": "C++17 scoped_lock Deadlock Defense", "text": "Always use std::scoped_lock lock(accountA.mtx, accountB.mtx); when acquiring multiple mutexes. It uses a deadlock-avoidance algorithm automatically!"}},
            "deadlock_scoped_lock.cpp",
            """#include <iostream>
#include <mutex>
#include <thread>

class Account {
public:
    int id;
    double balance;
    mutable std::mutex mtx;

    Account(int accId, double bal) : id(accId), balance(bal) {}
};

void transferFundsSafe(Account& from, Account& to, double amount) {
    // std::scoped_lock acquires BOTH mutexes without any deadlock risk!
    std::scoped_lock lock(from.mtx, to.mtx);
    if (from.balance >= amount) {
        from.balance -= amount;
        to.balance += amount;
        std::cout << "Transferred $" << amount << " from " << from.id << " to " << to.id << "\\n";
    }
}

int main() {
    Account acc1{1, 1000.0};
    Account acc2{2, 1000.0};

    // Thread 1: 1 -> 2 | Thread 2: 2 -> 1 (Classic Deadlock scenario solved by scoped_lock!)
    std::thread t1(transferFundsSafe, std::ref(acc1), std::ref(acc2), 100.0);
    std::thread t2(transferFundsSafe, std::ref(acc2), std::ref(acc1), 200.0);

    t1.join();
    t2.join();
    return 0;
}"""
            ,"std::scoped_lock locks both accounts atomically using deadlock-avoidance.",
            "Bank account transfers, Dining Philosophers problem, Multi-resource transaction coordinators.",
            "Use std::scoped_lock whenever a function needs to lock 2 or more mutexes simultaneously.",
            "Do not acquire locks in arbitrary order across different functions.",
            "100% immune to circular wait deadlocks.",
            "Slightly higher lock acquisition latency than single mutex.",
            "Hierarchical Locking, Lock Ordering by pointer address, Deadlock Detection Graphs.",
            "Acquiring Mutex A then Mutex B in Function 1, and Mutex B then Mutex A in Function 2.",
            "What are the 4 Coffman conditions required for a deadlock to occur?",
            "1. Mutual Exclusion, 2. Hold and Wait, 3. No Preemption, 4. Circular Wait. Breaking ANY ONE condition prevents deadlocks.",
            "Dining Philosophers Deadlock Fix",
            "Implement pickForks() for philosopher using std::scoped_lock on left and right forks.",
            "void eat(Fork& left, Fork& right) { std::scoped_lock l(left.m, right.m); }"
        ),
        make_18_step_topic(
            "condition-variables", "Condition Variables & Producer-Consumer Queues",
            "Signaling and thread synchronization using std::condition_variable for blocking concurrent task queues.",
            "<code>std::condition_variable</code> is a synchronization primitive that allows threads to sleep (block) without consuming CPU cycles until notified by another thread that a condition is met.",
            "Busy-waiting in a <code>while(!ready) {}</code> loop consumes 100% CPU on a core. Condition variables put threads to sleep efficiently.",
            "Consumer calls <code>cv.wait(lock, []{ return !queue.empty(); });</code>. Producer pushes item and calls <code>cv.notify_one()</code>.",
            "<code>cv.wait</code> atomically unlocks the mutex and puts thread to sleep; when awakened, it reacquires the lock and checks predicate (defends against Spurious Wakeups).",
            {"callout": {"type": "important", "title": "Spurious Wakeup Defense", "text": "ALWAYS pass a predicate lambda to cv.wait(lock, [&]{ return !queue.empty(); }); to protect against spurious wakeups (waking up without a signal)!"}},
            "producer_consumer_queue.cpp",
            """#include <iostream>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <thread>

template <typename T>
class ThreadSafeQueue {
private:
    std::queue<T> queue;
    mutable std::mutex mtx;
    std::condition_variable cv;
    bool isFinished{false};

public:
    void push(T item) {
        {
            std::lock_guard<std::mutex> lock(mtx);
            queue.push(std::move(item));
        }
        cv.notify_one(); // Wake up one sleeping consumer thread!
    }

    bool pop(T& item) {
        std::unique_lock<std::mutex> lock(mtx);
        // Wait until queue is non-empty OR shutdown signaled (handles spurious wakeups!)
        cv.wait(lock, [this]() { return !queue.empty() || isFinished; });

        if (queue.empty() && isFinished) return false;

        item = std::move(queue.front());
        queue.pop();
        return true;
    }

    void shutdown() {
        {
            std::lock_guard<std::mutex> lock(mtx);
            isFinished = true;
        }
        cv.notify_all(); // Wake all consumers to exit cleanly
    }
};

int main() {
    ThreadSafeQueue<int> taskQueue;
    std::thread consumer([&taskQueue]() {
        int val;
        while (taskQueue.pop(val)) {
            std::cout << "[Consumer] Processed task #" << val << "\\n";
        }
        std::cout << "[Consumer] Exited cleanly.\\n";
    });

    for (int i = 1; i <= 3; ++i) {
        taskQueue.push(i);
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
    taskQueue.shutdown();
    consumer.join();
    return 0;
}""",
            "ThreadSafeQueue implements blocking pop() and notify_one() with condition variable.",
            "Thread pool work-stealing queues, message brokers, logging background flushers.",
            "Use for producer-consumer pipelines, thread pools, and event dispatch queues.",
            "Do not call cv.wait() without a predicate lambda (spurious wakeup bug).",
            "Zero CPU usage while waiting; instant wakeup on data arrival.",
            "Requires careful shutdown signaling.",
            "std::condition_variable (requires unique_lock<mutex>), std::condition_variable_any.",
            "Calling cv.wait without a lock or without a predicate loop.",
            "What is a Spurious Wakeup in multi-threading?",
            "A condition where a sleeping thread awakens from <code>wait()</code> even though no thread called <code>notify()</code>. Passing a predicate loop (<code>cv.wait(lock, []{ return ready; })</code>) ensures the thread re-checks the invariant before proceeding.",
            "Blocking Work Queue",
            "Implement a bounded blocking queue with max capacity that blocks producers when full.",
            "class BoundedQueue { condition_variable not_full, not_empty; /* ... */ };"
        ),
        make_18_step_topic(
            "atomics-lock-free-basics", "std::atomic & Lock-Free Design Concepts",
            "Lock-free atomic primitives, memory orderings, and hardware CPU cache line synchronization in C++20.",
            "<code>std::atomic&lt;T&gt;</code> provides lock-free, race-free operations on primitive types using CPU hardware instructions (e.g. <code>LOCK CMPXCHG</code> on x86) without operating system mutex locks.",
            "Mutex locks incur kernel context-switch overhead (microsecond scale). Atomics execute in hardware nanosecond cycles.",
            "Hardware atomic instructions guarantee that read-modify-write operations (<code>fetch_add</code>, <code>compare_exchange_strong</code>) are indivisible.",
            "Use <code>std::atomic&lt;int&gt;</code> for high-speed counters, sequence generators, and lock-free ring buffers.",
            {"callout": {"type": "tip", "title": "CAS (Compare-And-Swap)", "text": "expected = 10; bool ok = atomicVal.compare_exchange_strong(expected, 20); // If atomicVal == 10, sets to 20 atomically. If not, updates expected with actual value!"}},
            "atomic_lock_free_demo.cpp",
            """#include <iostream>
#include <atomic>
#include <thread>
#include <vector>

class LockFreeCounter {
private:
    std::atomic<uint64_t> counter{0}; // Hardware atomic
public:
    void increment() {
        // Atomic fetch_add executes in hardware without mutex!
        counter.fetch_add(1, std::memory_order_relaxed);
    }

    [[nodiscard]] uint64_t get() const {
        return counter.load(std::memory_order_relaxed);
    }
};

int main() {
    LockFreeCounter counter;
    std::vector<std::thread> workers;

    for (int i = 0; i < 4; ++i) {
        workers.emplace_back([&counter]() {
            for (int j = 0; j < 250000; ++j) counter.increment();
        });
    }

    for (auto& w : workers) w.join();
    std::cout << "Final Atomic Count: " << counter.get() << " (Expected: 1000000)\\n";
    return 0;
}""",
            "std::atomic<uint64_t> handles 1,000,000 increments across 4 threads lock-free.",
            "High-frequency trading order matching, lock-free SPSC queues, real-time audio mixers.",
            "Use for simple counters, flags, and lock-free state machines.",
            "Do not build complex lock-free data structures without expert knowledge of ABA problem and memory orderings.",
            "Blazing fast performance; immune to deadlocks and priority inversion.",
            "Difficult to write and debug complex lock-free data structures.",
            "std::atomic, std::atomic_flag, Memory orderings (relaxed, acquire, release, seq_cst).",
            "Assuming non-primitive large structs are lock-free (check <code>atomic.is_lock_free()</code>).",
            "What is the ABA problem in lock-free programming?",
            "A condition where Thread 1 reads value A, Thread 2 changes A -> B -> A, and Thread 1's Compare-And-Swap succeeds thinking the value never changed, causing memory corruption. Solved using tagged pointers or hazard pointers.",
            "Atomic Spinlock Mutex",
            "Implement a simple Spinlock using std::atomic_flag.",
            "class Spinlock { std::atomic_flag flag = ATOMIC_FLAG_INIT; public: void lock() { while(flag.test_and_set(std::memory_order_acquire)) {} } void unlock() { flag.clear(std::memory_order_release); } };"
        ),
        make_18_step_topic(
            "thread-safe-singleton", "Thread-safe Singleton & Double-Checked Locking Trap",
            "Why naive double-checked locking was broken in C++98, and why Meyers Singleton is the optimal modern C++ solution.",
            "A <strong>Thread-Safe Singleton</strong> guarantees exactly one instance is initialized safely under multi-threaded concurrency.",
            "Naive singletons create race conditions where two threads simultaneously execute <code>if (instance == nullptr)</code> and instantiate two duplicate singletons.",
            "C++11 Meyers Singleton guarantees thread-safe initialization via static local variables.",
            "The compiler generates internal guards ensuring that only the first thread executes initialization while other threads wait.",
            {"callout": {"type": "trap", "title": "The Double-Checked Locking Anti-Pattern", "text": "In C++98, DCLP (if (!inst) { lock; if (!inst) inst = new T(); }) was broken due to CPU out-of-order execution allocating memory before constructor finishes! In modern C++, always use Meyers Singleton!"}},
            "thread_safe_singleton.cpp",
            """#include <iostream>
#include <thread>
#include <vector>

class ThreadSafeDatabase {
private:
    ThreadSafeDatabase() {
        std::cout << "[Database Engine] Initialized strictly ONCE by thread id: " 
                  << std::this_thread::get_id() << "\\n";
    }

public:
    ThreadSafeDatabase(const ThreadSafeDatabase&) = delete;
    ThreadSafeDatabase& operator=(const ThreadSafeDatabase&) = delete;

    // C++11 Meyers Singleton: Guaranteed Thread-Safe by Language Standard!
    static ThreadSafeDatabase& getInstance() {
        static ThreadSafeDatabase instance; // Magic static
        return instance;
    }

    void executeQuery(const std::string& sql) {
        std::cout << "Executing SQL: " << sql << "\\n";
    }
};

int main() {
    std::vector<std::thread> threads;
    for (int i = 0; i < 5; ++i) {
        threads.emplace_back([]() {
            // Concurrent access to Singleton
            ThreadSafeDatabase::getInstance().executeQuery("SELECT 1");
        });
    }
    for (auto& t : threads) t.join();
    return 0;
}""",
            "Meyers Singleton executes constructor exactly once across 5 concurrent threads.",
            "Logging engines, Configuration registries, Hardware drivers.",
            "Use when an application strictly requires a single shared instance.",
            "Do not write manual Double-Checked Locking with mutexes in modern C++.",
            "Clean, zero manual locks, compiler-enforced thread safety.",
            "Global state makes unit testing with mocks difficult.",
            "Meyers Singleton, std::call_once with std::once_flag.",
            "Implementing raw pointer DCLP without atomic acquire/release fences.",
            "Why was Double-Checked Locking broken before C++11?",
            "Because CPU instruction reordering could reorder pointer assignment before the object constructor finished executing, allowing another thread to observe a non-null pointer to an uninitialized object.",
            "std::call_once Singleton",
            "Implement a thread-safe singleton using std::call_once and std::once_flag.",
            "class S { static void init() {} public: static void get() { static std::once_flag f; std::call_once(f, init); } };"
        )
    ]
}

# ==============================================================================
# MODULE 14: Memory & Resource Management
# ==============================================================================
mod_14 = {
    "module_id": "14",
    "title": "Memory & Resource Management",
    "level": "Advanced",
    "category": "Systems",
    "description": "Stack vs heap memory layouts, ownership transfer semantics, circular references, custom deleters, and memory-safe LLD architectures.",
    "topics": [
        make_18_step_topic(
            "stack-vs-heap-lifetime", "Stack vs Heap Lifetime & Ownership Semantics",
            "Understanding memory allocation mechanics, cache locality, and deterministic stack lifetimes.",
            "<strong>Stack Memory</strong> is fast, automatic, LIFO memory managed by CPU stack pointer adjustments. <strong>Heap Memory</strong> is dynamic memory allocated via <code>new</code> / <code>malloc</code> requiring explicit lifetime management.",
            "Stack allocation is nanoseconds fast ($O(1)$ stack pointer move) with perfect CPU cache locality. Heap allocation involves operating system free-list searches ($O(N)$ allocator overhead) and pointer indirection.",
            "Default to stack allocation. Use heap allocation only when objects must outlive the current scope, have dynamic sizes, or require polymorphic base pointers.",
            "Stack objects are destroyed automatically when exiting scope. Heap objects must be wrapped in RAII smart pointers.",
            {"comparison": {
                "title": "Stack vs Heap Allocation in C++",
                "columns": ["Property", "Stack Allocation", "Heap Allocation"],
                "rows": [
                    ["Speed", "Ultra-fast ($O(1)$ stack pointer shift)", "Slower (OS allocator traversal)"],
                    ["Lifetime", "Scope-bound (Automatic LIFO cleanup)", "Dynamic (Manual or Smart Pointer)"],
                    ["Cache Locality", "Excellent (Contiguous memory)", "Poor (Fragmented heap pages)"],
                    ["Size Limit", "Small (Typically 1MB - 8MB per thread)", "Gigabytes (Virtual memory limit)"]
                ]
            }},
            "stack_vs_heap_demo.cpp",
            """#include <iostream>
#include <memory>
#include <vector>

struct HeavyData { int data[1000]; };

void stackAllocationExample() {
    HeavyData localStack; // Fast, automatic cleanup
}

void heapAllocationExample() {
    auto heapObject = std::make_unique<HeavyData>(); // Dynamic, managed via RAII
}""",
            "Demonstrates stack allocation vs unique_ptr heap allocation.",
            "Real-time game loops, high-performance packet parsers, database engines.",
            "Prefer stack objects for value semantics. Use heap for polymorphism and dynamic buffers.",
            "Do not allocate huge 50MB buffers on the stack (triggers Stack Overflow crash).",
            "Stack gives deterministic cleanup and maximum CPU cache efficiency.",
            "Stack size is strictly limited per thread.",
            "Stack, Heap, Static/BSS segment, Thread-Local Storage (TLS).",
            "Returning a pointer to a stack-allocated local variable.",
            "What causes a Stack Overflow error in C++?",
            "Allocating an array too large for the stack (e.g. <code>int arr[10000000];</code>) or infinite deep recursion without a base exit condition.",
            "Stack Memory Arena",
            "Implement a fixed-size StackArena allocator.",
            "class StackArena { char buf[1024]; int offset{0}; public: void* alloc(size_t s) { void* p = &buf[offset]; offset += s; return p; } };"
        ),
        make_18_step_topic(
            "smart-pointer-ownership-models", "Smart Pointer Ownership Models & Custom Deleters",
            "Deep dive into std::unique_ptr, std::shared_ptr control blocks, and integrating C API custom deleters.",
            "Smart pointers express explicit ownership semantics in modern C++: exclusive (<code>unique_ptr</code>), shared (<code>shared_ptr</code>), and observing (<code>weak_ptr</code>).",
            "Eliminates memory leaks, dangling pointers, and double-free vulnerabilities.",
            "Custom deleters allow smart pointers to manage non-memory OS handles (e.g. C file handles, sockets, database transaction handles).",
            "<code>std::unique_ptr&lt;FILE, decltype(&amp;fclose)&gt; file(fopen(\"...\"), &amp;fclose);</code>.",
            {"callout": {"type": "tip", "title": "Custom Deleter Anatomy", "text": "std::unique_ptr custom deleter is part of the TYPE. std::shared_ptr custom deleter is stored inside the CONTROL BLOCK!"}},
            "custom_deleter_socket.cpp",
            """#include <iostream>
#include <memory>

struct MockSocket { int fd; };
void closeMockSocket(MockSocket* s) {
    std::cout << "[Socket API] Closed socket fd #" << s->fd << "\\n";
    delete s;
}

using UniqueSocket = std::unique_ptr<MockSocket, decltype(&closeMockSocket)>;

UniqueSocket createSocket(int fd) {
    return UniqueSocket(new MockSocket{fd}, &closeMockSocket);
}

int main() {
    {
        UniqueSocket sock = createSocket(8080);
        std::cout << "Socket active on fd: " << sock->fd << "\\n";
    } // closeMockSocket called automatically!
    return 0;
}""",
            "UniqueSocket wraps MockSocket with custom closeMockSocket deleter.",
            "C API integrations (OpenSSL SSL_free, POSIX close, SDL_DestroyWindow).",
            "Use custom deleters whenever wrapping legacy C handles in RAII.",
            "Do not pass stateful heavy custom deleters to unique_ptr without considering type bloat.",
            "Automatic leak-free management of any C handle.",
            "unique_ptr type includes the deleter signature.",
            "Function pointer deleters, Lambda deleters, Functor deleters.",
            "Creating two independent shared_ptr instances from the same raw pointer.",
            "Why is the custom deleter of std::shared_ptr not part of its type?",
            "Because <code>std::shared_ptr</code> uses Type Erasure in its heap control block to store the deleter, keeping the <code>std::shared_ptr&lt;T&gt;</code> type clean and uniform.",
            "OpenGL Texture Smart Pointer",
            "Create unique_ptr wrapper calling glDeleteTextures custom deleter.",
            "using UniqueTex = std::unique_ptr<GLuint, void(*)(GLuint*)>;"
        ),
        make_18_step_topic(
            "circular-reference-weak-ptr", "Circular Dependency Resolution with std::weak_ptr",
            "Breaking cyclic shared_ptr memory leaks using non-owning weak references.",
            "A <strong>Circular Reference</strong> occurs when Object A holds a <code>std::shared_ptr</code> to Object B, and Object B holds a <code>std::shared_ptr</code> to Object A, causing reference counts to stay $\ge 1$ forever (Memory Leak).",
            "Even though all external pointers go out of scope, the objects keep each other alive in memory indefinitely.",
            "Break the cycle: Child holds <code>std::weak_ptr&lt;Parent&gt;</code> back-pointer.",
            "<code>weak_ptr</code> increments <code>weak_count</code>, NOT <code>use_count</code>. To use it, call <code>wp.lock()</code> returning a temporary <code>shared_ptr</code>.",
            {"callout": {"type": "important", "title": "Weak Pointer Lock", "text": "std::shared_ptr<Parent> p = child->parent.lock(); if (p) { p->doSomething(); } // Safe access!"}},
            "circular_weak_ptr_demo.cpp",
            """#include <iostream>
#include <memory>
#include <string>

class Window; // Forward declaration

class Button {
public:
    std::string label;
    // WEAK POINTER: Breaks cyclic leak back to parent window!
    std::weak_ptr<Window> parentWindow;

    explicit Button(std::string l) : label(std::move(l)) {}
    ~Button() { std::cout << "  [Button " << label << "] Destroyed.\\n"; }

    void onClick() {
        if (auto win = parentWindow.lock()) { // Safely promote weak_ptr to shared_ptr
            std::cout << "Button clicked inside Window!\\n";
        } else {
            std::cout << "Parent Window has already been destroyed.\\n";
        }
    }
};

class Window {
public:
    std::string title;
    std::shared_ptr<Button> closeButton;

    explicit Window(std::string t) : title(std::move(t)) {}
    ~Window() { std::cout << "[Window " << title << "] Destroyed.\\n"; }
};

int main() {
    {
        auto win = std::make_shared<Window>("MainWindow");
        auto btn = std::make_shared<Button>("CloseBtn");

        win->closeButton = btn; // Window owns Button
        btn->parentWindow = win; // Button observes Window via weak_ptr!

        btn->onClick();
    } // BOTH Window and Button destroyed cleanly with zero memory leaks!

    std::cout << "Memory verified: No circular leaks!\\n";
    return 0;
}""",
            "Button uses std::weak_ptr<Window> preventing circular reference memory leaks.",
            "DOM Trees, Observer subscriber registries, Graph structures, Cache expiry observers.",
            "Use weak_ptr for parent back-pointers, caches, and observer registries.",
            "Do not use weak_ptr if the relationship is exclusive ownership (use unique_ptr).",
            "Completely eliminates reference cycle memory leaks.",
            "Requires calling lock() before accessing the underlying object.",
            "std::weak_ptr, std::enable_shared_from_this.",
            "Dereferencing a weak_ptr directly without checking if lock() returned non-null.",
            "How does std::enable_shared_from_this use weak_ptr internally?",
            "It holds a private <code>std::weak_ptr&lt;T&gt;</code> to <code>this</code>. Calling <code>shared_from_this()</code> locks this internal weak pointer, safely returning a new <code>std::shared_ptr&lt;T&gt;</code> without creating a duplicate control block.",
            "Graph Node Weak Pointer",
            "Implement a doubly linked graph node using shared_ptr for next and weak_ptr for prev.",
            "class Node { std::shared_ptr<Node> next; std::weak_ptr<Node> prev; };"
        )
    ]
}

# ==============================================================================
# MODULE 15: Exception & Error Design
# ==============================================================================
mod_15 = {
    "module_id": "15",
    "title": "Exception & Error Handling Design",
    "level": "Intermediate",
    "category": "Robustness",
    "description": "Exception safety guarantees (Basic, Strong, Nothrow), std::optional, std::expected (C++23), and robust error propagation.",
    "topics": [
        make_18_step_topic(
            "exception-safety-guarantees", "Exception Safety Guarantees (Basic, Strong, Nothrow)",
            "Mastering the 3 levels of exception safety: Basic guarantee, Strong (Commit-or-Rollback), and Nothrow.",
            "<strong>Exception Safety Guarantees</strong> define the state of an application if an exception is thrown during an operation:<br>• <strong>Basic Guarantee:</strong> No resources leaked; objects remain in valid states.<br>• <strong>Strong Guarantee:</strong> Commit-or-Rollback (if operation fails, state is rolled back to exactly what it was before).<br>• <strong>Nothrow Guarantee (<code>noexcept</code>):</strong> Operation is guaranteed never to fail or throw.",
            "Without exception safety, partial failures leave objects corrupted, invariants broken, and resources leaked.",
            "Use Copy-and-Swap idiom to achieve the Strong Exception Guarantee.",
            "Perform all risky allocations in temporary objects. Once successful, swap state using <code>noexcept</code> swap.",
            {"comparison": {
                "title": "3 Exception Safety Guarantees",
                "columns": ["Guarantee", "Behavior on Exception", "Technique to Achieve"],
                "rows": [
                    ["Basic Guarantee", "No memory leaks, valid invariants", "RAII wrappers"],
                    ["Strong Guarantee", "Commit-or-Rollback (Zero state change)", "Copy-and-Swap idiom"],
                    ["Nothrow (noexcept)", "Never throws under any condition", "Primitive swaps, move constructors, destructors"]
                ]
            }},
            "strong_exception_safety.cpp",
            """#include <iostream>
#include <vector>
#include <string>
#include <utility>

class SafeDatabaseRecord {
private:
    std::string recordId;
    std::vector<int> payload;

public:
    SafeDatabaseRecord(std::string id, std::vector<int> data)
        : recordId(std::move(id)), payload(std::move(data)) {}

    // Strong Exception Guarantee via Copy-and-Swap!
    void updatePayload(std::vector<int> newPayload) {
        // Step 1: Work on temporary copy (can throw std::bad_alloc)
        std::vector<int> temp = std::move(newPayload);

        // Step 2: Commit changes using non-throwing swap!
        payload.swap(temp); // noexcept swap
    }
};""",
            "updatePayload provides Strong Exception Guarantee: if an exception occurs, original payload is unchanged.",
            "Database transaction updates, container push_back reallocations.",
            "Aim for Strong Exception Guarantee on all critical state mutations.",
            "Do not mark functions noexcept if they can legitimately throw.",
            "Predictable, resilient software that recovers from errors gracefully.",
            "Copy-and-swap can require temporary allocations.",
            "Basic, Strong, Nothrow, Destructor noexcept.",
            "Throwing exceptions from inside destructors or swap functions.",
            "Why must destructors and move constructors be marked noexcept in C++?",
            "Because throwing an exception during stack unwinding (when another exception is already active) triggers immediate <code>std::terminate()</code> and crashes the process. Move constructors must be <code>noexcept</code> so standard containers like <code>std::vector</code> can move elements safely during reallocation.",
            "Strong Stack Push",
            "Implement a Stack::push() with Strong Exception Guarantee.",
            "void push(T val) { T* next = new T[size + 1]; /* copy */ std::swap(data, next); delete[] next; }"
        ),
        make_18_step_topic(
            "optional-and-expected-design", "std::optional & std::expected for Explicit Errors",
            "Modern error handling without exception overhead using std::optional (C++17) and std::expected (C++23).",
            "<code>std::optional&lt;T&gt;</code> represents a value that may or may not exist (eliminating magic sentinel return values like -1 or null). <code>std::expected&lt;T, E&gt;</code> represents either a valid value <code>T</code> or an error <code>E</code>.",
            "Exceptions should be reserved for <em>exceptional</em> failures (e.g. disk failure, out of memory). Expected domain failures (e.g. invalid user input, item not found) are better modeled explicitly in return types.",
            "Return <code>std::optional&lt;User&gt;</code> for queries that can be empty. Return <code>std::expected&lt;Token, AuthError&gt;</code> for operations that can fail with specific error reasons.",
            "Caller checks <code>if (res.has_value())</code> or uses monadic operations (<code>and_then</code>, <code>transform</code>).",
            {"callout": {"type": "tip", "title": "Exceptions vs Explicit Return Types", "text": "Exceptional errors (Network down, Corrupt DB) -> Exceptions.\\nExpected domain outcomes (User not found, Invalid password) -> std::optional / std::expected."}},
            "optional_expected_demo.cpp",
            """#include <iostream>
#include <optional>
#include <string>
#include <unordered_map>

class UserRepository {
private:
    std::unordered_map<int, std::string> users{{1, "Alice"}, {2, "Bob"}};

public:
    // Explicit return: Cleanly signals that a user might not exist without exceptions!
    [[nodiscard]] std::optional<std::string> findUsernameById(int id) const {
        auto it = users.find(id);
        if (it != users.end()) return it->second;
        return std::nullopt; // Empty
    }
};

int main() {
    UserRepository repo;
    auto user = repo.findUsernameById(1);
    if (user) {
        std::cout << "Found user: " << *user << "\\n";
    }

    auto missing = repo.findUsernameById(99);
    std::cout << "User 99 exists? " << (missing.has_value() ? "Yes" : "No") << "\\n";
    return 0;
}""",
            "findUsernameById returns std::optional<std::string> avoiding null pointer traps.",
            "Database repository lookups, configuration parsers, mathematical domain calculations.",
            "Use optional/expected for expected operational results (e.g. cache misses, validation failures).",
            "Do not use optional for fatal system failures.",
            "Expressive function signatures; zero runtime exception overhead.",
            "Requires checking has_value() at call sites.",
            "std::optional (C++17), std::expected (C++23), Monadic operations.",
            "Calling .value() on an empty optional without checking has_value() (throws std::bad_optional_access).",
            "What is the advantage of std::expected over returning error codes or throwing exceptions?",
            "<code>std::expected</code> forces callers to handle both the success value and error type at compile time with zero heap allocation or stack unwinding overhead.",
            "Safe String to Int Parser",
            "Build a safeStringToInt() returning std::optional<int>.",
            "std::optional<int> safeToInt(const std::string& s) { try { return std::stoi(s); } catch(...) { return std::nullopt; } }"
        ),
        make_18_step_topic(
            "error-handling-tradeoffs", "Exceptions vs Error Codes in Low-Level Design",
            "Architectural evaluation: Performance, stack unwinding latency, binary size, and domain error strategies.",
            "A structured evaluation of when to use C++ Exceptions vs Error Codes / Monadic Result types.",
            "Low-latency systems (HFT, game engines) often disable C++ exceptions (<code>-fno-exceptions</code>) due to binary bloat and non-deterministic stack unwinding latency.",
            "Use exceptions for rare, fatal system failures. Use error codes/expected for predictable domain logic branches.",
            "Benchmark and align error handling with non-functional latency requirements.",
            {"comparison": {
                "title": "Exceptions vs Error Codes / std::expected",
                "columns": ["Dimension", "C++ Exceptions", "std::expected / Error Codes"],
                "rows": [
                    ["Happy Path Performance", "Zero-cost (Zero overhead if no throw)", "Small return value check overhead"],
                    ["Error Path Performance", "Slow (Stack unwinding, OS tables)", "Fast ($O(1)$ value branch)"],
                    ["API Clarity", "Can be invisible (hidden throw)", "Explicit in function signature"],
                    ["Binary Size", "Increases executable size (EH tables)", "Compact binary"]
                ]
            }},
            "error_tradeoffs_demo.cpp",
            """#include <iostream>
#include <string>

enum class ParseError { INVALID_FORMAT, OUT_OF_RANGE };

struct ParseResult {
    bool success;
    int value;
    ParseError error;
};

ParseResult parsePort(const std::string& str) {
    if (str.empty()) return {false, 0, ParseError::INVALID_FORMAT};
    int p = std::stoi(str);
    if (p < 1 || p > 65535) return {false, 0, ParseError::OUT_OF_RANGE};
    return {true, p, ParseError::INVALID_FORMAT};
}""",
            "Explicit ParseResult struct avoiding exception overhead in network parser.",
            "Embedded microcontrollers, real-time operating systems, trading gateways.",
            "Follow company/system coding standards (e.g. Google C++ Style Guide avoids exceptions).",
            "Do not mix unstructured error codes and exceptions randomly without architectural rules.",
            "Clear error contracts and predictable runtime behavior.",
            "Error codes can be ignored if not marked [[nodiscard]].",
            "Error Codes, [[nodiscard]], std::expected, C++ Exceptions.",
            "Ignoring error code returns.",
            "Why is the happy path faster with zero-cost exceptions, but the error path slower?",
            "Zero-cost exceptions emit side tables (DWARF / SEH) that add zero instructions during normal execution. However, when an exception is thrown, the runtime must parse these tables and unwind the stack, which is orders of magnitude slower.",
            "Nodiscard Error Code Function",
            "Declare a [[nodiscard]] function returning error status.",
            "[[nodiscard]] bool writePacket(const void* buf, size_t len);"
        )
    ]
}

# ==============================================================================
# MODULE 16: API & Interface Design
# ==============================================================================
mod_16 = {
    "module_id": "16",
    "title": "API & Interface Design",
    "level": "Advanced",
    "category": "Architecture",
    "description": "Designing intuitive, foolproof, and stable C++ public interfaces, contracts, preconditions, and ABI evolution.",
    "topics": [
        make_18_step_topic(
            "stable-public-interfaces", "Designing Intuitive & Hard-to-Misuse Interfaces",
            "Scott Meyers' rule: 'Make interfaces easy to use correctly and hard to use incorrectly.'",
            "A well-designed public interface uses strong typing, <code>[[nodiscard]]</code>, explicit constructors, and const-correctness to prevent caller misuse at compile time.",
            "Stringly-typed APIs (e.g. <code>setTime(int, int, int)</code> where caller mixes up hours, minutes, and seconds) cause catastrophic production bugs.",
            "Use Strong Types (e.g. <code>Seconds</code>, <code>Milliseconds</code>) instead of raw integers.",
            "Design APIs where invalid states fail to compile.",
            {"callout": {"type": "tip", "title": "Strong Typing Defense", "text": "Before: setDuration(1000); // Is it seconds or milliseconds?\\nAfter: setDuration(std::chrono::milliseconds(1000)); // Completely unambiguous!"}},
            "strong_type_api.cpp",
            """#include <iostream>
#include <chrono>

struct UserId { explicit UserId(int id) : value(id) {} int value; };
struct OrderId { explicit OrderId(int id) : value(id) {} int value; };

class OrderService {
public:
    // Strong Types prevent passing OrderId where UserId is expected!
    void cancelOrder(UserId user, OrderId order) {
        std::cout << "User #" << user.value << " cancelled Order #" << order.value << "\\n";
    }
};

int main() {
    OrderService service;
    UserId user{42};
    OrderId order{999};

    service.cancelOrder(user, order);
    // service.cancelOrder(order, user); // COMPILE ERROR! Cannot mix up arguments!
    return 0;
}""",
            "Strong types UserId and OrderId prevent parameter ordering bugs at compile time.",
            "Chrono duration types, Financial currency APIs, Embedded GPIO pin configurations.",
            "Use strong types whenever an interface accepts multiple parameters of the same primitive type.",
            "Do not create wrappers for trivial single-argument helper functions.",
            "Eliminates subtle parameter swapping bugs at compile time.",
            "Small amount of boilerplate wrapper struct definitions.",
            "Strong Typedefs, Enum Classes, Chrono Durations, Named Parameters.",
            "Accepting boolean flags (e.g. <code>initialize(true, false, true)</code>) instead of explicit enum options.",
            "Why is <code>setMode(bool isFast, bool isEncrypted)</code> a bad interface design?",
            "Because call sites look like <code>setMode(true, false)</code>, which is completely unreadable and prone to swapping argument order. An enum class (<code>setMode(Speed::FAST, Security::ENCRYPTED)</code>) is self-documenting and foolproof.",
            "Strong Type Coordinates",
            "Create strong types Latitude and Longitude to prevent coordinate swapping.",
            "struct Latitude { double val; }; struct Longitude { double val; };"
        ),
        make_18_step_topic(
            "design-by-contract", "Design by Contract (Preconditions, Postconditions, Invariants)",
            "Formalizing software correctness through preconditions, postconditions, and class invariants.",
            "<strong>Design by Contract (DbC)</strong> views software components as collaborating parties fulfilling mutual obligations:<br>• <strong>Preconditions:</strong> What must be true before calling a method.<br>• <strong>Postconditions:</strong> What the method guarantees upon return.<br>• <strong>Invariants:</strong> What must remain true throughout object lifetime.",
            "Unclear contracts lead to defensive code duplication where every function re-validates the same inputs.",
            "If the caller violates preconditions, the method fails fast (assert / throw). The method guarantees postconditions.",
            "Use <code>assert()</code> for programming bugs and exceptions for runtime environment failures.",
            {"callout": {"type": "tip", "title": "Contract Triad", "text": "Precondition: balance >= amount\\nAction: balance -= amount\\nPostcondition: balance == old_balance - amount\\nInvariant: balance >= overdraft_limit"}},
            "design_by_contract.cpp",
            """#include <iostream>
#include <cassert>

class BoundedBuffer {
private:
    int count{0};
    const int capacity{10};

    void checkClassInvariants() const {
        assert(count >= 0 && count <= capacity && "Invariant Broken: Count out of bounds!");
    }

public:
    void push() {
        // Precondition
        assert(count < capacity && "Precondition Broken: Buffer is full!");

        int oldCount = count;
        ++count; // Action

        // Postcondition & Invariant
        assert(count == oldCount + 1 && "Postcondition Broken!");
        checkClassInvariants();
    }
};""",
            "BoundedBuffer validates preconditions, postconditions, and class invariants.",
            "Mission-critical avionics (Eiffel, Ada), safety-critical automotive systems (AUTOSAR C++).",
            "Use DbC thinking in all domain classes to clarify caller vs callee obligations.",
            "Do not disable precondition checks in production without verified static analysis.",
            "Self-documenting, mathematically verifiable system integrity.",
            "Adds assertion overhead during debug builds.",
            "C++20/26 Contracts, Assertions, Static Analysis annotations.",
            "Treating precondition bugs as catchable runtime exceptions instead of fixing the caller bug.",
            "What is the difference between a Precondition violation and a Runtime Exception?",
            "A <strong>Precondition violation</strong> is a <em>bug in the calling code</em> (should never happen in correct software). A <strong>Runtime Exception</strong> is an <em>unpredictable environmental failure</em> (e.g. disk full, network lost).",
            "Stack Contract Verification",
            "Implement pop() verifying precondition !empty() and postcondition size == old - 1.",
            "void pop() { assert(!empty()); --size; }"
        ),
        make_18_step_topic(
            "backward-compatibility-versioning", "API Evolution, Versioning & Extensibility",
            "Evolving C++ APIs without breaking existing clients or binary ABI compatibility.",
            "Techniques for evolving C++ libraries gracefully: Deprecation attributes (<code>[[deprecated]]</code>), default arguments, versioned inline namespaces, and PImpl ABI preservation.",
            "Breaking changes in public APIs force all dependent client projects to rewrite code and recompile.",
            "Never remove or change existing function signatures in minor versions; add overloaded extensions and mark old methods deprecated.",
            "Use <code>inline namespace v2</code> to version APIs seamlessly.",
            {"callout": {"type": "tip", "title": "Inline Namespace Versioning", "text": "namespace Lib { inline namespace v2 { class Engine; } namespace v1 { class Engine; } }"}},
            "api_versioning_demo.cpp",
            """#include <iostream>

namespace DatabaseLib {
    // Legacy Version 1
    namespace v1 {
        class Connector {
        public:
            [[deprecated("Use v2::Connector with connection timeout support")]]
            void connect() { std::cout << "[v1] Connected without timeout\\n"; }
        };
    }

    // Modern Version 2 (Default via inline namespace!)
    inline namespace v2 {
        class Connector {
        public:
            void connect(int timeoutMs = 5000) {
                std::cout << "[v2] Connected with timeout: " << timeoutMs << "ms\\n";
            }
        };
    }
}

int main() {
    DatabaseLib::Connector modern; // Automatically resolves to v2
    modern.connect(3000);

    DatabaseLib::v1::Connector legacy; // Explicit v1 access
    legacy.connect();
    return 0;
}""",
            "Demonstrates seamless API evolution using inline namespace v2 and [[deprecated]] attributes.",
            "Boost C++ libraries, Standard Library versioning, Game engine SDKs.",
            "Use when publishing reusable libraries used by other development teams.",
            "Do not over-engineer versioning for internal single-team applications.",
            "Smooth deprecation cycles without abrupt breaking changes.",
            "Maintaining legacy version code increases library footprint.",
            "Inline Namespaces, SemVer, Deprecation Warnings, PImpl ABI firewalls.",
            "Modifying the memory layout of exported classes in minor version library updates (breaking ABI).",
            "How do inline namespaces enable library versioning in C++11?",
            "An <code>inline namespace</code> makes its members accessible in the enclosing namespace without qualification by default, allowing new versions to be default while keeping older version namespaces explicitly available.",
            "Deprecated Method Migration",
            "Mark old login() method [[deprecated]] while providing modern login(token).",
            "class Auth { public: [[deprecated]] void login(string u, string p); void login(Token t); };"
        )
    ]
}

# ==============================================================================
# MODULE 17: Extensibility
# ==============================================================================
mod_17 = {
    "module_id": "17",
    "title": "Extensibility & Open-Closed Architectures",
    "level": "Advanced",
    "category": "Architecture",
    "description": "Refactoring massive if-else/switch state machines into polymorphic, plug-and-play extensible systems using plugin registries.",
    "topics": [
        make_18_step_topic(
            "refactoring-switch-chains", "Refactoring Giant Switch/If-Else Chains",
            "Techniques to replace hardcoded procedural switch-case chains with polymorphic strategy dispatch.",
            "Replacing monolithic <code>switch(type)</code> statements with polymorphic class hierarchies or strategy maps.",
            "Switch chains violate the Open/Closed Principle: every new feature requires modifying every switch block across the entire project.",
            "Extract each case block into a standalone class implementing a shared interface.",
            "Use a factory or registry map to dispatch to the correct class polymorphically.",
            {"callout": {"type": "tip", "title": "Before vs After", "text": "Before: switch(type) { case PDF: ... case CSV: ... case JSON: ... } (Bloated)\\nAfter: exporterMap[type]->exportData() (Extensible!)"}},
            "refactor_switch_to_poly.cpp",
            """#include <iostream>
#include <memory>
#include <unordered_map>
#include <string>

class IReportExporter {
public:
    virtual ~IReportExporter() = default;
    virtual void exportReport(const std::string& data) = 0;
};

class PdfExporter : public IReportExporter {
public:
    void exportReport(const std::string& data) override { std::cout << "[PDF] Exported: " << data << "\\n"; }
};

class CsvExporter : public IReportExporter {
public:
    void exportReport(const std::string& data) override { std::cout << "[CSV] Exported: " << data << "\\n"; }
};

// Extensible Registry replacing giant switch statement!
class ReportExportRegistry {
private:
    std::unordered_map<std::string, std::unique_ptr<IReportExporter>> registry;
public:
    void registerExporter(const std::string& format, std::unique_ptr<IReportExporter> exporter) {
        registry[format] = std::move(exporter);
    }

    void executeExport(const std::string& format, const std::string& data) {
        auto it = registry.find(format);
        if (it != registry.end()) {
            it->second->exportReport(data);
        } else {
            std::cout << "Unsupported format: " << format << "\\n";
        }
    }
};

int main() {
    ReportExportRegistry exporter;
    exporter.registerExporter("pdf", std::make_unique<PdfExporter>());
    exporter.registerExporter("csv", std::make_unique<CsvExporter>());

    exporter.executeExport("pdf", "Financial Q3 Data");
    return 0;
}""",
            "ReportExportRegistry replaces switch statements with dynamic hash map dispatch.",
            "Payment processors, document exporters, game command handlers.",
            "Use whenever you see duplicate switch(enum) statements scattered across multiple files.",
            "Do not replace simple 2-case switches for static state.",
            "Zero switch maintenance; new formats registered at runtime.",
            "Small hash map lookup indirection.",
            "Map of Strategies, Factory Pattern, Polymorphic Subclasses.",
            "Leaving default switch cases that throw runtime errors when new enums are added.",
            "Why is switch-case over an enum considered a code smell in object-oriented design?",
            "Because adding a new enum value requires searching and editing every switch block across the entire codebase, violating OCP and risking unhandled cases.",
            "Refactor Shape Renderer Switch",
            "Refactor renderShape(ShapeType) switch to shape->render().",
            "class IShape { public: virtual void render() = 0; };"
        ),
        make_18_step_topic(
            "plugin-and-registry-architecture", "Plugin & Registry Architectures in C++",
            "Designing dynamic self-registering plugin architectures using static initialization and factory maps.",
            "A <strong>Plugin Registry</strong> allows new classes to automatically register themselves with a central factory at startup without modifying the factory source code.",
            "Adding a new plugin should not require modifying the central factory's <code>switch</code> statement.",
            "Self-registering static proxies register creator functions into a central map during static initialization.",
            "<code>REGISTER_PLUGIN(CsvExporter, \"csv\")</code> automatically registers the class before <code>main()</code> runs.",
            {"callout": {"type": "tip", "title": "Self-Registration Macro", "text": "static bool registered = PluginFactory::registerCreator(\"pdf\", []{ return make_unique<PdfPlugin>(); });"}},
            "plugin_registry_demo.cpp",
            """#include <iostream>
#include <memory>
#include <unordered_map>
#include <functional>
#include <string>

class IPlugin {
public:
    virtual ~IPlugin() = default;
    virtual void run() = 0;
};

class PluginFactory {
public:
    using Creator = std::function<std::unique_ptr<IPlugin>()>;

    static std::unordered_map<std::string, Creator>& getRegistry() {
        static std::unordered_map<std::string, Creator> registry;
        return registry;
    }

    static bool registerPlugin(const std::string& name, Creator creator) {
        getRegistry()[name] = std::move(creator);
        return true;
    }

    static std::unique_ptr<IPlugin> create(const std::string& name) {
        auto& reg = getRegistry();
        auto it = reg.find(name);
        return (it != reg.end()) ? it->second() : nullptr;
    }
};

// Plugin A (Self-Registering!)
class AudioPlugin : public IPlugin {
public:
    void run() override { std::cout << "[AudioPlugin] Processing high-fidelity audio stream.\\n"; }
    static inline bool isRegistered = PluginFactory::registerPlugin("audio", []() {
        return std::make_unique<AudioPlugin>();
    });
};

int main() {
    auto plugin = PluginFactory::create("audio");
    if (plugin) plugin->run();
    return 0;
}""",
            "AudioPlugin self-registers into PluginFactory before main() executes.",
            "Photoshop filters, Audio DAW VSTs, Database dialect plugins in ORMs.",
            "Use when building extensible software frameworks where 3rd parties can add new plugins.",
            "Do not rely on static registration across static library (.a / .lib) boundaries without linker include flags.",
            "True 100% decoupling: adding a plugin requires zero edits to core engine files.",
            "Static initialization order subtleties across shared libraries.",
            "Dynamic DLL/so loading via dlopen/LoadLibrary, Static Registry.",
            "Static initialization order fiasco when registry map is initialized after plugins.",
            "How does self-registration work during static initialization in C++?",
            "A static global or <code>static inline</code> boolean variable in the plugin's <code>.cpp</code> file initializes before <code>main()</code> runs, calling the central factory's registration method.",
            "Self-Registering Database Driver",
            "Build self-registering driver framework for Postgres and MySQL.",
            "class DriverRegistry { public: static void reg(string n, Creator c); };"
        ),
        make_18_step_topic(
            "extensible-payment-system-case-study", "Case Study: Multi-Gateway Extensible Payment Engine",
            "End-to-end architectural case study refactoring a monolithic payment engine into an open-closed extensible system.",
            "A comprehensive case study applying SOLID, Strategy, Factory, and Dependency Injection to architect a multi-gateway payment engine.",
            "Payment systems must support credit cards, PayPal, Apple Pay, Crypto, and regional gateways without modifying checkout workflows.",
            "Decouple checkout orchestrator from payment execution strategies and gateway adapters.",
            "Gateway Registry + Strategy Pattern + Invariant Validation.",
            {"diagram": {
                "title": "Extensible Payment System Architecture",
                "classes": [
                    {"name": "CheckoutCoordinator", "attributes": [{"visibility": "-", "name": "factory", "type": "PaymentGatewayFactory"}]},
                    {"name": "IPaymentGateway", "stereotype": "interface", "isInterface": True, "attributes": [], "methods": [{"visibility": "+", "name": "charge", "params": "amount: double", "returnType": "bool"}]},
                    {"name": "StripeGateway", "attributes": [], "methods": [{"visibility": "+", "name": "charge", "params": "amount: double", "returnType": "bool override"}]},
                    {"name": "PayPalGateway", "attributes": [], "methods": [{"visibility": "+", "name": "charge", "params": "amount: double", "returnType": "bool override"}]}
                ],
                "relationships": [
                    {"from": "StripeGateway", "to": "IPaymentGateway", "type": "inheritance", "label": "implements"},
                    {"from": "PayPalGateway", "to": "IPaymentGateway", "type": "inheritance", "label": "implements"}
                ]
            }},
            "extensible_payment_system.cpp",
            """#include <iostream>
#include <memory>
#include <string>
#include <unordered_map>

class IPaymentStrategy {
public:
    virtual ~IPaymentStrategy() = default;
    virtual bool pay(double amount) = 0;
};

class CreditCardStrategy : public IPaymentStrategy {
public:
    bool pay(double amount) override {
        std::cout << "[Stripe API] Processed Credit Card payment of $" << amount << "\\n";
        return true;
    }
};

class CryptoStrategy : public IPaymentStrategy {
public:
    bool pay(double amount) override {
        std::cout << "[Web3 Gateway] Transferred $" << amount << " in USDC stablecoin\\n";
        return true;
    }
};

class PaymentEngine {
private:
    std::unordered_map<std::string, std::shared_ptr<IPaymentStrategy>> strategies;
public:
    void registerStrategy(const std::string& name, std::shared_ptr<IPaymentStrategy> s) {
        strategies[name] = std::move(s);
    }

    bool checkout(const std::string& method, double amount) {
        auto it = strategies.find(method);
        if (it == strategies.end()) {
            std::cout << "Error: Payment method '" << method << "' not supported.\\n";
            return false;
        }
        return it->second->pay(amount);
    }
};

int main() {
    PaymentEngine engine;
    engine.registerStrategy("card", std::make_shared<CreditCardStrategy>());
    engine.registerStrategy("crypto", std::make_shared<CryptoStrategy>());

    engine.checkout("card", 129.50);
    engine.checkout("crypto", 500.00);
    return 0;
}""",
            "PaymentEngine orchestrates payment strategies dynamically with zero hardcoded switch blocks.",
            "E-commerce platforms (Shopify, Amazon), SaaS subscription billing engines (Stripe Billing).",
            "Use in any multi-provider integration architecture.",
            "Do not use if only one fixed payment provider is supported.",
            "100% Open/Closed; seamless gateway onboarding.",
            "Requires robust error translation from 3rd-party gateway error codes.",
            "Synchronous Payment Engine, Asynchronous Webhook Payment Engine.",
            "Hardcoding currency conversion logic inside individual gateway classes.",
            "How do you handle gateway-specific configuration (e.g. API keys) in an extensible payment engine?",
            "Pass gateway-specific configuration objects to concrete strategy constructors during initialization or factory assembly, keeping the shared IPaymentStrategy interface clean and generic.",
            "Payment Refund Extension",
            "Add refund() capability to payment engine without breaking pay().",
            "class IRefundable { public: virtual bool refund(string txId) = 0; };"
        )
    ]
}

# ==============================================================================
# MODULE 18: Common LLD Patterns
# ==============================================================================
mod_18 = {
    "module_id": "18",
    "title": "Common LLD Composite Patterns",
    "level": "Intermediate",
    "category": "Design Patterns",
    "description": "Object Pool Pattern for high-performance allocation reuse, Repository / DAO patterns for clean persistence, and Service Locator vs Dependency Injection.",
    "topics": [
        make_18_step_topic(
            "object-pool-pattern", "Object Pool Pattern for High-Performance C++",
            "Reusing expensive-to-construct objects from a pre-allocated pool to eliminate dynamic heap allocation overhead.",
            "The <strong>Object Pool Pattern</strong> maintains a cache of pre-allocated initialized objects, leasing them to clients and reclaiming them upon completion instead of allocating on the heap.",
            "Frequent <code>new</code> and <code>delete</code> calls fragment heap memory and cause latency spikes in high-performance systems.",
            "Pre-allocate $N$ objects in a vector/queue. <code>acquire()</code> returns an object; custom deleter returns it to the pool upon destruction.",
            "Combine with <code>std::unique_ptr</code> and custom deleters for seamless RAII automatic recycling.",
            {"callout": {"type": "tip", "title": "Automatic Pool Recycling", "text": "unique_ptr<Connection, PoolDeleter> conn = pool.acquire(); // When conn exits scope, it returns to pool automatically without calling delete!"}},
            "object_pool_raii.cpp",
            """#include <iostream>
#include <vector>
#include <memory>
#include <functional>

class DatabaseConnection {
public:
    int connectionId;
    explicit DatabaseConnection(int id) : connectionId(id) {
        std::cout << "[DB Connection #" << connectionId << "] Created in pool.\\n";
    }
    void resetState() { std::cout << "[DB Connection #" << connectionId << "] Reset state.\\n"; }
};

class ConnectionPool {
private:
    std::vector<std::unique_ptr<DatabaseConnection>> pool;
public:
    explicit ConnectionPool(size_t initialSize) {
        for (size_t i = 1; i <= initialSize; ++i) {
            pool.push_back(std::make_unique<DatabaseConnection>(i));
        }
    }

    using PooledConn = std::unique_ptr<DatabaseConnection, std::function<void(DatabaseConnection*)>>;

    PooledConn acquire() {
        if (pool.empty()) {
            throw std::runtime_error("Pool exhausted");
        }
        auto rawPtr = pool.back().release();
        pool.pop_back();

        // Custom deleter returns object to pool instead of deleting!
        return PooledConn(rawPtr, [this](DatabaseConnection* conn) {
            conn->resetState();
            pool.push_back(std::unique_ptr<DatabaseConnection>(conn));
            std::cout << "[Pool] Reclaimed connection #" << conn->connectionId << "\\n";
        });
    }

    [[nodiscard]] size_t available() const { return pool.size(); }
};

int main() {
    ConnectionPool pool(2);
    {
        auto conn1 = pool.acquire();
        std::cout << "Using connection #" << conn1->connectionId << "\\n";
    } // conn1 automatically recycled back to pool!

    std::cout << "Available in pool: " << pool.available() << "\\n";
    return 0;
}""",
            "ConnectionPool uses custom RAII deleter to automatically recycle DatabaseConnection instances.",
            "Database connection pools, Game particle/bullet pools, Thread pools, Network buffer pools.",
            "Use when object creation/destruction cost is high and objects are reused frequently.",
            "Do not use for simple, lightweight structs where standard stack allocation is faster.",
            "Zero heap fragmentation; deterministic high-throughput performance.",
            "Requires resetting dirty object state before recycling.",
            "Fixed-size Pool, Dynamic Growing Pool, Thread-Safe Pool.",
            "Forgetting to reset state before reuse, leaking dirty data across requests.",
            "How can std::unique_ptr be used to automate object recycling in an Object Pool?",
            "By passing a custom lambda deleter to <code>std::unique_ptr</code> that pushes the raw pointer back into the pool's internal collection instead of calling <code>delete</code>.",
            "Game Bullet Pool",
            "Implement a 100-bullet pre-allocated BulletPool.",
            "class BulletPool { vector<unique_ptr<Bullet>> pool; public: auto get(); };"
        ),
        make_18_step_topic(
            "repository-dao-pattern", "Repository & Data Access Object (DAO) Patterns",
            "Decoupling domain business logic from database persistence layers.",
            "The <strong>Repository Pattern</strong> mediates between domain and data mapping layers, providing a collection-like interface (<code>find()</code>, <code>save()</code>, <code>remove()</code>) for domain entities.",
            "Mixing SQL queries directly in domain business logic makes testing impossible and ties business rules to database schemas.",
            "Domain code talks to <code>IUserRepository</code>. Repository handles SQL/NoSQL mapping.",
            "Repository mimics an in-memory collection of domain entities.",
            {"callout": {"type": "tip", "title": "Repository Layer", "text": "Domain Service -> IUserRepository -> [SqlUserRepository / InMemoryMockRepository]"}},
            "repository_pattern.cpp",
            """#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <optional>

struct User { int id; std::string name; };

class IUserRepository {
public:
    virtual ~IUserRepository() = default;
    virtual void save(const User& user) = 0;
    virtual std::optional<User> findById(int id) = 0;
};

class InMemoryUserRepository : public IUserRepository {
private:
    std::vector<User> storage;
public:
    void save(const User& user) override {
        storage.push_back(user);
        std::cout << "[Repository] Saved user: " << user.name << "\\n";
    }

    std::optional<User> findById(int id) override {
        for (const auto& u : storage) {
            if (u.id == id) return u;
        }
        return std::nullopt;
    }
};

int main() {
    auto repo = std::make_shared<InMemoryUserRepository>();
    repo->save(User{1, "Alice"});
    auto found = repo->findById(1);
    if (found) std::cout << "Retrieved: " << found->name << "\\n";
    return 0;
}""",
            "InMemoryUserRepository provides clean collection interface over User entity storage.",
            "Domain-Driven Design enterprise applications, microservice persistence tiers.",
            "Use in all applications that persist domain entities to external storage.",
            "Do not create repositories for individual non-aggregate child objects.",
            "Clean abstraction; trivial in-memory mock testing.",
            "Adds abstraction layer over database queries.",
            "Generic Repository, Specific Domain Aggregate Repository.",
            "Leaking database connection/SQL types through repository interface methods.",
            "What is the difference between Repository and DAO?",
            "<strong>DAO</strong> is a low-level database mapping abstraction (table CRUD operations). <strong>Repository</strong> is a higher-level Domain-Driven Design pattern representing an in-memory collection of complete domain Aggregates.",
            "Order Repository Interface",
            "Implement IOrderRepository with save(Order) and findByCustomerId(int).",
            "class IOrderRepo { public: virtual void save(const Order&) = 0; };"
        ),
        make_18_step_topic(
            "service-locator-di", "Service Locator vs Dependency Injection",
            "Comparing Dependency Injection and Service Locator: Why DI is superior for testability and explicit dependencies.",
            "<strong>Service Locator</strong> is a central registry where classes look up dependencies. <strong>Dependency Injection</strong> passes dependencies directly via constructor.",
            "Service Locator hides true dependencies inside class method bodies, making dependencies invisible from class signatures.",
            "DI makes dependencies explicit in the constructor signature. Service Locator uses a global locator singleton.",
            "Prefer Constructor Dependency Injection over Service Locator.",
            {"comparison": {
                "title": "Service Locator vs Dependency Injection",
                "columns": ["Feature", "Dependency Injection (Preferred)", "Service Locator (Anti-pattern)"],
                "rows": [
                    ["Visibility", "Explicit in constructor signature", "Hidden inside method bodies"],
                    ["Testability", "Trivial (Pass mocks directly)", "Hard (Must configure global locator state)"],
                    ["Coupling", "Zero coupling to container", "Tightly coupled to locator registry"]
                ]
            }},
            "di_vs_locator.cpp",
            """#include <iostream>
#include <memory>

class ILogger { public: virtual ~ILogger() = default; virtual void log(const std::string& m) = 0; };
class ConsoleLog : public ILogger { public: void log(const std::string& m) override { std::cout << m << "\\n"; } };

// Preferred: Constructor Dependency Injection
class CleanService {
    std::shared_ptr<ILogger> logger; // Explicit dependency!
public:
    explicit CleanService(std::shared_ptr<ILogger> l) : logger(std::move(l)) {}
    void doWork() { logger->log("Work completed cleanly."); }
};""",
            "CleanService explicitly declares ILogger dependency in constructor.",
            "Framework architecture comparisons in system design interviews.",
            "Use Dependency Injection as the default standard.",
            "Avoid Service Locator in modern object-oriented architectures.",
            "Explicit contracts and compile-time verification of dependencies.",
            "Constructor parameter lists can grow if not modularized.",
            "Constructor DI, Setter DI, Ambient Context.",
            "Using Service Locator to hide 15 dependencies inside a class.",
            "Why is Service Locator considered an anti-pattern compared to Dependency Injection?",
            "Because Service Locator hides class dependencies, introduces a global singleton dependency, and makes unit testing error-prone due to shared state.",
            "Refactor Service Locator to DI",
            "Refactor ServiceLocator::get<IDb>() to constructor injection.",
            "class Svc { std::shared_ptr<IDb> db; public: Svc(std::shared_ptr<IDb> d): db(d) {} };"
        )
    ]
}

write_module(mod_12)
write_module(mod_13)
write_module(mod_14)
write_module(mod_15)
write_module(mod_16)
write_module(mod_17)
write_module(mod_18)
