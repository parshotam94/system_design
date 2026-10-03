import json
import os

CONTENT_DIR = "content/hld"
os.makedirs(CONTENT_DIR, exist_ok=True)

# -------------------------------------------------------------
# MODULE 21: Security, Authentication & Zero-Trust
# -------------------------------------------------------------
mod_21 = {
  "module_id": "21",
  "module_title": "Security, Authentication & Zero-Trust Architecture",
  "description": "Master modern security architecture: JWT vs Session cookies, OAuth 2.0 / OpenID Connect, mutual TLS (mTLS), Role & Attribute-Based Access Control (RBAC/ABAC), and OWASP Top 10 mitigation.",
  "topics": [
    {
      "id": "jwt-vs-sessions-and-oauth2",
      "title": "Authentication Architecture: JWT Tokens vs Stateful Sessions & OAuth 2.0 / OIDC",
      "definition": "Authentication verifies user identity. Stateful Sessions store session data on the server (e.g. in Redis) and issue an opaque Session ID cookie. Stateless JWTs (JSON Web Tokens) encode cryptographically signed claims directly inside the token string.",
      "why_we_need_it": "A single centralized session database becomes a severe bottleneck and single point of failure under 100,000 requests per second. Cryptographically signed tokens allow any backend microservice to verify identity locally with zero database lookups.",
      "real_world_analogy": "A Stateful Session is a coat check ticket: the attendant must look up your coat in the back room closet. A JWT is an embossed official passport: any border guard can verify the cryptographic seal and read your name directly from the passport without calling the president.",
      "how_it_works": "<p>1. <strong>JWT Structure:</strong> `Header.Payload.Signature` (Base64URL encoded). Verified using asymmetric public/private keys (RS256 / EdDSA).<br>2. <strong>OAuth 2.0 & OIDC:</strong> Authorization framework providing Access Tokens, Refresh Tokens, and Identity Tokens via Authorization Code Flow with PKCE (Proof Key for Code Exchange).<br>3. <strong>Token Rotation Strategy:</strong> Short-lived Access Tokens (15 minutes) + Long-lived Refresh Tokens (30 days) stored in secure `HttpOnly, SameSite=Strict` cookies with automated token rotation.</p>",
      "conceptual_breakdown": [
        "<strong>The Invalidation Dilemma:</strong> Because JWTs are stateless, you cannot 'delete' a JWT before its expiration without maintaining a distributed Blacklist in Redis.",
        "<strong>OIDC (OpenID Connect):</strong> An identity layer built on top of OAuth 2.0 that provides standardized user profile info (`/userinfo`, `id_token`).",
        "<strong>PKCE:</strong> Protects mobile and single-page apps (SPAs) against authorization code interception attacks."
      ],
      "comparison_matrix": {
        "title": "Stateful Sessions vs Stateless JWTs",
        "columns": ["Dimension", "Stateful Sessions (Redis)", "Stateless JWTs (RS256)"],
        "rows": [
          ["Server Storage", "Requires Redis cluster storage (~1KB per active user)", "Zero server memory storage required"],
          ["Verification Latency", "Network round-trip to Redis (~1-2ms)", "Instant local CPU cryptographic verification (<0.1ms)"],
          ["Instant Revocation", "Instant (Delete session key from Redis)", "Hard (Requires token blacklisting or short TTLs)"],
          ["Microservice Scalability", "All services query central Redis cluster", "Services verify token locally via public key"],
          ["Payload Size", "Small (32-byte opaque cookie string)", "Large (500-2000 bytes sent on every HTTP header)"]
        ]
      },
      "failure_scenarios": "<strong>Compromised JWT without Revocation:</strong> An employee's JWT token is stolen. Because the token is stateless and valid for 24 hours, the attacker accesses company APIs even after the employee changes their password. <em>Mitigation:</em> Keep access token TTL under 10 minutes and check user `password_changed_at` timestamp in JWT claims.",
      "common_mistakes": [
        {
          "mistake": "Storing sensitive JWT tokens in browser `localStorage` where they are vulnerable to Cross-Site Scripting (XSS) theft.",
          "correction": "Store tokens in `HttpOnly, Secure, SameSite=Strict` cookies to block JavaScript XSS access."
        }
      ],
      "interview_questions": [
        {
          "question": "How do you revoke a stateless JWT immediately if a user's account is compromised?",
          "answer": "Implement a distributed Redis Token Revocation Blacklist storing only revoked token IDs (`jti`) with a TTL equal to the remaining token lifetime, or maintain a `token_version` / `revocation_epoch` integer on the user record which invalidates all tokens issued prior to that timestamp."
        }
      ]
    },
    {
      "id": "rbac-abac-and-zero-trust",
      "title": "Authorization Models: RBAC vs ABAC & Zero-Trust Network Architecture",
      "definition": "RBAC (Role-Based Access Control) grants permissions based on static predefined roles (Admin, Editor, Viewer). ABAC (Attribute-Based Access Control) evaluates dynamic contextual policies based on Subject, Resource, Action, and Environment attributes (e.g. time of day, IP location, device posture). Zero-Trust Architecture enforces 'Never Trust, Always Verify' across all internal and external network boundaries.",
      "why_we_need_it": "Static roles fail in complex enterprise systems (e.g. 'A doctor can only view patient records in their specific department during active on-call shift hours from an approved hospital iPad'). ABAC solves fine-grained authorization.",
      "real_world_analogy": "RBAC is a VIP wristband that lets you into the lounge at any time. ABAC is a biometric vault that checks your role, your current security clearance, whether it is during daylight hours, and whether the fire alarm is off before unlocking.",
      "how_it_works": "<p>1. <strong>Policy Decision Point (PDP) / OPA (Open Policy Agent):</strong> Decouples authorization logic from microservices using Rego declarative policy code.<br>2. <strong>Zero-Trust Principles:</strong> Micro-segmentation, continuous identity verification, ephemeral credentials, and mutual TLS (mTLS) for all internal service-to-service communications.<br>3. <strong>OWASP Top 10 Mitigation:</strong> SQL Injection (Parameterized Prepared Statements), XSS (Content Security Policy + Sanitization), CSRF (SameSite cookies + Anti-CSRF tokens), and SSRF (Private IP metadata blacklists).</p>",
      "conceptual_breakdown": [
        "<strong>mTLS (Mutual TLS):</strong> Both client and server authenticate each other with X.509 certificates, encrypting internal service mesh traffic.",
        "<strong>OPA / Zanzibar:</strong> Google Zanzibar inspired authorization engines (e.g. Ory Keto, Auth0 FGA) for relation-based access control (ReBAC).",
        "<strong>SSRF Prevention:</strong> Block internal cloud metadata IP `169.254.169.254` and private VPC subnet ranges."
      ],
      "failure_scenarios": "<strong>Server-Side Request Forgery (SSRF) Cloud Key Theft:</strong> A user supplies an image URL `http://169.254.169.254/latest/meta-data/iam/security-credentials/`. The backend server fetches it and leaks the AWS EC2 IAM role credentials to the attacker. <em>Mitigation:</em> Strict egress firewalls and blocking all link-local/private IP destinations.",
      "common_mistakes": [
        {
          "mistake": "Relying on network perimeter firewalls and assuming internal microservice traffic is safe (Castle-and-Moat approach).",
          "correction": "Adopt Zero-Trust Architecture: enforce mTLS, identity verification, and least-privilege RBAC on every internal RPC."
        }
      ],
      "interview_questions": [
        {
          "question": "What is the difference between Policy Enforcement Point (PEP) and Policy Decision Point (PDP)?",
          "answer": "The PEP (e.g. API Gateway or Service Middleware) intercepts the request and asks the PDP 'Is this action allowed?'. The PDP (e.g. Open Policy Agent) evaluates the request context against declarative policy rules and returns a binary 'ALLOW' or 'DENY' decision to the PEP."
        }
      ]
    }
  ]
}

# -------------------------------------------------------------
# MODULE 22: Observability, Monitoring & Reliability (SRE)
# -------------------------------------------------------------
mod_22 = {
  "module_id": "22",
  "module_title": "Observability, Monitoring & Reliability (SRE)",
  "description": "Master the 3 Pillars of Observability (Metrics, Logs, Traces), Prometheus & Grafana, Distributed Tracing (OpenTelemetry/Jaeger), and Google SRE reliability principles (SLI, SLO, SLA, Error Budgets).",
  "topics": [
    {
      "id": "three-pillars-of-observability",
      "title": "The 3 Pillars of Observability: Metrics, Logs & Distributed Traces",
      "definition": "Observability is the ability to infer the internal state of a complex distributed system based on its external telemetry outputs. The three core pillars are Metrics (numeric aggregated time-series), Logs (timestamped discrete event records), and Distributed Traces (end-to-end request lifecycle graphs spanning multiple microservices).",
      "why_we_need_it": "When an API request fails in a system of 50 microservices, looking at individual server logs is impossible. Distributed tracing pinpoints the exact service, function, and database query that caused the failure in seconds.",
      "real_world_analogy": "A hospital patient monitor: Metrics are continuous vital signs (heart rate, blood pressure). Logs are doctor medical notes written in the chart. Distributed Tracing is an X-ray dye passing through blood vessels, illuminating the exact blockage point across all organs.",
      "how_it_works": "<p>1. <strong>Metrics (Prometheus):</strong> Counter, Gauge, Histogram, Summary. Polled via pull model; ultra-low storage footprint.<br>2. <strong>Logs (Elasticsearch / Grafana Loki):</strong> Structured JSON logs indexed by timestamp and tags.<br>3. <strong>Distributed Tracing (OpenTelemetry / Jaeger):</strong> Injects `trace_id` and `span_id` headers into W3C TraceContext across HTTP/gRPC boundaries. Spans capture start/end timestamps, child spans, tags, and error logs.</p>",
      "conceptual_breakdown": [
        "<strong>OpenTelemetry (OTel):</strong> Vendor-neutral standard framework for instrumenting, generating, and collecting telemetry data.",
        "<strong>The 4 Golden Signals (Google SRE):</strong> Latency, Traffic, Errors, and Saturation.",
        "<strong>Sampling:</strong> Trace 1% of normal requests + 100% of error/slow requests (Head/Tail Sampling) to minimize storage costs."
      ],
      "comparison_matrix": {
        "title": "Metrics vs Logs vs Distributed Traces",
        "columns": ["Pillar", "Data Type", "Volume / Cost", "Strengths", "Primary Tool"],
        "rows": [
          ["Metrics", "Aggregated numerical time-series", "Very Low (Constant size)", "Real-time alerting, dashboards, trend analysis", "Prometheus, Grafana, Datadog"],
          ["Logs", "Discrete text/JSON event strings", "Very High (Linear with traffic)", "Granular root-cause debugging, error context", "Elasticsearch, OpenSearch, Grafana Loki"],
          ["Traces", "Directed Acyclic Graphs (DAG) of Spans", "Moderate (Controlled via sampling)", "Pinpointing distributed latency bottlenecks & cascades", "OpenTelemetry, Jaeger, AWS X-Ray"]
        ]
      },
      "failure_scenarios": "<strong>High-Cardinality Metric Explosion:</strong> Storing unique `user_id` or `order_id` as Prometheus metric labels creates millions of unique time-series, consuming hundreds of gigabytes of RAM and crashing Prometheus server. <em>Mitigation:</em> Keep metric labels low-cardinality (e.g. `status_code`, `method`, `service`); put high-cardinality IDs in logs/traces.",
      "common_mistakes": [
        {
          "mistake": "Adding high-cardinality fields (like UUIDs or emails) as Prometheus metric labels.",
          "correction": "Prometheus metric labels must be bounded (e.g., HTTP status code 200, 400, 500). Use logs and traces for unique identifiers."
        }
      ],
      "interview_questions": [
        {
          "question": "How does Distributed Tracing propagate context across asynchronous message queues like Apache Kafka?",
          "answer": "OpenTelemetry instruments the message producer to inject the W3C `traceparent` metadata into Kafka message headers. When the consumer worker polls the message, it extracts the traceparent header and starts a child span linked to the original trace ID."
        }
      ]
    },
    {
      "id": "sre-sli-slo-sla-error-budgets",
      "title": "Site Reliability Engineering (SRE): SLIs, SLOs, SLAs & Error Budgets",
      "definition": "Google SRE methodology establishes quantitative reliability targets: SLIs (Service Level Indicators) measure real-time performance, SLOs (Service Level Objectives) define internal target reliability, SLAs (Service Level Agreements) define contractual commitments with financial penalties, and Error Budgets govern release velocity.",
      "why_we_need_it": "Aiming for 100% uptime is financially irrational and slows product innovation to a crawl. Error budgets balance feature velocity against platform stability.",
      "real_world_analogy": "A speed limit and fine: The speedometer is your SLI (real-time speed). The target driving speed is your SLO (staying under 65 mph). The police ticket threshold is your SLA (exceeding 75 mph triggers a fine). The Error Budget is the margin of speed you can safely use to pass a slow truck.",
      "how_it_works": "<p>1. <strong>SLI (Formula):</strong> `Good_Events / Total_Events` (e.g. `Successful HTTP 2xx requests with latency < 200ms / Total Requests`).<br>2. <strong>SLO (Target):</strong> e.g., 99.9% of requests meet SLI over a rolling 30-day window.<br>3. <strong>Error Budget:</strong> $100\\% - \\text{SLO} = 0.1\\%$ allowed unreliability. If the team has 43 minutes of allowed downtime per month and burns 40 minutes in an outage, new feature deployments freeze and engineering focuses 100% on reliability.</p>",
      "conceptual_breakdown": [
        "<strong>99.9% (3 Nines):</strong> 43.8 minutes downtime per month.",
        "<strong>99.99% (4 Nines):</strong> 4.38 minutes downtime per month.",
        "<strong>99.999% (5 Nines):</strong> 26.3 seconds downtime per month (requires multi-region active-active zero-downtime automation).",
        "<strong>Error Budget Freeze:</strong> Automatic policy: when error budget hits 0%, CI/CD pipelines block new feature releases until reliability is restored."
      ],
      "failure_scenarios": "<strong>Misaligned SLA vs SLO:</strong> Setting the external customer SLA equal to the internal SLO (e.g. both at 99.99%). Any minor internal SLO breach instantly triggers contractual customer penalty payouts. <em>Mitigation:</em> Make internal SLO strictly tighter than external SLA (e.g. SLO 99.95%, SLA 99.9%).",
      "common_mistakes": [
        {
          "mistake": "Measuring uptime using simple ping checks rather than user-perceived critical user journeys (CUJs).",
          "correction": "Measure SLIs based on business-critical user journeys (e.g. successful checkout transactions)."
        }
      ],
      "interview_questions": [
        {
          "question": "How does an Error Budget resolve the natural conflict between Product Managers (features) and Operations/SREs (stability)?",
          "answer": "An Error Budget creates an objective, agreed-upon framework: as long as the error budget is healthy (>0%), product teams have green light to deploy features rapidly and take calculated risks; if outages exhaust the budget, product deployments halt and all engineering effort pivots to stability improvements."
        }
      ]
    }
  ]
}

# -------------------------------------------------------------
# MODULE 23: Deployment Strategies, CI/CD & Infrastructure
# -------------------------------------------------------------
mod_23 = {
  "module_id": "23",
  "module_title": "Deployment Strategies, CI/CD & Infrastructure",
  "description": "Master zero-downtime deployment patterns (Blue-Green, Canary, Rolling, Shadow/Dark Launching), feature flags, and Infrastructure as Code (Terraform/Kubernetes).",
  "topics": [
    {
      "id": "deployment-strategies-blue-green-canary",
      "title": "Zero-Downtime Deployments: Rolling, Blue-Green, Canary & Shadow Deployments",
      "definition": "Deployment strategies manage the safe transition of production traffic from an old software version to a new software version with zero user downtime and immediate rollback capabilities.",
      "why_we_need_it": "Stopping all servers to deploy new code (Recreate strategy) causes complete site downtime. Faulty releases deployed to 100% of servers simultaneously can cause massive business outages.",
      "real_world_analogy": "Canary deployment is sending a canary bird into a coal mine: if the canary is healthy, it is safe for miners to enter. If the canary gets sick (errors detected), miners retreat immediately before anyone is harmed.",
      "how_it_works": "<p>1. <strong>Rolling Deployment:</strong> Incrementally replaces instances one by one (e.g., 25% at a time). Cost-effective, but runs v1 and v2 concurrently in production.<br>2. <strong>Blue-Green Deployment:</strong> Spins up a complete identical duplicate environment (Green) running v2. Runs smoke tests on Green. Load balancer switches 100% of traffic from Blue to Green instantly. Instant rollback by switching router back to Blue.<br>3. <strong>Canary Deployment:</strong> Routes a tiny fraction of real user traffic (1% -> 5% -> 25% -> 100%) to the new version while automated analyzers monitor error rates and latency. Automatically rolls back on anomalies.<br>4. <strong>Shadow (Dark) Deployment:</strong> Duplicates (mirrors) live production traffic at the Load Balancer, sending copies to v2. v2 processes requests but its responses are discarded, validating real-world performance with ZERO user risk.</p>",
      "comparison_matrix": {
        "title": "Zero-Downtime Deployment Strategies Comparison",
        "columns": ["Strategy", "Cost / Resource Overhead", "Rollback Speed", "User Impact on Bug", "Database Complexity"],
        "rows": [
          ["Rolling Deployment", "Zero extra infrastructure (Replaces in-place)", "Slow (Requires reverse rolling update)", "Affects portion of users (25%)", "DB schema must support v1 and v2 simultaneously"],
          ["Blue-Green Deployment", "High (2x duplicate server infrastructure)", "Instant (<1s via Load Balancer switch)", "Affects 100% of users if bug slips through smoke tests", "Strict backward/forward schema compatibility required"],
          ["Canary Deployment", "Low (Small canary pool)", "Fast (Re-route canary traffic to v1)", "Minimal (Only 1% of users exposed to canary)", "Requires backward-compatible schemas"],
          ["Shadow (Dark) Launch", "Moderate (Duplicate compute)", "Instant (Disable mirroring)", "Zero (User never sees shadow responses)", "Shadow writes must be mocked/isolated"]
        ]
      },
      "failure_scenarios": "<strong>Breaking Database Changes during Rolling Updates:</strong> Deploying v2 with a destructive database migration (e.g. dropping a column) crashes the remaining 75% of v1 servers currently running in production. <em>Mitigation:</em> Follow the Expand-and-Contract (Parallel Run) database migration pattern.",
      "common_mistakes": [
        {
          "mistake": "Renaming or dropping database columns in the same release as application code changes.",
          "correction": "Always use Expand-and-Contract: Step 1 (Add new column), Step 2 (Dual write to both), Step 3 (Backfill), Step 4 (Read from new), Step 5 (Drop old column in subsequent release)."
        }
      ],
      "interview_questions": [
        {
          "question": "How does the Expand-and-Contract (Parallel Change) pattern enable zero-downtime database schema migrations?",
          "answer": "It breaks destructive schema changes into non-breaking multi-phase deployments: first expanding the database with new columns/tables while maintaining backward compatibility with old code, running dual-writes, backfilling historical data, switching code to read the new schema, and finally contracting by removing deprecated columns in a future release."
        }
      ]
    },
    {
      "id": "feature-flags-and-gitops",
      "title": "Feature Flags (LaunchDarkly), Trunk-Based Development & GitOps",
      "definition": "Feature Flags (Feature Toggles) dynamically enable or disable features in production at runtime without redeploying code. GitOps uses Git repositories as the single source of truth for declaratively managed cloud infrastructure and application deployments (ArgoCD/Flux).",
      "why_we_need_it": "Decoupling code deployment from feature release allows engineering to deploy code continuously to production while product managers control when features go live to specific customer cohorts.",
      "real_world_analogy": "A physical light switch in an apartment: the electrician installs the wiring and fixtures weeks in advance (Code Deployment), but the lights only turn on when you flip the wall switch (Feature Flag).",
      "how_it_works": "<p>1. <strong>Feature Flag Evaluation:</strong> Evaluates flags in-memory in <1ms using local rule engines synced via streaming SSE from feature flag servers (LaunchDarkly, Unleash).<br>2. <strong>Targeted Rollouts:</strong> Enable feature for `@company.com` emails -> 10% beta users -> 100% global users.<br>3. <strong>GitOps Workflow:</strong> Developers push Kubernetes manifests to Git -> ArgoCD controller detects drift and reconciles live cluster state automatically.</p>",
      "conceptual_breakdown": [
        "<strong>Trunk-Based Development:</strong> Developers merge short-lived branches into `main` multiple times per day behind feature flags, eliminating painful merge conflicts.",
        "<strong>Kill Switches:</strong> Instant emergency shutdown of misbehaving micro-features in <1s without rollbacks.",
        "<strong>Technical Debt Warning:</strong> Stale feature flags must be systematically deleted once 100% rolled out."
      ],
      "failure_scenarios": "<strong>The Knight Capital Disastrous Stale Flag Bug:</strong> In 2012, Knight Capital repurposed a dead feature flag during an incomplete deployment, triggering dormant automated trading code that executed millions of erroneous financial trades, bankrupting the company ($440M loss) in 45 minutes. <em>Mitigation:</em> Treat feature flags with strict lifecycle audits and never repurpose old flags.",
      "common_mistakes": [
        {
          "mistake": "Leaving permanent feature flag conditionals littered throughout the codebase indefinitely.",
          "correction": "Create scheduled cleanup tickets to remove feature flag code branches within 2-4 weeks after 100% rollout."
        }
      ],
      "interview_questions": [
        {
          "question": "How do Feature Flags decouple Code Deployment from Feature Release?",
          "answer": "Code Deployment is a technical operation (moving binaries to production servers); Feature Release is a business operation (making functionality visible to users). Feature flags wrap new code in conditionals, allowing code to be deployed safely in a dormant state and activated dynamically at any time via UI controls."
        }
      ]
    }
  ]
}

# -------------------------------------------------------------
# MODULE 24: Real-World Case Studies 1: Social & Messaging
# -------------------------------------------------------------
mod_24 = {
  "module_id": "24",
  "module_title": "Real-World Case Studies 1: Social & Messaging",
  "description": "End-to-end interview blueprints: Design Twitter/X Newsfeed (Fan-out on write vs read), WhatsApp / Telegram Chat Architecture, and Instagram Photo Sharing.",
  "topics": [
    {
      "id": "design-twitter-newsfeed",
      "title": "Case Study: Design Twitter / X Newsfeed (Fan-Out on Write vs Read)",
      "definition": "Design a distributed real-time newsfeed system capable of handling 500 million Daily Active Users (DAU), 500 million tweets/day, and delivering customized chronological / ranked feeds with sub-200ms latency.",
      "why_we_need_it": "The definitive classic system design interview problem testing distributed caching, fan-out architectures, and handling extreme celebrity skew (Justin Bieber / Elon Musk problem).",
      "real_world_analogy": "A physical newspaper delivery vs a library corkboard: Fan-out on write is delivering a copy of your flyer into every follower's home mailbox the moment you write it. Fan-out on read is tacking the flyer on a central corkboard and making followers walk to the library to scan and assemble their own feed.",
      "how_it_works": "<p>1. <strong>Fan-out on Write (Push Model):</strong> When User A posts a tweet, background workers look up User A's followers and inject the tweet ID into every follower's in-memory Redis Home Timeline list (`LPUSH timeline:user_id tweet_id`). Reading feed is a lightning-fast `O(1)` Redis `LRANGE` operation.<br>2. <strong>The Celebrity Problem:</strong> If an account with 100 million followers tweets, fan-out on write requires 100 million Redis writes, locking servers and taking minutes.<br>3. <strong>Hybrid Fan-out Architecture (Production Solution):</strong> Normal users use Fan-out on Write. Celebrity users (>50,000 followers) bypass fan-out on write. When a user requests their feed, the system fetches their precomputed Redis feed AND dynamically fetches tweets from the few celebrities they follow (Fan-out on Read), merging the two lists in memory.</p>",
      "conceptual_breakdown": [
        "<strong>Twitter Scale Math:</strong> 500M DAU, 500M tweets/day = 6,000 tweets/sec avg (20,000 peak). Read QPS = 300,000 QPS (50:1 read/write ratio).",
        "<strong>Storage:</strong> Tweet metadata in PostgreSQL/DynamoDB; User timelines in Redis clusters (storing 800 most recent tweet IDs per active user in RAM).",
        "<strong>Media:</strong> Photos and videos uploaded directly to S3 via Presigned URLs, served via Global CDN."
      ],
      "arch_diagram": {
        "title": "Twitter / X Hybrid Fan-Out Architecture",
        "tiers": [
          {
            "label": "Client & Ingress",
            "nodes": [
              {
                "name": "Mobile / Web App",
                "type": "client",
                "icon": "📱",
                "what": "Twitter Mobile Client",
                "why": "Renders chronological & algorithmic feeds",
                "when": "User scrolls timeline",
                "failure": "Local client SQLite cache fallback"
              },
              {
                "name": "API Gateway / LB",
                "type": "gateway",
                "icon": "🛡️",
                "what": "Ingress Envoy Gateway",
                "why": "TLS termination & auth verification",
                "when": "Every incoming tweet or feed fetch",
                "failure": "Multi-region redundant failover"
              }
            ]
          },
          {
            "label": "Tweet & Fanout Services",
            "nodes": [
              {
                "name": "Tweet Service",
                "type": "service",
                "icon": "✍️",
                "what": "Tweet Creation Service",
                "why": "Persists tweet to DB and emits event to Kafka",
                "when": "On POST /tweets",
                "failure": "Queues tweet in local buffer"
              },
              {
                "name": "Fan-Out Engine",
                "type": "service",
                "icon": "⚡",
                "what": "Background Fan-out Workers",
                "why": "Evaluates follower graphs and populates Redis timelines",
                "when": "Consuming TweetCreated events",
                "failure": "Kafka consumer group auto-rebalance"
              }
            ]
          },
          {
            "label": "Storage & Timeline Caches",
            "nodes": [
              {
                "name": "Redis Timeline Cache",
                "type": "cache",
                "icon": "🔴",
                "what": "In-Memory User Timelines (ZSET / Lists)",
                "why": "Sub-5ms feed generation",
                "when": "User opens app / pulls to refresh",
                "failure": "Reconstructed from DB by background warmers"
              },
              {
                "name": "Tweet & User DB",
                "type": "database",
                "icon": "🗄️",
                "what": "Sharded PostgreSQL / Manhattan DB",
                "why": "Durable permanent storage of tweet entities",
                "when": "Cache misses and tweet writes",
                "failure": "Master-Replica automated failover"
              }
            ]
          }
        ]
      },
      "failure_scenarios": "<strong>Inactive User Redis RAM Bloat:</strong> Precomputing timelines for 500 million registered users who haven't logged in for 3 years wastes terabytes of expensive RAM. <em>Mitigation:</em> Only precompute timelines for users who were active within the last 14 days (Lazy loading on login for inactive users).",
      "common_mistakes": [
        {
          "mistake": "Using pure Fan-out on Read (`SELECT * FROM tweets WHERE user_id IN (following_ids) ORDER BY created_at DESC`) for all 500 million users.",
          "correction": "This generates catastrophic multi-million row JOIN queries under 300,000 QPS. Use the Hybrid Fan-Out model."
        }
      ],
      "interview_questions": [
        {
          "question": "How does Twitter handle the 'Celebrity Fan-out Problem' in production?",
          "answer": "Twitter uses a Hybrid approach: tweets from normal users are pushed into their followers' Redis timelines immediately on write (Fan-out on Write). Tweets from celebrity accounts with millions of followers bypass fan-out on write; instead, when a user opens their feed, the system dynamically pulls and merges the latest tweets from any celebrities that user follows (Fan-out on Read)."
        }
      ]
    },
    {
      "id": "design-whatsapp-chat-messenger",
      "title": "Case Study: Design WhatsApp / Messenger (1-on-1 & Group Chat Architecture)",
      "definition": "Design a globally distributed instant messaging platform supporting 2 billion users, end-to-end encryption (Signal Protocol), 100 billion messages/day, online presence status, and group messaging.",
      "why_we_need_it": "Tests persistent bi-directional WebSocket connection management, ephemeral message delivery pipelines, distributed presence tracking, and offline message storage.",
      "real_world_analogy": "A dedicated pneumatic tube system between every pair of office desks: when you drop a capsule in, it shoots instantly to your colleague's desk if they are sitting there. If their desk is empty, the capsule drops into their locked drawer until they return.",
      "how_it_works": "<p>1. <strong>Connection Gateway:</strong> Millions of mobile clients maintain persistent TCP/WebSocket connections to a fleet of distributed Chat Gateway servers (e.g. built with Erlang/Elixir BEAM or Netty).<br>2. <strong>User Session Registry:</strong> A distributed Redis cluster maps `user_id -> Gateway_Server_ID` (e.g., `Alice -> Gateway-14`, `Bob -> Gateway-89`).<br>3. <strong>Message Delivery Flow (1-on-1):</strong> Alice sends message to Gateway-14. Gateway looks up Bob in Session Registry -> forwards message to Gateway-89 -> Gateway-89 pushes message down Bob's active WebSocket connection.<br>4. <strong>Offline Queue:</strong> If Bob is offline, message is stored in an ephemeral Cassandra/DynamoDB offline queue. When Bob reconnects, he pulls all pending offline messages, and the server deletes them upon ACK.<br>5. <strong>Group Chat:</strong> Group service expands group membership list and creates individual fan-out delivery jobs for each member.</p>",
      "conceptual_breakdown": [
        "<strong>End-to-End Encryption (E2EE):</strong> WhatsApp servers CANNOT read message contents; servers only route encrypted ciphertext blobs between public keys.",
        "<strong>Message Statuses:</strong> Single Tick (Sent to server), Double Grey Tick (Delivered to recipient phone), Blue Double Tick (Read by user).",
        "<strong>Presence Engine:</strong> Heartbeat pings every 30s update Redis TTL key `presence:{user_id}`."
      ],
      "failure_scenarios": "<strong>Massive Group Chat Message Multiplication:</strong> A group with 1,000 members where 50 users are texting simultaneously generates $50 \\times 1,000 = 50,000$ messages per second. <em>Mitigation:</em> Client-side group message pulling and batching via Kafka topics."
    }
  ]
}

# -------------------------------------------------------------
# MODULE 25: Real-World Case Studies 2: Video & Streaming
# -------------------------------------------------------------
mod_25 = {
  "module_id": "25",
  "module_title": "Real-World Case Studies 2: Video & Streaming",
  "description": "End-to-end interview blueprints: Design YouTube (Video Ingestion, Transcoding DAG & CDN Delivery), Netflix Global Streaming Architecture, and Twitch Live Streaming.",
  "topics": [
    {
      "id": "design-youtube-video-platform",
      "title": "Case Study: Design YouTube (Video Ingestion, Transcoding DAG & Adaptive Bitrate)",
      "definition": "Design a global video sharing and streaming platform supporting 2 billion users, 500 hours of video uploaded every minute, multi-resolution adaptive bitrate streaming (HLS/DASH), and sub-2-second video start times.",
      "why_we_need_it": "Tests massive blob storage pipelines, distributed asynchronous task DAG processing, video encoding codecs, and CDN video chunk streaming.",
      "real_world_analogy": "A global movie film factory: filmmakers upload massive raw film reels (Raw Video). A giant robotic assembly line (Transcoding DAG) cuts the film into 10-second clips, compresses them into 4K, 1080p, 720p, 480p, and 360p formats, and stocks every neighborhood video store (CDN Edge) in the world.",
      "how_it_works": "<p>1. <strong>Direct-to-S3 Upload:</strong> Client requests Presigned URL from API Gateway and uploads raw MP4/MOV chunks directly to S3 Raw Video Bucket in parallel.<br>2. <strong>Transcoding DAG Engine:</strong> S3 upload event triggers an asynchronous Directed Acyclic Graph (DAG) workflow (e.g. AWS Step Functions / Temporal / Celery).<br>3. <strong>Video Chunking & Parallel Encoding:</strong> Raw video is split into 10-second segments. Worker nodes transcode segments in parallel across multiple codecs (H.264, H.265, AV1) and resolutions (1080p, 720p, 480p, 360p).<br>4. <strong>Packaging & Manifests:</strong> Transcoded chunks are assembled into HLS (`.m3u8` playlist) and DASH (`.mpd`) formats and stored in S3 Output Bucket.<br>5. <strong>Adaptive Bitrate Streaming (ABR):</strong> Video player client detects live network bandwidth and switches quality dynamically (e.g. drops from 1080p to 480p when mobile signal weakens) without buffering.</p>",
      "conceptual_breakdown": [
        "<strong>Adaptive Bitrate (ABR):</strong> Client player measures download time of 10s chunks and requests higher/lower bitrate chunk from `.m3u8` playlist accordingly.",
        "<strong>Video Deduplication:</strong> Compute perceptual hash on first 60s of video to detect and reject duplicate re-uploads.",
        "<strong>Thumbnail Generation:</strong> Distributed workers extract 5 frame snapshots at $0\\%, 25\\%, 50\\%, 75\\%, 100\\%$ video timestamps."
      ],
      "comparison_matrix": {
        "title": "Video Streaming Protocols Comparison",
        "columns": ["Protocol", "Transport", "Chunk Duration", "Latency", "Best Use Case"],
        "rows": [
          ["HLS (HTTP Live Streaming)", "Standard HTTP/HTTPS", "2 - 6 seconds", "Moderate (4 - 10s)", "YouTube, Netflix VOD, general mobile video"],
          ["DASH (Dynamic Adaptive Streaming)", "Standard HTTP/HTTPS", "2 - 4 seconds", "Moderate (3 - 8s)", "Modern web players, open standard VOD"],
          ["LL-HLS (Low Latency HLS)", "HTTP/2 Partial Chunks", "0.5 - 1 second", "Low (1 - 2s)", "Sports streaming, live interactive events"],
          ["WebRTC", "UDP / SRTP", "Continuous frame stream", "Ultra-Low (<500ms)", "Twitch streamer chat, Zoom, video calls"]
        ]
      },
      "failure_scenarios": "<strong>Transcoding Worker Crash Mid-Job:</strong> A worker node running a 45-minute FFmpeg encoding job runs out of memory. <em>Mitigation:</em> Transcode videos as independent 10-second chunks rather than a single monolithic file. If a chunk fails, only that 10s chunk retries.",
      "common_mistakes": [
        {
          "mistake": "Transcoding raw multi-gigabyte video files sequentially on a single server node.",
          "correction": "Split video into independent GOP (Group of Pictures) chunks and transcode them in parallel across a distributed worker fleet."
        }
      ],
      "interview_questions": [
        {
          "question": "How does Adaptive Bitrate Streaming (ABR) work in modern video players like YouTube?",
          "answer": "The video is split into short 2-6 second chunks encoded at multiple bitrates (360p, 720p, 1080p, 4K) described in a master playlist manifest (`.m3u8`). The client player continuously measures real-time network throughput; if bandwidth drops, the player seamlessly requests the next 4-second chunk at a lower bitrate without interrupting playback."
        }
      ]
    },
    {
      "id": "design-netflix-global-streaming",
      "title": "Case Study: Design Netflix (Open Connect Appliance CDN & Pre-Positioning)",
      "definition": "Design Netflix's streaming architecture capable of delivering 15% of global internet downstream traffic with zero buffering using Open Connect Appliances (OCA) embedded directly inside ISP networks.",
      "why_we_need_it": "Commercial CDNs charge billions for petabyte-scale video traffic. Netflix's Open Connect custom CDN architecture demonstrates extreme edge caching economics.",
      "real_world_analogy": "A vending machine company placing fully stocked vending machines inside every corporate office building: instead of delivering each soda can across the city on a truck when someone is thirsty, the machine is pre-stocked overnight during off-peak hours.",
      "how_it_works": "<p>1. <strong>Control Plane (AWS Cloud):</strong> User registration, recommendation algorithms, search, billing, and content management run on AWS.<br>2. <strong>Data Plane (Open Connect Appliances - OCA):</strong> Netflix builds custom high-density FreeBSD storage servers (100Gbps+ throughput) and installs them physically inside thousands of Internet Service Provider (ISP) data centers globally for FREE.<br>3. <strong>Predictive Proactive Caching (Pre-Positioning):</strong> Machine learning models predict which movies will be popular in each city. During off-peak night hours (2 AM - 5 AM), Netflix pushes new movie releases directly to local ISP OCAs.<br>4. <strong>Stream Request:</strong> When user clicks Play, AWS directs client to the exact local OCA inside their ISP router, streaming video over local fiber with 0 cross-continental transit fees.</p>",
      "conceptual_breakdown": [
        "<strong>OCA Pre-Positioning:</strong> Eliminates daytime internet transit congestion by pushing video files during night hours.",
        "<strong>Title Chunking:</strong> Every movie is encoded into ~120 different file variations (resolutions, languages, codecs, bitrates).",
        "<strong>Multi-OCA Failover:</strong> If local ISP OCA is busy, client smoothly fails over to regional Internet Exchange Point (IXP) OCA."
      ]
    }
  ]
}

modules = [mod_21, mod_22, mod_23, mod_24, mod_25]
for m in modules:
    filename = os.path.join(CONTENT_DIR, f"module_{m['module_id']}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print(f"Generated {filename} with {len(m['topics'])} topics")
