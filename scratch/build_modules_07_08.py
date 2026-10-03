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

# Helper to build standard 18-step format topics with rich details
def make_18_step_topic(topic_id, title, desc, what_is, why_need, core_idea, how_works, visual_dict, code_filename, code_content, walkthrough, real_world, when_use, when_not_use, advantages, disadvantages, variations, mistakes, q_text, a_text, practice_title, practice_stmt, practice_code):
    sections = [
        {"step_number": 1, "title": "1. What is it?", "content": f"<p>{what_is}</p>"},
        {"step_number": 2, "title": "2. Why do we need it?", "content": f"<p>{why_need}</p>"},
        {"step_number": 3, "title": "3. Core idea", "content": f"<p>{core_idea}</p>"},
        {"step_number": 4, "title": "4. How it works", "content": f"<p>{how_works}</p>"}
    ]
    
    # Step 5 Visual
    sec_5 = {"step_number": 5, "title": "5. Visual explanation", "content": "<p>Visual Architecture & Mechanics:</p>"}
    if "diagram" in visual_dict:
        sec_5["diagram"] = visual_dict["diagram"]
    elif "comparison" in visual_dict:
        sec_5["comparison"] = visual_dict["comparison"]
    elif "callout" in visual_dict:
        sec_5["callout"] = visual_dict["callout"]
    elif "animation" in visual_dict:
        sec_5["animation"] = visual_dict["animation"]
    sections.append(sec_5)
    
    # Step 6 C++ code
    sections.append({
        "step_number": 6, "title": "6. C++ implementation", "content": "<p>Complete Production C++20 Implementation:</p>",
        "code_example": {"filename": code_filename, "code": code_content}
    })
    # Step 7-14
    sections.append({"step_number": 7, "title": "7. Code walkthrough", "content": f"<p>{walkthrough}</p>"})
    sections.append({"step_number": 8, "title": "8. Real-world example", "content": f"<p>{real_world}</p>"})
    sections.append({"step_number": 9, "title": "9. When to use", "content": f"<p>{when_use}</p>"})
    sections.append({"step_number": 10, "title": "10. When NOT to use", "content": f"<p>{when_not_use}</p>"})
    sections.append({"step_number": 11, "title": "11. Advantages", "content": f"<p>{advantages}</p>"})
    sections.append({"step_number": 12, "title": "12. Disadvantages", "content": f"<p>{disadvantages}</p>"})
    sections.append({"step_number": 13, "title": "13. Variations / Types", "content": f"<p>{variations}</p>"})
    sections.append({"step_number": 14, "title": "14. Common mistakes", "content": f"<p>{mistakes}</p>"})
    sections.append({"step_number": 15, "title": "15. Interview questions", "content": f"<p><strong>Q:</strong> {q_text}</p>"})
    sections.append({"step_number": 16, "title": "16. Interview answer", "content": f"<p><strong>Answer:</strong> {a_text}</p>"})
    
    # Step 17 Practice
    sections.append({
        "step_number": 17, "title": "17. Practice problem", "content": f"<p>{practice_stmt}</p>",
        "practice": {
            "title": practice_title,
            "problemStatement": practice_stmt,
            "requirements": ["Production C++20 code", "Adhere to design principles"],
            "constraints": ["Zero memory leaks"],
            "hint": "Focus on separation of responsibilities.",
            "expectedEntities": [{"name": practice_title, "responsibility": "Encapsulates problem domain."}],
            "referenceCode": {"filename": "practice_sol.cpp", "code": practice_code}
        }
    })
    
    # Step 18 Summary
    sections.append({"step_number": 18, "title": "18. Summary", "content": f"<p>Mastering {title} is essential for robust Low-Level System Design.</p>"})
    
    return {
        "id": topic_id,
        "title": title,
        "description": desc,
        "sections": sections
    }

# ==============================================================================
# MODULE 07: Object Modeling
# ==============================================================================
mod_07 = {
    "module_id": "07",
    "title": "Object Modeling & Domain Discovery",
    "level": "Intermediate",
    "category": "Modeling",
    "description": "Techniques for mapping ambiguous problem statements into tangible domain entities, immutable value objects, CRC responsibility cards, and low coupling.",
    "topics": [
        make_18_step_topic(
            "entities-vs-value-objects",
            "Entities vs Value Objects",
            "Differentiating between stateful entities with distinct identities and immutable value objects.",
            "An <strong>Entity</strong> is an object defined by its unique identity that runs through time (e.g. User ID, Bank Account Number). A <strong>Value Object</strong> is defined purely by its attributes and has no identity (e.g. Money, DateRange, Address).",
            "Treating everything as an entity creates complex mutable state graphs. Value objects simplify reasoning because they are completely immutable.",
            "If two objects have identical attributes and are interchangeable, they are Value Objects (e.g. two $10 bills). If they have the same attributes but represent different real-world items, they are Entities (e.g. two twins with different SSNs).",
            "Entities maintain mutable state protected by invariants. Value objects are initialized in the constructor, have all members marked const, and return new instances upon modification.",
            {"comparison": {
                "title": "Entities vs Value Objects Matrix",
                "columns": ["Dimension", "Entity", "Value Object"],
                "rows": [
                    ["Identity", "Unique ID (UUID / Int)", "No identity (Equality by all fields)"],
                    ["Mutability", "Mutable via domain methods", "100% Immutable"],
                    ["Lifecycle", "Long-lived across system state", "Transient, easily created/discarded"],
                    ["C++ Representation", "class User with private ID", "class Money { const double amt; const string curr; };"]
                ]
            }},
            "entity_vs_value_obj.cpp",
            """#include <iostream>
#include <string>

// Value Object: Immutable Address
class Address {
public:
    const std::string street;
    const std::string city;
    const std::string zipCode;

    Address(std::string s, std::string c, std::string z)
        : street(std::move(s)), city(std::move(c)), zipCode(std::move(z)) {}

    bool operator==(const Address& other) const noexcept {
        return street == other.street && city == other.city && zipCode == other.zipCode;
    }
};

// Domain Entity: User with unique ID
class User {
private:
    const std::string userId; // Unique Identity
    std::string name;
    Address homeAddress;      // Value Object

public:
    User(std::string id, std::string n, Address addr)
        : userId(std::move(id)), name(std::move(n)), homeAddress(std::move(addr)) {}

    void relocate(Address newAddress) {
        homeAddress = std::move(newAddress);
    }
};""",
            "Address is immutable with value-based equality; User maintains unique identity.",
            "E-commerce order shipping addresses vs User account entities.",
            "Use Value Objects for measurements, coordinates, and currencies. Use Entities for users, orders, and products.",
            "Do not make Entities immutable if their state naturally evolves over time.",
            "Eliminates concurrency race conditions on value objects; clarifies domain boundaries.",
            "Requires creating new instances when updating value objects.",
            "DDD Aggregates, Identity vs Attribute comparison.",
            "Giving value objects mutable setter methods.",
            "What is the difference between entity equality and value object equality?",
            "Entity equality compares unique IDs (e.g. user1.id == user2.id). Value object equality compares all internal attributes (e.g. addr1.street == addr2.street && addr1.zip == addr2.zip).",
            "GeoCoordinate Value Object",
            "Implement an immutable GeoCoordinate value object validating latitude (-90 to +90) and longitude (-180 to +180).",
            "class GeoCoordinate { public: const double lat, lon; GeoCoordinate(double la, double lo): lat(la), lon(lo) {} };"
        ),
        make_18_step_topic(
            "identifying-responsibilities",
            "CRC Cards & Identifying Responsibilities",
            "Class-Responsibility-Collaboration (CRC) technique to identify domain boundaries.",
            "<strong>CRC Cards</strong> (Class, Responsibility, Collaborators) are an index-card brainstorming technique to map classes, their obligations, and their helper partners.",
            "Prevents giant God classes by bounding the responsibilities of each class before writing a single line of code.",
            "Every class answers two questions: What do I know? (State) and What do I do? (Behavior).",
            "Write candidate classes on 3x5 cards. List responsibilities on the left, collaborating classes on the right.",
            {"callout": {"type": "tip", "title": "CRC Structure", "text": "Class: ParkingLot\\nResponsibilities: Manage spot allocation, Calculate total revenue\\nCollaborators: ParkingFloor, ParkingSpot, PricingStrategy"}},
            "crc_parking_lot.cpp",
            """#include <vector>
#include <memory>
class ParkingSpot {};
class PricingStrategy {};
class ParkingLot {
    std::vector<std::unique_ptr<ParkingSpot>> spots; // Collaborator
    std::shared_ptr<PricingStrategy> pricing;         // Collaborator
public:
    void parkVehicle();
    double calculateFee();
};""",
            "Shows state knowledge and behavioral responsibilities decoupled into collaborators.",
            "System design interviews for Parking Lot, Elevator, and Ride Sharing.",
            "Use during the first 10 minutes of an interview to decompose requirements.",
            "Do not skip directly to code without bounding responsibilities.",
            "High cohesion and clear division of labor.",
            "Informal; requires translation to formal UML.",
            "CRC Brainstorming, Responsibility-Driven Design (RDD).",
            "Assigning 20+ responsibilities to a single class.",
            "What is the goal of CRC cards in an LLD interview?",
            "To quickly identify the core noun entities, their verbs (responsibilities), and how they pass messages to collaborating classes.",
            "Library Management CRC",
            "Model Library, Book, and Member responsibilities.",
            "class Book {}; class Member {}; class Library { std::vector<Book> books; };"
        ),
        make_18_step_topic(
            "domain-invariants-boundaries",
            "Domain Invariants & Boundary Design",
            "Enforcing business invariants and defining Aggregate Roots in domain modeling.",
            "<strong>Domain Invariants</strong> are business rules that must ALWAYS hold true throughout the lifetime of an object (e.g. Account balance cannot drop below -$500 overdraft limit).",
            "Guarantees that database records and memory state are never corrupted by invalid concurrent operations.",
            "An <strong>Aggregate Root</strong> is the single gateway entity responsible for defending invariants for an entire cluster of child objects (e.g. Order defends OrderItems).",
            "Constructor verifies invariants upon creation; public mutating methods verify invariants before changing state.",
            {"callout": {"type": "important", "title": "Aggregate Boundary", "text": "External code must NEVER mutate OrderItem directly. External code asks Order: order.addItem(item), and Order verifies max order limits!"}},
            "aggregate_order_boundary.cpp",
            """#include <vector>
#include <string>
#include <stdexcept>

class OrderItem {
public:
    std::string productId;
    int quantity;
    double price;
    OrderItem(std::string id, int qty, double p) : productId(std::move(id)), quantity(qty), price(p) {}
};

// Order is the Aggregate Root guarding invariants!
class OrderAggregate {
private:
    std::vector<OrderItem> items;
    double totalAmount{0.0};
    static constexpr int MAX_ITEMS = 50;

public:
    void addItem(const std::string& prodId, int qty, double price) {
        if (items.size() >= MAX_ITEMS) {
            throw std::runtime_error("Invariant Violation: Max items per order exceeded!");
        }
        if (qty <= 0 || price < 0.0) {
            throw std::invalid_argument("Invalid quantity or price");
        }
        items.emplace_back(prodId, qty, price);
        totalAmount += qty * price;
    }

    [[nodiscard]] double getTotal() const noexcept { return totalAmount; }
};""",
            "OrderAggregate strictly guards item count and non-negative pricing invariants.",
            "E-commerce carts, banking ledger aggregates, flight seat reservation boundaries.",
            "Use Aggregate Roots whenever multiple objects have interdependent invariants.",
            "Do not bypass aggregate roots with direct child setters.",
            "Bulletproof consistency and transactional integrity.",
            "Slight overhead routing calls through the aggregate root.",
            "DDD Aggregates, Invariant Guards, Preconditions/Postconditions.",
            "Exposing internal mutable collections to callers.",
            "What is an Aggregate Root in Low-Level Design?",
            "An Aggregate Root is a master domain entity that external objects interact with. It encapsulates a cluster of associated objects and strictly defends all internal business invariants.",
            "Bank Account Overdraft Guard",
            "Implement a BankAccount that enforces a strict $500 overdraft limit invariant.",
            "class BankAccount { double bal{0}; public: void withdraw(double a) { if(bal - a < -500) throw std::runtime_error('Overdraft'); bal -= a; } };"
        ),
        make_18_step_topic(
            "cohesion-and-coupling",
            "High Cohesion & Low Coupling",
            "The twin metrics of software quality: maximizing internal focus and minimizing inter-module dependencies.",
            "<strong>Cohesion</strong> measures how focused and related the responsibilities of a single module are. <strong>Coupling</strong> measures how tightly dependent different modules are on each other.",
            "High Cohesion + Low Coupling = Maintainable, reusable, easily testable architecture.",
            "Goal: <strong>High Cohesion</strong> (a class does one thing exceptionally well) and <strong>Low Coupling</strong> (classes communicate through abstract interfaces with minimal direct knowledge).",
            "Reduce coupling using Dependency Injection and interfaces. Increase cohesion by splitting disparate responsibilities into separate classes.",
            {"comparison": {
                "title": "Cohesion vs Coupling Spectrum",
                "columns": ["Property", "Ideal State", "Bad State", "Remedy"],
                "rows": [
                    ["Cohesion", "High (Focused, single purpose)", "Low (God class, scattered features)", "Split class using SRP"],
                    ["Coupling", "Low (Decoupled via interfaces)", "High (Direct concrete dependencies)", "Use Dependency Injection (DIP)"]
                ]
            }},
            "cohesion_coupling_demo.cpp",
            """#include <iostream>
#include <memory>
// High Cohesion: Focused solely on calculation
class InvoiceCalculator {
public:
    double computeTotal(double subtotal, double taxRate) const noexcept {
        return subtotal * (1.0 + taxRate);
    }
};

// Low Coupling: Communicates via abstract interface
class IPaymentService { public: virtual ~IPaymentService() = default; virtual void pay(double) = 0; };
class CheckoutCoordinator {
    InvoiceCalculator calc; // High Cohesion helper
    std::shared_ptr<IPaymentService> payment; // Low Coupling dependency
public:
    CheckoutCoordinator(std::shared_ptr<IPaymentService> p) : payment(std::move(p)) {}
    void complete(double amount) {
        double finalPrice = calc.computeTotal(amount, 0.08);
        payment->pay(finalPrice);
    }
};""",
            "Combines high internal calculation cohesion with low interface payment coupling.",
            "High-scale distributed systems and enterprise microservices.",
            "Evaluate every new class against cohesion and coupling metrics.",
            "Do not over-decouple into thousands of 1-line classes (extremes cause complexity).",
            "Maximum maintainability, testability, and parallel team development.",
            "Requires careful interface design up front.",
            "Content coupling, Common coupling, Control coupling, Stamp coupling, Data coupling.",
            "Tight coupling to concrete third-party SDKs.",
            "How do Dependency Injection and Interfaces achieve low coupling?",
            "They replace concrete type dependencies with abstract contracts, allowing modules to be developed, tested, and replaced without modifying dependent code.",
            "Decouple Order and Email",
            "Decouple Order from direct SMTP email using an INotifier interface.",
            "class INotifier { public: virtual ~INotifier() = default; virtual void send(std::string) = 0; };"
        )
    ]
}

# ==============================================================================
# MODULE 08: Core Software Design Principles
# ==============================================================================
mod_08 = {
    "module_id": "08",
    "title": "Core Software Design Principles",
    "level": "Intermediate",
    "category": "Principles",
    "description": "Essential software design heuristics: DRY, KISS, YAGNI, Law of Demeter (Least Knowledge), Separation of Concerns, and Encapsulating What Varies.",
    "topics": [
        make_18_step_topic(
            "dry-kiss-yagni",
            "DRY, KISS, and YAGNI",
            "Don't Repeat Yourself, Keep It Simple Stupid, and You Aren't Gonna Need It.",
            "<strong>DRY</strong>: Every piece of knowledge must have a single authoritative representation. <strong>KISS</strong>: Simple designs are easier to maintain than clever complex designs. <strong>YAGNI</strong>: Do not implement features until they are actually needed.",
            "Over-engineering and code duplication are the two primary causes of technical debt and maintenance nightmares.",
            "Write the simplest code that solves today's requirements. Extract common logic to prevent copy-paste bugs.",
            "Avoid speculative generality (e.g. building a multi-tenant plugin engine when only single-user support is required).",
            {"callout": {"type": "tip", "title": "YAGNI Rule", "text": "Always implement things when you actually need them, never when you just foresee that you may need them!"}},
            "dry_kiss_yagni_demo.cpp",
            """#include <iostream>
#include <string>
#include <regex>

// KISS & DRY: Single authoritative email validator
class ValidationUtils {
public:
    static bool isValidEmail(const std::string& email) {
        // Simple, readable regex check
        const std::regex pattern("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\\\.[a-zA-Z0-9-.]+$");
        return std::regex_match(email, pattern);
    }
};""",
            "Reusable validation logic avoiding duplicate regexes across registration and profile updates.",
            "Every production software development lifecycle.",
            "Apply KISS and YAGNI constantly during system design interviews.",
            "Do not over-apply DRY to coincidentally similar code that serves different domain purposes.",
            "Clean, readable, concise code with minimal bugs.",
            "Premature DRY can create artificial coupling between distinct business domains.",
            "DRY (Knowledge duplication vs accidental duplication).",
            "Building complex generic abstractions for features that never get used.",
            "When should you violate DRY?",
            "When two pieces of code look identical today but belong to different business domains and will evolve for completely different reasons (accidental duplication).",
            "DRY Pricing Calculation",
            "Refactor duplicated tax calculation into a shared helper.",
            "class Tax { public: static double withTax(double a) { return a * 1.08; } };"
        ),
        make_18_step_topic(
            "law-of-demeter",
            "Law of Demeter (Principle of Least Knowledge)",
            "A method should only talk to its immediate friends, avoiding long train-wreck call chains.",
            "The <strong>Law of Demeter (LoD)</strong> states that a method of an object may only call methods of: itself, its parameters, objects it creates, or its direct component members. Avoid <code>a.getB().getC().getD().doSomething()</code>.",
            "Train-wreck calls create brittle coupling: changing class C breaks class A even though class A only wanted something from D.",
            "<em>'Tell, Don't Ask.'</em> Tell the immediate friend to perform the operation instead of navigating through its internal object graph.",
            "Instead of <code>customer.getWallet().getCard().charge()</code>, write <code>customer.charge(amount)</code>.",
            {"callout": {"type": "trap", "title": "Train-Wreck Anti-Pattern", "text": "user.getProfile().getAddress().getGeo().getCoordinates(); // Violates Law of Demeter! Coupling to 4 nested classes!"}},
            "law_of_demeter_demo.cpp",
            """#include <iostream>

class Wallet {
    double money{100.0};
public:
    bool deduct(double amt) {
        if (money >= amt) { money -= amt; return true; }
        return false;
    }
};

class Customer {
    Wallet wallet; // Private internal component
public:
    // Follows Law of Demeter: Encapsulates wallet interaction
    bool makePayment(double amount) {
        return wallet.deduct(amount);
    }
};

class StoreRegister {
public:
    void checkout(Customer& customer, double total) {
        // Law of Demeter: Tells customer to pay, doesn't reach inside wallet!
        if (customer.makePayment(total)) {
            std::cout << "Payment approved!\\n";
        }
    }
};""",
            "StoreRegister communicates only with Customer, remaining ignorant of Wallet internals.",
            "Microservice domain boundaries and object-oriented encapsulation.",
            "Use LoD to minimize ripple effects when internal object structures change.",
            "Do not apply LoD to fluent builders (e.g. <code>QueryBuilder.select().from()</code> where each method returns *this).",
            "Loose coupling and high maintainability.",
            "May require creating forwarding methods on container classes.",
            "Tell Don't Ask, Method forwarding.",
            "Reaching into nested getters across multiple layers.",
            "Why is <code>a.getB().getC().doAction()</code> a violation of the Law of Demeter?",
            "Because class A now directly depends on the internal navigation structure of B and C. If B's internal representation changes, class A breaks.",
            "Refactor PaperBoy LoD",
            "Refactor PaperBoy taking money from Customer's Wallet into Customer.pay(amount).",
            "class Customer { Wallet w; public: bool pay(double a) { return w.deduct(a); } };"
        ),
        make_18_step_topic(
            "separation-of-concerns",
            "Separation of Concerns & Modularity",
            "Dividing a software application into distinct features that overlap in functionality as little as possible.",
            "<strong>Separation of Concerns (SoC)</strong> is the software design principle of breaking an architecture into distinct sections, where each section addresses a separate concern (e.g. Presentation, Business Logic, Persistence).",
            "Mixing database queries, UI rendering, and business calculations in a single function makes code unmaintainable.",
            "Each module has a dedicated role: Model represents business state, View renders UI, Controller coordinates user interaction.",
            "Organize code into clear architectural tiers (MVC, Clean Architecture, Hexagonal Ports & Adapters).",
            {"callout": {"type": "tip", "title": "Architectural Tiers", "text": "UI Layer -> Business Service Layer -> Data Access Layer -> Storage"}},
            "soc_layered_arch.cpp",
            """#include <iostream>
#include <string>

// Tier 1: Domain Entity
struct Account { std::string id; double balance; };

// Tier 2: Data Access Layer
class AccountDao {
public:
    Account findAccount(const std::string& id) { return Account{id, 500.0}; }
};

// Tier 3: Business Logic Layer
class BankingService {
    AccountDao dao;
public:
    void transfer(const std::string& fromId, const std::string& toId, double amount) {
        Account from = dao.findAccount(fromId);
        std::cout << "[Service] Validated transfer of $" << amount << " from " << from.id << "\\n";
    }
};""",
            "Clean separation between database retrieval and business transfer validation.",
            "Enterprise web backends, financial trading systems, desktop applications.",
            "Use layered architecture in all non-trivial systems.",
            "Do not create excessive tiers for simple CRUD utilities.",
            "Independent team development, testability, and technology swap freedom.",
            "Requires passing data transfer objects across layer boundaries.",
            "MVC, MVP, MVVM, Clean Architecture.",
            "Writing raw SQL queries inside UI click event handlers.",
            "How does Separation of Concerns relate to Single Responsibility Principle?",
            "SoC is a high-level system architectural principle (separating UI, logic, data layers), while SRP is the class-level object-oriented realization of SoC.",
            "Layered Weather Architecture",
            "Structure WeatherModel, WeatherFetcher, and WeatherDisplay classes.",
            "class WeatherModel {}; class WeatherFetcher {}; class WeatherDisplay {};"
        ),
        make_18_step_topic(
            "encapsulate-variation",
            "Encapsulate What Varies & Favor Immutability",
            "Identify the aspects of your application that vary and separate them from what stays the same.",
            "<strong>Encapsulate What Varies</strong> is a core design heuristic: identify the parts of a system that change frequently and encapsulate them behind an interface to protect stable parts.",
            "Prevents constant churn and regression testing across the entire system when business rules change.",
            "Isolate the moving parts behind interfaces (Strategy / Factory patterns) and make static parts immutable.",
            "Extract dynamic algorithms into polymorphic classes. Mark unchanged state <code>const</code>.",
            {"callout": {"type": "tip", "title": "Core Heuristic", "text": "Take what varies and 'encapsulate' it so it won't affect the rest of your code!"}},
            "encapsulate_variation_pricing.cpp",
            """#include <iostream>
#include <memory>

// What varies: Pricing calculation algorithms
class IPricingRule { public: virtual ~IPricingRule() = default; virtual double calculate(double base) const = 0; };
class PeakHoursPricing : public IPricingRule { public: double calculate(double b) const override { return b * 1.5; } };
class OffPeakPricing : public IPricingRule { public: double calculate(double b) const override { return b * 0.9; } };

// What stays the same: Ride dispatch workflow
class RideBooking {
    std::unique_ptr<IPricingRule> pricingRule;
public:
    explicit RideBooking(std::unique_ptr<IPricingRule> rule) : pricingRule(std::move(rule)) {}
    double getFare(double base) const { return pricingRule->calculate(base); }
};""",
            "Pricing volatility is encapsulated in strategy classes; RideBooking workflow stays stable.",
            "Ride-sharing surge pricing, airline ticketing, dynamic insurance underwriting.",
            "Use whenever business policies, algorithms, or integrations vary frequently.",
            "Do not encapsulate aspects that are guaranteed never to change.",
            "Protects core workflow stability; enables zero-risk runtime algorithm swapping.",
            "Increases class count.",
            "Strategy Pattern, Policy-based Design, Immutability.",
            "Hardcoding varying calculation rules inside main business classes.",
            "How does 'Encapsulate What Varies' lead directly to the Strategy Design Pattern?",
            "When algorithm variations are extracted into separate classes implementing a common interface, that structure IS the Strategy Design Pattern.",
            "Tax Rule Encapsulation",
            "Encapsulate state-by-state tax calculation variation.",
            "class ITaxRule { public: virtual ~ITaxRule() = default; virtual double tax(double) = 0; };"
        )
    ]
}

write_module(mod_07)
write_module(mod_08)
