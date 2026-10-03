"""
Append Module 09 and Module 10 to complete the 06-10 set.
"""
import json
from pathlib import Path

HLD_DIR = Path('content/hld')
HLD_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# MODULE 09: Database Foundations & Relational DBs
# ==========================================
m09 = {
  "module_id": "09",
  "module_title": "Database Foundations & Relational DBs",
  "description": "Master relational vs NoSQL paradigms, ACID transaction internals (Write-Ahead Logging, Two-Phase Locking), Normalization vs Denormalization, and Connection Pooling mechanics.",
  "topics": [
    {
      "id": "relational-vs-nosql-paradigm",
      "title": "Relational (RDBMS) vs NoSQL: Data Modeling & Query Paradigms",
      "definition": "Relational Database Management Systems (RDBMS) organize data into strictly typed tables with predefined schemas, foreign key constraints, and declarative SQL joins. NoSQL (Not Only SQL) databases relax relational constraints in favor of horizontal partition scaling, flexible schemaless documents, key-value mappings, wide-column tables, or graph networks.",
      "why_we_need_it": "No single database fits every workload. Using an RDBMS for high-velocity IoT telemetry (100,000 writes/sec) will choke due to B-Tree write lock contention. Conversely, using a key-value store for financial accounting with complex multi-table invariant audits risks data corruption without foreign keys and ACID transactions.",
      "real_world_analogy": "RDBMS is a traditional formal bank vault with strict ledger books, indexed by row and column, verified by multiple accountants before any ledger entry is stamped. NoSQL is a high-speed automated shipping warehouse with modular bins, pallets, and conveyor belts built for massive throughput without checking if two boxes have matching serial numbers.",
      "how_it_works": "<p>1. <strong>Relational Data Modeling:</strong> Based on Codd's Relational Model. Entities are represented as relations (tables), rows are tuples, and columns are attributes. Relationships (1:1, 1:N, N:M) are established via Primary Keys and Foreign Keys. The SQL query optimizer dynamically plans index scans, nested loops, and hash joins to answer ad-hoc relational queries.</p><p>2. <strong>NoSQL Paradigms:</strong> Organized into four distinct architectures:<br>&bull; <em>Key-Value (Redis, DynamoDB):</em> $O(1)$ lookup via partition key hashing.<br>&bull; <em>Document (MongoDB, Couchbase):</em> Hierarchical JSON/BSON trees allowing embedded sub-documents.<br>&bull; <em>Wide-Column (Cassandra, ScyllaDB):</em> Sparse multidimensional sorted maps keyed by Partition Key and Clustering Columns.<br>&bull; <em>Graph (Neo4j):</em> First-class nodes and directed edges traversing relationships in $O(1)$ index-free adjacency time.</p><p>3. <strong>Impedance Mismatch:</strong> Object-Oriented code uses complex nested object graphs. RDBMS requires normalizing this into flat tables and rejoining them via SQL (Object-Relational Impedance Mismatch). Document stores store the entire JSON object as a single atomic document, eliminating join latency at the cost of duplicate data across documents.</p>",
      "conceptual_breakdown": [
        "<strong>Schema-on-Write vs Schema-on-Read:</strong> RDBMS validates schema upon insertion (rejects invalid columns); Document NoSQL accepts any JSON shape on write, deferring schema parsing to the application reading the payload.",
        "<strong>Vertical vs Horizontal Scaling:</strong> RDBMS traditionally scales vertically (beefier CPU/RAM) because cross-table joins across 20 sharded database nodes are prohibitively expensive. NoSQL scales horizontally (adding 50 cheap commodity nodes) by partitioning data along a shard key.",
        "<strong>Declarative SQL vs Access-Pattern Modeling:</strong> SQL lets you query by any column combination using ad-hoc joins. Cassandra/NoSQL requires you to know your exact read query patterns *before* designing table partition keys.",
        "<strong>ACID vs BASE:</strong> RDBMS guarantees Atomicity, Consistency, Isolation, Durability. NoSQL typically provides Basically Available, Soft state, Eventual consistency."
      ],
      "arch_diagram": {
        "title": "Relational vs NoSQL Storage Paradigms",
        "tiers": [
          {
            "label": "Workload Classification",
            "nodes": [
              {
                "name": "Transactional Workload",
                "type": "client",
                "icon": "💳",
                "what": "Financial ledger, e-commerce orders",
                "why": "Requires ACID, foreign keys & zero data loss",
                "when": "Strong consistency needed",
                "failure": "Rollback transaction"
              },
              {
                "name": "High-Throughput Ingest",
                "type": "client",
                "icon": "📡",
                "what": "IoT Telemetry, clickstream, chat logs",
                "why": "Requires horizontal write elasticity",
                "when": "Eventual consistency acceptable",
                "failure": "Buffer in message queue"
              }
            ]
          },
          {
            "label": "Database Engine Choice",
            "nodes": [
              {
                "name": "RDBMS (PostgreSQL / MySQL)",
                "type": "database",
                "icon": "🐘",
                "what": "ACID Relational Storage Engine",
                "why": "Strict schemas, B-Tree indexes & SQL joins",
                "when": "Relational queries",
                "failure": "Multi-AZ synchronous replication"
              },
              {
                "name": "NoSQL (Cassandra / DynamoDB)",
                "type": "database",
                "icon": "⚡",
                "what": "Distributed Hash Partitioned Store",
                "why": "Linear write scaling via LSM-trees",
                "when": "Known access-pattern lookups",
                "failure": "Tunable quorum consistency"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "RDBMS vs NoSQL Decision Matrix",
        "columns": ["Feature", "Relational (RDBMS)", "Document (MongoDB)", "Wide-Column (Cassandra)", "Key-Value (DynamoDB)"],
        "rows": [
          ["Primary Data Model", "Tables, Rows, Columns", "JSON / BSON Documents", "Sparse multidimensional tables", "Key-Value Pairs"],
          ["Schema Flexibility", "Strict (DDL migrations required)", "Dynamic / Schemaless", "Fixed columns per partition", "Schemaless values"],
          ["Transactions", "Full multi-table ACID", "Multi-document ACID (slower)", "Row-level lightweight only", "Multi-item ACID transactions"],
          ["Join Capabilities", "Native declarative SQL JOINs", "Lookup aggregation (expensive)", "No JOIN support (application join)", "No JOIN support"],
          ["Scaling Strategy", "Vertical primarily, Read Replicas", "Horizontal sharding", "Masterless horizontal rings", "Managed infinite horizontal scale"],
          ["Best For", "Banking, ERP, E-commerce Checkout", "Content Management, User Profiles", "Time-series, Chat history, IoT", "Session State, Shopping Carts"]
        ]
      },
      "tradeoffs": "<strong>RDBMS:</strong> Pros: Absolute data integrity, expressive queries, complex reporting, ACID guarantees. Cons: Expensive to scale writes beyond 20k QPS on a single instance, rigid migrations. <strong>NoSQL:</strong> Pros: Infinite horizontal scale, low write latency, schema agility. Cons: Eventual consistency bugs, duplicate data, lack of ad-hoc join queries requiring application-side stitching.",
      "failure_scenarios": "<strong>The Ad-Hoc Query Trap in Cassandra:</strong> An engineering team migrates from MySQL to Cassandra for scaling, but their business team frequently asks for ad-hoc reports like `SELECT * FROM orders WHERE customer_state = 'CA' AND discount_code = 'SUMMER'`. Because Cassandra tables must be partitioned strictly by query key, answering this ad-hoc query requires a full-cluster scan across 50 nodes, timing out and crashing the cluster. <em>Mitigation:</em> Replicate data into Elasticsearch or Snowflake for ad-hoc analytical queries.",
      "common_mistakes": [
        {"mistake": "Choosing NoSQL purely because it is 'newer' or 'web-scale' when relational integrity is paramount.", "correction": "Start with PostgreSQL. PostgreSQL scales to millions of users with proper indexing and connection pooling before NoSQL is ever warranted."},
        {"mistake": "Attempting to perform deep relational JOINs across multiple collections in MongoDB.", "correction": "Denormalize related child entities into the parent document, or use an RDBMS if your domain is inherently highly relational."}
      ],
      "interview_questions": [
        {"question": "When should you choose a Relational Database over a NoSQL database?", "answer": "Choose an <strong>RDBMS</strong> when: 1. Your data is inherently relational with complex entity relationships (1:N, N:M); 2. You require strict multi-table ACID transactions (financial transactions, inventory reservations); 3. Your query patterns are unpredictable and require ad-hoc analytical queries and joins; 4. Data consistency is more important than raw write throughput."},
        {"question": "What is the Object-Relational Impedance Mismatch?", "answer": "It refers to the technical difficulty of mapping complex, nested, polymorphic object-oriented programming models (classes, inheritance, object references) to flat, two-dimensional relational database tables governed by mathematical set theory. ORM frameworks bridge this gap, but often introduce N+1 query performance problems and leaky abstractions."}
      ]
    },
    {
      "id": "acid-transactions-explained",
      "title": "ACID Properties: Atomicity, Consistency, Isolation & Durability",
      "definition": "ACID is a set of four database properties that guarantee data validity and reliability despite errors, power failures, crashes, and concurrent multi-user execution: Atomicity (All or Nothing), Consistency (Invariant Preservation), Isolation (Concurrent Independence), and Durability (Committed State Survives Crashes).",
      "why_we_need_it": "In a bank transfer of $100 from Alice to Bob, the system must subtract $100 from Alice AND add $100 to Bob. If the server crashes mid-flight after subtracting from Alice, without Atomicity, $100 vanishes into thin air. ACID guarantees financial correctness under all failure conditions.",
      "real_world_analogy": "A signed legal contract: Atomicity means either both parties sign and the deal is done, or no deal exists. Consistency means the contract cannot violate local laws. Isolation means two buyers competing for the same house don't sign contracts simultaneously. Durability means the deed is recorded in the city vault on fireproof parchment—burning the real estate office down doesn't invalidate your property ownership.",
      "how_it_works": "<p>1. <strong>Atomicity (WAL & Undo Logs):</strong> Implemented using <strong>Write-Ahead Logging (WAL)</strong> and Undo Logs. Before any table row is mutated in memory, the database writes the change to an append-only log on disk. If a crash occurs or `ROLLBACK` is issued, the engine reads the undo log in reverse order, restoring original values.</p><p>2. <strong>Consistency (Invariants):</strong> The database guarantees that data moves from one valid state to another valid state, strictly enforcing primary key uniqueness, foreign key relationships, `NOT NULL` constraints, and check constraints (`CHECK balance >= 0`).</p><p>3. <strong>Isolation (Concurrency Control):</strong> Governs how concurrent transactions see each other's intermediate mutations. Implemented via <strong>Two-Phase Locking (2PL)</strong> or <strong>Multi-Version Concurrency Control (MVCC)</strong>. MVCC creates a private snapshot of the database for each transaction, allowing readers to read without locking writers, and writers to write without blocking readers.</p><p>4. <strong>Durability (fsync & Redo Logs):</strong> Once a transaction executes `COMMIT`, the database flushes the WAL log to non-volatile disk storage via the OS `fsync()` system call. Even if power cuts out 1 millisecond later, upon reboot the recovery manager replays the Redo Log to reconstruct the committed state.</p>",
      "conceptual_breakdown": [
        "<strong>WAL (Write-Ahead Log) Principle:</strong> 'Never write a dirty data page to disk until the corresponding log record describing the update has been flushed to non-volatile storage.'",
        "<strong>MVCC (Multi-Version Concurrency Control):</strong> PostgreSQL and MySQL InnoDB never overwrite rows in place. Updates create a new version of the row with a transaction ID (`xmin`, `xmax`). Obsolete dead versions are cleaned up later by background Vacuum/Purge threads.",
        "<strong>Dirty Read vs Phantom Read:</strong> A dirty read sees uncommitted data from a concurrent transaction that might rollback. A phantom read occurs when a transaction queries a range of rows twice and sees newly inserted rows that were committed by another transaction in between.",
        "<strong>Durability Trade-off (fsync cost):</strong> Calling `fsync()` on every single commit limits disk throughput to ~1,000-5,000 transactions/sec on spinning disks/standard SSDs. Group Commit batches multiple concurrent transactions into a single disk fsync."
      ],
      "arch_diagram": {
        "title": "ACID Transaction Engine Mechanics (WAL + MVCC + Buffer Pool)",
        "tiers": [
          {
            "label": "Transaction Execution Tier",
            "nodes": [
              {
                "name": "Transaction Coordinator",
                "type": "service",
                "icon": "🔄",
                "what": "BEGIN / COMMIT Manager",
                "why": "Assigns monotonic Transaction ID (XID)",
                "when": "Client begins transaction",
                "failure": "Issues automatic ROLLBACK on timeout"
              }
            ]
          },
          {
            "label": "In-Memory Buffer & Engine",
            "nodes": [
              {
                "name": "Buffer Pool (Shared RAM)",
                "type": "cache",
                "icon": "🧠",
                "what": "Caches 8KB Database Pages",
                "why": "Accelerates reads and buffers dirty writes",
                "when": "Active queries",
                "failure": "Dirty pages reconstructed via WAL on crash"
              },
              {
                "name": "MVCC Snapshot Engine",
                "type": "service",
                "icon": "📸",
                "what": "Read View Isolation",
                "why": "Provides repeatable read snapshots without locks",
                "when": "SELECT execution",
                "failure": "Vacuum daemon purges obsolete row versions"
              }
            ]
          },
          {
            "label": "Durable Disk Storage Tier",
            "nodes": [
              {
                "name": "Write-Ahead Log (WAL / Redo Log)",
                "type": "database",
                "icon": "📜",
                "what": "Sequential Append-Only Log on Disk",
                "why": "Guarantees Durability via fsync() before commit ACK",
                "when": "Every state mutation",
                "failure": "Crash recovery engine replays log"
              },
              {
                "name": "Data Files (.ibd / heap)",
                "type": "database",
                "icon": "💾",
                "what": "B-Tree Tablespace Data Pages",
                "why": "Permanent organized table storage",
                "when": "Flushed asynchronously by checkpoint thread",
                "failure": "Backed up to cloud object store"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "ACID Implementation Mechanisms Matrix",
        "columns": ["Property", "Meaning", "Implementation Mechanism", "Failure Mode if Missing"],
        "rows": [
          ["Atomicity", "All operations succeed or all fail together", "Undo Logs & Write-Ahead Logging (WAL)", "Partial updates (e.g. money deducted, never deposited)"],
          ["Consistency", "Database invariants and constraints are preserved", "Declarative Constraints (FK, UNIQUE, CHECK)", "Corrupted business state (negative bank balances)"],
          ["Isolation", "Concurrent transactions do not interfere with each other", "MVCC, 2-Phase Locking (2PL), Row Locks", "Dirty reads, non-repeatable reads, lost updates"],
          ["Durability", "Committed state survives server crashes and power loss", "Redo Log flush via fsync() to non-volatile disk", "Data loss upon power outage immediately after commit"]
        ]
      },
      "tradeoffs": "<strong>Strong Isolation vs Concurrency:</strong> Serializable isolation guarantees 100% correctness by preventing all concurrency anomalies, but causes massive lock contention, transaction aborts, and serialization failures. Read Committed / Repeatable Read provides 10x higher concurrency by tolerating specific rare anomalies like write skew.",
      "failure_scenarios": "<strong>The Lost Update Anomaly:</strong> Two users concurrently attempt to book the last seat on a flight. Transaction A reads `seat = FREE`. Transaction B reads `seat = FREE`. Transaction A updates `seat = OCCUPIED_BY_A` and commits. Transaction B immediately updates `seat = OCCUPIED_BY_B` and commits, overwriting User A's booking. <em>Mitigation:</em> Pessimistic Locking (`SELECT * FROM seats WHERE id = 1 FOR UPDATE`) or Optimistic Concurrency Control using a version column (`UPDATE seats SET booked_by = 'B', version = version + 1 WHERE id = 1 AND version = 5`).",
      "common_mistakes": [
        {"mistake": "Holding open long database transactions while waiting for an external third-party HTTP call (e.g., Stripe API).", "correction": "Never make network I/O calls inside a database transaction. Execute the external HTTP call first, and then run a fast, sub-millisecond DB transaction to persist the result."},
        {"mistake": "Disabling database foreign key constraints to make inserts faster without an application-level integrity guard.", "correction": "Keep foreign key constraints intact, or use strict asynchronous validation pipelines if running at massive distributed scale."}
      ],
      "interview_questions": [
        {"question": "How does Multi-Version Concurrency Control (MVCC) eliminate read-write lock contention?", "answer": "In traditional 2-Phase Locking, a write transaction acquires an exclusive lock on a row, blocking all readers until the write commits. In <strong>MVCC</strong>, when a row is updated, the database keeps the old version and appends the new version with transaction timestamp metadata. Readers see a consistent snapshot of the data as it existed when their transaction started, reading older row versions. Consequently, <strong>readers never block writers, and writers never block readers</strong>."},
        {"question": "What is the difference between Write-Ahead Logging (WAL) and the actual data table files?", "answer": "Writing to data table files involves random I/O (modifying B-Tree leaves across scattered disk sectors), which is slow. The <strong>Write-Ahead Log (WAL)</strong> is an append-only sequential file. Appending to a sequential log is orders of magnitude faster. The database writes changes to the WAL and commits immediately, while a background 'checkpoint' process lazily flushes dirty pages in the buffer pool to the actual table data files."}
      ]
    },
    {
      "id": "normalization-vs-denormalization",
      "title": "Database Normalization (1NF to 3NF) vs Intentional Denormalization",
      "definition": "Database Normalization is the systematic process of organizing relational schemas to eliminate data redundancy and anomalies (Insertion, Update, Deletion anomalies) by decomposing tables into Third Normal Form (3NF) or BCNF. Denormalization is the intentional re-introduction of redundancy to optimize read performance by eliminating expensive multi-table SQL joins.",
      "why_we_need_it": "In un-normalized schemas, updating a customer's address requires executing `UPDATE` statements across 50,000 order rows; if one row fails, data becomes corrupt (Update Anomaly). However, a fully normalized 3NF schema for an e-commerce checkout might require joining 8 tables (Users, Orders, LineItems, Products, Categories, Addresses, Discounts, Taxes), producing unacceptable query latencies under 50,000 QPS load.",
      "real_world_analogy": "A grocery receipt: A fully normalized database would print a receipt containing only ID numbers: `CustomerID: 48, ItemIDs: [99, 102, 401]`. You would have to look up the item names and prices in an encyclopedia. Denormalization is printing the actual item names, unit prices, and store address directly on the paper receipt at the moment of checkout so you can read it instantly without looking up anything else.",
      "how_it_works": "<p>1. <strong>First Normal Form (1NF):</strong> Enforces atomicity: each column must contain only atomic (indivisible) values, no repeating groups or comma-separated lists, and each row must have a unique primary key.</p><p>2. <strong>Second Normal Form (2NF):</strong> Must be in 1NF and have <em>No Partial Dependencies</em>: every non-key column must depend on the whole primary key, not a subset of a composite key.</p><p>3. <strong>Third Normal Form (3NF):</strong> Must be in 2NF and have <em>No Transitive Dependencies</em>: non-key columns must depend *only* on the primary key, not on other non-key columns ('The key, the whole key, and nothing but the key, so help me Codd').</p><p>4. <strong>Intentional Denormalization:</strong> In high-read production systems, 3NF schemas are selectively denormalized by: duplicating frequently read columns (e.g. copying `user_name` directly onto the `comments` table to avoid joining `users`), maintaining pre-computed aggregate columns (e.g. `order_total`, `comment_count`), or using Materialized Views.</p>",
      "conceptual_breakdown": [
        "<strong>Write Optimization vs Read Optimization:</strong> 3NF minimizes write overhead (you update an address in exactly 1 place); Denormalization minimizes read latency (you read everything in 1 table scan with zero joins).",
        "<strong>Anomalies Guard:</strong> Normalization eliminates Insertion Anomalies (cannot record product without a seller), Deletion Anomalies (deleting an order deletes the customer's identity), and Update Anomalies (updating a name in some rows but missing others).",
        "<strong>Materialized Views:</strong> A database feature that automatically computes and persists the result of a complex multi-table join on disk, refreshing periodically or via triggers.",
        "<strong>Read/Write Ratio Rule of Thumb:</strong> Write-heavy transactional systems (ERP, Banking, Core Ledger) favor 3NF. Read-heavy web systems (Social Feeds, Product Catalogs, Dashboards) favor Denormalization."
      ],
      "arch_diagram": {
        "title": "Normalized 3NF vs Denormalized Storage Topology",
        "tiers": [
          {
            "label": "Normalized 3NF Model (Zero Redundancy)",
            "nodes": [
              {
                "name": "Users Table",
                "type": "database",
                "icon": "👤",
                "what": "user_id, name, email",
                "why": "Single authoritative identity row",
                "when": "User profile changes",
                "failure": "Requires JOIN to get order names"
              },
              {
                "name": "Orders Table",
                "type": "database",
                "icon": "📦",
                "what": "order_id, user_id, date",
                "why": "Pure relationship mapping",
                "when": "Order placed",
                "failure": "Requires 3-way join for invoice"
              }
            ]
          },
          {
            "label": "Denormalized Read Model (Pre-Joined)",
            "nodes": [
              {
                "name": "Order_Summary_View",
                "type": "database",
                "icon": "⚡",
                "what": "order_id, user_name, total, items_json",
                "why": "Sub-millisecond single-table SELECT",
                "when": "Mobile app loads order feed",
                "failure": "Requires background sync when name changes"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Normalization (3NF) vs Denormalization Comparison",
        "columns": ["Dimension", "Normalized (3NF)", "Denormalized"],
        "rows": [
          ["Data Redundancy", "Strictly zero (every piece of data stored once)", "High (data duplicated across multiple tables)"],
          ["Write Performance", "Fast (single row insert/update)", "Slower (multiple tables must be updated in sync)"],
          ["Read Performance", "Slower under load (expensive multi-table SQL JOINs)", "Extremely fast (single table lookup, zero JOINs)"],
          ["Storage Footprint", "Minimal disk space required", "Higher disk space usage due to repeated columns"],
          ["Risk of Inconsistency", "Zero risk of data inconsistency", "High (if sync fails, tables store conflicting values)"],
          ["Ideal Architecture", "OLTP Core Financial Ledger, Master Records", "OLAP Data Warehousing, High-Traffic Public APIs"]
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> Denormalization trades write complexity and storage space for dramatic reductions in read latency. When you denormalize `user_name` onto 1,000,000 `posts` rows, a user changing their name requires updating 1,000,000 rows (or accepting that past posts retain the old display name).",
      "failure_scenarios": "<strong>The Split-Brain User Name Bug:</strong> An engineer copies `user_email` into the `orders` table for fast lookups. When a customer updates their email address on their profile, the app updates the `users` table but misses the `orders` table. Subsequent shipping receipts and fraud alerts are dispatched to the old compromised email. <em>Mitigation:</em> Encapsulate all updates in domain events, or maintain denormalized data through automated database triggers or Change Data Capture (CDC) streams.",
      "common_mistakes": [
        {"mistake": "Denormalizing prematurely before profiling actual production database query bottlenecks.", "correction": "Start with a clean 3NF relational schema. Add proper B-Tree indexes. Denormalize only specific tables when slow query logs prove that join latency is hurting user experience."},
        {"mistake": "Storing comma-separated ID strings (e.g., `tag_ids = '1,4,9,12'`) in a single relational column.", "correction": "Violates 1NF! It breaks indexing, prevents foreign key constraints, and makes searching for a tag require a slow full-table text regex scan."}
      ],
      "interview_questions": [
        {"question": "What is the Third Normal Form (3NF) in simple engineering terms?", "answer": "A table is in 3NF if: 1. It is in 2NF (all attributes depend on the primary key); and 2. <strong>There are no transitive dependencies</strong>—meaning non-key columns must not depend on other non-key columns. For example, if a table has `(order_id, customer_id, customer_city)`, `customer_city` depends on `customer_id`, not directly on `order_id`. To reach 3NF, move `customer_id` and `customer_city` into a separate `customers` table."},
        {"question": "How do you maintain data consistency in intentionally denormalized tables?", "answer": "Use one of three patterns: 1. <strong>Synchronous Dual-Writes inside a single ACID transaction</strong> (best when tables reside in the same database); 2. <strong>Database Triggers</strong> that automatically update duplicate rows; 3. <strong>Asynchronous Change Data Capture (CDC) with Kafka</strong> (best for microservices/distributed stores), where mutations on the primary table stream events to background worker consumers that update read views."}
      ]
    },
    {
      "id": "connection-pooling-and-locks",
      "title": "Connection Pooling, Optimistic vs Pessimistic Locking & Deadlocks",
      "definition": "Database connection pooling maintains a warm cache of reusable database connections (e.g., HikariCP, PgBouncer), eliminating the severe CPU/memory cost of establishing new TCP and TLS handshakes on every request. Concurrency locking controls access to shared rows using either Pessimistic Locking (blocking locks) or Optimistic Locking (version checking).",
      "why_we_need_it": "Establishing a new PostgreSQL connection consumes ~10MB of server RAM and takes 20-50ms of CPU time (forking a new backend process). If 2,000 concurrent web requests hit PostgreSQL simultaneously without a pooler, the server runs out of RAM and crashes with Out Of Memory (OOM).",
      "real_world_analogy": "A public taxi stand: Connection pooling is having 20 warm taxis waiting at the curb for passengers to jump in and out sequentially. Without pooling, every passenger would have to order a brand-new car from the factory, wait for it to be assembled and delivered, take a 2-minute ride, and then crush the car in a junkyard.",
      "how_it_works": "<p>1. <strong>Connection Pool Mechanics:</strong> The application initializes a pool of $N$ persistent database connections (e.g., 20 connections) at startup. When an HTTP request needs to execute a query, it leases a connection from the pool, runs the query, and immediately returns the connection to the pool. If all connections are busy, incoming requests queue up until a connection becomes available or a `connectionTimeout` (e.g. 250ms) trips.</p><p>2. <strong>PgBouncer Modes:</strong> In high-scale PostgreSQL, an external proxy pooler (PgBouncer) is placed between application servers and the database:<br>&bull; <em>Session Pooling:</em> Connection assigned to client for the entire duration of its login session.<br>&bull; <em>Transaction Pooling:</em> Connection assigned only for the duration of a single transaction (`BEGIN` to `COMMIT`), allowing 10,000 application pods to multiplex over 100 database connections.<br>&bull; <em>Statement Pooling:</em> Connection released after each individual SQL statement (cannot use multi-statement transactions).</p><p>3. <strong>Pessimistic Locking (`SELECT ... FOR UPDATE`):</strong> Acquires an exclusive row-level lock in the database engine. Other transactions attempting to read with `FOR UPDATE` or mutate that row are blocked until the lock-holding transaction commits. Ideal for high-contention, low-duration write paths.</p><p>4. <strong>Optimistic Concurrency Control (OCC):</strong> No database locks are acquired. Each row includes a `version` integer column. When updating: `UPDATE accounts SET balance = balance - 50, version = version + 1 WHERE id = 1 AND version = 3`. If another transaction modified the row in the meantime, `Rows Affected` returns 0. The application detects the conflict and retries.</p><p>5. <strong>Deadlocks & Detection:</strong> Occurs when Transaction 1 holds Lock A and waits for Lock B, while Transaction 2 holds Lock B and waits for Lock A. The database engine's Deadlock Detector periodically scans the Wait-For Graph for directed cycles, automatically killing one transaction with a `DeadlockDetectedException` to let the other proceed.</p>",
      "conceptual_breakdown": [
        "<strong>Optimal Pool Sizing Formula:</strong> By PostgreSQL lead developer empirical testing: $\\text{Connections} = (\\text{Core Count} \\times 2) + \\text{Effective Spindle Count}$. A 16-core database server performs optimally with only ~34 pooled connections! Oversizing the pool causes catastrophic CPU context-switching thrashing.",
        "<strong>Optimistic vs Pessimistic Rule of Thumb:</strong> Use Optimistic locking when conflict frequency is low (&lt;5% collision rate, e.g. editing a user profile wiki). Use Pessimistic locking when conflict frequency is high (e.g. flash-sale ticketing where 100 users fight for the last concert seat).",
        "<strong>Lock Ordering:</strong> The universal algorithmic prevention for deadlocks: always acquire locks on multiple resources in the exact same deterministic global order (e.g., always lock resources by ascending numerical ID: `id = 1` then `id = 2`).",
        "<strong>PgBouncer Transaction Mode Caveat:</strong> Prepared statements, temporary tables, and `SET timezone` settings cannot be used with transaction-mode pooling because state leaks across different clients sharing the socket."
      ],
      "arch_diagram": {
        "title": "Connection Pooling & Transaction Multiplexing Architecture",
        "tiers": [
          {
            "label": "Application Fleet (1,000 Pods)",
            "nodes": [
              {
                "name": "App Pod 1..1000",
                "type": "client",
                "icon": "📦",
                "what": "Microservice instances",
                "why": "Requires database queries",
                "when": "User requests",
                "failure": "Retries on pool acquisition timeout"
              }
            ]
          },
          {
            "label": "Multiplexing Proxy Tier",
            "nodes": [
              {
                "name": "PgBouncer Cluster",
                "type": "lb",
                "icon": "🛡️",
                "what": "Transaction Connection Pooler",
                "why": "Multiplexes 10,000 app sockets -> 50 DB sockets",
                "when": "Active SQL transactions",
                "failure": "Active-passive standby failover"
              }
            ]
          },
          {
            "label": "Database Engine Tier",
            "nodes": [
              {
                "name": "PostgreSQL Primary (16 Cores)",
                "type": "database",
                "icon": "🐘",
                "what": "50 Dedicated Worker Processes",
                "why": "Executes queries without context-switching thrash",
                "when": "Continuous",
                "failure": "Deadlock detector aborts cycle"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Optimistic vs Pessimistic Locking Comparison",
        "columns": ["Feature", "Optimistic Locking (OCC)", "Pessimistic Locking (2PL)"],
        "rows": [
          ["Mechanism", "Version column / Timestamp checking (`WHERE version = 5`)", "Exclusive database row lock (`SELECT FOR UPDATE`)"],
          ["Lock Acquired", "None during read; checked only at commit time", "Immediate row-level exclusive lock on read"],
          ["Contention Suitability", "Best for LOW conflict workloads", "Best for HIGH conflict workloads"],
          ["Performance Impact", "Zero blocking; high throughput when collisions are rare", "Transactions block; threads sleep waiting for locks"],
          ["Deadlock Vulnerability", "Zero risk of database deadlocks", "High risk of deadlocks if locking order is inconsistent"],
          ["Failure Behavior", "Returns 0 rows affected; application retries loop", "Wait timeout or Deadlock detected exception"]
        ]
      },
      "tradeoffs": "<strong>Pessimistic Locking:</strong> Guarantees that once you read a row, nobody else can touch it, preventing wasted computation. However, long-held locks degrade system throughput and risk deadlocks. <strong>Optimistic Locking:</strong> Completely non-blocking and highly scalable, but if 100 users attempt to purchase an item simultaneously, 99 transactions fail their version check and must retry, burning CPU.",
      "failure_scenarios": "<strong>The Inverted Lock Order Deadlock:</strong> Transaction 1 transfers money from Account A to B: locks A, then attempts to lock B. Simultaneously, Transaction 2 transfers money from Account B to A: locks B, then attempts to lock A. Both threads hang forever waiting for each other until the database deadlock detector kills one. <em>Mitigation:</em> Sort IDs before locking: `first_id = min(A, B); second_id = max(A, B); lock(first_id); lock(second_id);`.",
      "common_mistakes": [
        {"mistake": "Setting application connection pool sizes to 500 connections per app instance across 20 instances (10,000 connections total).", "correction": "Follow the formula: `(cores * 2)`. Oversized connection pools cause massive CPU cache misses and lock thrashing, slowing down the database."},
        {"mistake": "Using Pessimistic Locking (`SELECT FOR UPDATE`) across user interaction workflows (e.g. holding a lock while waiting for a user to type their credit card).", "correction": "Never hold database locks across user thinking time or external HTTP calls. Use Optimistic Locking with a short expiration timer."}
      ],
      "interview_questions": [
        {"question": "How do you calculate the optimal connection pool size for a relational database?", "answer": "The standard heuristic formula is: $\\text{Connections} = (\\text{CPU Cores} \\times 2) + \\text{Disk Count}$. For modern NVMe SSDs, a server with 16 cores achieves maximum query throughput with 32 to 40 connections. Setting pool size to 500 does NOT make it faster; it forces the CPU to spend more time context-switching between 500 competing processes than executing actual SQL queries."},
        {"question": "How do you detect and resolve a distributed deadlock?", "answer": "Distributed deadlocks cannot be detected by a single local database engine. Solutions: 1. <strong>Strict Lock Ordering:</strong> Enforce that all services always acquire locks in a globally deterministic lexicographical order; 2. <strong>Lock Acquisition Timeouts:</strong> Every lock request specifies a strict timeout (e.g., 500ms). If the lock is not granted within the timeout, the transaction immediately releases all held locks and retries with randomized backoff; 3. <strong>Wait-Die / Wound-Wait algorithms:</strong> Use transaction timestamps to decide whether older transactions wound or wait for younger transactions."}
      ]
    }
  ]
}

# Write Module 09
with open(HLD_DIR / "module_09.json", "w", encoding="utf-8") as f:
  json.dump(m09, f, ensure_ascii=False, indent=2)
print("Module 09 written successfully!")
