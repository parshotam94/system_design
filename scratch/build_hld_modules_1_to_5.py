import json
import os

hld_dir = os.path.join("content", "hld")
os.makedirs(hld_dir, exist_ok=True)

# =========================================================================
# MODULE 1: System Design Foundations
# =========================================================================
m1 = {
    "module_id": "01",
    "module_title": "System Design Foundations",
    "description": "Start from absolute zero: Clients, Servers, APIs, Databases, Infrastructure, and the progressive evolution from single-server to distributed architecture.",
    "topics": [
        {
            "id": "what-is-system-design",
            "title": "What is System Design & Software Architecture?",
            "definition": "System Design is the discipline of defining the architecture, components, modules, interfaces, and data strategies for a system to satisfy specified business and technical requirements at scale.",
            "why_we_need_it": "A system built for 10 users will completely collapse under 1,000,000 users. System design provides the engineering principles, failure models, and scaling patterns to build software that remains fast, available, reliable, secure, and cost-effective under massive load.",
            "real_world_analogy": "Designing a building: you start with civil blueprints (HLD: foundation, load-bearing pillars, electrical grids, plumbing systems) before deciding on brick patterns and interior door hinges (LLD: classes, design patterns, loops).",
            "how_it_works": "<p>System design transforms ambiguous business ideas into high-level architecture diagrams, concrete service boundaries, API contracts, data schemas, caching topologies, and network pipelines.</p><p>Instead of thinking in lines of code, an architect evaluates <strong>system boundaries</strong>, <strong>network throughput</strong>, <strong>storage limits</strong>, <strong>single points of failure (SPOFs)</strong>, and <strong>trade-offs</strong> between latency, consistency, and cost.</p>",
            "conceptual_breakdown": [
                "<strong>System Design vs Coding:</strong> Coding is <em>how</em> a single function executes; System Design is <em>how hundreds of servers cooperate</em> across a network.",
                "<strong>Software Architecture:</strong> The fundamental organization of a system embodied in its components, their relationships to each other and to the environment, and the principles guiding its design and evolution (IEEE 1471).",
                "<strong>Non-Negotiable Triad:</strong> Scalability (handling growth), Reliability (working despite hardware crashes), and Maintainability (enabling engineering teams to evolve the codebase without breaking production)."
            ],
            "arch_diagram": {
                "title": "The End-to-End System Design Landscape",
                "tiers": [
                    {
                        "label": "Clients",
                        "nodes": [
                            {"name": "Web App", "type": "client", "icon": "💻", "what": "Browser client (React/HTML)", "why": "Renders UI for desktop users", "when": "Direct user interaction", "failure": "Client-side retry on network disconnect"}
                        ]
                    },
                    {
                        "label": "Gateway Tier",
                        "nodes": [
                            {"name": "DNS / CDN", "type": "client", "icon": "🌐", "what": "Route 53 + Cloudflare", "why": "Global edge caching & IP routing", "when": "Static assets & low-latency DNS", "failure": "Anycast failover to alternate edge PoP"},
                            {"name": "Load Balancer", "type": "lb", "icon": "⚖️", "what": "NGINX / AWS ALB", "why": "Distributes HTTP traffic across servers", "when": "Multiple backend instances", "failure": "Active-passive backup LB with VRRP / Keepalived"}
                        ]
                    },
                    {
                        "label": "Application Tier",
                        "nodes": [
                            {"name": "API Service A", "type": "service", "icon": "⚙️", "what": "Stateless backend instance", "why": "Executes core business logic", "when": "Handles user requests", "failure": "Health check drops dead node; auto-scaler spawns replacement"},
                            {"name": "API Service B", "type": "service", "icon": "⚙️", "what": "Stateless backend instance", "why": "Executes core business logic", "when": "Handles user requests", "failure": "Traffic redirected to healthy siblings"}
                        ]
                    },
                    {
                        "label": "Data & Caching Tier",
                        "nodes": [
                            {"name": "Redis Cache", "type": "cache", "icon": "⚡", "what": "In-memory key-value cache", "why": "Sub-millisecond read access", "when": "Hot frequently-read data", "failure": "Cache miss queries primary DB; Redis Sentinel auto-failover"},
                            {"name": "Primary SQL DB", "type": "db", "icon": "🗄️", "what": "PostgreSQL / MySQL Primary", "why": "ACID transactional truth", "when": "Write mutations & relational storage", "failure": "Promote read replica to new primary"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "Classic Request-Response Traversal",
                "steps": [
                    {"step": 1, "description": "User clicks 'View Product'. Mobile App resolves IP via DNS and sends HTTPS GET /product/101.", "active_nodes": ["Web App", "DNS / CDN"]},
                    {"step": 2, "description": "Load Balancer terminates TLS, inspects health checks, and routes request to API Service A.", "active_nodes": ["Load Balancer", "API Service A"]},
                    {"step": 3, "description": "API Service checks Redis Cache. Cache HIT! Returns product JSON in 1.2ms without touching SQL DB.", "active_nodes": ["API Service A", "Redis Cache"]},
                    {"step": 4, "description": "Load Balancer forwards response back to User. Screen renders instantly.", "active_nodes": ["Load Balancer", "Web App"]}
                ]
            },
            "tradeoffs": "Designing for 100M users on Day 1 is an expensive anti-pattern (Premature Optimization). The master skill of a software architect is building modular architectures that are simple today but possess clean evolutionary seams to scale 10x and 100x as traffic grows.",
            "comparison_matrix": {
                "title": "Architectural Paradigms Overview",
                "headers": ["Dimension", "Single Monolithic Server", "Multi-Tier Distributed System"],
                "rows": [
                    ["Operational Complexity", "Very Low (1 machine to deploy)", "High (service discovery, network orchestration)"],
                    ["Single Point of Failure (SPOF)", "100% Vulnerable (server crash = total outage)", "Zero (redundant instances across availability zones)"],
                    ["Scaling Ceiling", "Hardware limit (CPU cores / RAM limit)", "Practically infinite (horizontal auto-scaling)"],
                    ["Data Consistency", "Trivial (local ACID transactions)", "Complex (CAP theorem, eventual consistency)"],
                    ["Cost at Low Traffic", "Minimal ($10/month VPS)", "Higher (Load balancers, DB clusters, VPCs)"]
                ]
            },
            "failure_scenarios": "When a single server fails in a monolithic architecture, 100% of users experience downtime. In a distributed system, individual nodes fail continuously; the system employs health checks, circuit breakers, and automatic failover so users never notice.",
            "common_mistakes": [
                {"mistake": "Treating system design as a tool memorization contest (e.g. 'Just use Kafka and Redis for everything')", "correction": "Always justify every component with concrete numbers: traffic QPS, read/write ratio, data volume, and latency constraints."},
                {"mistake": "Ignoring the network reality", "correction": "Networks are unreliable, asynchronous, and have variable latency. Always account for timeouts, packet drops, and retries with jitter."}
            ],
            "interview_questions": [
                {"question": "How do you define the difference between High Availability (HA) and Fault Tolerance (FT)?", "answer": "High Availability aims to ensure the system is operational and accessible with minimal downtime (e.g. 99.99% uptime via fast failover), whereas Fault Tolerance guarantees zero interruption or degradation even during hardware failure (e.g. redundant parallel lockstep hardware)."},
                {"question": "What is the very first step when given a vague system design interview prompt like 'Design Twitter'?", "answer": "Never start drawing boxes. First ask clarifying questions to establish Functional Requirements (what users do), Non-Functional Requirements (traffic scale, latency, availability), and explicit System Boundaries."}
            ]
        },
        {
            "id": "hld-vs-lld",
            "title": "High-Level Design (HLD) vs Low-Level Design (LLD)",
            "definition": "HLD defines the macro-architecture (services, load balancers, databases, caches, queues, and network boundaries), while LLD defines the micro-architecture (class hierarchies, object interactions, design patterns, data structures, and memory layouts).",
            "why_we_need_it": "Engineers often confuse the two: drawing class diagrams when asked to design a distributed cache, or talking about Kafka topics when asked to write thread-safe C++ object code. Mastering the boundary is essential for both daily engineering and FAANG interviews.",
            "real_world_analogy": "Building a passenger jet: HLD is the aerodynamic layout, engine thrust specs, fuel tank plumbing, and flight computer bus. LLD is the precise alloy composition of turbine blades, hydraulic valve class interfaces, and landing gear spring mechanics.",
            "how_it_works": "<p>In production engineering workflows, <strong>HLD precedes LLD</strong>. You first establish what services exist, their communication protocol (gRPC / HTTP), and how data is stored. Once service boundaries are agreed upon, LLD details how the internal code of that service is structured in C++.</p>",
            "conceptual_breakdown": [
                "<strong>HLD Scope:</strong> Scalability, Availability, Network Latency, Partitioning, Replication, Storage Engines, Distributed Consensus, SPOF elimination.",
                "<strong>LLD Scope:</strong> SOLID principles, OOP polymorphism, VTable overhead, Smart pointers, RAII, Mutex locks, Design Patterns (Strategy, Factory, Observer).",
                "<strong>The Contract:</strong> HLD defines the <em>External API Contract</em> (JSON/Protobuf over wire); LLD defines the <em>Internal Interface Contract</em> (C++ abstract classes / pure virtual functions)."
            ],
            "arch_diagram": {
                "title": "The HLD-to-LLD Transformation Pipeline",
                "tiers": [
                    {
                        "label": "HLD Level",
                        "nodes": [
                            {"name": "Payment Microservice", "type": "service", "icon": "💳", "what": "Distributed Payment Gateway", "why": "Processes credit card & Stripe transactions", "when": "Order checkout event", "failure": "Queue in dead-letter queue and retry with idempotency key"}
                        ]
                    },
                    {
                        "label": "LLD Level (Inside Service)",
                        "nodes": [
                            {"name": "IPaymentStrategy", "type": "service", "icon": "🔌", "what": "C++ Abstract Interface", "why": "Decouples Stripe vs PayPal implementations", "when": "Polymorphic dispatch", "failure": "Throws custom PaymentGatewayException"},
                            {"name": "StripeStrategy", "type": "service", "icon": "⚡", "what": "Concrete C++ Class", "why": "Executes Stripe SDK calls", "when": "User chooses card", "failure": "Catches network error and applies retry"},
                            {"name": "PaymentPoolManager", "type": "cache", "icon": "🧵", "what": "Thread-safe Connection Pool", "why": "Reuses HTTP keep-alive connections", "when": "High concurrent checkout", "failure": "Bounded blocking queue prevents thread starvation"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "How HLD Architecture Triggers LLD Execution",
                "steps": [
                    {"step": 1, "description": "HLD Layer: API Gateway routes POST /checkout to Payment Microservice over gRPC.", "active_nodes": ["Payment Microservice"]},
                    {"step": 2, "description": "LLD Layer: C++ Controller invokes PaymentFactory to instantiate StripeStrategy.", "active_nodes": ["Payment Microservice", "IPaymentStrategy", "StripeStrategy"]},
                    {"step": 3, "description": "LLD Layer: StripeStrategy acquires connection from PaymentPoolManager under std::unique_lock.", "active_nodes": ["StripeStrategy", "PaymentPoolManager"]},
                    {"step": 4, "description": "HLD Layer: Payment Microservice persists transaction record in PostgreSQL and emits Kafka event.", "active_nodes": ["Payment Microservice"]}
                ]
            },
            "tradeoffs": "Focusing exclusively on HLD leads to untestable, buggy code inside services. Focusing exclusively on LLD leads to beautifully written C++ code that crashes because the single database cannot handle 50,000 queries per second. A senior engineer balances both.",
            "comparison_matrix": {
                "title": "Comprehensive HLD vs LLD Comparison Matrix",
                "headers": ["Criterion", "High-Level Design (HLD)", "Low-Level Design (LLD)"],
                "rows": [
                    ["Primary Focus", "Services, Databases, Caches, Queues, Load Balancers", "Classes, Methods, Interfaces, Design Patterns, Data Structures"],
                    ["Scale Level", "Multiple servers, clusters, availability zones", "Single machine, single process, memory layout"],
                    ["Key Questions", "'Where is data cached? How do we shard the database?'", "'Which design pattern decouples this? How is thread safety ensured?'"],
                    ["Primary Diagram", "System Block Architecture Diagram, Network Flow", "UML Class Diagram, Sequence Diagram, State Machine"],
                    ["Target Language", "Language-agnostic (Architectural blueprints)", "Concrete language (Modern C++20, RAII, Smart Pointers)"],
                    ["Interview Format", "45-minute System Design Round (Whiteboard/Excalidraw)", "45-minute Machine Coding / Object-Oriented Design Round"]
                ]
            },
            "failure_scenarios": "An HLD failure is a network partition or database CPU saturation causing cascading outages. An LLD failure is a null-pointer dereference, memory leak, or mutex deadlock causing a segmentation fault in a single process.",
            "common_mistakes": [
                {"mistake": "Drawing UML class inheritance diagrams during a High-Level System Design interview", "correction": "In HLD rounds, draw architectural block diagrams showing services, databases, caches, and load balancers."},
                {"mistake": "Using HLD tools (like adding a distributed Kafka queue) to solve an internal in-process concurrency problem", "correction": "Use appropriate LLD primitives (`std::queue`, `std::mutex`, `std::condition_variable`) for in-process thread communication."}
            ],
            "interview_questions": [
                {"question": "How do you explain the connection between an API Gateway in HLD and the Facade Pattern in LLD?", "answer": "Both serve the exact same architectural principle at different scales: they provide a simplified, unified entry point to a complex subsystem. An API Gateway is a distributed network-level Facade, while the Facade Pattern is an in-process class-level abstraction."}
            ]
        },
        {
            "id": "anatomy-of-systems",
            "title": "Components, Services, Modules, Dependencies & Boundaries",
            "definition": "The foundational taxonomy of software systems: Components (self-contained units of functionality), Services (independently deployable network endpoints), Modules (code-level packaging), Dependencies (coupling between units), and System Boundaries (isolation fences).",
            "why_we_need_it": "Without strict boundary definitions, systems devolve into an unmaintainable 'Big Ball of Mud' where changing one database column in the billing module silently breaks the user recommendation engine.",
            "real_world_analogy": "An international airport: terminals, luggage carousels, customs, and air traffic control are distinct services with strict physical security boundaries and standardized conveyor protocols.",
            "how_it_works": "<p>A healthy system organizes software into <strong>loosely coupled, highly cohesive</strong> services. Each service owns its own data store (Database-per-Service pattern) and communicates exclusively through published public APIs (REST, gRPC, or asynchronous message queues), never by directly reaching into another service's internal database.</p>",
            "conceptual_breakdown": [
                "<strong>Component:</strong> A modular, deployable, and replaceable part of a system that encapsulates implementation and exposes a set of interfaces.",
                "<strong>Service:</strong> A standalone process exposing network endpoints over HTTP/gRPC/Kafka. It has an independent CI/CD deployment lifecycle.",
                "<strong>Module:</strong> A logical grouping of code (C++ namespace, package, library) within a single codebase.",
                "<strong>System Boundary:</strong> The perimeter separating internal trusted services from external untrusted clients (guarded by API Gateways and Firewalls)."
            ],
            "arch_diagram": {
                "title": "System Boundaries and Service Decoupling",
                "tiers": [
                    {
                        "label": "Public Untrusted Zone",
                        "nodes": [
                            {"name": "External Mobile Client", "type": "client", "icon": "📱", "what": "iOS / Android App", "why": "End-user interface", "when": "Public Internet", "failure": "Handle offline mode & retry"}
                        ]
                    },
                    {
                        "label": "DMZ / Gateway Boundary",
                        "nodes": [
                            {"name": "API Gateway (Boundary)", "type": "lb", "icon": "🚪", "what": "Kong / Envoy Gateway", "why": "Authentication, TLS termination, Rate limiting", "when": "Every incoming request", "failure": "Return 429 / 503 error"}
                        ]
                    },
                    {
                        "label": "Private VPC Service Zone",
                        "nodes": [
                            {"name": "User Service", "type": "service", "icon": "👤", "what": "User Profile Service", "why": "Manages accounts & auth", "when": "Profile requests", "failure": "Circuit breaker fallback"},
                            {"name": "Order Service", "type": "service", "icon": "📦", "what": "Order Processing Service", "why": "Manages cart & checkout", "when": "Checkout actions", "failure": "Queue in outbox table"}
                        ]
                    },
                    {
                        "label": "Private Data Zone",
                        "nodes": [
                            {"name": "User DB (Private)", "type": "db", "icon": "🗄️", "what": "Postgres User Database", "why": "Private to User Service ONLY", "when": "Direct queries from User Service", "failure": "Read replica failover"},
                            {"name": "Order DB (Private)", "type": "db", "icon": "🗄️", "what": "Postgres Order Database", "why": "Private to Order Service ONLY", "when": "Direct queries from Order Service", "failure": "Read replica failover"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "Bounded Context Communication Flow",
                "steps": [
                    {"step": 1, "description": "Client sends request across System Boundary to API Gateway with JWT Auth header.", "active_nodes": ["External Mobile Client", "API Gateway (Boundary)"]},
                    {"step": 2, "description": "API Gateway validates JWT, strips public headers, and forwards internal request to Order Service.", "active_nodes": ["API Gateway (Boundary)", "Order Service"]},
                    {"step": 3, "description": "Order Service needs user address. Instead of querying User DB directly (Forbidden!), it calls User Service via gRPC.", "active_nodes": ["Order Service", "User Service"]},
                    {"step": 4, "description": "Each service queries its own private database, enforcing strict encapsulation.", "active_nodes": ["User Service", "User DB (Private)", "Order Service", "Order DB (Private)"]}
                ]
            },
            "tradeoffs": "Strict service boundaries prevent spaghetti dependencies but introduce network latency and distributed transaction complexity (Saga pattern instead of simple SQL JOINs).",
            "comparison_matrix": {
                "title": "Architectural Units Taxonomy",
                "headers": ["Unit", "Deployment Boundary", "Communication", "Data Storage"],
                "rows": [
                    ["Module", "Compiled into same binary", "In-memory function calls", "Shared process memory"],
                    ["Component", "Library / DLL / Package", "Linker / Interface calls", "Process memory / shared DB"],
                    ["Service", "Independent container / VM", "Network RPC (HTTP/gRPC/Kafka)", "Dedicated private database"],
                    ["Subsystem", "Collection of cooperating services", "Event streams & APIs", "Distributed data cluster"]
                ]
            },
            "failure_scenarios": "When Service A directly queries Service B's database, a schema change in Service B instantly crashes Service A without compile-time warning (Hidden Coupling Disaster). Always enforce API contracts.",
            "common_mistakes": [
                {"mistake": "Allowing multiple microservices to read/write to the same shared database instance", "correction": "Enforce the Database-per-Service pattern. Services must access foreign data exclusively via public APIs."}
            ],
            "interview_questions": [
                {"question": "Why is high cohesion and loose coupling considered the golden rule of system architecture?", "answer": "High cohesion ensures all code inside a service belongs to the same business capability, making it easy to understand and modify. Loose coupling ensures services have minimal knowledge of each other's internals, allowing teams to deploy, scale, and refactor independently."}
            ]
        },
        {
            "id": "client-server-api-database",
            "title": "The Core Foundation: Client, Server, API, Database & Infra",
            "definition": "The universal 5-element foundation of every distributed software system on Earth: Client (User Agent), Server (Compute), API (Communication Protocol), Database (Stateful Persistence), and Infrastructure (Compute, Network & OS Hosting).",
            "why_we_need_it": "Every complex platform—whether Netflix, Uber, or Amazon—is ultimately built by composing and scaling these 5 core building blocks.",
            "real_world_analogy": "A restaurant: Client is the customer, API is the printed menu & waiter protocol, Server is the kitchen chefs, Database is the pantry/refrigerator storage, and Infrastructure is the physical building, gas lines, and electricity.",
            "how_it_works": "<p>Clients initiate requests; Servers process computational logic; APIs define the payload schema (JSON/Protobuf over TCP/TLS); Databases provide durable ACID persistence; Infrastructure provides the hardware execution environment (Bare Metal, VMs, Docker Containers, Kubernetes clusters, Cloud VPCs).</p>",
            "conceptual_breakdown": [
                "<strong>Client:</strong> Web browser, Mobile app, IoT sensor, or another backend service acting as a consumer.",
                "<strong>Server:</strong> Stateless computational node that executes business rules and returns structured responses.",
                "<strong>API (Application Programming Interface):</strong> The formal contract specifying endpoints, request headers, query params, and JSON error structures.",
                "<strong>Database:</strong> The durable state store providing indexing, transactional atomicity, and query capabilities.",
                "<strong>Infrastructure:</strong> Compute (EC2/K8s), Storage (EBS/S3), Networking (VPC, Subnets, Gateways), and IAM security policies."
            ],
            "arch_diagram": {
                "title": "The 5 Core Elements of Software Architecture",
                "tiers": [
                    {
                        "label": "1. Client",
                        "nodes": [
                            {"name": "Client (User Agent)", "type": "client", "icon": "💻", "what": "Mobile / Web / CLI", "why": "Captures user input and renders output", "when": "Every user interaction", "failure": "Offline queueing & optimistic UI"}
                        ]
                    },
                    {
                        "label": "2. Network & API",
                        "nodes": [
                            {"name": "API Contract (HTTPS / JSON)", "type": "lb", "icon": "📜", "what": "REST / gRPC Interface", "why": "Standardized wire communication", "when": "Data in transit", "failure": "TLS handshake retry"}
                        ]
                    },
                    {
                        "label": "3. Server (Compute)",
                        "nodes": [
                            {"name": "Backend Application Server", "type": "service", "icon": "🖥️", "what": "Stateless C++ / Go / Java App", "why": "Executes domain business rules", "when": "Request processing", "failure": "Horizontally scaled behind Load Balancer"}
                        ]
                    },
                    {
                        "label": "4. Database (State)",
                        "nodes": [
                            {"name": "Database Persistence", "type": "db", "icon": "💾", "what": "PostgreSQL / DynamoDB", "why": "Durable transactional storage", "when": "State reads/writes", "failure": "Automated WAL backup & standby replica"}
                        ]
                    },
                    {
                        "label": "5. Infrastructure",
                        "nodes": [
                            {"name": "Cloud Infrastructure (AWS / K8s)", "type": "storage", "icon": "☁️", "what": "VPC, Linux Containers, EBS, Subnets", "why": "Hosting environment", "when": "Continuous execution", "failure": "Multi-AZ redundancy"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "End-to-End 5-Element Request Lifecycle",
                "steps": [
                    {"step": 1, "description": "1. Client (Browser) captures user login form and serializes credentials into JSON.", "active_nodes": ["Client (User Agent)"]},
                    {"step": 2, "description": "2. API Layer transmits payload over HTTPS POST /api/v1/auth/login across the Internet.", "active_nodes": ["Client (User Agent)", "API Contract (HTTPS / JSON)"]},
                    {"step": 3, "description": "3. Server receives request, validates bcrypt password hash, and generates session token.", "active_nodes": ["API Contract (HTTPS / JSON)", "Backend Application Server"]},
                    {"step": 4, "description": "4. Database executes query 'SELECT * FROM users WHERE email = ?' and records login timestamp.", "active_nodes": ["Backend Application Server", "Database Persistence"]},
                    {"step": 5, "description": "5. Infrastructure routes JSON HTTP 200 OK response back to Client.", "active_nodes": ["Cloud Infrastructure (AWS / K8s)", "Client (User Agent)"]}
                ]
            },
            "tradeoffs": "Stateless servers can scale horizontally from 1 to 10,000 instances instantly, but stateful databases cannot. Therefore, system design prioritizes pushing state out of the compute tier into specialized, replicated storage engines.",
            "comparison_matrix": {
                "title": "Stateful vs Stateless System Components",
                "headers": ["Characteristic", "Stateless Servers (Compute)", "Stateful Databases (Storage)"],
                "rows": [
                    ["Horizontal Scaling", "Trivial (Add 50 EC2 instances behind Load Balancer)", "Complex (Requires sharding, replication lag handling, consensus)"],
                    ["Crash Recovery", "Instant (Spawn new container, zero data loss)", "Requires replaying write-ahead logs (WAL) & crash recovery"],
                    ["Local Disk Dependency", "None (Ephemeral disk)", "Strict (High IOPS NVMe SSDs with RAID/EBS)"],
                    ["Routing Affinity", "Any server can process any user request", "Requests must route to the specific primary or shard owner"]
                ]
            },
            "failure_scenarios": "Storing session state in local server RAM: when that server crashes or auto-scales down, all active user logins are lost. Solution: Store sessions in a shared distributed Redis cluster.",
            "common_mistakes": [
                {"mistake": "Storing user uploaded images or files directly in local server folders (`/var/www/uploads`)", "correction": "Local disks on cloud servers are ephemeral. Store all media in durable Object Storage (Amazon S3 / Google Cloud Storage)."}
            ],
            "interview_questions": [
                {"question": "Why is keeping the web application tier strictly stateless considered the most important scaling rule?", "answer": "Because stateless servers allow auto-scaling groups to scale up or down dynamically based on CPU/traffic without worrying about losing user session state, and allow load balancers to route any request to any healthy server indiscriminately."}
            ]
        },
        {
            "id": "system-evolution-journey",
            "title": "The Progressive Evolution: 1 Server to Multi-Tier Distributed Web",
            "definition": "The step-by-step evolutionary blueprint demonstrating how an architecture naturally transforms from a single $5 server into a global, multi-region distributed system serving 50 million active users.",
            "why_we_need_it": "Prevents overengineering on Day 1 while showing interviewers you understand the exact trigger point (bottleneck) for introducing Load Balancers, Caches, Read Replicas, Sharding, CDNs, and Queues.",
            "real_world_analogy": "A solo baker starting in a home kitchen (1 server) -> opening a retail shop with a cashier and separate ovens (2 tiers) -> opening 50 franchise branches with centralized warehouse distribution (Multi-region CDN & Sharding).",
            "how_it_works": "<p>Architecture evolves through 6 distinct stages driven by specific resource bottlenecks:</p><ol><li><strong>Stage 1 (1-100 Users):</strong> Single Server (App + DB on same box).</li><li><strong>Stage 2 (1,000 Users):</strong> Separate Web Tier from DB Tier.</li><li><strong>Stage 3 (10,000 Users):</strong> Add Load Balancer + Multiple App Servers.</li><li><strong>Stage 4 (100,000 Users):</strong> Add Redis Cache + CDN for static assets.</li><li><strong>Stage 5 (1,000,000 Users):</strong> Master-Slave DB Replication + Async Message Queues (Kafka/RabbitMQ).</li><li><strong>Stage 6 (10,000,000+ Users):</strong> Database Sharding + Microservices + Multi-Region Active-Active Deployments.</li></ol>",
            "conceptual_breakdown": [
                "<strong>Bottleneck 1 (CPU/RAM exhaustion):</strong> Separate web server from database server.",
                "<strong>Bottleneck 2 (Web server throughput limit):</strong> Introduce Load Balancer with horizontal stateless scaling.",
                "<strong>Bottleneck 3 (Database read overload):</strong> Introduce in-memory Cache (Redis) and Database Read Replicas.",
                "<strong>Bottleneck 4 (Global latency & static asset load):</strong> Introduce Content Delivery Network (CDN).",
                "<strong>Bottleneck 5 (Database write throughput & disk IOPS):</strong> Horizontal database sharding & asynchronous message queues."
            ],
            "arch_diagram": {
                "title": "Stage 6: Mature Multi-Tier Scaled System Architecture",
                "tiers": [
                    {
                        "label": "Edge Tier",
                        "nodes": [
                            {"name": "Global CDN (Edge)", "type": "client", "icon": "🌐", "what": "Cloudflare / CloudFront", "why": "Caches static images/videos at edge", "when": "Static assets", "failure": "Origin shield fallback"}
                        ]
                    },
                    {
                        "label": "Traffic Tier",
                        "nodes": [
                            {"name": "Elastic Load Balancer", "type": "lb", "icon": "⚖️", "what": "AWS ALB / NGINX", "why": "Distributes requests across app cluster", "when": "Dynamic traffic", "failure": "Multi-AZ redundant pair"}
                        ]
                    },
                    {
                        "label": "Compute Tier",
                        "nodes": [
                            {"name": "App Cluster (Node 1)", "type": "service", "icon": "⚙️", "what": "Stateless API server", "why": "Executes business logic", "when": "Dynamic requests", "failure": "Auto-scaling replacement"},
                            {"name": "App Cluster (Node 2)", "type": "service", "icon": "⚙️", "what": "Stateless API server", "why": "Executes business logic", "when": "Dynamic requests", "failure": "Auto-scaling replacement"}
                        ]
                    },
                    {
                        "label": "Cache & Queue Tier",
                        "nodes": [
                            {"name": "Redis Distributed Cache", "type": "cache", "icon": "⚡", "what": "Redis Cluster", "why": "Absorbs 90% of read traffic", "when": "Hot reads", "failure": "Redis Sentinel auto-failover"},
                            {"name": "Kafka Message Queue", "type": "queue", "icon": "📬", "what": "Apache Kafka Log", "why": "Asynchronous task buffer", "when": "Heavy writes & notifications", "failure": "Replicated partitions"}
                        ]
                    },
                    {
                        "label": "Storage Tier",
                        "nodes": [
                            {"name": "Primary DB (Writes)", "type": "db", "icon": "🗄️", "what": "Postgres Primary", "why": "Handles all INSERT/UPDATE writes", "when": "State mutations", "failure": "Promote read replica"},
                            {"name": "Read Replicas (Reads)", "type": "db", "icon": "📖", "what": "Postgres Read Replicas", "why": "Handles heavy read queries", "when": "Search & feeds", "failure": "Drop dead replica from pool"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "Evolutionary Scaling Request Routing",
                "steps": [
                    {"step": 1, "description": "Stage 1-2: Direct client to server connection collapses under 5,000 concurrent connections.", "active_nodes": ["App Cluster (Node 1)"]},
                    {"step": 2, "description": "Stage 3: Load Balancer deployed. Traffic distributed evenly across Node 1 and Node 2.", "active_nodes": ["Elastic Load Balancer", "App Cluster (Node 1)", "App Cluster (Node 2)"]},
                    {"step": 3, "description": "Stage 4: Redis Cache absorbs 85% of read queries. Database CPU drops from 95% to 15%.", "active_nodes": ["Redis Distributed Cache", "App Cluster (Node 1)"]},
                    {"step": 4, "description": "Stage 5: Heavy write jobs (Video transcoding / Emails) offloaded to Kafka Queue for async worker processing.", "active_nodes": ["Kafka Message Queue", "Primary DB (Writes)"]}
                ]
            },
            "tradeoffs": "Every added component (Cache, Queue, Replica, Shard) increases system throughput but introduces consistency challenges, operational maintenance overhead, and debugging complexity.",
            "comparison_matrix": {
                "title": "System Scale Evolution Matrix",
                "headers": ["Scale Stage", "Target Users", "Architecture Topology", "Primary Bottleneck Addressed"],
                "rows": [
                    ["Stage 1", "1 - 100", "Single Box (App + DB)", "None (Simple MVP)"],
                    ["Stage 2", "1,000", "App Server + Dedicated DB Server", "CPU & RAM resource contention"],
                    ["Stage 3", "10,000", "Load Balancer + N Stateless App Servers", "Web server connection saturation & SPOF"],
                    ["Stage 4", "100,000", "App Cluster + Redis Cache + CDN", "Database read latency & static asset bandwidth"],
                    ["Stage 5", "1,000,000", "Cache + Master-Slave DB + Message Queues", "Database write lock contention & synchronous lag"],
                    ["Stage 6", "10,000,000+", "Microservices + DB Sharding + Multi-Region", "Single database storage ceiling & cross-continental latency"]
                ]
            },
            "failure_scenarios": "Scaling by making the single database server bigger (Vertical Scaling / Scale-Up) eventually hits a hard physical limit where the largest available cloud instance ($10,000/month 128-core machine) still runs out of memory. Horizontal scaling is the only viable path to planetary scale.",
            "common_mistakes": [
                {"mistake": "Adding microservices and Kafka to a prototype with 50 active users", "correction": "Start with a clean modular monolith on a single database. Evolve to distributed components only when concrete performance metrics demand it."}
            ],
            "interview_questions": [
                {"question": "When an interviewer asks you to scale a system from 10k to 10M users, what is the systematic order of components you introduce?", "answer": "1. Split App and DB -> 2. Add Load Balancer and horizontal app servers -> 3. Add Redis cache for hot reads -> 4. Add CDN for static media -> 5. Add Database Read Replicas -> 6. Add Message Queues for async workloads -> 7. Shard the Database horizontally by Partition Key."}
            ]
        }
    ]
}

# =========================================================================
# MODULE 2: Requirements Analysis & Scoping
# =========================================================================
m2 = {
    "module_id": "02",
    "module_title": "Requirements Analysis & Scoping",
    "description": "How to start any system design problem: Functional vs Non-Functional Requirements, Constraints, Assumptions, Traffic, and System Boundaries.",
    "topics": [
        {
            "id": "functional-vs-non-functional",
            "title": "Functional vs Non-Functional Requirements (NFRs)",
            "definition": "Functional Requirements (FR) define WHAT a system must do (features, user actions, business workflows). Non-Functional Requirements (NFR) define HOW WELL the system must perform (availability, latency, consistency, scalability, durability, security).",
            "why_we_need_it": "A system that correctly stores a tweet (FR) but takes 15 seconds to load and crashes every Friday (failed NFR) is an engineering failure. Senior system design interviews are 80% about solving NFRs.",
            "real_world_analogy": "Buying an automobile: Functional requirement is that it drives from Point A to Point B with 4 passengers. Non-functional requirements are fuel efficiency (35 MPG), top speed (120 MPH), safety rating (5-star crash durability), and maintenance intervals (every 10,000 miles).",
            "how_it_works": "<p>In the first 5 minutes of any system design discussion, you must explicitly partition the problem space into two clear lists: 3-5 core Functional use-cases and 4-5 measurable Non-Functional targets.</p>",
            "conceptual_breakdown": [
                "<strong>Functional Scope (FR):</strong> User post creation, timeline feed retrieval, user search, follow graph, push notifications.",
                "<strong>High Availability (NFR):</strong> System must achieve 99.99% uptime (~52 minutes downtime per year).",
                "<strong>Low Latency (NFR):</strong> p99 read latency < 100ms for timeline rendering; p99 write latency < 500ms for post ingestion.",
                "<strong>Eventual vs Strong Consistency (NFR):</strong> Timelines can tolerate 2-3 seconds of replication lag (Eventual Consistency), but credit card billing requires Strong Consistency."
            ],
            "arch_diagram": {
                "title": "Requirements Decomposition Matrix",
                "tiers": [
                    {
                        "label": "User Actions",
                        "nodes": [
                            {"name": "Functional: Post Tweet", "type": "client", "icon": "✍️", "what": "User publishes 280-char text + media", "why": "Core content generation", "when": "Write path", "failure": "Store in client outbox & retry"}
                        ]
                    },
                    {
                        "label": "Architectural Guardrails",
                        "nodes": [
                            {"name": "NFR: 99.99% Availability", "type": "lb", "icon": "🛡️", "what": "Multi-AZ redundant infrastructure", "why": "Zero single points of failure", "when": "System availability", "failure": "Automatic DNS health failover"},
                            {"name": "NFR: p99 Latency < 100ms", "type": "cache", "icon": "⚡", "what": "Redis Fan-out Timeline Cache", "why": "Sub-millisecond feed generation", "when": "Read path", "failure": "Pre-computed timeline cache"}
                        ]
                    },
                    {
                        "label": "Data Guarantees",
                        "nodes": [
                            {"name": "NFR: 100% Durability", "type": "db", "icon": "💾", "what": "3x Replicated Distributed Storage", "why": "Never lose user data once ACKed", "when": "Data persistence", "failure": "Cross-region backup"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "Balancing FRs with Strict NFR Latency Budgets",
                "steps": [
                    {"step": 1, "description": "FR Execution: User requests Timeline Feed (GET /feed).", "active_nodes": ["Functional: Post Tweet"]},
                    {"step": 2, "description": "NFR Enforcement: Request hits Redis timeline cache to satisfy < 100ms p99 latency SLA.", "active_nodes": ["NFR: p99 Latency < 100ms"]},
                    {"step": 3, "description": "NFR Enforcement: Multi-AZ load balancer guarantees 99.99% availability even if Zone A is offline.", "active_nodes": ["NFR: 99.99% Availability"]},
                    {"step": 4, "description": "Result: Functional requirement delivered while strictly meeting all Non-Functional SLAs.", "active_nodes": ["NFR: 100% Durability"]}
                ]
            },
            "tradeoffs": "You cannot maximize all NFRs simultaneously. For example, guaranteeing absolute Strong Consistency (ACID across regions) increases write latency and decreases availability during network partitions (CAP theorem).",
            "comparison_matrix": {
                "title": "Core Non-Functional Requirements Spectrum",
                "headers": ["NFR Metric", "Target SLA Example", "Primary Architecture Solution"],
                "rows": [
                    ["Availability", "99.99% (4 Nines)", "Redundant active-active instances across multiple Availability Zones"],
                    ["Read Latency", "p99 < 50ms", "Distributed in-memory caching (Redis), CDNs, and read replicas"],
                    ["Write Latency", "p99 < 200ms", "Asynchronous task queues (Kafka) and Write-Ahead Logging"],
                    ["Data Durability", "99.999999999% (11 Nines)", "Multi-region Erasure Coding and 3x replica storage (Amazon S3)"],
                    ["Consistency", "Eventual vs Strong", "Choose between CP (Raft/Paxos) and AP (Dynamo/Cassandra)"]
                ]
            },
            "failure_scenarios": "Failing to define NFRs upfront: designing a payment system with eventual consistency that double-charges customers, or designing a chat app with synchronous SQL queries that freezes under 10,000 active group chats.",
            "common_mistakes": [
                {"mistake": "Listing 25 functional features during an interview instead of focusing on the top 3-4 core workflows", "correction": "Deep-dive into 3 core use cases. Interviewers evaluate architectural depth, not exhaustive feature lists."}
            ],
            "interview_questions": [
                {"question": "How do you handle conflicting NFRs like ultra-low latency vs strong data consistency?", "answer": "Explicitly identify which data requires strict consistency (e.g. financial balances require CP) versus data that thrives on low latency with eventual consistency (e.g. video view counters, social feeds). Apply different architectural pipelines to each."}
            ]
        },
        {
            "id": "assumptions-and-constraints",
            "title": "Establishing Constraints, Assumptions, Users & Actors",
            "definition": "The technique of establishing explicit mathematical scale, traffic boundaries, user demographics, hardware constraints, and out-of-scope agreements to eliminate ambiguity.",
            "why_we_need_it": "Vague questions like 'Design Netflix' can mean designing the video encoding pipeline, the recommendation machine learning model, the billing engine, or the content delivery network. Establishing constraints scopes the problem to a solvable engineering goal.",
            "real_world_analogy": "A defense contractor building a military vehicle: before designing, they must know if it operates in desert heat (-10°C to +50°C), aquatic rivers, or urban roads, and whether ammunition weight is 500kg or 5,000kg.",
            "how_it_works": "<p>Actively state reasonable assumptions and confirm them with the interviewer:</p><ul><li>'I assume our target is 100 million Daily Active Users with a 10:1 Read-to-Write ratio.'</li><li>'I assume video files are up to 4K resolution with an average duration of 10 minutes.'</li><li>'I will treat user recommendation ML algorithms as an external black-box service and focus on video ingestion, encoding, storage, and streaming CDN delivery.'</li></ul>",
            "conceptual_breakdown": [
                "<strong>Actors:</strong> Creators (uploaders), Consumers (viewers), Moderators (admins), Automated Systems (billing cron, transcoders).",
                "<strong>Hard Constraints:</strong> Maximum upload size (2 GB), network bandwidth budget, legal data compliance (GDPR in EU).",
                "<strong>Out of Scope:</strong> Explicitly agreeing on features NOT to build in this 45-minute session to avoid wasting time."
            ],
            "arch_diagram": {
                "title": "System Scoping and Boundary Partitioning",
                "tiers": [
                    {
                        "label": "System Actors",
                        "nodes": [
                            {"name": "Content Creator (Writer)", "type": "client", "icon": "🎥", "what": "Uploads 1080p/4K raw video", "why": "Ingestion path actor", "when": "Upload sessions", "failure": "Resumable chunked upload"},
                            {"name": "Content Viewer (Reader)", "type": "client", "icon": "🍿", "what": "Streams video on mobile/TV", "why": "Egress path actor (95% of traffic)", "when": "Playback", "failure": "Adaptive bitrate switching"}
                        ]
                    },
                    {
                        "label": "In Scope System",
                        "nodes": [
                            {"name": "Video Streaming Architecture", "type": "service", "icon": "⚡", "what": "Ingestion -> Transcode -> CDN Delivery", "why": "Core design focus", "when": "In-Scope", "failure": "Handled with full redundancy"}
                        ]
                    },
                    {
                        "label": "Explicitly Out of Scope",
                        "nodes": [
                            {"name": "Ad Bidding / Payment Engine", "type": "storage", "icon": "🚫", "what": "External third-party integration", "why": "Agreed out of scope to preserve focus", "when": "Out of scope", "failure": "Mocked with stub interface"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "Actor-Based Request Routing",
                "steps": [
                    {"step": 1, "description": "Creator uploads 1GB video file via resumable HTTP multipart upload.", "active_nodes": ["Content Creator (Writer)", "Video Streaming Architecture"]},
                    {"step": 2, "description": "System transcodes video into 360p, 720p, 1080p, 4K HLS chunked streams.", "active_nodes": ["Video Streaming Architecture"]},
                    {"step": 3, "description": "100,000 Viewers stream chunks simultaneously from Edge CDN with zero origin server strain.", "active_nodes": ["Content Viewer (Reader)", "Video Streaming Architecture"]}
                ]
            },
            "tradeoffs": "Designing for an overly broad scope results in shallow box-drawing. Designing for a tightly scoped set of constraints allows deep architectural exploration of bottlenecks and failure handling.",
            "comparison_matrix": {
                "title": "System Actors and Workload Characteristics",
                "headers": ["Actor / Persona", "Traffic Ratio", "Primary Operation", "Critical SLA"],
                "rows": [
                    ["Content Consumer", "95% - 99% of requests", "Read-heavy (GET requests, CDN caching)", "Sub-second start latency (TTFB < 200ms)"],
                    ["Content Producer", "1% - 5% of requests", "Write-heavy (Large multipart file uploads)", "100% upload durability & zero data corruption"],
                    ["System Admin / Ops", "< 0.1% of requests", "Audit queries, moderation flags, analytics", "Audit trail consistency over raw speed"]
                ]
            },
            "failure_scenarios": "Assuming an unlimited upload size without constraints: a single user uploading a 500 GB file consumes all server memory and disk space, starving other users (Denial of Service).",
            "common_mistakes": [
                {"mistake": "Silently making assumptions in your head without stating them to the interviewer", "correction": "Always vocalize your assumptions clearly and ask: 'Does this scale match your expectations for this problem?'"}
            ],
            "interview_questions": [
                {"question": "How do you handle an interviewer who refuses to answer your clarifying questions and says 'You decide'?", "answer": "State: 'Understood. In that case, I will assume a large-scale global service with 50M DAU, 10:1 read/write ratio, and 99.99% availability target. If our time allows, I will show how the architecture adapts if these constraints change.'"}
            ]
        },
        {
            "id": "defining-system-boundaries",
            "title": "System Boundaries, Core APIs & Data Contracts",
            "definition": "The practice of creating formal input/output contracts (APIs) and defining data entity schemas before designing internal storage and microservice topologies.",
            "why_we_need_it": "APIs and Data Schemas represent the non-negotiable contract between your system and the outside world. Designing the API first (API-First Design) ensures the architecture directly satisfies real user use cases.",
            "real_world_analogy": "Ordering goods in international shipping: the standardized shipping container dimensions (20ft / 40ft ISO standards) dictate crane designs, cargo ship layouts, and highway truck trailers worldwide.",
            "how_it_works": "<p>Translate functional requirements directly into clean RESTful endpoints or gRPC Protobuf definitions with explicit request payloads, response codes, and query parameters.</p>",
            "conceptual_breakdown": [
                "<strong>API Signature:</strong> HTTP Method + URL path + Query parameters + Request Headers (Authorization, Idempotency-Key).",
                "<strong>Data Contract:</strong> Strict JSON / Protobuf schema with field types, required/optional flags, and validation rules.",
                "<strong>Core Entities:</strong> Nouns representing persistent state (e.g. `User`, `Video`, `Comment`, `Channel`)."
            ],
            "arch_diagram": {
                "title": "API Contract and Data Boundary",
                "tiers": [
                    {
                        "label": "Public Interface",
                        "nodes": [
                            {"name": "POST /api/v1/videos/upload", "type": "client", "icon": "📤", "what": "Video Upload Endpoint", "why": "Initiates multipart video upload session", "when": "Creator publishes content", "failure": "400 Bad Request on invalid format"},
                            {"name": "GET /api/v1/videos/{id}/manifest", "type": "client", "icon": "📥", "what": "Streaming Manifest Endpoint", "why": "Returns HLS/DASH .m3u8 playlist", "when": "Playback start", "failure": "404 Not Found if video deleted"}
                        ]
                    },
                    {
                        "label": "Core Data Entities",
                        "nodes": [
                            {"name": "Entity: Video Metadata", "type": "db", "icon": "📋", "what": "video_id, title, duration, uploader_id, s3_url", "why": "Relational metadata model", "when": "Query / search", "failure": "Stored in PostgreSQL with read replicas"},
                            {"name": "Entity: Video Chunks", "type": "storage", "icon": "📦", "what": "TS / fMP4 chunks (4-second segments)", "why": "Binary media storage", "when": "CDN edge caching", "failure": "Stored in S3 with 11 Nines durability"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "API Request Contract Validation",
                "steps": [
                    {"step": 1, "description": "Client invokes POST /api/v1/videos/upload with video title and size metadata.", "active_nodes": ["POST /api/v1/videos/upload"]},
                    {"step": 2, "description": "Gateway validates authorization token and payload schema against API Contract.", "active_nodes": ["POST /api/v1/videos/upload", "Entity: Video Metadata"]},
                    {"step": 3, "description": "System issues Presigned S3 Upload URL to client. Binary video stream uploads directly to S3 without passing through API servers!", "active_nodes": ["Entity: Video Chunks"]}
                ]
            },
            "tradeoffs": "Streaming heavy file uploads through backend API servers burns CPU and network bandwidth. Using presigned object storage URLs offloads massive binary traffic directly to S3.",
            "comparison_matrix": {
                "title": "API Protocols for System Boundaries",
                "headers": ["Protocol", "Serialization Format", "Transport", "Best Suited For"],
                "rows": [
                    ["REST over HTTPS", "JSON / Text", "HTTP/1.1 or HTTP/2", "Public client-facing APIs (Web/Mobile)"],
                    ["gRPC", "Protocol Buffers (Binary)", "HTTP/2 (Multiplexed streams)", "Internal microservice-to-microservice high-speed RPC"],
                    ["GraphQL", "JSON", "HTTP POST", "Complex dashboards requiring custom field selection in 1 request"],
                    ["WebSockets", "Raw Binary / Text", "Persistent TCP connection", "Bi-directional real-time chat & live market feeds"]
                ]
            },
            "failure_scenarios": "Failing to version APIs (`/api/v1/` vs `/api/`): when you change a field name from `userId` to `user_id`, millions of legacy mobile apps in the wild crash instantly upon updating.",
            "common_mistakes": [
                {"mistake": "Jumping into database schema design before establishing the public API endpoints", "correction": "Define the API endpoints first. APIs define how the system is used; the database schema is an internal implementation detail that supports the API."}
            ],
            "interview_questions": [
                {"question": "How do you design a file upload API for a 20 GB video file without exhausting web server memory?", "answer": "Use a two-step API: 1. `POST /videos/upload-session` creates a metadata record and returns a Presigned S3 Multipart Upload URL. 2. The client uploads 5MB chunks directly from the browser to Amazon S3 via S3's Multipart API. The API servers never touch the raw video bytes."}
            ]
        },
        {
            "id": "interview-scoping-walkthrough",
            "title": "Interview Case Walkthrough: Scoping 'Design YouTube' from Scratch",
            "definition": "A step-by-step masterclass demonstrating the exact dialogue, mathematical scoping, and requirement extraction for a top-tier FAANG interview problem: 'Design YouTube'.",
            "why_we_need_it": "Provides learners with a concrete template they can replicate in real interviews to convert an ambiguous 2-word prompt into a structured, production-ready system design blueprint.",
            "real_world_analogy": "A courtroom trial opening statement: establishing the exact facts, scope, and boundaries before presenting the detailed evidence.",
            "how_it_works": "<p>Follow the 5-phase opening formula:</p><ol><li><strong>Clarification (2 mins):</strong> Clarify core features (Upload, Watch, Search). Confirm out of scope (Comments, Live streaming).</li><li><strong>Functional Requirements (2 mins):</strong> 3 core FRs.</li><li><strong>Non-Functional Requirements (2 mins):</strong> Availability (99.99%), Latency (Smooth playback, < 200ms start), Durability (Zero video loss).</li><li><strong>Capacity & Scale Estimation (3 mins):</strong> 1B DAU, 5B video views/day, 50M uploads/day, compute QPS, Storage & CDN egress bandwidth.</li><li><strong>High-Level Architecture (5 mins):</strong> Draw the block diagram.</li></ol>",
            "conceptual_breakdown": [
                "<strong>Functional Scope:</strong> 1. Upload Video, 2. Stream/Watch Video, 3. Search Video by Title.",
                "<strong>Scale Numbers:</strong> 1B DAU &bull; 5 Billion views/day &bull; 50M uploads/day &bull; 100:1 View-to-Upload Ratio.",
                "<strong>Storage Reality:</strong> 50M videos &times; 100MB avg = 5 PB storage per day &bull; 1.825 Exabytes per year!",
                "<strong>Egress Bandwidth:</strong> 5B views &times; 100MB / 86,400s = 5.78 TB/sec (Must heavily utilize Global CDN edge caching)."
            ],
            "arch_diagram": {
                "title": "Design YouTube: Scoped High-Level Architecture",
                "tiers": [
                    {
                        "label": "User Tier",
                        "nodes": [
                            {"name": "Creator Uploading", "type": "client", "icon": "🎥", "what": "Uploads raw video", "why": "Ingestion", "when": "Write path", "failure": "Chunked resumable upload"},
                            {"name": "Viewer Streaming", "type": "client", "icon": "📱", "what": "Streams HLS video", "why": "Egress", "when": "Read path", "failure": "CDN fallback"}
                        ]
                    },
                    {
                        "label": "Traffic & CDN Tier",
                        "nodes": [
                            {"name": "Global Video CDN", "type": "client", "icon": "🌐", "what": "Cloudflare / Akamai", "why": "Caches 95% of video chunks at edge", "when": "Video playback", "failure": "Origin S3 fetch"},
                            {"name": "API Gateway / LB", "type": "lb", "icon": "⚖️", "what": "NGINX / Envoy", "why": "Routes metadata queries", "when": "Search & view actions", "failure": "Multi-AZ redundancy"}
                        ]
                    },
                    {
                        "label": "Processing Tier",
                        "nodes": [
                            {"name": "Upload Service", "type": "service", "icon": "📤", "what": "Presigned URL generator", "why": "Direct S3 ingestion", "when": "Upload start", "failure": "Auto-scaling"},
                            {"name": "Transcoding Workers", "type": "queue", "icon": "⚙️", "what": "FFmpeg GPU Cluster", "why": "Encodes into 360p, 720p, 1080p, 4K", "when": "Async queue", "failure": "DLQ retry"}
                        ]
                    },
                    {
                        "label": "Data Tier",
                        "nodes": [
                            {"name": "Metadata DB (Postgres)", "type": "db", "icon": "🗄️", "what": "Video title, uploader, views", "why": "Relational metadata", "when": "Queries", "failure": "Read replicas"},
                            {"name": "Raw & Encoded S3 Storage", "type": "storage", "icon": "📦", "what": "Object Storage (5 PB/day)", "why": "Durable blob storage", "when": "Persistent video storage", "failure": "Cross-region replication"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "YouTube Upload & Streaming Separation",
                "steps": [
                    {"step": 1, "description": "1. Ingestion: Creator uploads video directly to S3 Raw Bucket via Presigned URL.", "active_nodes": ["Creator Uploading", "Upload Service", "Raw & Encoded S3 Storage"]},
                    {"step": 2, "description": "2. S3 triggers event to Kafka Queue; Transcoding Worker pool encodes chunks into multiple bitrates.", "active_nodes": ["Transcoding Workers", "Raw & Encoded S3 Storage"]},
                    {"step": 3, "description": "3. Metadata saved in PostgreSQL with Redis caching.", "active_nodes": ["Metadata DB (Postgres)"]},
                    {"step": 4, "description": "4. Viewer requests video: 95% of chunks streamed directly from nearest Edge CDN PoP in 15ms.", "active_nodes": ["Viewer Streaming", "Global Video CDN"]}
                ]
            },
            "tradeoffs": "Encoding videos synchronously during upload would cause 30-minute HTTP timeouts. Using an asynchronous worker pool with message queues decouples upload completion from encoding duration.",
            "comparison_matrix": {
                "title": "YouTube Read vs Write Pipeline Separation",
                "headers": ["Pipeline Dimension", "Upload / Write Path", "Streaming / Read Path"],
                "rows": [
                    ["Traffic Volume", "50M uploads/day (~580 writes/sec)", "5 Billion views/day (~57,870 reads/sec)"],
                    ["Latency Target", "Asynchronous background (minutes acceptable)", "Immediate start (TTFB < 200ms)"],
                    ["Primary Infrastructure", "Upload Service + Kafka + GPU Transcoder Pool", "Global Edge CDN + S3 Origin + Redis Metadata Cache"],
                    ["Data Flow", "Client -> S3 Raw Bucket -> Transcoder -> S3 Chunks", "Client -> Edge CDN -> (Cache Miss: S3 Chunks)"]
                ]
            },
            "failure_scenarios": "Transcoding worker crashes halfway through a 2-hour 4K video encoding: without chunk-level checkpointing, the entire 2-hour job must restart. Solution: Chunk video into 4-second segments and encode chunks independently in parallel.",
            "common_mistakes": [
                {"mistake": "Trying to stream video bytes through the PostgreSQL metadata database", "correction": "Never store binary video files in relational databases. Store metadata (title, URL) in SQL and binary chunks in Object Storage (S3) served via CDN."}
            ],
            "interview_questions": [
                {"question": "Why is Adaptive Bitrate Streaming (HLS / MPEG-DASH) crucial for platforms like YouTube?", "answer": "HLS breaks video into 4-second chunks encoded at multiple resolutions (360p to 4K). The client's video player dynamically monitors live network bandwidth on the fly: if mobile signal drops from 5G to 3G, the player seamlessly requests the next 4-second chunk at 480p instead of buffering."}
            ]
        }
    ]
}

# =========================================================================
# MODULE 3: Capacity Estimation & Back-of-the-Envelope
# =========================================================================
m3 = {
    "module_id": "03",
    "module_title": "Capacity Estimation & Back-of-the-Envelope",
    "description": "Master QPS, peak multipliers, read/write ratios, storage growth, network bandwidth, memory, cache sizing, and units (KB to PB).",
    "topics": [
        {
            "id": "math-units-and-latency-numbers",
            "title": "System Units (KB to PB, QPS) & Numbers Every Engineer Should Know",
            "definition": "The standard engineering arithmetic and latency constants: Powers of 2 ($2^{10} = 1\\text{ KB}$, $2^{20} = 1\\text{ MB}$, $2^{30} = 1\\text{ GB}$, $2^{40} = 1\\text{ TB}$, $2^{50} = 1\\text{ PB}$) and computer hardware latency orders of magnitude.",
            "why_we_need_it": "Without knowing hardware latency orders of magnitude, you might propose reading from a hard disk during a 10ms real-time trading request, causing a 100x latency SLA breach.",
            "real_world_analogy": "A civil engineer knowing the weight limit of steel beams (10,000 lbs) versus wood timber (500 lbs) before specifying skyscraper columns.",
            "how_it_works": "<p>Memorize the 3 core conversion rules and the classic <em>Latency Numbers Every Programmer Should Know</em> (Peter Norvig / Jeff Dean):</p><ul><li>$1\\text{ day} \\approx 86,400\\text{ seconds} \\approx 10^5\\text{ seconds}$ (for fast mental math).</li><li>$1\\text{ Million requests / day} \\approx 12\\text{ QPS}$.</li><li>$100\\text{ Million requests / day} \\approx 1,200\\text{ QPS}$.</li><li>$1\\text{ Billion requests / day} \\approx 12,000\\text{ QPS}$.</li></ul>",
            "conceptual_breakdown": [
                "<strong>L1 Cache Hit:</strong> 0.5 nanoseconds ($0.5\\text{ ns}$).",
                "<strong>L2 Cache Hit:</strong> 7 nanoseconds ($7\\text{ ns}$).",
                "<strong>RAM Access:</strong> 100 nanoseconds ($100\\text{ ns}$) &bull; $1000\\times$ faster than disk!",
                "<strong>NVMe SSD Read:</strong> 150 microseconds ($150\\text{ }\\mu\\text{s}$).",
                "<strong>Cross-Country Network Roundtrip (NYC to SF):</strong> 100 milliseconds ($100\\text{ ms}$).",
                "<strong>Satellite / Cross-Continental Network Roundtrip:</strong> 200 - 500 milliseconds."
            ],
            "arch_diagram": {
                "title": "Hardware Memory & Latency Hierarchy",
                "tiers": [
                    {
                        "label": "Ultra Fast (Nanoseconds)",
                        "nodes": [
                            {"name": "CPU L1 / L2 Cache", "type": "cache", "icon": "⚡", "what": "0.5 ns - 7 ns", "why": "Hardware register speed", "when": "Active CPU registers", "failure": "L1 cache miss goes to RAM"}
                        ]
                    },
                    {
                        "label": "In-Memory Tier",
                        "nodes": [
                            {"name": "System RAM (Redis)", "type": "cache", "icon": "🧠", "what": "100 ns", "why": "1000x faster than disk", "when": "In-memory caching", "failure": "RAM eviction"}
                        ]
                    },
                    {
                        "label": "Solid State Storage",
                        "nodes": [
                            {"name": "NVMe SSD Read", "type": "db", "icon": "💾", "what": "150 µs", "why": "Persistent high-speed I/O", "when": "Database disk reads", "failure": "Disk wear"}
                        ]
                    },
                    {
                        "label": "Network Boundary",
                        "nodes": [
                            {"name": "Cross-Continent Network", "type": "client", "icon": "🌐", "what": "100 ms (100,000,000 ns!)", "why": "Speed of light in fiber optic cable", "when": "Remote API fetch", "failure": "Network partition"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "Latency Speed Comparison Scale",
                "steps": [
                    {"step": 1, "description": "L1 Cache hit completes in 0.5ns (Equivalent to 1 heart beat).", "active_nodes": ["CPU L1 / L2 Cache"]},
                    {"step": 2, "description": "Main RAM access completes in 100ns (Equivalent to walking across the room).", "active_nodes": ["System RAM (Redis)"]},
                    {"step": 3, "description": "SSD Read takes 150µs (Equivalent to walking to the local grocery store).", "active_nodes": ["NVMe SSD Read"]},
                    {"step": 4, "description": "Cross-Country Network roundtrip takes 100ms (Equivalent to walking across the entire globe!).", "active_nodes": ["Cross-Continent Network"]}
                ]
            },
            "tradeoffs": "RAM is $1000\\times$ faster than SSD but costs $10\\times$ more per gigabyte and is volatile (loses data on power loss). Solid system design caches hot data in RAM while keeping durable source-of-truth on SSD.",
            "comparison_matrix": {
                "title": "Data Storage Hierarchy & Latencies",
                "headers": ["Storage Level", "Latency", "Cost per TB", "Volatility"],
                "rows": [
                    ["CPU Registers / L1", "0.5 ns - 1 ns", "Extreme ($$$$)", "Volatile"],
                    ["RAM (DRAM)", "100 ns", "~$3,000 / TB", "Volatile"],
                    ["NVMe Flash SSD", "100 - 200 µs", "~$100 / TB", "Non-Volatile (Durable)"],
                    ["Hard Disk Drive (HDD)", "5 - 10 ms", "~$20 / TB", "Non-Volatile (Sequential only)"],
                    ["Network Roundtrip (Same DC)", "500 µs", "Network bandwidth cost", "N/A"]
                ]
            },
            "failure_scenarios": "Relying on disk seek operations for high-throughput random reads: HDDs can only achieve ~150 IOPS (Input/Output Operations per second) due to physical arm movement. Modern NVMe SSDs deliver 500,000+ IOPS.",
            "common_mistakes": [
                {"mistake": "Over-calculating with exact calculator precision (e.g. '86,400 divided by 17.382 equals 4970.658')", "correction": "System design capacity estimation is an order-of-magnitude approximation (Back-of-the-envelope). Round $86,400 \\approx 100,000$ to do fast, clean mental math."}
            ],
            "interview_questions": [
                {"question": "Why is cross-data-center replication latency bounded by the speed of light in optical fiber?", "answer": "Light travels through fiber glass at ~200,000 km/s (roughly 2/3 the speed of light in vacuum). A roundtrip between New York and London (~11,000 km total) has a theoretical physical minimum latency of ~55ms, meaning no software algorithm can ever make synchronous cross-Atlantic commits in under 60ms."}
            ]
        },
        {
            "id": "traffic-and-qps-estimation",
            "title": "DAU/MAU to Average & Peak QPS Estimation",
            "definition": "The standard methodology for calculating Average Queries Per Second (QPS), Peak Traffic Multipliers, and Read/Write QPS splits from Daily Active Users (DAU).",
            "why_we_need_it": "Determines how many server instances, database connections, and load balancer clusters are required to handle peak holiday or evening burst traffic without crashing.",
            "real_world_analogy": "A highway department designing toll booths: you cannot build booths for the 3:00 AM average traffic; you must size them for the 8:30 AM rush-hour peak multiplier (3x - 5x average).",
            "how_it_works": "<p>Step-by-Step QPS Formula:</p><ol><li>$\\text{Total Daily Requests} = \\text{DAU} \\times \\text{Requests per User per Day}$.</li><li>$\\text{Average QPS} = \\frac{\\text{Total Daily Requests}}{86,400\\text{ seconds}}$.</li><li>$\\text{Peak QPS} = \\text{Average QPS} \\times \\text{Peak Multiplier (typically 2x to 5x)}$.</li><li>Partition into $\\text{Read QPS}$ and $\\text{Write QPS}$ based on the system's Read-to-Write ratio.</li></ol>",
            "conceptual_breakdown": [
                "<strong>Example: Twitter-Scale:</strong>",
                "$\\text{DAU} = 300\\text{ Million}$.",
                "Avg views per user = 50 tweets/day $\\implies 300\\text{M} \\times 50 = 15\\text{ Billion reads/day}$.",
                "Avg posts per user = 2 tweets/day $\\implies 300\\text{M} \\times 2 = 600\\text{ Million writes/day}$.",
                "$\\text{Average Read QPS} = \\frac{15\\times 10^9}{86,400} \\approx 173,600\\text{ Read QPS}$.",
                "$\\text{Peak Read QPS (2x)} = 173,600 \\times 2 \\approx 350,000\\text{ Peak Read QPS}$.",
                "$\\text{Average Write QPS} = \\frac{600\\times 10^6}{86,400} \\approx 7,000\\text{ Write QPS}$ (Peak $\\approx 14,000\\text{ Write QPS}$)."
            ],
            "arch_diagram": {
                "title": "QPS Sizing and Server Fleet Capacity",
                "tiers": [
                    {
                        "label": "Peak Ingress",
                        "nodes": [
                            {"name": "350,000 Peak Read QPS", "type": "client", "icon": "⚡", "what": "350k concurrent requests/sec", "why": "Incoming peak load", "when": "Rush hour / Breaking news", "failure": "Rate limiter sheds excess load"}
                        ]
                    },
                    {
                        "label": "Stateless Fleet",
                        "nodes": [
                            {"name": "350 Web App Servers (1k QPS each)", "type": "service", "icon": "🖥️", "what": "Auto-scaling EC2 / K8s Pods", "why": "Each modern 8-core server handles ~1,000 QPS", "when": "Stateless compute", "failure": "Auto-scaling group provisions +50 servers"}
                        ]
                    },
                    {
                        "label": "Storage Ingress",
                        "nodes": [
                            {"name": "14,000 Write QPS", "type": "db", "icon": "💾", "what": "14k database inserts/sec", "why": "Exceeds single Postgres primary capacity", "when": "Write path", "failure": "Partitioned into 10 Database Shards"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "Peak QPS Traffic Absorption",
                "steps": [
                    {"step": 1, "description": "World Cup Final triggers sudden 350,000 QPS burst on Twitter timeline.", "active_nodes": ["350,000 Peak Read QPS"]},
                    {"step": 2, "description": "Load Balancer spreads 350,000 QPS evenly across 350 web application servers (1,000 QPS per instance).", "active_nodes": ["350,000 Peak Read QPS", "350 Web App Servers (1k QPS each)"]},
                    {"step": 3, "description": "14,000 Write QPS routed to Kafka Queue to prevent database write deadlocks.", "active_nodes": ["14,000 Write QPS"]}
                ]
            },
            "tradeoffs": "Over-provisioning servers for 10x peak traffic 24/7 wastes millions of dollars. Using Cloud Horizontal Pod Autoscaling (HPA) automatically provisions nodes when CPU > 70% and scales down at night.",
            "comparison_matrix": {
                "title": "QPS Scale Tiers and Typical Hardware Requirements",
                "headers": ["QPS Range", "System Archetype", "App Tier Hardware", "Database Strategy"],
                "rows": [
                    ["1 - 500 QPS", "Small Startup", "1 - 2 EC2 instances", "Single PostgreSQL RDS instance"],
                    ["500 - 5,000 QPS", "Medium Enterprise", "5 - 10 instances behind ALB", "Primary + 2 Read Replicas + Redis Cache"],
                    ["5,000 - 50,000 QPS", "High Scale (Uber, Airbnb)", "50 - 100 microservice pods", "Sharded Database + Distributed Redis Cluster + Kafka"],
                    ["50,000 - 500,000+ QPS", "Hyper Scale (Twitter, Netflix)", "500+ pods across multiple AZs", "NoSQL (Cassandra/DynamoDB) + Global Edge CDNs"]
                ]
            },
            "failure_scenarios": "Calculating only average QPS and ignoring peak traffic: during breaking news or Cyber Monday sales, traffic spikes 4x, overwhelming connection pools and crashing the entire platform.",
            "common_mistakes": [
                {"mistake": "Assuming a single database primary can handle 50,000 write queries per second", "correction": "A single PostgreSQL/MySQL primary typically caps at 5,000 - 10,000 write QPS depending on disk IOPS. Beyond that, you MUST shard the database or write to Kafka queues asynchronously."}
            ],
            "interview_questions": [
                {"question": "How do you calculate how many server instances are needed given a peak of 100,000 QPS?", "answer": "Assuming a typical production web server (e.g. Go, Java Netty, or C++ Crow) handles ~1,000 requests per second safely at 60% CPU utilization, you need: $\\frac{100,000\\text{ QPS}}{1,000\\text{ QPS/server}} = 100\\text{ server instances}$. Add 20% buffer for redundancy ($120\\text{ instances}$)."}
            ]
        },
        {
            "id": "storage-and-bandwidth-estimation",
            "title": "Read/Write Ratios, Storage Growth & Ingress/Egress Bandwidth",
            "definition": "Formulas for calculating daily storage ingestion, 5-year capacity growth with replication overhead, and network ingress/egress bandwidth in Gigabits per second (Gbps).",
            "why_we_need_it": "Ensures you budget for sufficient disk capacity, avoid cloud network egress bill shocks, and know when to compress payloads or adopt object storage tiering.",
            "real_world_analogy": "A water treatment plant: estimating both daily water inflow pipe diameter (ingress bandwidth) and water reservoir tank volume for 5-year drought reserves (storage capacity).",
            "how_it_works": "<p>Storage & Bandwidth Formulas:</p><ol><li>$\\text{Daily Storage} = \\text{Daily Writes} \\times \\text{Average Payload Size}$.</li><li>$\\text{5-Year Storage} = \\text{Daily Storage} \\times 365\\text{ days} \\times 5\\text{ years} \\times 3\\text{ (Replication Factor)}$.</li><li>$\\text{Ingress Bandwidth} = \\text{Write QPS} \\times \\text{Average Write Size} \\times 8\\text{ (bits/byte)}$.</li><li>$\\text{Egress Bandwidth} = \\text{Read QPS} \\times \\text{Average Read Size} \\times 8\\text{ (bits/byte)}$.</li></ol>",
            "conceptual_breakdown": [
                "<strong>Example: Instagram Photo Storage:</strong>",
                "20 Million photo uploads / day &bull; 200 KB average compressed JPEG size.",
                "$\\text{Daily Storage} = 20\\text{M} \\times 200\\text{ KB} = 4\\text{ Terabytes / day}$.",
                "$\\text{1-Year Storage} = 4\\text{ TB} \\times 365 = 1.46\\text{ Petabytes / year}$.",
                "$\\text{5-Year Storage with 3x Replication} = 1.46\\text{ PB} \\times 5 \\times 3 \\approx 21.9\\text{ Petabytes}$.",
                "$\\text{Egress Bandwidth (200M photo views/day)} = \\frac{200\\times 10^6 \\times 200\\text{ KB}}{86,400} \\approx 463\\text{ MB/sec} = 3.7\\text{ Gbps}$."
            ],
            "arch_diagram": {
                "title": "Storage Growth & Bandwidth Pipeline",
                "tiers": [
                    {
                        "label": "Network Ingress/Egress",
                        "nodes": [
                            {"name": "Egress: 3.7 Gbps", "type": "client", "icon": "📡", "what": "Outgoing photo stream", "why": "Delivers photos to users", "when": "User browsing", "failure": "CDN edge caching reduces origin egress by 90%"}
                        ]
                    },
                    {
                        "label": "Storage Tiering",
                        "nodes": [
                            {"name": "Hot Storage (S3 Standard)", "type": "storage", "icon": "🔥", "what": "First 30 days photos (~120 TB)", "why": "Frequent access", "when": "New posts", "failure": "Instant NVMe retrieval"},
                            {"name": "Cold Storage (S3 Glacier)", "type": "db", "icon": "🧊", "what": "Past 5 years photos (~21 PB)", "why": "90% cheaper storage cost", "when": "Old archives", "failure": "Lifecycle transition policy"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "Storage Tiering Lifecycle Flow",
                "steps": [
                    {"step": 1, "description": "New photo uploaded: Written to S3 Standard Hot Tier (4 TB ingested daily).", "active_nodes": ["Hot Storage (S3 Standard)"]},
                    {"step": 2, "description": "First 30 days: 95% of reads served from CDN Edge & Hot Tier.", "active_nodes": ["Network Ingress/Egress", "Hot Storage (S3 Standard)"]},
                    {"step": 3, "description": "After 90 days: Automated S3 Lifecycle Rule moves photo to S3 Glacier Deep Archive, slashing storage bills by 85%.", "active_nodes": ["Cold Storage (S3 Glacier)"]}
                ]
            },
            "tradeoffs": "Storing 22 Petabytes in standard SSD storage costs ~$50,000/month. Using automated S3 Lifecycle policies to transition cold photos older than 60 days to Amazon S3 Glacier cuts costs down to ~$8,000/month.",
            "comparison_matrix": {
                "title": "Storage Pricing & Access Latency Tiers (AWS Example)",
                "headers": ["Storage Class", "Cost per GB/mo", "Retrieval Latency", "Durability", "Best For"],
                "rows": [
                    ["S3 Standard", "$0.023", "Milliseconds", "99.999999999% (11 9s)", "Active photos & feeds (First 30 days)"],
                    ["S3 Infrequent Access (IA)", "$0.0125", "Milliseconds", "11 Nines", "Photos accessed 1-2 times a month"],
                    ["S3 Glacier Flexible", "$0.0036", "Minutes to Hours", "11 Nines", "Archives older than 90 days"],
                    ["S3 Glacier Deep Archive", "$0.00099", "12 Hours", "11 Nines", "Long-term compliance / multi-year backups"]
                ]
            },
            "failure_scenarios": "Forgetting replication overhead: calculating 1 PB raw storage, but forgetting that 3x replication (Primary + 2 Standbys) requires purchasing 3 PB of physical disk space.",
            "common_mistakes": [
                {"mistake": "Confusing Megabytes per second (MB/s) with Megabits per second (Mbps)", "correction": "Remember that 1 Byte = 8 bits ($1\\text{ MB/s} = 8\\text{ Mbps}$). Network bandwidth is quoted in bits (Gbps); storage is quoted in Bytes (GB/TB)."}
            ],
            "interview_questions": [
                {"question": "How do you calculate 5-year storage requirements for a chat app handling 100M messages per day?", "answer": "1. Average message = 100 bytes text + 100 bytes metadata = 200 bytes. 2. Daily text = $100\\text{M} \\times 200\\text{ bytes} = 20\\text{ GB/day}$. 3. Add media: if 10% contain a 100KB thumbnail = $10\\text{M} \\times 100\\text{ KB} = 1\\text{ TB/day}$. 4. Total daily = $\\sim 1.02\\text{ TB/day}$. 5. 5-Year storage with 3x replication = $1.02\\text{ TB} \\times 365 \\times 5 \\times 3 \\approx 5.58\\text{ Petabytes}$."}
            ]
        },
        {
            "id": "memory-and-cache-sizing",
            "title": "Memory, 80/20 Rule & Distributed Cache Sizing",
            "definition": "The Pareto Principle (80/20 rule) applied to systems design: 20% of content generates 80% of read traffic. Sizing in-memory caches (Redis) to hold this hot 20% guarantees an 80%+ cache hit ratio.",
            "why_we_need_it": "RAM is expensive ($3,000/TB vs $100/TB for SSD). Sizing cache appropriately avoids overpaying for RAM while protecting the database from read overload.",
            "real_world_analogy": "A library front desk: keeping the top 20 bestsellers on the counter shelf for instant pickup, rather than walking into the 5-story basement archive for every customer.",
            "how_it_works": "<p>Cache Sizing Formula:</p><ol><li>Calculate total daily read request volume in Bytes: $\\text{Daily Volume} = \\text{Daily Read Requests} \\times \\text{Average Payload Size}$.</li><li>Apply the 80/20 Pareto rule: $\\text{Cache Memory (RAM)} = \\text{Daily Volume} \\times 0.20$.</li><li>Add 25% overhead for Redis metadata & pointer memory structures: $\\text{Total RAM} = \\text{Cache Memory} \\times 1.25$.</li></ol>",
            "conceptual_breakdown": [
                "<strong>Example: E-Commerce Product Catalog:</strong>",
                "500 Million product page views per day &bull; 50 KB product JSON payload.",
                "$\\text{Daily Read Volume} = 500\\text{M} \\times 50\\text{ KB} = 25\\text{ Terabytes / day}$.",
                "$\\text{20% Hot Working Set} = 25\\text{ TB} \\times 0.20 = 5\\text{ TB RAM}$.",
                "With 25% Redis metadata overhead: $5\\text{ TB} \\times 1.25 = 6.25\\text{ TB RAM}$.",
                "Sizing the cluster: A fleet of 50 Redis nodes with 128 GB RAM each ($50 \\times 128\\text{ GB} = 6.4\\text{ TB}$) easily caches all hot products."
            ],
            "arch_diagram": {
                "title": "80/20 Distributed Cache Cluster Sizing",
                "tiers": [
                    {
                        "label": "Incoming Reads",
                        "nodes": [
                            {"name": "500M Daily Product Reads", "type": "client", "icon": "🛍️", "what": "500M page requests", "why": "High read traffic", "when": "E-Commerce browsing", "failure": "Fast cache lookup"}
                        ]
                    },
                    {
                        "label": "In-Memory Cache (80% Traffic)",
                        "nodes": [
                            {"name": "6.25 TB Redis Cluster (50 Nodes)", "type": "cache", "icon": "⚡", "what": "50 x 128GB RAM Nodes", "why": "Holds top 20% hot products (80% hits)", "when": "Cache HIT (Sub-millisecond)", "failure": "Redis Sentinel auto-failover"}
                        ]
                    },
                    {
                        "label": "Database Tier (20% Traffic)",
                        "nodes": [
                            {"name": "PostgreSQL Primary + Replicas", "type": "db", "icon": "🗄️", "what": "Durable product catalog", "why": "Handles only 20% cache misses", "when": "Cache MISS (Cold products)", "failure": "Connection pool guard"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "Pareto 80/20 Cache Hit vs Miss Traversal",
                "steps": [
                    {"step": 1, "description": "User requests trending iPhone 15 page. Query hits Redis Cache. 80% HIT probability!", "active_nodes": ["500M Daily Product Reads", "6.25 TB Redis Cluster (50 Nodes)"]},
                    {"step": 2, "description": "Redis returns product JSON in 0.8ms. Database receives zero traffic load.", "active_nodes": ["6.25 TB Redis Cluster (50 Nodes)"]},
                    {"step": 3, "description": "User requests obscure 2012 cable adapter (Cold item). Cache MISS.", "active_nodes": ["500M Daily Product Reads", "PostgreSQL Primary + Replicas"]},
                    {"step": 4, "description": "Service queries PostgreSQL, returns item, and asynchronously populates Redis with 24h TTL.", "active_nodes": ["PostgreSQL Primary + Replicas", "6.25 TB Redis Cluster (50 Nodes)"]}
                ]
            },
            "tradeoffs": "Caching 100% of all data in RAM costs a fortune with diminishing returns ($25\\text{ TB RAM} \\approx \\$75,000/\\text{month}$). Caching the top 20% costs $\\$15,000/\\text{month}$ while absorbing 80%+ of total traffic.",
            "comparison_matrix": {
                "title": "Cache Eviction Policies Comparison",
                "headers": ["Policy", "Eviction Rule", "Best Suited For", "Weakness"],
                "rows": [
                    ["LRU (Least Recently Used)", "Evicts item unused for longest time", "General web caching, feeds, product pages", "Polluted by single-pass batch scans"],
                    ["LFU (Least Frequently Used)", "Evicts item with lowest request count", "Consistent hot assets (e.g. site logo, celebrity profiles)", "Historical items stay cached forever"],
                    ["FIFO (First In First Out)", "Evicts oldest inserted item", "Simple streaming buffers", "May evict frequently accessed hot keys"],
                    ["Random Eviction", "Picks random victim node", "Uniform access distributions", "Sub-optimal hit ratio"]
                ]
            },
            "failure_scenarios": "Redis out-of-memory crash (OOM): if you do not configure an explicit maxmemory eviction policy (`maxmemory-policy allkeys-lru`), Redis rejects all new write requests when RAM is full (`OOM command not allowed`).",
            "common_mistakes": [
                {"mistake": "Calculating cache size based only on raw string payload without accounting for Redis object overhead", "correction": "Always add 20% - 30% memory buffer for Redis internal hash table pointers, jemalloc memory fragmentation, and key metadata."}
            ],
            "interview_questions": [
                {"question": "How do you size a distributed cache for a news website with 50M daily article reads where each article is 100 KB?", "answer": "1. Daily read volume = $50\\text{M} \\times 100\\text{ KB} = 5\\text{ TB}$. 2. 80/20 Rule: Hot working set = $20\\% \\times 5\\text{ TB} = 1\\text{ TB RAM}$. 3. Add 25% Redis pointer overhead = $1.25\\text{ TB RAM}$. 4. Sizing: Deploy 10 Redis nodes with 128 GB RAM each (Total 1.28 TB RAM)."}
            ]
        },
        {
            "id": "interactive-capacity-calculator",
            "title": "Interactive Back-of-the-Envelope Capacity Calculator Tool",
            "definition": "A live interactive browser-based calculator allowing learners to adjust DAU, read/write ratios, payload size, and peak multipliers to dynamically compute system throughput and storage scale.",
            "why_we_need_it": "Builds intuitive muscle memory for mental arithmetic during high-pressure system design interviews.",
            "real_world_analogy": "A flight simulator for system architects: tweaking passenger load factors and seeing fuel consumption numbers update in real time.",
            "how_it_works": "<p>Adjust the sliders below to calculate QPS, Bandwidth, 5-Year Storage, and RAM Cache requirements live using real-time JavaScript formula engines.</p>",
            "capacity_calculator": True,
            "conceptual_breakdown": [
                "<strong>Real-time Reactive Math:</strong> Calculates Average QPS, Peak QPS ($2.5\\times$), Daily Ingestion, 5-Year Storage ($3\\times$ replicas), and 80/20 RAM sizing instantly.",
                "<strong>Unit Normalization:</strong> Automatically converts raw bytes into KB, MB, GB, TB, and PB based on magnitude.",
                "<strong>Interview Cheat Sheet:</strong> Use these exact formulas in FAANG whiteboard interviews."
            ],
            "tradeoffs": "Capacity estimation is not about exact financial auditing; it is about choosing the right architectural tier (e.g. knowing whether you need 1 Postgres DB or a 50-node Cassandra cluster).",
            "comparison_matrix": {
                "title": "Quick Reference Scale Table",
                "headers": ["DAU Scale", "Average QPS (10 req/user)", "Peak QPS (2.5x)", "Daily Storage (10KB payload)", "5-Yr 3x Replica Storage"],
                "rows": [
                    ["1 Million", "116 QPS", "290 QPS", "10 GB / day", "54.7 TB"],
                    ["10 Million", "1,157 QPS", "2,893 QPS", "100 GB / day", "547.5 TB"],
                    ["50 Million", "5,787 QPS", "14,467 QPS", "500 GB / day", "2.73 PB"],
                    ["200 Million", "23,148 QPS", "57,870 QPS", "2 TB / day", "10.95 PB"],
                    ["1 Billion", "115,740 QPS", "289,350 QPS", "10 TB / day", "54.75 PB"]
                ]
            },
            "failure_scenarios": "Designing a single server architecture for a problem whose math reveals 50,000 Write QPS and 10 PB storage: an instant failure in any senior engineering review.",
            "common_mistakes": [
                {"mistake": "Skipping capacity estimation in an interview and jumping directly into drawing microservice boxes", "correction": "Always spend 3-4 minutes on estimation. The numbers dictate whether you need simple SQL replicas or multi-region NoSQL sharding."}
            ],
            "interview_questions": [
                {"question": "Why is the capacity estimation step so critical for justifying architectural decisions to interviewers?", "answer": "Because architecture without numbers is pure speculation. When you calculate 30,000 Write QPS, you have mathematical proof for why you chose a NoSQL database or message queue rather than a single SQL database."}
            ]
        }
    ]
}

# =========================================================================
# MODULE 4: Internet & Networking Foundations
# =========================================================================
m4 = {
    "module_id": "04",
    "module_title": "Internet & Networking Foundations",
    "description": "Everything needed for HLD: IP, MAC, DNS resolution, TCP vs UDP, TLS/HTTPS, NAT, Firewalls, Proxies, WebSockets, and SSE.",
    "topics": [
        {
            "id": "dns-resolution-lifecycle",
            "title": "DNS Lifecycle: Browser to Root, TLD & Authoritative Nameservers",
            "definition": "Domain Name System (DNS) is the decentralized global hierarchical phonebook of the Internet, translating human-readable hostnames (`api.netflix.com`) into routable IP addresses (`198.51.100.42`).",
            "why_we_need_it": "Routers communicate exclusively via binary IP addresses. Without DNS, users would have to memorize 32-bit IPv4 numbers for every website. DNS also enables GeoDNS routing, load balancing, and zero-downtime failover.",
            "real_world_analogy": "Looking up a contact in your phone: you tap 'Alice' (Hostname) and your phone dials '+1-555-0199' (IP address).",
            "how_it_works": "<p>DNS resolution executes through an 8-step iterative lookup hierarchy:</p><ol><li><strong>Browser Cache:</strong> Checks local browser DNS cache (chrome://net-internals/#dns).</li><li><strong>OS Cache & Hosts File:</strong> Checks local operating system DNS resolver cache.</li><li><strong>Recursive Resolver (ISP / 8.8.8.8):</strong> If cache misses, queries the Recursive DNS Resolver.</li><li><strong>Root Nameserver (`.`):</strong> Directs query to the `.com` Top-Level Domain (TLD) server.</li><li><strong>TLD Nameserver (`.com`):</strong> Directs query to the authoritative nameserver for `netflix.com`.</li><li><strong>Authoritative Nameserver (Route 53):</strong> Returns the exact `A` record (IPv4) or `AAAA` record (IPv6) with a TTL (Time-To-Live).</li><li><strong>Caching & Connection:</strong> Recursive resolver caches IP and returns it to browser to initiate TCP handshake.</li></ol>",
            "conceptual_breakdown": [
                "<strong>A Record:</strong> Maps hostname to IPv4 address (`api.site.com -> 93.184.216.34`).",
                "<strong>AAAA Record:</strong> Maps hostname to 128-bit IPv6 address.",
                "<strong>CNAME (Canonical Name):</strong> Maps alias hostname to another hostname (`www.site.com -> site.com`).",
                "<strong>TTL (Time-To-Live):</strong> Expiration time (in seconds) that DNS records can be cached by resolvers.",
                "<strong>Anycast DNS:</strong> Same IP address announced globally from 300+ edge locations; BGP routes query to nearest physical server in < 10ms."
            ],
            "arch_diagram": {
                "title": "8-Step Recursive DNS Resolution Architecture",
                "tiers": [
                    {
                        "label": "Client Tier",
                        "nodes": [
                            {"name": "Client Browser", "type": "client", "icon": "💻", "what": "Queries api.netflix.com", "why": "Initiates web request", "when": "Initial visit", "failure": "Local cache fallback"}
                        ]
                    },
                    {
                        "label": "Resolver Tier",
                        "nodes": [
                            {"name": "Recursive Resolver (8.8.8.8)", "type": "service", "icon": "🔄", "what": "ISP / Cloudflare 1.1.1.1", "why": "Performs iterative queries on behalf of client", "when": "Cache miss", "failure": "Fallback secondary DNS resolver"}
                        ]
                    },
                    {
                        "label": "Hierarchical DNS Authority Tier",
                        "nodes": [
                            {"name": "Root Server (.)", "type": "lb", "icon": "🌍", "what": "13 Global Root Server Clusters", "why": "Points to .com TLD", "when": "Step 1 of hierarchy", "failure": "Anycast redundancy"},
                            {"name": "TLD Server (.com)", "type": "lb", "icon": "🏢", "what": "Verisign .com Registry", "why": "Points to netflix.com NS", "when": "Step 2 of hierarchy", "failure": "Anycast redundancy"},
                            {"name": "Authoritative NS (Route 53)", "type": "db", "icon": "📜", "what": "AWS Route 53 Nameserver", "why": "Holds official A Record IP", "when": "Final authoritative answer", "failure": "Multi-provider DNS redundancy"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "Iterative DNS Lookup Cycle",
                "steps": [
                    {"step": 1, "description": "Client asks Recursive Resolver for IP of 'api.netflix.com'.", "active_nodes": ["Client Browser", "Recursive Resolver (8.8.8.8)"]},
                    {"step": 2, "description": "Recursive Resolver asks Root Server (.) -> Root returns .com TLD server address.", "active_nodes": ["Recursive Resolver (8.8.8.8)", "Root Server (.)"]},
                    {"step": 3, "description": "Resolver asks .com TLD Server -> TLD returns Authoritative Route 53 server.", "active_nodes": ["Recursive Resolver (8.8.8.8)", "TLD Server (.com)"]},
                    {"step": 4, "description": "Resolver asks Authoritative Route 53 -> Returns IP: 198.51.100.42 (TTL: 300s).", "active_nodes": ["Recursive Resolver (8.8.8.8)", "Authoritative NS (Route 53)"]},
                    {"step": 5, "description": "Resolver returns IP to Browser. Browser caches record and initiates TCP handshake.", "active_nodes": ["Recursive Resolver (8.8.8.8)", "Client Browser"]}
                ]
            },
            "tradeoffs": "Setting a long DNS TTL (e.g. 24 hours) reduces DNS query traffic and latency, but makes emergency IP failovers take up to 24 hours to propagate worldwide. Production systems set TTL to 60 - 300 seconds for agile routing.",
            "comparison_matrix": {
                "title": "DNS Record Types and Routing Strategies",
                "headers": ["DNS Strategy", "How It Works", "Primary Use Case", "Trade-off"],
                "rows": [
                    ["Standard A / AAAA Record", "Static mapping from name to IP", "Basic websites", "No dynamic failover"],
                    ["GeoDNS Routing", "Resolves to IP nearest to user's geographic country", "Multi-region latency optimization", "Can route inaccurately if resolver is far from client"],
                    ["Weighted Round-Robin DNS", "Rotates multiple IPs with percentage weights", "Canary deployments & load distribution", "Client DNS caching causes uneven traffic splits"],
                    ["DNS Health-Check Failover", "Monitors IP health; removes dead IP from DNS response", "Disaster recovery", "Propagates only as fast as TTL expiration"]
                ]
            },
            "failure_scenarios": "DNS DDoS attack: an attacker floods authoritative nameservers with garbage queries (e.g. 2016 Dyn Cyberattack). If DNS goes down, the entire website is unreachable even if all backend servers are 100% healthy. Mitigation: Use redundant multi-provider DNS (AWS Route 53 + Cloudflare secondary).",
            "common_mistakes": [
                {"mistake": "Relying on DNS alone for fine-grained real-time load balancing", "correction": "DNS caching in ISPs and operating systems ignores rapid changes. Use DNS only for coarse geographic routing to regional Load Balancers; let L4/L7 Load Balancers handle real-time server balancing."}
            ],
            "interview_questions": [
                {"question": "What happens when you type 'google.com' into a browser and press Enter?", "answer": "1. DNS lookup resolves hostname to IP. 2. TCP 3-way handshake establishes connection on port 443. 3. TLS 1.3 handshake negotiates cipher keys. 4. HTTP GET request sent. 5. Load Balancer routes to web server. 6. Server renders response. 7. Browser parses HTML/CSS/JS and renders DOM."}
            ]
        },
        {
            "id": "tcp-vs-udp-tls-handshake",
            "title": "TCP 3-Way Handshake, UDP, and TLS 1.3 Encryption Handshake",
            "definition": "The core transport and security protocols of the Internet: TCP (Transmission Control Protocol: connection-oriented, reliable, ordered, byte-stream with flow/congestion control), UDP (User Datagram Protocol: connectionless, lightweight, unordered), and TLS 1.3 (Transport Layer Security: cryptographic encryption).",
            "why_we_need_it": "Choosing between TCP and UDP dictates whether your system prioritizes 100% data reliability (e.g. banking, file transfer) or absolute minimal latency (e.g. video conferencing, online gaming, DNS).",
            "real_world_analogy": "TCP is a certified registered letter requiring signature confirmation; UDP is a postcard dropped in a mailbox; TLS is sending the message written in an unbreakable secret military cipher inside a locked titanium briefcase.",
            "how_it_works": "<p><strong>TCP 3-Way Handshake:</strong></p><ol><li><strong>SYN:</strong> Client sends Synchronize packet with random initial sequence number ($ISN_c$).</li><li><strong>SYN-ACK:</strong> Server acknowledges ($ACK = ISN_c + 1$) and sends server sequence number ($ISN_s$).</li><li><strong>ACK:</strong> Client acknowledges ($ACK = ISN_s + 1$). Connection established!</li></ol><p><strong>TLS 1.3 Handshake (1-RTT):</strong> Client sends supported ciphers + Diffie-Hellman key share in <code>ClientHello</code>; Server responds with selected cipher + server key share in <code>ServerHello</code>; Encrypted session key derived immediately in 1 roundtrip!</p>",
            "conceptual_breakdown": [
                "<strong>TCP Guarantees:</strong> In-order delivery, packet retransmission on drop, flow control (sliding window), congestion control (AIMD / BBR).",
                "<strong>UDP Advantages:</strong> Zero connection overhead (0-RTT), no head-of-line blocking, lightweight 8-byte header (vs 20-60B for TCP).",
                "<strong>Head-of-Line (HoL) Blocking:</strong> If 1 packet is lost in TCP, all subsequent packets must wait in queue until the lost packet is retransmitted. HTTP/3 (QUIC) runs over UDP to eliminate HoL blocking!",
                "<strong>TLS 1.3 vs 1.2:</strong> TLS 1.3 reduced handshake latency from 2-RTT to 1-RTT (and supports 0-RTT session resumption)."
            ],
            "arch_diagram": {
                "title": "TCP 3-Way Handshake & TLS 1.3 Negotiation",
                "tiers": [
                    {
                        "label": "Client Initiation",
                        "nodes": [
                            {"name": "Client", "type": "client", "icon": "💻", "what": "Initiates connection", "why": "Wants secure data exchange", "when": "New connection", "failure": "SYN timeout retry"}
                        ]
                    },
                    {
                        "label": "Transport Layer (TCP Handshake)",
                        "nodes": [
                            {"name": "1. SYN (seq=X) ->", "type": "lb", "icon": "📤", "what": "Client sync", "why": "Starts handshake", "when": "Step 1", "failure": "Drop on network partition"},
                            {"name": "2. <- SYN-ACK (ack=X+1, seq=Y)", "type": "service", "icon": "📥", "what": "Server sync-ack", "why": "Confirms readiness", "when": "Step 2", "failure": "SYN Flood attack"},
                            {"name": "3. ACK (ack=Y+1) ->", "type": "lb", "icon": "🤝", "what": "Client ack", "why": "Connection ESTABLISHED", "when": "Step 3", "failure": "RST packet reset"}
                        ]
                    },
                    {
                        "label": "Security Layer (TLS 1.3 Handshake)",
                        "nodes": [
                            {"name": "ClientHello (Keyshare) ->", "type": "cache", "icon": "🔑", "what": "Diffie-Hellman Key Exchange", "why": "Negotiates encryption in 1 RTT", "when": "TLS Step", "failure": "Cipher mismatch"},
                            {"name": "<- ServerHello (Finished)", "type": "db", "icon": "🔒", "what": "Encrypted Session Active", "why": "Zero eavesdropping / tampering", "when": "Secure pipeline", "failure": "Certificate expired"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "Combined TCP + TLS 1.3 Handshake Flow",
                "steps": [
                    {"step": 1, "description": "Step 1: Client sends TCP SYN packet to Server Port 443.", "active_nodes": ["Client", "1. SYN (seq=X) ->"]},
                    {"step": 2, "description": "Step 2: Server responds with TCP SYN-ACK.", "active_nodes": ["2. <- SYN-ACK (ack=X+1, seq=Y)"]},
                    {"step": 3, "description": "Step 3: Client sends TCP ACK + TLS 1.3 ClientHello containing Diffie-Hellman public key share.", "active_nodes": ["3. ACK (ack=Y+1) ->", "ClientHello (Keyshare) ->"]},
                    {"step": 4, "description": "Step 4: Server replies with ServerHello. Symmetric AES-GCM session key is generated. Encrypted data stream begins!", "active_nodes": ["<- ServerHello (Finished)"]}
                ]
            },
            "tradeoffs": "TCP guarantees 100% reliability but suffers from Head-of-Line blocking and handshake latency. UDP provides raw wire speed with zero handshake overhead but leaves packet reordering and loss handling entirely to application code.",
            "comparison_matrix": {
                "title": "TCP vs UDP Comprehensive Comparison",
                "headers": ["Dimension", "TCP (Transmission Control Protocol)", "UDP (User Datagram Protocol)"],
                "rows": [
                    ["Connection Model", "Connection-oriented (3-way handshake required)", "Connectionless (Send datagram directly)"],
                    ["Reliability", "Guaranteed (Retransmits dropped packets)", "Unreliable (Packets may be dropped silently)"],
                    ["Ordering", "Strict in-order sequence numbers", "No ordering guarantees (Packets may arrive out of order)"],
                    ["Speed / Overhead", "Heavier (20-60 Byte header, ACK overhead)", "Ultra-fast (8 Byte header, zero ACK overhead)"],
                    ["Flow / Congestion Control", "Yes (Sliding window, Slow Start, Congestion Avoidance)", "None (Transmits at maximum hardware rate)"],
                    ["Typical Protocols", "HTTP/1.1, HTTP/2, HTTPS, SSH, FTP, SMTP, MySQL", "DNS, VoIP, Live Video (WebRTC), Gaming, HTTP/3 (QUIC)"]
                ]
            },
            "failure_scenarios": "SYN Flood Attack: malicious bots send millions of TCP SYN packets from spoofed IPs and never send the final ACK. The server allocates TCB memory for every half-open connection until RAM is exhausted. Mitigation: Enable Linux Kernel SYN Cookies (`net.ipv4.tcp_syncookies = 1`).",
            "common_mistakes": [
                {"mistake": "Assuming UDP is obsolete and TCP should always be used for everything", "correction": "HTTP/3 (the newest global web standard powering Google, Meta, and Cloudflare) runs on QUIC over UDP because it eliminates TCP Head-of-Line blocking over mobile networks."}
            ],
            "interview_questions": [
                {"question": "Why does HTTP/3 run over UDP instead of TCP?", "answer": "In HTTP/2 over TCP, multiple multiplexed data streams share a single TCP connection. If one packet from Stream A is dropped, the entire TCP connection freezes (Head-of-Line blocking) until that packet is retransmitted. HTTP/3 uses QUIC over UDP, allowing independent stream multiplexing where packet loss on Stream A never blocks Stream B."}
            ]
        },
        {
            "id": "proxies-and-firewalls",
            "title": "Forward Proxy, Reverse Proxy, NAT & Web Application Firewalls (WAF)",
            "definition": "Network intermediaries that regulate traffic: Forward Proxy (protects and masks internal clients accessing the internet), Reverse Proxy (protects and load-balances traffic for backend servers), NAT (translates private IPs to public IPs), and WAF (inspects HTTP payloads for SQL injection and XSS).",
            "why_we_need_it": "Without reverse proxies, backend servers would be exposed directly to the public internet, vulnerable to direct port attacks, without centralized SSL termination, caching, or DDoS shielding.",
            "real_world_analogy": "Forward proxy is a corporate secretary placing outgoing phone calls on behalf of employees (keeping employee personal numbers private); Reverse proxy is a hotel receptionist greeting all incoming guests and directing them to specific rooms.",
            "how_it_works": "<p><strong>Forward Proxy:</strong> Sits in front of clients. Client sends request to proxy $\\to$ proxy fetches from internet $\\to$ returns to client. Target servers see only the proxy's IP address.</p><p><strong>Reverse Proxy (NGINX/Envoy):</strong> Sits in front of web servers. Clients believe they are talking to the website directly $\\to$ Reverse proxy terminates TLS, applies rate limits, checks cache, and forwards request to private backend instances.</p>",
            "conceptual_breakdown": [
                "<strong>Forward Proxy Use Cases:</strong> Corporate content filtering, geo-unblocking (VPNs), employee anonymity, outgoing bandwidth caching.",
                "<strong>Reverse Proxy Use Cases:</strong> SSL/TLS Termination, Load Balancing, Gzip/Brotli compression, Static file serving, Security shield.",
                "<strong>WAF (Web Application Firewall):</strong> Layer 7 deep packet inspection shielding against OWASP Top 10 vulnerabilities (SQLi, XSS, CSRF, Path Traversal).",
                "<strong>NAT (Network Address Translation):</strong> Allows 10,000 servers inside a private subnet with `10.0.x.x` IPs to share 1 public elastic IP for outbound updates."
            ],
            "arch_diagram": {
                "title": "Forward Proxy vs Reverse Proxy Architecture",
                "tiers": [
                    {
                        "label": "Client Zone",
                        "nodes": [
                            {"name": "Corporate Office Clients", "type": "client", "icon": "👥", "what": "1,000 Internal Employees", "why": "Browse external internet", "when": "Outbound", "failure": "Failover proxy"}
                        ]
                    },
                    {
                        "label": "Outbound Boundary",
                        "nodes": [
                            {"name": "Forward Proxy (Squid)", "type": "lb", "icon": "🛡️", "what": "Masks client IPs & filters malware", "why": "Client privacy & security", "when": "Outbound HTTP", "failure": "Redundant forward proxy"}
                        ]
                    },
                    {
                        "label": "Public Internet Boundary",
                        "nodes": [
                            {"name": "WAF & Reverse Proxy (NGINX)", "type": "service", "icon": "🚪", "what": "Terminates TLS, shields backend", "why": "Server security & load balance", "when": "Inbound HTTP", "failure": "Active-passive cluster"}
                        ]
                    },
                    {
                        "label": "Private Backend Zone",
                        "nodes": [
                            {"name": "Private Backend Servers", "type": "db", "icon": "🗄️", "what": "Instances on private 10.0.0.0/16 subnet", "why": "Zero public IP exposure", "when": "Execution", "failure": "Auto-scaling replacement"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "Reverse Proxy Inbound Request Shielding",
                "steps": [
                    {"step": 1, "description": "Attacker sends malicious SQL Injection payload (GET /users?id=' OR 1=1--).", "active_nodes": ["Corporate Office Clients", "WAF & Reverse Proxy (NGINX)"]},
                    {"step": 2, "description": "WAF inspects Layer 7 payload, detects regex SQL injection pattern, drops packet, and returns HTTP 403 Forbidden.", "active_nodes": ["WAF & Reverse Proxy (NGINX)"]},
                    {"step": 3, "description": "Legitimate User sends GET /profile: Reverse proxy terminates TLS and forwards clean request to Private Backend.", "active_nodes": ["WAF & Reverse Proxy (NGINX)", "Private Backend Servers"]}
                ]
            },
            "tradeoffs": "Placing a reverse proxy in front of every service introduces a small network hop (< 1ms), but provides massive benefits in security, SSL termination, and centralized observability.",
            "comparison_matrix": {
                "title": "Forward Proxy vs Reverse Proxy Matrix",
                "headers": ["Feature", "Forward Proxy", "Reverse Proxy"],
                "rows": [
                    ["Position", "In front of Clients (Client-side)", "In front of Servers (Server-side)"],
                    ["Who is protected?", "Protects Clients (Hides client IP from internet)", "Protects Servers (Hides server IPs from public)"],
                    ["Primary Functions", "Content filtering, VPN anonymity, caching outbound requests", "Load balancing, SSL termination, caching, DDoS shielding"],
                    ["Configuration", "Configured in client browser / OS network settings", "Configured by server DevOps engineers in DNS A records"],
                    ["Example Software", "Squid, Charles Proxy, Shadowsocks", "NGINX, Envoy, HAProxy, AWS ALB, Traefik"]
                ]
            },
            "failure_scenarios": "Reverse proxy CPU saturation during TLS handshake termination: handling 50,000 new TLS handshakes per second exhausts proxy CPU. Mitigation: Enable TLS Session Resumption (Session IDs & Session Tickets) and scale reverse proxy horizontally.",
            "common_mistakes": [
                {"mistake": "Assigning public IP addresses directly to internal database instances", "correction": "Never assign public IPs to databases. Place databases in private isolated VPC subnets accessible ONLY via internal reverse proxies or application servers."}
            ],
            "interview_questions": [
                {"question": "What is SSL/TLS Termination and why is it performed at the Reverse Proxy layer?", "answer": "SSL/TLS Termination is the process of decrypting incoming HTTPS traffic at the reverse proxy (edge) and forwarding unencrypted plain HTTP traffic across the internal private VPC network to backend app servers. This offloads expensive cryptographic CPU calculations from application servers and centralizes SSL certificate renewal."}
            ]
        },
        {
            "id": "real-time-protocols",
            "title": "Real-time Communication: WebSockets, Long Polling & Server-Sent Events (SSE)",
            "definition": "The architectural mechanisms for achieving bi-directional, server-to-client, and low-latency real-time data streaming over HTTP and TCP.",
            "why_we_need_it": "Standard HTTP request-response is client-initiated only; the server cannot push new data (like a new WhatsApp message or stock price update) to the browser without a real-time protocol.",
            "real_world_analogy": "Short Polling is repeatedly asking 'Are we there yet?' every 2 seconds; Long Polling is asking 'Tell me when we arrive' and waiting quietly in silence; WebSocket is putting on a live two-way walkie-talkie headset.",
            "how_it_works": "<p><strong>1. Short Polling:</strong> Client sends HTTP request every $X$ seconds. Server responds immediately (usually with empty data). Massive wasted CPU & network bandwidth!</p><p><strong>2. Long Polling:</strong> Client sends HTTP request. Server holds connection open until new data arrives (or timeout occurs) $\\to$ sends data $\\to$ client immediately opens a new request.</p><p><strong>3. Server-Sent Events (SSE):</strong> Client opens 1 HTTP connection with <code>Accept: text/event-stream</code>. Server pushes continuous uni-directional text events over the single open stream.</p><p><strong>4. WebSockets:</strong> Client sends HTTP Upgrade request (<code>Upgrade: websocket</code>). Connection transitions to a full-duplex, bi-directional persistent TCP stream with minimal 2-byte framing overhead.</p>",
            "conceptual_breakdown": [
                "<strong>Short Polling:</strong> High latency, terrible efficiency, simple to implement.",
                "<strong>Long Polling:</strong> Moderate latency, HTTP header overhead on every event, fallback for older browsers.",
                "<strong>SSE (Server-Sent Events):</strong> Optimal for 1-way server-to-client streams (Live Stock Tickers, ChatGPT streaming responses, Sports Scores). Built-in auto-reconnect!",
                "<strong>WebSockets:</strong> Optimal for 2-way real-time collaboration (Chat, Multiplayer gaming, Collaborative Whiteboards, Financial Trading)."
            ],
            "arch_diagram": {
                "title": "Real-Time Protocol Architecture Comparison",
                "tiers": [
                    {
                        "label": "Client Layer",
                        "nodes": [
                            {"name": "Client Application", "type": "client", "icon": "💻", "what": "Browser / Mobile App", "why": "Wants live real-time updates", "when": "Live session", "failure": "Auto-reconnect with backoff"}
                        ]
                    },
                    {
                        "label": "Protocol Choices",
                        "nodes": [
                            {"name": "WebSocket (Full Duplex)", "type": "service", "icon": "↔️", "what": "Persistent 2-way TCP connection", "why": "Bi-directional chat / games", "when": "Low latency 2-way", "failure": "Heartbeat ping/pong timeout"},
                            {"name": "SSE (1-Way Server Push)", "type": "cache", "icon": "➡️", "what": "text/event-stream over HTTP/2", "why": "Unidirectional live feeds / AI stream", "when": "Server-to-client only", "failure": "Built-in auto-reconnection"},
                            {"name": "Long Polling (Fallback)", "type": "lb", "icon": "⏳", "what": "Hangs HTTP connection until event", "why": "Legacy browser compatibility", "when": "Fallback only", "failure": "Connection timeout retry"}
                        ]
                    },
                    {
                        "label": "Real-Time Backend Tier",
                        "nodes": [
                            {"name": "WebSocket Gateway Cluster", "type": "db", "icon": "🌐", "what": "Maintains 1,000,000 open TCP sockets", "why": "Connection management & pub/sub routing", "when": "Real-time state", "failure": "Redis Pub/Sub backplane"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "WebSocket Connection Upgrade & Live Exchange",
                "steps": [
                    {"step": 1, "description": "1. Handshake: Client sends HTTP GET with 'Upgrade: websocket' and 'Connection: Upgrade' headers.", "active_nodes": ["Client Application", "WebSocket (Full Duplex)"]},
                    {"step": 2, "description": "2. Server responds with HTTP 101 Switching Protocols. Connection is now a persistent binary TCP stream!", "active_nodes": ["WebSocket (Full Duplex)", "WebSocket Gateway Cluster"]},
                    {"step": 3, "description": "3. Bidirectional data frames stream instantly with only 2 bytes overhead per message (Zero HTTP header re-transmission!).", "active_nodes": ["Client Application", "WebSocket (Full Duplex)", "WebSocket Gateway Cluster"]}
                ]
            },
            "tradeoffs": "WebSockets maintain stateful open TCP connections on specific servers. This requires a distributed Pub/Sub backplane (e.g. Redis Pub/Sub) so Server A can route a message to User B connected on Server 42.",
            "comparison_matrix": {
                "title": "Real-Time Communication Protocols Decision Matrix",
                "headers": ["Protocol", "Directionality", "Connection Model", "Header Overhead", "Best Use Case"],
                "rows": [
                    ["Short Polling", "Client -> Server", "New HTTP connection every X sec", "Huge (800B headers per poll)", "Rarely used in production"],
                    ["Long Polling", "Client -> Server (Hangs)", "New HTTP connection per event", "Moderate (Full HTTP headers on each message)", "Legacy fallback when WebSockets blocked"],
                    ["Server-Sent Events (SSE)", "Server -> Client ONLY", "Single persistent HTTP/2 stream", "Minimal (Plain text stream)", "ChatGPT token streaming, live sports scores, stock feeds"],
                    ["WebSockets", "Bi-directional (Full Duplex)", "Single persistent TCP connection", "Ultra low (2 - 10 bytes per frame)", "Chat apps (WhatsApp), Multiplayer games, Live trading"]
                ]
            },
            "failure_scenarios": "WebSocket connection state loss during server restart: when WebSocket Server 1 crashes, 50,000 clients disconnect simultaneously and hammer the cluster with reconnection storms (Thundering Herd). Mitigation: Add randomized reconnect jitter and route user session state through Redis Pub/Sub.",
            "common_mistakes": [
                {"mistake": "Using WebSockets for a unidirectional notification feed where Server-Sent Events (SSE) is much simpler and runs over standard HTTP/2", "correction": "If the client never needs to send data back over the socket, use Server-Sent Events (SSE). It handles firewall traversal and auto-reconnection natively."}
            ],
            "interview_questions": [
                {"question": "How do you scale a WebSocket architecture across 50 backend servers when User A on Server 1 wants to message User B connected to Server 15?", "answer": "Use a distributed Pub/Sub message broker (like Redis Pub/Sub or Kafka). When User A sends a message, Server 1 publishes the event to Redis channel `user:B:messages`. Server 15 (which holds User B's active WebSocket connection) subscribes to that channel, receives the event from Redis, and pushes it down User B's open socket."}
            ]
        }
    ]
}

# =========================================================================
# MODULE 5: HTTP & API Design: REST, GraphQL & gRPC
# =========================================================================
m5 = {
    "module_id": "05",
    "module_title": "HTTP & API Design: REST, GraphQL & gRPC",
    "description": "HTTP semantics, REST principles, GraphQL schemas, gRPC Protocol Buffers, API Gateways, rate limiting, idempotency keys, and pagination.",
    "topics": [
        {
            "id": "http-methods-headers-status-codes",
            "title": "HTTP Methods (GET, POST, PUT, PATCH, DELETE), Status Codes & Headers",
            "definition": "The formal vocabulary and semantic rules of Hypertext Transfer Protocol (HTTP), governing how client-server systems request, mutate, delete, cache, and authenticate resources.",
            "why_we_need_it": "Adhering to HTTP semantics ensures your API is predictable, cacheable by CDNs, safe from data corruption, and self-documenting across international engineering teams.",
            "real_world_analogy": "Standard postal mail: HTTP Method is the action label (Return to sender, Certified delivery), Headers are the envelope stamps and return address, Status Codes are postal tracking confirmations (Delivered, Address not found, Returned).",
            "how_it_works": "<p><strong>HTTP Methods & Idempotence:</strong></p><ul><li><code>GET</code>: Safe & Idempotent (Fetches resource without mutation). Cacheable!</li><li><code>POST</code>: Unsafe & Non-Idempotent (Creates a new resource; calling 5 times creates 5 records).</li><li><code>PUT</code>: Idempotent (Replaces entire resource; calling 5 times results in same state).</li><li><code>PATCH</code>: Non-Idempotent / Partial Update (Mutates specific fields).</li><li><code>DELETE</code>: Idempotent (Removes resource; calling 5 times produces same result).</li></ul>",
            "conceptual_breakdown": [
                "<strong>2xx Success:</strong> 200 OK, 201 Created, 204 No Content (Deletion success with empty body).",
                "<strong>3xx Redirection:</strong> 301 Moved Permanently (SEO permanent redirect), 304 Not Modified (Conditional GET cache hit).",
                "<strong>4xx Client Errors:</strong> 400 Bad Request, 401 Unauthorized (Missing auth), 403 Forbidden (Authenticated but lacking permissions), 404 Not Found, 409 Conflict, 429 Too Many Requests.",
                "<strong>5xx Server Errors:</strong> 500 Internal Error, 502 Bad Gateway (Upstream crashed), 503 Service Unavailable (Overload/maintenance), 504 Gateway Timeout."
            ],
            "arch_diagram": {
                "title": "HTTP Method Semantics & Status Flow",
                "tiers": [
                    {
                        "label": "Client Actions",
                        "nodes": [
                            {"name": "GET /orders/101", "type": "client", "icon": "📥", "what": "Fetch Order 101", "why": "Read operation (Safe & Idempotent)", "when": "View order", "failure": "404 Not Found"},
                            {"name": "POST /orders", "type": "client", "icon": "📤", "what": "Create New Order", "why": "Mutation (Non-Idempotent)", "when": "Checkout click", "failure": "400 Bad Request / 409 Conflict"},
                            {"name": "PUT /orders/101", "type": "client", "icon": "🔄", "what": "Replace Full Order 101", "why": "Full update (Idempotent)", "when": "Overwriting entity", "failure": "404 Not Found"}
                        ]
                    },
                    {
                        "label": "Gateway Semantic Verification",
                        "nodes": [
                            {"name": "REST API Gateway", "type": "lb", "icon": "⚖️", "what": "Validates Headers & Methods", "why": "Enforces protocol semantics", "when": "Every incoming request", "failure": "Returns 405 Method Not Allowed"}
                        ]
                    },
                    {
                        "label": "Response Status Tier",
                        "nodes": [
                            {"name": "201 Created / 200 OK", "type": "db", "icon": "✅", "what": "Successful execution", "why": "Standard success confirmation", "when": "Happy path", "failure": "N/A"},
                            {"name": "429 Too Many Requests", "type": "cache", "icon": "🛑", "what": "Rate limit exceeded with Retry-After", "why": "Prevents DDoS abuse", "when": "Traffic spike", "failure": "Client backoff"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "Conditional GET & 304 Not Modified Caching",
                "steps": [
                    {"step": 1, "description": "1. Client sends GET /product/42. Server returns JSON with 'ETag: 0xABCD12' and 'Cache-Control: max-age=3600'.", "active_nodes": ["GET /orders/101", "REST API Gateway", "201 Created / 200 OK"]},
                    {"step": 2, "description": "2. Client re-requests product later: sends 'If-None-Match: 0xABCD12' in request header.", "active_nodes": ["GET /orders/101", "REST API Gateway"]},
                    {"step": 3, "description": "3. Server checks hash: Product unchanged! Returns lightweight HTTP 304 Not Modified with ZERO response body bytes.", "active_nodes": ["REST API Gateway", "201 Created / 200 OK"]}
                ]
            },
            "tradeoffs": "Using `PUT` requires the client to send the entire object payload (wasting bandwidth for 1-field changes). Using `PATCH` saves bandwidth by sending only changed fields (`{ \"status\": \"shipped\" }`) but requires complex partial update validation.",
            "comparison_matrix": {
                "title": "HTTP Methods Idempotence & Safety Matrix",
                "headers": ["HTTP Method", "Safe? (No mutation)", "Idempotent? (N calls = 1 call)", "Cacheable?", "Typical Usage"],
                "rows": [
                    ["GET", "YES", "YES", "YES", "Fetch resource data"],
                    ["HEAD", "YES", "YES", "YES", "Fetch headers only without body (Checking ETag / file size)"],
                    ["POST", "NO", "NO", "Only with explicit headers", "Create new entity / Submit payment"],
                    ["PUT", "NO", "YES", "NO", "Replace entire entity (Full update)"],
                    ["PATCH", "NO", "NO (typically)", "NO", "Partial field update"],
                    ["DELETE", "NO", "YES", "NO", "Delete entity"]
                ]
            },
            "failure_scenarios": "Using `GET` for state-modifying actions (e.g. `GET /user/delete?id=5`): web crawlers, search indexing bots, and browser pre-fetching engines automatically trigger GET requests, unintentionally deleting entire databases.",
            "common_mistakes": [
                {"mistake": "Returning HTTP 200 OK with an error body like `{ \"status\": \"error\", \"code\": 404 }`", "correction": "Always use real HTTP status codes (e.g. 404, 401, 500). Proxies, CDNs, load balancers, and monitoring tools rely on true HTTP status codes for alerting and caching."}
            ],
            "interview_questions": [
                {"question": "What is the difference between HTTP 401 Unauthorized and HTTP 403 Forbidden?", "answer": "HTTP 401 Unauthorized means authentication is missing or invalid (the server does not know who you are; provide a valid JWT/API key). HTTP 403 Forbidden means the server knows who you are, but you do not have permission to access that specific resource (RBAC authorization failure)."}
            ]
        },
        {
            "id": "rest-vs-graphql-vs-grpc",
            "title": "Protocol Shootout: REST vs GraphQL vs gRPC Trade-offs",
            "definition": "The definitive technical comparison between the 3 major API paradigms: REST (Resource-oriented JSON over HTTP), GraphQL (Query-driven flexible client schemas), and gRPC (High-performance Protocol Buffers over HTTP/2).",
            "why_we_need_it": "Choosing the wrong API protocol cripples performance: using REST for high-throughput internal microservices wastes CPU parsing ASCII JSON strings, while using gRPC for public web clients requires heavy browser proxy polyfills.",
            "real_world_analogy": "REST is ordering a set combo meal from a menu; GraphQL is a custom salad bar where you pick the exact 3 ingredients you want; gRPC is a pneumatic tube delivering compressed military capsules at Mach 2.",
            "how_it_works": "<p><strong>REST:</strong> Resource URLs (`/users/42/posts`). Simple, universal, highly cacheable by CDNs, but suffers from Over-fetching (getting 50 fields when you need 1) and Under-fetching (requiring 5 sequential network calls to load 1 screen).</p><p><strong>GraphQL:</strong> Single POST endpoint (`/graphql`). Client specifies exact fields needed in query body. Eliminates over/under-fetching, but prevents native CDN caching and risks complex nested N+1 database queries.</p><p><strong>gRPC:</strong> Defines services in `.proto` files. Compiles into compact binary Protocol Buffers over HTTP/2 multiplexed streams. $7\\times - 10\\times$ faster serialization and $30\\% - 50\\%$ smaller payloads than JSON!</p>",
            "conceptual_breakdown": [
                "<strong>REST:</strong> Best for Public Developer APIs and standard CRUD web applications.",
                "<strong>GraphQL:</strong> Best for Mobile Apps, complex analytics dashboards, and aggregating multi-service backends (Backend-For-Frontend / BFF pattern).",
                "<strong>gRPC:</strong> Best for Internal East-West microservice communication, real-time streaming, and polyglot systems (C++, Go, Java, Python)."
            ],
            "arch_diagram": {
                "title": "REST vs GraphQL vs gRPC Architectural Placement",
                "tiers": [
                    {
                        "label": "External Client Boundary (North-South Traffic)",
                        "nodes": [
                            {"name": "Public Mobile / Web App", "type": "client", "icon": "📱", "what": "GraphQL / REST Client", "why": "Fetches exact view data in 1 request", "when": "Public Internet", "failure": "Token refresh"}
                        ]
                    },
                    {
                        "label": "API Gateway / BFF Tier",
                        "nodes": [
                            {"name": "GraphQL BFF Gateway", "type": "lb", "icon": "🧩", "what": "Aggregates Microservices", "why": "Translates public GraphQL to internal gRPC", "when": "North-South boundary", "failure": "Query depth limiting"}
                        ]
                    },
                    {
                        "label": "Internal Microservice Tier (East-West Traffic)",
                        "nodes": [
                            {"name": "Order Microservice (gRPC)", "type": "service", "icon": "⚡", "what": "C++ / Go Service", "why": "Ultra fast binary Protobuf over HTTP/2", "when": "Internal inter-service RPC", "failure": "Circuit breaker fallback"},
                            {"name": "Inventory Microservice (gRPC)", "type": "service", "icon": "⚡", "what": "Java / C++ Service", "why": "Multiplexed streams", "when": "Internal inter-service RPC", "failure": "Circuit breaker fallback"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "BFF Pattern: GraphQL Ingress to gRPC Internal Mesh",
                "steps": [
                    {"step": 1, "description": "Mobile App sends 1 GraphQL Query: 'query { user(id:1) { name, orders { id, total } } }'.", "active_nodes": ["Public Mobile / Web App", "GraphQL BFF Gateway"]},
                    {"step": 2, "description": "GraphQL Gateway parses AST and fires 2 parallel gRPC binary calls to User Service and Order Service.", "active_nodes": ["GraphQL BFF Gateway", "Order Microservice (gRPC)", "Inventory Microservice (gRPC)"]},
                    {"step": 3, "description": "Internal services respond via binary Protobuf in 1.5ms. Gateway combines data and returns clean JSON to mobile app.", "active_nodes": ["Order Microservice (gRPC)", "GraphQL BFF Gateway", "Public Mobile / Web App"]}
                ]
            },
            "tradeoffs": "GraphQL solves over-fetching but shifts query complexity to the backend; malicious users can submit 10-level deep nested queries that crash the database. Always enforce query depth limits and query cost analysis in GraphQL.",
            "comparison_matrix": {
                "title": "REST vs GraphQL vs gRPC Technical Shootout",
                "headers": ["Metric", "REST (HTTP/JSON)", "GraphQL", "gRPC (HTTP/2 Protobuf)"],
                "rows": [
                    ["Data Format", "JSON (Text / ASCII)", "JSON (Text / ASCII)", "Protocol Buffers (Compact Binary)"],
                    ["Network Transport", "HTTP/1.1 or HTTP/2", "HTTP/1.1 or HTTP/2 POST", "HTTP/2 Strictly (Multiplexing)"],
                    ["Performance / Latency", "Baseline (1x)", "Moderate (AST parsing overhead)", "7x - 10x Faster (Binary serialization)"],
                    ["Payload Size", "Large (Verbose JSON keys)", "Optimized (Only requested fields)", "Ultra-compact (30-50% smaller than JSON)"],
                    ["CDN Caching", "Trivial (GET /resource cacheable)", "Difficult (Most queries use HTTP POST)", "Not designed for edge HTTP caching"],
                    ["Contract Definition", "OpenAPI / Swagger (Optional)", "GraphQL Schema Definition (SDL)", "Strict `.proto` file contract (Compile-time code-gen)"],
                    ["Streaming Support", "Limited (SSE)", "Subscriptions (WebSockets)", "Native Bi-directional streaming"]
                ]
            },
            "failure_scenarios": "The GraphQL N+1 Problem: fetching 100 users and their orders executes 1 query for users plus 100 individual queries for each user's orders (101 SQL queries total). Mitigation: Use Facebook's `DataLoader` pattern to batch and memoize database queries into a single `SELECT * FROM orders WHERE user_id IN (...)`.",
            "common_mistakes": [
                {"mistake": "Using JSON REST for high-frequency internal microservice communication handling 100k QPS", "correction": "Use gRPC for internal service-to-service communication. Parsing text JSON consumes up to 30% of CPU time at high throughput."}
            ],
            "interview_questions": [
                {"question": "How do you explain the architectural decision of using GraphQL at the edge and gRPC internally?", "answer": "GraphQL is ideal for North-South client traffic because mobile devices over cellular connections need to fetch heterogeneous data in a single roundtrip without over-fetching. gRPC is ideal for East-West internal traffic because datacenter networks benefit from HTTP/2 multiplexing, binary serialization speed, and strict compile-time Protobuf typing."}
            ]
        },
        {
            "id": "api-pagination-filtering-sorting",
            "title": "Pagination (Offset vs Cursor-based), Filtering, and Sorting Strategies",
            "definition": "Techniques for querying and streaming large database result sets across API boundaries without exhausting database memory or suffering from the 'Missing/Duplicate Item' pagination bug.",
            "why_we_need_it": "Returning 1,000,000 database rows in a single HTTP response crashes server memory and browser DOMs. Choosing between Offset and Cursor pagination determines whether query performance degrades as users scroll deeper.",
            "real_world_analogy": "Offset pagination is counting 5,000 pages into a physical encyclopedia from Page 1 every single time; Cursor pagination is keeping a bookmark on the exact page you just read.",
            "how_it_works": "<p><strong>1. Offset-Based Pagination:</strong> Uses SQL <code>LIMIT 20 OFFSET 10000</code>. The database must scan and discard the first 10,000 rows before returning 20. Performance degrades linearly ($O(N)$). Also causes duplicate/skipped items when new rows are inserted!</p><p><strong>2. Cursor-Based Pagination (Keyset):</strong> Uses SQL <code>WHERE id < 'last_seen_id' ORDER BY id DESC LIMIT 20</code>. The database jumps directly to the indexed cursor in $O(1)$ / $O(\\log N)$ time. Infinite scroll stays lightning fast regardless of depth!</p>",
            "conceptual_breakdown": [
                "<strong>Offset Pagination:</strong> `GET /items?page=5&limit=20` &bull; Good for static admin tables where jumping to a specific page (e.g. Page 12) is required.",
                "<strong>Cursor Pagination:</strong> `GET /feed?cursor=eyJpZCI6MTAxfQ==&limit=20` &bull; Standard for social feeds (Twitter, Instagram, Reddit, TikTok infinite scroll).",
                "<strong>Cursor Structure:</strong> Base64-encoded string containing `(timestamp, id)` ensuring unique tie-breaking on identical timestamps."
            ],
            "arch_diagram": {
                "title": "Offset Pagination vs Cursor Pagination Performance",
                "tiers": [
                    {
                        "label": "Client Scrolling",
                        "nodes": [
                            {"name": "Client Infinite Scroll", "type": "client", "icon": "📜", "what": "User scrolls to item #100,000", "why": "Fetches next page", "when": "Scroll bottom", "failure": "Retry with last valid cursor"}
                        ]
                    },
                    {
                        "label": "Offset Approach (Slow)",
                        "nodes": [
                            {"name": "LIMIT 20 OFFSET 100000", "type": "cache", "icon": "🐢", "what": "Scans 100,000 rows in memory & discards", "why": "O(N) full index scan", "when": "Page 5,000", "failure": "Database CPU 100% saturation"}
                        ]
                    },
                    {
                        "label": "Cursor Approach (Optimal)",
                        "nodes": [
                            {"name": "WHERE id < cursor LIMIT 20", "type": "db", "icon": "⚡", "what": "B-Tree index seek directly to key", "why": "O(log N) constant time", "when": "Infinite scroll", "failure": "N/A"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "Cursor-Based Infinite Scroll Request Flow",
                "steps": [
                    {"step": 1, "description": "1. Client requests initial feed: GET /api/v1/feed?limit=10.", "active_nodes": ["Client Infinite Scroll", "Cursor Approach (Optimal)"]},
                    {"step": 2, "description": "2. Server queries DB: 'SELECT * FROM posts ORDER BY id DESC LIMIT 10'. Returns posts + 'next_cursor: 1042'.", "active_nodes": ["Cursor Approach (Optimal)"]},
                    {"step": 3, "description": "3. New post inserted at top by another user.", "active_nodes": ["Cursor Approach (Optimal)"]},
                    {"step": 4, "description": "4. User scrolls: Client sends GET /api/v1/feed?cursor=1042&limit=10. Queries 'WHERE id < 1042'. Zero duplicate posts!", "active_nodes": ["Client Infinite Scroll", "Cursor Approach (Optimal)"]}
                ]
            },
            "tradeoffs": "Cursor pagination delivers optimal $O(1)$ performance and prevents duplicate items, but prevents users from jumping directly to arbitrary page numbers (e.g. 'Jump to Page 45').",
            "comparison_matrix": {
                "title": "Offset vs Cursor Pagination Comparison",
                "headers": ["Dimension", "Offset Pagination (`LIMIT/OFFSET`)", "Cursor Pagination (`WHERE id < cursor`)"],
                "rows": [
                    ["Query Performance", "Degrades linearly $O(N)$ (Very slow on page 10,000)", "Constant $O(\\log N)$ B-Tree seek time"],
                    ["Data Drift Immunity", "Unsafe (New inserts cause duplicate/skipped items)", "Immune (Cursor points to immutable anchor key)"],
                    ["Jump to Page Number", "Yes (`page=42`)", "No (Only `next` and `prev` navigation)"],
                    ["Implementation Complexity", "Trivial (`page * limit`)", "Moderate (Requires indexed sort keys and encoding)"],
                    ["Best Suited For", "Internal Admin dashboards with numbered pages", "High-scale consumer feeds, mobile infinite scroll, chat logs"]
                ]
            },
            "failure_scenarios": "The Offset Pagination Duplication Glitch: User is viewing Page 1 (Items 1-10). A new post is published at the top. User clicks Page 2 (`OFFSET 10`). Item #10 has now shifted to position #11, so the user sees Item #10 a second time on Page 2.",
            "common_mistakes": [
                {"mistake": "Using `OFFSET 50000` on a table with 100 million rows", "correction": "Never use large offsets on massive tables. Always adopt cursor-based pagination with indexed timestamp/ID compound keys."}
            ],
            "interview_questions": [
                {"question": "How do you construct a tamper-proof cursor for cursor-based pagination with multiple sort fields (e.g. sort by likes, then by id)?", "answer": "Combine the sort fields into a tuple, serialize to JSON, and Base64-encode it: `base64_encode(JSON.stringify({ likes: 450, id: \"post_992\" }))`. In SQL, use row-value comparison: `WHERE (likes, id) < (450, 'post_992') ORDER BY likes DESC, id DESC LIMIT 20`."}
            ]
        },
        {
            "id": "idempotency-retries-rate-limiting",
            "title": "Idempotency Keys, Exponential Backoff Retries & API Gateway Routing",
            "definition": "The reliability triad of distributed APIs: Idempotency Keys (guaranteeing that duplicate network requests execute exactly once), Exponential Backoff with Jitter (safe client retries), and API Gateway rate-limiting policies.",
            "why_we_need_it": "Networks drop packets. If a mobile user clicks 'Pay $100' and the Wi-Fi disconnects after the server charges the card but before returning the HTTP 200 response, the mobile app retries. Without an idempotency key, the user is double-charged.",
            "real_world_analogy": "An elevator call button: pressing the button 10 times in a row produces the exact same result as pressing it once (Idempotent).",
            "how_it_works": "<p><strong>Idempotency Key Workflow (Stripe Standard):</strong></p><ol><li>Client generates a unique UUID (<code>Idempotency-Key: 7b3e9...</code>) and attaches it in HTTP header.</li><li>Server receives request and attempts an atomic <code>SET idempotency:7b3e9... IN_PROGRESS NX EX 120</code> in Redis.</li><li>If key already exists with status <code>COMPLETED</code>, server skips execution and immediately returns the cached HTTP response from Redis!</li><li>If key does not exist, server executes payment, stores final response in Redis, and returns HTTP 200.</li></ol>",
            "conceptual_breakdown": [
                "<strong>Idempotency-Key Header:</strong> Client-generated UUID attached to unsafe `POST` requests.",
                "<strong>Exponential Backoff:</strong> Retrying with exponentially increasing wait times ($T = 2^{\\text{attempt}} \\times 100\\text{ms}$).",
                "<strong>Full Jitter:</strong> Adding randomized noise to backoff ($T = \\text{random}(0, 2^{\\text{attempt}} \\times 100\\text{ms})$) to prevent the <em>Thundering Herd</em> retry storm.",
                "<strong>API Gateway Rate Limiting:</strong> Enforces token-bucket rate limits returning `HTTP 429 Too Many Requests` with `Retry-After: 30` header."
            ],
            "arch_diagram": {
                "title": "Idempotency Key & Redis Deduplication Engine",
                "tiers": [
                    {
                        "label": "Client Retry Layer",
                        "nodes": [
                            {"name": "Client (Idempotency-Key: UUID-101)", "type": "client", "icon": "💳", "what": "Submits $100 Payment with UUID-101", "why": "Network drops initial response", "when": "Retry attempt #2", "failure": "Client backoff"}
                        ]
                    },
                    {
                        "label": "Deduplication Gateway",
                        "nodes": [
                            {"name": "API Gateway / Payment Service", "type": "lb", "icon": "⚖️", "what": "Checks Redis for UUID-101", "why": "Prevents duplicate charge", "when": "Every incoming mutation", "failure": "Atomic Redis lock"}
                        ]
                    },
                    {
                        "label": "Idempotency Store",
                        "nodes": [
                            {"name": "Redis Idempotency Cache", "type": "cache", "icon": "⚡", "what": "Key: UUID-101 -> Stored HTTP 200 Response", "why": "Cached payment confirmation", "when": "Duplicate request", "failure": "TTL expiry after 24h"}
                        ]
                    },
                    {
                        "label": "Payment Execution",
                        "nodes": [
                            {"name": "Stripe / Banking Core", "type": "db", "icon": "🏦", "what": "Executes credit card charge ONCE", "why": "Financial state mutation", "when": "First execution only", "failure": "Card declined"}
                        ]
                    }
                ]
            },
            "system_flow_animation": {
                "title": "Idempotent Payment Retry Execution",
                "steps": [
                    {"step": 1, "description": "1. Client submits POST /checkout with 'Idempotency-Key: UUID-99'. Initial payment charges $100.", "active_nodes": ["Client (Idempotency-Key: UUID-101)", "API Gateway / Payment Service", "Payment Execution"]},
                    {"step": 2, "description": "2. Payment succeeds, response cached in Redis, but Wi-Fi drops before client receives ACK!", "active_nodes": ["Redis Idempotency Cache"]},
                    {"step": 3, "description": "3. Client re-sends POST /checkout with identical 'Idempotency-Key: UUID-99'.", "active_nodes": ["Client (Idempotency-Key: UUID-101)", "API Gateway / Payment Service"]},
                    {"step": 4, "description": "4. Gateway finds UUID-99 in Redis with status COMPLETED. Returns cached HTTP 200 instantly without re-charging card!", "active_nodes": ["Redis Idempotency Cache", "Client (Idempotency-Key: UUID-101)"]}
                ]
            },
            "tradeoffs": "Retrying without jitter causes thousands of failed clients to retry at the exact same second (e.g. at $t=1\\text{s}, t=2\\text{s}, t=4\\text{s}$), delivering a synchronized DDoS wave that crashes the recovering server.",
            "comparison_matrix": {
                "title": "Client Retry Strategies Comparison",
                "headers": ["Strategy", "Formula", "Thundering Herd Risk", "Recovery Behavior"],
                "rows": [
                    ["Immediate Retry", "Retry immediately ($0\\text{ms}$)", "Severe (Destroys overloaded server)", "Guarantees complete outage"],
                    ["Fixed Interval Retry", "Retry every $1,000\\text{ms}$", "High (Clients synchronize on 1-sec pulses)", "Prolongs recovery time"],
                    ["Exponential Backoff", "$T = 2^{\\text{attempt}} \\times \\text{base}$", "Moderate (Spreads attempts, but identical clients still pulse together)", "Acceptable"],
                    ["Exponential Backoff + Full Jitter", "$T = \\text{rand}(0, 2^{\\text{attempt}} \\times \\text{base})$", "Zero (Smooths retry traffic evenly over time spectrum)", "Optimal production standard"]
                ]
            },
            "failure_scenarios": "Double-Charging Bug: Mobile user taps 'Pay' twice during slow 3G connectivity. Without an idempotency key, the server processes two distinct database inserts, debiting the user's bank account twice.",
            "common_mistakes": [
                {"mistake": "Generating the Idempotency Key on the server side", "correction": "The Idempotency Key MUST be generated on the CLIENT side (in the mobile app/browser) BEFORE transmitting the first network request, so retries carry the identical key."}
            ],
            "interview_questions": [
                {"question": "How do you implement an atomic idempotency check in distributed systems using Redis?", "answer": "Use Redis atomic command: `SET idempotency:<key> \"IN_PROGRESS\" NX EX 120`. 1. If return is `OK` (key was set), this is the first execution -> proceed to execute business logic. 2. When execution completes, update key with the response JSON: `SET idempotency:<key> \"{\\\"status\\\":200,...}\" EX 86400`. 3. If initial `SET NX` returned `nil` (key already exists), check its value: if still `IN_PROGRESS`, return HTTP 409 Conflict / 425 Too Early; if contains completed response, return cached response immediately."}
            ]
        }
    ]
}

# Write modules 1 to 5 to JSON files
modules = [m1, m2, m3, m4, m5]
for m in modules:
    mod_id = m["module_id"]
    file_path = os.path.join(hld_dir, f"module_{mod_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print(f"Generated {file_path} with {len(m['topics'])} topics")
