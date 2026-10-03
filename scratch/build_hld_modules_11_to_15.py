import json
import os

CONTENT_DIR = "content/hld"
os.makedirs(CONTENT_DIR, exist_ok=True)

# -------------------------------------------------------------
# MODULE 11: NoSQL Databases: Key-Value, Document, Wide-Column, Graph
# -------------------------------------------------------------
mod_11 = {
  "module_id": "11",
  "module_title": "NoSQL Databases: Key-Value, Document, Wide-Column, Graph",
  "description": "Master NoSQL architectures: Key-Value (Redis/DynamoDB), Document (MongoDB), Wide-Column (Cassandra/ScyllaDB), and Graph (Neo4j) database engines.",
  "topics": [
    {
      "id": "nosql-categories-and-internals",
      "title": "The 4 NoSQL Engines: Key-Value, Document, Wide-Column & Graph",
      "definition": "NoSQL encompasses four distinct non-relational database paradigms designed for horizontal scalability, unstructured schemas, and specific data access access patterns: Key-Value, Document, Wide-Column, and Graph.",
      "why_we_need_it": "Relational databases cannot scale writes horizontally across hundreds of commodity nodes without complex sharding or sacrificing multi-table ACID transactions. NoSQL specializes data structures for linear scalability.",
      "real_world_analogy": "Key-Value is a coat check ticket (1 key -> 1 coat). Document store is a physical medical folder full of diverse paper reports. Wide-Column is an enormous spreadsheet where each row can have completely different columns. Graph DB is an airport route map showing flight paths between cities.",
      "how_it_works": "<p>1. <strong>Key-Value (Redis, DynamoDB):</strong> Simple hash table lookups `O(1)` by primary key.<br>2. <strong>Document (MongoDB, Couchbase):</strong> Stores self-contained JSON/BSON documents with nested sub-objects and dynamic schemas.<br>3. <strong>Wide-Column (Cassandra, ScyllaDB, HBase):</strong> Two-dimensional key-value store indexed by `(Partition Key, Clustering Key)` with sparse columns.<br>4. <strong>Graph (Neo4j, AWS Neptune):</strong> Stores Nodes, Edges (Relationships), and Properties, performing index-free adjacency graph traversals in `O(1)` per hop.</p>",
      "conceptual_breakdown": [
        "<strong>Key-Value:</strong> Ultra-fast, minimal query flexibility (get/put/delete by key).",
        "<strong>Document:</strong> High developer velocity, rich ad-hoc query capabilities on JSON attributes.",
        "<strong>Wide-Column:</strong> Massive write throughput, time-series telemetry, query-driven table modeling.",
        "<strong>Graph:</strong> Complex multi-hop relational traversals (social networks, fraud detection, recommendation engines)."
      ],
      "comparison_matrix": {
        "title": "The 4 NoSQL Database Families",
        "columns": ["Paradigm", "Primary Engine", "Data Structure", "Query Flexibility", "Best Fit Use Case"],
        "rows": [
          ["Key-Value", "Redis / DynamoDB", "Hash Map / Key-Blob", "Low (Key lookup only)", "User sessions, caching, shopping carts"],
          ["Document", "MongoDB / Couchbase", "JSON / BSON documents", "High (Secondary indexes on nested fields)", "Content management, user profiles, e-commerce catalogs"],
          ["Wide-Column", "Cassandra / ScyllaDB", "LSM Tree + Sparse Rows", "Moderate (Query restricted to partition key)", "IoT time-series metrics, message history, financial audits"],
          ["Graph", "Neo4j / Amazon Neptune", "Nodes & Edges Pointer Graph", "Very High (Graph Cypher queries)", "Social networks, fraud rings, knowledge graphs"]
        ]
      },
      "failure_scenarios": "<strong>Graph DB Traversal Explosions:</strong> Querying 6-degrees of separation on high-degree 'celebrity' nodes (millions of edges) causes exponential graph traversal blow-up and out-of-memory crashes. <em>Mitigation:</em> Restrict max traversal depth (`LIMIT 3`) and prune dense nodes.",
      "common_mistakes": [
        {
          "mistake": "Treating Apache Cassandra like a relational database and trying to perform ad-hoc filtering or JOINs.",
          "correction": "Cassandra requires Query-Driven Data Modeling: create 1 dedicated table per query pattern."
        }
      ],
      "interview_questions": [
        {
          "question": "When would you choose Cassandra over MongoDB in a system design interview?",
          "answer": "Choose Cassandra for write-heavy (>100k QPS) time-series data or multi-region masterless active-active replication without single points of failure. Choose MongoDB when you need rich flexible document querying, secondary indexes, and atomic updates on nested JSON structures."
        }
      ]
    },
    {
      "id": "mongodb-and-document-stores",
      "title": "Document Stores: MongoDB BSON, Indexing & Embedding vs Referencing",
      "definition": "Document stores serialize data into self-describing BSON (Binary JSON) records. Data modeling revolves around the fundamental trade-off between Embedding (nested sub-documents) and Referencing (normalized ID pointers).",
      "why_we_need_it": "Modern applications work natively with object models. Embedding related entities inside a single document allows fetching all required UI data in a single disk read without complex multi-table SQL JOINs.",
      "real_world_analogy": "Embedding is putting a passport photo and driver's license inside a wallet so you have everything at once. Referencing is keeping a locker key in your wallet; you must walk to the locker whenever you need your passport.",
      "how_it_works": "<p><strong>Embedding (1-to-Few):</strong> Store child items (e.g., user addresses) directly inside the parent document `user: { name: 'Alice', addresses: [{ city: 'NYC' }] }`. Read is `O(1)` atomic.<br><strong>Referencing (1-to-Many / Many-to-Many):</strong> Store foreign ObjectIds `order: { user_id: ObjectId('...') }` and use `$lookup` aggregation to join when needed, preventing 16MB document size limits.</p>",
      "conceptual_breakdown": [
        "<strong>16MB BSON Limit:</strong> MongoDB enforces a hard 16MB limit per document to prevent RAM bloat during memory-mapped I/O.",
        "<strong>WiredTiger Engine:</strong> Uses B-Trees for indexes, document-level locking, and snappy compression in memory.",
        "<strong>Replica Sets:</strong> 1 Primary node for writes with automatic failover election via Raft-like consensus to Secondary read replicas."
      ],
      "failure_scenarios": "<strong>Unbounded Document Growth:</strong> Embedding an activity log array inside a user document causes document growth, triggering frequent expensive disk relocations and eventually crashing into the 16MB document size limit.",
      "common_mistakes": [
        {
          "mistake": "Embedding unbounded arrays (e.g. comments on a viral post) inside a single document.",
          "correction": "Use Referencing: store comments in a separate collection with a `post_id` index."
        }
      ],
      "interview_questions": [
        {
          "question": "What are the rules of thumb for Embedding vs Referencing in MongoDB?",
          "answer": "Embed for 1-to-1 or 1-to-Few relationships where child data is always queried together with the parent and has bounded size. Reference for 1-to-Many (>100 children), Many-to-Many, or when child records are frequently accessed independently."
        }
      ]
    },
    {
      "id": "cassandra-and-wide-column",
      "title": "Wide-Column Stores: Apache Cassandra, LSM-Trees & Tunable Consistency",
      "definition": "Apache Cassandra is a masterless, linearly scalable wide-column distributed database utilizing Consistent Hashing, Log-Structured Merge (LSM) trees, and Tunable Consistency (Quorum reads/writes).",
      "why_we_need_it": "Traditional databases have a single primary master for writes, creating a write throughput ceiling and single point of failure. Cassandra allows ANY node in a 1,000-node cluster to accept writes with zero downtime.",
      "real_world_analogy": "A decentralized team of 10 equal partners: anyone can sign a receipt and inform the team via a gossip protocol. If 3 partners are traveling, the remaining 7 partners continue approving business seamlessly.",
      "how_it_works": "<p>1. <strong>Partition Key:</strong> Hashes key (Murmur3) to determine which cluster nodes hold the data on the token ring.<br>2. <strong>Clustering Key:</strong> Sorts data physically on disk within that partition.<br>3. <strong>Write Path:</strong> Writes append to CommitLog on disk (durability) and MemTable in RAM (blazing fast). When MemTable is full, flushed sequentially to immutable SSTables.<br>4. <strong>Tunable Consistency:</strong> Formula `R + W > N` guarantees strong consistency (where N = Replication Factor, W = Write Quorum, R = Read Quorum).</p>",
      "conceptual_breakdown": [
        "<strong>Masterless (Peer-to-Peer):</strong> No master node. All nodes communicate via the Gossip Protocol.",
        "<strong>Compaction:</strong> Background worker merges multiple SSTables, discarding tombstone deletes and stale versions.",
        "<strong>Tombstones:</strong> Deletes in Cassandra don't erase disk immediately; they write a 'tombstone' marker with a TTL to prevent zombie resurrects during anti-entropy repair."
      ],
      "tradeoffs": "<strong>Trade-off:</strong> Blazing write speed and high availability in exchange for no JOINs, no aggregations (`GROUP BY`), and having to duplicate data into multiple tables to satisfy different query filters.",
      "failure_scenarios": "<strong>Tombstone Overload:</strong> Deleting millions of rows creates huge volumes of tombstones; queries scanning through millions of tombstones trigger `TombstoneOverwhelmingException` and crash the node. <em>Mitigation:</em> Design tables with short TTLs or drop entire partition tables.",
      "common_mistakes": [
        {
          "mistake": "Designing Cassandra tables around entities instead of specific query patterns.",
          "correction": "Model Cassandra tables strictly around queries: 1 Table = 1 SELECT query shape."
        }
      ],
      "interview_questions": [
        {
          "question": "How does Cassandra achieve Strong Consistency with Tunable Consistency parameters?",
          "answer": "By setting Replication Factor `N = 3`, Write Consistency `LOCAL_QUORUM` (2 nodes), and Read Consistency `LOCAL_QUORUM` (2 nodes). Because `W + R > N` (2 + 2 = 4 > 3), the read set and write set are mathematically guaranteed to overlap by at least one node holding the latest timestamped record."
        }
      ]
    },
    {
      "id": "dynamodb-and-single-table-design",
      "title": "Amazon DynamoDB & Single-Table Design Architecture",
      "definition": "Amazon DynamoDB is a fully managed serverless key-value and document database offering single-digit millisecond latency at any scale. Single-Table Design is an advanced modeling pattern where an entire application domain is stored inside a single DynamoDB table using overloaded Partition (PK) and Sort Keys (SK).",
      "why_we_need_it": "In multi-table DynamoDB designs, fetching a user and their 10 recent orders requires multiple network round-trips. Single-Table Design allows retrieving heterogeneous entities (User + Orders + Items) in a single ultra-fast `Query` API call.",
      "real_world_analogy": "A physical binder organized with tabs: under tab `USER#123`, page 1 is their Profile, pages 2-10 are their Orders, and page 11 is their Shipping Address. Flipping to tab `USER#123` retrieves everything in one glance.",
      "how_it_works": "<p>1. <strong>Partition Key (PK):</strong> Determines the physical partition storage node.<br>2. <strong>Sort Key (SK):</strong> Organizes and sorts items within that partition.<br>3. <strong>Overloading:</strong> Generic names `PK` and `SK` store multiple entity types (e.g. `PK = USER#101, SK = METADATA` for User; `PK = USER#101, SK = ORDER#2026-001` for Order).<br>4. <strong>GSI (Global Secondary Index):</strong> Allows swapping keys (e.g., `GSI1-PK = ORDER#2026-001, GSI1-SK = STATUS#SHIPPED`) to query reverse relationships.</p>",
      "conceptual_breakdown": [
        "<strong>Query vs Scan:</strong> `Query` uses PK and is sub-10ms; `Scan` scans the entire database table and is a critical production anti-pattern.",
        "<strong>RCU and WCU:</strong> Read/Write Capacity Units govern provisioned throughput (1 RCU = 4KB strong read/sec; 1 WCU = 1KB write/sec).",
        "<strong>DAX (DynamoDB Accelerator):</strong> In-memory microsecond cache tier for DynamoDB."
      ],
      "failure_scenarios": "<strong>Hot Partition Throttling:</strong> If all writes use the same Partition Key (e.g. `PK = DATE#2026-10-03`), a single physical partition exceeds its 1,000 WCU limit and DynamoDB returns `ProvisionedThroughputExceededException`. <em>Mitigation:</em> Suffix partition keys with random salt hashes (`PK = DATE#2026-10-03#rand(0, 10)`).",
      "common_mistakes": [
        {
          "mistake": "Using DynamoDB `Scan` in production API request paths.",
          "correction": "Always design access patterns using `Query` on PK and SK with GSIs."
        }
      ],
      "interview_questions": [
        {
          "question": "What is the primary trade-off of DynamoDB Single-Table Design?",
          "answer": "It provides extreme predictable single-digit millisecond latency and cost efficiency at massive scale, but requires all access patterns to be known upfront; ad-hoc reporting or unexpected new query patterns require building new GSIs or exporting to analytical stores (Athena/Snowflake)."
        }
      ]
    }
  ]
}

# -------------------------------------------------------------
# MODULE 12: Database Scaling & Sharding
# -------------------------------------------------------------
mod_12 = {
  "module_id": "12",
  "module_title": "Database Scaling & Sharding",
  "description": "Master Read Replicas, Master-Slave vs Multi-Master replication, Horizontal Sharding, Shard Keys, Resharding, and Distributed 2-Phase Commit (2PC) transactions.",
  "topics": [
    {
      "id": "read-replicas-and-replication-lag",
      "title": "Primary-Replica Topologies, Async vs Sync Replication & Lag",
      "definition": "Primary-Replica (Master-Slave) replication separates write operations (directed exclusively to 1 Primary instance) from read operations (distributed across multiple Read Replicas) via transaction log streaming.",
      "why_we_need_it": "90% of web workloads are read-heavy (e.g., 95% reads, 5% writes). Adding 5 read replicas scales read capacity by 5x without modifying database schemas.",
      "real_world_analogy": "A newspaper printing press: 1 author writes the master article (Primary); 10 delivery vans distribute copies to readers across the city (Replicas). Readers don't need to visit the author's desk to read the news.",
      "how_it_works": "<p>1. <strong>Synchronous Replication:</strong> Primary writes WAL and waits for replica ACK before committing to client (Zero data loss, high write latency).<br>2. <strong>Asynchronous Replication:</strong> Primary commits immediately, streaming WAL logs in background (Sub-millisecond writes, risk of Replication Lag and data loss on primary crash).<br>3. <strong>Semi-Synchronous:</strong> Primary waits for at least 1 replica to ACK receipt before committing.</p>",
      "conceptual_breakdown": [
        "<strong>Replication Lag:</strong> The time delay (e.g. 50ms to 2s) between a commit on the primary and its replay on a read replica.",
        "<strong>Read-Your-Own-Writes Consistency:</strong> After a user posts a comment, routing their immediate next read to the Primary (or waiting for replica LSN) so they don't see their own comment disappear."
      ],
      "failure_scenarios": "<strong>Split-Brain in Auto-Failover:</strong> A network glitch isolates the Primary; the cluster elects a new Primary. When the old Primary reconnects, both accept writes simultaneously, causing diverging incompatible databases. <em>Mitigation:</em> Enforce STONITH (Shoot The Other Node In The Head) fencing and Quorum elections.",
      "common_mistakes": [
        {
          "mistake": "Routing immediate post-action UI reads to read replicas, causing users to see stale data.",
          "correction": "Route the modifying user's reads to the Primary for a short grace window (e.g., 2 seconds)."
        }
      ],
      "interview_questions": [
        {
          "question": "How do you achieve Read-Your-Own-Writes consistency in an asynchronous replica architecture?",
          "answer": "Route reads to the Primary DB for recently updated users (based on a short session cookie timestamp), use Replica Lag Tokens (tracking Log Sequence Numbers / LSNs), or pin the user's reads to the primary for 2-5 seconds after any write operation."
        }
      ]
    },
    {
      "id": "horizontal-sharding-and-partitioning",
      "title": "Horizontal Sharding: Range, Hash & Directory-Based Sharding",
      "definition": "Database Sharding is the horizontal partitioning of a massive database dataset across multiple independent database server instances (Shards), each holding a subset of total rows.",
      "why_we_need_it": "When database storage exceeds 10TB or write QPS exceeds single-server limits (>20,000 writes/sec), vertical scaling hits a physical hardware wall. Sharding distributes data and write traffic across N database machines.",
      "real_world_analogy": "Dividing a 5,000-page encyclopedia into 26 distinct physical volumes (A, B, C... Z). If 26 researchers want to read different letters, they all read their own volume simultaneously with zero contention.",
      "how_it_works": "<p>1. <strong>Hash-Based Sharding:</strong> `Shard_ID = Hash(ShardKey) % Num_Shards`. Provides uniform data distribution across all shards.<br>2. <strong>Range-Based Sharding:</strong> Divides data by contiguous key ranges (e.g. User IDs 1-1M -> Shard 1, 1M-2M -> Shard 2). Allows fast range scans but creates hot spots for recent auto-increment IDs.<br>3. <strong>Directory-Based (Lookup Table):</strong> A central lookup service maps Shard Keys to Shard IDs, enabling dynamic rebalancing without complex mathematical remapping.</p>",
      "conceptual_breakdown": [
        "<strong>Shard Key Selection:</strong> The single most critical architectural decision. A good shard key has high cardinality, uniform distribution, and matches primary query access patterns (e.g., `user_id` or `tenant_id`).",
        "<strong>Cross-Shard Queries:</strong> A query without a shard key (e.g. `SELECT * FROM orders WHERE status = 'PENDING'`) must scatter-gather to ALL shards, destroying performance."
      ],
      "failure_scenarios": "<strong>Celebrity Shard Hotspotting:</strong> Sharding Twitter by `user_id` places Elon Musk on Shard 4. Whenever he tweets, millions of likes hit Shard 4, blowing its CPU while Shards 1, 2, 3 sit at 5% load. <em>Mitigation:</em> Hybrid fan-out routing or separate hot-user partitions.",
      "common_mistakes": [
        {
          "mistake": "Sharding by auto-incrementing `created_at` timestamp.",
          "correction": "This routes 100% of all current write traffic to the single latest shard, completely defeating the purpose of sharding."
        }
      ],
      "interview_questions": [
        {
          "question": "What are the major challenges introduced when sharding a relational database?",
          "answer": "Loss of cross-shard foreign keys and JOINs, complex distributed transactions (requiring 2PC or Sagas), scatter-gather query latency, and high operational overhead when resharding/rebalancing data as the cluster grows."
        }
      ]
    },
    {
      "id": "resharding-and-zero-downtime-migration",
      "title": "Resharding Strategies & Zero-Downtime Data Migration",
      "definition": "Resharding is the process of splitting existing overloaded shards or increasing the total shard count (e.g. from 16 to 32 shards) while maintaining 100% live production availability and data integrity.",
      "why_we_need_it": "As business data grows 10x, initial shard storage fills up. Migrating petabytes of live operational data without taking the platform offline is a premier system design challenge.",
      "real_world_analogy": "Widening a 4-lane highway into an 8-lane highway while 100,000 cars are actively driving on it at 70 mph without stopping traffic.",
      "how_it_works": "<p>The standard 4-phase Zero-Downtime Migration Pattern:<br>1. <strong>Dual Writing:</strong> Application writes new data to BOTH old and new shard topologies simultaneously.<br>2. <strong>Backfill:</strong> Background batch workers copy historical data from old shards to new shards with Change Data Capture (CDC) deduplication.<br>3. <strong>Data Validation:</strong> Automated verification reconciles checksums between old and new shards.<br>4. <strong>Cutover:</strong> Switch read traffic to new shards, monitor error rates for 48 hours, then turn off writes to old shards.</p>",
      "conceptual_breakdown": [
        "<strong>Virtual Shards:</strong> Start with 1,024 virtual shards mapped to 16 physical machines (64 per machine). Scaling to 32 machines simply moves 32 virtual shards to each new machine without changing hash formulas.",
        "<strong>CDC (Change Data Capture):</strong> Debezium streaming database WAL logs to Kafka guarantees no writes are lost during the multi-hour backfill phase."
      ],
      "failure_scenarios": "<strong>Dual-Write Race Conditions:</strong> Writing to Old DB then New DB without distributed transaction guarantees can leave New DB with corrupted or partial records if the application crashes between writes. <em>Mitigation:</em> Use CDC from the Old DB WAL to populate New DB asynchronously instead of in-app dual writing.",
      "common_mistakes": [
        {
          "mistake": "Attempting resharding via a scheduled maintenance downtime window for large datasets.",
          "correction": "Always implement zero-downtime CDC backfill and virtual sharding topologies."
        }
      ],
      "interview_questions": [
        {
          "question": "How does Virtual Sharding (Pre-Sharding) simplify database scaling?",
          "answer": "By creating a large fixed number of logical shards (e.g. 1,024) on day one mapped to a few physical servers, future scaling only requires migrating logical database files between servers rather than recomputing shard key hash algorithms across billions of rows."
        }
      ]
    },
    {
      "id": "distributed-transactions-and-2pc",
      "title": "Distributed Transactions: Two-Phase Commit (2PC) vs Sagas",
      "definition": "Two-Phase Commit (2PC) is a distributed consensus protocol that guarantees ACID atomic transactions across multiple distinct database shards or services. Sagas manage distributed transactions via a sequence of local transactions coordinated with compensating rollback events.",
      "why_we_need_it": "When financial transfers or order bookings span multiple sharded databases, either all shards commit or all roll back; partial commits corrupt data integrity.",
      "real_world_analogy": "2PC is a wedding ceremony: The coordinator asks Partner A 'Do you take...?' (Prepare). Partner A says 'I do'. Coordinator asks Partner B (Prepare). Partner B says 'I do'. Coordinator says 'I now pronounce you married' (Commit). If either says 'No', the wedding is cancelled (Abort).",
      "how_it_works": "<p><strong>2PC Protocol:</strong><br>&bull; <em>Phase 1 (Prepare):</em> Coordinator asks all participants to prepare and lock rows. Nodes write to WAL and respond 'VOTE_COMMIT' or 'VOTE_ABORT'.<br>&bull; <em>Phase 2 (Commit):</em> If ALL voted yes, coordinator logs 'GLOBAL_COMMIT' and sends commit command. If anyone voted no or timed out, coordinator sends 'GLOBAL_ABORT'.<br><strong>Sagas:</strong> Avoids blocking locks. Step 1 commits locally. If Step 3 fails, the saga orchestrator executes Compensating Actions for Steps 2 and 1 in reverse order.</p>",
      "conceptual_breakdown": [
        "<strong>2PC Blocking Vulnerability:</strong> If the Coordinator crashes during Phase 2, participant shards hold database row locks indefinitely, blocking all other transactions.",
        "<strong>Saga Eventual Consistency:</strong> Trades isolation for high throughput; intermediate uncommitted states are visible to other users."
      ],
      "comparison_matrix": {
        "title": "Two-Phase Commit (2PC) vs Saga Pattern",
        "columns": ["Feature", "Two-Phase Commit (2PC)", "Saga Pattern (Orchestrated/Choreographed)"],
        "rows": [
          ["ACID Guarantee", "Full ACID (Strong Consistency & Isolation)", "ACD (Eventual Consistency, No Isolation)"],
          ["Locking & Latency", "Heavy blocking locks held across network round-trips", "Zero distributed locks; fast local commits"],
          ["Failure Recovery", "Automatic rollback via WAL logs", "Application-level Compensating Transactions"],
          ["Scalability & Throughput", "Poor (Bottlenecks at scale >10 nodes)", "Extremely High (Asynchronous event-driven)"],
          ["Best Use Case", "Internal sharded RDBMS partitions", "Cross-microservice business workflows"]
        ]
      },
      "failure_scenarios": "<strong>Coordinator Crash in 2PC:</strong> Shard 1 voted yes and is holding locks waiting for the coordinator's commit message. The coordinator crashes. Shard 1 cannot commit or abort on its own, locking out all traffic on those rows. <em>Mitigation:</em> 3-Phase Commit (3PC) or Paxos-backed consensus coordinators.",
      "common_mistakes": [
        {
          "mistake": "Using 2PC across microservices spanning multiple cloud regions or third-party APIs.",
          "correction": "Use Sagas with Idempotent Compensating Actions for distributed microservices."
        }
      ],
      "interview_questions": [
        {
          "question": "Why is Two-Phase Commit rarely used in modern high-throughput internet-scale microservices?",
          "answer": "2PC is a synchronous, blocking protocol. Holding distributed database locks across network boundaries dramatically increases latency, degrades throughput, and creates availability vulnerabilities whenever any participating node or network link stutters."
        }
      ]
    }
  ]
}

# -------------------------------------------------------------
# MODULE 13: Distributed Systems Core: CAP, PACELC & Consensus
# -------------------------------------------------------------
mod_13 = {
  "module_id": "13",
  "module_title": "Distributed Systems Core: CAP, PACELC & Consistency Models",
  "description": "Master CAP Theorem, PACELC, the 8 Fallacies of Distributed Computing, Consistency Models (Linearizable to Eventual), and Vector Clocks.",
  "topics": [
    {
      "id": "cap-theorem-explained",
      "title": "CAP Theorem: Consistency, Availability & Partition Tolerance",
      "definition": "The CAP Theorem (Brewer's Theorem) states that in any asynchronous distributed network subject to network partitions (P), a system can guarantee at most two of the three properties: Consistency (C) or Availability (A). Because network partitions are unavoidable in physical reality, the real trade-off is CP vs AP.",
      "why_we_need_it": "Hardware cables get cut, routers reboot, and cross-datacenter fiber links fail. CAP provides the mathematical foundation for making deliberate architectural trade-offs during network partitions.",
      "real_world_analogy": "Two bank tellers in different cities whose telephone wire gets cut (Partition). If a customer deposits $100 in City A: Either Teller B refuses to dispense cash until the phone is fixed (CP - Consistency over Availability), or Teller B dispenses cash based on old balance, risking overdrafts (AP - Availability over Consistency).",
      "how_it_works": "<p>1. <strong>Consistency (Linearizability):</strong> Every read receives the most recent write or an error.<br>2. <strong>Availability:</strong> Every non-failing node returns a non-error response for every request (no guarantee it is the newest write).<br>3. <strong>Partition Tolerance:</strong> The system continues operating despite arbitrary dropped or delayed network packets between nodes.<br>4. <strong>The CP Choice (e.g. HBase, Zookeeper, etcd):</strong> Rejects writes or returns errors to preserve 100% data correctness.<br>5. <strong>The AP Choice (e.g. Cassandra, DynamoDB, Couchbase):</strong> Accepts writes on all sides of the partition, resolving conflicts later via eventual consistency.</p>",
      "conceptual_breakdown": [
        "<strong>'CA' is a Myth:</strong> You cannot 'choose CA'. A system without Partition Tolerance is a single machine that crashes whenever a network wire disconnects.",
        "<strong>Normal Mode vs Partition Mode:</strong> In normal operation (no network partition), systems provide BOTH Consistency and Availability."
      ],
      "comparison_matrix": {
        "title": "CP vs AP Systems Comparison",
        "columns": ["Dimension", "CP Systems (Consistency + Partition Tolerance)", "AP Systems (Availability + Partition Tolerance)"],
        "rows": [
          ["Behavior during Partition", "Blocks or returns errors on isolated nodes", "Accepts reads and writes on all partitions"],
          ["Data Freshness", "Always returns latest committed data", "May return stale or conflicting data"],
          ["Conflict Resolution", "Not needed (Only 1 valid leader commits)", "Last-Write-Wins (LWW) or Vector Clocks / CRDTs"],
          ["Typical Technologies", "etcd, Consul, Zookeeper, Google Spanner, CockroachDB", "Apache Cassandra, Amazon DynamoDB, CouchDB"],
          ["Best Application Domain", "Financial ledgers, distributed locks, cluster metadata", "Shopping carts, social media feeds, IoT metrics"]
        ]
      },
      "failure_scenarios": "<strong>Misclassifying System Requirements:</strong> Choosing AP for a banking balance ledger allows double-spending during network partitions; choosing CP for a social feed causes global site outages whenever a minor switch stutters.",
      "common_mistakes": [
        {
          "mistake": "Claiming an RDBMS like PostgreSQL is a 'CA system' in a distributed systems interview.",
          "correction": "In a distributed context, network partitions are inevitable; PostgreSQL in a distributed replica setup is CP or AP depending on synchronous vs asynchronous replication configuration."
        }
      ],
      "interview_questions": [
        {
          "question": "Why is it mathematically impossible for a distributed system to achieve CA during a network partition?",
          "answer": "If Node 1 and Node 2 cannot communicate (Partition P), and a client writes data to Node 1: if Node 2 serves a subsequent read, it must either return stale data (violating Consistency C) or refuse to answer / return an error (violating Availability A)."
        }
      ]
    },
    {
      "id": "pacelc-theorem-deep-dive",
      "title": "PACELC Theorem: Latency vs Consistency in Normal Operation",
      "definition": "The PACELC Theorem extends CAP by stating: If there is a **P**artition, how does your system choose between **A**vailability and **C**onsistency? **E**lse (in normal operation), how does your system trade off **L**atency vs **C**onsistency?",
      "why_we_need_it": "Partitions happen <0.1% of the time. PACELC explains the engineering trade-offs made 99.9% of the time during normal operation: waiting for synchronous multi-node replication increases read/write latency.",
      "real_world_analogy": "A restaurant chef: During a storm (Partition), do you close (CP) or serve cold food (AP)? On a normal sunny day (Else), do you make customers wait 30 minutes for a freshly cooked meal (Consistency/PC) or serve instant pre-made buffet food in 10 seconds (Latency/PA/EL)?",
      "how_it_works": "<p>Classifications:<br>&bull; <strong>PC/EC (e.g. Google Spanner, etcd):</strong> Under partition choose Consistency; during normal operation choose Consistency (higher latency for consensus).<br>&bull; <strong>PA/EL (e.g. Cassandra, DynamoDB, Riak):</strong> Under partition choose Availability; during normal operation choose Latency (async replication for sub-5ms responses).<br>&bull; <strong>PA/EC (e.g. MongoDB):</strong> Under partition chooses Availability; during normal operation waits for primary commit consistency.</p>",
      "conceptual_breakdown": [
        "<strong>Latency vs Consistency:</strong> Strong consistency requires waiting for cross-node network round-trips (`fsync` + ACK), increasing p99 latency.",
        "<strong>Modern Cloud Reality:</strong> Most system design decisions in production are actually **EL** (Latency) vs **EC** (Consistency) decisions."
      ],
      "failure_scenarios": "<strong>High p99 Latency from Over-Constrained Consistency:</strong> Setting synchronous write replication across 3 continents to achieve EC drops write throughput to <50 QPS and spikes p99 latency to 350ms due to speed-of-light propagation delays.",
      "common_mistakes": [
        {
          "mistake": "Relying solely on CAP theorem without understanding the latency cost of strong consistency in normal operating conditions.",
          "correction": "Use PACELC to evaluate latency vs consistency trade-offs when designing multi-region distributed architectures."
        }
      ],
      "interview_questions": [
        {
          "question": "How is Amazon DynamoDB classified under the PACELC theorem?",
          "answer": "DynamoDB is classified as **PA/EL**: during a network partition it favors Availability (PA); during normal operation it defaults to low Latency with eventual consistency (EL), but allows developers to opt into EC (Strong Consistency) on individual read operations."
        }
      ]
    },
    {
      "id": "fallacies-of-distributed-computing",
      "title": "The 8 Fallacies of Distributed Computing",
      "definition": "The 8 Fallacies of Distributed Computing are false assumptions developers make when transitioning from single-process monoliths to networked distributed systems, originally formulated by Peter Deutsch and James Gosling.",
      "why_we_need_it": "Assuming the network is perfect leads to missing timeouts, lack of retries, unhandled partial failures, and catastrophic cascade crashes.",
      "real_world_analogy": "Assuming every postal package mailed will arrive in exactly 24 hours without being lost, damaged, delayed by rain, or delivered to the wrong address.",
      "how_it_works": "<p>The 8 Core Fallacies:<br>1. <strong>The network is reliable:</strong> Packets drop, switches reboot, links flap.<br>2. <strong>Latency is zero:</strong> Every RPC incurs network traversal and serialization cost.<br>3. <strong>Bandwidth is infinite:</strong> Large payloads congest NICs and saturation queues.<br>4. <strong>The network is secure:</strong> Zero-trust mTLS encryption is mandatory.<br>5. <strong>Topology doesn't change:</strong> Nodes constantly autoscale, die, and move IPs.<br>6. <strong>There is one administrator:</strong> Multiple teams configure firewalls, DNS, and proxies independently.<br>7. <strong>Transport cost is zero:</strong> Serialization (JSON/Protobuf) and TLS crypto burn CPU.<br>8. <strong>The network is homogeneous:</strong> Systems run across Linux, Windows, ARM, x86, iOS, and Android.</p>",
      "conceptual_breakdown": [
        "<strong>Partial Failure:</strong> In a single process, code either runs or crashes. In distributed systems, a server can hang indefinitely without failing.",
        "<strong>Architectural Safeguards:</strong> Timeouts, Circuit Breakers, Exponential Backoff with Jitter, Bulkheads, and Idempotency Keys."
      ],
      "failure_scenarios": "<strong>Infinite Socket Hang:</strong> Calling an external HTTP API without an explicit socket timeout causes client worker threads to hang forever when the remote server freezes, completely depleting the web server thread pool within 2 minutes.",
      "common_mistakes": [
        {
          "mistake": "Instantiating network HTTP clients without configuring explicit connect and read timeouts.",
          "correction": "Always set aggressive connect timeouts (e.g. 500ms) and read timeouts (e.g. 2s) on all outbound network requests."
        }
      ],
      "interview_questions": [
        {
          "question": "Which of the 8 Fallacies causes the most production outages and how is it mitigated?",
          "answer": "'The network is reliable' and 'Latency is zero'. When downstreams hang, upstream callers exhaust thread pools and collapse. Mitigate using strict timeouts, circuit breakers, rate limiters, and bulkhead thread pool isolation."
        }
      ]
    },
    {
      "id": "vector-clocks-and-eventual-consistency",
      "title": "Logical Clocks: Lamport Timestamps, Vector Clocks & CRDTs",
      "definition": "Logical Clocks and Vector Clocks are mechanisms for capturing causal relationships and event ordering in distributed systems without relying on synchronized physical wall-clock time. Conflict-Free Replicated Data Types (CRDTs) enable concurrent edits to converge automatically without conflicts.",
      "why_we_need_it": "Physical server clocks suffer from Clock Drift (NTP synchronization skew). Relying on physical `System.currentTimeMillis()` causes Last-Write-Wins (LWW) to silently erase valid user updates.",
      "real_world_analogy": "Numbering messages in a postal pen-pal correspondence: Message 1, 2, 3... Even if Letter 3 arrives before Letter 2 due to postal delays, you know Letter 2 was written first based on its causal sequence number.",
      "how_it_works": "<p>1. <strong>Lamport Timestamps:</strong> A single scalar counter incremented on every event and passed in RPC headers. Defines a partial order (`Happens-Before` relation $A \\rightarrow B$).<br>2. <strong>Vector Clocks:</strong> An array of logical counters, one per node $V = [N_1: c_1, N_2: c_2, ...]$. Allows distinguishing between causally ordered events ($V_A < V_B$) and concurrent conflicting events ($V_A \\parallel V_B$).<br>3. <strong>CRDTs (State-based & Operation-based):</strong> Mathematical data structures (G-Counter, PN-Counter, LWW-Element-Set, Text CRDTs in Google Docs/Figma) whose merge operations are Commutative, Associative, and Idempotent ($A + B = B + A$).</p>",
      "conceptual_breakdown": [
        "<strong>Happens-Before Relationship ($\\rightarrow$):</strong> If event A caused event B, then $V(A) < V(B)$.",
        "<strong>Concurrent Conflicts:</strong> If neither vector clock dominates, a causal conflict occurred; application prompts user or merges via domain rules.",
        "<strong>CRDT Convergence:</strong> All replicas eventually reach the exact same state once all update operations are exchanged, with ZERO locking."
      ],
      "failure_scenarios": "<strong>Clock Skew Data Erasure in Cassandra LWW:</strong> Server A's physical clock is 500ms in the future due to bad NTP. When Server B writes a newer update with a correct clock, Cassandra silently discards B's update because A's timestamp appears higher, permanently losing data.",
      "common_mistakes": [
        {
          "mistake": "Relying on physical timestamps for distributed transaction sequencing across independent server nodes.",
          "correction": "Use Vector Clocks, Hybrid Logical Clocks (HLC), or Google TrueTime (GPS + Atomic Clocks) for deterministic ordering."
        }
      ],
      "interview_questions": [
        {
          "question": "How do Vector Clocks detect concurrent conflicts between two write operations?",
          "answer": "Given two vector clocks $V_A$ and $V_B$: if every counter in $V_A \\ge V_B$ with at least one strictly greater, $V_A$ causally succeeds $V_B$. If $V_A$ has some counters greater than $V_B$ while $V_B$ has other counters greater than $V_A$, the writes occurred concurrently in parallel without knowledge of each other, signaling a conflict that requires resolution."
        }
      ]
    }
  ]
}

# -------------------------------------------------------------
# MODULE 14: Distributed Consensus & Coordination
# -------------------------------------------------------------
mod_14 = {
  "module_id": "14",
  "module_title": "Distributed Consensus & Coordination",
  "description": "Master distributed consensus protocols (Raft, Paxos), cluster coordination engines (Zookeeper, etcd), leader election, and distributed locking with Redlock.",
  "topics": [
    {
      "id": "raft-consensus-algorithm",
      "title": "Raft Consensus Algorithm: Leader Election, Log Replication & Safety",
      "definition": "Raft is a distributed consensus algorithm designed for understandability, equivalent to multi-Paxos in fault tolerance and performance. It maintains a replicated state machine across a cluster of $2F+1$ nodes, tolerating up to $F$ node failures.",
      "why_we_need_it": "In distributed databases and Kubernetes control planes, all nodes must agree on the exact sequence of state updates and elect a single authoritative leader without split-brain.",
      "real_world_analogy": "A parliamentary committee of 5 members: 1 elected Chairperson leads the agenda. To pass any new rule, at least 3 members (Quorum) must vote yes. If the Chairperson passes out, the remaining members vote and elect a new Chairperson immediately.",
      "how_it_works": "<p>1. <strong>Node Roles:</strong> Leader, Follower, or Candidate.<br>2. <strong>Leader Election:</strong> Followers expect periodic heartbeats. If a randomized Election Timeout (150ms-300ms) elapses without heartbeats, a Follower converts to Candidate, increments `currentTerm`, and requests votes. First to win Quorum (`(N/2)+1`) becomes Leader.<br>3. <strong>Log Replication:</strong> Clients send commands to the Leader. Leader appends command to its log and sends `AppendEntries` RPCs to Followers. Once a majority of followers acknowledge writing to their disk, the Leader commits the entry and applies it to its state machine.<br>4. <strong>Safety Invariants:</strong> Election Safety, Leader Append-Only, Log Matching Property, and Leader Completeness (a candidate must possess all committed logs to win election).</p>",
      "conceptual_breakdown": [
        "<strong>Odd Number of Nodes:</strong> Clusters use 3 or 5 nodes (3 nodes tolerate 1 failure; 5 nodes tolerate 2 failures).",
        "<strong>Split Votes:</strong> Randomized election timers prevent simultaneous candidate voting deadlocks.",
        "<strong>Term Numbers:</strong> Logical clocks that detect obsolete leaders and stale RPCs."
      ],
      "comparison_matrix": {
        "title": "Raft vs Paxos vs Zab Consensus Comparison",
        "columns": ["Dimension", "Raft (etcd, Consul, CockroachDB)", "Multi-Paxos (Google Spanner, Chubby)", "Zab (Apache Zookeeper)"],
        "rows": [
          ["Understandability", "High (Decomposed into Election, Replication, Safety)", "Very Low (Abstract, notoriously difficult)", "Moderate (Primary-Backup with epoch recovery)"],
          ["Leader Role", "Strong Leader (All writes & reads go to leader)", "Weak/Multi-Leader (Any node can propose)", "Primary Leader (Atomic broadcast)"],
          ["Log Discrepancies", "Leader forces followers to overwrite discrepancies", "Complex reconciliation rounds", "Followers sync to Leader's epoch snapshot"],
          ["Production Adoption", "etcd (Kubernetes), TiKV, CockroachDB, Raft engines", "Google Spanner, AWS internal control planes", "Apache Kafka (pre-KRaft), Apache Hadoop"]
        ]
      },
      "failure_scenarios": "<strong>Network Partition Split Brain:</strong> A 5-node cluster splits into Partition A (2 nodes with old leader) and Partition B (3 nodes). Partition B elects a new leader and reaches Quorum (3/5) for writes. Partition A cannot reach Quorum (2/5) and rejects writes. When reconnected, Partition A's old leader steps down and overwrites its log with B's authoritative log.",
      "common_mistakes": [
        {
          "mistake": "Deploying an even number of consensus nodes (e.g. 4 nodes).",
          "correction": "Always use an odd number of nodes ($2F+1$). 4 nodes still only tolerate 1 failure while requiring a 3-node Quorum, giving worse availability than 3 nodes."
        }
      ],
      "interview_questions": [
        {
          "question": "How does Raft guarantee that a newly elected Leader contains all previously committed log entries?",
          "answer": "Followers will reject `RequestVote` RPCs from any Candidate whose log is less up-to-date than their own (compared by last log term, then last log index). Because any committed entry must reside on a majority of nodes, and winning an election requires votes from a majority of nodes, the winning candidate is mathematically guaranteed to overlap with at least one node holding all committed entries."
        }
      ]
    },
    {
      "id": "etcd-and-zookeeper",
      "title": "Cluster Coordination Engines: etcd vs Apache Zookeeper",
      "definition": "Distributed coordination engines provide strongly consistent hierarchical key-value storage, distributed locks, cluster membership heartbeats, leader election, and event watchers for cloud infrastructure.",
      "why_we_need_it": "Kubernetes clusters, distributed databases, and Kafka brokers require a rock-solid single source of truth for node discovery, configuration management, and failover coordination.",
      "real_world_analogy": "A master building directory and key registry: all security guards, elevator operators, and maintenance teams read and watch this one verified board to coordinate building operations.",
      "how_it_works": "<p><strong>etcd (Go, Raft):</strong> Stores keys in a multi-version concurrency control (MVCC) bbolt key-value store. Provides gRPC APIs, atomic transactions (`Txn`), lease-based key expiration, and long-lived streaming Watchers on key prefixes.<br><strong>Zookeeper (Java, Zab):</strong> Hierarchical tree structure resembling a filesystem (`/services/auth/node-1`). Provides ephemeral znodes (auto-deleted on client disconnect) and sequential znodes for distributed leader elections.</p>",
      "conceptual_breakdown": [
        "<strong>Kubernetes Backbone:</strong> etcd stores 100% of Kubernetes cluster state (Pods, Services, Deployments, Secrets).",
        "<strong>Watch Mechanism:</strong> Clients subscribe to key prefixes via HTTP/2 or gRPC streams, receiving push notifications in <1ms when configurations change.",
        "<strong>Ephemeral Leases:</strong> Nodes attach a 5-second lease to their registration key; if the node crashes and stops renewing the lease, the key vanishes automatically."
      ],
      "failure_scenarios": "<strong>Slow Disk fsync Stalling etcd:</strong> etcd requires continuous disk `fsync` on WAL commits. If running on slow HDDs or shared cloud EBS volumes with noisy neighbors, fsync latency spikes to >50ms, causing missed Raft heartbeats, leader election storms, and Kubernetes API freezes. <em>Mitigation:</em> Run etcd exclusively on dedicated NVMe SSDs.",
      "common_mistakes": [
        {
          "mistake": "Storing large binary payloads or application databases (>100MB) in etcd.",
          "correction": "etcd is optimized for small metadata keys (<10KB) with total database size limit of 2GB to 8GB."
        }
      ],
      "interview_questions": [
        {
          "question": "How do ephemeral znodes in Zookeeper enable automated Leader Election?",
          "answer": "All candidate nodes attempt to create the same ephemeral znode (e.g., `/app/leader`). The first node to succeed becomes Leader. Remaining nodes set a Watcher on that znode. If the Leader crashes, its session disconnects, Zookeeper automatically deletes the ephemeral znode, and the Watcher alerts remaining nodes to race to create the znode and become the new Leader."
        }
      ]
    },
    {
      "id": "distributed-locks-and-redlock",
      "title": "Distributed Locks: Redis (SETNX / Redlock) vs etcd Leases",
      "definition": "Distributed Locks enforce mutual exclusion across multiple independent processes running on separate servers to prevent concurrent execution of critical sections (e.g. charging a payment or booking a seat).",
      "why_we_need_it": "Standard programming language mutexes (`std::mutex`, `synchronized`) only work within a single operating system process memory space. Distributed locks coordinate across multiple cloud machines.",
      "real_world_analogy": "A single physical restroom key hanging on a hook: only one employee at the office can hold the key at a time. If someone takes the key, everyone else must wait for it to be returned.",
      "how_it_works": "<p>1. <strong>Redis Single-Node Lock:</strong> `SET resource_name my_random_token NX PX 30000` (Acquire lock only if Not eXists, with 30s TTL). Release via atomic Lua script matching `my_random_token`.<br>2. <strong>Redlock Algorithm:</strong> To survive Redis master crash before async replica sync, client acquires lock on a majority (e.g. 3 of 5) of independent Redis master nodes.<br>3. <strong>etcd / Zookeeper Locks (Safest):</strong> Acquire lock via ephemeral lease and monotonic sequence numbers (Fencing Tokens).</p>",
      "conceptual_breakdown": [
        "<strong>Fencing Tokens:</strong> Every lock grant generates a monotonically increasing counter (1, 2, 3...). The shared storage resource (DB) rejects any write with a token lower than the highest seen token, preventing GC pause corruption.",
        "<strong>GC Pause Vulnerability (Martin Kleppmann critique):</strong> Process A acquires lock -> freezes in a 60s Java GC pause -> lock TTL expires -> Process B acquires lock -> Process A wakes up and writes corrupted data simultaneously."
      ],
      "failure_scenarios": "<strong>Asynchronous Redis Failover Lock Duplication:</strong> Client A acquires lock on Redis Master. Master crashes before replicating to Replica. Replica is promoted to Master. Client B acquires the same lock. Now Client A and Client B both hold the lock simultaneously. <em>Mitigation:</em> Use Redlock across 5 independent masters or use etcd/Consul.",
      "common_mistakes": [
        {
          "mistake": "Releasing a distributed lock in Redis with a simple `DEL lock_key` command.",
          "correction": "Never use simple `DEL`. If your process ran slow and the lock expired, you will delete another process's newly acquired lock. Always use a Lua script verifying token ownership."
        }
      ],
      "interview_questions": [
        {
          "question": "What is a Fencing Token and why is it mandatory for 100% correct distributed locking?",
          "answer": "A Fencing Token is an incrementing sequence number issued by the lock service. It protects against cases where a lock holder freezes (e.g. GC pause or network stall) and continues executing after its lock lease expired. The backend storage system verifies that incoming write tokens are greater than all previously accepted tokens, dropping stale writes from expired lock holders."
        }
      ]
    }
  ]
}

# -------------------------------------------------------------
# MODULE 15: Message Queues & Event Streaming
# -------------------------------------------------------------
mod_15 = {
  "module_id": "15",
  "module_title": "Message Queues & Event Streaming",
  "description": "Master asynchronous messaging: RabbitMQ vs Apache Kafka, SQS vs SNS, Publish-Subscribe topologies, consumer groups, backpressure, and Dead-Letter Queues (DLQ).",
  "topics": [
    {
      "id": "message-queue-fundamentals",
      "title": "Message Queues vs Event Streams: Push vs Pull & Point-to-Point vs Pub/Sub",
      "definition": "Message Queues (RabbitMQ, SQS) buffer transient messages for point-to-point worker task execution with individual message acknowledgments and deletions. Event Streaming platforms (Apache Kafka, Apache Pulsar) record continuous, immutable, ordered append-only logs replayed by multiple consumer groups at their own pace.",
      "why_we_need_it": "Synchronous HTTP calls couple services tightly: if Service B is slow or down, Service A fails. Message brokers decouple producer execution, absorb massive traffic spikes, and guarantee reliable asynchronous delivery.",
      "real_world_analogy": "A Message Queue is an individual postal mailbox: you drop a letter in, a postal worker picks it up, delivers it, and shreds the envelope once processed. An Event Stream is a continuous recorded TV broadcast: viewers can tune in live, rewind to yesterday's news, or re-watch episodes from the beginning.",
      "how_it_works": "<p><strong>Message Queues (Push model / Smart Broker):</strong> Broker tracks individual message delivery, routing messages to available consumer workers via AMQP/HTTP. Messages are deleted upon ACK.<br><strong>Event Streams (Pull model / Dumb Broker, Smart Consumer):</strong> Broker appends events sequentially to disk partitions. Consumers pull batches of messages and track their own cursor position (Offset). Messages persist on disk according to retention policies (e.g. 7 days).</p>",
      "conceptual_breakdown": [
        "<strong>Point-to-Point:</strong> Each message is consumed by exactly ONE worker in the consumer pool.",
        "<strong>Publish-Subscribe (Pub/Sub):</strong> A single published message is broadcast and copied to ALL subscribed queues/services.",
        "<strong>Backpressure:</strong> Pull-based consumers only fetch as many messages as they have CPU capacity to process, preventing server out-of-memory crashes."
      ],
      "comparison_matrix": {
        "title": "Message Queues (RabbitMQ/SQS) vs Event Streams (Kafka)",
        "columns": ["Feature", "Message Queues (RabbitMQ / SQS)", "Event Streaming (Apache Kafka / Pulsar)"],
        "rows": [
          ["Data Model", "Transient messages deleted upon ACK", "Persistent, immutable append-only commit log"],
          ["Delivery Paradigm", "Push (Broker pushes to workers)", "Pull (Consumers poll batches from brokers)"],
          ["Message Ordering", "Strict within single FIFO queue", "Strict within individual partition only"],
          ["Message Replay", "Not possible (Deleted once consumed)", "Supported (Reset offset to replay historical data)"],
          ["Throughput", "Moderate (10k - 50k msgs/sec)", "Massive (Millions of events/sec via sequential disk I/O)"],
          ["Best Use Case", "Background task jobs, complex routing, notifications", "Real-time analytics, event sourcing, CDC, clickstreams"]
        ]
      },
      "failure_scenarios": "<strong>Poison Pill Crash Loops:</strong> A malformed message causes the worker process to crash with an unhandled exception before sending an ACK. The broker requeues the message, sending it to another worker which also crashes, taking down the entire worker fleet in minutes. <em>Mitigation:</em> Configure Dead-Letter Queues (DLQ) with max retry counts.",
      "common_mistakes": [
        {
          "mistake": "Using Apache Kafka as a simple task queue with individual message acknowledgments and arbitrary delays.",
          "correction": "Use RabbitMQ or AWS SQS for individual task routing and delay queues; use Kafka for high-throughput stream processing."
        }
      ],
      "interview_questions": [
        {
          "question": "Why is Kafka's pull-based consumer architecture superior to push-based brokers for high-throughput stream processing?",
          "answer": "Pull-based architecture prevents fast producers from overwhelming slow consumers (built-in backpressure). Consumers control their own polling rate, batch sizes, and memory usage, and can easily replay past data by seeking their offset backwards."
        }
      ]
    },
    {
      "id": "kafka-architecture-deep-dive",
      "title": "Apache Kafka Internals: Topics, Partitions, Offsets & KRaft",
      "definition": "Apache Kafka is a distributed event store and stream processing platform designed for high throughput (>1M events/sec), horizontal scalability, and low latency (<10ms) using sequential disk I/O and Zero-Copy networking.",
      "why_we_need_it": "Modern platforms generate billions of telemetry events, audit logs, and transaction streams daily. Kafka serves as the central nervous system connecting microservices and data pipelines.",
      "real_world_analogy": "A mega-highway with multiple parallel lanes (Partitions). Cars (Events) travel down specific lanes based on their license plate hash. Multiple buses (Consumer Group instances) drive on separate lanes simultaneously without colliding.",
      "how_it_works": "<p>1. <strong>Topics & Partitions:</strong> A Topic is sharded into multiple Partitions distributed across broker nodes. Partitions are the unit of parallelism.<br>2. <strong>Producers & Partitioning:</strong> Events with identical keys (`user_id`) hash to the SAME partition, guaranteeing strict per-key FIFO ordering.<br>3. <strong>Consumer Groups:</strong> Each partition in a topic is consumed by exactly ONE consumer instance within a consumer group.<br>4. <strong>High-Performance Secrets:</strong> Sequential Disk I/O (as fast as RAM), OS Page Cache, and Zero-Copy network transfer (`sendfile` system call transferring disk data directly to network socket without user-space buffer copies).<br>5. <strong>KRaft:</strong> Modern Kafka consensus protocol replacing external Zookeeper with built-in Raft quorum controllers.</p>",
      "conceptual_breakdown": [
        "<strong>Replication Factor (RF):</strong> Each partition has 1 Leader replica and $N-1$ In-Sync Replicas (ISR).",
        "<strong>`acks=all`:</strong> Producer waits for all ISR replicas to commit before acknowledging success.",
        "<strong>Consumer Rebalance:</strong> When a consumer joins or leaves, Kafka reassigns partition ownership across group members."
      ],
      "failure_scenarios": "<strong>Partition Skew & Hot Partitioning:</strong> If all producers send events with `null` keys or identical keys, 100% of traffic flows to Partition 0, overloading 1 broker while remaining partitions sit idle. <em>Mitigation:</em> Choose high-cardinality partition keys or use default round-robin sticky partitioner.",
      "common_mistakes": [
        {
          "mistake": "Adding more consumer instances than the total number of partitions in a Kafka topic.",
          "correction": "In Kafka, a single partition can only be consumed by 1 consumer per group. Excess consumers will sit completely idle."
        }
      ],
      "interview_questions": [
        {
          "question": "How does Kafka achieve millions of writes per second on standard mechanical hard drives?",
          "answer": "Kafka relies exclusively on Sequential Disk Append writes (avoiding random disk seek penalties), utilizes the Linux OS Page Cache heavily, batches network requests, and utilizes OS Zero-Copy (`sendfile`) to stream data directly from page cache to network sockets without CPU copying."
        }
      ]
    },
    {
      "id": "sqs-sns-and-cloud-messaging",
      "title": "AWS SQS, SNS & EventBridge: Fan-Out & Dead-Letter Queues",
      "definition": "AWS SNS is a managed serverless pub/sub topic service that fans out messages to multiple subscribers. AWS SQS is a distributed message queue service for decoupling worker jobs. SNS + SQS Fan-Out is a foundational cloud architecture pattern.",
      "why_we_need_it": "When a user places an order, multiple independent subsystems (Inventory, Payment, Shipping, Email) must execute tasks asynchronously without the checkout API making 4 separate HTTP calls.",
      "real_world_analogy": "A radio station broadcast (SNS): the DJ speaks once over the antenna. Five different people in five different rooms have their own cassette recorders (SQS Queues) recording the song to listen to later.",
      "how_it_works": "<p>1. <strong>SNS + SQS Fan-Out:</strong> Producer sends a single message to an SNS Topic. SNS immediately pushes copies to 4 distinct SQS queues (OrderQueue, EmailQueue, AnalyticsQueue, InventoryQueue).<br>2. <strong>Visibility Timeout (SQS):</strong> When a worker receives a message, SQS hides it from other workers for 30s. If the worker deletes the message within 30s, it is completed. If the worker crashes, the visibility timeout expires and the message becomes visible to other workers automatically.<br>3. <strong>Dead-Letter Queue (DLQ):</strong> If a message fails processing `maxReceiveCount = 3` times, SQS moves it to a DLQ for manual inspection.</p>",
      "conceptual_breakdown": [
        "<strong>Standard vs FIFO SQS:</strong> Standard provides nearly unlimited throughput with at-least-once delivery and best-effort ordering; FIFO guarantees strict ordering and exactly-once deduplication up to 3,000 msgs/sec.",
        "<strong>Long Polling:</strong> SQS `WaitTimeSeconds = 20` reduces API cost and latency by holding connections open until a message arrives."
      ],
      "failure_scenarios": "<strong>Visibility Timeout Exceeded on Slow Tasks:</strong> A worker takes 45 seconds to generate a PDF report with a 30s Visibility Timeout. SQS assumes the worker died and redelivers the message to a second worker, causing duplicate PDF processing. <em>Mitigation:</em> Extend the visibility timeout dynamically via `ChangeMessageVisibility` heartbeat calls.",
      "common_mistakes": [
        {
          "mistake": "Using short polling (`WaitTimeSeconds = 0`) resulting in millions of empty SQS API requests on AWS billing.",
          "correction": "Always configure SQS Long Polling (`WaitTimeSeconds = 20`)."
        }
      ],
      "interview_questions": [
        {
          "question": "How does the SNS-to-SQS Fan-Out pattern ensure fault isolation between microservices?",
          "answer": "Each subscriber microservice consumes from its own dedicated SQS queue. If the Email Service experiences an outage and stops consuming, its queue buffers messages safely without affecting or delaying the Payment, Inventory, or Shipping services."
        }
      ]
    }
  ]
}

modules = [mod_11, mod_12, mod_13, mod_14, mod_15]
for m in modules:
    filename = os.path.join(CONTENT_DIR, f"module_{m['module_id']}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print(f"Generated {filename} with {len(m['topics'])} topics")
