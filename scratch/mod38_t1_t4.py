# module 38 topics 1 to 4
import json

t1 = {
    "id": "design-url-shortener-tinyurl",
    "title": "Problem 1 (Beginner): Design a URL Shortener (TinyURL / Bitly)",
    "definition": "A URL Shortening Service (e.g., TinyURL, Bitly) provides short aliases (e.g., `https://tiny.cc/xyz89`) for long, unwieldy URLs. When a user clicks the shortened URL, the service resolves the alias and redirects the browser to the original target URL using HTTP redirection (301 Permanent vs 302/307 Temporary).",
    "why_we_need_it": "### System Requirements\n**Functional Requirements:**\n1. Given a long URL, generate a unique, short 7-character alias.\n2. When accessing the short URL, redirect to original URL with minimal latency (<20ms).\n3. Custom URL alias support (optional vanity URLs).\n4. Configurable link expiration (TTL) and basic click analytics.\n\n**Non-Functional Requirements:**\n1. Ultra-high availability (99.99%) and low-latency reads (<10ms).\n2. Read-heavy system: Read to Write ratio is 100:1.\n3. URLs must not be easily guessable (security against sequential enumeration).\n\n### Capacity Estimations\n- **Write Traffic:** 100 million new URLs created per month -> ~40 writes/sec.\n- **Read Traffic (100:1):** 4,000 redirects/sec (Peak: 8,000 QPS).\n- **Storage (5 Years):** 100M * 12 * 5 = 6 billion URLs. At 500 bytes per record: 6B * 500B = 3 Terabytes total storage.\n- **Cache Memory:** 80-20 Pareto Rule: Cache top 20% daily read requests: 350M requests * 0.2 * 500B = ~35 GB RAM (easily fits in 1 Redis node).",
    "real_world_analogy": "Imagine a coat-check room at a luxury opera house. Instead of dragging your giant heavy winter coat, luggage, and umbrella into the theater seat, the attendant takes your items, places them in a large locker in the back vault (Long URL), and hands you a tiny plastic claim token with a 4-digit number: #4928 (Short URL). When the opera ends, you present token #4928, and the attendant instantly retrieves your coat.",
    "how_it_works": "<p>Designing TinyURL involves key encoding and routing decisions:</p><ol><li><strong>Encoding Strategy (Base62):</strong> An alphanumeric character set <code>[a-zA-Z0-9]</code> yields 62 distinct characters. With a 7-character string: $62^7 \\approx 3.52 \\text{ trillion}$ unique combinations, comfortably exceeding our 6 billion requirement.</li><li><strong>Distributed ID Generation:</strong> Rather than hashing long URLs (which requires collision resolution), generate a globally unique 64-bit monotonic ID using Twitter Snowflake or Range Ticket Servers, and encode the integer into Base62.</li><li><strong>HTTP Redirection (301 vs 302):</strong> Use <code>HTTP 302 Found</code> or <code>307 Temporary Redirect</code> to force client browsers to hit the shortener on every click, enabling accurate real-time click telemetry.</li><li><strong>Storage Tier:</strong> Use a high-performance NoSQL Key-Value store (DynamoDB / Cassandra) or sharded PostgreSQL indexed by <code>short_hash (PK)</code>.</li></ol>",
    "conceptual_breakdown": [
        {"concept": "Base62 Encoding Algorithm", "explanation": "Converting a 64-bit integer into Base62 by repeated division by 62 and mapping remainders to `0-9a-zA-Z`. Zero collisions, guaranteed O(1)."},
        {"concept": "Distributed Ticket Range Allocator", "explanation": "A central coordinator (ZooKeeper/etcd) assigns ID ranges to application servers (e.g., Server 1 gets 1M-2M), allowing servers to increment in memory without locks."},
        {"concept": "Preventing Sequential Enumeration", "explanation": "Sequential Base62 IDs allow scraping. Mitigate by passing the integer through a lightweight Feistel cipher or bit-permutation before Base62 encoding."},
        {"concept": "Lazy Expiration", "explanation": "Avoid expensive full-table delete sweeps. Check `expires_at` on read; if expired, return 404 and asynchronously delete the key."}
    ],
    "arch_diagram": {
        "nodes": [
            {"id": "client", "label": "Client Browser / Mobile", "type": "client", "tier": "client"},
            {"id": "cdn", "label": "Edge CDN / Route 53", "type": "cache", "tier": "cache"},
            {"id": "lb", "label": "Application Load Balancer", "type": "service", "tier": "service"},
            {"id": "app", "label": "URL Shortener Service (Base62)", "type": "service", "tier": "service"},
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
            ["Lookup Overhead", "Requires DB lookup on collision", "Zero collision check needed (O(1))", "Severe DB read penalty before every insert"],
            ["ID Length", "Fixed 7 characters", "Dynamic (grows smoothly with ID)", "Fixed length"],
            ["Predictability", "Random looking", "Sequential (requires bit permutation)", "Completely random"]
        ]
    },
    "tradeoffs": [
        {"factor": "HTTP 301 vs 302 Redirection", "analysis": "301 Permanent saves origin bandwidth because browsers cache the redirect, but strips the business of click analytics. 302/307 Temporary forces a server hit on every click, allowing granular analytics at the cost of infrastructure scaling."},
        {"factor": "Relational SQL vs NoSQL Key-Value", "analysis": "TinyURL requires zero complex joins or multi-table ACID transactions. A NoSQL key-value store (DynamoDB or Redis) offers effortless horizontal partitioning and single-digit millisecond latency under billions of keys."}
    ],
    "failure_scenarios": [
        {"scenario": "ID Range Generator Node Dies Abruptly", "impact": "Application server holding Range 1M to 2M crashes while at ID 1.2M.", "mitigation": "The unused 800k IDs in that range are simply skipped and abandoned. Range gaps in a 3.5 trillion namespace are completely harmless."},
        {"scenario": "Viral Short URL Causes Cache Hotspot", "impact": "A viral link receives 100k clicks/second, overloading a single Redis shard.", "mitigation": "Enable Read Replicas on Redis, or cache the redirect mapping directly at Cloudflare/Fastly CDN edge PoPs with a 60-second TTL."}
    ],
    "common_mistakes": [
        {"mistake": "Using MD5 hash and checking database for collisions in a tight while-loop", "correction": "As the table reaches billions of rows, hash collisions multiply, creating catastrophic database lock contention. Use distributed ID generation + Base62 conversion."},
        {"mistake": "Storing sequential IDs directly in the public short URL (/1, /2, /3)", "correction": "Allows competitors to scrape your entire customer database and estimate company transaction volume. Permute or encrypt the integer ID before Base62 encoding."}
    ],
    "interview_questions": [
        {"question": "How does the Base62 encoding algorithm work, and why Base62 instead of Base64?", "answer": "Base62 utilizes characters `[0-9a-zA-Z]` (10 digits + 26 lowercase + 26 uppercase = 62 characters). Base64 includes `+` and `/` (or `=` for padding). In HTTP URLs, characters like `+`, `/`, and `=` have reserved protocol meanings and must be URL-encoded, which expands URL length and causes parsing bugs. Base62 consists strictly of alphanumeric characters that are 100% URL-safe without escaping."},
        {"question": "How do you handle custom (vanity) URLs like 'tiny.cc/my-summer-sale'?", "answer": "Maintain a secondary lookup or single index where `short_hash` can be either the Base62 generated token or the custom string. Impose validation rules (length 4-25 characters, alphanumeric and hyphens). When creating a custom URL, run an atomic `INSERT ... ON CONFLICT DO NOTHING` against the datastore. If the write fails due to unique constraint violation, return HTTP 409 Conflict ('Custom alias already taken')."}
    ]
}

t2 = {
    "id": "design-pastebin-storage",
    "title": "Problem 2 (Beginner): Design Pastebin / Text Sharing Service",
    "definition": "Pastebin is a text storage and sharing web service that allows users to upload plain text blocks or source code snippets and receive a unique shareable URL. The system stores multi-megabyte text documents durably, enforces expiration policies, and allows users to set access privacy (public, unlisted, password-protected).",
    "why_we_need_it": "### System Requirements\n**Functional Requirements:**\n1. Upload text paste (up to 10MB) and generate unique link.\n2. Retrieve paste content via unique link with high throughput.\n3. Optional paste expiration (1 hour, 1 day, never).\n4. Read-only pastes (no edits after creation).\n\n**Non-Functional Requirements:**\n1. Strict durability (uploaded text must never be lost or corrupted).\n2. Read-heavy system (50:1 read to write ratio).\n3. Low read latency (<30ms).\n\n### Capacity Estimations\n- **Writes:** 1 million pastes uploaded per day = ~12 pastes/sec.\n- **Reads:** 600 reads/sec.\n- **Storage Volume:** Average paste size = 50 KB. Daily storage: 1M * 50KB = 50 GB/day. Annual storage: ~18 Terabytes/year. Over 5 years: ~90 TB.\n- **Decoupled Architecture:** Storing 90 TB of multi-kilobyte text blobs directly inside relational database tables (PostgreSQL/MySQL) degrades buffer pools and inflates backup costs. Metadata and text blobs must be decoupled.",
    "real_world_analogy": "Imagine a public storage locker facility. When you arrive with a giant trunk of documents, the manager doesn't shove the giant trunk into the tiny front-desk filing cabinet next to the receipt book. Instead, the manager places your trunk into a large industrial warehouse in the back (Object Storage: Amazon S3), and writes only your Name, Locker Number, and Expiration Date onto a 3x5 index card in the front-desk card catalog (Metadata Database).",
    "how_it_works": "<p>A scalable Pastebin architecture decouples metadata from blob storage:</p><ol><li><strong>Storage Decoupling:</strong> The actual text content is stored as an immutable object in distributed Object Storage (Amazon S3 / Google Cloud Storage / MinIO). The metadata record (Paste ID, Owner ID, S3 Object Path, Creation Time, Expiration Time, Character Count) is stored in a scalable NoSQL Key-Value database (DynamoDB / Cassandra) or PostgreSQL.</li><li><strong>Write Path:</strong> Client POSTs text content to API Gateway. Application server generates a unique Paste ID (via Base62 ID generator), uploads the raw text bytes to S3 at key <code>pastes/{paste_id}.txt</code>, writes the metadata row to DynamoDB, and returns the short URL to the client.</li><li><strong>Read Path:</strong> Client requests <code>GET /pastes/{paste_id}</code>. Application checks Redis cache for hot pastes. On cache miss, queries DynamoDB for metadata; if expired, returns 404. Otherwise, fetches the text blob from S3 and returns the raw text.</li><li><strong>TTL & Purging:</strong> Cloud Object Storage (S3) provides native Object Lifecycle Management rules that automatically delete expired objects based on tags or prefixes with zero server CPU overhead.</li></ol>",
    "conceptual_breakdown": [
        {"concept": "Blob Storage vs Database BLOBs", "explanation": "Storing large text blobs directly in relational database rows bloats B-trees and table pages, evicting indexes from memory buffer pools. Offloading text to S3 reduces database row size to <200 bytes."},
        {"concept": "Direct Upload via Pre-Signed S3 URLs", "explanation": "For large 10MB pastes, application servers shouldn't buffer megabytes of payload. The client requests an upload authorization; the API returns a pre-signed S3 URL. The client uploads the text directly to S3, bypassing app server memory."},
        {"concept": "Content Compression (Gzip / Snappy)", "explanation": "Source code and text compress exceptionally well (~60-70% ratio). Compressing pastes before writing to S3 slashes storage and network egress costs by more than half."},
        {"concept": "DDoS and Paste Spam Prevention", "explanation": "Pastebins are prime targets for bot scrapers and malware distribution. Implement IP-based token bucket rate limiting and integrate automated virus/malware scanning (ClamAV) on uploaded blobs."}
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
        {"factor": "Two-Phase Upload vs Single Request Simplicity", "analysis": "Uploading directly to S3 via pre-signed URLs eliminates app server memory bottlenecks, but requires the client to execute a two-step handshake. For standard pastes (<100KB), routing through the app server is simpler."},
        {"factor": "Full-Text Search vs Storage Costs", "analysis": "Indexing 90TB of arbitrary code snippets in Elasticsearch is financially exorbitant. Restrict search to metadata (title, author, tags) or support search only for authenticated enterprise users."}
    ],
    "failure_scenarios": [
        {"scenario": "S3 Write Succeeds But Metadata DB Write Fails", "impact": "An orphaned text blob exists in S3 with no database reference.", "mitigation": "S3 lifecycle policies prune unreferenced objects after 7 days, or execute metadata write first with status PENDING_UPLOAD."},
        {"scenario": "Abusive Client Spams 10,000 Large Pastes per Minute", "impact": "Consumes S3 bandwidth and generates excessive small objects.", "mitigation": "Enforce strict per-IP rate limiting (10 pastes/min), CAPTCHA verification for anonymous users, and file size quotas."}
    ],
    "common_mistakes": [
        {"mistake": "Storing 50KB text pastes directly inside MongoDB or MySQL rows", "correction": "Databases are engineered for structured query indexing, not bulk unstructured document storage. Offload raw text to S3 object storage."},
        {"mistake": "Running DELETE FROM pastes WHERE expires_at < NOW() on a 500M row SQL table", "correction": "Massive SQL deletes lock table pages and cause transaction log bloat. Use S3 Object Lifecycle rules or partition tables by day and drop old partitions."}
    ],
    "interview_questions": [
        {"question": "Why is S3 object storage superior to a relational database for storing paste text bodies?", "answer": "Relational databases store data in fixed-size 8KB or 16KB data pages loaded into memory buffer pools. Large multi-kilobyte text blobs span multiple pages, pushing hot index pages out of RAM and destroying query caching. S3 is designed specifically for unstructured blobs: it provides 11 9s durability, near-infinite capacity, built-in automated expiration lifecycle policies, and costs 5-10x less per gigabyte than database SSD storage."},
        {"question": "How do you implement client-side end-to-end encryption for sensitive pastes?", "answer": "The client browser generates an AES-256 encryption key and encrypts the text locally in JavaScript before dispatching to the API. The encryption key is included only in the URL fragment/hash (`https://pastebin.com/p/xyz#mySecretKey123`). Because RFC 3986 specifies that URL fragments after `#` are never sent over the network to the HTTP server, the backend server and database only ever see and store encrypted ciphertext. When another user opens the URL, their browser parses the key from the fragment and decrypts the text locally."}
    ]
}

t3 = {
    "id": "design-scalable-notification-system",
    "title": "Problem 3 (Beginner): Design a Scalable Notification Service (SMS, Email, Push)",
    "definition": "A Scalable Notification Service is a centralized, distributed platform responsible for delivering millions of notifications across multiple outbound channels: Mobile Push Notifications (APNs, FCM), SMS text messages (Twilio), Email (SendGrid, Amazon SES), and In-App notification feeds, guaranteeing reliable delivery, rate limiting, and user preference enforcement.",
    "why_we_need_it": "### System Requirements\n**Functional Requirements:**\n1. Send notifications across Push (iOS/Android), SMS, and Email.\n2. Support real-time transactional alerts (OTP codes, order updates) and delayed bulk marketing broadcasts.\n3. User Notification Preferences (e.g., mute SMS, enable email only for billing).\n4. Deduplication (prevent sending duplicate notifications during network retries).\n\n**Non-Functional Requirements:**\n1. High throughput (100 million notifications/day = ~1,200 notifications/sec average, 10,000/sec peak).\n2. Low latency for transactional alerts (OTP delivered in <5 seconds).\n3. Fault tolerance: Third-party vendor outages (e.g., Twilio outage) must not cause message loss.\n\n### Challenges\nThird-party gateway providers impose strict rate limits and suffer intermittent downtime. Synchronously calling external APIs inside business flows causes thread exhaustion. A decoupled, queue-driven worker architecture with prioritization is mandatory.",
    "real_world_analogy": "Imagine a multinational post office sorting facility: incoming letters arrive from courtrooms (critical legal notices), banks (credit card OTPs), and clothing brands (marketing flyers). The post office does not hand all letters to one mail carrier. It sorts mail into three distinct priority conveyor belts: (1) Urgent Express (OTP/Transactional); (2) Standard First-Class; (3) Bulk Media Mail. Independent delivery fleets handle airplanes, trucks, and couriers.",
    "how_it_works": "<p>A notification platform operates as a multi-tier asynchronous pipeline:</p><ol><li><strong>Notification Request Ingestion:</strong> Upstream microservices (Order, Auth, Billing) call <code>POST /v1/notifications</code> with <code>recipient_id</code>, <code>event_type</code>, <code>template_id</code>, and <code>parameters</code>. The API Gateway validates schemas and authenticates callers.</li><li><strong>User Preference & Opt-Out Evaluation:</strong> Notification Service checks the User Preference Cache (Redis): if the user has disabled marketing push notifications, the message is discarded immediately.</li><li><strong>Template Engine & Personalization:</strong> Fetches parameterized templates and hydrates personalized content.</li><li><strong>Priority Queue Fan-out:</strong> Enqueues jobs into channel-specific, priority-segmented Kafka topics or RabbitMQ queues: <code>queue:sms:critical</code>, <code>queue:push:normal</code>, <code>queue:email:bulk</code>.</li><li><strong>Channel Worker Fleets:</strong> Dedicated autoscaled worker clusters pull jobs from queues and interface with third-party providers (APNs, FCM, Twilio, SendGrid).</li><li><strong>Vendor Fallback & Circuit Breaker:</strong> If Twilio returns 500 errors or rate limits, SMS workers automatically fail over to a backup provider (e.g., Infobip).</li></ol>",
    "conceptual_breakdown": [
        {"concept": "Priority Queuing (OTP vs Marketing)", "explanation": "If a marketing campaign of 10 million emails is queued, a user requesting a password reset OTP must not wait behind 10 million marketing messages. Separate physical queues guarantee transactional OTPs are serviced with zero delay."},
        {"concept": "Deduplication via Idempotency Key", "explanation": "If an upstream service retries an order confirmation call, the notification engine checks an `inbox_notifications` table with key `hash(user_id, event_id, date)` to discard duplicate alerts."},
        {"concept": "Third-Party Rate Limiting Compliance", "explanation": "Third-party APIs (like Twilio) enforce hard quotas (e.g., 100 SMS/sec per shortcode). Workers use token bucket rate limiters to pace outbound requests and prevent 429 account suspensions."},
        {"concept": "User Quiet Hours & Batching", "explanation": "Non-urgent notifications scheduled during night hours (10:00 PM to 8:00 AM in user's local timezone) are delayed and batched into a morning digest."}
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
        {"scenario": "Twilio SMS Outage During Flash Sale", "impact": "SMS OTP delivery stalls, preventing users from logging in or checking out.", "mitigation": "Circuit breaker detects Twilio 5xx rate > 20% and trips. Worker fleet automatically diverts outbound SMS payloads to AWS SNS or Infobip fallback gateway."},
        {"scenario": "Invalid Device Tokens Result in APNs Rate Throttling", "impact": "Sending push notifications to uninstalled apps wastes bandwidth and triggers Apple throttling.", "mitigation": "Listen to APNs / FCM feedback service error callbacks (DeviceNotRegistered); immediately delete invalid device tokens from user device database."}
    ],
    "common_mistakes": [
        {"mistake": "Calling third-party notification APIs synchronously within checkout request paths", "correction": "Third-party APIs take 500ms to 5 seconds. If Twilio hangs, your checkout flow hangs. Always dispatch notifications asynchronously via background message queues."},
        {"mistake": "Mixing bulk marketing notifications with transactional OTPs in the same queue", "correction": "A 5-million email marketing campaign will backlog the queue for hours, starving urgent password-reset OTPs. Physically isolate priority queues."}
    ],
    "interview_questions": [
        {"question": "How do you guarantee that a user never receives duplicate push notifications during network retries?", "answer": "Implement end-to-end deduplication using idempotency keys: (1) The producer generates a deterministic idempotency key for the business event (`notif_order_shipped_10492`); (2) Before publishing or sending, the worker attempts an atomic `SET notif_key EX 86400 NX` in Redis or an `INSERT INTO processed_notifications` in the database; (3) If the key already exists, the worker acknowledges and discards the message without dispatching to APNs/FCM."},
        {"question": "How would you handle user 'Quiet Hours' across multiple worldwide timezones?", "answer": "Store the user's IANA timezone in their profile. When an event is ingested, calculate current local time in that timezone. If local time falls between quiet hours (22:00 - 08:00) and the notification priority is non-critical, calculate the Unix timestamp for 08:05 AM in that timezone and insert the task into a Redis Sorted Set or AWS SQS delayed message buffer, releasing the notification when morning arrives."}
    ]
}

t4 = {
    "id": "design-youtube-video-streaming",
    "title": "Problem 4 (Intermediate): Design YouTube / Netflix Video Streaming Platform",
    "definition": "A Global Video Streaming Platform (e.g., YouTube, Netflix) enables creators to upload high-resolution video content, transcodes raw video into multiple bitrates and resolutions, segments videos into small temporal chunks, and streams them smoothly to millions of heterogeneous devices using Adaptive Bitrate Streaming (HLS / MPEG-DASH) via globally distributed Content Delivery Networks (CDNs).",
    "why_we_need_it": "### System Requirements\n**Functional Requirements:**\n1. Creators can upload videos up to 4K resolution.\n2. Viewers can stream video smoothly with minimal buffering and adaptive quality switching.\n3. Search and view video metadata (title, views, comments).\n4. Fast video thumbnail generation and scrubbing preview.\n\n**Non-Functional Requirements:**\n1. Ultra-high video streaming availability (99.99%) and low start latency (<1 second).\n2. Video playback must never stall or buffer unexpectedly.\n3. Cost-effective bandwidth distribution (video constitutes ~70% of global internet traffic).\n\n### Capacity Estimations\n- **Daily Active Users (DAU):** 500 million viewers.\n- **Video Views:** 2.5 billion video views per day.\n- **Uploads:** 500 hours of video uploaded every minute = ~8.3 hours of raw video per second.\n- **Egress Bandwidth:** Average viewing bitrate = 2 Mbps (720p/1080p). Concurrent viewers at peak = 25 million -> 25M * 2 Mbps = 50 Terabits per second (Tbps)! Distributing 50 Tbps directly from origin servers would cost billions; 95%+ of video traffic must be absorbed by CDN edge caches.",
    "real_world_analogy": "Imagine a global publishing house translating a massive 1,000-page historical encyclopedia into 15 languages, binding it into 10-page lightweight pocket pamphlets, and placing copies in neighborhood newsstands across every town in the world. When a commuter boards a train, they don't carry the 50-pound master book; they grab only pamphlet #1 in their preferred language. If the train enters a dark tunnel, they swap to a cheaper, large-print pocket edition (Adaptive Bitrate) that is easier to read without stopping.",
    "how_it_works": "<p>A production video streaming architecture operates through distinct ingestion and delivery pipelines:</p><ol><li><strong>Chunked Ingestion & Object Storage:</strong> The creator's client uploads raw video directly to an S3/GCS bucket using multi-part parallel uploads via pre-signed URLs.</li><li><strong>DAG Transcoding Pipeline:</strong> An event trigger (S3 Event Notification) notifies a Workflow Orchestrator (Temporal / AWS Step Functions). The orchestrator splits the raw video into 10-second segments and dispatches distributed parallel worker jobs (using FFmpeg on GPU worker nodes) to transcode chunks into multiple resolutions (240p, 480p, 720p, 1080p, 4K) and codecs (H.264, VP9, AV1).</li><li><strong>Adaptive Bitrate (ABR) Manifest Generation:</strong> Workers generate an HLS (HTTP Live Streaming) or MPEG-DASH manifest file (<code>master.m3u8</code>). The manifest lists available resolutions and file paths for each 5-second video chunk.</li><li><strong>Edge CDN Caching & Delivery:</strong> Video chunks are static, immutable files cached at CDN Edge PoPs (Cloudflare, Fastly, or Netflix Open Connect appliances embedded inside ISP data centers).</li><li><strong>Client Adaptive Player:</strong> The video player downloads <code>master.m3u8</code>. It continuously measures real-time network download speed: if bandwidth drops, the player seamlessly requests the next 5-second chunk at 480p instead of 1080p without interrupting playback.</li></ol>",
    "conceptual_breakdown": [
        {"concept": "Adaptive Bitrate Streaming (HLS / DASH)", "explanation": "Splitting video into 2-10 second `.ts` or `.m4s` chunks at varying quality tiers. The client player dynamically selects the chunk quality matching current network throughput."},
        {"concept": "Video Codecs (H.264 vs VP9 vs AV1)", "explanation": "Codecs compress raw pixel frames. AV1 delivers 30-40% smaller file sizes than H.264 at equivalent visual quality, saving petabytes of bandwidth at the cost of higher CPU encoding time."},
        {"concept": "Netflix Open Connect (ISP Edge Caches)", "explanation": "Instead of paying commercial CDN transit fees, Netflix embeds custom storage appliances (OCAs) directly inside local ISP facilities, serving 95% of traffic over local metro networks with zero internet transit cost."},
        {"concept": "Distributed Chunk Transcoding (DAG)", "explanation": "Transcoding a 2-hour 4K movie on 1 machine takes 4 hours. Splitting the movie into 120 1-minute segments across 120 cloud worker nodes transcodes the entire movie in under 3 minutes."}
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
        {"scenario": "Transcoding Worker Pod Dies Mid-Way Through Hour 1 of Movie", "impact": "Worker crashes on segment #45 due to GPU memory leak.", "mitigation": "The workflow orchestrator (Temporal) tracks segment task states independently. It reschedules only segment #45 onto another worker node without restarting the entire movie."},
        {"scenario": "CDN Cache Miss Spike on Breaking News Video", "impact": "1 million users click a new video simultaneously. First requests miss CDN and hit origin S3 bucket, causing S3 503 Slow Down rate limits.", "mitigation": "Configure CDN Origin Shield (Request Collapsing / Single Flight): CDN collapses 10,000 identical chunk requests into 1 single origin fetch and multicasts the response to all edge nodes."}
    ],
    "common_mistakes": [
        {"mistake": "Streaming video as a monolithic single MP4 file over HTTP", "correction": "Monolithic MP4 files cannot adapt to fluctuating user network bandwidth and require buffering the entire file. Always segment videos into HLS / MPEG-DASH chunks."},
        {"mistake": "Transcoding entire 2-hour videos sequentially in a single process", "correction": "A single crash wastes hours of work and blocks publication. Always split raw video into temporal chunks and transcode in parallel across a distributed worker fleet."}
    ],
    "interview_questions": [
        {"question": "How does Adaptive Bitrate (ABR) streaming work at the client player level?", "answer": "When a viewer plays a video, the player first fetches the `master.m3u8` index file, which declares available bitrates, resolutions, and stream URLs. The player requests the first 5-second chunk at an initial conservative bitrate (e.g., 720p). As the chunk downloads, the player calculates actual throughput: `Bandwidth = Chunk Size / Download Time`. If actual bandwidth is significantly higher than required for 1080p, the player requests the next 5-second chunk at 1080p. If throughput plummets, the player requests the subsequent chunk at 480p. Because chunks are temporally aligned at keyframes, switching occurs seamlessly without visual stutter."},
        {"question": "How does YouTube optimize storage costs for the 'Long Tail' of videos that get almost zero views?", "answer": "YouTube leverages tiered hierarchical storage and on-demand transcoding: (1) Popular Top 5% Videos: Stored in high-performance NVMe SSD caches across global CDN edges, transcoded in all resolutions and modern efficient codecs (AV1, VP9, H.264); (2) Long Tail (95% of videos with <100 views): Evicted from CDN caches to cheaper Cold Object Storage (S3 Glacier / Google Coldline) in standard H.264 480p/720p only. If an old video suddenly goes viral, it is fetched from cold storage, loaded into CDN caches, and transcoded into additional formats on the fly."}
    ]
}

with open('scratch/t1_t4.json', 'w', encoding='utf-8') as f:
    json.dump([t1, t2, t3, t4], f, indent=2, ensure_ascii=False)
print("Topics 1-4 written successfully!")
