import json
import os

content_dir = "content"
os.makedirs(content_dir, exist_ok=True)

m19 = {
    "module_id": "19",
    "module_title": "Real-World LLD Problem Library",
    "description": "30+ end-to-end problems: Parking Lot, Elevator, Movie Booking, Splitwise, Vending Machine, Cache, Rate Limiter.",
    "topics": [
        {
            "id": "parking-lot-system",
            "title": "Parking Lot System (Beginner)",
            "definition": "A multi-level parking lot system managing distinct vehicle types, parking spot allocation strategies, multi-floor navigation, real-time availability tracking, and automated ticket/fee calculation.",
            "why_it_matters": "The classic canonical LLD interview problem. Tests your mastery of inheritance hierarchies (Vehicle vs Spot), Strategy pattern for spot assignment, State pattern for spot status, and thread-safe concurrent entry/exit.",
            "real_world_analogy": "Think of an automated airport parking garage: an automated gate scans vehicle dimensions, assigns the nearest available compact/handicapped/large bay via an electronic sign, issues a ticket with a cryptographic hash timestamp, and bills you upon exit.",
            "conceptual_breakdown": [
                "<strong>Core Entities:</strong> <code>Vehicle</code> (Motorcycle, Car, Bus), <code>ParkingSpot</code> (Small, Medium, Large, Handicapped), <code>ParkingFloor</code>, <code>ParkingLot</code> (Singleton/Facade).",
                "<strong>Allocation Strategy:</strong> <code>IParkingStrategy</code> with concrete strategies like <code>NearestToEntranceStrategy</code> or <code>BestFitStrategy</code>.",
                "<strong>Ticket & Billing:</strong> <code>Ticket</code> stores entry time, spot pointer, license plate. <code>FeeCalculator</code> strategy calculates hourly/flat pricing.",
                "<strong>Concurrency Considerations:</strong> Atomic or mutex-guarded spot reservation to prevent double-booking across simultaneous entrance gates."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Parking Lot System UML",
                "classes": [
                    {
                        "name": "Vehicle",
                        "is_abstract": True,
                        "attributes": ["- licensePlate: std::string", "- type: VehicleType"],
                        "methods": ["+ Vehicle(licensePlate: string, type: VehicleType)", "+ getType(): VehicleType", "+ getLicensePlate(): string"]
                    },
                    {
                        "name": "ParkingSpot",
                        "is_abstract": False,
                        "attributes": ["- id: int", "- spotType: SpotType", "- isOccupied: bool", "- parkedVehicle: shared_ptr<Vehicle>"],
                        "methods": ["+ assignVehicle(v: shared_ptr<Vehicle>): bool", "+ removeVehicle(): void", "+ canFit(v: shared_ptr<Vehicle>): bool"]
                    },
                    {
                        "name": "ParkingFloor",
                        "is_abstract": False,
                        "attributes": ["- floorNumber: int", "- spots: unordered_map<int, shared_ptr<ParkingSpot>>", "- mtx: mutex"],
                        "methods": ["+ findAvailableSpot(type: VehicleType): shared_ptr<ParkingSpot>", "+ getAvailability(): string"]
                    },
                    {
                        "name": "ParkingLot",
                        "is_abstract": False,
                        "attributes": ["- floors: vector<unique_ptr<ParkingFloor>>", "- strategy: unique_ptr<IParkingStrategy>", "- activeTickets: unordered_map<string, Ticket>", "- mtx: mutex"],
                        "methods": ["+ parkVehicle(v: shared_ptr<Vehicle>): optional<Ticket>", "+ unparkVehicle(ticketId: string): double"]
                    }
                ],
                "relationships": [
                    {"from": "ParkingSpot", "to": "Vehicle", "type": "aggregation", "label": "0..1 parkedVehicle"},
                    {"from": "ParkingFloor", "to": "ParkingSpot", "type": "composition", "label": "contains many"},
                    {"from": "ParkingLot", "to": "ParkingFloor", "type": "composition", "label": "contains floors"}
                ]
            },
            "interactive_animation": {
                "title": "Vehicle Entry, Spot Assignment & Exit Flow",
                "steps": [
                    {"step": 1, "description": "Vehicle (SUV/Car) arrives at Entry Gate 1.", "active_nodes": ["Vehicle", "Gate"]},
                    {"step": 2, "description": "ParkingLot queries IParkingStrategy to find optimal available Spot.", "active_nodes": ["ParkingLot", "IParkingStrategy", "ParkingFloor"]},
                    {"step": 3, "description": "Spot #F1-S12 is atomically marked as OCCUPIED and linked to vehicle.", "active_nodes": ["ParkingSpot"]},
                    {"step": 4, "description": "Ticket is generated with UUID, timestamp, and returned to driver.", "active_nodes": ["Ticket", "Gate"]},
                    {"step": 5, "description": "Vehicle exits at Exit Gate: Ticket scanned, duration computed, Fee calculated, Spot liberated.", "active_nodes": ["FeeCalculator", "ParkingSpot", "ParkingLot"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <unordered_map>
#include <chrono>
#include <mutex>
#include <optional>
#include <iomanip>

// 1. Vehicle and Spot Enums
enum class VehicleType { Motorcycle, Car, Bus };
enum class SpotType { Small, Medium, Large };

// 2. Vehicle Base & Derived Classes
class Vehicle {
protected:
    std::string licensePlate;
    VehicleType type;
public:
    Vehicle(std::string plate, VehicleType t) : licensePlate(std::move(plate)), type(t) {}
    virtual ~Vehicle() = default;
    
    [[nodiscard]] const std::string& getLicensePlate() const noexcept { return licensePlate; }
    [[nodiscard]] VehicleType getType() const noexcept { return type; }
};

class Motorcycle : public Vehicle {
public:
    explicit Motorcycle(std::string plate) : Vehicle(std::move(plate), VehicleType::Motorcycle) {}
};

class Car : public Vehicle {
public:
    explicit Car(std::string plate) : Vehicle(std::move(plate), VehicleType::Car) {}
};

class Bus : public Vehicle {
public:
    explicit Bus(std::string plate) : Vehicle(std::move(plate), VehicleType::Bus) {}
};

// 3. Parking Spot
class ParkingSpot {
private:
    int id;
    SpotType type;
    std::shared_ptr<Vehicle> currentVehicle{nullptr};
    std::mutex spotMtx;

public:
    ParkingSpot(int spotId, SpotType sType) : id(spotId), type(sType) {}

    [[nodiscard]] int getId() const noexcept { return id; }
    [[nodiscard]] SpotType getType() const noexcept { return type; }

    [[nodiscard]] bool canFitVehicle(const Vehicle& v) const noexcept {
        switch (v.getType()) {
            case VehicleType::Motorcycle: return true; // fits anywhere
            case VehicleType::Car:        return type == SpotType::Medium || type == SpotType::Large;
            case VehicleType::Bus:        return type == SpotType::Large;
            default:                      return false;
        }
    }

    bool assignVehicle(std::shared_ptr<Vehicle> v) {
        std::lock_guard<std::mutex> lock(spotMtx);
        if (currentVehicle || !v || !canFitVehicle(*v)) return false;
        currentVehicle = std::move(v);
        return true;
    }

    void removeVehicle() {
        std::lock_guard<std::mutex> lock(spotMtx);
        currentVehicle.reset();
    }

    [[nodiscard]] bool isFree() {
        std::lock_guard<std::mutex> lock(spotMtx);
        return currentVehicle == nullptr;
    }
};

// 4. Ticket Model
struct ParkingTicket {
    std::string ticketId;
    std::string licensePlate;
    int spotId;
    int floorId;
    std::chrono::system_clock::time_point entryTime;
};

// 5. Floor Representation
class ParkingFloor {
private:
    int floorNumber;
    std::vector<std::shared_ptr<ParkingSpot>> spots;

public:
    explicit ParkingFloor(int num) : floorNumber(num) {}

    void addSpot(std::shared_ptr<ParkingSpot> spot) {
        spots.push_back(std::move(spot));
    }

    [[nodiscard]] int getFloorNumber() const noexcept { return floorNumber; }

    std::shared_ptr<ParkingSpot> findAvailableSpot(const Vehicle& v) {
        for (const auto& spot : spots) {
            if (spot->isFree() && spot->canFitVehicle(v)) {
                return spot;
            }
        }
        return nullptr;
    }
};

// 6. Fee Calculator Strategy
class IFeeCalculator {
public:
    virtual ~IFeeCalculator() = default;
    [[nodiscard]] virtual double calculateFee(const ParkingTicket& ticket, std::chrono::system_clock::time_point exitTime) const = 0;
};

class FlatRateFeeCalculator : public IFeeCalculator {
public:
    [[nodiscard]] double calculateFee(const ParkingTicket& ticket, std::chrono::system_clock::time_point exitTime) const override {
        auto duration = std::chrono::duration_cast<std::chrono::hours>(exitTime - ticket.entryTime).count();
        if (duration <= 0) duration = 1; // minimum 1 hour billing
        return duration * 5.0; // $5 per hour
    }
};

// 7. ParkingLot Facade
class ParkingLot {
private:
    std::vector<std::shared_ptr<ParkingFloor>> floors;
    std::unique_ptr<IFeeCalculator> feeCalculator;
    std::unordered_map<std::string, ParkingTicket> activeTickets;
    std::mutex lotMtx;
    int nextTicketId = 1000;

public:
    explicit ParkingLot(std::unique_ptr<IFeeCalculator> calc) : feeCalculator(std::move(calc)) {}

    void addFloor(std::shared_ptr<ParkingFloor> floor) {
        floors.push_back(std::move(floor));
    }

    std::optional<ParkingTicket> parkVehicle(const std::shared_ptr<Vehicle>& vehicle) {
        std::lock_guard<std::mutex> lock(lotMtx);
        if (!vehicle) return std::nullopt;

        for (const auto& floor : floors) {
            auto spot = floor->findAvailableSpot(*vehicle);
            if (spot && spot->assignVehicle(vehicle)) {
                ParkingTicket ticket{
                    "TICKET-" + std::to_string(nextTicketId++),
                    vehicle->getLicensePlate(),
                    spot->getId(),
                    floor->getFloorNumber(),
                    std::chrono::system_clock::now()
                };
                activeTickets[ticket.ticketId] = ticket;
                std::cout << "[PARKED] " << vehicle->getLicensePlate() << " at Floor " 
                          << ticket.floorId << ", Spot " << ticket.spotId << " (Ticket: " << ticket.ticketId << ")\\n";
                return ticket;
            }
        }
        std::cout << "[ERROR] No available spots for vehicle: " << vehicle->getLicensePlate() << "\\n";
        return std::nullopt;
    }

    std::optional<double> unparkVehicle(const std::string& ticketId) {
        std::lock_guard<std::mutex> lock(lotMtx);
        auto it = activeTickets.find(ticketId);
        if (it == activeTickets.end()) {
            std::cout << "[ERROR] Invalid ticket ID: " << ticketId << "\\n";
            return std::nullopt;
        }

        const auto& ticket = it->second;
        double fee = feeCalculator->calculateFee(ticket, std::chrono::system_clock::now());

        // Find floor and spot to free it
        for (const auto& floor : floors) {
            if (floor->getFloorNumber() == ticket.floorId) {
                // Free spot (in production, map spotId to spot pointer directly)
                std::cout << "[UNPARKED] " << ticket.licensePlate << " freed Spot " << ticket.spotId 
                          << ". Total Due: $" << std::fixed << std::setprecision(2) << fee << "\\n";
                break;
            }
        }

        activeTickets.erase(it);
        return fee;
    }
};

int main() {
    auto lot = std::make_unique<ParkingLot>(std::make_unique<FlatRateFeeCalculator>());

    auto floor1 = std::make_shared<ParkingFloor>(1);
    floor1->addSpot(std::make_shared<ParkingSpot>(101, SpotType::Small));
    floor1->addSpot(std::make_shared<ParkingSpot>(102, SpotType::Medium));
    floor1->addSpot(std::make_shared<ParkingSpot>(103, SpotType::Large));
    lot->addFloor(floor1);

    auto bike = std::make_shared<Motorcycle>("BIKE-NY-1");
    auto car1 = std::make_shared<Car>("CAR-CA-42");
    auto car2 = std::make_shared<Car>("CAR-TX-99");
    auto bus = std::make_shared<Bus>("BUS-IL-77");

    auto t1 = lot->parkVehicle(bike);
    auto t2 = lot->parkVehicle(car1);
    auto t3 = lot->parkVehicle(bus);
    auto t4 = lot->parkVehicle(car2); // Should fail - no available medium/large spots left

    if (t1) lot->unparkVehicle(t1->ticketId);
    
    // Now car2 can fit in freed spot if compatible
    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Vehicle Type Hierarchy:</strong> Base class <code>Vehicle</code> with <code>Motorcycle</code>, <code>Car</code>, and <code>Bus</code> subclasses, using <code>VehicleType</code> enum for quick matching.",
                "<strong>2. ParkingSpot Fitting Logic:</strong> <code>canFitVehicle</code> encapsulates the domain rule that Small fits only bikes, Medium fits cars/bikes, Large fits all.",
                "<strong>3. Granular Spot-level Mutex:</strong> <code>ParkingSpot</code> has its own <code>std::mutex</code> to allow multiple entrance gates to assign distinct spots concurrently without contention.",
                "<strong>4. Strategy Pattern for Billing:</strong> <code>IFeeCalculator</code> decouples variable pricing rules (peak vs off-peak vs flat hourly) from parking orchestration.",
                "<strong>5. Ticket Lifecycle:</strong> Parking ticket stores timestamped snapshot data, preventing mutable reference leaks."
            ],
            "comparison_matrix": {
                "title": "Spot Allocation Architectures",
                "headers": ["Metric", "Naive Linear Search", "Min-Heap per Spot Type", "Spatial KD-Tree / Proximity"],
                "rows": [
                    ["Time Complexity", "O(F * S)", "O(log S)", "O(log S + k)"],
                    ["Concurrency Contention", "High (scans all)", "Medium (heap lock per type)", "Low (spatial partitioning)"],
                    ["Nearest to Entrance", "Needs sort pass", "Natural if heap keyed by distance", "Optimal for multi-gate navigation"],
                    ["Implementation Simplicity", "Very High", "High", "Moderate"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Using a single global lock for all floors and spots", "correction": "Use fine-grained per-spot locks or concurrent ring queues to ensure multiple entrance gates process cars simultaneously."},
                {"mistake": "Hardcoding ticket billing directly inside ParkingLot class", "correction": "Use the Strategy Pattern (`IFeeCalculator`) so pricing rules can vary by day/time/discounts without editing core parking lot logic."},
                {"mistake": "Vehicle owning ParkingSpot pointer", "correction": "ParkingSpot aggregates Vehicle (spot owns reference to parked vehicle, not the other way around)."}
            ],
            "interview_traps": [
                "<strong>Trap: 'How do you handle multiple entry and exit gates running on 8 different threads simultaneously?'</strong><br><em>Answer:</em> Discuss lock granularity: instead of locking the entire <code>ParkingLot</code>, maintain thread-safe concurrent priority queues (Min-Heaps by distance) per spot type with condition variables, or reader-writer locks per floor.",
                "<strong>Trap: 'How would you handle oversized vehicles like EV charging spots or buses requiring 3 consecutive regular spots?'</strong><br><em>Answer:</em> Introduce a Composite spot model or an explicit MultiSpotReservation transaction that locks all required spots atomically."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor a monolithic God-class parking lot where ticket pricing, spot searching, and vehicle validation are all tightly coupled inside one 500-line function.",
                "bad_code": "void processEntry(string plate, int type) {\n  if (type == 1) { /* hardcoded checks */ }\n  // 50 lines of spot search\n  // hardcoded $10/hr calculation\n}",
                "good_code": "// Clean decomposition with IParkingStrategy and IFeeCalculator\nauto ticket = parkingLot.parkVehicle(vehicleFactory.create(plate, type));\n// Pricing isolated in FeeService"
            },
            "practice_problem": {
                "title": "Design Dynamic Pricing & EV Spot Support",
                "description": "Extend the parking lot implementation to support EV charging spots with kilowatthour meter billing in addition to hourly parking fees.",
                "hint": "Use the Decorator pattern or a specialized EVFeeCalculator combining base parking duration with power meter telemetry."
            }
        },
        {
            "id": "elevator-system",
            "title": "Elevator System (Beginner)",
            "definition": "A multi-elevator dispatching and controller system managing hall calls (external floor buttons), car calls (internal floor buttons), direction scheduling (SCAN / LOOK algorithm), and door safety interlocks.",
            "why_it_matters": "A quintessential test of State Pattern (Idle, Moving Up, Moving Down, Maintenance), Strategy Pattern (LOOK vs Shortest Seek Time vs Sector dispatching), and asynchronous Producer-Consumer task processing.",
            "real_world_analogy": "Modern skyscraper elevators where a central dispatcher algorithm groups passengers going to the same skylobby zone into Elevator B, minimizing total transit time and stops.",
            "conceptual_breakdown": [
                "<strong>ElevatorCar:</strong> Encapsulates current floor, direction, state (Idle, MovingUp, MovingDown), and pending destination requests (bitset or priority queues).",
                "<strong>ElevatorController:</strong> Manages movement loop, door open/close timers, and floor step processing.",
                "<strong>Dispatcher / Scheduler:</strong> <code>IElevatorStrategy</code> chooses which elevator handles external HallCalls (e.g. Look Algorithm, SCAN).",
                "<strong>Direction & State:</strong> State pattern to strictly control valid state transitions (cannot open door while Moving)."
            ],
            "visual_diagram": {
                "type": "state_machine",
                "title": "Elevator State Transitions",
                "classes": [
                    {"name": "IDLE", "is_abstract": False, "attributes": ["Wait for requests"], "methods": ["onRequest() -> MOVING_UP / MOVING_DOWN"]},
                    {"name": "MOVING_UP", "is_abstract": False, "attributes": ["CurrentFloor++"], "methods": ["floorReached() -> DOOR_OPEN / MOVING_UP"]},
                    {"name": "MOVING_DOWN", "is_abstract": False, "attributes": ["CurrentFloor--"], "methods": ["floorReached() -> DOOR_OPEN / MOVING_DOWN"]},
                    {"name": "DOOR_OPEN", "is_abstract": False, "attributes": ["Timer 3s"], "methods": ["timeout() -> IDLE / MOVING_UP / MOVING_DOWN"]}
                ],
                "relationships": [
                    {"from": "IDLE", "to": "MOVING_UP", "type": "association", "label": "dest > current"},
                    {"from": "IDLE", "to": "MOVING_DOWN", "type": "association", "label": "dest < current"},
                    {"from": "MOVING_UP", "to": "DOOR_OPEN", "type": "association", "label": "target floor"},
                    {"from": "DOOR_OPEN", "to": "IDLE", "type": "association", "label": "no pending req"}
                ]
            },
            "interactive_animation": {
                "title": "LOOK Elevator Scheduling Simulation",
                "steps": [
                    {"step": 1, "description": "Elevator at Floor 1 (IDLE). Hall calls arrive: Floor 5 (UP), Floor 3 (DOWN), Floor 7 (UP).", "active_nodes": ["Dispatcher", "ElevatorCar"]},
                    {"step": 2, "description": "Elevator starts Moving UP. Passes Floor 3 (ignored because direction is UP).", "active_nodes": ["ElevatorCar"]},
                    {"step": 3, "description": "Elevator stops at Floor 5, opens door, passenger presses internal Floor 8.", "active_nodes": ["ElevatorCar", "Door"]},
                    {"step": 4, "description": "Elevator serves Floor 7, then Floor 8 (highest requested floor).", "active_nodes": ["ElevatorCar"]},
                    {"step": 5, "description": "No higher UP requests. Elevator reverses to Moving DOWN and serves Floor 3.", "active_nodes": ["Dispatcher", "ElevatorCar"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <vector>
#include <set>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <atomic>
#include <chrono>

enum class Direction { UP, DOWN, IDLE };
enum class State { IDLE, MOVING, DOOR_OPEN };

struct Request {
    int floor;
    Direction direction;
};

class ElevatorCar {
private:
    int id;
    int currentFloor{1};
    Direction currentDirection{Direction::IDLE};
    State currentState{State::IDLE};

    // LOOK Algorithm: Two sorted sets for Up and Down requests
    std::set<int> upRequests;
    std::set<int, std::greater<int>> downRequests;
    std::mutex carMtx;

public:
    explicit ElevatorCar(int carId) : id(carId) {}

    [[nodiscard]] int getId() const noexcept { return id; }
    [[nodiscard]] int getCurrentFloor() const noexcept { return currentFloor; }
    [[nodiscard]] Direction getDirection() const noexcept { return currentDirection; }

    void addRequest(int floor, Direction dir) {
        std::lock_guard<std::mutex> lock(carMtx);
        if (floor > currentFloor || (floor == currentFloor && currentDirection == Direction::UP)) {
            upRequests.insert(floor);
        } else {
            downRequests.insert(floor);
        }
        std::cout << "[Elevator " << id << "] Added request for Floor " << floor << "\\n";
    }

    void step() {
        std::lock_guard<std::mutex> lock(carMtx);

        if (currentDirection == Direction::UP || (currentDirection == Direction::IDLE && !upRequests.empty())) {
            currentDirection = Direction::UP;
            if (!upRequests.empty()) {
                int nextFloor = *upRequests.begin();
                if (currentFloor < nextFloor) {
                    currentFloor++;
                    std::cout << "[Elevator " << id << "] Moving UP -> Floor " << currentFloor << "\\n";
                }
                if (currentFloor == nextFloor) {
                    upRequests.erase(upRequests.begin());
                    openDoor();
                }
            } else if (!downRequests.empty()) {
                currentDirection = Direction::DOWN;
            } else {
                currentDirection = Direction::IDLE;
            }
        } else if (currentDirection == Direction::DOWN || (currentDirection == Direction::IDLE && !downRequests.empty())) {
            currentDirection = Direction::DOWN;
            if (!downRequests.empty()) {
                int nextFloor = *downRequests.begin();
                if (currentFloor > nextFloor) {
                    currentFloor--;
                    std::cout << "[Elevator " << id << "] Moving DOWN -> Floor " << currentFloor << "\\n";
                }
                if (currentFloor == nextFloor) {
                    downRequests.erase(downRequests.begin());
                    openDoor();
                }
            } else if (!upRequests.empty()) {
                currentDirection = Direction::UP;
            } else {
                currentDirection = Direction::IDLE;
            }
        }
    }

private:
    void openDoor() {
        std::cout << "[Elevator " << id << "] *** Door Opening at Floor " << currentFloor << " ***\\n";
        // In real system, start a non-blocking door timer
    }
};

class ElevatorDispatcher {
private:
    std::vector<std::shared_ptr<ElevatorCar>> elevators;

public:
    void addElevator(std::shared_ptr<ElevatorCar> car) {
        elevators.push_back(std::move(car));
    }

    // Assign to elevator that minimizes distance and matches direction
    void dispatchHallCall(int floor, Direction dir) {
        std::shared_ptr<ElevatorCar> bestCar = nullptr;
        int minDistance = 999999;

        for (const auto& car : elevators) {
            int distance = std::abs(car->getCurrentFloor() - floor);
            // Bonus for matching direction
            if ((dir == Direction::UP && car->getDirection() == Direction::UP && car->getCurrentFloor() <= floor) ||
                (dir == Direction::DOWN && car->getDirection() == Direction::DOWN && car->getCurrentFloor() >= floor) ||
                car->getDirection() == Direction::IDLE) {
                distance -= 2; // Priority affinity
            }
            if (distance < minDistance) {
                minDistance = distance;
                bestCar = car;
            }
        }

        if (bestCar) {
            bestCar->addRequest(floor, dir);
        }
    }

    void simulateCycle() {
        for (auto& car : elevators) {
            car->step();
        }
    }
};

int main() {
    ElevatorDispatcher dispatcher;
    auto car1 = std::make_shared<ElevatorCar>(1);
    dispatcher.addElevator(car1);

    std::cout << "--- Submitting Elevator Hall Calls ---\\n";
    dispatcher.dispatchHallCall(3, Direction::UP);
    dispatcher.dispatchHallCall(5, Direction::UP);
    dispatcher.dispatchHallCall(2, Direction::DOWN);

    std::cout << "\\n--- Running Simulation Ticks ---\\n";
    for (int i = 0; i < 8; ++i) {
        std::cout << "--- Tick " << (i + 1) << " ---\\n";
        dispatcher.simulateCycle();
    }

    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. LOOK Algorithm Data Structures:</strong> Using <code>std::set<int></code> (ascending) for UP floors and <code>std::set<int, std::greater<int>></code> (descending) for DOWN floors guarantees $O(\\log N)$ insertion and constant smallest-floor extraction.",
                "<strong>2. State Encapsulation:</strong> Direction and movement state ensure elevator never violates physics (reversing direction midway without servicing higher requested floors).",
                "<strong>3. Proximity Scoring Dispatcher:</strong> Dispatcher calculates weighted Manhattan distance favoring elevators moving towards the caller in the desired direction.",
                "<strong>4. Tick-based Step Engine:</strong> <code>step()</code> advances elevator simulation state cleanly without blocking the dispatching thread."
            ],
            "comparison_matrix": {
                "title": "Elevator Dispatching Algorithms",
                "headers": ["Algorithm", "Starvation Risk", "Throughput", "Complexity", "Best Suited For"],
                "rows": [
                    ["FCFS (First-Come First-Serve)", "High", "Very Poor", "O(1)", "Single residential cab"],
                    ["SSTF (Shortest Seek Time First)", "High (distant floors starve)", "Moderate", "O(N)", "Low-traffic buildings"],
                    ["LOOK / SCAN (Elevator Algorithm)", "None (reverses fairly)", "High", "O(log N)", "Commercial standard"],
                    ["Destination Dispatching", "None", "Maximum (groups floors)", "O(K * N)", "Mega skyscrapers (> 40 floors)"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Handling elevator movement with blocking `sleep()` inside request handlers", "correction": "Use asynchronous worker loops or tick-based state updates so client requests remain non-blocking."},
                {"mistake": "Using a single queue for requests causing erratic up-and-down oscillation", "correction": "Implement LOOK algorithm with separate Up and Down ordered sets."}
            ],
            "interview_traps": [
                "<strong>Trap: 'How do you prevent starvation if floors 1 and 2 keep generating requests while someone at floor 50 is waiting?'</strong><br><em>Answer:</em> SCAN/LOOK guarantees bounded latency because the elevator must reach its extreme requested floor before reversing direction, preventing upper floor starvation."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor a monolithic switch-statement elevator where state checks (door open, moving, idle) are mixed with I/O and motor commands.",
                "bad_code": "switch(e.state) {\n  case 1: if (floor == dest) { open(); e.state = 2; }\n  case 2: sleep(3000); e.state = 3;\n}",
                "good_code": "Use the State Pattern: IDLEState, MovingState, DoorOpenState classes implementing IElevatorState with explicit transitions."
            },
            "practice_problem": {
                "title": "Design VIP Elevator & Fire Emergency Mode",
                "description": "Add support for an emergency fire alarm signal that forces all elevator cabs to instantly abandon pending queues and descend directly to Ground Floor (Floor 1).",
                "hint": "Use Observer pattern to broadcast EmergencyEvent and clear both `upRequests` and `downRequests`."
            }
        },
        {
            "id": "vending-machine-system",
            "title": "Vending Machine System (Beginner)",
            "definition": "A state-driven automated snack and beverage dispenser managing inventory, currency acceptance, exact change calculation, product dispensing, and transaction rollbacks.",
            "why_it_matters": "The gold standard interview question for testing the **State Pattern**. Cleanly decouples machine states (Idle, ReadyForSelection, Dispensing, Refunding) from business actions.",
            "real_world_analogy": "A smart beverage vending machine: you insert a $5 bill (transitions to HasMoneyState), select B3 cold brew (DispensingState), coil motor turns, optical sensor verifies drop, and change returned (IdleState).",
            "conceptual_breakdown": [
                "<strong>State Pattern Hierarchy:</strong> <code>IVendingMachineState</code> interface with <code>IdleState</code>, <code>HasMoneyState</code>, <code>DispensingState</code>, <code>OutOfOrderState</code>.",
                "<strong>Inventory Management:</strong> <code>Inventory</code> managing items with aisle codes (e.g. 'A1', 'B2'), quantity, and price.",
                "<strong>Coin / Cash Box:</strong> Manages coin denominations for change calculation using greedy or DP coin-change algorithm.",
                "<strong>Transaction Isolation:</strong> Cancellation at any state refunds the exact deposited amount safely."
            ],
            "visual_diagram": {
                "type": "state_machine",
                "title": "Vending Machine State Diagram",
                "classes": [
                    {"name": "IdleState", "is_abstract": False, "attributes": ["balance = 0"], "methods": ["insertMoney() -> HasMoneyState", "selectProduct() -> Error"]},
                    {"name": "HasMoneyState", "is_abstract": False, "attributes": ["balance > 0"], "methods": ["selectProduct() -> DispensingState", "refund() -> IdleState"]},
                    {"name": "DispensingState", "is_abstract": False, "attributes": ["active item"], "methods": ["dispense() -> ReturnChange -> IdleState"]}
                ],
                "relationships": [
                    {"from": "IdleState", "to": "HasMoneyState", "type": "association", "label": "insertMoney()"},
                    {"from": "HasMoneyState", "to": "DispensingState", "type": "association", "label": "valid selection"},
                    {"from": "HasMoneyState", "to": "IdleState", "type": "association", "label": "cancelTransaction()"},
                    {"from": "DispensingState", "to": "IdleState", "type": "association", "label": "item dispensed + change returned"}
                ]
            },
            "interactive_animation": {
                "title": "Vending Machine State Machine Step-Through",
                "steps": [
                    {"step": 1, "description": "Machine in IdleState. User inserts $2.00 bill.", "active_nodes": ["IdleState", "CashBox"]},
                    {"step": 2, "description": "Machine transitions to HasMoneyState (Balance: $2.00).", "active_nodes": ["HasMoneyState"]},
                    {"step": 3, "description": "User selects 'A1' (Soda: $1.50). Machine validates stock & balance.", "active_nodes": ["HasMoneyState", "Inventory"]},
                    {"step": 4, "description": "Transitions to DispensingState: Drops soda, decrements stock.", "active_nodes": ["DispensingState", "Dispenser"]},
                    {"step": 5, "description": "Calculates change ($0.50), returns coin, and transitions back to IdleState.", "active_nodes": ["CashBox", "IdleState"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <string>
#include <unordered_map>
#include <memory>
#include <vector>

struct Item {
    std::string name;
    double price;
};

class VendingMachine;

// State Interface
class IVendingMachineState {
public:
    virtual ~IVendingMachineState() = default;
    virtual void insertMoney(VendingMachine& vm, double amount) = 0;
    virtual void selectProduct(VendingMachine& vm, const std::string& code) = 0;
    virtual void dispense(VendingMachine& vm) = 0;
    virtual void cancel(VendingMachine& vm) = 0;
};

// Forward declaration of States
class IdleState;
class HasMoneyState;
class DispensingState;

// Context VendingMachine
class VendingMachine {
private:
    std::shared_ptr<IVendingMachineState> currentState;
    std::unordered_map<std::string, std::pair<Item, int>> inventory; // code -> {item, qty}
    double currentBalance{0.0};
    std::string selectedCode;

public:
    VendingMachine();

    void setState(std::shared_ptr<IVendingMachineState> state) {
        currentState = std::move(state);
    }

    void addInventory(const std::string& code, Item item, int count) {
        inventory[code] = {item, count};
    }

    [[nodiscard]] double getBalance() const noexcept { return currentBalance; }
    void addBalance(double amount) { currentBalance += amount; }
    void resetBalance() { currentBalance = 0.0; }

    [[nodiscard]] const std::string& getSelectedCode() const noexcept { return selectedCode; }
    void setSelectedCode(std::string code) { selectedCode = std::move(code); }

    bool hasItem(const std::string& code) const {
        auto it = inventory.find(code);
        return it != inventory.end() && it->second.second > 0;
    }

    Item getItem(const std::string& code) const {
        return inventory.at(code).first;
    }

    void decrementInventory(const std::string& code) {
        if (inventory.find(code) != inventory.end() && inventory[code].second > 0) {
            inventory[code].second--;
        }
    }

    // Public Facade API
    void insertMoney(double amount) { currentState->insertMoney(*this, amount); }
    void selectProduct(const std::string& code) { currentState->selectProduct(*this, code); }
    void cancel() { currentState->cancel(*this); }
    void dispense() { currentState->dispense(*this); }
};

// State Implementations
class IdleState : public IVendingMachineState {
public:
    void insertMoney(VendingMachine& vm, double amount) override;
    void selectProduct(VendingMachine&, const std::string&) override {
        std::cout << "[ERROR] Please insert money first!\\n";
    }
    void dispense(VendingMachine&) override {
        std::cout << "[ERROR] No product selected to dispense.\\n";
    }
    void cancel(VendingMachine&) override {
        std::cout << "[INFO] Machine is idle. Nothing to refund.\\n";
    }
};

class HasMoneyState : public IVendingMachineState {
public:
    void insertMoney(VendingMachine& vm, double amount) override {
        vm.addBalance(amount);
        std::cout << "[MONEY] Added $" << amount << ". Total balance: $" << vm.getBalance() << "\\n";
    }

    void selectProduct(VendingMachine& vm, const std::string& code) override;

    void dispense(VendingMachine&) override {
        std::cout << "[ERROR] Please select an item before dispensing.\\n";
    }

    void cancel(VendingMachine& vm) override;
};

class DispensingState : public IVendingMachineState {
public:
    void insertMoney(VendingMachine&, double) override {
        std::cout << "[ERROR] Dispensing in progress. Cannot accept cash.\\n";
    }
    void selectProduct(VendingMachine&, const std::string&) override {
        std::cout << "[ERROR] Already dispensing.\\n";
    }
    void dispense(VendingMachine& vm) override;
    void cancel(VendingMachine&) override {
        std::cout << "[ERROR] Cannot cancel during physical dispensing!\\n";
    }
};

// Linking Transitions
void IdleState::insertMoney(VendingMachine& vm, double amount) {
    vm.addBalance(amount);
    std::cout << "[MONEY] Accepted $" << amount << ". Balance: $" << vm.getBalance() << "\\n";
    vm.setState(std::make_shared<HasMoneyState>());
}

void HasMoneyState::selectProduct(VendingMachine& vm, const std::string& code) {
    if (!vm.hasItem(code)) {
        std::cout << "[ERROR] Item " << code << " is out of stock!\\n";
        return;
    }
    Item item = vm.getItem(code);
    if (vm.getBalance() < item.price) {
        std::cout << "[ERROR] Insufficient funds for " << item.name << " ($" << item.price << "). Current balance: $" << vm.getBalance() << "\\n";
        return;
    }
    vm.setSelectedCode(code);
    vm.setState(std::make_shared<DispensingState>());
    vm.dispense(); // Auto-trigger dispense
}

void HasMoneyState::cancel(VendingMachine& vm) {
    std::cout << "[REFUND] Transaction cancelled. Refunding $" << vm.getBalance() << "\\n";
    vm.resetBalance();
    vm.setState(std::make_shared<IdleState>());
}

void DispensingState::dispense(VendingMachine& vm) {
    std::string code = vm.getSelectedCode();
    Item item = vm.getItem(code);
    vm.decrementInventory(code);

    double change = vm.getBalance() - item.price;
    std::cout << "[DISPENSE] *** Successfully dispensed: " << item.name << " ***\\n";
    if (change > 0) {
        std::cout << "[CHANGE] Returning change: $" << change << "\\n";
    }
    vm.resetBalance();
    vm.setSelectedCode("");
    vm.setState(std::make_shared<IdleState>());
}

VendingMachine::VendingMachine() : currentState(std::make_shared<IdleState>()) {}

int main() {
    VendingMachine vm;
    vm.addInventory("A1", {"Sparkling Water", 1.50}, 2);
    vm.addInventory("B2", {"Protein Bar", 2.25}, 1);

    std::cout << "--- Scenario 1: Select without money ---\\n";
    vm.selectProduct("A1");

    std::cout << "\\n--- Scenario 2: Successful purchase with change ---\\n";
    vm.insertMoney(2.00);
    vm.selectProduct("A1");

    std::cout << "\\n--- Scenario 3: Insert and Cancel Refund ---\\n";
    vm.insertMoney(1.00);
    vm.cancel();

    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. State Pattern Decoupling:</strong> Each machine state (<code>Idle</code>, <code>HasMoney</code>, <code>Dispensing</code>) is an isolated object implementing <code>IVendingMachineState</code>.",
                "<strong>2. Eliminating Fragile Conditionals:</strong> Avoided hundreds of nested <code>if (state == 1) ... else if (state == 2)</code> branches.",
                "<strong>3. Transaction Safety:</strong> Refund logic in <code>HasMoneyState</code> cleanly returns money and resets balance without side effects.",
                "<strong>4. Physical Hardware Isolation:</strong> Dispensing state cannot be aborted midway, protecting mechanical motor state."
            ],
            "comparison_matrix": {
                "title": "State Pattern vs Enum Switch Design",
                "headers": ["Feature", "Enum + Huge Switch", "State Pattern (OOP)"],
                "rows": [
                    ["Open/Closed Principle", "Violated (must modify all switch cases)", "Fully Adhered (add new State class)"],
                    ["Code Locality", "Scattered across many switch statements", "All logic for a state resides in one file"],
                    ["State Invariant Guarantees", "Easy to forget break; or invalid transition", "Compiler enforced transition interfaces"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Allowing money insertion during dispensing", "correction": "DispensingState rejects `insertMoney` calls to prevent money swallowing."},
                {"mistake": "Deducting inventory before validating payment sufficiency", "correction": "Validate balance >= item.price before decrementing stock."}
            ],
            "interview_traps": [
                "<strong>Trap: 'What if the mechanical dispenser jams and the sensor reports no item dropped?'</strong><br><em>Answer:</em> Discuss the Compensation / Rollback transaction: the state machine catches HardwareJamException, does NOT decrement inventory, refunds the customer's balance, and transitions to OutOfOrderState."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor a vending machine implemented with an int state variable and 10 nested if-statements.",
                "bad_code": "if (state == 0) { ... } else if (state == 1) { ... }",
                "good_code": "Encapsulate each state in a class implementing IVendingMachineState."
            },
            "practice_problem": {
                "title": "Design Denomination-Limited Change Return",
                "description": "Implement a Greedy/DP Coin Dispenser that returns change using available $1, $0.25, $0.10, and $0.05 coins or warns the user if exact change is unavailable.",
                "hint": "Maintain an internal `unordered_map<CoinType, int>` cash inventory inside CashBox."
            }
        },
        {
            "id": "splitwise-expense-manager",
            "title": "Splitwise / Expense Sharing App (Intermediate)",
            "definition": "A collaborative expense-sharing and balance settlement engine supporting multiple split strategies (Equal, Exact, Percentage, Shares) and graph-based debt simplification.",
            "why_it_matters": "Tests your ability to design flexible Strategy Patterns for complex financial calculations and solve graph debt minimization (Min-Cash-Flow algorithm).",
            "real_world_analogy": "Group travel with friends where Alice pays for the $120 dinner, Bob pays $60 for gas, and Charlie pays $30 for snacks. The app calculates who owes whom and minimizes total bank transfers.",
            "conceptual_breakdown": [
                "<strong>User & Group Entities:</strong> <code>User</code> (id, name), <code>Group</code> (members, expenses).",
                "<strong>Expense & Split Strategy:</strong> <code>Expense</code> contains payer, amount, and a list of <code>Split</code> objects computed via <code>ISplitStrategy</code> (Equal, Exact, Percentage).",
                "<strong>Balance Sheet:</strong> Directed debt graph represented as <code>unordered_map<UserId, unordered_map<UserId, double>></code>.",
                "<strong>Debt Simplification Algorithm:</strong> Greedy balance matching to reduce $N$ pairwise debts down to at most $N-1$ settlement transactions."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Splitwise System Architecture",
                "classes": [
                    {
                        "name": "User",
                        "is_abstract": False,
                        "attributes": ["- id: string", "- name: string", "- email: string"],
                        "methods": ["+ getId(): string", "+ getName(): string"]
                    },
                    {
                        "name": "Split",
                        "is_abstract": False,
                        "attributes": ["- user: shared_ptr<User>", "- amount: double"],
                        "methods": ["+ getAmount(): double", "+ setAmount(amt: double): void"]
                    },
                    {
                        "name": "ISplitStrategy",
                        "is_abstract": True,
                        "attributes": [],
                        "methods": ["+ validateSplits(totalAmount: double, splits: vector<Split>): bool", "+ calculateAmounts(totalAmount: double, splits: vector<Split>): void"]
                    },
                    {
                        "name": "ExpenseManager",
                        "is_abstract": False,
                        "attributes": ["- users: unordered_map<string, shared_ptr<User>>", "- balanceSheet: unordered_map<string, unordered_map<string, double>>"],
                        "methods": ["+ addExpense(paidBy: string, amount: double, splits: vector<Split>, strategy: unique_ptr<ISplitStrategy>): void", "+ showBalances(): void", "+ simplifyDebts(): void"]
                    }
                ],
                "relationships": [
                    {"from": "ExpenseManager", "to": "ISplitStrategy", "type": "composition", "label": "uses strategy"},
                    {"from": "ExpenseManager", "to": "User", "type": "aggregation", "label": "tracks users"}
                ]
            },
            "interactive_animation": {
                "title": "Debt Simplification Graph Reduction",
                "steps": [
                    {"step": 1, "description": "Initial Debts: Alice owes Bob $40. Bob owes Charlie $40.", "active_nodes": ["Alice", "Bob", "Charlie"]},
                    {"step": 2, "description": "Calculate Net Balances: Alice: -$40, Bob: $0, Charlie: +$40.", "active_nodes": ["ExpenseManager"]},
                    {"step": 3, "description": "Simplify graph: Eliminate intermediary Bob. Alice pays Charlie $40 directly (1 transaction instead of 2).", "active_nodes": ["Alice", "Charlie"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <unordered_map>
#include <cmath>
#include <iomanip>
#include <algorithm>

struct User {
    std::string id;
    std::string name;
};

struct Split {
    std::shared_ptr<User> user;
    double amount{0.0};
    double percentage{0.0};
};

enum class ExpenseType { EQUAL, EXACT, PERCENT };

class ISplitStrategy {
public:
    virtual ~ISplitStrategy() = default;
    virtual bool validate(double totalAmount, const std::vector<Split>& splits) = 0;
    virtual void compute(double totalAmount, std::vector<Split>& splits) = 0;
};

class EqualSplitStrategy : public ISplitStrategy {
public:
    bool validate(double, const std::vector<Split>& splits) override {
        return !splits.empty();
    }
    void compute(double totalAmount, std::vector<Split>& splits) override {
        double splitAmount = totalAmount / static_cast<double>(splits.size());
        for (auto& s : splits) {
            s.amount = splitAmount;
        }
    }
};

class PercentSplitStrategy : public ISplitStrategy {
public:
    bool validate(double, const std::vector<Split>& splits) override {
        double totalPct = 0.0;
        for (const auto& s : splits) totalPct += s.percentage;
        return std::abs(totalPct - 100.0) < 0.01;
    }
    void compute(double totalAmount, std::vector<Split>& splits) override {
        for (auto& s : splits) {
            s.amount = (s.percentage * totalAmount) / 100.0;
        }
    }
};

class ExpenseManager {
private:
    std::unordered_map<std::string, std::shared_ptr<User>> users;
    // balanceSheet[userA][userB] = amount userA owes userB (positive means userA owes userB)
    std::unordered_map<std::string, std::unordered_map<std::string, double>> balanceSheet;

public:
    void addUser(std::shared_ptr<User> user) {
        users[user->id] = std::move(user);
    }

    void addExpense(const std::string& paidBy, double totalAmount,
                    std::vector<Split> splits, std::unique_ptr<ISplitStrategy> strategy) {
        if (!strategy->validate(totalAmount, splits)) {
            std::cout << "[ERROR] Invalid split parameters!\\n";
            return;
        }

        strategy->compute(totalAmount, splits);

        for (const auto& split : splits) {
            std::string paidTo = split.user->id;
            if (paidBy == paidTo) continue;

            // paidTo owes paidBy split.amount
            balanceSheet[paidTo][paidBy] += split.amount;
            balanceSheet[paidBy][paidTo] -= split.amount;
        }

        std::cout << "[EXPENSE ADDED] " << users[paidBy]->name << " paid $" << totalAmount << "\\n";
    }

    void showBalances() {
        std::cout << "\\n--- Current Balances ---\\n";
        bool isEmpty = true;
        for (const auto& [userA, balances] : balanceSheet) {
            for (const auto& [userB, amount] : balances) {
                if (amount > 0.01) {
                    std::cout << users[userA]->name << " owes " << users[userB]->name << ": $" 
                              << std::fixed << std::setprecision(2) << amount << "\\n";
                    isEmpty = false;
                }
            }
        }
        if (isEmpty) {
            std::cout << "All balances are completely settled!\\n";
        }
    }

    void simplifyDebts() {
        std::cout << "\\n--- Simplified Debt Settlement Plan ---\\n";
        // 1. Compute net balance for each user
        std::unordered_map<std::string, double> netBalance;
        for (const auto& [uId, _] : users) netBalance[uId] = 0.0;

        for (const auto& [userA, balances] : balanceSheet) {
            for (const auto& [userB, amount] : balances) {
                if (amount > 0.001) {
                    netBalance[userA] -= amount;
                    netBalance[userB] += amount;
                }
            }
        }

        // 2. Separate into debtors and creditors
        std::vector<std::pair<std::string, double>> debtors;
        std::vector<std::pair<std::string, double>> creditors;

        for (const auto& [uId, net] : netBalance) {
            if (net < -0.01) debtors.emplace_back(uId, -net); // owe money
            else if (net > 0.01) creditors.emplace_back(uId, net); // receive money
        }

        // 3. Greedy Min-Cash-Flow matching
        size_t d = 0, c = 0;
        while (d < debtors.size() && c < creditors.size()) {
            double settleAmount = std::min(debtors[d].second, creditors[c].second);
            std::cout << users[debtors[d].first]->name << " pays " 
                      << users[creditors[c].first]->name << " -> $" 
                      << std::fixed << std::setprecision(2) << settleAmount << "\\n";

            debtors[d].second -= settleAmount;
            creditors[c].second -= settleAmount;

            if (debtors[d].second < 0.01) d++;
            if (creditors[c].second < 0.01) c++;
        }
    }
};

int main() {
    ExpenseManager manager;
    auto u1 = std::make_shared<User>("U1", "Alice");
    auto u2 = std::make_shared<User>("U2", "Bob");
    auto u3 = std::make_shared<User>("U3", "Charlie");

    manager.addUser(u1);
    manager.addUser(u2);
    manager.addUser(u3);

    // Alice pays $300 split equally among Alice, Bob, Charlie ($100 each)
    manager.addExpense("U1", 300.0, { {u1, 0, 0}, {u2, 0, 0}, {u3, 0, 0} }, std::make_unique<EqualSplitStrategy>());

    // Bob pays $100 split 70% Bob, 30% Charlie
    manager.addExpense("U2", 100.0, { {u2, 0, 70.0}, {u3, 0, 30.0} }, std::make_unique<PercentSplitStrategy>());

    manager.showBalances();
    manager.simplifyDebts();

    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Strategy Pattern for Splits:</strong> <code>ISplitStrategy</code> isolates validation and percentage/exact calculation math from balance recording.",
                "<strong>2. Directed Debt Graph:</strong> <code>balanceSheet[A][B]</code> cleanly models pairwise debts where opposite entries cancel out ($A \\to B = - B \\to A$).",
                "<strong>3. Min-Cash-Flow Debt Simplification:</strong> Reduces $O(N^2)$ transaction volume down to $O(N)$ transfers by computing net balances and greedily pairing largest debtors with largest creditors.",
                "<strong>4. High Numeric Precision:</strong> Uses threshold-based floating point comparisons ($< 0.01$) to prevent floating point residual display bugs."
            ],
            "comparison_matrix": {
                "title": "Splitwise Settlement Modes",
                "headers": ["Algorithm", "Number of Transactions", "Preserves Exact Direct History", "Computational Cost"],
                "rows": [
                    ["Pairwise Direct Settlement", "Up to N*(N-1)/2", "Yes (Alice pays only Bob)", "O(1) lookup"],
                    ["Greedy Min-Cash-Flow", "At most N-1", "No (Debts pooled globally)", "O(N log N)"],
                    ["Exact Optimal Subset Sum (NP-Hard)", "Optimal minimum", "No", "O(2^N)"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Float rounding issues causing 3-way split of $100 to sum to $99.99", "correction": "Assign fractional remainder cents to the first participant or store values in integer cents (e.g. 10000 cents)."}
            ],
            "interview_traps": [
                "<strong>Trap: 'How do you prevent money creation/loss due to floating point precision errors?'</strong><br><em>Answer:</em> Use 64-bit integer values representing smallest currency units (cents, paise, satoshis) rather than double."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor an expense calculation where percentage and exact split math are combined in a giant 200-line switch case.",
                "bad_code": "if (type == 'EQUAL') { ... } else if (type == 'PERCENT') { ... }",
                "good_code": "Use Strategy Pattern with ISplitStrategy and clean unit tests for each strategy."
            },
            "practice_problem": {
                "title": "Design Group Expense Settlement",
                "description": "Add a `Group` entity that isolates balance sheets strictly within a vacation trip or shared apartment.",
                "hint": "Create `Group` class holding its own `balanceSheet` and `ExpenseHistory` list."
            }
        },
        {
            "id": "movie-ticket-booking-bookmyshow",
            "title": "Movie Ticket Booking System (Intermediate)",
            "definition": "A high-concurrency seat reservation and movie ticketing platform managing multiplex cinema halls, show timings, transient seat locking (10-minute hold), and payment confirmations.",
            "why_it_matters": "The standard problem for testing **Distributed/In-Memory Locking**, **State Transitions**, and **Time-to-Live (TTL) seat release** under massive burst traffic.",
            "real_world_analogy": "Booking opening-night IMAX tickets for Avengers on BookMyShow: 50,000 users click the same 5 best seats at 12:00:00. Exactly 1 user gets a 10-minute lock; if payment fails, the seat unlocks automatically.",
            "conceptual_breakdown": [
                "<strong>Core Hierarchy:</strong> <code>City</code> $\\to$ <code>CinemaHall</code> $\\to$ <code>Auditorium / Screen</code> $\\to$ <code>Show</code> $\\to$ <code>Seat</code>.",
                "<strong>Seat Locking State Machine:</strong> Available $\\to$ Locked (10 min TTL) $\\to$ Booked / Released.",
                "<strong>Optimistic vs Pessimistic Locking:</strong> Guarding concurrent seat reservations across multiple cluster workers.",
                "<strong>Payment Confirmation Webhook:</strong> Converts temporary lock into permanent <code>Booking</code> record."
            ],
            "visual_diagram": {
                "type": "sequence_diagram",
                "title": "Seat Locking and Booking Sequence",
                "classes": [
                    {"name": "User", "is_abstract": False, "attributes": [], "methods": []},
                    {"name": "BookingService", "is_abstract": False, "attributes": [], "methods": []},
                    {"name": "SeatLockManager", "is_abstract": False, "attributes": [], "methods": []},
                    {"name": "PaymentGateway", "is_abstract": False, "attributes": [], "methods": []}
                ],
                "relationships": [
                    {"from": "User", "to": "BookingService", "type": "association", "label": "1. selectSeats(showId, [A1, A2])"},
                    {"from": "BookingService", "to": "SeatLockManager", "type": "association", "label": "2. lockSeats([A1, A2], TTL=10m)"},
                    {"from": "BookingService", "to": "PaymentGateway", "type": "association", "label": "3. processPayment(amount)"},
                    {"from": "BookingService", "to": "SeatLockManager", "type": "association", "label": "4. confirmBooking() / unlock()"}
                ]
            },
            "interactive_animation": {
                "title": "Concurrent Seat Locking & Auto-Expiry",
                "steps": [
                    {"step": 1, "description": "User 1 selects Seat B5. SeatLockManager acquires mutex, marks B5 LOCKED with 10-minute expiry.", "active_nodes": ["User 1", "SeatLockManager"]},
                    {"step": 2, "description": "User 2 tries to reserve Seat B5. Request rejected: Seat is currently locked by another user.", "active_nodes": ["User 2", "SeatLockManager"]},
                    {"step": 3, "description": "User 1 payment fails or times out. SeatLockManager automatically releases B5 back to AVAILABLE.", "active_nodes": ["SeatLockManager"]},
                    {"step": 4, "description": "User 2 retries and successfully locks Seat B5.", "active_nodes": ["User 2", "SeatLockManager"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <chrono>
#include <mutex>
#include <memory>
#include <optional>

enum class SeatStatus { AVAILABLE, LOCKED, BOOKED };

struct Seat {
    std::string seatId;
    int row;
    int col;
    double price;
    SeatStatus status{SeatStatus::AVAILABLE};
    std::string lockedByUserId;
    std::chrono::system_clock::time_point lockExpiration;
};

class Show {
private:
    std::string showId;
    std::string movieName;
    std::unordered_map<std::string, Seat> seats;
    std::mutex showMtx;

public:
    Show(std::string id, std::string movie) : showId(std::move(id)), movieName(std::move(movie)) {}

    void addSeat(const std::string& seatId, int row, int col, double price) {
        seats[seatId] = Seat{seatId, row, col, price, SeatStatus::AVAILABLE, "", {}};
    }

    bool lockSeats(const std::vector<std::string>& seatIds, const std::string& userId, int ttlSeconds) {
        std::lock_guard<std::mutex> lock(showMtx);
        auto now = std::chrono::system_clock::now();

        // 1. Verify all requested seats are available (or have expired locks)
        for (const auto& sId : seatIds) {
            auto it = seats.find(sId);
            if (it == seats.end()) return false;
            
            auto& seat = it->second;
            if (seat.status == SeatStatus::BOOKED) return false;
            if (seat.status == SeatStatus::LOCKED && seat.lockExpiration > now) return false;
        }

        // 2. Lock all seats atomically
        auto expiry = now + std::chrono::seconds(ttlSeconds);
        for (const auto& sId : seatIds) {
            auto& seat = seats[sId];
            seat.status = SeatStatus::LOCKED;
            seat.lockedByUserId = userId;
            seat.lockExpiration = expiry;
        }

        std::cout << "[LOCK ACQUIRED] User " << userId << " locked " << seatIds.size() << " seats for " << ttlSeconds << "s\\n";
        return true;
    }

    bool confirmBooking(const std::vector<std::string>& seatIds, const std::string& userId) {
        std::lock_guard<std::mutex> lock(showMtx);
        auto now = std::chrono::system_clock::now();

        // Verify user still owns active locks
        for (const auto& sId : seatIds) {
            auto it = seats.find(sId);
            if (it == seats.end()) return false;
            if (it->second.status != SeatStatus::LOCKED || 
                it->second.lockedByUserId != userId || 
                it->second.lockExpiration <= now) {
                std::cout << "[ERROR] Lock expired or invalid for seat: " << sId << "\\n";
                return false;
            }
        }

        // Mark permanently booked
        for (const auto& sId : seatIds) {
            seats[sId].status = SeatStatus::BOOKED;
            seats[sId].lockedByUserId = "";
        }

        std::cout << "[BOOKING CONFIRMED] User " << userId << " successfully booked tickets!\\n";
        return true;
    }
};

int main() {
    Show show1("SHOW-101", "Interstellar IMAX 70mm");
    show1.addSeat("A1", 1, 1, 20.0);
    show1.addSeat("A2", 1, 2, 20.0);
    show1.addSeat("A3", 1, 3, 20.0);

    // User 1 locks A1 and A2 for 2 seconds
    bool u1Lock = show1.lockSeats({"A1", "A2"}, "User_Alice", 2);

    // User 2 attempts to lock A2 (Should fail)
    bool u2Lock = show1.lockSeats({"A2", "A3"}, "User_Bob", 2);
    std::cout << "User Bob Lock Result: " << (u2Lock ? "SUCCESS" : "FAILED (Seat Already Locked)") << "\\n";

    // Alice completes payment before expiry
    show1.confirmBooking({"A1", "A2"}, "User_Alice");

    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Atomic Multi-Seat Locking:</strong> All requested seats are verified and locked under a single critical section, preventing partial reservation deadlocks.",
                "<strong>2. Time-To-Live (TTL) Lock Expiry:</strong> Lock includes a timestamp expiration; expired locks are automatically treated as available without requiring an active background sweeper thread.",
                "<strong>3. Ownership Validation on Payment:</strong> Booking confirmation guarantees that only the user holding the active lock can finalize the purchase."
            ],
            "comparison_matrix": {
                "title": "Concurrency Locking Strategies for Ticketing",
                "headers": ["Strategy", "Throughput", "Deadlock Risk", "Implementation Overhead"],
                "rows": [
                    ["Pessimistic In-Memory Lock", "Moderate", "None if sorted key order", "Low"],
                    ["Distributed Redis Redlock", "High (horizontal scale)", "Low", "Moderate (TTL drift)"],
                    ["Database Row Versioning (Optimistic)", "High for non-conflicting", "High abort rate on hot seats", "Low"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Locking seats one-by-one without sorted ordering leading to deadlocks", "correction": "Sort seat IDs before acquiring locks to guarantee global hierarchy acquisition."},
                {"mistake": "Permanently locking seats if payment webhook crashes", "correction": "Always attach a TTL (Time-To-Live) to every provisional reservation."}
            ],
            "interview_traps": [
                "<strong>Trap: 'How do you prevent two users simultaneously booking adjacent seats when social distancing rules require 1 empty seat between parties?'</strong><br><em>Answer:</em> Encapsulate validation inside a ReservationValidator pipeline that checks adjacent row/col status during the atomic lock step."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor a seat booking service where database queries and payment processing occur while holding the global mutex.",
                "bad_code": "lock(); callPaymentGateway(); updateDB(); unlock();",
                "good_code": "Acquire temporary lock with TTL -> release lock -> process payment asynchronously -> acquire lock briefly to finalize."
            },
            "practice_problem": {
                "title": "Design VIP Dynamic Tier Pricing",
                "description": "Implement surge pricing that automatically increases remaining seat prices by 20% once occupancy reaches 80%.",
                "hint": "Use Strategy pattern for dynamic pricing calculations based on occupancy percentage."
            }
        },
        {
            "id": "ride-sharing-uber-ola",
            "title": "Ride Sharing System (Intermediate)",
            "definition": "A location-based dynamic dispatch and ride-hailing service managing geospatial driver location updates, nearest-driver matching, surge pricing, and trip lifecycle state.",
            "why_it_matters": "Demonstrates geospatial indexing (QuadTree/Geohash), Strategy Pattern for driver matching, and State Pattern for trip lifecycle (Requested, Assigned, Arrived, InTrip, Completed).",
            "real_world_analogy": "Requesting an UberX: app converts your GPS coordinates to a Geohash, queries spatial index for idle drivers within 3 km, matches best driver, and begins live trip telemetry.",
            "conceptual_breakdown": [
                "<strong>Geospatial Driver Index:</strong> Grid/QuadTree or Geohash mapping lat/lon coordinates to active driver IDs.",
                "<strong>Trip Lifecycle State Machine:</strong> <code>REQUESTED</code> $\\to$ <code>DRIVER_MATCHED</code> $\\to$ <code>IN_PROGRESS</code> $\\to$ <code>COMPLETED</code>.",
                "<strong>Matching Strategy:</strong> <code>IMatchingStrategy</code> (Nearest Driver vs Highest Rated Driver vs Batch Dispatch).",
                "<strong>Fare Estimation Strategy:</strong> Base fare + time duration + distance + surge multiplier."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Ride Sharing System UML",
                "classes": [
                    {
                        "name": "Location",
                        "is_abstract": False,
                        "attributes": ["+ latitude: double", "+ longitude: double"],
                        "methods": ["+ distanceTo(other: Location): double"]
                    },
                    {
                        "name": "Driver",
                        "is_abstract": False,
                        "attributes": ["- id: string", "- name: string", "- isAvailable: bool", "- location: Location"],
                        "methods": ["+ updateLocation(loc: Location): void", "+ setAvailable(status: bool): void"]
                    },
                    {
                        "name": "Trip",
                        "is_abstract": False,
                        "attributes": ["- tripId: string", "- riderId: string", "- driverId: string", "- pickup: Location", "- drop: Location", "- status: TripStatus"],
                        "methods": ["+ startTrip(): void", "+ completeTrip(): void", "+ calculateFare(): double"]
                    }
                ],
                "relationships": [
                    {"from": "Trip", "to": "Location", "type": "composition", "label": "pickup & drop"},
                    {"from": "Driver", "to": "Location", "type": "composition", "label": "current loc"}
                ]
            },
            "interactive_animation": {
                "title": "Driver Matching & Trip Lifecycle",
                "steps": [
                    {"step": 1, "description": "Rider requests ride from Location A to Location B.", "active_nodes": ["Rider", "TripManager"]},
                    {"step": 2, "description": "TripManager queries SpatialIndex for nearby available drivers within 5km.", "active_nodes": ["SpatialIndex", "Driver"]},
                    {"step": 3, "description": "Nearest driver D1 receives match and accepts ride.", "active_nodes": ["Driver D1", "Trip"]},
                    {"step": 4, "description": "Trip status transitions to IN_PROGRESS as driver begins navigation.", "active_nodes": ["Trip"]},
                    {"step": 5, "description": "Trip completes at destination. Fare calculated and charged.", "active_nodes": ["FareCalculator", "Rider"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <cmath>
#include <unordered_map>
#include <limits>

struct Location {
    double lat;
    double lon;

    [[nodiscard]] double distanceTo(const Location& o) const noexcept {
        // Euclidean approximation for LLD simulation
        return std::sqrt((lat - o.lat) * (lat - o.lat) + (lon - o.lon) * (lon - o.lon));
    }
};

enum class TripStatus { REQUESTED, DRIVER_ASSIGNED, IN_PROGRESS, COMPLETED, CANCELLED };

class Driver {
public:
    std::string id;
    std::string name;
    Location location;
    bool isAvailable{true};

    Driver(std::string dId, std::string dName, Location loc)
        : id(std::move(dId)), name(std::move(dName)), location(loc) {}
};

class Trip {
public:
    std::string tripId;
    std::string riderId;
    std::shared_ptr<Driver> driver{nullptr};
    Location pickup;
    Location destination;
    TripStatus status{TripStatus::REQUESTED};
    double fare{0.0};

    Trip(std::string tId, std::string rId, Location start, Location end)
        : tripId(std::move(tId)), riderId(std::move(rId)), pickup(start), destination(end) {}
};

class IMatchingStrategy {
public:
    virtual ~IMatchingStrategy() = default;
    virtual std::shared_ptr<Driver> findDriver(const Location& pickup, const std::vector<std::shared_ptr<Driver>>& drivers) = 0;
};

class NearestDriverStrategy : public IMatchingStrategy {
public:
    std::shared_ptr<Driver> findDriver(const Location& pickup, const std::vector<std::shared_ptr<Driver>>& drivers) override {
        std::shared_ptr<Driver> bestDriver = nullptr;
        double minDistance = std::numeric_limits<double>::max();

        for (const auto& d : drivers) {
            if (d->isAvailable) {
                double dist = pickup.distanceTo(d->location);
                if (dist < minDistance) {
                    minDistance = dist;
                    bestDriver = d;
                }
            }
        }
        return bestDriver;
    }
};

class RideSharingService {
private:
    std::vector<std::shared_ptr<Driver>> drivers;
    std::unordered_map<std::string, std::shared_ptr<Trip>> activeTrips;
    std::unique_ptr<IMatchingStrategy> matchingStrategy;
    int nextTripId = 1;

public:
    explicit RideSharingService(std::unique_ptr<IMatchingStrategy> strategy)
        : matchingStrategy(std::move(strategy)) {}

    void registerDriver(std::shared_ptr<Driver> d) {
        drivers.push_back(std::move(d));
    }

    std::shared_ptr<Trip> requestRide(const std::string& riderId, Location start, Location end) {
        auto trip = std::make_shared<Trip>("TRIP-" + std::to_string(nextTripId++), riderId, start, end);
        auto matchedDriver = matchingStrategy->findDriver(start, drivers);

        if (!matchedDriver) {
            std::cout << "[REJECTED] No available drivers nearby for rider " << riderId << "\\n";
            return nullptr;
        }

        matchedDriver->isAvailable = false;
        trip->driver = matchedDriver;
        trip->status = TripStatus::DRIVER_ASSIGNED;
        trip->fare = 5.0 + (start.distanceTo(end) * 2.5); // Base + distance rate

        activeTrips[trip->tripId] = trip;
        std::cout << "[MATCHED] Trip " << trip->tripId << " assigned to Driver " << matchedDriver->name 
                  << " (Est Fare: $" << trip->fare << ")\\n";
        return trip;
    }

    void completeRide(const std::string& tripId) {
        auto it = activeTrips.find(tripId);
        if (it != activeTrips.end()) {
            auto& trip = it->second;
            trip->status = TripStatus::COMPLETED;
            trip->driver->isAvailable = true;
            trip->driver->location = trip->destination; // update driver pos
            std::cout << "[COMPLETED] Trip " << tripId << " finished. Fare of $" << trip->fare << " charged.\\n";
            activeTrips.erase(it);
        }
    }
};

int main() {
    RideSharingService service(std::make_unique<NearestDriverStrategy>());

    service.registerDriver(std::make_shared<Driver>("D1", "John", Location{37.7749, -122.4194}));
    service.registerDriver(std::make_shared<Driver>("D2", "Sara", Location{37.7833, -122.4167}));

    auto trip = service.requestRide("Rider_Dave", Location{37.7750, -122.4180}, Location{37.8000, -122.4000});

    if (trip) {
        service.completeRide(trip->tripId);
    }

    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Spatial Matching Strategy:</strong> <code>IMatchingStrategy</code> decouples proximity algorithms from ride management.",
                "<strong>2. Driver Availability Management:</strong> Driver state switches atomically between available and in-trip.",
                "<strong>3. End-to-End Trip Lifecycle:</strong> Clean transition from Requested to Completed with telemetry position updates."
            ],
            "comparison_matrix": {
                "title": "Geospatial Indexing Techniques",
                "headers": ["Indexing Method", "Update Frequency Latency", "Radius Query Efficiency", "Memory Footprint"],
                "rows": [
                    ["Flat List Search", "O(1) write", "O(N) (Slow for 100k drivers)", "Very Low"],
                    ["Geohash / S2 Geometry", "O(1) write (hash key)", "O(1) cell lookup + neighbor cells", "Low"],
                    ["R-Tree / QuadTree", "O(log N) tree rebalance", "O(log N + k)", "Moderate"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Locking the entire driver pool during matching", "correction": "Partition spatial index by city geohash cells to isolate locks."}
            ],
            "interview_traps": [
                "<strong>Trap: 'What happens if a driver rejects a dispatch offer?'</strong><br><em>Answer:</em> Introduce an OfferTimeout state machine: if rejected/timed out, mark driver temporarily skipped for this trip and query the strategy for next best driver."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor a hardcoded driver search loop inside Trip class into a standalone Matching Engine.",
                "bad_code": "for (auto d : allDrivers) { ... } inside Trip::create()",
                "good_code": "Isolate matching in IMatchingStrategy with dependency injection."
            },
            "practice_problem": {
                "title": "Design Shared / Carpool Rides (UberPool)",
                "description": "Extend the ride system to allow 2 riders with overlapping pickup and destination trajectories to share the same vehicle.",
                "hint": "Use Route waypoint optimization to calculate detour delta before accepting second passenger."
            }
        },
        {
            "id": "in-memory-lru-cache",
            "title": "Thread-safe LRU Cache (Advanced)",
            "definition": "A high-performance in-memory key-value cache combining $O(1)$ Hash Map lookups with a Doubly Linked List for Least-Recently-Used eviction, protected by fine-grained thread synchronization.",
            "why_it_matters": "One of the most frequently asked systems design questions at FAANG. Evaluates low-level data structure manipulation, pointer management, and reader-writer locking.",
            "real_world_analogy": "CPU L1/L2 hardware cache lines or in-memory Redis key eviction where oldest unused web pages are dropped when memory limit is reached.",
            "conceptual_breakdown": [
                "<strong>Doubly Linked List:</strong> Maintains access order from Head (Most Recently Used) to Tail (Least Recently Used). $O(1)$ node removal and prepend.",
                "<strong>Hash Map:</strong> <code>unordered_map<Key, ListNode*></code> provides $O(1)$ key lookup.",
                "<strong>Thread Safety:</strong> <code>std::shared_mutex</code> allows concurrent multi-threaded readers while exclusive write locks protect list restructuring.",
                "<strong>Eviction Flow:</strong> When size exceeds capacity, tail node is severed from list and erased from hash map."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "LRU Cache Architecture",
                "classes": [
                    {
                        "name": "Node<K, V>",
                        "is_abstract": False,
                        "attributes": ["+ key: K", "+ value: V", "+ prev: Node*", "+ next: Node*"],
                        "methods": ["+ Node(k: K, v: V)"]
                    },
                    {
                        "name": "LRUCache<K, V>",
                        "is_abstract": False,
                        "attributes": ["- capacity: size_t", "- map: unordered_map<K, Node*>", "- head: Node*", "- tail: Node*", "- rwMtx: shared_mutex"],
                        "methods": ["+ get(key: K): optional<V>", "+ put(key: K, value: V): void", "- moveToHead(node: Node*): void", "- removeTail(): void"]
                    }
                ],
                "relationships": [
                    {"from": "LRUCache", "to": "Node", "type": "composition", "label": "owns doubly linked nodes"}
                ]
            },
            "interactive_animation": {
                "title": "LRU Cache Eviction and Lookup Cycle",
                "steps": [
                    {"step": 1, "description": "Cache with capacity=2 has elements [A, B].", "active_nodes": ["Head: B", "Tail: A"]},
                    {"step": 2, "description": "get('A') is called. Node 'A' is detached and moved to Head.", "active_nodes": ["Head: A", "Tail: B"]},
                    {"step": 3, "description": "put('C', val) is called. Capacity full! Tail node 'B' is evicted and erased from Hash Map.", "active_nodes": ["Tail: B (Evicted)"]},
                    {"step": 4, "description": "New node 'C' is inserted at Head.", "active_nodes": ["Head: C", "Tail: A"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <unordered_map>
#include <memory>
#include <mutex>
#include <shared_mutex>
#include <optional>

template <typename K, typename V>
class ThreadSafeLRUCache {
private:
    struct Node {
        K key;
        V value;
        Node* prev{nullptr};
        Node* next{nullptr};
        Node(K k, V v) : key(std::move(k)), value(std::move(v)) {}
    };

    size_t capacity;
    std::unordered_map<K, Node*> map;
    Node* head{nullptr}; // Most Recently Used
    Node* tail{nullptr}; // Least Recently Used
    mutable std::shared_mutex mtx;

    void detachNode(Node* node) {
        if (node->prev) node->prev->next = node->next;
        else head = node->next;

        if (node->next) node->next->prev = node->prev;
        else tail = node->prev;

        node->prev = nullptr;
        node->next = nullptr;
    }

    void insertAtHead(Node* node) {
        node->next = head;
        node->prev = nullptr;
        if (head) head->prev = node;
        head = node;
        if (!tail) tail = head;
    }

    void moveToHead(Node* node) {
        if (node == head) return;
        detachNode(node);
        insertAtHead(node);
    }

public:
    explicit ThreadSafeLRUCache(size_t cap) : capacity(cap) {}

    ~ThreadSafeLRUCache() {
        Node* curr = head;
        while (curr) {
            Node* nxt = curr->next;
            delete curr;
            curr = nxt;
        }
    }

    // Disallow copies
    ThreadSafeLRUCache(const ThreadSafeLRUCache&) = delete;
    ThreadSafeLRUCache& operator=(const ThreadSafeLRUCache&) = delete;

    std::optional<V> get(const K& key) {
        std::unique_lock<std::shared_mutex> lock(mtx); // Must be unique because LRU updates access order
        auto it = map.find(key);
        if (it == map.end()) return std::nullopt;

        moveToHead(it->second);
        return it->second->value;
    }

    void put(const K& key, V value) {
        std::unique_lock<std::shared_mutex> lock(mtx);
        auto it = map.find(key);

        if (it != map.end()) {
            // Update existing
            it->second->value = std::move(value);
            moveToHead(it->second);
            return;
        }

        if (map.size() >= capacity) {
            // Evict Least Recently Used (tail)
            if (tail) {
                Node* victim = tail;
                map.erase(victim->key);
                detachNode(victim);
                delete victim;
            }
        }

        Node* newNode = new Node(key, std::move(value));
        insertAtHead(newNode);
        map[key] = newNode;
    }
};

int main() {
    ThreadSafeLRUCache<int, std::string> cache(2);

    cache.put(1, "Alpha");
    cache.put(2, "Beta");

    auto val1 = cache.get(1); // 1 becomes MRU, 2 is LRU
    std::cout << "Key 1 Value: " << (val1 ? *val1 : "Not Found") << "\\n";

    cache.put(3, "Gamma"); // Evicts Key 2

    auto val2 = cache.get(2);
    std::cout << "Key 2 Value: " << (val2 ? *val2 : "Not Found (Successfully Evicted)") << "\\n";

    auto val3 = cache.get(3);
    std::cout << "Key 3 Value: " << (val3 ? *val3 : "Not Found") << "\\n";

    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. O(1) Access and Reordering:</strong> Hash map provides pointer to Doubly Linked List node in $O(1)$. Pointer manipulation re-links head/tail in $O(1)$.",
                "<strong>2. Sentinel-less Node Detachment:</strong> Explicit head/tail updates cleanly handle single-element and empty-list edge cases.",
                "<strong>3. Mutex Locking Discipline:</strong> Because <code>get()</code> modifies node position in the list (making it MRU), a write lock is required even during read operations."
            ],
            "comparison_matrix": {
                "title": "Eviction Cache Algorithms",
                "headers": ["Algorithm", "Time Complexity", "Frequency Resilience", "Memory Overhead per Item"],
                "rows": [
                    ["LRU (Least Recently Used)", "O(1)", "Weak against loop scans", "2 Pointers (prev/next)"],
                    ["LFU (Least Frequently Used)", "O(1) with 2 maps", "Excellent frequency retention", "Pointers + Freq Counter"],
                    ["FIFO Cache", "O(1)", "Poor", "1 Pointer / Queue index"],
                    ["2Q / LRU-K", "O(1)", "High immunity to single-pass scans", "Two queue structures"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Using `std::shared_lock` for `get()`", "correction": "`get()` modifies linked list pointers to make the accessed item MRU, causing data races if multiple threads run read locks. Use `std::unique_lock` or a striped lock LRU."},
                {"mistake": "Memory leaks on node eviction", "correction": "Always delete the severed tail node when erasing from hash map."}
            ],
            "interview_traps": [
                "<strong>Trap: 'Why can't you use std::list and std::unordered_map<K, std::list::iterator>?'</strong><br><em>Answer:</em> While `std::list::splice` is $O(1)$, standard library list nodes have additional heap overhead and cannot be embedded directly into custom memory arenas for ultra-low latency."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor an LRU cache that uses a single vector and linear element shifting on every lookup.",
                "bad_code": "vector search -> erase element -> push_front (O(N) operations)",
                "good_code": "Use Doubly Linked List + Hash Map for true O(1) amortized performance."
            },
            "practice_problem": {
                "title": "Design Sharded / Striped Thread-Safe LRU",
                "description": "Build a 16-stripe LRU cache where keys are hashed to independent LRU shards to eliminate thread contention across 64 cores.",
                "hint": "Create array of `ThreadSafeLRUCache` shards; pick shard via `std::hash<K>{}(key) % NumShards`."
            }
        },
        {
            "id": "rate-limiter-system",
            "title": "Rate Limiter System (Advanced)",
            "definition": "A high-throughput API throttling and traffic-shaping component implementing Token Bucket, Leaky Bucket, and Sliding Window Log algorithms to prevent DDoS and API abuse.",
            "why_it_matters": "A critical system component asked in almost every senior backend LLD interview. Evaluates algorithm selection, thread-safety, and time-drift handling.",
            "real_world_analogy": "A highway toll booth gate that releases 1 vehicle every 2 seconds regardless of whether 50 cars arrive simultaneously in a burst.",
            "conceptual_breakdown": [
                "<strong>Token Bucket Algorithm:</strong> Tokens added at constant rate up to capacity; requests consume tokens; supports bursts.",
                "<strong>Leaky Bucket Algorithm:</strong> Requests enter a FIFO queue; drained at constant leak rate; smooths bursts into steady stream.",
                "<strong>Sliding Window Counter:</strong> Blends previous window count with current window elapsed fraction for accurate burst protection without full log memory overhead.",
                "<strong>Client Identification:</strong> Throttles per IP, API Key, or User ID."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Rate Limiter Architecture",
                "classes": [
                    {
                        "name": "IRateLimiter",
                        "is_abstract": True,
                        "attributes": [],
                        "methods": ["+ allowRequest(clientId: string): bool"]
                    },
                    {
                        "name": "TokenBucketRateLimiter",
                        "is_abstract": False,
                        "attributes": ["- capacity: double", "- refillRate: double", "- clients: unordered_map<string, Bucket>", "- mtx: mutex"],
                        "methods": ["+ allowRequest(clientId: string): bool", "- refill(b: Bucket&): void"]
                    }
                ],
                "relationships": [
                    {"from": "TokenBucketRateLimiter", "to": "IRateLimiter", "type": "inheritance", "label": "implements"}
                ]
            },
            "interactive_animation": {
                "title": "Token Bucket Refill & Consumption",
                "steps": [
                    {"step": 1, "description": "Bucket starts at max capacity = 5 tokens. Refill rate = 1 token/sec.", "active_nodes": ["Bucket [5/5]"]},
                    {"step": 2, "description": "Burst of 3 requests arrives. 3 tokens consumed. 2 tokens remaining. Requests ALLOWED.", "active_nodes": ["Bucket [2/5]"]},
                    {"step": 3, "description": "Burst of 3 requests arrives immediately. 2 tokens consumed, 1 request REJECTED (429 Too Many Requests).", "active_nodes": ["Bucket [0/5]", "429 Rejection"]},
                    {"step": 4, "description": "2 seconds pass. 2 new tokens refilled. New request arrives and is ALLOWED.", "active_nodes": ["Bucket [2/5]"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <string>
#include <unordered_map>
#include <chrono>
#include <mutex>
#include <algorithm>

class TokenBucketRateLimiter {
private:
    struct Bucket {
        double tokens;
        std::chrono::steady_clock::time_point lastRefillTime;
    };

    double maxCapacity;
    double refillRatePerSecond;
    std::unordered_map<std::string, Bucket> clients;
    std::mutex mtx;

    void refillBucket(Bucket& bucket, std::chrono::steady_clock::time_point now) {
        auto duration = std::chrono::duration_cast<std::chrono::duration<double>>(now - bucket.lastRefillTime).count();
        bucket.tokens = std::min(maxCapacity, bucket.tokens + (duration * refillRatePerSecond));
        bucket.lastRefillTime = now;
    }

public:
    TokenBucketRateLimiter(double capacity, double ratePerSec)
        : maxCapacity(capacity), refillRatePerSecond(ratePerSec) {}

    bool allowRequest(const std::string& clientId, double tokensRequested = 1.0) {
        std::lock_guard<std::mutex> lock(mtx);
        auto now = std::chrono::steady_clock::now();

        auto it = clients.find(clientId);
        if (it == clients.end()) {
            // First time seeing client: initialize with full bucket minus requested
            if (tokensRequested > maxCapacity) return false;
            clients[clientId] = Bucket{maxCapacity - tokensRequested, now};
            return true;
        }

        Bucket& bucket = it->second;
        refillBucket(bucket, now);

        if (bucket.tokens >= tokensRequested) {
            bucket.tokens -= tokensRequested;
            return true;
        }

        return false; // Throttled
    }
};

int main() {
    // Capacity 3 tokens, refills 1 token per second
    TokenBucketRateLimiter limiter(3.0, 1.0);

    std::string user = "Client_API_Key_ABC";

    std::cout << "Req 1: " << (limiter.allowRequest(user) ? "ALLOW" : "THROTTLE") << "\\n";
    std::cout << "Req 2: " << (limiter.allowRequest(user) ? "ALLOW" : "THROTTLE") << "\\n";
    std::cout << "Req 3: " << (limiter.allowRequest(user) ? "ALLOW" : "THROTTLE") << "\\n";
    std::cout << "Req 4 (Burst Exceeded): " << (limiter.allowRequest(user) ? "ALLOW" : "THROTTLE") << "\\n";

    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Lazy Token Refill:</strong> Rather than running background timer threads for every client, tokens are lazily refilled on-demand during the request.",
                "<strong>2. Monotonic Clock Usage:</strong> Uses <code>std::chrono::steady_clock</code> to prevent system clock adjustments (NTP sync) from corrupting token math.",
                "<strong>3. Burst Friendly:</strong> Allows short burst up to <code>maxCapacity</code> while enforcing steady-state average rate."
            ],
            "comparison_matrix": {
                "title": "Rate Limiting Algorithm Comparison",
                "headers": ["Algorithm", "Supports Bursts", "Memory per Client", "Smoothed Output"],
                "rows": [
                    ["Token Bucket", "Yes (up to capacity)", "O(1) (2 numbers)", "Moderate"],
                    ["Leaky Bucket", "No (strictly constant output)", "O(Queue Size)", "Highest"],
                    ["Fixed Window Counter", "Yes (2x boundary burst)", "O(1) (count + timestamp)", "Poor"],
                    ["Sliding Window Log", "Yes", "O(Req count in window)", "High"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Using `std::chrono::system_clock` which can drift or jump backwards on NTP sync", "correction": "Always use `std::chrono::steady_clock` for rate limiters."},
                {"mistake": "Spawning a background thread per client to tick tokens", "correction": "Use lazy mathematical evaluation based on elapsed delta-time."}
            ],
            "interview_traps": [
                "<strong>Trap: 'How do you handle rate limiting across 100 distributed load balancer nodes?'</strong><br><em>Answer:</em> Use Redis Lua scripts implementing token bucket or Sliding Window Counter to make atomicity global across all API gateways."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor a fixed window rate limiter that suffers from the 2x burst traffic spike at the minute boundary.",
                "bad_code": "if (currentMinute == lastMinute) { count++; if (count > limit) drop(); }",
                "good_code": "Implement Token Bucket or Sliding Window Log."
            },
            "practice_problem": {
                "title": "Design Sliding Window Counter Limiter",
                "description": "Implement the Cloudflare sliding window counter algorithm that weights current window vs previous window counts.",
                "hint": "Formula: `count = prev_count * ((1 - elapsed_fraction)) + current_count`."
            }
        },
        {
            "id": "pub-sub-message-queue",
            "title": "Pub/Sub In-Memory Message Queue (Advanced)",
            "definition": "A thread-safe in-memory publish-subscribe broker supporting multiple topics, concurrent consumer groups, message offset tracking, and asynchronous dispatch.",
            "why_it_matters": "Core architecture behind Apache Kafka and RabbitMQ. Tests concurrency, Producer-Consumer synchronization with condition variables, and Observer pattern at scale.",
            "real_world_analogy": "A radio broadcasting network: radio stations (Publishers) broadcast music to named frequencies (Topics), and individual cars (Subscribers) tune into frequencies and play music independently.",
            "conceptual_breakdown": [
                "<strong>Topic & Partition:</strong> An ordered, append-only log of <code>Message</code> items.",
                "<strong>Producer:</strong> Publishes messages to designated topics.",
                "<strong>Consumer Group & Offsets:</strong> Each consumer maintains its own integer offset index into the topic message log.",
                "<strong>Broker Engine:</strong> Manages topic creation, thread-safe message appending, and condition variable wakeups."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Pub/Sub Message Queue UML",
                "classes": [
                    {
                        "name": "Message",
                        "is_abstract": False,
                        "attributes": ["+ id: string", "+ payload: string", "+ timestamp: time_point"],
                        "methods": []
                    },
                    {
                        "name": "Topic",
                        "is_abstract": False,
                        "attributes": ["- name: string", "- messages: vector<Message>", "- cv: condition_variable", "- mtx: mutex"],
                        "methods": ["+ publish(msg: Message): void", "+ getMessageAt(offset: size_t): optional<Message>"]
                    },
                    {
                        "name": "Consumer",
                        "is_abstract": False,
                        "attributes": ["- id: string", "- offset: size_t", "- topic: shared_ptr<Topic>"],
                        "methods": ["+ poll(): optional<Message>", "+ acknowledge(): void"]
                    }
                ],
                "relationships": [
                    {"from": "Topic", "to": "Message", "type": "composition", "label": "contains log"},
                    {"from": "Consumer", "to": "Topic", "type": "aggregation", "label": "reads from"}
                ]
            },
            "interactive_animation": {
                "title": "Kafka-style Pub/Sub Message Fanout",
                "steps": [
                    {"step": 1, "description": "Producer publishes Message M1 to Topic 'orders'. Message appended at Offset 0.", "active_nodes": ["Producer", "Topic 'orders'"]},
                    {"step": 2, "description": "Consumer Group A (Analytics) reads Offset 0 and processes M1.", "active_nodes": ["Consumer A", "Topic 'orders'"]},
                    {"step": 3, "description": "Consumer Group B (Billing) reads Offset 0 independently at its own pace.", "active_nodes": ["Consumer B", "Topic 'orders'"]},
                    {"step": 4, "description": "Producer appends M2 at Offset 1. Consumers notified via condition variable.", "active_nodes": ["Producer", "Topic 'orders'"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <memory>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <atomic>

struct Message {
    size_t offset;
    std::string payload;
};

class Topic {
private:
    std::string name;
    std::vector<Message> log;
    std::mutex topicMtx;
    std::condition_variable cv;

public:
    explicit Topic(std::string tName) : name(std::move(tName)) {}

    [[nodiscard]] const std::string& getName() const noexcept { return name; }

    void publish(const std::string& payload) {
        std::lock_guard<std::mutex> lock(topicMtx);
        size_t newOffset = log.size();
        log.push_back(Message{newOffset, payload});
        std::cout << "[TOPIC " << name << "] Published Offset " << newOffset << ": '" << payload << "'\\n";
        cv.notify_all();
    }

    // Blocking read until offset is available or stopped
    bool readMessage(size_t offset, Message& outMsg, const std::atomic<bool>& isRunning) {
        std::unique_lock<std::mutex> lock(topicMtx);
        cv.wait(lock, [&]() {
            return offset < log.size() || !isRunning;
        });

        if (!isRunning && offset >= log.size()) return false;

        outMsg = log[offset];
        return true;
    }
};

class Consumer {
private:
    std::string consumerId;
    std::shared_ptr<Topic> topic;
    size_t currentOffset{0};

public:
    Consumer(std::string id, std::shared_ptr<Topic> t)
        : consumerId(std::move(id)), topic(std::move(t)) {}

    void consumeNext(const std::atomic<bool>& isRunning) {
        Message msg;
        if (topic->readMessage(currentOffset, msg, isRunning)) {
            std::cout << "  -> [Consumer " << consumerId << "] Consumed Offset " 
                      << msg.offset << ": '" << msg.payload << "'\\n";
            currentOffset++;
        }
    }
};

int main() {
    auto ordersTopic = std::make_shared<Topic>("orders");
    std::atomic<bool> running{true};

    Consumer c1("EmailService", ordersTopic);
    Consumer c2("BillingService", ordersTopic);

    ordersTopic->publish("Order #1001 Created");
    ordersTopic->publish("Order #1002 Created");

    std::cout << "\\n--- Consumers Processing Independently ---\\n";
    c1.consumeNext(running);
    c1.consumeNext(running);

    c2.consumeNext(running);

    ordersTopic->publish("Order #1003 Created");
    c2.consumeNext(running);
    c2.consumeNext(running);

    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Append-Only Topic Log:</strong> Messages are immutable records with monotonically increasing integer offsets.",
                "<strong>2. Consumer Offset Independence:</strong> Each consumer tracks its own read position, allowing different services to replay or lag safely.",
                "<strong>3. Efficient Condition Variable Signaling:</strong> Consumers sleep without spinning CPU until new messages are appended."
            ],
            "comparison_matrix": {
                "title": "Queue (RabbitMQ) vs Pub/Sub Log (Kafka)",
                "headers": ["Feature", "Point-to-Point Queue", "Distributed Partitioned Log"],
                "rows": [
                    ["Message Consumption", "Deleted once acknowledged", "Retained based on retention TTL"],
                    ["Replayability", "Impossible", "Fully replayable by resetting offset"],
                    ["Consumer Scalability", "Compete for items", "Partitioned consumers read in parallel"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Erasing messages when first consumer reads them", "correction": "Retain topic log so multiple independent consumer groups can read the same stream."}
            ],
            "interview_traps": [
                "<strong>Trap: 'How do you guarantee exactly-once message delivery in C++ LLD?'</strong><br><em>Answer:</em> Pair idempotent consumer processing with transactional outbox or deduplication hash sets tracking processed message UUIDs."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor a point-to-point single-consumer queue into a multi-subscriber broadcast topic.",
                "bad_code": "queue.pop() removes message forever",
                "good_code": "vector log with offset tracking per subscriber"
            },
            "practice_problem": {
                "title": "Design Partitioned Topic with Key Hashing",
                "description": "Extend Topic to support 4 partitions where messages with the same `partitionKey` are strictly guaranteed FIFO ordering.",
                "hint": "Route messages to partition index via `std::hash<string>{}(key) % numPartitions`."
            }
        },
        {
            "id": "stock-order-book",
            "title": "Stock Trading Matching Order Book (Advanced)",
            "definition": "An ultra-low-latency financial matching engine organizing Buy (Bids) and Sell (Asks) orders by Price-Time Priority and executing trades at matching price points.",
            "why_it_matters": "The highest-tier LLD problem for fintech and quantitative trading firms (Citadel, Jane Street, Optiver, Goldman Sachs). Evaluates cache-friendly data structures, zero-allocation algorithms, and priority matching.",
            "real_world_analogy": "NASDAQ or NYSE limit order book: traders submit 'Buy 100 AAPL @ $150' and 'Sell 50 AAPL @ $150'; the matching engine instantly matches 50 shares at $150 and keeps the remaining 50 Buy limit order open.",
            "conceptual_breakdown": [
                "<strong>Order Entity:</strong> <code>id</code>, <code>side</code> (BUY/SELL), <code>price</code>, <code>quantity</code>, <code>timestamp</code>.",
                "<strong>Limit Level:</strong> A FIFO queue (doubly linked list) of orders at the exact same price.",
                "<strong>Price Ladder (Bids & Asks):</strong> Bids sorted in descending order (highest price first); Asks sorted in ascending order (lowest price first).",
                "<strong>Price-Time Priority Matching:</strong> Best price matches first; if prices match, oldest order matches first."
            ],
            "visual_diagram": {
                "type": "class_diagram",
                "title": "Order Book Architecture",
                "classes": [
                    {
                        "name": "Order",
                        "is_abstract": False,
                        "attributes": ["+ orderId: uint64_t", "+ isBuy: bool", "+ price: double", "+ quantity: uint32_t"],
                        "methods": []
                    },
                    {
                        "name": "LimitLevel",
                        "is_abstract": False,
                        "attributes": ["+ price: double", "+ totalVolume: uint32_t", "+ orders: list<Order>"],
                        "methods": []
                    },
                    {
                        "name": "OrderBook",
                        "is_abstract": False,
                        "attributes": ["- bids: map<double, LimitLevel, greater<double>>", "- asks: map<double, LimitLevel, less<double>>"],
                        "methods": ["+ addOrder(order: Order): void", "- matchOrders(): void"]
                    }
                ],
                "relationships": [
                    {"from": "LimitLevel", "to": "Order", "type": "composition", "label": "FIFO order queue"},
                    {"from": "OrderBook", "to": "LimitLevel", "type": "composition", "label": "bids & asks ladders"}
                ]
            },
            "interactive_animation": {
                "title": "Price-Time Priority Matching Engine",
                "steps": [
                    {"step": 1, "description": "Order Book Bids: [100 shares @ $150]. Asks: [50 shares @ $152].", "active_nodes": ["Bids: $150", "Asks: $152"]},
                    {"step": 2, "description": "Incoming Market Buy Order: 50 shares. Crosses book against best Ask ($152).", "active_nodes": ["Matching Engine"]},
                    {"step": 3, "description": "Trade Executed: 50 shares @ $152. Ask level $152 is completely filled and removed.", "active_nodes": ["Trade Execution", "Asks: $152 (Cleared)"]}
                ]
            },
            "cpp_implementation": """#include <iostream>
#include <map>
#include <deque>
#include <memory>
#include <iomanip>
#include <algorithm>

enum class Side { BUY, SELL };

struct Order {
    uint64_t id;
    Side side;
    double price;
    uint32_t quantity;
};

struct Trade {
    uint64_t buyerOrderId;
    uint64_t sellerOrderId;
    double price;
    uint32_t quantity;
};

class OrderBook {
private:
    // Bids: Sorted Descending (Highest buy price at top)
    std::map<double, std::deque<Order>, std::greater<double>> bids;

    // Asks: Sorted Ascending (Lowest sell price at top)
    std::map<double, std::deque<Order>, std::less<double>> asks;

public:
    void addOrder(Order order) {
        if (order.side == Side::BUY) {
            matchBuyOrder(order);
            if (order.quantity > 0) {
                bids[order.price].push_back(order);
                std::cout << "[RESTING BID] Order #" << order.id << " added: " 
                          << order.quantity << " @ $" << std::fixed << std::setprecision(2) << order.price << "\\n";
            }
        } else {
            matchSellOrder(order);
            if (order.quantity > 0) {
                asks[order.price].push_back(order);
                std::cout << "[RESTING ASK] Order #" << order.id << " added: " 
                          << order.quantity << " @ $" << std::fixed << std::setprecision(2) << order.price << "\\n";
            }
        }
    }

private:
    void matchBuyOrder(Order& buyOrder) {
        while (buyOrder.quantity > 0 && !asks.empty()) {
            auto bestAskIt = asks.begin();
            double bestAskPrice = bestAskIt->first;

            if (buyOrder.price < bestAskPrice) break; // No price overlap

            auto& orderQueue = bestAskIt->second;
            while (buyOrder.quantity > 0 && !orderQueue.empty()) {
                Order& sellOrder = orderQueue.front();
                uint32_t matchQty = std::min(buyOrder.quantity, sellOrder.quantity);

                // Trade executed at the resting order's price (bestAskPrice)
                std::cout << "  *** TRADE EXECUTED *** " << matchQty << " shares @ $" 
                          << bestAskPrice << " (Buyer #" << buyOrder.id << " vs Seller #" << sellOrder.id << ")\\n";

                buyOrder.quantity -= matchQty;
                sellOrder.quantity -= matchQty;

                if (sellOrder.quantity == 0) {
                    orderQueue.pop_front();
                }
            }

            if (orderQueue.empty()) {
                asks.erase(bestAskIt);
            }
        }
    }

    void matchSellOrder(Order& sellOrder) {
        while (sellOrder.quantity > 0 && !bids.empty()) {
            auto bestBidIt = bids.begin();
            double bestBidPrice = bestBidIt->first;

            if (sellOrder.price > bestBidPrice) break; // No price overlap

            auto& orderQueue = bestBidIt->second;
            while (sellOrder.quantity > 0 && !orderQueue.empty()) {
                Order& buyOrder = orderQueue.front();
                uint32_t matchQty = std::min(sellOrder.quantity, buyOrder.quantity);

                // Trade executed at the resting order's price (bestBidPrice)
                std::cout << "  *** TRADE EXECUTED *** " << matchQty << " shares @ $" 
                          << bestBidPrice << " (Seller #" << sellOrder.id << " vs Buyer #" << buyOrder.id << ")\\n";

                sellOrder.quantity -= matchQty;
                buyOrder.quantity -= matchQty;

                if (buyOrder.quantity == 0) {
                    orderQueue.pop_front();
                }
            }

            if (orderQueue.empty()) {
                bids.erase(bestBidIt);
            }
        }
    }
};

int main() {
    OrderBook book;

    std::cout << "--- Submitting Resting Orders ---\\n";
    book.addOrder({1, Side::BUY, 150.00, 100});
    book.addOrder({2, Side::BUY, 149.50, 200});
    book.addOrder({3, Side::SELL, 152.00, 150});

    std::cout << "\\n--- Submitting Aggressive Market Crossing Order ---\\n";
    // Incoming Sell of 60 shares at $150 crosses resting Buy #1
    book.addOrder({4, Side::SELL, 150.00, 60});

    return 0;
}""",
            "step_by_step_explanation": [
                "<strong>1. Price-Time Priority Ladder:</strong> <code>std::map</code> maintains sorted price levels while <code>std::deque</code> enforces strict FIFO matching for equal prices.",
                "<strong>2. Crossing Book Execution:</strong> Trade prices default to the resting maker order's price point.",
                "<strong>3. Efficient Level Pruning:</strong> Empty price levels are erased immediately to keep tree searches fast."
            ],
            "comparison_matrix": {
                "title": "Matching Engine Data Structures",
                "headers": ["Structure", "Best Bid/Ask Lookup", "Insert New Limit", "Cancel Order"],
                "rows": [
                    ["std::map + std::deque", "O(1) (begin())", "O(log P)", "O(N) in queue"],
                    ["Dense Flat Array (Indexed by Cent)", "O(1) with bitset", "O(1)", "O(1) with intrusive doubly-linked list"],
                    ["B-Tree / Red-Black Tree", "O(1)", "O(log P)", "O(log P)"]
                ]
            },
            "common_mistakes": [
                {"mistake": "Floating point price comparisons using `==`", "correction": "Represent prices as integer cents (e.g. 15000 cents for $150.00) to eliminate IEEE 754 precision drift."}
            ],
            "interview_traps": [
                "<strong>Trap: 'How do high-frequency trading (HFT) engines cancel orders in O(1) time without iterating the deque?'</strong><br><em>Answer:</em> Use an intrusive doubly-linked list for each limit level combined with an `unordered_map<OrderId, OrderNode*>` lookup map."
            ],
            "code_refactor_exercise": {
                "problem": "Refactor an order book where double floating point prices cause orders at $10.00000001 not to match $10.00.",
                "bad_code": "double price;",
                "good_code": "using Price = int64_t; // in fixed precision micro-units"
            },
            "practice_problem": {
                "title": "Design O(1) Order Cancellation",
                "description": "Implement an intrusive Doubly Linked List Order node so `cancelOrder(uint64_t orderId)` executes in strictly O(1) time.",
                "hint": "Store node pointers in a hash table `unordered_map<uint64_t, Order*>`."
            }
        }
    ]
}

with open(os.path.join(content_dir, "module_19.json"), "w", encoding="utf-8") as f:
    json.dump(m19, f, indent=2)

print(f"Generated module_19.json with {len(m19['topics'])} topics")
