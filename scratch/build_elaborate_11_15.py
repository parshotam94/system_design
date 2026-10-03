"""
Elaborate generator for Modules 11 to 15.
Matches exact topics from app/data/hld_roadmap.json
"""
import json
from pathlib import Path

HLD_DIR = Path('content/hld')
HLD_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# MODULE 11: NoSQL Databases: Key-Value, Document, Wide-Column, Graph
# ==========================================
m11 = {
  "module_id": "11",
  "module_title": "NoSQL Databases: Key-Value, Document, Wide-Column, Graph",
  "description": "Master the 4 NoSQL architectures: Document stores (MongoDB), Wide-Column (Cassandra/ScyllaDB), Key-Value (DynamoDB), and Graph databases (Neo4j), plus the decision matrix for SQL vs NoSQL.",
  "topics": [
    {
      "id": "nosql-categories-and-internals",
      "title": "The 4 NoSQL Engines: Key-Value, Document, Wide-Column & Graph",
      "definition": "NoSQL encompasses four distinct non-relational database architectures designed for horizontal scalability, unstructured/semi-structured schemas, and specialized access patterns: Key-Value stores, Document databases, Wide-Column stores, and Graph databases.",
      "why_we_need_it": "Relational databases enforce strict schemas and relational joins that make horizontal scaling past 50,000 writes/second extremely difficult. Understanding the 4 NoSQL engines allows architects to choose storage engines aligned with data shapes and query patterns.",
      "real_world_analogy": "Vehicle categorization: Key-Value is a high-speed motorcycle (fast, nimble, carries a single backpack); Document is an SUV with flexible cargo space (carries nested gear); Wide-Column is a massive freight train with infinite flatcars (carries billions of identical crates across continents); Graph is an airline flight route map (navigates complex interconnected destinations).",
      "how_it_works": "<p>1. <strong>Key-Value (Redis, DynamoDB):</strong> Simplest model. Maps a unique partition key to an opaque binary/JSON blob. Provides O(1) reads and writes by hashing keys directly to server partition slots. Ideal for user sessions, shopping carts, and caching.</p><p>2. <strong>Document (MongoDB, Couchbase):</strong> Stores self-describing, hierarchical documents (JSON/BSON). Supports secondary indexes on nested fields (e.g. `addresses.city`), dynamic schemas, and aggregation pipelines. Ideal for catalogs, user profiles, and content management systems.</p><p>3. <strong>Wide-Column (Cassandra, ScyllaDB, HBase):</strong> Two-dimensional sorted map using a composite key: `(Partition Key, Clustering Columns)`. Data is written sequentially using LSM-Trees and SSTables. Delivers linear horizontal write scalability across dozens of nodes. Ideal for time-series, telemetry, and activity feeds.</p><p>4. <strong>Graph (Neo4j, AWS Neptune):</strong> Models entities as Nodes and relationships as directed, labeled Edges with properties. Implements <em>Index-Free Adjacency</em>: each node holds direct memory pointers to adjacent nodes, executing multi-hop traversals in O(1) time without SQL joins. Ideal for social networks, fraud rings, and recommendation knowledge graphs.</p>",
      "conceptual_breakdown": [
        "<strong>Index-Free Adjacency:</strong> In Neo4j, traversing from friend to friend follows direct memory pointers rather than computing expensive cross-table B-Tree lookups.",
        "<strong>LSM-Tree Storage Engine:</strong> Cassandra and RocksDB use Log-Structured Merge-Trees, converting random disk writes into high-speed sequential appends.",
        "<strong>Tunable Consistency:</strong> Cassandra and DynamoDB allow tuning consistency per query: ONE, QUORUM, or ALL.",
        "<strong>Denormalization Requirement:</strong> NoSQL generally lacks cross-partition joins. Data must be intentionally denormalized and duplicated to satisfy specific read access patterns."
      ],
      "arch_diagram": {
        "title": "The 4 NoSQL Engine Architecture Taxonomy",
        "tiers": [
          {
            "label": "Access Pattern Layer",
            "nodes": [
              {
                "name": "Key-Value Client",
                "type": "client",
                "icon": "🔑",
                "what": "GET /user_session:102",
                "why": "O(1) direct hash lookup",
                "when": "Session token validation",
                "failure": "Cache miss fallback"
              },
              {
                "name": "Graph Traversal Client",
                "type": "client",
                "icon": "🕸️",
                "what": "MATCH (u)-[:FRIENDS]->(f)",
                "why": "Pointer-hopping relationship traversal",
                "when": "Friend-of-friend recommendation",
                "failure": "Depth limit bounding"
              }
            ]
          },
          {
            "label": "Engine Classification",
            "nodes": [
              {
                "name": "Document Store (MongoDB)",
                "type": "database",
                "icon": "🍃",
                "what": "BSON Hierarchical Trees",
                "why": "Nested document indexing",
                "when": "Product catalog queries",
                "failure": "Replica set election"
              },
              {
                "name": "Wide-Column Store (Cassandra)",
                "type": "database",
                "icon": "📊",
                "what": "SSTable Partitioned Log",
                "why": "100k+ writes/sec linear scale",
                "when": "Sensor telemetry / chat history",
                "failure": "Peer gossip node repair"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "The 4 NoSQL Engine Families Comparison",
        "columns": ["Family", "Primary Engines", "Data Model", "Strengths", "Weaknesses"],
        "rows": [
          ["Key-Value", "Redis, DynamoDB", "Key -> Opaque Blob", "Blazing sub-millisecond O(1) latency", "Cannot query by value attributes"],
          ["Document", "MongoDB, Couchbase", "JSON / BSON Hierarchies", "Rich secondary indexing, schema agility", "Higher memory usage, lookup joins are slow"],
          ["Wide-Column", "Cassandra, ScyllaDB", "Partition Key + Clustering Columns", "Unbounded horizontal write throughput", "No ad-hoc queries; schema tightly coupled to queries"],
          ["Graph", "Neo4j, Amazon Neptune", "Nodes, Edges, Properties", "Blazing multi-hop relationship traversals", "Hard to shard horizontally across multiple machines"]
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> NoSQL delivers immense horizontal scale and schema flexibility, but sacrifices declarative ad-hoc SQL joins, centralized data normalization, and standard multi-table ACID transactions.",
      "failure_scenarios": "<strong>The Relational Query on Cassandra Crash:</strong> A developer attempts to query Cassandra with an un-indexed column filter using `ALLOW FILTERING`. The coordinator node broadcasts full-table scan requests to every single node in a 40-node cluster, causing CPU spikes, timeouts, and cascading node dropouts. <em>Mitigation:</em> Model tables strictly around known queries; never use `ALLOW FILTERING` in production.",
      "common_mistakes": [
        {"mistake": "Treating MongoDB like a relational database with 15 normalized collections and `$lookup` joins.", "correction": "Embrace document embedding. If child data is accessed together with parent data, embed it directly into the parent document."},
        {"mistake": "Using a Graph Database to store flat time-series sensor data.", "correction": "Graph databases are optimized for deep relationship traversals. For time-series metrics, use Wide-Column stores or TimescaleDB."}
      ],
      "interview_questions": [
        {"question": "How does Index-Free Adjacency in Graph Databases outperform SQL self-joins for social networks?", "answer": "In an RDBMS, finding friends-of-friends requires joining a 100-million row `friendships` table to itself, scanning B-Trees in O(log N) per hop. In a Graph DB with <strong>Index-Free Adjacency</strong>, each node stores direct memory pointers to its adjacent neighbor nodes. Traversing a relationship is a simple pointer dereference (O(1)), meaning query time depends only on the number of friends visited, not the total size of the global graph."},
        {"question": "When would you choose DynamoDB over MongoDB?", "answer": "Choose <strong>DynamoDB</strong> when you need fully managed, zero-maintenance serverless scalability with predictable single-digit millisecond latency at any throughput, and your access patterns are well-defined by partition keys. Choose <strong>MongoDB</strong> when you require complex nested ad-hoc queries, multi-field secondary indexes, aggregation pipelines, or geographic geospatial queries."}
      ]
    },
    {
      "id": "mongodb-and-document-stores",
      "title": "Document Stores: MongoDB BSON, Indexing & Embedding vs Referencing",
      "definition": "Document databases store semi-structured data as BSON (Binary JSON) documents organized into collections. They allow developers to model complex hierarchical data using either Embedding (nesting child objects directly) or Referencing (storing document IDs and joining via $lookup).",
      "why_we_need_it": "Relational normalization splits a single customer profile into 6 separate tables (Users, Addresses, Phones, Preferences, Roles, Badges), requiring a 6-way SQL join on every page load. Document stores save the entire entity as a single atomic BSON document, retrieving it in a single disk read.",
      "real_world_analogy": "A physical patient medical folder: Embedding is clipping the lab results, prescriptions, and allergy warnings directly inside the patient's single paper folder. Referencing is putting a library index card in the folder that says 'See Room 402, Cabinet B for Lab Results'.",
      "how_it_works": "<p>1. <strong>BSON Serialization:</strong> MongoDB stores data in BSON, a binary encoding format supporting rich data types not present in standard JSON (int32, int64, Date, Decimal128, Binary/UUID). BSON documents have a hard size limit of 16MB.</p><p>2. <strong>Embedding vs Referencing Decisions:</strong><br>&bull; <em>Embed When:</em> 'Contains' relationships (1:1 or 1:Few bounded, e.g., User has 2 addresses); child data does not exist independently; data is always read together; high read performance is needed.<br>&bull; <em>Reference When:</em> 1:Many unbounded (e.g., User has 50,000 tweets); Many-to-Many relationships; child data is updated frequently and independently; embedding would exceed the 16MB document size limit.</p><p>3. <strong>WiredTiger Storage Engine:</strong> Uses B-Tree indexes for fast lookups. Writes append to a journaling log for durability. Checkpoints flush dirty memory pages to disk every 60 seconds.</p><p>4. <strong>Replication & Sharding:</strong> Replica sets consist of 1 Primary and multiple Secondaries with Raft-like automatic failover. Sharding distributes collections across shards using a <em>Shard Key</em> via range-based or hash-based chunk routing.</p>",
      "conceptual_breakdown": [
        "<strong>16MB Document Limit:</strong> MongoDB enforces a 16MB maximum document size to prevent memory bloat and network serialization latency.",
        "<strong>Unbounded Array Anti-Pattern:</strong> Embedding an array that grows infinitely (e.g. `comments: []` on a viral post) causes documents to continuously move on disk and eventually crash when hitting 16MB.",
        "<strong>Write Concern (w: 'majority'):</strong> Ensures writes are acknowledged only after being replicated to a majority of replica set members, preventing rollbacks on primary crash.",
        "<strong>Read Concern ('majority' vs 'local'):</strong> Controls isolation level. 'majority' ensures clients only read data that cannot be rolled back by an ungraceful failover."
      ],
      "arch_diagram": {
        "title": "MongoDB Sharded Cluster Architecture (Mongos Router + Shards)",
        "tiers": [
          {
            "label": "Routing & Client Layer",
            "nodes": [
              {
                "name": "Mongos Query Router",
                "type": "lb",
                "icon": "🧭",
                "what": "Stateless Query Dispatcher",
                "why": "Routes reads/writes to correct shard based on shard key",
                "when": "Client queries",
                "failure": "Multiple redundant mongos instances"
              }
            ]
          },
          {
            "label": "Cluster Metadata Tier",
            "nodes": [
              {
                "name": "Config Server Replica Set",
                "type": "database",
                "icon": "⚙️",
                "what": "Stores Chunk-to-Shard Mapping",
                "why": "Authoritative routing table for cluster",
                "when": "Mongos startup & chunk split",
                "failure": "Raft-like election"
              }
            ]
          },
          {
            "label": "Data Shards (Replica Sets)",
            "nodes": [
              {
                "name": "Shard A (Primary + 2 Sec)",
                "type": "database",
                "icon": "🍃",
                "what": "Chunks for Shard Key range [0 - 1000]",
                "why": "Stores subset of collection data",
                "when": "Routed by mongos",
                "failure": "Secondary auto-promotes to Primary"
              },
              {
                "name": "Shard B (Primary + 2 Sec)",
                "type": "database",
                "icon": "🍃",
                "what": "Chunks for Shard Key range [1001 - 2000]",
                "why": "Stores subset of collection data",
                "when": "Routed by mongos",
                "failure": "Secondary auto-promotes to Primary"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Embedding vs Referencing in Document Stores",
        "columns": ["Criteria", "Embedding (Nested Objects)", "Referencing ($lookup / Manual Join)"],
        "rows": [
          ["Query Performance", "Ultra-fast (single disk read fetches all data)", "Slower (requires secondary lookup or application join)"],
          ["Data Redundancy", "Higher (can cause duplication if shared)", "Minimal (normalized single record)"],
          ["Atomic Updates", "Atomic within the single document", "Requires multi-document transactions across collections"],
          ["Relationship Scale", "1:1 and 1:Few (bounded arrays < 100 items)", "1:Many unbounded (10,000+ items) and Many-to-Many"],
          ["Risk", "Exceeding 16MB document limit; disk fragmentation", "Higher query latency; N+1 query vulnerability"]
        ]
      },
      "tradeoffs": "<strong>Embedding:</strong> Delivers superior read performance with atomic updates, but risks hitting the 16MB limit and causes memory bloat if documents contain fields rarely needed by queries. <strong>Referencing:</strong> Prevents document growth and avoids duplicate data, but requires multiple queries or expensive `$lookup` pipeline stages.",
      "failure_scenarios": "<strong>The Unbounded Array Outage:</strong> A social app embeds comments inside the post document: `{ post_id: 1, text: 'Hello', comments: [...] }`. A viral post receives 500,000 comments. The BSON document balloons past 16MB, throwing `BSONObjectTooLarge` errors. The post becomes completely unreadable and un-updatable, crashing the frontend. <em>Mitigation:</em> Use the <strong>Subset Pattern</strong>: embed only the 10 most recent comments in the post document, and store the full comment archive in a separate `comments` collection referenced by `post_id`.",
      "common_mistakes": [
        {"mistake": "Choosing a low-cardinality shard key (e.g. `status: 'ACTIVE'`).", "correction": "Shard keys must have high cardinality and balanced frequency distribution. Low cardinality causes Jumbo Chunks that cannot be split or moved across shards."},
        {"mistake": "Neglecting compound index direction when sorting on multiple fields in MongoDB.", "correction": "For sorting on `(A ASC, B DESC)`, the index MUST be created with matching sort orders: `{ a: 1, b: -1 }`."}
      ],
      "interview_questions": [
        {"question": "How does MongoDB handle write consistency across replica set members?", "answer": "MongoDB uses <strong>Write Concern</strong>. With `w: 1`, the primary acknowledges the write as soon as it updates its local memory/journal. With `w: 'majority'`, the primary waits until a majority of data-bearing replica nodes have written the mutation to their in-memory WAL before acknowledging the client. Using `w: 'majority'` combined with `j: true` (journaled) guarantees zero data loss even if the primary crashes immediately after."},
        {"question": "What is the Bucket Pattern in MongoDB time-series data modeling?", "answer": "Instead of storing each sensor reading as an individual document (which causes massive B-Tree index overhead for millions of small rows), the <strong>Bucket Pattern</strong> groups readings into time intervals (e.g., 1 hour per document). The document stores `device_id`, `start_time`, `end_time`, and an embedded array of 360 readings (`measurements: [{sec: 1, temp: 22.4}, ...]`), reducing index size by 99% and dramatically boosting read/write throughput."}
      ]
    },
    {
      "id": "cassandra-and-wide-column",
      "title": "Wide-Column Stores: Cassandra Architecture, SSTables, Memtables & Compaction",
      "definition": "Apache Cassandra is a distributed, decentralized, masterless Wide-Column NoSQL database modeled after Google Bigtable and Amazon Dynamo. It uses a composite primary key consisting of a Partition Key (which determines which node stores the row) and Clustering Columns (which physically sort rows on disk within the partition).",
      "why_we_need_it": "When systems ingest massive continuous write volumes (e.g., 500,000 telemetry metrics/sec or millions of chat messages), traditional databases lock up under B-Tree random write I/O. Cassandra's LSM-Tree append-only architecture delivers linearly scalable write throughput with zero single points of failure.",
      "real_world_analogy": "A massive Amazon fulfillment warehouse: The Partition Key is the aisle number where the crate is stored. The Clustering Columns are the sorted bin numbers along that specific aisle. When you ask for an item, the robotic picker drives straight to the aisle (Partition Key) and slides along the sorted shelf (Clustering Column) in seconds.",
      "how_it_works": "<p>1. <strong>Masterless Ring Topology:</strong> All nodes in a Cassandra cluster are completely identical (no master/replica distinction). Any node can act as a <strong>Coordinator Node</strong> for any client request. The coordinator hashes the Partition Key using Murmur3 to locate the replica nodes responsible for the token on the consistent hashing ring.</p><p>2. <strong>Write Path (LSM-Tree):</strong> When a write arrives:<br>&bull; Step 1: Appended sequentially to the on-disk <strong>CommitLog</strong> for crash durability.<br>&bull; Step 2: Written to the in-memory <strong>Memtable</strong> (sorted Skip List).<br>&bull; Step 3: Write is immediately acknowledged to client (&lt;2ms).<br>&bull; Step 4: When Memtable fills up, it is flushed to disk as an immutable <strong>SSTable</strong> (Sorted String Table).</p><p>3. <strong>Read Path:</strong> Coordinator checks the Memtable, and then probes candidate SSTables using <strong>Bloom Filters</strong> (avoiding reading files that definitely don't contain the partition key), the Partition Summary, and Partition Index.</p><p>4. <strong>Compaction:</strong> Background threads periodically merge multiple immutable SSTables into a single new sorted SSTable (Size-Tiered or Leveled Compaction), discarding overwritten row versions and purging deleted rows marked with <strong>Tombstones</strong>.</p><p>5. <strong>Tunable Quorum Math:</strong> Consistency is configured per read/write query. For strong consistency, ensure $R + W > N$ (where $R$ is read quorum, $W$ is write quorum, and $N$ is replication factor). Example: $N=3, W=\\text{QUORUM} (2), R=\\text{QUORUM} (2) \\implies 2 + 2 > 3$, guaranteeing the read always includes the latest written replica.</p>",
      "conceptual_breakdown": [
        "<strong>Query-Driven Data Modeling:</strong> You cannot design tables in Cassandra based on entity relationships. You must design one specific table per query! If you need to search users by `user_id` and by `email`, you create TWO separate tables: `users_by_id` and `users_by_email`.",
        "<strong>Tombstones & Deletions:</strong> In an append-only LSM-Tree, deleting a row writes a special marker called a <em>Tombstone</em>. The row is not physically deleted from disk until compaction runs after `gc_grace_seconds` (default 10 days).",
        "<strong>Gossip Protocol:</strong> Nodes exchange cluster state, token assignments, and node health metadata peer-to-peer every second without any centralized coordinator (like ZooKeeper).",
        "<strong>No JOINs or Foreign Keys:</strong> All relationships must be handled via denormalization or application-side joins."
      ],
      "arch_diagram": {
        "title": "Apache Cassandra Masterless Ring & LSM-Tree Write Path",
        "tiers": [
          {
            "label": "Client & Coordinator Tier",
            "nodes": [
              {
                "name": "Coordinator Node (Any Node)",
                "type": "lb",
                "icon": "🔄",
                "what": "Hashes Partition Key via Murmur3",
                "why": "Determines target replica nodes on ring",
                "when": "Client write request",
                "failure": "Client retries another peer node"
              }
            ]
          },
          {
            "label": "Target Node In-Memory Path",
            "nodes": [
              {
                "name": "CommitLog (Disk)",
                "type": "database",
                "icon": "📜",
                "what": "Sequential Append-Only Log",
                "why": "Guarantees crash durability",
                "when": "Immediate on write",
                "failure": "Replayed on node boot"
              },
              {
                "name": "Memtable (RAM)",
                "type": "cache",
                "icon": "🧠",
                "what": "Sorted In-Memory Buffer",
                "why": "Fast O(log N) inserts in RAM",
                "when": "Immediate on write",
                "failure": "Flushed to SSTable when full"
              }
            ]
          },
          {
            "label": "Immutable On-Disk Storage",
            "nodes": [
              {
                "name": "SSTable Files (Disk)",
                "type": "database",
                "icon": "💾",
                "what": "Sorted String Tables + Bloom Filters",
                "why": "Immutable disk storage",
                "when": "Flushed from Memtable",
                "failure": "Merged via Compaction daemon"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Cassandra Compaction Strategies Comparison",
        "columns": ["Strategy", "Compaction Trigger", "Write Amplification", "Read Latency", "Best Workload"],
        "rows": [
          ["Size-Tiered (STCS)", "When 4 SSTables of similar size accumulate", "Low", "Moderate (many SSTables to check)", "Write-heavy workloads (logging, metrics)"],
          ["Leveled Compaction (LCS)", "Strict size tiers (L0=10MB, L1=100MB, L2=1GB)", "High (frequent rewrites)", "Low & predictable (90% reads hit 1 SSTable)", "Read-heavy or read-modify-write workloads"],
          ["Time-Window (TWCS)", "Configured time windows (e.g. 1 hour/day)", "Lowest", "Fast for time-bounded queries", "Strict time-series data with fixed TTLs"]
        ]
      },
      "tradeoffs": "<strong>Pros:</strong> Boundless horizontal write scalability, zero single point of failure (true masterless), tunable consistency per query, multi-datacenter replication built-in. <strong>Cons:</strong> No relational joins, no transactions across partitions, tombstone scan performance traps on frequent deletes, rigid query patterns.",
      "failure_scenarios": "<strong>The Tombstone Overwhelming Outage:</strong> An application uses Cassandra as a temporary job queue, rapidly inserting and deleting millions of rows. Thousands of Tombstones accumulate. When a query scans the table, Cassandra reads 100,000 tombstones before finding 1 real row, triggering `TombstoneOverwhelmingException` and dropping the query. <em>Mitigation:</em> Cassandra is NOT a message queue! Never use Cassandra for queue-like workloads with high delete rates. Use RabbitMQ or Redis Streams instead.",
      "common_mistakes": [
        {"mistake": "Creating massive partitions with millions of rows exceeding 100MB.", "correction": "Keep partition sizes under 100MB and fewer than 100,000 rows. Add bucketing columns (e.g. `date_bucket`) to partition keys to avoid hotspot nodes."},
        {"mistake": "Using `SELECT COUNT(*)` across an entire Cassandra table.", "correction": "`COUNT(*)` triggers an all-node distributed scan that will time out. Maintain counters using Cassandra Counter columns or external Redis counters."}
      ],
      "interview_questions": [
        {"question": "How does Cassandra achieve tunable consistency and what is the Quorum formula?", "answer": "Cassandra allows clients to specify the consistency level for each read and write. The formula for Strong Consistency is: $R + W > N$, where $R$ is Read consistency, $W$ is Write consistency, and $N$ is Replication Factor. If $N=3$, choosing $W=\\text{QUORUM}$ (2 nodes must acknowledge) and $R=\\text{QUORUM}$ (2 nodes must respond) guarantees that the read set and write set overlap by at least one node, ensuring the client always receives the latest write."},
        {"question": "What is the difference between the Partition Key and Clustering Columns in Cassandra?", "answer": "The <strong>Partition Key</strong> is hashed by Murmur3 to determine which physical nodes in the cluster ring store the data. The <strong>Clustering Columns</strong> determine the physical on-disk sort order of rows <em>within</em> that specific partition, enabling high-performance range queries (e.g., `WHERE device_id = 'XYZ' AND timestamp >= '2026-10-01' ORDER BY timestamp DESC`)."}
      ]
    },
    {
      "id": "graph-databases-and-sql-vs-nosql",
      "title": "Graph DBs (Neo4j) & The Comprehensive SQL vs NoSQL Decision Matrix",
      "definition": "Graph databases (Neo4j, Amazon Neptune) treat relationships as first-class citizens using property graphs (Nodes, Edges, Properties). The SQL vs NoSQL Decision Matrix is the architectural evaluation framework used to select the optimal data persistence engine based on data relationships, access patterns, scalability requirements, and consistency constraints.",
      "why_we_need_it": "Querying 5 degrees of social separation or detecting fraud rings across 10 million transactions in SQL requires recursive CTEs and 5 self-joins that take minutes or time out. A Graph database traverses the same graph in 10 milliseconds. Choosing between SQL and the 4 NoSQL engines is one of the most critical decisions in system design.",
      "real_world_analogy": "Navigating a city: SQL is looking at a master satellite map of every single building in the state and calculating intersections mathematically from scratch. Graph DB is driving along roads by following physical directional signs at each intersection: you only care about the street connected to the corner you are currently standing on.",
      "how_it_works": "<p>1. <strong>Property Graph Model:</strong><br>&bull; <em>Nodes:</em> Discrete domain entities (e.g., `(:User {name: 'Alice', id: 101})`).<br>&bull; <em>Relationships (Edges):</em> Directed, typed connections between nodes (e.g., `-[:TRANSFERRED_MONEY {amount: 5000}]->`).<br>&bull; <em>Properties:</em> Arbitrary key-value metadata attached to both nodes and edges.</p><p>2. <strong>Index-Free Adjacency Mechanics:</strong> Each node directly stores bidirectional memory pointers (linked lists) to its incoming and outgoing relationships. Traversing from Node A to Node B does not require scanning a global index. The traversal complexity is $O(k)$ where $k$ is the degree of the node, completely independent of the total graph size.</p><p>3. <strong>Cypher Query Language:</strong> Declarative graph query syntax representing patterns visually: `MATCH (a:Account)-[r:TRANSFERRED_MONEY]->(b:Account) WHERE r.amount > 10000 RETURN a, b`.</p><p>4. <strong>Master Decision Matrix:</strong> Systematically evaluates the 5 database families against ACID needs, relational complexity, write throughput, and query flexibility.</p>",
      "conceptual_breakdown": [
        "<strong>When to choose SQL:</strong> Structured tabular data, strict ACID transactions, complex reporting/BI with ad-hoc joins, write volume < 20,000 QPS.",
        "<strong>When to choose Key-Value:</strong> Ultra-fast point lookups by primary ID, session tokens, rate limiter counters, caching.",
        "<strong>When to choose Document:</strong> Hierarchical entities where child records are viewed with parent, dynamic product catalogs, CMS.",
        "<strong>When to choose Wide-Column:</strong> Massive linear write scale (>100,000 writes/sec), time-series metrics, chat history, known query patterns.",
        "<strong>When to choose Graph:</strong> Highly interconnected data (3+ degrees of relationships), social graphs, fraud rings, identity graphs, recommendation engines."
      ],
      "arch_diagram": {
        "title": "Master Database Architecture Decision Tree",
        "tiers": [
          {
            "label": "Workload Requirements Evaluation",
            "nodes": [
              {
                "name": "Data Structure Analysis",
                "type": "client",
                "icon": "🧭",
                "what": "Relational vs Hierarchical vs Graph vs Key",
                "why": "Identifies fundamental data shape",
                "when": "Architecture design phase",
                "failure": "Mismatched paradigm causes performance cliff"
              }
            ]
          },
          {
            "label": "Decision Path",
            "nodes": [
              {
                "name": "ACID & Complex Joins? -> RDBMS",
                "type": "database",
                "icon": "🐘",
                "what": "PostgreSQL / MySQL",
                "why": "Foreign keys, financial consistency",
                "when": "Core transactional business logic",
                "failure": "Scale vertically or read replicas"
              },
              {
                "name": "100k+ Writes/sec? -> Wide-Column",
                "type": "database",
                "icon": "📊",
                "what": "Cassandra / ScyllaDB",
                "why": "LSM-Tree linear write scaling",
                "when": "IoT telemetry & chat logs",
                "failure": "Tunable quorum consistency"
              },
              {
                "name": "Deep Network Traversal? -> Graph",
                "type": "database",
                "icon": "🕸️",
                "what": "Neo4j / Amazon Neptune",
                "why": "Index-free adjacency pointer hops",
                "when": "Social graphs & fraud detection",
                "failure": "Bounded depth limits"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Comprehensive Database Selection Master Matrix",
        "columns": ["Database Engine", "Data Model", "ACID Support", "Scalability", "Best Use Case", "Avoid When"],
        "rows": [
          ["PostgreSQL / MySQL", "Relational Tables", "Full Multi-Table ACID", "Vertical (Read Replicas)", "Banking, E-Commerce, ERP", "Unbounded writes >50k/sec"],
          ["Redis / DynamoDB", "Key-Value", "Single/Multi-Item ACID", "Horizontal (Sharding)", "Sessions, Leaderboards, Carts", "Need ad-hoc search across values"],
          ["MongoDB", "Document (BSON)", "Multi-Document ACID", "Horizontal (Sharding)", "Product Catalogs, User Profiles", "Highly interconnected graph data"],
          ["Cassandra", "Wide-Column (LSM)", "Row-level only (BASE)", "Linear Horizontal", "Time-series, IoT, Chat History", "Need ad-hoc queries or SQL joins"],
          ["Neo4j", "Property Graph", "Full Graph ACID", "Vertical / Read Replicas", "Social Graphs, Fraud Rings", "High-throughput sequential logs"]
        ]
      },
      "tradeoffs": "<strong>Graph DB Trade-off:</strong> Delivers unbeatable performance for relationship traversals, but is difficult to shard horizontally across multiple servers because graph partitioning is an NP-hard problem. Most graph databases rely on vertical scaling or read-replica clusters.",
      "failure_scenarios": "<strong>The Fraud Ring Graph Explosion:</strong> A FinTech company attempts to detect synthetic identity fraud rings using recursive SQL joins on a relational database. As transaction history grows to 200 million rows, a 4-degree relationship query joins the transaction table 4 times, producing a combinatorial explosion that locks database memory for 2 hours. <em>Mitigation:</em> Replicate account transaction edges into Neo4j; run Cypher pattern matching queries that complete in 15 milliseconds.",
      "common_mistakes": [
        {"mistake": "Picking a NoSQL database first and then trying to implement relational joins in application code.", "correction": "If your application requires extensive cross-entity joins, start with PostgreSQL."},
        {"mistake": "Assuming Polyglot Persistence means using 8 different databases for a 5-person startup.", "correction": "Start with PostgreSQL. PostgreSQL has JSONB (Document), hstore (Key-Value), and ltree/recursive CTEs (Graph). Adopt dedicated NoSQL engines only when specific scale limits are hit."}
      ],
      "interview_questions": [
        {"question": "How do you explain the choice between SQL and NoSQL in a system design interview?", "answer": "Structure your answer around 4 pillars: 1. <strong>Data Structure:</strong> Is data tabular with fixed schemas (SQL) or hierarchical/unstructured (NoSQL)?; 2. <strong>Query Patterns:</strong> Do you need ad-hoc multi-table joins and aggregations (SQL) or known key-based lookups (NoSQL)?; 3. <strong>Consistency vs Availability (CAP):</strong> Do you require immediate ACID consistency (SQL) or high availability with eventual consistency (NoSQL)?; 4. <strong>Scale:</strong> Is write throughput within single-server limits (&lt;20k writes/sec, SQL) or does it require linear multi-master horizontal scaling (Cassandra/DynamoDB)?"},
        {"question": "What is Polyglot Persistence?", "answer": "<strong>Polyglot Persistence</strong> is the architectural practice of using different database engines within the same system, matching each microservice or component to the database best suited for its specific data model and access pattern. For example: PostgreSQL for user accounts and financial transactions, Redis for caching and rate limiting, Elasticsearch for product search, Cassandra for clickstream analytics, and Neo4j for social friend recommendations."}
      ]
    }
  ]
}

# Write Module 11
with open(HLD_DIR / "module_11.json", "w", encoding="utf-8") as f:
  json.dump(m11, f, ensure_ascii=False, indent=2)
print("Module 11 written successfully!")
