import json
import os

content_dir = "content"
os.makedirs(content_dir, exist_ok=True)

# Module 20: Advanced Low-Level Design & Scaling
m20 = {
    "module_id": "20",
    "module_title": "Advanced Low-Level Design & Scaling",
    "description": "High-throughput memory alignment, zero-copy, lock-free ring buffers, cache locality, and latency optimization.",
    "topics": [
        {
            "id": "cache-locality-data-oriented-design",
            "title": "Cache Locality & Data-Oriented Design vs OOP",
            "definition": "Data-Oriented Design (DOD) prioritizes the layout of data in hardware memory (L1/L2/L3 caches) to maximize cache hits, contrasting traditional OOP (Array of Structures - AoS) with Structure of Arrays (SoA).",
            "why_it_matters": "A cache miss can cost 200+ CPU cycles while an L1 cache hit takes only 4 cycles. High-performance game engines, quant trading, and database engines organize data layout to eliminate pointer indirection cache misses.",
            "real_world_analogy": "A grocery warehouse: if order pickers only need product weights, storing weights in one contiguous ledger allows fast scanning of 1,000 items in a single glance (SoA), rather than walking to 1,000 separate aisles to read each full product box (AoS).",
            "conceptual_breakdown": [
                "<strong>CPU Cache Lines:</strong> Memory is loaded in 64-byte chunks. Touching one byte loads the adjacent 63 bytes into L1 cache for free.",
                "<strong>Array of Structures (AoS):</strong> Classic OOP layout: <code>struct Particle { float x, y, z; int id; string name; }; vector<Particle></code>. Iterating over positions wastes cache bandwidth fetching unused names and IDs.",
                "<strong>Structure of Arrays (SoA):</strong> Data-Oriented layout: <code>struct ParticleSystem { vector<float> x, y, z; };</code>. SIMD auto-vectorization and pure contiguous cache line utilization.",
                "<strong>Pointer Chasing Penalty:</strong> Classic polymorphic OOP (<code>vector<unique_ptr<Base>></code>) scatters objects across the heap, causing L1 cache misses on almost every dereference."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "AoS vs SoA Memory Layout",
                "classes": [
                    {
                        "name": "ArrayOfStructures_AoS",
                        "is_abstract": False,
                        "attributes": ["[x0, y0, mass0, name0]", "[x1, y1, mass1, name1]", "[x2, y2, mass2, name2]"],
                        "methods": ["Low cache locality for position update (wastes bandwidth on names)"]
                    },
                    {
                        "name": "StructureOfArrays_SoA",
                        "is_abstract": False,
                        "attributes": ["X: [x0, x1, x2, x3, ...]", "Y: [y0, y1, y2, y3, ...]", "Mass: [m0, m1, m2, m3, ...]"],
                        "methods": ["100% Cache Line Utilization (Packed 64B SIMD ready)"]
                    }
                ],
                "relationships": []
            },
            "interactive_animation": {
                "title": "L1 Cache Line Traversal Simulation",
                "steps": [
                    {"step": 1, "description": "CPU fetches 64-byte Cache Line from RAM containing 16 contiguous float coordinates (SoA).", "active_nodes": ["RAM", "L3 Cache", "L1 Cache"]},
                    {"step": 2, "description": "SIMD AVX-512 register loads 16 floats in parallel and updates coordinates in 1 cycle.", "active_nodes": ["L1 Cache", "CPU AVX Register"]},
                    {"step": 3, "description": "In contrast, AoS pointer dereference incurs 200ns RAM stall on every object jump.", "active_nodes": ["RAM Stall (Cache Miss)"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <vector>
#include <chrono>
#include <numeric>

// 1. Traditional OOP (Array of Structures - AoS)
struct ParticleAoS {
    float x, y, z;
    float vx, vy, vz;
    int id;
    char name[32]; // Unused during physics update, clogs 64B cache line!
};

// 2. Data-Oriented Design (Structure of Arrays - SoA)
struct ParticleSystemSoA {
    std::vector<float> x;
    std::vector<float> y;
    std::vector<float> z;
    std::vector<float> vx;
    std::vector<float> vy;
    std::vector<float> vz;

    void resize(size_t n) {
        x.resize(n, 0.0f); y.resize(n, 0.0f); z.resize(n, 0.0f);
        vx.resize(n, 1.0f); vy.resize(n, 1.0f); vz.resize(n, 1.0f);
    }

    void updatePhysics(float dt) {
        // Contiguous memory access - compiler auto-vectorizes to AVX/SIMD!
        const size_t n = x.size();
        for (size_t i = 0; i < n; ++i) {
            x[i] += vx[i] * dt;
            y[i] += vy[i] * dt;
            z[i] += vz[i] * dt;
        }
    }
};

int main() {
    constexpr size_t N = 1'000'000;
    
    // SoA Benchmark
    ParticleSystemSoA soa;
    soa.resize(N);

    auto start = std::chrono::high_resolution_clock::now();
    for (int iter = 0; iter < 10; ++iter) {
        soa.updatePhysics(0.016f);
    }
    auto end = std::chrono::high_resolution_clock::now();
    
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
    std::cout << "[SoA Benchmark] 1,000,000 particles 10 physics ticks: " << duration << " us\\n";

    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. 64-Byte Cache Line Saturation:</strong> By storing <code>float x[]</code> sequentially, a single 64B cache line fetch delivers 16 sequential coordinates with zero wasted bytes.",
                "<strong>2. SIMD Auto-Vectorization:</strong> Modern compilers (GCC `-O3`, Clang, MSVC) transform the SoA loop into 512-bit vector registers processing 16 updates per clock.",
                "<strong>3. Elimination of Pointer Dereferencing:</strong> Contiguous vectors eliminate heap fragmentation and translation lookaside buffer (TLB) thrashing."
            ],
            "comparison_matrix": {
                "title": "AoS vs SoA Architectural Comparison",
                "headers": ["Metric", "OOP / AoS", "Data-Oriented / SoA"],
                "rows": [
                    ["Cache Line Density", "Low (contains cold data)", "100% Optimal (hot data packed)"],
                    ["SIMD Vectorization", "Difficult / Impossible", "Trivial and automatic"],
                    ["Ease of Domain Modeling", "High (mental match with objects)", "Moderate (tables of columns)"],
                    ["Performance on Bulk Updates", "Baseline (1x)", "5x - 20x Faster"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Using `std::vector<std::unique_ptr<Base>>` in high-frequency loops", "correction": "Use DOD data pools or contiguous arrays of concrete types to avoid pointer chasing."}
            ],
            "interview_traps": [
                "<strong>Trap: 'Should we always rewrite all OOP systems into SoA?'</strong><br><em>Answer:</em> No. Apply DOD to hot batch-processing loops (physics, graphics, matching engines, analytics); keep traditional OOP for high-level business entities and complex state machines."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor a polymorphic game entity update loop into a cache-friendly component data array.",
                "bad_code": "for (auto& entity : entities) entity->update(); // Virtual call + cache miss",
                "good_code": "physicsComponentArray.updateAll(); renderComponentArray.renderAll();"
            },
            "practice_problem": {
                "title": "Design Entity-Component-System (ECS) Storage",
                "description": "Implement a sparse-set ECS storage mechanism that maps Entity IDs to contiguous Component arrays in O(1) time.",
                "hint": "Use a sparse array `sparse[entityId] = denseIndex` and packed dense array `dense[denseIndex] = component`."
            }
        },
        {
            "id": "lock-free-spsc-queue",
            "title": "Lock-free SPSC Ring Buffer Design",
            "definition": "A Single-Producer Single-Consumer (SPSC) circular queue utilizing atomic head/tail indices and memory order fences (Acquire-Release) to achieve wait-free, zero-lock IPC and inter-thread messaging.",
            "why_it_matters": "Standard mutex-based queues incur kernel context switches (1-5 microseconds) and priority inversions. SPSC queues deliver nanosecond latency (sub-20ns) essential for high-frequency trading and real-time audio.",
            "real_world_analogy": "A conveyor belt sushi bar with 1 chef (Producer) placing dishes on empty rotating plates and 1 customer (Consumer) picking them up without ever stopping or speaking to each other.",
            "conceptual_breakdown": [
                "<strong>Circular Ring Buffer:</strong> Fixed-size array with power-of-two capacity for fast bitwise modulo: <code>index = pos & (capacity - 1)</code>.",
                "<strong>Atomic Indices:</strong> <code>std::atomic<size_t> head</code> (written only by Consumer) and <code>std::atomic<size_t> tail</code> (written only by Producer).",
                "<strong>Acquire-Release Memory Ordering:</strong> Producer uses <code>std::memory_order_release</code> on tail write; Consumer uses <code>std::memory_order_acquire</code> on tail read.",
                "<strong>False Sharing Prevention:</strong> <code>alignas(hardware_destructive_interference_size)</code> to keep head and tail on separate 64-byte cache lines."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "SPSC Lock-Free Ring Buffer",
                "classes": [
                    {
                        "name": "SPSCQueue<T, Capacity>",
                        "is_abstract": False,
                        "attributes": [
                            "- buffer: array<T, Capacity>",
                            "alignas(64) - tail: atomic<size_t>",
                            "alignas(64) - head: atomic<size_t>"
                        ],
                        "methods": [
                            "+ push(item: const T&): bool",
                            "+ pop(item: T&): bool",
                            "+ empty(): bool",
                            "+ full(): bool"
                        ]
                    }
                ],
                "relationships": []
            },
            "interactive_animation": {
                "title": "Lock-Free SPSC Push & Pop Stepping",
                "steps": [
                    {"step": 1, "description": "Producer checks (tail - head < Capacity). Buffer has free slot.", "active_nodes": ["Producer", "Tail"]},
                    {"step": 2, "description": "Producer writes item into buffer[tail & mask] with no locks.", "active_nodes": ["Buffer Slot"]},
                    {"step": 3, "description": "Producer increments tail with memory_order_release. Data is visible to Consumer.", "active_nodes": ["Tail Atomic"]},
                    {"step": 4, "description": "Consumer loads tail with memory_order_acquire, reads item, and advances head.", "active_nodes": ["Consumer", "Head Atomic"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <array>
#include <atomic>
#include <thread>
#include <cassert>
#include <new>

// Cache line size constant to prevent false sharing
#ifdef __cpp_lib_hardware_interference_size
    using std::hardware_destructive_interference_size;
#else
    constexpr size_t hardware_destructive_interference_size = 64;
#endif

template <typename T, size_t Capacity>
class LockFreeSPSCQueue {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of 2!");

private:
    std::array<T, Capacity> buffer;
    static constexpr size_t IndexMask = Capacity - 1;

    // Align to distinct cache lines to prevent false sharing cache ping-pong
    alignas(hardware_destructive_interference_size) std::atomic<size_t> tail{0}; // Written by Producer
    alignas(hardware_destructive_interference_size) std::atomic<size_t> head{0}; // Written by Consumer

public:
    LockFreeSPSCQueue() = default;

    bool push(const T& item) {
        const size_t currentTail = tail.load(std::memory_order_relaxed);
        const size_t currentHead = head.load(std::memory_order_acquire);

        if ((currentTail - currentHead) >= Capacity) {
            return false; // Queue full
        }

        buffer[currentTail & IndexMask] = item;
        tail.store(currentTail + 1, std::memory_order_release);
        return true;
    }

    bool pop(T& item) {
        const size_t currentHead = head.load(std::memory_order_relaxed);
        const size_t currentTail = tail.load(std::memory_order_acquire);

        if (currentHead == currentTail) {
            return false; // Queue empty
        }

        item = buffer[currentHead & IndexMask];
        head.store(currentHead + 1, std::memory_order_release);
        return true;
    }
};

int main() {
    LockFreeSPSCQueue<int, 1024> queue;
    constexpr int TotalMessages = 100'000;

    std::thread producer([&]() {
        for (int i = 0; i < TotalMessages; ++i) {
            while (!queue.push(i)) {
                std::this_thread::yield(); // Backoff when full
            }
        }
    });

    std::thread consumer([&]() {
        int received = 0;
        int val;
        while (received < TotalMessages) {
            if (queue.pop(val)) {
                assert(val == received);
                received++;
            } else {
                std::this_thread::yield(); // Backoff when empty
            }
        }
    });

    producer.join();
    consumer.join();

    std::cout << "[SUCCESS] Processed " << TotalMessages << " messages through Lock-Free SPSC Ring Buffer with zero mutexes!\\n";
    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. False Sharing Elimination:</strong> <code>alignas(64)</code> places <code>head</code> and <code>tail</code> into separate cache lines, eliminating core-to-core cache line bouncing.",
                "<strong>2. Acquire-Release Semantics:</strong> <code>std::memory_order_release</code> on tail publish guarantees all written item bytes in the array are committed before the index increment is observed by the consumer.",
                "<strong>3. Bitwise Fast Modulo:</strong> Power of 2 constraint allows <code>tail & (Capacity - 1)</code> instead of expensive integer division instructions."
            ],
            "comparison_matrix": {
                "title": "Queue Performance Comparison",
                "headers": ["Type", "Latency per Operation", "Contention Model", "Thread Scaling"],
                "rows": [
                    ["std::mutex + std::queue", "1,000 - 5,000 ns (Context switch)", "Blocking / Lock contention", "Degrades with cores"],
                    ["Spinlock Queue", "100 - 300 ns", "Busy-wait CPU burning", "High CPU load"],
                    ["Lock-Free SPSC", "5 - 15 ns", "Wait-free / Lock-free", "Zero contention (1P - 1C)"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Omitting `alignas(64)` on head and tail", "correction": "Causes false sharing, degrading throughput by up to 80% due to cache line invalidation between CPU cores."},
                {"mistake": "Using `std::memory_order_relaxed` for publication", "correction": "Allows CPU out-of-order execution to publish the tail index BEFORE the array data is written, resulting in uninitialized data reads."}
            ],
            "interview_traps": [
                "<strong>Trap: 'Can this SPSC queue be used safely with 2 Producers and 1 Consumer?'</strong><br><em>Answer:</em> Absolutely not. SPSC assumes single-writer per index. Multiple producers require MPMC queues using `atomic::compare_exchange_weak` and sequence numbers (e.g. Dmitry Vyukov's MPMC queue)."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor a mutex-guarded audio playback buffer into a lock-free SPSC ring buffer to prevent audio stutter glitches.",
                "bad_code": "std::lock_guard<std::mutex> lock(audioMtx); queue.push(sample);",
                "good_code": "spscQueue.push(sample); // Real-time safe, never blocks audio thread"
            },
            "practice_problem": {
                "title": "Design Batch-Push SPSC Queue",
                "description": "Implement `push_batch(const T* data, size_t count)` that writes multiple elements under a single atomic tail update.",
                "hint": "Check available capacity once: `(Capacity - (tail - head)) >= count`, write range, then store `tail + count`."
            }
        },
        {
            "id": "zero-copy-buffer-abstractions",
            "title": "Zero-Copy Buffer Abstractions",
            "definition": "Designing network and file I/O abstractions (`std::string_view`, `std::span`, scatter-gather I/O) that inspect and slice data without copying bytes across user and kernel memory spaces.",
            "why_it_matters": "Copying memory is CPU-intensive. At 100 Gbps network speeds, traditional `std::string` copies will saturate memory bus bandwidth. Zero-copy abstractions enable line-rate network packet processing.",
            "real_world_analogy": "Highlighting a sentence in a physical library book and passing the page coordinates (Page 42, Line 10) to a colleague, rather than hand-copying the entire 500-page book onto new sheets of paper.",
            "conceptual_breakdown": [
                "<strong>std::string_view & std::span (C++20):</strong> Non-owning reference views over contiguous memory slices consisting of just a pointer and a size.",
                "<strong>Scatter-Gather I/O (vectored I/O):</strong> <code>writev</code> and <code>readv</code> allow sending multiple non-contiguous memory buffers in a single system call.",
                "<strong>Ring Buffer Slicing:</strong> Passing pointer offsets into existing packet receive buffers directly to parsers.",
                "<strong>Ownership Boundaries:</strong> Ensuring source memory buffer lifetime outlives all referencing views."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Zero-Copy View vs Deep Copy",
                "classes": [
                    {
                        "name": "DeepCopy_Approach",
                        "is_abstract": False,
                        "attributes": ["Packet Buffer (1500B)", "std::string header = substr(0, 20)", "std::string payload = substr(20, 1480)"],
                        "methods": ["2 Heap Allocations + 1500B memcpy"]
                    },
                    {
                        "name": "ZeroCopy_std_span_Approach",
                        "is_abstract": False,
                        "attributes": ["Packet Buffer (1500B)", "string_view header(&buf[0], 20)", "span<uint8_t> payload(&buf[20], 1480)"],
                        "methods": ["0 Allocations, 0 memcpy, O(1) slicing"]
                    }
                ],
                "relationships": []
            },
            "interactive_animation": {
                "title": "Zero-Copy Network Packet Parsing",
                "steps": [
                    {"step": 1, "description": "NIC transfers 1500B Ethernet frame directly into DMA Ring Buffer.", "active_nodes": ["NIC", "DMA Buffer"]},
                    {"step": 2, "description": "Parser creates zero-copy std::span views for IP Header and TCP Payload without copying.", "active_nodes": ["Parser", "std::span View"]},
                    {"step": 3, "description": "Application processes payload directly in DMA memory. Latency is minimized.", "active_nodes": ["Application Engine"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <span>
#include <string_view>
#include <vector>
#include <cstdint>

// Protocol Header (POD struct)
#pragma pack(push, 1)
struct PacketHeader {
    uint16_t magic;
    uint16_t messageType;
    uint32_t payloadLength;
};
#pragma pack(pop)

class ZeroCopyPacketParser {
public:
    // Pure zero-copy parser taking contiguous byte span
    static void processFrame(std::span<const uint8_t> rawFrame) {
        if (rawFrame.size() < sizeof(PacketHeader)) {
            std::cout << "[ERROR] Corrupt frame: smaller than header size\\n";
            return;
        }

        // 1. Direct reinterpret view of header without copying
        const auto* header = reinterpret_cast<const PacketHeader*>(rawFrame.data());
        
        std::cout << "[ZERO-COPY PARSER] Header -> Magic: 0x" << std::hex << header->magic 
                  << ", MsgType: " << std::dec << header->messageType 
                  << ", PayloadLen: " << header->payloadLength << " bytes\\n";

        // 2. Create sub-span for payload (Zero-copy slice)
        std::span<const uint8_t> payload = rawFrame.subspan(sizeof(PacketHeader), header->payloadLength);

        // 3. Zero-copy string_view over ASCII payload section
        std::string_view textPayload(reinterpret_cast<const char*>(payload.data()), payload.size());
        std::cout << "  Payload Content View: \\"" << textPayload << "\\" (Allocations: 0)\\n";
    }
};

int main() {
    // Simulated Network Buffer received from OS socket / NIC ring
    std::vector<uint8_t> networkBuffer;
    
    PacketHeader hdr{0xABCD, 42, 11}; // Magic, Type=42, 11 bytes "Hello C++20"
    const uint8_t* hdrBytes = reinterpret_cast<const uint8_t*>(&hdr);
    networkBuffer.insert(networkBuffer.end(), hdrBytes, hdrBytes + sizeof(PacketHeader));
    
    std::string_view msg = "Hello C++20";
    networkBuffer.insert(networkBuffer.end(), msg.begin(), msg.end());

    // Execute zero-copy parsing
    ZeroCopyPacketParser::processFrame(networkBuffer);

    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. std::span Contiguous Memory View:</strong> <code>std::span<const uint8_t></code> represents any contiguous buffer (vector, raw array, memory-mapped file) without owning or copying it.",
                "<strong>2. Subspan Zero-Copy Slicing:</strong> <code>rawFrame.subspan()</code> performs an $O(1)$ offset calculation rather than copying bytes into a new container.",
                "<strong>3. Reinterpretation of Network Structs:</strong> Uses `#pragma pack` and pointer reinterpretation to read binary headers directly from wire buffers."
            ],
            "comparison_matrix": {
                "title": "Buffer Abstraction Trade-offs",
                "headers": ["Type", "Ownership", "Allocation Cost", "Dangling Pointer Risk"],
                "rows": [
                    ["std::string / std::vector", "Owns data (Deep copy)", "Heap allocation (unless SSO)", "None (Safe)"],
                    ["std::string_view", "Non-owning reference", "Zero allocation (16 bytes)", "Yes (if source is destroyed)"],
                    ["std::span<T>", "Non-owning mutable/const view", "Zero allocation (16 bytes)", "Yes (if buffer invalidated)"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Returning a `std::string_view` to a temporary local `std::string`", "correction": "The temporary string is destroyed at the end of the statement, creating a catastrophic dangling pointer."}
            ],
            "interview_traps": [
                "<strong>Trap: 'What is the danger of `reinterpret_cast` for zero-copy parsing across different CPU architectures?'</strong><br><em>Answer:</em> Endianness differences (Big-endian network order vs Little-endian x86) and unaligned memory access faults on ARM architectures. Use `ntohs`/`ntohl` or `std::endian` checks."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor a function taking `const std::string&` that uses `s.substr()` inside a loop.",
                "bad_code": "void parse(const string& s) { auto sub = s.substr(0, 10); } // Heap copy every slice",
                "good_code": "void parse(string_view s) { auto sub = s.substr(0, 10); } // O(1) pointer slice"
            },
            "practice_problem": {
                "title": "Design Scatter-Gather Chunk Buffer",
                "description": "Implement a `ChunkedBuffer` that chains multiple 4KB zero-copy memory blocks and exposes a unified `read_view(offset, len)` interface.",
                "hint": "Store a `std::vector<std::span<uint8_t>>`."
            }
        }
    ]
}

# Module 21: 14-Step LLD Interview Framework
m21 = {
    "module_id": "21",
    "module_title": "14-Step LLD Interview Framework",
    "description": "Master the repeatable 14-step battle-tested interview roadmap from requirement gathering to clean C++ code.",
    "topics": [
        {
            "id": "the-14-step-interview-process",
            "title": "The 14-Step Systematic Interview Roadmap",
            "definition": "A battle-tested, structured 45-minute execution blueprint designed to navigate any ambiguous Low-Level Design interview smoothly from problem definition to working modern C++ code.",
            "why_it_matters": "80% of candidates fail LLD interviews not due to bad code, but due to jumping straight to coding before clarifying scope, missing edge cases, and producing rigid, untestable designs.",
            "real_world_analogy": "An architectural construction process: no builder pours concrete without blueprints, client approval, load-bearing calculations, and plumbing schematics.",
            "conceptual_breakdown": [
                "<strong>Phase 1: Clarification & Scope (0-8 min):</strong> Steps 1-4: Functional, Non-Functional, Use Cases, Scale.",
                "<strong>Phase 2: Domain Modeling & OOP Design (8-20 min):</strong> Steps 5-8: Core Entities, Relationships, UML Class & Sequence Diagrams.",
                "<strong>Phase 3: Design Patterns & Architecture (20-28 min):</strong> Step 9: Pattern Selection (Strategy, Observer, State, Factory).",
                "<strong>Phase 4: Idiomatic C++ Coding (28-40 min):</strong> Steps 10-12: Header definitions, Thread Safety, Error Handling.",
                "<strong>Phase 5: Defense & Verification (40-45 min):</strong> Steps 13-14: Concurrency edge cases, Extensibility walkthrough."
            ],
            "visual_diagram": {
                "type": "sequence_diagram",
                "title": "45-Minute Interview Timeline",
                "classes": [
                    {"name": "Candidate", "is_abstract": False, "attributes": [], "methods": []},
                    {"name": "Interviewer", "is_abstract": False, "attributes": [], "methods": []}
                ],
                "relationships": [
                    {"from": "Candidate", "to": "Interviewer", "type": "association", "label": "1. Clarify Scope & Constraints (0-8 min)"},
                    {"from": "Candidate", "to": "Interviewer", "type": "association", "label": "2. Propose Entities & UML (8-20 min)"},
                    {"from": "Candidate", "to": "Interviewer", "type": "association", "label": "3. Agree on Patterns & Concurrency (20-28 min)"},
                    {"from": "Candidate", "to": "Interviewer", "type": "association", "label": "4. Write Modern C++ Code (28-40 min)"},
                    {"from": "Candidate", "to": "Interviewer", "type": "association", "label": "5. Walkthrough Edge Cases & Tests (40-45 min)"}
                ]
            },
            "interactive_animation": {
                "title": "14-Step Framework Progression",
                "steps": [
                    {"step": 1, "description": "Step 1-4: Gather requirements. Clarify constraints (e.g. multi-threading, scale, out of scope).", "active_nodes": ["Phase 1: Scope"]},
                    {"step": 2, "description": "Step 5-8: Identify Entities. Draw UML Class Diagram with clear Association vs Composition.", "active_nodes": ["Phase 2: Modeling"]},
                    {"step": 3, "description": "Step 9: Choose Design Patterns (e.g. Strategy for algorithms, State for lifecycles).", "active_nodes": ["Phase 3: Patterns"]},
                    {"step": 4, "description": "Step 10-12: Write production-grade C++20 code with smart pointers and RAII.", "active_nodes": ["Phase 4: Coding"]},
                    {"step": 5, "description": "Step 13-14: Walk through concurrency, exception safety, and unit testing.", "active_nodes": ["Phase 5: Defense"]}
                ]
            },
            "cpp_implementation": """// Complete Interview Checklist Skeleton in C++
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <mutex>
#include <optional>

// Step 1-4: Clear Domain Entities with explicit contracts
enum class OrderStatus { CREATED, PAID, FULFILLED, CANCELLED };

// Step 5-8: Value Objects and Entities
struct Money {
    int64_t cents{0};
};

// Step 9: Strategy Pattern for Extensibility
class IPaymentProcessor {
public:
    virtual ~IPaymentProcessor() = default;
    virtual bool process(Money amount) = 0;
};

class StripeProcessor : public IPaymentProcessor {
public:
    bool process(Money amount) override {
        std::cout << "[STRIPE] Processed $" << (amount.cents / 100.0) << "\\n";
        return true;
    }
};

// Step 10-12: Thread-Safe Facade Service
class OrderService {
private:
    std::unique_ptr<IPaymentProcessor> paymentProcessor;
    std::mutex serviceMtx;

public:
    explicit OrderService(std::unique_ptr<IPaymentProcessor> processor)
        : paymentProcessor(std::move(processor)) {}

    bool checkoutOrder(int orderId, Money total) {
        std::lock_guard<std::mutex> lock(serviceMtx);
        std::cout << "[ORDER " << orderId << "] Starting checkout...\\n";
        return paymentProcessor->process(total);
    }
};

int main() {
    auto orderService = std::make_unique<OrderService>(std::make_unique<StripeProcessor>());
    orderService->checkoutOrder(101, Money{4999}); // $49.99
    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Explicit Time Management:</strong> Dedicate no more than 8 minutes to scoping so at least 15 minutes remain for live coding.",
                "<strong>2. Top-Down Verbal Alignment:</strong> Always validate entity choices and diagram relationships with the interviewer before writing code.",
                "<strong>3. Modern C++ Best Practices:</strong> Demonstrate ownership semantics (`std::unique_ptr`, `std::shared_ptr`), RAII, and `std::mutex` discipline."
            ],
            "comparison_matrix": {
                "title": "Interview Approaches",
                "headers": ["Aspect", "Ad-Hoc Coding Candidate", "14-Step Framework Candidate"],
                "rows": [
                    ["Requirement Scope", "Starts coding immediately, misses key limits", "Clarifies boundary, scale, and out-of-scope"],
                    ["Extensibility", "Tightly coupled classes with hardcoded switches", "Modular Strategy & Factory pattern interfaces"],
                    ["Thread Safety", "Forgotten or added as crude global lock", "Clean per-entity or lock-free concurrency design"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Silently thinking and coding for 20 minutes without speaking", "correction": "Think out loud continuously. Treat the interview as a collaborative design review with a senior colleague."}
            ],
            "interview_traps": [
                "<strong>Trap: 'The candidate finishes coding in 15 minutes with a monolithic 300-line main() function.'</strong><br><em>Answer:</em> Instant rejection. LLD interviews evaluate modularity, encapsulation, interface segregation, and design patterns, not fast scripting."
            ],
            "code_refactor_exercise": {
                "problem": "Identify the missing steps in an interview submission that jumps directly from problem prompt to raw C++ structs.",
                "bad_code": "struct ParkingLot { int spots[100]; }; // No interface, no strategies, no tests",
                "good_code": "Establish IParkingStrategy, Vehicle hierarchies, and thread synchronization."
            },
            "practice_problem": {
                "title": "Timeboxed 30-Minute Mock Interview",
                "description": "Apply the 14-step framework to design an In-Memory File System within a strict 30-minute timer.",
                "hint": "Spend: 5m Clarify, 8m UML, 12m Code, 5m Concurrency & Verification."
            }
        },
        {
            "id": "clarifying-functional-and-non-functional",
            "title": "Step 1-4: Clarification & Domain Decomposition",
            "definition": "Techniques for asking probing questions to define precise system boundaries, distinguish functional from non-functional requirements, and establish entity vocabularies.",
            "why_it_matters": "Real-world engineering problems are inherently ambiguous. Demonstrating that you know which clarifying questions to ask proves senior-level engineering maturity.",
            "real_world_analogy": "A doctor conducting patient intake: before prescribing surgery, they gather medical history, check allergies, and evaluate vital signs.",
            "conceptual_breakdown": [
                "<strong>Functional Requirements (FR):</strong> What the system MUST do (e.g. Park vehicle, dispense ticket, calculate fee).",
                "<strong>Non-Functional Requirements (NFR):</strong> Performance, Concurrency, Latency, Extensibility, Thread-safety.",
                "<strong>Out of Scope:</strong> Explicitly agreeing on features NOT to build (e.g. Physical hardware drivers, web UI, database migrations).",
                "<strong>Scale & Constraints:</strong> Single machine in-memory vs distributed, QPS, memory footprint."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Requirements Clarification Matrix",
                "classes": [
                    {
                        "name": "FunctionalRequirements_FR",
                        "is_abstract": False,
                        "attributes": ["1. Park/Unpark Vehicle", "2. Dynamic Spot Search", "3. Multiple Vehicle Types", "4. Hourly Billing Calculation"],
                        "methods": []
                    },
                    {
                        "name": "NonFunctionalRequirements_NFR",
                        "is_abstract": False,
                        "attributes": ["1. Thread-safe entry/exit", "2. Low Latency (< 10ms)", "3. Extensible fee rules", "4. In-Memory persistence"],
                        "methods": []
                    }
                ],
                "relationships": []
            },
            "interactive_animation": {
                "title": "Clarification Dialog Flow",
                "steps": [
                    {"step": 1, "description": "Candidate asks: 'Should we support multiple entrance gates operating simultaneously?'", "active_nodes": ["Candidate"]},
                    {"step": 2, "description": "Interviewer confirms: 'Yes, assume 4 gates concurrently parking cars.'", "active_nodes": ["Interviewer"]},
                    {"step": 3, "description": "Candidate notes: 'Adding thread-safety (NFR) via fine-grained spot mutexes.'", "active_nodes": ["Candidate", "NFR Board"]}
                ]
            },
            "cpp_implementation": """// Demonstrating Domain Decomposition via C++ Strongly-Typed Domain Primitives
#include <iostream>
#include <string>
#include <chrono>

// Explicit Value Objects representing clarified constraints
struct VehicleDetails {
    std::string licensePlate;
    int weightKg;
};

// Strongly-typed ID to prevent primitive obsession
struct GateId {
    int value;
};

struct TicketId {
    std::string value;
};

class ClarifiedParkingDomain {
public:
    static void printClarifiedScope() {
        std::cout << "=== Clarified Scope Summary ===\\n"
                  << "1. Target: Multi-gate, in-memory thread-safe parking engine\\n"
                  << "2. Vehicles: Motorcycle, Sedan, Electric SUV\\n"
                  << "3. Constraints: Mutex-guarded spot reservation, O(1) spot lookup\\n"
                  << "4. Out of Scope: Payment gateway network integration\\n";
    }
};

int main() {
    ClarifiedParkingDomain::printClarifiedScope();
    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Define What is IN and OUT of Scope:</strong> Prevents scope creep and ensures alignment within the first 5 minutes.",
                "<strong>2. Identify Core Actions & Actors:</strong> Formulate use cases as: Actor -> Action -> System Result.",
                "<strong>3. Establish Strong Domain Types:</strong> Use custom structs instead of raw `int` or `string` for IDs."
            ],
            "comparison_matrix": {
                "title": "Requirement Scoping Techniques",
                "headers": ["Question Type", "Weak Question", "Strong Senior Question"],
                "rows": [
                    ["Concurrency", "'Is it multi-threaded?'", "'Will multiple entrance gates park vehicles concurrently, and what is the expected write contention rate?'"],
                    ["Pricing", "'How much does it cost?'", "'Should pricing be extensible to support dynamic peak-hour surges or EV kilowatt-hour billing via a Strategy pattern?'"],
                    ["Persistence", "'Do we need a database?'", "'Should we design this as a pure in-memory domain model with repository interfaces for future persistence?'"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Assuming single-threaded execution without asking the interviewer", "correction": "Always clarify concurrency requirements upfront."}
            ],
            "interview_traps": [
                "<strong>Trap: 'Candidate asks 25 questions and uses up 18 minutes of a 45-minute interview.'</strong><br><em>Answer:</em> Limit initial clarification to 4-5 high-impact questions; state reasonable assumptions for the rest and confirm them."
            ],
            "code_refactor_exercise": {
                "problem": "Convert ambiguous primitive arguments into explicit domain value objects.",
                "bad_code": "void book(int a, string b, double c);",
                "good_code": "void book(SeatId seat, UserId user, Price amount);"
            },
            "practice_problem": {
                "title": "Formulate 5 Core Clarifying Questions for a Hotel Booking System",
                "description": "Write down the 5 essential functional and non-functional questions you would ask before designing a Hotel Reservation engine.",
                "hint": "Cover room types, multi-room party reservations, cancellation policies, overbooking tolerance, and concurrent booking locks."
            }
        },
        {
            "id": "designing-clean-diagrams-live",
            "title": "Step 5-9: Drawing Class & Sequence Diagrams Live",
            "definition": "Visualizing domain models rapidly using standard UML class notations (attributes, methods, visibility), relationships (Inheritance, Composition, Aggregation, Association), and interaction sequence diagrams.",
            "why_it_matters": "A clear UML diagram allows the interviewer to spot architectural flaws in 30 seconds before a single line of C++ code is written, saving 20 minutes of costly code refactoring.",
            "real_world_analogy": "An electrical schematic: symbols clearly indicate resistors, capacitors, and power lines before fabricating the physical circuit board.",
            "conceptual_breakdown": [
                "<strong>UML Class Notation:</strong> Class name, attributes with visibility (`-` private, `+` public, `#` protected), methods.",
                "<strong>Relationship Symbols:</strong> Composition (filled diamond - lifetime bound), Aggregation (hollow diamond - shared pointer), Inheritance (hollow triangle).",
                "<strong>Sequence Diagrams:</strong> Lifeline columns, synchronous calls, asynchronous events, return arrows.",
                "<strong>Design Pattern Integration:</strong> Annotating interfaces with `<<interface>>` and strategy links."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Live UML Class Diagram Template",
                "classes": [
                    {
                        "name": "IBillingStrategy",
                        "is_abstract": True,
                        "attributes": [],
                        "methods": ["+ calculate(duration: int): double"]
                    },
                    {
                        "name": "HourlyBilling",
                        "is_abstract": False,
                        "attributes": ["- ratePerHour: double"],
                        "methods": ["+ calculate(duration: int): double"]
                    },
                    {
                        "name": "ParkingService",
                        "is_abstract": False,
                        "attributes": ["- billing: unique_ptr<IBillingStrategy>", "- spots: vector<shared_ptr<Spot>>"],
                        "methods": ["+ park(): Ticket", "+ unpark(t: Ticket): double"]
                    }
                ],
                "relationships": [
                    {"from": "HourlyBilling", "to": "IBillingStrategy", "type": "inheritance", "label": "implements"},
                    {"from": "ParkingService", "to": "IBillingStrategy", "type": "composition", "label": "uses strategy"}
                ]
            },
            "interactive_animation": {
                "title": "UML Synthesis Flow",
                "steps": [
                    {"step": 1, "description": "Candidate identifies entities: Room, Booking, Guest, PricingStrategy.", "active_nodes": ["Entities"]},
                    {"step": 2, "description": "Draws Composition: Booking OWNS Guest details. Hotel OWNS Rooms.", "active_nodes": ["Composition Links"]},
                    {"step": 3, "description": "Draws Strategy Interface for dynamic pricing.", "active_nodes": ["Strategy Interface"]},
                    {"step": 4, "description": "Interviewer reviews and approves architecture. Candidate transitions to coding.", "active_nodes": ["Approval"]}
                ]
            },
            "cpp_implementation": """// UML to C++ Code Translation Template
#include <iostream>
#include <memory>
#include <vector>

// <<interface>> IBillingStrategy
class IBillingStrategy {
public:
    virtual ~IBillingStrategy() = default;
    virtual double calculate(int hours) const = 0;
};

// Concrete Strategy
class HourlyBilling : public IBillingStrategy {
private:
    double rate;
public:
    explicit HourlyBilling(double r) : rate(r) {}
    double calculate(int hours) const override { return hours * rate; }
};

// Context Class with Composition
class ParkingService {
private:
    std::unique_ptr<IBillingStrategy> strategy;

public:
    explicit ParkingService(std::unique_ptr<IBillingStrategy> s) : strategy(std::move(s)) {}

    void process(int hours) {
        std::cout << "Computed Billing: $" << strategy->calculate(hours) << "\\n";
    }
};

int main() {
    ParkingService service(std::make_unique<HourlyBilling>(10.0));
    service.process(3); // $30.00
    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Translating Composition to C++:</strong> Use <code>std::unique_ptr<T></code> or direct value member variables for strong lifecycle ownership.",
                "<strong>2. Translating Aggregation to C++:</strong> Use <code>std::shared_ptr<T></code> or <code>std::weak_ptr<T></code> for shared or non-owning references.",
                "<strong>3. Abstract Interfaces:</strong> Use pure virtual classes with <code>virtual ~Class() = default;</code>."
            ],
            "comparison_matrix": {
                "title": "Diagramming Fidelity in Interviews",
                "headers": ["Format", "Speed", "Clarity", "Interviewer Feedback"],
                "rows": [
                    ["ASCII / Text UML", "Fastest", "Good", "Easy to review on web whiteboard"],
                    ["Formal UML Tool", "Slow", "Very High", "Can waste valuable coding time"],
                    ["No Diagram (Direct to Code)", "Risky", "Low", "High chance of major mid-interview rewrites"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Confusing Association, Aggregation, and Composition in UML", "correction": "Composition = exclusive ownership (delete parent destroys child); Aggregation = shared reference (child can exist independently)."}
            ],
            "interview_traps": [
                "<strong>Trap: 'Why did you choose an inheritance hierarchy for SpotType instead of an enum attribute?'</strong><br><em>Answer:</em> Explain polymorphism trade-offs: if spots have unique behavior (e.g. EV spots need metering telemetry), use inheritance; if they only differ by dimensions, an enum attribute is simpler and cleaner."
            ],
            "code_refactor_exercise": {
                "problem": "Convert a messy circular pointer dependency in UML into a clean mediator or observer design.",
                "bad_code": "Class A owns B, Class B owns A (shared_ptr cycle)",
                "good_code": "Class B holds weak_ptr to A or uses Observer callback."
            },
            "practice_problem": {
                "title": "Draw UML Diagram for an Amazon Locker System",
                "description": "Design the class diagram for Amazon Locker: LockerSize, LockerSlot, Package, DeliveryCode, and LockerHub.",
                "hint": "LockerHub has Composition of LockerSlots; LockerSlot has Aggregation (0..1) of Package."
            }
        },
        {
            "id": "writing-idiomatic-cpp-live",
            "title": "Step 10-14: Live C++ Coding & Concurrency Defense",
            "definition": "Executing the live coding phase cleanly using modern C++20 idioms: RAII, smart pointer ownership, const-correctness, thread safety guarantees, and defending design choices against edge cases.",
            "why_it_matters": "The final test of execution. Writing clean, compiling, idiomatic C++ with zero memory leaks and proper lock scopes differentiates top-tier candidates from average ones.",
            "real_world_analogy": "A master craftsman assembling precision watch gears: every piece fits snugly, springs have exact tension, and lubrication ensures frictionless movement under high load.",
            "conceptual_breakdown": [
                "<strong>Modern C++20 Ownership:</strong> <code>unique_ptr</code> (sole ownership), <code>shared_ptr</code> (shared), <code>std::weak_ptr</code> (cache/observers).",
                "<strong>RAII Concurrency:</strong> <code>std::lock_guard</code>, <code>std::unique_lock</code>, <code>std::shared_lock</code> (Reader-Writer).",
                "<strong>Const-Correctness & nodiscard:</strong> Mark accessors <code>[[nodiscard]] const noexcept</code>.",
                "<strong>Exception Safety:</strong> Strong vs Basic guarantee; avoid throwing in destructors.",
                "<strong>Extensibility Defense:</strong> Walk the interviewer through how a new feature can be added with ZERO modifications to existing classes (OCP)."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Idiomatic C++20 Production Class Template",
                "classes": [
                    {
                        "name": "ProductionClass",
                        "is_abstract": False,
                        "attributes": [
                            "- data: std::vector<std::string>",
                            "- mtx: mutable std::shared_mutex"
                        ],
                        "methods": [
                            "+ [[nodiscard]] std::optional<string> get(id: int) const",
                            "+ void insert(value: string)",
                            "+ ProductionClass(const ProductionClass&) = delete"
                        ]
                    }
                ],
                "relationships": []
            },
            "interactive_animation": {
                "title": "Live Coding & Defense Step-Through",
                "steps": [
                    {"step": 1, "description": "Candidate writes clean header declarations with nodiscard and smart pointers.", "active_nodes": ["Header Declarations"]},
                    {"step": 2, "description": "Applies std::lock_guard to critical sections protecting state invariants.", "active_nodes": ["Thread Safety RAII"]},
                    {"step": 3, "description": "Interviewer asks: 'How do you add PayPal support tomorrow?' Candidate explains OCP via IPaymentProcessor.", "active_nodes": ["OCP Defense"]},
                    {"step": 4, "description": "Interviewer asks: 'What happens during sudden thread cancellation?' Candidate highlights RAII lock unwinding.", "active_nodes": ["Exception Safety"]}
                ]
            },
            "cpp_implementation": """// Golden Production-Grade C++20 Reference Template for LLD Interviews
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <shared_mutex>
#include <optional>
#include <concepts>

// 1. C++20 Concept constraint for extensible items
template <typename T>
concept Validatable = requires(T a) {
    { a.isValid() } -> std::convertible_to<bool>;
};

struct Resource {
    int id;
    std::string name;
    [[nodiscard]] bool isValid() const noexcept { return id > 0 && !name.empty(); }
};

// 2. Thread-Safe Production Repository Pattern
class ThreadSafeResourceManager {
private:
    std::vector<Resource> resources;
    mutable std::shared_mutex rwMtx;

public:
    ThreadSafeResourceManager() = default;

    // Rule of 5: Disallow accidental slicing or multi-threaded copy bugs
    ThreadSafeResourceManager(const ThreadSafeResourceManager&) = delete;
    ThreadSafeResourceManager& operator=(const ThreadSafeResourceManager&) = delete;
    ThreadSafeResourceManager(ThreadSafeResourceManager&&) noexcept = default;
    ThreadSafeResourceManager& operator=(ThreadSafeResourceManager&&) noexcept = default;

    // Concurrent Reader (Shared Lock)
    [[nodiscard]] std::optional<Resource> findById(int id) const {
        std::shared_lock<std::shared_mutex> lock(rwMtx);
        for (const auto& res : resources) {
            if (res.id == id) return res;
        }
        return std::nullopt;
    }

    // Exclusive Writer (Unique Lock)
    bool addResource(Resource res) {
        if (!res.isValid()) return false;

        std::unique_lock<std::shared_mutex> lock(rwMtx);
        resources.push_back(std::move(res));
        return true;
    }

    [[nodiscard]] size_t size() const noexcept {
        std::shared_lock<std::shared_mutex> lock(rwMtx);
        return resources.size();
    }
};

int main() {
    ThreadSafeResourceManager manager;
    manager.addResource({1, "DatabaseConnectionPool"});
    manager.addResource({2, "KafkaConsumerGroup"});

    auto res = manager.findById(1);
    if (res) {
        std::cout << "[FOUND] Resource: " << res->name << "\\n";
    }

    std::cout << "[SUCCESS] Total Managed Resources: " << manager.size() << "\\n";
    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Modern Rule of 5 Discipline:</strong> Explicitly deleting copy constructors prevents accidental mutex copy or object slicing.",
                "<strong>2. Reader-Writer Lock Optimization:</strong> <code>std::shared_lock</code> allows 1,000 threads to read concurrently without contention.",
                "<strong>3. Value Semantics and Move Semantics:</strong> Passing by value and moving with <code>std::move()</code> achieves optimal performance for both rvalues and lvalues.",
                "<strong>4. Clean Optional Return Types:</strong> <code>std::optional<T></code> clearly communicates potential absence of data without using magic null pointers."
            ],
            "comparison_matrix": {
                "title": "Interview Code Quality Rubric",
                "headers": ["Criterion", "Beginner Code", "Senior C++20 Candidate Code"],
                "rows": [
                    ["Memory Management", "Raw `new` and `delete`", "RAII (`std::unique_ptr`, `std::make_shared`)"],
                    ["Null Handling", "Returning raw `nullptr` or -1", "`std::optional<T>` or `std::expected<T, Error>`"],
                    ["Concurrency", "Bare `mutex.lock()` (leak on throw)", "`std::lock_guard` / `std::scoped_lock`"],
                    ["Const Correctness", "No `const` methods", "`[[nodiscard]] const noexcept` throughout"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Writing `new` without a matching `delete` in interview whiteboard code", "correction": "Never use raw `new` in modern C++. Use `std::make_unique` or `std::make_shared`."},
                {"mistake": "Unlocking mutex manually at end of function instead of using RAII lock guards", "correction": "If an exception throws or early return triggers, manual unlock is skipped causing permanent deadlock."}
            ],
            "interview_traps": [
                "<strong>Trap: 'Why did you use std::lock_guard instead of std::unique_lock?'</strong><br><em>Answer:</em> `std::lock_guard` is lighter with zero runtime overhead when you don't need manual unlocking, deferring, or condition variables; use `std::unique_lock` when pairing with `std::condition_variable`."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor legacy C++ code with raw pointers and manual mutex locks into modern idiomatic C++20.",
                "bad_code": "Resource* r = new Resource(); mtx.lock(); list.push_back(r); mtx.unlock();",
                "good_code": "std::lock_guard<std::mutex> lock(mtx); list.push_back(std::make_unique<Resource>());"
            },
            "practice_problem": {
                "title": "Implement Thread-Safe Bounded Stack",
                "description": "Write a complete `ThreadSafeBoundedStack<T, Capacity>` using `std::mutex`, `std::condition_variable`, and `std::optional<T>`.",
                "hint": "Block `push` when full; block `pop` when empty."
            }
        }
    ]
}

# Module 22: Interactive LLD Practice Sandbox
m22 = {
    "module_id": "22",
    "module_title": "Interactive LLD Practice Sandbox",
    "description": "Design-This-Yourself interactive challenges with hidden entity checklists, diagrams, and reference C++ solutions.",
    "topics": [
        {
            "id": "practice-tic-tac-toe",
            "title": "Practice 1: Tic-Tac-Toe Game Engine",
            "definition": "An interactive $N \\times N$ multiplayer Tic-Tac-Toe game engine supporting customizable board sizes, arbitrary winning streak rules ($K$ in a row), Undo/Redo moves via Command Pattern, and AI bot players.",
            "why_it_matters": "Frequent warm-up LLD question at Microsoft and Amazon. Tests grid representations, win-checking algorithms in $O(1)$ time, and extensible player strategies.",
            "real_world_analogy": "Classic paper-and-pencil game generalized to an $N$-dimensional tournament board with move replay logs.",
            "conceptual_breakdown": [
                "<strong>Board Entity:</strong> $N \\times N$ grid with row, column, and diagonal counter arrays for $O(1)$ win checking.",
                "<strong>Player Hierarchy:</strong> <code>HumanPlayer</code> vs <code>BotPlayer</code> (Strategy Pattern).",
                "<strong>Game State Machine:</strong> <code>IN_PROGRESS</code>, <code>WON</code>, <code>DRAW</code>.",
                "<strong>Move History:</strong> Command Pattern with <code>makeMove()</code> and <code>undoMove()</code>."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Tic-Tac-Toe Class Diagram",
                "classes": [
                    {
                        "name": "Board",
                        "is_abstract": False,
                        "attributes": ["- size: int", "- grid: vector<vector<char>>", "- rowCounts: vector<int>", "- colCounts: vector<int>", "- diag: int", "- antiDiag: int"],
                        "methods": ["+ makeMove(r: int, c: int, piece: char): bool", "+ checkWin(r: int, c: int, piece: char): bool"]
                    },
                    {
                        "name": "Player",
                        "is_abstract": False,
                        "attributes": ["- name: string", "- piece: char"],
                        "methods": ["+ getPiece(): char", "+ getName(): string"]
                    },
                    {
                        "name": "TicTacToeGame",
                        "is_abstract": False,
                        "attributes": ["- board: Board", "- players: deque<Player>", "- status: GameStatus"],
                        "methods": ["+ playTurn(r: int, c: int): bool"]
                    }
                ],
                "relationships": [
                    {"from": "TicTacToeGame", "to": "Board", "type": "composition", "label": "owns"},
                    {"from": "TicTacToeGame", "to": "Player", "type": "composition", "label": "manages queue"}
                ]
            },
            "interactive_animation": {
                "title": "Tic-Tac-Toe O(1) Move & Win Check",
                "steps": [
                    {"step": 1, "description": "Player X places piece at (0, 0). rowCounts[0]++, diag++.", "active_nodes": ["Board", "Player X"]},
                    {"step": 2, "description": "Player O places piece at (1, 1). rowCounts[1]--, diag--.", "active_nodes": ["Board", "Player O"]},
                    {"step": 3, "description": "Player X places at (0, 1) and (0, 2). rowCounts[0] reaches +3 == N.", "active_nodes": ["Win Evaluator"]},
                    {"step": 4, "description": "Game transitions to WON. Player X wins in O(1) check time!", "active_nodes": ["Game Status: WON"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <vector>
#include <deque>
#include <string>

enum class Piece { EMPTY, X, O };

class Board {
private:
    int n;
    std::vector<std::vector<Piece>> grid;
    std::vector<int> rowSum;
    std::vector<int> colSum;
    int diagSum{0};
    int antiDiagSum{0};
    int movesCount{0};

public:
    explicit Board(int size) : n(size), grid(size, std::vector<Piece>(size, Piece::EMPTY)),
                               rowSum(size, 0), colSum(size, 0) {}

    [[nodiscard]] int getSize() const noexcept { return n; }
    [[nodiscard]] bool isFull() const noexcept { return movesCount == (n * n); }

    // O(1) Move execution and Win Check
    bool makeMove(int r, int c, Piece p, bool& outHasWon) {
        if (r < 0 || r >= n || c < 0 || c >= n || grid[r][c] != Piece::EMPTY) {
            return false;
        }

        grid[r][c] = p;
        movesCount++;
        int val = (p == Piece::X) ? 1 : -1;

        rowSum[r] += val;
        colSum[c] += val;
        if (r == c) diagSum += val;
        if (r + c == n - 1) antiDiagSum += val;

        int target = (p == Piece::X) ? n : -n;
        if (rowSum[r] == target || colSum[c] == target || diagSum == target || antiDiagSum == target) {
            outHasWon = true;
        } else {
            outHasWon = false;
        }

        return true;
    }

    void display() const {
        for (int r = 0; r < n; ++r) {
            for (int c = 0; c < n; ++c) {
                char ch = (grid[r][c] == Piece::X) ? 'X' : (grid[r][c] == Piece::O) ? 'O' : '.';
                std::cout << ch << " ";
            }
            std::cout << "\\n";
        }
    }
};

struct Player {
    std::string name;
    Piece piece;
};

class TicTacToeGame {
private:
    Board board;
    std::deque<Player> players;
    bool isGameOver{false};

public:
    TicTacToeGame(int size, Player p1, Player p2) : board(size) {
        players.push_back(std::move(p1));
        players.push_back(std::move(p2));
    }

    void playMove(int r, int c) {
        if (isGameOver) {
            std::cout << "[ERROR] Game is already finished!\\n";
            return;
        }

        Player current = players.front();
        bool hasWon = false;

        if (!board.makeMove(r, c, current.piece, hasWon)) {
            std::cout << "[INVALID MOVE] Spot (" << r << ", " << c << ") is invalid or occupied!\\n";
            return;
        }

        std::cout << current.name << " placed " << (current.piece == Piece::X ? "X" : "O") 
                  << " at (" << r << ", " << c << ")\\n";
        board.display();

        if (hasWon) {
            std::cout << "*** " << current.name << " WINS THE GAME! ***\\n";
            isGameOver = true;
            return;
        }

        if (board.isFull()) {
            std::cout << "*** GAME ENDED IN A DRAW! ***\\n";
            isGameOver = true;
            return;
        }

        // Rotate turn
        players.pop_front();
        players.push_back(current);
    }
};

int main() {
    TicTacToeGame game(3, {"Alice", Piece::X}, {"Bob", Piece::O});

    game.playMove(0, 0); // Alice X
    game.playMove(1, 0); // Bob O
    game.playMove(0, 1); // Alice X
    game.playMove(1, 1); // Bob O
    game.playMove(0, 2); // Alice X -> Completes Row 0 -> WINS!

    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. O(1) Win Checking Algorithm:</strong> By maintaining row, column, and diagonal counters ($+1$ for X, $-1$ for O), checking if a move won takes $O(1)$ time rather than $O(N)$ row/column scans.",
                "<strong>2. Player Rotation Queue:</strong> A <code>std::deque<Player></code> handles multiplayer turns cleanly via <code>pop_front()</code> and <code>push_back()</code>.",
                "<strong>3. Clean Encapsulation:</strong> The <code>Board</code> manages grid boundaries and move validation, while <code>TicTacToeGame</code> orchestrates turns."
            ],
            "comparison_matrix": {
                "title": "Win Checking Algorithms",
                "headers": ["Method", "Time Complexity", "Space Overhead", "Scales to N=1000"],
                "rows": [
                    ["Naive Scan Entire Board", "O(N^2)", "O(1)", "Very Slow"],
                    ["Scan Current Row/Col/Diag", "O(N)", "O(1)", "Acceptable"],
                    ["Row/Col Accumulator Arrays", "O(1)", "O(N) integers", "Optimal"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Running full O(N^2) board scans after every turn", "correction": "Use O(1) row/col counters."}
            ],
            "interview_traps": [
                "<strong>Trap: 'How would you support an N*N board where winning requires only K in a row (e.g. 5-in-a-row on 19x19 Go board)?'</strong><br><em>Answer:</em> Accumulator counters only work for $K=N$. For $K < N$, use directional ray casting sliding window checking $K$ steps in 4 axes from the placed coordinate."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor hardcoded 2-player turn logic into an arbitrary N-player queue.",
                "bad_code": "if (turn == 1) turn = 2; else turn = 1;",
                "good_code": "players.push_back(players.front()); players.pop_front();"
            },
            "practice_problem": {
                "title": "Add Move Undo/Redo via Command Pattern",
                "description": "Implement `undo()` and `redo()` on `TicTacToeGame` using a `std::vector<MoveCommand>` stack.",
                "hint": "Each MoveCommand stores `(r, c, piece)`. Undo resets grid spot and decrements accumulators."
            }
        },
        {
            "id": "practice-snake-and-ladder",
            "title": "Practice 2: Snake & Ladder Multiplayer Game",
            "definition": "A complete multiplayer board game simulation featuring variable board sizes, snake and ladder jump mappings, multi-dice rolling strategies, and winner ranking.",
            "why_it_matters": "Tests composition, Strategy Pattern for dice rolling, and graph/lookup jump resolution.",
            "real_world_analogy": "Classic board game with 100 tiles where landing on tile 14 slides you down to 7 (Snake) or tile 9 shoots you up to 31 (Ladder).",
            "conceptual_breakdown": [
                "<strong>Board Entity:</strong> Array of cells or Jump Map <code>unordered_map<int, int></code> mapping start tile to destination tile.",
                "<strong>Dice Rolling Strategy:</strong> <code>IDiceStrategy</code> (e.g. Standard 1-6 Dice, Loaded Dice, 2-Dice sum).",
                "<strong>Player Entity:</strong> <code>id</code>, <code>name</code>, <code>currentPosition</code>.",
                "<strong>Game Engine Loop:</strong> Roll dice $\\to$ advance position $\\to$ apply jump $\\to$ check win ($position == totalCells$)."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Snake & Ladder Class Diagram",
                "classes": [
                    {
                        "name": "IDiceStrategy",
                        "is_abstract": True,
                        "attributes": [],
                        "methods": ["+ roll(): int"]
                    },
                    {
                        "name": "SnakeAndLadderGame",
                        "is_abstract": False,
                        "attributes": [
                            "- boardSize: int",
                            "- jumps: unordered_map<int, int>",
                            "- players: deque<Player>",
                            "- dice: unique_ptr<IDiceStrategy>"
                        ],
                        "methods": ["+ playTurn(): bool"]
                    }
                ],
                "relationships": [
                    {"from": "SnakeAndLadderGame", "to": "IDiceStrategy", "type": "composition", "label": "uses dice"}
                ]
            },
            "interactive_animation": {
                "title": "Snake & Ladder Turn Resolution",
                "steps": [
                    {"step": 1, "description": "Player 1 at tile 12 rolls a 4 -> moves to tile 16.", "active_nodes": ["Player 1", "Dice"]},
                    {"step": 2, "description": "Tile 16 has a Ladder to 35 -> Player climbs to tile 35.", "active_nodes": ["Ladder Jump"]},
                    {"step": 3, "description": "Player 2 at tile 48 rolls a 5 -> moves to tile 53 (Snake to 10). Slides down to 10.", "active_nodes": ["Snake Jump"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <unordered_map>
#include <deque>
#include <string>
#include <memory>
#include <random>

class IDiceStrategy {
public:
    virtual ~IDiceStrategy() = default;
    virtual int roll() = 0;
};

class StandardDice : public IDiceStrategy {
private:
    std::mt19937 rng{std::random_device{}()};
    std::uniform_int_distribution<int> dist{1, 6};
public:
    int roll() override { return dist(rng); }
};

struct Player {
    std::string name;
    int position{1};
};

class SnakeAndLadderGame {
private:
    int targetCell;
    std::unordered_map<int, int> jumps; // start -> end (Snakes and Ladders)
    std::deque<Player> players;
    std::unique_ptr<IDiceStrategy> dice;

public:
    SnakeAndLadderGame(int cells, std::unique_ptr<IDiceStrategy> d)
        : targetCell(cells), dice(std::move(d)) {}

    void addJump(int from, int to) {
        jumps[from] = to;
    }

    void addPlayer(Player p) {
        players.push_back(std::move(p));
    }

    bool playTurn() {
        if (players.empty()) return false;

        Player current = players.front();
        players.pop_front();

        int roll = dice->roll();
        int nextPos = current.position + roll;

        std::cout << "[" << current.name << "] Rolled " << roll << " (from " << current.position << " -> " << nextPos << ")\\n";

        if (nextPos > targetCell) {
            std::cout << "  -> Needs exact roll to reach " << targetCell << ". Stays at " << current.position << "\\n";
            players.push_back(current);
            return false;
        }

        // Apply Snake or Ladder jump
        if (jumps.find(nextPos) != jumps.end()) {
            int jumpDest = jumps[nextPos];
            if (jumpDest > nextPos) {
                std::cout << "  *** CLIMBED LADDER from " << nextPos << " to " << jumpDest << "! ***\\n";
            } else {
                std::cout << "  *** BITTEN BY SNAKE from " << nextPos << " down to " << jumpDest << "! ***\\n";
            }
            nextPos = jumpDest;
        }

        current.position = nextPos;

        if (current.position == targetCell) {
            std::cout << "🎉🎉🎉 " << current.name << " REACHED " << targetCell << " AND WON THE GAME! 🎉🎉🎉\\n";
            return true;
        }

        players.push_back(current);
        return false;
    }
};

int main() {
    auto game = std::make_unique<SnakeAndLadderGame>(100, std::make_unique<StandardDice>());

    // Ladders
    game->addJump(4, 25);
    game->addJump(13, 46);
    game->addJump(50, 69);
    game->addJump(62, 81);

    // Snakes
    game->addJump(99, 5);
    game->addJump(88, 24);
    game->addJump(64, 18);

    game->addPlayer({"Alice", 1});
    game->addPlayer({"Bob", 1});

    std::cout << "--- Starting Snake & Ladder Match ---\\n";
    for (int i = 0; i < 20; ++i) {
        if (game->playTurn()) break;
    }

    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Unified Jump Representation:</strong> Storing both snakes and ladders in a single <code>unordered_map<int, int></code> simplifies jump logic without requiring distinct classes.",
                "<strong>2. Strategy Pattern for Dice:</strong> <code>IDiceStrategy</code> makes testing deterministic with mocked dice rolls.",
                "<strong>3. Exact Finish Rule:</strong> Handles boundary over-rolls ($pos + roll > target$) cleanly."
            ],
            "comparison_matrix": {
                "title": "Board Storage Approaches",
                "headers": ["Approach", "Memory", "Lookup Time", "Cycles Detection"],
                "rows": [
                    ["Array of 100 Cell Objects", "100 structs in memory", "O(1)", "Harder to validate"],
                    ["Sparse Hash Map Jumps", "Only entries for jumps (10-20)", "O(1) average", "Trivial graph cycle check"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Infinite jump cycles (Snake at 20 -> 10, Ladder at 10 -> 20)", "correction": "Validate acyclic DAG graph invariants when inserting jumps."}
            ],
            "interview_traps": [
                "<strong>Trap: 'Can a player land on a snake that drops them into another ladder in the same turn?'</strong><br><em>Answer:</em> Clarify whether jump chaining is allowed. If yes, replace `if (jump)` with `while (jump)` guarded by an iteration depth limit."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor hardcoded `rand() % 6 + 1` dice rolls into an injectable IDiceStrategy interface.",
                "bad_code": "int roll = rand() % 6 + 1;",
                "good_code": "int roll = diceStrategy->roll();"
            },
            "practice_problem": {
                "title": "Design Minimum Dice Rolls BFS Solver",
                "description": "Add a method `int findShortestPathToWin()` that uses BFS to find the minimum number of dice rolls needed to win from tile 1.",
                "hint": "Model the 100 tiles as an unweighted directed graph and run standard BFS."
            }
        },
        {
            "id": "practice-coffee-machine",
            "title": "Practice 3: Multi-recipe Coffee Machine",
            "definition": "An interactive smart coffee brewing system managing raw ingredient inventory (water, milk, coffee beans), recipe customization, dynamic price calculation, and parallel brewing dispensers.",
            "why_it_matters": "Demonstrates the Decorator Pattern (condiments like Extra Foam, Caramel drizzle), Factory Pattern (Espresso, Latte, Cappuccino), and Inventory Invariant validation.",
            "real_world_analogy": "A Starbucks automated barista kiosk that tracks milliliter levels of steamed milk and grams of ground espresso, warning staff when milk is depleted.",
            "conceptual_breakdown": [
                "<strong>Ingredient & Inventory:</strong> <code>Inventory</code> managing thread-safe counts of Water, Milk, Beans, Sugar.",
                "<strong>Beverage Decorator Pattern:</strong> <code>Beverage</code> base with <code>Espresso</code>, wrapped by <code>MochaDecorator</code>, <code>WhipDecorator</code>.",
                "<strong>Recipe Engine:</strong> Defines required ingredients per drink.",
                "<strong>Brewing Execution:</strong> Validates and deducts stock atomically before dispensing."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Coffee Machine Decorator UML",
                "classes": [
                    {
                        "name": "Beverage",
                        "is_abstract": True,
                        "attributes": ["# description: string"],
                        "methods": ["+ getDescription(): string", "+ getCost(): double"]
                    },
                    {
                        "name": "Espresso",
                        "is_abstract": False,
                        "attributes": [],
                        "methods": ["+ getCost(): double = $2.50"]
                    },
                    {
                        "name": "CondimentDecorator",
                        "is_abstract": True,
                        "attributes": ["# baseBeverage: unique_ptr<Beverage>"],
                        "methods": []
                    },
                    {
                        "name": "MochaDecorator",
                        "is_abstract": False,
                        "attributes": [],
                        "methods": ["+ getCost(): double = base + $0.75"]
                    }
                ],
                "relationships": [
                    {"from": "Espresso", "to": "Beverage", "type": "inheritance", "label": "is a"},
                    {"from": "CondimentDecorator", "to": "Beverage", "type": "inheritance", "label": "is a"},
                    {"from": "CondimentDecorator", "to": "Beverage", "type": "composition", "label": "wraps"}
                ]
            },
            "interactive_animation": {
                "title": "Beverage Decorator Composition & Dispensing",
                "steps": [
                    {"step": 1, "description": "Base Beverage: Espresso ($2.50).", "active_nodes": ["Espresso"]},
                    {"step": 2, "description": "Decorate with Milk (+$0.50) -> $3.00.", "active_nodes": ["Milk Decorator"]},
                    {"step": 3, "description": "Decorate with Caramel (+$0.60) -> $3.60.", "active_nodes": ["Caramel Decorator"]},
                    {"step": 4, "description": "CoffeeMachine deducts 50ml Water, 30g Beans, 50ml Milk and dispenses.", "active_nodes": ["Inventory", "Dispenser"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <string>
#include <memory>
#include <unordered_map>
#include <mutex>
#include <iomanip>

// 1. Decorator Pattern for Beverages
class Beverage {
public:
    virtual ~Beverage() = default;
    [[nodiscard]] virtual std::string getDescription() const = 0;
    [[nodiscard]] virtual double getCost() const = 0;
};

class Espresso : public Beverage {
public:
    [[nodiscard]] std::string getDescription() const override { return "Espresso"; }
    [[nodiscard]] double getCost() const override { return 2.50; }
};

class HouseBlend : public Beverage {
public:
    [[nodiscard]] std::string getDescription() const override { return "House Blend Coffee"; }
    [[nodiscard]] double getCost() const override { return 2.00; }
};

// Abstract Condiment Decorator
class CondimentDecorator : public Beverage {
protected:
    std::unique_ptr<Beverage> beverage;
public:
    explicit CondimentDecorator(std::unique_ptr<Beverage> bev) : beverage(std::move(bev)) {}
};

class Mocha : public CondimentDecorator {
public:
    using CondimentDecorator::CondimentDecorator;
    [[nodiscard]] std::string getDescription() const override {
        return beverage->getDescription() + ", Mocha";
    }
    [[nodiscard]] double getCost() const override {
        return beverage->getCost() + 0.60;
    }
};

class SteamedMilk : public CondimentDecorator {
public:
    using CondimentDecorator::CondimentDecorator;
    [[nodiscard]] std::string getDescription() const override {
        return beverage->getDescription() + ", Steamed Milk";
    }
    [[nodiscard]] double getCost() const override {
        return beverage->getCost() + 0.40;
    }
};

// 2. Thread-safe Coffee Machine Inventory
class CoffeeMachineInventory {
private:
    std::unordered_map<std::string, int> stock; // Ingredient -> quantity in ml/g
    std::mutex mtx;

public:
    void addStock(const std::string& ingredient, int qty) {
        std::lock_guard<std::mutex> lock(mtx);
        stock[ingredient] += qty;
    }

    bool consumeIngredients(const std::unordered_map<std::string, int>& required) {
        std::lock_guard<std::mutex> lock(mtx);
        
        // 1. Verify sufficiency
        for (const auto& [item, amount] : required) {
            if (stock[item] < amount) {
                std::cout << "[OUT OF STOCK] Insufficient " << item << " (Need " << amount << ", Have " << stock[item] << ")\\n";
                return false;
            }
        }

        // 2. Deduct atomically
        for (const auto& [item, amount] : required) {
            stock[item] -= amount;
        }

        return true;
    }
};

int main() {
    CoffeeMachineInventory inventory;
    inventory.addStock("Water", 500);
    inventory.addStock("Beans", 200);
    inventory.addStock("Milk", 300);

    // Build Custom Decorated Beverage: House Blend + Milk + Mocha + Mocha (Double Mocha Latte)
    std::unique_ptr<Beverage> myCoffee = std::make_unique<HouseBlend>();
    myCoffee = std::make_unique<SteamedMilk>(std::move(myCoffee));
    myCoffee = std::make_unique<Mocha>(std::move(myCoffee));
    myCoffee = std::make_unique<Mocha>(std::move(myCoffee));

    std::cout << "--- Ordered Custom Drink ---\\n";
    std::cout << "Description: " << myCoffee->getDescription() << "\\n";
    std::cout << "Total Cost:  $" << std::fixed << std::setprecision(2) << myCoffee->getCost() << "\\n";

    if (inventory.consumeIngredients({{"Water", 100}, {"Beans", 20}, {"Milk", 100}})) {
        std::cout << "☕ Dispensing your handcrafted drink! Enjoy!\\n";
    }

    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Dynamic Composition via Decorator:</strong> Allows combining arbitrary condiments (Mocha, Milk, Caramel) at runtime without creating $2^N$ subclass permutations.",
                "<strong>2. Recursive Cost Calculation:</strong> Calling <code>getCost()</code> delegates down the decorated chain, summing base beverage and all condiment prices cleanly.",
                "<strong>3. Atomic Inventory Deduction:</strong> Verification and deduction happen under a single mutex lock to avoid partial ingredient consumption."
            ],
            "comparison_matrix": {
                "title": "Beverage Modeling Approaches",
                "headers": ["Approach", "Class Explosion Risk", "Dynamic Customization", "Adheres to OCP"],
                "rows": [
                    ["Subclass per Combination (e.g. EspressoWithMilkAndMocha)", "Extreme (O(2^N))", "No (Compile-time fixed)", "Violated"],
                    ["Boolean Flags in Base Beverage", "Low", "Moderate", "Violated (must edit base class for new condiments)"],
                    ["Decorator Pattern", "Zero (O(N) classes)", "100% Dynamic at runtime", "Fully Adhered"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Deducting water first, failing on beans, and leaving water deducted (Dirty State)", "correction": "Verify ALL required ingredients exist before deducting any of them."}
            ],
            "interview_traps": [
                "<strong>Trap: 'How do you handle multiple cups brewing simultaneously on a 3-spout machine?'</strong><br><em>Answer:</em> Introduce a thread pool of SpoutWorkers with a semaphore(3) guarding concurrent dispenser spouts."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor a beverage class using 15 boolean condiment flags into a clean Decorator hierarchy.",
                "bad_code": "class Coffee { bool hasMilk, hasMocha, hasCaramel; double getCost() { ... } };",
                "good_code": "Use CondimentDecorator wrapping Beverage base."
            },
            "practice_problem": {
                "title": "Design Low-Inventory Alert System",
                "description": "Implement an Observer pattern that sends an alert to the Barista when any ingredient drops below 10% capacity.",
                "hint": "Attach `IInventoryListener` to `CoffeeMachineInventory`."
            }
        },
        {
            "id": "practice-logging-framework",
            "title": "Practice 4: Asynchronous Logging Framework",
            "definition": "A high-throughput non-blocking asynchronous logging framework buffering log events in memory and flushing to multiple sinks (Console, File, Socket) via a dedicated background worker thread.",
            "why_it_matters": "One of the most practical systems design questions. Tests Producer-Consumer concurrency, Chain of Responsibility (Log Level filtering), and Observer/Strategy for Log Appenders.",
            "real_world_analogy": "Log4j / Spdlog: application worker threads push log strings into an in-memory queue in nanoseconds, while a background disk I/O thread flushes batches to disk without slowing down user transactions.",
            "conceptual_breakdown": [
                "<strong>Log Levels:</strong> <code>DEBUG</code>, <code>INFO</code>, <code>WARN</code>, <code>ERROR</code>, <code>FATAL</code>.",
                "<strong>Log Appenders / Sinks:</strong> <code>IAppender</code> interface with <code>ConsoleAppender</code>, <code>FileAppender</code>.",
                "<strong>Asynchronous Ring Buffer:</strong> Thread-safe blocking queue decoupling caller threads from slow disk writes.",
                "<strong>Graceful Shutdown:</strong> Flushes all pending log entries during application termination."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Async Logger Architecture",
                "classes": [
                    {
                        "name": "IAppender",
                        "is_abstract": True,
                        "attributes": [],
                        "methods": ["+ append(msg: string): void"]
                    },
                    {
                        "name": "AsyncLogger",
                        "is_abstract": False,
                        "attributes": [
                            "- queue: deque<string>",
                            "- appenders: vector<shared_ptr<IAppender>>",
                            "- workerThread: thread",
                            "- running: atomic<bool>",
                            "- cv: condition_variable",
                            "- mtx: mutex"
                        ],
                        "methods": [
                            "+ log(level: LogLevel, msg: string): void",
                            "- workerLoop(): void"
                        ]
                    }
                ],
                "relationships": [
                    {"from": "AsyncLogger", "to": "IAppender", "type": "composition", "label": "dispatches to sinks"}
                ]
            },
            "interactive_animation": {
                "title": "Async Logger Batch Flush Cycle",
                "steps": [
                    {"step": 1, "description": "Worker threads push LogEvent('Order Created') into Ring Buffer in 15ns.", "active_nodes": ["Worker Threads", "Ring Buffer"]},
                    {"step": 2, "description": "Background Flush Thread wakes up on condition variable notification.", "active_nodes": ["Flush Thread"]},
                    {"step": 3, "description": "Swaps active queue with empty queue in O(1) pointer swap, minimizing lock hold time.", "active_nodes": ["Queue Swap"]},
                    {"step": 4, "description": "Writes batch to Disk File and Network Sinks without holding the incoming queue lock.", "active_nodes": ["Disk Sink", "Network Sink"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <string>
#include <vector>
#include <deque>
#include <memory>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <chrono>

enum class LogLevel { DEBUG, INFO, WARN, ERROR };

class ILogAppender {
public:
    virtual ~ILogAppender() = default;
    virtual void append(const std::string& formattedMsg) = 0;
};

class ConsoleAppender : public ILogAppender {
public:
    void append(const std::string& formattedMsg) override {
        std::cout << formattedMsg << "\\n";
    }
};

class AsyncLogger {
private:
    std::vector<std::shared_ptr<ILogAppender>> appenders;
    std::deque<std::string> queue;
    std::mutex mtx;
    std::condition_variable cv;
    std::atomic<bool> isRunning{true};
    std::thread backgroundWorker;

    void workerLoop() {
        while (isRunning || !queue.empty()) {
            std::deque<std::string> localBatch;
            {
                std::unique_lock<std::mutex> lock(mtx);
                cv.wait(lock, [this]() {
                    return !queue.empty() || !isRunning;
                });

                if (queue.empty() && !isRunning) break;

                // Double buffering / queue swap: O(1) swap to release lock immediately!
                localBatch.swap(queue);
            }

            // Flush batch to all appenders without holding the mutex
            for (const auto& msg : localBatch) {
                for (const auto& appender : appenders) {
                    appender->append(msg);
                }
            }
        }
    }

public:
    AsyncLogger() : backgroundWorker(&AsyncLogger::workerLoop, this) {}

    ~AsyncLogger() {
        stop();
    }

    void addAppender(std::shared_ptr<ILogAppender> appender) {
        appenders.push_back(std::move(appender));
    }

    void log(LogLevel level, const std::string& message) {
        std::string levelStr = (level == LogLevel::INFO) ? "[INFO] " :
                               (level == LogLevel::WARN) ? "[WARN] " :
                               (level == LogLevel::ERROR) ? "[ERROR] " : "[DEBUG] ";

        std::string fullMsg = levelStr + message;

        {
            std::lock_guard<std::mutex> lock(mtx);
            queue.push_back(std::move(fullMsg));
        }
        cv.notify_one();
    }

    void stop() {
        if (isRunning) {
            isRunning = false;
            cv.notify_all();
            if (backgroundWorker.joinable()) {
                backgroundWorker.join();
            }
        }
    }
};

int main() {
    AsyncLogger logger;
    logger.addAppender(std::make_shared<ConsoleAppender>());

    std::cout << "--- Firing Fast Non-blocking Async Log Events ---\\n";
    logger.log(LogLevel::INFO, "Application Server Started on port 8080");
    logger.log(LogLevel::WARN, "Database connection pool reached 85% capacity");
    logger.log(LogLevel::ERROR, "Payment Gateway timeout for Order #4492");

    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    logger.stop();

    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Double-Buffering Queue Swap:</strong> <code>localBatch.swap(queue)</code> extracts all pending log items in $O(1)$ time and releases the mutex immediately so application threads are never blocked by slow disk I/O.",
                "<strong>2. Observer / Strategy Pattern for Sinks:</strong> <code>ILogAppender</code> allows dynamically attaching file sinks, console printers, and syslog network forwarders.",
                "<strong>3. Graceful Shutdown Guarantee:</strong> The destructor signals <code>isRunning = false</code>, notifies the condition variable, and joins the worker thread after draining remaining queued entries."
            ],
            "comparison_matrix": {
                "title": "Synchronous vs Asynchronous Logging",
                "headers": ["Metric", "Synchronous File Logging", "Asynchronous Double-Buffered Logging"],
                "rows": [
                    ["Caller Latency", "50 - 5,000 microseconds (Disk I/O)", "15 - 50 nanoseconds (Memory push)"],
                    ["Disk Contention", "High (every thread locks file)", "Zero (1 dedicated background writer)"],
                    ["Crash Risk", "Logs committed immediately to disk", "Unflushed memory buffer may be lost if process SIGKILLs"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Performing disk write `file << msg` while holding the queue lock", "correction": "Swap the queue into a local batch and write to disk outside the critical section."}
            ],
            "interview_traps": [
                "<strong>Trap: 'What happens if application threads generate 1,000,000 logs/sec and the disk can only write 100,000/sec?'</strong><br><em>Answer:</em> Discuss backpressure policies: Bounded Queue with either Drop Oldest Logs, Drop Debug Logs, or Block Application Caller Thread."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor a synchronous logging class that opens a file on every log call into an asynchronous queue.",
                "bad_code": "ofstream file(\"app.log\", ios::app); file << msg; // Opens file every time",
                "good_code": "AsyncLogger with background worker and persistent open file stream."
            },
            "practice_problem": {
                "title": "Design Log File Rolling by Size & Date",
                "description": "Implement a `RollingFileAppender` that automatically renames and compresses `app.log` to `app.2026-10-03.1.gz` when file size exceeds 100 MB.",
                "hint": "Check `std::filesystem::file_size` before write; rotate file handle when threshold reached."
            }
        }
    ]
}

# Module 23: Curated LLD Interview Question Bank
m23 = {
    "module_id": "23",
    "module_title": "Curated LLD Interview Question Bank",
    "description": "100+ Top C++ LLD interview questions categorized by OOP, SOLID, Patterns, Concurrency, and Traps with interactive reveal.",
    "topics": [
        {
            "id": "cpp-oop-interview-questions",
            "title": "C++ OOP & Memory Interview Questions",
            "definition": "High-yield interview questions probing object layout, virtual tables, dynamic casting, object slicing, RAII, and custom memory management in C++.",
            "why_it_matters": "These technical questions test whether you understand what the C++ compiler actually produces at the assembly and memory level, separating senior engineers from casual programmers.",
            "real_world_analogy": "A mechanic who doesn't just know how to drive a sports car, but understands internal combustion, transmission ratios, and ECU timing maps.",
            "conceptual_breakdown": [
                "<strong>VTable & VPTR:</strong> 8-byte pointer per polymorphic object pointing to class function table.",
                "<strong>Virtual Destructor:</strong> Required in any base class with virtual methods to prevent partial destructor deletion leaks.",
                "<strong>Object Slicing:</strong> Passing derived objects by value cuts off derived members.",
                "<strong>Rule of 0 / 3 / 5:</strong> Deterministic resource lifecycle management."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "VTable Layout in Memory",
                "classes": [
                    {
                        "name": "DerivedObjectInstance",
                        "is_abstract": False,
                        "attributes": ["+ vptr (8 bytes) -> &Derived_VTable", "+ baseData (4 bytes)", "+ derivedData (4 bytes)"],
                        "methods": []
                    },
                    {
                        "name": "Derived_VTable",
                        "is_abstract": False,
                        "attributes": ["&Derived::virtFunc1", "&Derived::virtFunc2", "&Derived::~Derived"],
                        "methods": []
                    }
                ],
                "relationships": [
                    {"from": "DerivedObjectInstance", "to": "Derived_VTable", "type": "association", "label": "points to"}
                ]
            },
            "interactive_animation": {
                "title": "Virtual Dispatch Lookup Step-by-Step",
                "steps": [
                    {"step": 1, "description": "Base pointer `ptr->draw()` called on `Circle` instance.", "active_nodes": ["Base Pointer"]},
                    {"step": 2, "description": "CPU dereferences object's hidden `vptr` at offset 0.", "active_nodes": ["vptr Dereference"]},
                    {"step": 3, "description": "Indexes slot 0 in `Circle_VTable` and jumps to `Circle::draw()` assembly.", "active_nodes": ["Circle::draw()"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <memory>

class Base {
public:
    Base() { std::cout << "Base Constructor\\n"; }
    // Critical: Virtual Destructor ensures Derived destructor is invoked via Base pointer!
    virtual ~Base() { std::cout << "Base Destructor\\n"; }
    virtual void show() const { std::cout << "Base::show()\\n"; }
};

class Derived : public Base {
private:
    int* heapBuffer;
public:
    Derived() : heapBuffer(new int[100]) { std::cout << "Derived Constructor (Allocated 100 ints)\\n"; }
    ~Derived() override {
        delete[] heapBuffer;
        std::cout << "Derived Destructor (Freed 100 ints)\\n";
    }
    void show() const override { std::cout << "Derived::show()\\n"; }
};

int main() {
    std::cout << "--- Polymorphic Deletion via Base Pointer ---\\n";
    std::unique_ptr<Base> obj = std::make_unique<Derived>();
    obj->show();
    // Destructor runs cleanly: Derived Destructor -> Base Destructor!
    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Virtual Destructor Dispatch:</strong> Because <code>~Base()</code> is virtual, deleting via <code>Base*</code> looks up <code>Derived::~Derived()</code> in the VTable, freeing <code>heapBuffer</code>.",
                "<strong>2. Memory Leak Prevention:</strong> Without <code>virtual ~Base()</code>, only <code>Base::~Base()</code> executes, leaking the 100 ints.",
                "<strong>3. Modern RAII:</strong> Wrapping with <code>std::unique_ptr<Base></code> ensures deletion happens automatically when going out of scope."
            ],
            "comparison_matrix": {
                "title": "C++ Casting Mechanisms",
                "headers": ["Cast Type", "Safety Check", "Performance Cost", "Typical Use Case"],
                "rows": [
                    ["static_cast", "Compile-time type check", "Zero (free)", "Numeric conversions, related pointer up/downcast"],
                    ["dynamic_cast", "Runtime RTTI check", "Moderate (traverses type info)", "Safe downcasting with polymorphic classes"],
                    ["reinterpret_cast", "No checks (treats bits as type)", "Zero (free)", "Raw hardware buffers, packet byte serialization"],
                    ["const_cast", "Removes const qualifier", "Zero (free)", "Interfacing with legacy C APIs"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Calling virtual methods inside constructors or destructors", "correction": "During base construction, the derived portion is not yet initialized; virtual calls resolve to the base class implementation, NOT the derived one."}
            ],
            "interview_traps": [
                "<strong>Trap: 'Why does `sizeof(EmptyClass)` return 1 byte in C++ instead of 0?'</strong><br><em>Answer:</em> C++ requires every distinct object instance to have a unique memory address (`&a != &b`). In C++20, `[[no_unique_address]]` allows empty members to consume 0 bytes."
            ],
            "code_refactor_exercise": {
                "problem": "Fix a missing virtual destructor in a polymorphic abstract base class.",
                "bad_code": "class Shape { public: virtual void draw() = 0; };",
                "good_code": "class Shape { public: virtual ~Shape() = default; virtual void draw() = 0; };"
            },
            "practice_problem": {
                "title": "Analyze Virtual Table Sizing",
                "description": "Calculate the exact memory footprint of a class with 2 virtual functions, 1 int member, and 1 double member on a 64-bit architecture.",
                "hint": "8 bytes (vptr) + 4 bytes (int) + 4 bytes (padding) + 8 bytes (double) = 24 bytes."
            }
        },
        {
            "id": "solid-interview-questions",
            "title": "SOLID Principles Interview Questions",
            "definition": "Curated questions and deep technical trade-off scenarios on Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion in C++.",
            "why_it_matters": "Interviewers frequently present subtly flawed code snippets and ask candidates to identify which SOLID principle is violated and write the refactored C++ code.",
            "real_world_analogy": "Building a modular modular stereo system: speakers, turntable, and amplifiers connect via standard RCA cables (DIP), allowing upgrading the turntable without rewiring the speakers (OCP).",
            "conceptual_breakdown": [
                "<strong>SRP:</strong> A class should have only one reason to change.",
                "<strong>OCP:</strong> Open for extension, closed for modification (via interfaces/templates).",
                "<strong>LSP:</strong> Subtypes must be substitutable for their base types without altering program correctness.",
                "<strong>ISP:</strong> Clients should not be forced to depend on interfaces they do not use.",
                "<strong>DIP:</strong> High-level modules should depend on abstractions, not concrete implementations."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "LSP Violation: Rectangle vs Square",
                "classes": [
                    {
                        "name": "Rectangle",
                        "is_abstract": False,
                        "attributes": ["# width: int", "# height: int"],
                        "methods": ["+ setWidth(w: int)", "+ setHeight(h: int)", "+ getArea(): int"]
                    },
                    {
                        "name": "Square_Violates_LSP",
                        "is_abstract": False,
                        "attributes": [],
                        "methods": ["+ setWidth(w: int) { width = height = w; }"]
                    }
                ],
                "relationships": [
                    {"from": "Square_Violates_LSP", "to": "Rectangle", "type": "inheritance", "label": "violates LSP invariant"}
                ]
            },
            "interactive_animation": {
                "title": "LSP Invariant Violation Detection",
                "steps": [
                    {"step": 1, "description": "Function testRectangle(Rectangle& r) assumes setWidth(5) and setHeight(4) gives area 20.", "active_nodes": ["Test Function"]},
                    {"step": 2, "description": "Pass Square instance. setHeight(4) overrides width to 4. Area is 16 != 20! Invariant broken.", "active_nodes": ["Square", "LSP Violation"]},
                    {"step": 3, "description": "Refactor: Make Shape base with getArea(); separate Square and Rectangle hierarchies.", "active_nodes": ["Refactored Solution"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <memory>
#include <cassert>

// Clean LSP Hierarchy
class IShape {
public:
    virtual ~IShape() = default;
    [[nodiscard]] virtual int getArea() const = 0;
};

class Rectangle : public IShape {
private:
    int width;
    int height;
public:
    Rectangle(int w, int h) : width(w), height(h) {}
    [[nodiscard]] int getArea() const override { return width * height; }
};

class Square : public IShape {
private:
    int side;
public:
    explicit Square(int s) : side(s) {}
    [[nodiscard]] int getArea() const override { return side * side; }
};

void printArea(const IShape& shape) {
    std::cout << "Shape Area: " << shape.getArea() << "\\n";
}

int main() {
    Rectangle rect(5, 4);
    Square sq(5);

    printArea(rect); // 20
    printArea(sq);   // 25

    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Preserving Invariants:</strong> Square is NOT a behavioral subtype of Rectangle if mutators (<code>setWidth</code>) allow altering independent dimensions.",
                "<strong>2. Common Abstract Root:</strong> Both implement <code>IShape</code> with read-only contract <code>getArea()</code>.",
                "<strong>3. Immutability Principle:</strong> Making shapes immutable value objects completely eliminates LSP mutation bugs."
            ],
            "comparison_matrix": {
                "title": "SOLID Principles Summary",
                "headers": ["Principle", "Core Question", "Typical C++ Solution"],
                "rows": [
                    ["SRP", "Does this class do 2 unrelated things?", "Split into distinct focused classes"],
                    ["OCP", "Must I edit this file to add a new payment type?", "Use Strategy or Factory Pattern"],
                    ["LSP", "Does deriving break caller assumptions?", "Ensure derived classes strengthen preconditions"],
                    ["ISP", "Does class implement dummy no-op methods?", "Split giant interface into smaller role interfaces"],
                    ["DIP", "Does high-level service call concrete MySQL?", "Pass `IRepository` interface via constructor"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Creating a single God Interface `IEntity` with 50 methods", "correction": "Apply Interface Segregation Principle (ISP) to split into small interfaces (`IPrintable`, `ISerializable`, `IComparable`)."}
            ],
            "interview_traps": [
                "<strong>Trap: 'Is Dependency Inversion Principle the same as Dependency Injection?'</strong><br><em>Answer:</em> No. DIP is the high-level design principle (depend on abstractions). Dependency Injection (DI) is a specific design pattern / technique used to deliver dependencies to a class (e.g. constructor injection)."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor a NotificationService that directly instantiates SendGridAPI inside its constructor.",
                "bad_code": "NotificationService() { api = new SendGridAPI(); }",
                "good_code": "NotificationService(unique_ptr<IEmailSender> sender) : emailSender(move(sender)) {}"
            },
            "practice_problem": {
                "title": "Identify SOLID Violations in Monolithic E-Commerce Cart",
                "description": "Given a `ShoppingCart` class that calculates taxes, charges Stripe, updates MySQL, and sends emails, refactor it into 4 SRP-compliant components.",
                "hint": "Create `TaxCalculator`, `PaymentService`, `OrderRepository`, and `EmailNotifier`."
            }
        },
        {
            "id": "design-patterns-interview-questions",
            "title": "Design Patterns & Trade-offs Questions",
            "definition": "Deep-dive questions comparing creational, structural, and behavioral patterns: Factory vs Abstract Factory, Strategy vs State, Observer vs Pub/Sub, and Decorator vs Adapter.",
            "why_it_matters": "Interviewers test whether you understand the exact trade-offs of patterns rather than blindly applying them everywhere (Pattern Overuse / Anti-pattern).",
            "real_world_analogy": "Choosing the right tool from a master mechanic's toolbox: knowing when to use a torque wrench versus an impact driver.",
            "conceptual_breakdown": [
                "<strong>Factory vs Abstract Factory:</strong> Factory creates 1 product family; Abstract Factory creates families of related products (e.g. DarkTheme Button + Checkbox).",
                "<strong>Strategy vs State:</strong> Strategy is chosen by client to vary an algorithm; State transitions automatically internally based on object state.",
                "<strong>Decorator vs Adapter:</strong> Decorator adds behavior without changing interface; Adapter converts an incompatible interface into another.",
                "<strong>Proxy vs Decorator:</strong> Proxy controls access (caching, security, lazy loading); Decorator enhances functionality."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Strategy vs State Pattern",
                "classes": [
                    {
                        "name": "StrategyPattern",
                        "is_abstract": False,
                        "attributes": ["Client sets Strategy explicitly", "Independent interchangeable algorithms"],
                        "methods": ["+ sort(data)"]
                    },
                    {
                        "name": "StatePattern",
                        "is_abstract": False,
                        "attributes": ["Object changes state automatically", "Transitions governed by internal events"],
                        "methods": ["+ handleRequest() -> nextState"]
                    }
                ],
                "relationships": []
            },
            "interactive_animation": {
                "title": "Pattern Disambiguation Decision Flow",
                "steps": [
                    {"step": 1, "description": "Need to add responsibilities to an object dynamically without subclassing? -> Use DECORATOR.", "active_nodes": ["Decorator"]},
                    {"step": 2, "description": "Need to match an incompatible legacy interface to a new client? -> Use ADAPTER.", "active_nodes": ["Adapter"]},
                    {"step": 3, "description": "Need to control lazy loading or permissions to an expensive object? -> Use PROXY.", "active_nodes": ["Proxy"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <memory>

// Demonstrating Strategy vs State in C++
// Strategy: Client chooses algorithm
class ICompressionStrategy {
public:
    virtual ~ICompressionStrategy() = default;
    virtual void compress(const std::string& file) = 0;
};

class ZipCompression : public ICompressionStrategy {
public:
    void compress(const std::string& file) override { std::cout << "Compressing " << file << " using ZIP\\n"; }
};

class RarCompression : public ICompressionStrategy {
public:
    void compress(const std::string& file) override { std::cout << "Compressing " << file << " using RAR\\n"; }
};

class CompressionContext {
private:
    std::unique_ptr<ICompressionStrategy> strategy;
public:
    void setStrategy(std::unique_ptr<ICompressionStrategy> s) { strategy = std::move(s); }
    void execute(const std::string& file) { if (strategy) strategy->compress(file); }
};

int main() {
    CompressionContext ctx;
    ctx.setStrategy(std::make_unique<ZipCompression>());
    ctx.execute("dataset.csv");

    ctx.setStrategy(std::make_unique<RarCompression>());
    ctx.execute("dataset.csv");

    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Client-Driven Polymorphism:</strong> Strategy lets the caller dynamically swap algorithms at runtime.",
                "<strong>2. Zero Code Duplication:</strong> Eliminates nested switch statements for format types.",
                "<strong>3. Open for New Algorithms:</strong> Adding <code>TarGzCompression</code> requires zero edits to <code>CompressionContext</code>."
            ],
            "comparison_matrix": {
                "title": "Pattern Nuances Comparison",
                "headers": ["Pattern Pair", "Key Difference", "Interface Impact"],
                "rows": [
                    ["Adapter vs Facade", "Adapter wraps 1 class to fix interface; Facade simplifies a whole subsystem", "Adapter matches target interface; Facade creates new simple interface"],
                    ["Decorator vs Proxy", "Decorator adds new behavior; Proxy controls access/lifecycle", "Both preserve the original interface identical to target"],
                    ["Observer vs Mediator", "Observer is 1-to-many broadcast; Mediator encapsulates complex many-to-many communications", "Mediator centralizes coordination; Observer distributes notifications"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Overusing Singleton for things that are not genuinely unique (e.g. User, Configuration)", "correction": "Singleton creates hidden global state; prefer Dependency Injection."}
            ],
            "interview_traps": [
                "<strong>Trap: 'Why is the Visitor Pattern difficult to maintain if you frequently add new ConcreteElement classes?'</strong><br><em>Answer:</em> Adding a new element requires modifying the `IVisitor` interface and EVERY concrete visitor class, violating the Open-Closed Principle for the element dimension."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor a hardcoded switch statement selecting sorting algorithms into the Strategy Pattern.",
                "bad_code": "if (type == 1) quickSort(); else if (type == 2) mergeSort();",
                "good_code": "sortStrategy->sort(data);"
            },
            "practice_problem": {
                "title": "Select the Right Pattern for a Banking Pipeline",
                "description": "Which patterns would you use to design a Transaction processing pipeline with fraud scoring, fee calculation, ledger recording, and SMS alerts?",
                "hint": "Chain of Responsibility (pipeline) + Strategy (fee) + Observer (SMS alert)."
            }
        },
        {
            "id": "concurrency-interview-questions",
            "title": "Concurrency & Multi-threading LLD Questions",
            "definition": "Advanced questions on deadlocks, race conditions, memory models, reader-writer locking, double-checked locking, and thread pool starvation in C++.",
            "why_it_matters": "Multi-threading is the ultimate filter in senior C++ LLD interviews. Demonstrating precise locking disciplines and lock-free awareness is essential.",
            "real_world_analogy": "A 4-way traffic intersection: without traffic lights (locks) or roundabouts (lock-free), cars crash (data races) or create gridlock where nobody moves (deadlock).",
            "conceptual_breakdown": [
                "<strong>4 Conditions for Deadlock (Coffman):</strong> Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait.",
                "<strong>std::scoped_lock (C++17):</strong> Acquires multiple mutexes simultaneously using deadlock-avoidance algorithms (std::lock).",
                "<strong>Thread-Safe Meyer's Singleton:</strong> Guaranteed thread-safe in C++11 with zero locking overhead after initialization.",
                "<strong>False Sharing:</strong> Two threads writing to distinct variables on the same 64-byte cache line destroying performance."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Deadlock Circular Wait Condition",
                "classes": [
                    {
                        "name": "Thread_A",
                        "is_abstract": False,
                        "attributes": ["Holds: Mutex 1", "Waiting for: Mutex 2"],
                        "methods": []
                    },
                    {
                        "name": "Thread_B",
                        "is_abstract": False,
                        "attributes": ["Holds: Mutex 2", "Waiting for: Mutex 1"],
                        "methods": []
                    }
                ],
                "relationships": [
                    {"from": "Thread_A", "to": "Thread_B", "type": "association", "label": "Circular Dependency Deadlock"}
                ]
            },
            "interactive_animation": {
                "title": "Deadlock Resolution via std::scoped_lock",
                "steps": [
                    {"step": 1, "description": "Thread 1 wants to transfer from Account A to Account B.", "active_nodes": ["Thread 1"]},
                    {"step": 2, "description": "Thread 2 wants to transfer from Account B to Account A simultaneously.", "active_nodes": ["Thread 2"]},
                    {"step": 3, "description": "Both use `std::scoped_lock(mtxA, mtxB)`. Deadlock avoidance algorithm acquires both without circular wait.", "active_nodes": ["std::scoped_lock"]},
                    {"step": 4, "description": "Transfers complete safely with zero deadlock risk!", "active_nodes": ["Safe Completion"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <mutex>
#include <thread>

class BankAccount {
public:
    int id;
    double balance;
    mutable std::mutex mtx;

    BankAccount(int accId, double bal) : id(accId), balance(bal) {}
};

// Deadlock-Free Transfer using std::scoped_lock (C++17)
void transferMoney(BankAccount& from, BankAccount& to, double amount) {
    if (&from == &to) return; // Prevent self-locking

    // Atomically locks both mutexes with deadlock avoidance algorithm
    std::scoped_lock lock(from.mtx, to.mtx);

    if (from.balance >= amount) {
        from.balance -= amount;
        to.balance += amount;
        std::cout << "[TRANSFER SUCCESS] $" << amount << " transferred from Account " 
                  << from.id << " to Account " << to.id << "\\n";
    }
}

int main() {
    BankAccount acc1(101, 1000.0);
    BankAccount acc2(102, 500.0);

    std::thread t1(transferMoney, std::ref(acc1), std::ref(acc2), 200.0);
    std::thread t2(transferMoney, std::ref(acc2), std::ref(acc1), 100.0);

    t1.join();
    t2.join();

    std::cout << "Final Acc1: $" << acc1.balance << ", Acc2: $" << acc2.balance << "\\n";
    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. std::scoped_lock Deadlock Immunity:</strong> Eliminates lock-ordering bugs by acquiring all mutexes using a deadlock-avoidance algorithm.",
                "<strong>2. Self-Transfer Guard:</strong> <code>&from == &to</code> check prevents trying to lock the same non-recursive mutex twice.",
                "<strong>3. RAII Automatic Unlock:</strong> Mutexes are guaranteed unlocked upon function exit or exception throw."
            ],
            "comparison_matrix": {
                "title": "C++ Mutex Locking Wrappers",
                "headers": ["Wrapper", "Number of Mutexes", "Manual Unlock", "Condition Variable Support"],
                "rows": [
                    ["std::lock_guard", "1", "No (Strict scope)", "No"],
                    ["std::unique_lock", "1", "Yes (unlock/relock)", "Yes (required for cv.wait)"],
                    ["std::shared_lock", "1 (shared_mutex)", "Yes", "No"],
                    ["std::scoped_lock (C++17)", "1 to N", "No (Strict scope)", "No (Deadlock-free multi-lock)"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Acquiring mutexes in random order across different threads", "correction": "Always use `std::scoped_lock` or enforce a global hierarchical acquisition order based on object memory addresses."}
            ],
            "interview_traps": [
                "<strong>Trap: 'Is Double-Checked Locking safe in C++?'</strong><br><em>Answer:</em> In legacy C++98, it was broken due to CPU instruction reordering. In modern C++11+, Meyer's Singleton (`static Instance inst; return inst;`) is guaranteed thread-safe by the standard and should always be preferred over manual double-checked locking."
            ],
            "code_refactor_exercise": {
                "problem": "Fix a deadlock bug in an account transfer function acquiring locks sequentially.",
                "bad_code": "lock_guard l1(from.mtx); lock_guard l2(to.mtx);",
                "good_code": "std::scoped_lock lock(from.mtx, to.mtx);"
            },
            "practice_problem": {
                "title": "Design Read-Write Thread-Safe Cache",
                "description": "Implement a key-value store using `std::shared_mutex` allowing unlimited concurrent readers but exclusive single-thread writers.",
                "hint": "Use `std::shared_lock` in `get()` and `std::unique_lock` in `put()`."
            }
        },
        {
            "id": "top-interview-traps",
            "title": "Top 20 Critical C++ Interview Traps",
            "definition": "The definitive compilation of subtle C++ traps, undefined behaviors, and design anti-patterns that frequently catch candidates off-guard in technical rounds.",
            "why_it_matters": "Knowing these traps prevents unforced errors that lead to immediate disqualification by senior interviewers.",
            "real_world_analogy": "A pilot's pre-flight checklist: checking pitot tubes, fuel contamination, and rudder locks before takeoff to eliminate fatal surprises.",
            "conceptual_breakdown": [
                "<strong>Trap 1:</strong> Returning references/views to temporary local variables (Dangling References).",
                "<strong>Trap 2:</strong> Iterator Invalidation when mutating vectors inside loops.",
                "<strong>Trap 3:</strong> Slicing polymorphic objects by passing them by value.",
                "<strong>Trap 4:</strong> Memory order relaxed races in custom lock-free queues.",
                "<strong>Trap 5:</strong> Throwing exceptions from destructors (triggers `std::terminate`)."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Iterator Invalidation Trap",
                "classes": [
                    {
                        "name": "Vector_Reallocation_Trap",
                        "is_abstract": False,
                        "attributes": ["Vector at capacity 4", "push_back triggers reallocation to new heap address", "Old iterators still point to freed memory -> CRASH!"],
                        "methods": []
                    }
                ],
                "relationships": []
            },
            "interactive_animation": {
                "title": "Vector Iterator Invalidation Visualizer",
                "steps": [
                    {"step": 1, "description": "Vector capacity is full (4/4 elements at 0x1000).", "active_nodes": ["Vector @ 0x1000"]},
                    {"step": 2, "description": "Iterator holds pointer to element 2 (0x1008).", "active_nodes": ["Iterator @ 0x1008"]},
                    {"step": 3, "description": "push_back allocates new 8-element block at 0x5000 and frees 0x1000.", "active_nodes": ["New Vector @ 0x5000", "0x1000 FREED"]},
                    {"step": 4, "description": "Dereferencing old iterator reads deallocated memory (Undefined Behavior / Crash).", "active_nodes": ["Crash / UAF"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <vector>
#include <string_view>

// Trap 1: Returning string_view to temporary
std::string_view dangerousGetGreeting() {
    std::string s = "Hello World";
    return s; // BUG: s is destroyed at return; returns dangling string_view!
}

// Trap 2: Safe Vector Mutation during iteration
void safeVectorErase(std::vector<int>& vec) {
    // Correct C++20 idiom: std::erase_if (Erase-Remove Idiom)
    std::erase_if(vec, [](int x) { return x % 2 == 0; });
}

int main() {
    std::vector<int> nums = {1, 2, 3, 4, 5, 6, 7, 8};
    safeVectorErase(nums);

    std::cout << "Filtered Odd Numbers: ";
    for (int n : nums) std::cout << n << " ";
    std::cout << "\\n";

    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Dangling View Prevention:</strong> Never return <code>std::string_view</code> or <code>std::span</code> pointing to local stack variables.",
                "<strong>2. Safe Container Modification:</strong> In C++20, use <code>std::erase_if(vec, predicate)</code> instead of manually calling <code>vec.erase(it)</code> inside a raw loop.",
                "<strong>3. Lifetime Vigilance:</strong> Always track the lifetime owner of heap buffers when using non-owning pointer views."
            ],
            "comparison_matrix": {
                "title": "Top 5 Critical Interview Pitfalls",
                "headers": ["Trap Name", "Flawed Code", "Correct Modern C++ Fix"],
                "rows": [
                    ["Object Slicing", "`void func(Base b)`", "`void func(const Base& b)` or `unique_ptr<Base>`"],
                    ["Destructor Exception", "`~MyClass() { throw Error(); }`", "Mark `noexcept`, catch all internal exceptions"],
                    ["Raw Mutex Unlock", "`mtx.lock(); work(); mtx.unlock();`", "`std::lock_guard<std::mutex> lock(mtx);`"],
                    ["Dangling String View", "`string_view s = getTempString();`", "Store in `std::string` or ensure owner outlives view"],
                    ["Implicit Conversions", "`class Box { Box(int size); };`", "`explicit Box(int size);` to prevent accidental casts"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Leaving single-argument constructors without `explicit`", "correction": "Mark single-argument constructors `explicit` to prevent unintended implicit type conversions."}
            ],
            "interview_traps": [
                "<strong>Trap: 'Can a smart pointer circular reference occur with `std::unique_ptr`?'</strong><br><em>Answer:</em> No. `std::unique_ptr` enforces strict single exclusive ownership. Circular ownership cycles can only happen with `std::shared_ptr`, and are resolved using `std::weak_ptr`."
            ],
            "code_refactor_exercise": {
                "problem": "Fix an implicit constructor conversion bug.",
                "bad_code": "class Buffer { public: Buffer(int size); }; void process(Buffer b); process(42); // Converts 42 to Buffer silently!",
                "good_code": "class Buffer { public: explicit Buffer(int size); };"
            },
            "practice_problem": {
                "title": "Debug 3 Hidden Bugs in a Thread-Safe Singleton",
                "description": "Analyze a flawed double-checked locking Singleton with raw pointer allocations and fix it using modern C++11 Meyer's Singleton.",
                "hint": "Replace raw pointer and mutex with a static local variable."
            }
        }
    ]
}

# Module 24: Quick Revision Cheat Sheets
m24 = {
    "module_id": "24",
    "module_title": "Quick Revision Cheat Sheets",
    "description": "Compact, high-yield summary sheets for fast revision before tech interviews: SOLID, Patterns, UML, Pointers, and Mutexes.",
    "topics": [
        {
            "id": "solid-cheat-sheet",
            "title": "SOLID Quick Reference Matrix",
            "definition": "A 1-page condensed review cheat sheet of the 5 SOLID design principles with violation symptoms and immediate modern C++ refactoring remedies.",
            "why_it_matters": "Perfect for a 5-minute review right before entering an interview waiting room.",
            "real_world_analogy": "A laminated emergency checklist in an airplane cockpit.",
            "conceptual_breakdown": [
                "<strong>S - Single Responsibility:</strong> 1 class = 1 responsibility.",
                "<strong>O - Open/Closed:</strong> Open for extension, closed for modification.",
                "<strong>L - Liskov Substitution:</strong> Subtypes must be substitutable for base types.",
                "<strong>I - Interface Segregation:</strong> Client-specific narrow interfaces.",
                "<strong>D - Dependency Inversion:</strong> Depend on abstractions, not concretes."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "SOLID Quick Reference Summary",
                "classes": [
                    {
                        "name": "SOLID_Principles",
                        "is_abstract": False,
                        "attributes": [
                            "S: Single Responsibility",
                            "O: Open / Closed",
                            "L: Liskov Substitution",
                            "I: Interface Segregation",
                            "D: Dependency Inversion"
                        ],
                        "methods": []
                    }
                ],
                "relationships": []
            },
            "interactive_animation": {
                "title": "SOLID Quick Diagnostic",
                "steps": [
                    {"step": 1, "description": "Is a class modifying 5 unrelated features? -> Fix SRP.", "active_nodes": ["SRP"]},
                    {"step": 2, "description": "Are you adding case statements for new types? -> Fix OCP with Strategy/Factory.", "active_nodes": ["OCP"]},
                    {"step": 3, "description": "Are clients implementing empty dummy methods? -> Fix ISP by splitting interfaces.", "active_nodes": ["ISP"]}
                ]
            },
            "cpp_implementation": """// SOLID Cheat Sheet in 30 Lines
#include <iostream>
#include <memory>

// D - Dependency Inversion & O - Open/Closed
class IMessageSender {
public:
    virtual ~IMessageSender() = default;
    virtual void send(const std::string& msg) = 0;
};

class EmailSender : public IMessageSender {
public:
    void send(const std::string& msg) override { std::cout << "Email: " << msg << "\\n"; }
};

// S - Single Responsibility (Only handles notification orchestration)
class UserNotifier {
private:
    std::unique_ptr<IMessageSender> sender;
public:
    explicit UserNotifier(std::unique_ptr<IMessageSender> s) : sender(std::move(s)) {}
    void notify(const std::string& msg) { sender->send(msg); }
};

int main() {
    UserNotifier notifier(std::make_unique<EmailSender>());
    notifier.notify("Your order has shipped!");
    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Depend on IMessageSender abstraction:</strong> (DIP).",
                "<strong>2. Add SMS or Slack senders without modifying UserNotifier:</strong> (OCP).",
                "<strong>3. UserNotifier only coordinates messaging:</strong> (SRP)."
            ],
            "comparison_matrix": {
                "title": "SOLID Matrix Cheat Sheet",
                "headers": ["Letter", "Principle", "Violation Symptom", "C++ Solution"],
                "rows": [
                    ["S", "Single Responsibility", "Class > 500 lines doing UI + DB + Math", "Extract focused helper classes"],
                    ["O", "Open / Closed", "Large `switch(type)` statements", "Strategy / Factory Pattern"],
                    ["L", "Liskov Substitution", "Derived class overrides throw `NotSupported`", "Extract common interface or separate hierarchies"],
                    ["I", "Interface Segregation", "Dummy no-op implementations", "Decompose into smaller role interfaces"],
                    ["D", "Dependency Inversion", "Hardcoded `new ConcreteClass()` in constructor", "Constructor injection with `unique_ptr<IInterface>`"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Over-engineering tiny scripts into 20 SOLID classes", "correction": "Apply SOLID where requirements evolve, vary, or grow complex."}
            ],
            "interview_traps": [
                "<strong>Trap: 'Can SOLID principles conflict with performance?'</strong><br><em>Answer:</em> Virtual function indirection in deep OOP hierarchies can incur cache misses. In latency-critical hot paths, templates / CRTP (static polymorphism) achieve SOLID decoupling with zero runtime overhead."
            ],
            "code_refactor_exercise": {
                "problem": "Review a class that handles DB connection, PDF generation, and HTTP response.",
                "bad_code": "class InvoiceManager { saveDB(); renderPDF(); sendHTTP(); };",
                "good_code": "Split into InvoiceRepository, InvoicePDFRenderer, InvoiceHTTPController."
            },
            "practice_problem": {
                "title": "Quick Mental Drill",
                "description": "Name which SOLID principle is violated when a Derived `ReadOnlyFile` class throws an exception on `write()` inherited from `File` base.",
                "hint": "Liskov Substitution Principle (LSP)."
            }
        },
        {
            "id": "design-pattern-decision-tree",
            "title": "Design Pattern Selection Decision Tree",
            "definition": "A visual and conceptual decision tree mapping any system design problem directly to the optimal GoF design pattern.",
            "why_it_matters": "Eliminates hesitation during interview pattern selection.",
            "real_world_analogy": "A medical diagnostic flowchart for fast triage.",
            "conceptual_breakdown": [
                "<strong>Object Creation?</strong> $\\to$ Factory (variants), Builder (step-by-step), Prototype (clone), Singleton (1 instance).",
                "<strong>Interface Incompatibility?</strong> $\\to$ Adapter (convert), Facade (simplify), Bridge (decouple abstraction from implementation).",
                "<strong>Adding Behavior?</strong> $\\to$ Decorator (wrap), Proxy (access control), Composite (tree structures).",
                "<strong>Varying Algorithms or State?</strong> $\\to$ Strategy (algorithm), State (lifecycle), Observer (events), Command (undo/redo)."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Design Pattern Decision Tree",
                "classes": [
                    {
                        "name": "DesignPatternDecisionTree",
                        "is_abstract": False,
                        "attributes": [
                            "1. Creational: Factory, Builder, Singleton",
                            "2. Structural: Adapter, Decorator, Facade, Composite",
                            "3. Behavioral: Strategy, State, Observer, Command"
                        ],
                        "methods": []
                    }
                ],
                "relationships": []
            },
            "interactive_animation": {
                "title": "Interactive Pattern Selector Flow",
                "steps": [
                    {"step": 1, "description": "Need to construct an object with 10 optional parameters? -> BUILDER.", "active_nodes": ["Builder"]},
                    {"step": 2, "description": "Need to notify multiple subscribers of data changes? -> OBSERVER.", "active_nodes": ["Observer"]},
                    {"step": 3, "description": "Need to execute, queue, or undo user actions? -> COMMAND.", "active_nodes": ["Command"]}
                ]
            },
            "cpp_implementation": """// Quick Decision Tree Dispatcher Example
#include <iostream>
#include <string>

void patternSelector(const std::string& need) {
    if (need == "step_by_step_construction") std::cout << "-> Choose BUILDER PATTERN\\n";
    else if (need == "swap_algorithm") std::cout << "-> Choose STRATEGY PATTERN\\n";
    else if (need == "event_broadcast") std::cout << "-> Choose OBSERVER PATTERN\\n";
    else if (need == "state_transitions") std::cout << "-> Choose STATE PATTERN\\n";
    else if (need == "simplify_subsystem") std::cout << "-> Choose FACADE PATTERN\\n";
}

int main() {
    patternSelector("step_by_step_construction");
    patternSelector("swap_algorithm");
    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Identify the Primary Intent:</strong> Is the problem about creation, structure, or behavior?",
                "<strong>2. Match with Decision Tree:</strong> Pick the minimal pattern that solves the extensibility requirement.",
                "<strong>3. Avoid Overuse:</strong> If a plain function or enum suffices, do not introduce a complex pattern."
            ],
            "comparison_matrix": {
                "title": "Pattern Selection Quick Table",
                "headers": ["Problem Requirement", "Recommended Pattern", "C++ Implementation Mechanism"],
                "rows": [
                    ["Complex constructor with 8 parameters", "Builder", "Fluent method chaining returning `Builder&`"],
                    ["Family of related UI widgets", "Abstract Factory", "Virtual factory classes returning widget pointers"],
                    ["Tree of nested folders and files", "Composite", "Common `Component` base with `vector<unique_ptr<Component>>`"],
                    ["Dynamic condiments on coffee", "Decorator", "Wrapping `unique_ptr<Base>` recursively"],
                    ["Undoable text editor commands", "Command", "`execute()` and `unexecute()` command stack"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Using Abstract Factory when a simple Factory Method suffices", "correction": "Abstract Factory is only needed when creating *families* of related products."}
            ],
            "interview_traps": [
                "<strong>Trap: 'Why not use Builder for everything instead of constructors?'</strong><br><em>Answer:</em> Builder introduces boilerplate. For simple structs with 2-3 fields, standard constructors or C++20 designated initializers (`Point{.x=1, .y=2}`) are simpler and faster."
            ],
            "code_refactor_exercise": {
                "problem": "Select the right pattern to eliminate a 10-argument constructor.",
                "bad_code": "Car(engine, wheels, seats, gps, sunroof, stereo, color, spoiler, camera, tint);",
                "good_code": "CarBuilder().setEngine().setSunroof().build();"
            },
            "practice_problem": {
                "title": "Pattern Selection Quiz",
                "description": "Which pattern should be used to parse a mathematical Abstract Syntax Tree (AST) without modifying the AST node classes?",
                "hint": "Visitor Pattern."
            }
        },
        {
            "id": "uml-relationship-cheat-sheet",
            "title": "UML Relationships & C++ Code Mappings",
            "definition": "Visual cheat sheet mapping every UML arrow symbol (Dependency, Association, Aggregation, Composition, Generalization, Realization) to exact C++20 pointer and reference code.",
            "why_it_matters": "Instantly eliminates confusion when drawing class diagrams on whiteboards.",
            "real_world_analogy": "A translator dictionary converting English words directly into French phrases.",
            "conceptual_breakdown": [
                "<strong>Dependency ($-\\-\\succ$):</strong> Function parameter or local variable (Uses).",
                "<strong>Association ($-$):</strong> Member pointer or reference (Has-a).",
                "<strong>Aggregation ($\\diamond-$):</strong> Shared ownership (<code>std::shared_ptr</code>).",
                "<strong>Composition ($\\blacklozenge-$):</strong> Exclusive ownership (<code>std::unique_ptr</code> or direct value).",
                "<strong>Generalization ($\\triangle-$):</strong> Class inheritance (`public Base`).",
                "<strong>Realization ($-\\-\\triangle$):</strong> Interface implementation (`public IInterface`)."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "UML to C++ Translation Matrix",
                "classes": [
                    {
                        "name": "Composition_Example",
                        "is_abstract": False,
                        "attributes": ["- engine: Engine (Direct Value)", "- enginePtr: std::unique_ptr<Engine>"],
                        "methods": ["Exclusive Lifetime Bound"]
                    },
                    {
                        "name": "Aggregation_Example",
                        "is_abstract": False,
                        "attributes": ["- driver: std::shared_ptr<Driver>", "- supervisor: std::weak_ptr<Driver>"],
                        "methods": ["Independent Shared Lifetime"]
                    }
                ],
                "relationships": []
            },
            "interactive_animation": {
                "title": "UML to C++ Code Transformation",
                "steps": [
                    {"step": 1, "description": "UML: Filled Diamond (Composition) -> C++: std::unique_ptr<Engine> or direct value member.", "active_nodes": ["Composition"]},
                    {"step": 2, "description": "UML: Hollow Diamond (Aggregation) -> C++: std::shared_ptr<Department>.", "active_nodes": ["Aggregation"]},
                    {"step": 3, "description": "UML: Dashed Arrow (Dependency) -> C++: void process(const Context& ctx).", "active_nodes": ["Dependency"]}
                ]
            },
            "cpp_implementation": """// UML to C++ Mapping Reference
#include <iostream>
#include <memory>
#include <vector>

// 1. Dependency (Uses a Logger as parameter)
class ILogger { public: virtual ~ILogger() = default; virtual void log(const std::string&) = 0; };

class Service {
public:
    void doWork(ILogger& logger) { // Dependency (Dashed Arrow)
        logger.log("Working...");
    }
};

// 2. Composition (Filled Diamond -> Unique Ownership)
class Room { public: std::string name; };
class House {
private:
    std::vector<Room> rooms; // Composition (Destroying House destroys Rooms)
};

// 3. Aggregation (Hollow Diamond -> Shared Reference)
class Student {};
class Course {
private:
    std::vector<std::shared_ptr<Student>> students; // Aggregation (Students exist outside Course)
};

int main() {
    std::cout << "[UML CHEAT SHEET] All 6 UML relationship types compiled cleanly!\\n";
    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Composition:</strong> Value types or <code>std::unique_ptr</code> enforce that child dies when parent dies.",
                "<strong>2. Aggregation:</strong> <code>std::shared_ptr</code> or <code>std::weak_ptr</code> allow child to survive parent.",
                "<strong>3. Dependency:</strong> Passing via parameter prevents persistent coupling."
            ],
            "comparison_matrix": {
                "title": "UML Relationship Symbol Cheat Sheet",
                "headers": ["Relationship", "UML Symbol", "C++ Member Type", "Lifecycle Coupling"],
                "rows": [
                    ["Dependency", "Dashed open arrow `-->`", "Method parameter `(T&)`", "None (Temporary call)"],
                    ["Association", "Solid line `---`", "Raw pointer / reference", "Loose"],
                    ["Aggregation", "Hollow diamond `<>---`", "`std::shared_ptr<T>` / `weak_ptr<T>`", "Shared (Independent)"],
                    ["Composition", "Filled diamond `*---`", "`std::unique_ptr<T>` / Direct value `T`", "Strict (Parent owns Child)"],
                    ["Generalization", "Solid triangle `---|> `", "Class inheritance `class D : public B`", "Tight is-a"],
                    ["Realization", "Dashed triangle `- - -|> `", "Interface `class C : public IInterface`", "Contractual"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Drawing Composition when Aggregation is intended", "correction": "If an Employee can switch Departments without being deleted from existence, Department -> Employee is Aggregation, NOT Composition."}
            ],
            "interview_traps": [
                "<strong>Trap: 'Why should we prefer Composition over Inheritance in UML?'</strong><br><em>Answer:</em> Composition provides loose coupling, dynamic runtime swapping of behavior, avoids fragile base class hierarchies, and adheres to the Open-Closed Principle."
            ],
            "code_refactor_exercise": {
                "problem": "Convert a rigid inheritance hierarchy into a flexible composition relationship.",
                "bad_code": "class Car : public V8Engine { ... }; // Inheritance anti-pattern",
                "good_code": "class Car { private: unique_ptr<IEngine> engine; }; // Clean Composition"
            },
            "practice_problem": {
                "title": "Map UML Symbols to C++ Code",
                "description": "Given a University system with Professors, Departments, and Buildings, specify whether each link is Composition, Aggregation, or Association.",
                "hint": "University to Department (Composition), Department to Professor (Aggregation)."
            }
        },
        {
            "id": "smart-pointer-lifecycle-cheat-sheet",
            "title": "Smart Pointers Ownership Cheat Sheet",
            "definition": "Fast-reference guide for modern C++ smart pointer ownership semantics: `unique_ptr`, `shared_ptr`, `weak_ptr`, and custom deleters.",
            "why_it_matters": "Clean memory ownership is the bedrock of modern C++ LLD.",
            "real_world_analogy": "Vehicle ownership titles: 1 sole owner (`unique_ptr`), co-signers on a joint lease (`shared_ptr`), or a parking attendant with temporary inspection access (`weak_ptr`).",
            "conceptual_breakdown": [
                "<strong>std::unique_ptr:</strong> Exclusive ownership (Zero memory/CPU overhead compared to raw pointer).",
                "<strong>std::shared_ptr:</strong> Shared ownership via reference-counted control block (16 bytes: ptr + ctrl block).",
                "<strong>std::weak_ptr:</strong> Non-owning observer preventing circular reference memory leaks.",
                "<strong>make_unique / make_shared:</strong> Exception-safe single memory allocation."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Smart Pointer Reference Counting",
                "classes": [
                    {
                        "name": "SharedPtr_Instance",
                        "is_abstract": False,
                        "attributes": ["*ptr -> ManagedObject", "*ctrlBlock -> ControlBlock"],
                        "methods": []
                    },
                    {
                        "name": "ControlBlock",
                        "is_abstract": False,
                        "attributes": ["strongCount: 2", "weakCount: 1", "customDeleter"],
                        "methods": []
                    }
                ],
                "relationships": [
                    {"from": "SharedPtr_Instance", "to": "ControlBlock", "type": "association", "label": "tracks counts"}
                ]
            },
            "interactive_animation": {
                "title": "Smart Pointer Lifecycle Transitions",
                "steps": [
                    {"step": 1, "description": "std::make_shared allocates ManagedObject and ControlBlock in 1 contiguous memory block.", "active_nodes": ["make_shared"]},
                    {"step": 2, "description": "Copying shared_ptr increments strongCount to 2 with atomic increment.", "active_nodes": ["strongCount = 2"]},
                    {"step": 3, "description": "weak_ptr observes object without incrementing strongCount.", "active_nodes": ["weak_ptr", "weakCount = 1"]},
                    {"step": 4, "description": "Both shared_ptrs go out of scope -> strongCount = 0 -> Object destructor runs.", "active_nodes": ["Destructor Runs"]}
                ]
            },
            "cpp_implementation": """// Smart Pointer Cheat Sheet
#include <iostream>
#include <memory>

struct Resource {
    std::string name;
    Resource(std::string n) : name(std::move(n)) { std::cout << "Created " << name << "\\n"; }
    ~Resource() { std::cout << "Destroyed " << name << "\\n"; }
};

int main() {
    // 1. Exclusive ownership
    auto uPtr = std::make_unique<Resource>("ExclusiveResource");

    // 2. Shared ownership + Weak reference
    std::weak_ptr<Resource> wPtr;
    {
        auto sPtr = std::make_shared<Resource>("SharedResource");
        wPtr = sPtr; // Does not increment strong ref count

        if (auto locked = wPtr.lock()) {
            std::cout << "Accessed while alive: " << locked->name << "\\n";
        }
    } // sPtr destroyed here!

    if (wPtr.expired()) {
        std::cout << "Weak ptr correctly detects object was destroyed!\\n";
    }

    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Zero Overhead Unique Pointers:</strong> <code>sizeof(unique_ptr) == sizeof(void*)</code>.",
                "<strong>2. Lockable Weak Pointers:</strong> <code>wPtr.lock()</code> returns a valid <code>shared_ptr</code> if alive or <code>nullptr</code> if destroyed.",
                "<strong>3. Break Cycles:</strong> Always use <code>weak_ptr</code> for parent pointers or observer lists."
            ],
            "comparison_matrix": {
                "title": "Smart Pointer Properties",
                "headers": ["Pointer Type", "Size in Bytes (64-bit)", "Copyable", "Atomic Ref Counting Overhead", "Use Case"],
                "rows": [
                    ["std::unique_ptr<T>", "8 bytes", "No (Move only)", "Zero (No control block)", "Default exclusive ownership (90% of code)"],
                    ["std::shared_ptr<T>", "16 bytes", "Yes", "Yes (Atomic increments on copy)", "True shared ownership across threads"],
                    ["std::weak_ptr<T>", "16 bytes", "Yes", "Yes", "Breaking cycles, caches, observer registries"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Creating two independent `std::shared_ptr` from the same raw pointer", "correction": "Creates two separate control blocks leading to double deletion crash. Always use `std::make_shared`."}
            ],
            "interview_traps": [
                "<strong>Trap: 'Why does std::make_shared keep control block memory allocated if weak_ptr is still alive after object destruction?'</strong><br><em>Answer:</em> `make_shared` allocates object and control block contiguously; the object is destructed when `strongCount == 0`, but the single memory buffer cannot be freed until `weakCount == 0`."
            ],
            "code_refactor_exercise": {
                "problem": "Fix a double-free bug caused by multiple shared_ptr creations from raw pointer.",
                "bad_code": "Resource* r = new Resource(); shared_ptr<Resource> p1(r); shared_ptr<Resource> p2(r);",
                "good_code": "auto p1 = std::make_shared<Resource>(); auto p2 = p1;"
            },
            "practice_problem": {
                "title": "Design Custom Deleter for C FILE handle",
                "description": "Create a `std::unique_ptr<FILE, decltype(&fclose)>` wrapper that automatically closes files with `fclose` upon scope exit.",
                "hint": "`std::unique_ptr<FILE, int(*)(FILE*)> filePtr(fopen(\"data.txt\", \"r\"), fclose);`"
            }
        },
        {
            "id": "concurrency-safety-cheat-sheet",
            "title": "C++ Concurrency & Thread Safety Rules",
            "definition": "A 1-page condensed reference of C++ concurrency primitives: `std::mutex`, `std::shared_mutex`, `std::atomic`, memory orders, and condition variable idioms.",
            "why_it_matters": "Essential reference for writing bug-free concurrent systems in LLD interviews.",
            "real_world_analogy": "Safety checklist for high-voltage power stations: grounding rods, insulated gloves, and lock-out/tag-out switches.",
            "conceptual_breakdown": [
                "<strong>Rule 1:</strong> Always lock with RAII (`std::lock_guard`, `std::unique_lock`, `std::scoped_lock`).",
                "<strong>Rule 2:</strong> Always check condition variable predicate in a `while` loop (or use lambda predicate) to handle Spurious Wakeups.",
                "<strong>Rule 3:</strong> Use `std::shared_mutex` for high read-to-write ratios.",
                "<strong>Rule 4:</strong> Default to `std::memory_order_seq_cst` unless profiling proves atomic bottleneck.",
                "<strong>Rule 5:</strong> Use `alignas(64)` on atomics accessed by separate threads to eliminate False Sharing."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Concurrency Safety Matrix",
                "classes": [
                    {
                        "name": "ConcurrencyRules",
                        "is_abstract": False,
                        "attributes": [
                            "1. RAII Locks only (no manual unlock)",
                            "2. while(pred) for condition variables",
                            "3. scoped_lock for multiple mutexes",
                            "4. alignas(64) to prevent False Sharing"
                        ],
                        "methods": []
                    }
                ],
                "relationships": []
            },
            "interactive_animation": {
                "title": "Spurious Wakeup Defense Flow",
                "steps": [
                    {"step": 1, "description": "Consumer thread sleeps in `cv.wait(lock, []{ return !queue.empty(); })`.", "active_nodes": ["Consumer Sleeping"]},
                    {"step": 2, "description": "OS delivers Spurious Wakeup with queue still empty.", "active_nodes": ["Spurious Wakeup"]},
                    {"step": 3, "description": "Predicate evaluates false -> Thread automatically goes back to sleep!", "active_nodes": ["Safe Return to Sleep"]}
                ]
            },
            "cpp_implementation": """// Concurrency Quick Reference Skeleton
#include <iostream>
#include <mutex>
#include <condition_variable>
#include <queue>

template <typename T>
class ThreadSafeQueue {
private:
    std::queue<T> q;
    mutable std::mutex mtx;
    std::condition_variable cv;

public:
    void push(T item) {
        {
            std::lock_guard<std::mutex> lock(mtx);
            q.push(std::move(item));
        }
        cv.notify_one();
    }

    T pop() {
        std::unique_lock<std::mutex> lock(mtx);
        // Lambda predicate guards against spurious wakeups!
        cv.wait(lock, [this]() { return !q.empty(); });

        T val = std::move(q.front());
        q.pop();
        return val;
    }
};

int main() {
    ThreadSafeQueue<int> queue;
    queue.push(42);
    std::cout << "[CONCURRENCY CHEAT SHEET] Popped item: " << queue.pop() << "\\n";
    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. RAII Locks:</strong> <code>std::lock_guard</code> in push, <code>std::unique_lock</code> in pop.",
                "<strong>2. Spurious Wakeup Protection:</strong> <code>cv.wait</code> with lambda predicate automatically loops until <code>!q.empty()</code> is true.",
                "<strong>3. Move Semantics:</strong> <code>std::move()</code> transfers elements without costly copies."
            ],
            "comparison_matrix": {
                "title": "Thread Synchronization Primitives",
                "headers": ["Primitive", "Use Case", "Performance", "Deadlock Risk"],
                "rows": [
                    ["std::mutex", "Exclusive mutual exclusion", "Fast (Futex in user space if uncontended)", "Moderate if multiple mutexes"],
                    ["std::shared_mutex", "Many concurrent readers, few writers", "Optimal for Read-Heavy workloads", "Moderate"],
                    ["std::atomic<T>", "Single variable counters / flags", "Hardware instruction level (< 5ns)", "Zero (Lock-free)"],
                    ["std::condition_variable", "Signaling thread state changes", "Zero CPU spin while sleeping", "Low"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Using `cv.wait(lock)` without checking a predicate in a loop", "correction": "Spurious wakeups from the OS kernel can wake the thread while the queue is still empty, causing segfaults."}
            ],
            "interview_traps": [
                "<strong>Trap: 'Why does cv.wait require std::unique_lock instead of std::lock_guard?'</strong><br><em>Answer:</em> `cv.wait()` must be able to atomically release the mutex when entering sleep and re-acquire it upon waking up. `std::lock_guard` cannot be unlocked and re-locked."
            ],
            "code_refactor_exercise": {
                "problem": "Fix a condition variable wait susceptible to spurious wakeups.",
                "bad_code": "if (q.empty()) cv.wait(lock); // Insecure if spurious wakeup occurs",
                "good_code": "cv.wait(lock, [&]() { return !q.empty(); });"
            },
            "practice_problem": {
                "title": "Design Read-Write Spinlock using std::atomic",
                "description": "Implement a custom `RWSpinLock` using `std::atomic<int>` where positive integer represents number of active readers and -1 represents exclusive writer.",
                "hint": "Use `compare_exchange_weak` in a busy loop."
            }
        }
    ]
}

modules = [m20, m21, m22, m23, m24]
for m in modules:
    mod_id = m["module_id"]
    file_path = os.path.join(content_dir, f"module_{int(mod_id):02d}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print(f"Generated {os.path.basename(file_path)} with {len(m['topics'])} topics")
