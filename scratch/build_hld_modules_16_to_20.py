import json
import os

CONTENT_DIR = "content/hld"
os.makedirs(CONTENT_DIR, exist_ok=True)

# -------------------------------------------------------------
# MODULE 16: API Gateway, Rate Limiting & Service Mesh
# -------------------------------------------------------------
mod_16 = {
  "module_id": "16",
  "module_title": "API Gateway, Rate Limiting & Service Mesh",
  "description": "Master API Gateway routing, Token Bucket / Leaky Bucket / Sliding Window rate limiting algorithms, Circuit Breakers (Resilience4j), and Service Mesh (Envoy/Istio).",
  "topics": [
    {
      "id": "api-gateway-pattern-and-responsibilities",
      "title": "API Gateway Patterns: Routing, Auth, TLS Offload & Aggregation",
      "definition": "An API Gateway acts as a single ingress reverse proxy and reverse boundary for client requests, orchestrating authentication, rate limiting, SSL termination, request routing, header transformations, and API composition across downstream microservices.",
      "why_we_need_it": "Exposing internal microservices directly to clients forces every service to duplicate authentication, SSL certificates, CORS policies, and rate limiting logic, while exposing internal network topologies to public attackers.",
      "real_world_analogy": "A hotel front desk concierge: Guests (Clients) don't wander into the kitchen or laundry room. They talk to the concierge (API Gateway), who verifies their room key (Auth), calls the kitchen (Routing), and delivers the meal (Aggregation).",
      "how_it_works": "<p>1. <strong>Ingress & SSL Offloading:</strong> Terminates public HTTPS/TLS connections at the edge, converting them to internal HTTP/gRPC or mTLS.<br>2. <strong>Authentication & Authorization:</strong> Validates JWT tokens or OAuth2 session keys before forwarding requests downstream.<br>3. <strong>BFF Pattern (Backend for Frontend):</strong> Provides dedicated gateway instances customized for Web, iOS, Android, and IoT clients.<br>4. <strong>Request Aggregation:</strong> Fetches data from User Service, Order Service, and Notification Service in parallel, returning a single merged JSON payload to the mobile client.</p>",
      "conceptual_breakdown": [
        "<strong>BFF Pattern:</strong> Isolates mobile client endpoints (optimized for bandwidth) from desktop web endpoints.",
        "<strong>Kong, Apache APISIX & AWS API Gateway:</strong> High-performance gateway engines built on NGINX / OpenResty / Envoy.",
        "<strong>Anti-Pattern - Fat Gateway:</strong> Putting business domain logic into the gateway turns it into an unmaintainable distributed monolith bottleneck."
      ],
      "comparison_matrix": {
        "title": "API Gateway vs Load Balancer vs Reverse Proxy",
        "columns": ["Feature", "Load Balancer (e.g. AWS NLB/ALB)", "Reverse Proxy (e.g. NGINX)", "API Gateway (e.g. Kong, Envoy)"],
        "rows": [
          ["Primary Focus", "High-throughput traffic distribution", "Caching, compression, basic reverse routing", "API lifecycle, Auth, Rate limiting, Transformation"],
          ["Protocol Awareness", "L4 (TCP) / L7 (HTTP)", "L7 (HTTP, WebSockets)", "L7 + gRPC, GraphQL, WebSocket protocol mediation"],
          ["Authentication", "None / Basic OIDC", "Basic Auth / Lua scripts", "Full OAuth2, JWT verification, API Keys, RBAC"],
          ["Rate Limiting", "Basic IP connection limits", "Fixed rate limits per IP", "Sophisticated User/Tenant/Token Sliding Window algorithms"],
          ["Request Aggregation", "No", "No", "Yes (Aggregates multiple backend microservice calls)"]
        ]
      },
      "failure_scenarios": "<strong>API Gateway as Single Point of Failure (SPOF):</strong> A memory leak in a custom Lua auth plugin crashes the gateway process, causing 100% platform downtime globally. <em>Mitigation:</em> Multi-AZ redundant gateway clusters behind BGP Anycast DNS and keep plugins stateless.",
      "common_mistakes": [
        {
          "mistake": "Embedding domain business logic (e.g. order calculations) inside the API Gateway.",
          "correction": "Keep API Gateways strictly focused on routing, security, and transport policies. Delegate domain logic to backend services."
        }
      ],
      "interview_questions": [
        {
          "question": "What is the Backend-for-Frontend (BFF) pattern and why is it used?",
          "answer": "BFF is an architectural pattern where distinct API gateways are created for specific client types (e.g. Mobile App BFF vs Desktop Web BFF vs Smart TV BFF). It allows tailoring payload sizes, network protocols, and data formatting to the exact network constraints and UI requirements of each client platform."
        }
      ]
    },
    {
      "id": "rate-limiting-algorithms-deep-dive",
      "title": "Rate Limiting Algorithms: Token Bucket, Leaky Bucket, Fixed & Sliding Window",
      "definition": "Rate limiting restricts the number of requests a client can make within a given time window to protect backend services from denial-of-service (DoS) attacks, brute-force exploits, and resource starvation.",
      "why_we_need_it": "A single rogue script or DDoS bot sending 50,000 requests per second can exhaust thread pools and crash the database for all legitimate users.",
      "real_world_analogy": "A bouncer with a velvet rope letting at most 10 guests enter every minute. Or a water dispenser with a fixed dispenser faucet speed.",
      "how_it_works": "<p>The 4 Core Rate Limiting Algorithms:<br>1. <strong>Token Bucket (AWS, Stripe):</strong> A bucket holds up to $C$ tokens. Tokens refill at rate $R$ per second. Each request consumes 1 token. Allows burst traffic up to capacity $C$.<br>2. <strong>Leaky Bucket (Nginx):</strong> Requests enter a FIFO queue. Requests leak out of the queue at a smooth, constant rate. Excess bursts overflow and are rejected (`429 Too Many Requests`).<br>3. <strong>Fixed Window Counter:</strong> Counts requests in fixed time blocks (e.g. 12:00-12:01). Vulnerable to 2x burst traffic at window boundary transitions.<br>4. <strong>Sliding Window Log / Counter:</strong> Uses Redis Sorted Sets (ZSET) or sliding weight formulas to evaluate exact rolling time windows, eliminating boundary burst vulnerabilities.</p>",
      "conceptual_breakdown": [
        "<strong>HTTP 429 Too Many Requests:</strong> Standard response returned with `Retry-After: 30` header.",
        "<strong>Distributed Redis Rate Limiter:</strong> Executes atomic Lua scripts using `EVAL` with Redis keys like `ratelimit:{user_id}:{timestamp}`.",
        "<strong>Rate Limiting Keys:</strong> IP address (public unauthenticated), User ID (logged-in), API Key (B2B SaaS tier), or Endpoint Path."
      ],
      "system_flow_animation": {
        "title": "Sliding Window Redis Rate Limiting Flow",
        "steps": [
          {
            "num": 1,
            "title": "Client Sends API Request",
            "actor": "Client -> API Gateway",
            "desc": "Client sends GET /api/v1/search with Bearer Token 'user_481'.",
            "node": "API Gateway"
          },
          {
            "num": 2,
            "title": "Redis Sliding Window Evaluation",
            "actor": "API Gateway -> Redis",
            "desc": "Gateway runs atomic Lua script: removes timestamps older than (now - 60s), counts remaining items in ZSET, and checks limit (100 req/min).",
            "node": "Redis Rate Limiter"
          },
          {
            "num": 3,
            "title": "Decision & Header Injection",
            "actor": "API Gateway -> Backend Service",
            "desc": "Count is 42 <= 100: Request is allowed. Gateway injects headers 'X-RateLimit-Remaining: 58' and forwards request.",
            "node": "Backend Service"
          }
        ]
      },
      "comparison_matrix": {
        "title": "Rate Limiting Algorithms Comparison",
        "columns": ["Algorithm", "Burst Handling", "Memory Overhead", "Implementation Complexity", "Standard Use Case"],
        "rows": [
          ["Token Bucket", "Allows controlled bursts up to bucket size", "Low (2 numbers: tokens, last_refill)", "Low", "AWS APIs, Stripe API rate limiting"],
          ["Leaky Bucket", "Smooths traffic to strict constant rate", "Moderate (Queue buffer memory)", "Moderate", "Traffic shaping, NGINX burst queues"],
          ["Fixed Window", "Vulnerable to 2x burst at boundaries", "Lowest (Single integer counter)", "Very Low", "Basic internal rate limits"],
          ["Sliding Window Counter", "Prevents boundary burst attacks", "Low (Weighted past & current counter)", "Moderate", "Cloudflare, production SaaS API limits"]
        ]
      },
      "failure_scenarios": "<strong>Redis Rate Limiter Latency Overhead:</strong> Making a synchronous Redis network round-trip on every single API request adds 2-5ms to global latency and creates a critical dependency on Redis. <em>Mitigation:</em> Local in-memory token bucket on gateway instances with periodic async batch synchronization to Redis.",
      "common_mistakes": [
        {
          "mistake": "Rate limiting exclusively by Client IP address in mobile or enterprise environments.",
          "correction": "Thousands of legitimate enterprise users share a single NAT gateway IP. Use authenticated User IDs or API Keys for authenticated endpoints."
        }
      ],
      "interview_questions": [
        {
          "question": "How does the Sliding Window Counter algorithm prevent the boundary burst vulnerability of Fixed Window rate limiters?",
          "answer": "Sliding Window Counter calculates estimated requests in the rolling window by weighting the previous window's count: `Estimated_Count = Previous_Window_Count * ((1 - Current_Window_Elapsed_Time_Fraction)) + Current_Window_Count`. If this estimated value exceeds the threshold, requests are rejected, eliminating 2x boundary spikes with minimal memory overhead."
        }
      ]
    },
    {
      "id": "circuit-breaker-and-resilience",
      "title": "Resilience Patterns: Circuit Breaker, Bulkhead & Retry with Jitter",
      "definition": "The Circuit Breaker pattern prevents cascading failures by stopping calls to a failing remote downstream service, failing fast until the service recovers. Bulkhead isolates thread pools, and Retry with Jitter prevents thundering herds.",
      "why_we_need_it": "If downstream Payment Gateway hangs, 500 upstream checkout threads block waiting for socket timeouts, starving the entire application and crashing the whole website.",
      "real_world_analogy": "An electrical circuit breaker in your home: when a short circuit or current spike occurs, the breaker trips to 'OPEN', cutting power to prevent electrical fires, rather than letting the wires melt.",
      "how_it_works": "<p>1. <strong>Closed State (Normal):</strong> Requests pass through to downstream. Failures increment error counter.<br>2. <strong>Open State (Tripped):</strong> If error rate exceeds threshold (e.g. >50% errors over 10s), the breaker trips to OPEN. All subsequent requests fail FAST immediately (returning fallback/cached data) without making network calls.<br>3. <strong>Half-Open State (Testing):</strong> After a sleep window (e.g. 10s), the breaker transitions to Half-Open, allowing a trial percentage of requests through. If successful, resets to CLOSED; if failures persist, reverts to OPEN.</p>",
      "conceptual_breakdown": [
        "<strong>Fallback Response:</strong> Return cached data, default degraded responses, or queue for async processing when the circuit is open.",
        "<strong>Bulkhead Pattern:</strong> Allocates separate thread pools (e.g. 20 threads for Recommendation, 50 threads for Payment) so one slow dependency cannot consume 100% of server threads.",
        "<strong>Exponential Backoff with Full Jitter:</strong> $T = \\text{random}(0, \\min(\\text{Max}, \\text{Base} \\cdot 2^{\\text{attempt}}))$."
      ],
      "failure_scenarios": "<strong>Retry Storms without Jitter:</strong> 10,000 clients retry a failed service at exact 1-second intervals, repeatedly hammering the recovering service with synchronous waves of load and driving it back down. <em>Mitigation:</em> Always add random jitter to exponential backoff retries.",
      "common_mistakes": [
        {
          "mistake": "Retrying non-idempotent operations (e.g. POST /charges) on network socket timeout errors.",
          "correction": "Only retry idempotent operations or ensure requests include unique Idempotency Keys."
        }
      ],
      "interview_questions": [
        {
          "question": "What is the primary difference between the Circuit Breaker and Bulkhead patterns?",
          "answer": "Circuit Breaker stops invoking a failing downstream service based on error/latency thresholds to let it recover; Bulkhead isolates resources (thread pools/memory) between different dependencies so that a total failure in one dependency cannot exhaust resources needed by other healthy services."
        }
      ]
    },
    {
      "id": "service-mesh-and-sidecars",
      "title": "Service Mesh Architecture: Envoy, Istio & Sidecar Proxies",
      "definition": "A Service Mesh is a dedicated infrastructure layer that handles service-to-service (East-West) network communication, providing automated mutual TLS (mTLS) encryption, traffic routing, load balancing, observability, and distributed tracing via Sidecar proxies.",
      "why_we_need_it": "In a cluster of 200 microservices, implementing retries, circuit breakers, mTLS cert rotation, and tracing libraries in every programming language (Go, Java, Python, Node) creates massive SDK maintenance debt.",
      "real_world_analogy": "A personal diplomatic escort assigned to every diplomat: whenever Diplomat A wants to speak with Diplomat B, their escorts (Sidecars) handle translation, passport verification, security clearance, and transport logistics automatically.",
      "how_it_works": "<p>1. <strong>Data Plane (Envoy Sidecars):</strong> A lightweight C++ proxy deployed alongside every application container (Pod) intercepting all inbound and outbound network traffic.<br>2. <strong>Control Plane (Istio):</strong> Centralized manager that distributes routing rules, service discovery tables, access control policies, and cryptographic mTLS certificates to all Envoy proxies in the cluster.<br>3. <strong>Features:</strong> Canary deployments (90% traffic to v1, 10% to v2), fault injection testing, and automatic distributed tracing header propagation (`x-request-id`, `x-b3-traceid`).</p>",
      "conceptual_breakdown": [
        "<strong>North-South vs East-West:</strong> North-South is ingress traffic entering from the public Internet (API Gateway); East-West is internal microservice-to-microservice traffic (Service Mesh).",
        "<strong>Zero-Trust Security:</strong> Strict mTLS ensures that even if an attacker penetrates the network perimeter, they cannot eavesdrop or impersonate internal services."
      ],
      "tradeoffs": "<strong>Trade-off:</strong> Service mesh adds CPU/memory resource overhead (~50MB RAM per pod) and 1-2ms latency per network hop in exchange for universal observability, automated mTLS, and advanced traffic shifting.",
      "failure_scenarios": "<strong>Control Plane Disconnect:</strong> If the Istio control plane crashes, Envoy sidecars continue routing traffic based on their last cached configuration without interrupting live data-plane traffic.",
      "common_mistakes": [
        {
          "mistake": "Deploying a heavy service mesh for a simple architecture with only 4 microservices.",
          "correction": "Service meshes are beneficial for large organizations with dozens of microservices and multi-language polyglot environments."
        }
      ],
      "interview_questions": [
        {
          "question": "How does Envoy sidecar proxy achieve zero-downtime Canary deployments in Kubernetes?",
          "answer": "Envoy inspects HTTP headers or applies weighted routing rules (e.g. 95% traffic routed to Service v1 and 5% to Service v2) at the proxy level without restarting application pods or modifying client code."
        }
      ]
    }
  ]
}

# -------------------------------------------------------------
# MODULE 17: Distributed Storage, Object Stores & Data Lakes
# -------------------------------------------------------------
mod_17 = {
  "module_id": "17",
  "module_title": "Distributed Storage, Object Stores & Data Lakes",
  "description": "Master Block vs File vs Object storage, Amazon S3 internal architecture, Google Bigtable / HBase, and Data Lakes vs Data Warehouses (Snowflake/Delta Lake).",
  "topics": [
    {
      "id": "block-vs-file-vs-object-storage",
      "title": "Storage Paradigms: Block Storage vs File Storage vs Object Storage",
      "definition": "Block Storage (EBS, SAN) provides raw unformatted disk blocks for OS filesystems and databases. File Storage (NFS, EFS) organizes data in hierarchical folder trees shared across multiple servers. Object Storage (S3, GCS) stores immutable binary blobs accessible via HTTP REST APIs with flat namespaces and rich metadata.",
      "why_we_need_it": "Storing millions of video uploads or photo attachments in an RDBMS or standard POSIX filesystem exhausts file descriptor inodes and degrades performance. Object storage provides infinite horizontal capacity at 1/10th the cost.",
      "real_world_analogy": "Block Storage is a blank hard drive you screw into a computer. File Storage is an office filing cabinet where workers share folders. Object Storage is a valet coat check: you hand over a coat and receive a claim ticket ID (URL/UUID) to retrieve it later.",
      "how_it_works": "<p>1. <strong>Block (AWS EBS / NVMe SSD):</strong> Ultra-low latency (<1ms), high IOPS, mutable byte-level edits. Attached to 1 server.<br>2. <strong>File (NFS / AWS EFS):</strong> POSIX compliant (`open`, `read`, `write`, `seek`), shared read/write across hundreds of compute nodes.<br>3. <strong>Object (AWS S3 / Google Cloud Storage):</strong> Flat namespace, immutable (`PUT`, `GET`, `DELETE`), practically infinite capacity, 99.999999999% (11 9s) durability.</p>",
      "comparison_matrix": {
        "title": "Block vs File vs Object Storage Matrix",
        "columns": ["Dimension", "Block Storage (EBS / SAN)", "File Storage (NFS / EFS)", "Object Storage (S3 / GCS)"],
        "rows": [
          ["Data Structure", "Raw raw sector blocks", "Hierarchical directories & files", "Flat key-value buckets with metadata"],
          ["Access Method", "OS SCSI/NVMe storage protocols", "POSIX filesystem API (SMB, NFS)", "HTTP / REST APIs (GET, PUT, DELETE)"],
          ["Modifiability", "Direct byte-level updates in place", "File append and in-place byte editing", "Immutable (Edits require replacing whole object)"],
          ["Latency & IOPS", "Sub-millisecond, up to 256,000 IOPS", "Low (1-5ms latency)", "Moderate (50-100ms first-byte latency)"],
          ["Cost per GB", "High (~$0.08 - $0.12 / GB/mo)", "Moderate (~$0.30 / GB/mo)", "Very Low (~$0.023 / GB/mo)"]
        ]
      },
      "failure_scenarios": "<strong>POSIX File Inode Exhaustion:</strong> Storing 100 million tiny thumbnail images in a single Linux ext4 directory exhausts filesystem inodes, causing `No space left on device` errors even when 80% of disk capacity is free. <em>Mitigation:</em> Store unstructured media files exclusively in Object Storage.",
      "common_mistakes": [
        {
          "mistake": "Using S3 object storage for frequently mutated database tables requiring random in-place updates.",
          "correction": "Use Block Storage (EBS / local NVMe) for databases; use Object Storage for immutable media and append-only backups."
        }
      ],
      "interview_questions": [
        {
          "question": "Why is Object Storage fundamentally more scalable and durable than traditional Block or File storage?",
          "answer": "Object Storage uses a flat key-value namespace without hierarchical directory lock contention, distributes object chunks across multiple independent storage nodes and availability zones with erasure coding, and accesses data over stateless HTTP REST APIs."
        }
      ]
    },
    {
      "id": "s3-object-store-internals",
      "title": "Amazon S3 Internals: Metadata Partitioning, Erasure Coding & Multipart Upload",
      "definition": "Amazon S3 is a massively distributed object storage service providing 11 9s durability using distributed LSM-based metadata indexing, Reed-Solomon Erasure Coding, and parallel multipart chunk pipelines.",
      "why_we_need_it": "Storing exabytes of media requires surviving the loss of entire data centers without data loss while serving hundreds of thousands of concurrent multi-gigabyte video streams.",
      "real_world_analogy": "Erasure Coding is tearing a 10-page document into 10 pieces and adding 4 math puzzle pieces. Any 10 pieces out of the 14 total are sufficient to instantly reconstruct the entire document, allowing you to lose any 4 pieces without losing a word.",
      "how_it_works": "<p>1. <strong>Metadata vs Data Plane:</strong> Metadata tier (Key -> Location mapping) is separated from Storage Nodes holding raw binary chunks.<br>2. <strong>Erasure Coding (e.g. Reed-Solomon 8+4):</strong> Objects are split into 8 data chunks + 4 parity chunks distributed across independent AZs. System survives 4 concurrent node/drive crashes with only 1.5x storage overhead (vs 3x for 3-way replication).<br>3. <strong>Multipart Upload:</strong> Files >100MB are uploaded as independent 5MB-5GB parts in parallel. If Part 4 fails, only Part 4 retries without restarting the whole 10GB file.<br>4. <strong>Presigned URLs:</strong> Application generates a short-lived cryptographic signed URL allowing clients to upload directly to S3, bypassing application servers.</p>",
      "conceptual_breakdown": [
        "<strong>Strong Read-After-Write Consistency:</strong> Modern S3 guarantees immediate read-after-write consistency for PUTs and DELETEs.",
        "<strong>Presigned URLs:</strong> Offloads massive video/image upload bandwidth away from backend application web servers.",
        "<strong>S3 Storage Classes:</strong> Standard, Intelligent-Tiering, Glacier Flexible, and Glacier Deep Archive for tiered lifecycle cost optimization."
      ],
      "failure_scenarios": "<strong>S3 Key Prefix Throttling:</strong> Sending >3,500 PUTs or >5,500 GETs per second to a single S3 folder prefix (e.g. `/uploads/2026/`) triggers HTTP 503 Slow Down throttles. <em>Mitigation:</em> Partition prefixes using hash prefixes (e.g. `/uploads/{hash_prefix}/`).",
      "common_mistakes": [
        {
          "mistake": "Streaming heavy 5GB video uploads through backend application web servers to S3.",
          "correction": "Generate S3 Presigned URLs and let mobile/web clients upload multipart chunks directly to S3."
        }
      ],
      "interview_questions": [
        {
          "question": "How does Erasure Coding achieve higher durability than 3-way replication while saving storage costs?",
          "answer": "3-way replication incurs a 200% storage overhead (3x total data) and can only survive losing 2 replicas. Reed-Solomon 8+4 Erasure Coding adds only 50% storage overhead (1.5x total data) and can survive losing up to 4 arbitrary disk/node failures simultaneously."
        }
      ]
    },
    {
      "id": "data-lakes-and-warehouses",
      "title": "Analytics Storage: Data Warehouses (Snowflake) vs Data Lakes vs Lakehouses",
      "definition": "Data Warehouses (Snowflake, BigQuery, Redshift) store structured cleaned data optimized for fast SQL OLAP analytical aggregations. Data Lakes (S3 + Parquet/Iceberg) store massive raw unstructured and semi-structured data at low cost. Lakehouses combine both worlds.",
      "why_we_need_it": "Transactional OLTP databases crash when business analysts run complex `GROUP BY` analytical queries scanning 500 million rows across 5 years of historical logs.",
      "real_world_analogy": "A restaurant kitchen (OLTP) focuses on cooking individual fast meals (Transactions). A food manufacturing laboratory (OLAP Data Warehouse) analyzes 5-year sales trends across 10,000 restaurants to optimize supply chains.",
      "how_it_works": "<p>1. <strong>Columnar Storage (Apache Parquet / ORC):</strong> Stores data on disk grouped by columns rather than rows. Queries like `SELECT AVG(price) FROM sales` only read the `price` column pages from disk, achieving 10x-50x I/O reductions and massive compression.<br>2. <strong>ETL / ELT Pipelines:</strong> Extract raw data from OLTP databases -> Load to S3 Data Lake -> Transform into structured Parquet tables.<br>3. <strong>Table Formats (Apache Iceberg, Delta Lake):</strong> Add ACID transactions, time-travel queries, and schema evolution on top of raw S3 Parquet files.</p>",
      "comparison_matrix": {
        "title": "OLTP vs OLAP vs Data Lake",
        "columns": ["Feature", "OLTP (Postgres / MySQL)", "Data Warehouse (Snowflake / BigQuery)", "Data Lake (S3 + Iceberg / Spark)"],
        "rows": [
          ["Primary Workload", "High-concurrency fast CRUD transactions", "Complex analytical aggregations & BI reporting", "Machine learning, big data batch processing, raw archives"],
          ["Storage Format", "Row-oriented pages", "Columnar format (Proprietary micro-partitions)", "Open Columnar formats (Parquet, ORC, Avro)"],
          ["Data Structure", "Strict normalized 3NF relational schemas", "Star / Snowflake dimensional schemas", "Raw structured, semi-structured JSON, unstructured logs"],
          ["Query Latency", "Sub-10 milliseconds", "Seconds to minutes", "Minutes to hours (Distributed MapReduce / Spark)"]
        ]
      },
      "failure_scenarios": "<strong>Small Files Problem in Data Lakes:</strong> Streaming millions of tiny 5KB files into an S3 Data Lake causes Spark queries to spend 95% of execution time listing files and opening S3 connections rather than computing. <em>Mitigation:</em> Run periodic file compaction jobs merging tiny files into optimal 128MB-512MB Parquet blocks.",
      "common_mistakes": [
        {
          "mistake": "Running long-running analytical BI reports directly against the production OLTP primary database.",
          "correction": "Stream transactional data to an analytical OLAP Data Warehouse (BigQuery/Snowflake) via CDC."
        }
      ],
      "interview_questions": [
        {
          "question": "Why is Columnar Storage (Parquet) dramatically faster than Row-based storage for OLAP analytical queries?",
          "answer": "Analytical queries typically access only a few columns across billions of rows. Columnar storage reads only the specific column data blocks required from disk, skipping all other columns entirely, and achieves high compression ratios (Snappy/ZSTD) because identical data types and similar values are stored together sequentially."
        }
      ]
    }
  ]
}

# -------------------------------------------------------------
# MODULE 18: Search, Indexing & Information Retrieval
# -------------------------------------------------------------
mod_18 = {
  "module_id": "18",
  "module_title": "Search, Indexing & Information Retrieval",
  "description": "Master full-text search engines (Elasticsearch / Apache Lucene), Inverted Indexes, TF-IDF / BM25 ranking, fuzzy search, and Vector Databases (Pinecone/Milvus) with embeddings.",
  "topics": [
    {
      "id": "inverted-index-and-elasticsearch",
      "title": "Full-Text Search Internals: Apache Lucene & Inverted Indexes",
      "definition": "An Inverted Index is a data structure mapping individual words (tokens) to the list of document IDs (postings list) in which they occur. It forms the foundational engine of full-text search platforms like Elasticsearch and OpenSearch.",
      "why_we_need_it": "Relational SQL queries like `WHERE description LIKE '%system%design%'` perform full table scans across gigabytes of text, taking minutes. An inverted index evaluates full-text search across millions of documents in <10 milliseconds.",
      "real_world_analogy": "The index at the back of a textbook: looking up the word 'Distributed' gives page numbers `[12, 45, 89, 210]`. Looking up 'Consensus' gives `[45, 89, 300]`. Finding pages discussing both is a simple set intersection: `[45, 89]`.",
      "how_it_works": "<p>1. <strong>Text Analysis Pipeline:</strong> Character Filters -> Tokenizer (splits into words) -> Token Filters (Lowercasing, Stop-word removal, Stemming: 'running' -> 'run').<br>2. <strong>Inverted Index Structure:</strong> Term Dictionary (B-Tree/FST of unique words) -> Postings List (sorted array of document IDs + term frequencies + positions).<br>3. <strong>Elasticsearch Sharding:</strong> An index is sharded across multiple primary Lucene shards and replica shards with coordinator node routing.</p>",
      "conceptual_breakdown": [
        "<strong>Term Dictionary:</strong> Stored as a Finite State Transducer (FST) in RAM for microsecond word lookups.",
        "<strong>Postings List Compression:</strong> Compressed using Frame of Reference (FoR) and Roaring Bitmaps for ultra-fast bitwise AND/OR intersections.",
        "<strong>Near Real-Time (NRT):</strong> Changes are written to in-memory buffer and flushed to Lucene segment files every 1s (Refresh Interval)."
      ],
      "failure_scenarios": "<strong>Unmapped Dynamic Mapping Explosions:</strong> Ingesting unstructured JSON with dynamic keys creates thousands of new field mappings, blowing the Elasticsearch cluster metadata state and causing cluster-wide master node freezes. <em>Mitigation:</em> Set `dynamic: strict` in index mappings.",
      "common_mistakes": [
        {
          "mistake": "Using Elasticsearch as the primary source-of-truth ACID database for transactions.",
          "correction": "Always use an ACID RDBMS or NoSQL store as the primary source of truth; sync documents asynchronously to Elasticsearch via CDC for search queries."
        }
      ],
      "interview_questions": [
        {
          "question": "How does an Inverted Index execute a multi-word search query like 'distributed consensus' in sub-millisecond time?",
          "answer": "It looks up 'distributed' in the FST dictionary to retrieve its postings list `[1, 5, 8, 12]`, looks up 'consensus' to retrieve `[5, 8, 19]`, and performs a blazing-fast bitwise intersection of the two sorted lists using Roaring Bitmaps, finding common documents `[5, 8]` without scanning any document text."
        }
      ]
    },
    {
      "id": "ranking-algorithms-bm25-and-fuzzy",
      "title": "Relevance Ranking (BM25, TF-IDF) & Fuzzy Search Algorithms",
      "definition": "Relevance ranking determines the order in which search results appear using BM25 (Best Matching 25) statistical relevance scoring. Fuzzy search handles typos and spelling mistakes using Levenshtein distance and N-gram algorithms.",
      "why_we_need_it": "Matching 5,000 documents is useless to a user unless the top 10 most relevant documents are accurately ranked on page 1 of search results.",
      "real_world_analogy": "A research librarian: if you ask for 'Quantum Computing', books mentioning 'Quantum' on every page are ranked higher than a 1,000-page encyclopedia that only mentions the word once in a footnote.",
      "how_it_works": "<p>1. <strong>TF (Term Frequency):</strong> How often the word appears in the document (with diminishing returns).<br>2. <strong>IDF (Inverse Document Frequency):</strong> How rare the word is across the entire corpus (common words like 'the' have near-zero weight; rare words like 'Paxos' have huge weight).<br>3. <strong>Document Length Normalization:</strong> Penalizes long documents so a short article dedicated to a topic outranks a massive document that mentions the term in passing.<br>4. <strong>Fuzzy Matching:</strong> Uses Levenshtein Edit Distance (insertions, deletions, substitutions) mapped to a Finite State Automaton to find matches within edit distance $\\le 2$.</p>",
      "conceptual_breakdown": [
        "<strong>BM25 vs TF-IDF:</strong> BM25 saturates Term Frequency (a document with 100 occurrences of a word doesn't get 10x more score than one with 10 occurrences).",
        "<strong>N-Gram Tokenization:</strong> Splits words into sub-strings (e.g. 'search' -> `['se', 'sea', 'sear', 'search']`) for instant auto-complete typeahead suggestions."
      ],
      "failure_scenarios": "<strong>Fuzzy Wildcard Performance Degradation:</strong> Executing fuzzy queries with edit distance >2 or leading wildcards on huge vocabularies forces Lucene to traverse millions of FST paths, spiking CPU usage to 100%. <em>Mitigation:</em> Limit prefix length (`min_prefix_length = 2`) and max expansions.",
      "common_mistakes": [
        {
          "mistake": "Running deep pagination (`from: 10000, size: 10`) on Elasticsearch clusters.",
          "correction": "Deep pagination forces coordinator nodes to merge and sort millions of results across all shards. Use `search_after` with cursor sorting instead."
        }
      ],
      "interview_questions": [
        {
          "question": "Why is BM25 preferred over traditional TF-IDF in modern search engines?",
          "answer": "BM25 introduces Term Frequency Saturation (preventing keyword-stuffing documents from dominating rankings) and Document Length Normalization (adjusting scores based on whether a document is longer or shorter than the average document length in the corpus)."
        }
      ]
    },
    {
      "id": "vector-databases-and-embeddings",
      "title": "Vector Databases & Semantic Search: HNSW, Pinecone & Embeddings",
      "definition": "Vector Databases (Pinecone, Milvus, Qdrant, pgvector) store high-dimensional dense vector embeddings generated by machine learning models, performing Approximate Nearest Neighbor (ANN) search to find semantic similarity rather than exact keyword matches.",
      "why_we_need_it": "Keyword search fails when users search for concepts using different words (e.g. 'inexpensive puppy food' vs 'cheap dog kibble'). Semantic vector search understands conceptual meaning.",
      "real_world_analogy": "A 3D solar system where every book is a planet: books about space travel float close to NASA manuals, while romance novels float together on the other side of the galaxy. Finding similar items is simply finding the closest neighboring planets in space.",
      "how_it_works": "<p>1. <strong>Embedding Generation:</strong> An AI embedding model (e.g., text-embedding-3-small) converts text/images into a 1536-dimensional floating-point array: $[0.024, -0.812, 0.449, ...]$.<br>2. <strong>Vector Similarity Metrics:</strong> Cosine Similarity, Dot Product, or Euclidean Distance (L2).<br>3. <strong>HNSW (Hierarchical Navigable Small World):</strong> Multi-layer geometric graph indexing structure that navigates high-dimensional space in $O(\\log N)$ time with skip-list highway layers.<br>4. <strong>Hybrid Search:</strong> Combines Dense Vector Search (semantic meaning) with Sparse BM25 Keyword Search (exact keyword matches) using Reciprocal Rank Fusion (RRF).</p>",
      "conceptual_breakdown": [
        "<strong>RAG (Retrieval-Augmented Generation):</strong> User query -> Generate embedding -> Query Vector DB for top-5 chunks -> Feed chunks to LLM context.",
        "<strong>HNSW vs IVF:</strong> HNSW provides high recall and low latency at the cost of high RAM usage; IVF uses clustering for lower memory footprint.",
        "<strong>pgvector:</strong> PostgreSQL extension adding native vector indexing (`vector(1536)`) for applications wanting to keep relational data and vector embeddings in a single database."
      ],
      "failure_scenarios": "<strong>RAM Exhaustion in HNSW Indexes:</strong> HNSW indexes must reside entirely in RAM for fast graph traversal. Storing 50 million 1536-dimensional vectors requires over 300GB of high-speed RAM. <em>Mitigation:</em> Use Product Quantization (PQ) or Scalar Quantization (SQ) to compress vectors by 4x-8x.",
      "common_mistakes": [
        {
          "mistake": "Relying exclusively on Vector Search for SKU numbers, legal terms, or exact product IDs.",
          "correction": "Vector search struggles with exact alphanumeric serial numbers. Always use Hybrid Search (BM25 + Dense Vectors)."
        }
      ],
      "interview_questions": [
        {
          "question": "How does Hierarchical Navigable Small World (HNSW) achieve sub-10ms nearest neighbor search across millions of vectors?",
          "answer": "HNSW constructs a multi-layered geometric proximity graph inspired by Skip Lists. Top layers have sparse nodes with long-distance links for rapid coarse-grained navigation across the vector space; lower layers have denser links for fine-grained local neighborhood exploration, achieving logarithmic $O(\\log N)$ search complexity."
        }
      ]
    }
  ]
}

# -------------------------------------------------------------
# MODULE 19: Real-Time & Stream Processing
# -------------------------------------------------------------
mod_19 = {
  "module_id": "19",
  "module_title": "Real-Time & Stream Processing",
  "description": "Master stream processing architectures: Apache Flink vs Kafka Streams, Windowing operations (Tumbling, Sliding, Session), State Management, and Exactly-Once Semantics.",
  "topics": [
    {
      "id": "stream-processing-fundamentals",
      "title": "Batch vs Stream Processing: Apache Flink, Kafka Streams & Spark Streaming",
      "definition": "Batch Processing processes bounded, finite historical datasets in scheduled bulk intervals (e.g. hourly Hadoop/Spark jobs). Stream Processing continuously processes unbounded, infinite data streams in real-time with millisecond-to-second latencies (e.g. Apache Flink, Kafka Streams).",
      "why_we_need_it": "Fraud detection, live ride pricing, stock market alerts, and real-time gaming leaderboards cannot wait for nightly batch jobs; actions must be calculated the instant events happen.",
      "real_world_analogy": "Batch processing is collecting 100 dirty shirts in a laundry basket and washing them all on Sunday afternoon. Stream processing is washing each shirt the second you take it off.",
      "how_it_works": "<p>1. <strong>Event Time vs Processing Time:</strong> Event Time is when the event actually occurred on the client device (embedded timestamp in payload); Processing Time is when the stream worker server received the event.<br>2. <strong>Watermarks:</strong> A progress mechanism signaling that all events up to timestamp $T$ have arrived, allowing the engine to close windows and handle out-of-order/late-arriving data.<br>3. <strong>Stateful Stream Processing:</strong> Flink maintains local state (e.g. RocksDB) checkpointed asynchronously to S3/HDFS for instant state recovery.</p>",
      "conceptual_breakdown": [
        "<strong>Kappa Architecture:</strong> A single stream processing pipeline (Kafka + Flink) handles both real-time streaming and historical batch replays, replacing complex dual-pipeline Lambda architectures.",
        "<strong>Kafka Streams vs Apache Flink:</strong> Kafka Streams is a lightweight Java library embedded inside standard microservice JVMs; Flink is a dedicated distributed compute cluster engine."
      ],
      "failure_scenarios": "<strong>Late-Arriving Data Drops:</strong> Mobile users in airplane mode submit events 2 hours late. If the watermark has already advanced past that window, events are discarded unless explicit side-outputs are configured. <em>Mitigation:</em> Configure Allowed Lateness windows and Side Outputs in Flink.",
      "common_mistakes": [
        {
          "mistake": "Using processing-time windowing for analytics dependent on real-world chronological order.",
          "correction": "Always use Event-Time windowing with Watermarks for business-critical stream metrics."
        }
      ],
      "interview_questions": [
        {
          "question": "What is the difference between Event Time and Processing Time in stream processing?",
          "answer": "Event Time is the exact timestamp when the user action occurred at the source (e.g. mobile sensor); Processing Time is the wall-clock time of the server node executing the streaming code. Event Time guarantees deterministic results regardless of network delays or data replays."
        }
      ]
    },
    {
      "id": "windowing-and-stateful-processing",
      "title": "Stream Windowing Strategies: Tumbling, Sliding, Session & Global Windows",
      "definition": "Windowing divides unbounded continuous event streams into finite chunks of time or event counts for stateful aggregations (e.g., counting total clicks per 5-minute window).",
      "why_we_need_it": "You cannot calculate 'average clicks' across an infinite stream; you must bound the calculation to specific discrete time windows.",
      "real_world_analogy": "A restaurant tab window: A Tumbling window is a fixed hourly bill (12-1, 1-2). A Sliding window is checking your spending over the 'past 60 minutes' every 10 minutes. A Session window opens when you sit at the table and closes 30 minutes after your last drink order.",
      "how_it_works": "<p>1. <strong>Tumbling Windows:</strong> Fixed size, non-overlapping contiguous time blocks (e.g., every 5 minutes: 12:00-12:05, 12:05-12:10).<br>2. <strong>Sliding (Hopping) Windows:</strong> Fixed size with overlapping slide intervals (e.g., 10-minute window sliding every 1 minute).<br>3. <strong>Session Windows:</strong> Dynamically bounded by periods of user inactivity (e.g., group events until an inactivity gap of 30 minutes occurs).<br>4. <strong>Global Windows:</strong> Groups all events with identical keys indefinitely, triggered by custom counts.</p>",
      "comparison_matrix": {
        "title": "Stream Windowing Types Comparison",
        "columns": ["Window Type", "Boundaries", "Overlapping", "Trigger Condition", "Common Use Case"],
        "rows": [
          ["Tumbling Window", "Fixed duration (e.g. 5m)", "No (Clean adjacent edges)", "Window time expires", "Hourly revenue totals, metric dashboards"],
          ["Sliding Window", "Fixed duration, slide interval", "Yes (Events belong to multiple windows)", "Slide interval expires", "Moving average latency, 1-hour rate limiters"],
          ["Session Window", "Dynamic (Inactivity gap)", "No (Data-driven boundaries)", "Gap timeout exceeded", "User web browsing sessions, gaming matches"],
          ["Count Window", "Fixed element count (e.g. 100)", "No", "N items received", "Batch buffer flushing, sensor batching"]
        ]
      },
      "failure_scenarios": "<strong>Memory Leak in Long Session Windows:</strong> If a user or bot continuously emits an event every 10 seconds, the session window gap timeout never expires, causing Flink to accumulate state indefinitely until the worker dies of Out Of Memory (OOM). <em>Mitigation:</em> Configure maximum session window duration limits.",
      "common_mistakes": [
        {
          "mistake": "Setting ultra-small slide intervals (e.g. 1-hour window sliding every 100ms) leading to exponential memory state duplication.",
          "correction": "Choose slide intervals proportional to business requirements (e.g. 1-hour window sliding every 1 minute)."
        }
      ],
      "interview_questions": [
        {
          "question": "How do Session Windows differ from Tumbling and Sliding windows in stream processing?",
          "answer": "Tumbling and Sliding windows have fixed pre-determined time boundaries; Session windows have dynamic, data-driven boundaries that expand as long as events arrive within a configured inactivity gap timeout and close only when silence is detected."
        }
      ]
    },
    {
      "id": "exactly-once-processing-semantics",
      "title": "Delivery Semantics: At-Least-Once, At-Most-Once & Exactly-Once (EOS)",
      "definition": "Message delivery semantics define the processing guarantees of a distributed streaming pipeline under node failures and network retries: At-Most-Once (0 or 1), At-Least-Once (1 or more, with duplicates), and Exactly-Once (effectively processed exactly once without loss or duplicates).",
      "why_we_need_it": "In payment processing and financial accounting, duplicating a transaction event charges a customer twice; dropping an event loses money.",
      "real_world_analogy": "Sending a birthday gift: At-Most-Once is mailing the gift once; if the mail truck crashes, you do nothing (gift lost). At-Least-Once is mailing gifts repeatedly until you receive a thank-you letter (friend might get 3 identical gifts). Exactly-Once is sending a gift with a unique tracking code so your friend signs for it once and refuses any duplicate copies.",
      "how_it_works": "<p>1. <strong>At-Most-Once:</strong> Commit offset BEFORE processing message. If processing crashes, message is lost.<br>2. <strong>At-Least-Once:</strong> Commit offset AFTER processing message. If server crashes after processing but before offset commit, message is re-processed on restart (duplicates generated).<br>3. <strong>Exactly-Once Processing (EOS):</strong> Achieved via <strong>Idempotent Sinks</strong> (e.g. DB upserts by unique UUID) OR <strong>Two-Phase Commit (2PC) Stream Transactions</strong> (e.g. Kafka Transactions + Flink Checkpointing with Chandy-Lamport distributed snapshotting).</p>",
      "conceptual_breakdown": [
        "<strong>'Effectively Once':</strong> Distributed systems cannot stop network packets from being physically transmitted twice. EOS means the end state is *as if* the message was processed exactly once.",
        "<strong>Chandy-Lamport Algorithm:</strong> Flink injects Barrier markers into the event stream to snapshot consistent operator state without pausing execution."
      ],
      "failure_scenarios": "<strong>Duplicate Side Effects in External APIs:</strong> An EOS pipeline successfully deduplicates database writes via Kafka transactions, but an uncoordinated step calls a 3rd-party non-transactional email API inside the streaming loop, sending duplicate emails during worker recovery restarts.",
      "common_mistakes": [
        {
          "mistake": "Assuming `Kafka EOS` guarantees exactly-once delivery to non-transactional external HTTP endpoints.",
          "correction": "Kafka EOS only guarantees exactly-once within the Kafka-to-Kafka/Flink ecosystem. Interfacing with external systems requires idempotent receiver keys."
        }
      ],
      "interview_questions": [
        {
          "question": "How does Apache Flink achieve End-to-End Exactly-Once Processing across Kafka and external sinks?",
          "answer": "Flink coordinates distributed Checkpoint Barriers (Chandy-Lamport algorithm) with a Two-Phase Commit (2PC) sink protocol. On checkpoint start, Flink opens a transaction; when all operators acknowledge the checkpoint barrier, the coordinator commits the transaction to Kafka/DB atomically."
        }
      ]
    }
  ]
}

# -------------------------------------------------------------
# MODULE 20: Content Delivery Networks (CDNs) & Edge Computing
# -------------------------------------------------------------
mod_20 = {
  "module_id": "20",
  "module_title": "Content Delivery Networks (CDNs) & Edge Computing",
  "description": "Master CDN Edge caching, Dynamic Site Acceleration (DSA), BGP Anycast routing, Cache-Control headers, invalidation strategies, and Edge Workers (Cloudflare Workers / Lambda@Edge).",
  "topics": [
    {
      "id": "cdn-architecture-and-edge-caching",
      "title": "CDN Architecture: Points of Presence (PoPs), Edge Caching & Anycast BGP",
      "definition": "A Content Delivery Network (CDN) is a geographically distributed network of Edge proxy servers (Points of Presence / PoPs) that cache and deliver web content (images, videos, HTML, API responses) close to end users to minimize latency and offload origin server infrastructure.",
      "why_we_need_it": "Speed of light in fiber optic cables takes ~70ms to travel from Tokyo to Virginia. A user in Tokyo requesting data from an origin in Virginia experiences high latency and TCP handshake delays. Serving from a Tokyo CDN Edge PoP delivers content in <5ms.",
      "real_world_analogy": "A global chain of neighborhood grocery convenience stores: instead of every customer flying to the central factory in Switzerland to buy chocolate, the factory ships pallets to local neighborhood stores so customers buy chocolate in 2 minutes.",
      "how_it_works": "<p>1. <strong>BGP Anycast Routing:</strong> Multiple CDN PoP servers across 100+ countries share the exact same public IP address. Internet routers automatically direct user packets to the topologically closest PoP.<br>2. <strong>Static Content Delivery:</strong> Images, CSS, JS, and video segments are cached with long TTLs. Cache Hits never touch origin servers.<br>3. <strong>Dynamic Site Acceleration (DSA):</strong> For non-cacheable dynamic requests, CDN maintains persistent, warmed TCP/TLS connection pools to the origin and uses route optimization across private backbone fibers to bypass congested public internet routes.</p>",
      "conceptual_breakdown": [
        "<strong>Origin Shield (Tiered Caching):</strong> An intermediate caching layer between Edge PoPs and Origin that consolidates cache misses, preventing origin thundering herds.",
        "<strong>Cache-Control Directives:</strong> `public, max-age=31536000, immutable` for versioned static assets; `s-maxage` for CDN caches vs `max-age` for browser caches.",
        "<strong>Stale-While-Revalidate:</strong> Serves stale cached content instantly to user while asynchronously fetching fresh content from origin in the background."
      ],
      "comparison_matrix": {
        "title": "Edge PoP vs Origin Server Delivery",
        "columns": ["Metric", "Direct Origin Request", "CDN Edge PoP Delivery"],
        "rows": [
          ["Global User Latency", "100ms - 300ms (Cross-continental)", "Sub-10ms (Local edge server)"],
          ["Origin Server Load", "100% of all requests hit origin", "90% - 98% absorbed by CDN edge"],
          ["TLS Handshake Latency", "Full 1-RTT to distant origin", "Terminated at local edge in 2ms"],
          ["DDoS Absorption", "Origin easily saturated", "Absorbed by multi-terabit CDN edge capacity"]
        ]
      },
      "failure_scenarios": "<strong>Instant Global Cache Invalidation Storm:</strong> Running a global wildcard purge (`PURGE /*`) on an e-commerce CDN flushes millions of cached items, causing 100,000 QPS of subsequent user traffic to hit origin servers simultaneously, crashing the database. <em>Mitigation:</em> Use versioned URLs (`/app.v2.js`) and soft purging.",
      "common_mistakes": [
        {
          "mistake": "Using CDN cache purging as the primary mechanism for static asset updates.",
          "correction": "Use Content Hashing / Cache Busting in file names (`bundle.a8f2c.js`) with 1-year immutable cache headers."
        }
      ],
      "interview_questions": [
        {
          "question": "How does BGP Anycast direct users to the nearest CDN Point of Presence (PoP)?",
          "answer": "With BGP Anycast, all CDN edge data centers advertise the exact same IP prefix into the global Internet routing table (BGP). Upstream ISP routers compute the shortest AS-Path and automatically route the user's TCP packets to the topologically nearest PoP data center."
        }
      ]
    },
    {
      "id": "edge-computing-and-workers",
      "title": "Edge Computing: Cloudflare Workers, Lambda@Edge & V8 Isolates",
      "definition": "Edge Computing executes lightweight application code and serverless functions directly at CDN edge nodes across the globe, processing user requests within microseconds of their physical location.",
      "why_we_need_it": "Executing authentication checks, geolocation redirects, A/B testing variations, and personalization at the origin adds unnecessary cross-continental latency. Edge computing evaluates logic right at the user's doorstep.",
      "real_world_analogy": "A border customs officer stamping visas at the airport gate (Edge) instead of making passengers fly to the capital city just to get a stamp before entering.",
      "how_it_works": "<p>1. <strong>V8 Isolates (Cloudflare Workers):</strong> Instead of spinning up heavy Docker containers or VMs (which take 500ms+ to boot), Edge Workers run inside lightweight Google V8 JavaScript Isolates with <5ms startup time and tiny memory footprints.<br>2. <strong>Edge Key-Value / D1 Databases:</strong> Globally distributed, eventually consistent edge key-value stores (Workers KV, Upstash) replicated to all PoPs.<br>3. <strong>Common Use Cases:</strong> Dynamic A/B testing, JWT validation, geo-fencing, header mutation, dynamic image resizing, and bot mitigation.</p>",
      "conceptual_breakdown": [
        "<strong>Zero Cold Starts:</strong> V8 Isolates start in under 5 milliseconds.",
        "<strong>Sub-Request Limits:</strong> Edge workers have strict CPU execution time limits (e.g. 50ms) to maintain edge throughput.",
        "<strong>Edge Rendering (SSR):</strong> Rendering HTML pages at the edge using frameworks like Next.js and Remix."
      ],
      "failure_scenarios": "<strong>Origin State Desynchronization at Edge:</strong> An edge worker writes to a locally replicated edge KV store that has a 60-second replication propagation delay, causing a user traveling between regions to read stale state. <em>Mitigation:</em> Route writes to centralized databases or use strong consistency options.",
      "common_mistakes": [
        {
          "mistake": "Running long compute-heavy machine learning inference or heavy batch parsing inside edge workers.",
          "correction": "Keep Edge Workers focused on lightweight routing, auth validation, and rapid caching transforms; delegate heavy computing to core cloud data centers."
        }
      ],
      "interview_questions": [
        {
          "question": "Why are V8 Isolates superior to containerized micro-VMs for Edge Computing?",
          "answer": "V8 Isolates share a single running process memory space while enforcing strict security isolation, allowing thousands of tenant scripts to run on a single edge server with zero container startup overhead, sub-millisecond cold starts, and minimal RAM footprint per tenant."
        }
      ]
    }
  ]
}

modules = [mod_16, mod_17, mod_18, mod_19, mod_20]
for m in modules:
    filename = os.path.join(CONTENT_DIR, f"module_{m['module_id']}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print(f"Generated {filename} with {len(m['topics'])} topics")
