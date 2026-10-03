import json
import os

CONTENT_DIR = "content/hld"
os.makedirs(CONTENT_DIR, exist_ok=True)

# -------------------------------------------------------------
# MODULE 36: Edge AI, Real-Time Audio/Video & WebRTC
# -------------------------------------------------------------
mod_36 = {
  "module_id": "36",
  "module_title": "Edge AI, Real-Time Audio/Video & WebRTC Architecture",
  "description": "Master ultra-low-latency real-time communications: WebRTC SFU (Selective Forwarding Unit) vs MCU, STUN/TURN/ICE NAT traversal, and Media Servers (Janus / LiveKit).",
  "topics": [
    {
      "id": "webrtc-sfu-vs-mcu-architecture",
      "title": "WebRTC Multi-Party Conferencing: SFU vs MCU & NAT Traversal (STUN/TURN/ICE)",
      "definition": "WebRTC provides peer-to-peer real-time audio, video, and data streaming with sub-500ms latency. For group video calls (Zoom, Google Meet, Discord), media servers route streams using SFU (Selective Forwarding Unit) or MCU (Multipoint Control Unit) topologies.",
      "why_we_need_it": "Mesh peer-to-peer WebRTC collapses for >4 participants because each client must upload $N-1$ video streams simultaneously, saturating uplink bandwidth. SFUs solve group video scaling.",
      "real_world_analogy": "A conference room with 10 people: Mesh is having 10 separate bilateral phone calls (90 calls total). MCU is having a television director mix all 10 video feeds into one composite picture. SFU is a smart postal hub that receives each person's 1 video feed and efficiently forwards copies to the other 9 people without re-encoding.",
      "how_it_works": "<p>1. <strong>NAT Traversal (STUN / TURN / ICE):</strong><br>&bull; <em>STUN:</em> Discovers public IP/Port behind simple NAT.<br>&bull; <em>TURN:</em> Relays encrypted media traffic when symmetric firewall NATs block direct P2P connections.<br>&bull; <em>ICE (Interactive Connectivity Establishment):</em> Framework that tries STUN first and smoothly falls back to TURN relay.<br>2. <strong>SFU (Selective Forwarding Unit - e.g. LiveKit, Mediasoup):</strong> Clients upload 1 video stream (Simulcast with High, Med, Low quality layers). The SFU forwards individual streams without re-encoding (ultra-low CPU cost, supports hundreds of callers per server).<br>3. <strong>MCU (Multipoint Control Unit):</strong> Media server decodes, combines, and re-encodes all incoming video streams into 1 single composite video grid (High CPU cost, high latency, ideal only for legacy hardware video endpoints).</p>",
      "comparison_matrix": {
        "title": "Mesh vs SFU vs MCU Architecture",
        "columns": ["Architecture", "Client Upload Bandwidth", "Server CPU Cost", "Latency", "Max Callers"],
        "rows": [
          ["Mesh (P2P)", "High ($O(N)$ streams uploaded)", "Zero (No server required)", "Ultra-Low (<100ms)", "3 - 4 participants"],
          ["SFU (Selective Forwarding)", "Low (1 stream uploaded)", "Low (Pure packet forwarding)", "Very Low (100 - 200ms)", "Hundreds of participants (Zoom, Discord)"],
          ["MCU (Multipoint Mixing)", "Lowest (1 stream up / 1 down)", "Extremely High (Video re-encoding)", "Moderate (300 - 600ms)", "Limited by server GPU/CPU capacity"]
        ]
      }
    }
  ]
}

# -------------------------------------------------------------
# MODULE 37: Complex Event Processing & Fraud Detection
# -------------------------------------------------------------
mod_37 = {
  "module_id": "37",
  "module_title": "Complex Event Processing & Fraud Detection Systems",
  "description": "Master real-time fraud prevention architectures: Apache Flink CEP, Graph DB fraud rings (Neo4j), Real-Time Rule Engines, and Sliding Window Feature Aggregations.",
  "topics": [
    {
      "id": "real-time-fraud-detection-pipeline",
      "title": "Real-Time Fraud & Anomaly Detection: Flink CEP, Graph DBs & ML Scoring",
      "definition": "A real-time fraud detection system intercepts financial transactions and user actions, evaluating complex pattern sequences, risk rules, and ML inference models in under 50 milliseconds to block fraudulent credit card transactions and account takeovers.",
      "why_we_need_it": "Detecting fraud 2 hours after a transaction via batch jobs is too late; once stolen funds leave the bank, recovery is nearly impossible.",
      "real_world_analogy": "A vigilant airport security scanner: it scans your passport, checks whether you just checked into another airport 5,000 miles away 10 minutes ago (Impossible Velocity), inspects your baggage, and makes a go/no-go decision before you board the plane.",
      "how_it_works": "<p>1. <strong>Event Stream Ingestion:</strong> Kafka ingests payment authorization events at 50,000 events/sec.<br>2. <strong>Stateful Feature Aggregation (Flink + Redis):</strong> Computes real-time sliding window features (e.g. `user_payment_count_last_10min`, `total_amount_last_1hour`, `distinct_ip_count`).<br>3. <strong>Velocity & Rule Checks:</strong> Impossible Travel Rule: detects Card Swipe in London 10 minutes after Card Swipe in New York ($Velocity > 1,000\\text{ km/h}$).<br>4. <strong>Graph DB Fraud Ring Analysis (Neo4j / Amazon Neptune):</strong> Traverses shared device fingerprints, credit card numbers, and shipping addresses to detect organized crime syndicates sharing stolen identities.<br>5. <strong>ML Risk Scoring (Triton / ONNX):</strong> Low-latency (<5ms) gradient-boosted tree / neural network outputs a Risk Score from 0 to 100. Score $\\ge 85$ -> Block; $60-84$ -> Step-up 2FA challenge; $<60$ -> Approve.</p>"
    }
  ]
}

# -------------------------------------------------------------
# MODULE 38: Distributed Caching Internals & Advanced Topologies
# -------------------------------------------------------------
mod_38 = {
  "module_id": "38",
  "module_title": "Distributed Caching Internals & Advanced Topologies",
  "description": "Master multi-tier caching architectures: L1 In-Memory + L2 Distributed Cache coherence, Redis Cluster Gossip protocol & Slot Resharding, and Cache Stampede Mutex locking.",
  "topics": [
    {
      "id": "two-level-caching-and-redis-cluster",
      "title": "Two-Level (L1/L2) Caching Coherence & Redis Cluster Internals",
      "definition": "Two-Level Caching combines a microsecond local in-memory L1 cache (Caffeine/GoCache) on each application server with a sub-millisecond centralized L2 distributed cache (Redis Cluster), maintaining cache coherence via Redis Pub/Sub invalidation broadcasts.",
      "why_we_need_it": "Hot keys getting 100k QPS saturate a single Redis server's network NIC. An L1 in-memory cache absorbs 95% of reads directly in local process RAM (100 nanosecond latency), protecting Redis.",
      "real_world_analogy": "A student taking notes: L1 cache is looking at the page currently on your open desk. L2 cache is looking at a shared textbook on the table. The library (Database) is only visited when neither has the answer.",
      "how_it_works": "<p>1. <strong>L1 + L2 Read Path:</strong> Check local L1 memory -> On Miss check Redis L2 -> On Miss query Database -> Populate L2 and L1.<br>2. <strong>Cache Invalidation Broadcast:</strong> When an application server updates the database, it publishes an invalidation event to a Redis Pub/Sub channel (`cache:invalidate:user_123`). All other application instances receive the message and instantly evict `user_123` from their local L1 memory.<br>3. <strong>Redis Cluster Hash Slots:</strong> Redis Cluster partitions the keyspace across 16,384 Hash Slots (`Slot = CRC16(key) % 16384`). Nodes exchange cluster topology and health pings continuously via the binary Gossip Protocol.</p>"
    }
  ]
}

# -------------------------------------------------------------
# MODULE 39: Cloud-Native & Kubernetes Architecture
# -------------------------------------------------------------
mod_39 = {
  "module_id": "39",
  "module_title": "Cloud-Native & Kubernetes Architecture",
  "description": "Master Kubernetes architecture: Control Plane (API Server, etcd, Scheduler, Kube-Controller), Worker Nodes (Kubelet, Containerd, Kube-Proxy), CNI Overlay Networking, and Ingress Controllers.",
  "topics": [
    {
      "id": "kubernetes-control-plane-and-networking",
      "title": "Kubernetes Architecture: Control Plane, Kubelet, CNI Overlay & Ingress Controllers",
      "definition": "Kubernetes is an open-source container orchestration platform that automates the deployment, scaling, healing, and networking of containerized microservices across a cluster of bare-metal or cloud compute nodes.",
      "why_we_need_it": "Managing 500 Docker containers manually across 50 servers is impossible: containers crash, hosts run out of memory, and rolling updates require complex custom scripting.",
      "real_world_analogy": "A giant container shipping port: The Control Plane is the port authority tower scheduling cranes, assigning docking berths (Nodes), and monitoring cargo manifests. The Kubelet is the local crane operator on each ship loading and unloading shipping containers (Pods).",
      "how_it_works": "<p>1. <strong>Control Plane:</strong><br>&bull; <em>API Server:</em> Stateless gateway handling all REST requests, backed by etcd.<br>&bull; <em>etcd:</em> Distributed key-value store holding 100% of cluster state.<br>&bull; <em>kube-scheduler:</em> Assigns new Pods to worker nodes based on CPU/RAM resources and affinity rules.<br>&bull; <em>kube-controller-manager:</em> Continuously reconciles Desired State vs Actual State.<br>2. <strong>Worker Nodes:</strong><br>&bull; <em>Kubelet:</em> Node agent ensuring containers described in PodSpecs are running and healthy.<br>&bull; <em>Kube-Proxy:</em> Manages IPTables/IPVS routing rules for Kubernetes Service Virtual IPs.<br>&bull; <em>CNI (Container Network Interface - e.g. Cilium / Calico):</em> Implements overlay network (e.g. eBPF or VXLAN) allowing every Pod across the entire cluster to have a unique IP and communicate directly with every other Pod without NAT.</p>"
    }
  ]
}

# -------------------------------------------------------------
# MODULE 40: System Design Interview Mastery & Rubric
# -------------------------------------------------------------
mod_40 = {
  "module_id": "40",
  "module_title": "System Design Interview Mastery & FAANG Rubric",
  "description": "The ultimate interview execution playbook: The 45-Minute 4-Step Framework, FAANG scoring rubrics, trade-off communication strategies, whiteboard layout tactics, and avoiding fatal failure traps.",
  "topics": [
    {
      "id": "system-design-interview-framework",
      "title": "The 45-Minute System Design Interview Blueprint: 4-Step Framework & FAANG Rubric",
      "definition": "A structured battle-tested framework for navigating 45-minute High-Level Design interviews at Tier-1 tech companies (Google, Meta, Amazon, Netflix, Apple, Uber) from initial scoping to deep-dive trade-off defense.",
      "why_we_need_it": "Most candidates fail system design interviews not due to lack of technical knowledge, but due to lack of structure, getting bogged down in minor details, or failing to drive the conversation as a senior engineer.",
      "real_world_analogy": "An architectural presentation to a company CTO: you don't start by discussing which screw to use on the door. You start with business goals and budget, outline the high-level skyscraper blueprints, calculate power and water requirements, and then deep-dive into the earthquake-proofing pillars.",
      "how_it_works": "<p>The 4-Step 45-Minute Interview Timeline:<br>1. <strong>Step 1: Understand Problem & Scope (0 - 8 mins):</strong> Clarify functional requirements (3 core features), non-functional requirements (Availability, Latency, Consistency), constraints, and back-of-the-envelope scale calculations (DAU, QPS, Storage).<br>2. <strong>Step 2: High-Level Design & Core APIs (8 - 20 mins):</strong> Define REST/gRPC API contracts, core database data models, and draw the end-to-end multi-tier architecture diagram (Clients -> CDN -> LB -> Services -> DBs -> Caches).<br>3. <strong>Step 3: Deep-Dive Critical Components (20 - 38 mins):</strong> Zoom in on the hardest architectural bottlenecks: Caching strategies, sharding keys, race condition mitigations, consensus protocols, and failure scenarios.<br>4. <strong>Step 4: Wrap-Up, Bottlenecks & Failure Modes (38 - 45 mins):</strong> Address Single Points of Failure (SPOFs), monitoring metrics, future scaling bottlenecks, and answer interviewer questions.</p>",
      "conceptual_breakdown": [
        "<strong>FAANG Scoring Dimensions:</strong> 1. Scope & Requirement Clarification (20%), 2. Architecture & System Flow (30%), 3. Deep-Dive & Trade-off Justification (30%), 4. Communication & Leadership (20%).",
        "<strong>Golden Interview Rule:</strong> Never state a technology without articulating its trade-off (e.g. 'I choose Cassandra for linear write scalability at the cost of eventual consistency and no JOIN capabilities')."
      ],
      "comparison_matrix": {
        "title": "Junior vs Senior vs Staff System Design Signals",
        "columns": ["Dimension", "Junior / Mid-Level", "Senior Engineer (L5)", "Staff / Principal (L6+)"],
        "rows": [
          ["Problem Scoping", "Jumps directly to drawing boxes without asking questions", "Clarifies functional vs NFRs and estimates QPS/storage", "Drives business ambiguity, scopes out edge cases & constraints"],
          ["Architecture", "Draws generic boxes without clear data flow", "Draws clean multi-tier diagrams with clear component roles", "Designs decoupled event-driven systems with fault domains & blast radius isolation"],
          ["Trade-offs", "Says 'Redis is fast' or 'MongoDB is scalable'", "Articulates concrete trade-offs (e.g. Cache-Aside vs Write-Through)", "Quantifies trade-offs in terms of p99 latency, cost, and failure modes"],
          ["Failure Handling", "Assumes all servers and networks are 100% reliable", "Identifies SPOFs and proposes basic replica failover", "Designs for graceful degradation, circuit breakers, backpressure, and disaster recovery"]
        ]
      },
      "failure_scenarios": "<strong>The Fatal Interview Silence Trap:</strong> Spending 10 minutes silently thinking without speaking to the interviewer. <em>Mitigation:</em> Think out loud continuously, explain your reasoning, and validate design assumptions with the interviewer.",
      "common_mistakes": [
        {
          "mistake": "Rushing into drawing database schemas before clarifying scale and core functional requirements.",
          "correction": "Always spend the first 5-8 minutes scoping features, constraints, and calculating back-of-the-envelope capacity."
        }
      ],
      "interview_questions": [
        {
          "question": "What is the most effective way to communicate trade-offs during a system design interview?",
          "answer": "Use the 'Option A vs Option B' framework: explicitly state the alternative options considered, identify the key constraint or requirement of the current problem, explain why Option A was chosen over Option B under those specific constraints, and acknowledge the known disadvantages and mitigation strategies for Option A."
        }
      ]
    }
  ]
}

modules = [mod_36, mod_37, mod_38, mod_39, mod_40]
for m in modules:
    filename = os.path.join(CONTENT_DIR, f"module_{m['module_id']}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print(f"Generated {filename} with {len(m['topics'])} topics")
