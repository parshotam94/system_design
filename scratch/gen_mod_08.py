"""
Elaborate generator for Module 08: Caching Strategies & Distributed Caches
"""
import json
from pathlib import Path

m08 = {
  "module_id": "08",
  "module_title": "Caching Strategies & Distributed Caches",
  "description": "Master cache topologies, write policies (Cache-Aside, Write-Through, Write-Back), Redis vs Memcached architecture, eviction policies (LRU/LFU), and stampede/avalanche prevention.",
  "topics": [
    {
      "id": "caching-fundamentals-and-locality",
      "title": "Caching Fundamentals: Hits, Misses, TTL & Eviction Policies (LRU/LFU)",
      "definition": "Caching is the practice of storing copies of data in high-speed, temporary storage (typically in-memory RAM) so that future requests can be served orders of magnitude faster than querying primary disk-bound databases or remote network APIs. Eviction policies (LRU, LFU, FIFO) govern which keys are purged when memory limits are reached.",
      "why_we_need_it": "RAM access latency is ~100 nanoseconds; SSD NVMe storage latency is ~100 microseconds (1,000x slower); rotational hard disk or cross-network database queries take 5-50 milliseconds (50,000x slower). Caching leverages the 80/20 rule (Pareto principle: 80% of read traffic accesses 20% of data) to protect databases from overwhelming QPS.",
      "real_world_analogy": "A scholar working in a massive library: The library archives (Database on disk) hold 5 million books. The scholar's desktop desk (In-Memory Cache) holds the 5 books they are actively referencing right now. When the desk gets full, they put the least recently read book back on the shelf (LRU Eviction) to make room for a new one.",
      "how_it_works": "<p>1. <strong>Locality of Reference:</strong> Caching exploits two fundamental computational properties: <em>Temporal Locality</em> (data accessed recently is likely to be accessed again soon) and <em>Spatial Locality</em> (data stored near recently accessed items is likely to be accessed soon).</p><p>2. <strong>Time-To-Live (TTL):</strong> Every cached key can have an expiration timestamp. When TTL elapses, the key becomes invalid and is either lazily deleted on next read or proactively pruned by a background expiration thread.</p><p>3. <strong>LRU (Least Recently Used) Internals:</strong> Implemented via a combination of a Hash Map (for O(1) key lookup) and a Doubly-Linked List (for O(1) node removal and head-insertion). When a key is read or updated, its node moves to the head. When capacity is exceeded, the node at the tail is evicted.</p><p>4. <strong>LFU (Least Frequently Used) Internals:</strong> Tracks access frequency counters for every key. Evicts the key with the lowest hit counter. Advanced variants like <em>TinyLFU</em> and <em>W-TinyLFU</em> (used in Caffeine cache) use Count-Min Sketches to track frequency with tiny memory footprints while maintaining resistance to one-hit-wonder frequency pollutions.</p><p>5. <strong>ARC (Adaptive Replacement Cache):</strong> Dynamically tunes between recency (LRU) and frequency (LFU) using dual cache lists, achieving optimal hit ratios across shifting production workloads.</p>",
      "conceptual_breakdown": [
        "<strong>Cache Hit Ratio:</strong> Metric calculated as Hits / (Hits + Misses). Production systems target >95% hit rates for stable read-heavy services.",
        "<strong>LRU Doubly-Linked List:</strong> Enables O(1) operations: moving accessed items to the front and evicting cold items from the tail without traversing memory.",
        "<strong>TTL vs Event-Driven Invalidation:</strong> TTL guarantees eventual expiration but tolerates stale data for the duration of the TTL. Event-driven invalidation purges keys immediately upon database mutation, guaranteeing freshness at the cost of invalidation complexity.",
        "<strong>Cold Start Penalty:</strong> When a fresh cache cluster starts with empty memory, the hit ratio is 0%, causing 100% of read traffic to hammer the primary database until the cache warms up."
      ],
      "arch_diagram": {
        "title": "LRU In-Memory Cache Mechanics (Hash Map + Doubly-Linked List)",
        "tiers": [
          {
            "label": "Hash Map Index (O(1) Access)",
            "nodes": [
              {
                "name": "Key Index Table",
                "type": "cache",
                "icon": "🗂️",
                "what": "Hash Map mapping Key -> Node Pointer",
                "why": "Instant O(1) memory lookup",
                "when": "Every cache GET / SET",
                "failure": "Rehashes bucket on collision"
              }
            ]
          },
          {
            "label": "Doubly Linked List (Recency Order)",
            "nodes": [
              {
                "name": "Head (Most Recently Used)",
                "type": "service",
                "icon": "🔥",
                "what": "MRU Node: 'user:101'",
                "why": "Accessed 2 seconds ago",
                "when": "Moved to head on every read/write",
                "failure": "Prevents eviction"
              },
              {
                "name": "Tail (Least Recently Used)",
                "type": "service",
                "icon": "❄️",
                "what": "LRU Node: 'user:104'",
                "why": "Accessed 4 hours ago",
                "when": "Evicted instantly when memory limit hits",
                "failure": "Freed from memory"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Cache Eviction Policies Comparison",
        "columns": ["Policy", "Eviction Criteria", "Data Structure", "Best Use Case", "Weakness"],
        "rows": [
          ["LRU (Least Recently Used)", "Oldest access timestamp", "Hash Map + Doubly-Linked List", "General web and API workloads", "Vulnerable to single full-table scan flushing cache"],
          ["LFU (Least Frequently Used)", "Lowest total hit count", "Hash Map + Frequency Buckets", "Stable long-term popularity", "Old historic keys hold onto slots even if no longer accessed"],
          ["FIFO (First In First Out)", "Oldest insertion timestamp", "Simple Queue", "Streaming time-ordered logs", "Frequently accessed popular keys get purged prematurely"],
          ["W-TinyLFU", "Window LRU + Count-Min Sketch", "Dual Ring + Bloom Filter Sketch", "High-throughput Java/Go microservices", "Higher algorithmic implementation complexity"]
        ]
      },
      "tradeoffs": "<strong>LRU vs LFU:</strong> LRU is simple and adapts quickly to shifting trends, but a batch job doing a full scan can flush out all hot data in seconds. LFU resists scan-pollution because new cold items have access count = 1, but historic keys with 10,000 hits can become 'zombies' that never get evicted even when their popularity drops to zero.",
      "failure_scenarios": "<strong>Batch Scan Cache Flushing:</strong> A nightly analytical cron job executes `SELECT * FROM users` and iterates through 10 million rows, populating the cache with keys that will never be read again. In doing so, it evicts all real user session keys, dropping the production cache hit ratio from 98% to 5% and overwhelming the primary database. <em>Mitigation:</em> Bypass the cache for analytical batch jobs using a dedicated read-replica or use W-TinyLFU eviction.",
      "common_mistakes": [
        {"mistake": "Setting no TTL on cached keys, relying entirely on memory eviction policies.", "correction": "Always configure a sane TTL on every key. Even if eviction is configured, stale or orphaned keys from deleted entities will waste precious RAM indefinitely."},
        {"mistake": "Caching large binary objects (e.g., 50MB PDF files or raw video) directly inside Redis.", "correction": "Store large binary files in object storage (AWS S3) and cache only metadata and CDN presigned URLs in Redis."}
      ],
      "interview_questions": [
        {"question": "How would you implement an LRU Cache in code with O(1) time complexity for both get and put operations?", "answer": "Use a <strong>Hash Map combined with a Doubly-Linked List</strong>. The Hash Map stores the key as the hash key, and the value is a pointer to the corresponding node in the Doubly-Linked List. `get(key)` looks up the node in O(1), unlinks it from the list, and attaches it at the head. `put(key, value)` adds or updates the node at the head. If capacity is exceeded, remove the tail node from both the list and the hash map in O(1)."},
        {"question": "What is the difference between active and passive cache expiration in Redis?", "answer": "In <strong>passive expiration</strong>, Redis only checks the TTL of a key when a client attempts to read it. If expired, it deletes the key and returns null. In <strong>active expiration</strong>, Redis runs a periodic background task (10 times per second) that randomly samples 20 keys with TTLs, deletes expired ones, and repeats until fewer than 25% of sampled keys are expired."}
      ]
    },
    {
      "id": "caching-patterns-and-write-strategies",
      "title": "Caching Patterns: Cache-Aside, Read-Through, Write-Through, Write-Back & Write-Around",
      "definition": "Caching patterns dictate how the application, cache layer, and database interact during read and write operations. The primary strategies are Cache-Aside (Lazy Loading), Read-Through, Write-Through, Write-Back (Write-Behind), and Write-Around.",
      "why_we_need_it": "Dual-write problems and race conditions between caches and databases frequently lead to data inconsistency (e.g., database has updated balance $100, but cache retains stale balance $50). Choosing the correct caching pattern ensures the right balance of write latency, read throughput, and data freshness.",
      "real_world_analogy": "Updating a public library: Cache-Aside is the student asking the librarian for a book; if not on the reserve shelf, the student walks to the deep basement stacks, grabs it, and puts a photocopy on the reserve shelf. Write-Back is taking notes on a scratchpad and only typing up the final published manuscript into the archive once every evening.",
      "how_it_works": "<p>1. <strong>Cache-Aside (Lazy Loading):</strong> The application coordinates cache and database. On read: query Cache first; if hit, return; if miss, query DB, write result to Cache with TTL, and return. On write: write to DB, and then <em>delete</em> (invalidate) the key from the Cache.</p><p>2. <strong>Read-Through:</strong> The application treats the cache as the primary data store. On a cache miss, the cache infrastructure automatically loads missing data from the database, caches it, and returns it to the client.</p><p>3. <strong>Write-Through:</strong> The application writes to the Cache. The Cache synchronously writes to the Database in the same transaction before returning success. Freshness is guaranteed, but write latency includes two network hops.</p><p>4. <strong>Write-Back (Write-Behind):</strong> The application writes directly to the in-memory Cache and receives immediate success (&lt;1ms). The cache asynchronously queues and batch-persists mutations to the database in background intervals. High write throughput, but risks data loss if the cache node crashes before flushing.</p><p>5. <strong>Write-Around:</strong> Writes go directly to the Database, completely bypassing the Cache. Only reads populate the cache via Cache-Aside.</p>",
      "conceptual_breakdown": [
        "<strong>Cache Invalidation vs Updating:</strong> On a database update, always <em>DELETE (invalidate)</em> the cache key rather than writing the new value into the cache. Updating the cache introduces race conditions where concurrent writes can overwrite fresh cache data with stale values.",
        "<strong>Write-Back Durability Risk:</strong> Write-Back transforms the cache into a transient single point of data loss. If power fails before the flush worker runs, data is permanently lost.",
        "<strong>Dual-Write Inconsistency:</strong> If an application updates the DB and crashes before evicting the cache, the cache serves stale data until TTL expires.",
        "<strong>Cache-Aside Simplicity:</strong> The de facto standard in microservices because it works with any existing database without requiring custom cache-to-DB plugin adapters."
      ],
      "arch_diagram": {
        "title": "Caching Write Patterns Topology",
        "tiers": [
          {
            "label": "Application Layer",
            "nodes": [
              {
                "name": "App Service",
                "type": "service",
                "icon": "⚙️",
                "what": "Executes domain logic",
                "why": "Coordinates cache and persistence layers",
                "when": "Client requests",
                "failure": "Fallback to database on cache failure"
              }
            ]
          },
          {
            "label": "In-Memory Caching Tier",
            "nodes": [
              {
                "name": "Redis Cache Cluster",
                "type": "cache",
                "icon": "⚡",
                "what": "In-Memory Key-Value Store",
                "why": "Sub-millisecond read access",
                "when": "Cache-Aside read checks & Write-Through",
                "failure": "Read replica failover via Sentinel"
              }
            ]
          },
          {
            "label": "Primary Persistence Tier",
            "nodes": [
              {
                "name": "PostgreSQL Primary",
                "type": "database",
                "icon": "🐘",
                "what": "ACID Relational Database",
                "why": "Authoritative persistent storage on disk",
                "when": "Cache miss or DB writes",
                "failure": "Synchronous standby promotion"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Caching Strategies Comparison Matrix",
        "columns": ["Strategy", "Read Latency", "Write Latency", "Data Freshness", "Risk of Data Loss"],
        "rows": [
          ["Cache-Aside", "Low on hit, High on miss", "Low (writes only to DB, invalidates cache)", "Eventually consistent (bounded by TTL)", "Zero data loss (DB is source of truth)"],
          ["Read-Through", "Low on hit, High on miss", "N/A (Read strategy only)", "Always synchronized via cache provider", "Zero data loss"],
          ["Write-Through", "Ultra-low (data is pre-warmed)", "High (synchronous dual write: Cache + DB)", "Strictly consistent between cache and DB", "Zero data loss"],
          ["Write-Back", "Ultra-low", "Blazing fast (<1ms in-memory ACK)", "Inconsistent until background flush completes", "High (crashed cache loses unwritten writes)"],
          ["Write-Around", "High on first read (always miss)", "Fast (single write directly to DB)", "Stale if key exists in cache without eviction", "Zero data loss"]
        ]
      },
      "tradeoffs": "<strong>Cache-Aside:</strong> Pros: Resilient to cache failure (app gracefully degrades to DB), only caches actually requested data. Cons: Cache miss penalty on first read, potential for stale reads if invalidation fails. <strong>Write-Back:</strong> Pros: Massive write throughput absorption. Cons: Extreme data loss risk if the cache process crashes.",
      "failure_scenarios": "<strong>Race Condition on Cache Update:</strong> Thread 1 writes new balance $100 to DB. Thread 2 writes $200 to DB. Due to network jitter, Thread 2 updates Redis first with $200, and Thread 1 updates Redis with $100. Cache permanently holds stale $100 while DB holds $200! <em>Mitigation:</em> Never update cache on writes—always <strong>DELETE</strong> the cache key: `redis.del(key)`.",
      "common_mistakes": [
        {"mistake": "Updating the cache value on every database write instead of invalidating (deleting) the key.", "correction": "Always delete the key from the cache (`DEL key`). Let the next read lazily repopulate fresh state to avoid concurrency write race conditions."},
        {"mistake": "Using Write-Back caching for financial balances or checkout transactions.", "correction": "Write-Back should only be used for loss-tolerant high-throughput data (e.g., video view counters, game telemetry). Never use it for financial ledgers."}
      ],
      "interview_questions": [
        {"question": "Why should you delete a cache entry instead of updating it during a database write?", "answer": "Deleting the key avoids <strong>concurrent write race conditions</strong>. If two requests update the database in order A then B, but network delays cause the cache updates to arrive in order B then A, the cache will permanently store stale value A while the database stores value B. Evicting the key ensures the subsequent read atomically fetches authoritative database state."},
        {"question": "How does Facebook's Tao handle cache consistency across global data centers?", "answer": "Tao uses <strong>Cache-Aside with asynchronous invalidation via database replication logs</strong>. When a write hits the primary MySQL database, a tailer daemon reads the MySQL binlog and broadcasts invalidation messages to regional caching tiers. To prevent stale reads during replication lag, clients receive a version token that routes subsequent reads to the primary until the replica catches up."}
      ]
    },
    {
      "id": "redis-vs-memcached-distributed-cache",
      "title": "Distributed Caching: Redis Architecture vs Memcached",
      "definition": "Redis and Memcached are the two dominant distributed in-memory data stores. Memcached is a high-throughput, multi-threaded, pure key-value memory engine. Redis is an advanced in-memory data structure server offering rich data types (Strings, Lists, Sets, Hashes, Sorted Sets, Bitmaps, Streams), disk persistence, replication, and clustering.",
      "why_we_need_it": "Single-server caches are bounded by the RAM of a single physical box (e.g., 256GB). Distributed caching partitions data across dozens of nodes, unlocking terabytes of in-memory storage, hundreds of thousands of operations per second, and automatic failover redundancy.",
      "real_world_analogy": "Memcached is a high-speed highway toll booth with 16 parallel lanes: pure, simple, fast, and multi-threaded, but it only accepts exact cash and has no memory of past cars. Redis is a multi-service airport terminal: it handles cargo, passports, currency exchange, lockers, and flights, complete with backup power generators and black box flight recorders.",
      "how_it_works": "<p>1. <strong>Concurrency Models:</strong> Memcached uses a multi-threaded architecture with event-driven libevent I/O and fine-grained mutex locks. It scales near-linearly across multiple CPU cores. Redis uses a single-threaded event loop (multiplexed via epoll/kqueue) for command execution, eliminating mutex contention. Redis 6.0+ introduced multi-threaded I/O purely for socket network parsing.</p><p>2. <strong>Data Structures:</strong> Memcached only stores raw binary strings up to 1MB. Redis natively supports Strings, Hashes, Lists, Sets, Sorted Sets (Skip Lists for leaderboards), HyperLogLogs, and Geospatial indexes.</p><p>3. <strong>Persistence Options:</strong> Redis supports RDB (point-in-time snapshots) and AOF (Append-Only File logging every write command). Memcached is 100% ephemeral: if it restarts, all data is lost.</p><p>4. <strong>Redis Cluster (Sharding):</strong> Partitions keys across 16,384 virtual Hash Slots using CRC16: Slot = CRC16(key) mod 16384. Master nodes own subsets of slots and have asynchronous read replicas. Automatic failover occurs via Raft-like quorum voting.</p><p>5. <strong>Memory Management:</strong> Memcached uses a Slab Allocator to prevent memory fragmentation. Redis uses jemalloc/tcmalloc, dynamically allocating memory as data structures expand.</p>",
      "conceptual_breakdown": [
        "<strong>Single-Threaded Atomicity:</strong> Redis commands like `INCR`, `HSET`, and Lua scripts are guaranteed 100% atomic without requiring application-level distributed locks.",
        "<strong>Hash Tags {} in Redis Cluster:</strong> Putting curly braces in keys (`{user:123}:profile` and `{user:123}:orders`) forces both keys to hash to the exact same hash slot, allowing multi-key transactions within a sharded cluster.",
        "<strong>Replication Lag:</strong> Redis replication is asynchronous. If a master dies before replicating, the write is lost (eventual consistency).",
        "<strong>Sub-Millisecond Execution:</strong> Because all operations execute directly in L1/L2 CPU cache and system RAM, Redis commands complete in 50 to 500 microseconds."
      ],
      "arch_diagram": {
        "title": "Redis Cluster Architecture (16,384 Hash Slots & Master-Replica Topology)",
        "tiers": [
          {
            "label": "Client Layer",
            "nodes": [
              {
                "name": "Cluster-Aware Client",
                "type": "client",
                "icon": "💻",
                "what": "Caches Hash Slot-to-Node Map",
                "why": "Directly routes CRC16(key) to target master",
                "when": "Client read/write",
                "failure": "Follows MOVED / ASK redirects"
              }
            ]
          },
          {
            "label": "Sharded Master Tier (16,384 Slots)",
            "nodes": [
              {
                "name": "Master Node 1",
                "type": "cache",
                "icon": "🔴",
                "what": "Slots 0 - 5460",
                "why": "Handles writes & primary reads",
                "when": "Key in slot range",
                "failure": "Replica 1 promotes to Master"
              },
              {
                "name": "Master Node 2",
                "type": "cache",
                "icon": "🔵",
                "what": "Slots 5461 - 10922",
                "why": "Handles writes & primary reads",
                "when": "Key in slot range",
                "failure": "Replica 2 promotes to Master"
              },
              {
                "name": "Master Node 3",
                "type": "cache",
                "icon": "🟢",
                "what": "Slots 10923 - 16383",
                "why": "Handles writes & primary reads",
                "when": "Key in slot range",
                "failure": "Replica 3 promotes to Master"
              }
            ]
          },
          {
            "label": "Asynchronous Replica Tier",
            "nodes": [
              {
                "name": "Replica Node 1",
                "type": "cache",
                "icon": "🛡️",
                "what": "Async Standby for Master 1",
                "why": "High availability & read scaling",
                "when": "Continuous async replication stream",
                "failure": "Resynchronizes via PSYNC"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Redis vs Memcached Comparison Matrix",
        "columns": ["Feature", "Redis", "Memcached"],
        "rows": [
          ["Thread Architecture", "Single-threaded execution loop (Multi-threaded I/O in v6+)", "True Multi-threaded (scales linearly with CPU cores)"],
          ["Data Structures", "Strings, Lists, Sets, Hashes, Sorted Sets, Streams, Bitmaps", "Pure Key-Value Strings only"],
          ["Persistence to Disk", "Yes: RDB Snapshots + AOF (Append-Only File)", "No: 100% In-Memory volatile only"],
          ["Clustering & Sharding", "Native Redis Cluster (16,384 Hash Slots, auto-failover)", "Client-side consistent hashing only"],
          ["Pub/Sub & Streaming", "Native Pub/Sub, Redis Streams with Consumer Groups", "No message brokering capabilities"],
          ["Maximum Value Size", "512 MB per key/string", "1 MB default"]
        ]
      },
      "tradeoffs": "<strong>Choose Memcached when:</strong> You have a simple read-heavy key-value workload, require linear multi-threaded scaling on massive multi-core servers (32+ cores), and need zero operational complexity. <strong>Choose Redis when:</strong> You need complex data types (e.g. leaderboards with ZSETs), disk persistence, atomic operations, Pub/Sub messaging, or native high-availability clustering.",
      "failure_scenarios": "<strong>Redis AOF Fsync Disk Stalls:</strong> Configuring Redis with `appendfsync always` forces a synchronous disk write on every single command. When running on cloud EBS volumes with burst limits, disk write queues fill up, blocking the single-threaded Redis event loop for 100+ milliseconds and freezing all read traffic. <em>Mitigation:</em> Configure `appendfsync everysec` or use read-replicas for persistence offloading.",
      "common_mistakes": [
        {"mistake": "Running the `KEYS *` command in a production Redis instance with 10 million keys.", "correction": "`KEYS *` blocks the single-threaded event loop for seconds, completely freezing production traffic. Always use cursor-based non-blocking `SCAN` instead."},
        {"mistake": "Treating Redis as your primary authoritative database without secondary backups.", "correction": "Redis replication is asynchronous and memory-constrained. Always use a durable database (Postgres, DynamoDB) as source of truth."}
      ],
      "interview_questions": [
        {"question": "How does Redis achieve high performance despite being largely single-threaded?", "answer": "1. <strong>In-Memory Operations:</strong> All operations run purely in RAM, eliminating disk I/O bottlenecks.<br>2. <strong>Non-Blocking I/O Multiplexing:</strong> Uses `epoll` (Linux) or `kqueue` (BSD) to monitor thousands of concurrent client sockets on a single thread.<br>3. <strong>Zero Lock Contention:</strong> Eliminates mutex locks, semaphores, context switching, and thread synchronization overhead.<br>4. <strong>Efficient Data Structures:</strong> Optimized implementations like Skip Lists (ZSET), IntSets, and ZipLists reduce memory footprint."},
        {"question": "What happens when a Redis master node crashes in Redis Cluster?", "answer": "The cluster nodes detect the failure via Gossip heartbeats. If a majority of master nodes fail to receive a heartbeat from Master A within `cluster-node-timeout`, Master A is declared `FAIL`. Replicas of Master A hold an election; the replica with the most up-to-date replication offset requests votes from the remaining masters. Upon receiving majority approval, the replica is promoted to Master and assumes ownership of Master A's hash slots."}
      ]
    },
    {
      "id": "cache-stampede-avalanche-penetration",
      "title": "Cache Traps: Stampede, Avalanche, Penetration, Hot Key Mitigation & Mutex Locks",
      "definition": "Production cache systems are vulnerable to four catastrophic failure modes: Cache Stampede (Thundering Herd), Cache Avalanche, Cache Penetration, and Cache Breakdown (Hot Key Expiry). Understanding the algorithmic defenses for each is essential for high-availability system architecture.",
      "why_we_need_it": "A single expired cache key for a popular entity (e.g., a viral tweet or Black Friday deal) can unleash 50,000 concurrent database queries within 100 milliseconds, overwhelming the database connection pool, sending CPU to 100%, and causing a total site outage.",
      "real_world_analogy": "A physical ticket booth: Cache Stampede is 10,000 fans rushing the customer service counter at the exact second the scoreboard turns off. Cache Penetration is prank callers continuously asking for a non-existent employee name, forcing the receptionist to walk back to the filing room 100,000 times a day to verify that the person doesn't exist.",
      "how_it_works": "<p>1. <strong>Cache Stampede (Thundering Herd):</strong> Occurs when a high-traffic key expires. Thousands of concurrent requests experience a cache miss simultaneously and all query the database in parallel. <em>Fix:</em> Distributed Mutex Locking (via `SET NX EX`), or <strong>Probabilistic Early Expiration (XFetch algorithm)</strong> where the cache begins asynchronously recomputing the key in the background shortly before its actual TTL expires.</p><p>2. <strong>Cache Avalanche:</strong> Occurs when thousands of different cache keys are saved with the <em>exact same TTL</em> (e.g., 3600 seconds). When the hour strikes, all keys expire at the same instant, sending all traffic directly to the database. <em>Fix:</em> Add <strong>Randomized Jitter</strong> to every TTL: Actual TTL = Base TTL + Random(-300s, +300s).</p><p>3. <strong>Cache Penetration:</strong> Malicious or buggy clients query keys that <em>do not exist in either cache or database</em> (`GET /user/-99999`). Every request bypasses the cache and hits the database. <em>Fix:</em> <strong>Bloom Filters</strong> placed in front of cache to reject non-existent keys in O(1) memory, or <strong>Cache Null Values</strong> with a short TTL (e.g. 60 seconds).</p><p>4. <strong>Cache Breakdown (Hot Spot Key):</strong> A single key that receives 200,000 QPS maxes out the network bandwidth of the single Redis node hosting that key. <em>Fix:</em> Add local in-memory L1 cache on the application servers, or replicate the hot key with randomized suffixes: `key_copy_1`, `key_copy_2` across different Redis shards.</p>",
      "conceptual_breakdown": [
        "<strong>Bloom Filter Guarantees:</strong> Probabilistic data structure that returns either 'Definitely Not in Set' (100% guaranteed) or 'Probably in Set' (tunable false positive rate, e.g., 1%). Non-existent keys are rejected before ever touching the database.",
        "<strong>Distributed Lock (SETNX):</strong> Only the first worker that acquires `SET lock:key token NX EX 5` queries the database and repopulates the cache. All other concurrent workers sleep and retry, reading the fresh cache entry.",
        "<strong>TTL Jitter Formula:</strong> TTL = base_ttl + rand(0, jitter). Prevents synchronized mass expiration cliffs.",
        "<strong>Multi-Tier Caching (L1 + L2):</strong> L1 cache is local in-process memory (Guava / Caffeine in RAM, 0ms latency); L2 cache is distributed Redis (network hop, 1ms latency). Protects Redis from hot-key network saturation."
      ],
      "arch_diagram": {
        "title": "Comprehensive Cache Defense Architecture (Bloom Filter + Mutex + L1/L2)",
        "tiers": [
          {
            "label": "Ingress & Edge Guard",
            "nodes": [
              {
                "name": "Bloom Filter",
                "type": "gateway",
                "icon": "🌸",
                "what": "Bit Array in Redis / App Memory",
                "why": "Eliminates Cache Penetration for non-existent IDs",
                "when": "Before querying cache",
                "failure": "Reconstruct from database on reboot"
              },
              {
                "name": "L1 App Cache (Caffeine)",
                "type": "cache",
                "icon": "⚡",
                "what": "In-process memory (10,000 hot keys)",
                "why": "Absorbs Hot Key bursts (0ms, zero network)",
                "when": "Ultra-hot keys",
                "failure": "Falls back to L2 Redis"
              }
            ]
          },
          {
            "label": "Distributed Caching (L2)",
            "nodes": [
              {
                "name": "Redis L2 Cluster",
                "type": "cache",
                "icon": "🗄️",
                "what": "Distributed Shared Cache",
                "why": "Shared cache with Jittered TTLs",
                "when": "L1 miss",
                "failure": "Promotes replica"
              },
              {
                "name": "Distributed Mutex Lock",
                "type": "lb",
                "icon": "🔒",
                "what": "Redis SET NX EX Lock",
                "why": "Ensures only 1 thread rebuilds cache on miss",
                "when": "Cache miss detection",
                "failure": "Lock expires after 5s TTL"
              }
            ]
          },
          {
            "label": "Protected Persistence Tier",
            "nodes": [
              {
                "name": "Database Cluster",
                "type": "database",
                "icon": "🐘",
                "what": "PostgreSQL / MySQL",
                "why": "Authoritative persistent store",
                "when": "Queried ONLY by the 1 lock-holder thread",
                "failure": "Protected from connection spikes"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Cache Attack Modes & Defense Strategies Matrix",
        "columns": ["Failure Mode", "Root Cause", "Symptoms", "Primary Defense", "Secondary Defense"],
        "rows": [
          ["Cache Stampede (Thundering Herd)", "A single hot key expires under massive concurrent QPS", "Thousands of parallel DB queries for 1 key; DB CPU spikes to 100%", "Distributed Mutex Lock (SETNX)", "Probabilistic Early Expiration (XFetch algorithm)"],
          ["Cache Avalanche", "Massive volume of keys expire at the exact same second", "Global cache hit ratio plunges to 0%; total database collapse", "Add Randomized Jitter to all TTLs (+/- 10-20%)", "Pre-warming cache before major launch events"],
          ["Cache Penetration", "Queries for keys that do not exist in DB or Cache", "High constant database read load on non-existent records", "Bloom Filter at ingress tier", "Cache Null values with short 60s TTL"],
          ["Cache Breakdown (Hot Key)", "Single key receives 500k+ QPS, saturating 1 Redis node NIC", "Single Redis node network bandwidth saturated, packet drops", "Local L1 in-process memory cache (Caffeine)", "Key Splitting: key_1, key_2 across shards"]
        ]
      },
      "tradeoffs": "<strong>Bloom Filters:</strong> Pros: Drastically reduces database load from rogue non-existent queries, tiny memory footprint. Cons: Cannot easily delete items from standard Bloom filters without using complex Counting Bloom Filters, and requires periodic synchronization with the database.",
      "failure_scenarios": "<strong>The Synchronized Midnight Avalanche:</strong> An e-commerce developer sets all product cache TTLs to `expires_at = midnight`. At 00:00:00 UTC, 500,000 product cache entries expire simultaneously. Flash-sale traffic arrives at 00:00:01, producing 80,000 database queries per second. The primary database pool crashes, and the web app displays HTTP 500 across the entire storefront for 45 minutes. <em>Mitigation:</em> Mandatory TTL jittering: `ttl = 86400 + rand(-3600, 3600)`.",
      "common_mistakes": [
        {"mistake": "Setting static TTL values like exactly 60 minutes across all entities.", "correction": "Always apply a jitter multiplier: `ttl = base_ttl + (Math.random() * jitter_range)`."},
        {"mistake": "Not caching negative / null responses when a database query returns no record.", "correction": "If an ID is not found, write `cache.set(key, 'NULL', 60)` to prevent the client from repeatedly bypassing the cache."}
      ],
      "interview_questions": [
        {"question": "How does the XFetch algorithm prevent cache stampedes without explicit distributed locks?", "answer": "The XFetch algorithm evaluates: delta - beta * ln(random()) > TTL. As the key nears expiration, the probability that an incoming read initiates an <strong>asynchronous background refresh</strong> approaches 1.0. The first lucky request kicks off background recomputation while immediately returning the stale cached value to the user, preventing any blocking thundering herd."},
        {"question": "How does a Bloom Filter work and what are its memory characteristics?", "answer": "A Bloom Filter consists of a bit array of size m initialized to all 0s, and k independent hash functions. When adding an element, compute all k hashes and set the corresponding bit positions to 1. To query an element, check if all k bits are 1. If any bit is 0, the item is <strong>definitely not in the set</strong>. It uses ~10 bits per item for a 1% false positive rate, requiring only 1.2MB of RAM to index 1,000,000 items."}
      ]
    }
  ]
}

with open(Path('content/hld/module_08.json'), 'w', encoding='utf-8') as f:
    json.dump(m08, f, ensure_ascii=False, indent=2)
print("Module 08 written successfully!")
