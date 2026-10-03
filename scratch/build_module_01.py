import json
from pathlib import Path

content_dir = Path("content")
content_dir.mkdir(exist_ok=True)

module_01_data = {
    "module_id": "01",
    "title": "Programming Foundations for LLD",
    "level": "Beginner",
    "category": "Foundations",
    "description": "Master essential C++ concepts required for object-oriented system design: Classes, Objects, Constructors, RAII, Rule of 0/3/5, Move Semantics, and Smart Pointers.",
    "topics": [
        # -------------------------------------------------------------
        # 1. Classes & Objects
        # -------------------------------------------------------------
        {
            "id": "classes-and-objects",
            "title": "Classes & Objects in C++",
            "description": "Fundamental building blocks of object-oriented design in C++, memory layout, and stack vs heap object lifetimes.",
            "sections": [
                {
                    "step_number": 1,
                    "title": "1. What is it?",
                    "content": "<p>A <strong>Class</strong> is a user-defined blueprint or data type that encapsulates data members (state) and member functions (behavior) into a cohesive unit. An <strong>Object</strong> is a concrete, tangible instance of that class instantiated in memory.</p>"
                },
                {
                    "step_number": 2,
                    "title": "2. Why do we need it?",
                    "content": "<p>Without classes, procedural programming relies on disconnected primitive variables and scattered functions. Low-Level Design demands cohesive domain models where business invariants (e.g., a bank account balance cannot be negative without an overdraft limit) are tightly protected and coupled to their mutating behaviors.</p>"
                },
                {
                    "step_number": 3,
                    "title": "3. Core idea",
                    "content": "<p>Bind state and behavior together under strict access control. The object guarantees that it is always in a valid state from the moment its constructor finishes until its destructor runs.</p>"
                },
                {
                    "step_number": 4,
                    "title": "4. How it works",
                    "content": "<p>In C++, a class definition does not allocate memory for data. When an object is instantiated on the <strong>stack</strong> (<code>Car myCar;</code>) or on the <strong>heap</strong> (<code>auto carPtr = std::make_unique&lt;Car&gt;();</code>), memory is laid out for all non-static member variables according to compiler alignment and padding rules. Member functions exist once in the code/text segment and receive an implicit pointer <code>this</code> pointing to the invoking instance.</p>"
                },
                {
                    "step_number": 5,
                    "title": "5. Visual explanation",
                    "content": "<p>UML Class representation and memory layout representation of a Car object with its encapsulated state and behavior:</p>",
                    "diagram": {
                        "title": "Car Class & Object Layout",
                        "classes": [
                            {
                                "name": "Car",
                                "attributes": [
                                    {"visibility": "-", "name": "vin", "type": "std::string"},
                                    {"visibility": "-", "name": "speed", "type": "double"},
                                    {"visibility": "-", "name": "isRunning", "type": "bool"}
                                ],
                                "methods": [
                                    {"visibility": "+", "name": "start", "params": "", "returnType": "void"},
                                    {"visibility": "+", "name": "accelerate", "params": "double amount", "returnType": "void"},
                                    {"visibility": "+", "name": "getSpeed", "params": "", "returnType": "double"}
                                ]
                            }
                        ],
                        "relationships": []
                    }
                },
                {
                    "step_number": 6,
                    "title": "6. C++ implementation",
                    "content": "<p>Here is the complete, robust C++20 implementation of a domain <code>Car</code> entity with invariant enforcement:</p>",
                    "code_example": {
                        "filename": "car_entity.cpp",
                        "code": """#include <iostream>
#include <string>
#include <stdexcept>

class Car {
private:
    std::string vin;
    double speed{0.0};
    bool isRunning{false};

public:
    // Parameterized constructor enforcing domain invariant
    explicit Car(std::string vehicleId) : vin(std::move(vehicleId)) {
        if (vin.empty()) {
            throw std::invalid_argument("VIN cannot be empty");
        }
    }

    void start() {
        if (isRunning) {
            std::cout << "[Car " << vin << "] Engine is already running.\\n";
            return;
        }
        isRunning = true;
        std::cout << "[Car " << vin << "] Engine ignited.\\n";
    }

    void accelerate(double amount) {
        if (!isRunning) {
            throw std::logic_error("Cannot accelerate while engine is off");
        }
        if (amount < 0.0) {
            throw std::invalid_argument("Acceleration delta must be positive");
        }
        speed += amount;
        std::cout << "[Car " << vin << "] Accelerating to " << speed << " km/h.\\n";
    }

    [[nodiscard]] double getSpeed() const noexcept {
        return speed;
    }

    [[nodiscard]] bool getIsRunning() const noexcept {
        return isRunning;
    }
};

int main() {
    Car sedan{"1HGCR2F83HA000000"};
    sedan.start();
    sedan.accelerate(45.5);
    std::cout << "Current Speed: " << sedan.getSpeed() << " km/h\\n";
    return 0;
}"""
                    }
                },
                {
                    "step_number": 7,
                    "title": "7. Code walkthrough",
                    "content": "<p><strong>Line 11 (explicit constructor):</strong> Marking single-argument constructors <code>explicit</code> prevents accidental implicit conversions from string literals.<br><strong>Lines 24-34 (accelerate):</strong> Enforces domain logic preconditions: an engine must be running before speed changes occur.<br><strong>Line 37 ([[nodiscard]] & const):</strong> Ensures getters never mutate object state and warns if return values are discarded.</p>"
                },
                {
                    "step_number": 8,
                    "title": "8. Real-world example",
                    "content": "<p>In an automotive telematics system or ride-sharing fleet manager (Uber/Lyft), every vehicle is represented as a stateful <code>Vehicle</code> object tracking GPS coordinates, occupancy, engine diagnostics, and operational status.</p>"
                },
                {
                    "step_number": 9,
                    "title": "9. When to use",
                    "content": "<p>Use classes whenever you need to model domain entities that have identity, internal state, and strict business invariants that must be guarded from external corruption.</p>"
                },
                {
                    "step_number": 10,
                    "title": "10. When NOT to use",
                    "content": "<p>Do not use full classes with private getters/setters for simple Passive Data Objects (Plain Old Data / DTOs). Use <code>struct</code> with public members when data has no invariants (e.g., a simple 2D Coordinate <code>struct Point { double x; double y; };</code>).</p>"
                },
                {
                    "step_number": 11,
                    "title": "11. Advantages",
                    "content": "<ul style='margin-left: 1.25rem; line-height: 1.7;'><li><strong>Encapsulation:</strong> Internal representation can change without breaking client code.</li><li><strong>Invariant Safety:</strong> Constructor guarantees valid state; methods protect valid state.</li><li><strong>Polymorphism Readiness:</strong> Can be extended into hierarchies or interface contracts.</li></ul>"
                },
                {
                    "step_number": 12,
                    "title": "12. Disadvantages",
                    "content": "<ul style='margin-left: 1.25rem; line-height: 1.7;'><li>Small memory overhead due to alignment and padding.</li><li>Can lead to over-engineering if applied to trivial POD data transfer objects.</li></ul>"
                },
                {
                    "step_number": 13,
                    "title": "13. Variations / Types",
                    "content": "<ul style='margin-left: 1.25rem; line-height: 1.7;'><li><strong>Entity Classes:</strong> Defined by a unique identifier (e.g. <code>User</code>, <code>Car</code>, <code>Order</code>).</li><li><strong>Value Objects:</strong> Defined solely by their attributes (e.g. <code>Money</code>, <code>Address</code>, <code>DateRange</code>).</li><li><strong>Service Classes:</strong> Stateless operation coordinators (e.g. <code>PaymentGatewayClient</code>).</li></ul>"
                },
                {
                    "step_number": 14,
                    "title": "14. Common mistakes",
                    "content": "<p>Creating <strong>'Anemic Domain Models'</strong> (classes that are just public getters and setters with zero logic) while business logic is scattered across giant controller procedures. This completely defeats object-oriented encapsulation.</p>",
                    "callout": {
                        "type": "trap",
                        "title": "Interview Trap: Class vs Struct in C++",
                        "text": "In C++, the ONLY technical difference between class and struct is default visibility: class members are private by default, struct members are public by default. Conventionally, use struct for data bundles with no invariants and class for domain entities."
                    }
                },
                {
                    "step_number": 15,
                    "title": "15. Interview questions",
                    "content": "<p><strong>Q1:</strong> What happens to object layout in memory if a class adds a virtual function?<br><strong>Q2:</strong> Why should single-parameter constructors almost always be marked <code>explicit</code>?</p>"
                },
                {
                    "step_number": 16,
                    "title": "16. Interview answer",
                    "content": "<p><strong>Answer:</strong> Adding a virtual function introduces a hidden Virtual Table Pointer (<code>vptr</code>) at the beginning of the object layout (typically 8 bytes on a 64-bit architecture), increasing <code>sizeof(Object)</code>. Marking constructors <code>explicit</code> prevents hazardous implicit type conversions (e.g. passing a string to a function expecting a <code>Car</code> implicitly calling <code>Car(string)</code> without warning).</p>"
                },
                {
                    "step_number": 17,
                    "title": "17. Practice problem",
                    "content": "<p>Design an immutable <code>Money</code> Value Object representing an amount and 3-letter currency code (e.g., 'USD', 'EUR') that enforces non-negative amounts, validates currency codes, and prevents arithmetic between mismatched currencies.</p>",
                    "practice": {
                        "title": "Immutable Money Value Object",
                        "problemStatement": "Implement a C++ Money class that enforces strict invariant validation, supports safe addition with matching currency, and prevents accidental currency mismatch bugs.",
                        "requirements": [
                            "Amount must be non-negative (>= 0.0)",
                            "Currency code must be exactly 3 uppercase letters (ISO 4217)",
                            "Adding two Money objects with different currencies must throw std::invalid_argument",
                            "Money objects must be completely immutable once constructed"
                        ],
                        "constraints": [
                            "No raw heap pointers",
                            "Must be const-correct"
                        ],
                        "hint": "Make member variables const, validate in constructor, and return a new Money instance from the add() method.",
                        "expectedEntities": [
                            {"name": "Money", "responsibility": "Encapsulates immutable currency amount and currency validation logic."}
                        ],
                        "referenceCode": {
                            "filename": "money_solution.cpp",
                            "code": """#include <iostream>
#include <string>
#include <stdexcept>

class Money {
private:
    const double amount;
    const std::string currency;

    static bool isValidCurrency(const std::string& curr) {
        if (curr.length() != 3) return false;
        for (char c : curr) {
            if (c < 'A' || c > 'Z') return false;
        }
        return true;
    }

public:
    Money(double amt, std::string curr) : amount(amt), currency(std::move(curr)) {
        if (amount < 0.0) throw std::invalid_argument("Amount cannot be negative");
        if (!isValidCurrency(currency)) throw std::invalid_argument("Invalid 3-letter ISO currency");
    }

    [[nodiscard]] double getAmount() const noexcept { return amount; }
    [[nodiscard]] const std::string& getCurrency() const noexcept { return currency; }

    [[nodiscard]] Money add(const Money& other) const {
        if (this->currency != other.currency) {
            throw std::invalid_argument("Cannot add different currencies: " + currency + " vs " + other.currency);
        }
        return Money(this->amount + other.amount, this->currency);
    }
};"""
                        }
                    }
                },
                {
                    "step_number": 18,
                    "title": "18. Summary",
                    "content": "<p>Classes are the core encapsulation mechanism in C++. By combining state with behavior, enforcing preconditions in constructors, and maintaining const-correctness, you lay the foundation for robust Low-Level System Design.</p>"
                }
            ]
        },

        # -------------------------------------------------------------
        # 2. Constructors & Destructors
        # -------------------------------------------------------------
        {
            "id": "constructors-destructors",
            "title": "Constructors & Destructors",
            "description": "Object initialization lifecycles, member initializer lists, delegating constructors, explicit specifiers, and deterministic destruction.",
            "sections": [
                {
                    "step_number": 1,
                    "title": "1. What is it?",
                    "content": "<p>A <strong>Constructor</strong> is a special member function invoked automatically when an object is instantiated to initialize its state. A <strong>Destructor</strong> is invoked automatically when the object goes out of scope or is deleted, releasing any acquired system resources.</p>"
                },
                {
                    "step_number": 2,
                    "title": "2. Why do we need it?",
                    "content": "<p>In languages without deterministic destructors (like Java or Python), resource cleanup relies on garbage collection or explicit <code>close()</code> calls that programmers easily forget. In C++, constructors guarantee valid initialization, and destructors guarantee leak-free, deterministic resource reclamation.</p>"
                },
                {
                    "step_number": 3,
                    "title": "3. Core idea",
                    "content": "<p>Guarantee that an object never exists in an uninitialized or corrupt state, and guarantee that resources (files, sockets, mutex locks, heap memory) are released automatically when the object's lifetime ends.</p>"
                },
                {
                    "step_number": 4,
                    "title": "4. How it works",
                    "content": "<p>Constructors initialize base classes first, then member variables in the <strong>exact order of declaration in the class definition</strong> (regardless of the order in the initializer list), and finally execute the constructor body. Destructors run in the <strong>exact reverse order</strong>.</p>"
                },
                {
                    "step_number": 5,
                    "title": "5. Visual explanation",
                    "content": "<p>Construction vs Destruction Order Lifecycle:</p>",
                    "callout": {
                        "type": "important",
                        "title": "Construction vs Destruction Order",
                        "text": "Construction: Base Class -> Member 1 -> Member 2 -> Constructor Body.\\nDestruction: Destructor Body -> Member 2 -> Member 1 -> Base Class."
                    }
                },
                {
                    "step_number": 6,
                    "title": "6. C++ implementation",
                    "content": "<p>Demonstrating Member Initializer Lists, Delegating Constructors, and Destructors:</p>",
                    "code_example": {
                        "filename": "constructors_demo.cpp",
                        "code": """#include <iostream>
#include <string>

class DatabaseConnection {
private:
    std::string host;
    int port;
    bool isConnected{false};

public:
    // Primary Parameterized Constructor with Member Initializer List
    DatabaseConnection(std::string dbHost, int dbPort)
        : host(std::move(dbHost)), port(dbPort) {
        connect();
    }

    // Delegating Constructor: reuses primary constructor with default port
    explicit DatabaseConnection(std::string dbHost)
        : DatabaseConnection(std::move(dbHost), 5432) {
        std::cout << "[DatabaseConnection] Delegated to default port 5432\\n";
    }

    // Destructor: guarantees clean disconnection
    ~DatabaseConnection() {
        disconnect();
    }

private:
    void connect() {
        isConnected = true;
        std::cout << "[Connected] to " << host << ":" << port << "\\n";
    }

    void disconnect() {
        if (isConnected) {
            isConnected = false;
            std::cout << "[Disconnected] from " << host << ":" << port << "\\n";
        }
    }
};

int main() {
    {
        std::cout << "--- Entering Scope ---\\n";
        DatabaseConnection db{"postgres-primary.cluster.internal"};
        std::cout << "--- Doing work with DB ---\\n";
    } // <-- Destructor automatically runs here!
    std::cout << "--- Exited Scope ---\\n";
    return 0;
}"""
                    }
                },
                {
                    "step_number": 7,
                    "title": "7. Code walkthrough",
                    "content": "<p><strong>Lines 11-14 (Initializer List):</strong> Directly initializes <code>host</code> and <code>port</code> before entering constructor body, avoiding default construction followed by assignment.<br><strong>Lines 17-20 (Delegating Constructor):</strong> C++11 delegating constructor prevents duplicated initialization logic.<br><strong>Lines 23-25 (Destructor):</strong> Guaranteed to run when exiting scope, ensuring connection cleanup even if an exception occurs.</p>"
                },
                {
                    "step_number": 8,
                    "title": "8. Real-world example",
                    "content": "<p>Connection pools, file streams (<code>std::ifstream</code>), mutex guards (<code>std::lock_guard</code>), and OS graphics device contexts rely entirely on constructor acquisition and destructor reclamation.</p>"
                },
                {
                    "step_number": 9,
                    "title": "9. When to use",
                    "content": "<p>Always use member initializer lists for all member fields, and write a custom destructor whenever a class directly manages a native resource (file descriptor, raw pointer, mutex lock).</p>"
                },
                {
                    "step_number": 10,
                    "title": "10. When NOT to use",
                    "content": "<p>Do not write manual destructors if your class only holds standard library types and smart pointers. Rely on the <strong>Rule of Zero</strong> where the compiler-generated destructor cleans up members automatically.</p>"
                },
                {
                    "step_number": 11,
                    "title": "11. Advantages",
                    "content": "<ul style='margin-left: 1.25rem; line-height: 1.7;'><li>Guaranteed initialization without uninitialized memory garbage.</li><li>Zero risk of resource leaks upon scope exit.</li><li>Exception safety: stack unwinding automatically calls destructors of all initialized sub-objects.</li></ul>"
                },
                {
                    "step_number": 12,
                    "title": "12. Disadvantages",
                    "content": "<ul style='margin-left: 1.25rem; line-height: 1.7;'><li>Throwing exceptions inside a destructor during stack unwinding will trigger <code>std::terminate()</code> and crash the process. Destructors must be <code>noexcept</code>.</li></ul>"
                },
                {
                    "step_number": 13,
                    "title": "13. Variations / Types",
                    "content": "<ul style='margin-left: 1.25rem; line-height: 1.7;'><li><strong>Default Constructor:</strong> <code>Car() = default;</code></li><li><strong>Parameterized Constructor:</strong> <code>Car(string id, int year);</code></li><li><strong>Copy Constructor:</strong> <code>Car(const Car& other);</code></li><li><strong>Move Constructor:</strong> <code>Car(Car&& other) noexcept;</code></li><li><strong>Delegating Constructor:</strong> Calls another constructor in the same class.</li></ul>"
                },
                {
                    "step_number": 14,
                    "title": "14. Common mistakes",
                    "content": "<p>1. Assigning members inside the constructor body instead of using the initializer list (causes double initialization).<br>2. Expecting members to initialize in the order written in the constructor initializer list rather than the order declared in the class header.</p>",
                    "callout": {
                        "type": "trap",
                        "title": "Critical C++ Trap: Member Initialization Order",
                        "text": "Members are ALWAYS initialized in the exact order they are declared in the class definition, NOT the order in the initializer list. Misordering can cause undefined behavior if member B depends on member A being initialized first."
                    }
                },
                {
                    "step_number": 15,
                    "title": "15. Interview questions",
                    "content": "<p><strong>Q:</strong> What happens if an exception is thrown in the middle of a constructor? Does the object's destructor execute?</p>"
                },
                {
                    "step_number": 16,
                    "title": "16. Interview answer",
                    "content": "<p><strong>Answer:</strong> If an exception is thrown in a constructor, the object is considered to have never been fully constructed. Therefore, its destructor will <strong>NOT</strong> run. However, the destructors of all successfully constructed base classes and member variables will run in reverse order during stack unwinding.</p>"
                },
                {
                    "step_number": 17,
                    "title": "17. Practice problem",
                    "content": "<p>Write a <code>ScopedTimer</code> class whose constructor accepts a string label and records the start time using <code>std::chrono::high_resolution_clock</code>, and whose destructor automatically computes and prints elapsed time in milliseconds when exiting scope.</p>",
                    "practice": {
                        "title": "Benchmarking ScopedTimer",
                        "problemStatement": "Build a RAII ScopedTimer utility that measures elapsed execution time between construction and destruction.",
                        "requirements": [
                            "Constructor records start timestamp and takes a string label",
                            "Destructor prints duration in milliseconds",
                            "Destructor must be marked noexcept"
                        ],
                        "constraints": ["Use <chrono> header"],
                        "hint": "Store std::chrono::time_point in the constructor and calculate std::chrono::duration in the destructor.",
                        "expectedEntities": [
                            {"name": "ScopedTimer", "responsibility": "Measures scope lifetime execution duration."}
                        ],
                        "referenceCode": {
                            "filename": "scoped_timer.cpp",
                            "code": """#include <iostream>
#include <chrono>
#include <string>

class ScopedTimer {
private:
    std::string label;
    std::chrono::time_point<std::chrono::high_resolution_clock> start;

public:
    explicit ScopedTimer(std::string timerLabel)
        : label(std::move(timerLabel)), start(std::chrono::high_resolution_clock::now()) {}

    ~ScopedTimer() noexcept {
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
        std::cout << "[Timer: " << label << "] Elapsed: " << duration << " us\\n";
    }
};"""
                        }
                    }
                },
                {
                    "step_number": 18,
                    "title": "18. Summary",
                    "content": "<p>Constructors and destructors are the twin pillars of C++ memory and resource management. Leveraging initializer lists and deterministic destructors ensures robust, leak-free object design.</p>"
                }
            ]
        },

        # -------------------------------------------------------------
        # 3. Access Modifiers & Encapsulation
        # -------------------------------------------------------------
        {
            "id": "access-modifiers",
            "title": "Access Modifiers & Encapsulation",
            "description": "Information hiding via public, private, protected access specifiers, friend classes, and encapsulation boundary defense.",
            "sections": [
                {
                    "step_number": 1,
                    "title": "1. What is it?",
                    "content": "<p><strong>Access Modifiers</strong> (<code>public</code>, <code>private</code>, <code>protected</code>) control the visibility and accessibility of class members from outside code and derived subclasses.</p>"
                },
                {
                    "step_number": 2,
                    "title": "2. Why do we need it?",
                    "content": "<p>If class members are publicly accessible, any external function can directly modify internal fields into illegal states (e.g. Setting a negative account balance or resetting a state machine illegally), breaking system invariants and tightly coupling caller code to internal implementation details.</p>"
                },
                {
                    "step_number": 3,
                    "title": "3. Core idea",
                    "content": "<p>Hide internal representation details behind a minimal, stable public interface. Keep all data members <code>private</code> and provide intent-revealing member functions.</p>"
                },
                {
                    "step_number": 4,
                    "title": "4. How it works",
                    "content": "<p>Access specifiers are checked strictly at <strong>compile time</strong>. <code>public</code> members are accessible everywhere. <code>private</code> members are accessible only within the class itself and declared <code>friend</code> entities. <code>protected</code> members are accessible within the class and derived classes.</p>"
                },
                {
                    "step_number": 5,
                    "title": "5. Visual explanation",
                    "content": "<p>Visibility matrix comparison in C++:</p>",
                    "comparison": {
                        "title": "Access Specifier Visibility Matrix",
                        "columns": ["Specifier", "Inside Class", "Derived Subclass", "External World", "LLD Best Practice"],
                        "rows": [
                            ["private", "✓ Yes", "✗ No", "✗ No", "Default for ALL data members"],
                            ["protected", "✓ Yes", "✓ Yes", "✗ No", "Use sparingly for extension hooks"],
                            ["public", "✓ Yes", "✓ Yes", "✓ Yes", "Strictly for clean interface methods"]
                        ]
                    }
                },
                {
                    "step_number": 6,
                    "title": "6. C++ implementation",
                    "content": "<p>Encapsulated Bank Account with Friend Auditing Service:</p>",
                    "code_example": {
                        "filename": "encapsulation_bank.cpp",
                        "code": """#include <iostream>
#include <string>
#include <stdexcept>

class BankAccount {
private:
    std::string accountNumber;
    double balance{0.0};

    // Declare external Auditor as a friend class
    friend class AccountAuditor;

public:
    BankAccount(std::string accNum, double initialDeposit)
        : accountNumber(std::move(accNum)), balance(initialDeposit) {
        if (balance < 0.0) throw std::invalid_argument("Initial balance cannot be negative");
    }

    void deposit(double amount) {
        if (amount <= 0.0) throw std::invalid_argument("Deposit must be positive");
        balance += amount;
    }

    void withdraw(double amount) {
        if (amount <= 0.0) throw std::invalid_argument("Withdrawal must be positive");
        if (amount > balance) throw std::runtime_error("Insufficient funds");
        balance -= amount;
    }

    [[nodiscard]] double getBalance() const noexcept {
        return balance;
    }
};

class AccountAuditor {
public:
    void auditInternalLedger(const BankAccount& acc) {
        // Friend class can directly inspect private state for high-speed compliance audits
        std::cout << "[AUDIT] Account: " << acc.accountNumber << " | Exact Balance: $" << acc.balance << "\\n";
    }
};

int main() {
    BankAccount myAccount{"ACC-9921", 500.0};
    myAccount.deposit(250.0);
    myAccount.withdraw(100.0);
    
    AccountAuditor auditor;
    auditor.auditInternalLedger(myAccount);
    return 0;
}"""
                    }
                },
                {
                    "step_number": 7,
                    "title": "7. Code walkthrough",
                    "content": "<p><strong>Lines 7-8:</strong> <code>accountNumber</code> and <code>balance</code> are strictly <code>private</code>.<br><strong>Lines 11:</strong> <code>friend class AccountAuditor;</code> grants selective internal visibility without exposing members to the entire application.<br><strong>Lines 20-30:</strong> Business invariants (no negative deposits/withdrawals, no overdraft) are enforced inside the class.</p>"
                },
                {
                    "step_number": 8,
                    "title": "8. Real-world example",
                    "content": "<p>E-commerce checkout engines encapsulate shopping cart items and pricing logic so external UI components cannot alter item discounts directly.</p>"
                },
                {
                    "step_number": 9,
                    "title": "9. When to use",
                    "content": "<p>Make all data members private by default. Expose public methods only when callers need to command an action.</p>"
                },
                {
                    "step_number": 10,
                    "title": "10. When NOT to use",
                    "content": "<p>Avoid making data members <code>protected</code>. Protected data breaks encapsulation because any derived class can corrupt base invariants without base class awareness.</p>"
                },
                {
                    "step_number": 11,
                    "title": "11. Advantages",
                    "content": "<ul style='margin-left: 1.25rem;'><li>Prevents external corruption of state.</li><li>Decouples callers from internal memory representations.</li><li>Simplifies debugging by localizing state changes to member functions.</li></ul>"
                },
                {
                    "step_number": 12,
                    "title": "12. Disadvantages",
                    "content": "<ul style='margin-left: 1.25rem;'><li>Overusing <code>friend</code> can punch holes in encapsulation and create tight coupling.</li></ul>"
                },
                {
                    "step_number": 13,
                    "title": "13. Variations / Types",
                    "content": "<p>Public inheritance (is-a), Protected inheritance (implementation detail), Private inheritance (composition alternative).</p>"
                },
                {
                    "step_number": 14,
                    "title": "14. Common mistakes",
                    "content": "<p>Providing boilerplate getters AND setters for every private variable. A setter is just public access with extra syntax!</p>",
                    "callout": {
                        "type": "trap",
                        "title": "The Getter/Setter Illusion",
                        "text": "If a class has `getBalance()` and `setBalance(double)`, it is NOT encapsulated. Prefer behavioral methods like `deposit(amount)` and `withdraw(amount)` that guard business rules."
                    }
                },
                {
                    "step_number": 15,
                    "title": "15. Interview questions",
                    "content": "<p><strong>Q:</strong> Why is <code>protected</code> data considered an architectural code smell in modern C++ Low-Level Design?</p>"
                },
                {
                    "step_number": 16,
                    "title": "16. Interview answer",
                    "content": "<p><strong>Answer:</strong> Protected data creates unbounded coupling across inheritance trees. If a base class invariant changes, every derived class in the codebase might break. Instead, keep data <code>private</code> and provide <code>protected</code> accessor/mutation helper functions if subclasses need extension points.</p>"
                },
                {
                    "step_number": 17,
                    "title": "17. Practice problem",
                    "content": "<p>Refactor a flawed <code>UserAccount</code> class with public raw password and balance fields into a fully encapsulated domain model with password hashing validation.</p>",
                    "refactor": {
                        "title": "Encapsulating User Account Invariants",
                        "problemSummary": "The initial design leaves password strings and wallet balance open to direct public tampering.",
                        "violations": [
                            "Public raw balance can be set to negative values.",
                            "Public password string exposed in plain text."
                        ],
                        "badCode": {
                            "filename": "bad_user.cpp",
                            "code": """// Flawed: Zero encapsulation
struct BadUser {
    std::string username;
    std::string password;
    double walletBalance;
};"""
                        },
                        "goodCode": {
                            "filename": "clean_user.cpp",
                            "code": """// Clean: Fully encapsulated
class CleanUser {
private:
    std::string username;
    std::string passwordHash;
    double walletBalance{0.0};

public:
    CleanUser(std::string user, std::string pwdHash)
        : username(std::move(user)), passwordHash(std::move(pwdHash)) {}

    bool verifyPassword(const std::string& inputHash) const noexcept {
        return passwordHash == inputHash;
    }

    void addFunds(double amount) {
        if (amount <= 0.0) throw std::invalid_argument("Must add positive funds");
        walletBalance += amount;
    }
};"""
                        },
                        "benefits": [
                            "Password hash cannot be overwritten directly.",
                            "Wallet balance changes are strictly audited and validated."
                        ]
                    }
                },
                {
                    "step_number": 18,
                    "title": "18. Summary",
                    "content": "<p>Encapsulation is not just about writing <code>private</code>; it is about guaranteeing domain invariants and hiding internal implementation details from caller dependencies.</p>"
                }
            ]
        },

        # -------------------------------------------------------------
        # 4. Static Members & Const Correctness
        # -------------------------------------------------------------
        {
            "id": "static-and-const",
            "title": "Static Members & Const Correctness",
            "description": "Static class-level shared state, utility factories, const member functions, mutable caching fields, and physical vs logical constness.",
            "sections": [
                {
                    "step_number": 1,
                    "title": "1. What is it?",
                    "content": "<p><strong>Static Members</strong> belong to the class itself rather than any individual object instance. <strong>Const Correctness</strong> is the practice of using <code>const</code> to prevent unintended mutations of variables, parameters, and class states.</p>"
                },
                {
                    "step_number": 2,
                    "title": "2. Why do we need it?",
                    "content": "<p>In multi-threaded and large-scale systems, const-correctness enables compiler optimization and guarantees read-only thread safety. Static members provide centralized counters, configuration registries, or factory instantiation methods without instantiating unnecessary dummy objects.</p>"
                },
                {
                    "step_number": 3,
                    "title": "3. Core idea",
                    "content": "<p>If a member function does not modify the observable logical state of the object, it MUST be marked <code>const</code>. If data or a method belongs to the class concept as a whole (e.g. <code>IdGenerator::next()</code>), make it <code>static</code>.</p>"
                },
                {
                    "step_number": 4,
                    "title": "4. How it works",
                    "content": "<p>Inside a <code>const</code> member function, the implicit <code>this</code> pointer has type <code>const ClassName* const</code>. Attempting to modify non-static member variables causes a compile error, unless a member is explicitly declared <code>mutable</code> (used for internal caching or mutex locking that does not alter logical constness).</p>"
                },
                {
                    "step_number": 5,
                    "title": "5. Visual explanation",
                    "content": "<p>Const Correctness vs Mutable internal caching:</p>",
                    "callout": {
                        "type": "tip",
                        "title": "Physical vs Logical Constness",
                        "text": "Physical constness means not a single bit in the object's memory changes. Logical constness means the external observable state doesn't change, even if internal cache counters or mutexes change using the mutable keyword."
                    }
                },
                {
                    "step_number": 6,
                    "title": "6. C++ implementation",
                    "content": "<p>High-Performance Product Cache with Static Counters and Mutable Thread Mutex:</p>",
                    "code_example": {
                        "filename": "const_static_cache.cpp",
                        "code": """#include <iostream>
#include <string>
#include <mutex>

class ProductCatalog {
private:
    std::string catalogId;
    // static member: shared across all instances
    static inline int totalCatalogsCreated{0};

    // mutable member: allows thread-safe locking inside const query methods
    mutable std::mutex cacheMutex;
    mutable int accessCount{0};

public:
    explicit ProductCatalog(std::string id) : catalogId(std::move(id)) {
        ++totalCatalogsCreated;
    }

    // Static member function
    static int getTotalCatalogs() noexcept {
        return totalCatalogsCreated;
    }

    // Const member function with internal mutable tracking
    std::string getCatalogDetails() const {
        std::lock_guard<std::mutex> lock(cacheMutex);
        ++accessCount; // Valid because accessCount is mutable
        return "Catalog ID: " + catalogId + " (Accessed " + std::to_string(accessCount) + " times)";
    }
};

int main() {
    const ProductCatalog electronics{"CAT-ELEC-01"};
    std::cout << electronics.getCatalogDetails() << "\\n";
    std::cout << "Total Catalogs: " << ProductCatalog::getTotalCatalogs() << "\\n";
    return 0;
}"""
                    }
                },
                {
                    "step_number": 7,
                    "title": "7. Code walkthrough",
                    "content": "<p><strong>Line 8 (static inline int):</strong> C++17 <code>inline static</code> allows in-class initialization of non-const static variables.<br><strong>Lines 11-12 (mutable):</strong> <code>mutable std::mutex</code> allows <code>std::lock_guard</code> to be instantiated inside <code>getCatalogDetails() const</code> without violating constness.<br><strong>Line 23:</strong> <code>getCatalogDetails() const</code> guarantees read-only access for callers holding <code>const ProductCatalog&</code>.</p>"
                },
                {
                    "step_number": 8,
                    "title": "8. Real-world example",
                    "content": "<p>Singleton instances, thread-safe object pools, shared database connection counters, and memoized calculation caches rely on static members and mutable synchronization primitives.</p>"
                },
                {
                    "step_number": 9,
                    "title": "9. When to use",
                    "content": "<p>Mark every getter and non-mutating query function <code>const</code>. Use <code>static</code> methods for utility helper functions and factory creation methods.</p>"
                },
                {
                    "step_number": 10,
                    "title": "10. When NOT to use",
                    "content": "<p>Do not use global static mutable variables as hidden shared state across unrelated components; this causes hidden coupling and multi-threading race conditions.</p>"
                },
                {
                    "step_number": 11,
                    "title": "11. Advantages",
                    "content": "<ul style='margin-left: 1.25rem;'><li>Compile-time enforcement of immutability.</li><li>Enables callers to pass <code>const T&</code> safely, avoiding expensive object copies.</li><li>Static methods can be called without instantiating dummy objects.</li></ul>"
                },
                {
                    "step_number": 12,
                    "title": "12. Disadvantages",
                    "content": "<ul style='margin-left: 1.25rem;'><li>Static state introduces global lifecycle management issues and makes unit test mocking harder.</li></ul>"
                },
                {
                    "step_number": 13,
                    "title": "13. Variations / Types",
                    "content": "<p><code>const</code> member functions, <code>const</code> return types, <code>constexpr</code> compile-time evaluations, <code>mutable</code> fields.</p>"
                },
                {
                    "step_number": 14,
                    "title": "14. Common mistakes",
                    "content": "<p>Forgetting <code>const</code> on a getter method, which prevents that method from being called on any <code>const T&</code> reference passed throughout the system.</p>"
                },
                {
                    "step_number": 15,
                    "title": "15. Interview questions",
                    "content": "<p><strong>Q:</strong> Can a <code>static</code> member function access non-static class members or call <code>this</code>?</p>"
                },
                {
                    "step_number": 16,
                    "title": "16. Interview answer",
                    "content": "<p><strong>Answer:</strong> No. Static member functions do not have an implicit <code>this</code> pointer because they are associated with the class, not an object instance. They can only access static data members and other static member functions.</p>"
                },
                {
                    "step_number": 17,
                    "title": "17. Practice problem",
                    "content": "<p>Design a <code>TransactionIdGenerator</code> class with a private constructor and a static method <code>generateId(const std::string& prefix)</code> that increments an internal atomic static counter and returns formatted transaction IDs.</p>",
                    "practice": {
                        "title": "Thread-safe Static ID Generator",
                        "problemStatement": "Implement a static ID generator that formats prefix + sequential counter safely.",
                        "requirements": [
                            "Private constructor to prevent instantiation",
                            "Static method generateId(prefix)",
                            "Sequential counter increment"
                        ],
                        "constraints": ["No object instances should ever be created"],
                        "hint": "Use static inline std::atomic<uint64_t> counter in C++17/20.",
                        "expectedEntities": [
                            {"name": "TransactionIdGenerator", "responsibility": "Generates unique sequential transaction ID strings."}
                        ],
                        "referenceCode": {
                            "filename": "id_gen.cpp",
                            "code": """#include <iostream>
#include <string>
#include <atomic>

class TransactionIdGenerator {
private:
    static inline std::atomic<uint64_t> counter{1000};
    TransactionIdGenerator() = delete; // Disallow instantiation

public:
    static std::string generateId(const std::string& prefix) {
        uint64_t current = counter.fetch_add(1, std::memory_order_relaxed);
        return prefix + "_" + std::to_string(current);
    }
};"""
                        }
                    }
                },
                {
                    "step_number": 18,
                    "title": "18. Summary",
                    "content": "<p>Const correctness is a fundamental contract in C++ software engineering. Marking non-mutating functions const enables safe pass-by-const-reference and enhances compiler optimization.</p>"
                }
            ]
        },

        # -------------------------------------------------------------
        # 5. Pointers, References & The this Pointer
        # -------------------------------------------------------------
        {
            "id": "pointers-and-references",
            "title": "Pointers, References & the 'this' Pointer",
            "description": "Memory addresses, pointer arithmetic, references vs pointers, method chaining with *this, and nullability semantics in LLD.",
            "sections": [
                {
                    "step_number": 1,
                    "title": "1. What is it?",
                    "content": "<p>A <strong>Pointer</strong> is a variable that stores the memory address of another object. A <strong>Reference</strong> is an alias for an existing object that cannot be null or reseated. The <strong><code>this</code></strong> pointer is an implicit pointer passed to non-static member functions pointing to the calling object instance.</p>"
                },
                {
                    "step_number": 2,
                    "title": "2. Why do we need it?",
                    "content": "<p>Passing large objects by value causes expensive deep copies. References and pointers enable zero-copy parameter passing, polymorphic base-class access, and method chaining (Fluent Interfaces).</p>"
                },
                {
                    "step_number": 3,
                    "title": "3. Core idea",
                    "content": "<p>Prefer <code>const T&</code> for non-null read-only inputs, <code>T&</code> for non-null mutating inputs, and smart pointers (or raw pointers for non-owning optional relationships) when nullability or lifetime transfer is needed.</p>"
                },
                {
                    "step_number": 4,
                    "title": "4. How it works",
                    "content": "<p>References must be initialized upon declaration and cannot be null. Pointers can be reassigned and can hold <code>nullptr</code>. In member functions, returning <code>*this</code> allows chaining multiple method calls sequentially on the same instance.</p>"
                },
                {
                    "step_number": 5,
                    "title": "5. Visual explanation",
                    "content": "<p>Pointer vs Reference comparison:</p>",
                    "comparison": {
                        "title": "Pointers vs References in C++",
                        "columns": ["Feature", "Reference (T&)", "Raw Pointer (T*)", "Best Practice"],
                        "rows": [
                            ["Nullability", "Cannot be null", "Can be nullptr", "Use Reference if object must exist"],
                            ["Reassignment", "Cannot be reseated", "Can point to new address", "Use Pointer if target changes"],
                            ["Syntax", "Direct object access (.)", "Arrow operator (->) or (*ptr)", "References are cleaner"],
                            ["Memory Overhead", "Zero overhead (compiler alias)", "Holds 8-byte address", "References are preferred for params"]
                        ]
                    }
                },
                {
                    "step_number": 6,
                    "title": "6. C++ implementation",
                    "content": "<p>Fluent Request Builder using <code>*this</code> Method Chaining:</p>",
                    "code_example": {
                        "filename": "fluent_builder_this.cpp",
                        "code": """#include <iostream>
#include <string>

class HttpRequest {
private:
    std::string url;
    std::string method{"GET"};
    std::string body;
    int timeoutMs{5000};

public:
    HttpRequest& setUrl(std::string targetUrl) {
        this->url = std::move(targetUrl);
        return *this; // Return reference to current instance for chaining
    }

    HttpRequest& setMethod(std::string httpMethod) {
        this->method = std::move(httpMethod);
        return *this;
    }

    HttpRequest& setBody(std::string requestBody) {
        this->body = std::move(requestBody);
        return *this;
    }

    HttpRequest& setTimeout(int ms) {
        this->timeoutMs = ms;
        return *this;
    }

    void send() const {
        std::cout << "[HTTP SEND] " << method << " " << url 
                  << " | Timeout: " << timeoutMs << "ms"
                  << " | Body: " << body << "\\n";
    }
};

int main() {
    HttpRequest request;
    // Method chaining enabled by returning *this
    request.setUrl("https://api.payment.com/v1/charge")
           .setMethod("POST")
           .setBody("{\\"amount\\": 1500}")
           .setTimeout(3000)
           .send();

    return 0;
}"""
                    }
                },
                {
                    "step_number": 7,
                    "title": "7. Code walkthrough",
                    "content": "<p><strong>Line 12:</strong> <code>return *this;</code> dereferences the implicit <code>this</code> pointer, returning an lvalue reference <code>HttpRequest&</code> to allow continuous dot-chaining.</p>"
                },
                {
                    "step_number": 8,
                    "title": "8. Real-world example",
                    "content": "<p>The <strong>Builder Pattern</strong>, <code>std::cout &lt;&lt; a &lt;&lt; b</code> stream operators, and SQL Query DSLs (e.g. <code>Query().select().from().where()</code>) are driven by returning <code>*this</code>.</p>"
                },
                {
                    "step_number": 9,
                    "title": "9. When to use",
                    "content": "<p>Use references for function parameters whenever you want to avoid copies. Use pointers only when optionality (nullability) or dynamic reseating is necessary.</p>"
                },
                {
                    "step_number": 10,
                    "title": "10. When NOT to use",
                    "content": "<p>Never return references or pointers to local stack variables that go out of scope (dangling pointer/reference bug).</p>"
                },
                {
                    "step_number": 11,
                    "title": "11. Advantages",
                    "content": "<p>Zero runtime copy overhead; enables flexible method chaining and polymorphic dynamic dispatch.</p>"
                },
                {
                    "step_number": 12,
                    "title": "12. Disadvantages",
                    "content": "<p>Dangling pointers/references cause undefined behavior and memory corruption if object lifetimes are mismanaged.</p>"
                },
                {
                    "step_number": 13,
                    "title": "13. Variations / Types",
                    "content": "<p>Lvalue references (<code>T&</code>), Const lvalue references (<code>const T&</code>), Rvalue references (<code>T&&</code>), Raw pointers (<code>T*</code>), Smart pointers.</p>"
                },
                {
                    "step_number": 14,
                    "title": "14. Common mistakes",
                    "content": "<p>Returning a reference to a temporary local variable from a member function.</p>",
                    "callout": {
                        "type": "trap",
                        "title": "Dangling Reference Bug",
                        "text": "const std::string& getName() { std::string temp = 'abc'; return temp; } // FATAL: temp is destroyed when function returns, caller gets dangling reference!"
                    }
                },
                {
                    "step_number": 15,
                    "title": "15. Interview questions",
                    "content": "<p><strong>Q:</strong> Can you call <code>delete this;</code> in C++? If so, when is it legal and what are the catastrophic risks?</p>"
                },
                {
                    "step_number": 16,
                    "title": "16. Interview answer",
                    "content": "<p><strong>Answer:</strong> <code>delete this;</code> is technically legal ONLY if the object was guaranteed to have been allocated on the heap via <code>new</code>, and no member functions or variables of <code>this</code> are accessed after the delete statement. Calling it on a stack-allocated object causes immediate fatal undefined behavior (double free / invalid heap pointer).</p>"
                },
                {
                    "step_number": 17,
                    "title": "17. Practice problem",
                    "content": "<p>Implement a <code>StringBuilder</code> class supporting <code>append(str)</code>, <code>appendLine(str)</code>, and <code>toString()</code> using fluent method chaining returning <code>*this</code>.</p>",
                    "practice": {
                        "title": "Fluent StringBuilder",
                        "problemStatement": "Create a fluent StringBuilder with method chaining.",
                        "requirements": ["append(string)", "appendLine(string)", "toString() const", "Chainable methods"],
                        "constraints": ["Return StringBuilder& from mutating methods"],
                        "hint": "Maintain an internal std::string buffer and return *this from all append operations.",
                        "expectedEntities": [
                            {"name": "StringBuilder", "responsibility": "Accumulates string fragments efficiently."}
                        ],
                        "referenceCode": {
                            "filename": "string_builder.cpp",
                            "code": """#include <iostream>
#include <string>

class StringBuilder {
private:
    std::string buffer;
public:
    StringBuilder& append(const std::string& str) {
        buffer += str;
        return *this;
    }
    StringBuilder& appendLine(const std::string& str) {
        buffer += str + "\\n";
        return *this;
    }
    [[nodiscard]] std::string toString() const {
        return buffer;
    }
};"""
                        }
                    }
                },
                {
                    "step_number": 18,
                    "title": "18. Summary",
                    "content": "<p>References provide safe, non-null aliasing for parameters, while <code>this</code> enables expressive fluent builders and self-referential member operations.</p>"
                }
            ]
        },

        # -------------------------------------------------------------
        # 6. Namespaces & Header/Source Separation
        # -------------------------------------------------------------
        {
            "id": "friend-and-namespaces",
            "title": "Namespaces & Header/Source Separation",
            "description": "Organizing modular C++ architectures, header guards, forward declarations, and compilation firewall techniques.",
            "sections": [
                {
                    "step_number": 1,
                    "title": "1. What is it?",
                    "content": "<p><strong>Namespaces</strong> prevent symbol naming collisions across libraries. <strong>Header/Source Separation</strong> divides code into class declarations (<code>.hpp</code>/<code>.h</code>) and implementation definitions (<code>.cpp</code>).</p>"
                },
                {
                    "step_number": 2,
                    "title": "2. Why do we need it?",
                    "content": "<p>In massive production systems, having thousands of classes in headers causes circular compilation dependencies and exponential build times. Proper separation with forward declarations isolates translation units.</p>"
                },
                {
                    "step_number": 3,
                    "title": "3. Core idea",
                    "content": "<p>Declare interfaces in header files, define heavy implementations in <code>.cpp</code> files, group cohesive subsystems in nested namespaces, and use forward declarations (<code>class Engine;</code>) whenever only pointers or references are needed in the header.</p>"
                },
                {
                    "step_number": 4,
                    "title": "4. How it works",
                    "content": "<p>The C++ preprocessor replaces <code>#include</code> with the literal file contents. <code>#pragma once</code> prevents multiple inclusion in a single translation unit. Forward declarations tell the compiler a class exists so it can allocate pointer sizes without parsing the full class layout.</p>"
                },
                {
                    "step_number": 5,
                    "title": "5. Visual explanation",
                    "content": "<p>Compilation model and Forward Declarations:</p>",
                    "callout": {
                        "type": "tip",
                        "title": "Forward Declaration Rule of Thumb",
                        "text": "If a header only uses `Engine*` or `const Engine&`, do NOT `#include \"Engine.hpp\"`. Simply write `class Engine;` at the top of your header. This drastically reduces build times and breaks circular `#include` cycles."
                    }
                },
                {
                    "step_number": 6,
                    "title": "6. C++ implementation",
                    "content": "<p>Clean Header/Source layout with Namespaces:</p>",
                    "code_example": {
                        "filename": "order_service.hpp",
                        "code": """#pragma once
#include <string>
#include <memory>

// Forward declarations to avoid heavy header includes
namespace Payment { class IPaymentGateway; }
namespace Notification { class INotificationService; }

namespace Core::Commerce {

    class OrderService {
    private:
        std::shared_ptr<Payment::IPaymentGateway> paymentGateway;
        std::shared_ptr<Notification::INotificationService> notifier;

    public:
        OrderService(std::shared_ptr<Payment::IPaymentGateway> gateway,
                     std::shared_ptr<Notification::INotificationService> notificationService);

        void processOrder(const std::string& orderId, double amount);
    };

} // namespace Core::Commerce"""
                    }
                },
                {
                    "step_number": 7,
                    "title": "7. Code walkthrough",
                    "content": "<p><strong>Line 1 (<code>#pragma once</code>):</strong> Standard header guard.<br><strong>Lines 6-7 (Forward Declarations):</strong> Declares types without including full gateway/notification headers.<br><strong>Line 9 (<code>namespace Core::Commerce</code>):</strong> C++17 nested namespace syntax organizes system packages cleanly.</p>"
                },
                {
                    "step_number": 8,
                    "title": "8. Real-world example",
                    "content": "<p>Enterprise game engines (Unreal Engine) and trading platforms (Bloomberg, Citadel) strictly enforce forward declarations and namespace modularity to keep multi-million-line compilation times under minutes.</p>"
                },
                {
                    "step_number": 9,
                    "title": "9. When to use",
                    "content": "<p>Always separate declarations and definitions in production C++ projects, except for template classes which must remain in headers.</p>"
                },
                {
                    "step_number": 10,
                    "title": "10. When NOT to use",
                    "content": "<p>Never put <code>using namespace std;</code> in a header file, as it forces the entire std namespace into every file that includes that header (namespace pollution).</p>"
                },
                {
                    "step_number": 11,
                    "title": "11. Advantages",
                    "content": "<p>Eliminates symbol naming clashes, drastically reduces incremental compilation times, and prevents circular dependency errors.</p>"
                },
                {
                    "step_number": 12,
                    "title": "12. Disadvantages",
                    "content": "<p>Requires maintaining two files (<code>.hpp</code> and <code>.cpp</code>) per class.</p>"
                },
                {
                    "step_number": 13,
                    "title": "13. Variations / Types",
                    "content": "<p>Named namespaces, Nested namespaces (<code>namespace A::B</code>), Anonymous (unnamed) namespaces for internal linkage, Inline namespaces for ABI versioning.</p>"
                },
                {
                    "step_number": 14,
                    "title": "14. Common mistakes",
                    "content": "<p>Putting <code>using namespace ...</code> inside header files; causing circular dependency deadlock where Header A includes Header B which includes Header A.</p>"
                },
                {
                    "step_number": 15,
                    "title": "15. Interview questions",
                    "content": "<p><strong>Q:</strong> What is the purpose of an unnamed (anonymous) namespace in a <code>.cpp</code> file?</p>"
                },
                {
                    "step_number": 16,
                    "title": "16. Interview answer",
                    "content": "<p><strong>Answer:</strong> An anonymous namespace gives functions and variables <strong>internal linkage</strong>, meaning they are visible only within that single translation unit (<code>.cpp</code> file). It is the modern C++ replacement for the C-style <code>static</code> global function/variable specifier.</p>"
                },
                {
                    "step_number": 17,
                    "title": "17. Practice problem",
                    "content": "<p>Structure a modular namespace hierarchy for a <code>TradingEngine</code> with <code>OrderBook</code>, <code>MatchingEngine</code>, and <code>RiskManager</code> components.</p>",
                    "practice": {
                        "title": "Modular Namespace Architecture",
                        "problemStatement": "Design clean namespaces for a trading engine subsystem.",
                        "requirements": ["Nested namespaces", "Proper header guards", "Forward declarations"],
                        "constraints": ["No using namespace in headers"],
                        "hint": "Use namespace Trading::Execution and namespace Trading::Risk.",
                        "expectedEntities": [
                            {"name": "OrderBook", "responsibility": "Maintains bids and asks."},
                            {"name": "RiskManager", "responsibility": "Validates margin before execution."}
                        ],
                        "referenceCode": {
                            "filename": "trading_ns.hpp",
                            "code": """#pragma once
namespace Trading::Risk { class RiskManager; }
namespace Trading::Execution {
    class OrderBook {
    public:
        void addOrder(int id, double price);
    };
}"""
                        }
                    }
                },
                {
                    "step_number": 18,
                    "title": "18. Summary",
                    "content": "<p>Proper namespace scoping and forward declarations are essential for modular, clean, and fast-building C++ software architectures.</p>"
                }
            ]
        },

        # -------------------------------------------------------------
        # 7. Composition in C++
        # -------------------------------------------------------------
        {
            "id": "composition",
            "title": "Composition in C++",
            "description": "Strong 'has-a' lifetime ownership relationship, member object lifecycles, and composition vs aggregation.",
            "sections": [
                {
                    "step_number": 1,
                    "title": "1. What is it?",
                    "content": "<p><strong>Composition</strong> is a strong 'has-a' relationship where the parent object owns the complete lifetime of the child component. When the parent object is destroyed, the child component is destroyed immediately with it.</p>"
                },
                {
                    "step_number": 2,
                    "title": "2. Why do we need it?",
                    "content": "<p>Composition is the cornerstone of the fundamental LLD principle: <em>'Favor object composition over class inheritance'</em>. It allows systems to be built from small, reusable, independent components without brittle inheritance hierarchies.</p>"
                },
                {
                    "step_number": 3,
                    "title": "3. Core idea",
                    "content": "<p>A <code>Car</code> has an <code>Engine</code>. The Engine cannot exist without the Car in this context; creating a Car creates the Engine, and destroying the Car destroys the Engine.</p>"
                },
                {
                    "step_number": 4,
                    "title": "4. How it works",
                    "content": "<p>In C++, composition is implemented by declaring child objects directly as non-static value members (<code>Engine engine;</code>) or as exclusive owning pointers (<code>std::unique_ptr&lt;Engine&gt; engine;</code>). The parent object's destructor automatically invokes the child's destructor.</p>"
                },
                {
                    "step_number": 5,
                    "title": "5. Visual explanation",
                    "content": "<p>UML Composition Diagram (Filled Diamond notation):</p>",
                    "diagram": {
                        "title": "Car and Engine Composition UML",
                        "classes": [
                            {
                                "name": "Car",
                                "attributes": [
                                    {"visibility": "-", "name": "engine", "type": "Engine"},
                                    {"visibility": "-", "name": "vin", "type": "std::string"}
                                ],
                                "methods": [
                                    {"visibility": "+", "name": "startCar", "params": "", "returnType": "void"}
                                ]
                            },
                            {
                                "name": "Engine",
                                "attributes": [
                                    {"visibility": "-", "name": "cylinders", "type": "int"},
                                    {"visibility": "-", "name": "isRunning", "type": "bool"}
                                ],
                                "methods": [
                                    {"visibility": "+", "name": "ignite", "params": "", "returnType": "void"},
                                    {"visibility": "+", "name": "shutdown", "params": "", "returnType": "void"}
                                ]
                            }
                        ],
                        "relationships": [
                            {
                                "from": "Car",
                                "to": "Engine",
                                "type": "composition",
                                "label": "owns",
                                "ownership": "Strict (Car owns Engine)",
                                "lifetime": "Coupled (Engine dies with Car)",
                                "coupling": "High internal cohesion",
                                "cppSyntax": "class Car { Engine engine; };"
                            }
                        ]
                    }
                },
                {
                    "step_number": 6,
                    "title": "6. C++ implementation",
                    "content": "<p>Complete C++ implementation of Composition:</p>",
                    "code_example": {
                        "filename": "composition_engine.cpp",
                        "code": """#include <iostream>
#include <string>

class Engine {
private:
    int horsepower;
    bool running{false};

public:
    explicit Engine(int hp) : horsepower(hp) {
        std::cout << "[Engine " << horsepower << " HP] Constructed.\\n";
    }

    ~Engine() {
        std::cout << "[Engine " << horsepower << " HP] Destroyed.\\n";
    }

    void ignite() {
        running = true;
        std::cout << "[Engine] Ignited and running.\\n";
    }
};

class Car {
private:
    std::string model;
    Engine engine; // Composition: Direct value member ownership

public:
    Car(std::string carModel, int hp)
        : model(std::move(carModel)), engine(hp) { // Initializes Engine
        std::cout << "[Car " << model << "] Constructed.\\n";
    }

    ~Car() {
        std::cout << "[Car " << model << "] Destroying...\\n";
    }

    void drive() {
        std::cout << "[Car " << model << "] Preparing to drive...\\n";
        engine.ignite();
    }
};

int main() {
    {
        Car mySedan{"Tesla Model S", 670};
        mySedan.drive();
    } // Both Car and Engine destroyed automatically here!
    return 0;
}"""
                    }
                },
                {
                    "step_number": 7,
                    "title": "7. Code walkthrough",
                    "content": "<p><strong>Line 24:</strong> <code>Engine engine;</code> is directly embedded in <code>Car</code>'s memory layout.<br><strong>Line 28:</strong> <code>Car</code>'s initializer list explicitly initializes the <code>engine(hp)</code> sub-object.<br><strong>Execution output:</strong> Shows Engine constructed first, Car constructed second. Upon scope exit, Car destructor runs first, Engine destructor runs second.</p>"
                },
                {
                    "step_number": 8,
                    "title": "8. Real-world example",
                    "content": "<p>In GUI systems, a <code>Window</code> has a <code>TitleBar</code> and <code>CloseButton</code> (Composition). In game engines, an <code>Actor</code> has a <code>TransformComponent</code> and <code>MeshComponent</code>.</p>"
                },
                {
                    "step_number": 9,
                    "title": "9. When to use",
                    "content": "<p>Use composition whenever a component has no meaning or independent lifecycle outside the context of its parent container.</p>"
                },
                {
                    "step_number": 10,
                    "title": "10. When NOT to use",
                    "content": "<p>Do not use composition if the child object must outlive the parent or be shared among multiple parents (use <strong>Aggregation</strong> with references/pointers instead).</p>"
                },
                {
                    "step_number": 11,
                    "title": "11. Advantages",
                    "content": "<ul style='margin-left: 1.25rem;'><li>Zero heap allocation overhead if stored as value member.</li><li>Deterministic, automatic resource cleanup.</li><li>Encapsulates component complexity inside parent.</li></ul>"
                },
                {
                    "step_number": 12,
                    "title": "12. Disadvantages",
                    "content": "<p>Tight coupling between parent and child implementation if direct value members are used instead of abstract interface pointers.</p>"
                },
                {
                    "step_number": 13,
                    "title": "13. Variations / Types",
                    "content": "<p>Value Composition (<code>Engine engine;</code>), Dynamic Exclusive Composition (<code>std::unique_ptr&lt;IEngine&gt; engine;</code>).</p>"
                },
                {
                    "step_number": 14,
                    "title": "14. Common mistakes",
                    "content": "<p>Using inheritance when composition is intended (e.g. <code>class Car : public Engine</code> is a major design smell: a Car is NOT an Engine; a Car HAS an Engine).</p>"
                },
                {
                    "step_number": 15,
                    "title": "15. Interview questions",
                    "content": "<p><strong>Q:</strong> What is the core difference between Composition and Aggregation in terms of lifetime and C++ memory representation?</p>"
                },
                {
                    "step_number": 16,
                    "title": "16. Interview answer",
                    "content": "<p><strong>Answer:</strong> In <strong>Composition</strong>, the child's lifetime is strictly bound to the parent (embedded value or <code>std::unique_ptr</code>). If the parent dies, the child dies. In <strong>Aggregation</strong>, the child exists independently of the parent container and can outlive it (represented via raw non-owning pointers <code>T*</code>, references <code>T&</code>, or <code>std::shared_ptr&lt;T&gt;</code>/<code>std::weak_ptr&lt;T&gt;</code>).</p>"
                },
                {
                    "step_number": 17,
                    "title": "17. Practice problem",
                    "content": "<p>Model a <code>Computer</code> class that has Composition with <code>CPU</code> and <code>RAM</code>, and Aggregation with an external <code>Monitor*</code>.</p>",
                    "practice": {
                        "title": "Computer Hardware Composition vs Aggregation",
                        "problemStatement": "Implement Computer with owned CPU/RAM (composition) and pluggable Monitor (aggregation).",
                        "requirements": [
                            "Computer owns CPU and RAM lifetimes",
                            "Monitor can be plugged/unplugged and outlives Computer",
                            "Proper destructor messages"
                        ],
                        "constraints": ["Demonstrate lifetime differences"],
                        "hint": "Use direct value members for CPU/RAM and a raw pointer for Monitor*.",
                        "expectedEntities": [
                            {"name": "CPU", "responsibility": "Internal processing chip (owned)."},
                            {"name": "Monitor", "responsibility": "External display peripheral (aggregated)."}
                        ],
                        "referenceCode": {
                            "filename": "computer_comp.cpp",
                            "code": """#include <iostream>
#include <string>

class CPU { public: ~CPU() { std::cout << "CPU destroyed\\n"; } };
class RAM { public: ~RAM() { std::cout << "RAM destroyed\\n"; } };
class Monitor { public: std::string model; };

class Computer {
private:
    CPU cpu;        // Composition
    RAM ram;        // Composition
    Monitor* display{nullptr}; // Aggregation
public:
    void attachMonitor(Monitor* m) { display = m; }
};"""
                        }
                    }
                },
                {
                    "step_number": 18,
                    "title": "18. Summary",
                    "content": "<p>Composition models strong ownership and encapsulation. It is the most frequent and reliable relationship in Low-Level Design.</p>"
                }
            ]
        },

        # -------------------------------------------------------------
        # 8. RAII (Resource Acquisition Is Initialization)
        # -------------------------------------------------------------
        {
            "id": "raii-and-resource-mgmt",
            "title": "RAII (Resource Acquisition Is Initialization)",
            "description": "The fundamental idiom of C++: binding resource acquisition to constructor initialization and resource release to destructor execution.",
            "sections": [
                {
                    "step_number": 1,
                    "title": "1. What is it?",
                    "content": "<p><strong>RAII</strong> (Resource Acquisition Is Initialization) is a C++ programming idiom where acquiring a resource (heap memory, file handle, socket, database connection, mutex lock) is performed in the constructor, and releasing the resource is guaranteed in the destructor.</p>"
                },
                {
                    "step_number": 2,
                    "title": "2. Why do we need it?",
                    "content": "<p>Manual resource management (e.g. <code>fclose(fp)</code>, <code>free(ptr)</code>, <code>mutex.unlock()</code>) is notorious for leaking resources whenever early returns or exceptions occur. RAII guarantees leak-free execution under all control flow branches.</p>"
                },
                {
                    "step_number": 3,
                    "title": "3. Core idea",
                    "content": "<p>Tie the lifetime of any system resource to the lifetime of a stack-allocated managing object. When the stack frame unwinds (normal return OR thrown exception), the destructor automatically releases the resource.</p>"
                },
                {
                    "step_number": 4,
                    "title": "4. How it works",
                    "content": "<p>C++ guarantees that local stack objects have their destructors called in reverse order of declaration when exiting scope. By wrapping raw resource handles in an RAII class, resource reclamation becomes 100% deterministic.</p>"
                },
                {
                    "step_number": 5,
                    "title": "5. Visual explanation",
                    "content": "<p>RAII Exception Safety flow:</p>",
                    "callout": {
                        "type": "important",
                        "title": "RAII vs Manual Cleanup under Exceptions",
                        "text": "Manual code: Lock -> Do Work -> Exception Thrown! -> Unlock NEVER called (Deadlock!).\\nRAII code: lock_guard -> Do Work -> Exception Thrown! -> Stack unwinds -> Destructor automatically unlocks mutex!"
                    }
                },
                {
                    "step_number": 6,
                    "title": "6. C++ implementation",
                    "content": "<p>Production-Grade RAII File Wrapper:</p>",
                    "code_example": {
                        "filename": "raii_file_guard.cpp",
                        "code": """#include <iostream>
#include <cstdio>
#include <stdexcept>
#include <string>

class FileHandle {
private:
    FILE* file{nullptr};
    std::string filename;

public:
    FileHandle(const std::string& path, const std::string& mode)
        : filename(path) {
        file = std::fopen(path.c_str(), mode.c_str());
        if (!file) {
            throw std::runtime_error("Failed to open file: " + path);
        }
        std::cout << "[RAII] File '" << filename << "' acquired & opened.\\n";
    }

    // Destructor guarantees file handle is closed
    ~FileHandle() noexcept {
        if (file) {
            std::fclose(file);
            std::cout << "[RAII] File '" << filename << "' safely closed.\\n";
        }
    }

    // Prevent accidental copying (resource duplication)
    FileHandle(const FileHandle&) = delete;
    FileHandle& operator=(const FileHandle&) = delete;

    // Allow move semantics
    FileHandle(FileHandle&& other) noexcept
        : file(other.file), filename(std::move(other.filename)) {
        other.file = nullptr;
    }

    void writeLine(const std::string& text) {
        if (!file || std::fputs((text + "\\n").c_str(), file) == EOF) {
            throw std::runtime_error("Write failed to file: " + filename);
        }
    }
};

int main() {
    try {
        FileHandle logFile{"application.log", "w"};
        logFile.writeLine("Initializing system components...");
        logFile.writeLine("Processing payment batches...");
        // If an exception is thrown here, file still closes cleanly!
    } catch (const std::exception& ex) {
        std::cerr << "Exception caught: " << ex.what() << "\\n";
    }
    return 0;
}"""
                    }
                },
                {
                    "step_number": 7,
                    "title": "7. Code walkthrough",
                    "content": "<p><strong>Lines 11-17 (Constructor):</strong> Opens the file and throws if invalid.<br><strong>Lines 20-25 (Destructor):</strong> Checks pointer and calls <code>fclose</code>, marked <code>noexcept</code>.<br><strong>Lines 28-29:</strong> Deletes copy constructor and assignment operator to prevent double-closing the same OS file handle.</p>"
                },
                {
                    "step_number": 8,
                    "title": "8. Real-world example",
                    "content": "<p><code>std::unique_ptr</code>, <code>std::vector</code>, <code>std::fstream</code>, <code>std::lock_guard</code>, and Vulkan/OpenGL GPU texture wrappers are all pure RAII implementations.</p>"
                },
                {
                    "step_number": 9,
                    "title": "9. When to use",
                    "content": "<p>Use RAII for ANY resource that requires acquisition and release steps (memory, files, sockets, locks, database transactions).</p>"
                },
                {
                    "step_number": 10,
                    "title": "10. When NOT to use",
                    "content": "<p>RAII is the core idiom of C++; there is virtually no scenario in modern C++ where manual acquisition/cleanup is preferred over RAII.</p>"
                },
                {
                    "step_number": 11,
                    "title": "11. Advantages",
                    "content": "<ul style='margin-left: 1.25rem;'><li>Zero resource leaks.</li><li>Complete exception safety during stack unwinding.</li><li>Eliminates boilerplate cleanup code.</li></ul>"
                },
                {
                    "step_number": 12,
                    "title": "12. Disadvantages",
                    "content": "<p>Requires understanding move vs copy semantics to prevent accidental resource copying.</p>"
                },
                {
                    "step_number": 13,
                    "title": "13. Variations / Types",
                    "content": "<p>Scope Guards, Smart Pointers, Lock Wrappers, Custom Transaction Rollback guards.</p>"
                },
                {
                    "step_number": 14,
                    "title": "14. Common mistakes",
                    "content": "<p>Failing to disable copy operations on RAII wrappers, leading to two objects pointing to the same handle and causing a double-free crash.</p>"
                },
                {
                    "step_number": 15,
                    "title": "15. Interview questions",
                    "content": "<p><strong>Q:</strong> How does RAII guarantee exception safety in C++ when an exception is thrown inside a deeply nested function call?</p>"
                },
                {
                    "step_number": 16,
                    "title": "16. Interview answer",
                    "content": "<p><strong>Answer:</strong> When an exception is thrown, the C++ runtime performs <strong>Stack Unwinding</strong>. It pops stack frames one by one until a matching <code>catch</code> block is found. As each stack frame is destroyed, all local objects in that frame have their destructors called in reverse order of construction, guaranteeing all acquired resources are freed.</p>"
                },
                {
                    "step_number": 17,
                    "title": "17. Practice problem",
                    "content": "<p>Build a <code>TransactionScope</code> RAII guard that begins a database transaction on construction, commits if <code>commit()</code> was explicitly called, and automatically rolls back in the destructor if commit was never called.</p>",
                    "practice": {
                        "title": "RAII Database Transaction Rollback Guard",
                        "problemStatement": "Build a TransactionScope RAII guard that rolls back on abnormal termination.",
                        "requirements": [
                            "Constructor logs [TX] BEGIN",
                            "commit() marks transaction as committed",
                            "Destructor checks isCommitted; if false, logs [TX] ROLLBACK; otherwise does nothing"
                        ],
                        "constraints": ["Copy operations deleted"],
                        "hint": "Use a bool isCommitted flag.",
                        "expectedEntities": [
                            {"name": "TransactionScope", "responsibility": "Guarantees transaction commit or automatic rollback."}
                        ],
                        "referenceCode": {
                            "filename": "tx_scope.cpp",
                            "code": """#include <iostream>

class TransactionScope {
private:
    bool isCommitted{false};
public:
    TransactionScope() { std::cout << "[TX] BEGIN\\n"; }
    ~TransactionScope() noexcept {
        if (!isCommitted) {
            std::cout << "[TX] AUTO-ROLLBACK (Uncommitted changes aborted)\\n";
        }
    }
    void commit() {
        isCommitted = true;
        std::cout << "[TX] COMMITTED\\n";
    }
    TransactionScope(const TransactionScope&) = delete;
    TransactionScope& operator=(const TransactionScope&) = delete;
};"""
                        }
                    }
                },
                {
                    "step_number": 18,
                    "title": "18. Summary",
                    "content": "<p>RAII is the bedrock of modern C++. It turns manual, error-prone cleanup into automatic, compiler-enforced lifetime guarantees.</p>"
                }
            ]
        },

        # -------------------------------------------------------------
        # 9. Rule of 0, Rule of 3, and Rule of 5
        # -------------------------------------------------------------
        {
            "id": "rule-of-0-3-5",
            "title": "Rule of 0, Rule of 3, and Rule of 5",
            "description": "Managing special member functions: Destructor, Copy Constructor, Copy Assignment, Move Constructor, Move Assignment, and the Copy-and-Swap idiom.",
            "sections": [
                {
                    "step_number": 1,
                    "title": "1. What is it?",
                    "content": "<p>The <strong>Rule of 0/3/5</strong> defines C++ guidelines for implementing special member functions:<br><strong>Rule of 3 (C++98):</strong> If you implement a Destructor, Copy Constructor, or Copy Assignment, you must implement all three.<br><strong>Rule of 5 (C++11):</strong> In modern C++, adding Move Constructor and Move Assignment completes the set of 5.<br><strong>Rule of 0:</strong> Design classes that manage NO raw resources directly (use smart pointers/containers), so the compiler can generate all 5 correctly!</p>"
                },
                {
                    "step_number": 2,
                    "title": "2. Why do we need it?",
                    "content": "<p>The compiler generates default copy constructors that perform a <strong>shallow member-wise copy</strong>. If your class holds a raw pointer or resource, shallow copying causes both objects to own the same pointer, resulting in double deletion and undefined behavior.</p>"
                },
                {
                    "step_number": 3,
                    "title": "3. Core idea",
                    "content": "<p>Aim for the <strong>Rule of Zero</strong> in 95% of domain classes. When writing low-level resource managers, implement the full <strong>Rule of Five</strong> with deep copying and efficient move semantics.</p>"
                },
                {
                    "step_number": 4,
                    "title": "4. How it works",
                    "content": "<p>The 5 special member functions are:<br>1. Destructor: <code>~Widget();</code><br>2. Copy Constructor: <code>Widget(const Widget&);</code><br>3. Copy Assignment: <code>Widget& operator=(const Widget&);</code><br>4. Move Constructor: <code>Widget(Widget&&) noexcept;</code><br>5. Move Assignment: <code>Widget& operator=(Widget&&) noexcept;</code></p>"
                },
                {
                    "step_number": 5,
                    "title": "5. Visual explanation",
                    "content": "<p>Comparison of Rule of 0 vs Rule of 3 vs Rule of 5:</p>",
                    "comparison": {
                        "title": "Rule of 0 vs Rule of 3 vs Rule of 5",
                        "columns": ["Rule", "When to Use", "Special Member Functions Written", "Risk Level"],
                        "rows": [
                            ["Rule of 0", "Standard domain classes holding string, vector, unique_ptr", "None (let compiler generate)", "Safest & Preferred"],
                            ["Rule of 3", "Legacy C++98 classes managing raw pointers/handles", "Destructor, Copy Ctor, Copy Assign", "High (No Move support)"],
                            ["Rule of 5", "Custom low-level memory/resource management classes", "All 5 (Destructor, Copy/Move Ctors, Copy/Move Assign)", "Requires precision"]
                        ]
                    }
                },
                {
                    "step_number": 6,
                    "title": "6. C++ implementation",
                    "content": "<p>Full Rule of 5 Dynamic Buffer with Copy-and-Swap Idiom:</p>",
                    "code_example": {
                        "filename": "rule_of_five_buffer.cpp",
                        "code": """#include <iostream>
#include <algorithm>
#include <utility>

class DynamicBuffer {
private:
    size_t size{0};
    int* data{nullptr};

public:
    // Default / Parameterized Constructor
    explicit DynamicBuffer(size_t n = 0) : size(n), data(n ? new int[n]() : nullptr) {
        std::cout << "[Buffer] Allocated " << size << " ints.\\n";
    }

    // 1. Destructor
    ~DynamicBuffer() noexcept {
        delete[] data;
        std::cout << "[Buffer] Deallocated size " << size << ".\\n";
    }

    // 2. Copy Constructor (Deep Copy)
    DynamicBuffer(const DynamicBuffer& other)
        : size(other.size), data(other.size ? new int[other.size] : nullptr) {
        std::copy(other.data, other.data + other.size, data);
        std::cout << "[Buffer] Deep Copied size " << size << ".\\n";
    }

    // 3. Move Constructor (Resource Steal)
    DynamicBuffer(DynamicBuffer&& other) noexcept
        : size(other.size), data(other.data) {
        other.size = 0;
        other.data = nullptr; // Leave source in valid empty state
        std::cout << "[Buffer] Move Constructed.\\n";
    }

    // Swap helper function for Copy-and-Swap idiom
    friend void swap(DynamicBuffer& first, DynamicBuffer& second) noexcept {
        using std::swap;
        swap(first.size, second.size);
        swap(first.data, second.data);
    }

    // 4 & 5. Unified Assignment Operator (Copy-and-Swap handles both copy & move)
    DynamicBuffer& operator=(DynamicBuffer other) noexcept {
        swap(*this, other);
        return *this;
    }
};

int main() {
    DynamicBuffer buf1(100);
    DynamicBuffer buf2 = buf1;              // Copy Constructor
    DynamicBuffer buf3 = std::move(buf1);   // Move Constructor
    buf2 = buf3;                            // Copy Assignment
    return 0;
}"""
                    }
                },
                {
                    "step_number": 7,
                    "title": "7. Code walkthrough",
                    "content": "<p><strong>Lines 20-24 (Copy Ctor):</strong> Performs deep allocation and memory copy.<br><strong>Lines 27-32 (Move Ctor):</strong> Steals pointer and sets <code>other.data = nullptr</code> in $O(1)$ time.<br><strong>Lines 41-44 (Unified operator=):</strong> Takes parameter by value (<code>DynamicBuffer other</code>); automatically handles both copy and move assignment using <code>swap</code> with strong exception safety!</p>"
                },
                {
                    "step_number": 8,
                    "title": "8. Real-world example",
                    "content": "<p><code>std::vector</code>, <code>std::string</code>, and audio PCM sound buffers implement the Rule of 5 to provide deep copies and blazing-fast moves.</p>"
                },
                {
                    "step_number": 9,
                    "title": "9. When to use",
                    "content": "<p>Apply Rule of 5 when creating low-level data structures (e.g., custom Matrix, RingBuffer). Apply Rule of 0 everywhere else.</p>"
                },
                {
                    "step_number": 10,
                    "title": "10. When NOT to use",
                    "content": "<p>Do not write manual copy/move functions if all members are already standard library types (e.g. <code>std::string</code>, <code>std::vector</code>).</p>"
                },
                {
                    "step_number": 11,
                    "title": "11. Advantages",
                    "content": "<p>Eliminates double-free crashes, supports move performance optimizations, and provides strong exception safety.</p>"
                },
                {
                    "step_number": 12,
                    "title": "12. Disadvantages",
                    "content": "<p>Requires meticulous attention to detail to ensure self-assignment safety and <code>noexcept</code> move guarantees.</p>"
                },
                {
                    "step_number": 13,
                    "title": "13. Variations / Types",
                    "content": "<p>Rule of 0, Rule of 3 (C++98), Rule of 5 (C++11), Copy-and-Swap idiom.</p>"
                },
                {
                    "step_number": 14,
                    "title": "14. Common mistakes",
                    "content": "<p>Forgetting to nullify the source object's pointers in the Move Constructor, resulting in double deletion when the temporary source object destructs.</p>"
                },
                {
                    "step_number": 15,
                    "title": "15. Interview questions",
                    "content": "<p><strong>Q:</strong> Why should Move Constructors and Move Assignment operators almost always be marked <code>noexcept</code>?</p>"
                },
                {
                    "step_number": 16,
                    "title": "16. Interview answer",
                    "content": "<p><strong>Answer:</strong> Standard library containers like <code>std::vector</code> check <code>std::is_nothrow_move_constructible</code> when resizing. If your move constructor is NOT marked <code>noexcept</code>, <code>std::vector</code> will fall back to expensive deep copies during reallocation to guarantee strong exception safety.</p>"
                },
                {
                    "step_number": 17,
                    "title": "17. Practice problem",
                    "content": "<p>Refactor a user profile class managing a raw string buffer to use the Rule of Zero with <code>std::string</code>.</p>",
                    "refactor": {
                        "title": "Refactor to Rule of Zero",
                        "problemSummary": "Legacy class uses raw char* and manually manages memory, violating Rule of Zero.",
                        "violations": [
                            "Manual new char[] and delete[] invites memory leaks.",
                            "Missing copy constructor causes double free on copy."
                        ],
                        "badCode": {
                            "filename": "bad_rule_profile.cpp",
                            "code": """// Flawed: Raw memory management without Rule of 5
class BadProfile {
    char* name;
public:
    BadProfile(const char* n) {
        name = new char[strlen(n) + 1];
        strcpy(name, n);
    }
    ~BadProfile() { delete[] name; }
    // BUG: Missing copy constructor & assignment!
};"""
                        },
                        "goodCode": {
                            "filename": "clean_rule_zero.cpp",
                            "code": """// Clean: Rule of Zero using std::string
class CleanProfile {
private:
    std::string name;
public:
    explicit CleanProfile(std::string n) : name(std::move(n)) {}
    // Compiler automatically generates perfect copy, move, and destructor!
};"""
                        },
                        "benefits": [
                            "Zero manual memory management.",
                            "Automatic exception safety and no risk of double free."
                        ]
                    }
                },
                {
                    "step_number": 18,
                    "title": "18. Summary",
                    "content": "<p>The Rule of 0/3/5 is essential for memory safety in C++. Default to Rule of 0; use Rule of 5 with Copy-and-Swap when building custom resource wrappers.</p>"
                }
            ]
        },

        # -------------------------------------------------------------
        # 10. Copy and Move Semantics
        # -------------------------------------------------------------
        {
            "id": "copy-and-move-semantics",
            "title": "Copy vs Move Semantics (rvalue references)",
            "description": "Lvalues, Rvalues, std::move, std::forward, rvalue references (&&), and high-performance zero-copy resource transfers in C++20.",
            "sections": [
                {
                    "step_number": 1,
                    "title": "1. What is it?",
                    "content": "<p><strong>Copy Semantics</strong> duplicates the contents of an object into a new memory location. <strong>Move Semantics</strong> transfers ownership of internal resources from a temporary/expiring object (rvalue) to a target object without allocating new memory or copying bytes.</p>"
                },
                {
                    "step_number": 2,
                    "title": "2. Why do we need it?",
                    "content": "<p>Before C++11, returning large objects (like a 10MB vector or string) from functions caused costly deep copies. Move semantics turns $O(N)$ deep copies into $O(1)$ pointer swaps.</p>"
                },
                {
                    "step_number": 3,
                    "title": "3. Core idea",
                    "content": "<p>An <strong>Lvalue</strong> is an expression that has an identifiable memory address (e.g. named variables). An <strong>Rvalue</strong> is a temporary value that has no persistent memory location (e.g. literals, function return values). <code>std::move</code> unconditionally casts an lvalue to an rvalue reference (<code>T&&</code>), enabling move constructors to steal its resources.</p>"
                },
                {
                    "step_number": 4,
                    "title": "4. How it works",
                    "content": "<p><code>std::move(x)</code> does NOT move anything at runtime; it is a compile-time <code>static_cast&lt;T&&&gt;(x)</code> that allows overload resolution to select the move constructor instead of the copy constructor.</p>"
                },
                {
                    "step_number": 5,
                    "title": "5. Visual explanation",
                    "content": "<p>Copy vs Move Mechanism:</p>",
                    "callout": {
                        "type": "tip",
                        "title": "Copy vs Move in Memory",
                        "text": "Copy: Allocate New Buffer -> Copy 1,000,000 items -> Two separate memory blocks.\\nMove: Target.ptr = Source.ptr -> Source.ptr = nullptr -> Zero new memory allocated (Instant $O(1)$ pointer steal)!"
                    }
                },
                {
                    "step_number": 6,
                    "title": "6. C++ implementation",
                    "content": "<p>Demonstrating Move vs Copy Performance with Custom Payload:</p>",
                    "code_example": {
                        "filename": "move_semantics_demo.cpp",
                        "code": """#include <iostream>
#include <vector>
#include <string>
#include <utility>

class HeavyPayload {
private:
    std::string name;
    std::vector<int> numbers;

public:
    HeavyPayload(std::string n, size_t count)
        : name(std::move(n)), numbers(count, 42) {
        std::cout << "[Created] " << name << " with " << numbers.size() << " elements.\\n";
    }

    // Copy Constructor
    HeavyPayload(const HeavyPayload& other)
        : name(other.name + " (Copy)"), numbers(other.numbers) {
        std::cout << "[COPIED] " << name << " - Deep copied " << numbers.size() << " elements.\\n";
    }

    // Move Constructor
    HeavyPayload(HeavyPayload&& other) noexcept
        : name(std::move(other.name)), numbers(std::move(other.numbers)) {
        std::cout << "[MOVED] " << name << " - Stole vector buffer in O(1) time!\\n";
    }
};

int main() {
    std::cout << "--- 1. Testing Copy ---\\n";
    HeavyPayload original{"DataSet-A", 1000000};
    HeavyPayload copyObj = original; // Deep copy

    std::cout << "\\n--- 2. Testing Move ---\\n";
    HeavyPayload movedObj = std::move(original); // Fast Move!
    return 0;
}"""
                    }
                },
                {
                    "step_number": 7,
                    "title": "7. Code walkthrough",
                    "content": "<p><strong>Line 23:</strong> <code>HeavyPayload(HeavyPayload&& other) noexcept</code> accepts an rvalue reference <code>&&</code> and uses <code>std::move</code> on members to steal memory pointers without copying array elements.</p>"
                },
                {
                    "step_number": 8,
                    "title": "8. Real-world example",
                    "content": "<p>Passing large request bodies into asynchronous thread queues in high-throughput network engines (e.g. NGINX C++ modules, Envoy proxy) without memory allocations.</p>"
                },
                {
                    "step_number": 9,
                    "title": "9. When to use",
                    "content": "<p>Use <code>std::move</code> when passing sinks (parameters that will be stored inside the object) and when transferring unique ownership (e.g. <code>std::unique_ptr</code>).</p>"
                },
                {
                    "step_number": 10,
                    "title": "10. When NOT to use",
                    "content": "<p>Never access a variable after calling <code>std::move(var)</code> on it. It is left in a 'valid but unspecified state'.</p>"
                },
                {
                    "step_number": 11,
                    "title": "11. Advantages",
                    "content": "<p>Drastic performance boost; eliminates unnecessary allocations; enables move-only types like <code>std::unique_ptr</code> and <code>std::thread</code>.</p>"
                },
                {
                    "step_number": 12,
                    "title": "12. Disadvantages",
                    "content": "<p>Use-after-move bugs if developers touch moved-from variables.</p>"
                },
                {
                    "step_number": 13,
                    "title": "13. Variations / Types",
                    "content": "<p>Rvalue references (<code>&&</code>), Universal/Forwarding references (<code>auto&&</code>, <code>T&&</code> in templates), <code>std::forward</code>.</p>"
                },
                {
                    "step_number": 14,
                    "title": "14. Common mistakes",
                    "content": "<p>Calling <code>std::move</code> on local variables returned by value (which inhibits <strong>NRVO - Named Return Value Optimization</strong>).</p>",
                    "callout": {
                        "type": "trap",
                        "title": "Pessimizing std::move Trap",
                        "text": "Writing `return std::move(localVar);` prevents NRVO (copy elision) where the compiler constructs the object directly in the caller's stack frame with ZERO copies or moves. Simply write `return localVar;`!"
                    }
                },
                {
                    "step_number": 15,
                    "title": "15. Interview questions",
                    "content": "<p><strong>Q:</strong> What is the difference between <code>std::move</code> and <code>std::forward</code>?</p>"
                },
                {
                    "step_number": 16,
                    "title": "16. Interview answer",
                    "content": "<p><strong>Answer:</strong> <code>std::move</code> performs an <strong>unconditional cast</strong> to an rvalue reference (<code>T&&</code>). <code>std::forward&lt;T&gt;</code> performs a <strong>conditional cast</strong>, preserving the original value category (lvalue remains lvalue, rvalue remains rvalue) inside template functions (Perfect Forwarding).</p>"
                },
                {
                    "step_number": 17,
                    "title": "17. Practice problem",
                    "content": "<p>Implement a sink constructor for a <code>Document</code> class taking a <code>std::vector&lt;std::string&gt;</code> and storing it via move semantics.</p>",
                    "practice": {
                        "title": "Move-Optimized Sink Constructor",
                        "problemStatement": "Write a Document class that accepts a vector of lines by value and moves it into member storage.",
                        "requirements": ["Constructor takes vector by value", "Uses std::move in initializer list", "Zero extra copies"],
                        "constraints": ["Const-correct getters"],
                        "hint": "Pass by value and std::move into the member variable.",
                        "expectedEntities": [
                            {"name": "Document", "responsibility": "Stores document lines efficiently."}
                        ],
                        "referenceCode": {
                            "filename": "document_sink.cpp",
                            "code": """#include <iostream>
#include <vector>
#include <string>

class Document {
private:
    std::string title;
    std::vector<std::string> lines;
public:
    Document(std::string t, std::vector<std::string> l)
        : title(std::move(t)), lines(std::move(l)) {}

    [[nodiscard]] size_t getLineCount() const noexcept { return lines.size(); }
};"""
                        }
                    }
                },
                {
                    "step_number": 18,
                    "title": "18. Summary",
                    "content": "<p>Move semantics is the superpower of modern C++, allowing zero-cost resource transfers and enabling true exclusive ownership patterns.</p>"
                }
            ]
        },

        # -------------------------------------------------------------
        # 11. Smart Pointers (unique_ptr, shared_ptr, weak_ptr)
        # -------------------------------------------------------------
        {
            "id": "smart-pointers-ownership",
            "title": "Smart Pointers (unique_ptr, shared_ptr, weak_ptr)",
            "description": "Modern C++ memory ownership models: exclusive ownership with std::unique_ptr, reference-counted std::shared_ptr, circular dependency resolution with std::weak_ptr, and custom deleters.",
            "sections": [
                {
                    "step_number": 1,
                    "title": "1. What is it?",
                    "content": "<p><strong>Smart Pointers</strong> are RAII wrapper classes that manage the lifetime of heap-allocated objects:<br>• <code>std::unique_ptr&lt;T&gt;</code>: Exclusive, single-owner pointer.<br>• <code>std::shared_ptr&lt;T&gt;</code>: Shared ownership via reference-counted control block.<br>• <code>std::weak_ptr&lt;T&gt;</code>: Non-owning observer that does not prevent object destruction.</p>"
                },
                {
                    "step_number": 2,
                    "title": "2. Why do we need it?",
                    "content": "<p>Raw pointers (<code>T*</code>) carry no ownership semantics: caller does not know whether to call <code>delete</code>, leading to memory leaks, dangling pointers, and double-free vulnerabilities. Smart pointers make ownership explicit in the type system.</p>"
                },
                {
                    "step_number": 3,
                    "title": "3. Core idea",
                    "content": "<p>Default to <code>std::unique_ptr</code> for 90% of Low-Level Design relationships (Composition, Factory returns). Use <code>std::shared_ptr</code> only when multiple components truly co-own an entity, and use <code>std::weak_ptr</code> to break cyclic dependency reference loops.</p>"
                },
                {
                    "step_number": 4,
                    "title": "4. How it works",
                    "content": "<p><code>std::unique_ptr</code> has zero runtime overhead (same size as raw pointer) and is move-only. <code>std::shared_ptr</code> stores a pointer to the object and a pointer to an atomic control block tracking <code>use_count</code> and <code>weak_count</code>. When <code>use_count</code> reaches 0, the object is destroyed.</p>"
                },
                {
                    "step_number": 5,
                    "title": "5. Visual explanation",
                    "content": "<p>Smart Pointer Ownership Models Comparison:</p>",
                    "comparison": {
                        "title": "Smart Pointers Ownership Comparison",
                        "columns": ["Smart Pointer", "Ownership Model", "Memory Overhead", "Copyable?", "Use Case in LLD"],
                        "rows": [
                            ["std::unique_ptr", "Exclusive (Single Owner)", "0 bytes (Same as raw pointer)", "No (Move Only)", "Factory returns, Composition, PImpl idiom"],
                            ["std::shared_ptr", "Shared (Co-owners)", "16-24 bytes (Control Block + Pointers)", "Yes (Increments use_count)", "Thread pool tasks, Shared caches, Observer publishers"],
                            ["std::weak_ptr", "Non-owning Observer", "16 bytes (Points to Control Block)", "Yes (Does not increment use_count)", "Breaking circular references, Cache observers"]
                        ]
                    }
                },
                {
                    "step_number": 6,
                    "title": "6. C++ implementation",
                    "content": "<p>Complete Smart Pointer Showcase: Exclusive Ownership, Shared Ownership, and Circular Reference Resolution:</p>",
                    "code_example": {
                        "filename": "smart_pointers_lld.cpp",
                        "code": """#include <iostream>
#include <memory>
#include <string>
#include <vector>

class Node {
public:
    std::string name;
    // Circular Reference Prevention: Use weak_ptr for parent pointer!
    std::weak_ptr<Node> parent;
    std::vector<std::shared_ptr<Node>> children;

    explicit Node(std::string nodeName) : name(std::move(nodeName)) {
        std::cout << "[Node " << name << "] Created.\\n";
    }

    ~Node() {
        std::cout << "[Node " << name << "] Destroyed.\\n";
    }

    void addChild(const std::shared_ptr<Node>& child) {
        children.push_back(child);
    }
};

// Factory producing unique_ptr
std::unique_ptr<Node> createRootNode(std::string name) {
    return std::make_unique<Node>(std::move(name));
}

int main() {
    std::cout << "--- 1. Unique Pointer Exclusive Ownership ---\\n";
    {
        std::unique_ptr<Node> root = createRootNode("RootNode");
        std::cout << "Root node active: " << root->name << "\\n";
    } // root destroyed immediately here

    std::cout << "\\n--- 2. Shared & Weak Pointer Tree ---\\n";
    {
        auto parent = std::make_shared<Node>("Parent");
        auto child = std::make_shared<Node>("Child");

        parent->addChild(child);
        child->parent = parent; // weak_ptr avoids cyclic leak!

        std::cout << "Parent use_count: " << parent.use_count() << " (Weak pointer does NOT increment)\\n";
        std::cout << "Child use_count: " << child.use_count() << "\\n";
    } // Both Parent and Child destroyed cleanly without memory leak!

    return 0;
}"""
                    }
                },
                {
                    "step_number": 7,
                    "title": "7. Code walkthrough",
                    "content": "<p><strong>Line 10 (<code>std::weak_ptr&lt;Node&gt; parent</code>):</strong> If parent had been a <code>std::shared_ptr</code>, <code>parent</code> would point to <code>child</code> and <code>child</code> would point to <code>parent</code>, keeping <code>use_count == 1</code> forever (Memory Leak). <code>std::weak_ptr</code> breaks the cycle!</p>"
                },
                {
                    "step_number": 8,
                    "title": "8. Real-world example",
                    "content": "<p>DOM Tree nodes, Observer subscriber lists, asynchronous event loop task delegates, and database connection pool lease tokens.</p>"
                },
                {
                    "step_number": 9,
                    "title": "9. When to use",
                    "content": "<p>Always use <code>std::make_unique</code> and <code>std::make_shared</code> instead of raw <code>new</code>. Use <code>unique_ptr</code> by default.</p>"
                },
                {
                    "step_number": 10,
                    "title": "10. When NOT to use",
                    "content": "<p>Do not pass <code>const std::shared_ptr&lt;T&gt;&</code> to functions that only need to read the object (pass <code>const T&</code> instead).</p>"
                },
                {
                    "step_number": 11,
                    "title": "11. Advantages",
                    "content": "<p>Completely eliminates memory leaks, dangling pointers, and manual delete calls; expressive ownership in APIs.</p>"
                },
                {
                    "step_number": 12,
                    "title": "12. Disadvantages",
                    "content": "<p><code>std::shared_ptr</code> incurs minor atomic increment/decrement overhead on copies and requires heap allocation for the control block.</p>"
                },
                {
                    "step_number": 13,
                    "title": "13. Variations / Types",
                    "content": "<p><code>std::unique_ptr&lt;T[]&gt;</code> arrays, custom deleters (e.g. for C APIs like <code>SDL_DestroyWindow</code> or <code>SSL_free</code>).</p>"
                },
                {
                    "step_number": 14,
                    "title": "14. Common mistakes",
                    "content": "<p>Creating two separate <code>shared_ptr</code> instances from the same raw pointer (creates two distinct control blocks, causing a double-free crash).</p>",
                    "callout": {
                        "type": "trap",
                        "title": "The Double Control Block Disaster",
                        "text": "Node* raw = new Node(); std::shared_ptr<Node> p1(raw); std::shared_ptr<Node> p2(raw); // CRASH: Two independent control blocks both delete raw pointer! Always use std::make_shared."
                    }
                },
                {
                    "step_number": 15,
                    "title": "15. Interview questions",
                    "content": "<p><strong>Q:</strong> Why is <code>std::make_shared</code> faster and more cache-friendly than <code>std::shared_ptr&lt;T&gt;(new T())</code>?</p>"
                },
                {
                    "step_number": 16,
                    "title": "16. Interview answer",
                    "content": "<p><strong>Answer:</strong> <code>std::make_shared</code> performs a <strong>single contiguous heap allocation</strong> for both the user object and the shared_ptr control block. <code>std::shared_ptr&lt;T&gt;(new T())</code> performs two separate allocations (one for the object via <code>new</code>, and another for the control block), doubling heap allocation overhead and degrading CPU cache locality.</p>"
                },
                {
                    "step_number": 17,
                    "title": "17. Practice problem",
                    "content": "<p>Write a factory method using a custom deleter with <code>std::unique_ptr</code> to manage a legacy C-style <code>FILE*</code> handle automatically.</p>",
                    "practice": {
                        "title": "Custom Deleter with unique_ptr",
                        "problemStatement": "Create a unique_ptr wrapper for FILE* with fclose as custom deleter.",
                        "requirements": [
                            "Use std::unique_ptr<FILE, decltype(&fclose)>",
                            "Auto-closes file on destruction",
                            "No manual fclose in caller"
                        ],
                        "constraints": ["Zero memory leaks"],
                        "hint": "Pass &std::fclose as the second constructor argument.",
                        "expectedEntities": [
                            {"name": "FileCloser", "responsibility": "Custom deleter for C file handles."}
                        ],
                        "referenceCode": {
                            "filename": "custom_deleter.cpp",
                            "code": """#include <iostream>
#include <memory>
#include <cstdio>

using UniqueFile = std::unique_ptr<FILE, decltype(&std::fclose)>;

UniqueFile makeUniqueFile(const char* path, const char* mode) {
    FILE* fp = std::fopen(path, mode);
    return UniqueFile(fp, &std::fclose);
}

int main() {
    auto file = makeUniqueFile("test.txt", "w");
    if (file) {
        std::fputs("Testing custom deleter\\n", file.get());
    } // std::fclose called automatically!
    return 0;
}"""
                        }
                    }
                },
                {
                    "step_number": 18,
                    "title": "18. Summary",
                    "content": "<p>Smart pointers make memory ownership crystal clear. By following <code>unique_ptr</code> by default, <code>shared_ptr</code> for co-ownership, and <code>weak_ptr</code> for cycle breaking, modern C++ systems achieve bulletproof memory safety.</p>"
                }
            ]
        }
    ]
}

out_file = Path("content/module_01.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(module_01_data, f, indent=2)

print(f"Successfully generated {out_file} with {len(module_01_data['topics'])} comprehensive topics!")
