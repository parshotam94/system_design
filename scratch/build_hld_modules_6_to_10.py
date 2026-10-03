import json
import os

CONTENT_DIR = "content/hld"
os.makedirs(CONTENT_DIR, exist_ok=True)

# -------------------------------------------------------------
# MODULE 06: System Architecture Patterns
# -------------------------------------------------------------
mod_06 = {
  "module_id": "06",
  "module_title": "System Architecture Patterns",
  "description": "Master monolithic vs microservices trade-offs, layered & hexagonal architectures, serverless event-driven topologies, and CQRS / Event Sourcing patterns.",
  "topics": [
    {
      "id": "monolith-to-microservices",
      "title": "Monolith, Modular Monolith & Microservices Trade-offs",
      "definition": "Monoliths package all business domains, UI, and persistence into a single deployable binary. Microservices decompose systems into independently deployable, bounded-context services communicating over lightweight network protocols (HTTP/gRPC/Kafka).",
      "why_we_need_it": "Monoliths start fast with zero network serialization overhead, but as engineering organizations grow to hundreds of developers, shared database schemas and single deployment pipelines cause catastrophic deployment bottlenecks and blast radius explosions.",
      "real_world_analogy": "A Monolith is a Swiss Army Knife: compact, all-in-one, handy. Microservices are an entire specialized industrial tool workshop: each tool is maintained by a separate craftsman and can be upgraded independently without breaking the entire building.",
      "how_it_works": "<p>In a <strong>Modular Monolith</strong>, business domains (Orders, Users, Payments) are strictly isolated into distinct code packages with explicit interface boundaries and private database tables, but run within a single process. In <strong>Microservices</strong>, each bounded context runs as its own containerized process with its own private database, communicating asynchronously via message brokers or synchronously via gRPC/REST.</p>",
      "conceptual_breakdown": [
        "<strong>Conway's Law:</strong> Organizations design systems that mirror their communication structures. Independent two-pizza teams require independent microservice deployables.",
        "<strong>Database per Service:</strong> The cardinal rule of microservices. Sharing a database across services couples their schemas and breaks independent deployability.",
        "<strong>Dual-Edged Sword:</strong> Microservices introduce distributed tracing complexity, network latency hops, partial failures, eventual consistency dilemmas, and data synchronization overhead."
      ],
      "arch_diagram": {
        "title": "Monolith vs Microservices Architecture Topology",
        "tiers": [
          {
            "label": "Client Layer",
            "nodes": [
              {
                "name": "Single Gateway / LB",
                "type": "gateway",
                "icon": "🚪",
                "what": "Ingress API Gateway & TLS termination",
                "why": "Single entrypoint for web and mobile clients",
                "when": "Always used to route traffic across services",
                "failure": "Multi-region redundant gateway failover"
              }
            ]
          },
          {
            "label": "Services Layer",
            "nodes": [
              {
                "name": "Auth Service",
                "type": "service",
                "icon": "🔑",
                "what": "JWT tokens & identity validation",
                "why": "Decoupled authentication logic",
                "when": "On every authenticated request",
                "failure": "Token validation cached locally via public keys"
              },
              {
                "name": "Order Service",
                "type": "service",
                "icon": "📦",
                "what": "Checkout & order lifecycle workflows",
                "why": "High transaction isolation",
                "when": "User creates or checks orders",
                "failure": "Saga pattern compensation rollback"
              },
              {
                "name": "Payment Service",
                "type": "service",
                "icon": "💳",
                "what": "Third-party payment gateway integration",
                "why": "PCI-DSS compliance isolation",
                "when": "Order payment processing",
                "failure": "Idempotent payment capture and retry queues"
              }
            ]
          },
          {
            "label": "Decoupled Databases",
            "nodes": [
              {
                "name": "Auth DB (Redis/Postgres)",
                "type": "database",
                "icon": "🗄️",
                "what": "User credentials & refresh tokens",
                "why": "Sub-millisecond token lookups",
                "when": "Login and session refresh",
                "failure": "Replica failover"
              },
              {
                "name": "Order DB (PostgreSQL)",
                "type": "database",
                "icon": "🐘",
                "what": "Relational ACID storage for order line items",
                "why": "Strict financial consistency",
                "when": "Order placement",
                "failure": "Multi-AZ synchronous replication"
              },
              {
                "name": "Payment DB (DynamoDB)",
                "type": "database",
                "icon": "⚡",
                "what": "High throughput append-only ledger",
                "why": "Infinite scaling with partition keys",
                "when": "Payment capture events",
                "failure": "Global tables multi-region failover"
              }
            ]
          }
        ]
      },
      "system_flow_animation": {
        "title": "Microservice Saga Pattern Checkout Flow",
        "steps": [
          {
            "num": 1,
            "title": "Client Initiates Checkout",
            "actor": "Client -> API Gateway",
            "desc": "Client sends POST /orders with Cart Items and Idempotency Key.",
            "node": "Single Gateway / LB"
          },
          {
            "num": 2,
            "title": "Order Service Creates Pending Order",
            "actor": "API Gateway -> Order Service",
            "desc": "Order service creates order in state 'PENDING' and publishes 'OrderCreated' event to Kafka.",
            "node": "Order Service"
          },
          {
            "num": 3,
            "title": "Payment Service Consumes & Charges",
            "actor": "Payment Service -> Stripe API",
            "desc": "Payment service consumes event, charges credit card, and publishes 'PaymentSucceeded'.",
            "node": "Payment Service"
          },
          {
            "num": 4,
            "title": "Order Confirmed & Response Returned",
            "actor": "Order Service -> Client",
            "desc": "Order service transitions status to 'CONFIRMED' and pushes WebSocket update to user.",
            "node": "Order DB (PostgreSQL)"
          }
        ]
      },
      "comparison_matrix": {
        "title": "Architectural Paradigms Comparison",
        "columns": ["Dimension", "Monolith", "Modular Monolith", "Microservices"],
        "rows": [
          ["Deployment Complexity", "Very Low (Single artifact)", "Low (Single artifact)", "High (Kubernetes, CI/CD per service)"],
          ["Network Latency", "Zero (In-memory calls)", "Zero (In-memory function calls)", "High (Network hops + serialization)"],
          ["Team Scalability", "Poor (>50 devs causes lock contention)", "High (Domain code ownership)", "Very High (Independent service teams)"],
          ["Data Consistency", "Strong ACID DB transactions", "Strong ACID DB transactions", "Eventual consistency (Sagas / 2PC)"],
          ["Blast Radius", "High (Bug crashes entire process)", "High (Single runtime crash)", "Low (Isolated service crashes)"]
        ]
      },
      "failure_scenarios": "<strong>Distributed Partial Failures:</strong> Service A calls B, which calls C. If C hangs, thread pools in A and B get exhausted, causing cascading cluster failure. <em>Mitigation:</em> Strict timeout policies (e.g., 200ms), circuit breakers (e.g., Resilience4j/Envoy), and graceful fallback degrades.",
      "common_mistakes": [
        {
          "mistake": "Adopting microservices before product-market fit or with a team of 3 developers.",
          "correction": "Start with a well-structured Modular Monolith. Refactor bounded contexts into microservices only when organizational scaling demands it."
        },
        {
          "mistake": "Multiple microservices directly querying or mutating each other's database tables.",
          "correction": "Strictly enforce Database-per-Service. Cross-service communication must always occur via public API contracts or event streams."
        }
      ],
      "interview_questions": [
        {
          "question": "How do you handle distributed transactions across microservices without 2-Phase Commit (2PC)?",
          "answer": "Use the <strong>Saga Pattern</strong> (Choreographed via Kafka events or Orchestrated via a state machine workflow engine like Temporal/AWS Step Functions). Each local transaction updates its own DB and publishes an event; if a step fails, compensating transactions are executed in reverse order to restore consistency."
        }
      ]
    },
    {
      "id": "three-tier-and-layered-architecture",
      "title": "Three-Tier, N-Tier & Hexagonal / Clean Architecture",
      "definition": "Layered and Hexagonal (Ports and Adapters) architectures structure application code into concentric rings of responsibility, isolating business logic from external frameworks, databases, and transport protocols.",
      "why_we_need_it": "Without architectural boundaries, database queries and HTTP handlers become intertwined with core domain algorithms, making testing impossible and locking the codebase into specific third-party vendors.",
      "real_world_analogy": "A power outlet and plug: Your laptop charger (domain logic) uses a standardized 2-prong port. It does not care if the electricity comes from solar, nuclear, or hydro (adapters).",
      "how_it_works": "<p>The <strong>Dependency Inversion Principle</strong> dictates that inner layers define interfaces (Ports), and outer infrastructure layers implement those interfaces (Adapters). Domain business logic has ZERO external dependencies.</p>",
      "conceptual_breakdown": [
        "<strong>Domain Layer (Core):</strong> Pure business entities and domain rules with no dependencies on SQL, HTTP, or libraries.",
        "<strong>Application Layer (Use Cases):</strong> Orchestrates domain models to fulfill application use cases (e.g., RegisterUserUseCase).",
        "<strong>Infrastructure / Adapters:</strong> PostgreSQL repository implementations, REST API controllers, Kafka event producers."
      ],
      "tradeoffs": "<strong>Trade-off:</strong> Hexagonal architecture introduces boilerplate DTO mappers and interface abstractions in exchange for near-100% unit-testability and seamless technology migration (e.g. swapping PostgreSQL for DynamoDB with zero business logic changes).",
      "failure_scenarios": "<strong>Domain Leakage:</strong> Leaking ORM models (e.g., Hibernate/GORM entities) into API responses exposes internal DB columns to public clients. Always use separate API DTOs.",
      "common_mistakes": [
        {
          "mistake": "Calling the database directly from UI/HTTP controller handlers.",
          "correction": "Inject an Application Service / UseCase interface into the controller to maintain separation of concerns."
        }
      ],
      "interview_questions": [
        {
          "question": "What is the primary benefit of Hexagonal Architecture in high-concurrency production systems?",
          "answer": "It allows mocking all I/O boundaries during testing, enables rapid refactoring of database storage engines without rewriting core algorithms, and enforces strict separation between network transport protocols and business invariants."
        }
      ]
    },
    {
      "id": "serverless-and-event-driven",
      "title": "Serverless Functions (FaaS) & Event-Driven Architecture",
      "definition": "Serverless (FaaS) executes stateless code snippets on demand in ephemeral sandboxes (AWS Lambda, Google Cloud Run) with automatic scaling to zero. Event-Driven Architecture (EDA) coordinates decoupled services via asynchronous event publication and consumption.",
      "why_we_need_it": "Traditional 24/7 provisioned servers incur continuous compute costs during idle periods. Serverless allows pay-per-millisecond execution, while event-driven architecture eliminates synchronous blocking HTTP latency.",
      "real_world_analogy": "Uber driver dispatch: A passenger requesting a ride publishes a 'RideRequested' event. Nearby drivers consume this event asynchronously without the passenger having to call 50 drivers one by one on the phone.",
      "how_it_works": "<p>Producers emit immutable domain events (e.g. `UserSignedUp`, `VideoUploaded`) to an event router or log (AWS EventBridge, Apache Kafka). Independent consumer services subscribe to event topics, processing messages asynchronously with retry policies and dead-letter queues (DLQs).</p>",
      "conceptual_breakdown": [
        "<strong>Cold Starts:</strong> The latency spike (100ms - 2s) when a cloud provider spins up a new micro-VM container sandbox on the first invocation.",
        "<strong>At-Least-Once Delivery:</strong> Event buses guarantee messages won't be lost, but duplicate events can arrive. Consumers MUST be idempotent.",
        "<strong>Dead-Letter Queue (DLQ):</strong> Unprocessable or poison-pill events are routed to a separate queue after maximum retry attempts for developer inspection."
      ],
      "tradeoffs": "<strong>Trade-off:</strong> Eventual consistency and asynchronous debugging complexity in exchange for infinite burst elasticity, decoupled deployment lifecycles, and zero idle compute costs.",
      "failure_scenarios": "<strong>Event Loopback Storm:</strong> Service A emits Event 1 -> Service B consumes it and emits Event 2 -> Service A consumes Event 2 and emits Event 1 again, burning millions of Lambda executions. <em>Mitigation:</em> Event idempotency hashes and strict topic cycle validation.",
      "common_mistakes": [
        {
          "mistake": "Using serverless functions for long-running batch computing (>15 min) or persistent WebSocket connections.",
          "correction": "Use dedicated containerized workloads (ECS/Kubernetes) for long-lived processes and persistent TCP sockets."
        }
      ],
      "interview_questions": [
        {
          "question": "How do you mitigate serverless cold starts in latency-critical APIs?",
          "answer": "Use Provisioned Concurrency, keep deployment packages lightweight (avoid huge dependencies), choose fast runtimes (Go/Rust/Node.js over heavy JVM runtimes), and configure periodic warm-up pings."
        }
      ]
    },
    {
      "id": "cqrs-and-event-sourcing",
      "title": "CQRS (Command Query Responsibility Segregation) & Event Sourcing",
      "definition": "CQRS separates data mutation operations (Commands) from read operations (Queries) into distinct models and database engines. Event Sourcing persists state not as a mutable snapshot, but as an immutable append-only sequence of historical domain events.",
      "why_we_need_it": "In high-scale systems, read workloads (e.g. 100,000 QPS) often dwarf write workloads (e.g. 500 QPS). Traditional single-database schemas force difficult indexing compromises between write throughput and complex analytical search queries.",
      "real_world_analogy": "A bank account ledger: The bank never stores just a single mutable number `balance = $500`. It stores every single deposit and withdrawal transaction line. Your balance is calculated by replaying all historical ledger entries.",
      "how_it_works": "<p>1. <strong>Command Side:</strong> Writes send commands to an ACID write store (e.g., PostgreSQL or EventStoreDB), which appends an immutable event (`ItemAddedToCart`).<br>2. <strong>Projection Worker:</strong> Asynchronously consumes events and projects denormalized read models into specialized query databases (e.g. Elasticsearch for full-text search, Redis for key-value lookups).<br>3. <strong>Query Side:</strong> Reads query the read-optimized store directly with sub-5ms response times.</p>",
      "conceptual_breakdown": [
        "<strong>Command Side:</strong> Focuses exclusively on domain validation, invariants, and high-speed appending.",
        "<strong>Query Side:</strong> Focuses exclusively on denormalized, zero-JOIN reads customized for UI views.",
        "<strong>Event Store:</strong> The single source of truth. Entire read databases can be destroyed and rebuilt from scratch by replaying events from offset 0."
      ],
      "comparison_matrix": {
        "title": "CRUD vs CQRS + Event Sourcing",
        "columns": ["Feature", "Traditional CRUD", "CQRS + Event Sourcing"],
        "rows": [
          ["State Storage", "Current mutable snapshot (UPDATE/DELETE)", "Immutable append-only event stream (INSERT only)"],
          ["Audit Trail", "Manual audit tables or triggers", "Built-in 100% complete chronological audit history"],
          ["Read Performance", "Limited by JOINs & relational indexes", "Blazing fast (Denormalized views in Redis/Elasticsearch)"],
          ["Consistency", "Immediate Strong Consistency", "Eventual Consistency between Command and Query stores"],
          ["Implementation Complexity", "Low", "High (Requires event projectors, schema versioning & snapshots)"]
        ]
      },
      "failure_scenarios": "<strong>Projection Lag:</strong> A user updates their profile (Command) and immediately refreshes the page, but the Read Store has not caught up yet due to a 50ms Kafka consumer delay, causing user confusion. <em>Mitigation:</em> Read-your-own-writes consistency (routing reads to primary or using version tokens).",
      "common_mistakes": [
        {
          "mistake": "Applying Event Sourcing and CQRS to simple CRUD applications like blogs or basic internal dashboards.",
          "correction": "Only use CQRS/Event Sourcing for complex domains with rich domain events, high read-to-write disparities, or strict regulatory audit requirements (e.g., Banking, E-commerce, Healthcare)."
        }
      ],
      "interview_questions": [
        {
          "question": "How do you handle event schema evolution in an Event Sourced system when business rules change over time?",
          "answer": "Use Schema Upcasting (converting old event versions v1 -> v2 dynamically when reading from the log), Weak Schema validation (Avro/Protobuf optional fields), or version-specific event handler methods."
        }
      ]
    }
  ]
}

# -------------------------------------------------------------
# MODULE 07: Load Balancing & Reverse Proxies
# -------------------------------------------------------------
mod_07 = {
  "module_id": "07",
  "module_title": "Load Balancing & Reverse Proxies",
  "description": "Master Layer 4 vs Layer 7 load balancing, balancing algorithms (Round Robin, Least Connections, Consistent Hashing), active health checking, SSL termination, and high-availability failover.",
  "topics": [
    {
      "id": "why-load-balancing-l4-vs-l7",
      "title": "Why Load Balancers? Layer 4 (Transport) vs Layer 7 (Application) Routing",
      "definition": "Load Balancers distribute incoming network traffic across multiple backend servers to prevent overload, eliminate single points of failure, and maximize throughput. Layer 4 operates at the transport layer (TCP/UDP IPs & Ports), while Layer 7 operates at the application layer (HTTP headers, URLs, cookies).",
      "why_we_need_it": "A single web server can only handle a finite number of concurrent TCP connections and CPU requests. Load balancing allows horizontal scaling from 1 server to thousands seamlessly behind a single stable IP.",
      "real_world_analogy": "L4 is like a postal sorting office routing packages based only on the ZIP code on the envelope (IP/Port). L7 is like an executive assistant opening the letter, reading the request (HTTP header/URL), and forwarding it to the exact department specialist.",
      "how_it_works": "<p><strong>Layer 4 LB (e.g., AWS NLB, Linux IPVS, HAProxy TCP mode):</strong> Routes raw TCP packets using a 5-tuple hash (Source IP, Source Port, Dest IP, Dest Port, Protocol) without decrypting TLS or inspecting HTTP headers. Extremely high throughput (>10M packets/sec).<br><strong>Layer 2/7 LB (e.g., AWS ALB, NGINX, Envoy):</strong> Terminates TLS, parses HTTP headers/paths (e.g., `/api/v1/video` -> Video Cluster, `/api/v1/auth` -> Auth Cluster), inspects cookies for sticky sessions, and applies rate limiting.</p>",
      "conceptual_breakdown": [
        "<strong>L4 Advantages:</strong> Minimal CPU overhead, ultra-low latency (<1ms), packet-level NAT routing.",
        "<strong>L7 Advantages:</strong> Intelligent content-based routing, header mutation, TLS offloading, gzip compression, and granular microservice path routing.",
        "<strong>Topology Pattern:</strong> High-traffic systems use L4 LBs at the outer edge to balance traffic across a pool of L7 NGINX/Envoy reverse proxies."
      ],
      "arch_diagram": {
        "title": "Two-Tier Load Balancing Architecture (L4 + L7)",
        "tiers": [
          {
            "label": "Internet & DNS",
            "nodes": [
              {
                "name": "BGP Anycast DNS",
                "type": "dns",
                "icon": "🌐",
                "what": "Geo-routed DNS IP",
                "why": "Routes user to nearest data center edge",
                "when": "Initial hostname lookup",
                "failure": "BGP route withdrawal on DC outage"
              }
            ]
          },
          {
            "label": "Tier 1: Layer 4 LBs",
            "nodes": [
              {
                "name": "L4 NLB / IPVS Cluster",
                "type": "load_balancer",
                "icon": "⚖️",
                "what": "High throughput TCP packet router",
                "why": "Handles millions of raw packets with zero TLS decrypt CPU cost",
                "when": "TCP connection establishment",
                "failure": "ECMP (Equal-Cost Multi-Path) hardware router failover"
              }
            ]
          },
          {
            "label": "Tier 2: Layer 7 Reverse Proxies",
            "nodes": [
              {
                "name": "NGINX / Envoy API Gateway",
                "type": "gateway",
                "icon": "🛡️",
                "what": "TLS termination & path-based router",
                "why": "Routes /orders to Order App and /users to User App",
                "when": "HTTP request processing",
                "failure": "Health check removes unhealthy node in 1s"
              }
            ]
          },
          {
            "label": "Application Pools",
            "nodes": [
              {
                "name": "App Server Pool A",
                "type": "service",
                "icon": "🚀",
                "what": "Stateless backend application instances",
                "why": "Executes business logic",
                "when": "On incoming HTTP requests",
                "failure": "Auto-scaling group replaces crashed instances"
              },
              {
                "name": "App Server Pool B",
                "type": "service",
                "icon": "🚀",
                "what": "Stateless backend application instances",
                "why": "Executes business logic",
                "when": "On incoming HTTP requests",
                "failure": "Auto-scaling group replaces crashed instances"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Layer 4 vs Layer 7 Load Balancing Matrix",
        "columns": ["Feature", "Layer 4 (Transport)", "Layer 7 (Application)"],
        "rows": [
          ["Protocol Level", "TCP / UDP / IP", "HTTP / HTTPS / gRPC / WebSockets"],
          ["TLS Decryption", "Pass-through (No decryption)", "Terminates & decrypts SSL/TLS certificates"],
          ["Path/Header Routing", "Not possible", "Fully supported (e.g. /checkout vs /search)"],
          ["Performance & QPS", "Extremely fast (Millions of QPS, <0.5ms latency)", "Moderate (CPU intensive parsing, 10k-100k QPS per core)"],
          ["Security & WAF", "Basic IP/Port ACL firewall rules", "Full WAF inspection (SQLi, XSS, header injection)"]
        ]
      },
      "failure_scenarios": "<strong>Load Balancer as a Single Point of Failure (SPOF):</strong> If the single LB hardware crashes, the entire system goes down. <em>Mitigation:</em> Active-Passive or Active-Active LB clusters with VRRP (Virtual Router Redundancy Protocol) / Keepalived and BGP Anycast.",
      "common_mistakes": [
        {
          "mistake": "Terminating SSL on each backend application server individually instead of the Load Balancer / Reverse Proxy.",
          "correction": "Offload SSL/TLS termination at the L7 Load Balancer / API Gateway to save CPU cycles on application nodes and centralize certificate renewal."
        }
      ],
      "interview_questions": [
        {
          "question": "How does Equal-Cost Multi-Path (ECMP) routing enable horizontal scaling of Load Balancers?",
          "answer": "ECMP is a network layer routing strategy where routers hash packet headers and distribute traffic across multiple physical load balancer nodes sharing the same Virtual IP (VIP), preventing any single hardware LB from becoming a bottleneck."
        }
      ]
    },
    {
      "id": "load-balancing-algorithms",
      "title": "Balancing Algorithms: Round Robin, Weighted, Least Conn & IP Hash",
      "definition": "Load balancing algorithms determine which specific backend server instance receives each incoming request based on deterministic logic, server capacity, active connection load, or client attributes.",
      "why_we_need_it": "Without proper load distribution algorithms, one server can become saturated and run out of memory while other identical servers sit idle with 2% CPU usage.",
      "real_world_analogy": "A bank with multiple teller lines: Round Robin sends every customer to the next window regardless of how long the current customer's transaction will take. Least Connections sends the customer to whichever teller currently has the fewest people in their queue.",
      "how_it_works": "<p>1. <strong>Round Robin:</strong> Cycles sequentially through server list (Server 1 -> 2 -> 3 -> 1). Best for stateless, uniform request durations.<br>2. <strong>Weighted Round Robin:</strong> Assigns higher frequency to servers with greater CPU/RAM capacities (e.g. Server A with weight 3 gets 3x more traffic than Server B with weight 1).<br>3. <strong>Least Connections:</strong> Routes to the server with the fewest active TCP/HTTP connections. Best for long-lived connections (WebSockets, video streaming, file uploads).<br>4. <strong>IP Hash:</strong> Hashes client IP modulo N. Guarantees that requests from the same user always hit the same server (simple sticky sessions).</p>",
      "conceptual_breakdown": [
        "<strong>Static vs Dynamic:</strong> Static algorithms (Round Robin, IP Hash) ignore real-time server load; Dynamic algorithms (Least Conn, Least Response Time) inspect live latency and connection pools.",
        "<strong>Peak Thundering Herd:</strong> Simple IP Hash breaks down when thousands of corporate users browse behind a single corporate NAT gateway with identical public IPs."
      ],
      "failure_scenarios": "<strong>The Long-Tail Request Trap in Round Robin:</strong> If 1% of requests take 30 seconds (heavy reports) and 99% take 5ms, Round Robin will eventually dump multiple 30s tasks onto one server, causing thread pool starvation. <em>Mitigation:</em> Use Least Connections or Peak-EWMA (Exponentially Weighted Moving Average) latency routing.",
      "common_mistakes": [
        {
          "mistake": "Using IP Hash for load balancing when clients are behind mega-proxies or mobile cellular carrier NATs.",
          "correction": "Use cookie-based session affinity or move session state to a shared Redis cluster so requests can be balanced with Least Connections."
        }
      ],
      "interview_questions": [
        {
          "question": "When would you choose Least Response Time over Least Connections?",
          "answer": "When backend servers have heterogeneous performance characteristics or when some requests involve heavy database processing. Least Response Time directs traffic to the server currently completing requests fastest."
        }
      ]
    },
    {
      "id": "consistent-hashing-deep-dive",
      "title": "Consistent Hashing with Virtual Nodes Deep Dive",
      "definition": "Consistent Hashing is a distributed hashing technique where both keys and server nodes are mapped to a circular 360-degree hash ring (0 to 2^32 - 1). Adding or removing a server only requires remapping k/N keys, rather than all keys as in traditional modulo hashing.",
      "why_we_need_it": "In traditional hash routing `hash(key) % N`, when 1 server out of N fails, N changes to N-1, causing almost 100% of cached keys to hash to new servers. This triggers a catastrophic cache stampede that overwhelms backend databases.",
      "real_world_analogy": "A round table where 4 students are seated. When a paper is passed around, whoever sits immediately clockwise takes it. If one student leaves, only their papers pass to the next student; the other 3 students keep working on their own papers unaffected.",
      "how_it_works": "<p>1. Hash both Server IDs and Object Keys using the same cryptographic hash function (e.g. MurmurHash3 or MD5) onto a 0 to 2^32-1 integer ring.<br>2. To find the server for a key, hash the key and walk <strong>clockwise</strong> along the ring until encountering the first server node.<br>3. <strong>Virtual Nodes (Vnodes):</strong> To prevent non-uniform data distribution and 'hot spots', each physical server is assigned 100 to 256 virtual positions on the ring (e.g., `NodeA#1`, `NodeA#2`, `NodeA#100`).</p>",
      "conceptual_breakdown": [
        "<strong>Minimal Disruption:</strong> Adding server N+1 only takes a fraction of keys from its immediate neighbor. (1/N of keys remapped).",
        "<strong>Virtual Nodes:</strong> Solves data skew and cascade failures by evenly scattering virtual replicas across the entire keyspace.",
        "<strong>Used in:</strong> DynamoDB, Apache Cassandra (Token Ring), Memcached / Redis clusters, Akamai CDN routing."
      ],
      "system_flow_animation": {
        "title": "Consistent Hashing Ring Lookup & Node Addition",
        "steps": [
          {
            "num": 1,
            "title": "Key Hash Calculated",
            "actor": "Client -> Router",
            "desc": "Key 'user_8492' hashes to integer value 1,450,200 on the 32-bit hash ring.",
            "node": "L4 NLB / IPVS Cluster"
          },
          {
            "num": 2,
            "title": "Clockwise Ring Traversal",
            "actor": "Router Ring Lookup",
            "desc": "Router performs binary search on the ring and finds the first node with hash >= 1,450,200 (Node B Virtual Replica #4).",
            "node": "NGINX / Envoy API Gateway"
          },
          {
            "num": 3,
            "title": "Node Addition Scenario",
            "actor": "Cluster Administrator",
            "desc": "New Node D joins the ring. It only claims a small arc of keys from Node B; Nodes A and C remain completely undisturbed.",
            "node": "App Server Pool A"
          }
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> Requires maintaining a synchronized client-side or proxy routing table of the hash ring in exchange for preventing database collapse during cluster auto-scaling.",
      "failure_scenarios": "<strong>Cascading Node Failure without Virtual Nodes:</strong> If Node A dies, all of Node A's load dumps onto Node B immediately clockwise. If Node B becomes overwhelmed and crashes, its load plus Node A's load dumps onto Node C, triggering total cluster collapse. <em>Mitigation:</em> Configure at least 150-250 Virtual Nodes per physical server.",
      "common_mistakes": [
        {
          "mistake": "Using `hash(key) % N` for distributed cache routing in dynamic autoscaling environments.",
          "correction": "Always use Consistent Hashing with Virtual Nodes for distributed caches and sharded databases."
        }
      ],
      "interview_questions": [
        {
          "question": "How many keys need to be relocated when a node is added to a Consistent Hashing cluster of N nodes?",
          "answer": "On average, only K/N keys are relocated (where K is total keys and N is total servers), compared to almost K keys (100%) in standard modulo hashing."
        }
      ]
    },
    {
      "id": "health-checks-failover-sticky-sessions",
      "title": "Active/Passive Health Checks, DNS Failover & Sticky Sessions",
      "definition": "Health checking mechanisms detect failing backend nodes and automatically pull them out of service rotation before users encounter 5xx errors. Sticky sessions (session affinity) ensure a client's requests consistently route to the same backend server instance.",
      "why_we_need_it": "Hardware failures, kernel panics, and out-of-memory crashes are inevitable in distributed systems. Automated health checking provides zero-downtime fault tolerance.",
      "real_world_analogy": "A hospital triage desk: If a doctor steps out or gets sick, the triage nurse stops sending patients to their examination room immediately and reassigns patients to active doctors.",
      "how_it_works": "<p><strong>Active Health Checks:</strong> The Load Balancer sends periodic synthetic HTTP requests (e.g. `GET /healthz` every 5 seconds). If a server fails 3 consecutive checks, it is marked 'DOWN'.<br><strong>Passive Health Checks:</strong> The LB monitors real user traffic. If a server returns 5 consecutive `502 Bad Gateway` responses to live users, it is temporarily ejected.<br><strong>Sticky Sessions:</strong> The LB injects an encrypted HTTP cookie (e.g. `AWSALB=xyz`) on the first response. Subsequent requests containing this cookie are routed to the same backend node.</p>",
      "conceptual_breakdown": [
        "<strong>Shallow vs Deep Health Checks:</strong> Shallow checks verify the web server is listening; Deep checks verify database connections, disk space, and downstream dependencies (use with care to prevent false cascade alarms).",
        "<strong>Sticky Session Anti-Pattern:</strong> Sticky sessions create unequal load distribution and cause data loss if a server crashes. Best practice is to store session state in a centralized Redis cluster."
      ],
      "failure_scenarios": "<strong>Deep Health Check Cascade Failure:</strong> If an underlying DB slows down, all backend servers fail their deep `/healthz` checks simultaneously, causing the Load Balancer to mark 100% of backend servers unhealthy and return global 503 errors. <em>Mitigation:</em> Keep `/healthz` checks shallow and use readiness/liveness probes properly.",
      "common_mistakes": [
        {
          "mistake": "Writing a `/healthz` endpoint that executes heavy DB queries on every 2-second LB probe across 100 instances.",
          "correction": "Make `/healthz` lightweight and cache dependency status asynchronously in memory."
        }
      ],
      "interview_questions": [
        {
          "question": "Why is stateless application architecture preferred over Load Balancer sticky sessions?",
          "answer": "Stateless servers allow any request to be handled by any instance, enabling seamless auto-scaling, instant traffic rebalancing, and zero-downtime rolling deployments without interrupting logged-in user sessions."
        }
      ]
    }
  ]
}

# -------------------------------------------------------------
# MODULE 08: Caching Strategies & Distributed Caches
# -------------------------------------------------------------
mod_08 = {
  "module_id": "08",
  "module_title": "Caching Strategies & Distributed Caches",
  "description": "Master Cache-Aside, Read-Through, Write-Through, Write-Back, Redis vs Memcached architecture, eviction algorithms (LRU/LFU), and advanced failure traps (Stampede, Avalanche, Penetration).",
  "topics": [
    {
      "id": "caching-fundamentals-and-locality",
      "title": "Caching Fundamentals: Hits, Misses, TTL & Eviction Policies (LRU/LFU)",
      "definition": "Caching is the practice of storing copies of data in high-speed volatile memory (RAM) to serve future requests with sub-millisecond latency and protect slow disk-based databases from excessive load.",
      "why_we_need_it": "Reading from RAM takes ~100 nanoseconds, while reading from NVMe SSD takes ~100 microseconds (1,000x slower) and network DB queries take ~5 to 20 milliseconds (100,000x slower). Caching provides massive throughput acceleration.",
      "real_world_analogy": "Keeping your favorite books on your desktop study table (RAM Cache) rather than walking to the national library (Disk/Database) every time you need to look up a sentence.",
      "how_it_works": "<p>When a request arrives, the application checks the cache. A <strong>Cache Hit</strong> returns data immediately. A <strong>Cache Miss</strong> reads from the primary database, populates the cache with a <strong>Time-To-Live (TTL)</strong>, and returns the result. When memory is full, an <strong>Eviction Policy</strong> frees space.</p>",
      "conceptual_breakdown": [
        "<strong>Cache Hit Ratio:</strong> `Hits / (Hits + Misses)`. Production target is typically >95%.",
        "<strong>LRU (Least Recently Used):</strong> Evicts items that haven't been accessed for the longest time (Doubly-Linked List + Hash Map, O(1)).",
        "<strong>LFU (Least Frequently Used):</strong> Evicts items with the lowest access frequency counter.",
        "<strong>FIFO & Random:</strong> Simpler eviction policies with lower memory overhead."
      ],
      "comparison_matrix": {
        "title": "Cache Eviction Algorithms Comparison",
        "columns": ["Algorithm", "Mechanism", "Time Complexity", "Memory Overhead", "Best Use Case"],
        "rows": [
          ["LRU (Least Recently Used)", "Evicts oldest accessed item", "O(1) Get & Put", "Moderate (Doubly-linked list pointers)", "General web applications & user sessions"],
          ["LFU (Least Frequently Used)", "Evicts lowest hit counter", "O(1) with frequency buckets", "High (Counters + frequency lists)", "Long-term static assets & video recommendation catalogs"],
          ["FIFO (First In First Out)", "Evicts oldest inserted item", "O(1) Queue", "Very Low (Simple queue)", "Time-series sequential logging"],
          ["TTL Eviction", "Evicts when expiration timestamp passes", "O(1) passive / O(N) active sampling", "Low (Timestamp per key)", "Transient auth tokens and rate-limiting counters"]
        ]
      },
      "failure_scenarios": "<strong>Cache Polluting Scans:</strong> A large batch job scans millions of obscure records once, evicting all hot items from the LRU cache and dropping the cache hit ratio to 0%. <em>Mitigation:</em> Use 2-Queue (2Q) or Adaptive Replacement Cache (ARC) policies.",
      "common_mistakes": [
        {
          "mistake": "Storing unbounded cache keys without configuring a TTL or MaxMemory Eviction Policy in Redis.",
          "correction": "Always set a reasonable TTL and configure Redis `maxmemory-policy allkeys-lru`."
        }
      ],
      "interview_questions": [
        {
          "question": "How do you implement an O(1) LRU Cache in code?",
          "answer": "Combine a `std::unordered_map<Key, Node*>` for O(1) key lookups with a `Doubly-Linked List` of key-value nodes. On read/write, move the accessed node to the head of the list. On eviction, remove the node from the tail."
        }
      ]
    },
    {
      "id": "caching-patterns-and-write-strategies",
      "title": "Caching Patterns: Cache-Aside, Read-Through, Write-Through, Write-Back & Write-Around",
      "definition": "Caching patterns dictate how applications synchronize data between the volatile cache and the persistent source-of-truth database during read and write operations.",
      "why_we_need_it": "Without clear write synchronization strategies, caches quickly return stale, corrupted, or inconsistent data, leading to incorrect account balances or broken user states.",
      "real_world_analogy": "Write-Through is paying cash at a store counter and receiving an instant paper receipt stamped in the cash register ledger. Write-Back is leaving your order on a restaurant tab; the waiter batches and settles the charges at the end of the night.",
      "how_it_works": "<p>1. <strong>Cache-Aside (Lazy Loading):</strong> Application code directly coordinates both cache and DB. On read: check cache, on miss read DB and write to cache. On write: write to DB, then invalidate (delete) cache key.<br>2. <strong>Read-Through / Write-Through:</strong> Application treats cache as main store; cache library automatically fetches from or writes synchronously to DB.<br>3. <strong>Write-Back (Write-Behind):</strong> Application writes to cache immediately; cache asynchronously batches writes to DB in background (extreme write throughput, risk of data loss on crash).<br>4. <strong>Write-Around:</strong> Writes go directly to DB bypassing cache entirely. Cache is only populated on subsequent read misses.</p>",
      "conceptual_breakdown": [
        "<strong>Cache Invalidation Rule:</strong> Always <em>DELETE</em> the cache key on DB write rather than updating it, avoiding race conditions with concurrent writes.",
        "<strong>Write-Back Superpower:</strong> Absorbs massive write spikes (e.g., IoT sensor telemetry, gaming leaderboards) by batching 10,000 writes into 1 bulk DB INSERT."
      ],
      "arch_diagram": {
        "title": "Caching Topologies & Synchronization Patterns",
        "tiers": [
          {
            "label": "App Layer",
            "nodes": [
              {
                "name": "Application Service",
                "type": "service",
                "icon": "⚡",
                "what": "Executes domain business operations",
                "why": "Controls caching decisions",
                "when": "Every incoming user read/write",
                "failure": "Graceful fallback to DB on cache outage"
              }
            ]
          },
          {
            "label": "Cache Layer",
            "nodes": [
              {
                "name": "Redis Distributed Cache",
                "type": "cache",
                "icon": "🔴",
                "what": "In-memory key-value store",
                "why": "Sub-millisecond read access",
                "when": "Hot data reads",
                "failure": "Redis Sentinel / Cluster master failover"
              }
            ]
          },
          {
            "label": "Persistent Storage",
            "nodes": [
              {
                "name": "PostgreSQL Primary DB",
                "type": "database",
                "icon": "🐘",
                "what": "Durable ACID relational database",
                "why": "Single source of truth",
                "when": "Cache misses and transactional mutations",
                "failure": "Synchronous standby replica promotion"
              }
            ]
          }
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> Cache-Aside provides high resilience (cache outage doesn't stop reads) with eventual consistency; Write-Through guarantees zero stale reads with higher write latency.",
      "failure_scenarios": "<strong>Write-Back Data Loss on Node Crash:</strong> If an in-memory cache node dies before dirty pages are flushed to the database, recent writes are permanently lost. <em>Mitigation:</em> Use Write-Back only for non-critical telemetry or ensure battery-backed RAM / append-only files (AOF).",
      "common_mistakes": [
        {
          "mistake": "Updating the cache value directly on write instead of invalidating (deleting) the key.",
          "correction": "Deleting the key prevents race conditions where an earlier slow write overwrites a newer fast write in the cache."
        }
      ],
      "interview_questions": [
        {
          "question": "Why should you invalidate (delete) a cache key rather than update it when updating a database record?",
          "answer": "If two concurrent requests A and B update the same record, Request A might write to DB first, then Request B writes to DB, but Request A updates the cache second due to network jitter, leaving the cache permanently holding stale data from A. Deleting the key forces the next read to fetch the latest state from the DB."
        }
      ]
    },
    {
      "id": "redis-vs-memcached-distributed-cache",
      "title": "Distributed Caching: Redis Architecture vs Memcached",
      "definition": "Redis and Memcached are the two industry-standard in-memory distributed caching engines. Redis provides rich data structures, persistence, pub/sub, and replication, while Memcached provides simple multi-threaded key-value caching.",
      "why_we_need_it": "A single application server's local in-memory cache is isolated; when multiple servers scale horizontally, a distributed cache provides a single unified cache tier shared across all nodes.",
      "real_world_analogy": "Memcached is a high-speed post office locker: simple, ultra-fast, multi-threaded storage. Redis is a Swiss Army Command Center: it holds lockers, sorts documents, keeps backup copies in a safe, and broadcasts alerts over loudspeakers.",
      "how_it_works": "<p><strong>Memcached:</strong> Pure multi-threaded key-value store. Scales vertically across multi-core CPUs easily. Data is strictly non-persistent strings/blobs.<br><strong>Redis:</strong> Single-threaded event loop (using `epoll`/`kqueue`) for atomic operations with multi-threaded I/O in Redis 6+. Supports Strings, Hashes, Lists, Sets, Sorted Sets (ZSETs), Bitmaps, HyperLogLogs, Geospatial indexes, Lua scripts, and persistence via RDB snapshots & AOF logs.</p>",
      "conceptual_breakdown": [
        "<strong>Redis Atomicity:</strong> Single-threaded core execution guarantees that commands like `INCR`, `HSET`, and Lua scripts execute atomically without lock contention.",
        "<strong>Redis Clustering:</strong> Shards keys across 16,384 hash slots using CRC16 hashing, supporting master-replica failover.",
        "<strong>Memcached Simplicity:</strong> Better for simple large blob caching where multi-core vertical scaling is desired."
      ],
      "comparison_matrix": {
        "title": "Redis vs Memcached Architectural Comparison",
        "columns": ["Feature", "Redis", "Memcached"],
        "rows": [
          ["Data Structures", "Strings, Hashes, Lists, Sets, Sorted Sets, Streams", "Simple Key-Value strings only"],
          ["Threading Model", "Single-threaded execution loop + Multi-threaded I/O", "Multi-threaded (Scales cleanly on multi-core)"],
          ["Persistence", "RDB Snapshots + Append-Only File (AOF)", "None (Pure volatile RAM)"],
          ["Replication & High Availability", "Built-in Redis Sentinel & Redis Cluster", "None (Relies on client-side consistent hashing)"],
          ["Pub/Sub & Streaming", "Native Pub/Sub & Redis Streams", "None"],
          ["Primary Use Case", "Complex caching, leaderboards, rate limiters, sessions", "High-throughput static key-value caching"]
        ]
      },
      "failure_scenarios": "<strong>Redis Long-Running Command Blockage:</strong> Running `KEYS *` or huge `HGETALL` commands on a million-item hash blocks the single-threaded event loop, stalling all client requests globally. <em>Mitigation:</em> Use `SCAN` and `HSCAN` instead of blocking wildcard commands.",
      "common_mistakes": [
        {
          "mistake": "Running `KEYS *` in a production Redis cluster.",
          "correction": "Disable `KEYS` command via `rename-command KEYS ''` in `redis.conf` and use cursor-based `SCAN`."
        }
      ],
      "interview_questions": [
        {
          "question": "How does Redis achieve high performance despite being primarily single-threaded?",
          "answer": "It operates entirely in volatile RAM (zero disk seek latency), utilizes non-blocking I/O multiplexing (`epoll`/`kqueue`) to handle tens of thousands of concurrent network sockets, and avoids CPU context switching and lock contention overheads."
        }
      ]
    },
    {
      "id": "cache-stampede-avalanche-penetration",
      "title": "Cache Traps: Stampede, Avalanche, Penetration, Hot Key Mitigation & Mutex Locks",
      "definition": "Cache failure traps are systemic breakdown modes where cache misses, expirations, or malicious queries bypass the cache tier and overwhelm backend databases, causing catastrophic cascading outages.",
      "why_we_need_it": "A system operating at 99% cache hit ratio under 100,000 QPS only sends 1,000 QPS to the database. If a cache failure occurs, the full 100,000 QPS hits the database instantly, destroying it within seconds.",
      "real_world_analogy": "A security gate at a stadium: Normally guards check tickets in 1 second. If the gate breaks (cache miss), thousands of fans rush the small entrance door simultaneously, crushing the ticket collectors.",
      "how_it_works": "<p>1. <strong>Cache Stampede (Thundering Herd):</strong> A high-traffic key expires; thousands of concurrent requests miss simultaneously and all query the DB to recompute the same key.<br>2. <strong>Cache Avalanche:</strong> Many keys are set with identical TTLs (e.g. 3600s); they all expire at the exact same second, dumping massive traffic on the DB.<br>3. <strong>Cache Penetration:</strong> Malicious requests query non-existent IDs (e.g. `GET /user/-999`); cache misses every time and hits the DB.<br>4. <strong>Hot Key Saturation:</strong> A celebrity account (e.g., Justin Bieber) gets 500k QPS directed to a single Redis node, saturating its network NIC.</p>",
      "conceptual_breakdown": [
        "<strong>Stampede Mitigation:</strong> Distributed Mutex Lock (only 1 thread queries DB; others wait/retry) or Probabilistic Early Expiration (XFetch algorithm).",
        "<strong>Avalanche Mitigation:</strong> Add random jitter to TTLs: `TTL = 3600 + rand(0, 300)` seconds.",
        "<strong>Penetration Mitigation:</strong> Bloom Filters (reject invalid keys before hitting DB) or Cache Null Objects with short TTL (e.g. 30s).",
        "<strong>Hot Key Mitigation:</strong> Local in-memory caching (Caffeine/L1) on application servers or Key Replicas with random suffixes (`key_1`, `key_2`)."
      ],
      "system_flow_animation": {
        "title": "Cache Stampede Distributed Mutex Protection Flow",
        "steps": [
          {
            "num": 1,
            "title": "Cache Miss for Hot Key",
            "actor": "1,000 Concurrent Requests -> Cache",
            "desc": "Key 'trending_news' expires. 1,000 concurrent threads detect a cache miss.",
            "node": "Redis Distributed Cache"
          },
          {
            "num": 2,
            "title": "Distributed Lock Acquisition",
            "actor": "Request #1 -> Redis SETNX",
            "desc": "Thread #1 successfully acquires lock 'lock:trending_news' via SETNX with 5s lease.",
            "node": "Application Service"
          },
          {
            "num": 3,
            "title": "Remaining Requests Wait",
            "actor": "Requests #2-1000 -> Sleep & Retry",
            "desc": "Remaining 999 threads fail to acquire lock, sleep 50ms, and retry reading cache.",
            "node": "Application Service"
          },
          {
            "num": 4,
            "title": "Database Query & Cache Refresh",
            "actor": "Request #1 -> DB -> Cache",
            "desc": "Thread #1 queries DB, updates Redis with new TTL, releases lock. Remaining 999 threads now hit warm cache!",
            "node": "PostgreSQL Primary DB"
          }
        ]
      },
      "failure_scenarios": "<strong>Bloom Filter False Positives vs False Negatives:</strong> A Bloom Filter can return a False Positive (says key exists when it doesn't), which safely falls back to DB, but it NEVER returns a False Negative (if it says key does not exist, it definitely does not exist).",
      "common_mistakes": [
        {
          "mistake": "Setting fixed round TTLs (e.g. exactly 1 hour) across all cached database records.",
          "correction": "Always introduce random TTL jitter (`TTL + random(-10%, +10%)`) to prevent simultaneous Cache Avalanche."
        }
      ],
      "interview_questions": [
        {
          "question": "How does a Bloom Filter prevent Cache Penetration in high-scale systems?",
          "answer": "A Bloom Filter is a memory-efficient probabilistic data structure that hashes incoming keys across bit arrays. If the Bloom Filter indicates a key does not exist, the application immediately returns 404 without querying either the cache or the database."
        }
      ]
    }
  ]
}

# -------------------------------------------------------------
# MODULE 09: Database Foundations & Relational DBs
# -------------------------------------------------------------
mod_09 = {
  "module_id": "09",
  "module_title": "Database Foundations & Relational DBs",
  "description": "Master Relational vs NoSQL paradigms, ACID transactions, normalization vs denormalization trade-offs, connection pooling, and concurrency locking strategies.",
  "topics": [
    {
      "id": "relational-vs-nosql-paradigm",
      "title": "Relational (RDBMS) vs NoSQL: Data Modeling & Query Paradigms",
      "definition": "Relational databases (RDBMS) store structured data in tables with predefined schemas, foreign keys, and ACID guarantees using SQL. NoSQL databases prioritize horizontal scalability, schema flexibility, and partition tolerance using diverse models (Document, Key-Value, Wide-Column, Graph).",
      "why_we_need_it": "Choosing the wrong storage engine early in system design leads to severe scaling bottlenecks, excessive operational maintenance, or catastrophic data corruption.",
      "real_world_analogy": "An RDBMS is a standardized corporate filing cabinet with strict alphabetical folders and mandatory forms. NoSQL is a versatile shipping container yard: you can load palletized boxes (Documents), giant bulk grain (Key-Value), or connected shipping routes (Graph).",
      "how_it_works": "<p><strong>RDBMS (PostgreSQL, MySQL):</strong> Organizes entities into normalized tables, enforcing integrity constraints via foreign keys and performing relational JOINs at query time.<br><strong>NoSQL (MongoDB, Cassandra, DynamoDB):</strong> Denormalizes data into self-contained records or partitioned key spaces, eliminating multi-table JOINs to enable linear horizontal partitioning across hundreds of server nodes.</p>",
      "conceptual_breakdown": [
        "<strong>When to choose RDBMS:</strong> Complex relational queries, strict ACID transaction requirements (financial ledgers, order checkouts), structured schemas.",
        "<strong>When to choose NoSQL:</strong> Massive write throughput (>100k QPS), unstructured/evolving schemas, global multi-region replication, horizontal scaling beyond single-node storage limits."
      ],
      "comparison_matrix": {
        "title": "RDBMS vs NoSQL Core Comparison Matrix",
        "columns": ["Dimension", "Relational Databases (RDBMS)", "NoSQL Databases"],
        "rows": [
          ["Data Model", "Tables, Rows, Columns with fixed schema", "Key-Value, Document (JSON/BSON), Wide-Column, Graph"],
          ["Transactions", "Strict ACID guarantees", "BASE (Basically Available, Soft state, Eventual consistency)"],
          ["Scalability", "Vertical (Scale-up) primary + Read replicas", "Horizontal (Scale-out) sharding across commodity nodes"],
          ["Query Mechanism", "Structured SQL with complex JOINs", "Primary Key / Partition Key lookups or specialized APIs"],
          ["Examples", "PostgreSQL, MySQL, Oracle, SQLite", "Redis, MongoDB, Apache Cassandra, Neo4j, DynamoDB"]
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> RDBMS offers strong relational integrity and complex query flexibility at the cost of horizontal write scaling limits; NoSQL offers near-infinite horizontal write scaling at the cost of eventual consistency and lack of multi-table JOINs.",
      "failure_scenarios": "<strong>Scaling Out RDBMS Joins:</strong> Running a 6-table JOIN on an RDBMS table with 500 million rows locks tables, burns 100% CPU, and causes query timeouts. <em>Mitigation:</em> Denormalize query views or pre-aggregate data in read models.",
      "common_mistakes": [
        {
          "mistake": "Assuming NoSQL is always faster than RDBMS for all workloads.",
          "correction": "A properly indexed PostgreSQL query on a single machine easily outperforms a poorly keyed distributed NoSQL query."
        }
      ],
      "interview_questions": [
        {
          "question": "When would you deliberately choose a relational database over NoSQL in an interview?",
          "answer": "When the system requires strict ACID transactions across multiple entities (e.g. banking transfers, order checkouts), when data has rich relational foreign-key connections requiring ad-hoc JOIN queries, or when data volume comfortably fits within a single primary database instance with read replicas."
        }
      ]
    },
    {
      "id": "acid-transactions-explained",
      "title": "ACID Properties: Atomicity, Consistency, Isolation & Durability",
      "definition": "ACID is a set of four non-negotiable guarantees provided by database transaction management systems to ensure data reliability and validity despite software crashes, network partitions, or concurrent updates.",
      "why_we_need_it": "In a financial money transfer of $100 from Account A to Account B, if the server crashes after deducting from A but before adding to B, money vanishes into thin air without ACID Atomicity guarantees.",
      "real_world_analogy": "Sending an express delivery package: The delivery is an all-or-nothing event (Atomicity). The recipient must sign for it (Consistency). Other packages on the truck don't mix their contents (Isolation). Once delivered and signed, the package cannot vanish even if the truck breaks down later (Durability).",
      "how_it_works": "<p>1. <strong>Atomicity:</strong> All operations in a transaction succeed or all are rolled back (All-or-Nothing). Implemented via Write-Ahead Logging (WAL) and undo logs.<br>2. <strong>Consistency:</strong> The transaction transitions database from one valid state to another, enforcing all constraints, triggers, and foreign keys.<br>3. <strong>Isolation:</strong> Concurrent transactions execute without interfering with one another. Implemented via Multi-Version Concurrency Control (MVCC) or 2-Phase Locking (2PL).<br>4. <strong>Durability:</strong> Once committed, updates survive power outages and server crashes. Implemented by flushing WAL to non-volatile disk (`fsync`).</p>",
      "conceptual_breakdown": [
        "<strong>WAL (Write-Ahead Logging):</strong> The database writes changes sequentially to an append-only transaction log on disk BEFORE modifying in-memory data pages.",
        "<strong>fsync Trade-off:</strong> Executing `fsync` on every single commit guarantees durability but limits single-thread disk write throughput to ~1,000-5,000 QPS."
      ],
      "failure_scenarios": "<strong>Dirty Reads & Lost Updates:</strong> Without proper transaction isolation, Transaction A reads uncommitted data from Transaction B, which later rolls back, leading to catastrophic decision errors based on phantom data.",
      "common_mistakes": [
        {
          "mistake": "Keeping long-running external HTTP API calls inside an open database transaction block.",
          "correction": "Never make network I/O calls inside a DB transaction; it holds database locks open, exhausting connection pools."
        }
      ],
      "interview_questions": [
        {
          "question": "How does Write-Ahead Logging (WAL) guarantee both Atomicity and Durability?",
          "answer": "WAL records all intent modifications to an append-only log on disk before modifying database pages in RAM. On crash recovery, the database scans the WAL: committed transactions with unwritten pages are REDO-ed (Durability), while uncommitted in-flight transactions are UNDO-ed (Atomicity)."
        }
      ]
    },
    {
      "id": "normalization-vs-denormalization",
      "title": "Database Normalization (1NF to 3NF) vs Intentional Denormalization",
      "definition": "Normalization is the systematic process of organizing database tables to eliminate data redundancy and anomalies (1NF, 2NF, 3NF, BCNF). Denormalization is the intentional re-introduction of redundancy to optimize read performance and eliminate expensive JOINs.",
      "why_we_need_it": "Over-normalized databases require 8-table JOINs for simple web pages, causing severe query latency. Completely unnormalized databases suffer from update anomalies where editing a user's name leaves hundreds of rows with conflicting stale names.",
      "real_world_analogy": "Normalization is keeping one master employee record and referencing Employee ID in 20 departments. Denormalization is printing the employee's name directly on every department door badge to avoid calling HR every time someone walks into a room.",
      "how_it_works": "<p>1. <strong>1NF:</strong> Atomic values (no repeating groups/arrays in a single cell).<br>2. <strong>2NF:</strong> In 1NF and no partial dependencies on composite primary keys.<br>3. <strong>3NF:</strong> In 2NF and no transitive dependencies (non-key columns depend ONLY on primary key).<br>4. <strong>Denormalization:</strong> Storing `user_name` directly in `orders` table to display order histories in a single-table lookup without joining the `users` table.</p>",
      "conceptual_breakdown": [
        "<strong>Write-Heavy vs Read-Heavy:</strong> Normalization optimizes for write speed and storage integrity; Denormalization optimizes for read speed and throughput.",
        "<strong>Sync Burden:</strong> When denormalized data is updated (e.g., user changes username), all duplicate copies must be updated asynchronously (via CDC or events)."
      ],
      "tradeoffs": "<strong>Trade-off:</strong> Denormalization achieves lightning-fast reads with zero JOINs in exchange for larger disk footprints and the complexity of keeping duplicate columns synchronized across tables.",
      "failure_scenarios": "<strong>Update Anomaly in Denormalized Tables:</strong> A user changes their email address, but an async job fails halfway, leaving 50 historical order records with the old email and 50 with the new email. <em>Mitigation:</em> Use Transactional Outbox pattern or Event Sourcing to guarantee eventual consistency.",
      "common_mistakes": [
        {
          "mistake": "Prematurely denormalizing database tables before identifying real read latency bottlenecks.",
          "correction": "Start with 3NF normalization. Introduce selective denormalization only after profiling queries and verifying index optimizations are insufficient."
        }
      ],
      "interview_questions": [
        {
          "question": "How do you maintain data consistency across denormalized tables in a microservices architecture?",
          "answer": "Use Change Data Capture (CDC via Debezium/Kafka) or Domain Event Streams. When the primary entity updates, an event is emitted, and background consumer workers asynchronously update all denormalized projections."
        }
      ]
    },
    {
      "id": "connection-pooling-and-locks",
      "title": "Connection Pooling, Optimistic vs Pessimistic Locking & Deadlocks",
      "definition": "Connection pooling reuses persistent database connections to eliminate the overhead of TCP and TLS handshakes. Concurrency locking controls access to shared database rows: Pessimistic Locking prevents concurrent modifications via explicit locks (`SELECT FOR UPDATE`), while Optimistic Locking validates record versions at commit time (`version = version + 1`).",
      "why_we_need_it": "Opening a new PostgreSQL connection consumes ~10MB of server memory and requires a 3-way handshake + TLS negotiation. Creating 5,000 connections simultaneously exhausts server RAM and crashes the database.",
      "real_world_analogy": "Connection Pooling is a taxi fleet: instead of buying a new car for every passenger and scrapping it after the trip, passengers share a pool of 50 active taxis. Pessimistic Locking is holding the taxi door shut while you shop; Optimistic Locking is letting anyone try to hail a cab, but only the first person to tap their card gets the ride.",
      "how_it_works": "<p><strong>Connection Poolers (e.g., PgBouncer, HikariCP):</strong> Maintain a warm pool of 50-200 open backend connections, multiplexing thousands of incoming application client requests over them.<br><strong>Pessimistic Locking:</strong> Executes `SELECT * FROM inventory WHERE item_id = 1 FOR UPDATE`. Other transactions trying to read/modify item 1 are blocked until commit/rollback.<br><strong>Optimistic Locking:</strong> Executes `UPDATE inventory SET stock = stock - 1, version = version + 1 WHERE item_id = 1 AND version = 3`. If row count affected is 0, another transaction updated it first; application retries.</p>",
      "conceptual_breakdown": [
        "<strong>When to use Optimistic Locking:</strong> Low-to-moderate contention workloads (e.g. editing user profiles). High throughput, zero blocking.",
        "<strong>When to use Pessimistic Locking:</strong> High-contention financial or ticket booking scenarios (e.g. reserving the last concert ticket) where rollback retries would be expensive.",
        "<strong>Deadlocks:</strong> Occur when Transaction 1 holds Lock A and requests Lock B, while Transaction 2 holds Lock B and requests Lock A. DB engine detects cycles and aborts one transaction."
      ],
      "failure_scenarios": "<strong>Connection Pool Exhaustion:</strong> Application threads take connections from the pool but leak them due to unhandled exceptions, stalling all incoming requests. <em>Mitigation:</em> Strict connection acquisition timeouts (`connectionTimeout = 250ms`, `maxLifetime = 30min`).",
      "common_mistakes": [
        {
          "mistake": "Acquiring locks in arbitrary order across multiple transactions, triggering database deadlocks.",
          "correction": "Always enforce a globally consistent lock acquisition order (e.g. sort resource IDs in ascending order: Lock ID 10 then Lock ID 20)."
        }
      ],
      "interview_questions": [
        {
          "question": "Why does setting a database connection pool size too high (e.g. 5,000) degrade performance rather than improve it?",
          "answer": "Operating systems on multi-core CPUs spend more time performing CPU context switching and disk I/O queue contention than executing actual queries. The optimal pool size formula is `connections = (2 * CPU cores) + disk spindle count` (often ~20-50 connections for peak throughput)."
        }
      ]
    }
  ]
}

# -------------------------------------------------------------
# MODULE 10: Deep Dive SQL: PostgreSQL, MySQL & Indexing
# -------------------------------------------------------------
mod_10 = {
  "module_id": "10",
  "module_title": "Deep Dive SQL: PostgreSQL, MySQL & Indexing",
  "description": "Master B-Tree index internals, clustered vs secondary indexes, composite indexes & leftmost prefix rules, SQL transaction isolation levels, and EXPLAIN query plan optimization.",
  "topics": [
    {
      "id": "btree-and-indexing-internals",
      "title": "B-Tree & LSM Index Internals: Clustered vs Secondary Indexes",
      "definition": "Database indexes are auxiliary search data structures that allow the query engine to locate matching rows in logarithmic time O(log N) instead of performing a full table scan O(N). B-Trees (B+ Trees) optimize for read-heavy disk I/O, while Log-Structured Merge Trees (LSM Trees) optimize for write-heavy throughput.",
      "why_we_need_it": "A full table scan on a 50-million-row table requires reading gigabytes of raw pages from disk (taking 15-30 seconds). A B-Tree index lookup reaches the exact row in 3 to 4 page hops (taking <1 millisecond).",
      "real_world_analogy": "An index at the back of a 1,000-page encyclopedia: instead of reading every page from page 1 to 1,000, you look up 'Distributed Systems', find 'page 742', and flip directly there.",
      "how_it_works": "<p><strong>B+ Tree:</strong> Self-balancing N-ary tree where internal nodes store search keys and leaf nodes store pointers to actual data. Leaf nodes are linked as a doubly-linked list for ultra-fast range scans (`WHERE age BETWEEN 20 AND 30`).<br><strong>Clustered Index (Primary Key):</strong> Table rows are physically sorted and stored on disk in the order of the primary key (e.g. MySQL InnoDB).<br><strong>Secondary Index:</strong> Separate B-Tree whose leaf nodes point to the Clustered Primary Key (MySQL) or physical tuple ID/TID (PostgreSQL Heap).</p>",
      "conceptual_breakdown": [
        "<strong>Index Write Penalty:</strong> Every `INSERT`, `UPDATE`, or `DELETE` requires updating every associated index on that table, increasing write latency and disk I/O.",
        "<strong>LSM Trees (Cassandra/RocksDB):</strong> Writes append to in-memory MemTable and commit log; flushed sequentially to immutable disk SSTables, providing blazing write throughput."
      ],
      "comparison_matrix": {
        "title": "B+ Tree vs LSM Tree Indexing Comparison",
        "columns": ["Feature", "B+ Tree (PostgreSQL, MySQL)", "LSM Tree (Cassandra, RocksDB, ScyllaDB)"],
        "rows": [
          ["Read Performance", "Blazing fast point & range queries (O(log N))", "Moderate (Requires checking MemTable + Bloom Filters + SSTables)"],
          ["Write Performance", "Moderate (Random I/O page updates & rebalancing)", "Extremely high (Sequential append-only writes)"],
          ["Space Amplification", "Moderate (Page fragmentation & fill factor)", "Low to Moderate (Periodic compaction needed)"],
          ["Primary Workload", "Read-heavy relational OLTP workloads", "Write-heavy telemetry, logging, messaging feeds"]
        ]
      },
      "failure_scenarios": "<strong>Index Bloat & Fragmentation:</strong> Frequent random updates in PostgreSQL create dead tuples, causing B-Tree indexes to balloon in size and degrade cache hit rates. <em>Mitigation:</em> Configure automated aggressive `VACUUM` and run `REINDEX CONCURRENTLY`.",
      "common_mistakes": [
        {
          "mistake": "Adding an index on every single column in a table with high write volume.",
          "correction": "Only index columns used in `WHERE`, `JOIN`, and `ORDER BY` clauses; monitor unused indexes via `pg_stat_user_indexes` and drop them."
        }
      ],
      "interview_questions": [
        {
          "question": "Why are B+ Trees preferred over Binary Search Trees (BST) or Red-Black Trees for database disk storage?",
          "answer": "B+ Trees have massive branching factors (fan-out of 100 to 1,000 keys per node), keeping tree height very low (3 to 4 levels for millions of rows), which minimizes expensive disk page reads. In addition, linked leaf nodes allow efficient sequential disk range scans."
        }
      ]
    },
    {
      "id": "composite-and-covering-indexes",
      "title": "Composite Indexes, Leftmost Prefix Rule & Covering Indexes",
      "definition": "A Composite Index is an index on multiple columns `(colA, colB, colC)`. The Leftmost Prefix Rule dictates that queries can only use the index if they filter by the leftmost prefix of indexed columns. A Covering Index includes all columns required by a query, allowing the engine to return results directly from the index without reading table heap pages (Index-Only Scan).",
      "why_we_need_it": "Multi-column queries (e.g., `WHERE tenant_id = 5 AND status = 'ACTIVE' ORDER BY created_at DESC`) cannot efficiently utilize two separate single-column indexes. A well-designed composite index executes in sub-millisecond time.",
      "real_world_analogy": "A physical telephone directory sorted by `(Last_Name, First_Name)`. You can effortlessly find all people with Last Name 'Smith', or 'Smith, John'. But you cannot use the phone book to find all people whose First Name is 'John' without reading the entire book from start to finish.",
      "how_it_works": "<p>1. <strong>Leftmost Prefix Rule:</strong> An index on `(A, B, C)` accelerates queries on `(A)`, `(A, B)`, and `(A, B, C)`. It CANNOT accelerate queries on `(B)` or `(B, C)` alone.<br>2. <strong>Index-Only Scan (Covering Index):</strong> If query `SELECT id, status FROM orders WHERE user_id = 123` is backed by index `(user_id, status, id)`, the database reads data entirely from the index B-Tree in memory, skipping the table data heap entirely (Zero Table I/O).</p>",
      "conceptual_breakdown": [
        "<strong>Column Ordering Rule:</strong> Place high-cardinality equality columns first, followed by range/inequality filter columns (`<`, `>`), followed by `ORDER BY` columns.",
        "<strong>`INCLUDE` Clause (PostgreSQL):</strong> Allows adding payload columns to the leaf pages of an index without making them part of the search key tree (e.g. `CREATE INDEX ON orders (user_id) INCLUDE (status, total_price)`)."
      ],
      "failure_scenarios": "<strong>Breaking Leftmost Prefix with Wildcard Starts:</strong> Querying `WHERE last_name LIKE '%son'` bypasses the B-Tree index and triggers a full table scan because the leading character is unknown. <em>Mitigation:</em> Use Trigram (`pg_trgm`) or GIN indexes for leading wildcard text searches.",
      "common_mistakes": [
        {
          "mistake": "Creating 3 separate indexes on (A), (B), and (C) instead of a single composite index on (A, B, C) for multi-column queries.",
          "correction": "Use a single composite index matching query filtering and sorting orders."
        }
      ],
      "interview_questions": [
        {
          "question": "Given an index on `(status, created_at)`, will query `SELECT * FROM orders WHERE created_at > '2026-01-01'` use the index efficiently?",
          "answer": "No. Because `status` (the leftmost column) is not included in the WHERE clause, the database cannot use the B-Tree hierarchy for prefix search and will perform a full table scan (or inefficient full index scan)."
        }
      ]
    },
    {
      "id": "transaction-isolation-levels",
      "title": "SQL Isolation Levels: Dirty Read, Non-Repeatable Read & Phantom Read",
      "definition": "SQL Transaction Isolation Levels define the degree to which concurrent transactions are isolated from one another's intermediate data modifications, balancing consistency guarantees against concurrency throughput.",
      "why_we_need_it": "Without proper isolation, concurrent transactions experience race condition anomalies (Dirty Reads, Non-Repeatable Reads, Phantom Reads, Serialization Anomalies) that corrupt business balances.",
      "real_world_analogy": "Editing a shared Google Doc: Read Uncommitted is seeing letters appear character-by-character as a colleague types a draft. Serializable is locking the document so only one person can view or edit at a time while everyone else waits in a queue.",
      "how_it_works": "<p>Standard SQL defines 4 isolation levels:<br>1. <strong>Read Uncommitted:</strong> Allows Dirty Reads (reading uncommitted changes from another transaction).<br>2. <strong>Read Committed (Postgres default):</strong> Prevents Dirty Reads. Queries only see data committed before the query began.<br>3. <strong>Repeatable Read (MySQL default):</strong> Prevents Dirty Reads & Non-Repeatable Reads. Reading the same row twice inside a transaction returns identical data via MVCC snapshots.<br>4. <strong>Serializable:</strong> Highest level. Prevents all anomalies including Phantom Reads and Write Skew as if transactions ran one after another sequentially.</p>",
      "conceptual_breakdown": [
        "<strong>Anomalies Defined:</strong><br>&bull; <em>Dirty Read:</em> T1 reads uncommitted data written by T2; T2 rolls back.<br>&bull; <em>Non-Repeatable Read:</em> T1 reads a row; T2 updates that row and commits; T1 reads row again and sees changed values.<br>&bull; <em>Phantom Read:</em> T1 reads rows matching a condition; T2 inserts a new row matching that condition; T1 queries again and sees a new 'phantom' row.<br>&bull; <em>Write Skew:</em> Two transactions read overlapping data, satisfy constraints independently, and make conflicting updates.",
        "<strong>MVCC (Multi-Version Concurrency Control):</strong> PostgreSQL and MySQL maintain multiple row versions (`xmin`/`xmax`), allowing readers to never block writers and writers to never block readers."
      ],
      "comparison_matrix": {
        "title": "SQL Isolation Levels & Concurrency Anomalies",
        "columns": ["Isolation Level", "Dirty Read", "Non-Repeatable Read", "Phantom Read", "Write Skew", "Performance Overhead"],
        "rows": [
          ["Read Uncommitted", "❌ Allowed", "❌ Allowed", "❌ Allowed", "❌ Allowed", "Lowest"],
          ["Read Committed", "✅ Prevented", "❌ Allowed", "❌ Allowed", "❌ Allowed", "Low (Default in Postgres)"],
          ["Repeatable Read", "✅ Prevented", "✅ Prevented", "✅ Prevented (in Postgres/MySQL MVCC)", "❌ Allowed", "Moderate (Default in MySQL)"],
          ["Serializable", "✅ Prevented", "✅ Prevented", "✅ Prevented", "✅ Prevented", "Highest (Abort/Retry overhead)"]
        ]
      },
      "failure_scenarios": "<strong>Serialization Failure Aborts:</strong> Under high concurrency, Serializable isolation triggers serialization errors (`could not serialize access due to concurrent update - 40001`). Applications MUST implement automatic retry loops with exponential backoff.",
      "common_mistakes": [
        {
          "mistake": "Setting global database isolation level to Serializable for high-throughput low-latency web apps.",
          "correction": "Use Read Committed or Repeatable Read as the default, applying explicit row locks (`SELECT FOR UPDATE`) or optimistic concurrency control only where critical."
        }
      ],
      "interview_questions": [
        {
          "question": "How does Multi-Version Concurrency Control (MVCC) eliminate read-write lock contention in PostgreSQL?",
          "answer": "MVCC creates a new tuple version with transaction IDs (`xmin`, `xmax`) whenever a row is modified, rather than overwriting existing data. Readers query an immutable snapshot of committed tuples matching their transaction start timestamp, so reads never block writes and writes never block reads."
        }
      ]
    },
    {
      "id": "query-optimization-and-explain",
      "title": "Query Planning, EXPLAIN ANALYZE & Slow Query Optimization",
      "definition": "Query optimization is the process of inspecting the database Cost-Based Optimizer (CBO) execution plan using `EXPLAIN (ANALYZE, BUFFERS)` to diagnose slow table scans, ineffective indexes, expensive nested loop joins, and disk spills.",
      "why_we_need_it": "A query that runs in 5ms during local testing can degrade to 45 seconds in production when table size scales from 1,000 rows to 100 million rows.",
      "real_world_analogy": "A GPS navigation route planner: `EXPLAIN` shows the calculated fastest route (highways vs city streets). `EXPLAIN ANALYZE` actually drives the car, measuring exact traffic delays and road tolls at every intersection.",
      "how_it_works": "<p>1. <strong>`EXPLAIN`:</strong> Displays the optimizer's estimated plan (Seq Scan, Index Scan, Bitmap Heap Scan, Nested Loop, Hash Join, Merge Join) and estimated cost units.<br>2. <strong>`EXPLAIN ANALYZE`:</strong> Executes the query in real-time, displaying actual execution time (ms), rows returned, and memory buffer hits vs disk reads.<br>3. <strong>Key Warning Signs:</strong> Sequential Scans on large tables, huge discrepancies between estimated vs actual rows (stale stats), and 'Sort Method: external disk' (insufficient `work_mem`).</p>",
      "conceptual_breakdown": [
        "<strong>Seq Scan:</strong> Reads every page from disk. Red flag on tables with >10,000 rows.",
        "<strong>Index Scan:</strong> Traverses B-Tree and fetches matching tuple pages from heap.",
        "<strong>Bitmap Index Scan:</strong> Builds an in-memory bitmap of matching physical page addresses, sorting them to perform sequential disk I/O.",
        "<strong>Join Types:</strong> Nested Loop (best for small inputs), Hash Join (best for large unsorted equality joins), Merge Join (best for pre-sorted inputs)."
      ],
      "failure_scenarios": "<strong>Outdated Table Statistics:</strong> If a table grows rapidly without `ANALYZE`, the query planner assumes it still has 100 rows and selects an inefficient Nested Loop join instead of a Hash Join, causing 100x latency degradation. <em>Mitigation:</em> Tune autovacuum analyze thresholds.",
      "common_mistakes": [
        {
          "mistake": "Applying functions to indexed columns in WHERE clauses (e.g. `WHERE UPPER(email) = 'TEST@EXAMPLE.COM'`).",
          "correction": "This disables standard B-Tree indexes. Use expression/functional indexes (`CREATE INDEX ON users (UPPER(email))`) or normalize input before querying."
        }
      ],
      "interview_questions": [
        {
          "question": "What is the difference between an Index Scan and a Bitmap Index Scan in PostgreSQL?",
          "answer": "An Index Scan traverses the B-Tree and immediately fetches matching rows from the heap one by one (ideal when returning very few rows). A Bitmap Index Scan first scans the index to construct a bitmap of matching heap pages in RAM, sorts page numbers physically, and reads them sequentially, drastically reducing random disk I/O when fetching multiple rows."
        }
      ]
    }
  ]
}

# Write modules
modules = [mod_06, mod_07, mod_08, mod_09, mod_10]
for m in modules:
    filename = os.path.join(CONTENT_DIR, f"module_{m['module_id']}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print(f"Generated {filename} with {len(m['topics'])} topics")

