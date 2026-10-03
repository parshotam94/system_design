/**
 * Home Page Interactive Architecture Thought Process Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  initArchitecturePipeline();
});

function initArchitecturePipeline() {
  const pipelineNodes = document.querySelectorAll('.pipeline-node');
  const detailViewer = document.getElementById('pipeline-detail-viewer');
  if (!pipelineNodes.length || !detailViewer) return;

  const pipelineData = {
    "requirements": {
      title: "1. Clarify Requirements & Scope",
      icon: "📋",
      desc: "Dissect vague problem statements into strict Functional Requirements (e.g. multi-floor parking, dynamic pricing) and Non-Functional Goals (e.g. low latency, thread safety). Ask clarifying questions up front.",
      example: "Parking Lot: How many entry gates? Support for EV vs Truck? Single-level or multi-story? Live occupancy display required?"
    },
    "entities": {
      title: "2. Identify Domain Entities",
      icon: "📦",
      desc: "Extract nouns and core tangible domain actors. Distinguish between true Entities (with unique IDs) and Value Objects (immutable data like Money or GPS Coordinates).",
      example: "Entities: ParkingLot, ParkingFloor, ParkingSpot, Vehicle, Ticket, PaymentInvoice, EntryGate, ExitGate."
    },
    "responsibilities": {
      title: "3. Identify Responsibilities (CRC)",
      icon: "🎯",
      desc: "Define what each entity knows (state/invariants) and what it does (behaviors). Apply Single Responsibility Principle (SRP) to prevent bloated 'God classes'.",
      example: "ParkingSpot: tracks availability & vehicle assignment. PricingEngine: calculates cost based on duration & vehicle tier."
    },
    "classes": {
      title: "4. Design Classes & Encapsulation",
      icon: "🏛️",
      desc: "Structure data members, access modifiers (public/private/protected), constructors, RAII resource ownership, and const-correct member methods.",
      example: "class ParkingSpot { private: int spotId; SpotType type; std::unique_ptr<Vehicle> currentVehicle; public: bool isAvailable() const; };"
    },
    "relationships": {
      title: "5. Define Class Relationships",
      icon: "🔗",
      desc: "Establish coupling and lifetime semantics: Composition (Car owns Engine - dies together), Aggregation (Department has Professor), Association, or Inheritance.",
      example: "ParkingFloor has Composition with ParkingSpots (floor owns lifetime of spots). Vehicle has Association with Ticket."
    },
    "interfaces": {
      title: "6. Define Abstract Interfaces",
      icon: "🔌",
      desc: "Design abstract base classes with pure virtual functions (= 0) and virtual destructors. Program to interfaces, not concrete implementations (DIP / OCP).",
      example: "class IPricingStrategy { public: virtual ~IPricingStrategy() = default; virtual double calculateCost(const Ticket& t) = 0; };"
    },
    "patterns": {
      title: "7. Select & Apply Design Patterns",
      icon: "🧩",
      desc: "Choose appropriate creational, structural, and behavioral patterns. Don't force patterns where simple composition suffices; apply Strategy for algorithms, Factory for instantiation, Observer for events.",
      example: "Strategy Pattern for Hourly vs Dynamic Surge Pricing; Observer Pattern for Real-time Display Board updates."
    },
    "implementation": {
      title: "8. Write Maintainable C++ Code",
      icon: "⚡",
      desc: "Implement classes with modern C++ best practices: Smart pointers (`std::unique_ptr`, `std::shared_ptr`), move semantics, thread safety (`std::mutex`, `std::lock_guard`), and const-correctness.",
      example: "std::lock_guard<std::mutex> lock(spotMutex); auto ticket = std::make_unique<Ticket>(vehicle->getId(), spotId);"
    },
    "tradeoffs": {
      title: "9. Evaluate Trade-offs & Concurrency",
      icon: "⚖️",
      desc: "Analyze time/space complexity, memory footprint, cache locality, lock contention, deadlock risks, and extensibility for future business rules.",
      example: "Trade-off: Coarse-grained parking lot mutex is simple but limits throughput under 100 concurrent gate entries; fine-grained floor-level locking improves concurrency."
    }
  };

  pipelineNodes.forEach(node => {
    node.addEventListener('click', () => {
      pipelineNodes.forEach(n => n.classList.remove('active'));
      node.classList.add('active');

      const stepKey = node.getAttribute('data-step');
      const data = pipelineData[stepKey];
      if (data) {
        detailViewer.innerHTML = `
          <div class="pipeline-detail-card">
            <div class="pipeline-detail-icon">${data.icon}</div>
            <div class="pipeline-detail-body">
              <h4>${data.title}</h4>
              <p>${data.desc}</p>
              <div class="pipeline-detail-example">💡 <strong>Applied Example:</strong> ${data.example}</div>
            </div>
          </div>
        `;
      }
    });
  });
}
