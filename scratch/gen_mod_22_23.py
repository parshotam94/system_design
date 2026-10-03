"""
Elaborate generator for Modules 22 and 23.
Matches exact topics from app/data/hld_roadmap.json
"""
import json
from pathlib import Path

HLD_DIR = Path('content/hld')
HLD_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# MODULE 22: Distributed Rate Limiting & Traffic Management
# ==========================================
m22 = {
  "module_id": "22",
  "module_title": "Distributed Rate Limiting & Traffic Management",
  "description": "Master distributed rate limiting: The 4 core algorithms (Token Bucket, Leaky Bucket, Fixed Window, Sliding Window Counter), race-condition-free Redis Lua implementations, client identification, and tiered edge enforcement.",
  "topics": [
    {
      "id": "rate-limiting-algorithms-comparison",
      "title": "The 4 Rate Limiting Algorithms: Token Bucket, Leaky Bucket, Fixed Window & Sliding Window Counter",
      "definition": "Rate limiting restricts the number of requests a client can submit to an API within a specified time window. The four foundational algorithms are Token Bucket (allows controlled bursts), Leaky Bucket (enforces a smooth constant output rate), Fixed Window Counter (simple, but vulnerable to boundary spikes), and Sliding Window Counter (accurate, memory-efficient smoothing).",
      "why_we_need_it": "Without rate limiting, a single rogue script, aggressive web scraper, or DDoS botnet can monopolize database connections and crash an API for all paying users. Rate limiting protects backend capacity, defends against brute-force attacks, and enforces commercial SaaS monetization tiers.",
      "real_world_analogy": "A nightclub bouncer: Token Bucket is the bouncer giving out 10 entry tokens at the start of every hour; if 10 friends arrive together, they all enter at once (burst), but after that, they must wait for tokens to refill. Leaky Bucket is a revolving turnstile that physically permits only 1 person through every 5 seconds, completely smoothing traffic into a steady trickle.",
      "how_it_works": "<p>1. <strong>Token Bucket:</strong> A bucket has a maximum capacity $B$. Tokens are continuously added to the bucket at a constant refill rate $R$ tokens/second. When a request arrives: if tokens $\\ge 1$, decrement token count by 1 and allow the request; if tokens $< 1$, drop or reject the request (`HTTP 429 Too Many Requests`). <em>Key advantage:</em> Easily accommodates legitimate short-term traffic bursts up to capacity $B$.</p><p>2. <strong>Leaky Bucket:</strong> Requests enter a FIFO queue of capacity $B$. The queue leaks (dispatches to workers) at a constant, fixed rate $R$. If the queue is full when a new request arrives, it overflows and is dropped. <em>Key advantage:</em> Completely eliminates bursts, providing smooth, predictable downstream load.</p><p>3. <strong>Fixed Window Counter:</strong> Divides time into fixed windows (e.g. 1 minute from 12:00 to 12:01). Increments a counter for each request. If counter exceeds limit, reject. <em>Fatal Flaw (Boundary Spike):</em> A client sends 100 requests at 12:00:59, and another 100 requests at 12:01:01. In a 2-second window across the boundary, the client submitted 200 requests (2x the allowed limit!).</p><p>4. <strong>Sliding Window Counter (Cloudflare Hybrid):</strong> Combines the current window count and the previous window count weighted by elapsed time: $\\text{Estimated Count} = \\text{Current Window Count} + \\left(\\text{Previous Window Count} \\times (1 - \\text{elapsed\\_ratio})\\right)$. Prevents boundary spikes with minimal memory overhead ($O(1)$ memory, only storing 2 integers per client).</p>",
      "conceptual_breakdown": [
        "<strong>HTTP 429 Headers:</strong> Standard rate limiting responses MUST include: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `Retry-After: <seconds>` (telling clients exactly how long to back off).",
        "<strong>Burst Capacity vs Sustained Rate:</strong> Token Bucket is uniquely popular for public web APIs because real human users click in bursts (e.g. loading a page makes 15 API requests simultaneously) and then pause for 30 seconds.",
        "<strong>Sliding Window Log vs Counter:</strong> A Sliding Window Log stores the exact timestamp of every request in a Redis Sorted Set (ZSET). It provides 100% precision, but consumes massive memory ($O(N)$ per client). The Sliding Window Counter approximates it in $O(1)$ memory.",
        "<strong>Drop vs Queue:</strong> For interactive web APIs, reject immediately with HTTP 429; for background asynchronous workers, queue delayed tasks."
      ],
      "arch_diagram": {
        "title": "The 4 Rate Limiting Algorithms Conceptual Topologies",
        "tiers": [
          {
            "label": "Incoming Traffic Stream",
            "nodes": [
              {
                "name": "Burst of 15 Requests",
                "type": "client",
                "icon": "🌊",
                "what": "High-velocity client burst",
                "why": "Web page loading / API script",
                "when": "Arrival at t = 0",
                "failure": "Evaluated against algorithm"
              }
            ]
          },
          {
            "label": "Algorithm Mechanics",
            "nodes": [
              {
                "name": "Token Bucket (Refill Rate R)",
                "type": "lb",
                "icon": "🪣",
                "what": "Tokens accumulate up to Capacity B",
                "why": "Allows 15 requests immediately if tokens available!",
                "when": "Burst-tolerant workloads",
                "failure": "Rejects when tokens = 0"
              },
              {
                "name": "Leaky Bucket (Constant Outflow)",
                "type": "lb",
                "icon": "🚰",
                "what": "FIFO Buffer leaking at constant rate",
                "why": "Smoothes 15 requests into 1 request every 100ms",
                "when": "Protecting fragile databases",
                "failure": "Drops request if buffer overflows"
              }
            ]
          },
          {
            "label": "Downstream Protected Backend",
            "nodes": [
              {
                "name": "Microservice Fleet",
                "type": "service",
                "icon": "⚙️",
                "what": "Protected API services",
                "why": "Guaranteed safe from CPU saturation",
                "when": "Within allowed rate limits",
                "failure": "Returns HTTP 429 Too Many Requests"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Rate Limiting Algorithms Comparison",
        "columns": ["Algorithm", "Allows Bursts?", "Memory Overhead", "Accuracy", "Implementation Complexity"],
        "rows": [
          ["Token Bucket", "Yes (up to bucket capacity B)", "O(1) (2 numbers: tokens, last_refill_time)", "High", "Low-to-moderate"],
          ["Leaky Bucket", "No (Strictly smooth constant rate)", "O(Queue Size) (buffers requests)", "High", "Moderate (requires queuing engine)"],
          ["Fixed Window Counter", "No (Vulnerable to 2x boundary spikes)", "O(1) (1 integer counter per window)", "Low (boundary spike flaw)", "Lowest (single INCR command)"],
          ["Sliding Window Log", "Yes", "O(N) (stores timestamp of every request in ZSET)", "100% Precise", "High (expensive memory consumption)"],
          ["Sliding Window Counter", "Smooth / Controlled", "O(1) (2 integer counters)", "Near-perfect (~99.5% accuracy)", "Low-to-moderate"]
        ]
      },
      "tradeoffs": "<strong>Token Bucket:</strong> The industry gold standard for general API rate limiting (used by AWS, Stripe, GitHub) because it tolerates legitimate user bursts without dropping traffic. <strong>Leaky Bucket:</strong> Best for background task ingestion and communicating with rate-limited third-party vendors (e.g. third-party SMS gateways that strictly allow at most 10 requests/second).",
      "failure_scenarios": "<strong>The Fixed Window Double-Rate DDoS:</strong> An API applies a Fixed Window Rate Limit of 100 requests per minute reset at the top of each minute. An attacker submits 100 requests at 11:59:59 and another 100 requests at 12:00:01. In a 2-second span, 200 requests hit the database, exceeding capacity and crashing the server while both fixed windows show '100% compliant'. <em>Mitigation:</em> Replace Fixed Window with <strong>Sliding Window Counter</strong>.",
      "common_mistakes": [
        {"mistake": "Running a background timer thread that wakes up every second to increment tokens in millions of user buckets.", "correction": "Never use background refill threads! Calculate token refills lazily on the fly when a request arrives: `tokens = min(capacity, current_tokens + (elapsed_time * refill_rate))`."},
        {"mistake": "Using Sliding Window Log in Redis without bounding ZSET sizes.", "correction": "Under heavy traffic, storing 100,000 timestamps per client in Redis ZSETs consumes gigabytes of memory. Use the $O(1)$ Sliding Window Counter instead."}
      ],
      "interview_questions": [
        {"question": "How do you implement a Token Bucket algorithm lazily without a background timer thread?", "answer": "Store two values in the database/Redis for each client: `last_refill_timestamp` and `tokens`. When a request arrives at time $t_{\\text{now}}$: 1. Calculate time elapsed: $\\Delta t = t_{\\text{now}} - t_{\\text{last}}$; 2. Calculate new tokens generated: $\\text{new\\_tokens} = \\Delta t \\times \\text{refill\\_rate}$; 3. Update current tokens: $\\text{tokens} = \\min(\\text{capacity}, \\text{tokens} + \\text{new\\_tokens})$; 4. Update $t_{\\text{last}} = t_{\\text{now}}$; 5. If $\\text{tokens} \\ge 1$, decrement by 1 and allow; otherwise, reject. This achieves $O(1)$ performance with zero background timer threads!"},
        {"question": "What is the boundary problem in Fixed Window rate limiting and how does Sliding Window Counter fix it?", "answer": "In <strong>Fixed Window</strong>, if the limit is 100 requests/minute, an attacker can send 100 requests at the very end of Window 1 (minute 0:59) and another 100 requests at the beginning of Window 2 (minute 1:01). Over a 2-second span, 200 requests pass through, providing a 2x traffic surge. The <strong>Sliding Window Counter</strong> fixes this by taking a weighted sum of the current and previous windows based on elapsed time: $\\text{Estimated Count} = \\text{Current Count} + (\\text{Previous Count} \\times (1 - \\text{elapsed\\_percentage}))$. At minute 1:01, the previous window's weight is 59/60 (~98%), immediately rejecting the surge and smoothing the traffic curve."}
      ]
    },
    {
      "id": "distributed-rate-limiter-with-redis",
      "title": "Distributed Rate Limiter: Redis Lua Scripts, Race Conditions & Race-Condition-Free Sliding Logs",
      "definition": "A Distributed Rate Limiter coordinates rate limiting policies across a cluster of independent application servers using a shared in-memory data store (Redis). To prevent concurrency race conditions (check-then-act bugs), rate limiting logic is executed atomically inside the Redis engine using Redis Lua Scripts or Redis Cell (module).",
      "why_we_need_it": "In a microservice deployment with 50 application pods behind a load balancer, each pod maintaining a local in-memory rate limiter allows a client to submit 50x the allowed limit (by round-robining across all 50 pods). A centralized Redis rate limiter coordinates global counts across all servers.",
      "real_world_analogy": "A shared family credit card: If 4 family members are shopping at different stores simultaneously without a shared cellular connection to the central bank (local rate limiters), each person can spend up to the $1,000 credit limit simultaneously ($4,000 total). A centralized bank authorization terminal (Redis Distributed Rate Limiter) validates every swipe in real time against the global credit balance.",
      "how_it_works": "<p>1. <strong>The Check-Then-Act Race Condition Bug:</strong> If an application server queries `count = redis.get(key)` and then runs `if count < 10: redis.incr(key)`, two concurrent requests running on different servers can both read `count = 9` and both increment, allowing 11 requests through (violating the limit).</p><p>2. <strong>Atomic Redis Lua Scripting:</strong> Redis executes Lua scripts <em>single-threaded and atomically</em>. No other Redis command can execute in the middle of a Lua script. The entire Token Bucket or Sliding Window logic runs inside a single atomic round trip:<br>&bull; Redis runs the Lua script.<br>&bull; The script evaluates the timestamps, refills tokens, checks limits, and decrements atomically.<br>&bull; Returns `1` (Allowed) or `0` (Blocked) alongside remaining token count and retry seconds.</p><p>3. <strong>Redis Cell Module (Generic Cell Rate Algorithm - GCRA):</strong> An optimized C-module for Redis implementing the leaky-bucket GCRA algorithm using a single key and single command: `CL.THROTTLE <key> <max_burst> <count_per_period> <period_seconds> [cost]`.</p><p>4. <strong>High-Availability & Fail-Open Policy:</strong> What happens if the Redis rate-limiting cluster crashes? Systems enforce a <strong>Fail-Open Policy</strong>: if Redis times out or is unreachable, the API gateway logs a warning and allows the request through, prioritizing service availability over rate limiting enforcement.</p>",
      "conceptual_breakdown": [
        "<strong>Atomic Lua Execution:</strong> Eliminates network round trips and prevents check-then-act concurrency race conditions.",
        "<strong>Fail-Open vs Fail-Closed:</strong> Public user APIs should <em>Fail-Open</em> (prioritize uptime if Redis dies); high-security endpoints (e.g. login brute-force limiters) must <em>Fail-Closed</em> (block access if limiter fails).",
        "<strong>Local Memory Batching (Token Pre-allocation):</strong> To reduce Redis network QPS under extreme load, app servers batch-reserve 20 tokens from Redis at a time and allocate them locally in RAM.",
        "<strong>Key Eviction via TTL:</strong> Always configure Redis rate limiting keys with an automatic expiration TTL (e.g. 1 hour) so inactive user counters are automatically freed from RAM."
      ],
      "arch_diagram": {
        "title": "Distributed Rate Limiter with Atomic Redis Lua Script Pipeline",
        "tiers": [
          {
            "label": "Application Cluster Tier (50 Pods)",
            "nodes": [
              {
                "name": "App Pod 1",
                "type": "service",
                "icon": "📦",
                "what": "Calls redis.eval(lua_script, [user_id])",
                "why": "Delegates rate check to shared cluster",
                "when": "Client HTTP request arrives",
                "failure": "Fails Open if Redis unreachable"
              },
              {
                "name": "App Pod 2",
                "type": "service",
                "icon": "📦",
                "what": "Calls redis.eval(lua_script, [user_id])",
                "why": "Shares exact same global user key",
                "when": "Concurrent request arrives",
                "failure": "Fails Open if Redis unreachable"
              }
            ]
          },
          {
            "label": "Distributed Rate Limiting Engine",
            "nodes": [
              {
                "name": "Redis Primary (Lua Engine)",
                "type": "cache",
                "icon": "⚡",
                "what": "Atomic Token Bucket Script Execution",
                "why": "Single-threaded zero-race condition execution (<0.5ms)",
                "when": "evalsha execution",
                "failure": "Failover to Redis Sentinel replica"
              }
            ]
          },
          {
            "label": "Decision Response Tier",
            "nodes": [
              {
                "name": "Allow: HTTP 200",
                "type": "service",
                "icon": "🟢",
                "what": "Tokens >= 1 (Tokens decremented)",
                "why": "Request routed to backend microservice",
                "when": "Approved",
                "failure": "Passes through"
              },
              {
                "name": "Reject: HTTP 429",
                "type": "service",
                "icon": "🔴",
                "what": "Tokens == 0 (Drop with Retry-After: 4)",
                "why": "Short-circuited at API gateway; protects backend",
                "when": "Limit exceeded",
                "failure": "Client backs off"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Local vs Distributed Rate Limiter Comparison",
        "columns": ["Dimension", "Local In-Memory Limiter (Guava / In-Process)", "Distributed Limiter (Redis Lua)"],
        "rows": [
          ["Latency", "Zero (<1 microsecond in RAM)", "Low (0.5ms - 1ms Redis network round-trip)"],
          ["Cluster Accuracy", "Poor (Client can send N x limit across N pods)", "100% Global Accuracy across entire fleet"],
          ["Operational Complexity", "Zero (built into application code)", "Requires maintaining a high-availability Redis cluster"],
          ["Memory Usage", "Multiplied across all application pods", "Centralized in Redis with automated TTL eviction"],
          ["Best Use Case", "Single-instance services, internal microservice protection", "Public API Gateways, multi-tenant SaaS, billing limits"]
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> Distributed rate limiting provides 100% global accuracy across auto-scaling clusters, but introduces a centralized Redis infrastructure dependency and adds 0.5-1ms of network latency to every incoming API call.",
      "failure_scenarios": "<strong>The Redis Rate Limiter Outage Cascade:</strong> A high-traffic API uses a distributed Redis cluster for rate limiting. The Redis master crashes, and the client library is configured with a 5-second socket timeout and Fail-Closed policy. Every incoming user request hangs for 5 seconds waiting for Redis before returning 500 Internal Server Error. The entire platform experiences a total blackout! <em>Mitigation:</em> Configure <strong>Fail-Open</strong> with a strict 20ms circuit-breaker timeout: if Redis does not respond in 20ms, log an alert and let the user request proceed.",
      "common_mistakes": [
        {"mistake": "Sending raw Lua script text over the network on every single HTTP request.", "correction": "Preload the Lua script into Redis at startup using `SCRIPT LOAD`, and execute it using its SHA-1 hash via `EVALSHA` to save network bandwidth."},
        {"mistake": "Failing-Closed during a rate limiter infrastructure outage on public customer traffic.", "correction": "Always Fail-Open on public read endpoints. It is better to process requests without rate limiting for 10 minutes than to take down the entire company's storefront."}
      ],
      "interview_questions": [
        {"question": "How do you prevent race conditions when implementing a distributed rate limiter in Redis?", "answer": "Use a <strong>Redis Lua Script</strong>. Because Redis executes Lua scripts single-threaded and atomically on the server, the entire sequence (reading current tokens, calculating elapsed time, refilling tokens, checking limits, and updating state) executes in a single isolated step. No other command can read or write the key in the middle of execution, completely eliminating check-then-act concurrency race conditions."},
        {"question": "How do you scale a distributed rate limiter to handle 10 million requests per second?", "answer": "1. <strong>Local Batching / Pre-allocation:</strong> Application servers reserve a batch of tokens (e.g. 50 tokens) from Redis in a single request and decrement them locally in RAM, reducing Redis QPS by 50x;<br>2. <strong>Redis Cluster Sharding:</strong> Partition user rate limiting keys across 16,384 hash slots on multiple Redis nodes (each user key hashes to an independent master);<br>3. <strong>Edge Rate Limiting:</strong> Push rate limiting to Cloudflare Workers or AWS CloudFront edge PoPs, rejecting abusive bots at the network perimeter before traffic ever reaches your cloud data center."}
      ]
    },
    {
      "id": "client-identification-and-tiering",
      "title": "Client Identification, Tiered Rate Limits & Edge Rate Limiting (Cloudflare / API Gateways)",
      "definition": "Client Identification determines the unique entity to which rate limiting policies are applied (IP Address, API Key, User ID, JWT Subject, or Hybrid combination). Tiered Rate Limiting assigns different rate quotas based on commercial pricing plans (Free vs Pro vs Enterprise). Edge Rate Limiting enforces quotas directly at CDN Edge PoPs (Cloudflare, Fastly, AWS WAF) before requests enter the cloud VPC.",
      "why_we_need_it": "Rate limiting purely by IP address unfairly penalizes thousands of corporate employees sharing a single NAT gateway, while failing to block distributed botnets that rotate through 10,000 residential proxy IPs. Client identification ensures precise enforcement, protects monetization tiers, and rejects abusive traffic at the edge.",
      "real_world_analogy": "An amusement park entrance: IP-based limiting is counting how many cars enter through the highway toll gate. Client Identification is scanning individual wristbands at each roller coaster ride: VIP Platinum pass holders get priority access (Enterprise Tier: 10,000 req/min), standard ticket holders wait in regular lines (Free Tier: 60 req/min), and anyone jumping the fence without a wristband is stopped at the main perimeter gate (Edge WAF).",
      "how_it_works": "<p>1. <strong>Identification Hierarchy:</strong><br>&bull; <em>Authenticated Endpoints:</em> Use `User_ID` or `API_Key` extracted from the cryptographically verified JWT bearer token or header. Immune to NAT clustering and IP rotation.<br>&bull; <em>Unauthenticated Endpoints (Login/Signup):</em> Use a hybrid key: `Hash(Client_IP + User-Agent + JA3_Fingerprint)` to track abusive bots.<br>&bull; <em>Multi-Tenant Systems:</em> Rate limit by `Tenant_ID` (Company Account) AND `User_ID` (preventing one rogue employee from exhausting the entire company's quota).</p><p>2. <strong>Commercial Tiering Strategy:</strong><br>&bull; <em>Free Tier:</em> 60 requests/minute, bursting up to 10.<br>&bull; <em>Pro Tier:</em> 1,000 requests/minute, bursting up to 100.<br>&bull; <em>Enterprise Tier:</em> 50,000 requests/minute with custom dedicated capacity and SLA guarantees.</p><p>3. <strong>Edge Rate Limiting (Cloudflare / AWS WAF):</strong> Enforces rate limiting at the global CDN edge PoP (5ms from user). High-volume DDoS attacks or credential-stuffing bots are dropped at the edge, saving 100% of origin network bandwidth, compute, and database capacity.</p>",
      "conceptual_breakdown": [
        "<strong>The NAT Proxy Problem:</strong> Thousands of legitimate users at a university, corporate office, or airport share a single public IPv4 address. IP-based limits will block innocent users. Always prioritize authenticated user IDs or API keys.",
        "<strong>JA3 TLS Fingerprinting:</strong> Inspects the client's TLS Client Hello packet (cipher suites, extensions, elliptic curves) to identify automated bot scripts (Python requests, curl) even if they spoof the `User-Agent` HTTP header.",
        "<strong>Tiered Response Headers:</strong> Return transparent quota status in standard headers: `RateLimit-Limit: 1000`, `RateLimit-Remaining: 482`, `RateLimit-Reset: 1728000000`.",
        "<strong>Shadow / Dry-Run Mode:</strong> When introducing new rate limits, run in 'Shadow Mode' for 2 weeks: log alerts when clients exceed limits without actually dropping traffic, allowing developers to tune thresholds before enforcing."
      ],
      "arch_diagram": {
        "title": "Multi-Tiered Client Identification & Edge Rate Limiting Topology",
        "tiers": [
          {
            "label": "Edge Defense Layer (Cloudflare WAF / CDN)",
            "nodes": [
              {
                "name": "Edge WAF (IP + JA3 Fingerprint)",
                "type": "gateway",
                "icon": "🛡️",
                "what": "Blocks Volumetric Scrapers & DDoS",
                "why": "Drops abusive traffic at edge (0% origin load)",
                "when": "Client TLS connection",
                "failure": "Allows clean traffic through"
              }
            ]
          },
          {
            "label": "API Gateway Tier (Kong / Envoy)",
            "nodes": [
              {
                "name": "API Key & JWT Extractor",
                "type": "gateway",
                "icon": "🔑",
                "what": "Identifies Tenant: 'AcmeCorp' | Tier: 'Enterprise'",
                "why": "Selects rate limit policy: 50,000 req/min",
                "when": "HTTP request parsing",
                "failure": "Assigns default Free Tier limit"
              }
            ]
          },
          {
            "label": "Distributed Policy Enforcement",
            "nodes": [
              {
                "name": "Redis Tier Limiter",
                "type": "cache",
                "icon": "⚡",
                "what": "Key: ratelimit:tenant_102:enterprise",
                "why": "Enforces SLA quota across all microservices",
                "when": "Before forwarding to services",
                "failure": "Returns HTTP 429 with Tier Upgrade Link"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Client Identification Strategies Comparison",
        "columns": ["Identifier", "Vulnerability", "Best Use Case", "Implementation Effort"],
        "rows": [
          ["IP Address", "Vulnerable to NAT aggregation & IP rotation / proxy botnets", "Unauthenticated public endpoints, DDoS perimeter", "Lowest (built into load balancers)"],
          ["API Key / JWT Subject", "Requires authentication; keys can be leaked", "Public developer APIs, SaaS B2B integrations", "Low (extract header / token claims)"],
          ["Tenant ID + User ID (Hybrid)", "Requires custom middleware", "Enterprise SaaS (protects company from single rogue user)", "Moderate"],
          ["Device Fingerprint (JA3 + Canvas)", "Can produce occasional false positives on browser updates", "Anti-fraud, login credential stuffing defense", "High (requires specialized edge WAF)"]
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> Fine-grained multi-tier rate limiting (by Tenant, User, and Endpoint) enables SaaS monetization and protects multi-tenant infrastructure, but requires extracting and validating auth tokens on every request before the rate limit check can execute.",
      "failure_scenarios": "<strong>The University NAT Blackout:</strong> A university campus has 20,000 students preparing for semester finals. A streaming study app applies a strict IP-based rate limit of 500 requests/minute. Because all 20,000 students share the university's single egress NAT IP, student traffic immediately exceeds 500 req/min. The entire university is locked out of the application for 4 hours! <em>Mitigation:</em> For authenticated users, **never rate limit by IP address alone**. Rate limit by `user_id` or session token.",
      "common_mistakes": [
        {"mistake": "Applying the exact same rate limit to all API endpoints.", "correction": "Tier endpoints by computational cost: lightweight `GET /ping` can allow 5,000 req/min, while expensive `POST /reports/export_pdf` should be limited to 5 req/min."},
        {"mistake": "Failing to return the `Retry-After` header with HTTP 429 responses.", "correction": "Without `Retry-After`, client SDKs will poll aggressively, keeping your servers under continuous load."}
      ],
      "interview_questions": [
        {"question": "How do you rate limit unauthenticated users safely without blocking users sharing an office/university NAT IP?", "answer": "1. <strong>Hybrid Fingerprinting:</strong> Combine client IP with browser characteristics: `Key = Hash(IP + User-Agent + Accept-Language + JA3_TLS_Fingerprint)`;<br>2. <strong>Client-Side Anonymous UUID:</strong> Issue an encrypted, cryptographically signed HTTP-only cookie containing an anonymous device UUID on first visit, and rate limit by cookie ID;<br>3. <strong>Progressive Challenges (CAPTCHA / Proof-of-Work):</strong> When an IP address exceeds the initial threshold, do NOT return a hard HTTP 429 block; instead, serve a Cloudflare Turnstile / CAPTCHA challenge. Automated scrapers will be blocked while legitimate human users sharing the NAT complete the challenge and proceed."},
        {"question": "How do you design a tiered rate limiter for a B2B SaaS platform (Free, Pro, Enterprise)?", "answer": "1. <strong>Authentication & Tier Lookup:</strong> The API Gateway validates the client's API Key / JWT and extracts the `tenant_id` and subscription `plan_tier`;<br>2. <strong>Policy Resolution:</strong> The gateway looks up the quota profile (e.g. Free = 60/min, Pro = 1,000/min, Enterprise = 50,000/min), cached locally in API gateway memory;<br>3. <strong>Distributed Atomic Counter:</strong> The gateway calls Redis with key `rl:{tenant_id}:{window}` using a Sliding Window Counter;<br>4. <strong>Header Transparency:</strong> Return `RateLimit-Limit`, `RateLimit-Remaining`, and `RateLimit-Reset` on all responses;<br>5. <strong>Graceful Throttling:</strong> For Enterprise clients, offer a 'Soft Limit' where bursts beyond quota incur overage billing rather than hard 429 rejections."}
      ]
    }
  ]
}

# ==========================================
# MODULE 23: High Availability, Reliability & Disaster Recovery
# ==========================================
m23 = {
  "module_id": "23",
  "module_title": "High Availability, Reliability & Disaster Recovery",
  "description": "Master resilient system architecture: Calculating availability 'Nines' (99.9% to 99.999%), eliminating Single Points of Failure (SPOFs), Active-Passive vs Active-Active multi-region disaster recovery, RTO/RPO metrics, and Chaos Engineering.",
  "topics": [
    {
      "id": "availability-metrics-and-nines",
      "title": "High Availability Metrics: Calculating Uptime & 'Nines' (99.9% to 99.999%)",
      "definition": "High Availability (HA) is a measure of a system's ability to remain continuously operational and accessible over a given time period. It is formally measured in 'Nines' of uptime (from 99.9% / Three Nines up to 99.999% / Five Nines). System reliability is mathematically modeled through Serial Availability, Parallel Redundancy Availability, MTBF (Mean Time Between Failures), and MTTR (Mean Time to Repair).",
      "why_we_need_it": "Downtime costs money, damages brand reputation, and violates contractual SLAs. For an e-commerce platform generating $10 million/day, 99% availability means 3.65 days of downtime per year ($36 million lost!). Five Nines (99.999%) permits only 5 minutes and 15 seconds of total downtime per year.",
      "real_world_analogy": "An airplane's engines: A single-engine plane has no redundancy; if the engine fails, the plane crashes (Serial System). A commercial Boeing 777 has twin independent jet engines (Parallel Redundancy); if Engine 1 catches fire mid-flight, Engine 2 immediately carries the aircraft safely to an airport (High Availability).",
      "how_it_works": "<p>1. <strong>The Math of Nines (Downtime per Year):</strong><br>&bull; <em>99% (Two Nines):</em> 3.65 days downtime / year.<br>&bull; <em>99.9% (Three Nines - Standard SaaS):</em> 8 hours, 45 minutes downtime / year.<br>&bull; <em>99.99% (Four Nines - Cloud Infrastructure):</em> 52 minutes, 35 seconds downtime / year.<br>&bull; <em>99.999% (Five Nines - Telco / Mission Critical):</em> <strong>5 minutes, 15 seconds downtime / year!</strong></p><p>2. <strong>Serial Availability Formula:</strong> If a request must traverse Component A AND Component B sequentially, total availability is the product of their availabilities: $A_{\\text{system}} = A_1 \\times A_2 \\times \\dots \\times A_n$. Notice that serial dependencies *always reduce availability*! If you chain three 99.9% services together: $0.999 \\times 0.999 \\times 0.999 = 0.997$ (99.7% availability, dropping from 8 hours downtime to over 26 hours!).</p><p>3. <strong>Parallel Redundancy Formula:</strong> If a component has an independent parallel backup (active-active or active-passive): $A_{\\text{system}} = 1 - (1 - A_1)(1 - A_2)$. If two redundant load balancers each have 99% availability: $1 - (0.01 \\times 0.01) = 0.9999$ (Four Nines, 99.99%!). Redundancy multiplies availability exponentially.</p><p>4. <strong>MTBF & MTTR Equations:</strong> $\\text{Availability} = \\frac{\\text{MTBF}}{\\text{MTBF} + \\text{MTTR}}$. To maximize availability, you can either increase MTBF (make systems fail less often) or <strong>minimize MTTR</strong> (automated recovery, instant health failovers, and rollback pipelines).</p>",
      "conceptual_breakdown": [
        "<strong>Serial Degradation Law:</strong> The more microservices you synchronously chain together to fulfill a single request, the lower your overall system availability.",
        "<strong>MTTR is the Real Hero:</strong> Decreasing Mean Time to Repair (MTTR) from 1 hour to 10 seconds via automated Kubernetes pod restarts improves availability far more than trying to make hardware unbreakable.",
        "<strong>Planned vs Unplanned Downtime:</strong> Modern HA architectures forbid planned maintenance windows. Zero-downtime rolling deploys and online schema migrations are mandatory.",
        "<strong>Five Nines Cost Cliff:</strong> Moving from Three Nines to Four Nines costs ~2x in infrastructure; moving from Four Nines to Five Nines costs ~10x (multi-region active-active, custom hardware, 24/7 dedicated SREs)."
      ],
      "arch_diagram": {
        "title": "Serial Degradation vs Parallel Redundancy Math Topology",
        "tiers": [
          {
            "label": "Serial Chain (Availability Multiplies Downward)",
            "nodes": [
              {
                "name": "Gateway (99.9%)",
                "type": "gateway",
                "icon": "🚪",
                "what": "0.999",
                "why": "Sequential hop",
                "when": "Every request",
                "failure": "Single point of failure"
              },
              {
                "name": "App (99.9%)",
                "type": "service",
                "icon": "⚙️",
                "what": "0.999",
                "why": "Sequential hop",
                "when": "Every request",
                "failure": "Single point of failure"
              },
              {
                "name": "Database (99.9%)",
                "type": "database",
                "icon": "🐘",
                "what": "0.999",
                "why": "Sequential hop",
                "when": "Every request",
                "failure": "Result: 0.999 x 0.999 x 0.999 = 99.7% (26h downtime!)"
              }
            ]
          },
          {
            "label": "Parallel Redundancy (Availability Multiplies Upward)",
            "nodes": [
              {
                "name": "App Node 1 (99%)",
                "type": "service",
                "icon": "💻",
                "what": "Parallel active node",
                "why": "Independent failure domain",
                "when": "Parallel traffic",
                "failure": "Failover to Node 2"
              },
              {
                "name": "App Node 2 (99%)",
                "type": "service",
                "icon": "💻",
                "what": "Parallel active node",
                "why": "Independent failure domain",
                "when": "Parallel traffic",
                "failure": "Result: 1 - (0.01 x 0.01) = 99.99% (Four Nines!)"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "The Nines of Availability Master Reference",
        "columns": ["Nines", "Uptime %", "Downtime / Year", "Downtime / Month", "Target Systems"],
        "rows": [
          ["Two Nines", "99.0%", "3 days, 15.6 hours", "7.2 hours", "Internal batch jobs, non-critical dev tools"],
          ["Three Nines", "99.9%", "8 hours, 45 minutes", "43.2 minutes", "Standard SaaS web applications, B2B portals"],
          ["Four Nines", "99.99%", "52 minutes, 35 seconds", "4.32 minutes", "Cloud infrastructure (AWS S3/RDS), Payment Gateways"],
          ["Five Nines", "99.999%", "5 minutes, 15 seconds", "26 seconds", "Telecommunications core, Emergency 911 dispatch, Spanner"],
          ["Six Nines", "99.9999%", "31.5 seconds", "2.6 seconds", "Nuclear reactor safety systems, Aerospace control"]
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> Chasing 'Five Nines' (99.999%) requires automated sub-second failover, multi-region active-active deployments, zero maintenance windows, and continuous chaos engineering testing, dramatically increasing engineering complexity and cloud bills.",
      "failure_scenarios": "<strong>The Serial Microservice Dependency Collapse:</strong> An architect builds an API that synchronously calls 10 microservices in a single HTTP request. Each microservice independently boasts '99.9% uptime'. The overall API availability is $0.999^{10} \\approx 0.990$ (99.0%). The API experiences over 3.6 days of downtime a year, violating the company's 99.9% customer SLA. <em>Mitigation:</em> Decouple dependencies using asynchronous event queues, cached fallbacks, and circuit breakers with degraded responses.",
      "common_mistakes": [
        {"mistake": "Promising 'Five Nines' (99.999%) to customers when your underlying cloud provider SLA (e.g. AWS EC2) is only 99.99%.", "correction": "Your system cannot have higher availability than its un-replicated dependencies. To exceed cloud provider limits, you must deploy across multiple independent cloud regions or providers."},
        {"mistake": "Focusing solely on preventing failures rather than optimizing MTTR (Mean Time to Repair).", "correction": "Hardware and software failures are mathematically guaranteed. Designing automated self-healing systems that recover in seconds yields higher availability than trying to write perfect code."}
      ],
      "interview_questions": [
        {"question": "How do you calculate the overall availability of a system with both serial and parallel components?", "answer": "1. <strong>Serial Components:</strong> Multiply their individual availabilities: $A_{\\text{serial}} = A_1 \\times A_2 \\times \\dots \\times A_n$;<br>2. <strong>Parallel Redundant Components:</strong> Compute the probability that ALL parallel components fail simultaneously and subtract from 1: $A_{\\text{parallel}} = 1 - (1 - A_1)(1 - A_2) \\dots (1 - A_m)$;<br>3. <strong>Combined System:</strong> Reduce each parallel block to its equivalent availability using the parallel formula, and then multiply the resulting series of components together."},
        {"question": "Why does reducing MTTR have a more dramatic impact on availability than increasing MTBF?", "answer": "In the formula $\\text{Availability} = \\frac{\\text{MTBF}}{\\text{MTBF} + \\text{MTTR}}$, doubling MTBF (making hardware fail every 2 years instead of 1) requires massive engineering expenditure and yields tiny fractional percentage gains. In contrast, reducing MTTR from 2 hours (human manual intervention) to <strong>10 seconds</strong> (automated health check failover and Kubernetes pod self-healing) slashes downtime by 99.8%, instantly jumping a system from Two Nines (99%) to Four Nines (99.99%) with modest engineering effort."}
      ]
    },
    {
      "id": "spof-elimination-and-redundancy",
      "title": "Eliminating Single Points of Failure (SPOF): Redundancy, Heartbeats & Failover Mechanics",
      "definition": "A Single Point of Failure (SPOF) is any individual component (hardware, software, network switch, power supply, or third-party service) whose failure causes the entire system to stop functioning. Eliminating SPOFs requires designing redundant parallel components across physical failure domains, continuous heartbeat health monitoring, and automated failover mechanics.",
      "why_we_need_it": "If an entire multi-million dollar platform relies on a single master database, single NGINX load balancer, or single DNS provider, a single blown power capacitor or rogue software update takes the entire company offline. Eliminating SPOFs is the primary rule of production systems architecture.",
      "real_world_analogy": "A modern passenger aircraft: The aircraft has dual electrical generators, dual hydraulic systems, dual flight computers, and two pilots. If the primary pilot suffers a medical emergency, the co-pilot takes the controls immediately with zero disruption to the flight.",
      "how_it_works": "<p>1. <strong>Identifying SPOFs:</strong> Audit every single tier of the request path: DNS &rarr; CDN &rarr; Load Balancer &rarr; API Gateway &rarr; App Servers &rarr; Cache &rarr; Primary Database &rarr; Third-Party APIs. If removing a node leaves no viable backup path, it is a SPOF.</p><p>2. <strong>Redundancy Across Failure Domains:</strong> Redundancy must be placed across physically isolated failure domains: separate server racks, separate power grids, and distinct <strong>Availability Zones (AZs)</strong> (isolated data centers connected via low-latency fiber).</p><p>3. <strong>Heartbeat & Peer Liveness Probing:</strong> Redundant pairs exchange continuous network heartbeats (e.g. every 500ms). If the primary fails to send heartbeats for 3 consecutive intervals, the secondary assumes the primary is dead.</p><p>4. <strong>Automated Failover Protocols:</strong><br>&bull; <em>VRRP / Floating Virtual IP (Keepalived):</em> Two load balancers share a virtual IP. If Master drops, Backup claims the IP via gratuitous ARP in &lt;1 second.<br>&bull; <em>Automated Database Failover (Patroni / Orchestrator):</em> Uses Raft/Consul consensus. Promotes the most up-to-date replica to primary, updates DNS/ProxySQL routing, and fences the old primary to prevent split-brain.<br>&bull; <em>DNS Failover (Route 53):</em> Updates public DNS A-records to secondary IP if health checks fail.</p>",
      "conceptual_breakdown": [
        "<strong>N+1 vs 2N Redundancy:</strong> $N+1$ provides 1 extra spare node to survive single-node loss; $2N$ (100% redundancy) runs a complete duplicate mirror of the entire infrastructure.",
        "<strong>Fencing / STONITH:</strong> Before promoting a secondary to primary, the cluster MUST verify or forcibly kill ('Shoot The Other Node In The Head') the old primary to prevent split-brain dual-primary corruption.",
        "<strong>Silent SPOFs:</strong> Hidden single points of failure: a shared database subnet switch, a shared TLS certificate authority, a shared third-party auth provider (Auth0), or a single deployment pipeline.",
        "<strong>Failover Testing:</strong> Failover mechanisms that are not tested continuously in production will fail when real disasters strike."
      ],
      "arch_diagram": {
        "title": "End-to-End Zero SPOF Multi-AZ Architecture",
        "tiers": [
          {
            "label": "Dual Anycast Edge & DNS",
            "nodes": [
              {
                "name": "Dual DNS Providers",
                "type": "gateway",
                "icon": "🌐",
                "what": "Route 53 + Cloudflare DNS",
                "why": "Protects against DNS provider DDoS",
                "when": "Client name resolution",
                "failure": "Automatic resolver fallback"
              }
            ]
          },
          {
            "label": "Redundant Multi-AZ Load Balancers",
            "nodes": [
              {
                "name": "ALB Instance (AZ-1)",
                "type": "lb",
                "icon": "⚖️",
                "what": "Active Load Balancer",
                "why": "Terminates TLS and routes traffic",
                "when": "AZ-1 healthy",
                "failure": "Traffic routes to AZ-2 ALB"
              },
              {
                "name": "ALB Instance (AZ-2)",
                "type": "lb",
                "icon": "⚖️",
                "what": "Active Load Balancer",
                "why": "Terminates TLS and routes traffic",
                "when": "AZ-2 healthy",
                "failure": "Traffic routes to AZ-1 ALB"
              }
            ]
          },
          {
            "label": "Clustered High-Availability Storage",
            "nodes": [
              {
                "name": "Primary DB (AZ-1)",
                "type": "database",
                "icon": "👑",
                "what": "Synchronous Replication to Standby",
                "why": "Handles ACID writes",
                "when": "Active state",
                "failure": "Patroni auto-promotes Standby in <10s"
              },
              {
                "name": "Standby DB (AZ-2)",
                "type": "database",
                "icon": "🛡️",
                "what": "Hot Standby Replica",
                "why": "RPO = 0 Data Guarantee",
                "when": "Continuous sync",
                "failure": "Survives total AZ-1 destruction"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Redundancy Levels Comparison",
        "columns": ["Redundancy Model", "Cost Overhead", "Failover Latency", "Survives Multiple Failures?", "Typical Components"],
        "rows": [
          ["Active-Passive (Cold Standby)", "Low (Standby VM powered off until needed)", "Slow (Minutes to hours to boot & sync)", "No", "Disaster recovery archive servers"],
          ["Active-Passive (Hot Standby)", "High (100% duplicate infrastructure running)", "Fast (<10 seconds via VIP / Patroni)", "Yes (Survives 1 failure cleanly)", "Primary/Replica Databases, Virtual Routers"],
          ["Active-Active (N+1)", "Moderate (+20-30% extra capacity)", "Instantaneous (Traffic naturally redistributes)", "Yes", "Stateless Web App Pods, Envoy Proxies"],
          ["Active-Active Multi-Region", "Highest (2x-3x global infrastructure)", "Instantaneous (Global Anycast / Geo-DNS)", "Yes (Survives entire datacenter destruction)", "Google Spanner, Netflix Global Edge"]
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> Eliminating every SPOF requires redundant hardware across multiple data centers and automated failover tooling, significantly increasing cloud infrastructure costs and introducing distributed consensus complexity.",
      "failure_scenarios": "<strong>The Third-Party Auth SPOF Disaster:</strong> A company builds a fully redundant, multi-AZ Kubernetes cluster with sharded databases and zero internal SPOFs. However, user logins rely synchronously on a single third-party identity provider (e.g. Auth0). Auth0 suffers a 3-hour global outage. Despite the company's internal servers being 100% healthy, zero users can log in, resulting in a total business blackout. <em>Mitigation:</em> Cache validated public signing keys locally and support fallback authentication methods.",
      "common_mistakes": [
        {"mistake": "Running redundant load balancers and database replicas inside the exact same physical server rack or Availability Zone.", "correction": "A localized rack power failure or network switch crash kills all replicas simultaneously. Always distribute replicas across separate Availability Zones."},
        {"mistake": "Failing to test automated failover mechanisms in production.", "correction": "Un-tested failover scripts fail in real emergencies. Conduct regular disaster recovery fire drills (Chaos Engineering) to verify failover automation."}
      ],
      "interview_questions": [
        {"question": "How do you identify Single Points of Failure (SPOFs) in a complex system architecture?", "answer": "Perform a systematic <strong>Failure Mode and Effects Analysis (FMEA)</strong>: Trace the end-to-end request path from client DNS lookup to database disk sector. For every single hop (DNS, CDN, LB, Gateway, Service, Cache, Database, Third-Party APIs, CI/CD pipeline, and Cloud Region), ask: <em>'If this component crashes right now, what happens to the user?'</em> If the answer is 'the entire system returns errors', it is a SPOF. Remediate by introducing redundancy across independent failure domains, automated health checks, and graceful fallbacks."},
        {"question": "How does automated database failover prevent Split-Brain using Patroni and etcd?", "answer": "<strong>Patroni</strong> uses <strong>etcd</strong> as a Distributed Configuration Store (DCS). The primary database periodically renews a leader lease key in etcd with a short TTL (e.g. 10s). If the primary crashes or experiences a network partition, it cannot renew its lease. The lease expires in etcd. The standby replicas notice the expired lease and hold a leader election via etcd's Raft consensus. The replica with the most up-to-date WAL LSN wins, acquires the lease, and promotes itself to primary. If the old primary revives, it checks etcd, sees that it no longer holds the lease, and <strong>fences itself (demoting to replica)</strong>, mathematically preventing split-brain."}
      ]
    },
    {
      "id": "active-active-vs-active-passive-dr",
      "title": "Disaster Recovery Patterns: Active-Passive (Hot Standby) vs Active-Active Multi-Region",
      "definition": "Disaster Recovery (DR) architectures prepare systems to survive catastrophic regional datacenter outages (earthquakes, power grid collapses, transatlantic cable cuts). Active-Passive (Hot Standby / Pilot Light) routes all production traffic to a primary region while replicating data to a secondary standby region. Active-Active Multi-Region serves live production traffic from two or more geographically distributed data centers simultaneously.",
      "why_we_need_it": "Cloud providers experience major regional outages (e.g. AWS `us-east-1` outages) multiple times a year, knocking down thousands of companies for hours. If your architecture is confined to a single cloud region, an AWS region failure is an extinction-level event for your business.",
      "real_world_analogy": "Two power generators for a hospital: Active-Passive is having one main generator running the hospital and a secondary backup generator sitting warm in the basement; if the main generator explodes, an automated switch turns on the basement generator (small momentary flicker). Active-Active is having two generators running simultaneously, each sharing 50% of the hospital's electrical load; if one explodes, the other instantly absorbs 100% of the load with zero flicker.",
      "how_it_works": "<p>1. <strong>Active-Passive (Hot Standby):</strong> Region 1 (Primary) handles 100% of reads and writes. Database mutations are asynchronously replicated across the WAN to Region 2 (Secondary). During a regional disaster, Global DNS (Route 53) shifts traffic to Region 2, and the secondary database promotes itself to primary. RTO is 1-5 minutes; RPO is a few seconds of replication lag.</p><p>2. <strong>Active-Passive Variants:</strong><br>&bull; <em>Cold Standby (Backup & Restore):</em> Backups stored in S3; infrastructure spun up from Terraform upon disaster (RTO: hours).<br>&bull; <em>Pilot Light:</em> Database replicates continuously; application servers are scaled to zero and auto-scale up on disaster (RTO: 10-15 mins).<br>&bull; <em>Warm Standby:</em> Scaled-down fleet running in secondary region (RTO: 1-2 mins).</p><p>3. <strong>Active-Active Multi-Region:</strong> Both Region 1 and Region 2 accept live user traffic simultaneously. Handled via:<br>&bull; <em>Geo-Partitioned Active-Active:</em> US users write to US Region; EU users write to EU Region. Each region is authoritative for its local users, eliminating cross-region write latency.<br>&bull; <em>Global Multi-Master (CRDT / Spanner):</em> Multi-region consensus or conflict-free replication allows any user to write to any region, automatically converging state.</p>",
      "conceptual_breakdown": [
        "<strong>The Two-Way Write Conflict Nightmare:</strong> True multi-region active-active on relational databases is extremely difficult because concurrent writes to Region 1 and Region 2 on the same row create split-brain conflicts.",
        "<strong>Geo-Sharding (The Pragmatic Active-Active Solution):</strong> Shard users by geographic home region: a European user's data lives in Frankfurt; an American user's data lives in Virginia. Cross-region writes are rare, eliminating multi-master conflicts.",
        "<strong>Egress Bandwidth Cost:</strong> Replicating petabytes of database WAL logs across public internet or cloud inter-region WANs incurs significant cloud data transfer costs.",
        "<strong>DNS Propagation Delay in Failover:</strong> DNS TTL means some ISP resolvers will cache the dead region's IP address for minutes after failover. BGP Anycast provides faster failover than DNS."
      ],
      "arch_diagram": {
        "title": "Active-Passive vs Active-Active Multi-Region Topologies",
        "tiers": [
          {
            "label": "Global Traffic Director (Anycast / Route 53)",
            "nodes": [
              {
                "name": "Global Latency Router",
                "type": "gateway",
                "icon": "🌐",
                "what": "Routes US users to US Region; EU to EU",
                "why": "Minimizes global user latency",
                "when": "Client DNS query",
                "failure": "Health check diverts 100% traffic on regional outage"
              }
            ]
          },
          {
            "label": "Primary Region (US-East)",
            "nodes": [
              {
                "name": "US-East App & Database",
                "type": "service",
                "icon": "🏛️",
                "what": "Active Region (Handles 50% or 100% traffic)",
                "why": "Serves American users locally",
                "when": "Normal operation",
                "failure": "Cross-region async replication to EU"
              }
            ]
          },
          {
            "label": "Secondary / Active Region (EU-West)",
            "nodes": [
              {
                "name": "EU-West App & Database",
                "type": "service",
                "icon": "🏛️",
                "what": "Active-Active: Serves EU | Active-Passive: Hot Standby",
                "why": "Disaster recovery resilience",
                "when": "Continuous sync",
                "failure": "Absorbs 100% of global traffic on US crash"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Disaster Recovery Strategies Comparison",
        "columns": ["DR Strategy", "RTO (Recovery Time)", "RPO (Data Loss)", "Infrastructure Cost", "Complexity"],
        "rows": [
          ["Backup & Restore (Cold)", "24 - 48 Hours", "12 - 24 Hours", "Lowest (~1x + S3 storage)", "Lowest"],
          ["Pilot Light", "15 - 30 Minutes", "Minutes (Async DB sync)", "Low (~1.2x)", "Moderate (Terraform auto-scale)"],
          ["Warm Standby", "2 - 5 Minutes", "Seconds (Replication lag)", "Moderate (~1.5x)", "Moderate"],
          ["Active-Passive (Hot Standby)", "< 1 Minute", "Near-zero (<1-5 seconds)", "High (2x infrastructure cost)", "High (Automated failover orchestration)"],
          ["Active-Active Multi-Region", "Zero (Instantaneous)", "Zero to Seconds (Model dependent)", "Highest (2.5x - 3x cost)", "Extreme (Multi-region conflict resolution)"]
        ]
      },
      "tradeoffs": "<strong>Active-Passive:</strong> Simpler data consistency model (single write master) and lower complexity, but 50% of your paid server hardware sits idle in the standby region, and DNS failover takes 1-3 minutes. <strong>Active-Active:</strong> 100% resource utilization and instant zero-downtime failover, but requires complex multi-master replication, conflict resolution (CRDTs), and high inter-region data transfer costs.",
      "failure_scenarios": "<strong>The Inadvertent Cross-Region Split-Brain Write Disaster:</strong> A company runs Active-Passive across US-East and US-West. A network blip cuts communication between the two regions for 60 seconds. The US-West orchestrator assumes US-East was destroyed by an earthquake, promotes the standby database to primary, and updates DNS. Meanwhile, US-East is still alive and accepting writes from clients with cached DNS! Both databases accept conflicting writes for 20 minutes until engineers intervene. <em>Mitigation:</em> Require <strong>Third-Party Witness Quorum</strong> (e.g. an independent witness node in US-Central or Europe); a region cannot promote itself unless a majority of 3 global locations agree the primary is dead.",
      "common_mistakes": [
        {"mistake": "Attempting multi-region active-active writes on a traditional single-master relational database.", "correction": "Standard RDBMS cannot handle concurrent multi-region writes without extreme cross-region latency or split-brain. Use Geo-Partitioning or CockroachDB/Spanner."},
        {"mistake": "Failing to test cross-region disaster recovery failover annually.", "correction": "Disaster recovery plans that are not simulated regularly fail when actual regional outages strike. Conduct annual GameDay exercises."}
      ],
      "interview_questions": [
        {"question": "How do you achieve multi-region Active-Active architecture without suffering from cross-region write latency?", "answer": "Use <strong>Geographic Partitioning (Geo-Sharding)</strong>: Shard your user data based on their geographic home region. A European user's account and data partition reside in the European data center; an American user's data resides in the US data center. Reads and writes execute locally in sub-5ms against the local regional database. Cross-region writes are eliminated for 99% of transactions. Only rare cross-border interactions (e.g. an American user messaging a European user) require cross-region asynchronous message queues."},
        {"question": "What is the difference between a Pilot Light and a Warm Standby disaster recovery strategy?", "answer": "In a <strong>Pilot Light</strong> architecture, the database is running continuously in the DR region replicating data, but the application compute servers are either scaled down to near-zero (e.g. 1 minimal VM) or deployed as dormant container manifests. When disaster strikes, auto-scaling scripts spin up the compute fleet in 10-15 minutes. In a <strong>Warm Standby</strong> architecture, a scaled-down but fully functional fleet of application servers is actively running 24/7 in the DR region, handling background jobs or small canary traffic. Failover simply requires scaling up the existing fleet and shifting DNS in 1-2 minutes."}
      ]
    },
    {
      "id": "rto-rpo-and-chaos-engineering",
      "title": "RTO (Recovery Time Objective), RPO (Recovery Point Objective) & Chaos Engineering Principles",
      "definition": "RTO (Recovery Time Objective) is the maximum acceptable duration of system downtime after a disaster before service must be restored. RPO (Recovery Point Objective) is the maximum acceptable age of data that can be permanently lost due to a disaster, measured in time. Chaos Engineering (pioneered by Netflix with Chaos Monkey) is the disciplined practice of intentionally injecting controlled failures into production systems to build confidence in the system's resilience capabilities.",
      "why_we_need_it": "Without clear RTO and RPO targets, engineering teams overspend millions on gold-plated architectures for non-critical services, or build fragile systems that lose days of business data. Without Chaos Engineering, your disaster recovery mechanisms will fail on the very day a real disaster strikes.",
      "real_world_analogy": "Fire safety in a skyscraper: RTO is the evacuation mandate: 'All occupants must be out of the building within 5 minutes of an alarm'. RPO is the document vault guarantee: 'Fireproof safes ensure records are updated every 15 minutes, so at most 15 minutes of paperwork can be lost'. Chaos Engineering is the unannounced quarterly fire drill where smoke machines are set off in stairwells to verify that emergency doors unlock and alarms sound.",
      "how_it_works": "<p>1. <strong>RTO vs RPO Metrics:</strong><br>&bull; <em>RTO (Downtime Clock):</em> Ticks forward from the moment the disaster strikes until the system is fully operational. If RTO = 1 hour, services must be back online within 60 minutes.<br>&bull; <em>RPO (Data Loss Clock):</em> Measures backwards from the disaster timestamp to the most recent committed backup or synchronized replica. If the last backup was taken at midnight, and the server explodes at 2:00 AM, 2 hours of data is permanently lost (RPO = 2 hours).</p><p>2. <strong>The 4 Principles of Chaos Engineering (PrinciplesOfChaos.org):</strong><br>&bull; <em>1. Hypothesize around Steady State:</em> Define a measurable business steady-state metric (e.g., 'Video start rate = 50,000 streams/min', 'Order placement rate = 1,000/sec').<br>&bull; <em>2. Vary Real-World Events:</em> Simulate hardware crashes, packet loss, network latency spikes, disk exhaustion, clock skew, and datacenter blackouts.<br>&bull; <em>3. Run Experiments in Production:</em> Testing in staging fails to replicate real-world scale, traffic diversity, and production configurations.<br>&bull; <em>4. Automate Experiments to Run Continuously:</em> Integrate chaos injection into automated CI/CD schedules.</p><p>3. <strong>The Simian Army Tooling (Netflix):</strong><br>&bull; <em>Chaos Monkey:</em> Randomly terminates production EC2 instances during business hours.<br>&bull; <em>Chaos Kong:</em> Drops an entire AWS Availability Zone or Region to verify multi-region failover automation.<br>&bull; <em>Latency Monkey:</em> Injects artificial network delays to verify circuit breakers and timeouts.</p>",
      "conceptual_breakdown": [
        "<strong>Blast Radius Containment:</strong> Always start chaos experiments on a tiny canary group (1% of traffic) with automated rollback triggers before expanding blast radius.",
        "<strong>Business-Driven RTO/RPO:</strong> Engineering does not set RTO/RPO; business leadership sets it based on regulatory compliance and the cost of downtime versus the cost of redundancy.",
        "<strong>RPO = 0 Requirement:</strong> Achieving RPO = 0 requires synchronous multi-node replication (meaning every write commits to at least 2 physical failure domains before ACK).",
        "<strong>GameDays:</strong> Cross-functional live fire drills where engineering teams simulate unexpected catastrophic failures to validate on-call runbooks and monitoring dashboards."
      ],
      "arch_diagram": {
        "title": "Chaos Engineering Experiment Loop & Blast Radius Control",
        "tiers": [
          {
            "label": "Steady-State Monitoring Tier",
            "nodes": [
              {
                "name": "Prometheus / Datadog SLA Monitor",
                "type": "service",
                "icon": "📈",
                "what": "Tracks Steady-State: Orders/sec > 500 & p99 < 150ms",
                "why": "Continuous baseline verification",
                "when": "Pre, during & post experiment",
                "failure": "Aborts experiment if SLA violated"
              }
            ]
          },
          {
            "label": "Chaos Injection Engine",
            "nodes": [
              {
                "name": "Chaos Mesh / Gremlin Agent",
                "type": "lb",
                "icon": "🐒",
                "what": "Injects: 200ms Packet Latency on Payment DB",
                "why": "Validates Circuit Breaker & Fallback behavior",
                "when": "Controlled business hours window",
                "failure": "Automatic killswitch rolls back experiment"
              }
            ]
          },
          {
            "label": "Resilient Microservice Cluster",
            "nodes": [
              {
                "name": "Payment Service (Circuit Breaker)",
                "type": "database",
                "icon": "🛡️",
                "what": "Trips Circuit Breaker & Serves Fallback",
                "why": "System maintains steady-state despite latency!",
                "when": "Under chaos injection",
                "failure": "Proves architectural resilience"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "RTO & RPO Tiers by System Criticality",
        "columns": ["Tier Level", "System Category", "Target RTO (Downtime)", "Target RPO (Data Loss)", "Architectural Mechanism"],
        "rows": [
          ["Tier 0 (Mission Critical)", "Core Payment Ledger, Order Placement, Auth", "< 30 Seconds", "Zero (RPO = 0)", "Multi-AZ Synchronous DB, Raft Consensus, Active-Active"],
          ["Tier 1 (Business Critical)", "Product Catalog, Search Engine, Messaging", "< 15 Minutes", "< 1 Minute", "Read Replicas, Warm Standby, Automated Failover"],
          ["Tier 2 (Important)", "Recommendation Engine, Review System", "< 2 Hours", "< 1 Hour", "Cold Standby, Pilot Light, S3 Async Snapshots"],
          ["Tier 3 (Non-Critical)", "Internal Reporting, Analytics, Dev Environments", "< 24 Hours", "< 24 Hours", "Nightly Batch Backups to S3 Glacier"]
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> Achieving RPO = 0 requires synchronous replication, which penalizes write latency by requiring cross-network acknowledgments. Lowering RTO requires expensive continuous hot standby infrastructure and automated orchestration.",
      "failure_scenarios": "<strong>The 24-Hour Backup Restoration Surprise:</strong> A company tests database backups only by checking if the backup cron job returns status 0. A ransomware attack encrypts their production database. The team downloads their 15TB backup from S3, only to discover that uncompressing, copying, and rebuilding B-Tree indexes takes <strong>38 hours</strong>! The company's business SLA promised RTO = 2 hours, resulting in a breach of contract lawsuit. <em>Mitigation:</em> Continually run automated <strong>Restore Drills</strong>: an automated pipeline that restores backups into a staging database every week and verifies data integrity.",
      "common_mistakes": [
        {"mistake": "Running Chaos Engineering experiments without an automated emergency killswitch.", "correction": "Every chaos experiment must have a dead-man's killswitch that immediately halts chaos injection if core business steady-state metrics degrade past safety boundaries."},
        {"mistake": "Claiming RPO = 0 while using asynchronous database replication.", "correction": "Asynchronous replication means committed writes on the primary have not reached the replica yet. If the primary hardware explodes, un-replicated writes are permanently lost (RPO > 0)."}
      ],
      "interview_questions": [
        {"question": "How do you explain RTO and RPO to stakeholders and how do they drive system design decisions?", "answer": "<strong>RTO (Recovery Time Objective)</strong> is: <em>'How long can the business afford to be down?'</em>. <strong>RPO (Recovery Point Objective)</strong> is: <em>'How much data can the business afford to lose?'</em>.<br>&bull; If RPO = 0, we MUST use synchronous replication and consensus (e.g. Spanner or multi-AZ sync Postgres);<br>&bull; If RPO = 5 minutes, we can use asynchronous replication with read replicas;<br>&bull; If RTO = 30 seconds, we MUST implement automated failover orchestration (Patroni / Keepalived);<br>&bull; If RTO = 4 hours, we can save budget by using Pilot Light or automated Terraform cold recovery."},
        {"question": "What is Chaos Engineering and why did Netflix pioneer Chaos Monkey in production?", "answer": "<strong>Chaos Engineering</strong> is the disciplined practice of intentionally injecting realistic failures (server crashes, network latency, disk failures) into production systems to identify architectural weaknesses before they cause outages. Netflix pioneered <strong>Chaos Monkey</strong> when migrating from physical data centers to AWS cloud: because cloud VMs can be terminated by the cloud provider at any time, Netflix built Chaos Monkey to randomly kill production EC2 instances during business hours. This forced Netflix software engineers to architect every service to be stateless, redundant, and self-healing, ensuring that when real hardware crashes occur, end users never notice."}
      ]
    }
  ]
}

# Write Module 22 and 23
with open(HLD_DIR / "module_22.json", "w", encoding="utf-8") as f:
  json.dump(m22, f, ensure_ascii=False, indent=2)
print("Module 22 written successfully!")

with open(HLD_DIR / "module_23.json", "w", encoding="utf-8") as f:
  json.dump(m23, f, ensure_ascii=False, indent=2)
print("Module 23 written successfully!")
