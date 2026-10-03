"""
Elaborate generator for Module 12: Database Scaling: Replication, Sharding & Partitioning
"""
import json
from pathlib import Path

m12 = {
  "module_id": "12",
  "module_title": "Database Scaling: Replication, Sharding & Partitioning",
  "description": "Master horizontal database scaling: Primary-Replica replication, handling replication lag, horizontal sharding strategies (hash, range, directory), consistent hashing, hot partition rebalancing, and distributed joins.",
  "topics": [
    {
      "id": "read-replicas-and-replication-lag",
      "title": "Primary-Replica Replication: Sync vs Async & Handling Replication Lag",
      "definition": "Database replication copies data from a primary database instance (which handles all write operations) to one or more read replicas (which handle read queries). Synchronous replication guarantees zero data loss by waiting for replicas to confirm writes, while Asynchronous replication maximizes write throughput at the cost of Replication Lag.",
      "why_we_need_it": "Most web applications exhibit a 90:10 or 95:5 read-to-write ratio. A single database server runs out of CPU capacity serving read queries long before write capacity is reached. Adding read replicas offloads read traffic, scales read throughput linearly, and provides high-availability failover nodes.",
      "real_world_analogy": "A daily newspaper: The editor-in-chief (Primary Database) writes and edits articles. The printing press produces 500,000 copies (Read Replicas) distributed across the city. Readers read the copies. If a reader buys a newspaper printed at 6:00 AM, they won't see breaking news that happened at 6:05 AM until the next edition arrives (Replication Lag).",
      "how_it_works": "<p>1. <strong>Asynchronous Replication Mechanics:</strong> Client sends `INSERT` to Primary. Primary writes to local WAL and commits immediately, returning success to the client. In the background, the Primary's replication sender thread streams WAL/binlog events across the network to Replicas. Replicas replay the log entries in their own storage engine. The time difference between the primary commit and replica replay is <strong>Replication Lag</strong> (typically 10ms-500ms, but can spike to minutes under heavy write load).</p><p>2. <strong>Synchronous Replication:</strong> The Primary does not return success to the client until at least one synchronous replica confirms that the log record has been flushed to its local disk. Guarantees <strong>RPO = 0 (Zero Data Loss)</strong> upon primary crash, but write latency is penalized by network round-trip time (RTT).</p><p>3. <strong>Semi-Synchronous Replication:</strong> A pragmatic middle ground: Primary waits for <em>one</em> replica to acknowledge receipt of the log record into memory, while other replicas replicate asynchronously.</p><p>4. <strong>Mitigating Replication Lag in Applications:</strong><br>&bull; <em>Read-Your-Own-Writes Consistency:</em> After a user updates their profile, route that user's subsequent read requests to the <strong>Primary</strong> for the next 5-10 seconds, while all other users read from replicas.<br>&bull; <em>Monotonic Reads:</em> Pin a client session to a specific replica (via sticky hash) to prevent time-travel anomalies where consecutive page refreshes hit replicas with different lag times.<br>&bull; <em>Replication Offset Tokens:</em> Primary returns a WAL LSN (Log Sequence Number) to the client. The client requests data from replicas with `LSN >= token`; if the replica hasn't caught up, it waits or routes to primary.</p>",
      "conceptual_breakdown": [
        "<strong>Replication Lag Causes:</strong> Long-running queries on replicas, network saturation between data centers, heavy bulk write transactions on the primary, single-threaded replica SQL replay.",
        "<strong>RPO (Recovery Point Objective):</strong> The maximum acceptable data loss measured in time. Async replication has RPO > 0; Sync replication achieves RPO = 0.",
        "<strong>RTO (Recovery Time Objective):</strong> The maximum acceptable downtime to promote a replica to primary and re-point application traffic (typically 10-30 seconds via automated orchestrators like Orchestrator / Patroni).",
        "<strong>Split-Brain Risk:</strong> If a network partition isolates the Primary, and a replica prematurely promotes itself, two nodes will accept writes simultaneously, corrupting data. Quorum-based fencing (Raft/Consul) is required."
      ],
      "arch_diagram": {
        "title": "Primary-Replica Replication Architecture & Read-Your-Own-Writes Router",
        "tiers": [
          {
            "label": "Application Routing Layer",
            "nodes": [
              {
                "name": "Database Proxy / Router",
                "type": "lb",
                "icon": "🔀",
                "what": "Smart SQL Router (ProxySQL / App Driver)",
                "why": "Routes writes to Primary; splits reads to Replicas",
                "when": "Every database query",
                "failure": "Detects replica lag and removes stale nodes"
              }
            ]
          },
          {
            "label": "Authoritative Primary Tier",
            "nodes": [
              {
                "name": "PostgreSQL Primary",
                "type": "database",
                "icon": "👑",
                "what": "Handles 100% of Writes",
                "why": "Single authoritative source for ACID commits",
                "when": "INSERT / UPDATE / DELETE",
                "failure": "Automatic failover via Patroni"
              }
            ]
          },
          {
            "label": "Scalable Read Replica Tier",
            "nodes": [
              {
                "name": "Read Replica 1 (AZ-1)",
                "type": "database",
                "icon": "📖",
                "what": "Handles 50% of Reads",
                "why": "Scales read throughput linearly",
                "when": "SELECT queries",
                "failure": "Traffic diverted to Replica 2"
              },
              {
                "name": "Read Replica 2 (AZ-2)",
                "type": "database",
                "icon": "📖",
                "what": "Handles 50% of Reads",
                "why": "Scales read throughput linearly",
                "when": "SELECT queries",
                "failure": "Traffic diverted to Replica 1"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Replication Modes Comparison Matrix",
        "columns": ["Mode", "Write Latency", "Data Loss on Primary Crash (RPO)", "Availability on Replica Failure", "Typical Use Case"],
        "rows": [
          ["Asynchronous", "Lowest (commits immediately)", "High (un-replicated transactions are lost)", "High (primary continues writing)", "Standard web applications, social media"],
          ["Synchronous", "Highest (waits for replica disk fsync)", "Zero (RPO = 0 guaranteed)", "Low (primary hangs if replica dies)", "High-stakes banking, stock exchanges"],
          ["Semi-Synchronous", "Medium (waits for replica memory ACK)", "Near-zero (lost only if both die simultaneously)", "High (falls back to async if replica times out)", "Modern high-reliability cloud databases"]
        ]
      },
      "tradeoffs": "<strong>Replicas solve read scalability, NOT write scalability.</strong> Every write must execute on the primary AND replay on every single replica. If your workload reaches 50,000 writes/sec, adding more read replicas makes performance WORSE because the primary must stream replication logs to more network destinations.",
      "failure_scenarios": "<strong>The Post-and-Refresh Disappearing Content Bug:</strong> A user posts a comment on an article. The write hits the Primary. The user's browser immediately refreshes the page, and the read request routes to a Read Replica that is 150ms behind. The user does not see their comment, panics, and submits the comment 5 times. <em>Mitigation:</em> Enforce <strong>Read-Your-Own-Writes</strong>: route reads for the submitting user to the Primary for 5 seconds after a mutation.",
      "common_mistakes": [
        {"mistake": "Adding read replicas to fix a write-heavy database bottleneck.", "correction": "Read replicas do not increase write capacity. To scale writes, you must implement Database Sharding or adopt a distributed multi-master engine."},
        {"mistake": "Failing to monitor replication lag in alerting systems.", "correction": "Alert on replication lag metrics (`pg_stat_replication.replay_lag` or `Seconds_Behind_Master`). When lag exceeds 5 seconds, temporarily take the replica out of the load balancing pool."}
      ],
      "interview_questions": [
        {"question": "How do you guarantee Read-Your-Own-Writes consistency in a system with asynchronous read replicas?", "answer": "1. <strong>Time-based routing:</strong> Track the timestamp of a user's last write. If $T_{\\text{current}} - T_{\\text{write}} < 5\\text{s}$, route that user's read queries directly to the Primary;<br>2. <strong>Replication Token (LSN tracking):</strong> On a write, the primary returns the Log Sequence Number (LSN). The client sends this token with read requests. The router only forwards the query to a replica if `replica.lsn >= token`; otherwise, it routes to primary;<br>3. <strong>Optimistic Client UI:</strong> Immediately update the client-side UI state in memory from the write response without waiting for a re-fetch from the database."},
        {"question": "What is the Split-Brain scenario during database primary failover and how is it prevented?", "answer": "<strong>Split-brain</strong> occurs when the primary temporarily becomes unresponsive (e.g. transient network blip). A health checker assumes the primary is dead and promotes a replica to be the new primary. When the old primary recovers, both nodes believe they are the authoritative primary and accept conflicting writes, permanently corrupting the data set. Prevention: <strong>STONITH ('Shoot The Other Node In The Head')</strong> or hardware fencing to forcibly power off the old primary, combined with distributed consensus (Raft/ZooKeeper/Consul) where a primary must hold a majority quorum lease to accept writes."}
      ]
    },
    {
      "id": "database-sharding-strategies",
      "title": "Horizontal Sharding: Range-based, Hash-based, Directory-based & Consistent Hashing",
      "definition": "Database Sharding is the architectural practice of horizontally partitioning a large database across multiple independent physical database instances (shards). Each shard holds a disjoint subset of data rows and shares no memory or disk (Shared-Nothing Architecture). Sharding strategies include Range-based, Hash-based, Directory-based, and Consistent Hashing.",
      "why_we_need_it": "When a table grows past 10-50TB or write throughput exceeds 50,000 transactions/second, vertical scaling hits physical hardware limits and replication cannot help. Sharding splits the dataset across 10, 50, or 500 servers, unlocking unlimited horizontal storage and write capacity.",
      "real_world_analogy": "A national library filing system: Instead of putting all 50 million citizen files in one massive room that collapses under its own weight, the government builds 26 regional buildings: Building A holds citizens whose last names start with A, Building B holds names starting with B (Range Sharding), or assigns files by the last digit of their national ID number (Hash Sharding).",
      "how_it_works": "<p>1. <strong>The Shard Key:</strong> The foundational architectural decision. The Shard Key is the attribute(s) present in every row that determines which physical shard stores that row (e.g., `user_id`, `tenant_id`, `country_code`).</p><p>2. <strong>Range-Based Sharding:</strong> Data is partitioned into contiguous ranges based on the shard key (e.g., `user_id` 1-1,000,000 on Shard 1; 1,000,001-2,000,000 on Shard 2). Excellent for range queries (`WHERE id BETWEEN 500 AND 600`), but creates severe write hotspots when IDs are auto-incrementing (100% of new writes hit the highest range shard).</p><p>3. <strong>Hash-Based Sharding:</strong> Computes a cryptographic hash of the shard key: $\\text{Shard} = \\text{Hash}(\\text{user\\_id}) \\pmod N$. Provides perfectly uniform data and write distribution across all $N$ shards. However, range queries cannot be localized and require querying all shards in parallel (Scatter-Gather).</p><p>4. <strong>Directory-Based (Lookup) Sharding:</strong> A centralized lookup service or mapping table maps Shard Keys to physical Shard IDs (e.g., `Tenant_123 -> Shard_4`). Provides total flexibility to move individual tenants between shards without mathematical rehashing, but introduces a single point of failure and extra lookup latency.</p><p>5. <strong>Consistent Hashing:</strong> Maps shards and shard keys onto a 360-degree ring. When adding new shards to the cluster, only $1/N$ of the data needs to be migrated, minimizing rebalancing downtime.</p>",
      "conceptual_breakdown": [
        "<strong>Shared-Nothing Architecture:</strong> Each shard runs its own CPU, RAM, and storage independently. There is no shared storage or SAN.",
        "<strong>The Shard Key Immutability Rule:</strong> The shard key of a row should NEVER change. If a user changes their `country_code`, and `country_code` is the shard key, the database must delete the row from Shard US and insert it into Shard EU across a distributed transaction.",
        "<strong>Cardinality Requirement:</strong> The shard key must have high cardinality (millions of distinct values). Sharding by `gender` or `status` produces only 2-3 massive shards that cannot scale.",
        "<strong>Scatter-Gather Queries:</strong> Any query that does NOT include the Shard Key in its `WHERE` clause must be broadcast to EVERY shard in the cluster, multiplying latency and load."
      ],
      "arch_diagram": {
        "title": "Horizontal Sharding Routing Topology (Hash-Based Shard Router)",
        "tiers": [
          {
            "label": "Client & Router Tier",
            "nodes": [
              {
                "name": "Shard Router / Vitess",
                "type": "lb",
                "icon": "🧭",
                "what": "Hash(user_id) mod 4",
                "why": "Determines target shard in O(1) time",
                "when": "Every incoming SQL query",
                "failure": "Stateless router failover"
              }
            ]
          },
          {
            "label": "Sharded Database Cluster (Shared-Nothing)",
            "nodes": [
              {
                "name": "Shard 1 (Hash 0)",
                "type": "database",
                "icon": "🐘",
                "what": "Postgres Node (25% of users)",
                "why": "Owns partition hash range 0",
                "when": "user_id hashes to 0",
                "failure": "Dedicated replica failover"
              },
              {
                "name": "Shard 2 (Hash 1)",
                "type": "database",
                "icon": "🐘",
                "what": "Postgres Node (25% of users)",
                "why": "Owns partition hash range 1",
                "when": "user_id hashes to 1",
                "failure": "Dedicated replica failover"
              },
              {
                "name": "Shard 3 (Hash 2)",
                "type": "database",
                "icon": "🐘",
                "what": "Postgres Node (25% of users)",
                "why": "Owns partition hash range 2",
                "when": "user_id hashes to 2",
                "failure": "Dedicated replica failover"
              },
              {
                "name": "Shard 4 (Hash 3)",
                "type": "database",
                "icon": "🐘",
                "what": "Postgres Node (25% of users)",
                "why": "Owns partition hash range 3",
                "when": "user_id hashes to 3",
                "failure": "Dedicated replica failover"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Sharding Strategies Comparison Matrix",
        "columns": ["Strategy", "Data Distribution", "Range Query Efficiency", "Resharding Complexity", "Hotspot Vulnerability"],
        "rows": [
          ["Hash-Based", "Uniform / Evenly distributed", "Poor (Scatter-Gather across all shards)", "High (changing N moves almost all data)", "Low (randomized hashing breaks up clusters)"],
          ["Range-Based", "Can be skewed", "Excellent (Targeted to 1 or 2 shards)", "Low (split range boundaries)", "Severe (auto-incrementing IDs burn latest shard)"],
          ["Directory-Based", "Completely configurable", "Moderate (consults directory table)", "Zero (update directory entry)", "Low (can isolate hot tenants to dedicated shards)"],
          ["Consistent Hashing", "Uniform via Virtual Nodes", "Poor (keys distributed along ring)", "Minimal (only K/N keys rebalance)", "Low (Vnodes balance load across physical nodes)"]
        ]
      },
      "tradeoffs": "<strong>Sharding is the ultimate scalability weapon, but introduces immense architectural pain:</strong> Cross-shard joins are impossible without scatter-gather, cross-shard transactions require complex two-phase commit protocols, schema migrations must run across 100 databases in parallel, and foreign keys cannot span shards.",
      "failure_scenarios": "<strong>The Monotonic ID Range Shard Meltdown:</strong> A company shards orders by date range: Shard 1 = January, Shard 2 = February, Shard 3 = March. In March, 100% of the company's writes and 95% of active reads hit Shard 3. Shard 3 crashes under load while Shards 1 and 2 sit at 1% CPU utilization. <em>Mitigation:</em> Shard by `Hash(order_id)` or `Hash(user_id)` to distribute writes uniformly across all nodes regardless of time.",
      "common_mistakes": [
        {"mistake": "Sharding prematurely when proper indexing, read replicas, and caching would solve the problem.", "correction": "Sharding introduces massive operational complexity. Exhaust caching, vertical scaling, read replicas, and partitioning first."},
        {"mistake": "Selecting a shard key that does not appear in your most critical API queries.", "correction": "If 90% of your queries filter by `user_id`, make `user_id` the shard key. If you shard by `created_at`, every single user profile lookup becomes an expensive broadcast query."}
      ],
      "interview_questions": [
        {"question": "How do you pick an effective Shard Key in a system design interview?", "answer": "Evaluate candidate keys against 4 criteria: 1. <strong>High Cardinality:</strong> Millions of unique values (e.g., `user_id`, NOT `status`); 2. <strong>Uniform Distribution:</strong> Evenly distributes data volume and write QPS across shards (avoid celebrity keys); 3. <strong>Query Alignment:</strong> Must be present in the `WHERE` clause of >85% of critical read and write queries to avoid Scatter-Gather; 4. <strong>Immutability:</strong> The value must never change after creation."},
        {"question": "What is Scatter-Gather and why is it dangerous at scale?", "answer": "<strong>Scatter-Gather</strong> occurs when a query does not include the shard key. The shard router must 'scatter' the query by broadcasting it to all $N$ shards in parallel, wait for every shard to respond, and 'gather' (merge/sort) the results in memory. It is dangerous because: 1. A single slow shard delays the entire response (tail latency / p99 explosion); 2. It multiplies cluster CPU and connection load by $N$ for a single user query."}
      ]
    },
    {
      "id": "hot-partitions-and-rebalancing",
      "title": "Hot Partitions (Celebrity Problem), Resharding & Zero-Downtime Data Migration",
      "definition": "A Hot Partition occurs when a single shard receives an overwhelming disproportion of read or write traffic (the Celebrity / Influencer Problem). Resharding and Zero-Downtime Migration are the operational techniques used to split shards, rebalance keys across new cluster nodes, and migrate live datasets without taking application traffic offline.",
      "why_we_need_it": "In a social network sharded by `user_id`, an average user has 200 followers and receives 1 read/sec. A celebrity (e.g. Elon Musk or Cristiano Ronaldo) has 150 million followers and receives 100,000 reads/sec. The single physical database shard hosting the celebrity's account will be crushed by traffic, even if the other 99 shards are completely idle.",
      "real_world_analogy": "A highway toll plaza: 9 lanes have normal sedans passing through at 1 car per minute. Lane 5 suddenly has 500 oversized semi-trucks trying to squeeze through at the exact same second. Lane 5 experiences a 2-hour traffic jam while the other 8 lanes sit empty.",
      "how_it_works": "<p>1. <strong>Salting the Shard Key:</strong> For high-write hot entities, append a randomized or bounded numeric salt to the shard key: $\\text{Key} = \\text{celebrity\\_id} + \\text{'_'} + \\text{random}(0, 9)$. This scatters the celebrity's data across 10 different physical shards, dividing write load by 10. Reads must query all 10 salted shards in parallel and merge results.</p><p>2. <strong>Dedicated VIP Sharding:</strong> Isolate extreme outlier accounts onto dedicated physical database instances with custom caching layers, keeping them completely separated from standard multi-tenant shards.</p><p>3. <strong>Zero-Downtime Resharding & Migration Pipeline (The 4-Step Playbook):</strong><br>&bull; <em>Phase 1 (Dual Writing):</em> Application is updated to write to BOTH the old database and the new database simultaneously. Reads continue querying the old database exclusively.<br>&bull; <em>Phase 2 (Historical Backfill):</em> A background batch worker copies all historical data from the old DB to the new DB, taking care not to overwrite newer dual-written records.<br>&bull; <em>Phase 3 (Continuous Verification / CDC):</em> Compare data between old and new stores using Change Data Capture (Debezium/Kafka) or a shadow validator service until parity reaches 100.00%.<br>&bull; <em>Phase 4 (Read Switch & Decommission):</em> Shift 1% of read traffic to the new database (Canary), gradually ramp to 100%, and finally disable writes to the old database.</p>",
      "conceptual_breakdown": [
        "<strong>Celebrity Problem (Fan-out on Read vs Write):</strong> For normal users, fan-out on write (pushing to follower timeline caches) is fast. For celebrities with 50M followers, fan-out on write crashes the queue. Systems switch to a Hybrid Model: normal users use fan-out on write; celebrities use fan-out on read (dynamically merged at query time).",
        "<strong>Key Salting Trade-off:</strong> Divides write load evenly, but forces reads to query multiple shards and aggregate results in memory.",
        "<strong>Dual-Write Idempotency:</strong> During migration, the new database must use idempotent upserts (`ON CONFLICT DO UPDATE`) to handle duplicate events from simultaneous backfill and live writes.",
        "<strong>Shadow Reads:</strong> In Phase 3, send real production queries to both databases, return the old DB response to the user, and asynchronously compare latency and results in background metrics."
      ],
      "arch_diagram": {
        "title": "Zero-Downtime Database Migration Pipeline (Dual-Write + CDC Verification)",
        "tiers": [
          {
            "label": "Application Layer",
            "nodes": [
              {
                "name": "App Service (Dual Write)",
                "type": "service",
                "icon": "✍️",
                "what": "Writes to Old DB + New DB",
                "why": "Maintains live synchronization during migration",
                "when": "Phase 1 - 4",
                "failure": "Logs failure to migration queue"
              }
            ]
          },
          {
            "label": "Database Tiers (Old vs New)",
            "nodes": [
              {
                "name": "Old Sharded Cluster",
                "type": "database",
                "icon": "🏛️",
                "what": "Current Production Store (4 Shards)",
                "why": "Serves 100% of live user reads",
                "when": "Active read path",
                "failure": "Standard primary failover"
              },
              {
                "name": "New Sharded Cluster",
                "type": "database",
                "icon": "🚀",
                "what": "New Target Store (16 Shards)",
                "why": "Receives dual-writes + backfill data",
                "when": "Shadow verification",
                "failure": "Does not impact live users"
              }
            ]
          },
          {
            "label": "Backfill & Reconciliation Engine",
            "nodes": [
              {
                "name": "CDC Reconciler (Debezium + Kafka)",
                "type": "queue",
                "icon": "🔄",
                "what": "Validates checksums row-by-row",
                "why": "Guarantees 100.0% data parity before cutover",
                "when": "Continuous background diff",
                "failure": "Flags discrepancies for auto-repair"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Migration Strategies Comparison Matrix",
        "columns": ["Strategy", "Downtime Required", "Rollback Safety", "Implementation Effort", "Risk Level"],
        "rows": [
          ["Maintenance Window (Cold Cutover)", "High (Hours of maintenance downtime)", "Easy (revert DNS to old DB)", "Lowest", "High (unforeseen bugs under live traffic)"],
          ["Dual-Write + Backfill", "Zero downtime", "Instant (reads stay on old DB until verified)", "Moderate-to-high", "Lowest (battle-tested industry standard)"],
          ["Logical Replication / CDC Cutover", "Near-zero (<30s connection pause)", "Moderate (reverse replication stream required)", "Moderate", "Low (engine-native replication minimizes app code changes)"]
        ]
      },
      "tradeoffs": "<strong>Dual-Write Migration:</strong> Guarantees zero downtime and zero user impact with instant rollback capability, but requires maintaining dual-write application logic, running two complete database infrastructures simultaneously for weeks (double cost), and building a custom reconciliation checker.",
      "failure_scenarios": "<strong>The Celebrity Live-Stream Crash:</strong> A live-streaming platform shards by `stream_id`. An influencer with 5 million concurrent viewers goes live. The single shard hosting that `stream_id` receives 400,000 chat messages and viewer heartbeats per second, running out of socket buffers and crashing. <em>Mitigation:</em> Salt the chat stream into 20 sub-rooms (`stream_id:room_1`, `stream_id:room_2`), and use an in-memory Redis cluster with Read Replicas to fan-out chat messages.",
      "common_mistakes": [
        {"mistake": "Attempting a 'Big Bang' instant cutover for a 10TB production database over a weekend.", "correction": "Big Bang cutovers almost always fail due to unforeseen query plan changes or latency regressions. Always use Dual-Write with canary traffic shifting."},
        {"mistake": "Overwriting newer live writes with older historical backfill records during migration.", "correction": "Use timestamps or version checks on the target database so historical backfill jobs never overwrite newer live transactions."}
      ],
      "interview_questions": [
        {"question": "How do you solve the Celebrity / Hot Key problem in a sharded database?", "answer": "1. <strong>Key Salting:</strong> Append a random suffix (0 to $M$) to the partition key on write to distribute data across $M$ shards. Reads query all $M$ shards and merge results;<br>2. <strong>Aggressive Multi-Tier Caching:</strong> Cache the celebrity's profile and public posts in local in-memory L1 cache (Caffeine) and distributed Redis L2 to intercept 99.9% of read traffic before it touches the database;<br>3. <strong>Hybrid Fan-out Architecture:</strong> For ordinary users, use fan-out on write (push). For celebrities, use fan-out on read (pull) to prevent a single post from triggering 50 million database write events."},
        {"question": "Walk me through the zero-downtime database migration process.", "answer": "The standard 4-phase process: 1. <strong>Dual Writing:</strong> Modify application code to write to both Old and New databases (with errors on New logged but non-blocking); 2. <strong>Historical Backfill:</strong> Run a background script copying past records from Old to New, using idempotent upserts; 3. <strong>CDC Verification:</strong> Stream change data capture events and run automated checksum diffing to verify 100% parity; 4. <strong>Canary Read Shift:</strong> Route 1% of reads to New, monitor p99 latency and error rates, gradually ramp to 100%, and finally stop writes to the Old database."}
      ]
    },
    {
      "id": "cross-shard-queries-and-distributed-joins",
      "title": "Solving Cross-Shard Queries, Scatter-Gather & Distributed Joins",
      "definition": "Cross-Shard Queries occur when a database request requires data stored across multiple physically separate shards. Distributed Joins occur when a relational join (`JOIN`) must merge rows residing on different machines. Solving these challenges requires architectural techniques including Scatter-Gather aggregation, Global Secondary Indexing, Two-Phase Commit (2PC), and Application-Side Joins.",
      "why_we_need_it": "In a sharded architecture where users are on Shard 1 and orders are on Shard 2, the database engine cannot execute a single SQL `JOIN` because the tables exist on different physical servers. Understanding how to handle cross-shard queries is the primary hurdle of distributed database design.",
      "real_world_analogy": "Two different police stations in different cities: Station A has criminal records; Station B has vehicle registrations. A detective cannot simply open a drawer and find both. The detective must call Station A for the criminal name, call Station B for the car license plate, and cross-reference the two pieces of paper on their own desk (Application-Side Join).",
      "how_it_works": "<p>1. <strong>Scatter-Gather Engine:</strong> When a query filters by a non-shard key (e.g. `SELECT * FROM orders WHERE status = 'SHIPPED'` on an order database sharded by `user_id`):<br>&bull; Step 1: The coordinator/router broadcasts the query to all $N$ shards simultaneously.<br>&bull; Step 2: Each shard executes the query locally using its local B-Tree indexes.<br>&bull; Step 3: Shards return matching row sets to the coordinator.<br>&bull; Step 4: The coordinator merges, sorts, and applies `LIMIT / OFFSET` pagination in memory before returning results to the client.</p><p>2. <strong>Global Secondary Indexes (GSI):</strong> To avoid scatter-gather, maintain a separate dedicated index table sharded by the secondary attribute (e.g., a table sharded by `order_id` that maps `order_id -> user_id`). Queries look up the GSI first in O(1) time to find the responsible shard, and then query that single shard directly.</p><p>3. <strong>Co-Location (Entity Groups):</strong> Ensure related tables share the exact same Shard Key and land on the exact same physical database instance. For example, shard both `users` and `orders` by `user_id`. When querying `orders JOIN users WHERE user_id = 42`, the join executes 100% locally within a single database instance with full relational ACID speed!</p><p>4. <strong>Distributed Joins (Broadcast vs Hash Join):</strong><br>&bull; <em>Broadcast Join:</em> If joining a huge sharded table with a small lookup table (e.g. 50 US States), replicate the small table to *every single shard* so joins execute locally.<br>&bull; <em>Application-Side Join:</em> Service queries Service A for user records, extracts IDs, queries Service B with `WHERE id IN (...)`, and joins objects in memory.</p>",
      "conceptual_breakdown": [
        "<strong>Co-Location / Table Colocation:</strong> The single most powerful design pattern in sharding. Placing parent and child rows on the same machine preserves local relational joins.",
        "<strong>Pagination Flaw in Scatter-Gather:</strong> Running `ORDER BY created_at LIMIT 10 OFFSET 1000` across 10 shards requires each shard to return 1,010 rows to the coordinator (10,100 rows transferred across network) just to discard 1,000 rows. Use Cursor-based / Keyset pagination instead.",
        "<strong>Distributed Deadlocks in Multi-Shard Writes:</strong> If a cross-shard transaction acquires locks on Shard A then B, and another acquires locks on B then A, a distributed deadlock occurs that local database engines cannot detect.",
        "<strong>Two-Phase Commit (2PC) Overhead:</strong> Cross-shard ACID transactions require 2PC (Prepare + Commit). 2PC is slow, blocking, and scales poorly past 5 shards."
      ],
      "arch_diagram": {
        "title": "Cross-Shard Query Resolution (Global Secondary Index vs Scatter-Gather)",
        "tiers": [
          {
            "label": "Incoming Non-Shard-Key Query",
            "nodes": [
              {
                "name": "Query: WHERE order_id = 'ORD-9842'",
                "type": "client",
                "icon": "🔍",
                "what": "Database sharded by user_id",
                "why": "Query does not contain shard key!",
                "when": "Client request",
                "failure": "Needs routing resolution"
              }
            ]
          },
          {
            "label": "Global Secondary Index Lookup Tier",
            "nodes": [
              {
                "name": "GSI Table (order_id -> user_id)",
                "type": "cache",
                "icon": "🗂️",
                "what": "Maps ORD-9842 -> user_id: 104",
                "why": "Identifies responsible shard in 1ms",
                "when": "Before data query",
                "failure": "Falls back to scatter-gather if GSI fails"
              }
            ]
          },
          {
            "label": "Targeted Shard Execution",
            "nodes": [
              {
                "name": "Target Shard 2 (Holds user_id: 104)",
                "type": "database",
                "icon": "🎯",
                "what": "Single Shard Point Lookup",
                "why": "Executes locally with B-Tree speed; ZERO broadcast!",
                "when": "Routed by user_id",
                "failure": "Standard node failover"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Cross-Shard Resolution Patterns Comparison",
        "columns": ["Pattern", "Network Overhead", "Latency", "Data Freshness", "Implementation Cost"],
        "rows": [
          ["Scatter-Gather Broadcast", "High (Broadcasts to all N shards)", "High (bounded by slowest shard p99)", "Strictly fresh", "Low (handled in routing layer)"],
          ["Global Secondary Index (GSI)", "Low (1 lookup + 1 point read)", "Low (single-digit ms)", "Eventually consistent (async index sync)", "Medium (maintain secondary index table)"],
          ["Table Co-Location", "Zero (Executes entirely on 1 machine)", "Fastest (Sub-millisecond local join)", "Strictly consistent (ACID)", "Requires designing schema around 1 root key"],
          ["Replicated Lookup Tables", "Zero on reads (replicated everywhere)", "Fastest for dimension joins", "Eventual (slow on table updates)", "Low (ideal for country codes, categories)"]
        ]
      },
      "tradeoffs": "<strong>Table Co-Location:</strong> Provides full relational joins and local ACID transactions without network hops, but limits cross-entity queries and forces all related data for an entity onto a single physical server.",
      "failure_scenarios": "<strong>The Deep Pagination Scatter-Gather Death Spiral:</strong> A user queries page 500 of an e-commerce order history: `SELECT * FROM orders WHERE status = 'PENDING' ORDER BY date DESC LIMIT 20 OFFSET 10000`. The coordinator broadcasts this to 50 shards. Each of the 50 shards scans and sorts 10,020 rows, transmitting 501,000 rows across the internal network to the coordinator. The coordinator runs out of memory sorting 500,000 rows and crashes with OOM. <em>Mitigation:</em> Forbid deep `OFFSET` pagination on distributed queries. Enforce <strong>Keyset / Cursor Pagination</strong>: `WHERE (date, id) < (:last_date, :last_id) LIMIT 20`.",
      "common_mistakes": [
        {"mistake": "Attempting to execute distributed transactions across 20 shards using Two-Phase Commit (2PC) under high throughput.", "correction": "2PC is blocking and fragile. Use the asynchronous Saga Pattern with compensating transactions instead."},
        {"mistake": "Using `ORDER BY` and `LIMIT` without an indexed tie-breaking column across sharded datasets.", "correction": "Always include a unique primary key in the sort order (`ORDER BY created_at DESC, id DESC`) to ensure deterministic pagination across multiple shards."}
      ],
      "interview_questions": [
        {"question": "How do you perform a JOIN between two tables that are sharded across different physical database nodes?", "answer": "1. <strong>Table Co-Location (Best):</strong> Shard both tables using the same shard key (e.g. `customer_id`). All matching rows reside on the exact same physical instance, allowing standard local SQL `JOIN`s;<br>2. <strong>Broadcast Join:</strong> If one table is a small static dimension table (e.g., `tax_rates`), replicate that table entirely onto every shard;<br>3. <strong>Application-Side Join:</strong> Query Service A for IDs, and query Service B with `WHERE id IN (...)`, merging results in application memory;<br>4. <strong>Denormalization / CQRS:</strong> Pre-join the data using asynchronous event pipelines and store read-optimized documents in Elasticsearch or MongoDB."},
        {"question": "What is the difference between a Local Secondary Index (LSI) and a Global Secondary Index (GSI)?", "answer": "A <strong>Local Secondary Index (LSI)</strong> is scoped to a single partition: it is partitioned on the exact same partition key as the table, indexing only rows within that specific shard (fast to update, but queries without the partition key require scatter-gather). A <strong>Global Secondary Index (GSI)</strong> is partitioned on an entirely different column (e.g., table partitioned by `user_id`, GSI partitioned by `email`). GSIs allow direct point lookups on secondary attributes across the entire cluster, but require asynchronous cross-shard replication to stay up-to-date."}
      ]
    }
  ]
}

with open(Path('content/hld/module_12.json'), 'w', encoding='utf-8') as f:
    json.dump(m12, f, ensure_ascii=False, indent=2)
print("Module 12 written successfully!")
