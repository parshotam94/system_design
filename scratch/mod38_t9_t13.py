# module 38 topics 9 to 13
import json

t9 = {
    "id": "design-distributed-cache-redis",
    "title": "Problem 9 (Intermediate): Design a Distributed In-Memory Cache (Redis-like)",
    "definition": "A Distributed In-Memory Key-Value Cache (e.g., Redis, Memcached, Hazelcast) stores frequently accessed datasets in RAM across a cluster of nodes, delivering sub-millisecond read and write latency. The system supports high throughput, memory eviction policies (LRU/LFU), data partitioning via Consistent Hashing, primary-replica replication, and persistent snapshot recovery (RDB / AOF).",
    "why_we_need_it": "### System Requirements\n**Functional Requirements:**\n1. `GET(key)` and `SET(key, value, ttl)` with sub-millisecond response times.\n2. Automatic memory eviction when RAM capacity is reached (LRU, LFU).\n3. High availability via automated replication and failover.\n4. Configurable persistence to disk to survive power outages.\n\n**Non-Functional Requirements:**\n1. 10 million requests/sec throughput across a horizontally partitioned cluster.\n2. Sub-millisecond latency (p99 < 1ms for in-memory reads).\n3. Scalability: Nodes can be added or removed with minimal cache churn via Consistent Hashing.",
    "real_world_analogy": "Imagine a stock exchange trading desk. Instead of walking downstairs into the basement records vault (Disk Database) every time a trader asks for the price of Apple stock, the trader keeps a dry-erase whiteboard right next to their computer screen (In-Memory Cache). Writing and reading on the whiteboard takes 1 second. If the whiteboard runs out of space, the trader erases the stock ticker that hasn't been looked at for the longest time (LRU Eviction).",
    "how_it_works": "<p>A distributed in-memory cache architecture coordinates single-threaded fast memory engines with consistent hashing clusters:</p><ol><li><strong>Single-Threaded Event-Loop Core:</strong> Like Redis, each cache node uses an asynchronous non-blocking event loop (epoll) and single-threaded execution. By avoiding thread context switching and lock contention (mutexes), a single core handles 100k+ operations/sec easily.</li><li><strong>Consistent Hash Ring Partitioning:</strong> Keys are partitioned across $N$ cache nodes using a Consistent Hash Ring with 256 Virtual Nodes per physical node. When a node is added or removed, only $1/N$ fraction of keys are remapped.</li><li><strong>In-Memory Data Structures:</strong> Combines a Hash Table (for $O(1)$ key lookups) with a Doubly-Linked List (for $O(1)$ LRU node eviction tracking).</li><li><strong>Replication & High Availability:</strong> Each master node streams an asynchronous replication log to 1-2 replica nodes. Redis Sentinel or Raft consensus monitors node health and promotes a replica if the master fails.</li><li><strong>Durability Modes:</strong> (a) <em>RDB (Redis Database Snapshots):</em> Periodic point-in-time binary snapshots to disk using <code>fork()</code> copy-on-write; (b) <em>AOF (Append-Only File):</em> Append-only log recording every write command with configurable <code>fsync</code> policies.</li></ol>",
    "conceptual_breakdown": [
        {"concept": "LRU Implementation via Doubly-Linked List + Hash Map", "explanation": "Hash map stores pointers to doubly-linked list nodes. On access, move node to head in O(1). When memory is full, evict node at tail in O(1)."},
        {"concept": "Copy-on-Write (COW) Forking for Snapshots", "explanation": "Redis calls Linux `fork()` to create a child process for background disk writes. The OS shares physical memory pages between parent and child; pages are duplicated only when the parent writes, minimizing memory bloat."},
        {"concept": "Consistent Hashing with Virtual Nodes", "explanation": "Virtual nodes balance key distribution across physical servers, preventing hotspots and ensuring smooth linear capacity scaling."},
        {"concept": "Active vs Passive TTL Expiration", "explanation": "Passive: Check TTL on key access; if expired, delete. Active: Randomly sample 20 keys with TTL 10 times per second; delete expired keys to prevent memory leaks for untouched keys."}
    ],
    "arch_diagram": {
        "nodes": [
            {"id": "clients", "label": "Client Application (Smart Driver)", "type": "client", "tier": "client"},
            {"id": "hash_ring", "label": "Consistent Hash Ring (Client-Side / Proxy)", "type": "service", "tier": "service"},
            {"id": "node1", "label": "Cache Master 1 (LRU Engine)", "type": "cache", "tier": "cache"},
            {"id": "node2", "label": "Cache Master 2 (LRU Engine)", "type": "cache", "tier": "cache"},
            {"id": "rep1", "label": "Replica 1 (Async WAL Replication)", "type": "cache", "tier": "cache"},
            {"id": "disk", "label": "Persistent Storage (RDB Snapshot / AOF)", "type": "database", "tier": "database"}
        ],
        "connections": [
            {"from": "clients", "to": "hash_ring", "label": "1. GET / SET Key", "type": "sync"},
            {"from": "hash_ring", "to": "node1", "label": "2. Route to Shard 1 (Hash Range)", "type": "sync"},
            {"from": "hash_ring", "to": "node2", "label": "2. Route to Shard 2 (Hash Range)", "type": "sync"},
            {"from": "node1", "to": "rep1", "label": "3. Async Stream Replication", "type": "async"},
            {"from": "node1", "to": "disk", "label": "4. Background COW Snapshot (fork)", "type": "async"}
        ]
    },
    "comparison_matrix": {
        "headers": ["Feature", "Redis", "Memcached", "Hazelcast / Apache Ignite"],
        "rows": [
            ["Thread Architecture", "Single-threaded event loop per instance", "Multi-threaded with internal locks", "Multi-threaded distributed grid"],
            ["Data Types Supported", "Strings, Hashes, Lists, Sets, Sorted Sets, Bitmaps", "Strings / Plain Blobs only", "Complex Java Objects, Distributed Maps"],
            ["Persistence to Disk", "Yes (RDB snapshots & AOF logs)", "No (Pure volatile RAM cache)", "Yes (Native persistence)"],
            ["Clustering / Replication", "Native Redis Cluster & Sentinel", "Client-side consistent hashing only", "Peer-to-peer automatic cluster mesh"]
        ]
    },
    "tradeoffs": [
        {"factor": "Single-Threaded Simplicity vs Multi-Core Utilization", "analysis": "Single-threaded design eliminates race conditions and lock overhead, maximizing single-core speed. To utilize a 64-core machine, deploy 64 independent Redis processes on different ports."},
        {"factor": "AOF fsync Everysec vs Disk I/O Bottlenecks", "analysis": "Setting `appendfsync always` guarantees zero data loss but reduces write throughput to mechanical disk speeds. Setting `appendfsync everysec` provides 99.99% durability with <1 second data loss risk at 100x higher throughput."}
    ],
    "failure_scenarios": [
        {"scenario": "Master Node Sudden Hardware Crash", "impact": "Master node goes offline; in-flight writes lost.", "mitigation": "Redis Sentinel / Raft coordinator detects missing heartbeat within 3 seconds, promotes Replica to Master, and updates client routing tables."},
        {"scenario": "Massive Memory Fragmentation During Heavy Writes", "impact": "Operating system reports 95% memory usage while Redis reports 50% data size (mem_fragmentation_ratio > 1.8).", "mitigation": "Enable active memory defragmentation (`activedefrag yes`) and configure jemalloc memory allocator tuning."}
    ],
    "common_mistakes": [
        {"mistake": "Running long-running blocking commands like KEYS * in production", "correction": "Because Redis is single-threaded, KEYS * scans the entire key space, freezing the event loop for seconds. Always use cursor-based incremental SCAN in production."},
        {"mistake": "Using Redis as a primary relational database without persistence tuning", "correction": "Redis is fundamentally an in-memory store. If used as primary storage, strictly configure AOF with appendfsync everysec and multi-AZ replication."}
    ],
    "interview_questions": [
        {"question": "How does Redis achieve 100k+ QPS on a single CPU core despite being single-threaded?",
        "answer": "Redis achieves high throughput through three architectural principles: (1) In-Memory Operations: All data structures reside in RAM, avoiding mechanical disk I/O latency; (2) I/O Multiplexing (epoll/kqueue): A non-blocking event-driven loop handles thousands of client connections concurrently without thread creation or context switching overhead; (3) Zero Lock Overhead: Because state execution is single-threaded, Redis requires zero internal mutexes, semaphores, or synchronization primitives, eliminating lock contention and CPU pipeline stalls."},
        {"question": "Explain how an in-memory LRU cache is constructed using O(1) time complexity for both Get and Set.",
        "answer": "An O(1) LRU cache combines a Hash Map and a Doubly-Linked List: (1) The Hash Map maps key to NodePointer, enabling O(1) lookups; (2) The Doubly-Linked List maintains access recency order (Head = Most Recently Used, Tail = Least Recently Used); (3) On GET(key): Locate node via Hash Map in O(1), unlink node from its current position in the list, and attach to Head (O(1) pointer swaps); (4) On SET(key, value): If key exists, update value and move to Head. If new key, insert node at Head and add to Hash Map. If cache exceeds capacity, remove the node at Tail from both the list and the Hash Map in O(1) time."}
    ]
}

t10 = {
    "id": "design-google-drive-file-sync",
    "title": "Problem 10 (Advanced): Design Google Drive / Dropbox Cloud File Synchronization",
    "definition": "A Cloud File Storage and Multi-Device Synchronization Platform (e.g., Google Drive, Dropbox, OneDrive) allows users to upload, download, and synchronize files across desktop and mobile devices seamlessly. The platform leverages chunk-based file deduplication, delta synchronization (syncing only modified byte diffs), block-level encryption, and conflict resolution.",
    "why_we_need_it": "### System Requirements\n**Functional Requirements:**\n1. Users can upload, download, and sync files (up to 50GB per file) across multiple devices.\n2. Automatic background delta-sync: modifying a 5-page section of a 500MB video/document re-uploads only the changed byte chunks.\n3. File version history and rollback (last 30 days).\n4. Offline editing with automated sync upon reconnection.\n\n**Non-Functional Requirements:**\n1. Bandwidth optimization: Never re-upload unchanged file chunks.\n2. Strong consistency: Files must never be corrupted; concurrent edits resolved gracefully.\n3. Extreme durability (11 9s durability for storage objects).\n\n### Scale Math\n- 500 million registered users, 100 million DAU.\n- 1 billion files synced per day.",
    "real_world_analogy": "Imagine a 1,000-page printed legal encyclopedia. If you fix a typo on page #47, you do not reprint and ship the entire 1,000-page book across the country. Instead, the publisher mails only page #47 (Chunking & Delta Sync). The recipient unbinds page #47 and snaps the new sheet into the 3-ring binder (Local Reconstruction).",
    "how_it_works": "<p>A cloud file synchronization engine operates through chunking, metadata indexing, and notification loops:</p><ol><li><strong>Content-Defined Chunking (Rabin Fingerprinting / FastCDC):</strong> Client desktop daemon splits large files into small 4MB chunks. Chunks are hashed using SHA-256 (e.g., <code>chunk_hash = '8a3b...'</code>).</li><li><strong>Global Chunk Deduplication:</strong> Before uploading, the client queries the Metadata Service: <em>'Do you already have chunk 8a3b...?'</em> If another user (or previous version) has already uploaded that chunk, the upload is skipped entirely, saving massive network bandwidth and cloud storage.</li><li><strong>Delta Synchronization:</strong> When a user edits a file, only the modified 4MB chunks are uploaded. The metadata service updates the <strong>File Recipe</strong> (a manifest listing ordered chunk hashes representing the file: <code>file_v2 = [chunk_A, chunk_B_new, chunk_C]</code>).</li><li><strong>Real-Time Sync Notification:</strong> A long-polling or WebSocket Notification Service pushes an invalidation event to all other connected devices belonging to the user.</li><li><strong>Conflict Resolution:</strong> If two offline devices edit the exact same file simultaneously, the server detects a version conflict and generates a conflicted copy.</li></ol>",
    "conceptual_breakdown": [
        {"concept": "Content-Defined Chunking (CDC)", "explanation": "Using sliding window hashing (Rabin Fingerprint) to split files at boundary markers rather than fixed offsets. If bytes are inserted at the beginning, only the first chunk shifts; all subsequent chunks retain identical hashes."},
        {"concept": "File Recipe / Manifest", "explanation": "A file is represented purely as an ordered array of SHA-256 chunk hashes stored in the metadata database: file_id -> [hash_1, hash_2, hash_3]."},
        {"concept": "Cold Storage Tiering", "explanation": "Chunks not accessed for 90 days are migrated from S3 Standard to S3 Glacier Flexible Archive to optimize storage expenditure."},
        {"concept": "Block-Level Zero-Knowledge Encryption", "explanation": "Chunks are encrypted with client AES keys before network transmission, preventing cloud providers from viewing private user data."}
    ],
    "arch_diagram": {
        "nodes": [
            {"id": "client", "label": "Client Desktop Daemon (Chunker)", "type": "client", "tier": "client"},
            {"id": "meta_api", "label": "Metadata API Service", "type": "service", "tier": "service"},
            {"id": "block_svc", "label": "Block / Chunk Upload Service", "type": "service", "tier": "service"},
            {"id": "s3_blocks", "label": "S3 Object Store (Deduplicated Chunks)", "type": "database", "tier": "database"},
            {"id": "meta_db", "label": "Metadata DB (File Recipes & Versions)", "type": "database", "tier": "database"},
            {"id": "notif_svc", "label": "Notification Sync Service (WebSockets)", "type": "service", "tier": "service"},
            {"id": "device2", "label": "User's Second Device (Laptop)", "type": "client", "tier": "client"}
        ],
        "connections": [
            {"from": "client", "to": "meta_api", "label": "1. Check Chunk Hashes (Dedup)", "type": "sync"},
            {"from": "client", "to": "block_svc", "label": "2. Upload New Modified Chunks (4MB)", "type": "sync"},
            {"from": "block_svc", "to": "s3_blocks", "label": "3. Store Raw Chunks", "type": "sync"},
            {"from": "meta_api", "to": "meta_db", "label": "4. Commit File Manifest Recipe", "type": "sync"},
            {"from": "meta_api", "to": "notif_svc", "label": "5. Publish FileUpdated Event", "type": "async"},
            {"from": "notif_svc", "to": "device2", "label": "6. Push Sync Notification", "type": "async"},
            {"from": "device2", "to": "s3_blocks", "label": "7. Download Only Changed Chunk", "type": "sync"}
        ]
    },
    "comparison_matrix": {
        "headers": ["Sync Strategy", "Fixed-Size Chunking (4MB)", "Content-Defined Chunking (CDC)", "Full File Upload"],
        "rows": [
            ["Byte Insertion Sensitivity", "High (1 byte shift changes all subsequent chunk hashes)", "Zero (shifts localized to modified chunk only)", "Uploads entire 100% file again"],
            ["Bandwidth Efficiency", "Moderate", "Highest", "Lowest"],
            ["CPU Overhead on Client", "Low (simple offset chunking)", "Moderate (sliding window hashing)", "Zero chunking overhead"],
            ["Deduplication Ratio", "Good", "Industry Best (~60-70% savings)", "Zero intra-file deduplication"]
        ]
    },
    "tradeoffs": [
        {"factor": "Chunk Size (1MB vs 8MB)", "analysis": "Small chunks (1MB) maximize deduplication and minimize delta upload size, but multiply metadata overhead (more chunk hashes to store). 4MB is the industry standard balance."},
        {"factor": "Client vs Server Chunking", "analysis": "Chunking on the client minimizes upload bandwidth because unchanged chunks are never sent over the wire. However, it requires a native client desktop daemon application."}
    ],
    "failure_scenarios": [
        {"scenario": "Chunk Upload Interrupted by Laptop Sleep / WiFi Drop", "impact": "Upload of 10-chunk file halts after 6 chunks.", "mitigation": "Client maintains local SQLite staging state. Upon reconnect, queries metadata API for already uploaded chunk hashes and resumes from chunk #7."},
        {"scenario": "Simultaneous Offline Edits on Two Devices", "impact": "Both devices edit line 10 while disconnected from internet.", "mitigation": "First device to sync commits as Version 2. Second device sync detects parent version mismatch and creates a 'Conflicted Copy' file to preserve both edits without data loss."}
    ],
    "common_mistakes": [
        {"mistake": "Uploading full 500MB files on minor edits", "correction": "Always implement chunking and delta-synchronization to upload strictly modified byte blocks."},
        {"mistake": "Using fixed-size chunking without sliding window boundary markers", "correction": "Fixed-size chunking suffers from the boundary shift problem: inserting 1 byte at index 0 invalidates all downstream chunk hashes. Use Content-Defined Chunking (Rabin Fingerprint)."}
    ],
    "interview_questions": [
        {"question": "How does Content-Defined Chunking (CDC) solve the 'Boundary Shift' problem of fixed-size chunking?",
        "answer": "In fixed-size chunking (rigid 4MB blocks), inserting a single byte at the beginning of a 100MB file shifts every byte by 1 position. Consequently, all 25 chunk boundaries shift, generating 25 completely new SHA-256 hashes, forcing a re-upload of the entire 100MB file. In Content-Defined Chunking (CDC), chunk boundaries are determined by content patterns using a rolling hash (Rabin Fingerprinting) over a sliding window. When a byte is inserted, only the immediate chunk containing the edit changes its boundary; all downstream chunks encounter the exact same content patterns and retain identical SHA-256 hashes, ensuring only 1 chunk is re-uploaded."},
        {"question": "How does Google Drive handle file versioning and file recovery?",
        "answer": "Google Drive uses an immutable chunk store paired with a versioned metadata ledger: (1) Storage chunks in S3/Blob are immutable and never overwritten; (2) The Metadata Database maintains a file_versions table containing (file_id, version_num, timestamp, chunk_manifest_array); (3) When a file is updated, a new version record is inserted with the updated chunk recipe; (4) Rolling back to Version 3 simply updates the active file pointer to point to Version 3's chunk manifest, restoring the file instantaneously with zero data copying."}
    ]
}

t11 = {
    "id": "design-google-docs-collaborative-editor",
    "title": "Problem 11 (Advanced): Design Google Docs Real-time Collaborative Editor (OT / CRDT)",
    "definition": "A Real-Time Collaborative Document Editor (e.g., Google Docs, Notion, Figma) enables multiple geographically distributed users to edit the same rich-text document simultaneously with sub-50ms latency. The system guarantees convergence (all clients converge to the exact same document state), preserves user editing intention, and resolves character conflicts using Operational Transformation (OT) or Conflict-Free Replicated Data Types (CRDTs).",
    "why_we_need_it": "### System Requirements\n**Functional Requirements:**\n1. Real-time multi-user concurrent character editing.\n2. Collaborative user presence (displaying active cursor positions and selections).\n3. Offline editing mode with automatic reconciliation upon reconnecting.\n4. Document change history and snapshot recovery.\n\n**Non-Functional Requirements:**\n1. Real-time latency: Local user keystrokes render instantly (0ms locally); remote updates propagate in <100ms.\n2. Absolute Convergence: If all users stop editing, all clients must display 100% identical document text.\n3. Intention Preservation: If Alice inserts 'A' at index 0 and Bob inserts 'B' at index 0 concurrently, both characters must be preserved without character deletion.",
    "real_world_analogy": "Imagine two musicians improvising a piano duet while separated by soundproof glass. If both musicians simultaneously play a note on beat 1, they don't erase each other's music. Instead, an automated musical conductor (Operational Transformation Server) adjusts the second musician's sheet music by shifting their note half a beat later, ensuring both notes harmonize together seamlessly.",
    "how_it_works": "<p>Real-time collaborative editing relies on mathematical transformation algorithms and WebSocket document servers:</p><ol><li><strong>Operational Transformation (OT) Core:</strong> Operations are modeled as atomic mutations: <code>Insert(pos, char)</code> and <code>Delete(pos)</code>. When client operations clash over concurrent network flights, the transformation function adjusts character indices so that applying OpA then OpB-prime yields identical state to applying OpB then OpA-prime.</li><li><strong>Centralized OT Authority (Google Docs Model):</strong> A dedicated <strong>Doc Session Server</strong> acts as the single source of truth for each active document. The server maintains a strictly monotonically increasing document revision number.</li><li><strong>Client Optimistic Execution:</strong> When a user types a letter, the local UI updates immediately (0ms local perceived latency). The client queues the operation and transmits to the server over WebSockets.</li><li><strong>Server Transformation & Broadcast:</strong> The server receives operations sequentially, transforms concurrent operations against committed revisions, and broadcasts the transformed operation to all connected collaborators.</li><li><strong>CRDT Alternative (Figma / Automerge Model):</strong> Uses Conflict-Free Replicated Data Types where each character is assigned a globally unique fractional identifier. CRDT operations commute mathematically without requiring a centralized coordinator server.</li></ol>",
    "conceptual_breakdown": [
        {"concept": "Operational Transformation (OT) vs CRDT", "explanation": "OT requires a centralized server to order operations and transform positional indices. CRDTs assign immutable unique fractional IDs to characters, enabling decentralized peer-to-peer convergence at the expense of higher memory metadata."},
        {"concept": "Intention Preservation", "explanation": "Ensuring that the semantic meaning of an operation (e.g., inserting a word inside quotation marks) is maintained even after other concurrent operations shift surrounding characters."},
        {"concept": "Ephemeral Cursor & Presence Tracking", "explanation": "Live cursor coordinates (user_id, cursor_pos, color) are broadcast ephemerally over WebSockets without persisting to disk, keeping document storage clean."},
        {"concept": "Periodic Document Compaction (Snapshots)", "explanation": "Replaying 500,000 fine-grained character keystroke operations on document open is slow. The server periodically compacts historical operations into a base text snapshot every 100 revisions."}
    ],
    "arch_diagram": {
        "nodes": [
            {"id": "alice", "label": "Alice Client (Typing 'Hello')", "type": "client", "tier": "client"},
            {"id": "bob", "label": "Bob Client (Typing 'World')", "type": "client", "tier": "client"},
            {"id": "gw", "label": "Collaboration Gateway (WebSockets)", "type": "service", "tier": "service"},
            {"id": "doc_server", "label": "Doc Session Master (OT Engine)", "type": "service", "tier": "service"},
            {"id": "redis_sess", "label": "Active Session Registry (Redis)", "type": "cache", "tier": "cache"},
            {"id": "db_doc", "label": "Document Store (Postgres / Spanner)", "type": "database", "tier": "database"}
        ],
        "connections": [
            {"from": "alice", "to": "gw", "label": "1. Send Op(Rev 5, Ins(0, 'H'))", "type": "sync"},
            {"from": "bob", "to": "gw", "label": "1. Send Op(Rev 5, Ins(0, 'W'))", "type": "sync"},
            {"from": "gw", "to": "doc_server", "label": "2. Route to Active Document Actor", "type": "sync"},
            {"from": "doc_server", "to": "doc_server", "label": "3. Transform & Order: T(OpA, OpB)", "type": "sync"},
            {"from": "doc_server", "to": "gw", "label": "4. Broadcast Transformed Rev 6 & 7", "type": "async"},
            {"from": "gw", "to": "alice", "label": "5. Apply Remote Op", "type": "async"},
            {"from": "gw", "to": "bob", "label": "5. Apply Remote Op", "type": "async"},
            {"from": "doc_server", "to": "db_doc", "label": "6. Periodic Snapshot & Operation Log", "type": "async"}
        ]
    },
    "comparison_matrix": {
        "headers": ["Algorithm / Architecture", "Operational Transformation (OT)", "Conflict-Free Replicated Data Types (CRDT)", "Pessimistic Locking (Co-author Lock)"],
        "rows": [
            ["Coordination Model", "Centralized server required as authority", "Decentralized / Peer-to-Peer / Leaderless", "Centralized lock manager"],
            ["Memory Overhead", "Lowest (standard string + small op log)", "High (each character carries UUID & fractional index)", "Zero"],
            ["Concurrent Editing", "Full real-time character-by-character", "Full real-time character-by-character", "None (1 user locks paragraph/doc)"],
            ["Offline Reconciliation", "Complex transformation history replay", "Natural algebraic merge on reconnect", "Fails; lock expires"],
            ["Real-World Adopters", "Google Docs, Etherpad, Microsoft Office", "Figma, Apple Notes, Automerge, Yjs", "Legacy SharePoint, CMS editors"]
        ]
    },
    "tradeoffs": [
        {"factor": "OT Centralization vs CRDT Memory Overhead", "analysis": "OT requires maintaining an authoritative central session server per open document, but preserves lean string memory representations. CRDTs allow peer-to-peer editing without central servers, but increase document memory size by 5x-10x due to character metadata."},
        {"factor": "Keystroke Streaming vs Debounced Batching", "analysis": "Sending a WebSocket message per keystroke provides hyper-fluid live presence, but generates thousands of network messages per minute. Batching keystrokes every 50ms smooths network traffic with zero human-perceptible lag."}
    ],
    "failure_scenarios": [
        {"scenario": "Doc Session Server Crashes Mid-Editing Session", "impact": "WebSockets drop for 50 users editing a company doc.", "mitigation": "Clients reconnect to another Doc Server. The new server loads the last snapshot and uncommitted operations from Redis/Postgres and resumes OT sequencing."},
        {"scenario": "Client Disconnects for 2 Hours (Offline Plane Flight)", "impact": "Client accumulates 500 local offline operations while remote collaborators advance 1,000 revisions.", "mitigation": "Upon reconnecting, client sends its local operations tagged with parent revision; server performs multi-version transformation matrix to reconcile changes safely."}
    ],
    "common_mistakes": [
        {"mistake": "Relying on simple Last-Write-Wins (LWW) timestamps for collaborative text editing", "correction": "LWW will overwrite and delete concurrent keystrokes typed by other users at the same index. Collaborative text requires OT or CRDT algorithms."},
        {"mistake": "Replaying full historical operation logs from scratch on every document load", "correction": "A document with 1 million historical keystrokes takes seconds to parse. Always maintain periodic compacted snapshots (e.g., every 100 revisions) and replay only recent operations."}
    ],
    "interview_questions": [
        {"question": "How does Operational Transformation (OT) handle two users inserting characters at the exact same index simultaneously?",
        "answer": "Suppose document is empty at Revision 0. Alice types 'A' at index 0, and Bob types 'B' at index 0. (1) The central server receives Alice's Op first, commits it at Rev 1 (doc becomes 'A'), and broadcasts to Bob; (2) The server then receives Bob's Op (which was created against Rev 0); (3) The server applies transformation: because Alice already inserted 1 character at index 0, Bob's insertion position must shift by +1 (Ins(1, 'B')); (4) The server commits Bob's transformed Op as Rev 2 (doc becomes 'AB') and broadcasts to Alice; (5) Both clients converge to 'AB' without character loss."},
        {"question": "What is the difference between OT and CRDT in terms of network topology and scalability?",
        "answer": "OT requires a Centralized Server Authority to impose a canonical total ordering of operations and perform contextual transformations. It cannot operate in a pure peer-to-peer network because transformations depend on knowing the exact revision history state. In contrast, CRDTs (Conflict-Free Replicated Data Types) are mathematically designed with commutative and associative merge operations. Operations commute (A * B = B * A), meaning operations can arrive out-of-order across any network topology (peer-to-peer, mesh, decentralized) and all replicas will mathematically converge to the exact same state without transformation or central coordinators."}
    ]
}

t12 = {
    "id": "design-distributed-web-crawler",
    "title": "Problem 12 (Advanced): Design a Distributed Web Crawler & Indexer at Scale",
    "definition": "A Distributed Web Crawler (e.g., Googlebot, Bingbot, Common Crawl) systematically and autonomously discovers, fetches, parses, and indexes billions of web pages across the public internet. The system manages crawl frontiers, enforces domain politeness (robots.txt and rate limits), deduplicates identical content, and handles distributed DNS resolution at planetary scale.",
    "why_we_need_it": "### System Requirements\n**Functional Requirements:**\n1. Crawl billions of web pages starting from seed URLs.\n2. Extract text content, metadata, and outgoing hyperlinks to discover new pages.\n3. Content deduplication (avoid indexing duplicate or mirrored pages).\n4. Respect `robots.txt` protocol and maintain host politeness.\n\n**Non-Functional Requirements:**\n1. High throughput: Crawl 1 billion pages per month = ~400 pages/second (Peak: 1,500 pages/sec).\n2. Scalability: Horizontally scalable across hundreds of distributed crawler worker nodes.\n3. Robustness against crawler traps (infinite loops, dynamically generated calendar pages).\n4. Freshness: Periodically re-crawl high-value dynamic pages (news) while crawling static pages less frequently.",
    "real_world_analogy": "Imagine a worldwide fleet of millions of autonomous robotic librarians. You hand the librarians 100 famous starting books (Seed URLs). Each librarian reads a book, writes a catalog index of its contents, highlights every citation referencing other books (Hyperlinks), and drops those new book titles into a central sorting conveyer belt (Crawl Frontier). To avoid harassing authors, each librarian visits a specific author's house at most once every 10 seconds (Politeness).",
    "how_it_works": "<p>A production web crawler operates via a disciplined crawl loop and dual-queue frontier architecture:</p><ol><li><strong>Seed URLs & URL Frontier:</strong> Seed URLs are placed in the URL Frontier. The Frontier manages which URL to crawl next using two sub-systems: (a) <em>Priority Queues:</em> Orders URLs by PageRank and domain authority; (b) <em>Politeness Queues:</em> Binds one FIFO queue per distinct domain name with a delay timer to enforce politeness (e.g., 1 request per 2 seconds per domain).</li><li><strong>DNS Resolver Cache:</strong> DNS lookups are major bottlenecks. Crawlers maintain an in-memory distributed DNS cache (Redis/Unbound) to resolve domain IPs in sub-milliseconds.</li><li><strong>HTML Fetcher & HTTP Engine:</strong> Lightweight non-blocking HTTP workers download raw HTML, enforcing strict timeouts (3 seconds) and size caps (10MB max).</li><li><strong>Robots.txt & Link Extractor:</strong> Evaluates domain <code>robots.txt</code> rules. Parses HTML DOM to extract all outgoing hyperlinks, normalizes relative URLs to canonical absolute URLs.</li><li><strong>Content Deduplication (SimHash / MinHash):</strong> Computes a 64-bit SimHash of text content. Compares against existing hashes via Hamming Distance: if distance &lt;= 3, content is near-duplicate and discarded.</li><li><strong>URL Filter & Bloom Filter:</strong> Checks an in-memory Bloom Filter: if the extracted URL has already been visited, discard; if new, push to URL Frontier.</li></ol>",
    "conceptual_breakdown": [
        {"concept": "URL Frontier Politeness Architecture (Mercator Model)", "explanation": "Separates queues into Priority Queues (F1: importance/freshness) and Politeness Queues (F2: 1 queue per hostname with delay timer managed by a heap), preventing DoS attacks on external sites."},
        {"concept": "SimHash for Near-Duplicate Detection", "explanation": "A locality-sensitive hash algorithm where similar text documents produce hashes with small Hamming distances (differing by only a few bits), allowing rapid duplicate identification."},
        {"concept": "Bloom Filters for URL Seen Check", "explanation": "A space-efficient probabilistic data structure used to test whether 5 billion URLs have been seen. Uses ~10 bits per URL with a 1% false positive rate, requiring only ~6GB of RAM."},
        {"concept": "Crawler Traps Mitigation", "explanation": "Infinite URL generation loops (e.g., /calendar?day=1, /calendar?day=2... or symlink recursion). Mitigated by capping URL path depth (max 10 slashes) and limiting pages per domain."}
    ],
    "arch_diagram": {
        "nodes": [
            {"id": "frontier", "label": "URL Frontier (Priority + Politeness Queues)", "type": "queue", "tier": "queue"},
            {"id": "dns_cache", "label": "Distributed DNS Cache", "type": "cache", "tier": "cache"},
            {"id": "fetchers", "label": "HTML Fetcher Workers (epoll / Async)", "type": "service", "tier": "service"},
            {"id": "parser", "label": "HTML Parser & Link Extractor", "type": "service", "tier": "service"},
            {"id": "simhash", "label": "SimHash Dedup Engine", "type": "service", "tier": "service"},
            {"id": "bloom", "label": "URL Seen Filter (Bloom Filter / Redis)", "type": "cache", "tier": "cache"},
            {"id": "storage", "label": "Raw Web Page Store (Bigtable / S3)", "type": "database", "tier": "database"}
        ],
        "connections": [
            {"from": "frontier", "to": "fetchers", "label": "1. Dequeue Polite URL", "type": "async"},
            {"from": "fetchers", "to": "dns_cache", "label": "2. Resolve Host IP (<1ms)", "type": "sync"},
            {"from": "fetchers", "to": "parser", "label": "3. Stream HTML Content", "type": "sync"},
            {"from": "parser", "to": "simhash", "label": "4. Check Content Fingerprint", "type": "sync"},
            {"from": "simhash", "to": "storage", "label": "5. Save Unique Web Page", "type": "sync"},
            {"from": "parser", "to": "bloom", "label": "6. Check Discovered Links", "type": "sync"},
            {"from": "bloom", "to": "frontier", "label": "7. Enqueue New Unseen URLs", "type": "async"}
        ]
    },
    "comparison_matrix": {
        "headers": ["Deduplication Technique", "Mechanism", "Memory Usage", "Accuracy", "Best Use Case"],
        "rows": [
            ["Exact Hashing (MD5 / SHA256)", "Cryptographic hash of raw HTML bytes", "16-32 bytes per document", "100% exact match only", "Detecting identical byte-for-byte files"],
            ["SimHash (Locality-Sensitive)", "Weighted feature vector hash", "8 bytes (64-bit integer)", "Detects near-duplicates (Hamming distance)", "Web pages with different ads/timestamps but identical text"],
            ["MinHash / Jaccard", "Set intersection approximation", "Variable (100-200 integers)", "High for text similarity", "Clustering large news articles and academic papers"]
        ]
    },
    "tradeoffs": [
        {"factor": "Crawl Breadth vs Crawl Depth (BFS vs DFS)", "analysis": "Pure BFS explores wide domains across the web; pure DFS goes deep into a single website. Crawlers use a hybrid Priority BFS to index high-value root pages across millions of sites first."},
        {"factor": "Headless Browser (Puppeteer) vs Raw HTTP Fetching", "analysis": "Fetching raw HTML is fast (10ms) and lightweight. Running headless Chromium to execute client-side JavaScript (React/Vue sites) takes 2 seconds and 500MB RAM per page. Crawlers use raw HTTP for 90% of pages and spawn headless browsers only for high-value JS-rendered domains."}
    ],
    "failure_scenarios": [
        {"scenario": "Spider Trap Generates Infinite Calendar Pages", "impact": "Crawler gets stuck crawling /events/2026/10/03/day/1... consuming all frontier queue bandwidth.", "mitigation": "Enforce maximum URL path depth limits, query parameter length caps, and restrict maximum pages crawled per domain to 50,000."},
        {"scenario": "DNS Server Overload Spikes Fetch Latency", "impact": "Standard DNS lookups take 200ms, stalling 1,000 fetcher threads.", "mitigation": "Maintain a warm, local in-memory DNS cache with pre-resolved IP addresses and asynchronous background DNS refreshers."}
    ],
    "common_mistakes": [
        {"mistake": "Failing to respect robots.txt and crawling sites with 100 concurrent threads", "correction": "Triggers IP bans, legal liability, and crashes target servers. Always parse robots.txt and throttle to max 1-2 requests per second per host."},
        {"mistake": "Using a relational database table to check if 10 billion URLs have been seen", "correction": "SQL SELECT WHERE url = ? on 10B rows destroys disk I/O. Use an in-memory Bloom Filter or partitioned Redis Bitmaps."}
    ],
    "interview_questions": [
        {"question": "How does the URL Frontier enforce both Page Priority and Host Politeness simultaneously?",
        "answer": "The URL Frontier uses the Mercator Two-Tier Queue Architecture: (1) Priority Queue Tier (F1): Discovered URLs are classified into K priority queues (e.g., based on PageRank or domain quality). High-priority queues are dequeued more frequently; (2) Politeness Queue Tier (F2): Contains M FIFO queues, where each queue contains URLs strictly for a single specific host. A central Queue Manager maintains a min-heap of (queue_id, next_available_timestamp). When a worker requests a URL, the manager pops the queue whose cooldown timer has elapsed, fetches the URL, sets next_available_timestamp = NOW() + 2s, and re-inserts the queue into the heap. This guarantees host politeness while prioritizing important pages."},
        {"question": "How does SimHash detect near-duplicate web pages differing only in dynamic timestamps and sidebar ads?",
        "answer": "SimHash works in four steps: (1) Tokenize text into words, stripping HTML tags; (2) Hash each word into a 64-bit binary hash; (3) Initialize a 64-element integer vector V = [0, 0, ... 0]. For each word hash, if bit i is 1, add word weight +w to V[i]; if bit i is 0, subtract -w from V[i]; (4) Collapse vector V: if V[i] > 0, set output bit i = 1, else 0. The resulting 64-bit SimHash possesses a unique mathematical property: similar documents produce hashes that differ by only a few bit flips. By checking if the Hamming distance between two SimHashes is <= 3, the system identifies near-duplicate pages in O(1) bitwise XOR operations."}
    ]
}

t13 = {
    "id": "design-distributed-job-scheduler",
    "title": "Problem 13 (Advanced): Design a Distributed Task / Job Scheduler at Scale",
    "definition": "A Distributed Task and Job Scheduling Platform (e.g., Apache Airflow, Temporal, AWS Step Functions, Quartz) coordinates the execution of millions of recurring (cron-based), delayed, and dependency-chained (DAG) background jobs across a distributed cluster of worker nodes, guaranteeing fault tolerance, priority scheduling, and exactly-once / at-least-once execution semantics.",
    "why_we_need_it": "### System Requirements\n**Functional Requirements:**\n1. Schedule one-time delayed jobs and recurring cron jobs across millions of tasks.\n2. Support Directed Acyclic Graph (DAG) task dependencies (Job B runs only after Job A succeeds).\n3. Configurable task execution timeouts, retries with exponential backoff, and dead-letter queues.\n4. Real-time task execution status tracking and execution logs.\n\n**Non-Functional Requirements:**\n1. High scale: Handle 100 million scheduled tasks/day with millisecond execution precision.\n2. High availability: Zero single point of failure (SPOF); scheduler master failover in <5 seconds.\n3. Fault tolerance: If a worker node crashes mid-job, the task must be automatically re-assigned to a healthy worker.",
    "real_world_analogy": "Imagine an automated air traffic control tower. The tower manages thousands of flight departures: (1) Scheduled departures (Cron flights at 8:00 AM); (2) Contingency routes (If de-icing finishes, clear plane for runway 4L); (3) Runway prioritization (Medical emergency flight lands before standard passenger flight). If the primary flight controller collapses, the backup controller immediately reads the master radar screen and resumes flight dispatching without dropping any plane.",
    "how_it_works": "<p>A high-scale distributed job scheduler operates via coordination, time-indexed storage, and worker execution fleets:</p><ol><li><strong>Job Definition & DAG Ingestion:</strong> Users submit job descriptors defining execution interval, payload, dependencies (DAG parent/child tasks), and priority.</li><li><strong>Time-Indexed Fast Staging (Redis ZSET / Time Wheels):</strong> Scheduled jobs for the current hour are staged into distributed Redis Sorted Sets (ZSET) where <code>Score = Target_Unix_Timestamp</code> and <code>Member = Task_ID</code>.</li><li><strong>Leader-Elected Scheduler Dispatcher:</strong> A cluster of scheduler nodes uses Raft/etcd leader election. The active Leader polls Redis every 500ms using atomic Lua scripts (<code>ZRANGEBYSCORE ... ZREM</code>) to fetch ready jobs and pushes them into priority queues (Kafka / RabbitMQ).</li><li><strong>DAG Dependency Engine:</strong> For multi-step workflows, when Job A finishes, the worker publishes <code>JobCompleted(Job_A)</code>. The DAG Evaluator evaluates parent dependencies: if all parents of Job B are complete, it transitions Job B from <code>BLOCKED</code> to <code>READY</code> and enqueues it.</li><li><strong>Worker Fleet & Heartbeat Leases:</strong> Workers claim tasks from queues. While processing, the worker maintains a heartbeating lease in the database (e.g., <code>UPDATE task SET lease_expires = NOW() + 30s</code>). If the worker crashes, the lease expires, and the supervisor re-queues the job.</li></ol>",
    "conceptual_breakdown": [
        {"concept": "Two-Tier Storage Architecture", "explanation": "Durable long-term jobs (months in advance) sit in relational databases (PostgreSQL/DynamoDB). Jobs scheduled for the immediate next 15 minutes are prefetched into low-latency in-memory Redis ZSETs."},
        {"concept": "DAG Topological Sort", "explanation": "Validates that multi-task workflows have zero cyclic dependencies and determines the valid execution sequence across parallel worker threads."},
        {"concept": "Worker Heartbeat & Task Leases", "explanation": "Workers periodically renew a short lease. If a worker dies or gets stuck, the watchdog scheduler detects the expired lease and triggers automatic re-assignment."},
        {"concept": "Fencing Tokens for Task Execution", "explanation": "Monotonic tokens issued with each lease prevent zombie workers (stalled by GC pauses) from corrupting state when they wake up."}
    ],
    "arch_diagram": {
        "nodes": [
            {"id": "api", "label": "Job Submission API", "type": "service", "tier": "service"},
            {"id": "db_jobs", "label": "Durable Job Metadata DB", "type": "database", "tier": "database"},
            {"id": "zset", "label": "Time Wheel / Redis ZSET (Score = Timestamp)", "type": "cache", "tier": "cache"},
            {"id": "scheduler", "label": "Scheduler Leader (etcd Elected)", "type": "service", "tier": "service"},
            {"id": "dag_engine", "label": "DAG Dependency Evaluator", "type": "service", "tier": "service"},
            {"id": "queue", "label": "Priority Task Queues (Kafka / SQS)", "type": "queue", "tier": "queue"},
            {"id": "workers", "label": "Distributed Worker Fleet (Auto-scaled)", "type": "service", "tier": "service"}
        ],
        "connections": [
            {"from": "api", "to": "db_jobs", "label": "1. Save Job Definition", "type": "sync"},
            {"from": "db_jobs", "to": "zset", "label": "2. Prefetch Next 15m Jobs", "type": "async"},
            {"from": "scheduler", "to": "zset", "label": "3. Atomic ZRANGEBYSCORE + ZREM", "type": "sync"},
            {"from": "scheduler", "to": "dag_engine", "label": "4. Check Parent Task Status", "type": "sync"},
            {"from": "dag_engine", "to": "queue", "label": "5. Push Ready Tasks to Priority Queue", "type": "async"},
            {"from": "queue", "to": "workers", "label": "6. Claim Task & Send Heartbeat Lease", "type": "async"},
            {"from": "workers", "to": "db_jobs", "label": "7. Mark Task Complete", "type": "sync"}
        ]
    },
    "comparison_matrix": {
        "headers": ["Scheduling Engine", "Temporal / Cadence", "Apache Airflow", "Quartz Scheduler (Java)", "AWS Step Functions"],
        "rows": [
            ["Workflow Model", "Code-as-Workflows (Durable Execution)", "Python DAG configuration files", "Java JobDetail + Trigger annotations", "JSON State Machine (ASL)"],
            ["Execution Precision", "Sub-second millisecond timers", "Batch oriented (Minutes)", "Milliseconds", "Sub-second"],
            ["State Persistence", "Event Sourcing / Append-only history", "Relational Database (PostgreSQL)", "JDBC Relational Tables", "Managed Serverless state store"],
            ["Primary Use Case", "Microservice sagas, financial workflows", "Data engineering & ETL pipelines", "Enterprise backend cron jobs", "Serverless AWS Lambda orchestration"]
        ]
    },
    "tradeoffs": [
        {"factor": "Polling Interval vs Database CPU Load", "analysis": "Polling the database every 100ms provides high precision but exhausts database IOPS. Using in-memory Redis ZSETs for the active window decouples scheduling precision from database load."},
        {"factor": "At-Least-Once vs Exactly-Once Execution", "analysis": "In distributed environments, network drops during worker completion acks will cause tasks to be retried. The scheduler guarantees At-Least-Once execution; task business logic must enforce idempotency via idempotency keys."}
    ],
    "failure_scenarios": [
        {"scenario": "Scheduler Leader Node Dies Abruptly", "impact": "Task dispatching pauses for current second.", "mitigation": "etcd leader election detects missing heartbeat within 2 seconds; a standby scheduler node is promoted to leader and resumes dispatching from Redis ZSET."},
        {"scenario": "Worker Hangs on Infinite HTTP Socket Timeout", "impact": "Worker thread blocked indefinitely; job remains unfinished.", "mitigation": "Enforce strict task-level timeouts (`timeout_seconds = 300`) and verify worker heartbeat leases. When the lease expires, the scheduler terminates the worker container and re-queues the task."}
    ],
    "common_mistakes": [
        {"mistake": "Running polling SQL queries (`WHERE run_at <= NOW()`) directly on a 10M row table without partial indexing", "correction": "Causes full table locks and query degradation. Use a partial B-tree index `WHERE status = 'PENDING'` or stage ready tasks into Redis ZSETs."},
        {"mistake": "Writing DAG task handlers that are not idempotent", "correction": "Worker crashes or network timeouts will cause task retries. Always make task handlers idempotent using business transaction deduplication keys."}
    ],
    "interview_questions": [
        {"question": "How do you architect a Distributed Job Scheduler to support both recurring cron schedules and dynamic DAG dependencies?",
        "answer": "Implement a three-component architecture: (1) Time Trigger Component (Cron & Delayed Jobs): Uses a prefetch daemon that reads upcoming jobs from PostgreSQL into sharded Redis Sorted Sets (ZSETs). Scheduler dispatchers use Lua scripts to pop ready jobs and push them to execution queues; (2) DAG State Machine Component: For multi-step workflows, each job definition is stored as an adjacency list DAG. When a task completes, the worker emits TaskCompleted(task_id). The DAG engine decrements the in-degree count of all dependent child tasks. When a child task's in-degree reaches 0 (all parents satisfied), it is immediately pushed to the ready queue; (3) Worker Pool with Heartbeating Leases: Workers process tasks, renew short leases every 10s, and update state upon completion."},
        {"question": "How do you prevent duplicate job execution when multiple scheduler nodes run concurrently?",
        "answer": "Use one of two proven patterns: (1) Leader Election: Use a distributed consensus store (etcd / ZooKeeper) to elect a single Active Scheduler Leader. Only the leader queries the timing queues and pushes tasks to message brokers; (2) Atomic Optimistic Claiming: If multiple schedulers run concurrently without a leader, tasks are claimed using atomic Redis Lua scripts (ZREM) or database queries with row-level locks and SKIP LOCKED: SELECT * FROM tasks WHERE run_at <= NOW() AND status = 'PENDING' LIMIT 100 FOR UPDATE SKIP LOCKED. This guarantees each task is claimed by exactly one scheduler node without lock contention."}
    ]
}

with open('scratch/t9_t13.json', 'w', encoding='utf-8') as f:
    json.dump([t9, t10, t11, t12, t13], f, indent=2, ensure_ascii=False)
print("Topics 9-13 written successfully!")
