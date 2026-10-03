"""
Elaborate content generator for Module 10: Deep Dive SQL: PostgreSQL, MySQL & Indexing.
"""
import json
from pathlib import Path

HLD_DIR = Path('content/hld')
HLD_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# MODULE 10: Deep Dive SQL: PostgreSQL, MySQL & Indexing
# ==========================================
m10 = {
  "module_id": "10",
  "module_title": "Deep Dive SQL: PostgreSQL, MySQL & Indexing",
  "description": "Master B-Tree and LSM indexing internals, composite index leftmost prefix rules, covering indexes, ANSI SQL isolation levels, and EXPLAIN query plan optimization.",
  "topics": [
    {
      "id": "btree-and-indexing-internals",
      "title": "B-Tree & LSM Index Internals: Clustered vs Secondary Indexes",
      "definition": "A database index is an auxiliary data structure that enables fast search, range queries, and ordered retrieval without scanning every row in a table. The two foundational storage engine index architectures are B+ Trees (optimized for read-heavy workloads with balanced node fanout) and Log-Structured Merge-Trees (LSM-Trees, optimized for high-throughput write workloads).",
      "why_we_need_it": "A full table scan on a 50-million-row customer table requires reading ~50GB of raw disk blocks, taking 30-60 seconds. A B+ Tree index pinpoints the exact record in 3-4 pointer hops ($O(\\log N)$), completing the lookup in sub-millisecond time (~0.2ms).",
      "real_world_analogy": "The index at the back of a physical 1,000-page textbook: Instead of reading all 1,000 pages line-by-line to find where 'Consistent Hashing' is mentioned (Full Table Scan), you flip to the back alphabetized index (B-Tree), find 'Consistent Hashing -> page 412', and jump directly to that exact page.",
      "how_it_works": "<p>1. <strong>B+ Tree Internals:</strong> A self-balancing search tree where all data records are stored exclusively in leaf nodes. Internal nodes hold only routing keys and child page pointers. A high fanout (branching factor of 100 to 500) ensures a 4-level B+ Tree can index over 100 million rows with a depth of just 4 I/O lookups. Leaf nodes are linked via bidirectional pointers, making range scans (`BETWEEN 10 AND 50`) simple sequential traversals.</p><p>2. <strong>Clustered vs Secondary Indexes:</strong><br>&bull; <em>Clustered Index (MySQL InnoDB Primary Key):</em> The table rows themselves are stored physically ordered inside the leaf pages of the B+ Tree. A table can have only ONE clustered index.<br>&bull; <em>Secondary Index:</em> A separate B+ Tree where leaf nodes do not contain full table rows; instead, they store the indexed column value and a pointer (in Postgres: Heap Tuple ID / TID; in MySQL: the Clustered Primary Key value) requiring a secondary lookup (Index Hop).</p><p>3. <strong>LSM-Tree Internals (RocksDB, Cassandra):</strong> Writes are strictly appended in memory to an active <strong>MemTable</strong> (Skip List) and an on-disk WAL. When the MemTable fills up (e.g. 64MB), it is flushed to disk as an immutable <strong>SSTable</strong> (Sorted String Table). Background Compaction merges and deduplicates overlapping SSTables. Writes are 100% sequential ($O(1)$ disk speed), making LSM-Trees 5-10x faster than B-Trees for write-heavy systems.</p>",
      "conceptual_breakdown": [
        "<strong>Clustered Index Primary Key Trap:</strong> Using random UUIDs as a clustered primary key in MySQL InnoDB causes severe page splitting and fragmentation because random values insert into arbitrary B-Tree leaf pages. Always use monotonic auto-incrementing IDs or ULIDs/UUIDv7.",
        "<strong>B+ Tree vs B-Tree:</strong> In a classic B-Tree, keys and data records are stored in internal nodes as well as leaves. In a B+ Tree, internal nodes only store routing keys, maximizing branch fanout and keeping tree height low.",
        "<strong>Write Amplification:</strong> In B-Trees, updating a 10-byte integer requires writing an entire 8KB or 16KB dirty page to disk. In LSM-Trees, compaction repeatedly rewrites data, producing background write amplification.",
        "<strong>Index Overhead:</strong> Indexes are not free. Every index on a table adds disk storage and slows down `INSERT`, `UPDATE`, and `DELETE` operations because every B-Tree must be rebalanced on write."
      ],
      "arch_diagram": {
        "title": "B+ Tree Index Structure vs LSM-Tree Architecture",
        "tiers": [
          {
            "label": "B+ Tree (Read-Optimized / Postgres / MySQL)",
            "nodes": [
              {
                "name": "Root Page (Level 1)",
                "type": "database",
                "icon": "🌲",
                "what": "Routing keys [100, 500, 1000]",
                "why": "Fanout routes search to intermediate nodes",
                "when": "Query initiation",
                "failure": "Cached in RAM Buffer Pool"
              },
              {
                "name": "Leaf Pages (Level 4)",
                "type": "database",
                "icon": "🍃",
                "what": "Data rows & Bidirectional links",
                "why": "Stores clustered data records / row pointers",
                "when": "Leaf reached",
                "failure": "Double-linked list range traversal"
              }
            ]
          },
          {
            "label": "LSM-Tree (Write-Optimized / Cassandra / RocksDB)",
            "nodes": [
              {
                "name": "MemTable (RAM)",
                "type": "cache",
                "icon": "⚡",
                "what": "In-memory Skip List buffer",
                "why": "Absorbs writes at RAM speed",
                "when": "All INSERT/UPDATE mutations",
                "failure": "Replayed from WAL on crash"
              },
              {
                "name": "Immutable SSTables (Disk)",
                "type": "database",
                "icon": "💾",
                "what": "Sorted String Tables (L0, L1, L2)",
                "why": "Sequential disk storage with Bloom filters",
                "when": "Flushed from MemTable",
                "failure": "Merged via background compaction"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "B+ Tree vs LSM-Tree Storage Engine Matrix",
        "columns": ["Feature", "B+ Tree (Postgres / MySQL InnoDB)", "LSM-Tree (RocksDB / Cassandra / ScyllaDB)"],
        "rows": [
          ["Write Performance", "Slower (Random I/O page updates, page splits)", "Blazing fast (100% sequential append-only writes)"],
          ["Point Read Performance", "Fast & predictable (3-4 disk page reads via tree)", "Moderate (May require checking MemTable + multiple SSTables)"],
          ["Range Scan Performance", "Superior (Leaves linked in continuous sorted order)", "Slower (Must merge iterators across multiple SSTable files)"],
          ["Space Overhead", "Higher (Internal fragmentation from 50-70% page fills)", "Low (High compression ratio on immutable SSTables)"],
          ["Memory Requirement", "Moderate (Buffer pool for hot pages)", "High (Bloom filters and block indexes for every SSTable)"],
          ["Ideal Workloads", "OLTP, E-commerce, Financial Ledgers, Web APIs", "Time-series, Messaging logs, Metrics ingestion, Key-Value"]
        ]
      },
      "tradeoffs": "<strong>B+ Tree:</strong> Best for read-heavy or mixed transactional workloads requiring fast point lookups, predictable range scans, and multi-version concurrency control. <strong>LSM-Tree:</strong> Best for write-heavy workloads (e.g., logging 500,000 events/sec) where write throughput cannot be bottlenecked by random disk I/O.",
      "failure_scenarios": "<strong>Random UUID Primary Key Fragmentation Disaster:</strong> An application uses randomly generated `UUIDv4` as the clustered primary key in MySQL InnoDB. As the table grows to 20 million rows, every new insert lands on an arbitrary leaf page scattered randomly across disk. Leaf pages fill up and trigger continuous expensive 50/50 page splits, degrading insert throughput by 95% and inflating disk storage by 2.5x. <em>Mitigation:</em> Use time-ordered sequential UUIDv7 or ULIDs, or an auto-incrementing BigInt primary key with a secondary unique index on UUID.",
      "common_mistakes": [
        {"mistake": "Adding an index on every single column in a table.", "correction": "Each index adds write overhead. Only index columns that appear in WHERE clauses, JOIN conditions, or ORDER BY statements of high-frequency queries."},
        {"mistake": "Creating a secondary index on low-cardinality columns (e.g. `gender` or `is_active`).", "correction": "B-Tree indexes are inefficient on low-cardinality columns. The query planner will ignore the index and perform a full table scan. Use Partial Indexes or Bitmap Indexes instead."}
      ],
      "interview_questions": [
        {"question": "Why are B+ Trees preferred over Binary Search Trees (BST) or Red-Black Trees for database indexes?", "answer": "Binary Search Trees have a fanout of only 2. For 100 million rows, a BST would have a depth of ~27 levels, requiring up to 27 separate random disk reads per query. A <strong>B+ Tree has a massive fanout of 100 to 500</strong>, meaning a tree depth of only 3 or 4 levels can index hundreds of millions of rows, requiring at most 3-4 disk reads (and the top 2-3 levels typically fit entirely in RAM)."},
        {"question": "What is the difference between a Clustered Index and a Secondary Index in MySQL InnoDB?", "answer": "In MySQL InnoDB, the <strong>Clustered Index</strong> is the table itself: leaf pages contain the complete table row data, physically organized by the Primary Key. A <strong>Secondary Index</strong> is an independent B+ Tree where leaf pages store only the indexed column value and the corresponding Primary Key. When querying via a secondary index, the engine first traverses the secondary index to find the primary key, and then traverses the clustered index to retrieve the full row (an operation known as an Index Lookup or Bookmark Lookup)."}
      ]
    },
    {
      "id": "composite-and-covering-indexes",
      "title": "Composite Indexes, Leftmost Prefix Rule & Covering Indexes",
      "definition": "A Composite Index is an index built across multiple columns in a specific order (e.g., `INDEX (tenant_id, status, created_at)`). The Leftmost Prefix Rule dictates that the query planner can only utilize the index if the query filters on a contiguous sequence of columns starting from the very first column. A Covering Index contains all columns requested by a query, allowing the database to satisfy the query entirely from the index leaf pages without ever touching the underlying table heap.",
      "why_we_need_it": "Separate single-column indexes on `(status)` and `(created_at)` force the database to scan one index and filter the other in memory. A composite index satisfies both filters and sorts simultaneously, dropping execution time from 1,200ms to 2ms. A covering index eliminates the expensive secondary table heap lookup altogether.",
      "real_world_analogy": "A physical telephone directory indexed by `(Last_Name, First_Name, City)`. You can effortlessly find people if you know their Last Name ('Smith'), or Last Name + First Name ('Smith, John'). But if someone asks you to find everyone named 'John' without providing a Last Name, the book's alphabetical order is useless—you have to scan the entire phone book from cover to cover.",
      "how_it_works": "<p>1. <strong>Leftmost Prefix Rule:</strong> For an index on `(A, B, C)`:<br>&bull; `WHERE A = 1` &rarr; Uses index (Column A).<br>&bull; `WHERE A = 1 AND B = 2` &rarr; Uses index (Columns A and B).<br>&bull; `WHERE A = 1 AND B = 2 AND C = 3` &rarr; Uses index (Columns A, B, and C).<br>&bull; `WHERE B = 2` or `WHERE C = 3` &rarr; <strong>CANNOT USE INDEX</strong> (fails leftmost rule).<br>&bull; `WHERE A = 1 AND C = 3` &rarr; Uses index for A, but must evaluate C via filtering.</p><p>2. <strong>Range Query Cutoff:</strong> If a range condition (`>`, `<`, `BETWEEN`, `LIKE 'prefix%'`) is used on a column, subsequent columns in the composite index *cannot* be used for index searching. For example, in `WHERE A = 1 AND B > 10 AND C = 5`, the index searches on A and B, but cannot search on C.</p><p>3. <strong>Covering Indexes (`Using Index`):</strong> When a query only requests columns that are present inside the index: `SELECT user_id, email FROM users WHERE user_id = 42;`. If `(user_id, email)` is an index, the database extracts the values directly from the index B+ Tree leaf page, completely bypassing the table heap/data pages. In PostgreSQL, this displays as `Index Only Scan`; in MySQL, `Using index`.</p><p>4. <strong>PostgreSQL `INCLUDE` Clause:</strong> Modern databases allow non-key payload columns to be attached to the leaf pages of an index without making them part of the search B-Tree: `CREATE INDEX idx_user ON users (user_id) INCLUDE (email, status);`. This enables covering index scans without inflating intermediate B-Tree routing nodes.</p>",
      "conceptual_breakdown": [
        "<strong>Column Ordering Rule:</strong> Place Equality columns first, followed by Sorting columns, followed by Range columns (Equality &rarr; Sort &rarr; Range).",
        "<strong>Index-Only Scan:</strong> The Holy Grail of SQL optimization. Eliminates random disk I/O to the table heap, speeding up high-frequency API endpoints by 10x-50x.",
        "<strong>PostgreSQL Visibility Map:</strong> For Postgres to execute an Index-Only Scan, the corresponding table heap page must be marked as all-visible in the Visibility Map; otherwise, it must verify tuple visibility against MVCC in the heap.",
        "<strong>Multi-Index Scans (Bitmap Index Scan):</strong> If separate indexes exist on Column A and Column B, Postgres can scan both indexes, build two in-memory bitmaps, compute a bitwise `AND`, and fetch matching heap pages."
      ],
      "arch_diagram": {
        "title": "Covering Index (Index-Only Scan) vs Table Heap Lookup",
        "tiers": [
          {
            "label": "SQL Query Request",
            "nodes": [
              {
                "name": "SELECT id, email FROM users",
                "type": "client",
                "icon": "🔍",
                "what": "WHERE tenant_id = 5",
                "why": "Client requests 2 columns",
                "when": "API call",
                "failure": "Query planner picks optimal path"
              }
            ]
          },
          {
            "label": "Composite Covering Index (tenant_id, email)",
            "nodes": [
              {
                "name": "B+ Tree Index Leaves",
                "type": "database",
                "icon": "🍃",
                "what": "Contains [tenant_id, email, id]",
                "why": "All requested columns live inside index leaf!",
                "when": "Covering scan hit",
                "failure": "Returns immediately: ZERO heap I/O!"
              }
            ]
          },
          {
            "label": "Bypassed Table Heap (Unused)",
            "nodes": [
              {
                "name": "Raw Table Data Heap Pages",
                "type": "database",
                "icon": "💾",
                "what": "Full 50GB table data blocks",
                "why": "Contains remaining 40 columns",
                "when": "Only accessed if index lacks requested column",
                "failure": "Random I/O avoided completely!"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Index Scan Types Comparison",
        "columns": ["Scan Type", "Heap Access Required", "Relative Speed", "Cost Metric"],
        "rows": [
          ["Sequential Scan (Table Scan)", "Reads 100% of table heap pages", "Slowest (O(N))", "High disk I/O, saturates buffer pool"],
          ["Index Scan", "Reads index, then fetches row from heap", "Fast (O(log N) + random heap read)", "Moderate (Random I/O per matched row)"],
          ["Bitmap Index Scan", "Reads index, builds RAM bitmap, batches heap reads", "Fast for multi-row results", "Converts random heap I/O into sequential chunks"],
          ["Index-Only Scan (Covering)", "ZERO heap access (all data in index)", "Blazing fast (sub-millisecond)", "Optimal (Zero table heap disk lookups)"]
        ]
      },
      "tradeoffs": "<strong>Covering Index Trade-off:</strong> Attaching extra columns (`INCLUDE (email, created_at)`) expands the physical disk size of the index B+ Tree and consumes more Buffer Pool RAM. However, it completely eliminates table heap lookups, making it an essential pattern for hot API endpoints.",
      "failure_scenarios": "<strong>The Unusable Index in Production:</strong> A developer builds a composite index on `(created_at, status)`. The API endpoint runs: `SELECT * FROM orders WHERE status = 'PENDING' ORDER BY created_at DESC`. Because the query filters by `status` without specifying `created_at` first, it violates the Leftmost Prefix Rule. The database ignores the index and performs a full-table sequential scan, spiking query latency to 8 seconds. <em>Mitigation:</em> Reorder the composite index columns to `(status, created_at)`.",
      "common_mistakes": [
        {"mistake": "Applying functions or math to indexed columns in WHERE clauses (e.g. `WHERE YEAR(created_at) = 2026` or `WHERE LOWER(email) = 'user@example.com'`).", "correction": "Wrapping an indexed column in a function disables B-Tree search. Use Expression / Functional Indexes (`CREATE INDEX ON users (LOWER(email))`) or range bounds: `WHERE created_at >= '2026-01-01' AND created_at < '2027-01-01'`."},
        {"mistake": "Assuming `SELECT *` can use a covering index.", "correction": "`SELECT *` requests all columns, forcing the engine to fetch the table heap. Explicitly select only the indexed columns to enable an Index-Only Scan."}
      ],
      "interview_questions": [
        {"question": "Given an index on (A, B, C), will the query `SELECT * FROM tbl WHERE A = 5 AND C = 10` use the index?", "answer": "Yes, but only for column A. The engine uses the index to narrow down rows where $A = 5$. However, because column B was omitted from the filter condition, the engine cannot use the index to seek on $C = 10$. It must evaluate $C = 10$ as a secondary filter across all matching $A = 5$ index entries or heap rows."},
        {"question": "How do you design an optimal composite index for a query with an equality filter, a range filter, and an ORDER BY clause?", "answer": "Follow the <strong>Equality &rarr; Sort &rarr; Range</strong> rule. 1. Place columns with exact equality filters (`status = 'ACTIVE'`) first; 2. Place the sorting column (`ORDER BY created_at`) second to avoid an in-memory Filesort; 3. Place range filter columns (`amount > 100`) last. For example: `INDEX (status, created_at, amount)`."}
      ]
    },
    {
      "id": "transaction-isolation-levels",
      "title": "SQL Isolation Levels: Dirty Read, Non-Repeatable Read & Phantom Read",
      "definition": "ANSI SQL defines four standard transaction isolation levels (Read Uncommitted, Read Committed, Repeatable Read, and Serializable) that specify the degree to which concurrent transactions are insulated from each other's uncommitted or intermediate state changes. Higher isolation levels eliminate concurrency anomalies at the expense of locking overhead and reduced throughput.",
      "why_we_need_it": "Without transaction isolation, concurrent users transferring money, modifying shopping carts, or reserving concert tickets will overwrite each other's data, read phantom rows, and calculate incorrect balances.",
      "real_world_analogy": "Drafting documents in a shared office: Read Uncommitted is peeking over a colleague's shoulder while they are typing a draft that they might delete 5 seconds later. Read Committed is reading only memos that have been formally signed and stamped. Repeatable Read is taking a photocopy of the filing cabinet into your private office so nobody can alter what you are reading. Serializable is locking everyone else out of the entire building so only one person can work at a time.",
      "how_it_works": "<p>1. <strong>Read Uncommitted:</strong> Transactions can read rows that have been modified by concurrent transactions but not yet committed. Suffers from <strong>Dirty Reads</strong> (reading data that gets rolled back).</p><p>2. <strong>Read Committed (Postgres & Oracle Default):</strong> Guarantees transactions only read committed data. Every single `SELECT` statement acquires a fresh snapshot of committed rows. Prevents Dirty Reads, but vulnerable to <strong>Non-Repeatable Reads</strong> (reading row X, another transaction commits an update to X, reading row X again returns different values).</p><p>3. <strong>Repeatable Read (MySQL InnoDB Default):</strong> Guarantees that any row read during a transaction will return the identical values throughout the entire transaction. Uses MVCC snapshots established at the <em>beginning of the transaction</em>. In ANSI SQL, it permits <strong>Phantom Reads</strong> (new rows inserted by another transaction appearing in range queries), though MySQL InnoDB prevents phantom reads using Next-Key Locks.</p><p>4. <strong>Serializable:</strong> The highest isolation level. Guarantees execution is equivalent to running transactions serially (one after another). Implemented via Strict Two-Phase Locking (S2PL) or Serializable Snapshot Isolation (SSI in PostgreSQL) which tracks read-write dependency cycles (rw-antidependencies) in a lock-free manner and aborts conflicting transactions.</p>",
      "conceptual_breakdown": [
        "<strong>Dirty Read:</strong> Transaction A updates balance to $1000 without committing. Transaction B reads $1000. Transaction A aborts/rolls back. Transaction B operated on phantom dirty data that never officially existed.",
        "<strong>Non-Repeatable Read:</strong> Transaction A reads user status 'ACTIVE'. Transaction B updates status to 'BANNED' and commits. Transaction A reads user status again and sees 'BANNED'.",
        "<strong>Phantom Read:</strong> Transaction A queries `SELECT COUNT(*) FROM users WHERE age > 30` (returns 10). Transaction B inserts a new 35-year-old user and commits. Transaction A runs the count again and gets 11.",
        "<strong>Write Skew Anomaly:</strong> Occurs in Repeatable Read: two concurrent transactions evaluate an invariant across multiple rows (e.g. 'at least one doctor must be on call'). Both see 2 doctors on call, so both update their respective doctor status to 'OFF CALL' and commit, leaving ZERO doctors on call! Prevented only by Serializable isolation or explicit row locks."
      ],
      "arch_diagram": {
        "title": "SQL Isolation Levels & Concurrency Anomalies Hierarchy",
        "tiers": [
          {
            "label": "Isolation Level Hierarchy",
            "nodes": [
              {
                "name": "Read Uncommitted",
                "type": "database",
                "icon": "⚠️",
                "what": "Vulnerable to Dirty Reads",
                "why": "Zero locking, maximum throughput",
                "when": "Almost never in production",
                "failure": "Reads aborted data"
              },
              {
                "name": "Read Committed",
                "type": "database",
                "icon": "🛡️",
                "what": "Prevents Dirty Reads",
                "why": "PostgreSQL default; fresh snapshot per statement",
                "when": "Standard web apps",
                "failure": "Non-repeatable reads possible"
              },
              {
                "name": "Repeatable Read",
                "type": "database",
                "icon": "🔒",
                "what": "Prevents Non-Repeatable Reads",
                "why": "MySQL InnoDB default; snapshot per transaction",
                "when": "Reporting, complex forms",
                "failure": "Write skew anomaly possible"
              },
              {
                "name": "Serializable",
                "type": "database",
                "icon": "👑",
                "what": "Prevents All Anomalies",
                "why": "Strict 2PL or SSI graph tracking",
                "when": "High-risk financial ledgers",
                "failure": "Aborts transactions on conflict"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "ANSI SQL Isolation Levels vs Anomalies Matrix",
        "columns": ["Isolation Level", "Dirty Read", "Non-Repeatable Read", "Phantom Read", "Write Skew"],
        "rows": [
          ["Read Uncommitted", "Permitted", "Permitted", "Permitted", "Permitted"],
          ["Read Committed (Postgres Default)", "Prevented", "Permitted", "Permitted", "Permitted"],
          ["Repeatable Read (MySQL Default)", "Prevented", "Prevented", "Permitted (Prevented in InnoDB)", "Permitted"],
          ["Serializable", "Prevented", "Prevented", "Prevented", "Prevented"]
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> Increasing isolation from Read Committed to Serializable guarantees 100% mathematical correctness, but increases transaction abort rates and lock contention. In high-concurrency systems, Serializable transactions must be accompanied by application-level retry loops with exponential backoff.",
      "failure_scenarios": "<strong>The On-Call Doctor Write Skew Disaster:</strong> A hospital system requires at least one doctor active. Alice and Bob are currently on call. Both simultaneously submit a request to take time off. Under Repeatable Read isolation, Alice's transaction checks `SELECT COUNT(*) FROM on_call` (returns 2), and Bob's transaction checks the same count (returns 2). Both transactions update their status to OFF and commit successfully. The hospital has NO doctors on call. <em>Mitigation:</em> Use `SERIALIZABLE` isolation or explicit lock elevation (`SELECT ... FOR UPDATE`).",
      "common_mistakes": [
        {"mistake": "Assuming that Repeatable Read prevents all concurrency bugs.", "correction": "Repeatable Read permits Write Skew and Read-Only Transaction Anomalies. For complex multi-row invariant validation, use Serializable or explicit locks."},
        {"mistake": "Not writing application-level retry logic when using Serializable isolation.", "correction": "Serializable engines abort transactions that encounter serialization conflicts. Applications MUST catch 40001 serialization errors and retry automatically."}
      ],
      "interview_questions": [
        {"question": "What is Write Skew and why does Repeatable Read fail to prevent it?", "answer": "<strong>Write Skew</strong> occurs when two concurrent transactions read overlapping data sets, satisfy an invariant, and then make disjoint writes that collectively violate the invariant. Because each transaction writes to a different row, row-level locks and MVCC snapshots in Repeatable Read detect no write conflict, allowing both to commit. Only <strong>Serializable isolation</strong> detects the cross-transaction dependency cycle and aborts one."},
        {"question": "How does MySQL InnoDB prevent Phantom Reads in Repeatable Read?", "answer": "MySQL InnoDB uses <strong>Next-Key Locking</strong> (a combination of a record lock and a gap lock). When executing a range query like `SELECT * FROM orders WHERE id > 100 FOR UPDATE`, InnoDB locks not only the existing matching index records, but also the 'gaps' between them and beyond. If a concurrent transaction tries to `INSERT` a new record into that gap, it is blocked until the first transaction commits."}
      ]
    },
    {
      "id": "query-optimization-and-explain",
      "title": "Query Planning, EXPLAIN ANALYZE & Slow Query Optimization",
      "definition": "Query optimization is the process by which a database Cost-Based Optimizer (CBO) analyzes SQL syntax, evaluates available indexes, inspects table statistics (histograms), and generates the lowest-cost physical execution plan. `EXPLAIN` shows the estimated query execution plan, while `EXPLAIN ANALYZE` executes the query in real time and reports exact node execution latencies and memory usage.",
      "why_we_need_it": "A poorly written SQL query with an accidental Cartesian product (Cross Join) or an unindexed subquery can consume 100% of database CPU, locking worker threads and causing a company-wide production outage. Profiling queries with `EXPLAIN ANALYZE` is the core diagnostic skill for database engineering.",
      "real_world_analogy": "GPS navigation: When you input a destination, the GPS engine (Cost-Based Optimizer) calculates multiple routes (highways, side streets, toll roads), estimates drive times using live traffic statistics, and picks the fastest route. Running `EXPLAIN ANALYZE` is driving the route with a stopwatch to measure the exact seconds spent at every traffic light.",
      "how_it_works": "<p>1. <strong>Optimizer Lifecycle:</strong> SQL Parser &rarr; Rewriter (view expansion) &rarr; Cost-Based Optimizer (CBO) &rarr; Physical Plan Generator &rarr; Execution Engine.</p><p>2. <strong>Cost Metric:</strong> The optimizer estimates cost in arbitrary units based on disk I/O and CPU: $\\text{Cost} = (\\text{Disk Pages Read} \\times 1.0) + (\\text{CPU Tuples Processed} \\times 0.01)$. The path with the minimum total cost wins.</p><p>3. <strong>Common Execution Plan Nodes:</strong><br>&bull; <em>Seq Scan (Full Table Scan):</em> Reads every block from disk ($O(N)$). Red flag on large tables.<br>&bull; <em>Index Scan:</em> Traverses B+ Tree and fetches matching heap pages ($O(\\log N)$).<br>&bull; <em>Index Only Scan:</em> Satisfies query entirely from index; zero heap reads.<br>&bull; <em>Nested Loop Join:</em> For every row in outer table, loops through inner table. Fast with indexes and small datasets.<br>&bull; <em>Hash Join:</em> Builds an in-memory hash table of the smaller table, then streams the larger table through it. Best for large unindexed joins.<br>&bull; <em>Merge Join:</em> Both tables are sorted on the join key and zipped together sequentially.</p><p>4. <strong>Table Statistics & ANALYZE:</strong> The CBO relies on `pg_statistic` (histograms, most common values / MCV, null fractions). If statistics are stale, the optimizer can miscalculate costs by 1,000,000x and choose a disastrous sequential scan. Running `ANALYZE table_name` updates statistics.</p>",
      "conceptual_breakdown": [
        "<strong>EXPLAIN vs EXPLAIN ANALYZE:</strong> `EXPLAIN` is an estimate (never runs the query, safe for deletes); `EXPLAIN ANALYZE` executes the query for real and reports actual timings (never run with an uncommitted `DELETE` in production!).",
        "<strong>Buffers Metric in Postgres:</strong> Always run `EXPLAIN (ANALYZE, BUFFERS)` to see memory hits: `Buffers: shared hit=421 read=12`. `hit` came from RAM cache; `read` came from physical disk.",
        "<strong>The N+1 Query Anti-Pattern:</strong> Application code fetches 100 orders, and then inside a loop executes 100 individual queries to fetch each customer (`SELECT * FROM customers WHERE id = ?`). Replace with a single join or `WHERE id IN (...)`.",
        "<strong>Work_Mem & External Merge Disk Spills:</strong> If an `ORDER BY` or `Hash Join` exceeds the database's `work_mem` setting (e.g. 4MB), the engine spills the sort to temporary disk files, degrading performance by 100x. Increase `work_mem` for analytical queries."
      ],
      "arch_diagram": {
        "title": "Cost-Based Query Optimizer Pipeline",
        "tiers": [
          {
            "label": "Parser & Rewriter",
            "nodes": [
              {
                "name": "SQL Text Input",
                "type": "client",
                "icon": "📝",
                "what": "Raw SELECT query",
                "why": "Declarative syntax",
                "when": "Client query dispatch",
                "failure": "Syntax / permission error"
              },
              {
                "name": "Abstract Syntax Tree",
                "type": "service",
                "icon": "🌳",
                "what": "Parsed relational algebra",
                "why": "Validates table schemas & types",
                "when": "Compilation phase",
                "failure": "Rejects invalid column names"
              }
            ]
          },
          {
            "label": "Cost-Based Optimizer (CBO)",
            "nodes": [
              {
                "name": "Statistics Engine (pg_statistic)",
                "type": "database",
                "icon": "📊",
                "what": "Histograms & Frequency Lists",
                "why": "Estimates row selectivity",
                "when": "Updated by autovacuum/analyze",
                "failure": "Stale stats cause bad plan choices"
              },
              {
                "name": "Plan Tree Cost Evaluator",
                "type": "service",
                "icon": "🧮",
                "what": "Compares Index Scan vs Seq Scan",
                "why": "Selects plan with lowest calculated cost",
                "when": "Every query execution",
                "failure": "Generates optimal physical plan"
              }
            ]
          },
          {
            "label": "Execution Engine",
            "nodes": [
              {
                "name": "Physical Execution Engine",
                "type": "database",
                "icon": "⚡",
                "what": "Iterates plan tree (Index Scan -> Hash Join)",
                "why": "Streams result tuples to client socket",
                "when": "Runtime execution",
                "failure": "Work_mem spill to disk if memory exceeded"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "SQL Join Strategies Comparison",
        "columns": ["Join Algorithm", "Memory Requirement", "Best Dataset Size", "Requires Sorted Input?"],
        "rows": [
          ["Nested Loop", "Minimal (O(1))", "Small outer table + Indexed inner table", "No"],
          ["Hash Join", "High (O(M) memory for in-memory hash table)", "Medium-to-large unindexed datasets", "No"],
          ["Merge Join", "Low-to-moderate", "Large datasets with pre-sorted keys (or B-Tree indexed)", "Yes (Input tables must be sorted on join key)"]
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> The optimizer evaluates join permutations ($N!$). For complex queries with 12+ tables, the planning phase itself can take longer than query execution. Databases use genetic query algorithms (GEQO) to approximate optimal plans when table counts exceed thresholds.",
      "failure_scenarios": "<strong>The Stale Statistics Disconnect:</strong> A company imports 10 million new orders in a bulk batch overnight. The database autovacuum has not updated statistics yet, so the optimizer believes the table has only 1,000 rows. It chooses a Nested Loop Join instead of a Hash Join, causing a 5-minute CPU lockup that halts all checkout processing. <em>Mitigation:</em> Explicitly trigger `ANALYZE orders;` immediately following bulk data loads.",
      "common_mistakes": [
        {"mistake": "Running `EXPLAIN ANALYZE DELETE FROM orders;` in production to check performance.", "correction": "`EXPLAIN ANALYZE` actually executes the statement! Always wrap test mutations in a transaction that you rollback: `BEGIN; EXPLAIN ANALYZE ...; ROLLBACK;`."},
        {"mistake": "Using `LIKE '%keyword%'` with a leading wildcard and wondering why the B-Tree index is not used.", "correction": "Leading wildcards cannot use B-Tree indexes. Use PostgreSQL Full-Text Search with a GIN index, or Trigram indexes (`pg_trgm`)."}
      ],
      "interview_questions": [
        {"question": "How do you diagnose and fix a slow SQL query in a production environment?", "answer": "1. Identify the slow query using database slow query logs (`pg_stat_statements` or MySQL Slow Query Log);<br>2. Run `EXPLAIN (ANALYZE, BUFFERS)` to inspect the execution plan;<br>3. Check for high-cost nodes: look for `Seq Scan` on large tables, high `Rows Removed by Filter`, disk spills in `Sort Method: external merge Disk`, or massive discrepancies between estimated rows and actual rows;<br>4. Remediate: Add missing composite/covering indexes, update stale table statistics via `ANALYZE`, increase `work_mem` to prevent disk spills, or rewrite queries to eliminate correlated subqueries."},
        {"question": "What is the difference between a Nested Loop Join and a Hash Join?", "answer": "A <strong>Nested Loop Join</strong> takes each row from the outer table and performs a lookup into the inner table (optimal when the outer table is tiny and the inner table has a B-Tree index on the join key). A <strong>Hash Join</strong> scans the smaller table, builds an in-memory hash table of join keys in RAM, and then scans the second table probing the hash table (optimal for joining large, unindexed datasets where reading the tables sequentially is faster than random index hops)."}
      ]
    }
  ]
}

# Write Module 10
with open(HLD_DIR / "module_10.json", "w", encoding="utf-8") as f:
  json.dump(m10, f, ensure_ascii=False, indent=2)
print("Module 10 written successfully!")
