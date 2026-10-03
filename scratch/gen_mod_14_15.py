"""
Elaborate generator for Modules 14 and 15.
"""
import json
from pathlib import Path

HLD_DIR = Path('content/hld')
HLD_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# MODULE 14: CAP Theorem & PACELC Explained
# ==========================================
m14 = {
  "module_id": "14",
  "module_title": "CAP Theorem & PACELC Explained",
  "description": "Master distributed trade-offs: The mathematical realities of the CAP Theorem, CP vs AP system categorization, and the modern PACELC theorem bridging latency and consistency.",
  "topics": [
    {
      "id": "cap-theorem-deep-dive",
      "title": "CAP Theorem Realities: Why You Can NEVER Choose 'CA' Over a Partition",
      "definition": "The CAP Theorem (formulated by Eric Brewer and formally proven by Gilbert & Lynch) states that any distributed data store can simultaneously provide at most two of three guarantees: Consistency (every read receives the most recent write or an error), Availability (every non-failing node returns a non-error response without guarantee of latest data), and Partition Tolerance (the system continues to operate despite arbitrary network packet drops or delays between nodes).",
      "why_we_need_it": "In interviews and real engineering architecture, junior engineers frequently claim: 'I will design a CA (Consistent and Available) system'. In the real physical world, networks WILL partition (cables get cut, switches fail, cross-cloud links hiccup). Therefore, Partition Tolerance (P) is mandatory. The only real architectural choice in a distributed system is between CP and AP when a partition strikes.",
      "real_world_analogy": "Two cellular towers on opposite sides of a mountain: A snowstorm knocks down the fiber cable connecting the two towers (Network Partition). Customer Alice deposits $100 at Tower 1. Customer Bob attempts to withdraw $100 at Tower 2. Tower 2 has two choices: 1. Refuse Bob's withdrawal with an error because it cannot verify Alice's balance with Tower 1 (Consistency over Availability - CP); or 2. Allow Bob's withdrawal, risking that Alice already withdrew the money, causing a negative balance (Availability over Consistency - AP). You cannot have both!",
      "how_it_works": "<p>1. <strong>Formal Definition of C (Linearizability):</strong> In CAP, Consistency means <em>Linearizability</em>. If a write completes at physical time $t_0$, any read that starts at time $t_1 > t_0$ anywhere in the cluster MUST return the updated value or later.</p><p>2. <strong>Formal Definition of A (Availability):</strong> Every non-failing node must return a non-error response to every request it receives. Returning an HTTP 500 error or dropping a request violates CAP availability.</p><p>3. <strong>Formal Definition of P (Partition Tolerance):</strong> The network between nodes will lose, delay, or partition arbitrary messages. Because physical networks are fundamentally asynchronous and fallible, $P$ is non-negotiable for any system spanning more than one machine.</p><p>4. <strong>The Trilemma Fallacy (Pick Any 2 is a Myth):</strong> You cannot pick 'CA'. A 'CA' system only exists if network partitions never happen—which is physically impossible outside of a single-node computer. Therefore, the CAP theorem really means: <em>'In the presence of a network partition, do you choose Consistency (CP) or Availability (AP)?'</em></p>",
      "conceptual_breakdown": [
        "<strong>CP Choice (Consistency over Availability):</strong> When the network partitions, nodes in the minority partition refuse reads and writes (returning errors) until network connectivity is restored, preserving absolute consistency.",
        "<strong>AP Choice (Availability over Consistency):</strong> When the network partitions, all nodes accept reads and writes. Nodes in partitioned partitions serve stale data and accept conflicting writes, deferring reconciliation to later.",
        "<strong>Partitions are Rare, but Defining:</strong> When the network is healthy (99.9% of the time), systems provide both consistency and availability. CAP trade-offs only trigger during active network partitions.",
        "<strong>Single-Node CA:</strong> A single standalone PostgreSQL instance on a single machine is 'CA' only because there is no network between nodes to partition!"
      ],
      "arch_diagram": {
        "title": "CAP Theorem Partition Scenario (Minority Partition vs Majority Partition)",
        "tiers": [
          {
            "label": "Majority Partition (AZ-1 & AZ-2)",
            "nodes": [
              {
                "name": "Node 1 (Leader)",
                "type": "database",
                "icon": "👑",
                "what": "Holds Quorum (2 of 3 nodes)",
                "why": "Accepts reads and writes",
                "when": "Network partitioned",
                "failure": "Continues operating normally"
              },
              {
                "name": "Node 2 (Follower)",
                "type": "database",
                "icon": "🛡️",
                "what": "Replicates from Node 1",
                "why": "Forms quorum majority",
                "when": "Partition active",
                "failure": "Reaches consensus"
              }
            ]
          },
          {
            "label": "Network Partition Barrier",
            "nodes": [
              {
                "name": "Severed Cross-AZ Fiber Link",
                "type": "lb",
                "icon": "⚡",
                "what": "Packets Dropped Between AZs",
                "why": "Simulated hardware/switch failure",
                "when": "Active Partition Event",
                "failure": "Forces CAP decision"
              }
            ]
          },
          {
            "label": "Minority Partition (AZ-3 Isolated)",
            "nodes": [
              {
                "name": "Node 3 (Isolated)",
                "type": "database",
                "icon": "🏝️",
                "what": "CP: Returns Error (Unavailable) | AP: Accepts Stale Writes",
                "why": "Cannot contact majority quorum",
                "when": "Client query hits Node 3",
                "failure": "CP sacrifices A; AP sacrifices C"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "CAP System Classification Matrix",
        "columns": ["Classification", "Partition Behavior", "Data Guarantee", "Representative Systems", "Best Use Case"],
        "rows": [
          ["CP (Consistency + Partition Tolerance)", "Minority partition nodes reject writes/reads with errors", "Strict Linearizability; zero stale data", "Google Spanner, ZooKeeper, etcd, HBase, CockroachDB", "Banking, Stock Trading, Master Election, Inventory"],
          ["AP (Availability + Partition Tolerance)", "All nodes accept reads/writes; serve stale data", "Eventual Consistency; conflict resolution required", "Apache Cassandra, Amazon DynamoDB, Couchbase, Riak", "Social Media feeds, Video streaming, IoT Telemetry, Shopping Carts"],
          ["'CA' (Theoretical Single Box)", "Fails completely if network is introduced", "Local ACID consistency", "Single-node MySQL / PostgreSQL on 1 server", "Small monolithic internal applications"]
        ]
      },
      "tradeoffs": "<strong>CP Systems:</strong> Guarantee absolute data correctness and eliminate race conditions, but sacrifice uptime: if a network partition isolates nodes, clients in the isolated partition receive 500 errors. <strong>AP Systems:</strong> Guarantee 100% uptime and low latency across partitions, but permit stale reads and conflicting updates that must be resolved via CRDTs or human review.",
      "failure_scenarios": "<strong>The Inadvertent AP Financial Overdraft Disaster:</strong> A bank configures an AP database across two data centers. A cross-region network cable is severed. A customer with $500 balance withdraws $500 in Region East, and simultaneously withdraws $500 in Region West. Because both regional nodes are configured to be Available (AP), both transactions succeed, leaving the bank with a $500 deficit. <em>Mitigation:</em> Financial ledgers MUST be CP systems.",
      "common_mistakes": [
        {"mistake": "Claiming in a system design interview that your distributed system is 'CA'.", "correction": "Never claim CA in a distributed interview. All distributed systems must choose CP or AP when network partitions occur."},
        {"mistake": "Believing that CAP applies when the network is completely healthy.", "correction": "CAP only dictates behavior during a network partition. When the network is healthy, PACELC dictates the trade-off between Latency and Consistency."}
      ],
      "interview_questions": [
        {"question": "Why is 'CA' impossible in any real-world distributed system?", "answer": "In any system spanning two or more physical network nodes, network partitions (packet loss, switch failures, cable cuts) are inevitable. When a partition occurs, nodes on one side of the partition cannot communicate with nodes on the other side. If a client writes to Node 1, Node 2 cannot learn of the write. The system MUST choose: either Node 2 refuses reads to prevent serving stale data (sacrificing Availability for Consistency - <strong>CP</strong>), or Node 2 answers reads with stale data (sacrificing Consistency for Availability - <strong>AP</strong>). A system cannot choose to ignore partitions, making CA physically impossible in distributed environments."},
        {"question": "Is Amazon DynamoDB a CP or AP system?", "answer": "DynamoDB is fundamentally an <strong>AP system by default</strong> (offering Eventual Consistency on reads with high availability across multi-AZ partitions). However, DynamoDB allows clients to issue <strong>Strongly Consistent Reads</strong> (`ConsistentRead = true`) on a per-query basis, forcing the read to query a leader replica and behave as CP for that specific operation."}
      ]
    },
    {
      "id": "cp-vs-ap-systems",
      "title": "CP Systems (HBase, Zookeeper) vs AP Systems (Cassandra, DynamoDB)",
      "definition": "CP systems (HBase, ZooKeeper, etcd, Spanner) prioritize data correctness over uptime during network disruptions, halting operations in minority partitions. AP systems (Cassandra, DynamoDB, Riak) prioritize continuous uptime and write availability over absolute consistency, allowing nodes to accept conflicting mutations during partitions.",
      "why_we_need_it": "Categorizing systems into CP vs AP governs critical architectural decisions: you cannot build a distributed locks coordinator on an AP system (it will issue duplicate locks), and you cannot build a global social media newsfeed on a CP system (minority network partitions will break user feeds globally).",
      "real_world_analogy": "Air Traffic Control (CP) vs Twitter Feed (AP): Air Traffic Control must be CP—if communication between towers is severed, airplanes are grounded and prevented from landing until communication is restored, because a single inconsistency means planes crash. Twitter Feed is AP—if a user in London posts a tweet during a transatlantic cable cut, users in Tokyo don't need to see it immediately; continuous scrolling is more important than instant global synchronization.",
      "how_it_works": "<p>1. <strong>CP System Architecture (Leader-Based Quorums):</strong> Relies on a single elected Leader (via Raft, Paxos, or ZAB). All writes must pass through the leader and be confirmed by a majority quorum ($N/2 + 1$). If a network partition splits a 5-node cluster into {3 nodes} and {2 nodes}, the majority partition {3} continues operating. The minority partition {2} <em>stops accepting writes and reads</em> because it cannot reach quorum, preserving linearizable consistency.</p><p>2. <strong>AP System Architecture (Masterless Gossip Rings):</strong> Every node can accept writes independently. Cassandra writes to $W$ replicas (e.g. $W=1$). If nodes are partitioned, writes succeed locally in both partitions. When the partition heals, replicas synchronize via <strong>Hinted Handoff</strong> and <strong>Read Repair</strong>, reconciling conflicting updates using Last-Write-Wins (LWW) or Vector Clocks.</p><p>3. <strong>ZooKeeper / etcd (The Archetypal CP Store):</strong> Used for configuration management, leader election, and distributed locking. Will refuse client requests and trigger election freezes rather than risk returning stale or conflicting leader states.</p><p>4. <strong>Cassandra / DynamoDB (The Archetypal AP Store):</strong> Tunable consistency allows tuning from pure AP (`Read: ONE, Write: ONE`) to strong consistency (`Read: QUORUM, Write: QUORUM`).</p>",
      "conceptual_breakdown": [
        "<strong>Quorum Math in CP:</strong> Requires strictly odd numbers of nodes (3, 5, 7) to guarantee that only ONE majority partition can ever exist ($5 \\to 3+2$).",
        "<strong>Split-Brain Guardrail:</strong> CP systems prevent split-brain by requiring majority votes for leader election. A 2-node partition in a 5-node cluster cannot elect a leader ($2 < 3$).",
        "<strong>Hinted Handoff (AP):</strong> If Node 3 is unreachable due to a network partition, the coordinator node temporarily stores the write in a local 'hint' buffer. When Node 3 reconnects, the coordinator streams the buffered hints to Node 3.",
        "<strong>Anti-Entropy Repair:</strong> AP systems run background Merkle Tree exchange processes to synchronize out-of-sync replicas."
      ],
      "arch_diagram": {
        "title": "CP Consensus Cluster vs AP Gossip Ring Architecture",
        "tiers": [
          {
            "label": "CP Architecture (ZooKeeper / Raft)",
            "nodes": [
              {
                "name": "Leader Node (Consensus)",
                "type": "database",
                "icon": "👑",
                "what": "Atomic Broadcast Leader",
                "why": "Enforces strict total order",
                "when": "Active majority quorum",
                "failure": "Election triggers on timeout"
              },
              {
                "name": "Follower Quorum Nodes",
                "type": "database",
                "icon": "🛡️",
                "what": "Synchronous Log Replicas",
                "why": "Must confirm writes before commit ACK",
                "when": "Every write",
                "failure": "Minority failures tolerated"
              }
            ]
          },
          {
            "label": "AP Architecture (Cassandra Gossip Ring)",
            "nodes": [
              {
                "name": "Masterless Node 1",
                "type": "database",
                "icon": "⭕",
                "what": "Peer Coordinator",
                "why": "Accepts writes independently",
                "when": "Client write hits node",
                "failure": "Routes hints to peers"
              },
              {
                "name": "Masterless Node 2",
                "type": "database",
                "icon": "⭕",
                "what": "Peer Coordinator",
                "why": "Reconciles via Read Repair",
                "when": "Continuous background sync",
                "failure": "Eventual consistency convergence"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "CP vs AP Systems Deep Comparison",
        "columns": ["Feature", "CP Systems (etcd, ZooKeeper, Spanner)", "AP Systems (Cassandra, DynamoDB, Riak)"],
        "rows": [
          ["Availability Guarantee", "Sacrificed in minority partitions (errors returned)", "100% available across all surviving partitions"],
          ["Consistency Guarantee", "Strict Linearizability (Immediate consistency)", "Eventual Consistency (Stale reads permitted)"],
          ["Node Topology", "Leader-Follower (Single active leader)", "Masterless Peer-to-Peer Ring"],
          ["Conflict Resolution", "None needed (Leader establishes total order)", "Last-Write-Wins (LWW) or Vector Clocks / CRDTs"],
          ["Failure Handling", "Requires majority quorum (N/2 + 1)", "Hinted Handoff, Read Repair, Anti-Entropy"],
          ["Representative Engines", "Google Spanner, CockroachDB, etcd, HBase", "Apache Cassandra, Amazon DynamoDB, Couchbase"]
        ]
      },
      "tradeoffs": "<strong>CP Trade-off:</strong> Total data safety and transaction serializability at the cost of higher latency (due to consensus handshakes) and partial system outages during network splits. <strong>AP Trade-off:</strong> Low latency and uninterrupted uptime at the cost of eventual consistency bugs, duplicate writes, and application-level conflict resolution.",
      "failure_scenarios": "<strong>The ZooKeeper 2-Node Cluster Deadlock:</strong> A developer deploys a 2-node ZooKeeper cluster for high availability. One node crashes. The surviving node attempts to form a quorum. In a 2-node cluster, a majority is $\\lfloor 2/2 \\rfloor + 1 = 2$. The single surviving node cannot reach a majority, so it immediately refuses all requests and shuts down, turning a 1-node failure into a 100% system outage! <em>Mitigation:</em> Always deploy CP consensus clusters with an <strong>odd number of nodes</strong> (minimum 3, ideally 5).",
      "common_mistakes": [
        {"mistake": "Deploying an even number of nodes (e.g. 2 or 4) for a Raft / ZooKeeper cluster.", "correction": "Always use an odd number of nodes (3 or 5). Adding a 4th node does not increase fault tolerance; it requires 3 nodes for a quorum just like a 3-node cluster, but increases failure points."},
        {"mistake": "Using an AP database (like Cassandra) to store distributed locks.", "correction": "AP databases permit conflicting writes during network partitions, which will cause multiple clients to simultaneously acquire the same distributed lock."}
      ],
      "interview_questions": [
        {"question": "Why do consensus systems (Raft, Paxos, ZooKeeper) always require an odd number of nodes (3, 5, 7)?", "answer": "An odd number of nodes maximizes fault tolerance while minimizing quorum size: A <strong>3-node cluster</strong> can tolerate 1 failure (majority = 2). A <strong>4-node cluster</strong> can ALSO only tolerate 1 failure (majority = 3), but requires more network votes and has more hardware failure points. A <strong>5-node cluster</strong> can tolerate 2 failures (majority = 3). Furthermore, odd numbers mathematically prevent split-brain ties ($5 \\to 3+2$, exactly one majority)."},
        {"question": "How does Cassandra heal stale data after a network partition resolves?", "answer": "Cassandra uses three complementary mechanisms: 1. <strong>Hinted Handoff:</strong> When a replica is unreachable, the coordinator buffers writes locally as 'hints' and replays them once the node recovers; 2. <strong>Read Repair:</strong> When a client reads data with `QUORUM`, the coordinator queries multiple replicas, compares timestamps, returns the newest value to the client, and asynchronously writes the newest value to any replica that had stale data; 3. <strong>Anti-Entropy Repair:</strong> Scheduled background processes exchange Merkle Trees between replicas to detect and synchronize out-of-sync byte ranges."}
      ]
    },
    {
      "id": "pacelc-theorem-and-latency",
      "title": "Beyond CAP: PACELC Theorem (Else Latency vs Consistency)",
      "definition": "The PACELC Theorem, formulated by Daniel Abadi in 2012, extends the CAP theorem to describe distributed database trade-offs during NORMAL operational conditions (when no network partition exists): If there is a Partition (P), how does the system choose between Availability (A) and Consistency (C)?; ELSE (E), when the network is running normally, how does the system choose between Latency (L) and Consistency (C)?",
      "why_we_need_it": "The CAP theorem only applies when the network partitions (which is a rare event, <0.1% of operational time). PACELC answers the critical question: 'How does your database behave during the 99.9% of time when the network is completely healthy?' It recognizes that high consistency requires waiting for cross-node replication, fundamentally increasing Latency.",
      "real_world_analogy": "Sending an email confirmation to a customer: In normal conditions (no network partition), you have two choices: 1. Wait synchronously until 3 backup servers confirm the email is saved before returning success to the user (Consistency over Latency - PC/EC: slower, but 100% safe); or 2. Return success immediately in 5 milliseconds and replicate in the background (Latency over Consistency - PA/EL: ultra-fast, but brief window of stale reads).",
      "how_it_works": "<p>1. <strong>The PACELC Formula:</strong><br>&bull; <strong>If [P] Partition:</strong> Choose between [A] Availability or [C] Consistency.<br>&bull; <strong>[E] Else (Normal Conditions):</strong> Choose between [L] Latency or [C] Consistency.</p><p>2. <strong>PC/EC Systems (e.g., Google Spanner, CockroachDB):</strong><br>&bull; Under Partition: Chooses Consistency (PC).<br>&bull; Under Normal Operations: Chooses Consistency over Latency (EC). Synchronously replicates writes via Raft/Paxos before acknowledging, accepting higher write latency (10-50ms) to guarantee zero stale reads.</p><p>3. <strong>PA/EL Systems (e.g., Cassandra, DynamoDB, MongoDB default):</strong><br>&bull; Under Partition: Chooses Availability (PA).<br>&bull; Under Normal Operations: Chooses Latency over Consistency (EL). Replicates asynchronously, returning success immediately (&lt;2ms) to optimize latency while tolerating brief replication lag.</p><p>4. <strong>PC/EL Systems (e.g., MongoDB with primary writes and replica reads):</strong><br>&bull; Under Partition: Enforces Consistency on the primary (PC).<br>&bull; Under Normal Operations: Reads from un-synced secondaries to achieve low Latency, serving stale data (EL).</p>",
      "conceptual_breakdown": [
        "<strong>Latency is the Real Enemy:</strong> In production systems, 99.9% of user friction comes from high p99 read/write latency, not rare network partitions.",
        "<strong>Speed-of-Light Constraint:</strong> Network packets cannot travel faster than the speed of light in fiber optic cables (~200 km/ms). Synchronously replicating a write from Virginia to Ireland (6,000 km) physically requires at least 60ms of round-trip network latency. You CANNOT have strong consistency without latency across continents.",
        "<strong>Tunable PACELC in DynamoDB:</strong> DynamoDB is natively PA/EL, but passing `ConsistentRead = true` switches it to PC/EC for that query.",
        "<strong>Replication Lag is Latency's Byproduct:</strong> Choosing low latency (EL) directly creates the replication lag window."
      ],
      "arch_diagram": {
        "title": "PACELC Theorem Architectural Trade-off Flowchart",
        "tiers": [
          {
            "label": "Network State Check",
            "nodes": [
              {
                "name": "Network Health Sensor",
                "type": "lb",
                "icon": "🩺",
                "what": "Evaluates packet drops & heartbeat timeouts",
                "why": "Determines which PACELC branch applies",
                "when": "Continuous",
                "failure": "Triggers partition branch"
              }
            ]
          },
          {
            "label": "PACELC Decision Branches",
            "nodes": [
              {
                "name": "IF Partition (P)",
                "type": "service",
                "icon": "⚡",
                "what": "Choose: Availability (PA) vs Consistency (PC)",
                "why": "CAP theorem trade-off during failures",
                "when": "Network split active",
                "failure": "Isolates minority partition"
              },
              {
                "name": "ELSE Normal (E)",
                "type": "service",
                "icon": "🕊️",
                "what": "Choose: Latency (EL) vs Consistency (EC)",
                "why": "Fundamental daily operating trade-off",
                "when": "99.9% of operational time",
                "failure": "Replication latency vs write ACK speed"
              }
            ]
          },
          {
            "label": "Engine Categorization",
            "nodes": [
              {
                "name": "PA / EL (Cassandra / DynamoDB)",
                "type": "database",
                "icon": "🚀",
                "what": "Prioritizes Low Latency & High Uptime",
                "why": "Sub-millisecond writes, eventual consistency",
                "when": "High throughput read/write",
                "failure": "Reconciles asynchronously"
              },
              {
                "name": "PC / EC (Spanner / CockroachDB)",
                "type": "database",
                "icon": "💎",
                "what": "Prioritizes Absolute Data Integrity",
                "why": "Synchronous consensus before write ACK",
                "when": "Financial ledger & ACID",
                "failure": "Blocks writes if quorum lost"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Major Database Systems Classified by PACELC",
        "columns": ["Database", "PACELC Classification", "Partition Choice (P)", "Normal Choice (E)", "Why"],
        "rows": [
          ["Google Spanner", "PC / EC", "Consistency (PC)", "Consistency (EC)", "Uses TrueTime commit-wait; accepts higher latency for linearizability"],
          ["Apache Cassandra", "PA / EL", "Availability (PA)", "Latency (EL)", "Masterless append-only; returns immediately and replicates async"],
          ["Amazon DynamoDB", "PA / EL (Tunable)", "Availability (PA)", "Latency (EL)", "Default eventual reads; can toggle to EC with ConsistentRead=true"],
          ["MongoDB", "PC / EC (Configurable)", "Consistency (PC)", "Consistency (EC)", "Default w:1 is PA/EL; setting w:'majority' makes it PC/EC"],
          ["CockroachDB", "PC / EC", "Consistency (PC)", "Consistency (EC)", "Multi-Raft consensus enforces strict serializability at latency cost"],
          ["Redis Replication", "PA / EL", "Availability (PA)", "Latency (EL)", "Master acknowledges write before async replica confirms"]
        ]
      },
      "tradeoffs": "<strong>PC/EC (Spanner):</strong> Eliminates all data anomalies and provides global ACID consistency, but imposes a 20-50ms latency floor on writes due to cross-datacenter Paxos rounds. <strong>PA/EL (Cassandra):</strong> Delivers 1ms write latency and 100% uptime, but applications must tolerate replication lag and handle potential read-your-own-writes inconsistencies.",
      "failure_scenarios": "<strong>The Global Latency Shockwave:</strong> An engineering team deploys a PC/EC database (CockroachDB) across three continents (US, Europe, Asia) to achieve strong consistency. Every single `INSERT` and `UPDATE` now requires a cross-oceanic Raft consensus round-trip. API write latency jumps from 5ms to 280ms, exhausting application thread pools and crashing the web gateway. <em>Mitigation:</em> For globally distributed systems, use <strong>Geo-Partitioning</strong> (confining data to local regions) or adopt a PA/EL model with CRDT conflict resolution.",
      "common_mistakes": [
        {"mistake": "Believing you can have sub-millisecond writes AND strong multi-datacenter consistency across continents.", "correction": "Physics forbids it. The speed of light imposes a minimum 60-100ms round-trip latency across continents. You must choose between Latency (EL) or Consistency (EC)."},
        {"mistake": "Using PACELC classification as a rigid label rather than understanding tunable client query options.", "correction": "Most modern databases (Cassandra, DynamoDB, MongoDB) allow tuning PACELC per query via Read/Write consistency parameters."}
      ],
      "interview_questions": [
        {"question": "How does the PACELC theorem expand on the CAP theorem?", "answer": "The CAP theorem only describes database behavior <strong>during a rare network partition</strong> (choose Consistency or Availability). Daniel Abadi created <strong>PACELC</strong> because systems spend >99.9% of their time running normally without partitions. PACELC states: If there is a Partition (P), how do you choose between (A) and (C)?; <strong>ELSE (E)</strong>, during normal operation, how do you choose between <strong>Latency (L) and Consistency (C)</strong>? This captures the daily trade-off: do you wait for synchronous multi-node replication (Consistency at the cost of Latency), or return immediately and replicate asynchronously (Latency at the cost of Consistency)?"},
        {"question": "Explain how a database can be classified as PC/EC vs PA/EL with examples.", "answer": "A <strong>PC/EC</strong> system (like Google Spanner or CockroachDB) chooses Consistency during a partition (refusing writes in minority partitions), and chooses Consistency under normal operation (waiting for synchronous Paxos/Raft consensus before acknowledging writes, accepting 20ms+ latency). A <strong>PA/EL</strong> system (like Cassandra or DynamoDB) chooses Availability during a partition (accepting writes everywhere), and chooses Latency under normal operation (acknowledging writes in RAM in <1ms and replicating asynchronously in the background)."}
      ]
    }
  ]
}

# ==========================================
# MODULE 15: Consistency Models: Strong to Eventual
# ==========================================
m15 = {
  "module_id": "15",
  "module_title": "Consistency Models: Strong to Eventual",
  "description": "Master the spectrum of distributed consistency models: Linearizability (Strict Strong Consistency), Sequential Consistency, Causal Consistency, Eventual Consistency, Read-Your-Writes, Monotonic Reads, and CRDTs.",
  "topics": [
    {
      "id": "linearizability-and-strong-consistency",
      "title": "Strong Consistency & Linearizability: Strict Global Time Ordering",
      "definition": "Linearizability (also known as Strong Consistency, Atomic Consistency, or External Consistency) is the strongest non-transactional consistency model in distributed systems. It guarantees that the entire distributed system behaves as if there were only a single copy of the data, and every read operation returns the value of the most recent write based on a global, real-world physical wall-clock timeline.",
      "why_we_need_it": "In financial transfers, leader election, and distributed locking, stale reads are fatal. If Lock Holder 1 releases a lock at 12:00:00.100, and Lock Holder 2 checks the lock at 12:00:00.101, Lock Holder 2 MUST see that the lock is free. Linearizability guarantees that once any client's write finishes, all subsequent reads across all servers in the world immediately see the new value.",
      "real_world_analogy": "A physical megaphone in a small quiet room: When Alice speaks into the megaphone, sound waves travel instantaneously to everyone in the room. Bob, Charlie, and Dave all hear the exact same words at the exact same physical millisecond. There is no possibility that Bob hears Alice's words 5 seconds before Charlie does.",
      "how_it_works": "<p>1. <strong>The Linearization Point:</strong> Every operation (read or write) takes effect atomically at an exact instantaneous point in real physical time between its start timestamp and its completion timestamp.</p><p>2. <strong>Recency Guarantee:</strong> If Client A completes a write to key $X = 5$ at 12:00:00.000, it is mathematically impossible for Client B to start a read at 12:00:00.001 and receive the old value $X = 4$.</p><p>3. <strong>Implementation Mechanisms:</strong><br>&bull; <em>Single-Leader with Synchronous Replication:</em> All reads and writes route to a single leader. The leader commits writes to all replicas before acknowledging.<br>&bull; <em>Consensus Protocol (Raft / Paxos):</em> Leader must achieve majority quorum on writes, and execute a quorum read (or verify its leader lease via heartbeats) before serving reads to avoid reading from a deposed leader (Split-Brain stale read).<br>&bull; <em>Google TrueTime Commit-Wait:</em> Bounded physical time intervals ensure linearizability without cross-region locks.</p><p>4. <strong>Performance Cost:</strong> Linearizability requires synchronous network coordination on every mutation. Network latency sets a hard physical limit on throughput.</p>",
      "conceptual_breakdown": [
        "<strong>Linearizability vs Serializability:</strong> Frequently confused! <em>Linearizability</em> is a recency guarantee on a SINGLE object (register). <em>Serializability</em> is an isolation guarantee on MULTI-OBJECT transactions (executing transactions in some valid serial order, but with no real-time recency guarantee). Systems providing both are called <strong>Strict Serializable</strong>.",
        "<strong>Non-Stale Reads in Raft (Read Index):</strong> In Raft, a leader cannot simply return its local in-memory state on a read! It might have been partitioned into a minority partition while another leader was elected. The leader must exchange heartbeats with a majority of nodes (or use Read Index / Leader Leases) to confirm it is still the authoritative leader before returning data.",
        "<strong>CAP Theorem Equivalence:</strong> The 'C' in CAP theorem is strictly defined as Linearizability.",
        "<strong>High Availability Incompatibility:</strong> Linearizability is impossible in any system that must remain available during a network partition."
      ],
      "arch_diagram": {
        "title": "Linearizability vs Stale Read Timeline",
        "tiers": [
          {
            "label": "Client Operations (Real Time Timeline)",
            "nodes": [
              {
                "name": "Client A: WRITE x = 5",
                "type": "client",
                "icon": "✍️",
                "what": "Starts: 100ms | Commits: 150ms",
                "why": "Updates global state",
                "when": "Time t0",
                "failure": "Retries on timeout"
              },
              {
                "name": "Client B: READ x",
                "type": "client",
                "icon": "👁️",
                "what": "Starts: 151ms (AFTER write completes)",
                "why": "Queries global state",
                "when": "Time t1 > t0",
                "failure": "Must return 5 in linearizable store!"
              }
            ]
          },
          {
            "label": "Linearizable Storage Engine",
            "nodes": [
              {
                "name": "Raft Consensus Leader",
                "type": "database",
                "icon": "👑",
                "what": "Enforces Linearization Point",
                "why": "Quorum read confirmation",
                "when": "t = 120ms (Atomic commit point)",
                "failure": "Returns error if quorum lost"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Consistency Models Hierarchy (Strongest to Weakest)",
        "columns": ["Consistency Model", "Global Real-Time Ordering?", "Permits Stale Reads?", "Tolerates Network Partitions?", "Latency"],
        "rows": [
          ["Linearizability (Strict Strong)", "Yes (Strict physical wall-clock order)", "No (Impossible to read stale data)", "No (Sacrifices availability on partition)", "Highest (network quorum roundtrips)"],
          ["Sequential Consistency", "No (Logical order preserved across all nodes)", "Yes (Can lag physical time, but all agree on order)", "No", "High"],
          ["Causal Consistency", "No (Only causally related events ordered)", "Yes (Concurrent independent events unordered)", "Yes (Available under partition)", "Low-to-medium"],
          ["Read-Your-Writes", "No (Scoped to individual client session)", "Yes (Other clients may see stale data)", "Yes", "Low"],
          ["Eventual Consistency", "No (No ordering guarantees during transit)", "Yes (Replicas lag indefinitely until quiescent)", "Yes (100% available under partition)", "Lowest (<1ms local memory read)"]
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> Linearizability provides the gold standard of data correctness—eliminating race conditions and phantom updates—at the cost of reduced write throughput, higher p99 latency, and complete unavailability in minority network partitions.",
      "failure_scenarios": "<strong>The Stale Leader Split-Brain Read:</strong> In a 5-node consensus cluster, a network partition isolates Leader A with Node 2, while Nodes 3, 4, and 5 form a new majority and elect Leader B. Client 1 sends `WRITE balance = $1000` to Leader B, which commits with majority quorum {3,4,5}. Client 2 sends `READ balance` to Leader A. If Leader A serves the read from its local memory without verifying its lease with a majority, Client 2 reads the stale balance `$0`! <em>Mitigation:</em> Enforce <strong>Raft ReadIndex / Leader Leases</strong>: the leader must confirm its leadership with a majority before returning read data.",
      "common_mistakes": [
        {"mistake": "Assuming that PostgreSQL or MySQL provides Linearizability by default.", "correction": "Relational databases default to Read Committed or Repeatable Read isolation, which permit reading stale snapshots from replicas. Linearizability requires synchronous replication and explicit serializable locking."},
        {"mistake": "Using a non-linearizable cache (like Redis standalone) to store bank account balances or auction bids.", "correction": "Use a linearizable consensus store (etcd / Spanner / ZooKeeper) or a transactional relational database for state where stale reads cause business corruption."}
      ],
      "interview_questions": [
        {"question": "What is the precise difference between Linearizability and Serializability?", "answer": "<strong>Linearizability</strong> is a <em>recency and time guarantee on single operations</em>: once a write completes in real physical time, all subsequent reads anywhere in the cluster must see that write or a newer one. <strong>Serializability</strong> is an <em>isolation guarantee on multi-operation transactions</em>: transactions can execute concurrently, but the final outcome must be equivalent to executing them in *some* serial sequential order (without any real-time recency guarantee—a serializable system could legally return data from yesterday as long as it preserves transaction order). Combining both yields <strong>Strict Serializability</strong> (External Consistency), as implemented in Google Spanner."},
        {"question": "How does a Raft leader serve reads without executing a full log commit on every read query?", "answer": "Using <strong>ReadIndex</strong>: 1. When a read arrives, the leader records its current commit index as `read_index`; 2. The leader sends a round of lightweight heartbeat pings to all followers to verify it still holds majority quorum; 3. Once majority confirms, the leader waits until its state machine has applied all log entries up to `read_index`; 4. The leader executes the read locally and returns results, guaranteeing linearizability without writing a new log entry to disk."}
      ]
    },
    {
      "id": "eventual-consistency-and-guarantees",
      "title": "Eventual Consistency, Read-Your-Writes & Monotonic Reads",
      "definition": "Eventual Consistency is a weak consistency model where, in the absence of new mutations, all replicas will eventually converge to identical values. Client-Centric Consistency models (Read-Your-Writes, Monotonic Reads, Monotonic Writes, and Writes-Follow-Reads) provide strong localized guarantees for individual user sessions without requiring global cluster synchronization.",
      "why_we_need_it": "Global synchronous consensus across 50 data centers around the world is bottlenecked by the speed of light. Eventual consistency decouples writes from cross-datacenter replication, allowing writes to commit locally in 1 millisecond while replicating asynchronously across the globe.",
      "real_world_analogy": "Social media 'Likes': When a celebrity posts a photo, 100,000 users click the 'Like' heart button in 5 seconds. If every click required global linearizable locks, Instagram would crash. Instead, the like counter replicates eventually. User A might see 48,201 likes while User B sees 48,195 likes. Within a few seconds after the burst stops, both screens display the exact same converged count.",
      "how_it_works": "<p>1. <strong>Eventual Consistency Mechanics:</strong> Writes are committed to a local node and acknowledged to the client in &lt;1ms. In the background, changes propagate asynchronously via Gossip protocols, Kafka change streams, or database replication logs. The system guarantees that <em>if no further updates occur, all replicas will eventually reach the same state</em>. However, it provides zero guarantees about how long 'eventually' takes.</p><p>2. <strong>Read-Your-Own-Writes Consistency:</strong> Guarantees that if a client updates a record, that same client will ALWAYS see their own update on subsequent reads. Implemented by pinning that user's read queries to the primary database for a short window (e.g. 5-10 seconds), or checking replica LSN tokens.</p><p>3. <strong>Monotonic Reads:</strong> Guarantees that if a client reads value $v_1$ at time $t_1$, they will never subsequently read an older value $v_0$ at time $t_2$ ('Time Travel Anomaly'). Implemented by hashing client user IDs to sticky read replicas so the client never switches from an up-to-date replica to a lagging replica.</p><p>4. <strong>Monotonic Writes:</strong> Guarantees that a client's writes are serialized in the order they were submitted.</p>",
      "conceptual_breakdown": [
        "<strong>The Time-Travel Anomaly:</strong> A user refreshes their Twitter feed at 12:00:00 and sees Tweet #5 (served by up-to-date Replica A). They refresh again at 12:00:01, hit lagging Replica B, and Tweet #5 disappears! Monotonic Reads prevents this.",
        "<strong>Client-Centric vs Data-Centric:</strong> Data-centric models (Linearizability) enforce guarantees globally across all users; Client-centric models enforce guarantees only from the perspective of an individual user session.",
        "<strong>Replication Convergence:</strong> Eventually consistent systems must implement mathematical convergence mechanisms (e.g., Last-Write-Wins timestamps, Version Vectors, or CRDTs) to reconcile conflicting writes.",
        "<strong>Quorum Eventual Consistency:</strong> In DynamoDB/Cassandra, reading with $R=1$ and writing with $W=1$ provides pure eventual consistency with lowest latency."
      ],
      "arch_diagram": {
        "title": "Client-Centric Consistency Guardrails (Read-Your-Writes Router)",
        "tiers": [
          {
            "label": "Client Session Context",
            "nodes": [
              {
                "name": "User Browser Session",
                "type": "client",
                "icon": "📱",
                "what": "Tracks last_write_timestamp = 12:05:00",
                "why": "Enforces Read-Your-Own-Writes",
                "when": "Continuous session",
                "failure": "Stored in local cookie"
              }
            ]
          },
          {
            "label": "Consistency-Aware Dispatcher",
            "nodes": [
              {
                "name": "Smart Read Router",
                "type": "lb",
                "icon": "🧭",
                "what": "Evaluates: (now - last_write) < 5s?",
                "why": "Routes recent mutators to Primary",
                "when": "Every read query",
                "failure": "Falls back to sticky replica"
              }
            ]
          },
          {
            "label": "Storage Engine Replicas",
            "nodes": [
              {
                "name": "Primary Database (Fresh)",
                "type": "database",
                "icon": "👑",
                "what": "Authoritative write store",
                "why": "Serves mutator reads (Zero Stale Window)",
                "when": "Recent writer",
                "failure": "Standard failover"
              },
              {
                "name": "Async Replicas (Lagging 200ms)",
                "type": "database",
                "icon": "📖",
                "what": "Eventual consistency pool",
                "why": "Serves 95% of passive readers",
                "when": "Normal reads",
                "failure": "Sticky hash prevents time-travel"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Client-Centric Consistency Guarantees Matrix",
        "columns": ["Guarantee", "Definition", "Anomaly Prevented", "Implementation Mechanism"],
        "rows": [
          ["Read-Your-Writes", "A user always sees their own updates immediately", "User edits profile, refreshes, and sees old profile", "Route user reads to Primary for 5s after write; or check LSN token"],
          ["Monotonic Reads", "A user never observes older state after seeing newer state", "Time-travel anomaly (refreshing page shows older comments)", "Sticky hash user session to a single replica"],
          ["Monotonic Writes", "A user's writes execute in the order they were submitted", "Update 2 applied before Update 1 on replica", "Route all writes for a user to the same partition leader"],
          ["Writes-Follow-Reads", "A write made after observing a read causally follows it", "Replying to a comment before the parent comment exists", "Attach vector clock or causal token to outbound writes"]
        ]
      },
      "tradeoffs": "<strong>Pros of Eventual Consistency:</strong> Sub-millisecond latency, massive write throughput, uninterrupted availability during cross-datacenter network splits. <strong>Cons:</strong> Stale data windows, complex application-level conflict resolution, debugging nightmare when reproducing intermittent timing-dependent bugs.",
      "failure_scenarios": "<strong>The Disappearing Comment Support Ticket Storm:</strong> A social media company shifts to eventual consistency read replicas without sticky sessions or Read-Your-Writes routing. Users post comments, refresh the page, see their comments vanish, and submit angry support tickets. 5 seconds later, the replica catches up and the comment reappears. <em>Mitigation:</em> Implement <strong>Read-Your-Own-Writes</strong> via routing cookies or update client UI optimistically in React/browser state.",
      "common_mistakes": [
        {"mistake": "Relying on eventual consistency for financial transactions or inventory reservation.", "correction": "Never use pure eventual consistency where double-spending or overselling causes legal or financial loss. Use strong consistency / linearizability for inventory and ledgers."},
        {"mistake": "Assuming 'eventual' means 'within 100 milliseconds'.", "correction": "Under network degradation, GC pauses, or replica node rebuilding, 'eventual' can stretch to minutes or hours. Always monitor and alert on replication lag percentiles."}
      ],
      "interview_questions": [
        {"question": "How do you implement Read-Your-Own-Writes consistency in a web application using eventual consistency?", "answer": "1. <strong>Timestamp / Cookie Gateway Routing:</strong> When a user writes, update a client cookie `last_write_timestamp = now()`. The API Gateway checks the cookie: if $(T_{\\text{now}} - T_{\\text{write}}) < 5\\text{s}$, route all reads to the primary database; otherwise route to read replicas;<br>2. <strong>Replication LSN Tokens:</strong> The primary returns the transaction's Log Sequence Number (LSN). The client sends this token in read headers. Replicas with `replica.lsn < token` wait or reject the request, forwarding to primary;<br>3. <strong>Optimistic Client State:</strong> The browser immediately updates the local UI state without making a network read request."},
        {"question": "What is the Monotonic Reads consistency model and what anomaly does it prevent?", "answer": "<strong>Monotonic Reads</strong> guarantees that if a client has observed a particular value of an object at time $t_1$, they will never subsequently observe an older version of that object at time $t_2$. It prevents the <strong>Time-Travel Anomaly</strong>: in a cluster with asynchronous read replicas, if a user's first query hits a replica with 10ms lag, and their second query hits a replica with 500ms lag, the user will see data revert to an older state, causing confusion."}
      ]
    },
    {
      "id": "causal-consistency-and-conflict-resolution",
      "title": "Causal Consistency, Last-Write-Wins (LWW) & Conflict-Free Replicated Data Types (CRDTs)",
      "definition": "Causal Consistency is the strongest consistency model that remains 100% available during network partitions. It guarantees that operations that are causally related are observed by every node in the exact same order, while concurrent independent operations may be observed in different orders. Conflict-Free Replicated Data Types (CRDTs) and Last-Write-Wins (LWW) are mathematical strategies used to automatically resolve concurrent conflicting writes.",
      "why_we_need_it": "In collaborative applications (Google Docs, Figma, multiplayer games) and distributed multi-master databases, concurrent edits occur across disconnected nodes. Without formal conflict resolution, concurrent updates either overwrite each other (causing silent data loss) or require manual human merge conflict dialogs.",
      "real_world_analogy": "A group messaging thread: Causal consistency guarantees that a question ('Where should we eat?') is always displayed BEFORE the answer ('Let's get pizza!'). If someone in another chat room says 'Nice weather today', that independent message can arrive before or after the pizza question without causing confusion.",
      "how_it_works": "<p>1. <strong>Causal Consistency Mechanics:</strong> If Event A causes Event B (e.g. User reads Post A and writes Reply B, or User updates profile and sends verification email), every node in the cluster must observe A before B. Events with no causal relationship are <em>concurrent</em> and can be applied in arbitrary order.</p><p>2. <strong>Last-Write-Wins (LWW) Conflict Resolution:</strong> The simplest conflict resolver (used by Cassandra). Each write is tagged with a physical microsecond timestamp. When a conflict occurs, the replica with the highest timestamp overwrites the older timestamp. <em>Fatal Flaw:</em> Physical clock skew causes legitimate updates to be silently dropped, and concurrent edits to different fields in the same object overwrite each other.</p><p>3. <strong>Conflict-Free Replicated Data Types (CRDTs):</strong> Mathematically proven data structures that can be replicated across multiple machines, mutated concurrently without central coordination, and are guaranteed to <strong>automatically converge to identical state</strong> using mathematically Commutative, Associative, and Idempotent merge operators.</p><p>4. <strong>Two Types of CRDTs:</strong><br>&bull; <em>CvRDT (State-based CRDTs):</em> Nodes send their entire state to peers; peers merge states using a join semi-lattice: $\\text{State} = A \\sqcup B$.<br>&bull; <em>CmRDT (Operation-based CRDTs):</em> Nodes broadcast atomic mutation operations over an at-most-once reliable transport layer.</p><p>5. <strong>Classic CRDT Structures:</strong><br>&bull; <em>P-N Counter:</em> Positive-Negative counter (e.g. Likes vs Dislikes). Each node tracks local increments and decrements; merge takes the element-wise maximum.<br>&bull; <em>LWW-Element-Set:</em> Add set and Remove set with timestamps.<br>&bull; <em>RGA / Yjs / Automerge:</em> Sequence CRDTs enabling real-time collaborative text editing without centralized locking (the engine powering Figma and modern collaborative tools).</p>",
      "conceptual_breakdown": [
        "<strong>Mathematical Convergence (Lattice):</strong> CRDT merge functions must satisfy three algebraic properties: Commutative ($A \\sqcup B = B \\sqcup A$), Associative ($(A \\sqcup B) \\sqcup C = A \\sqcup (B \\sqcup C)$), and Idempotent ($A \\sqcup A = A$).",
        "<strong>LWW Silent Data Loss:</strong> If Node 1's physical clock is 10ms behind Node 2, an update made on Node 1 *after* Node 2 will be permanently discarded by LWW.",
        "<strong>Operational Transformation (OT) vs CRDTs:</strong> OT (used in original Google Docs) requires a centralized coordinator server to transform text character indexes; CRDTs are peer-to-peer and require no central coordinator.",
        "<strong>Causal Consistency is the Ceiling for Availability:</strong> Mahajan et al. mathematically proved that Causal Consistency is the strongest possible consistency model achievable in a completely available (AP) system."
      ],
      "arch_diagram": {
        "title": "CRDT Distributed Convergence Pipeline (P-N Counter Lattice Merge)",
        "tiers": [
          {
            "label": "Concurrent Independent Replicas",
            "nodes": [
              {
                "name": "Node A (San Francisco)",
                "type": "service",
                "icon": "🌉",
                "what": "Local state: P=[5, 0], N=[1, 0]",
                "why": "Net balance: +4",
                "when": "Local client click",
                "failure": "Gossips state to Node B"
              },
              {
                "name": "Node B (Tokyo)",
                "type": "service",
                "icon": "🗼",
                "what": "Local state: P=[0, 3], N=[0, 0]",
                "why": "Net balance: +3",
                "when": "Concurrent client click",
                "failure": "Gossips state to Node A"
              }
            ]
          },
          {
            "label": "Asynchronous Gossip Sync",
            "nodes": [
              {
                "name": "CRDT Lattice Merge Engine",
                "type": "database",
                "icon": "🔄",
                "what": "P_merged = max(P_A, P_B) = [5, 3] | N_merged = max(N_A, N_B) = [1, 0]",
                "why": "Commutative, Associative, Idempotent Math",
                "when": "State payload arrival",
                "failure": "Zero conflicts; mathematically identical convergence"
              }
            ]
          },
          {
            "label": "Converged Consistent State",
            "nodes": [
              {
                "name": "Final Converged Counter",
                "type": "database",
                "icon": "🎯",
                "what": "Total = (5 + 3) - (1 + 0) = 7",
                "why": "Both nodes reach 7 with ZERO locks!",
                "when": "Quiescence reached",
                "failure": "100% data preservation"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Conflict Resolution Mechanisms Matrix",
        "columns": ["Mechanism", "Central Coordinator Required?", "Risk of Data Loss", "Implementation Complexity", "Real-World Systems"],
        "rows": [
          ["Last-Write-Wins (LWW)", "No (peer-to-peer timestamp compare)", "High (clock drift silently deletes updates)", "Extremely low (compare timestamps)", "Apache Cassandra, DynamoDB"],
          ["Operational Transformation (OT)", "Yes (Central server transforms operations)", "Zero", "High (complex index transformation matrices)", "Google Docs (original), Etherpad"],
          ["CRDTs (State & Op based)", "No (Completely peer-to-peer)", "Zero (all concurrent edits merged)", "High (data structure design)", "Figma, Apple Notes, Redis Enterprise, Yjs"],
          ["Manual Git-Style Merge", "No", "Zero", "Requires human UI / interactive resolution", "Git, CouchDB"]
        ]
      },
      "tradeoffs": "<strong>CRDTs:</strong> Guarantees 100% conflict-free peer-to-peer convergence without central locks or data loss, but data structures have higher memory overhead (tombstones and metadata must be retained to maintain causal history) and cannot easily express arbitrary relational multi-table invariants (e.g. `balance >= 0`).",
      "failure_scenarios": "<strong>The Negative Inventory CRDT Trap:</strong> An engineer attempts to implement e-commerce product inventory using a CRDT P-N Counter across 3 data centers to achieve zero latency. Product X has 1 item in stock. Simultaneously, User A purchases it in US-East (decrement counter), and User B purchases it in EU-West (decrement counter). Both nodes accept the write locally. When CRDT states merge, the converged inventory is `-1`. Two customers bought 1 physical item! <em>Mitigation:</em> CRDTs CANNOT enforce global negative balance constraints. Inventory reservation MUST use a CP store with distributed consensus or reservation tokens.",
      "common_mistakes": [
        {"mistake": "Relying on Last-Write-Wins (LWW) to resolve concurrent JSON object field edits.", "correction": "LWW at the document level will overwrite the entire document. If User A updates `email` and User B concurrently updates `phone`, LWW will erase one of the updates. Use field-level merging or CRDT maps."},
        {"mistake": "Using CRDTs for financial bank accounts with overdraft limits.", "correction": "CRDTs cannot enforce non-local invariant constraints (like preventing negative balances). Use a linearizable ACID database for bank balances."}
      ],
      "interview_questions": [
        {"question": "How does Figma use CRDTs to achieve real-time collaborative design across hundreds of concurrent designers?", "answer": "Figma represents the canvas as a tree of objects with immutable IDs and fractional index coordinates. Each property (position, color, text) is managed via a CRDT register. When designers concurrently drag shapes or edit colors, operations are transmitted via WebSockets and merged using <strong>Last-Writer-Wins CRDT registers scoped to individual property fields</strong>. Because the merge operator is commutative and associative, every designer's browser converges to the exact identical canvas state without any central locking or server-side transformation delays."},
        {"question": "What are the three mathematical properties required for a CRDT merge function?", "answer": "The merge operator $\\sqcup$ must form a <strong>join-semilattice</strong>, requiring three algebraic invariants: 1. <strong>Commutative:</strong> $A \\sqcup B = B \\sqcup A$ (order of message arrival does not matter); 2. <strong>Associative:</strong> $(A \\sqcup B) \\sqcup C = A \\sqcup (B \\sqcup C)$ (network packet batching does not matter); 3. <strong>Idempotent:</strong> $A \\sqcup A = A$ (duplicate message delivery does not alter the converged state)."}
      ]
    }
  ]
}

# Write Module 14 and 15
with open(HLD_DIR / "module_14.json", "w", encoding="utf-8") as f:
  json.dump(m14, f, ensure_ascii=False, indent=2)
print("Module 14 written successfully!")

with open(HLD_DIR / "module_15.json", "w", encoding="utf-8") as f:
  json.dump(m15, f, ensure_ascii=False, indent=2)
print("Module 15 written successfully!")
