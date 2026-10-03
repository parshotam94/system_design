import json
from pathlib import Path

content_dir = Path("content")
content_dir.mkdir(exist_ok=True)

def write_module(mod_data):
    mod_id = mod_data["module_id"]
    path = content_dir / f"module_{mod_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mod_data, f, indent=2)
    print(f"Generated module_{mod_id}.json with {len(mod_data['topics'])} topics")

# ==============================================================================
# MODULE 04: UML for Low-Level Design
# ==============================================================================
mod_04 = {
    "module_id": "04",
    "title": "UML for Low-Level Design",
    "level": "Beginner",
    "category": "Modeling",
    "description": "Visual modeling for LLD interviews: Class diagrams with visibility symbols (+, -, #), relationship notations, Sequence diagrams with lifelines, State machines, and Activity diagrams.",
    "topics": [
        {
            "id": "uml-class-diagrams",
            "title": "UML Class Diagram Notations (+, -, #)",
            "description": "Standard UML 3-box compartment notation: Class name, attributes, methods, and visibility specifiers.",
            "sections": [
                {"step_number": 1, "title": "1. What is it?", "content": "<p>A <strong>UML Class Diagram</strong> is a static structural diagram that describes the structure of a system by showing classes, attributes, operations, and relationships among objects.</p>"},
                {"step_number": 2, "title": "2. Why do we need it?", "content": "<p>In Low-Level Design interviews and technical design documents, UML diagrams communicate architecture instantaneously without getting bogged down in syntax details.</p>"},
                {"step_number": 3, "title": "3. Core idea", "content": "<p>Represent a class as a 3-compartment rectangle: Top = Class Name / Stereotype, Middle = Attributes, Bottom = Methods with visibility modifiers (+ public, - private, # protected, ~ package).</p>"},
                {"step_number": 4, "title": "4. How it works", "content": "<p>Attribute syntax: <code>[visibility] name : type [= default]</code>.<br>Method syntax: <code>[visibility] name(param: type) : returnType</code>.</p>"},
                {"step_number": 5, "title": "5. Visual explanation", "content": "<p>Standard UML Class Box:</p>", "diagram": {
                    "title": "Account & Customer UML Representation",
                    "classes": [
                        {
                            "name": "BankAccount",
                            "attributes": [
                                {"visibility": "-", "name": "accountNumber", "type": "std::string"},
                                {"visibility": "-", "name": "balance", "type": "double"},
                                {"visibility": "#", "name": "creationTimestamp", "type": "uint64_t"}
                            ],
                            "methods": [
                                {"visibility": "+", "name": "deposit", "params": "amount: double", "returnType": "void"},
                                {"visibility": "+", "name": "withdraw", "params": "amount: double", "returnType": "bool"},
                                {"visibility": "+", "name": "getBalance", "params": "", "returnType": "double"}
                            ]
                        }
                    ],
                    "relationships": []
                }},
                {"step_number": 6, "title": "6. C++ implementation", "content": "<p>Exact C++ mapping of the BankAccount UML class diagram:</p>", "code_example": {
                    "filename": "uml_bank_account.cpp",
                    "code": """#include <iostream>
#include <string>
#include <cstdint>

class BankAccount {
private:
    std::string accountNumber; // - accountNumber : std::string
    double balance{0.0};        // - balance : double

protected:
    uint64_t creationTimestamp; // # creationTimestamp : uint64_t

public:
    BankAccount(std::string accNum, double initBal, uint64_t ts)
        : accountNumber(std::move(accNum)), balance(initBal), creationTimestamp(ts) {}

    void deposit(double amount) { // + deposit(amount: double) : void
        balance += amount;
    }

    bool withdraw(double amount) { // + withdraw(amount: double) : bool
        if (amount > balance) return false;
        balance -= amount;
        return true;
    }

    [[nodiscard]] double getBalance() const noexcept { // + getBalance() : double
        return balance;
    }
};"""
                }},
                {"step_number": 7, "title": "7. Code walkthrough", "content": "<p><strong>Visibility translation:</strong> <code>+</code> translates to <code>public:</code>, <code>-</code> to <code>private:</code>, and <code>#</code> to <code>protected:</code>.</p>"},
                {"step_number": 8, "title": "8. Real-world example", "content": "<p>Technical architecture design documents for financial services, gaming engines, and cloud distributed microservices.</p>"},
                {"step_number": 9, "title": "9. When to use", "content": "<p>Use class diagrams in Phase 2 of any LLD interview immediately after identifying domain entities.</p>"},
                {"step_number": 10, "title": "10. When NOT to use", "content": "<p>Do not draw private utility helper functions or trivial variables that clutter the diagram during a timed interview.</p>"},
                {"step_number": 11, "title": "11. Advantages", "content": "<p>Universal standard language understood by all software engineers worldwide.</p>"},
                {"step_number": 12, "title": "12. Disadvantages", "content": "<p>Excessive detail can become outdated quickly if not synchronized with code.</p>"},
                {"step_number": 13, "title": "13. Variations / Types", "content": "<p>Conceptual Class Diagrams, Specification Class Diagrams, Implementation Class Diagrams.</p>"},
                {"step_number": 14, "title": "14. Common mistakes", "content": "<p>Writing C++ syntax inside UML boxes (e.g. Writing <code>double balance;</code> instead of the standard UML <code>- balance: double</code>).</p>"},
                {"step_number": 15, "title": "15. Interview questions", "content": "<p><strong>Q:</strong> What does an italicized class name or method name signify in UML?</p>"},
                {"step_number": 16, "title": "16. Interview answer", "content": "<p><strong>Answer:</strong> An italicized class name indicates an <strong>Abstract Class</strong>. An italicized method name indicates an <strong>Abstract / Pure Virtual Method</strong> (e.g. <code><em>+ draw() : void</em></code> signifies <code>virtual void draw() = 0;</code>).</p>"},
                {"step_number": 17, "title": "17. Practice problem", "content": "<p>Draw the UML notation for an abstract <code>IVehicle</code> with pure virtual <code>startEngine()</code> and derived <code>Motorcycle</code>.</p>", "practice": {
                    "title": "UML Class Mapping Practice",
                    "problemStatement": "Map an IVehicle interface to clean C++20 code.",
                    "requirements": ["Abstract IVehicle", "Derived Motorcycle", "Proper access specifiers"],
                    "constraints": ["Const-correct"],
                    "hint": "Use interface stereotype in UML.",
                    "expectedEntities": [{"name": "IVehicle", "responsibility": "Vehicle contract."}],
                    "referenceCode": {
                        "filename": "uml_practice.cpp",
                        "code": """class IVehicle {
public:
    virtual ~IVehicle() = default;
    virtual void startEngine() = 0;
};
class Motorcycle : public IVehicle {
public:
    void startEngine() override {}
};"""
                    }
                }},
                {"step_number": 18, "title": "18. Summary", "content": "<p>UML class diagrams are the standard visual shorthand for expressing object-oriented architecture in Low-Level Design.</p>"}
            ]
        },
        {
            "id": "uml-relationships-notation",
            "title": "UML Relationship Arrows & Multiplicities",
            "description": "Mastering UML connector symbols: Inheritance, Realization, Composition, Aggregation, Association, and Dependency.",
            "sections": [
                {"step_number": 1, "title": "1. What is it?", "content": "<p>UML Relationships define the structural and behavioral links between classes: <strong>Inheritance (──▷)</strong>, <strong>Realization (..▷)</strong>, <strong>Composition (──◆)</strong>, <strong>Aggregation (──◇)</strong>, <strong>Association (──>)</strong>, and <strong>Dependency (..>)</strong>.</p>"},
                {"step_number": 2, "title": "2. Why do we need it?", "content": "<p>Accurately communicating ownership, lifecycle binding, and coupling is essential in design discussions.</p>"},
                {"step_number": 3, "title": "3. Core idea", "content": "<p>Solid line with filled diamond = strong lifetime ownership (Composition). Solid line with hollow diamond = shared container (Aggregation). Dashed line with open arrow = temporary use (Dependency).</p>"},
                {"step_number": 4, "title": "4. How it works", "content": "<p>Multiplicities denote quantities (e.g. <code>1</code>, <code>0..1</code>, <code>*</code>, <code>1..*</code>). In C++, <code>1..*</code> maps to a container member like <code>std::vector&lt;T&gt;</code>.</p>"},
                {"step_number": 5, "title": "5. Visual explanation", "content": "<p>UML Relationship Arrow Matrix:</p>", "comparison": {
                    "title": "UML Relationship Arrow Symbols & C++ Mappings",
                    "columns": ["Relationship", "UML Symbol", "Lifetime Dependency", "C++ Implementation Mapping"],
                    "rows": [
                        ["Inheritance", "──────▷ (Solid triangle)", "Is-a subtype", "class Dog : public Animal"],
                        ["Realization", " - - - ▷ (Dashed triangle)", "Implements interface", "class Service : public IService"],
                        ["Composition", "──────◆ (Filled diamond)", "Strong (Parent owns Child)", "class Car { Engine engine; };"],
                        ["Aggregation", "──────◇ (Hollow diamond)", "Weak (Child outlives Parent)", "class Dept { Teacher* t; };"],
                        ["Association", "──────> (Solid arrow)", "Uses / Navigates to", "class Order { Customer* c; };"],
                        ["Dependency", " - - - > (Dashed arrow)", "Temporary parameter / local", "void print(const Document& d);"]
                    ]
                }},
                {"step_number": 6, "title": "6. C++ implementation", "content": "<p>Code implementing all 6 UML relationship types in a single system:</p>", "code_example": {
                    "filename": "all_uml_relationships.cpp",
                    "code": """#include <iostream>
#include <vector>
#include <memory>
#include <string>

// 1. Realization: Interface contract
class IPrintable {
public:
    virtual ~IPrintable() = default;
    virtual void print() const = 0;
};

// 2. Composition Target: Engine owned by Car
class Engine {
public:
    void run() const { std::cout << "Engine purring\\n"; }
};

// 3. Aggregation Target: Driver exists independently
class Driver {
public:
    std::string name;
    explicit Driver(std::string n) : name(std::move(n)) {}
};

// 4. Dependency Target: Temporary GPS coordinates
class GpsCoordinate {
public:
    double lat, lon;
};

// Car integrates all relationships!
class Car : public IPrintable { // Realization (IPrintable)
private:
    Engine engine;            // Composition (──◆)
    Driver* currentDriver;     // Aggregation (──◇)

public:
    Car() : currentDriver(nullptr) {}

    void assignDriver(Driver* d) { // Aggregation setup
        currentDriver = d;
    }

    void navigateTo(const GpsCoordinate& target) { // Dependency (..>)
        std::cout << "[Car] Navigating to lat: " << target.lat << "\\n";
        engine.run();
    }

    void print() const override { // Realization override
        std::cout << "[Car System] Driver: " << (currentDriver ? currentDriver->name : "None") << "\\n";
    }
};"""
                }},
                {"step_number": 7, "title": "7. Code walkthrough", "content": "<p><strong>Line 27 (Composition):</strong> <code>Engine engine;</code> is directly embedded.<br><strong>Line 28 (Aggregation):</strong> <code>Driver* currentDriver;</code> does not own Driver memory.<br><strong>Line 35 (Dependency):</strong> <code>navigateTo(const GpsCoordinate& target)</code> receives GPS as a temporary parameter without storing it.</p>"},
                {"step_number": 8, "title": "8. Real-world example", "content": "<p>Enterprise software architecture blueprints (e.g. AWS / Google Cloud reference architectures).</p>"},
                {"step_number": 9, "title": "9. When to use", "content": "<p>Use precise relationship arrows on system architecture whiteboards to clarify object lifecycles.</p>"},
                {"step_number": 10, "title": "10. When NOT to use", "content": "<p>Do not draw Dependency arrows for every standard library type (like <code>std::string</code>) to prevent diagram clutter.</p>"},
                {"step_number": 11, "title": "11. Advantages", "content": "<p>Unambiguous specification of lifetime, ownership, and coupling.</p>"},
                {"step_number": 12, "title": "12. Disadvantages", "content": "<p>Distinguishing Aggregation vs Association can be subjective in informal discussions.</p>"},
                {"step_number": 13, "title": "13. Variations / Types", "content": "<p>Bidirectional Association, Unidirectional Association, Multiplicity bounds (<code>1..*</code>).</p>"},
                {"step_number": 14, "title": "14. Common mistakes", "content": "<p>Confusing Composition (filled diamond) with Aggregation (hollow diamond).</p>"},
                {"step_number": 15, "title": "15. Interview questions", "content": "<p><strong>Q:</strong> What is the difference between an Association and a Dependency in C++ code?</p>"},
                {"step_number": 16, "title": "16. Interview answer", "content": "<p><strong>Answer:</strong> An <strong>Association</strong> is a structural link where class A holds a persistent reference or pointer to class B as a <em>member variable</em>. A <strong>Dependency</strong> is a transient behavioral relationship where class A uses class B only as a <em>method parameter or local variable inside a function body</em>.</p>"},
                {"step_number": 17, "title": "17. Practice problem", "content": "<p>Model a <code>Hospital</code> that has Composition with <code>Room</code> and Aggregation with <code>Doctor*</code>.</p>", "practice": {
                    "title": "Hospital Ownership Modeling",
                    "problemStatement": "Implement Hospital with owned Rooms and aggregated Doctors.",
                    "requirements": ["Hospital owns std::vector<Room>", "Hospital aggregates std::vector<Doctor*>"],
                    "constraints": ["Clean destructors"],
                    "hint": "Use unique_ptr or value objects for Rooms and raw/weak pointers for Doctors.",
                    "expectedEntities": [{"name": "Hospital", "responsibility": "Container for rooms and doctor affiliations."}],
                    "referenceCode": {
                        "filename": "hospital_uml.cpp",
                        "code": """#include <vector>
#include <string>
class Room { public: int number; };
class Doctor { public: std::string name; };
class Hospital {
    std::vector<Room> rooms;      // Composition
    std::vector<Doctor*> doctors; // Aggregation
public:
    void addRoom(Room r) { rooms.push_back(r); }
    void affiliateDoctor(Doctor* d) { doctors.push_back(d); }
};"""
                    }
                }},
                {"step_number": 18, "title": "18. Summary", "content": "<p>Mastering UML relationship symbols allows you to express object lifecycles and coupling with precision in system design interviews.</p>"}
            ]
        },
        {
            "id": "uml-sequence-diagrams",
            "title": "Sequence Diagrams & Lifelines",
            "description": "Visualizing dynamic runtime message passing, synchronous calls, return messages, and object lifelines over time.",
            "sections": [
                {"step_number": 1, "title": "1. What is it?", "content": "<p>A <strong>UML Sequence Diagram</strong> is an interaction diagram that shows how objects collaborate over time by depicting message exchanges along vertical lifelines.</p>"},
                {"step_number": 2, "title": "2. Why do we need it?", "content": "<p>Class diagrams show static structure, but Sequence diagrams show dynamic runtime behavior (e.g. what happens when a user clicks 'Buy Now').</p>"},
                {"step_number": 3, "title": "3. Core idea", "content": "<p>Time flows downward. Vertical dashed lines represent object lifelines. Horizontal solid arrows represent synchronous method calls; dashed arrows represent return values.</p>"},
                {"step_number": 4, "title": "4. How it works", "content": "<p>Components: Lifelines (<code>Client</code>, <code>OrderService</code>, <code>PaymentGateway</code>), Activation Bars (execution period), Synchronous Messages (<code>──></code>), Asynchronous Messages (<code>──>></code>), and Self-Calls.</p>"},
                {"step_number": 5, "title": "5. Visual explanation", "content": "<p>Order Checkout Sequence Flow:</p>", "callout": {
                    "type": "tip",
                    "title": "Sequence Flow: Checkout Order",
                    "text": "1. Customer -> checkout(cartId) -> OrderService\\n2. OrderService -> calculateTotal(cartId) -> CartService\\n3. OrderService -> charge(amount) -> PaymentGateway\\n4. PaymentGateway --> [TX_SUCCESS] --> OrderService\\n5. OrderService -> sendReceipt(email) -> NotificationService\\n6. OrderService --> [OrderConfirmed] --> Customer"
                }},
                {"step_number": 6, "title": "6. C++ implementation", "content": "<p>C++ implementation matching the Checkout Sequence Diagram:</p>", "code_example": {
                    "filename": "checkout_sequence.cpp",
                    "code": """#include <iostream>
#include <string>
#include <memory>

class PaymentGateway {
public:
    bool charge(double amount) {
        std::cout << "  [PaymentGateway] Charged $" << amount << "\\n";
        return true;
    }
};

class NotificationService {
public:
    void sendConfirmation(const std::string& email) {
        std::cout << "  [NotificationService] Receipt emailed to " << email << "\\n";
    }
};

class OrderService {
private:
    std::shared_ptr<PaymentGateway> payment;
    std::shared_ptr<NotificationService> notifier;
public:
    OrderService(std::shared_ptr<PaymentGateway> p, std::shared_ptr<NotificationService> n)
        : payment(std::move(p)), notifier(std::move(n)) {}

    void checkout(double amount, const std::string& email) {
        std::cout << "[OrderService] Initiating checkout...\\n";
        if (payment->charge(amount)) {
            notifier->sendConfirmation(email);
            std::cout << "[OrderService] Checkout completed successfully!\\n";
        }
    }
};

int main() {
    auto p = std::make_shared<PaymentGateway>();
    auto n = std::make_shared<NotificationService>();
    OrderService orders(p, n);
    orders.checkout(89.50, "alice@example.com");
    return 0;
}"""
                }},
                {"step_number": 7, "title": "7. Code walkthrough", "content": "<p><strong>Lines 26-31:</strong> <code>checkout()</code> orchestrates the exact sequential message-passing flow illustrated in the Sequence Diagram.</p>"},
                {"step_number": 8, "title": "8. Real-world example", "content": "<p>OAuth2 3-way authorization flows, payment processing gateways, and database 2-phase commit protocols.</p>"},
                {"step_number": 9, "title": "9. When to use", "content": "<p>Use sequence diagrams whenever explaining complex multi-object business workflows in an interview.</p>"},
                {"step_number": 10, "title": "10. When NOT to use", "content": "<p>Do not draw sequence diagrams for trivial single-class CRUD operations.</p>"},
                {"step_number": 11, "title": "11. Advantages", "content": "<p>Visually highlights bottlenecks, redundant round-trips, and order of execution.</p>"},
                {"step_number": 12, "title": "12. Disadvantages", "content": "<p>Can become wide and difficult to read if more than 6 lifelines are involved.</p>"},
                {"step_number": 13, "title": "13. Variations / Types", "content": "<p>Synchronous Sequence, Asynchronous Sequence with reply loops, Communication Diagrams.</p>"},
                {"step_number": 14, "title": "14. Common mistakes", "content": "<p>Omitting return arrows or mixing up asynchronous message notation.</p>"},
                {"step_number": 15, "title": "15. Interview questions", "content": "<p><strong>Q:</strong> What is an activation box in a UML sequence diagram?</p>"},
                {"step_number": 16, "title": "16. Interview answer", "content": "<p><strong>Answer:</strong> An <strong>Activation Box</strong> (or execution occurrence) is a thin vertical rectangle placed on an object's lifeline representing the exact time period during which that object is actively executing a method on the CPU or call stack.</p>"},
                {"step_number": 17, "title": "17. Practice problem", "content": "<p>Implement a 3-step <code>ATMWithdrawal</code> workflow: <code>ATM -&gt; CardReader -&gt; BankBackend -&gt; CashDispenser</code>.</p>", "practice": {
                    "title": "ATM Withdrawal Sequence Workflow",
                    "problemStatement": "Implement ATM sequence workflow coordinating reader, backend, and dispenser.",
                    "requirements": ["Authenticate PIN", "Deduct balance", "Dispense cash"],
                    "constraints": ["Sequential validation"],
                    "hint": "Return false early if PIN validation fails.",
                    "expectedEntities": [{"name": "ATM", "responsibility": "Orchestrates withdrawal steps."}],
                    "referenceCode": {
                        "filename": "atm_seq.cpp",
                        "code": """#include <iostream>
class BankBackend { public: bool verifyAndDeduct(int pin, double amt) { return pin == 1234; } };
class CashDispenser { public: void dispense(double amt) { std::cout << "Dispensed $" << amt << "\\n"; } };
class ATM {
    BankBackend bank;
    CashDispenser dispenser;
public:
    bool withdraw(int pin, double amt) {
        if (bank.verifyAndDeduct(pin, amt)) {
            dispenser.dispense(amt);
            return true;
        }
        return false;
    }
};"""
                    }
                }},
                {"step_number": 18, "title": "18. Summary", "content": "<p>Sequence diagrams provide a crystal-clear timeline of runtime interactions across collaborating system objects.</p>"}
            ]
        },
        {
            "id": "uml-state-and-activity",
            "title": "State Machines & Activity Diagrams",
            "description": "Modeling object lifecycle state transitions, guard conditions, and algorithmic flowcharts in UML.",
            "sections": [
                {"step_number": 1, "title": "1. What is it?", "content": "<p>A <strong>UML State Machine Diagram</strong> models the lifecycle states of a single entity (e.g. <code>Order: CREATED -&gt; PAID -&gt; SHIPPED</code>). A <strong>UML Activity Diagram</strong> models business workflow algorithms and decision branches.</p>"},
                {"step_number": 2, "title": "2. Why do we need it?", "content": "<p>Complex real-world entities (Vending Machines, Orders, Hotel Bookings) have strict state-dependent behaviors. State diagrams visualize valid and invalid transitions.</p>"},
                {"step_number": 3, "title": "3. Core idea", "content": "<p>States are rounded rectangles. Transitions are arrows labeled with <code>Event [Guard] / Action</code>.</p>"},
                {"step_number": 4, "title": "4. How it works", "content": "<p>In C++, finite state machines are implemented using the <strong>State Design Pattern</strong> or an <code>enum class State</code> with guarded transition methods.</p>"},
                {"step_number": 5, "title": "5. Visual explanation", "content": "<p>Vending Machine State Machine Flow:</p>", "callout": {
                    "type": "tip",
                    "title": "Vending Machine State Lifecycle",
                    "text": "[IdleState] -- insertCoin() --> [HasCoinState] -- selectItem() --> [DispensingState] -- dispense() --> [IdleState]"
                }},
                {"step_number": 6, "title": "6. C++ implementation", "content": "<p>Guarded Finite State Machine in C++:</p>", "code_example": {
                    "filename": "fsm_vending.cpp",
                    "code": """#include <iostream>
#include <stdexcept>

enum class VendingState { IDLE, HAS_MONEY, DISPENSING, SOLD_OUT };

class VendingMachineFSM {
private:
    VendingState currentState{VendingState::IDLE};
    double balance{0.0};
    int itemCount{5};

public:
    void insertMoney(double amount) {
        if (currentState != VendingState::IDLE && currentState != VendingState::HAS_MONEY) {
            throw std::logic_error("Cannot insert money during current operation");
        }
        balance += amount;
        currentState = VendingState::HAS_MONEY;
        std::cout << "[FSM: HAS_MONEY] Current balance: $" << balance << "\\n";
    }

    void selectItem(double price) {
        if (currentState != VendingState::HAS_MONEY) {
            throw std::logic_error("Please insert money first");
        }
        if (balance < price) {
            throw std::runtime_error("Insufficient balance");
        }
        balance -= price;
        currentState = VendingState::DISPENSING;
        std::cout << "[FSM: DISPENSING] Dispensing item...\\n";
        dispense();
    }

private:
    void dispense() {
        --itemCount;
        std::cout << "[FSM] Item ejected. Remaining inventory: " << itemCount << "\\n";
        currentState = (itemCount > 0) ? VendingState::IDLE : VendingState::SOLD_OUT;
    }
};

int main() {
    VendingMachineFSM vm;
    vm.insertMoney(2.00);
    vm.selectItem(1.50);
    return 0;
}"""
                }},
                {"step_number": 7, "title": "7. Code walkthrough", "content": "<p><strong>Lines 13-35:</strong> Transitions between <code>IDLE -&gt; HAS_MONEY -&gt; DISPENSING -&gt; IDLE</code> enforce state invariants and throw on illegal transitions.</p>"},
                {"step_number": 8, "title": "8. Real-world example", "content": "<p>TCP connection lifecycle (<code>LISTEN -&gt; SYN_SENT -&gt; ESTABLISHED -&gt; FIN_WAIT -&gt; CLOSED</code>).</p>"},
                {"step_number": 9, "title": "9. When to use", "content": "<p>Use state diagrams when an entity's behavior changes fundamentally based on internal state.</p>"},
                {"step_number": 10, "title": "10. When NOT to use", "content": "<p>Do not create state diagrams for stateless calculation utilities.</p>"},
                {"step_number": 11, "title": "11. Advantages", "content": "<p>Prevents illegal state transitions and unhandled edge-case bugs.</p>"},
                {"step_number": 12, "title": "12. Disadvantages", "content": "<p>State transition tables can grow to $O(N^2)$ if there are many states.</p>"},
                {"step_number": 13, "title": "13. Variations / Types", "content": "<p>Hierarchical State Machines (Statecharts), Activity Flowcharts.</p>"},
                {"step_number": 14, "title": "14. Common mistakes", "content": "<p>Allowing transitions from terminal states (e.g. mutating an order after it has been <code>CANCELLED</code>).</p>"},
                {"step_number": 15, "title": "15. Interview questions", "content": "<p><strong>Q:</strong> What design pattern is best suited for complex state machines with dozens of transitions?</p>"},
                {"step_number": 16, "title": "16. Interview answer", "content": "<p><strong>Answer:</strong> The <strong>State Design Pattern</strong>, where each state is encapsulated as its own polymorphic class (e.g. <code>HasMoneyState</code>, <code>DispensingState</code>) implementing a common <code>IVendingState</code> interface, eliminating massive switch-case blocks.</p>"},
                {"step_number": 17, "title": "17. Practice problem", "content": "<p>Implement an <code>AudioPlayer</code> FSM supporting <code>PLAYING</code>, <code>PAUSED</code>, and <code>STOPPED</code> states.</p>", "practice": {
                    "title": "Audio Player FSM",
                    "problemStatement": "Implement AudioPlayer state transitions for play, pause, and stop.",
                    "requirements": ["States: STOPPED, PLAYING, PAUSED", "Valid transitions only"],
                    "constraints": ["Throw on invalid transitions"],
                    "hint": "Cannot pause when stopped.",
                    "expectedEntities": [{"name": "AudioPlayer", "responsibility": "Controls playback states."}],
                    "referenceCode": {
                        "filename": "audio_fsm.cpp",
                        "code": """#include <iostream>
#include <stdexcept>
enum class AudioState { STOPPED, PLAYING, PAUSED };
class AudioPlayer {
    AudioState state{AudioState::STOPPED};
public:
    void play() { state = AudioState::PLAYING; }
    void pause() {
        if (state != AudioState::PLAYING) throw std::logic_error("Cannot pause when not playing");
        state = AudioState::PAUSED;
    }
    void stop() { state = AudioState::STOPPED; }
};"""
                    }
                }},
                {"step_number": 18, "title": "18. Summary", "content": "<p>State machine and activity diagrams model the dynamic lifecycle and algorithmic workflows of mission-critical systems.</p>"}
            ]
        }
    ]
}

write_module(mod_04)
