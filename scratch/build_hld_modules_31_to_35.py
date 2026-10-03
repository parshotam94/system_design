import json
import os

CONTENT_DIR = "content/hld"
os.makedirs(CONTENT_DIR, exist_ok=True)

# -------------------------------------------------------------
# MODULE 31: Advanced Distributed Data & Consensus
# -------------------------------------------------------------
mod_31 = {
  "module_id": "31",
  "module_title": "Advanced Distributed Data & Consensus",
  "description": "Master cutting-edge distributed databases: Google Spanner & TrueTime API (GPS/Atomic clocks), CockroachDB Multi-Raft consensus, and CRDTs in real-time collaborative editors (Figma/Google Docs).",
  "topics": [
    {
      "id": "google-spanner-and-truetime",
      "title": "Google Spanner Internals: TrueTime API, Atomic Clocks & External Consistency",
      "definition": "Google Cloud Spanner is the world's first globally distributed database providing both strict External Consistency (Linearizability) and high availability across continents without global locking, powered by hardware GPS and atomic clocks (TrueTime API).",
      "why_we_need_it": "Traditional distributed databases cannot guarantee cross-datacenter serializable transactions without slow global locks or suffering from physical clock skew anomalies.",
      "real_world_analogy": "A synchronized global stopwatch: every master referee in Tokyo, London, and New York has a synchronized atomic watch. If an athlete runs at 12:00:00.000 in Tokyo, the London referee knows with 100% mathematical certainty that an event at 12:00:00.005 in London happened strictly after Tokyo.",
      "how_it_works": "<p>1. <strong>TrueTime API:</strong> Represents time not as a single number, but as an uncertainty interval $[t.earliest, t.latest]$ with bounded error $\\epsilon \\approx 1-7\\text{ms}$.<br>2. <strong>Commit Wait Rule:</strong> When a transaction commits at timestamp $T$, the leader delays returning to the client until $t.earliest > T$ (waiting out the clock uncertainty $\\epsilon$). This guarantees that any subsequent transaction globally will receive a strictly higher commit timestamp.<br>3. <strong>Paxos Groups:</strong> Data is split into Splits (Directories), each managed by its own independent Paxos consensus replication group.<br>4. <strong>Two-Phase Locking (2PL) + Multi-Version Concurrency Control (MVCC):</strong> Readers take lock-free timestamped snapshot reads with zero interference from writers.</p>",
      "conceptual_breakdown": [
        "<strong>External Consistency (Linearizability):</strong> If Transaction 2 starts after Transaction 1 commits anywhere in the world, T2's commit timestamp is strictly greater than T1's.",
        "<strong>Commit Wait:</strong> Waiting out the $\\epsilon$ uncertainty window (~7ms) replaces expensive cross-continent consensus rounds for read transactions."
      ],
      "failure_scenarios": "<strong>Clock Uncertainty Drift Spike:</strong> If GPS antennas or atomic clock oscillators fail, uncertainty $\\epsilon$ widens from 2ms to 200ms, causing Spanner commit wait times to spike to 200ms and degrading write throughput globally. <em>Mitigation:</em> Redundant atomic clock master servers in every datacenter.",
      "interview_questions": [
        {
          "question": "How does Spanner's Commit Wait rule eliminate the need for distributed locks during read transactions?",
          "answer": "By waiting out the clock uncertainty window $\\epsilon$ before finalizing writes, Spanner guarantees that commit timestamps reflect real-world causal ordering. Read transactions simply specify a read timestamp $T_{read}$ and execute lock-free against immutable MVCC snapshots without taking any locks or coordinating with other nodes."
        }
      ]
    },
    {
      "id": "cockroachdb-multi-raft",
      "title": "CockroachDB Architecture: Multi-Raft Consensus, Range Leases & Hybrid Logical Clocks",
      "definition": "CockroachDB is an open-source distributed SQL database that implements Multi-Raft consensus across 64MB key ranges, Hybrid Logical Clocks (HLC), and Range Leases to achieve horizontal SQL scalability and multi-cloud resilience.",
      "why_we_need_it": "A single Raft consensus group becomes a write bottleneck for the entire database. Multi-Raft partitions data into thousands of independent Raft groups running in parallel across the cluster.",
      "real_world_analogy": "A giant company with 1,000 independent product teams: instead of requiring all 10,000 employees to vote on every single decision in one giant meeting, each 10-person team (Range Raft Group) votes on their own localized decisions independently.",
      "how_it_works": "<p>1. <strong>Ranges (64MB):</strong> Database key space is ordered and sliced into contiguous 64MB Ranges.<br>2. <strong>Multi-Raft:</strong> Each Range is replicated across 3 or 5 nodes via its own independent Raft consensus group.<br>3. <strong>Range Leaseholder:</strong> One node in the Raft group is granted a Range Lease, allowing it to serve read requests directly without round-trip Raft consensus votes.<br>4. <strong>Hybrid Logical Clocks (HLC):</strong> Combines physical wall-clock time with logical Lamport counters, bounding clock skew within a configurable threshold (e.g. 500ms) without requiring atomic clock hardware.</p>"
    }
  ]
}

# -------------------------------------------------------------
# MODULE 32: Cost Engineering & FinOps
# -------------------------------------------------------------
mod_32 = {
  "module_id": "32",
  "module_title": "Cost Engineering & FinOps for Cloud Architecture",
  "description": "Master cloud infrastructure cost optimization: AWS/GCP pricing mechanics, EC2 Spot Instances, S3 tiered lifecycle management, Network Egress cost traps, and Rightsizing.",
  "topics": [
    {
      "id": "cloud-cost-mechanics-and-finops",
      "title": "Cloud Cost Economics: Compute (Spot/Savings Plans), Storage & Network Egress",
      "definition": "Cloud Cost Engineering (FinOps) is the discipline of architecting cloud systems to maximize business value while eliminating waste across Compute (On-Demand vs Reserved vs Spot), Storage tiers, and Network Data Transfer (Egress).",
      "why_we_need_it": "Unoptimized cloud architectures can result in massive monthly AWS/GCP bills (e.g. $100k/month spent on avoidable cross-AZ data transfer and oversized idle compute instances).",
      "real_world_analogy": "Insulating a house: leaving air conditioning running with open windows (uncompressed data transfer, idle on-demand compute) runs up electric bills. Proper insulation (Spot instances, S3 lifecycle rules, private VPC endpoints) cuts costs by 70% with zero performance loss.",
      "how_it_works": "<p>1. <strong>Compute Optimization:</strong> Use AWS Savings Plans / Reserved Instances (up to 72% discount) for predictable baseline load + Spot Instances (up to 90% discount) for stateless stateless background worker fleets and ML training.<br>2. <strong>Storage Optimization:</strong> S3 Intelligent-Tiering automatically transitions untouched objects to Glacier Instant / Deep Archive after 30/90 days ($0.023/GB -> $0.00099/GB - a 95% savings).<br>3. <strong>Network Egress Traps:</strong> Data transfer over the public Internet ($0.09/GB) and Cross-AZ data transfer ($0.01/GB in + out) add up to huge costs. <em>Solution:</em> Keep inter-service traffic within the same Availability Zone where possible, and use AWS VPC Endpoints / PrivateLink to avoid internet NAT gateway fees.</p>",
      "comparison_matrix": {
        "title": "AWS Compute Pricing Models Comparison",
        "columns": ["Model", "Discount vs On-Demand", "Commitment", "Interruption Risk", "Best Workload Fit"],
        "rows": [
          ["On-Demand", "0% (Full price)", "None (Pay per second)", "Zero interruptions", "Unpredictable traffic spikes, dev/testing"],
          ["Savings Plans / RI", "30% - 72% discount", "1 or 3 year commitment", "Zero interruptions", "Core databases, API gateways, stable baseline services"],
          ["Spot Instances", "70% - 90% discount", "None (Bidding spare capacity)", "2-minute interruption notice", "Kafka consumers, batch video encoding, ML training"]
        ]
      }
    }
  ]
}

# -------------------------------------------------------------
# MODULE 33: Microservices Communication & Protocols
# -------------------------------------------------------------
mod_33 = {
  "module_id": "33",
  "module_title": "Microservices Communication & Protocols",
  "description": "Master modern inter-service communication: gRPC over HTTP/2, Protocol Buffers v3, GraphQL Federation (Apollo Router), and Asynchronous Event Choreography vs Orchestration.",
  "topics": [
    {
      "id": "grpc-and-protobuf-internals",
      "title": "gRPC & Protocol Buffers v3 Internals: Binary Serialization & HTTP/2 Multiplexing",
      "definition": "gRPC is a high-performance open-source RPC framework that utilizes HTTP/2 for transport (multiplexing, streaming, header compression) and Protocol Buffers (Protobuf) for compact binary serialization.",
      "why_we_need_it": "Text-based JSON over HTTP/1.1 incurs severe CPU serialization overhead and requires opening multiple TCP sockets. gRPC is up to 7x-10x faster with 60% smaller payloads.",
      "real_world_analogy": "JSON is spelling out words using full handwritten English sentences on paper. Protobuf is transmitting compressed binary Morse code pulses: 10x faster and requires 1/5th the ink.",
      "how_it_works": "<p>1. <strong>Protobuf Binary Encoding:</strong> Uses Varints and Tag-Length-Value (TLV) encoding. Field names are NOT transmitted in the payload; only numeric field tags (`tag 1 = int32`, `tag 2 = string`) are encoded, drastically shrinking payload size.<br>2. <strong>HTTP/2 Multiplexing:</strong> Transmits multiple bidirectional RPC calls concurrently over a single persistent TCP connection using binary streams and HPACK header compression.<br>3. <strong>Streaming Paradigms:</strong> Unary (1 request -> 1 response), Server Streaming, Client Streaming, and Bidirectional Streaming.</p>"
    }
  ]
}

# -------------------------------------------------------------
# MODULE 34: Data Privacy, Compliance & Governance
# -------------------------------------------------------------
mod_34 = {
  "module_id": "34",
  "module_title": "Data Privacy, Compliance & Governance (GDPR, HIPAA, PCI-DSS)",
  "description": "Master data regulatory architecture: GDPR Right to be Forgotten in immutable append-only logs, Crypto-Shredding, PCI-DSS Tokenization Vaults, and HIPAA PII / PHI Encryption.",
  "topics": [
    {
      "id": "gdpr-right-to-be-forgotten-crypto-shredding",
      "title": "GDPR Compliance in Immutable Systems: Crypto-Shredding & Anonymization",
      "definition": "GDPR Article 17 mandates the 'Right to be Forgotten' (erasing user personal data on request). In immutable systems (Apache Kafka, Event Sourcing, WORM storage), records cannot be deleted. Crypto-Shredding solves this by encrypting each user's PII with a unique per-user encryption key and destroying the key upon deletion request.",
      "why_we_need_it": "Rewriting multi-terabyte Kafka logs or S3 backups to delete 1 user's email corrupts log offsets and takes hours of compute. Crypto-shredding makes data permanently unreadable in 1 millisecond.",
      "real_world_analogy": "Locking your diary in a steel safe with a unique key: if you throw the key into a volcano (Crypto-Shredding), the diary is still physically in the room, but no one on Earth can ever read it again.",
      "how_it_works": "<p>1. <strong>Per-User Key Management:</strong> When User 123 registers, generate a unique AES-256 Data Encryption Key (DEK) managed in AWS KMS / HashiCorp Vault.<br>2. <strong>Field-Level Encryption:</strong> Encrypt all PII fields (Name, Email, SSN, Address) using `DEK_123` before writing to Kafka or PostgreSQL.<br>3. <strong>Crypto-Shredding (Erasure Request):</strong> When User 123 requests account deletion under GDPR, delete `DEK_123` from the Key Vault. All historical Kafka events, S3 backups, and DB records encrypted with that key become permanently unrecoverable random noise, satisfying legal erasure requirements without modifying append-only logs.</p>"
    }
  ]
}

# -------------------------------------------------------------
# MODULE 35: AI/ML Infrastructure & LLM Serving
# -------------------------------------------------------------
mod_35 = {
  "module_id": "35",
  "module_title": "AI/ML Infrastructure & LLM Serving Architecture",
  "description": "Master production AI/ML architectures: LLM Serving engines (vLLM / Triton / PagedAttention), Vector RAG pipelines, Feature Stores (Feast), and Model Training Pipelines (Kubeflow).",
  "topics": [
    {
      "id": "llm-serving-and-paged-attention",
      "title": "High-Throughput LLM Serving: vLLM, PagedAttention & Continuous Batching",
      "definition": "LLM Serving architecture optimizes inference throughput and GPU VRAM utilization for Large Language Models using PagedAttention (virtual memory paging for KV-Cache) and Continuous (Iteration-Level) Batching.",
      "why_we_need_it": "Traditional naive LLM inference wastes up to 60-80% of GPU VRAM on KV-Cache memory fragmentation and sits idle waiting for variable-length output completions. PagedAttention increases serving throughput by 2x-4x.",
      "real_world_analogy": "Virtual memory paging in an Operating System: instead of requiring contiguous physical memory for a program, the OS divides memory into small 4KB pages. PagedAttention divides GPU attention memory into discrete block pages so non-contiguous VRAM is utilized 100% without waste.",
      "how_it_works": "<p>1. <strong>KV-Cache Bottleneck:</strong> During auto-regressive decoding, Transformer models store Key and Value tensors for all previous tokens in GPU memory. For large context windows (128k tokens), KV-cache dwarfs model weight size.<br>2. <strong>PagedAttention (vLLM):</strong> Allocates KV-cache in non-contiguous physical GPU memory blocks (pages), managed via a logical-to-physical block table.<br>3. <strong>Continuous (Iteration-Level) Batching:</strong> As soon as a request finishes generating its stop token, a new incoming request joins the batch at the very next iteration without waiting for the longest request in the batch to complete.<br>4. <strong>Quantization (AWQ, GPTQ, FP8):</strong> Compresses 16-bit weights to 8-bit or 4-bit, doubling GPU serving density.</p>"
    }
  ]
}

modules = [mod_31, mod_32, mod_33, mod_34, mod_35]
for m in modules:
    filename = os.path.join(CONTENT_DIR, f"module_{m['module_id']}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print(f"Generated {filename} with {len(m['topics'])} topics")
