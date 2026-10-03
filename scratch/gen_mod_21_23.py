"""
Elaborate generator for Modules 21, 22, and 23.
Matches exact topics from app/data/hld_roadmap.json
"""
import json
from pathlib import Path

HLD_DIR = Path('content/hld')
HLD_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# MODULE 21: Distributed Search Systems: Elasticsearch & Inverted Index
# ==========================================
m21 = {
  "module_id": "21",
  "module_title": "Distributed Search Systems: Elasticsearch & Inverted Index",
  "description": "Master distributed search: Inverted index mechanics, tokenization, BM25 scoring, Elasticsearch cluster architecture (Master/Data/Coordinating nodes), shard routing, Translog write durability, and real-time typeahead autocomplete.",
  "topics": [
    {
      "id": "inverted-index-and-tokenization",
      "title": "The Inverted Index: Tokenization, Stemming, Stop Words & Postings Lists",
      "definition": "An Inverted Index is the foundational data structure of search engines (Elasticsearch, Apache Lucene). Instead of mapping documents to words (like a normal document store), it inverts the relationship: mapping every unique word (Term) to a sorted list of Document IDs where that word appears (Postings List). Tokenization, normalization, stemming, and stop-word filtering convert raw unstructured text into searchable index terms.",
      "why_we_need_it": "Searching for the words 'distributed caching' across 100 million product descriptions in SQL using `WHERE description LIKE '%distributed caching%'` requires a full-table sequential scan that takes minutes and consumes 100% CPU. An Inverted Index looks up the terms 'distributed' and 'caching' in O(1) time and intersects their Postings Lists in sub-millisecond time.",
      "real_world_analogy": "The glossary at the back of an encyclopedia: Instead of reading all 20 volumes page-by-page to find where 'Julius Caesar' is mentioned, you flip to the back alphabetized index. Under 'Caesar, Julius', you see the exact page numbers: [Page 12, Page 45, Page 302]. The page numbers are the Postings List.",
      "how_it_works": "<p>1. <strong>Analysis Pipeline (Text to Terms):</strong> When text is indexed, it passes through an Analyzer composed of three components:<br>&bull; <em>Character Filters:</em> Strips HTML tags (`<p>`) and converts symbols (`&` &rarr; `and`).<br>&bull; <em>Tokenizer:</em> Splits text stream into discrete tokens by whitespace and punctuation.<br>&bull; <em>Token Filters:</em> Applies Lowercasing, Stop Word removal (filters out 'the', 'is', 'at'), Stemming (reduces 'running', 'runs', 'ran' to root 'run' via the Porter Stemmer algorithm), and Synonyms ('fast' &rarr; 'quick').</p><p>2. <strong>The Postings List:</strong> For each analyzed term, Lucene maintains a sorted array of document IDs along with term frequency (TF) and byte positions (for phrase queries like `'distributed' followed immediately by 'caching'`).</p><p>3. <strong>Postings List Compression & Intersection:</strong> Postings lists are compressed using delta-encoding and bit-packing (Frame of Reference / Roaring Bitmaps). To evaluate a multi-word search (`distributed AND caching`), the search engine performs an ultra-fast bitwise intersection of the two sorted postings lists using skip pointers in $O(M + N)$ time.</p><p>4. <strong>FST (Finite State Transducer):</strong> Lucene stores the dictionary of all unique terms in a compressed memory structure called an FST, allowing instant prefix lookups and fuzzy matching within L1/L2 CPU cache.</p>",
      "conceptual_breakdown": [
        "<strong>Term Dictionary + Postings List:</strong> The Term Dictionary stores all unique terms sorted alphabetically; the Postings List stores the Document IDs containing each term.",
        "<strong>Roaring Bitmaps:</strong> Compressed bitmap format that accelerates boolean search intersections (`AND`, `OR`, `NOT`) by orders of magnitude.",
        "<strong>Stemming Trade-off:</strong> Aggressive stemming increases recall (finding related words) at the expense of precision (accidentally matching unrelated words).",
        "<strong>Position Vectors for Phrase Search:</strong> Storing word offset positions allows executing exact phrase queries (`'system design'`) and proximity queries (`'load balancer' within 3 words of 'latency'`)."
      ],
      "arch_diagram": {
        "title": "Inverted Index Generation Pipeline (Text -> Tokenizer -> Postings List)",
        "tiers": [
          {
            "label": "Document Ingestion & Analysis Tier",
            "nodes": [
              {
                "name": "Raw Document Ingest",
                "type": "client",
                "icon": "📄",
                "what": "Doc 1: 'The quick brown fox jumps'",
                "why": "Unstructured text input",
                "when": "Indexing request",
                "failure": "Buffers in translog"
              },
              {
                "name": "Text Analyzer Engine",
                "type": "service",
                "icon": "⚙️",
                "what": "Lowercase + Stemming + Stop Words",
                "why": "Extracts normalized terms: ['quick', 'brown', 'fox', 'jump']",
                "when": "Analysis pipeline",
                "failure": "Fallback to standard analyzer"
              }
            ]
          },
          {
            "label": "Inverted Index Storage Tier (Lucene)",
            "nodes": [
              {
                "name": "Term Dictionary (FST in RAM)",
                "type": "cache",
                "icon": "📖",
                "what": "Alphabetized Terms: ['brown', 'fox', 'jump', 'quick']",
                "why": "O(1) memory lookup for search terms",
                "when": "Query evaluation",
                "failure": "Persisted in immutable segment"
              },
              {
                "name": "Postings Lists (Disk/PageCache)",
                "type": "database",
                "icon": "📜",
                "what": "'fox' -> [Doc 1, Doc 4, Doc 12] | 'quick' -> [Doc 1, Doc 8]",
                "why": "Sorted doc IDs for bitwise intersection",
                "when": "Search execution",
                "failure": "Replicated across shard replicas"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Forward Index vs Inverted Index",
        "columns": ["Dimension", "Forward Index (Standard DB)", "Inverted Index (Search Engine)"],
        "rows": [
          ["Mapping Direction", "Document ID -> List of Words", "Word (Term) -> List of Document IDs"],
          ["Full-Text Search Speed", "Slow (Requires scanning every document: O(N))", "Blazing fast (Direct Term lookup + Postings intersection: O(1))"],
          ["Update Complexity", "Simple (Direct append or overwrite)", "Complex (Must update multiple term postings lists)"],
          ["Storage Overhead", "Low (Stores original text only)", "Higher (Stores term dictionary, postings, position offsets)"],
          ["Primary Engines", "PostgreSQL, MongoDB, MySQL", "Elasticsearch, Apache Solr, Typesense, Meilisearch"]
        ]
      },
      "tradeoffs": "<strong>Inverted Index:</strong> Delivers sub-10ms full-text and phrase search across billions of documents, but updates and inserts are CPU-intensive because a single document mutation requires modifying dozens of individual term postings lists.",
      "failure_scenarios": "<strong>The Wildcard Prefix Search Meltdown:</strong> A user executes a search query with a leading wildcard: `*caching`. Because the Term Dictionary is a forward-sorted B-Tree / FST (sorted alphabetically from A to Z), a leading wildcard cannot use the index. Elasticsearch is forced to iterate through every single term in the entire cluster's term dictionary (millions of terms), sending CPU to 100% across all data nodes. <em>Mitigation:</em> Forbid leading wildcards in search APIs, or index reverse tokens / use N-gram tokenizers.",
      "common_mistakes": [
        {"mistake": "Using `LIKE '%keyword%'` in a relational database for large-scale production search.", "correction": "Relational B-Tree indexes cannot index substring searches. Use an inverted index engine like Elasticsearch or PostgreSQL GIN indexes."},
        {"mistake": "Indexing full high-cardinality raw text fields with keyword analyzers without disabling fielddata.", "correction": "Enabling fielddata on text fields for sorting or aggregations loads all terms into JVM heap memory, quickly triggering Out Of Memory (OOM) crashes."}
      ],
      "interview_questions": [
        {"question": "How does an Inverted Index evaluate a multi-term search query like 'distributed systems'?", "answer": "1. <strong>Tokenization:</strong> The query is analyzed into two terms: `'distributed'` and `'system'`;<br>2. <strong>Term Lookup:</strong> The engine looks up both terms in the in-memory Term Dictionary (FST) to locate their respective on-disk Postings Lists: e.g. `distributed -> [Doc 2, Doc 5, Doc 8, Doc 15]` and `system -> [Doc 5, Doc 8, Doc 20]`;<br>3. <strong>Postings Intersection:</strong> The engine performs a <strong>bitwise intersection</strong> of the two sorted lists using skip pointers in $O(M + N)$ time, identifying the matching documents: `[Doc 5, Doc 8]`;<br>4. <strong>Relevance Scoring:</strong> Computes the BM25 relevance score for each matching document and returns the top $K$ sorted results."},
        {"question": "What is the purpose of Stop Words and Stemming in search analysis?", "answer": "<strong>Stop Words</strong> are extremely common words (e.g. 'the', 'is', 'at', 'and') that appear in almost every document and provide zero discriminatory search value. Filtering them out saves 30-40% of postings list storage and accelerates query processing. <strong>Stemming</strong> reduces words to their grammatical root form (e.g. 'engineering', 'engineer', 'engineered' all reduce to 'engin'). This maximizes <em>Search Recall</em>, allowing a user who searches for 'engineer' to match documents containing 'engineering'."}
      ]
    },
    {
      "id": "elasticsearch-architecture-and-sharding",
      "title": "Elasticsearch Architecture: Master/Data/Coordinating Nodes & Primary vs Replica Shards",
      "definition": "Elasticsearch is a distributed, JSON-native search and analytics engine built on Apache Lucene. A cluster consists of specialized node roles: Master Nodes (cluster state and metadata), Data Nodes (holding shards and executing search/indexing I/O), and Coordinating Nodes (routing client requests and aggregating scatter-gather search results). Data is horizontally partitioned into Primary and Replica Shards.",
      "why_we_need_it": "A single Lucene index cannot scale past ~2 billion documents or the disk limits of a single machine. Elasticsearch automatically shards Lucene indexes across dozens of physical machines, distributes search queries in parallel, and provides automatic high-availability failover.",
      "real_world_analogy": "A national postal sorting facility: The Master Node is the station manager (maintains the master map of which truck goes to which city). The Data Nodes are the postal sorting warehouses with loading docks (store actual packages and scan barcodes). The Coordinating Nodes are the front-desk intake clerks: they accept a customer's package, check the master map, and hand it to the correct sorting warehouse.",
      "how_it_works": "<p>1. <strong>Dedicated Node Roles:</strong> In production clusters, node roles are strictly separated:<br>&bull; <em>Master-Eligible Nodes (`node.master: true`):</em> Only manage cluster state, index creation, and shard routing. Do not store data or handle search queries (protects them from high memory load).<br>&bull; <em>Data Nodes (`node.data: true`):</em> Store shards on SSDs and execute CPU/memory-heavy search, indexing, and aggregations.<br>&bull; <em>Coordinating Nodes (`node.roles: []`):</em> Act as smart load balancers. They parse client HTTP requests, scatter searches to relevant data shards, and gather/merge top results before returning JSON to the client.</p><p>2. <strong>Primary & Replica Shards:</strong> Each Elasticsearch index is divided into $N$ Primary Shards (immutable after creation) and $M$ Replica Shards. An individual shard is a <em>fully functional, self-contained Apache Lucene index</em>. Writes route to the Primary Shard, which concurrently replicates to Replica Shards. Reads can execute against either Primary or Replica shards, multiplying read throughput.</p><p>3. <strong>Shard Routing Formula:</strong> $\\text{Shard} = \\text{Murmur3}(\\text{routing\\_key}) \\pmod{\\text{primary\\_shards}}$. Default routing key is the document `_id`.</p><p>4. <strong>Cluster Resiliency:</strong> If a data node hosting Primary Shard 1 crashes, the Master node immediately promotes Replica Shard 1 on a surviving node to Primary, and provisions a new replica elsewhere with zero downtime.</p>",
      "conceptual_breakdown": [
        "<strong>Primary Shard Immutability:</strong> The number of primary shards on an index CANNOT be changed after creation (because changing $N$ breaks `hash(id) % N`). You must reindex into a new index to change primary shard counts.",
        "<strong>Split-Brain Protection:</strong> Elasticsearch uses Raft-like master quorum consensus. A master can only be elected if approved by a majority of master-eligible nodes (`(N/2) + 1`).",
        "<strong>Shard Size Rule of Thumb:</strong> Target shard sizes between <strong>10GB and 50GB</strong>. Having 1,000 tiny 50MB shards creates massive JVM heap metadata overhead; having a single 500GB shard makes rebalancing and node recovery painfully slow.",
        "<strong>Segment Merging:</strong> Lucene writes immutable segment files. Background merge threads combine smaller segments into larger ones, physically purging deleted records."
      ],
      "arch_diagram": {
        "title": "Elasticsearch Production Cluster Architecture (Master / Data / Coordinating Roles)",
        "tiers": [
          {
            "label": "Client Ingress Tier",
            "nodes": [
              {
                "name": "Coordinating Node (Client Gateway)",
                "type": "lb",
                "icon": "🧭",
                "what": "Scatter-Gather Query Router",
                "why": "Scatters search to data shards; merges top results",
                "when": "Client HTTP REST requests",
                "failure": "Stateless horizontal failover"
              }
            ]
          },
          {
            "label": "Consensus Master Tier (No Data Storage)",
            "nodes": [
              {
                "name": "Dedicated Master Quorum (3 Nodes)",
                "type": "database",
                "icon": "👑",
                "what": "Manages Cluster State & Shard Routing",
                "why": "Isolated from heavy query/indexing CPU load",
                "when": "Cluster state change / failover",
                "failure": "Raft-like majority election"
              }
            ]
          },
          {
            "label": "Sharded Data Storage Tier (Lucene Engines)",
            "nodes": [
              {
                "name": "Data Node 1",
                "type": "database",
                "icon": "💾",
                "what": "Primary Shard 0 (P0) + Replica Shard 1 (R1)",
                "why": "Executes inverted index search & translog writes",
                "when": "Active search/index I/O",
                "failure": "R0 on Node 2 promoted"
              },
              {
                "name": "Data Node 2",
                "type": "database",
                "icon": "💾",
                "what": "Primary Shard 1 (P1) + Replica Shard 0 (R0)",
                "why": "Executes inverted index search & translog writes",
                "when": "Active search/index I/O",
                "failure": "R1 on Node 1 promoted"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Elasticsearch Node Roles Comparison",
        "columns": ["Role", "Configuration", "Responsibilities", "Resource Needs", "Stores Data?"],
        "rows": [
          ["Master-Eligible", "node.roles: [master]", "Maintains cluster state, manages shard allocation, handles failover", "High CPU stability, Low RAM (4-8GB), Fast disk", "NO (Data stored elsewhere)"],
          ["Data Node", "node.roles: [data]", "Executes search queries, indexes documents, performs aggregations", "Massive RAM (32GB heap limit), Fast NVMe SSDs, Multi-core CPU", "YES (Holds primary & replica shards)"],
          ["Coordinating Node", "node.roles: []", "Load balances requests, executes scatter-gather phase 2 merges", "High CPU & Network, Medium RAM for aggregation buffers", "NO (Stateless router)"],
          ["Ingest Node", "node.roles: [ingest]", "Runs pre-processing ingest pipelines (Grok parsing, GeoIP lookup)", "High CPU for regex/transformations", "NO"]
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> Dedicated node roles increase cloud infrastructure costs (paying for separate master and coordinating VMs), but prevent production outages where a heavy analytical query locks a data node's CPU and accidentally kills the cluster master.",
      "failure_scenarios": "<strong>The Shard Explosion JVM Heap OOM Death:</strong> A DevOps team creates a new Elasticsearch index for every customer every day: 500 customers x 365 days = 182,500 indexes x 5 shards = ~1,000,000 shards! Every shard consumes Lucene memory structures in the JVM heap. The data nodes exceed their 32GB JVM heap limits, enter permanent Stop-the-World GC pauses, and the entire cluster collapses. <em>Mitigation:</em> Consolidate into time-based indices with <strong>Index Lifecycle Management (ILM)</strong> and keep total shard count under 20 shards per GB of JVM heap.",
      "common_mistakes": [
        {"mistake": "Setting Elasticsearch JVM heap size to greater than 32GB (e.g. 64GB).", "correction": "Never allocate more than 31GB of JVM heap! At 32GB, the JVM loses Compressed Object Pointers (Compressed OOPs), instantly wasting 50% of your RAM on pointer overhead."},
        {"mistake": "Using a single node role for all servers in a large production cluster.", "correction": "Separate Dedicated Masters from Data Nodes in clusters with >5 nodes to protect cluster stability."}
      ],
      "interview_questions": [
        {"question": "How does Elasticsearch execute a search query across multiple shards (Query-Then-Fetch)?", "answer": "1. <strong>Query Phase:</strong> The coordinating node receives the search request and broadcasts it to one copy (primary or replica) of every shard in the index. Each shard executes the search locally, scores documents using BM25, and returns *only* the matching document IDs and relevance scores (the top $K$ IDs) to the coordinating node;<br>2. <strong>Gather & Merge:</strong> The coordinating node merges the results from all shards, sorts them globally, and identifies the true top $K$ documents (e.g. top 10);<br>3. <strong>Fetch Phase:</strong> The coordinating node sends point requests *only to the specific shards* hosting those top 10 documents to retrieve the full `_source` JSON bodies, minimizing network bandwidth and serialization overhead."},
        {"question": "Why is the number of primary shards immutable in an Elasticsearch index?", "answer": "Elasticsearch routes documents to shards using the formula: $\\text{Shard} = \\text{Murmur3}(\\text{_id}) \\pmod{\\text{num\\_primary\\_shards}}$. If the number of primary shards were changed dynamically, the mathematical hash modulo result for every existing document would point to the wrong shard, making existing documents impossible to locate. Changing primary shards requires creating a new index and running the `_reindex` API."}
      ]
    },
    {
      "id": "relevance-ranking-and-indexing-pipeline",
      "title": "Relevance Scoring: TF-IDF vs BM25 & Translog Write Pipeline",
      "definition": "Relevance scoring calculates a numerical match score for each document against a search query, ranking the most relevant results at the top. Okapi BM25 is the modern probabilistic relevance algorithm that superseded classic TF-IDF by introducing Term Frequency Saturation and Document Length Normalization. The Translog (Transaction Log) is Elasticsearch's write-ahead log that guarantees real-time write durability alongside Lucene in-memory segment buffers.",
      "why_we_need_it": "A search engine that returns 10,000 matching documents in random chronological order is useless to users. Users expect the top 3 results on Page 1 to perfectly answer their intent. BM25 provides mathematically superior ranking, while the Translog ensures that newly indexed data survives server power crashes without forcing expensive disk fsyncs on every write.",
      "real_world_analogy": "BM25 is a human professor grading an essay: If an essay mentions 'Quantum Computing' 5 times, it gets high marks. If it mentions it 500 times, the professor recognizes that the student is just repeating the word to stuff keywords (Term Frequency Saturation) and doesn't give 100x more points. If an essay is a short concise 1-page paper, mentioning the term once carries much higher weight than mentioning it once in an 800-page encyclopedia (Length Normalization).",
      "how_it_works": "<p>1. <strong>The BM25 Formula Breakdown:</strong><br>&bull; <em>IDF (Inverse Document Frequency):</em> Measures how rare a term is across the entire corpus: $\\text{IDF}(q) = \\ln\\left(1 + \\frac{N - n + 0.5}{n + 0.5}\\right)$. Rare terms (like 'quarks') carry high weight; common terms (like 'computer') carry low weight.<br>&bull; <em>TF Saturation ($k_1$ parameter, typically 1.2):</em> In classic TF-IDF, if term frequency doubles, the score doubles. In BM25, the score approaches an asymptotic ceiling ($k_1 + 1$). Repeating a keyword 100 times yields diminishing returns, defeating keyword stuffers!<br>&bull; <em>Document Length Normalization ($b$ parameter, typically 0.75):</em> Penalizes overly long documents. If a short tweet and a long Wikipedia article both mention 'Bitcoin' twice, the tweet receives a higher relevance score because a higher percentage of its content is focused on the topic.</p><p>2. <strong>The Real-Time Write Pipeline (Translog & Refresh):</strong><br>&bull; Step 1: Write enters Data Node. Document is added to the in-memory <strong>Index Buffer</strong> AND appended to the sequential on-disk <strong>Translog</strong> for durability.<br>&bull; Step 2 (Refresh - Default 1s): Every second, the in-memory buffer is flushed to an in-memory <strong>Lucene Segment</strong> in the OS Page Cache (`refresh`). The document is now <em>Searchable</em> ('Near-Real-Time' search)!<br>&bull; Step 3 (Flush - Every 30m or Translog > 512MB): Lucene segments in page cache are flushed to physical disk via `fsync()`, and the Translog is truncated.</p>",
      "conceptual_breakdown": [
        "<strong>Near-Real-Time (NRT) Search:</strong> A document is searchable 1 second after insertion (`refresh_interval = 1s`), because Lucene writes to the OS page cache without waiting for an expensive physical disk `fsync()`.",
        "<strong>Term Frequency Saturation:</strong> BM25 prevents documents from dominating search results purely through keyword repetition.",
        "<strong>BM25 Tuning Parameters:</strong> $k_1$ (controls term frequency saturation limit; default 1.2); $b$ (controls document length normalization penalty; default 0.75).",
        "<strong>Translog Durability (`index.translog.durability`):</strong> Set to `request` (default, fsyncs translog on every request for zero data loss) or `async` (flushes translog every 5 seconds for extreme write throughput)."
      ],
      "arch_diagram": {
        "title": "Elasticsearch Write Pipeline (Index Buffer -> Translog -> Lucene Segment Refresh)",
        "tiers": [
          {
            "label": "Document Write Ingress",
            "nodes": [
              {
                "name": "Index Request (PUT /docs/1)",
                "type": "client",
                "icon": "📝",
                "what": "JSON document mutation",
                "why": "Writes to Primary Shard",
                "when": "Client indexing",
                "failure": "Replicated to ISR shards"
              }
            ]
          },
          {
            "label": "Dual In-Memory & Sequential Log Tier",
            "nodes": [
              {
                "name": "Index Buffer (RAM)",
                "type": "cache",
                "icon": "🧠",
                "what": "In-memory Lucene buffer",
                "why": "Accumulates documents before segment creation",
                "when": "Immediate on write",
                "failure": "Recoverable via Translog"
              },
              {
                "name": "Translog (Disk Append)",
                "type": "database",
                "icon": "📜",
                "what": "Sequential Write-Ahead Log",
                "why": "Guarantees crash durability",
                "when": "Immediate on write",
                "failure": "Replayed on node crash"
              }
            ]
          },
          {
            "label": "Searchable Segments (Page Cache / Disk)",
            "nodes": [
              {
                "name": "Lucene Segment (Page Cache)",
                "type": "database",
                "icon": "⚡",
                "what": "Created every 1s (Refresh)",
                "why": "Makes document searchable in Near-Real-Time!",
                "when": "refresh_interval: 1s",
                "failure": "Committed to disk on Flush"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Classic TF-IDF vs Okapi BM25 Scoring",
        "columns": ["Dimension", "Classic TF-IDF", "Okapi BM25 (Modern Standard)"],
        "rows": [
          ["Term Frequency Curve", "Linear / Unbounded (Score increases infinitely with count)", "Asymptotic Saturation (Score plateaus at k1 ceiling)"],
          ["Document Length Normalization", "Rudomatic vector length cosine normalization", "Explicit parameter 'b' calibrating length penalty"],
          ["Resistance to Keyword Stuffing", "Poor (Spamming a keyword 500 times guarantees top rank)", "High (500 occurrences yields negligible extra score over 10)"],
          ["Default in Search Engines", "Deprecated", "Standard in Elasticsearch, Solr, Lucene"]
        ]
      },
      "tradeoffs": "<strong>Refresh Interval Trade-off:</strong> The default 1-second refresh makes data searchable in near-real-time, but creates thousands of tiny segment files that cause high CPU merge churn. For bulk indexing workloads (e.g. log ingestion), setting `refresh_interval: 30s` or `-1` boosts indexing throughput by up to 3x.",
      "failure_scenarios": "<strong>The Bulk Ingest Refresh Storm:</strong> A data team imports 50 million historical log records into Elasticsearch with default settings (`refresh_interval = 1s`). Every second, Elasticsearch creates a new tiny Lucene segment file, spawning dozens of background merge threads that saturate all CPU cores and fill the disk with merge I/O. The cluster becomes unresponsive. <em>Mitigation:</em> During bulk loading, set `refresh_interval: -1` and `number_of_replicas: 0`. Once loading completes, trigger an explicit `_refresh`, run `_forcemerge`, and restore replicas.",
      "common_mistakes": [
        {"mistake": "Calling the `_refresh` API explicitly after every single document insert in application code.", "correction": "Forcing refreshes creates thousands of micro-segments, thrashing disk and CPU. Rely on the automated 1-second background refresh."},
        {"mistake": "Attempting to calculate relevance scores across shards with uneven document distributions.", "correction": "On small indices with multiple shards, local shard IDF skew causes identical documents to score differently. Use `dfs_query_then_fetch` or use 1 primary shard for small datasets."}
      ],
      "interview_questions": [
        {"question": "How does Okapi BM25 improve on classic TF-IDF relevance scoring?", "answer": "BM25 introduces two major mathematical advancements: 1. <strong>Term Frequency Saturation:</strong> In TF-IDF, term frequency is linear: a document with 100 occurrences of a word scores 10x higher than one with 10 occurrences. In BM25, the TF score asymptotically approaches a saturation limit ($k_1$), so extra occurrences yield diminishing returns, preventing spam/keyword-stuffing; 2. <strong>Document Length Normalization:</strong> Parameter $b$ scales the score based on document length relative to average document length in the corpus, ensuring concise, focused articles are not unfairly penalized when competing against 500-page documents."},
        {"question": "What is the difference between an Elasticsearch Refresh and an Elasticsearch Flush?", "answer": "A <strong>Refresh</strong> flushes the in-memory index buffer to a new <em>Lucene segment in the OS Page Cache</em> (default every 1 second). This makes newly indexed documents **Searchable in Near-Real-Time**, but does not guarantee on-disk durability. A <strong>Flush</strong> executes a physical `fsync()` to write all page-cache segments to non-volatile disk storage and clears the Translog (default every 30 minutes or when Translog reaches 512MB), guaranteeing **Physical Crash Durability**."}
      ]
    },
    {
      "id": "search-autocomplete-and-typeahead",
      "title": "Real-time Search Autocomplete & Typeahead at Scale (Prefix Trees / Trie vs Edge N-grams)",
      "definition": "Search Autocomplete (Typeahead / Suggest-as-you-type) is a real-time predictive text system that presents top-ranked search completions as the user types each keystroke in a search box. Architectural implementations range from In-Memory Prefix Trees (Tries with min-heaps) to Search Engine Tokenizers (Edge N-Grams) and Lucene Completion Suggesters (Finite State Transducers / FSTs).",
      "why_we_need_it": "Autocomplete receives massive query volume: every single keystroke typed by a user triggers a network API call (e.g. typing 'system design' produces 13 API requests). The system must evaluate prefix matches, rank suggestions by popularity/frequency, and return the top 5 suggestions within sub-20ms latency to deliver a seamless user experience.",
      "real_world_analogy": "A predictive text assistant on a smartphone: As you type 'sys', the keyboard immediately predicts 'system', 'system design', and 'systolic' based on the most common phrases typed in your language.",
      "how_it_works": "<p>1. <strong>Trie (Prefix Tree) Data Structure:</strong> A tree where each node represents a character. The path from the root to a node forms a prefix string (e.g., `r` &rarr; `o` &rarr; `o` &rarr; `t`).<br>&bull; <em>Optimization (Top-K Caching in Nodes):</em> Searching a naive Trie requires traversing to the prefix node and doing a DFS traversal of all subtrees, which is too slow ($O(V)$). In an optimized Trie, each node stores a <strong>pre-computed list of the Top 5 most popular completions</strong> (using a Min-Heap based on historical query frequency). Prefix search becomes $O(L)$ where $L$ is the length of the typed query string (e.g. 3-5 characters), independent of the size of the dictionary!</p><p>2. <strong>Edge N-Gram Tokenizer (Elasticsearch Approach):</strong> Slices words into prefix n-grams at index time: `'apple'` &rarr; `['a', 'ap', 'app', 'appl', 'apple']`. When a user types `'app'`, it performs a standard O(1) inverted index term match. Fast and supports fuzzy matching, but increases index size by 3x-5x.</p><p>3. <strong>Completion Suggester (Lucene FST):</strong> Compiles suggestions into an in-memory <strong>Finite State Transducer (FST)</strong> with pre-computed weights. Evaluates completely in RAM with sub-millisecond execution.</p><p>4. <strong>Client-Side Optimization (Debouncing):</strong> The browser client applies <strong>Debouncing</strong> (e.g. 150-300ms delay), waiting until the user pauses typing before dispatching the HTTP request, reducing network API calls by 70%.</p>",
      "conceptual_breakdown": [
        "<strong>Debouncing vs Throttling:</strong> Debouncing resets the timer on each keystroke and fires only after the user stops typing for $X$ milliseconds; Throttling fires at a fixed interval (e.g. at most once every 200ms).",
        "<strong>Client-Side Caching:</strong> The browser caches prefix suggestions in memory (e.g., `suggestions['sys']`). If the user types 'syst' and hits backspace back to 'sys', the client serves suggestions instantly from local memory with zero network calls.",
        "<strong>Offline Frequency Aggregation:</strong> Query popularity weights are NOT updated synchronously during user keystrokes! Logs are streamed to Kafka and aggregated hourly via Apache Flink / Spark to update Trie weights offline.",
        "<strong>Personalization Re-ranking:</strong> Top-K global suggestions are personalized on the edge using the user's location, language, and recent search history."
      ],
      "arch_diagram": {
        "title": "Real-Time Search Autocomplete Architecture (Trie Service + Offline Aggregator)",
        "tiers": [
          {
            "label": "Client Ingress Tier (Debounced)",
            "nodes": [
              {
                "name": "Search Box (Debounce 200ms)",
                "type": "client",
                "icon": "🔍",
                "what": "User types 'sys'",
                "why": "Debounces keystrokes to reduce QPS by 70%",
                "when": "User typing",
                "failure": "Serves from local browser cache"
              }
            ]
          },
          {
            "label": "Typeahead Autocomplete Cluster",
            "nodes": [
              {
                "name": "Trie In-Memory Service",
                "type": "cache",
                "icon": "🌲",
                "what": "In-Memory Prefix Tree + Top 5 Cache",
                "why": "Sub-5ms lookup for any prefix in RAM",
                "when": "Live autocomplete query",
                "failure": "Replicated across auto-scaled pods"
              },
              {
                "name": "Redis Prefix Cache",
                "type": "cache",
                "icon": "⚡",
                "what": "Caches top 100,000 hot prefixes",
                "why": "Absorbs 85% of query volume before Trie",
                "when": "Popular prefixes ('fac', 'goo')",
                "failure": "Falls back to Trie service"
              }
            ]
          },
          {
            "label": "Offline Popularity Aggregator Tier",
            "nodes": [
              {
                "name": "Search Log Stream (Kafka)",
                "type": "queue",
                "icon": "📜",
                "what": "Logs actual clicked search queries",
                "why": "Captures query frequencies",
                "when": "User clicks search",
                "failure": "Buffered for analytics"
              },
              {
                "name": "Spark / Flink Hourly Aggregator",
                "type": "service",
                "icon": "⚙️",
                "what": "Computes Top-K query weights",
                "why": "Builds new Trie snapshot hourly",
                "when": "Hourly cron batch",
                "failure": "Hot-swaps Trie snapshot in memory"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Autocomplete Implementation Approaches Comparison",
        "columns": ["Implementation", "Lookup Latency", "Memory Overhead", "Fuzzy / Typo Support?", "Dynamic Weight Updates"],
        "rows": [
          ["In-Memory Trie (Custom)", "Blazing (<2ms, RAM traversal)", "Moderate (can be optimized via Radix Tree)", "Complex to implement", "Requires offline snapshot swapping"],
          ["Elasticsearch Edge N-Grams", "Fast (5-15ms, Inverted Index)", "High (3x-5x index size expansion)", "Native fuzzy / Levenshtein distance support", "Real-time updates via document reindex"],
          ["Elasticsearch Completion Suggester", "Ultra-fast (<3ms, FST in RAM)", "Low-to-moderate", "Supports basic fuzzy prefix matching", "Requires reindexing to change weights"],
          ["Redis Sorted Sets (ZSET)", "Fast (3-8ms, ZRANGEBYLEX)", "Moderate", "No typo/fuzzy matching", "Real-time ZINCRBY frequency updates"]
        ]
      },
      "tradeoffs": "<strong>In-Memory Trie:</strong> Delivers sub-2ms lookups with custom ranking algorithms, but requires building a custom microservice and implementing snapshot re-loading pipelines. <strong>Edge N-Grams:</strong> Works out-of-the-box in Elasticsearch with rich fuzzy matching, but consumes massive disk space and has higher query latency under heavy load.",
      "failure_scenarios": "<strong>The Synchronous Autocomplete DB Denial of Service:</strong> A company implements search autocomplete by running `SELECT suggestion FROM queries WHERE prefix LIKE 'xyz%' ORDER BY frequency DESC LIMIT 5` directly against PostgreSQL on every keystroke. 100,000 users begin typing simultaneously on Black Friday. 1.2 million SQL queries per second hit the database, knocking it completely offline in 10 seconds. <em>Mitigation:</em> Autocomplete must NEVER query a primary relational database! Use an <strong>In-Memory Trie service</strong> or <strong>Redis ZSET</strong> with aggressive client debouncing and edge caching.",
      "common_mistakes": [
        {"mistake": "Dispatching an HTTP API request on every single keypress without debouncing.", "correction": "Always apply client-side debouncing (150-250ms). If the user types 'amazon' rapidly, only 1 or 2 API requests should be sent, not 6."},
        {"mistake": "Updating Trie suggestion weights synchronously on every user keystroke.", "correction": "Decouple analytics from search. Stream click logs to Kafka and recompute Trie weights asynchronously in background batch jobs."}
      ],
      "interview_questions": [
        {"question": "How do you optimize an In-Memory Trie to return the Top 5 most frequent search suggestions in sub-5ms?", "answer": "In a naive Trie, finding top suggestions requires traversing to the prefix node and performing a Depth-First Search (DFS) over all descendant nodes, which is too slow ($O(V)$). Optimization: <strong>Pre-compute and store the Top 5 suggestions directly at every Trie node</strong>. Each node stores a small fixed array of the top 5 query strings and their frequencies (maintained using a Min-Heap). When a user types a prefix of length $L$, the algorithm traverses $L$ steps down the tree and immediately returns the pre-computed array in $O(L)$ time (~sub-millisecond), completely independent of the size of the total search dictionary."},
        {"question": "How do you handle spelling errors and fuzzy matching in autocomplete systems?", "answer": "1. <strong>Levenshtein Distance / Damerau-Levenshtein:</strong> Allows matches within an edit distance of 1 or 2 (insertions, deletions, substitutions, transpositions);<br>2. <strong>Fuzzy Trie Traversal:</strong> When searching the Trie, if an exact branch does not exist, explore adjacent character branches while decrementing an edit-distance budget;<br>3. <strong>Phonetic Hashing (Double Metaphone / Soundex):</strong> Converts words to phonetic keys based on pronunciation (e.g. 'Smit' and 'Smith' map to the same phonetic code `SM0`), matching words that sound identical despite spelling errors."}
      ]
    }
  ]
}

# Write Module 21
with open(HLD_DIR / "module_21.json", "w", encoding="utf-8") as f:
  json.dump(m21, f, ensure_ascii=False, indent=2)
print("Module 21 written successfully!")
