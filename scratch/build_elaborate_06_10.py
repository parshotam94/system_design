"""
Full generator for Modules 06 through 10 with exhaustive, production-grade architectural content.
"""
import json
from pathlib import Path

HLD_DIR = Path('content/hld')
HLD_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# Import module 06 from previous script or define cleanly
# -------------------------------------------------------------
# Read m06 from existing file
with open(HLD_DIR / "module_06.json", "r", encoding="utf-8") as f:
    m06 = json.load(f)

# ==========================================
# MODULE 07: Load Balancing & Reverse Proxies
# ==========================================
m07 = {
  "module_id": "07",
  "module_title": "Load Balancing & Reverse Proxies",
  "description": "Master Layer 4 vs Layer 7 load balancing, balancing algorithms (Round Robin, Least Connections, Consistent Hashing), health checks, SSL termination, and Anycast routing.",
  "topics": [
    {
      "id": "why-load-balancing-l4-vs-l7",
      "title": "Why Load Balancers? Layer 4 (Transport) vs Layer 7 (Application) Routing",
      "definition": "A Load Balancer acts as a reverse proxy distributing incoming network traffic across multiple healthy backend servers. Layer 4 (L4) load balancers operate at the transport layer (TCP/UDP) routing raw packets without inspecting application payloads, while Layer 7 (L7) load balancers operate at the application layer inspecting HTTP headers, cookies, URLs, and JSON bodies.",
      "why_we_need_it": "A single server maxes out at ~10,000 to 50,000 concurrent TCP sockets and can crash at any time. Load balancing eliminates single points of failure (SPOFs), enables zero-downtime rolling deployments, terminates TLS at the edge, and distributes millions of requests evenly across server fleets.",
      "real_world_analogy": "Airport security check-in: An L4 load balancer is the airport highway traffic cop directing cars to parking lots based solely on license plates (IP/Port) without opening trunks. An L7 load balancer is the TSA officer inspecting tickets, passports, baggage contents, and flight class (headers, URLs, cookies) before routing travelers to specific priority lanes.",
      "how_it_works": "<p>1. <strong>L4 (Transport Layer) Mechanics:</strong> L4 balancers (e.g., AWS Network Load Balancer, HAProxy TCP mode, Linux Virtual Server/IPVS) examine IP packets and TCP/UDP port headers. The balancer modifies the destination IP/MAC address via Network Address Translation (NAT) or Direct Server Return (DSR). Because it does not terminate TCP or inspect payload bytes, L4 achieves blistering throughput (millions of packets/sec with sub-millisecond overhead).</p><p>2. <strong>L7 (Application Layer) Mechanics:</strong> L7 balancers (e.g., NGINX, AWS Application Load Balancer, Envoy) terminate the client TCP connection and TLS handshake. They parse full HTTP/HTTPS requests. This allows intelligent routing decisions: `/api/v1/orders` routes to the Order Service, `/static/*` routes to an S3/CDN cache, and headers like `Authorization: Bearer ...` trigger rate-limiting policies before reaching backends.</p><p>3. <strong>Direct Server Return (DSR):</strong> In high-throughput architectures (e.g., video streaming), client requests enter through the L4 load balancer, but backend servers reply directly to the client's public IP bypassing the balancer on the egress path. This prevents the load balancer from becoming an egress network bottleneck.</p>",
      "conceptual_breakdown": [
        "<strong>TCP Termination:</strong> L7 balancers establish two separate TCP connections: Client-to-LB and LB-to-Backend. L4 routes raw packets using a single spliced TCP session.",
        "<strong>TLS Offloading:</strong> The load balancer decrypts incoming HTTPS traffic using hardware cryptographic accelerators, saving backend application servers from burning 20-30% of their CPU on TLS handshakes.",
        "<strong>Direct Server Return (DSR):</strong> Ingress traffic is 1/10th the size of egress traffic. DSR allows backends to stream responses directly back to clients, scaling throughput to terabits per second.",
        "<strong>Reverse Proxy vs Forward Proxy:</strong> A forward proxy acts on behalf of clients (hiding client identities from the internet); a reverse proxy acts on behalf of backend servers (hiding server cluster topology from clients)."
      ],
      "arch_diagram": {
        "title": "Two-Tier Load Balancing Topology (L4 Edge + L7 App Gateway)",
        "tiers": [
          {
            "label": "Edge Ingress Tier",
            "nodes": [
              {
                "name": "BGP Anycast IP",
                "type": "gateway",
                "icon": "🌐",
                "what": "Global Edge IP Routing",
                "why": "Routes client to nearest geographical data center",
                "when": "DNS lookup resolution",
                "failure": "BGP withdraws route on data center failure"
              },
              {
                "name": "L4 NLB (IPVS / Maglev)",
                "type": "lb",
                "icon": "⚡",
                "what": "Kernel-level TCP load balancer",
                "why": "Handles millions of raw TCP packets/sec with DSR",
                "when": "TCP connection initiation",
                "failure": "Equal-Cost Multi-Path (ECMP) failover"
              }
            ]
          },
          {
            "label": "Application Routing Tier (L7)",
            "nodes": [
              {
                "name": "L7 ALB (NGINX / Envoy)",
                "type": "lb",
                "icon": "⚖️",
                "what": "HTTP Application Proxy & TLS Offloader",
                "why": "Inspects URI paths, cookies, and terminates TLS",
                "when": "HTTP request parsing",
                "failure": "Cross-zone auto-healing"
              }
            ]
          },
          {
            "label": "Backend Microservice Fleets",
            "nodes": [
              {
                "name": "Auth Fleet (/auth/*)",
                "type": "service",
                "icon": "🔑",
                "what": "Authentication microservice cluster",
                "why": "Handles token generation & verification",
                "when": "Routed by L7 based on path",
                "failure": "Health check evicts unhealthy instances"
              },
              {
                "name": "Order Fleet (/orders/*)",
                "type": "service",
                "icon": "📦",
                "what": "High-throughput order processing",
                "why": "Transactional commerce workflows",
                "when": "Routed by L7 path rules",
                "failure": "Auto-scaling group launches replacement nodes"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Layer 4 vs Layer 7 Load Balancing Matrix",
        "columns": ["Dimension", "Layer 4 (Transport)", "Layer 7 (Application)"],
        "rows": [
          ["Protocol Level", "TCP / UDP (Layer 4)", "HTTP, HTTPS, gRPC, WebSockets (Layer 7)"],
          ["Throughput & Latency", "Extreme (>10M packets/sec, sub-millisecond)", "High (100k-500k req/sec, 2-10ms overhead)"],
          ["Routing Intelligence", "Only IP address and TCP/UDP port number", "URL path, HTTP method, headers, cookies, payload"],
          ["TLS Termination", "Pass-through only (backend decrypts)", "Terminates TLS, inspects plaintext, re-encrypts"],
          ["Memory & CPU Usage", "Very low (stateful connection tracking only)", "High (buffers full HTTP headers and request bodies)"],
          ["Typical Technologies", "AWS NLB, HAProxy TCP mode, Linux IPVS, F5", "AWS ALB, NGINX, Envoy, Traefik, Kong"]
        ]
      },
      "tradeoffs": "<strong>L4 Pros:</strong> Blistering performance, minimal CPU overhead, handles arbitrary TCP/UDP protocols. <strong>L4 Cons:</strong> No path-based routing, cannot terminate SSL, blind to HTTP errors (cannot detect a server returning 500 Internal Server Errors). <strong>L7 Pros:</strong> Intelligent routing, URL rewriting, sticky sessions, TLS termination, WAF security inspection. <strong>L7 Cons:</strong> Higher latency, CPU intensive, susceptible to Slowloris HTTP attacks.",
      "failure_scenarios": "<strong>Load Balancer Single Point of Failure (SPOF):</strong> Deploying a single NGINX instance without redundancy. When the VM kernel panics, the entire platform goes offline. <em>Mitigation:</em> Active-Passive or Active-Active dual-balancer topology using Keepalived / VRRP (Virtual Router Redundancy Protocol) with floating Virtual IPs, or cloud managed balancers (AWS ALB) which automatically span 3+ Availability Zones.",
      "common_mistakes": [
        {"mistake": "Terminating TLS on each individual microservice pod instead of at the load balancer.", "correction": "Offload TLS at the L7 load balancer edge, and use lightweight internal mTLS (e.g. via Envoy sidecars) if internal encryption is required."},
        {"mistake": "Using L4 load balancing when your application requires sticky sessions based on user session cookies.", "correction": "L4 cannot inspect cookies. Use L7 for cookie-based session affinity, or better yet, make your services 100% stateless with Redis session tokens."}
      ],
      "interview_questions": [
        {"question": "How does Direct Server Return (DSR) work and why is it used?", "answer": "In DSR, the client sends a request to the load balancer's VIP. The L4 balancer modifies the destination MAC address to route the packet to a backend server without touching the destination IP. The backend server processes the request and sends the response <strong>directly to the client's IP</strong>, bypassing the load balancer completely. This eliminates the load balancer as an egress bandwidth bottleneck for data-heavy workloads like video streaming."},
        {"question": "Why can an L4 load balancer not detect if a backend is returning HTTP 500 errors?", "answer": "L4 operates purely at the transport layer (TCP packets). As long as the backend server completes the TCP 3-way handshake (SYN, SYN-ACK, ACK), the L4 balancer considers the backend healthy, even if every application thread is throwing uncaught exceptions and returning HTTP 500 Internal Server Error bodies."}
      ]
    },
    {
      "id": "load-balancing-algorithms",
      "title": "Balancing Algorithms: Round Robin, Weighted, Least Conn & IP Hash",
      "definition": "Load balancing algorithms are mathematical policies that determine which healthy backend server receives the next incoming network request. Classic algorithms include Round Robin, Weighted Round Robin, Least Connections, Weighted Least Connections, and IP Hash.",
      "why_we_need_it": "Without intelligent traffic distribution, requests clump onto random nodes, starving some servers while pushing others into CPU saturation and thread pool starvation, causing massive p99 latency spikes and cascaded failures.",
      "real_world_analogy": "A bank teller lobby: Round Robin gives the next customer to Teller 1, then Teller 2, then Teller 3, regardless of how long their transactions take. Least Connections looks at who has the fewest people waiting in line and directs the new customer to that teller.",
      "how_it_works": "<p>1. <strong>Round Robin:</strong> Cycles through the list of servers sequentially ($S_0, S_1, S_2, \\dots, S_{N-1}, S_0$). Best when all servers have identical hardware specifications and all incoming requests require roughly equal processing time.</p><p>2. <strong>Weighted Round Robin:</strong> Assigns an integer weight to each server reflecting its processing power (e.g., Server A weight 3, Server B weight 1). The balancer dispatches 3 requests to A for every 1 request to B.</p><p>3. <strong>Least Connections:</strong> Tracks active TCP sockets or concurrent in-flight HTTP requests per server. The next request routes to the server with $\\min(\\text{active\\_connections})$. Crucial for long-lived transactions, database connections, and WebSocket streams.</p><p>4. <strong>Weighted Least Connections:</strong> Divides active connections by server capacity weight: $\\text{Score} = \\frac{\\text{active\\_connections}}{\\text{weight}}$. Routes to the lowest score.</p><p>5. <strong>IP Hash:</strong> Computes a hash of the client's IP address: $\\text{Server} = \\text{Hash}(\\text{Client\\_IP}) \\pmod N$. Guarantees that a specific client always hits the same backend server (useful for session-sticky state without distributed cache synchronization).</p>",
      "conceptual_breakdown": [
        "<strong>Stateful vs Stateless Algorithms:</strong> Round Robin is stateless (only needs an atomic counter); Least Connections is stateful (must track connection opens and closes in real-time across all workers).",
        "<strong>The Heterogeneous Cluster Problem:</strong> If servers have different CPU/RAM sizes, Round Robin will overwhelm small nodes. Weighted algorithms are strictly required.",
        "<strong>Long-Lived Connection Skew:</strong> WebSockets or gRPC streams stay open for hours. Round Robin can accidentally place 100 long-lived streaming connections on one node while another node's short HTTP connections close immediately.",
        "<strong>IP Hash NAT Flaw:</strong> Thousands of users behind a single corporate proxy or university NAT share the same public IP address, causing IP Hash to dump all traffic onto a single backend server."
      ],
      "arch_diagram": {
        "title": "Load Balancing Algorithms Decision Pipeline",
        "tiers": [
          {
            "label": "Incoming Request Stream",
            "nodes": [
              {
                "name": "Traffic Ingress",
                "type": "client",
                "icon": "🌊",
                "what": "Mixed workload requests",
                "why": "WebSockets, short API calls & heavy file uploads",
                "when": "Continuous",
                "failure": "Buffer in socket backlog"
              }
            ]
          },
          {
            "label": "Algorithm Dispatch Engine",
            "nodes": [
              {
                "name": "Least Conn Router",
                "type": "lb",
                "icon": "🧮",
                "what": "Tracks active socket counters",
                "why": "Routes long-lived WebSocket sessions to emptiest nodes",
                "when": "WebSocket / streaming traffic",
                "failure": "Falls back to Round Robin"
              },
              {
                "name": "Consistent Hash Router",
                "type": "lb",
                "icon": "🔄",
                "what": "Ring-based client token hash",
                "why": "Maximizes local L1 cache hit ratio",
                "when": "Cache-sensitive data lookups",
                "failure": "Virtual node migration on node death"
              }
            ]
          },
          {
            "label": "Server Pool",
            "nodes": [
              {
                "name": "Backend Node 1 (32 Core)",
                "type": "service",
                "icon": "🖥️",
                "what": "High capacity server (Weight = 4)",
                "why": "Processes 4x workload share",
                "when": "Assigned by weighted scheduler",
                "failure": "Removed from ring on health check fail"
              },
              {
                "name": "Backend Node 2 (8 Core)",
                "type": "service",
                "icon": "💻",
                "what": "Standard capacity server (Weight = 1)",
                "why": "Processes 1x workload share",
                "when": "Assigned by weighted scheduler",
                "failure": "Drain connections gracefully"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Balancing Algorithms Comparison",
        "columns": ["Algorithm", "Complexity", "Best Workload", "Weakness"],
        "rows": [
          ["Round Robin", "O(1) - Extremely low", "Homogeneous servers, uniform short requests", "Severe load skew if request processing time varies"],
          ["Weighted Round Robin", "O(1) - Low", "Heterogeneous server specs (small vs large VMs)", "Does not account for real-time dynamic latency spikes"],
          ["Least Connections", "O(N) or O(log N)", "Long-lived connections (WebSockets, DB queries)", "Higher memory overhead to track active connection states"],
          ["IP Hash", "O(1) - Low", "Stateless session stickiness without external Redis", "NAT gateway clustering overloads a single server"],
          ["Least Response Time", "O(N) - Medium", "Dynamic network latency compensation", "Can cause oscillating thundering herd between servers"]
        ]
      },
      "tradeoffs": "<strong>Round Robin vs Least Connections:</strong> Round Robin has minimal CPU overhead and zero memory footprint, but breaks down when request execution times vary (e.g. simple 2ms ping vs 5000ms report generation). Least Connections dynamically balances uneven workloads at the cost of maintaining distributed connection counters in the load balancer.",
      "failure_scenarios": "<strong>The NAT Mega-Server Melt:</strong> An enterprise customer with 50,000 employees accesses your web app. Because all 50,000 employees egress through a single corporate NAT IP, IP Hash algorithm maps 100% of their requests to a single backend server, crashing it instantly while 19 other servers sit idle at 2% CPU. <em>Mitigation:</em> Use Cookie-based session stickiness or consistent hashing on session IDs instead of client IP.",
      "common_mistakes": [
        {"mistake": "Using simple Round Robin for WebSocket clusters.", "correction": "Use Least Connections for WebSockets. Since connections last for hours, Round Robin will cluster thousands of active persistent connections on unlucky servers."},
        {"mistake": "Using Round Robin in a cloud auto-scaling group with spot instances and mixed instance types.", "correction": "Use Weighted Least Connections or Peak EWMA (Exponentially Weighted Moving Average) latency-based routing."}
      ],
      "interview_questions": [
        {"question": "When would you choose Least Connections over Round Robin?", "answer": "Choose <strong>Least Connections</strong> when requests have high variance in execution time (e.g., long database exports vs instant cache hits) or when connections are persistent and stateful (e.g., WebSockets, gRPC streaming, SQL connection pools). Round Robin only works well when requests are uniform in execution duration."},
        {"question": "How does the Power of Two Random Choices algorithm improve load balancing?", "answer": "Instead of checking all N servers to find the least loaded (which is slow) or picking one randomly (which causes clustering), the balancer picks <strong>two servers at random</strong> and sends the request to whichever of the two has fewer connections. This simple $O(1)$ algorithm provides exponential load distribution improvements and prevents herd behavior."}
      ]
    },
    {
      "id": "consistent-hashing-deep-dive",
      "title": "Consistent Hashing with Virtual Nodes Deep Dive",
      "definition": "Consistent Hashing is a distributed hashing algorithm where both cache/database nodes and data keys are mapped onto a conceptual 360-degree circular ring ($0$ to $2^{32}-1$). Adding or removing a server node only requires remapping $K/N$ keys on average (where $K$ is total keys and $N$ is total servers), unlike traditional modulo hashing which remaps almost 100% of keys.",
      "why_we_need_it": "In traditional modulo hashing ($\\text{Node} = \\text{Hash}(\\text{key}) \\pmod N$), changing $N$ (adding 1 cache node or losing 1 crashed server) causes nearly every key to hash to a different node. This flushes the entire distributed cache simultaneously, triggering a catastrophic Cache Avalanche that crashes the underlying database fleet.",
      "real_world_analogy": "A circular dining room with 6 waitstations placed around the perimeter. When a food order arrives, it is walked clockwise until it reaches the nearest waitstation. If one waitstation closes, only the orders that were headed to that specific station walk a bit further to the next clockwise station. The other 5 stations keep working without disruption.",
      "how_it_works": "<p>1. <strong>The Hash Ring:</strong> The output range of a cryptographic hash function (e.g., MD5 or MurmurHash3) maps to a circular integer space from $0$ to $2^{32}-1$.</p><p>2. <strong>Placing Nodes on the Ring:</strong> Each physical server is hashed by its IP address or hostname: $\\text{pos} = \\text{Hash}(\\text{server\\_ip})$. This assigns each server a position on the ring.</p><p>3. <strong>Mapping Keys to Nodes:</strong> To store or look up key $K$, compute $\\text{pos} = \\text{Hash}(K)$. Move <em>clockwise</em> along the ring until encountering the first server node. That server is responsible for key $K$.</p><p>4. <strong>Node Failure / Addition:</strong> When Node $B$ crashes, only the keys previously assigned to $B$ fall clockwise onto Node $C$. All keys mapped to Nodes $A, D, E$ remain completely untouched.</p><p>5. <strong>Virtual Nodes (Vnodes):</strong> In a basic ring with 3 physical nodes, servers may end up non-uniformly spaced, causing severe data hotspots. Consistent Hashing solves this by creating 100 to 256 'Virtual Nodes' per physical server (e.g., `NodeA#1`, `NodeA#2`, ..., `NodeA#200`). Vnodes interleave uniformly across the entire ring, ensuring perfectly balanced load distributions ($\pm 2\\%$ variance).</p>",
      "conceptual_breakdown": [
        "<strong>Minimal Key Relocation:</strong> Only $K/N$ keys need migration during cluster scaling, preventing mass cache invalidation.",
        "<strong>Virtual Nodes (Vnodes):</strong> Eliminates hot spots caused by hash collisions. High-capacity physical servers can be assigned 500 Vnodes while smaller servers receive 100 Vnodes.",
        "<strong>Clockwise Traversal:</strong> Binary search ($O(\\log V)$ via a Skip List or TreeMap) quickly identifies the responsible node for any key.",
        "<strong>Replication Factor:</strong> In distributed databases (Cassandra, DynamoDB), a key is stored on the first node encountered clockwise, and then replicated to the next $R-1$ physically distinct nodes along the ring."
      ],
      "arch_diagram": {
        "title": "Consistent Hashing Ring with Virtual Nodes",
        "tiers": [
          {
            "label": "Key Ingress Tier",
            "nodes": [
              {
                "name": "Key Hash Input",
                "type": "client",
                "icon": "🔑",
                "what": "Key: 'user:98472'",
                "why": "Hash(Key) = 0x8F34A102",
                "when": "Client read/write",
                "failure": "Client retries lookup"
              }
            ]
          },
          {
            "label": "360-Degree Ring Router",
            "nodes": [
              {
                "name": "Binary Search TreeMap",
                "type": "lb",
                "icon": "⭕",
                "what": "In-memory Ring Index (O(log V))",
                "why": "Finds ceiling entry for key hash on ring",
                "when": "Every cache request",
                "failure": "Replicated across client SDKs"
              }
            ]
          },
          {
            "label": "Physical Nodes with Vnodes",
            "nodes": [
              {
                "name": "Node A (150 Vnodes)",
                "type": "cache",
                "icon": "🔴",
                "what": "Physical Redis Node 1",
                "why": "Owns 33.3% of ring segments",
                "when": "Clockwise hit on NodeA vnode",
                "failure": "Keys spill clockwise to Node B"
              },
              {
                "name": "Node B (150 Vnodes)",
                "type": "cache",
                "icon": "🔵",
                "what": "Physical Redis Node 2",
                "why": "Owns 33.3% of ring segments",
                "when": "Clockwise hit on NodeB vnode",
                "failure": "Keys spill clockwise to Node C"
              },
              {
                "name": "Node C (150 Vnodes)",
                "type": "cache",
                "icon": "🟢",
                "what": "Physical Redis Node 3",
                "why": "Owns 33.3% of ring segments",
                "when": "Clockwise hit on NodeC vnode",
                "failure": "Keys spill clockwise to Node A"
              }
            ]
          }
        ]
      },
      "tradeoffs": "<strong>Pros:</strong> Predictable scaling, negligible key reshuffling ($1/N$), eliminates cache thrashing, seamless cluster resizing. <strong>Cons:</strong> In-memory ring lookup overhead ($O(\\log V)$), complexity of maintaining ring metadata synchronization across distributed clients, handling cascading failures if replication is misconfigured.",
      "failure_scenarios": "<strong>Cascading Ring Overload:</strong> When physical Node A crashes, all of its Vnodes hand their keys to their immediate clockwise neighbors. If those neighbors were already at 90% memory/CPU capacity, the sudden surge in load crashes them too, setting off a domino effect that collapses the entire ring. <em>Mitigation:</em> Over-provision capacity (run nodes at &le;60% load) and use random Vnode distribution so dropped keys disperse evenly across ALL surviving nodes rather than just one neighbor.",
      "common_mistakes": [
        {"mistake": "Implementing consistent hashing without Virtual Nodes.", "correction": "Always use 100-256 Virtual Nodes per physical machine. Without Vnodes, statistical variance creates severe hot spots where one server stores 3x more data than another."},
        {"mistake": "Recomputing the hash ring on a centralized server for every single request.", "correction": "Cache the hash ring lookup table locally in client libraries (e.g., Jedis, libmemcached) and update it asynchronously via Gossip protocol or Zookeeper/etcd watches."}
      ],
      "interview_questions": [
        {"question": "How does DynamoDB or Cassandra use Consistent Hashing for data replication?", "answer": "They map the partition key of a record to a position on the ring. The record is written to the primary node (first node clockwise). Then, the coordinator node walks further clockwise and writes replicas to the next $N-1$ physically distinct nodes on the ring, skipping virtual nodes that belong to machines already hosting a replica."},
        {"question": "Why does standard modulo hashing ($K \\pmod N$) fail in elastic distributed caching?", "answer": "When a new cache node is added ($N \\to N+1$), almost every key's destination changes because $\\text{Hash}(K) \\pmod N \\neq \\text{Hash}(K) \\pmod{N+1}$. For 1,000,000 keys, ~99% of keys hash to different servers. This instantly invalidates the entire cache, causing a catastrophic database overload."}
      ]
    },
    {
      "id": "health-checks-failover-sticky-sessions",
      "title": "Active/Passive Health Checks, DNS Failover & Sticky Sessions",
      "definition": "Health checks are continuous automated probes performed by load balancers to detect backend server degradation. Active health checks periodically send HTTP GET or TCP ping probes; Passive health checks monitor live production traffic error rates. Sticky sessions bind a client's requests to a specific backend server using cookies or IP hashes.",
      "why_we_need_it": "Hardware failures, kernel panics, memory exhaustion, and deadlocks are inevitable in distributed systems. Without rapid health checks (sub-5 second detection), incoming traffic will continue hammering dead servers, resulting in user-facing 502/504 errors.",
      "real_world_analogy": "A hospital triage nurse checking patient vital signs: Active health checks are the nurse actively taking your blood pressure every 15 minutes. Passive health checks are noticing that a patient has suddenly collapsed in the hallway during transit and instantly calling for an emergency response.",
      "how_it_works": "<p>1. <strong>Active Health Checks:</strong> The load balancer sends an HTTP probe (e.g., `GET /healthz`) every 5 seconds. If the backend returns `HTTP 200 OK` within a 1-second timeout, it is marked healthy. If it returns 500 or times out for 3 consecutive attempts ('Unhealthy Threshold'), the balancer immediately stops routing traffic to that instance.</p><p>2. <strong>Deep vs Shallow Health Checks:</strong> A <em>shallow</em> check only tests if the web server process is alive. A <em>deep</em> check queries the database, checks Redis connectivity, and validates disk space. Deep checks must be carefully calibrated to prevent cascading failures if a shared database momentarily slows down.</p><p>3. <strong>Passive Health Checks (Outlier Detection):</strong> Instead of sending artificial probe traffic, the load balancer monitors live user traffic. If 5 consecutive real requests to Server B result in TCP connection resets or HTTP 503 errors, Server B is dynamically ejected from the routing pool for an ejection interval (e.g., 30 seconds).</p><p>4. <strong>DNS Failover (Route 53 / Cloudflare):</strong> Uses global health checks across geographical data centers. If an entire AWS region (e.g., `us-east-1`) fails its health checks, Route 53 updates DNS A-records or shifts Anycast routing to `us-west-2` within 30-60 seconds.</p><p>5. <strong>Sticky Sessions (Session Affinity):</strong> The L7 load balancer injects a set-cookie header (e.g., `AWSALB=xyz123`) on the first response. Future requests containing this cookie are routed to the exact same backend server, maintaining in-memory session state.</p>",
      "conceptual_breakdown": [
        "<strong>Flapping Mitigation:</strong> Flapping occurs when a dying server alternates between healthy and unhealthy every few seconds. Balancers enforce hysteresis: requiring 3 consecutive passes to enter service, but only 2 failures to exit.",
        "<strong>Graceful Connection Draining:</strong> When taking a server down for deployment, the load balancer stops sending new requests but allows existing in-flight connections to complete (typically for 30-60 seconds).",
        "<strong>The Sticky Session Trap:</strong> Sticky sessions break uniform load distribution. If a power user or web scraper connects to Server A, Server A will spike to 100% CPU while other servers sit idle.",
        "<strong>Deep Health Check Cascade:</strong> If the primary database goes down, and all 100 backend servers have deep health checks testing the DB, ALL 100 servers will report unhealthy simultaneously, causing the load balancer to drop all backends and return global 502 errors."
      ],
      "arch_diagram": {
        "title": "Health Check & Dynamic Failover Workflow",
        "tiers": [
          {
            "label": "Load Balancer Prober",
            "nodes": [
              {
                "name": "Health Monitor Daemon",
                "type": "lb",
                "icon": "🩺",
                "what": "Active probe loop (5s interval)",
                "why": "Validates /healthz endpoint status",
                "when": "Continuous background timer",
                "failure": "Dual prober consensus across AZs"
              }
            ]
          },
          {
            "label": "Dynamic Server Pool",
            "nodes": [
              {
                "name": "Server 1 (Healthy)",
                "type": "service",
                "icon": "🟢",
                "what": "HTTP 200 OK (Latency: 12ms)",
                "why": "Accepts live traffic",
                "when": "Routing state: ACTIVE",
                "failure": "Ejected after 2 failed probes"
              },
              {
                "name": "Server 2 (Failing / Deadlock)",
                "type": "service",
                "icon": "🔴",
                "what": "Timeout / HTTP 500",
                "why": "Ejected from active routing pool",
                "when": "Routing state: DRAINED",
                "failure": "Auto-scaling kills and replaces pod"
              }
            ]
          },
          {
            "label": "Dependency Verification",
            "nodes": [
              {
                "name": "Local App Context",
                "type": "service",
                "icon": "⚙️",
                "what": "Shallow Health Check",
                "why": "Verifies JVM/runtime thread readiness",
                "when": "Tested on /healthz",
                "failure": "Fails if event loop is blocked"
              },
              {
                "name": "Critical DB Dependency",
                "type": "database",
                "icon": "🗄️",
                "what": "Deep Health Check (/healthz/deep)",
                "why": "Tested only during startup probe",
                "when": "Kubernetes readiness gate",
                "failure": "Does not fail live traffic prober"
              }
            ]
          }
        ]
      },
      "tradeoffs": "<strong>Sticky Sessions:</strong> Pros: Allows stateful in-memory caching of user session state, simplifying legacy app development. Cons: Prevents even load balancing, complicates auto-scaling and zero-downtime rolling deploys, and loses user sessions if an instance crashes. Modern distributed design strictly favors stateless backends with distributed Redis sessions.",
      "failure_scenarios": "<strong>The Health Check Self-DDoS:</strong> A fleet of 50 load balancer instances probes 200 backend servers every 1 second with a heavy database query. The health checks alone generate 10,000 queries per second against the database, starving real user transactions and causing the system to crash. <em>Mitigation:</em> Use lightweight, non-database shallow health checks with 5-10 second intervals and randomized jitter.",
      "common_mistakes": [
        {"mistake": "Testing external third-party API dependencies (like Stripe or Twilio) inside your primary load balancer health check.", "correction": "Never fail your health check because a third party is down. Your service can still render fallback pages or cached views."},
        {"mistake": "Setting connection draining timeout to zero seconds during CI/CD deployments.", "correction": "Set connection draining to 30-60 seconds so active user checkouts and file uploads complete before the old container terminates."}
      ],
      "interview_questions": [
        {"question": "What is the difference between a Liveness Probe and a Readiness Probe in modern container systems (Kubernetes)?", "answer": "A <strong>Liveness Probe</strong> checks if the process is alive. If it fails, the container is killed and restarted. A <strong>Readiness Probe</strong> checks if the service is ready to accept user traffic (e.g., has finished warming up caches and loading schemas). If readiness fails, the load balancer stops routing traffic to the pod, but does NOT restart it."},
        {"question": "How do you achieve zero-downtime deployments with health checks?", "answer": "Use a <strong>Rolling Update or Blue-Green deployment</strong>. New instances spin up and run readiness health checks. The load balancer waits for 3 consecutive passing health checks before adding new instances to the live pool. Then, it initiates connection draining on the old instances, waiting 30-60 seconds for in-flight requests to complete before terminating the old containers."}
      ]
    }
  ]
}

# Write Module 07
with open(HLD_DIR / "module_07.json", "w", encoding="utf-8") as f:
  json.dump(m07, f, ensure_ascii=False, indent=2)
print("Module 07 written successfully!")
