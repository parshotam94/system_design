"""
Elaborate generator for Modules 16, 17, and 18.
Matches exact topics from app/data/hld_roadmap.json
"""
import json
from pathlib import Path

HLD_DIR = Path('content/hld')
HLD_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# MODULE 16: Distributed Consensus: Raft, Paxos & Quorums
# ==========================================
m16 = {
  "module_id": "16",
  "module_title": "Distributed Consensus: Raft, Paxos & Quorums",
  "description": "Master distributed consensus algorithms: Quorum mathematics (R + W > N), the Raft consensus protocol (Leader Election, Log Replication, Safety Invariants), and Paxos / ZooKeeper ZAB / etcd in production.",
  "topics": [
    {
      "id": "why-consensus-and-quorum-math",
      "title": "The Consensus Problem, Split-Brain & Quorum Arithmetic (R + W > N)",
      "definition": "The Distributed Consensus Problem is the challenge of getting a cluster of independent, potentially failing computers to agree on a single state value, sequence of log decisions, or leader election. Quorum Arithmetic (R + W > N) is the mathematical foundation ensuring that read and write operations always overlap on at least one current node without requiring 100% cluster agreement.",
      "why_we_need_it": "In a distributed system without consensus, a network partition causes multiple nodes to declare themselves 'Leader' simultaneously (Split-Brain), accepting conflicting writes and permanently destroying database integrity. Consensus algorithms guarantee that even if network cables are cut and machines crash, the cluster agrees on a single total order of state.",
      "real_world_analogy": "A courtroom jury of 12 people: To reach a verdict, the court requires a majority quorum. If 2 jurors get sick (node failures), the remaining 10 can still deliberate and reach a binding decision. If the courtroom is cut off from the outside world, no external rogue group can overturn the majority's verified vote.",
      "how_it_works": "<p>1. <strong>The Impossibility of Consensus (FLP Theorem):</strong> Fischer, Lynch, and Paterson mathematically proved that in a purely asynchronous distributed system, <em>no deterministic consensus protocol can guarantee termination in the presence of even a single unannounced crash failure</em>. Practical systems (Raft, Paxos) circumvent FLP by introducing randomized election timeouts or partial synchrony assumptions.</p><p>2. <strong>Quorum Arithmetic ($R + W > N$):</strong> In a cluster of $N$ replicas:<br>&bull; A write must be acknowledged by $W$ nodes (Write Quorum).<br>&bull; A read must query $R$ nodes (Read Quorum).<br>&bull; If $R + W > N$ (by the Pigeonhole Principle), the set of nodes read from and the set of nodes written to MUST overlap by at least 1 node! That overlapping node holds the newest timestamp or version number, guaranteeing strong consistency.</p><p>3. <strong>Majority Quorums ($Q = \\lfloor N/2 \\rfloor + 1$):</strong> In consensus protocols (Raft/Paxos), both $R$ and $W$ are set to a strict majority: in a 5-node cluster, $Q = 3$. Any two majorities of size 3 in a 5-node cluster will always intersect by at least one node, preventing split-brain.</p><p>4. <strong>Split-Brain Prevention:</strong> By requiring a strict majority ($>50\\%$), a cluster can NEVER be partitioned into two competing groups that both have a majority. If a 5-node cluster splits into 3 and 2, ONLY the 3-node partition can operate. The 2-node partition cannot form a majority and halts.</p>",
      "conceptual_breakdown": [
        "<strong>Pigeonhole Principle:</strong> If $N=5$, $W=3$, and $R=3$, then $3 + 3 = 6 > 5$. At least one node in every read was part of the previous write quorum.",
        "<strong>Fault Tolerance Formula:</strong> A cluster of size $N$ can tolerate $F = \\lfloor (N-1)/2 \\rfloor$ failures. A 3-node cluster tolerates 1 failure; a 5-node cluster tolerates 2 failures; a 7-node cluster tolerates 3 failures.",
        "<strong>Why Even Node Counts are Suboptimal:</strong> A 4-node cluster requires 3 nodes for majority ($4/2 + 1 = 3$). It can still only tolerate 1 failure ($4 - 3 = 1$), identical to a 3-node cluster, but introduces an extra node that can fail.",
        "<strong>Sloppy Quorums vs Strict Quorums:</strong> In Cassandra, 'Sloppy Quorums' allow writes to temporary surrogate nodes when primary replicas are down, trading strict consistency for high availability."
      ],
      "arch_diagram": {
        "title": "Quorum Intersection Mechanics (Pigeonhole Principle Overlap)",
        "tiers": [
          {
            "label": "Write Quorum (W = 3 of 5 Nodes)",
            "nodes": [
              {
                "name": "Node 1 (Written: v2)",
                "type": "database",
                "icon": "✍️",
                "what": "Acknowledged Write v2",
                "why": "Part of Write Quorum",
                "when": "Client mutation",
                "failure": "State preserved"
              },
              {
                "name": "Node 2 (Written: v2)",
                "type": "database",
                "icon": "✍️",
                "what": "Acknowledged Write v2",
                "why": "Part of Write Quorum",
                "when": "Client mutation",
                "failure": "State preserved"
              },
              {
                "name": "Node 3 (Overlap Node: v2)",
                "type": "database",
                "icon": "🎯",
                "what": "THE INTERSECTION NODE!",
                "why": "Present in BOTH Write & Read Quorums!",
                "when": "Guarantees Freshness",
                "failure": "Pigeonhole overlap"
              }
            ]
          },
          {
            "label": "Read Quorum (R = 3 of 5 Nodes)",
            "nodes": [
              {
                "name": "Node 4 (Stale: v1)",
                "type": "database",
                "icon": "📖",
                "what": "Did not receive Write v2",
                "why": "Missed write quorum",
                "when": "Read query",
                "failure": "Overridden by Node 3"
              },
              {
                "name": "Node 5 (Stale: v1)",
                "type": "database",
                "icon": "📖",
                "what": "Did not receive Write v2",
                "why": "Missed write quorum",
                "when": "Read query",
                "failure": "Overridden by Node 3"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Cluster Size vs Fault Tolerance Matrix",
        "columns": ["Cluster Size (N)", "Majority Quorum (N/2 + 1)", "Maximum Tolerable Node Failures", "Recommendation"],
        "rows": [
          ["1 Node", "1", "0 Failures", "Development / Testing only (Single point of failure)"],
          ["2 Nodes", "2", "0 Failures (Losing 1 node loses quorum!)", "NEVER USE IN PRODUCTION (Worse than 1 node)"],
          ["3 Nodes", "2", "1 Failure", "Standard production for non-critical coordination"],
          ["4 Nodes", "3", "1 Failure (Same as 3 nodes, but more failure points)", "Avoid (Even number anti-pattern)"],
          ["5 Nodes", "3", "2 Failures", "Gold standard for etcd, ZooKeeper, and Consul in enterprise"],
          ["7 Nodes", "4", "3 Failures", "High-security global control planes (higher write latency)"]
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> Increasing cluster size from 3 to 7 nodes improves crash resilience (survives 3 dead servers instead of 1), but increases write latency because the leader must collect more network votes before committing any log entry.",
      "failure_scenarios": "<strong>The Split-Brain Dual-Primary Catastrophe:</strong> A 4-node cluster splits into two equal 2-node partitions during a switch failure. Both sides attempt to elect a leader. If the quorum check is buggy (e.g. requires $\\ge 50\\%$ instead of $> 50\\%$), both sides elect a leader and accept customer payments independently. When the network heals, transactions conflict irrecoverably. <em>Mitigation:</em> Strict odd node sizing ($N=5$) and mathematically strict majority checking ($> \\lfloor N/2 \\rfloor$).",
      "common_mistakes": [
        {"mistake": "Setting up a 2-node consensus cluster assuming it provides high availability.", "correction": "A 2-node cluster requires 2 votes for a majority. If either node dies, quorum is lost and the cluster freezes. Always use 3 or 5 nodes."},
        {"mistake": "Configuring Cassandra with Read=1 and Write=1 and expecting strong consistency.", "correction": "For strong consistency, you must configure $R=\\text{QUORUM}$ and $W=\\text{QUORUM}$ so that $R + W > N$."}
      ],
      "interview_questions": [
        {"question": "What is the FLP Impossibility Theorem and how do real-world consensus systems bypass it?", "answer": "The <strong>FLP Theorem</strong> (Fischer, Lynch, Paterson) proves that in an asynchronous network, no deterministic consensus protocol can guarantee both safety (correctness) and liveness (eventual progress) if even one node can crash. Real-world systems like Raft and Paxos bypass FLP by: 1. Making <strong>partial synchrony assumptions</strong> (network delays and processing speeds are bounded *most* of the time); and 2. Introducing <strong>randomized election timeouts</strong> (in Raft), which breaks deterministic symmetry and ensures split votes resolve quickly."},
        {"question": "If a Cassandra cluster has Replication Factor N=5, what values of R and W guarantee strong consistency?", "answer": "Any combination where $R + W > 5$. Common configurations: 1. <strong>Balanced:</strong> $W=3$ (QUORUM) and $R=3$ (QUORUM) ($3 + 3 = 6 > 5$); 2. <strong>Fast Reads:</strong> $R=1$ and $W=5$ (ALL) ($1 + 5 = 6 > 5$, ideal for read-heavy caches); 3. <strong>Fast Writes:</strong> $W=1$ and $R=5$ (ALL) ($1 + 5 = 6 > 5$, ideal for high-throughput write ingestion)."}
      ]
    },
    {
      "id": "raft-consensus-algorithm",
      "title": "Raft Protocol: Leader Election, Heartbeats, Log Replication & Safety Invariants",
      "definition": "Raft is an understandable consensus algorithm designed by Ongaro and Ousterhout at Stanford as an alternative to Multi-Paxos. Raft decomposes consensus into three independent sub-problems: Leader Election (using randomized election timers), Log Replication (forcing follower logs to match the leader's append-only log), and Safety Invariants (preventing uncommitted or overwritten historical commits).",
      "why_we_need_it": "Paxos is notoriously esoteric and difficult to implement in production without subtle correctness bugs. Raft delivers equivalent formal safety and performance while being modular and understandable, forming the foundation of modern infrastructure like Kubernetes (etcd), HashiCorp Consul, CockroachDB, and TiKV.",
      "real_world_analogy": "A constitutional republic with regular term elections: Citizens (Followers) listen to the President (Leader). If the President stops broadcasting weekly radio addresses (Heartbeats), citizens get suspicious. A citizen steps up, declares a new Term Number, and asks for votes (Candidate). Whichever candidate receives votes from a majority of citizens becomes the new President. If the old President wakes up from a coma, their term number is expired, so they immediately step down.",
      "how_it_works": "<p>1. <strong>Node States:</strong> Every Raft node exists in one of three states: <em>Leader</em> (handles all client requests and coordinates replication), <em>Follower</em> (passive, responds to RPCs from leaders and candidates), or <em>Candidate</em> (attempts to elect itself leader).</p><p>2. <strong>Leader Election & Randomized Timers:</strong><br>&bull; Followers expect periodic `AppendEntries` heartbeat RPCs from the leader (every 50-100ms).<br>&bull; If a follower's <strong>Election Timeout</strong> (randomized between 150ms and 300ms) elapses with no heartbeat, it increments its `currentTerm`, transitions to Candidate, votes for itself, and broadcasts `RequestVote` RPCs.<br>&bull; Randomized timeouts prevent split votes: one node's timer almost always expires first.<br>&bull; The candidate that receives votes from a majority of nodes becomes Leader and immediately begins sending heartbeats.</p><p>3. <strong>Log Replication:</strong> Client sends command to Leader &rarr; Leader appends entry to its local log &rarr; Leader broadcasts `AppendEntries` RPC to all followers &rarr; Once a majority of followers acknowledge writing the entry to disk, the leader <strong>Commits</strong> the entry and applies it to its local state machine &rarr; Leader returns success to client &rarr; Followers commit entry on next heartbeat.</p><p>4. <strong>Raft Safety Invariants:</strong><br>&bull; <em>Election Safety:</em> At most one leader can be elected in a given term.<br>&bull; <em>Leader Append-Only:</em> A leader never overwrites or truncates its own log entries; it only appends.<br>&bull; <em>Log Matching Property:</em> If two logs contain an entry with the same index and term, they are identical in all entries up through the given index.<br>&bull; <em>Leader Completeness:</em> A voter REJECTS candidate votes if the candidate's log is less up-to-date than the voter's own log (`candidate_last_term < voter_last_term` or shorter log). This guarantees that a newly elected leader already contains ALL committed entries from all previous terms!</p>",
      "conceptual_breakdown": [
        "<strong>Randomized Election Timers:</strong> The genius of Raft. Spreading timeouts randomly between 150ms and 300ms ensures split-vote ties are resolved in 1-2 election rounds.",
        "<strong>Term Numbers:</strong> Logical clocks that detect obsolete leaders. If a leader receives an RPC with `term > currentTerm`, it immediately steps down to follower.",
        "<strong>Log Overwrite Mechanics:</strong> If a follower has uncommitted log entries that conflict with the leader, the leader forces the follower's log to overwrite its conflicting entries with the leader's entries.",
        "<strong>Linearizable Reads (ReadIndex):</strong> Prevents reading from an obsolete leader during a network partition by verifying heartbeats with a majority before returning data."
      ],
      "arch_diagram": {
        "title": "Raft State Transitions & Majority Log Replication Pipeline",
        "tiers": [
          {
            "label": "Client Ingress Tier",
            "nodes": [
              {
                "name": "Client Write: SET x=42",
                "type": "client",
                "icon": "💻",
                "what": "Sends command to Leader",
                "why": "All mutations must enter through Leader",
                "when": "Client interaction",
                "failure": "Redirected to Leader if follower contacted"
              }
            ]
          },
          {
            "label": "Elected Raft Leader (Term 2)",
            "nodes": [
              {
                "name": "Leader Node (Log Index 5)",
                "type": "database",
                "icon": "👑",
                "what": "Appends entry [Term:2, Cmd: x=42]",
                "why": "Coordinates majority replication",
                "when": "Write received",
                "failure": "Steps down if higher term seen"
              }
            ]
          },
          {
            "label": "Follower Quorum Tier",
            "nodes": [
              {
                "name": "Follower Node 1 (ACK)",
                "type": "database",
                "icon": "🛡️",
                "what": "Flushes entry to disk log",
                "why": "Forms 2/3 majority vote with Leader",
                "when": "AppendEntries RPC",
                "failure": "Leader commits entry!"
              },
              {
                "name": "Follower Node 2 (Lagging)",
                "type": "database",
                "icon": "⏳",
                "what": "Network delayed / transiently slow",
                "why": "Cluster proceeds without waiting!",
                "when": "Catches up on next heartbeat",
                "failure": "Does not block client commit"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Raft vs Multi-Paxos Comparison Matrix",
        "columns": ["Dimension", "Raft Consensus", "Multi-Paxos"],
        "rows": [
          ["Understandability & Teaching", "High (Structured into election, replication, safety)", "Very Low (Abstract, notoriously difficult)"],
          ["Leader Election", "Randomized timeouts, heartbeats, single leader per term", "Complex phase-1 leader proposals, dual leaders possible"],
          ["Log Structure", "Strict sequential append-only; no holes permitted", "Log can contain out-of-order uncommitted holes"],
          ["Membership Changes", "Joint Consensus / Single-server stepping", "Complex phase reconfiguration"],
          ["Production Adoption", "etcd (K8s), Consul, CockroachDB, TiKV, Kafka (KRaft)", "Google Spanner, Google Chubby, Apache Cassandra"]
        ]
      },
      "tradeoffs": "<strong>Pros of Raft:</strong> Formal safety, high performance, clean decomposition, easy to audit and reason about, battle-tested in Kubernetes. <strong>Cons:</strong> All client writes must funnel through the single elected leader, creating a potential throughput bottleneck. Systems with extreme write scale use Multi-Raft (sharding data into independent Raft groups).",
      "failure_scenarios": "<strong>The Split-Vote Stalemate (Non-Randomized Timers):</strong> An engineer implements Raft but sets a fixed 200ms election timeout on all 5 nodes. The leader dies. At exactly 200ms, all 4 followers time out, increment their term, and vote for themselves. Every candidate receives exactly 1 vote. The election fails. 200ms later, all 4 time out again and vote for themselves. The cluster remains leaderless indefinitely! <em>Mitigation:</em> Election timeouts MUST be randomized: `rand(150ms, 300ms)` so one candidate always claims majority first.",
      "common_mistakes": [
        {"mistake": "Allowing a Raft follower to vote for a candidate whose log is older or shorter than its own.", "correction": "Followers must reject candidates with less up-to-date logs (`candidate.last_term < voter.last_term` or equal term but shorter log length) to enforce the Leader Completeness invariant."},
        {"mistake": "Serving client read queries directly from a Raft leader's local memory without verifying leadership lease.", "correction": "An isolated leader might not know it was deposed. Use ReadIndex or Leader Leases to guarantee non-stale reads."}
      ],
      "interview_questions": [
        {"question": "How does Raft ensure that a newly elected leader never overwrites or misses previously committed log entries?", "answer": "Through the <strong>Leader Completeness Property</strong> enforced during leader election: when a candidate broadcasts `RequestVote`, it includes its last log index and term. A voter compares the candidate's log with its own log. The voter <strong>refuses to vote</strong> if the candidate's log is less up-to-date (if the candidate's last term is lower, or if terms match but the candidate's log is shorter). Because any committed entry must reside on a majority of nodes, and electing a leader requires a majority of votes, the two majorities must overlap by at least one node. That overlapping node will deny its vote to any candidate lacking the committed entry, ensuring the winner already contains all committed entries."},
        {"question": "What is Multi-Raft and why is it used in CockroachDB and TiKV?", "answer": "In standard Raft, a single cluster has one leader, limiting write throughput to what a single server can process. In <strong>Multi-Raft</strong>, the database divides its key space into small ranges (e.g. 64MB chunks). Each range forms an independent, isolated Raft consensus group with its own leader and followers. A single physical machine acts as leader for some ranges and follower for others. This scales write throughput horizontally across hundreds of nodes while maintaining strict linearizable consensus per range."}
      ]
    },
    {
      "id": "paxos-and-production-coordination",
      "title": "Paxos Concepts, Zookeeper ZAB & Production Coordination Services (etcd, Consul)",
      "definition": "Paxos is the foundational consensus protocol invented by Leslie Lamport. Modern distributed systems rely on battle-tested Production Coordination Services based on consensus protocols: Apache ZooKeeper (using the ZAB protocol), etcd (using Raft), and HashiCorp Consul (using Raft and Serf Gossip).",
      "why_we_need_it": "Large-scale distributed systems require a 'brain' to store critical cluster configuration, track live node memberships, elect service masters, and coordinate distributed locks. Writing custom ad-hoc consensus protocols in application code inevitably leads to data loss. Coordination services provide linearizable distributed primitives as a robust shared platform.",
      "real_world_analogy": "The United Nations Secretariat: Independent nations (microservices) make their own domestic decisions, but when they need to agree on international borders, treaty terms, or formal disputes (cluster configuration, leader election, distributed locks), they record and ratify agreements through the formal, immutable charter of the UN Secretariat (ZooKeeper / etcd).",
      "how_it_works": "<p>1. <strong>Basic Paxos Phases:</strong><br>&bull; <em>Phase 1 (Prepare / Promise):</em> Proposer chooses unique proposal number $n$ and sends `Prepare(n)` to Acceptors. Acceptors return `Promise(n)` agreeing not to accept proposals $< n$ and returning the highest proposal they already accepted.<br>&bull; <em>Phase 2 (Accept / Acknowledged):</em> Proposer sends `Accept(n, value)`. If a majority of Acceptors acknowledge, the value is chosen.</p><p>2. <strong>Apache ZooKeeper & ZAB Protocol:</strong> ZooKeeper exposes a hierarchical file-system tree of <strong>znodes</strong> (`/services/order_service/leader`). It uses the <strong>ZAB (ZooKeeper Atomic Broadcast)</strong> protocol, featuring a recovery mode (leader election) and broadcast mode (atomic two-phase commit log replication).</p><p>3. <strong>etcd (Kubernetes Backbone):</strong> A modern, lightweight, strongly consistent key-value store written in Go, using Raft. etcd powers the entire control plane of Kubernetes, storing all pod manifests, secrets, and cluster state. It features gRPC streaming, Watch APIs, and multi-version concurrency control (MVCC) with transactional compare-and-swap (`Txn`).</p><p>4. <strong>HashiCorp Consul:</strong> Combines a Raft-based CP coordination key-value store with an AP Serf Gossip protocol for decentralized node failure detection, service discovery, and service mesh traffic control.</p>",
      "conceptual_breakdown": [
        "<strong>Hierarchical Tree vs Flat Key-Value:</strong> ZooKeeper organizes state as a filesystem directory tree with znodes; etcd v3 uses a flat binary key space with range queries and MVCC revision counters.",
        "<strong>Watches & Event Streams:</strong> Instead of clients continuously polling for configuration changes (burning network and CPU), clients register a <em>Watch</em>. The coordination service pushes an event immediately when a key mutates or expires.",
        "<strong>Ephemeral Leases:</strong> Nodes attach a time-to-live lease to their registration key. If the node crashes, the lease expires and the key is automatically pruned from service discovery.",
        "<strong>Small Data Invariant:</strong> Coordination services are designed for small metadata (keys &lt;1MB). Storing massive datasets or binary blobs in etcd degrades Raft performance and exhausts memory."
      ],
      "arch_diagram": {
        "title": "Production Coordination Architecture (Kubernetes Control Plane on etcd)",
        "tiers": [
          {
            "label": "Control Plane API Layer",
            "nodes": [
              {
                "name": "Kube-API-Server 1",
                "type": "gateway",
                "icon": "☸️",
                "what": "Stateless REST Control Ingress",
                "why": "Translates kubectl commands into etcd Txns",
                "when": "Continuous deployment operations",
                "failure": "Load balanced across redundant API servers"
              },
              {
                "name": "Kube-API-Server 2",
                "type": "gateway",
                "icon": "☸️",
                "what": "Stateless REST Control Ingress",
                "why": "Translates kubectl commands into etcd Txns",
                "when": "Continuous deployment operations",
                "failure": "Load balanced across redundant API servers"
              }
            ]
          },
          {
            "label": "Consensus Coordination Tier (etcd Raft Cluster)",
            "nodes": [
              {
                "name": "etcd Node 1 (Raft Leader)",
                "type": "database",
                "icon": "👑",
                "what": "Linearizable Raft Leader",
                "why": "Owns all cluster state, pod leases & config",
                "when": "Active majority quorum",
                "failure": "Auto-election promotes Node 2"
              },
              {
                "name": "etcd Node 2 (Raft Follower)",
                "type": "database",
                "icon": "🛡️",
                "what": "Synchronous WAL Replica",
                "why": "Maintains quorum consensus",
                "when": "Every cluster mutation",
                "failure": "Node 3 provides surviving majority"
              },
              {
                "name": "etcd Node 3 (Raft Follower)",
                "type": "database",
                "icon": "🛡️",
                "what": "Synchronous WAL Replica",
                "why": "Maintains quorum consensus",
                "when": "Every cluster mutation",
                "failure": "Node 2 provides surviving majority"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "ZooKeeper vs etcd vs Consul Comparison Matrix",
        "columns": ["Dimension", "Apache ZooKeeper", "CoreOS etcd", "HashiCorp Consul"],
        "rows": [
          ["Consensus Protocol", "ZAB (ZooKeeper Atomic Broadcast)", "Raft Consensus", "Raft (Consensus) + Serf (Gossip)"],
          ["Data Model", "Hierarchical Tree (Znodes)", "Flat Key-Value with MVCC Revisions", "Hierarchical Key-Value + Service Catalog"],
          ["API Protocol", "Custom TCP binary protocol (JNI/Curator)", "gRPC over HTTP/2 + Protobuf", "HTTP / REST + DNS Interface"],
          ["Built-in Service Discovery", "No (must be built on znodes)", "No (used via Kubernetes DNS)", "Yes (Native DNS endpoint: service.consul)"],
          ["Primary Real-World Usage", "Kafka (legacy), Hadoop, HBase", "Kubernetes control plane, Cloud Foundry", "Service Mesh (Envoy), Multi-datacenter discovery"]
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> Coordination services guarantee strict linearizable consistency and bulletproof failure recovery, but cannot scale write throughput horizontally. All cluster mutations must serialize through a single Raft/ZAB leader and write to disk, limiting cluster write throughput to ~10,000-50,000 ops/second.",
      "failure_scenarios": "<strong>The etcd Database Size Limit Meltdown:</strong> By default, etcd enforces a 2GB to 8GB database size quota limit to keep Raft snapshots fast. A misconfigured Kubernetes controller creates millions of ephemeral event objects. etcd hits its 2GB limit, raises an alarm, and switches to <strong>Read-Only Mode</strong>. The entire Kubernetes cluster freezes: no new pods can deploy, auto-scaling stops, and dead pods cannot restart! <em>Mitigation:</em> Enable automated etcd history compaction (`--auto-compaction-retention=1h`), defragment disk spaces periodically, and store ephemeral event metrics outside etcd in a time-series database.",
      "common_mistakes": [
        {"mistake": "Running etcd or ZooKeeper on slow network storage (e.g. standard cloud EBS HDD volumes).", "correction": "Consensus algorithms require low-latency disk fsync. Always run coordination services on dedicated local NVMe SSDs to prevent heartbeat timeouts and leader flapping."},
        {"mistake": "Using ZooKeeper or etcd as a general-purpose application cache or message queue.", "correction": "Never store large user payloads or high-velocity messaging streams in a consensus store. Reserve it exclusively for critical cluster metadata."}
      ],
      "interview_questions": [
        {"question": "How does etcd implement Watch streams efficiently without polling?", "answer": "In etcd v3, Watches use persistent <strong>HTTP/2 gRPC streaming connections</strong>. The client registers a watch on a key or range prefix starting at a specific revision number: `watch(key, start_revision)`. etcd maintains an in-memory B-Tree index of keys to historical MVCC revisions. When a transaction commits, etcd matches the mutated keys against active watchers and pushes the update events down the gRPC stream in O(1) time with sub-millisecond latency and zero polling overhead."},
        {"question": "Why did Apache Kafka remove its dependency on ZooKeeper in favor of KRaft (Kafka Raft)?", "answer": "At massive scale (millions of partitions), maintaining dual state between Kafka brokers and ZooKeeper caused severe synchronization bottlenecks. When a broker crashed, ZooKeeper had to notify all controllers and rebuild metadata, taking tens of minutes to recover. <strong>KRaft (Kafka Raft)</strong> embeds the consensus log directly inside Kafka brokers as an internal metadata topic. This enables instant metadata propagation, accelerates broker failover from 20 minutes to under 1 second, and allows a single Kafka cluster to scale to 10+ million partitions."}
      ]
    }
  ]
}

# Write Module 16
with open(HLD_DIR / "module_16.json", "w", encoding="utf-8") as f:
  json.dump(m16, f, ensure_ascii=False, indent=2)
print("Module 16 written successfully!")
