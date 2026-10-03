"""
Elaborate generator for Modules 26, 27, and 28.
Matches exact topics from app/data/hld_roadmap.json
"""
import json
from pathlib import Path

HLD_DIR = Path('content/hld')
HLD_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# MODULE 26: System Security & Authentication Architecture
# ==========================================
m26 = {
  "module_id": "26",
  "module_title": "System Security & Authentication Architecture",
  "description": "Master distributed security: Authentication vs Authorization, OAuth 2.0 with PKCE, JWT token architectures, RBAC vs ABAC, TLS 1.3 & envelope encryption at rest, Zero Trust security models, and DDoS/WAF defenses.",
  "topics": [
    {
      "id": "authn-vs-authz-and-oauth2-jwt",
      "title": "Authentication vs Authorization: OAuth 2.0 Authorization Code Flow & JWT Tokens",
      "definition": "Authentication (AuthN) verifies WHO an entity is (identity verification via passwords, biometrics, or cryptographic keys). Authorization (AuthZ) verifies WHAT an authenticated entity is permitted to do (permissions, scopes, access control). OAuth 2.0 is the industry-standard delegated authorization framework, and JSON Web Tokens (JWT) provide cryptographically signed, stateless identity assertions.",
      "why_we_need_it": "In microservices, checking session state against a centralized database on every single inter-service RPC creates a severe database bottleneck. Stateless JWTs allow microservices to verify client identity locally in memory using public-key cryptography (RS256) with zero database queries.",
      "real_world_analogy": "An international airport and hotel: Authentication (AuthN) is showing your government passport at airport customs to prove who you are. Authorization (AuthZ) is checking into a hotel and receiving an RFID keycard (JWT Access Token); the keycard doesn't say your name, but it cryptographically grants access to Room 402 and the 4th-floor gym, but NOT the penthouse suite.",
      "how_it_works": "<p>1. <strong>OAuth 2.0 Authorization Code Flow with PKCE (Proof Key for Code Exchange):</strong> The gold standard for web and mobile apps:<br>&bull; Step 1: Client generates a random `code_verifier` and computes `code_challenge = SHA256(code_verifier)`.<br>&bull; Step 2: Client redirects user to Authorization Server (Auth0/Okta) with `code_challenge`. User logs in.<br>&bull; Step 3: Auth Server redirects back to client with an authorization `code`.<br>&bull; Step 4: Client exchanges `code` + original `code_verifier` for an <strong>Access Token (JWT)</strong> and <strong>Refresh Token</strong> over back-channel TLS. Prevents authorization code interception attacks!</p><p>2. <strong>JWT Structure (Header.Payload.Signature):</strong><br>&bull; <em>Header:</em> Algorithm & token type: `{'alg': 'RS256', 'typ': 'JWT'}`.<br>&bull; <em>Payload:</em> Standard claims (`sub`, `iss`, `exp`, `iat`) and custom scopes (`roles: ['admin']`). Base64URL-encoded (readable by anyone; NOT encrypted!).<br>&bull; <em>Signature:</em> Computed as `RSASHA256(Header + '.' + Payload, PrivateKey)`. Microservices verify the signature using the Auth Server's cached **Public Key (JWKS)**.</p><p>3. <strong>Stateless Verification:</strong> Downstream services verify the signature mathematically in RAM (&lt;0.1ms) without querying a database. Tokens include an expiration timestamp (`exp`).</p><p>4. <strong>Token Revocation & Refresh Tokens:</strong> Short-lived Access Tokens (e.g. 15 minutes) limit the damage of stolen tokens. Long-lived Refresh Tokens (e.g. 30 days) are stored in an encrypted database/Redis table with rotation to detect token theft.</p>",
      "conceptual_breakdown": [
        "<strong>AuthN vs AuthZ:</strong> AuthN answers 'Who are you?' (401 Unauthorized if missing); AuthZ answers 'Are you allowed to execute this action?' (403 Forbidden if denied).",
        "<strong>Asymmetric (RS256) vs Symmetric (HS256):</strong> In RS256, only the Auth Server holds the Private Key to sign tokens; all microservices verify using the public key. In HS256, all microservices must share the secret key, meaning if one microservice is compromised, the attacker can forge admin tokens for the entire system!",
        "<strong>JWT Revocation Problem:</strong> Because JWTs are stateless, you cannot easily revoke a leaked token before its `exp` time without introducing a distributed blacklist (Redis), re-introducing state.",
        "<strong>XSS vs CSRF Token Storage:</strong> Storing JWTs in browser `localStorage` leaves them vulnerable to Cross-Site Scripting (XSS). Store tokens in `HttpOnly, Secure, SameSite=Strict` cookies to defend against JavaScript token theft."
      ],
      "arch_diagram": {
        "title": "OAuth 2.0 PKCE Flow & Stateless JWT Microservice Verification",
        "tiers": [
          {
            "label": "Client Ingress Tier",
            "nodes": [
              {
                "name": "Single Page App (React/Mobile)",
                "type": "client",
                "icon": "📱",
                "what": "Sends Authorization Header",
                "why": "Bearer <JWT_ACCESS_TOKEN>",
                "when": "Every API request",
                "failure": "Refreshes via Refresh Token on 401"
              }
            ]
          },
          {
            "label": "Centralized Identity Tier (Auth Server)",
            "nodes": [
              {
                "name": "Auth0 / Keycloak Server",
                "type": "database",
                "icon": "🏛️",
                "what": "Signs JWTs with Private RSA Key",
                "why": "Issues tokens via OAuth 2.0 PKCE flow",
                "when": "Login & token refresh",
                "failure": "Exposes public JWKS keyset"
              }
            ]
          },
          {
            "label": "Decoupled Microservice Fleet",
            "nodes": [
              {
                "name": "Order Microservice",
                "type": "service",
                "icon": "📦",
                "what": "Verifies RS256 signature in RAM",
                "why": "Zero database calls! Uses cached public JWKS",
                "when": "Request arrival",
                "failure": "Rejects expired or tampered signatures"
              },
              {
                "name": "Payment Microservice",
                "type": "service",
                "icon": "💳",
                "what": "Verifies RS256 signature in RAM",
                "why": "Zero database calls! Uses cached public JWKS",
                "when": "Request arrival",
                "failure": "Rejects expired or tampered signatures"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Session Tokens vs JSON Web Tokens (JWT)",
        "columns": ["Feature", "Stateful Server Sessions (Redis/DB)", "Stateless JWT Tokens"],
        "rows": [
          ["Storage Location", "Server RAM/Redis (Session ID in Cookie)", "Client stores token; verified in-memory by services"],
          ["Microservice Scalability", "Requires centralized Redis lookup on every RPC", "Unlimited horizontal scale (Stateless local signature check)"],
          ["Revocation Capability", "Instantaneous (Delete session ID from Redis)", "Difficult (Must wait for `exp` or check distributed blacklist)"],
          ["Payload Size", "Tiny (32-byte opaque session ID)", "Large (500 - 2,000 bytes containing claims and signature)"],
          ["Security Model", "Protected by server-side state", "Cryptographic signature validation (RS256 / Ed25519)"]
        ]
      },
      "tradeoffs": "<strong>Stateless JWTs:</strong> Enable boundless microservice scaling without centralized database lookups, but make instant token revocation challenging and increase request header sizes. <strong>Stateful Sessions:</strong> Provide instant revocation and small payload sizes, but create a high-throughput single point of failure in the shared session database.",
      "failure_scenarios": "<strong>The Insecure None Algorithm JWT Hack:</strong> An API uses a poorly configured JWT library that accepts `alg: 'none'` in the header. An attacker modifies a valid token's payload to `{'user_id': 1, 'role': 'admin'}` and sets `alg: 'none'`. The API skips signature verification entirely and grants the attacker full root database administrative access! <em>Mitigation:</em> Hardcode explicit allowed algorithms in verification libraries: `jwt.verify(token, key, algorithms=['RS256'])`, explicitly forbidding `none` or symmetric fallback.",
      "common_mistakes": [
        {"mistake": "Storing sensitive unencrypted data (passwords, social security numbers) inside the JWT payload.", "correction": "JWT payloads are Base64URL-encoded, NOT encrypted! Anyone can decode and read the contents. Only store non-sensitive identifiers and claims."},
        {"mistake": "Setting JWT access token expiration to 30 days.", "correction": "Keep access tokens short-lived (5-15 minutes). Use long-lived refresh tokens stored securely in the database to issue new access tokens."}
      ],
      "interview_questions": [
        {"question": "How do you immediately revoke a stateless JWT before its expiration timestamp?", "answer": "Combine short lifespans with one of three hybrid patterns: 1. <strong>Short-Lived Access Tokens (Best Practice):</strong> Set access token TTL to 5-15 minutes. Revoking the refresh token in the database guarantees that the user loses access within 15 minutes without any blacklist overhead;<br>2. <strong>Distributed Blacklist (Bloom Filter + Redis):</strong> When a user logs out or changes passwords, add the JWT's `jti` (unique JWT ID) to Redis with a TTL matching the token's remaining lifespan. Services check Redis on sensitive mutations;<br>3. <strong>User Token Version / Epoch:</strong> Include a `token_version: 5` in the JWT claims and in the user's database record. When revoking sessions, increment the database `token_version` to 6. Any token presenting version 5 is instantly rejected."},
        {"question": "What is OAuth 2.0 PKCE and why is it mandatory for modern mobile and single-page apps?", "answer": "In traditional OAuth 2.0 Authorization Code Flow, the client exchanges the authorization code for a token using a `client_secret`. However, Single Page Apps (React/Vue) and Mobile Apps are <strong>Public Clients</strong>: they cannot securely store a secret (attackers can decompile the app or inspect browser source code). <strong>PKCE (Proof Key for Code Exchange)</strong> eliminates the client secret: 1. The client generates a dynamic secret `code_verifier` and sends its SHA-256 hash (`code_challenge`) to the auth server; 2. When exchanging the authorization code, the client sends the original `code_verifier`; 3. The auth server hashes it and verifies it matches the original challenge. Even if a malicious app intercepts the authorization code, it cannot exchange it for a token without the `code_verifier`."}
      ]
    },
    {
      "id": "rbac-vs-abac-and-api-security",
      "title": "Access Control: Role-Based (RBAC) vs Attribute-Based (ABAC) & API Key Management",
      "definition": "Access Control governs which authenticated users can perform specific operations on designated resources. Role-Based Access Control (RBAC) assigns permissions to user roles (Admin, Editor, Viewer). Attribute-Based Access Control (ABAC) evaluates dynamic Boolean policies based on attributes of the user, resource, action, and environment. API Key Management provides programmatic authentication with cryptographic hashing, scoping, and rotation.",
      "why_we_need_it": "Simple RBAC fails when business rules require context: e.g., 'A doctor can view medical records ONLY if the patient is currently assigned to that doctor's hospital ward during the doctor's active shift'. Trying to express this in RBAC results in a 'Role Explosion' (creating thousands of hyper-specific roles). ABAC enables granular, context-aware policy enforcement.",
      "real_world_analogy": "Building security badges: RBAC is having a 'Janitor' keycard that unlocks all maintenance closets in every building. ABAC is a smart biometric door lock that evaluates: 'Allow access IF badge holder is an Engineer, AND time is between 9 AM - 5 PM on a weekday, AND the laboratory safety equipment is verified active'.",
      "how_it_works": "<p>1. <strong>RBAC (Role-Based Access Control):</strong> Users are assigned one or more Roles (e.g., `ROLE_BILLING_ADMIN`). Roles are mapped to coarse-grained Permissions (`invoice:create`, `invoice:read`). Simple to understand and fast to evaluate in memory ($O(1)$ lookup in user claims).</p><p>2. <strong>ABAC (Attribute-Based Access Control / Open Policy Agent):</strong> Evaluates policy rules written in languages like Rego (OPA):<br>&bull; <em>Subject Attributes:</em> User role, department, clearance level.<br>&bull; <em>Resource Attributes:</em> Document owner, classification ('Confidential'), tenant ID.<br>&bull; <em>Action Attributes:</em> Read, Write, Delete, Approve.<br>&bull; <em>Environment Attributes:</em> Current time of day, client IP geolocation, device security posture.</p><p>3. <strong>Open Policy Agent (OPA):</strong> Decouples policy decision-making from application business logic. Application services query an OPA sidecar proxy over localhost REST/gRPC: `Is user X allowed to execute action Y on resource Z?`. OPA evaluates the policy and returns `allow: true/false` in microseconds.</p><p>4. <strong>Secure API Key Management:</strong><br>&bull; <em>Storage:</em> NEVER store API keys in plaintext in databases! Store a cryptographic one-way hash (e.g. SHA-256) of the key, showing the raw key to the user ONLY ONCE at creation time.<br>&bull; <em>Key Prefixing (GitHub / Stripe Standard):</em> Prefix keys with readable identifiers: `sk_live_51M...` or `ghp_...`. Enables automated secret-scanning bots to detect leaked keys in public GitHub commits instantly.</p>",
      "conceptual_breakdown": [
        "<strong>Role Explosion Trap:</strong> In pure RBAC, adding regional, tenant, or departmental constraints forces creating roles like `US_EAST_FINANCE_APPROVER_TIER2`, quickly resulting in thousands of unmanageable roles.",
        "<strong>Policy as Code:</strong> Defining security policies in version-controlled declarative code (Rego / Cedar) with automated unit tests.",
        "<strong>API Key Salt & Hash:</strong> Store `SHA256(api_key)` in the database. When a request arrives, hash the provided key and query `SELECT * FROM keys WHERE key_hash = ?`.",
        "<strong>Least Privilege Principle:</strong> Every user, service, and API key should be granted the minimum permissions required to perform its specific task and nothing more."
      ],
      "arch_diagram": {
        "title": "Decoupled Policy Architecture (Microservice + Open Policy Agent OPA)",
        "tiers": [
          {
            "label": "Client API Call",
            "nodes": [
              {
                "name": "API Request",
                "type": "client",
                "icon": "📱",
                "what": "POST /documents/doc_42/delete",
                "why": "User attempts sensitive mutation",
                "when": "Client action",
                "failure": "Evaluated against policy"
              }
            ]
          },
          {
            "label": "Enforcement Point (PEP)",
            "nodes": [
              {
                "name": "Document Microservice",
                "type": "service",
                "icon": "⚙️",
                "what": "Policy Enforcement Point (PEP)",
                "why": "Intercepts request; queries OPA sidecar",
                "when": "Before executing delete",
                "failure": "Returns 403 Forbidden if denied"
              }
            ]
          },
          {
            "label": "Decision Point (PDP - Open Policy Agent)",
            "nodes": [
              {
                "name": "OPA Daemon (Local Sidecar)",
                "type": "database",
                "icon": "⚖️",
                "what": "Evaluates Rego Rules in <1ms",
                "why": "Checks: user.department == doc.dept AND doc.locked == false",
                "when": "Localhost evaluation",
                "failure": "Enforces ABAC decision"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "RBAC vs ABAC Comparison Matrix",
        "columns": ["Dimension", "Role-Based Access Control (RBAC)", "Attribute-Based Access Control (ABAC)"],
        "rows": [
          ["Decision Basis", "Static user roles (Admin, Editor, Viewer)", "Dynamic attributes (User, Resource, Environment, Action)"],
          ["Policy Granularity", "Coarse-grained (User can edit all documents)", "Fine-grained (User can edit document IF owner AND during work hours)"],
          ["Scalability to Complex Rules", "Poor (Suffers from catastrophic Role Explosion)", "High (Single dynamic rule covers millions of resources)"],
          ["Evaluation Latency", "Instantaneous (O(1) role check in memory)", "Low (Evaluates boolean policy expressions in OPA)"],
          ["Governance & Auditability", "Simple (Audit who has which role)", "Requires Policy-as-Code test suites and telemetry"]
        ]
      },
      "tradeoffs": "<strong>RBAC:</strong> Simple to understand, easy to model in relational database tables, and lightning fast to evaluate, but cannot express context-dependent or fine-grained rules. <strong>ABAC:</strong> Virtually unlimited expressive power and eliminates role explosion, but requires deploying dedicated policy engines (OPA) and managing complex policy code.",
      "failure_scenarios": "<strong>The Plaintext API Key Database Leak:</strong> A SaaS company stores customer API keys in plaintext in MySQL. A developer's SQL backup script is accidentally uploaded to an open AWS S3 bucket. Attackers extract 50,000 live production API keys and drain customer accounts. <em>Mitigation:</em> Treat API keys exactly like passwords: **never store plaintext keys**! Store only `SHA256(api_key)` and display the key only once upon generation.",
      "common_mistakes": [
        {"mistake": "Hardcoding authorization checks inside application business logic (e.g. `if user.role == 'admin' or user.id == doc.owner`).", "correction": "Decouple authorization into an external Policy-as-Code engine (Open Policy Agent) or dedicated security middleware."},
        {"mistake": "Generating API keys as simple sequential numbers or predictable strings.", "correction": "Generate API keys using cryptographically secure random bytes (e.g. 256 bits from `/dev/urandom`) with distinct prefixes (`sk_live_...`)."}
      ],
      "interview_questions": [
        {"question": "When does Role-Based Access Control (RBAC) break down, and how does Attribute-Based Access Control (ABAC) solve it?", "answer": "RBAC breaks down when permissions depend on <strong>context or relationships</strong> rather than static job titles. For example, in an electronic health record system, an 'Oncologist' should not have access to ALL patient files globally—only patients assigned to their clinic during active treatment. Expressing this in RBAC requires creating millions of hyper-specific roles (e.g. `DOCTOR_CLINIC_A_PATIENT_B`), leading to <strong>Role Explosion</strong>. <strong>ABAC</strong> solves this with a single dynamic rule: `allow IF user.role == 'doctor' AND user.clinic_id == resource.clinic_id AND resource.status == 'active'`, evaluating attributes dynamically at runtime."},
        {"question": "How do you design a secure API Key management architecture like Stripe or GitHub?", "answer": "1. <strong>Generation:</strong> Generate 256 bits of cryptographic entropy and format with a recognizable prefix (`sk_live_...`) to enable automated secret detection in git commits;<br>2. <strong>One-Way Hash Storage:</strong> Compute `SHA256(key)` and store only the hash, key prefix (e.g. `sk_live_51M...`), creation date, and allowed scopes in the database. Display the full key to the user <strong>only once</strong>;<br>3. <strong>Authentication & Verification:</strong> On incoming API calls, hash the submitted key, query the database by `key_hash` in an indexed lookup, verify that it is active, and enforce attached rate limits and permissions;<br>4. <strong>Automated Scoping & Rotation:</strong> Support granular permissions per key and provide seamless dual-key rotation without service downtime."}
      ]
    },
    {
      "id": "encryption-and-zero-trust-architecture",
      "title": "Encryption in Transit (TLS 1.3), At Rest (AES-256 Envelope Encryption) & Zero Trust Principles",
      "definition": "Cryptographic architecture protects distributed systems across all physical boundaries: Encryption in Transit (TLS 1.3 and mutual TLS / mTLS) protects data over the network; Encryption at Rest (AES-256 with Envelope Encryption) protects physical disk bytes; and Zero Trust Architecture eliminates perimeter-based trust, enforcing continuous mutual authentication and least-privilege verification for every single network packet.",
      "why_we_need_it": "Traditional security relied on the 'Castle-and-Moat' model: once an attacker breached the external firewall or compromised an employee VPN, they had free unencrypted access to all internal microservices and databases. Zero Trust assumes the internal network is already compromised, encrypting and authenticating every internal microservice call.",
      "real_world_analogy": "High-security biological research laboratory: Castle-and-Moat is having a guard at the front gate, but once inside, all doors are unlocked. Zero Trust is having biometric fingerprint scanners and airlocks at every single hallway and room inside the building: even the lab director must scan their badge and iris to walk from the cafeteria into the refrigerator room.",
      "how_it_works": "<p>1. <strong>Encryption in Transit (TLS 1.3 & mTLS):</strong><br>&bull; <em>TLS 1.3:</em> Slashes handshake latency to a single round-trip (1-RTT) or zero round-trip (0-RTT resumption) using Diffie-Hellman Ephemeral (DHE) key exchange, providing Perfect Forward Secrecy.<br>&bull; <em>Mutual TLS (mTLS via Service Mesh / Envoy):</em> Both client and server present X.509 cryptographic certificates to verify each other's identity. All inter-service network packets inside the Kubernetes cluster are encrypted on the wire with automated certificate rotation via HashiCorp Vault or cert-manager.</p><p>2. <strong>Encryption at Rest & Envelope Encryption (AWS KMS):</strong> Encrypting a 100GB database directly with a centralized Master Key over the network is slow and insecure. Envelope Encryption uses a two-tier key hierarchy:<br>&bull; <em>Data Encryption Key (DEK):</em> Generated locally. Used to encrypt the actual data on disk using AES-256-GCM.<br>&bull; <em>Key Encryption Key (KEK / KMS Master Key):</em> The DEK is encrypted using the KMS Master Key (which never leaves the Hardware Security Module / HSM).<br>&bull; The encrypted data and the <strong>Encrypted DEK</strong> are stored together on disk. To decrypt: the server sends the Encrypted DEK to KMS, KMS decrypts the DEK and returns it in RAM, and the server decrypts the data.</p><p>3. <strong>The 3 Tenets of Zero Trust (NIST SP 800-207):</strong><br>&bull; <em>1. Verify Explicitly:</em> Always authenticate and authorize based on all available data points (identity, location, device health).<br>&bull; <em>2. Use Least Privilege Access:</em> Limit user and service access with Just-In-Time and Just-Enough-Access (JIT/JEA).<br>&bull; <em>3. Assume Breach:</em> Minimize blast radius, segment networks, verify end-to-end encryption, and use automated threat detection.</p>",
      "conceptual_breakdown": [
        "<strong>Envelope Encryption Advantage:</strong> Encrypts gigabytes of data locally at hardware speed with the DEK, while the centralized KMS only manages tiny 256-bit keys, preventing network bottlenecks.",
        "<strong>Perfect Forward Secrecy (PFS):</strong> Generates unique ephemeral session keys for each TLS session. Even if an attacker steals the server's private RSA key in the future, past recorded network traffic CANNOT be decrypted!",
        "<strong>Service Identity (SPIFFE / SPIRE):</strong> Assigns cryptographic identities to container workloads (`spiffe://prod/ns/orders/sa/orders-worker`), enabling automated mTLS between microservices without manual passwords.",
        "<strong>Hardware Security Modules (HSM):</strong> Tamper-resistant physical cryptographic hardware (FIPS 140-2 Level 3) where master encryption keys are generated and stored; keys can never be exported in plaintext."
      ],
      "arch_diagram": {
        "title": "Zero Trust mTLS & Envelope Encryption Pipeline (KMS + AES-256)",
        "tiers": [
          {
            "label": "Zero Trust Network Layer (mTLS via Envoy)",
            "nodes": [
              {
                "name": "Service A (Envoy Sidecar)",
                "type": "service",
                "icon": "🛡️",
                "what": "mTLS Handshake with X.509 Cert",
                "why": "Authenticates service identity cryptographically",
                "when": "Inter-service call",
                "failure": "Rejects untrusted certificates"
              },
              {
                "name": "Service B (Envoy Sidecar)",
                "type": "service",
                "icon": "🛡️",
                "what": "Validates Client Cert & Encrypts Wire",
                "why": "Zero unencrypted internal network packets",
                "when": "Wire transit",
                "failure": "Enforces mutual authentication"
              }
            ]
          },
          {
            "label": "Hardware Security Module (AWS KMS)",
            "nodes": [
              {
                "name": "AWS KMS / HashiCorp Vault",
                "type": "gateway",
                "icon": "👑",
                "what": "Master Key (KEK) inside HSM",
                "why": "Encrypts Data Encryption Key (DEK)",
                "when": "Envelope generation",
                "failure": "Master key NEVER leaves physical HSM!"
              }
            ]
          },
          {
            "label": "Encrypted Storage Tier (At Rest)",
            "nodes": [
              {
                "name": "PostgreSQL Database Disk",
                "type": "database",
                "icon": "💾",
                "what": "AES-256 Ciphertext + Encrypted DEK",
                "why": "Raw disk bytes are completely unreadable if stolen",
                "when": "Flushed to disk",
                "failure": "Survives physical hard drive theft"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "Castle-and-Moat vs Zero Trust Architecture",
        "columns": ["Dimension", "Castle-and-Moat (Perimeter Security)", "Zero Trust Architecture"],
        "rows": [
          ["Trust Assumption", "Internal corporate network is safe; external internet is dangerous", "Assume internal network is already compromised"],
          ["Inter-Service Comms", "Plaintext HTTP over internal VPC network", "Mutual TLS (mTLS) with short-lived X.509 certificates"],
          ["Network Segmentation", "Flat network; broad access once past VPN", "Micro-segmentation; each pod isolated by software policies"],
          ["Blast Radius on Breach", "Total (Attacker moves laterally across entire data center)", "Isolated to single microservice container"],
          ["Access Validation", "Validated once at login perimeter", "Continuously validated for every single request and packet"]
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> Zero Trust eliminates lateral movement by attackers and guarantees regulatory compliance (HIPAA, PCI-DSS, GDPR), but adds computational overhead (continuous TLS handshakes) and operational complexity (managing short-lived certificate authorities and service meshes).",
      "failure_scenarios": "<strong>The Lateral Movement Ransomware Nightmare:</strong> An attacker breaches a low-priority public marketing blog running outdated WordPress. The company uses a flat 'Castle-and-Moat' VPC network where internal database connections use unencrypted plaintext. The attacker sniffs the internal subnet, intercepts database passwords in transit, connects to the central customer database, and encrypts all tables with ransomware. <em>Mitigation:</em> <strong>Zero Trust & mTLS</strong>: all internal communication must require mutual TLS authentication, and database connections must enforce SSL/TLS encryption with strict network security group micro-segmentation.",
      "common_mistakes": [
        {"mistake": "Sending raw unencrypted database backups across the internet to an off-site cloud storage bucket.", "correction": "Always use Client-Side Envelope Encryption: encrypt backup files with AES-256 *before* transmitting them across network boundaries."},
        {"mistake": "Using long-lived static TLS certificates (e.g. valid for 5 years) for internal microservices.", "correction": "Use automated certificate management (SPIRE / cert-manager) with ephemeral certificates that rotate automatically every 24 hours."}
      ],
      "interview_questions": [
        {"question": "How does Envelope Encryption work and why is it used instead of encrypting data directly with a Master Key?", "answer": "In <strong>Envelope Encryption</strong>, data is encrypted locally using a unique <strong>Data Encryption Key (DEK)</strong> with AES-256-GCM. The DEK itself is then encrypted using a <strong>Key Encryption Key (KEK)</strong> managed by a centralized service like AWS KMS. The encrypted data and the encrypted DEK are stored together on disk.<br>Advantages: 1. <strong>Performance & Scale:</strong> Encrypting multi-gigabyte databases or files across the network using KMS would saturate network bandwidth; Envelope encryption encrypts large data locally at CPU memory speeds, sending only tiny 256-bit keys to KMS; 2. <strong>Security:</strong> The Master Key (KEK) never leaves the physical Hardware Security Module (HSM), eliminating the risk of master key theft."},
        {"question": "What is Mutual TLS (mTLS) and how does it establish identity in a microservices architecture?", "answer": "In standard TLS, only the server presents a certificate to prove its identity to the client (like a browser verifying a bank website). In <strong>Mutual TLS (mTLS)</strong>, <em>both the client and the server present X.509 digital certificates</em> to each other during the TLS handshake. The server verifies the client's certificate against a trusted internal Certificate Authority (CA) and extracts the client's identity (e.g. SPIFFE ID: `spiffe://cluster/ns/prod/sa/order-service`). This guarantees both <strong>end-to-end encryption on the wire</strong> AND <strong>cryptographic authentication of the calling microservice</strong>, completely preventing man-in-the-middle attacks and spoofing on internal networks."}
      ]
    },
    {
      "id": "ddos-mitigation-and-waf",
      "title": "DDoS Defense (SYN Flood, HTTP Flood) & Web Application Firewall (WAF) Rules",
      "definition": "Distributed Denial of Service (DDoS) attacks attempt to exhaust network bandwidth, server sockets, or application CPU by flooding targets with traffic from distributed botnets. Volumetric attacks (SYN Floods, UDP Amplification) strike Layers 3 and 4; Application attacks (HTTP Floods, Slowloris) strike Layer 7. Web Application Firewalls (WAF) inspect HTTP payloads to filter out SQL Injection (SQLi), Cross-Site Scripting (XSS), and malicious bots.",
      "why_we_need_it": "A 100 Gbps SYN flood can saturate an entire datacenter's internet transit pipe in 2 seconds. A Slowloris attack can hold open 20,000 Apache connections with almost zero attacker bandwidth. Defending modern systems requires multi-layered edge mitigation combining Anycast scrubbing, SYN Cookies, and adaptive WAF inspection.",
      "real_world_analogy": "Defending a VIP government building: A Volumetric DDoS attack is an angry mob of 100,000 people blocking all 8 highway lanes leading to the building (absorbed by Anycast highway diversion). An Application Layer HTTP Flood is 50,000 fake tourists entering the lobby and asking the receptionist for detailed historical tax records from 1850 (filtered by WAF bouncers checking credentials and intent).",
      "how_it_works": "<p>1. <strong>Layer 3/4 Volumetric Defense (SYN Floods & UDP Amplification):</strong><br>&bull; <em>SYN Flood:</em> Attacker sends millions of TCP SYN packets with spoofed IP addresses. The server allocates memory for half-open connections (SYN-RECEIVED) and waits for ACK, exhausting memory.<br>&bull; <em>SYN Cookies Defense:</em> The server does NOT allocate memory! It encodes connection state cryptographically into the Initial Sequence Number (ISN) of the SYN-ACK packet. Only when the client returns a valid ACK does the server verify the cookie and allocate memory, completely immune to SYN floods!<br>&bull; <em>BGP Anycast Scrubbing Centers:</em> Cloudflare/AWS Shield distribute multi-terabit volumetric floods across 250 global PoPs, filtering attack packets at the edge.</p><p>2. <strong>Layer 7 Application Attacks (HTTP Flood & Slowloris):</strong><br>&bull; <em>Slowloris:</em> Sends valid HTTP headers at an agonizingly slow pace (1 byte every 10 seconds), keeping server worker threads pinned. <em>Defense:</em> Enforce strict minimum data rate timeouts at the reverse proxy (NGINX `client_body_timeout 5s`).<br>&bull; <em>HTTP Flood:</em> Botnets submit thousands of complex search queries (`GET /search?q=...`) to burn database CPU. <em>Defense:</em> Challenge botnets with Cloudflare Turnstile / CAPTCHAs, rate limit by JA3 fingerprint, and enforce WAF rules.</p><p>3. <strong>Web Application Firewall (WAF) Rules (OWASP Top 10):</strong> Analyzes incoming HTTP requests using regex and AST tokenizers to block: SQL Injection (`' OR 1=1--`), Cross-Site Scripting (`<script>`), Remote File Inclusion, and Log4j exploit strings (`${jndi:ldap:...}`).</p>",
      "conceptual_breakdown": [
        "<strong>L3/L4 vs L7 Attacks:</strong> L3/L4 targets network bandwidth and OS socket buffers (measured in Gbps / PPS); L7 targets application CPU and database queries (measured in Requests Per Second / RPS).",
        "<strong>SYN Cookies:</strong> Cryptographic mechanism allowing servers to establish TCP connections without allocating memory until the handshake finishes.",
        "<strong>WAF False Positives:</strong> Overly aggressive WAF rules will accidentally block legitimate customer checkouts. Always deploy new WAF rules in 'Count / Monitor' mode before enforcing 'Block'.",
        "<strong>Origin Concealment:</strong> Your origin server IP must NEVER be exposed to the public internet! Lock down origin firewalls to accept traffic ONLY from CDN edge IP CIDR blocks."
      ],
      "arch_diagram": {
        "title": "Multi-Layered DDoS & WAF Defense Architecture",
        "tiers": [
          {
            "label": "Global Edge Scrubbing Tier (Cloudflare / AWS Shield)",
            "nodes": [
              {
                "name": "Anycast BGP Edge (100+ Tbps)",
                "type": "lb",
                "icon": "🌐",
                "what": "Absorbs L3/L4 SYN & UDP Floods",
                "why": "SYN Cookies eliminate half-open state",
                "when": "Network ingress",
                "failure": "Scrubbed traffic passed downstream"
              },
              {
                "name": "Cloud WAF Engine",
                "type": "gateway",
                "icon": "🛡️",
                "what": "Inspects HTTP Payloads (OWASP Top 10)",
                "why": "Blocks SQLi, XSS, and credential stuffing",
                "when": "L7 parsing",
                "failure": "Challenges suspicious traffic via Turnstile"
              }
            ]
          },
          {
            "label": "Private Transit Barrier",
            "nodes": [
              {
                "name": "AWS PrivateLink / Origin Firewall",
                "type": "gateway",
                "icon": "🔒",
                "what": "Allows ONLY CDN IP CIDR ranges",
                "why": "Prevents attackers from bypassing CDN to hit origin IP",
                "when": "Packet arrival",
                "failure": "Drops all direct non-CDN packets"
              }
            ]
          },
          {
            "label": "Protected Application Fleet",
            "nodes": [
              {
                "name": "Origin Backend Servers",
                "type": "service",
                "icon": "🏛️",
                "what": "Microservices & Databases",
                "why": "Processes strictly clean, authenticated traffic",
                "when": "Normal execution",
                "failure": "100% capacity reserved for genuine users"
              }
            ]
          }
        ]
      },
      "comparison_matrix": {
        "title": "DDoS Attack Vectors and Defense Mechanisms",
        "columns": ["Attack Type", "Target OSI Layer", "Attack Mechanism", "Primary Defense Strategy"],
        "rows": [
          ["SYN Flood", "Layer 4 (Transport)", "Floods half-open TCP handshakes to exhaust server backlog RAM", "SYN Cookies + L4 Edge Scrubbing (AWS Shield)"],
          ["UDP Amplification", "Layer 3/4 (Network)", "Spoofs victim IP to DNS/NTP servers; reflects 50x amplified data", "Anycast multi-terabit bandwidth absorption + BGP Blackholing"],
          ["Slowloris", "Layer 7 (Application)", "Sends partial HTTP headers slowly (1 byte/10s) to hold threads open", "Reverse proxy connection buffering (NGINX/Envoy) with min data rate limits"],
          ["HTTP Flood", "Layer 7 (Application)", "Botnet spams expensive search/checkout API queries to burn DB CPU", "Edge WAF rate limiting, JA3 TLS fingerprinting, CAPTCHA challenges"],
          ["SQLi / XSS", "Layer 7 (Application)", "Injects malicious database queries or JavaScript payloads", "WAF inspection rules (ModSecurity / AWS WAF managed rules)"]
        ]
      },
      "tradeoffs": "<strong>Trade-off:</strong> Cloud WAF inspection adds ~5-15ms of latency to incoming HTTP requests and can occasionally produce false positives that block legitimate users, but is strictly required to protect against zero-day exploits and volumetric shutdowns.",
      "failure_scenarios": "<strong>The Exposed Origin IP Bypass:</strong> A company spends $50,000/year on enterprise Cloudflare DDoS protection. However, a developer accidentally configures an un-proxied DNS record (`mail.company.com`) pointing to the exact same server IP address. An attacker discovers the origin IP, bypasses Cloudflare completely, and launches a 40 Gbps direct UDP flood at the origin IP, knocking the entire infrastructure offline! <em>Mitigation:</em> <strong>Conceal Origin IPs</strong>: configure origin security groups to accept traffic exclusively from Cloudflare's published IP prefixes, dropping all direct internet traffic.",
      "common_mistakes": [
        {"mistake": "Attempting to mitigate large volumetric DDoS attacks (50 Gbps+) using on-premise firewalls.", "correction": "Your ISP fiber line will saturate long before traffic reaches your firewall. Volumetric attacks MUST be scrubbed at the cloud edge using Anycast CDNs (Cloudflare / AWS Shield)."},
        {"mistake": "Relying on WAF regex rules as a substitute for secure coding practices (like prepared SQL statements).", "correction": "WAF is a secondary defense in depth. Always use Parameterized Queries (Prepared Statements) in code to eliminate SQL Injection fundamentally."}
      ],
      "interview_questions": [
        {"question": "How do SYN Cookies defend against TCP SYN Flood DDoS attacks?", "answer": "In a standard TCP handshake, when the server receives a SYN packet, it allocates memory in its listen queue (SYN backlog) and responds with SYN-ACK. In a SYN flood, the attacker sends millions of SYNs with spoofed IPs, filling the server's backlog and locking out legitimate users. With <strong>SYN Cookies</strong>, the server <em>does NOT allocate any memory or state</em> when receiving a SYN! Instead, it encodes the client's IP, port, and a secret cryptographic hash into the 32-bit Initial Sequence Number (ISN) of the SYN-ACK packet. When the client returns the final ACK with `ack_number = ISN + 1`, the server validates the cryptographic cookie mathematically. If valid, the server allocates connection memory. Attackers spoofing random IPs never return the final ACK, rendering the attack completely harmless to server memory."},
        {"question": "What is the Slowloris attack and how do modern reverse proxies mitigate it?", "answer": "<strong>Slowloris</strong> is a Layer 7 denial of service attack where an attacker opens thousands of concurrent HTTP connections to a web server (like Apache) and transmits valid HTTP headers agonizingly slowly (e.g. sending 1 header line every 15 seconds: `X-Header: value\\r\\n`). Because the HTTP request is incomplete, the server keeps its worker thread open indefinitely waiting for the final `\\r\\n\\r\\n`. With just a few hundred connections and almost zero bandwidth, the attacker starves all web server worker threads. <strong>Mitigation:</strong> Deploy a modern event-driven reverse proxy (NGINX, Envoy, or HAProxy) in front of the application. NGINX uses non-blocking `epoll` which can hold 100,000 idle connections with minimal RAM, and enforces strict timeouts (`client_header_timeout 5s`, `client_body_timeout 10s`), dropping connections that fail to transmit data at a healthy rate."}
      ]
    }
  ]
}

# Write Module 26
with open(HLD_DIR / "module_26.json", "w", encoding="utf-8") as f:
  json.dump(m26, f, ensure_ascii=False, indent=2)
print("Module 26 written successfully!")
