import json
import os

CONTENT_DIR = "content/hld"
os.makedirs(CONTENT_DIR, exist_ok=True)

# -------------------------------------------------------------
# MODULE 26: Real-World Case Studies 3: E-Commerce & Ridesharing
# -------------------------------------------------------------
mod_26 = {
  "module_id": "26",
  "module_title": "Real-World Case Studies 3: E-Commerce & Ridesharing",
  "description": "End-to-end interview blueprints: Design Uber / Lyft (Geo-spatial indexing with H3/S2 & matching engine), Amazon Flash Sale Checkout (High concurrency inventory lock), and Stripe Idempotent Payment Gateway.",
  "topics": [
    {
      "id": "design-uber-ridesharing-system",
      "title": "Case Study: Design Uber / Lyft (Geospatial Indexing & Driver-Rider Matching Engine)",
      "definition": "Design a real-time ride-matching and location-tracking system supporting 100 million active riders, 5 million drivers reporting GPS coordinates every 4 seconds, and matching riders to the closest available drivers with sub-second latency.",
      "why_we_need_it": "Classic interview problem testing high-throughput geospatial time-series indexing (Uber H3 / Google S2 / QuadTrees), WebSocket connection fleets, and distributed ride state machine workflows.",
      "real_world_analogy": "A city traffic grid divided into thousands of hexagonal honeycomb tiles: drivers broadcast which hexagon tile they are currently inside. When a rider calls a taxi, the system checks their immediate hexagon and surrounding adjacent hexagons to find available cabs.",
      "how_it_works": "<p>1. <strong>Location Ingestion (5M drivers x 0.25 GPS/sec = 1.25M updates/sec):</strong> Drivers stream GPS `(lat, lon, driver_id, status)` via WebSockets/gRPC to Location Gateway servers -> Location Gateway updates in-memory Redis Geospatial / H3 spatial cluster.<br>2. <strong>Geospatial Indexing (Uber H3 Hexagons):</strong> Divides the Earth's surface into discrete hexagonal hierarchical cells (Resolution 7-9: ~100m to 1km radius). Hexagons provide uniform adjacent neighbor distances (unlike squares).<br>3. <strong>Ride Request & Matching:</strong> Rider requests pickup at `(lat, lon)`. Matching service converts rider lat/lon to H3 Cell ID -> queries Redis for available drivers within that Cell + 6 neighboring cells -> sorts by Estimated Time of Arrival (ETA) via routing engine -> sends dispatch offer to closest driver with a 15-second acceptance timer.</p>",
      "conceptual_breakdown": [
        "<strong>Uber H3 Hexagonal Grid:</strong> All 6 adjacent neighbors have identical centroid distance (unlike QuadTree squares where diagonal distance is $\\sqrt{2}x$).",
        "<strong>Location Buffer (In-Memory):</strong> Storing ephemeral driver coordinates in durable disk databases burns 1.25M writes/sec unnecessarily. Keep live coordinates in Redis RAM with 30s TTL; write only completed trip trajectories to disk.",
        "<strong>Ride State Machine:</strong> `REQUESTED` -> `MATCHING` -> `ACCEPTED` -> `ARRIVING` -> `IN_TRIP` -> `COMPLETED`."
      ],
      "failure_scenarios": "<strong>Double Driver Booking Race Condition:</strong> Two riders request rides in the same isolated neighborhood simultaneously; both are matched to the single available driver. <em>Mitigation:</em> Atomic Redis distributed lock or conditional state transition on driver status (`SET driver:101:status 'OFFERED' NX EX 15`).",
      "common_mistakes": [
        {
          "mistake": "Writing every 4-second GPS coordinate from 5 million drivers directly to a relational PostgreSQL database table.",
          "correction": "Store ephemeral live location state in an in-memory Redis cluster or memory-mapped geospatial ring buffer; persist only trip audit milestones to durable storage."
        }
      ],
      "interview_questions": [
        {
          "question": "Why did Uber migrate from QuadTrees to the H3 Hexagonal Hierarchical Spatial Index?",
          "answer": "QuadTree squares have unequal distances to neighbors (orthogonal neighbors are distance 1, diagonal neighbors are distance 1.414), creating distortion in circular radius searches. Hexagons have 6 neighbors with identical centroid distances, simplifying circular neighborhood expansion algorithms."
        }
      ]
    },
    {
      "id": "design-amazon-flash-sale-inventory",
      "title": "Case Study: Design Amazon / Ticketmaster Flash Sale (High-Concurrency Inventory Reservation)",
      "definition": "Design an e-commerce flash sale system capable of selling 10,000 limited-edition items or concert tickets to 1 million concurrent users within 60 seconds without overselling or database lock contention.",
      "why_we_need_it": "Tests ultra-high write concurrency, race condition prevention, multi-stage inventory reservation with TTL expiration, and virtual waiting room queues.",
      "real_world_analogy": "A concert ticket booth with 100 physical tickets: 5,000 fans line up outside. A security guard lets 100 fans into the ticket window lobby with a 10-minute pass to pay. If someone doesn't pay within 10 minutes, their ticket is handed to the next person waiting in line.",
      "how_it_works": "<p>1. <strong>Virtual Waiting Room (Cloudflare / Redis Queue):</strong> Intercepts 1M users at the edge; assigns queue positions and drips users into the checkout cluster at a controlled rate (e.g. 500 users/sec).<br>2. <strong>In-Memory Stock Reservation (Redis Lua):</strong> Stock count is preloaded into Redis (`stock:item_123 = 10000`). An atomic Lua script checks `stock > 0`, decrements stock, and creates a 10-minute temporary reservation key (`reservation:user_456`).<br>3. <strong>Payment & Commit:</strong> User proceeds to payment gateway. If payment succeeds, order is confirmed and committed to PostgreSQL. If user abandons or payment fails, a Redis TTL expiration event triggers an inventory compensation rollback (`stock = stock + 1`).</p>",
      "conceptual_breakdown": [
        "<strong>Preventing Overselling:</strong> Executing stock decrement in atomic Redis Lua scripts (`redis.call('DECR')`) eliminates database row-lock serialization bottlenecks.",
        "<strong>Zero DB Lock Contention:</strong> The relational database only receives finalized, already-reserved orders, shielding it from 1M concurrent write attempts."
      ]
    },
    {
      "id": "design-stripe-payment-gateway",
      "title": "Case Study: Design Stripe (Idempotent Payment Gateway & Financial Ledger)",
      "definition": "Design an ultra-reliable payment processing platform processing billions of dollars daily with zero duplicate charges, strict PCI-DSS security compliance, and double-entry accounting ledger guarantees.",
      "why_we_need_it": "In financial systems, network timeouts are inevitable. Handling retries without charging the customer twice requires bulletproof idempotency and double-entry ledgering.",
      "real_world_analogy": "A traditional double-entry bank book: money never just appears or disappears. Every financial transaction is recorded as two balancing entries: a Debit to Account A and a Credit to Account B ($Debit + Credit = 0$).",
      "how_it_works": "<p>1. <strong>Idempotency Layer:</strong> Client generates a UUID `Idempotency-Key: 9f8a...` in HTTP header. The gateway saves the key in Redis/DB inside a transaction. If a retry arrives with the same key, the gateway returns the cached response with zero re-processing.<br>2. <strong>Payment State Machine:</strong> `INITIATED` -> `AUTH_PENDING` -> `AUTHORIZED` -> `CAPTURED` / `REFUNDED`.<br>3. <strong>Double-Entry Ledger:</strong> Every transaction inserts two immutable rows into the ledger table (`Debit: Customer_Card $50.00`, `Credit: Merchant_Balance $48.50`, `Credit: Stripe_Fee $1.50`).</p>",
      "conceptual_breakdown": [
        "<strong>Double-Entry Accounting:</strong> Sum of debits must equal sum of credits for every transaction. The ledger is append-only (no `UPDATE` or `DELETE` statements allowed).",
        "<strong>Webhook Delivery Engine:</strong> Exponential backoff retry queue (1s, 5s, 30s, 1m, 1h, 24h) to deliver payment events to merchant servers with HMAC cryptographic signatures."
      ]
    }
  ]
}

# -------------------------------------------------------------
# MODULE 27: Real-World Case Studies 4: Storage, Search & Cloud
# -------------------------------------------------------------
mod_27 = {
  "module_id": "27",
  "module_title": "Real-World Case Studies 4: Storage, Search & Cloud",
  "description": "End-to-end interview blueprints: Design Google Drive / Dropbox (File Chunking, Deduplication & Sync Protocol), TinyURL / Bitly URL Shortener, and Google Web Crawler with PageRank.",
  "topics": [
    {
      "id": "design-dropbox-file-sync",
      "title": "Case Study: Design Google Drive / Dropbox (Chunking, Content Hashing & Sync)",
      "definition": "Design a cloud file storage and synchronization service supporting 500 million users, cross-device multi-folder synchronization, delta sync (syncing only modified bytes), and content deduplication.",
      "why_we_need_it": "Uploading a 2GB file after editing 1 sentence should NOT re-upload 2GB of data. Delta chunking and content hashing are premier system design concepts.",
      "real_world_analogy": "A puzzle box: instead of mailing an entire giant wooden puzzle when you change 1 piece, you only mail the 1 modified puzzle piece. The recipient puts the piece into their existing puzzle frame.",
      "how_it_works": "<p>1. <strong>Client-Side Chunking:</strong> Files are split into 4MB chunks using rolling hash algorithms (e.g. Rabin Fingerprinting or CDC).<br>2. <strong>Content-Addressed Storage:</strong> Each chunk is hashed with SHA-256 (`Chunk_Hash = SHA256(data)`). Chunks are named by their hash and stored in S3.<br>3. <strong>Global Deduplication:</strong> If 1,000 users upload the same 100MB PDF, S3 stores the chunks ONCE; metadata tables simply map 1,000 user file records to the same underlying chunk hashes.<br>4. <strong>Delta Sync:</strong> When a file is edited, the client re-hashes chunks, detects only Chunk #4 has changed, and uploads only the 4MB of Chunk #4.<br>5. <strong>Notification & Sync Service:</strong> Long-polling/WebSocket service broadcasts chunk update notifications to the user's other connected devices.</p>",
      "conceptual_breakdown": [
        "<strong>Metadata DB:</strong> Sharded PostgreSQL / MySQL storing User, File, Folder, FileVersion, and FileChunkMapping tables.",
        "<strong>Block Storage:</strong> Amazon S3 storing immutable 4MB chunks named by SHA-256 hash.",
        "<strong>Conflict Resolution:</strong> If two devices edit offline and sync simultaneously, create a conflict file (`Report (Alice's conflicted copy).docx`)."
      ]
    },
    {
      "id": "design-tinyurl-shortener",
      "title": "Case Study: Design TinyURL / Bitly (Base62 Encoding & Key Generation Service)",
      "definition": "Design a scalable URL shortening service handling 100 million new URLs/month and 10 billion clicks/month with sub-10ms redirect latency and 99.999% availability.",
      "why_we_need_it": "The essential fundamental interview problem covering Base62 encoding, unique ID generation without collision, 301 vs 302 HTTP redirects, and cache sizing.",
      "real_world_analogy": "A cloakroom coat check ticket: you hand over a giant bulky winter coat (Long URL) and receive a tiny plastic token with number '7aB' (Short URL). When you show '7aB', you instantly get your coat back.",
      "how_it_works": "<p>1. <strong>Base62 Encoding:</strong> Uses `[a-z, A-Z, 0-9]` (62 characters). A 7-character string provides $62^7 \\approx 3.52 \\text{ Trillion}$ unique short URLs.<br>2. <strong>Key Generation Service (KGS):</strong> Dedicated background worker pre-generates billions of unique random 7-character Base62 keys and stores them in a Redis/DB table (`Used` vs `Unused`). When a user requests a short URL, the server instantly grabs a pre-generated unused key without hashing collisions.<br>3. <strong>HTTP Redirect Code:</strong> Returns `301 Moved Permanently` (browser caches redirect, saving server load) OR `302 Found` (browser queries server every time, enabling click analytics tracking).<br>4. <strong>Caching:</strong> 80/20 rule: Cache top 20% most clicked URLs in Redis RAM for sub-2ms redirect lookups.</p>",
      "comparison_matrix": {
        "title": "HTTP 301 vs 302 Redirect Comparison",
        "columns": ["Feature", "HTTP 301 Moved Permanently", "HTTP 302 Found / Temporary Redirect"],
        "rows": [
          ["Browser Caching", "Browser caches destination permanently", "Browser does NOT cache; queries server every time"],
          ["Server Load", "Extremely Low (Subsequent clicks bypass server)", "Higher (Every click hits TinyURL server)"],
          ["Analytics Tracking", "Only records the 1st click per user", "Accurately records 100% of all user clicks & geo-data"],
          ["SEO Impact", "Transfers full PageRank link equity", "Does not transfer PageRank link equity"]
        ]
      }
    },
    {
      "id": "design-google-web-crawler",
      "title": "Case Study: Design Google Web Crawler & PageRank Pipeline",
      "definition": "Design a distributed web crawler capable of crawling billions of web pages per month, respecting `robots.txt` politeness, handling DNS resolution bottlenecks, and detecting duplicate web pages.",
      "why_we_need_it": "Tests massive distributed queue architectures (Frontier Queues), Bloom Filter URL deduplication, politeness delay engines, and distributed graph PageRank computation.",
      "real_world_analogy": "A massive team of explorers mapping every road and signpost in the world: they start at a town square (Seed URLs), follow every road to new towns, note down the names, and mark visited towns on a giant map so they never walk in circles.",
      "how_it_works": "<p>1. <strong>URL Frontier:</strong> Priority Queues (ranks importance by PageRank/freshness) + Politeness Queues (maps hostnames to FIFO queues with mandatory 1-second host delay timers).<br>2. <strong>DNS Resolver Cache:</strong> Dedicated local DNS cache cluster to avoid millions of external DNS lookups.<br>3. <strong>HTML Fetcher & Parser:</strong> Fetches HTML via HTTP/2, extracts links, and parses text.<br>4. <strong>Deduplication Engines:</strong> Bloom Filters to check if URL was already crawled; SimHash / MinHash to detect duplicate and mirrored web page text.<br>5. <strong>Storage:</strong> Raw web pages saved to S3/Bigtable; document graph fed to MapReduce/Spark for PageRank graph calculations.</p>"
    }
  ]
}

# -------------------------------------------------------------
# MODULE 28: Real-World Case Studies 5: Gaming, IoT & FinTech
# -------------------------------------------------------------
mod_28 = {
  "module_id": "28",
  "module_title": "Real-World Case Studies 5: Gaming, IoT & FinTech",
  "description": "End-to-end interview blueprints: Design Real-Time Gaming Leaderboard (Redis Sorted Sets), IoT Sensor Ingestion Pipeline (Kafka + Time-Series DB), and Distributed Crypto/Stock Exchange Order Book.",
  "topics": [
    {
      "id": "design-gaming-leaderboard",
      "title": "Case Study: Design Real-Time Gaming Leaderboard (Redis Sorted Sets)",
      "definition": "Design a real-time gaming leaderboard system for 50 million active players supporting instant score updates and sub-10ms queries for Top-100 global players and Player Rank lookups.",
      "why_we_need_it": "Relational queries like `SELECT COUNT(*) FROM scores WHERE score > my_score` take 10+ seconds on 50 million rows. Redis Sorted Sets (Skip Lists) evaluate rank in $O(\\log N)$ time (~1 millisecond).",
      "real_world_analogy": "A physical race track scoreboard: when a car crosses the finish line, the scoreboard instantly moves their number card up the board without recalculating the times of all 10,000 cars from scratch.",
      "how_it_works": "<p>1. <strong>Redis Sorted Sets (ZSET):</strong> Combines a Hash Map (for $O(1)$ player score lookups) with a Skip List (for $O(\\log N)$ score insertion and rank retrieval).<br>2. <strong>Score Update:</strong> `ZINCRBY leaderboard:global 50 user_123` ($O(\\log N)$).<br>3. <strong>Top 100 Players:</strong> `ZREVRANGE leaderboard:global 0 99 WITHSCORES` ($O(\\log N + M)$ - sub-1ms).<br>4. <strong>Get My Rank:</strong> `ZREVRANK leaderboard:global user_123` ($O(\\log N)$).<br>5. <strong>Time-Bounded Leaderboards:</strong> Separate Redis keys for `leaderboard:daily:2026-10-03`, `leaderboard:weekly`, and `leaderboard:monthly`.</p>",
      "conceptual_breakdown": [
        "<strong>Skip List Internals:</strong> Multi-level linked list with probabilistic forward pointers enabling logarithmic $O(\\log N)$ search and insertion.",
        "<strong>Tie-Breaking:</strong> When two players have identical scores, encode the earlier timestamp into the fractional part: `Final_Score = Score + (1 - (Timestamp / 1e12))` so earlier players rank higher."
      ]
    },
    {
      "id": "design-iot-telemetry-pipeline",
      "title": "Case Study: Design IoT Telemetry Pipeline (MQTT, Kafka & TimescaleDB)",
      "definition": "Design a connected-vehicle telemetry pipeline ingesting 1 million IoT smart meters / cars emitting sensor telemetry every 5 seconds (200,000 events/sec), processing alerts in real-time, and archiving for historical analytics.",
      "why_we_need_it": "Tests lightweight binary protocols (MQTT), high-throughput ingest pipelines, downsampling rollups, and Time-Series Databases (TimescaleDB / InfluxDB).",
      "real_world_analogy": "A network of 1 million weather stations: each station transmits temperature and humidity every 5 seconds over radio. A central weather computer alerts for forest fire heat spikes in 1 second while storing daily averages for climate research.",
      "how_it_works": "<p>1. <strong>MQTT Ingestion:</strong> Devices connect to MQTT Brokers (EMQX / Mosquitto) over lightweight binary TCP packets.<br>2. <strong>Kafka Stream Buffer:</strong> MQTT broker bridges messages into Apache Kafka `sensor-telemetry` topic.<br>3. <strong>Real-Time Anomaly Engine:</strong> Apache Flink processes sliding windows (e.g. engine temperature > 120°C for 3 consecutive readings) and pushes immediate push notifications via WebSockets.<br>4. <strong>Time-Series Storage (TimescaleDB / InfluxDB):</strong> Ingests raw data using Hypertables with automatic chunk-based disk compression (90% compression ratio).<br>5. <strong>Continuous Downsampling:</strong> Roll up 5-second raw data into 1-minute, 1-hour, and 1-day averages after 30 days to optimize storage.</p>"
    }
  ]
}

# -------------------------------------------------------------
# MODULE 29: Low-Latency Systems & High-Frequency Trading
# -------------------------------------------------------------
mod_29 = {
  "module_id": "29",
  "module_title": "Low-Latency Systems & High-Frequency Architecture",
  "description": "Master microsecond and nanosecond architecture: C++ memory management, Lock-Free Ring Buffers (LMAX Disruptor), Kernel Bypass (DPDK / Solarflare Solarflare OpenOnload), and CPU Cache line alignment (false sharing).",
  "topics": [
    {
      "id": "low-latency-cpp-and-memory",
      "title": "Low-Latency Engineering: Cache Locality, False Sharing & Zero-Allocation",
      "definition": "Low-latency systems architecture optimizes software to execute in microseconds ($\\mu s$) or nanoseconds ($ns$) by eliminating operating system context switches, heap allocations in critical paths, and CPU cache misses.",
      "why_we_need_it": "In High-Frequency Trading (HFT) and real-time ad exchanges, an extra 50 microseconds of latency means losing millions of dollars to competing trading firms.",
      "real_world_analogy": "A Formula 1 pit stop: instead of searching through a messy toolbox in the garage (Heap memory), every specialized tool is laid out in exact order in the mechanic's hand (L1 CPU Cache) before the car arrives.",
      "how_it_works": "<p>1. <strong>Zero Dynamic Heap Allocation:</strong> Pre-allocate all memory buffers at server startup (Memory Pools / Arena Allocators). Zero calls to `malloc`/`new` in the hot trade path.<br>2. <strong>CPU Cache Line Alignment (64 Bytes):</strong> Align critical structs to 64-byte boundaries (`alignas(64)`) to prevent <strong>False Sharing</strong> where two CPU cores invalidate each other's L1 cache lines.<br>3. <strong>CPU Core Pinning (Thread Affinity):</strong> Pin critical worker threads to dedicated physical CPU cores (`pthread_setaffinity_np`) and isolate them from the OS scheduler (`isolcpus`), eliminating CPU context-switching overhead.</p>",
      "conceptual_breakdown": [
        "<strong>L1 Cache Latency:</strong> ~1 nanosecond (4 cycles).",
        "<strong>L3 Cache Latency:</strong> ~10-15 nanoseconds.",
        "<strong>Main RAM Latency:</strong> ~60-100 nanoseconds (100x slower than L1).",
        "<strong>Branch Prediction:</strong> Use `[[likely]]` and `[[unlikely]]` compiler hints in C++20 to optimize CPU branch instruction pipelines."
      ]
    },
    {
      "id": "kernel-bypass-and-lockfree-disruptor",
      "title": "Kernel Bypass (DPDK/Solarflare) & Lock-Free Ring Buffers (Disruptor)",
      "definition": "Kernel Bypass allows user-space applications to read raw Ethernet packets directly from the Network Interface Card (NIC) hardware ring buffer, bypassing the entire Linux OS TCP/IP kernel stack. Lock-free ring buffers pass messages between threads without mutex lock contention.",
      "why_we_need_it": "The Linux kernel's network stack (socket buffers, interrupts, context switching) introduces 5 to 25 microseconds of jitter. Kernel bypass cuts network I/O latency to <1 microsecond.",
      "real_world_analogy": "A dedicated private VIP highway exit directly into your private garage, completely bypassing public highway stoplights and toll booths.",
      "how_it_works": "<p>1. <strong>Kernel Bypass (DPDK / OpenOnload):</strong> NIC hardware writes network packets directly into user-space shared memory via Direct Memory Access (DMA). Application polls the ring buffer continuously in a busy loop without hardware interrupts.<br>2. <strong>LMAX Disruptor Pattern:</strong> A single circular lock-free Ring Buffer with power-of-2 size. Uses atomic memory barriers and cache-padded sequence numbers to achieve >10 million messages/sec per thread with nanosecond latencies.<br>3. <strong>Mechanical Sympathy:</strong> Designing software algorithms that work in harmony with the underlying hardware CPU architecture.</p>"
    }
  ]
}

# -------------------------------------------------------------
# MODULE 30: Multi-Region & Disaster Recovery
# -------------------------------------------------------------
mod_30 = {
  "module_id": "30",
  "module_title": "Multi-Region & Disaster Recovery Architecture",
  "description": "Master Multi-Region Active-Active vs Active-Passive architectures, RPO (Recovery Point Objective), RTO (Recovery Time Objective), Cross-Region Replication, and GDPR Data Residency.",
  "topics": [
    {
      "id": "active-active-vs-active-passive-dr",
      "title": "Multi-Region Topologies: Active-Active vs Active-Passive & RTO / RPO",
      "definition": "Multi-Region architecture deploys a system across multiple geographic cloud regions (e.g. US-East, EU-West, AP-South) to survive catastrophic cloud datacenter blackouts and provide ultra-low latency to global users. RTO (Recovery Time Objective) is the maximum acceptable downtime duration; RPO (Recovery Point Objective) is the maximum acceptable data loss window.",
      "why_we_need_it": "Power outages, hurricanes, or cloud provider regional control plane failures can take down an entire AWS/Azure region. Multi-region guarantees business continuity.",
      "real_world_analogy": "A corporate bank with headquarters in New York and London: Active-Passive is keeping the London branch closed as an empty backup building that takes 4 hours to open if New York burns down. Active-Active is running both New York and London fully staffed 24/7, processing customer transactions simultaneously.",
      "how_it_works": "<p>1. <strong>Active-Passive (Hot Standby / Pilot Light):</strong> Primary region serves 100% of traffic. Standby region receives async database replication. On primary disaster, DNS switches to Standby (RTO: 5-30 min, RPO: seconds of replication lag).<br>2. <strong>Active-Active (Multi-Primary):</strong> All regions serve live read and write traffic simultaneously. Requires Conflict-Free Replicated Data Types (CRDTs), CockroachDB/Google Spanner globally distributed consensus, or strict data partitioning by geographic user residency.<br>3. <strong>GeoDNS / Anycast Routing:</strong> Route53 / Cloudflare routes user to geographically closest healthy region.</p>",
      "comparison_matrix": {
        "title": "Disaster Recovery Topologies Comparison",
        "columns": ["Disaster Recovery Strategy", "RTO (Downtime)", "RPO (Data Loss)", "Cost Overhead", "Engineering Complexity"],
        "rows": [
          ["Backup & Restore (Cold Standby)", "Hours to Days", "Hours (Last backup snapshot)", "Lowest (~1.05x)", "Very Low"],
          ["Pilot Light (Warm Standby)", "10 - 30 minutes", "Minutes (Replication lag)", "Low (~1.3x)", "Moderate"],
          ["Active-Passive (Hot Standby)", "1 - 5 minutes", "Seconds (Near real-time sync)", "High (~1.8x)", "Moderate-High"],
          ["Active-Active Multi-Region", "Zero (<1s instant failover)", "Zero (Sync consensus)", "Highest (2x - 3x)", "Extremely High"]
        ]
      }
    },
    {
      "id": "cross-region-replication-and-gdpr",
      "title": "Cross-Region Data Replication, Split-Brain Prevention & GDPR Residency",
      "definition": "Cross-region replication synchronizes databases across continents while navigating the speed-of-light latency penalty ($~70ms$ transatlantic round-trip) and complying with legal data sovereignty mandates (GDPR / CCPA / HIPAA).",
      "why_we_need_it": "Synchronous replication across continents adds 100ms+ latency to every write, while regulatory laws strictly prohibit transmitting European citizens' personal data to US data centers.",
      "real_world_analogy": "An international shipping company keeping local inventory warehouses in Germany for EU customers and in Texas for US customers, maintaining compliance with local customs tariffs in each country.",
      "how_it_works": "<p>1. <strong>Geo-Partitioning:</strong> Shard database rows by country/region column (`country_code = 'DE'` -> stored exclusively on EU database nodes).<br>2. <strong>Asynchronous Cross-Region WAL Streaming:</strong> Primary region commits locally in 2ms, streaming WAL changes asynchronously to replica regions via dedicated cloud backbone links.<br>3. <strong>Split-Brain Fencing:</strong> Use odd-numbered region consensus (e.g. 3 regions: US-East, US-West, and EU-West witness node) to prevent two regions from both claiming to be primary during a transoceanic fiber cut.</p>"
    }
  ]
}

modules = [mod_26, mod_27, mod_28, mod_29, mod_30]
for m in modules:
    filename = os.path.join(CONTENT_DIR, f"module_{m['module_id']}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print(f"Generated {filename} with {len(m['topics'])} topics")
