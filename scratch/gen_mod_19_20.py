"""
Elaborate generator for Modules 19 and 20.
Matches exact topics from app/data/hld_roadmap.json
"""
import json
from pathlib import Path

HLD_DIR = Path('content/hld')
HLD_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# MODULE 19: Content Delivery Networks (CDN) & Edge Computing
# ==========================================
m19 = {
  "module_id": "19",
  "module_title": "Content Delivery Networks (CDN) & Edge Computing",
  "description": "Master global content delivery: Edge Points of Presence (PoPs), BGP Anycast routing, Origin Shielding, Dynamic Site Acceleration (DSA), cache invalidation policies, and Serverless Edge Workers (Cloudflare Workers).",
  "topics": [
    {
      "id": "cdn-architecture-and-anycast",
      "title": "CDN Architecture: Edge PoPs, Anycast BGP Routing & Origin Shielding",
      "definition": "A Content Delivery Network (CDN) is a globally distributed network of proxy servers deployed across hundreds of Edge Points of Presence (PoPs) worldwide. CDN architecture leverages BGP Anycast routing to advertise a single IP address globally, routing each client to the geographically closest Edge server to serve cached content with minimal latency and protect origin servers via Origin Shielding.",
      "why_we_need_it": "A user in Sydney accessing a web server in Virginia (15,000 km away) experiences ~200ms of speed-of-light network latency per round trip. Completing DNS, TCP 3-way handshake, and TLS 1.3 setup requires 3-4 round trips (800ms) before the first byte of HTML is even transmitted! A CDN terminates TCP and serves cached assets at an Edge PoP located 5 miles away in Sydney in 5 milliseconds.",
      "real_world_analogy": "A global book publisher: Instead of having a single print factory in London where every customer in Tokyo, New York, and Sydney must wait 3 weeks for international maritime air-freight delivery, the publisher stocks local bookstores (Edge PoPs) in 200 cities worldwide. When a reader wants a book, they walk to the local corner bookstore and buy it in 5 minutes.",
      "how_it_works": "<p>1. <strong>BGP Anycast Routing:</strong> Traditional routing (Unicast) assigns a unique IP address to a single server. In Anycast, dozens of CDN data centers across the globe <em>advertise the exact same public IP address</em> (e.g., Cloudflare's `1.1.1.1`) to the Internet's Border Gateway Protocol (BGP). Internet Service Provider (ISP) routers automatically forward a client's packets along the shortest autonomous system (AS) network path, landing the user at the nearest physical PoP.</p><p>2. <strong>Edge PoP (Point of Presence):</strong> Each PoP contains high-performance caching servers (NGINX/Varnish/Envoy) equipped with massive NVMe SSD caches and RAM. If the requested file is cached locally, it returns in 2-5ms (Cache Hit).</p><p>3. <strong>Origin Shielding (Mid-Tier Caching):</strong> If 200 edge PoPs around the world experience a cache miss for a viral video simultaneously, all 200 edge servers would hammer the origin database simultaneously (Thundering Herd). An <strong>Origin Shield</strong> is a centralized regional cache layer placed between the edge PoPs and the origin. Edge misses query the Origin Shield; only if the shield also misses does a single request reach the origin.</p><p>4. <strong>Request Collapsing (Coalescing):</strong> If 1,000 users at an edge PoP request the same video chunk simultaneously during a cache miss, the CDN collapses them into a <em>single outbound request</em> to the origin, streaming the response to all 1,000 waiting users.</p>",
      "conceptual_breakdown": [
        "<strong>Latency Breakdown (Speed of Light):</strong> Light travels ~200 km/ms in fiber optics. Physics sets a hard minimum latency floor. The ONLY way to reduce latency for global users is to move content physically closer to the user.",
        "<strong>Anycast Failover:</strong> If a PoP in London goes down, BGP withdraws the Anycast route announcement. Global routers automatically reroute London traffic to the Paris or Amsterdam PoP within seconds.",
        "<strong>Origin Offload:</strong> A high-performance CDN achieves 95-99% origin offload, reducing backend bandwidth costs and server fleet sizes by 20x.",
        "<strong>DDoS Absorption:</strong> Because CDNs have massive multi-terabit network capacity across global PoPs, volumetric DDoS attacks (e.g. 1 Tbps UDP floods) are absorbed and filtered at the edge before touching origin infrastructure."
      ],
      "arch_diagram": {
        "title": "Global CDN Architecture (Anycast BGP + Edge PoPs + Origin Shield)",
        "tiers": [
          {
            "label": "Global Edge Ingress (Anycast BGP)",
            "nodes": [
              {
                "name": "User in Tokyo",
                "type": "client",
                "icon": "🗼",
                "what": "Queries 1.1.1.1",
                "why": "BGP routes to Tokyo PoP (2ms)",
                "when": "Client browser request",
                "failure": "Anycast failover to Osaka"
              },
              {
                "name": "User in London",
                "type": "client",
                "icon": "🎡",
                "what": "Queries 1.1.1.1",
                "why": "BGP routes to London PoP (3ms)",
                "when": "Client browser request",
                "failure": "Anycast failover to Frankfurt"
              }
            ]
          },
          {
            "label": "Edge PoP & Origin Shield Tier",
            "nodes": [
              {
                "name": "Tokyo Edge PoP (RAM/SSD)",
                "type": "cache",
                "icon": "⚡",
                "what": "Local Edge Proxy",
                "why": "98% Cache Hit Ratio locally",
                "when": "Static assets & video chunks",
                "failure": "Origin Shield pull on miss"
              },
              {
                "name": "Origin Shield (Regional)",
                "type": "cache",
                "icon": "🛡️",
                "what": "Centralized Mid-Tier Cache",
                "why": "Protects Origin from multi-PoP stampedes",
                "when": "Edge cache miss",
                "failure": "Pass-through to Origin"
              }
            ]
          },
          {
            "label": "Protected Origin Infrastructure",
            "nodes": [
              {
                "name": "Origin Web Cluster",
                "type": "service",
                "icon": "🏛️",
                "what": "Primary Backend Application",
                "why": "Authoritative content generator",
                "when": "Complete cache miss / dynamic API",
                "failure": "Protected from 99% of global bandwidth"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Unicast DNS Routing vs Anycast BGP Routing",
        "columns": ["Routing Method", "How it Works", "Failover Speed", "DDoS Resilience", "Latency Consistency"],
        "rows": [
          ["Unicast + Geo-DNS", "DNS server looks up client resolver IP and returns specific regional IP", "Slow (Bounded by DNS TTL, 60s - 300s)", "Low (Single IP can be targeted and saturated)", "Can route clients to wrong continent if using public DNS (8.8.8.8)"],
          ["Anycast BGP", "Single IP advertised by all global PoPs; routers pick shortest BGP path", "Instantaneous (BGP route withdrawal < 5s)", "Extreme (DDoS distributed across 200 global PoPs)", "Always routes to the true topological closest edge node"]
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> Anycast routing provides instant failover and DDoS protection, but can cause TCP connection resets if internal ISP routing flaps and routes packets belonging to the same TCP connection to different physical PoPs mid-session.",
      "failure_scenarios": "<strong>The Origin Thundering Herd Catastrophe:</strong> A global breaking-news event publishes an image without Origin Shielding. 150 edge PoPs around the world experience a cache miss at the exact same millisecond. All 150 PoPs initiate full HTTP downloads to the origin server. The origin's network interface card (NIC) saturates at 100%, dropping packets. The edge PoPs time out, report 504 Gateway Timeout to millions of readers, and retry, keeping the origin pinned in a fatal crash loop. <em>Mitigation:</em> Enable <strong>Origin Shielding</strong> and <strong>Request Coalescing</strong> (e.g., NGINX `proxy_cache_use_stale updating`).",
      "common_mistakes": [
        {"mistake": "Relying purely on GeoDNS without understanding that DNS resolvers (like Google 8.8.8.8) mask the true user IP address.", "correction": "Ensure your DNS provider supports EDNS Client Subnet (ECS) to pass the client's actual subnet to the GeoDNS server, or switch to BGP Anycast."},
        {"mistake": "Caching sensitive user-specific data (e.g. `/api/profile` containing credit card details) on public CDN edges.", "correction": "Always set `Cache-Control: private, no-store` on authenticated API endpoints to forbid public CDNs from caching private user PII."}
      ],
      "interview_questions": [
        {"question": "How does BGP Anycast work in modern CDNs like Cloudflare and Fastly?", "answer": "In <strong>BGP Anycast</strong>, a single IP address (e.g. `1.1.1.1` or `151.101.1.1`) is assigned to servers in hundreds of distinct data centers across the globe. Each data center uses Border Gateway Protocol (BGP) to announce ownership of that IP prefix to adjacent Internet Service Provider (ISP) routers. When a user sends a packet to that IP, intermediate internet routers forward the packet along the lowest-cost BGP autonomous system (AS) hop path. As a result, the packet naturally lands at the <strong>geographically and topologically closest CDN PoP</strong> without requiring DNS-level geolocation lookups."},
        {"question": "What is Origin Shielding and why is it necessary for large-scale media sites?", "answer": "<strong>Origin Shielding</strong> is a centralized intermediate caching tier placed between edge PoPs and the origin server. In a CDN with 250 global PoPs, if an asset expires, all 250 PoPs could miss simultaneously, generating 250 parallel requests to the origin. With an Origin Shield (e.g. in the same cloud region as the origin), the 250 edge PoPs query the Origin Shield. The Origin Shield experiences a miss *only on the first request*, fetches the asset from the origin once, and serves all other 249 PoP requests from its own cache, reducing origin load by 99%."}
      ]
    },
    {
      "id": "static-vs-dynamic-acceleration",
      "title": "Static Asset Caching vs Dynamic Content Acceleration (TCP Optimization, TLS Termination)",
      "definition": "Static Asset Caching stores immutable static files (images, JS, CSS, video segments) on edge disks for direct delivery. Dynamic Content Acceleration (also known as Dynamic Site Acceleration / DSA) accelerates uncacheable, personalized API responses (e.g., search results, checkout carts) by optimizing network protocols, terminating TLS handshakes at the edge, maintaining persistent connection pools, and routing over private optimized fiber backbones.",
      "why_we_need_it": "Many engineers mistakenly believe CDNs can only cache static images. Dynamic API calls (`POST /checkout`, personalized feeds) cannot be cached. However, dynamic API calls still suffer from high connection setup latency (DNS + TCP + TLS). Dynamic Site Acceleration cuts dynamic API latency by 40-60% without caching a single byte of data!",
      "real_world_analogy": "Commuting via public roads vs a private bullet train: Static caching is having a grocery store on your street corner. Dynamic acceleration is needing to visit the downtown courthouse in person (uncacheable): instead of driving on congested public city streets with 50 traffic lights (public internet BGP hops), you get an escort onto a private high-speed underground bullet train (CDN private fiber backbone) that shoots you directly downtown in 3 minutes.",
      "how_it_works": "<p>1. <strong>Edge TLS Termination & TCP Optimization:</strong> The client establishes TCP and completes the TLS 1.3 cryptographic handshake with the <em>nearest Edge PoP</em> (e.g. 5ms away). This terminates the connection early. The CDN then communicates with the distant origin server using a <strong>pre-warmed pool of persistent, long-lived TCP connections</strong> with large TCP congestion windows (eliminating slow-start latency).</p><p>2. <strong>Private Backbone Routing:</strong> Standard public internet routing uses BGP, which prioritizes ISP cost agreements over latency, often routing packets across inefficient routes. Tier-1 CDNs route dynamic traffic over their own <strong>private global fiber backbones</strong>, bypassing public internet congestion points.</p><p>3. <strong>Protocol Multiplexing & HTTP/3 (QUIC):</strong> Edge servers negotiate modern HTTP/3 over UDP with modern mobile clients, eliminating Head-of-Line blocking and connection migration penalties when users switch between Wi-Fi and 5G cellular.</p><p>4. <strong>Edge Compression:</strong> CDNs dynamically compress API responses using <strong>Brotli</strong> (20-30% smaller than Gzip) on the fly before transmitting across the last mile.</p>",
      "conceptual_breakdown": [
        "<strong>TCP Slow-Start Elimination:</strong> New TCP connections start with a small Congestion Window (cwnd = 10 packets) and ramp up exponentially. CDN-to-origin connections stay warm forever with large congestion windows, achieving line-rate transmission instantly.",
        "<strong>Cache-Control Directives:</strong><br>&bull; `public, max-age=31536000, immutable`: Perfect for content-hashed assets (`main.a847f.js`).<br>&bull; `private, no-cache`: Can be accelerated dynamically by CDN, but CDN will not store the response.<br>&bull; `s-maxage=600`: Specifies TTL for public CDNs while allowing browser TTL to differ.",
        "<strong>Stale-While-Revalidate:</strong> `Cache-Control: max-age=60, stale-while-revalidate=30`. The CDN immediately serves a slightly stale cached asset to the user, and asynchronously triggers a background revalidation to the origin.",
        "<strong>Last-Mile Acceleration:</strong> 80% of dynamic latency occurs in the 'last mile' (the high-jitter cellular wireless connection between mobile phone and cell tower). Terminating connections at the closest edge minimizes packet retransmission timeouts."
      ],
      "arch_diagram": {
        "title": "Dynamic Site Acceleration (DSA) Network Optimization Pipeline",
        "tiers": [
          {
            "label": "Client Last-Mile (Cellular)",
            "nodes": [
              {
                "name": "Mobile Client (5G / Wi-Fi)",
                "type": "client",
                "icon": "📱",
                "what": "POST /api/v1/checkout",
                "why": "Terminates TCP/TLS at Edge in 5ms",
                "when": "Client mutation",
                "failure": "QUIC connection migration"
              }
            ]
          },
          {
            "label": "Edge Acceleration Tier (CDN PoP)",
            "nodes": [
              {
                "name": "Edge Envoy Proxy",
                "type": "lb",
                "icon": "⚡",
                "what": "Early TLS Termination + Brotli Compress",
                "why": "Eliminates TCP slow-start; pools warm connections",
                "when": "Every dynamic request",
                "failure": "Route over backup private path"
              }
            ]
          },
          {
            "label": "Optimized Private Fiber Transit Tier",
            "nodes": [
              {
                "name": "CDN Private Fiber Backbone",
                "type": "gateway",
                "icon": "🚀",
                "what": "Congestion-Free Private WAN",
                "why": "Bypasses public internet packet loss and BGP hops",
                "when": "Transit to Origin",
                "failure": "Pre-warmed persistent TCP tunnel"
              },
              {
                "name": "Origin API Server",
                "type": "service",
                "icon": "🏛️",
                "what": "Executes dynamic transaction",
                "why": "Receives request over pre-established socket",
                "when": "Execution phase",
                "failure": "Returns HTTP 200 with zero TLS overhead"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Static Asset Caching vs Dynamic Site Acceleration (DSA)",
        "columns": ["Dimension", "Static Asset Caching", "Dynamic Site Acceleration (DSA)"],
        "rows": [
          ["Content Type", "Images, CSS, JS, Fonts, Video Chunks", "Uncacheable API JSON, POST/PUT, User Feeds, Checkout"],
          ["Stored on Edge Disk?", "Yes (Cached until TTL expires or purged)", "No (Payload passes through without being stored)"],
          ["Optimization Mechanism", "Serves from local NVMe/RAM; zero origin hits", "Early TLS termination, pre-warmed TCP pools, private routing"],
          ["Cache-Control Header", "public, max-age=31536000, immutable", "private, no-cache, no-store"],
          ["Latency Reduction", "Drops from 200ms to 2ms (99% reduction)", "Drops from 800ms to 250ms (40-60% reduction)"]
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> DSA provides massive latency improvements for dynamic APIs, but requires premium Tier-1 CDN contracts (enterprise pricing) and does not reduce backend server CPU compute load (since every dynamic request still hits the origin).",
      "failure_scenarios": "<strong>The Accidental Dynamic User Account Leak:</strong> A developer removes `Cache-Control: no-cache` from `/api/me/profile`. The CDN's default caching rule treats the JSON response as a public static asset, caching User A's profile on the edge server for 1 hour. For the next 60 minutes, every other user visiting the website is served User A's cached personal profile, home address, and session tokens! <em>Mitigation:</em> Configure strict CDN edge rules that enforce `Cache-Control: private, no-store` on all authenticated endpoints and strip `Set-Cookie` headers on cached responses.",
      "common_mistakes": [
        {"mistake": "Believing that CDNs are useless for uncacheable dynamic APIs.", "correction": "CDNs provide Dynamic Site Acceleration (DSA): early TLS termination and warm persistent TCP connections reduce API response latency by 40-60% even if content is 0% cacheable."},
        {"mistake": "Using `Cache-Control: max-age=3600` on assets that have static unversioned filenames (`logo.png`).", "correction": "If you update the logo, users will see the old cached image for an hour. Use content-hashed filenames (`logo.8f3a1.png`) with `max-age=31536000` (1 year)."}
      ],
      "interview_questions": [
        {"question": "How does a CDN accelerate dynamic API requests that cannot be cached at the edge?", "answer": "Through <strong>Dynamic Site Acceleration (DSA)</strong>: 1. <strong>Early TLS Termination:</strong> The client completes the TCP handshake and TLS 1.3 negotiation with the nearest Edge PoP (e.g. 5ms away), eliminating 3 round-trips over long-haul WAN; 2. <strong>Connection Pooling:</strong> The edge maintains pre-warmed, persistent TCP connections to the origin with large TCP congestion windows, avoiding TCP slow-start; 3. <strong>Optimized Routing:</strong> The edge routes traffic over the CDN's private, congestion-free fiber backbone instead of the erratic public internet; 4. <strong>Edge Compression:</strong> Compresses API responses on-the-fly with Brotli before sending across the high-jitter mobile last mile."},
        {"question": "What is the difference between `no-cache` and `no-store` in HTTP Cache-Control headers?", "answer": "<strong>`no-store`</strong> means <em>do not store any copy of this response under any circumstances</em> in any browser, CDN, or proxy cache (strictly required for sensitive financial/PII data). <strong>`no-cache`</strong> is often misunderstood: it means <em>the cache CAN store the asset, but it MUST revalidate with the origin server (using ETag or If-Modified-Since) before serving it</em>. If the origin returns `HTTP 304 Not Modified`, the cache serves the cached copy, saving bandwidth."}
      ]
    },
    {
      "id": "cache-invalidation-and-edge-workers",
      "title": "Cache Purging/Invalidation Strategies & Serverless Edge Functions",
      "definition": "Cache Invalidation is the process of removing or updating stale cached objects across global CDN edge servers. Primary purging strategies include URL Purging, Surrogate-Key (Tag-Based) Invalidation, and Cache Invalidation via Asset Versioning (Cache Busting). Serverless Edge Functions (e.g. Cloudflare Workers, Fastly Compute@Edge, AWS Lambda@Edge) execute JavaScript/Wasm code directly at edge PoPs, intercepting requests before they reach origin servers.",
      "why_we_need_it": "'There are only two hard things in Computer Science: cache invalidation and naming things' (Phil Karlton). When an e-commerce price updates or a breaking news headline is corrected, serving stale cached data damages revenue and trust. Edge workers unlock programmable CDN edge execution: geofencing, A/B testing, header manipulation, and edge authentication with zero origin latency.",
      "real_world_analogy": "A national billboard campaign: URL Purging is driving a crew to all 5,000 billboards across the country to tear down the old posters one by one. Cache Busting (Asset Versioning) is simply printing the new poster with a new catalog number and ordering everyone to display only the new number. Edge Workers are hiring a live local actor at each billboard to dynamically swap the billboard slogan based on whether it is raining in that specific city right now.",
      "how_it_works": "<p>1. <strong>Purging Strategies:</strong><br>&bull; <em>Single URL Purge:</em> API call to CDN: `PURGE /products/101`. CDN broadcasts invalidation to all 200 PoPs within 150ms.<br>&bull; <em>Surrogate-Key / Cache-Tag Purging (Fastly / Cloudflare):</em> Origin attaches headers: `Surrogate-Key: product-101 brand-nike category-shoes`. When Nike changes its brand logo, the backend issues a single tag purge: `PURGE TAG brand-nike`. The CDN instantly evicts all 10,000 products associated with that tag globally!<br>&bull; <em>Cache Busting (Content Hashing):</em> Modern web frameworks append a content hash to filenames (`bundle.8f92a.js`). The file is cached forever (`max-age=31536000, immutable`). When code changes, the filename changes, completely bypassing the need for active cache purges.</p><p>2. <strong>Serverless Edge Workers (V8 Isolates / WebAssembly):</strong><br>&bull; Unlike traditional AWS Lambda which spins up heavy container micro-VMs (causing 100ms-1s cold starts), Cloudflare Workers use <strong>Google V8 Isolates</strong>. Thousands of isolated tenant contexts run inside a single shared memory process with <strong>zero cold starts (&lt;5ms)</strong>.<br>&bull; <em>Edge Use Cases:</em> JWT authentication validation at the edge, A/B test routing, Geo-redirection (`/us/` vs `/eu/`), bot mitigation, edge image resizing, and feature flag evaluation.</p>",
      "conceptual_breakdown": [
        "<strong>Soft Purge vs Hard Purge:</strong> <em>Hard Purge</em> instantly deletes the asset from cache; the next read blocks on origin fetch. <em>Soft Purge</em> marks the asset as stale: the edge serves the stale asset to the client while triggering an asynchronous background fetch to the origin.",
        "<strong>V8 Isolates Architecture:</strong> Isolates provide secure, lightweight multi-tenancy in pure memory. Starting a V8 Isolate takes ~0.5ms and consumes only ~5MB of RAM.",
        "<strong>Global Key-Value at Edge (Cloudflare KV):</strong> Low-latency distributed key-value store replicated across all CDN edge PoPs, providing read latencies &lt;15ms globally.",
        "<strong>Edge Auth Gatekeeper:</strong> Validating JWT cryptographic signatures at the edge rejects unauthorized API requests before they ever enter your cloud VPC, saving backend compute and database connection resources."
      ],
      "arch_diagram": {
        "title": "Edge Worker Interception & Tag-Based Cache Purge Architecture",
        "tiers": [
          {
            "label": "Global Client Ingress Tier",
            "nodes": [
              {
                "name": "Incoming HTTP Request",
                "type": "client",
                "icon": "🌐",
                "what": "GET /api/v1/feed with JWT",
                "why": "Edge worker intercepts first",
                "when": "Client query",
                "failure": "Blocked at edge if unauthorized"
              }
            ]
          },
          {
            "label": "Edge Computing Layer (Cloudflare Workers / V8)",
            "nodes": [
              {
                "name": "Edge Worker (V8 Isolate)",
                "type": "service",
                "icon": "⚡",
                "what": "Validates JWT + A/B Experiment Routing",
                "why": "Executes in 1ms with ZERO cold start",
                "when": "Edge interception",
                "failure": "Returns 401 Unauthorized directly from edge"
              },
              {
                "name": "Surrogate-Key Cache Index",
                "type": "cache",
                "icon": "🏷️",
                "what": "Cache Tags: [product-42, author-bob]",
                "why": "Enables instant multi-object tag purging",
                "when": "Cache lookup",
                "failure": "Pass-through to origin on miss"
              }
            ]
          },
          {
            "label": "Origin Database & Admin Purge Ingress",
            "nodes": [
              {
                "name": "Backend Admin Service",
                "type": "database",
                "icon": "🏛️",
                "what": "Issues: PURGE TAG 'product-42'",
                "why": "Purges 500 edge PoPs in 150ms globally",
                "when": "Price update in CMS",
                "failure": "Soft-purge background revalidation"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Cache Invalidation Strategies Comparison",
        "columns": ["Strategy", "How It Operates", "Purge Latency", "Implementation Complexity", "Reliability"],
        "rows": [
          ["Cache Busting (Fingerprinting)", "Filename hash changes (`app.8f3a.js`); cached forever", "Instantaneous (Clients request new URL)", "Low (Automated by Webpack/Vite)", "100% bulletproof (Zero stale risk)"],
          ["Surrogate-Key (Tag Purging)", "Origin emits tags in headers; API issues tag purge", "Fast (150ms across global PoPs)", "Medium (Requires CDN provider tag support)", "High (Purges entire related collections)"],
          ["URL API Purge", "Call CDN REST API to invalidate exact path", "Fast (100-300ms)", "Low", "Vulnerable to missed query parameters"],
          ["TTL-Only Expiry", "Wait for time-to-live to elapse", "Slow (Minutes to hours)", "Zero", "Poor (Stale data served during TTL window)"]
        ]
      },
      "tradeoffs": "<strong>Edge Workers:</strong> Deliver ultra-low latency (&lt;10ms) and eliminate origin load, but have strict compute constraints (e.g. 50ms CPU time limits, 128MB RAM limits) and cannot maintain stateful in-memory database connections.",
      "failure_scenarios": "<strong>The Massive Hard Purge Origin Meltdown:</strong> A marketing team changes a sitewide navbar link and triggers a 'Purge Everything' hard cache clear across Cloudflare. Instantly, all 200 edge PoPs wipe their local caches. The next second, 100,000 live users experience cache misses simultaneously. 100,000 requests hit the origin web servers, immediately crashing NGINX and MySQL with 100% CPU lockup. <em>Mitigation:</em> Never perform full cache purges! Use <strong>Soft Purges (Stale-While-Revalidate)</strong> so the CDN continues serving stale content while lazily refreshing the cache in the background.",
      "common_mistakes": [
        {"mistake": "Running full global cache purges during peak traffic hours.", "correction": "Use Soft Purge or Surrogate-Key targeted invalidations to avoid overwhelming your origin with a thundering herd."},
        {"mistake": "Attempting to run heavy relational database queries directly from inside a Cloudflare Edge Worker.", "correction": "Edge workers are ephemeral. Connect to global distributed edge databases (Hyperdrive, Cloudflare D1, Turso) or query via HTTP APIs."}
      ],
      "interview_questions": [
        {"question": "How does Surrogate-Key (Tag-Based) cache purging work in modern CDNs like Fastly and Cloudflare?", "answer": "When the origin serves an HTTP response, it attaches a `Surrogate-Key` header with space-separated identifiers: e.g. `Surrogate-Key: product-102 category-electronics brand-sony`. The CDN edge caches the asset and indexes it under those tags. When an inventory price changes for Sony, the backend sends an API request: `PURGE /service/xyz/key/brand-sony`. The CDN's control plane broadcasts this invalidation, and all edge PoPs globally <strong>evict every single cached page containing that tag in under 150 milliseconds</strong>, eliminating the need to track and purge thousands of individual product URLs."},
        {"question": "Why do Cloudflare Workers use V8 Isolates instead of Docker containers or AWS Lambda micro-VMs?", "answer": "AWS Lambda runs code inside micro-VMs (Firecracker), which require spinning up a guest Linux kernel and runtime environment, taking 100ms to 2 seconds for a 'cold start'. <strong>Cloudflare Workers use Google V8 Isolates</strong> (the same sandboxing mechanism Google Chrome uses to isolate browser tabs). An isolate runs within a single long-lived process, creating a secure, isolated JavaScript execution context in <strong>under 1 millisecond</strong> with only ~5MB of memory overhead, completely eliminating cold starts at the global edge."}
      ]
    }
  ]
}

# ==========================================
# MODULE 20: File & Storage Systems: Object, Block & File
# ==========================================
m20 = {
  "module_id": "20",
  "module_title": "File & Storage Systems: Object, Block & File",
  "description": "Master distributed storage architectures: Block Storage (SAN/EBS) vs Network File Systems (NFS/EFS) vs Object Storage (AWS S3/Ceph), metadata engines, presigned URLs, and Reed-Solomon Erasure Coding.",
  "topics": [
    {
      "id": "block-vs-file-vs-object-storage",
      "title": "Storage Typology: Block Storage (SAN/EBS) vs Network File Systems (NFS) vs Object Storage (S3)",
      "definition": "Modern computer systems utilize three distinct storage typologies: Block Storage (AWS EBS, SAN) exposes raw disk sectors managed by an OS filesystem; File Storage (NFS, AWS EFS, SMB) organizes data into a hierarchical directory tree with shared multi-client file locks; Object Storage (AWS S3, Ceph, Cloudflare R2) stores immutable unstructured data in a flat namespace accessed via HTTP REST APIs.",
      "why_we_need_it": "Attempting to store 50 petabytes of Instagram photos on a Network File System (NFS) will crash the operating system's directory inode tables. Attempting to run a high-performance PostgreSQL database on Object Storage (S3) will produce catastrophic query latencies. Choosing the right storage engine is foundational to system design.",
      "real_world_analogy": "Vehicle parking: Block Storage is owning a private dedicated garage stall right under your apartment (fast, low-latency, only accessible by your car). File Storage is an office shared valet parking lot with assigned rows and numbered spots (shared access, organized hierarchy). Object Storage is an infinite automated commercial shipping container port: containers have unique serial numbers (Keys); you hand a shipping slip to an automated crane, and it fetches the container from an infinite flat yard.",
      "how_it_works": "<p>1. <strong>Block Storage (Low Latency, Single Host):</strong> Exposes raw 512-byte or 4096-byte blocks to the operating system over Fibre Channel, iSCSI, or NVMe-oF. The host OS formats the volume with a filesystem (ext4, XFS, NTFS). Delivers single-digit microsecond latency and extreme IOPS (up to 256,000 IOPS on AWS EBS io2). Strictly limited to attachment by a single VM/compute host at a time.</p><p>2. <strong>File Storage (Shared Hierarchical POSIX):</strong> Exposes a POSIX-compliant hierarchical folder directory tree (`/mnt/shared/data/file.pdf`). Supports shared multi-reader / multi-writer access over the network with byte-range locking. However, file locking and directory traversal overhead cause performance degradation past millions of files.</p><p>3. <strong>Object Storage (Infinite Scale, Flat Namespace):</strong> Data is stored as immutable <strong>Objects</strong> comprising: <em>Unique Key</em> (string name), <em>Data Payload</em> (unstructured binary bytes), and <em>Metadata</em> (custom key-value pairs). Accessed strictly over HTTP via REST APIs (`GET`, `PUT`, `DELETE`). The namespace is completely flat (directories are merely visual slash `/` prefixes in key strings). Scales to exabytes of storage with 99.999999999% (11 9's) durability.</p>",
      "conceptual_breakdown": [
        "<strong>POSIX Compliance:</strong> Block and File storage support POSIX operations (random byte writes, file appends, atomic renames). Object storage does NOT support POSIX (you cannot modify 10 bytes inside a 5GB video file; you must overwrite the entire object).",
        "<strong>Throughput vs Latency:</strong> Block storage optimizes for ultra-low latency (&lt;1ms); Object storage optimizes for massive aggregate throughput (terabits/sec across thousands of parallel workers) and near-zero cost per gigabyte.",
        "<strong>Metadata Flexibility:</strong> Object storage allows attaching arbitrary custom metadata headers (e.g. `x-amz-meta-photographer: Alice`), enabling powerful search and lifecycle tagging.",
        "<strong>Cost Disparity:</strong> Block storage (EBS) costs ~$0.10/GB/month. Object storage (S3) costs ~$0.023/GB/month (4x cheaper), and S3 Glacier archive costs ~$0.00099/GB/month (100x cheaper!)."
      ],
      "arch_diagram": {
        "title": "Storage Typology Architecture Comparison (Block vs File vs Object)",
        "tiers": [
          {
            "label": "Workload Classification",
            "nodes": [
              {
                "name": "Database Engines (Postgres/MySQL)",
                "type": "database",
                "icon": "🐘",
                "what": "Requires random read/write byte I/O",
                "why": "Needs POSIX filesystem & sub-millisecond IOPS",
                "when": "ACID transactions",
                "failure": "Attached to Block Storage (EBS)"
              },
              {
                "name": "User Media & Archives (YouTube/Drive)",
                "type": "client",
                "icon": "🎥",
                "what": "Petabytes of videos, images, logs",
                "why": "Immutable binary data accessed via HTTP",
                "when": "Streaming & archiving",
                "failure": "Stored in Object Storage (S3)"
              }
            ]
          },
          {
            "label": "Storage Engine Implementations",
            "nodes": [
              {
                "name": "Block Storage (AWS EBS / SAN)",
                "type": "database",
                "icon": "🧱",
                "what": "Raw Sector Blocks (iSCSI/NVMe)",
                "why": "Dedicated single-instance extreme IOPS",
                "when": "Database disk volumes",
                "failure": "EBS snapshot backup"
              },
              {
                "name": "Shared File Storage (NFS / EFS)",
                "type": "database",
                "icon": "📁",
                "what": "Hierarchical POSIX Directory Tree",
                "why": "Shared multi-instance read/write",
                "when": "Legacy apps, WordPress media",
                "failure": "Network mount reconnect"
              },
              {
                "name": "Object Storage (AWS S3 / Ceph)",
                "type": "database",
                "icon": "🪣",
                "what": "Flat Key-Value REST Namespace",
                "why": "Exabyte scale, 11 9s durability, HTTP API",
                "when": "Cloud native file storage",
                "failure": "Cross-AZ Erasure Coding"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Block vs File vs Object Storage Comparison Matrix",
        "columns": ["Feature", "Block Storage (AWS EBS)", "File Storage (NFS / EFS)", "Object Storage (AWS S3)"],
        "rows": [
          ["Data Access Protocol", "Raw SCSI / NVMe blocks", "File protocols (NFS, SMB, CIFS)", "HTTP / REST API (GET, PUT, DELETE)"],
          ["Namespace Structure", "Flat disk blocks (formatted by OS)", "Hierarchical Directory Tree (Folders)", "Flat Key-Value namespace (Virtual prefixes)"],
          ["Latency", "Lowest (<1ms IOPS)", "Moderate (2 - 10ms)", "High (50 - 100ms first byte latency)"],
          ["POSIX Compatibility", "Full POSIX compliance", "Full POSIX compliance", "Non-POSIX (Immutable full object writes only)"],
          ["Scalability Limit", "Terabytes per volume (e.g. 64TB max)", "Petabytes (limited by directory metadata)", "Virtually Infinite (Exabytes across billions of keys)"],
          ["Cost per GB", "Highest (~$0.10 / GB)", "Moderate (~$0.30 / GB)", "Lowest (~$0.02 / GB; Archive: $0.001)"],
          ["Best Use Case", "Databases, OS Boot drives, Caches", "Shared home dirs, legacy multi-server apps", "Static assets, Big Data lakes, Backups, Videos"]
        ]
      },
      "tradeoffs": "<strong>Block Storage:</strong> Unbeatable latency and IOPS for databases, but cannot be shared across multiple web servers and is expensive. <strong>Object Storage:</strong> Boundless scale, massive aggregate throughput, and dirt cheap, but cannot perform partial byte modifications in place and has higher per-request latency.",
      "failure_scenarios": "<strong>The Inode Exhaustion Outage on File Storage:</strong> An application stores 20 million small uploaded profile avatars in a single directory on an NFS file share (`/var/uploads/`). The operating system's filesystem runs out of directory inodes and memory trying to stat the folder. New uploads fail with `No space left on device` even though 80% of disk gigabytes are completely free! <em>Mitigation:</em> Migrate all unstructured user file uploads to <strong>Object Storage (AWS S3)</strong>, which has a flat namespace with zero inode constraints.",
      "common_mistakes": [
        {"mistake": "Attempting to run a relational database (PostgreSQL/MySQL) directly on top of AWS EFS or S3.", "correction": "Network file systems lack the low latency, precise byte-locking, and high IOPS required by relational engines. Always use dedicated Block Storage (AWS EBS) for database data files."},
        {"mistake": "Storing petabytes of media files on local VM block storage volumes.", "correction": "Block volumes are expensive and hard to rebalance. Store all media files in S3 and distribute them globally via a CDN."}
      ],
      "interview_questions": [
        {"question": "Why is Object Storage like AWS S3 preferred over Network File Systems (NFS) for storing petabytes of user data?", "answer": "1. <strong>Unlimited Flat Scalability:</strong> NFS relies on hierarchical directory trees where directory locking and inode limits degrade past millions of files; S3 uses a flat key-value namespace partitioned across massive storage clusters;<br>2. <strong>Cost Efficiency:</strong> S3 is 5x-10x cheaper per GB and offers automated tiered lifecycle archiving (Glacier at $0.001/GB);<br>3. <strong>Extreme Durability:</strong> S3 uses Reed-Solomon Erasure Coding across 3+ Availability Zones, delivering 99.999999999% (11 9s) durability;<br>4. <strong>Native HTTP/REST Integration:</strong> Clients can stream media directly over HTTP using Presigned URLs without requiring network mount agents."},
        {"question": "Can you modify a portion of an existing object in AWS S3?", "answer": "No. Object storage treats objects as <strong>immutable entities</strong>. You cannot perform in-place random byte writes (e.g. updating 10 bytes in the middle of a file). To change an object, you must upload the complete new version of the object (`PUT`), replacing the old version entirely. (Though S3 does support byte-range reads via the `Range: bytes=0-1000` HTTP header)."}
      ]
    },
    {
      "id": "object-storage-internals",
      "title": "Object Storage Architecture: Buckets, Keys, Metadata, Immutability & Signed URLs",
      "definition": "Object Storage organizes data into flat containers called Buckets, where each item is identified by a unique String Key. Internally, the architecture decouples Metadata Management (LSM-trees / Key-Value indexes storing permissions, size, and chunk locations) from Blob Storage Engines (storage nodes persisting raw data chunks). Presigned URLs enable secure, direct client uploads without proxying heavy binary data through application servers.",
      "why_we_need_it": "Proxying 1GB video uploads through application web servers saturates application thread pools, exhausts network bandwidth, and inflates server costs. Presigned URLs allow web browsers to upload directly to S3 storage nodes securely, while S3's decoupled metadata architecture enables searching and lifecycle policy enforcement across billions of files.",
      "real_world_analogy": "A coat check at a luxury hotel: You hand your coat to the attendant. The attendant clips a plastic ticket with a unique number (Key) to your coat, puts the coat into an enormous automated warehouse (Blob Storage), and records your name and phone number on an index card (Metadata). When you return, you show your ticket, and the automated rack brings your coat back. You never enter the warehouse yourself.",
      "how_it_works": "<p>1. <strong>Decoupled Architecture:</strong> Object storage is split into two independent tiers:<br>&bull; <em>Metadata Tier:</em> Distributed key-value store (e.g., CockroachDB / Cassandra / RocksDB) that maps `Bucket + Key` &rarr; `[Chunk IDs, Version, Size, ACL, Custom Metadata]`.<br>&bull; <em>Storage Node Tier:</em> High-density commodity storage servers holding raw data chunks on disk with local block filesystems.</p><p>2. <strong>Flat Namespace Virtual Hierarchy:</strong> In S3, the key `images/2026/user_101.jpg` is a <em>single flat string</em>. S3 does not create an `images` directory or a `2026` folder. The forward slashes `/` are simply delimiter characters that the AWS console UI parses as virtual folders.</p><p>3. <strong>Strong Consistency in Modern S3:</strong> Since December 2020, AWS S3 provides <strong>Read-After-Write Strong Consistency</strong> for `PUT` and `DELETE` requests of objects in all regions without performance penalties.</p><p>4. <strong>Presigned URLs Workflow:</strong><br>&bull; Step 1: Web client asks backend: 'I want to upload a 500MB video `cat.mp4`'.<br>&bull; Step 2: Backend verifies user auth, calls AWS SDK to generate a <strong>Presigned PUT URL</strong> signed with IAM secret credentials, configured with a 15-minute expiration and exact S3 key destination.<br>&bull; Step 3: Backend returns the signed URL to the browser.<br>&bull; Step 4: Browser sends an `HTTP PUT` directly to S3's edge endpoints with the binary payload.<br>&bull; Step 5: S3 receives bytes directly, validates the cryptographic signature, persists the object, and emits an S3 Event Notification to AWS SQS/Lambda to notify the backend that the upload is complete!</p>",
      "conceptual_breakdown": [
        "<strong>Zero Application Server Load:</strong> Presigned URLs completely offload gigabytes of file upload/download traffic from your backend application servers directly to S3.",
        "<strong>Key Prefix Sharding:</strong> S3 automatically scales throughput across partitions based on key prefixes. To maximize throughput (thousands of PUTs/sec), design prefixes with high entropy.",
        "<strong>S3 Lifecycle Rules:</strong> Automated policies that transition objects between storage classes: Hot (Standard) &rarr; Warm (Infrequent Access, 30 days) &rarr; Cold Archive (Glacier, 90 days) &rarr; Delete (365 days).",
        "<strong>Multipart Upload Requirement:</strong> Any object larger than 100MB should be uploaded using S3 Multipart Upload."
      ],
      "arch_diagram": {
        "title": "Secure Direct Upload via S3 Presigned URLs Architecture",
        "tiers": [
          {
            "label": "Client Browser Tier",
            "nodes": [
              {
                "name": "Web / Mobile Client",
                "type": "client",
                "icon": "📱",
                "what": "1. Requests Upload Permit | 3. PUTs 500MB Video",
                "why": "Streams bytes directly to S3; skips app server!",
                "when": "Media upload flow",
                "failure": "Resumes via Multipart Upload"
              }
            ]
          },
          {
            "label": "Application Control Plane",
            "nodes": [
              {
                "name": "App Auth Server",
                "type": "service",
                "icon": "🔑",
                "what": "2. Generates Cryptographic Presigned URL",
                "why": "Enforces authorization and file size limits",
                "when": "Initial upload intent",
                "failure": "Rejects unauthorized users"
              }
            ]
          },
          {
            "label": "AWS S3 Object Storage Tier",
            "nodes": [
              {
                "name": "S3 Bucket Ingress Endpoint",
                "type": "database",
                "icon": "🪣",
                "what": "Validates IAM Signature & Stores Object",
                "why": "Direct streaming ingestion at terabit scale",
                "when": "Client PUT execution",
                "failure": "Emits S3:ObjectCreated Event to SQS"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Direct S3 Upload via Presigned URL vs App Server Proxy",
        "columns": ["Dimension", "Proxy Through Application Server", "Direct S3 Upload via Presigned URL"],
        "rows": [
          ["App Server Bandwidth", "Saturated (Every byte streams through app memory)", "Zero (App only generates a 200-byte URL string)"],
          ["App Server Thread Blocking", "High (Threads blocked for duration of slow upload)", "Zero (App server finishes in <10ms)"],
          ["Max File Size", "Constrained by web server RAM / reverse proxy limits", "Up to 5 Terabytes (via S3 Multipart Upload)"],
          ["Security Model", "App verifies cookies on upload", "Cryptographic HMAC-SHA256 signature in query params with strict TTL"],
          ["Failure Resilience", "Upload fails if app server redeploys", "Upload succeeds independently directly against S3 edge"]
        ]
      },
      "tradeoffs": "<strong>Presigned URLs:</strong> Offload 100% of bandwidth and scale to thousands of concurrent multi-gigabyte uploads with zero server load. However, the application loses real-time visibility into upload progress (must rely on S3 Event Notifications upon completion) and must handle post-upload virus/NSFW scanning asynchronously.",
      "failure_scenarios": "<strong>The App Server Thread Pool OOM Death:</strong> A company allows users to upload 4K video files by submitting `POST /api/upload` directly to their Node.js/Python backend. 200 users on slow 3G cellular connections begin uploading 1GB files simultaneously. 200 web worker threads are tied up for 20 minutes buffering network bytes in RAM. The web server runs out of heap memory, crashes with OOM, and takes down the entire public REST API for all users. <em>Mitigation:</em> Never proxy large file uploads through application servers. Always use <strong>S3 Presigned URLs</strong>.",
      "common_mistakes": [
        {"mistake": "Setting Presigned URL expiration to 24 hours.", "correction": "Presigned URLs should expire in 10-15 minutes. Once generated, the browser should begin the upload immediately."},
        {"mistake": "Using predictable sequential prefixes (e.g. `s3://bucket/2026-10-03/...`) for ultra-high-throughput ingest.", "correction": "Partition keys should have high entropy or random prefixes (e.g. `s3://bucket/a8f2-2026-10-03/...`) to avoid hotspotting S3 storage partitions when exceeding 3,500 PUTs/second."}
      ],
      "interview_questions": [
        {"question": "How do S3 Presigned URLs work under the hood and why are they cryptographically secure?", "answer": "A <strong>Presigned URL</strong> encodes authentication credentials into the URL query parameters using AWS Signature Version 4 (SigV4). The backend creates a canonical request string including the HTTP method (`PUT`), target S3 bucket, exact object key, expiration timestamp, and content headers. It computes an <strong>HMAC-SHA256 signature</strong> of this request using the backend's secret IAM access key. When the browser sends a `PUT` to the URL, S3 validates the signature using its internal key copy and verifies that the current timestamp is within the expiration window. The client never gets access to AWS credentials, but can upload to that exact key safely."},
        {"question": "How does S3 achieve Read-After-Write Strong Consistency?", "answer": "Historically, S3 was eventually consistent (using read-replicas for metadata). In 2020, AWS re-architected S3 metadata to provide <strong>Strong Read-After-Write Consistency</strong> for all `PUT` and `DELETE` operations. When an object is created or deleted, the mutation is committed to a replicated, strongly consistent metadata consensus tier before returning success to the caller. Any subsequent read immediately observes the new object or version."}
      ]
    },
    {
      "id": "erasure-coding-and-multipart-uploads",
      "title": "High Durability: Reed-Solomon Erasure Coding, Chunking & Resumable Multipart Uploads",
      "definition": "Reed-Solomon Erasure Coding is a mathematical data protection algorithm that divides an object into $K$ data chunks and computes $M$ parity chunks (total $N = K + M$). The original data can be 100% reconstructed from ANY $K$ of the $N$ chunks. Resumable Multipart Uploads divide large binary files into independent parallel parts (5MB to 5GB each) that can be uploaded concurrently and retried independently upon failure.",
      "why_we_need_it": "Traditional 3x replication consumes 200% storage overhead (storing 1PB requires 3PB of raw disk!). Reed-Solomon Erasure Coding (e.g. $8+4$) delivers equivalent or superior durability (99.999999999%) with only 50% storage overhead, saving cloud providers billions of dollars in hard drives.",
      "real_world_analogy": "A mathematical equation with variables: If you know that $x + y = 10$, and you lose $y$, but you still have $x=4$, you can solve for $y$ instantly. Erasure coding writes redundant mathematical parity equations across disks. If a hard drive explodes, the storage engine solves the linear equations using the surviving disks to reconstruct the missing data in real time.",
      "how_it_works": "<p>1. <strong>Reed-Solomon ($K + M$) Mechanics:</strong> An object is sliced into $K$ data blocks. Using Galois Field ($GF(2^8)$) matrix multiplication, the engine generates $M$ parity blocks.<br>&bull; Example: $K = 8, M = 4$. Total blocks = 12.<br>&bull; The 12 blocks are distributed across 12 physically separate server racks / Availability Zones.<br>&bull; The system can tolerate the simultaneous catastrophic failure of <strong>ANY 4 disks or servers</strong> with ZERO data loss!<br>&bull; Storage Overhead = $M/K = 4/8 = 50\\%$ (compared to 200% for 3x replication!).</p><p>2. <strong>Multipart Upload Lifecycle (Files > 100MB):</strong><br>&bull; Step 1 (`InitiateMultipartUpload`): S3 returns an `UploadId`.<br>&bull; Step 2 (`UploadPart`): Client slices a 10GB file into 1,000 independent 10MB chunks. Chunks are uploaded in parallel across 10 network threads. If Part #42 fails due to a network drop, <em>only Part #42 is retried</em> (saving 9.9GB of wasted bandwidth!). Each uploaded part returns an `ETag` checksum.<br>&bull; Step 3 (`CompleteMultipartUpload`): Client sends an ordered manifest of part numbers and ETags. S3 validates the checksums, concatenates the chunks into a single object, and completes the transaction.</p><p>3. <strong>Chunk Healing & Bit-Rot Scrubbing:</strong> Background scrubber daemons continuously compute SHA-256 checksums of stored blocks on disk. If bit-rot or sector decay is detected, the engine reads $K$ surviving blocks, reconstructs the damaged block via erasure coding, and writes it to a fresh disk.</p>",
      "conceptual_breakdown": [
        "<strong>11 9's Durability (99.999999999%):</strong> Statistically means that if you store 10,000,000 objects in S3, you can expect to lose a single object once every 10,000 years.",
        "<strong>CPU Trade-off:</strong> Erasure coding saves disk storage costs, but requires CPU compute cycles to calculate parity matrices during writes and reconstruct lost blocks during reads.",
        "<strong>Resumable Uploads:</strong> Multipart upload is mandatory for mobile or unstable networks; an interrupted 5GB upload can resume from the last completed part.",
        "<strong>S3 Part Constraints:</strong> Part size must be between 5MB and 5GB. Maximum number of parts per object is 10,000 (enabling maximum single object size of 5 Terabytes)."
      ],
      "arch_diagram": {
        "title": "Reed-Solomon Erasure Coding (K=8 Data + M=4 Parity across 12 Nodes)",
        "tiers": [
          {
            "label": "Data Slicing & Parity Matrix Tier",
            "nodes": [
              {
                "name": "Raw File (100MB)",
                "type": "client",
                "icon": "📄",
                "what": "Sliced into K=8 Data Chunks (12.5MB each)",
                "why": "Generates M=4 Parity Chunks via Vandermonde Matrix",
                "when": "Ingestion write path",
                "failure": "Distributed across 12 separate servers"
              }
            ]
          },
          {
            "label": "12 Dispersed Storage Nodes (Tolerates 4 Crashes)",
            "nodes": [
              {
                "name": "Data Nodes D1..D8",
                "type": "database",
                "icon": "💾",
                "what": "8 Primary Data Chunks",
                "why": "Standard data blocks",
                "when": "Normal reads",
                "failure": "If D2 and D5 crash, reconstructed from parity!"
              },
              {
                "name": "Parity Nodes P1..P4",
                "type": "database",
                "icon": "🛡️",
                "what": "4 Redundancy Parity Chunks",
                "why": "Provides mathematical recovery",
                "when": "Disk failure detected",
                "failure": "Can lose up to 4 nodes simultaneously"
              }
            ]
          },
          {
            "label": "Dynamic Reconstruction Tier",
            "nodes": [
              {
                "name": "Erasure Code Reconstructor",
                "type": "service",
                "icon": "🧮",
                "what": "Reads ANY 8 surviving chunks",
                "why": "Solves matrix equations to rebuild missing chunks",
                "when": "Disk crash or background scrubber repair",
                "failure": "100% data recovery guarantee"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "3x Replication vs Reed-Solomon Erasure Coding",
        "columns": ["Protection Scheme", "Storage Overhead", "Tolerable Node Failures", "Write CPU Overhead", "Reconstruction I/O Cost"],
        "rows": [
          ["3x Replication", "200% (1PB data requires 3PB raw disk)", "Tolerates 2 node failures", "Zero (simple byte copy)", "Low (copy surviving replica)"],
          ["Erasure Coding (RS 8+4)", "50% (1PB data requires 1.5PB raw disk)", "Tolerates 4 node failures (Double resilience!)", "High (Galois field matrix math)", "Higher (Must read 8 chunks to rebuild 1 dead chunk)"],
          ["Erasure Coding (RS 16+4)", "25% (1PB data requires 1.25PB raw disk)", "Tolerates 4 node failures", "Highest", "Must read 16 chunks to rebuild 1 dead chunk"]
        ]
      },
      "tradeoffs": "<strong>Replication:</strong> Best for ultra-low latency, small hot files, or local database WALs where CPU overhead cannot be tolerated. <strong>Erasure Coding:</strong> The universal standard for large-scale object storage, cold archives, and big data lakes, cutting infrastructure disk hardware costs by 50-75%.",
      "failure_scenarios": "<strong>The Incomplete Multipart Upload Billing Leak:</strong> A video platform's users initiate 50,000 multipart uploads a day. Many uploads fail or are abandoned halfway through. S3 stores all uploaded 100MB parts indefinitely until `CompleteMultipartUpload` or `AbortMultipartUpload` is called. Over 2 years, 500 Terabytes of orphan uncompleted parts accumulate, costing the company $12,000/month in wasted storage bills! <em>Mitigation:</em> Configure an automated <strong>S3 Lifecycle Rule</strong> to automatically abort and purge incomplete multipart uploads after 7 days.",
      "common_mistakes": [
        {"mistake": "Uploading a 5GB file to S3 as a single standard `PUT` request.", "correction": "Single `PUT` requests over 100MB are fragile; a dropped packet at 99% forces re-uploading the entire 5GB. Always use Multipart Upload for files >100MB."},
        {"mistake": "Applying Erasure Coding to small 1KB metadata files.", "correction": "Erasure coding small files creates chunk fragment overhead. Group small files into larger packs (like HDFS SequenceFiles or Ceph RADOS objects) before erasure coding."}
      ],
      "interview_questions": [
        {"question": "How does Reed-Solomon Erasure Coding provide 11 9's durability with only 50% storage overhead compared to 3x replication?", "answer": "In <strong>3x replication</strong>, 1GB of data is copied 3 times, requiring 3GB of disk (200% overhead) and can survive losing at most 2 copies. In <strong>Reed-Solomon Erasure Coding (e.g. $8+4$)</strong>, 1GB of data is sliced into 8 data chunks (125MB each) and 4 parity chunks (125MB each) using Galois field matrix math, totaling 1.5GB of disk (only 50% overhead!). The original data can be mathematically reconstructed from <strong>ANY 8 of the 12 chunks</strong>. This configuration survives the loss of <strong>4 simultaneous disk/server failures</strong>—providing twice the fault tolerance of 3x replication while saving 50% of raw disk costs."},
        {"question": "How do you design a reliable, resumable large video upload system (e.g. YouTube video upload)?", "answer": "1. <strong>Chunking & Multipart Upload:</strong> The client application slices the video into 10MB chunks; 2. <strong>Direct S3 Ingestion via Presigned URLs:</strong> The client requests Presigned URLs for each part and uploads parts in parallel directly to S3; 3. <strong>Client-Side Resumption Manifest:</strong> The client tracks uploaded part ETags in IndexedDB/local storage. If the user loses Wi-Fi or closes the browser, reopening the page checks the manifest and resumes uploading only the missing chunks; 4. <strong>Checksum Verification:</strong> S3 verifies MD5/SHA256 checksums per part; 5. <strong>Asynchronous Transcoding Trigger:</strong> Upon `CompleteMultipartUpload`, S3 emits an event to SQS to trigger the asynchronous transcoding worker pipeline."}
      ]
    }
  ]
}

with open(Path('content/hld/module_19.json'), 'w', encoding='utf-8') as f:
    json.dump(m19, f, ensure_ascii=False, indent=2)
print("Module 19 written successfully!")

with open(Path('content/hld/module_20.json'), 'w', encoding='utf-8') as f:
    json.dump(m20, f, ensure_ascii=False, indent=2)
print("Module 20 written successfully!")
