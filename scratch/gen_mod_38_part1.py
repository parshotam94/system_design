# Real-World System Design Case Studies: Problems 1 to 7
import json

topics_part1 = [
    {
        "id": "design-url-shortener-tinyurl",
        "title": "Problem 1 (Beginner): Design a URL Shortener (TinyURL / Bitly)",
        "definition": "A URL Shortening Service (e.g., TinyURL, Bitly) provides short aliases (e.g., `https://tiny.cc/xyz89`) for long, unwieldy URLs. When a user clicks the shortened URL, the service resolves the alias and redirects the browser to the original target URL using HTTP redirection (301 Permanent vs 302/307 Temporary).",
        "why_we_need_it": "### System Requirements\n**Functional Requirements:**\n1. Given a long URL, generate a unique, short 7-character alias.\n2. When accessing the short URL, redirect to original URL with minimal latency ($<20$ms).\n3. Custom URL alias support (optional vanity URLs).\n4. Configurable link expiration (TTL) and basic click analytics.\n\n**Non-Functional Requirements:**\n1. Ultra-high availability ($99.99\\%$) and low-latency reads ($<10$ms).\n2. Read-heavy system: Read to Write ratio is 100:1.\n3. URLs must not be easily guessable (security against sequential enumeration).\n\n### Capacity Estimations\n- **Write Traffic:** 100 million new URLs created per month $\\rightarrow \\frac{100M}{30 \\times 86400} \\approx 40$ writes/sec.\n- **Read Traffic (100:1):** $40 \\times 100 = 4,000$ redirects/sec (Peak: 8,000 QPS).\n- **Storage (5 Years):** $100M \\times 12 \\times 5 = 6 \\text{ billion URLs}$. At 500 bytes per record: $6B \\times 500B \\approx 3 \\text{ Terabytes}$ total storage.\n- **Cache Memory:** 80-20 Pareto Rule: Cache top 20% daily read requests. Daily reads: $4,000 \\times 86,400 \\approx 350M$ requests. Cache size: $350M \\times 0.2 \\times 500B \\approx 35 \\text{ GB RAM}$ (easily fits in 1 Redis node).",
        "real_world_analogy": "Imagine a coat-check room at a luxury opera house. Instead of dragging your giant heavy winter coat, luggage, and umbrella into the theater seat, the attendant takes your items, places them in a large locker in the back vault (Long URL), and hands you a tiny plastic claim token with a 4-digit number: #4928 (Short URL). When the opera ends, you present token #4928, and the attendant instantly retrieves your coat.",
        "how_it_works": "<p>Designing TinyURL involves key encoding and routing decisions:</p><ol><li><strong>Encoding Strategy: Base62 vs Hashing:</strong> An alphanumeric character set <code>[a-zA-Z0-9]</code> yields 62 distinct characters. With a 7-character string: $62^7 \\approx 3.52 \\text{ trillion}$ unique combinations, comfortably exceeding our 6 billion requirement.</li><li><strong>Counter-Based Base62 vs MD5 Hashing:</strong> Hashing the long URL via MD5 produces 128 bits; taking the first 43 bits (7 Base62 chars) risks hash collisions. If two users submit the same URL, or distinct URLs produce the same prefix, collision resolution requires recursive DB lookups. The optimal approach is a <strong>Distributed Unique ID Generator (Twitter Snowflake or Range Ticket Server)</strong> that generates a monotonic 64-bit integer ID, converted directly to Base62 (e.g., ID <code>11,157,105</code> $\\rightarrow$ Base62 <code>'aZ2'</code>). Zero collisions, guaranteed $O(1)$.</li><li><strong>HTTP Redirection Code (301 vs 302):</strong> <code>301 Moved Permanently</code> causes browsers to cache the redirection locally, reducing backend load to zero on repeat clicks, but preventing the service from tracking click analytics. <code>302 Found</code> or <code>307 Temporary Redirect</code> forces the browser to contact the URL shortener on every click, enabling accurate real-time analytics.</li><li><strong>Storage Schema:</strong> NoSQL Key-Value store (DynamoDB / Cassandra) or sharded PostgreSQL: <code>short_hash (PK)</code>, <code>original_url</code>, <code>user_id</code>, <code>created_at</code>, <code>expires_at</code>.</li></ol>",
        "conceptual_breakdown": [
            {
                "concept": "Base62 Encoding Algorithm",
                "explanation": "Converting a 64-bit integer into Base62 by repeated division by 62 and mapping remainders to the character set `0-9a-zA-Z`. Guarantees deterministic, collision-free bidirectional translation."
            },
            {
                "concept": "Distributed Ticket Range Allocator",
                "explanation": "To prevent a single auto-incrementing DB bottleneck, a central coordinator (ZooKeeper/etcd) assigns ID ranges to application servers (e.g., Server 1 gets range 1M-2M; Server 2 gets 2M-3M). Servers increment IDs in memory without distributed locks."
            },
            {
                "concept": "Preventing Sequential Scraping",
                "explanation": "Sequential Base62 IDs make it trivial for attackers to scrape all URLs (`/a`, `/b`, `/c`). Mitigate by applying a Feistel cipher or token shuffling to randomize the integer before Base62 encoding."
            },
            {
                "concept": "Purging Expired Links",
                "explanation": "Active periodic deletion scans slow down the database. Instead, use Lazy Expiration (check `expires_at` on read; if expired, return 404 and delete) combined with a slow background batch cleaner during off-peak hours."
            }
        ],
        "arch_diagram": {
            "nodes": [
                {"id": "client", "label": "Client Browser / App", "type": "client", "tier": "client"},
                {"id": "cdn", "label": "Edge CDN / Route 53", "type": "cache", "tier": "cache"},
                {"id": "lb", "label": "Application Load Balancer", "type": "service", "tier": "service"},
                {"id": "app", "label": "Shortener App Servers (Base62)", "type": "service", "tier": "service"},
                {"id": "redis", "label": "Redis Cache Cluster (Top 20% Keys)", "type": "cache", "tier": "cache"},
                {"id": "db", "label": "DynamoDB / Sharded SQL (Key-Value)", "type": "database", "tier": "database"},
                {"id": "kafka", "label": "Kafka Click Analytics Stream", "type": "queue", "tier": "queue"}
            ],
            "connections": [
                {"from": "client", "to": "cdn", "label": "1. GET /xyz89", "type": "sync"},
                {"from": "cdn", "to": "lb", "label": "2. Cache Miss -> LB", "type": "sync"},
                {"from": "lb", "to": "app", "label": "3. Forward Request", "type": "sync"},
                {"from": "app", "to": "redis", "label": "4. Check Cache (1ms)", "type": "sync"},
                {"from": "app", "to": "db", "label": "5. On Miss -> Fetch Long URL", "type": "sync"},
                {"from": "app", "to": "kafka", "label": "6. Emit Click Event (Async)", "type": "async"},
                {"from": "app", "to": "client", "label": "7. HTTP 302 Found (Location: target)", "type": "sync"}
            ]
        },
        "comparison_matrix": {
            "headers": ["Generation Approach", "MD5 Hash Truncation", "Distributed Snowflake ID + Base62", "Random String Generation + DB Check"],
            "rows": [
                ["Collision Probability", "Possible (requires retry loop)", "Zero (mathematically impossible)", "High as space fills up"],
                ["Lookup Overhead", "Requires DB lookup on collision", "Zero collision check needed ($O(1)$)", "Severe DB read penalty before every insert"],
                ["ID Length", "Fixed 7 characters", "Dynamic (grows smoothly with ID)", "Fixed length"],
                ["Predictability", "Random looking", "Sequential (requires bit permutation)", "Completely random"]
            ]
        },
        "tradeoffs": [
            {"factor": "HTTP 301 vs 302 Redirection", "analysis": "301 Permanent saves origin bandwidth because browsers cache the redirect, but strips the business of click analytics and monetization. 302/307 Temporary requires hitting origin on every click, allowing granular analytics at the cost of infrastructure scaling."},
            {"factor": "Relational SQL vs NoSQL Key-Value", "analysis": "TinyURL requires zero complex joins or multi-table ACID transactions. A NoSQL key-value store (DynamoDB or Redis) offers effortless horizontal partitioning and single-digit millisecond latency under billions of keys."}
        ],
        "failure_scenarios": [
            {
                "scenario": "ID Range Generator Node Dies Abruptly",
                "impact": "Application server holding Range 1M to 2M crashes while at ID 1.2M.",
                "mitigation": "The unused 800k IDs in that range are simply skipped and abandoned. Range gaps in a 3.5 trillion namespace are completely harmless."
            },
            {
                "scenario": "Viral Short URL Causes Cache Hotspot",
                "impact": "A viral link receives 100k clicks/second, overloading a single Redis shard.",
                "mitigation": "Enable Read Replicas on Redis, or cache the redirect mapping directly at Cloudflare/Fastly CDN edge PoPs with a 60-second TTL."
            }
        ],
        "common_mistakes": [
            {
                "mistake": "Using MD5 hash and checking database for collisions in a tight while-loop",
                "correction": "As the table reaches billions of rows, hash collisions multiply, creating catastrophic database lock contention. Use distributed ID generation + Base62 conversion."
            },
            {
                "mistake": "Storing sequential IDs directly in the public short URL (`/1`, `/2`, `/3`)",
                "correction": "Allows competitors to scrape your entire customer database and estimate company transaction volume. Permute or encrypt the integer ID before Base62 encoding."
            }
        ],
        "interview_questions": [
            {
                "question": "How does the Base62 encoding algorithm work, and why Base62 instead of Base64?",
                "answer": "Base62 utilizes characters `[0-9a-zA-Z]` (10 digits + 26 lowercase + 26 uppercase = 62 characters). Base64 includes `+` and `/` (or `=` for padding). In HTTP URLs, characters like `+`, `/`, and `=` have reserved protocol meanings (e.g., path separators or query delimiters) and must be URL-encoded, which expands URL length and causes parsing bugs. Base62 consists strictly of alphanumeric characters that are 100% URL-safe without escaping."
            },
            {
                "question": "How do you handle custom (vanity) URLs like 'tiny.cc/my-summer-sale'?",
                "answer": "Maintain a secondary lookup or single index where `short_hash` can be either the Base62 generated token or the custom string. Impose validation rules (length 4-25 characters, alphanumeric and hyphens). When creating a custom URL, run an atomic `INSERT ... ON CONFLICT DO NOTHING` against the datastore. If the write fails due to unique constraint violation, return HTTP 409 Conflict ('Custom alias already taken')."
            }
        ]
    },
    {
        "id": "design-pastebin-storage",
        "title": "Problem 2 (Beginner): Design Pastebin / Text Sharing Service",
        "definition": "Pastebin is a text storage and sharing web service that allows users to upload plain text blocks or source code snippets and receive a unique shareable URL. The system stores multi-megabyte text documents durably, enforces expiration policies, and allows users to set access privacy (public, unlisted, password-protected).",
        "why_we_need_it": "### System Requirements\n**Functional Requirements:**\n1. Upload text paste (up to 10MB) and generate unique link.\n2. Retrieve paste content via unique link with high throughput.\n3. Optional paste expiration (1 hour, 1 day, never).\n4. Read-only pastes (no edits after creation).\n\n**Non-Functional Requirements:**\n1. Strict durability (uploaded text must never be lost or corrupted).\n2. Read-heavy system (50:1 read to write ratio).\n3. Low read latency ($<30$ms).\n\n### Capacity Estimations\n- **Writes:** 1 million pastes uploaded per day $\\approx 12$ pastes/sec.\n- **Reads:** $12 \\times 50 = 600$ reads/sec.\n- **Storage Volume:** Average paste size = 50 KB. Daily storage: $1M \\times 50\\text{KB} = 50\\text{ GB/day}$. Annual storage: $50\\text{GB} \\times 365 \\approx 18 \\text{ Terabytes/year}$. Over 5 years: ~90 TB.\n- **Architecture Separation:** Storing 90 TB of multi-kilobyte text blobs directly inside relational database tables (like PostgreSQL or MySQL) degrades buffer pools and inflates backup costs. Metadata and text blobs must be decoupled.",
        "real_world_analogy": "Imagine a public storage locker facility. When you arrive with a giant trunk of documents, the manager doesn't shove the giant trunk into the tiny front-desk filing cabinet next to the receipt book. Instead, the manager places your trunk into a large industrial warehouse in the back (Object Storage: Amazon S3), and writes only your Name, Locker Number, and Expiration Date onto a 3x5 index card in the front-desk card catalog (Metadata Database).",
        "how_it_works": "<p>A scalable Pastebin architecture decouples metadata from blob storage:</p><ol><li><strong>Storage Decoupling:</strong> The actual text content is stored as an immutable object in distributed Object Storage (Amazon S3 / Google Cloud Storage / MinIO). The metadata record (Paste ID, Owner ID, S3 Object Path, Creation Time, Expiration Time, Character Count, Encryption Salt) is stored in a scalable NoSQL Key-Value database (DynamoDB / Cassandra) or PostgreSQL.</li><li><strong>Write Path:</strong> Client POSTs text content to API Gateway. Application server generates a unique Paste ID (via Base62 ID generator), uploads the raw text bytes to S3 at key <code>pastes/{paste_id}.txt</code>, writes the metadata row to DynamoDB, and returns the short URL to the client.</li><li><strong>Read Path:</strong> Client requests <code>GET /pastes/{paste_id}</code>. Application checks Redis cache for hot pastes. On cache miss, queries DynamoDB for metadata; if expired, returns 404. Otherwise, fetches the text blob from S3 (or generates a pre-signed S3 URL / CDN edge fetch) and returns the raw text.</li><li><strong>TTL & Purging:</strong> Cloud Object Storage (S3) provides native Object Lifecycle Management rules that automatically delete or transition expired objects based on tags or prefixes with zero server CPU overhead.</li></ol>",
        "conceptual_breakdown": [
            {
                "concept": "Blob Storage vs Database BLOBs",
                "explanation": "Storing large text blobs directly in relational database rows bloats B-trees and table pages, evicting indexes from memory buffer pools. Offloading text to S3 reduces database row size to <200 bytes."
            },
            {
                "concept": "Direct Upload via Pre-Signed S3 URLs",
                "explanation": "For large 10MB pastes, application servers shouldn't buffer megabytes of payload. The client requests an upload authorization; the API returns a pre-signed S3 URL. The client uploads the text directly to S3, bypassing app server memory."
            },
            {
                "concept": "Content Compression (Gzip / Snappy)",
                "explanation": "Source code and text compress exceptionally well (~60-70% ratio). Compressing pastes before writing to S3 slashes storage and network egress costs by more than half."
            },
            {
                "concept": "DDoS and Paste Spam Prevention",
                "explanation": "Pastebins are prime targets for bot scrapers and malware distribution. Implement IP-based token bucket rate limiting and integrate automated virus/malware scanning (ClamAV) on uploaded blobs."
            }
        ],
        "arch_diagram": {
            "nodes": [
                {"id": "user", "label": "Client Browser / CLI (cURL)", "type": "client", "tier": "client"},
                {"id": "gw", "label": "API Gateway (Rate Limiter)", "type": "service", "tier": "service"},
                {"id": "app", "label": "Pastebin Service (App Tier)", "type": "service", "tier": "service"},
                {"id": "s3", "label": "Object Store: S3 / MinIO (Raw Text Blobs)", "type": "database", "tier": "database"},
                {"id": "db", "label": "Metadata DB (DynamoDB / Postgres)", "type": "database", "tier": "database"},
                {"id": "redis", "label": "Redis Cache (Hot Pastes)", "type": "cache", "tier": "cache"}
            ],
            "connections": [
                {"from": "user", "to": "gw", "label": "1. POST /paste (50KB Text)", "type": "sync"},
                {"from": "gw", "to": "app", "label": "2. Route Request", "type": "sync"},
                {"from": "app", "to": "s3", "label": "3. PUT pastes/{id}.txt", "type": "sync"},
                {"from": "app", "to": "db", "label": "4. Save Metadata (TTL, S3 Key)", "type": "sync"},
                {"from": "user", "to": "app", "label": "5. GET /p/{id}", "type": "sync"},
                {"from": "app", "to": "redis", "label": "6. Cache Check", "type": "sync"},
                {"from": "app", "to": "s3", "label": "7. Fetch Blob on Miss", "type": "sync"}
            ]
        },
        "comparison_matrix": {
            "headers": ["Architectural Parameter", "All-in-Database (BLOB columns)", "S3 Object Store + Metadata DB", "Distributed File System (NFS/Ceph)"],
            "rows": [
                ["Storage Cost per GB", "High ($0.10 - $0.25/GB)", "Extremely Low ($0.023/GB)", "Moderate ($0.05/GB)"],
                ["DB Buffer Pool Impact", "Severe (large text evicts index pages)", "Zero (DB stores only lean metadata)", "Zero"],
                ["Max Payload Support", "Restricted by DB packet limits", "Up to 5 Terabytes per object", "Limited by disk partitions"],
                ["Lifecycle Management", "Requires expensive SQL DELETE sweeps", "Native automated S3 lifecycle rules", "Requires custom cron cleanup scripts"]
            ]
        },
        "tradeoffs": [
            {"factor": "Two-Phase Upload vs Single Request Simplicity", "analysis": "Uploading directly to S3 via pre-signed URLs eliminates app server memory bottlenecks, but requires the client to execute a two-step handshake. For standard pastes ($<100$KB), routing through the app server is simpler."},
            {"factor": "Full-Text Search vs Storage Costs", "analysis": "Indexing 90TB of arbitrary code snippets in Elasticsearch is financially exorbitant. Restrict search to metadata (title, author, tags) or support search only for authenticated enterprise users."}
        ],
        "failure_scenarios": [
            {
                "scenario": "S3 Write Succeeds But Metadata DB Write Fails",
                "impact": "An orphaned text blob exists in S3 with no database reference.",
                "mitigation": "S3 lifecycle policies prune unreferenced objects after 7 days, or execute metadata write first with status `PENDING_UPLOAD`."
            },
            {
                "scenario": "Abusive Client Spams 10,000 Large Pastes per Minute",
                "impact": "Consumes S3 bandwidth and generates excessive small objects.",
                "mitigation": "Enforce strict per-IP rate limiting (10 pastes/min), CAPTCHA verification for anonymous users, and file size quotas."
            }
        ],
        "common_mistakes": [
            {
                "mistake": "Storing 50KB text pastes directly inside MongoDB or MySQL rows",
                "correction": "Databases are engineered for structured query indexing, not bulk unstructured document storage. Offload raw text to S3 object storage."
            },
            {
                "mistake": "Running `DELETE FROM pastes WHERE expires_at < NOW()` on a 500M row SQL table",
                "correction": "Massive SQL deletes lock table pages and cause transaction log bloat. Use S3 Object Lifecycle rules or partition tables by day and drop old partitions."
            }
        ],
        "interview_questions": [
            {
                "question": "Why is S3 object storage superior to a relational database for storing paste text bodies?",
                "answer": "Relational databases store data in fixed-size 8KB or 16KB data pages loaded into memory buffer pools. Large multi-kilobyte text blobs span multiple pages, pushing hot index pages out of RAM and destroying query caching. S3 is designed specifically for unstructured blobs: it provides 11 9s durability, near-infinite capacity, built-in automated expiration lifecycle policies, and costs 5-10x less per gigabyte than database SSD storage."
            },
            {
                "question": "How do you implement client-side end-to-end encryption for sensitive pastes?",
                "answer": "The client browser generates an AES-256 encryption key and encrypts the text *locally* in JavaScript before dispatching to the API. The encryption key is included *only* in the URL fragment/hash (e.g., `https://pastebin.com/p/xyz#mySecretKey123`). Because RFC 3986 specifies that URL fragments after `#` are never sent over the network to the HTTP server, the backend server and database only ever see and store encrypted ciphertext. When another user opens the URL, their browser parses the key from the fragment and decrypts the text locally."
            }
        ]
    },
    {
        "id": "design-scalable-notification-system",
        "title": "Problem 3 (Beginner): Design a Scalable Notification Service (SMS, Email, Push)",
        "definition": "A Scalable Notification Service is a centralized, distributed platform responsible for delivering millions of notifications across multiple outbound channels: Mobile Push Notifications (APNs, FCM), SMS text messages (Twilio), Email (SendGrid, Amazon SES), and In-App notification feeds, guaranteeing reliable delivery, rate limiting, and user preference enforcement.",
        "why_we_need_it": "### System Requirements\n**Functional Requirements:**\n1. Send notifications across Push (iOS/Android), SMS, and Email.\n2. Support real-time transactional alerts (OTP codes, order updates) and delayed bulk marketing broadcasts.\n3. User Notification Preferences (e.g., mute SMS, enable email only for billing).\n4. Deduplication (prevent sending duplicate notifications during network retries).\n\n**Non-Functional Requirements:**\n1. High throughput (100 million notifications/day $\\approx 1,200$ notifications/sec average, 10,000/sec peak).\n2. Low latency for transactional alerts (OTP delivered in $<5$ seconds).\n3. Fault tolerance: Third-party vendor outages (e.g., Twilio outage) must not cause message loss.\n\n### Challenges\nThird-party gateway providers impose strict rate limits and suffer intermittent downtime. Synchronously calling external APIs inside business flows causes thread exhaustion. A decoupled, queue-driven worker architecture with prioritization is mandatory.",
        "real_world_analogy": "Imagine a multinational post office sorting facility: incoming letters arrive from courtrooms (critical legal notices), banks (credit card OTPs), and clothing brands (marketing flyers). The post office does not hand all letters to one mail carrier. It sorts mail into three distinct priority conveyor belts: (1) Urgent Express (OTP/Transactional); (2) Standard First-Class; (3) Bulk Media Mail. Independent delivery fleets handle airplanes, trucks, and couriers.",
        "how_it_works": "<p>A notification platform operates as a multi-tier asynchronous pipeline:</p><ol><li><strong>Notification Request Ingestion:</strong> Upstream microservices (Order, Auth, Billing) call <code>POST /v1/notifications</code> with <code>recipient_id</code>, <code>event_type</code>, <code>template_id</code>, and <code>parameters</code>. The API Gateway validates schemas and authenticates callers.</li><li><strong>User Preference & Opt-Out Evaluation:</strong> Notification Service checks the User Preference Cache (Redis): if the user has disabled marketing push notifications, the message is discarded immediately.</li><li><strong>Template Engine & Personalization:</strong> Fetches parameterized templates (e.g., <code>'Hi {{name}}, your order #{{order_id}} has shipped!'</code>) and hydrates personalized content.</li><li><strong>Priority Queue Fan-out:</strong> Enqueues jobs into channel-specific, priority-segmented Kafka topics or RabbitMQ queues: <code>queue:sms:critical</code>, <code>queue:push:normal</code>, <code>queue:email:bulk</code>.</li><li><strong>Channel Worker Fleets:</strong> Dedicated autoscaled worker clusters pull jobs from queues and interface with third-party providers: (a) <em>Push Workers:</em> Apple Push Notification service (APNs) & Firebase Cloud Messaging (FCM); (b) <em>SMS Workers:</em> Twilio / MessageBird; (c) <em>Email Workers:</em> Amazon SES / SendGrid.</li><li><strong>Vendor Fallback & Circuit Breaker:</strong> If Twilio returns 500 errors or rate limits, SMS workers automatically fail over to a backup provider (e.g., Infobip).</li></ol>",
        "conceptual_breakdown": [
            {
                "concept": "Priority Queuing (OTP vs Marketing)",
                "explanation": "If a marketing campaign of 10 million emails is queued, a user requesting a password reset OTP must not wait behind 10 million marketing messages. Separate physical queues guarantee transactional OTPs are serviced with zero delay."
            },
            {
                "concept": "Deduplication via Idempotency Key",
                "explanation": "If an upstream service retries an order confirmation call, the notification engine checks an `inbox_notifications` table with key `hash(user_id, event_id, date)` to discard duplicate alerts."
            },
            {
                "concept": "Third-Party Rate Limiting Compliance",
                "explanation": "Third-party APIs (like Twilio) enforce hard quotas (e.g., 100 SMS/sec per shortcode). Workers use token bucket rate limiters to pace outbound requests and prevent 429 account suspensions."
            },
            {
                "concept": "User Quiet Hours & Batching",
                "explanation": "Non-urgent notifications scheduled during night hours (10:00 PM to 8:00 AM in user's local timezone) are delayed and batched into a morning digest."
            }
        ],
        "arch_diagram": {
            "nodes": [
                {"id": "services", "label": "Internal Microservices (Auth / Order)", "type": "service", "tier": "service"},
                {"id": "api", "label": "Notification Ingress API", "type": "service", "tier": "service"},
                {"id": "pref_cache", "label": "User Preferences (Redis / DB)", "type": "cache", "tier": "cache"},
                {"id": "q_crit", "label": "Priority Queue: HIGH (OTP / Alerts)", "type": "queue", "tier": "queue"},
                {"id": "q_bulk", "label": "Priority Queue: LOW (Marketing)", "type": "queue", "tier": "queue"},
                {"id": "workers", "label": "Channel Worker Pool", "type": "service", "tier": "service"},
                {"id": "vendors", "label": "Third-Party Gateways (APNs, FCM, Twilio, SES)", "type": "service", "tier": "service"}
            ],
            "connections": [
                {"from": "services", "to": "api", "label": "1. POST /notify", "type": "sync"},
                {"from": "api", "to": "pref_cache", "label": "2. Verify Opt-in & Quiet Hours", "type": "sync"},
                {"from": "api", "to": "q_crit", "label": "3a. Enqueue Critical OTP", "type": "async"},
                {"from": "api", "to": "q_bulk", "label": "3b. Enqueue Marketing Digest", "type": "async"},
                {"from": "q_crit", "to": "workers", "label": "4. Workers Consume High Priority First", "type": "async"},
                {"from": "workers", "to": "vendors", "label": "5. Outbound HTTPS Dispatch", "type": "sync"}
            ]
        },
        "comparison_matrix": {
            "headers": ["Notification Channel", "Protocol / Mechanism", "Latency SLA", "Cost per Message", "Reliability Characteristics"],
            "rows": [
                ["Mobile Push (APNs / FCM)", "HTTP/2 persistent socket to Apple/Google", "< 2 seconds", "Free (included in OS platform)", "Best-effort; messages dropped if device offline for weeks"],
                ["SMS Text Message", "SMPP / REST API to Telco Aggregator", "< 5 seconds (OTP)", "High ($0.007 - $0.05/msg)", "High deliverability directly to cellular towers"],
                ["Email (SES / SendGrid)", "SMTP / REST API to Mail Transfer Agent", "< 30 seconds", "Extremely Low ($0.10 per 1,000 emails)", "Subject to spam filters, bounce handling, and domain reputation"]
            ]
        },
        "tradeoffs": [
            {"factor": "Multi-Vendor Redundancy vs Cost", "analysis": "Integrating secondary backup providers (Twilio primary, Infobip secondary) doubles integration maintenance but guarantees business continuity when primary telecommunications carriers fail."},
            {"factor": "Instant Send vs Message Aggregation (Digests)", "analysis": "Sending notifications immediately provides real-time satisfaction, but sending 20 separate push alerts during an active chat thread annoys users. Aggregating into a single digest improves user retention."}
        ],
        "failure_scenarios": [
            {
                "scenario": "Twilio SMS Outage During Flash Sale",
                "impact": "SMS OTP delivery stalls, preventing users from logging in or checking out.",
                "mitigation": "Circuit breaker detects Twilio 5xx rate > 20% and trips. Worker fleet automatically diverts outbound SMS payloads to AWS SNS or Infobip fallback gateway."
            },
            {
                "scenario": "Invalid Device Tokens Result in APNs Rate Throttling",
                "impact": "Sending push notifications to uninstalled apps wastes bandwidth and triggers Apple throttling.",
                "mitigation": "Listen to APNs / FCM feedback service error callbacks (`DeviceNotRegistered`); immediately delete invalid device tokens from user device database."
            }
        ],
        "common_mistakes": [
            {
                "mistake": "Calling third-party notification APIs synchronously within checkout request paths",
                "correction": "Third-party APIs take 500ms to 5 seconds. If Twilio hangs, your checkout flow hangs. Always dispatch notifications asynchronously via background message queues."
            },
            {
                "mistake": "Mixing bulk marketing notifications with transactional OTPs in the same queue",
                "correction": "A 5-million email marketing campaign will backlog the queue for hours, starving urgent password-reset OTPs. Physically isolate priority queues."
            }
        ],
        "interview_questions": [
            {
                "question": "How do you guarantee that a user never receives duplicate push notifications during network retries?",
                "answer": "Implement end-to-end deduplication using idempotency keys: (1) The producer generates a deterministic idempotency key for the business event (e.g., `notif_order_shipped_10492`); (2) Before publishing or sending, the worker attempts an atomic `SET notif_key EX 86400 NX` in Redis or an `INSERT INTO processed_notifications` in the database; (3) If the key already exists, the worker acknowledges and discards the message without dispatching to APNs/FCM."
            },
            {
                "question": "How would you handle user 'Quiet Hours' across multiple worldwide timezones?",
                "answer": "Store the user's IANA timezone (e.g., `America/New_York`) in their profile. When an event is ingested, calculate current local time in that timezone. If local time falls between quiet hours (e.g., 22:00 - 08:00) and the notification priority is non-critical, calculate the Unix timestamp for 08:05 AM in that timezone and insert the task into a Redis Sorted Set (delayed queue) or AWS SQS delayed message buffer, releasing the notification when morning arrives."
            }
        ]
    },
    {
        "id": "design-youtube-video-streaming",
        "title": "Problem 4 (Intermediate): Design YouTube / Netflix Video Streaming Platform",
        "definition": "A Global Video Streaming Platform (e.g., YouTube, Netflix) enables creators to upload high-resolution video content, transcodes raw video into multiple bitrates and resolutions, segments videos into small temporal chunks, and streams them smoothly to millions of heterogeneous devices using Adaptive Bitrate Streaming (HLS / MPEG-DASH) via globally distributed Content Delivery Networks (CDNs).",
        "why_we_need_it": "### System Requirements\n**Functional Requirements:**\n1. Creators can upload videos up to 4K resolution.\n2. Viewers can stream video smoothly with minimal buffering and adaptive quality switching.\n3. Search and view video metadata (title, views, comments).\n4. Fast video thumbnail generation and scrubbing preview.\n\n**Non-Functional Requirements:**\n1. Ultra-high video streaming availability ($99.99\\%$) and low start latency ($<1$ second).\n2. Video playback must never stall or buffer unexpectedly.\n3. Cost-effective bandwidth distribution (video constitutes ~70% of global internet traffic).\n\n### Capacity Estimations\n- **Daily Active Users (DAU):** 500 million viewers.\n- **Video Views:** 2.5 billion video views per day.\n- **Uploads:** 500 hours of video uploaded every minute $\\approx 8.3$ hours of raw video per second.\n- **Egress Bandwidth:** Average viewing bitrate = 2 Mbps (720p/1080p). Concurrent viewers at peak = 25 million $\\rightarrow 25M \\times 2 \\text{ Mbps} = 50 \\text{ Terabits per second (Tbps)}$! Distributing 50 Tbps directly from origin servers would cost billions; 95%+ of video traffic must be absorbed by CDN edge caches.",
        "real_world_analogy": "Imagine a global publishing house translating a massive 1,000-page historical encyclopedia into 15 languages, binding it into 10-page lightweight pocket pamphlets, and placing copies in neighborhood newsstands across every town in the world. When a commuter boards a train, they don't carry the 50-pound master book; they grab only pamphlet #1 in their preferred language. If the train enters a dark tunnel, they swap to a cheaper, large-print pocket edition (Adaptive Bitrate) that is easier to read without stopping.",
        "how_it_works": "<p>A production video streaming architecture operates through distinct ingestion and delivery pipelines:</p><ol><li><strong>Chunked Ingestion & Object Storage:</strong> The creator's client uploads raw video directly to an S3/GCS bucket using multi-part parallel uploads via pre-signed URLs.</li><li><strong>DAG Transcoding Pipeline:</strong> An event trigger (S3 Event Notification) notifies a Workflow Orchestrator (Temporal / AWS Step Functions). The orchestrator splits the raw video into 10-second segments and dispatches distributed parallel worker jobs (using FFmpeg on GPU worker nodes) to transcode chunks into multiple resolutions (240p, 480p, 720p, 1080p, 4K) and codecs (H.264, VP9, AV1).</li><li><strong>Adaptive Bitrate (ABR) Manifest Generation:</strong> Workers generate an HLS (HTTP Live Streaming) or MPEG-DASH manifest file (<code>master.m3u8</code>). The manifest lists available resolutions and file paths for each 5-second video chunk (e.g., <code>chunk_1080p_001.ts</code>, <code>chunk_720p_001.ts</code>).</li><li><strong>Edge CDN Caching & Delivery:</strong> Video chunks are static, immutable files. They are cached at CDN Edge PoPs (Cloudflare, Fastly, or Netflix Open Connect appliances embedded inside ISP data centers).</li><li><strong>Client Adaptive Player:</strong> The video player downloads <code>master.m3u8</code>. It continuously measures real-time network download speed: if bandwidth drops (e.g., user enters an elevator), the player seamlessly requests the next 5-second chunk at 480p instead of 1080p without interrupting playback.</li></ol>",
        "conceptual_breakdown": [
            {
                "concept": "Adaptive Bitrate Streaming (HLS / DASH)",
                "explanation": "Splitting video into 2-10 second `.ts` or `.m4s` chunks at varying quality tiers. The client player dynamically selects the chunk quality matching current network throughput."
            },
            {
                "concept": "Video Codecs (H.264 vs VP9 vs AV1)",
                "explanation": "Codecs compress raw pixel frames. AV1 delivers 30-40% smaller file sizes than H.264 at equivalent visual quality, saving petabytes of bandwidth at the cost of higher CPU encoding time."
            },
            {
                "concept": "Netflix Open Connect (ISP Edge Caches)",
                "explanation": "Instead of paying commercial CDN transit fees, Netflix embeds custom storage appliances (OCAs) directly inside local ISP facilities, serving 95% of traffic over local metro networks with zero internet transit cost."
            },
            {
                "concept": "Distributed Chunk Transcoding (DAG)",
                "explanation": "Transcoding a 2-hour 4K movie on 1 machine takes 4 hours. Splitting the movie into 120 1-minute segments across 120 cloud worker nodes transcodes the entire movie in under 3 minutes."
            }
        ],
        "arch_diagram": {
            "nodes": [
                {"id": "creator", "label": "Video Creator Upload", "type": "client", "tier": "client"},
                {"id": "s3_raw", "label": "Raw Video Bucket (S3 Multi-Part)", "type": "database", "tier": "database"},
                {"id": "orch", "label": "Transcoding DAG Orchestrator", "type": "service", "tier": "service"},
                {"id": "workers", "label": "GPU Worker Fleet (FFmpeg Chunker)", "type": "service", "tier": "service"},
                {"id": "s3_cdn", "label": "Processed Chunks (m3u8 + .ts)", "type": "database", "tier": "database"},
                {"id": "cdn", "label": "Global CDN / ISP Open Connect Edge", "type": "cache", "tier": "cache"},
                {"id": "viewer", "label": "Viewer Player (Adaptive Bitrate)", "type": "client", "tier": "client"}
            ],
            "connections": [
                {"from": "creator", "to": "s3_raw", "label": "1. Multi-part Upload (Pre-signed S3)", "type": "sync"},
                {"from": "s3_raw", "to": "orch", "label": "2. S3 ObjectCreated Event", "type": "async"},
                {"from": "orch", "to": "workers", "label": "3. Dispatch Parallel Chunk Jobs", "type": "async"},
                {"from": "workers", "to": "s3_cdn", "label": "4. Write 1080p/720p Chunks + Manifest", "type": "sync"},
                {"from": "s3_cdn", "to": "cdn", "label": "5. Edge Pull & Cache", "type": "async"},
                {"from": "viewer", "to": "cdn", "label": "6. GET master.m3u8 & .ts chunks", "type": "sync"}
            ]
        },
        "comparison_matrix": {
            "headers": ["Streaming Protocol", "Transport", "Latency", "Adaptive Bitrate?", "Device Compatibility"],
            "rows": [
                ["HLS (HTTP Live Streaming)", "HTTP/TCP (Standard web servers)", "Normal (6-15 seconds)", "Yes (Native manifest switching)", "100% (iOS, Android, Browsers, Smart TVs)"],
                ["MPEG-DASH", "HTTP/TCP", "Normal (6-15 seconds)", "Yes (MPD XML manifest)", "Broad (Android, Chrome, Web; limited iOS)"],
                ["WebRTC", "UDP (P2P / SFU)", "Ultra-low (<500ms)", "Complex custom implementation", "Browsers & native apps (Heavy server cost)"],
                ["RTMP (Legacy)", "TCP Port 1935", "Low (1-3 seconds)", "No (Single static bitrate)", "Dead on modern web (requires Flash)"]
            ]
        },
        "tradeoffs": [
            {"factor": "Chunk Duration (2s vs 10s)", "analysis": "Shorter chunks (2s) allow the player to switch bitrates rapidly and reduce live latency, but increase HTTP request overhead and reduce codec compression efficiency. 4 to 6-second chunks provide the optimal sweet spot."},
            {"factor": "Transcoding Cost vs Bandwidth Savings", "analysis": "Transcoding into high-efficiency AV1 codecs consumes heavy GPU compute cycles ($$$). For long-tail videos with 10 views, AV1 wastes money. Only transcode into AV1 for the top 5% popular videos; keep long-tail in standard H.264."}
        ],
        "failure_scenarios": [
            {
                "scenario": "Transcoding Worker Pod Dies Mid-Way Through Hour 1 of Movie",
                "impact": "Worker crashes on segment #45 due to GPU memory leak.",
                "mitigation": "The workflow orchestrator (Temporal) tracks segment task states independently. It reschedules only segment #45 onto another worker node without restarting the entire movie."
            },
            {
                "scenario": "CDN Cache Miss Spike on Breaking News Video",
                "impact": "1 million users click a new video simultaneously. First requests miss CDN and hit origin S3 bucket, causing S3 503 Slow Down rate limits.",
                "mitigation": "Configure CDN Origin Shield (Request Collapsing / Single Flight): CDN collapses 10,000 identical chunk requests into 1 single origin fetch and multicasts the response to all edge nodes."
            }
        ],
        "common_mistakes": [
            {
                "mistake": "Streaming video as a monolithic single MP4 file over HTTP",
                "correction": "Monolithic MP4 files cannot adapt to fluctuating user network bandwidth and require buffering the entire file. Always segment videos into HLS / MPEG-DASH chunks."
            },
            {
                "mistake": "Transcoding entire 2-hour videos sequentially in a single process",
                "correction": "A single crash wastes hours of work and blocks publication. Always split raw video into temporal chunks and transcode in parallel across a distributed worker fleet."
            }
        ],
        "interview_questions": [
            {
                "question": "How does Adaptive Bitrate (ABR) streaming work at the client player level?",
                "answer": "When a viewer plays a video, the player first fetches the `master.m3u8` index file, which declares available bitrates, resolutions, and stream URLs. The player requests the first 5-second chunk at an initial conservative bitrate (e.g., 720p). As the chunk downloads, the player calculates actual throughput: $\\text{Bandwidth} = \\frac{\\text{Chunk Size (bits)}}{\\text{Download Time (seconds)}}$. If actual bandwidth is significantly higher than required for 1080p, the player requests the *next* 5-second chunk at 1080p. If throughput plummets, the player requests the subsequent chunk at 480p. Because chunks are temporally aligned at keyframes (IDR frames), switching occurs seamlessly without visual stutter."
            },
            {
                "question": "How does YouTube optimize storage costs for the 'Long Tail' of videos that get almost zero views?",
                "answer": "YouTube leverages tiered hierarchical storage and on-demand transcoding: (1) Popular Top 5% Videos: Stored in high-performance NVMe SSD caches across global CDN edges, transcoded in all resolutions and modern efficient codecs (AV1, VP9, H.264); (2) Long Tail (95% of videos with $<100$ views): Evicted from CDN caches to cheaper Cold Object Storage (S3 Glacier / Google Coldline) in standard H.264 480p/720p only. If an old video suddenly goes viral, it is fetched from cold storage, loaded into CDN caches, and transcoded into additional formats on the fly."
            }
        ]
    },
    {
        "id": "design-twitter-newsfeed-system",
        "title": "Problem 5 (Intermediate): Design Twitter / X News Feed & Timeline Fan-out",
        "definition": "A Social Network Timeline & News Feed System (e.g., Twitter/X, Instagram, Facebook) aggregates, sorts, and delivers a personalized stream of posts from followed entities in real time. The core architectural challenge centers on Fan-out: deciding between Fan-out-on-Write (Push model) and Fan-out-on-Read (Pull model) to balance massive write bursts against ultra-low read latency.",
        "why_we_need_it": "### System Requirements\n**Functional Requirements:**\n1. Users can post tweets/updates (up to 280 characters, with media attachments).\n2. Users can follow other users.\n3. View a chronological Home Timeline of tweets from followed users.\n4. View a User Timeline of tweets posted by a specific user.\n\n**Non-Functional Requirements:**\n1. Ultra-fast Home Timeline delivery ($<100$ms read latency at p99).\n2. Real-time post availability: a posted tweet should appear in followers' feeds within 5 seconds.\n3. Support massive celebrity fan-out (e.g., accounts with 100M+ followers).\n\n### Capacity Estimations\n- **Users:** 300 million Daily Active Users (DAU).\n- **Tweets Posted:** 500 million tweets/day $\\approx 6,000$ tweets/sec (Peak: 12,000/sec).\n- **Timeline Reads:** 300M users $\\times$ 10 timeline views/day $= 3$ billion timeline views/day $\\approx 35,000$ reads/sec.\n- **Celebrity Math:** If an account with 100 million followers tweets, a naive push model writes 100 million timeline entries into Redis caches. At 6,000 tweets/sec, naive push crashes the cluster. The Celebrity / Hybrid model is mandatory.",
        "real_world_analogy": "Imagine delivering daily newspapers: (1) **Fan-out on Write (Push):** Every time a citizen writes a letter, a courier runs to the physical home mailbox of every single friend and drops a copy inside. When you wake up, your mailbox is pre-filled (instant reading). But if the President writes a letter, the courier must visit 100 million houses simultaneously. (2) **Fan-out on Read (Pull):** Nobody delivers mail. When you wake up, you walk to the city square, scan a bulletin board listing all 50 people you follow, and collect their latest notes. Easy for writers, but reading takes 1 hour. (3) **Hybrid Model:** Standard citizens have mail delivered to mailboxes. The President's speech is broadcast on the town radio tower (pulled only when you turn on your radio).",
        "how_it_works": "<p>A high-scale Twitter Timeline architecture uses a <strong>Hybrid Fan-out Model</strong>:</p><ol><li><strong>Home Timeline vs User Timeline Storage:</strong> (a) <em>User Timeline:</em> Stored in a sharded relational/NoSQL datastore (Postgres / Cassandra) partitioned by <code>user_id</code>: <code>SELECT * FROM tweets WHERE user_id = ? ORDER BY created_at DESC</code>; (b) <em>Home Timeline:</em> Stored as an in-memory Redis List or Sorted Set (ZSET) per user, holding the top 800 tweet IDs.</li><li><strong>Standard User Tweet Flow (Fan-out on Write / Push):</strong> When User A (with 200 followers) posts a tweet, the Tweet Service saves the tweet in the database and pushes an event to Apache Kafka. A fleet of <em>Fan-out Workers</em> reads the event, fetches User A's follower list from the Social Graph Service, and executes <code>LPUSH timeline:{follower_id} tweet_id</code> into each follower's Redis timeline cache in parallel.</li><li><strong>Celebrity Tweet Flow (Fan-out on Read / Pull):</strong> If a 'Celebrity / VIP' user (e.g., $>50,000$ followers) tweets, the Fan-out Workers <em>bypass</em> pushing to 50M timelines. The tweet is written only to the celebrity's User Timeline.</li><li><strong>Hybrid Read Merge:</strong> When User B opens their app to view their Home Timeline: (a) Fetch User B's pre-computed timeline from their Redis cache (containing normal users' tweets); (b) Fetch the latest tweets from the celebrities User B follows; (c) Merge and sort the two lists in memory by timestamp ($O(K \\log N)$ heap merge) and return the top 20 tweets to the client in $<20$ms.</li><li><strong>Timeline Truncation:</strong> Inactive users' Redis timelines are evicted after 14 days of no login. When an inactive user returns, their timeline is reconstructed via pull on demand.</li></ol>",
        "conceptual_breakdown": [
            {
                "concept": "Fan-out-on-Write (Push Model)",
                "explanation": "Pre-computes timelines at write time. Reads are an instantaneous $O(1)$ memory lookup from Redis, but writes are expensive ($O(F)$ where $F$ is follower count)."
            },
            {
                "concept": "Fan-out-on-Read (Pull Model)",
                "explanation": "No write overhead. When reading, queries all followed users and merges their tweets. Write is $O(1)$, but read is an expensive $O(F \\log F)$ distributed query."
            },
            {
                "concept": "The Celebrity Threshold",
                "explanation": "Accounts with followers exceeding a threshold (e.g., 25,000 followers) switch dynamically from Push to Pull to protect Redis worker pools from queue explosion."
            },
            {
                "concept": "Social Graph Partitioning (FlockDB)",
                "explanation": "Storing bidirectional user graph edges (`user_id_A follows user_id_B`). Partitions graph adjacency lists across distributed memory clusters for fast follower ID lookups."
            }
        ],
        "arch_diagram": {
            "nodes": [
                {"id": "author", "label": "Author Posting Tweet", "type": "client", "tier": "client"},
                {"id": "tweet_svc", "label": "Tweet Service", "type": "service", "tier": "service"},
                {"id": "tweet_db", "label": "Tweet Database (Postgres / Cassandra)", "type": "database", "tier": "database"},
                {"id": "kafka", "label": "Kafka Topic (tweet-events)", "type": "queue", "tier": "queue"},
                {"id": "fanout", "label": "Fan-out Workers (Follower Evaluator)", "type": "service", "tier": "service"},
                {"id": "redis", "label": "Timeline Cache (Redis ZSET per user)", "type": "cache", "tier": "cache"},
                {"id": "reader", "label": "Reader Loading Home Timeline", "type": "client", "tier": "client"},
                {"id": "agg", "label": "Timeline Aggregator (Hybrid Merge)", "type": "service", "tier": "service"}
            ],
            "connections": [
                {"from": "author", "to": "tweet_svc", "label": "1. POST /tweets", "type": "sync"},
                {"from": "tweet_svc", "to": "tweet_db", "label": "2. Write Tweet Record", "type": "sync"},
                {"from": "tweet_svc", "to": "kafka", "label": "3. Publish TweetEvent", "type": "async"},
                {"from": "kafka", "to": "fanout", "label": "4. Consume Event", "type": "async"},
                {"from": "fanout", "to": "redis", "label": "5. Standard: Push to Redis Timelines", "type": "async"},
                {"from": "reader", "to": "agg", "label": "6. GET /home-timeline", "type": "sync"},
                {"from": "agg", "to": "redis", "label": "7. Read Pre-computed ZSET", "type": "sync"},
                {"from": "agg", "to": "tweet_db", "label": "8. Fetch & Merge Followed Celebrities", "type": "sync"}
            ]
        },
        "comparison_matrix": {
            "headers": ["Strategy", "Fan-out on Write (Push)", "Fan-out on Read (Pull)", "Hybrid Push-Pull Model"],
            "rows": [
                ["Read Latency", "Blistering Fast ($<5$ms from Redis)", "Slow ($100$ms - 2s distributed joins)", "Ultra-fast ($<20$ms memory merge)"],
                ["Write Latency", "High (slowed down by millions of pushes)", "Instantaneous ($O(1)$ single DB write)", "Instantaneous ($O(1)$ for celebrities)"],
                ["Celebrity Problem", "Catastrophic (crashes Redis under 100M writes)", "Handles celebrities effortlessly", "Completely solved (celebrities pulled on read)"],
                ["Storage Consumption", "High (redundant tweet IDs in millions of lists)", "Minimal (1 copy of tweet in DB)", "Moderate (caches only active user feeds)"],
                ["Best Fit For", "Users with $<25$k followers", "Small systems or ad-hoc feeds", "Production-scale social networks (Twitter, LinkedIn)"]
            ]
        },
        "tradeoffs": [
            {"factor": "Timeline Memory Cache vs Cold User Costs", "analysis": "Keeping pre-computed Redis timelines for 300 million users requires hundreds of terabytes of expensive RAM. Evicting inactive users who haven't logged in for 14 days slashes Redis cluster memory costs by 65%."},
            {"factor": "Strict Chronological vs Algorithmic Feed Ranking", "analysis": "Chronological feeds require simple timestamp sorting in Redis ZSET. Machine-learning ranked feeds (relevance scoring) require an extra ranking inference stage, increasing p99 read latency from 15ms to 80ms."}
        ],
        "failure_scenarios": [
            {
                "scenario": "World Cup Final Triggers 100,000 Tweets/Sec",
                "impact": "Kafka fan-out queue lags by 45 minutes; tweets appear with massive delay.",
                "mitigation": "Scale Fan-out worker consumer group dynamically based on Kafka consumer lag, and temporarily lower the Celebrity threshold to 5,000 followers during the event."
            },
            {
                "scenario": "Redis Timeline Cache Eviction Thrashing",
                "impact": "Redis runs out of memory and evicts active users' timelines.",
                "mitigation": "Set hard limit of 800 tweet IDs per user timeline (`LTRIM timeline:{uid} 0 799`), and size Redis clusters with 30% headroom."
            }
        ],
        "common_mistakes": [
            {
                "mistake": "Storing entire tweet JSON payloads in every user's Redis timeline list",
                "correction": "Storing entire payloads multiplies storage by 1,000x. Store *only* 64-bit `tweet_id` integers in Redis lists; hydrate tweet text and author data in a single multi-get (`MGET`) from cache on read."
            },
            {
                "mistake": "Attempting pure Fan-out on Write for accounts with 80 million followers",
                "correction": "A single tweet from a celebrity will tie up millions of Redis writes, blocking standard users' queue processing. Always divert celebrities to Fan-out on Read."
            }
        ],
        "interview_questions": [
            {
                "question": "Why does Twitter use a Hybrid (Push-Pull) model instead of pure Push or pure Pull?",
                "answer": "Pure **Pull (Fan-out on Read)** requires querying the database for all 500 users a person follows, fetching their latest tweets, and sorting them on every single page load. At 35,000 reads/sec, this creates an impossible database read bottleneck. Pure **Push (Fan-out on Write)** solves read latency by pre-computing timelines into Redis lists. However, when an account with 100 million followers tweets, pure push requires 100 million writes into 100 million distinct Redis lists, causing massive queue delays and thread starvation. The **Hybrid Model** delivers the best of both: 99.9% of normal users use Push (instant reads), while high-follower Celebrity accounts are excluded from push and merged on-the-fly during read ($O(K)$ merge), completely eliminating the celebrity write bottleneck while maintaining sub-20ms read latency."
            },
            {
                "question": "How do you handle timeline generation for inactive users who haven't logged in for 6 months?",
                "answer": "Do not maintain pre-computed Redis timelines for inactive users. Enforce a Time-to-Live (TTL) or Least Recently Used (LRU) policy on Redis timelines: if a user does not open the app for 14 days, their timeline key expires and is evicted from Redis RAM. When the inactive user logs in after 6 months, the Timeline Service detects a cache miss, performs a Fallback Pull: queries the database for the user's followed accounts, queries the last 20 tweets from each followed user, merges the results into a fresh timeline, populates Redis, and serves the user."
            }
        ]
    },
    {
        "id": "design-whatsapp-chat-messenger",
        "title": "Problem 6 (Intermediate): Design WhatsApp / Real-time Messaging System",
        "definition": "A Real-time Instant Messaging Platform (e.g., WhatsApp, Telegram, Slack) facilitates instantaneous, bi-directional peer-to-peer and group messaging over persistent connections. The architecture supports end-to-end encryption (Signal Protocol), message delivery receipts (Sent, Delivered, Read), offline message buffering, and user online presence tracking at massive scale.",
        "why_we_need_it": "### System Requirements\n**Functional Requirements:**\n1. One-on-one real-time text and media messaging.\n2. Group chat support (up to 1,024 members).\n3. Message delivery acknowledgments: Sent (✓), Delivered (✓✓), Read (blue ✓✓).\n4. Offline message storage: unread messages delivered immediately when recipient reconnects.\n5. End-to-end encryption (E2EE).\n\n**Non-Functional Requirements:**\n1. Ultra-low latency ($<100$ms message delivery worldwide).\n2. Strict message ordering (messages must display in exact chronological order).\n3. High connection density: 2 billion users with 500 million concurrent active persistent TCP/WebSocket connections.\n4. Ephemeral storage: Once a message is delivered and acknowledged, it is permanently deleted from WhatsApp servers (privacy & storage minimization).\n\n### Scale Math\n- 100 billion messages delivered per day $\\approx 1.15$ million messages/second.\n- 500 million concurrent idle TCP connections."
    },
    {
        "id": "design-uber-ride-matching",
        "title": "Problem 7 (Intermediate): Design Uber / Ride Hailing & Spatial Matching Service",
        "definition": "A Ride Hailing and Location-Based Dispatch Platform (e.g., Uber, Lyft) connects nearby drivers and riders in real time based on geographic proximity. The system continuously ingests real-time GPS telemetry from millions of moving vehicles, maintains high-performance spatial indexes (Uber H3 hexagonal grid or Google S2 geometry), performs sub-second driver dispatch matching, and dynamically computes surge pricing."
    }
]

print(f"Part 1 topics defined: {len(topics_part1)}")
