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
# MODULE 03: C++ OOP Deep Dive
# ==============================================================================
mod_03 = {
    "module_id": "03",
    "title": "C++ OOP Deep Dive",
    "level": "Intermediate",
    "category": "OOP Core",
    "description": "Master advanced object-oriented mechanics in C++: Pure virtual functions, virtual destructors, object slicing, diamond problem with virtual inheritance, and dependency injection.",
    "topics": [
        {
            "id": "abstract-classes-interfaces",
            "title": "Abstract Classes & Pure Virtual Functions",
            "description": "Defining immutable API contracts with pure virtual functions (= 0) and interface segregation in C++.",
            "sections": [
                {
                    "step_number": 1,
                    "title": "1. What is it?",
                    "content": "<p>An <strong>Abstract Class</strong> is a class containing at least one <strong>Pure Virtual Function</strong> (syntax: <code>virtual void method() = 0;</code>). It defines an interface specification that cannot be instantiated directly.</p>"
                },
                {
                    "step_number": 2,
                    "title": "2. Why do we need it?",
                    "content": "<p>In large systems, modules must interact via stable behavioral contracts without binding to concrete subsystem implementations. Abstract classes enforce that derived classes implement required operations at compile time.</p>"
                },
                {
                    "step_number": 3,
                    "title": "3. Core idea",
                    "content": "<p>A pure virtual function acts as an obligatory checklist for subclasses. If a subclass fails to override even one pure virtual function, that subclass also becomes abstract and cannot be instantiated.</p>"
                },
                {
                    "step_number": 4,
                    "title": "4. How it works",
                    "content": "<p>The compiler sets the VTable entry for pure virtual functions to a null pointer or standard trap function (<code>__cxa_pure_virtual</code>). A derived class overrides this entry with its own function pointer.</p>"
                },
                {
                    "step_number": 5,
                    "title": "5. Visual explanation",
                    "content": "<p>Interface Contract Diagram:</p>",
                    "diagram": {
                        "title": "Abstract Database Connection Interface",
                        "classes": [
                            {
                                "name": "IDatabaseDriver",
                                "stereotype": "interface",
                                "isInterface": True,
                                "attributes": [],
                                "methods": [
                                    {"visibility": "+", "name": "connect", "params": "std::string connStr", "returnType": "virtual void = 0"},
                                    {"visibility": "+", "name": "executeQuery", "params": "std::string sql", "returnType": "virtual ResultSet = 0"}
                                ]
                            },
                            {
                                "name": "PostgresDriver",
                                "attributes": [{"visibility": "-", "name": "socketFd", "type": "int"}],
                                "methods": [
                                    {"visibility": "+", "name": "connect", "params": "std::string connStr", "returnType": "void override"},
                                    {"visibility": "+", "name": "executeQuery", "params": "std::string sql", "returnType": "ResultSet override"}
                                ]
                            }
                        ],
                        "relationships": [
                            {
                                "from": "PostgresDriver",
                                "to": "IDatabaseDriver",
                                "type": "inheritance",
                                "label": "realizes",
                                "ownership": "None",
                                "lifetime": "Polymorphic",
                                "coupling": "Decoupled",
                                "cppSyntax": "class PostgresDriver : public IDatabaseDriver"
                            }
                        ]
                    }
                },
                {
                    "step_number": 6,
                    "title": "6. C++ implementation",
                    "content": "<p>Clean Abstract Interface with Pure Virtual Destructor and Concrete Implementations:</p>",
                    "code_example": {
                        "filename": "abstract_interface_demo.cpp",
                        "code": """#include <iostream>
#include <memory>
#include <string>

// Pure Abstract Interface Contract
class ILogger {
public:
    // Pure virtual destructor MUST still have a body in C++
    virtual ~ILogger() = 0;
    virtual void logMessage(const std::string& level, const std::string& message) = 0;
};

// Definition of pure virtual destructor
inline ILogger::~ILogger() = default;

// Concrete Implementation 1: Console Logger
class ConsoleLogger : public ILogger {
public:
    void logMessage(const std::string& level, const std::string& message) override {
        std::cout << "[CONSOLE][" << level << "] " << message << "\\n";
    }
};

// Concrete Implementation 2: File Logger
class FileLogger : public ILogger {
public:
    void logMessage(const std::string& level, const std::string& message) override {
        std::cout << "[FILE_STREAM][" << level << "] " << message << " (flushed to disk)\\n";
    }
};

int main() {
    // Client code programs to interface
    std::unique_ptr<ILogger> logger = std::make_unique<ConsoleLogger>();
    logger->logMessage("INFO", "Application initialized successfully.");

    logger = std::make_unique<FileLogger>();
    logger->logMessage("WARN", "Disk capacity above 85%.");
    return 0;
}"""
                    }
                },
                {
                    "step_number": 7,
                    "title": "7. Code walkthrough",
                    "content": "<p><strong>Lines 6-11:</strong> <code>ILogger</code> has pure virtual functions <code>= 0</code>.<br><strong>Line 14:</strong> Pure virtual destructors must have an out-of-line body (<code>inline ILogger::~ILogger() = default;</code>) because derived destructors implicitly invoke the base destructor during cleanup.<br><strong>Lines 32-37:</strong> Demonstrates hot-swapping logger implementations seamlessly via <code>std::unique_ptr&lt;ILogger&gt;</code>.</p>"
                },
                {
                    "step_number": 8,
                    "title": "8. Real-world example",
                    "content": "<p>Operating system HALs (Hardware Abstraction Layers), graphics rendering APIs (Vulkan vs DirectX vs Metal), and cloud telemetry exporters.</p>"
                },
                {
                    "step_number": 9,
                    "title": "9. When to use",
                    "content": "<p>Use abstract classes whenever you want to define a strict API contract that multiple pluggable subclasses must fulfill.</p>"
                },
                {
                    "step_number": 10,
                    "title": "10. When NOT to use",
                    "content": "<p>Do not use abstract interfaces for concrete internal domain objects that have no polymorphic variations.</p>"
                },
                {
                    "step_number": 11,
                    "title": "11. Advantages",
                    "content": "<ul style='margin-left: 1.25rem;'><li>Compile-time verification of subclass completeness.</li><li>Zero-coupling dependency injection.</li><li>Clean mock injection for unit tests.</li></ul>"
                },
                {
                    "step_number": 12,
                    "title": "12. Disadvantages",
                    "content": "<p>Virtual function dispatch overhead ($O(1)$ VTable indirection).</p>"
                },
                {
                    "step_number": 13,
                    "title": "13. Variations / Types",
                    "content": "<p>Pure Interfaces (no member variables), Abstract Base Classes with shared state and helper methods.</p>"
                },
                {
                    "step_number": 14,
                    "title": "14. Common mistakes",
                    "content": "<p>Declaring a pure virtual destructor without providing a definition body, causing an unresolved external symbol linker error at runtime.</p>",
                    "callout": {
                        "type": "trap",
                        "title": "Pure Virtual Destructor Linker Trap",
                        "text": "Even if declared `virtual ~Base() = 0;`, you MUST provide a definition `Base::~Base() {}`. Destructors are always invoked in reverse hierarchy order during derived cleanup!"
                    }
                },
                {
                    "step_number": 15,
                    "title": "15. Interview questions",
                    "content": "<p><strong>Q:</strong> Can a pure virtual function have an implementation body in C++?</p>"
                },
                {
                    "step_number": 16,
                    "title": "16. Interview answer",
                    "content": "<p><strong>Answer:</strong> Yes! In C++, a pure virtual function can have a body defined outside the class (e.g. <code>void IBase::commonLogic() { ... }</code>). Derived classes must still explicitly override it, but they can choose to call the base implementation via <code>IBase::commonLogic()</code>.</p>"
                },
                {
                    "step_number": 17,
                    "title": "17. Practice problem",
                    "content": "<p>Design an <code>IAuthenticator</code> interface with pure virtual <code>authenticate(username, password)</code> and implement <code>OAuthAuthenticator</code> and <code>LdapAuthenticator</code>.</p>",
                    "practice": {
                        "title": "Pluggable Authenticator Interface",
                        "problemStatement": "Build an authentication abstraction supporting OAuth and LDAP backends.",
                        "requirements": [
                            "IAuthenticator with virtual ~IAuthenticator() = default",
                            "pure virtual bool authenticate(string u, string p) = 0",
                            "Concrete OAuth and LDAP classes"
                        ],
                        "constraints": ["Const-correct method signatures"],
                        "hint": "Return boolean success flags.",
                        "expectedEntities": [
                            {"name": "IAuthenticator", "responsibility": "Defines authentication contract."}
                        ],
                        "referenceCode": {
                            "filename": "auth_interface.cpp",
                            "code": """#include <iostream>
#include <string>

class IAuthenticator {
public:
    virtual ~IAuthenticator() = default;
    virtual bool authenticate(const std::string& username, const std::string& password) const = 0;
};

class OAuthAuthenticator : public IAuthenticator {
public:
    bool authenticate(const std::string& user, const std::string& pass) const override {
        std::cout << "[OAuth] Validated via token exchange for " << user << "\\n";
        return true;
    }
};"""
                        }
                    }
                },
                {
                    "step_number": 18,
                    "title": "18. Summary",
                    "content": "<p>Abstract classes and pure virtual functions are the foundation of decoupled, extensible, and clean Low-Level System Design in C++.</p>"
                }
            ]
        },
        {
            "id": "virtual-destructors",
            "title": "Virtual Destructors & Polymorphic Deletion",
            "description": "Why base classes with virtual functions must have virtual destructors to prevent fatal undefined behavior and memory leaks.",
            "sections": [
                {
                    "step_number": 1,
                    "title": "1. What is it?",
                    "content": "<p>A <strong>Virtual Destructor</strong> is a destructor declared with the <code>virtual</code> keyword in a base class (<code>virtual ~Base() = default;</code>) to guarantee that when a derived object is deleted through a base class pointer, the complete destructor chain executes in reverse hierarchy order.</p>"
                },
                {
                    "step_number": 2,
                    "title": "2. Why do we need it?",
                    "content": "<p>Deleting a derived object via a base pointer with a <em>non-virtual</em> destructor is <strong>Undefined Behavior (UB)</strong> according to the C++ Standard [§8.3.5]. The derived destructor is bypassed entirely, causing catastrophic memory leaks and unreleased OS resources.</p>"
                },
                {
                    "step_number": 3,
                    "title": "3. Core idea",
                    "content": "<p><em>'If a class has at least ONE virtual function, its destructor MUST be virtual.'</em></p>"
                },
                {
                    "step_number": 4,
                    "title": "4. How it works",
                    "content": "<p>When the destructor is virtual, its address is placed into the class's VTable. Calling <code>delete basePtr;</code> looks up the destructor dynamically, executing the derived destructor first, followed by base destructors.</p>"
                },
                {
                    "step_number": 5,
                    "title": "5. Visual explanation",
                    "content": "<p>Destructor call sequence comparison:</p>",
                    "comparison": {
                        "title": "Virtual vs Non-Virtual Destructor Deletion",
                        "columns": ["Scenario", "Destructor Call Order", "Derived Resources Freed?", "C++ Standard Status"],
                        "rows": [
                            ["Non-Virtual Destructor", "Base::~Base() ONLY", "✗ NO (Memory Leak!)", "Undefined Behavior (UB)"],
                            ["Virtual Destructor", "Derived::~Derived() -> Base::~Base()", "✓ YES (Complete cleanup)", "100% Safe & Standard"]
                        ]
                    }
                },
                {
                    "step_number": 6,
                    "title": "6. C++ implementation",
                    "content": "<p>Proof of Memory Leak with Non-Virtual vs Virtual Destructors:</p>",
                    "code_example": {
                        "filename": "virtual_destructor_proof.cpp",
                        "code": """#include <iostream>
#include <memory>

class BaseClean {
public:
    virtual ~BaseClean() {
        std::cout << "[BaseClean] Destructor executed.\\n";
    }
};

class DerivedResource : public BaseClean {
private:
    int* heavyBuffer;
public:
    DerivedResource() : heavyBuffer(new int[1000]) {
        std::cout << "[DerivedResource] Allocated 1000 ints on heap.\\n";
    }

    ~DerivedResource() override {
        delete[] heavyBuffer;
        std::cout << "[DerivedResource] Destructor executed: Freed 1000 ints.\\n";
    }
};

int main() {
    std::cout << "--- Safe Polymorphic Deletion ---\\n";
    BaseClean* polyPtr = new DerivedResource();
    // Because ~BaseClean is virtual, DerivedResource destructor runs first!
    delete polyPtr;
    return 0;
}"""
                    }
                },
                {
                    "step_number": 7,
                    "title": "7. Code walkthrough",
                    "content": "<p><strong>Line 5:</strong> <code>virtual ~BaseClean()</code> ensures <code>delete polyPtr</code> executes <code>DerivedResource::~DerivedResource()</code> before <code>BaseClean::~BaseClean()</code>, freeing the 1000-int heap buffer.</p>"
                },
                {
                    "step_number": 8,
                    "title": "8. Real-world example",
                    "content": "<p>Factory patterns creating plugins, UI controls, or database connections that are returned as <code>std::unique_ptr&lt;IBase&gt;</code>.</p>"
                },
                {
                    "step_number": 9,
                    "title": "9. When to use",
                    "content": "<p>Always declare base class destructors <code>virtual</code> if the class is designed for polymorphic inheritance.</p>"
                },
                {
                    "step_number": 10,
                    "title": "10. When NOT to use",
                    "content": "<p>Do not make destructors virtual for non-polymorphic value classes (like <code>std::vector</code>, <code>std::string</code>, or small math structs) because it injects an unnecessary 8-byte VPTR.</p>"
                },
                {
                    "step_number": 11,
                    "title": "11. Advantages",
                    "content": "<p>Guarantees complete resource reclamation and prevents undefined behavior.</p>"
                },
                {
                    "step_number": 12,
                    "title": "12. Disadvantages",
                    "content": "<p>8-byte VPTR overhead if the class had no other virtual functions.</p>"
                },
                {
                    "step_number": 13,
                    "title": "13. Variations / Types",
                    "content": "<p><code>virtual ~Base() = default;</code> (Preferred), <code>protected ~Base() = default;</code> (Disallows polymorphic deletion through base pointer).</p>"
                },
                {
                    "step_number": 14,
                    "title": "14. Common mistakes",
                    "content": "<p>Inheriting publicly from standard library containers (like <code>std::vector</code>) which have non-virtual destructors!</p>",
                    "callout": {
                        "type": "trap",
                        "title": "Inheriting from std::vector Trap",
                        "text": "class MyVector : public std::vector<int> { ... }; std::vector<int>* ptr = new MyVector(); delete ptr; // CATASTROPHIC UB: std::vector has no virtual destructor!"
                    }
                },
                {
                    "step_number": 15,
                    "title": "15. Interview questions",
                    "content": "<p><strong>Q:</strong> If a base class destructor is <code>protected</code> and non-virtual, what architectural constraint does it enforce?</p>"
                },
                {
                    "step_number": 16,
                    "title": "16. Interview answer",
                    "content": "<p><strong>Answer:</strong> A <code>protected</code> non-virtual destructor prevents callers from calling <code>delete basePtr;</code> (causing a compile-time error). It enforces that derived objects must be managed and deleted only through derived pointers, eliminating polymorphic deletion risks without paying for an 8-byte VPTR.</p>"
                },
                {
                    "step_number": 17,
                    "title": "17. Practice problem",
                    "content": "<p>Create a <code>PluginBase</code> class and verify that derived plugins clean up custom OS threads on destruction.</p>",
                    "practice": {
                        "title": "Plugin Cleanup Verification",
                        "problemStatement": "Implement PluginBase with virtual destructor to ensure thread shutdown.",
                        "requirements": ["virtual ~PluginBase()", "Derived plugin thread shutdown in destructor"],
                        "constraints": ["Zero memory leaks"],
                        "hint": "Mark destructor virtual in base.",
                        "expectedEntities": [
                            {"name": "PluginBase", "responsibility": "Base contract for dynamic plugins."}
                        ],
                        "referenceCode": {
                            "filename": "plugin_virtual_dtor.cpp",
                            "code": """#include <iostream>
#include <memory>

class PluginBase {
public:
    virtual ~PluginBase() { std::cout << "PluginBase destroyed\\n"; }
    virtual void run() = 0;
};

class AudioPlugin : public PluginBase {
public:
    ~AudioPlugin() override { std::cout << "AudioPlugin thread terminated cleanly\\n"; }
    void run() override {}
};"""
                        }
                    }
                },
                {
                    "step_number": 18,
                    "title": "18. Summary",
                    "content": "<p>Virtual destructors are a mandatory rule for polymorphic base classes in modern C++ Low-Level Design.</p>"
                }
            ]
        },
        {
            "id": "object-slicing",
            "title": "Object Slicing & Value Semantics Trap",
            "description": "Understanding object slicing when passing polymorphic objects by value, and how to defend against it.",
            "sections": [
                {
                    "step_number": 1,
                    "title": "1. What is it?",
                    "content": "<p><strong>Object Slicing</strong> occurs when a derived class object is assigned or passed by value to a base class object (<code>Base b = derivedObj;</code>). The derived portions (extra member variables and derived VTable) are literally sliced off, leaving only the base sub-object.</p>"
                },
                {
                    "step_number": 2,
                    "title": "2. Why do we need it?",
                    "content": "<p>Understanding object slicing is critical to avoid catastrophic bugs where polymorphism silently breaks because an object was passed by value instead of by reference/pointer.</p>"
                },
                {
                    "step_number": 3,
                    "title": "3. Core idea",
                    "content": "<p>Always pass polymorphic objects by <strong>reference</strong> (<code>const Base&</code>) or <strong>smart pointer</strong> (<code>std::unique_ptr&lt;Base&gt;</code>), NEVER by value.</p>"
                },
                {
                    "step_number": 4,
                    "title": "4. How it works",
                    "content": "<p>A <code>Base</code> object's memory is only large enough for <code>Base</code>'s members. When assigning a <code>Derived</code> object to a <code>Base</code> value, the copy constructor of <code>Base</code> executes, copying only the base fields and resetting the <code>vptr</code> to the <code>Base</code> VTable.</p>"
                },
                {
                    "step_number": 5,
                    "title": "5. Visual explanation",
                    "content": "<p>Slicing Diagram in Memory:</p>",
                    "callout": {
                        "type": "trap",
                        "title": "Memory Slicing Anatomy",
                        "text": "Derived Object: [Base Part: id, vptr_Derived] + [Derived Part: extraBuffer, customId]\\nPass By Value: Base b = derived; -> Copies ONLY [Base Part: id, vptr_BASE] -> [Derived Part] is discarded!"
                    }
                },
                {
                    "step_number": 6,
                    "title": "6. C++ implementation",
                    "content": "<p>Demonstrating Object Slicing Bug vs Reference Defense:</p>",
                    "code_example": {
                        "filename": "object_slicing_demo.cpp",
                        "code": """#include <iostream>
#include <string>

class Window {
public:
    virtual ~Window() = default;
    virtual void render() const {
        std::cout << "[Window] Generic window frame\\n";
    }
};

class ModalDialog : public Window {
private:
    std::string dialogTitle;
public:
    explicit ModalDialog(std::string title) : dialogTitle(std::move(title)) {}
    void render() const override {
        std::cout << "[ModalDialog] Rendered modal with title: '" << dialogTitle << "'\\n";
    }
};

// ❌ FLAWED: Passes by value -> Causes OBJECT SLICING!
void drawWindowSlices(Window w) {
    w.render(); // Calls Window::render(), NOT ModalDialog::render()!
}

// ✓ CORRECT: Passes by reference -> Preserves Polymorphism!
void drawWindowCorrect(const Window& w) {
    w.render(); // Calls ModalDialog::render() polymorphically!
}

int main() {
    ModalDialog dialog{"Save Changes?"};

    std::cout << "--- 1. Testing Flawed By-Value Function (Slicing) ---\\n";
    drawWindowSlices(dialog); // Output: [Window] Generic window frame

    std::cout << "\\n--- 2. Testing Correct By-Reference Function ---\\n";
    drawWindowCorrect(dialog); // Output: [ModalDialog] Rendered modal...
    return 0;
}"""
                    }
                },
                {
                    "step_number": 7,
                    "title": "7. Code walkthrough",
                    "content": "<p><strong>Line 21:</strong> <code>void drawWindowSlices(Window w)</code> slices the modal dialog into a plain <code>Window</code>.<br><strong>Line 26:</strong> <code>void drawWindowCorrect(const Window& w)</code> preserves the full <code>ModalDialog</code> instance in memory.</p>"
                },
                {
                    "step_number": 8,
                    "title": "8. Real-world example",
                    "content": "<p>Storing polymorphic objects inside standard containers: <code>std::vector&lt;Base&gt;</code> slices objects; use <code>std::vector&lt;std::unique_ptr&lt;Base&gt;&gt;</code> instead.</p>"
                },
                {
                    "step_number": 9,
                    "title": "9. When to use",
                    "content": "<p>Use value semantics for non-polymorphic Value Objects (e.g. <code>Money</code>, <code>Point2D</code>). Use reference semantics for polymorphic class hierarchies.</p>"
                },
                {
                    "step_number": 10,
                    "title": "10. When NOT to use",
                    "content": "<p>Never store polymorphic derived instances in a by-value base container (e.g. <code>std::vector&lt;Animal&gt;</code>).</p>"
                },
                {
                    "step_number": 11,
                    "title": "11. Advantages",
                    "content": "<p>Understanding slicing prevents silent logic bugs where overrides fail to execute.</p>"
                },
                {
                    "step_number": 12,
                    "title": "12. Disadvantages",
                    "content": "<p>Slicing is a C++ language quirk that does not produce a compile-time error by default.</p>"
                },
                {
                    "step_number": 13,
                    "title": "13. Variations / Types",
                    "content": "<p>Slicing during assignment (<code>b = d;</code>), Slicing during pass-by-value, Slicing during vector push_back.</p>"
                },
                {
                    "step_number": 14,
                    "title": "14. Common mistakes",
                    "content": "<p>Catching polymorphic exceptions by value (<code>catch (std::exception ex)</code> slices derived exception data; always write <code>catch (const std::exception& ex)</code>!).</p>"
                },
                {
                    "step_number": 15,
                    "title": "15. Interview questions",
                    "content": "<p><strong>Q:</strong> How can you make a polymorphic base class completely immune to object slicing at compile time?</p>"
                },
                {
                    "step_number": 16,
                    "title": "16. Interview answer",
                    "content": "<p><strong>Answer:</strong> Make the base class <strong>Abstract</strong> (at least one pure virtual function <code>= 0</code>) or delete/protect its copy constructor (<code>Base(const Base&) = delete;</code>). This causes the compiler to reject any attempt to instantiate or copy a <code>Base</code> object by value, eliminating slicing at compile time.</p>"
                },
                {
                    "step_number": 17,
                    "title": "17. Practice problem",
                    "content": "<p>Refactor a sliced <code>std::vector&lt;Employee&gt;</code> container into a memory-safe polymorphic <code>std::vector&lt;std::unique_ptr&lt;Employee&gt;&gt;</code> container.</p>",
                    "practice": {
                        "title": "Eliminating Vector Slicing",
                        "problemStatement": "Fix vector slicing by switching to unique_ptr storage.",
                        "requirements": ["Use std::vector<std::unique_ptr<Employee>>", "Demonstrate polymorphism"],
                        "constraints": ["No raw pointers"],
                        "hint": "Use std::make_unique<Manager>() and std::make_unique<Engineer>().",
                        "expectedEntities": [
                            {"name": "Employee", "responsibility": "Polymorphic base employee."}
                        ],
                        "referenceCode": {
                            "filename": "vector_slicing_fix.cpp",
                            "code": """#include <iostream>
#include <vector>
#include <memory>

class Employee {
public:
    virtual ~Employee() = default;
    virtual void work() const { std::cout << "General work\\n"; }
};

class Engineer : public Employee {
public:
    void work() const override { std::cout << "Writing clean C++20 code\\n"; }
};

int main() {
    std::vector<std::unique_ptr<Employee>> staff;
    staff.push_back(std::make_unique<Engineer>());
    staff[0]->work(); // Polymorphic!
    return 0;
}"""
                        }
                    }
                },
                {
                    "step_number": 18,
                    "title": "18. Summary",
                    "content": "<p>Defend against object slicing by passing polymorphic objects via references or smart pointers and making base classes abstract.</p>"
                }
            ]
        },
        {
            "id": "diamond-problem-virtual-inheritance",
            "title": "Diamond Problem & Virtual Inheritance",
            "description": "Resolving multiple inheritance ambiguity and duplicate base class instances using virtual base classes.",
            "sections": [
                {
                    "step_number": 1,
                    "title": "1. What is it?",
                    "content": "<p>The <strong>Diamond Problem</strong> occurs in multiple inheritance when a class derives from two classes that both inherit from a common base class. Without <strong>Virtual Inheritance</strong>, the most-derived class receives two duplicate copies of the common base class, creating ambiguity and wasted memory.</p>"
                },
                {
                    "step_number": 2,
                    "title": "2. Why do we need it?",
                    "content": "<p>In real-world architectures (like the standard C++ I/O stream hierarchy where <code>std::iostream</code> inherits from both <code>std::istream</code> and <code>std::ostream</code>, which both inherit from <code>std::ios_base</code>), duplicate base sub-objects corrupt shared state. Virtual inheritance guarantees exactly ONE shared base instance.</p>"
                },
                {
                    "step_number": 3,
                    "title": "3. Core idea",
                    "content": "<p>Use <code>virtual public Base</code> during intermediate inheritance: <code>class B : virtual public A</code>. This tells the compiler that class A is a shared virtual base.</p>"
                },
                {
                    "step_number": 4,
                    "title": "4. How it works",
                    "content": "<p>The compiler injects a <strong>Virtual Base Table Pointer (VBTR)</strong>. The most-derived class becomes directly responsible for constructing the shared virtual base class, bypassing intermediate constructors.</p>"
                },
                {
                    "step_number": 5,
                    "title": "5. Visual explanation",
                    "content": "<p>The Diamond Topology:</p>",
                    "diagram": {
                        "title": "Diamond Inheritance Structure",
                        "classes": [
                            {"name": "Device (Shared Virtual Base)", "attributes": [{"visibility": "#", "name": "deviceId", "type": "std::string"}]},
                            {"name": "Printer (virtual public Device)", "attributes": []},
                            {"name": "Scanner (virtual public Device)", "attributes": []},
                            {"name": "AllInOneMachine", "attributes": []}
                        ],
                        "relationships": [
                            {"from": "Printer", "to": "Device (Shared Virtual Base)", "type": "inheritance", "label": "virtual public"},
                            {"from": "Scanner", "to": "Device (Shared Virtual Base)", "type": "inheritance", "label": "virtual public"},
                            {"from": "AllInOneMachine", "to": "Printer", "type": "inheritance", "label": "public"},
                            {"from": "AllInOneMachine", "to": "Scanner", "type": "inheritance", "label": "public"}
                        ]
                    }
                },
                {
                    "step_number": 6,
                    "title": "6. C++ implementation",
                    "content": "<p>Complete Virtual Inheritance Solution for Diamond Problem:</p>",
                    "code_example": {
                        "filename": "diamond_virtual_inheritance.cpp",
                        "code": """#include <iostream>
#include <string>

// 1. Common Base Class
class Device {
protected:
    std::string deviceId;
public:
    explicit Device(std::string id) : deviceId(std::move(id)) {
        std::cout << "[Device] Constructed with ID: " << deviceId << "\\n";
    }
    virtual ~Device() = default;
    void printId() const {
        std::cout << "Device ID: " << deviceId << "\\n";
    }
};

// 2. Intermediate Class A: Uses virtual inheritance
class Printer : virtual public Device {
public:
    explicit Printer(std::string id) : Device(id) {}
    void printDocument() { std::cout << "[Printer " << deviceId << "] Printing page...\\n"; }
};

// 3. Intermediate Class B: Uses virtual inheritance
class Scanner : virtual public Device {
public:
    explicit Scanner(std::string id) : Device(id) {}
    void scanDocument() { std::cout << "[Scanner " << deviceId << "] Scanning optical document...\\n"; }
};

// 4. Most Derived Class: Directly initializes shared virtual base Device!
class CopierMachine : public Printer, public Scanner {
public:
    explicit CopierMachine(std::string id)
        : Device(id), Printer(id), Scanner(id) { // Direct initialization of Device
        std::cout << "[CopierMachine] Fully initialized.\\n";
    }
};

int main() {
    CopierMachine copier{"XEROX-PRO-9000"};
    // Zero ambiguity! Exactly ONE copy of deviceId exists.
    copier.printId();
    copier.printDocument();
    copier.scanDocument();
    return 0;
}"""
                    }
                },
                {
                    "step_number": 7,
                    "title": "7. Code walkthrough",
                    "content": "<p><strong>Lines 18 & 25:</strong> <code>virtual public Device</code> tells the compiler to share a single <code>Device</code> sub-object.<br><strong>Line 34:</strong> <code>CopierMachine</code> constructor directly calls <code>Device(id)</code>.<br><strong>Line 42:</strong> <code>copier.printId()</code> resolves with zero ambiguity!</p>"
                },
                {
                    "step_number": 8,
                    "title": "8. Real-world example",
                    "content": "<p>The standard library <code>std::iostream</code> (inheriting virtually from <code>std::basic_ios</code>).</p>"
                },
                {
                    "step_number": 9,
                    "title": "9. When to use",
                    "content": "<p>Use virtual inheritance when designing diamond class hierarchies that share common base state.</p>"
                },
                {
                    "step_number": 10,
                    "title": "10. When NOT to use",
                    "content": "<p>Avoid multiple inheritance with state altogether when composition or interface realization can be used instead.</p>"
                },
                {
                    "step_number": 11,
                    "title": "11. Advantages",
                    "content": "<p>Eliminates ambiguity and avoids duplicate base memory allocation.</p>"
                },
                {
                    "step_number": 12,
                    "title": "12. Disadvantages",
                    "content": "<p>Slight memory indirection overhead via virtual base pointer (VBTR); constructor delegation rules become complex.</p>"
                },
                {
                    "step_number": 13,
                    "title": "13. Variations / Types",
                    "content": "<p>Virtual Public, Virtual Protected, Virtual Private inheritance.</p>"
                },
                {
                    "step_number": 14,
                    "title": "14. Common mistakes",
                    "content": "<p>Forgetting to initialize the virtual base class from the most-derived constructor, leading to the default constructor being called unexpectedly.</p>"
                },
                {
                    "step_number": 15,
                    "title": "15. Interview questions",
                    "content": "<p><strong>Q:</strong> Who is responsible for calling the constructor of a virtual base class in C++?</p>"
                },
                {
                    "step_number": 16,
                    "title": "16. Interview answer",
                    "content": "<p><strong>Answer:</strong> In virtual inheritance, the <strong>most-derived class</strong> is directly responsible for invoking the constructor of the virtual base class. Intermediate classes' calls to the virtual base constructor are ignored during most-derived object instantiation.</p>"
                },
                {
                    "step_number": 17,
                    "title": "17. Practice problem",
                    "content": "<p>Model a <code>PoweredDevice</code>, <code>BatteryPowered</code>, <code>SolarPowered</code>, and <code>HybridSolarCar</code> hierarchy with virtual inheritance.</p>",
                    "practice": {
                        "title": "Hybrid Solar Car Virtual Inheritance",
                        "problemStatement": "Build a hybrid car hierarchy using virtual inheritance.",
                        "requirements": ["PoweredDevice virtual base", "HybridSolarCar resolves without ambiguity"],
                        "constraints": ["Zero member duplication"],
                        "hint": "Use virtual public PoweredDevice in intermediate classes.",
                        "expectedEntities": [
                            {"name": "PoweredDevice", "responsibility": "Shared power tracking base."}
                        ],
                        "referenceCode": {
                            "filename": "solar_hybrid.cpp",
                            "code": """#include <iostream>

class PoweredDevice {
public:
    int voltage;
    explicit PoweredDevice(int v) : voltage(v) {}
    virtual ~PoweredDevice() = default;
};

class BatteryPowered : virtual public PoweredDevice {
public:
    explicit BatteryPowered(int v) : PoweredDevice(v) {}
};

class SolarPowered : virtual public PoweredDevice {
public:
    explicit SolarPowered(int v) : PoweredDevice(v) {}
};

class HybridCar : public BatteryPowered, public SolarPowered {
public:
    explicit HybridCar(int v) : PoweredDevice(v), BatteryPowered(v), SolarPowered(v) {}
};"""
                        }
                    }
                },
                {
                    "step_number": 18,
                    "title": "18. Summary",
                    "content": "<p>Virtual inheritance solves the Diamond Problem by ensuring exactly one shared instance of a base class exists in the most-derived object.</p>"
                }
            ]
        },
        {
            "id": "composition-vs-inheritance",
            "title": "Composition vs Inheritance in C++",
            "description": "Architectural trade-offs: Why composition provides loose coupling, dynamic flexibility, and avoids brittle base class hierarchies.",
            "sections": [
                {
                    "step_number": 1,
                    "title": "1. What is it?",
                    "content": "<p><strong>Inheritance ('is-a')</strong> creates a compile-time static binding between a subclass and a base class. <strong>Composition ('has-a')</strong> builds complex systems by assembling independent component objects together at runtime.</p>"
                },
                {
                    "step_number": 2,
                    "title": "2. Why do we need it?",
                    "content": "<p>Overusing inheritance leads to the <strong>Brittle Base Class Problem</strong>: altering one base class method inadvertently breaks subclasses across the codebase. Composition keeps classes decoupled and easily testable.</p>"
                },
                {
                    "step_number": 3,
                    "title": "3. Core idea",
                    "content": "<p><em>'Favor object composition over class inheritance.'</em> Use inheritance ONLY for polymorphic interface contracts; use composition for code reuse and behavioral assembly.</p>"
                },
                {
                    "step_number": 4,
                    "title": "4. How it works",
                    "content": "<p>Instead of subclassing <code>class CustomSet : public std::vector</code>, compose the vector as a private member: <code>class CustomSet { std::vector&lt;int&gt; elements; };</code> and delegate only the necessary operations.</p>"
                },
                {
                    "step_number": 5,
                    "title": "5. Visual explanation",
                    "content": "<p>Comparison Table of Composition vs Inheritance:</p>",
                    "comparison": {
                        "title": "Composition vs Inheritance Matrix",
                        "columns": ["Dimension", "Inheritance ('is-a')", "Composition ('has-a')", "Architectural Verdict"],
                        "rows": [
                            ["Coupling", "White-box (High coupling to base internals)", "Black-box (Low coupling via public interface)", "Composition is far cleaner"],
                            ["Flexibility", "Fixed at compile time", "Can swap components at runtime", "Composition enables Strategy pattern"],
                            ["Encapsulation", "Exposes protected base state to subclasses", "Completely hides component state", "Composition preserves encapsulation"],
                            ["Testability", "Hard to isolate base behavior", "Easy to inject mock components", "Composition simplifies unit testing"]
                        ]
                    }
                },
                {
                    "step_number": 6,
                    "title": "6. C++ implementation",
                    "content": "<p>Refactoring Brittle Inheritance into Flexible Composition:</p>",
                    "code_example": {
                        "filename": "composition_refactor.cpp",
                        "code": """#include <iostream>
#include <memory>
#include <string>

// Strategy Interface for Engine behavior
class IEngine {
public:
    virtual ~IEngine() = default;
    virtual void start() = 0;
};

class V8GasolineEngine : public IEngine {
public:
    void start() override { std::cout << "[V8 Engine] Roaring with gasoline combustion!\\n"; }
};

class ElectricMotor : public IEngine {
public:
    void start() override { std::cout << "[Electric Motor] Silent high-torque acceleration!\\n"; }
};

// Car uses COMPOSITION: can switch engines dynamically at runtime!
class Vehicle {
private:
    std::string model;
    std::unique_ptr<IEngine> engine; // Composition of behavior

public:
    Vehicle(std::string m, std::unique_ptr<IEngine> eng)
        : model(std::move(m)), engine(std::move(eng)) {}

    void setEngine(std::unique_ptr<IEngine> newEngine) {
        engine = std::move(newEngine);
    }

    void drive() {
        std::cout << "[Vehicle: " << model << "] Starting drive:\\n  ";
        engine->start();
    }
};

int main() {
    Vehicle car{"Modular Roadster", std::make_unique<V8GasolineEngine>()};
    car.drive();

    std::cout << "\\n--- Upgrading Engine at Runtime via Composition ---\\n";
    car.setEngine(std::make_unique<ElectricMotor>());
    car.drive();
    return 0;
}"""
                    }
                },
                {
                    "step_number": 7,
                    "title": "7. Code walkthrough",
                    "content": "<p><strong>Line 23:</strong> <code>std::unique_ptr&lt;IEngine&gt; engine;</code> embeds the behavioral strategy.<br><strong>Line 30:</strong> <code>setEngine()</code> allows swapping propulsion algorithms at runtime—an impossibility with static class inheritance!</p>"
                },
                {
                    "step_number": 8,
                    "title": "8. Real-world example",
                    "content": "<p>Game entity component systems (ECS in Unity/Unreal), web server middleware pipelines, and customizable e-commerce pricing engines.</p>"
                },
                {
                    "step_number": 9,
                    "title": "9. When to use",
                    "content": "<p>Use composition whenever you need code reuse, dynamic component swapping, or loose coupling between subsystems.</p>"
                },
                {
                    "step_number": 10,
                    "title": "10. When NOT to use",
                    "content": "<p>Use inheritance only when there is a genuine polymorphic 'is-a' subtype relationship requiring Liskov substitution.</p>"
                },
                {
                    "step_number": 11,
                    "title": "11. Advantages",
                    "content": "<p>Eliminates class hierarchy explosion; allows dynamic behavior swapping; simplifies unit tests.</p>"
                },
                {
                    "step_number": 12,
                    "title": "12. Disadvantages",
                    "content": "<p>Requires writing forwarding/delegation methods.</p>"
                },
                {
                    "step_number": 13,
                    "title": "13. Variations / Types",
                    "content": "<p>Value Composition, Dynamic Strategy Composition (via interfaces), Delegation.</p>"
                },
                {
                    "step_number": 14,
                    "title": "14. Common mistakes",
                    "content": "<p>Inheriting from a class just to reuse one helper method (violates Liskov Substitution Principle).</p>"
                },
                {
                    "step_number": 15,
                    "title": "15. Interview questions",
                    "content": "<p><strong>Q:</strong> Why does composition adhere better to the Open/Closed Principle than inheritance?</p>"
                },
                {
                    "step_number": 16,
                    "title": "16. Interview answer",
                    "content": "<p><strong>Answer:</strong> With composition and interface pointers, new behaviors are added by writing new component classes and injecting them, requiring ZERO changes to the container class. With inheritance, modifying a base class affects all derived subclasses, risking regression bugs.</p>"
                },
                {
                    "step_number": 17,
                    "title": "17. Practice problem",
                    "content": "<p>Refactor an inheritance-based <code>Bird -&gt; FlyingBird / NonFlyingBird</code> hierarchy into a composed <code>Bird</code> with an injectable <code>IFlyingBehavior</code>.</p>",
                    "refactor": {
                        "title": "Refactoring Brittle Bird Hierarchy to Strategy Composition",
                        "problemSummary": "Inheritance forces all birds to inherit fly() methods, breaking Penguins and Ostriches.",
                        "violations": ["LSP violation when Penguin inherits fly()", "Rigid compile-time hierarchy"],
                        "badCode": {
                            "filename": "bad_bird_hierarchy.cpp",
                            "code": """class Bird {
public:
    virtual void fly() { std::cout << "Flying in sky\\n"; }
};
class Penguin : public Bird {
public:
    void fly() override { throw std::logic_error("Penguins cannot fly!"); } // LSP VIOLATION!
};"""
                        },
                        "goodCode": {
                            "filename": "clean_bird_composition.cpp",
                            "code": """class IFlyBehavior {
public:
    virtual ~IFlyBehavior() = default;
    virtual void performFly() = 0;
};
class FlyWithWings : public IFlyBehavior {
public:
    void performFly() override { std::cout << "Soaring through air\\n"; }
};
class NoFly : public IFlyBehavior {
public:
    void performFly() override { std::cout << "Cannot fly\\n"; }
};

class Bird {
    std::unique_ptr<IFlyBehavior> flyBehavior;
public:
    explicit Bird(std::unique_ptr<IFlyBehavior> fb) : flyBehavior(std::move(fb)) {}
    void fly() { flyBehavior->performFly(); }
};"""
                        },
                        "benefits": ["Zero LSP violations", "Penguins can swim, Eagles can soar"]
                    }
                },
                {
                    "step_number": 18,
                    "title": "18. Summary",
                    "content": "<p>Favoring composition over inheritance is the single most important design guideline for maintainable, decoupled object-oriented systems.</p>"
                }
            ]
        },
        {
            "id": "dependency-injection-delegation",
            "title": "Dependency Injection & Delegation Idioms",
            "description": "Constructor injection, interface delegation, inversion of control, and testable C++ architecture.",
            "sections": [
                {
                    "step_number": 1,
                    "title": "1. What is it?",
                    "content": "<p><strong>Dependency Injection (DI)</strong> is a technique where an object receives its dependencies from an external assembler rather than constructing them internally using <code>new</code>. <strong>Delegation</strong> is passing a method call directly to an internal helper object.</p>"
                },
                {
                    "step_number": 2,
                    "title": "2. Why do we need it?",
                    "content": "<p>Hardcoding <code>new MySQLDatabase()</code> inside a service makes unit testing impossible without running a live database. Dependency Injection allows passing mock objects effortlessly.</p>"
                },
                {
                    "step_number": 3,
                    "title": "3. Core idea",
                    "content": "<p>Objects should not know how to construct their dependencies; they should only declare what interfaces they require to perform their jobs.</p>"
                },
                {
                    "step_number": 4,
                    "title": "4. How it works",
                    "content": "<p>Dependencies are passed via <strong>Constructor Injection</strong> (preferred) or <strong>Setter Injection</strong> as <code>std::shared_ptr&lt;IInterface&gt;</code> or <code>std::unique_ptr&lt;IInterface&gt;</code>.</p>"
                },
                {
                    "step_number": 5,
                    "title": "5. Visual explanation",
                    "content": "<p>Dependency Injection Flow:</p>",
                    "callout": {
                        "type": "tip",
                        "title": "Inversion of Control (IoC)",
                        "text": "Traditional: Service -> creates -> ConcreteDatabase (High coupling)\\nDependency Injection: Main/Assembler -> injects -> Interface -> Service (Decoupled)"
                    }
                },
                {
                    "step_number": 6,
                    "title": "6. C++ implementation",
                    "content": "<p>Production-Grade Constructor Dependency Injection with Mock Testing:</p>",
                    "code_example": {
                        "filename": "dependency_injection_demo.cpp",
                        "code": """#include <iostream>
#include <memory>
#include <string>

// 1. Dependency Contract
class INotificationGateway {
public:
    virtual ~INotificationGateway() = default;
    virtual void send(const std::string& msg) = 0;
};

// 2. Production Implementation
class TwilioSmsGateway : public INotificationGateway {
public:
    void send(const std::string& msg) override {
        std::cout << "[Twilio Production API] Sent SMS: '" << msg << "'\\n";
    }
};

// 3. Test Mock Implementation
class MockNotificationGateway : public INotificationGateway {
public:
    int messagesSentCount{0};
    void send(const std::string& msg) override {
        ++messagesSentCount;
        std::cout << "[MOCK GATEWAY] Recorded test message: '" << msg << "'\\n";
    }
};

// 4. Domain Service with Constructor Dependency Injection
class UserService {
private:
    std::shared_ptr<INotificationGateway> notifier;
public:
    explicit UserService(std::shared_ptr<INotificationGateway> gateway)
        : notifier(std::move(gateway)) {}

    void registerUser(const std::string& username) {
        std::cout << "[UserService] User '" << username << "' registered in DB.\\n";
        notifier->send("Welcome to the platform, " + username + "!");
    }
};

int main() {
    std::cout << "--- 1. Running in Production Mode ---\\n";
    auto prodGateway = std::make_shared<TwilioSmsGateway>();
    UserService prodService(prodGateway);
    prodService.registerUser("alice_dev");

    std::cout << "\\n--- 2. Running in Unit Test Mode with Mock ---\\n";
    auto mockGateway = std::make_shared<MockNotificationGateway>();
    UserService testService(mockGateway);
    testService.registerUser("test_user_99");
    std::cout << "Assertions: Mock captured " << mockGateway->messagesSentCount << " message(s). (TEST PASSED)\\n";
    return 0;
}"""
                    }
                },
                {
                    "step_number": 7,
                    "title": "7. Code walkthrough",
                    "content": "<p><strong>Lines 30-34:</strong> <code>UserService</code> requires an <code>INotificationGateway</code> in its constructor.<br><strong>Lines 47-52:</strong> In unit tests, a lightweight mock is injected with zero network calls, verifying behavior instantly.</p>"
                },
                {
                    "step_number": 8,
                    "title": "8. Real-world example",
                    "content": "<p>Enterprise microservices, gRPC service handlers, and financial order processing systems.</p>"
                },
                {
                    "step_number": 9,
                    "title": "9. When to use",
                    "content": "<p>Always use Constructor Dependency Injection for external services, data storage, and network dependencies.</p>"
                },
                {
                    "step_number": 10,
                    "title": "10. When NOT to use",
                    "content": "<p>Do not inject primitive data structures (like <code>std::vector</code> or <code>std::string</code>) or trivial value objects.</p>"
                },
                {
                    "step_number": 11,
                    "title": "11. Advantages",
                    "content": "<p>100% testability; satisfies SOLID Dependency Inversion Principle; enables modular deployment.</p>"
                },
                {
                    "step_number": 12,
                    "title": "12. Disadvantages",
                    "content": "<p>Slight increase in constructor parameter boilerplate.</p>"
                },
                {
                    "step_number": 13,
                    "title": "13. Variations / Types",
                    "content": "<p>Constructor Injection, Setter Injection, Interface Injection, Dependency Injection Containers.</p>"
                },
                {
                    "step_number": 14,
                    "title": "14. Common mistakes",
                    "content": "<p>Using the Service Locator anti-pattern (a global registry that hides true dependencies) instead of explicit Constructor Injection.</p>"
                },
                {
                    "step_number": 15,
                    "title": "15. Interview questions",
                    "content": "<p><strong>Q:</strong> Why is Constructor Injection preferred over Setter Injection in C++?</p>"
                },
                {
                    "step_number": 16,
                    "title": "16. Interview answer",
                    "content": "<p><strong>Answer:</strong> Constructor Injection guarantees that the object is <strong>fully initialized and immutable</strong> with all required dependencies from the moment of construction. Setter Injection allows the object to exist in an incomplete, uninitialized state where calling methods before the setter triggers null pointer crashes.</p>"
                },
                {
                    "step_number": 17,
                    "title": "17. Practice problem",
                    "content": "<p>Implement an <code>OrderProcessor</code> that uses Constructor Injection to accept an <code>IPaymentGateway</code> and an <code>IInventoryRepository</code>.</p>",
                    "practice": {
                        "title": "Multi-Dependency Constructor Injection",
                        "problemStatement": "Build OrderProcessor taking payment gateway and inventory dependencies.",
                        "requirements": ["Constructor injection of two interfaces", "processOrder() coordinates both"],
                        "constraints": ["Zero concrete coupling"],
                        "hint": "Store both as shared_ptr interface members.",
                        "expectedEntities": [
                            {"name": "OrderProcessor", "responsibility": "Coordinates checkout workflow."}
                        ],
                        "referenceCode": {
                            "filename": "order_proc_di.cpp",
                            "code": """#include <iostream>
#include <memory>

class IPay { public: virtual ~IPay() = default; virtual bool charge() = 0; };
class IInv { public: virtual ~IInv() = default; virtual void reserve() = 0; };

class OrderProcessor {
    std::shared_ptr<IPay> payment;
    std::shared_ptr<IInv> inventory;
public:
    OrderProcessor(std::shared_ptr<IPay> p, std::shared_ptr<IInv> i)
        : payment(std::move(p)), inventory(std::move(i)) {}
    void checkout() {
        inventory->reserve();
        payment->charge();
    }
};"""
                        }
                    }
                },
                {
                    "step_number": 18,
                    "title": "18. Summary",
                    "content": "<p>Dependency Injection decouples high-level policy from low-level execution, enabling testable and production-ready object-oriented systems.</p>"
                }
            ]
        }
    ]
}

write_module(mod_03)
