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

def make_18_step_topic(topic_id, title, desc, what_is, why_need, core_idea, how_works, visual_dict, code_filename, code_content, walkthrough, real_world, when_use, when_not_use, advantages, disadvantages, variations, mistakes, q_text, a_text, practice_title, practice_stmt, practice_code):
    sections = [
        {"step_number": 1, "title": "1. What is it?", "content": f"<p>{what_is}</p>"},
        {"step_number": 2, "title": "2. Why do we need it?", "content": f"<p>{why_need}</p>"},
        {"step_number": 3, "title": "3. Core idea", "content": f"<p>{core_idea}</p>"},
        {"step_number": 4, "title": "4. How it works", "content": f"<p>{how_works}</p>"}
    ]
    sec_5 = {"step_number": 5, "title": "5. Visual explanation", "content": "<p>Visual Architecture & Mechanics:</p>"}
    if "diagram" in visual_dict: sec_5["diagram"] = visual_dict["diagram"]
    elif "comparison" in visual_dict: sec_5["comparison"] = visual_dict["comparison"]
    elif "callout" in visual_dict: sec_5["callout"] = visual_dict["callout"]
    elif "animation" in visual_dict: sec_5["animation"] = visual_dict["animation"]
    sections.append(sec_5)
    sections.append({"step_number": 6, "title": "6. C++ implementation", "content": "<p>Complete Production C++20 Implementation:</p>", "code_example": {"filename": code_filename, "code": code_content}})
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
    sections.append({
        "step_number": 17, "title": "17. Practice problem", "content": f"<p>{practice_stmt}</p>",
        "practice": {
            "title": practice_title, "problemStatement": practice_stmt,
            "requirements": ["Production C++20 code", "Adhere to design pattern"],
            "constraints": ["Zero memory leaks"], "hint": "Follow GoF pattern structure.",
            "expectedEntities": [{"name": practice_title, "responsibility": "Pattern implementation."}],
            "referenceCode": {"filename": "pattern_sol.cpp", "code": practice_code}
        }
    })
    sections.append({"step_number": 18, "title": "18. Summary", "content": f"<p>Mastering {title} is essential for advanced Low-Level Design interviews.</p>"})
    return {"id": topic_id, "title": title, "description": desc, "sections": sections}

# ==============================================================================
# MODULE 09: Creational Patterns
# ==============================================================================
mod_09 = {
    "module_id": "09",
    "title": "Creational Design Patterns",
    "level": "Intermediate",
    "category": "Design Patterns",
    "description": "Singleton (Meyers & Thread-safe), Factory Method, Abstract Factory, Builder, and Prototype in modern C++.",
    "topics": [
        make_18_step_topic(
            "singleton-pattern", "Singleton (Meyers Singleton & Concurrency)",
            "Ensuring a class has exactly one instance and providing a global point of access.",
            "The <strong>Singleton Pattern</strong> guarantees that a class has only one instance and provides a global access point to that instance.",
            "Useful for shared physical resources: Logger instance, Thread Pool coordinator, Hardware Device Controller.",
            "Private constructor + Deleted copy/move operations + Static instance method (Meyers Singleton).",
            "In C++11 and later, static local variable initialization in a function is guaranteed by the language standard to be <strong>thread-safe without manual mutex locks</strong> (Meyers Singleton).",
            {"callout": {"type": "important", "title": "Meyers Singleton Thread Safety", "text": "C++11 Standard [§6.7]: Static local variables are initialized exactly once, even when accessed simultaneously by multiple threads. Zero manual mutex locking required!"}},
            "meyers_singleton.cpp",
            """#include <iostream>
#include <string>

class Logger {
private:
    Logger() { std::cout << "[Logger] Initialized singleton instance.\\n"; }
    ~Logger() = default;

public:
    // Delete copy and move constructors/assignments
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;
    Logger(Logger&&) = delete;
    Logger& operator=(Logger&&) = delete;

    // Meyers Singleton: Thread-safe static local instance!
    static Logger& getInstance() {
        static Logger instance; // Initialized thread-safely on first call
        return instance;
    }

    void log(const std::string& msg) {
        std::cout << "[LOG] " << msg << "\\n";
    }
};

int main() {
    Logger::getInstance().log("System booted");
    Logger::getInstance().log("Processing transaction");
    return 0;
}""",
            "Meyers Singleton using static local variable, deleted copy/move, thread-safe access.",
            "Application Configuration Managers, Database Connection Pools, Hardware Serial Ports.",
            "Use when exactly one coordinating instance must exist across the entire process lifetime.",
            "Do not use as a glorified global variable bag; harms testability.",
            "Guaranteed single instance, lazy initialization, zero manual mutex overhead.",
            "Hidden dependencies; difficult to unit test with mock replacements.",
            "Meyers Singleton, Eager Singleton, Double-Checked Locking Pattern (legacy).",
            "Writing complex manual Double-Checked Locking with mutexes when Meyers Singleton is 10x cleaner.",
            "Why is Meyers Singleton thread-safe in C++11?",
            "The C++11 standard mandates that local static variables are initialized concurrently safe by the runtime during first function entry (magic statics).",
            "ConfigurationManager Singleton",
            "Build a thread-safe ConfigurationManager singleton.",
            "class Config { Config() = default; public: Config(const Config&) = delete; static Config& get() { static Config inst; return inst; } };"
        ),
        make_18_step_topic(
            "factory-method-pattern", "Factory Method Pattern",
            "Defining an interface for creating an object, but letting subclasses decide which class to instantiate.",
            "<strong>Factory Method</strong> defines an interface for creating objects, but lets derived subclasses or static factory routines decide which concrete class to instantiate.",
            "Decouples client creation code from concrete derived class constructors.",
            "Call a creation method instead of calling <code>new ConcreteClass()</code> directly.",
            "Client calls <code>VehicleFactory::createVehicle(type)</code> returning a <code>std::unique_ptr&lt;IVehicle&gt;</code>.",
            {"callout": {"type": "tip", "title": "Factory Method Flow", "text": "Client -> Factory::create(type) -> returns std::unique_ptr<IVehicle> -> Client uses interface"}},
            "factory_method.cpp",
            """#include <iostream>
#include <memory>
#include <string>

enum class VehicleType { CAR, BIKE, TRUCK };

class IVehicle { public: virtual ~IVehicle() = default; virtual void drive() = 0; };
class Car : public IVehicle { public: void drive() override { std::cout << "Driving Car\\n"; } };
class Bike : public IVehicle { public: void drive() override { std::cout << "Riding Bike\\n"; } };
class Truck : public IVehicle { public: void drive() override { std::cout << "Hauling Truck\\n"; } };

class VehicleFactory {
public:
    static std::unique_ptr<IVehicle> createVehicle(VehicleType type) {
        switch (type) {
            case VehicleType::CAR: return std::make_unique<Car>();
            case VehicleType::BIKE: return std::make_unique<Bike>();
            case VehicleType::TRUCK: return std::make_unique<Truck>();
        }
        throw std::invalid_argument("Unknown vehicle type");
    }
};""",
            "VehicleFactory centralizes construction and returns unique_ptr interface.",
            "Document parsing (PDF vs Word vs JSON), payment gateway selection.",
            "Use when creation logic involves complex decisions or varies based on parameters.",
            "Do not use for trivial classes that only have a single constructor.",
            "Adheres to Single Responsibility & Open/Closed principles.",
            "Requires creating factory abstractions.",
            "Static Factory Method, Polymorphic Factory Method (Virtual Creator).",
            "Returning raw pointers instead of std::unique_ptr.",
            "Why should Factory Methods return std::unique_ptr in modern C++?",
            "Because std::unique_ptr explicitly expresses exclusive ownership transfer from the factory to the caller with zero memory leak risk.",
            "Document Parser Factory",
            "Build a DocumentParser factory for JSON and XML.",
            "class Parser { public: virtual ~Parser() = default; }; class Factory { public: static std::unique_ptr<Parser> create(int); };"
        ),
        make_18_step_topic(
            "abstract-factory-pattern", "Abstract Factory Pattern",
            "Creating families of related or dependent objects without specifying their concrete classes.",
            "<strong>Abstract Factory</strong> provides an interface for creating families of related or dependent objects (e.g. Mac vs Windows UI buttons and scrollbars).",
            "Ensures that products from the same family are always used together without mixing incompatible UI components.",
            "A factory of factories: <code>IGUIFactory</code> creates both <code>IButton</code> and <code>IScrollBar</code>.",
            "Client receives an <code>IGUIFactory</code> (e.g. <code>MacFactory</code>) and creates all UI components from it consistently.",
            {"diagram": {
                "title": "Abstract Factory Structure",
                "classes": [
                    {"name": "IGUIFactory", "stereotype": "interface", "isInterface": True, "attributes": [], "methods": [{"visibility": "+", "name": "createButton", "params": "", "returnType": "IButton*"}, {"visibility": "+", "name": "createScrollbar", "params": "", "returnType": "IScrollbar*"}]},
                    {"name": "MacFactory", "attributes": [], "methods": [{"visibility": "+", "name": "createButton", "params": "", "returnType": "MacButton*"}, {"visibility": "+", "name": "createScrollbar", "params": "", "returnType": "MacScrollbar*"}]}
                ],
                "relationships": []
            }},
            "abstract_factory_ui.cpp",
            """#include <iostream>
#include <memory>

class IButton { public: virtual ~IButton() = default; virtual void render() = 0; };
class IScrollbar { public: virtual ~IScrollbar() = default; virtual void scroll() = 0; };

class WindowsButton : public IButton { public: void render() override { std::cout << "Windows Style Button\\n"; } };
class WindowsScrollbar : public IScrollbar { public: void scroll() override { std::cout << "Windows Scroll\\n"; } };

class MacButton : public IButton { public: void render() override { std::cout << "Mac Glassmorphism Button\\n"; } };
class MacScrollbar : public IScrollbar { public: void scroll() override { std::cout << "Mac Smooth Scroll\\n"; } };

// Abstract Factory
class IUIFactory {
public:
    virtual ~IUIFactory() = default;
    virtual std::unique_ptr<IButton> createButton() = 0;
    virtual std::unique_ptr<IScrollbar> createScrollbar() = 0;
};

class WindowsFactory : public IUIFactory {
public:
    std::unique_ptr<IButton> createButton() override { return std::make_unique<WindowsButton>(); }
    std::unique_ptr<IScrollbar> createScrollbar() override { return std::make_unique<WindowsScrollbar>(); }
};

class MacFactory : public IUIFactory {
public:
    std::unique_ptr<IButton> createButton() override { return std::make_unique<MacButton>(); }
    std::unique_ptr<IScrollbar> createScrollbar() override { return std::make_unique<MacScrollbar>(); }
};""",
            "MacFactory and WindowsFactory create matching UI component suites.",
            "Cross-platform OS rendering engines (Qt, Flutter), Database driver suites (Postgres vs Oracle connection+command+transaction).",
            "Use when an application needs to configure full product families consistently.",
            "Do not use when you only need to instantiate single unrelated objects (use Factory Method).",
            "Guarantees product compatibility across a family.",
            "Adding a new product type requires modifying the abstract factory interface.",
            "Cross-platform Theme Factories, Database Driver Suites.",
            "Mixing components from different concrete factories.",
            "What is the difference between Factory Method and Abstract Factory?",
            "Factory Method creates ONE product using inheritance/delegation. Abstract Factory creates FAMILIES of related products using object composition.",
            "Dark/Light Theme Factory",
            "Implement a Theme factory producing Panels and Buttons.",
            "class ITheme { public: virtual ~ITheme() = default; virtual std::unique_ptr<IButton> btn() = 0; };"
        ),
        make_18_step_topic(
            "builder-pattern", "Builder Pattern & Fluent Interfaces",
            "Separating the construction of a complex object from its representation.",
            "<strong>Builder Pattern</strong> constructs complex objects step-by-step, allowing the same construction process to create different representations.",
            "Constructors with 10+ parameters (Telescoping Constructor anti-pattern) are error-prone.",
            "Step-by-step configuration via fluent method chaining returning <code>*this</code> or dedicated Director.",
            "<code>HttpRequest::Builder().setUrl(\"...\").setMethod(\"POST\").build()</code>.",
            {"callout": {"type": "tip", "title": "Telescoping Constructor Solution", "text": "Before: Pizza(size, cheese, pepperoni, bacon, olives, onions, mushrooms...) -> Horrible!\\nAfter: Pizza::Builder().setSize(12).addCheese().addPepperoni().build();"}},
            "builder_pattern.cpp",
            """#include <iostream>
#include <string>

class UserProfile {
public:
    std::string username;
    std::string email;
    int age{0};
    std::string bio;

    class Builder {
    private:
        UserProfile profile;
    public:
        Builder& setUsername(std::string u) { profile.username = std::move(u); return *this; }
        Builder& setEmail(std::string e) { profile.email = std::move(e); return *this; }
        Builder& setAge(int a) { profile.age = a; return *this; }
        Builder& setBio(std::string b) { profile.bio = std::move(b); return *this; }
        UserProfile build() { return std::move(profile); }
    };
};

int main() {
    UserProfile user = UserProfile::Builder()
                        .setUsername("prshobhit")
                        .setEmail("prshobhit@example.com")
                        .setAge(25)
                        .setBio("C++ System Architect")
                        .build();
    std::cout << "User: " << user.username << " (" << user.email << ")\\n";
    return 0;
}""",
            "Nested Builder class constructing UserProfile step-by-step with clean fluent syntax.",
            "SQL Query Builders, HTTP Request Builders, Game Character Customizers.",
            "Use when constructing objects with multiple optional configuration parameters.",
            "Do not use for simple objects with 1-3 mandatory fields.",
            "Readable, self-documenting code; avoids telescoping constructors.",
            "Requires creating a separate Builder class.",
            "Fluent Builder, Director-driven Builder, Inner Static Builder.",
            "Forgetting to validate required fields inside build().",
            "What problem does the Builder pattern solve?",
            "It eliminates Telescoping Constructors (constructors with dozens of confusing parameters) and supports step-by-step immutable object creation.",
            "Computer Hardware Builder",
            "Build a Computer configuration builder (CPU, RAM, GPU, Storage).",
            "class Computer { public: class Builder { /* fluent methods */ }; };"
        ),
        make_18_step_topic(
            "prototype-pattern", "Prototype Pattern & Virtual Clone Idiom",
            "Creating new objects by copying an existing instance using virtual clone methods.",
            "<strong>Prototype Pattern</strong> creates new objects by duplicating existing instances (cloning) rather than going through fresh constructor initialization.",
            "When creating an object from scratch is computationally expensive (e.g. Loading 3D mesh files or database lookups).",
            "Virtual copy constructor: <code>virtual std::unique_ptr&lt;IShape&gt; clone() const = 0;</code>.",
            "Subclasses implement <code>clone()</code> by calling their copy constructor and returning a new <code>std::unique_ptr</code>.",
            {"callout": {"type": "tip", "title": "Virtual Copy Idiom", "text": "C++ has no virtual copy constructor by default. The Prototype Pattern solves this by adding virtual clone() const = 0!"}},
            "prototype_pattern.cpp",
            """#include <iostream>
#include <memory>
#include <string>

class IPrototype {
public:
    virtual ~IPrototype() = default;
    virtual std::unique_ptr<IPrototype> clone() const = 0;
    virtual void render() const = 0;
};

class Monster : public IPrototype {
private:
    std::string type;
    int health;
public:
    Monster(std::string t, int hp) : type(std::move(t)), health(hp) {}

    // Virtual clone implementation
    std::unique_ptr<IPrototype> clone() const override {
        return std::make_unique<Monster>(*this); // Uses copy constructor
    }

    void render() const override {
        std::cout << "[Monster: " << type << "] HP: " << health << "\\n";
    }
};

int main() {
    auto originalOrc = std::make_unique<Monster>("Orc Warrior", 100);
    // Clone prototype instantly without re-reading assets
    auto clonedOrc = originalOrc->clone();
    clonedOrc->render();
    return 0;
}""",
            "Virtual clone method returning unique_ptr copy of Monster instance.",
            "Game NPC spawning, Graphic shape stamping tools, Network packet template duplicating.",
            "Use when object creation cost is high or when cloning objects of unknown runtime types.",
            "Do not use when objects hold non-copyable unique handles.",
            "Fast $O(1)$ object spawning; polymorphic copy capability.",
            "Deep copying complex circular reference graphs can be challenging.",
            "Shallow Prototype, Deep Prototype with custom copy-and-swap.",
            "Performing shallow copies on internal heap pointers.",
            "How do you implement a Virtual Copy Constructor in C++?",
            "By declaring a pure virtual clone method (e.g. virtual unique_ptr<Base> clone() const = 0;) and implementing it in derived classes using return make_unique<Derived>(*this);.",
            "Game Bullet Prototype",
            "Implement Bullet prototype with clone() for high-speed particle spawning.",
            "class Bullet { public: virtual std::unique_ptr<Bullet> clone() const { return std::make_unique<Bullet>(*this); } };"
        )
    ]
}

# ==============================================================================
# MODULE 10: Structural Patterns
# ==============================================================================
mod_10 = {
    "module_id": "10",
    "title": "Structural Design Patterns",
    "level": "Intermediate",
    "category": "Design Patterns",
    "description": "Adapter, Bridge, Composite, Decorator, Facade, Flyweight, and Proxy with animated object graphs.",
    "topics": [
        make_18_step_topic(
            "adapter-pattern", "Adapter Pattern (Class & Object Adapter)",
            "Converting the interface of a class into another interface clients expect.",
            "The <strong>Adapter Pattern</strong> acts as a bridge between two incompatible interfaces, allowing classes with mismatched APIs to collaborate seamlessly.",
            "Reusing legacy libraries or 3rd-party vendor SDKs without modifying their source code.",
            "Wrap the incompatible adaptee inside an adapter class that implements the target interface.",
            "Client calls <code>targetInterface->request()</code>, and Adapter translates it to <code>adaptee->legacySpecificRequest()</code>.",
            {"callout": {"type": "tip", "title": "Object Adapter Structure", "text": "Client -> Target Interface <- [Adapter (has Adaptee)] -> calls Adaptee::legacyMethod()"}},
            "adapter_pattern.cpp",
            """#include <iostream>
#include <memory>
#include <string>

// Target Interface expected by modern client
class INewPaymentGateway {
public:
    virtual ~INewPaymentGateway() = default;
    virtual void processPayment(const std::string& customerId, double dollars) = 0;
};

// Incompatible 3rd Party Legacy Adaptee
class LegacyBankApi {
public:
    void transferCents(long cents, const char* accountNum) {
        std::cout << "[LegacyBank] Transferred " << cents << " cents to " << accountNum << "\\n";
    }
};

// Object Adapter: Implements INewPaymentGateway using LegacyBankApi
class BankPaymentAdapter : public INewPaymentGateway {
private:
    std::shared_ptr<LegacyBankApi> legacyApi;
public:
    explicit BankPaymentAdapter(std::shared_ptr<LegacyBankApi> api) : legacyApi(std::move(api)) {}

    void processPayment(const std::string& customerId, double dollars) override {
        long cents = static_cast<long>(dollars * 100.0);
        legacyApi->transferCents(cents, customerId.c_str());
    }
};

int main() {
    auto legacy = std::make_shared<LegacyBankApi>();
    std::unique_ptr<INewPaymentGateway> gateway = std::make_unique<BankPaymentAdapter>(legacy);
    gateway->processPayment("CUST_9918", 49.99);
    return 0;
}""",
            "BankPaymentAdapter bridges modern dollars/string interface to legacy cents/char* API.",
            "Payment gateway wrappers, UI graphics compatibility layers, file format converters.",
            "Use when integrating third-party code whose interface cannot be changed.",
            "Do not use when you have full control to refactor the original API directly.",
            "Separation of concerns; satisfies Open/Closed Principle.",
            "Introduces extra wrapper layer indirection.",
            "Object Adapter (Composition - preferred), Class Adapter (Multiple Inheritance).",
            "Leaking adaptee-specific exceptions through the adapter interface.",
            "What is the difference between Class Adapter and Object Adapter in C++?",
            "Object Adapter uses <strong>Composition</strong> (Adapter contains a pointer to Adaptee). Class Adapter uses <strong>Multiple Inheritance</strong> (Adapter inherits publicly from Target and privately from Adaptee).",
            "XML to JSON Adapter",
            "Build an adapter that translates JSON logger calls to a legacy XML printer.",
            "class XmlAdapter : public IJsonLogger { LegacyXml xml; public: void logJson(string j) override {} };"
        ),
        make_18_step_topic(
            "bridge-pattern", "Bridge Pattern",
            "Decoupling an abstraction from its implementation so that the two can vary independently.",
            "The <strong>Bridge Pattern</strong> splits a large class into two separate hierarchies: Abstraction (high-level logic) and Implementation (platform-specific execution).",
            "Prevents a Cartesian product explosion of classes (e.g., WindowsCircle, LinuxCircle, WindowsSquare, LinuxSquare = $M \times N$ classes).",
            "Abstraction holds a pointer to <code>IImplementation</code>: $M + N$ classes instead of $M \times N$.",
            "<code>Shape</code> (Abstraction) holds a pointer to <code>IRenderEngine</code> (Implementation).",
            {"comparison": {
                "title": "Class Explosion vs Bridge Solution",
                "columns": ["Design", "2 Shapes + 3 Operating Systems", "Total Classes Required"],
                "rows": [
                    ["Without Bridge", "WinCircle, LinuxCircle, MacCircle, WinSquare, LinuxSquare, MacSquare", "6 classes (M * N)"],
                    ["With Bridge", "2 Shapes (Circle, Square) + 3 Renderers (Win, Linux, Mac)", "5 classes (M + N)"]
                ]
            }},
            "bridge_pattern.cpp",
            """#include <iostream>
#include <memory>

// Implementation Hierarchy Contract
class IRenderer {
public:
    virtual ~IRenderer() = default;
    virtual void renderCircle(double r) = 0;
};

class DirectXRenderer : public IRenderer {
public:
    void renderCircle(double r) override { std::cout << "[DirectX] Rendered circle radius " << r << "\\n"; }
};

class OpenGLRenderer : public IRenderer {
public:
    void renderCircle(double r) override { std::cout << "[OpenGL] Rendered circle radius " << r << "\\n"; }
};

// Abstraction Hierarchy
class Shape {
protected:
    std::shared_ptr<IRenderer> renderer; // The Bridge!
public:
    explicit Shape(std::shared_ptr<IRenderer> r) : renderer(std::move(r)) {}
    virtual ~Shape() = default;
    virtual void draw() = 0;
};

class Circle : public Shape {
    double radius;
public:
    Circle(double r, std::shared_ptr<IRenderer> rend) : Shape(std::move(rend)), radius(r) {}
    void draw() override { renderer->renderCircle(radius); }
};

int main() {
    auto dx = std::make_shared<DirectXRenderer>();
    auto ogl = std::make_shared<OpenGLRenderer>();

    Circle c1{5.0, dx};
    Circle c2{10.0, ogl};
    c1.draw();
    c2.draw();
    return 0;
}""",
            "Shape delegates rendering to IRenderer bridge pointer, decoupling geometry from graphics.",
            "Cross-platform OS windowing (GUI window vs platform window handles), Database drivers.",
            "Use when you want to avoid compile-time binding between abstraction and implementation.",
            "Do not use when there is only one fixed platform implementation.",
            "Solves combinatorial class explosion; hides platform details.",
            "Increases design complexity with dual hierarchies.",
            "Bridge, PImpl Idiom (specific single-class bridge in C++).",
            "Confusing Bridge with Adapter (Bridge is designed up-front; Adapter retrofits existing code).",
            "How does the Bridge pattern prevent Cartesian product class explosion?",
            "By decoupling abstraction and implementation into two orthogonal hierarchies linked via composition, turning M * N subclasses into M + N independent classes.",
            "Device and Remote Bridge",
            "Build RemoteControl abstraction with TV and Radio device implementations.",
            "class IDevice {}; class Remote { std::shared_ptr<IDevice> dev; };"
        ),
        make_18_step_topic(
            "composite-pattern", "Composite Pattern (Tree Hierarchies)",
            "Composing objects into tree structures to represent part-whole hierarchies, treating individual objects and compositions uniformly.",
            "The <strong>Composite Pattern</strong> lets clients treat individual leaf objects and complex branch compositions uniformly through a shared interface.",
            "Hierarchical tree structures (e.g. File systems with Files and Folders, or UI view hierarchies) need recursive operations without custom type checks.",
            "Both Leaf (e.g. <code>File</code>) and Composite (e.g. <code>Directory</code>) implement <code>IFileSystemNode</code>.",
            "A composite contains a <code>std::vector&lt;std::shared_ptr&lt;Component&gt;&gt;</code> and delegates operations recursively to its children.",
            {"callout": {"type": "tip", "title": "Composite Recursion", "text": "Directory::getSize() -> loops through children -> sums child File::getSize() + nested Directory::getSize() recursively!"}},
            "composite_filesystem.cpp",
            """#include <iostream>
#include <vector>
#include <memory>
#include <string>

// Component Base
class IFileSystemItem {
public:
    virtual ~IFileSystemItem() = default;
    virtual void display(int indent = 0) const = 0;
    virtual size_t getSize() const = 0;
};

// Leaf Component
class File : public IFileSystemItem {
private:
    std::string name;
    size_t sizeBytes;
public:
    File(std::string n, size_t s) : name(std::move(n)), sizeBytes(s) {}

    void display(int indent = 0) const override {
        std::cout << std::string(indent, ' ') << "- File: " << name << " (" << sizeBytes << " bytes)\\n";
    }
    size_t getSize() const override { return sizeBytes; }
};

// Composite Component
class Directory : public IFileSystemItem {
private:
    std::string name;
    std::vector<std::shared_ptr<IFileSystemItem>> children;
public:
    explicit Directory(std::string n) : name(std::move(n)) {}

    void add(std::shared_ptr<IFileSystemItem> item) { children.push_back(item); }

    void display(int indent = 0) const override {
        std::cout << std::string(indent, ' ') << "+ Directory: " << name << "\\n";
        for (const auto& child : children) {
            child->display(indent + 2); // Recursive tree traversal!
        }
    }

    size_t getSize() const override {
        size_t total = 0;
        for (const auto& child : children) total += child->getSize();
        return total;
    }
};

int main() {
    auto root = std::make_shared<Directory>("root");
    auto bin = std::make_shared<Directory>("bin");
    bin->add(std::make_shared<File>("sh", 1024));
    bin->add(std::make_shared<File>("bash", 2048));

    root->add(bin);
    root->add(std::make_shared<File>("config.yaml", 256));

    root->display();
    std::cout << "Total Size: " << root->getSize() << " bytes\\n";
    return 0;
}""",
            "File (Leaf) and Directory (Composite) both implement IFileSystemItem with recursive size summation.",
            "DOM Trees in web browsers, UI Widget layouts, 3D Scene Graphs.",
            "Use whenever representing tree structures where leaves and branches share common operations.",
            "Do not use if leaf and branch operations differ radically and cannot share an interface.",
            "Simplifies client code; easy to add new component types.",
            "Hard to restrict which children can be added to specific composites at compile time.",
            "Safe Composite (add/remove on Composite only), Transparent Composite (add/remove on base).",
            "Modifying children list during recursive iteration.",
            "What is the difference between Safe and Transparent Composite?",
            "Transparent Composite defines child management (add/remove) in the base interface (leaves must throw). Safe Composite defines child management only in the Composite class (type safety).",
            "Graphic Shape Grouping",
            "Implement Composite for graphic shapes (Dot, Circle, and CompoundGraphic).",
            "class Compound : public IShape { std::vector<std::shared_ptr<IShape>> children; };"
        ),
        make_18_step_topic(
            "decorator-pattern", "Decorator Pattern",
            "Attaching additional responsibilities to an object dynamically without subclassing.",
            "The <strong>Decorator Pattern</strong> wraps an existing object dynamically to add new behavior without altering the original class code or using class inheritance.",
            "Inheritance is static and causes class explosion when combining features (e.g. SimpleCoffee, MilkCoffee, SugarCoffee, WhipCoffee, MilkSugarCoffee = $2^N$ classes!).",
            "The Decorator implements the same interface as the wrapped object AND contains a pointer to it.",
            "<code>Coffee* drink = new SugarDecorator(new MilkDecorator(new SimpleCoffee()))</code>.",
            {"callout": {"type": "tip", "title": "Decorator Stacking", "text": "SugarDecorator -> wraps -> MilkDecorator -> wraps -> SimpleCoffee. Cost: $0.20 + $0.50 + $2.00 = $2.70"}},
            "decorator_coffee.cpp",
            """#include <iostream>
#include <memory>
#include <string>

// Component Interface
class ICoffee {
public:
    virtual ~ICoffee() = default;
    virtual double getCost() const = 0;
    virtual std::string getDescription() const = 0;
};

// Concrete Base Component
class SimpleCoffee : public ICoffee {
public:
    double getCost() const override { return 2.00; }
    std::string getDescription() const override { return "Simple Coffee"; }
};

// Base Decorator
class CoffeeDecorator : public ICoffee {
protected:
    std::unique_ptr<ICoffee> wrapped;
public:
    explicit CoffeeDecorator(std::unique_ptr<ICoffee> coffee) : wrapped(std::move(coffee)) {}
    double getCost() const override { return wrapped->getCost(); }
    std::string getDescription() const override { return wrapped->getDescription(); }
};

// Concrete Decorator 1: Milk
class MilkDecorator : public CoffeeDecorator {
public:
    explicit MilkDecorator(std::unique_ptr<ICoffee> c) : CoffeeDecorator(std::move(c)) {}
    double getCost() const override { return wrapped->getCost() + 0.50; }
    std::string getDescription() const override { return wrapped->getDescription() + ", Steamed Milk"; }
};

// Concrete Decorator 2: Caramel
class CaramelDecorator : public CoffeeDecorator {
public:
    explicit CaramelDecorator(std::unique_ptr<ICoffee> c) : CoffeeDecorator(std::move(c)) {}
    double getCost() const override { return wrapped->getCost() + 0.75; }
    std::string getDescription() const override { return wrapped->getDescription() + ", Caramel Drizzle"; }
};

int main() {
    // Dynamic runtime layering of behaviors!
    std::unique_ptr<ICoffee> order = std::make_unique<SimpleCoffee>();
    order = std::make_unique<MilkDecorator>(std::move(order));
    order = std::make_unique<CaramelDecorator>(std::move(order));

    std::cout << "Order: " << order->getDescription() << "\\n";
    std::cout << "Total: $" << order->getCost() << "\\n";
    return 0;
}""",
            "MilkDecorator and CaramelDecorator wrap ICoffee dynamically, summing descriptions and costs.",
            "Java / C++ I/O streams (e.g. <code>BufferedInputStream(GZIPInputStream(FileInputStream))</code>), UI Scrollbars, HTTP Middleware.",
            "Use when you want to add capabilities to individual objects at runtime without subclassing.",
            "Do not use when the component interface is huge with dozens of methods.",
            "Adheres to Open/Closed and Single Responsibility principles; dynamic composability.",
            "Hard to remove a specific decorator from the middle of the wrapper stack.",
            "Dynamic Decorator, Static Compile-Time Decorator (Templates).",
            "Assuming object identity remains identical after wrapping.",
            "Why is Decorator preferred over subclassing for multi-feature combinations?",
            "Subclassing creates $2^N$ static classes for $N$ optional features. Decorator requires only $N$ decorator classes composed dynamically at runtime.",
            "Encrypted Log Decorator",
            "Build an EncryptedLogDecorator wrapping a basic FileWriter.",
            "class EncryptDecorator : public IWriter { std::unique_ptr<IWriter> w; public: void write(string s) override {} };"
        ),
        make_18_step_topic(
            "facade-pattern", "Facade Pattern",
            "Providing a unified, simplified higher-level interface to a complex subsystem.",
            "The <strong>Facade Pattern</strong> provides a simple, clean interface to a complex subsystem of interacting classes, masking internal complexity.",
            "Clients should not need to orchestrate 15 low-level audio, video, codec, and network classes just to play a video.",
            "Create a single high-level Facade class that encapsulates calls to all subsystem objects.",
            "<code>HomeTheaterFacade.watchMovie(\"Inception\")</code> turns on projector, dims lights, lowers screen, and starts audio amp.",
            {"callout": {"type": "tip", "title": "Facade Boundary", "text": "Client -> [HomeTheaterFacade] -> coordinates [Amplifier, Projector, Screen, DvdPlayer, Lights]"}},
            "facade_pattern.cpp",
            """#include <iostream>

class Amplifier { public: void on() { std::cout << "Amp On\\n"; } };
class Projector { public: void on() { std::cout << "Projector On\\n"; } };
class Lights { public: void dim() { std::cout << "Lights 10%\\n"; } };

// Facade: Unified Interface
class HomeTheaterFacade {
private:
    Amplifier amp;
    Projector proj;
    Lights lights;
public:
    void watchMovie() {
        std::cout << "--- Initializing Movie Mode ---\\n";
        lights.dim();
        proj.on();
        amp.on();
        std::cout << "Movie is playing!\\n";
    }
};

int main() {
    HomeTheaterFacade theater;
    theater.watchMovie();
    return 0;
}""",
            "HomeTheaterFacade orchestrates multiple low-level subsystems behind a single watchMovie() call.",
            "Database connection pools, Compiler subsystems, OS SDK wrappers.",
            "Use when you want to provide a simple default entry point to a complex framework.",
            "Do not use if client code needs fine-grained access to low-level subsystem internals.",
            "Reduces client coupling and shields callers from subsystem refactorings.",
            "Can turn into a God object if too many responsibilities are routed through it.",
            "Opaque Facade, Transparent Facade (allows access to low-level subsystem if needed).",
            "Forcing all access through the facade when advanced clients need low-level control.",
            "What is the difference between Facade and Adapter?",
            "<strong>Adapter</strong> makes two <em>existing incompatible interfaces</em> work together. <strong>Facade</strong> defines a <em>brand-new simplified interface</em> for an entire complex subsystem.",
            "Computer Boot Facade",
            "Build a ComputerFacade coordinating CPU, Memory, and HardDrive boot sequence.",
            "class ComputerFacade { CPU cpu; RAM ram; public: void start() { cpu.boot(); ram.load(); } };"
        ),
        make_18_step_topic(
            "flyweight-pattern", "Flyweight Pattern",
            "Minimizing memory usage by sharing fine-grained intrinsic state among thousands of objects.",
            "The <strong>Flyweight Pattern</strong> reduces memory footprint by sharing common immutable state (<strong>Intrinsic State</strong>) across thousands of objects, passing dynamic context (<strong>Extrinsic State</strong>) as method parameters.",
            "Rendering 1,000,000 trees in a forest game will crash RAM if each tree stores its own 50MB 3D mesh and texture.",
            "Split state into Intrinsic (shared TreeType mesh/texture) and Extrinsic (unique x, y coordinates).",
            "Flyweight Factory caches and shares <code>TreeType</code> instances.",
            {"callout": {"type": "important", "title": "Intrinsic vs Extrinsic State", "text": "Intrinsic (Shared Flyweight): Tree Mesh, Texture, Bark Color (Stored ONCE in RAM)\\nExtrinsic (Context): X, Y Coordinates, Current Age (Passed as parameters)"}},
            "flyweight_forest.cpp",
            """#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <memory>

// Flyweight: Shared Intrinsic State (Heavy mesh/texture data)
class TreeType {
public:
    std::string name;
    std::string textureData; // 50 MB texture
    TreeType(std::string n, std::string t) : name(std::move(n)), textureData(std::move(t)) {}

    void draw(int x, int y) const {
        std::cout << "Rendering " << name << " at (" << x << ", " << y << ")\\n";
    }
};

// Flyweight Factory: Manages pool of shared TreeTypes
class TreeFactory {
private:
    static inline std::unordered_map<std::string, std::shared_ptr<TreeType>> cache;
public:
    static std::shared_ptr<TreeType> getTreeType(const std::string& name, const std::string& texture) {
        if (cache.find(name) == cache.end()) {
            cache[name] = std::make_shared<TreeType>(name, texture);
            std::cout << "[Flyweight Factory] Created new shared TreeType: " << name << "\\n";
        }
        return cache[name];
    }
};

// Context Object: Lightweight Extrinsic State
class Tree {
public:
    int x, y;
    std::shared_ptr<TreeType> type; // Pointer to shared flyweight!
    Tree(int xPos, int yPos, std::shared_ptr<TreeType> t) : x(xPos), y(yPos), type(std::move(t)) {}
    void draw() const { type->draw(x, y); }
};

int main() {
    auto pineType = TreeFactory::getTreeType("Pine", "pine_50mb.png");
    
    std::vector<Tree> forest;
    for (int i = 0; i < 5; ++i) {
        forest.emplace_back(i * 10, i * 20, pineType); // Shares 1 single texture!
    }
    forest[0].draw();
    return 0;
}""",
            "TreeFactory shares a single 50MB TreeType flyweight across 5 tree instances.",
            "Word processor text glyph formatters, game particle engines, CSS styling engines in browsers.",
            "Use when an application instantiates millions of objects and memory usage is a bottleneck.",
            "Do not use if objects have completely unique, non-shareable state.",
            "Massive RAM savings; improves CPU cache locality.",
            "Increases CPU computation if extrinsic state must be recalculated on the fly.",
            "Text Glyph Flyweights, Particle Flyweights.",
            "Storing mutable extrinsic state inside the shared flyweight class.",
            "What is the difference between Intrinsic and Extrinsic state in Flyweight?",
            "<strong>Intrinsic State</strong> is constant, immutable, and shared (stored in the Flyweight). <strong>Extrinsic State</strong> varies by context and is passed to the Flyweight by caller methods.",
            "Game Bullet Particle Flyweight",
            "Implement BulletFlyweight sharing sprite texture across 10,000 bullets.",
            "class BulletType { public: string sprite; }; class Bullet { int x, y; shared_ptr<BulletType> type; };"
        ),
        make_18_step_topic(
            "proxy-pattern", "Proxy Pattern (Virtual, Remote, Protection)",
            "Providing a surrogate or placeholder for another object to control access to it.",
            "The <strong>Proxy Pattern</strong> provides a surrogate object that controls access to the original object, enabling lazy loading, caching, logging, or security access control.",
            "Directly loading a 4K video or connecting to a remote server on startup wastes resources if never accessed.",
            "The Proxy implements the same interface as the RealSubject, intercepts requests, and delegates when authorized.",
            "Virtual Proxy (Lazy Initialization), Protection Proxy (Auth check), Remote Proxy (Network RPC).",
            {"callout": {"type": "tip", "title": "Virtual Proxy Lazy Loading", "text": "Client -> ProxyImage::display() -> If realImage == null: new RealImage() -> realImage->display()"}},
            "proxy_lazy_image.cpp",
            """#include <iostream>
#include <memory>
#include <string>

// Subject Interface
class IImage {
public:
    virtual ~IImage() = default;
    virtual void display() = 0;
};

// Real Subject: Expensive to construct
class HighResImage : public IImage {
private:
    std::string filename;
    void loadFromDisk() { std::cout << "[DISK I/O] Loaded 500MB image: " << filename << "\\n"; }
public:
    explicit HighResImage(std::string fn) : filename(std::move(fn)) { loadFromDisk(); }
    void display() override { std::cout << "Displaying " << filename << " on screen.\\n"; }
};

// Virtual Proxy: Lazy Loader
class ImageProxy : public IImage {
private:
    std::string filename;
    std::unique_ptr<HighResImage> realImage{nullptr}; // Lazy initialized
public:
    explicit ImageProxy(std::string fn) : filename(std::move(fn)) {}

    void display() override {
        if (!realImage) {
            std::cout << "[Proxy] Lazy-loading high resolution image on demand...\\n";
            realImage = std::make_unique<HighResImage>(filename);
        }
        realImage->display();
    }
};

int main() {
    std::unique_ptr<IImage> image = std::make_unique<ImageProxy>("satellite_map_4k.raw");
    std::cout << "Application loaded (Image not loaded in RAM yet!)\\n";
    std::cout << "\\nUser clicked open map:\\n";
    image->display(); // Triggers lazy load
    return 0;
}""",
            "ImageProxy postpones expensive 500MB disk read until display() is explicitly invoked.",
            "Smart Pointers (C++ smart pointers are proxies!), gRPC client stubs, Spring security proxies.",
            "Use for lazy initialization, caching, access control, and remote RPC stubs.",
            "Do not use when direct access without interception is sufficient.",
            "Saves system resources; provides transparent access control.",
            "Adds latency on the initial intercept call.",
            "Virtual Proxy, Remote Proxy, Protection Proxy, Smart Reference Proxy.",
            "Infinite proxy loops when proxy intercepts calls to itself.",
            "How does a Proxy differ from a Decorator?",
            "<strong>Decorator</strong> adds <em>new dynamic behavior</em> without changing interface. <strong>Proxy</strong> <em>controls access</em>, lifecycle (lazy load), or security to the underlying object.",
            "Protection Proxy Auth Check",
            "Build an AccessProxy that blocks non-admin users from calling executeShutdown().",
            "class AuthProxy : public IAdmin { string role; public: void shutdown() { if(role == 'admin') real->shutdown(); } };"
        )
    ]
}

# ==============================================================================
# MODULE 11: Behavioral Patterns
# ==============================================================================
mod_11 = {
    "module_id": "11",
    "title": "Behavioral Design Patterns",
    "level": "Intermediate",
    "category": "Design Patterns",
    "description": "Observer, Strategy, Command, State, Chain of Responsibility, Template Method, Mediator, Iterator, Memento, and Visitor.",
    "topics": [
        make_18_step_topic(
            "observer-pattern", "Observer Pattern & Event Dispatchers",
            "Defining a one-to-many dependency so that when one object changes state, all dependents are notified automatically.",
            "The <strong>Observer Pattern</strong> (Publish-Subscribe) maintains a list of dependents and notifies them automatically of state changes by calling their update() method.",
            "Decouples event producers from consumers; producers don't need to know concrete subscriber types.",
            "Subject has <code>attach(observer)</code>, <code>detach(observer)</code>, and <code>notifyObservers()</code>.",
            "When subject state changes, it iterates through its registered observer list calling <code>obs->update()</code>.",
            {"callout": {"type": "tip", "title": "Observer Publish Flow", "text": "StockTicker::setPrice(150.0) -> notifyObservers() -> updates PhoneApp, WebDashboard, TradingBot"}},
            "observer_pattern.cpp",
            """#include <iostream>
#include <vector>
#include <memory>
#include <string>
#include <algorithm>

class IObserver {
public:
    virtual ~IObserver() = default;
    virtual void onUpdate(const std::string& symbol, double price) = 0;
};

class StockTicker {
private:
    std::string symbol;
    double price{0.0};
    std::vector<std::shared_ptr<IObserver>> observers;

public:
    explicit StockTicker(std::string s) : symbol(std::move(s)) {}

    void registerObserver(std::shared_ptr<IObserver> obs) { observers.push_back(obs); }
    void removeObserver(std::shared_ptr<IObserver> obs) {
        observers.erase(std::remove(observers.begin(), observers.end(), obs), observers.end());
    }

    void setPrice(double newPrice) {
        price = newPrice;
        notifyAll();
    }

private:
    void notifyAll() {
        for (const auto& obs : observers) {
            obs->onUpdate(symbol, price);
        }
    }
};

class MobileAppObserver : public IObserver {
public:
    void onUpdate(const std::string& symbol, double price) override {
        std::cout << "[Mobile Push] " << symbol << " updated: $" << price << "\\n";
    }
};

int main() {
    StockTicker aapl{"AAPL"};
    auto mobile = std::make_shared<MobileAppObserver>();
    aapl.registerObserver(mobile);
    aapl.setPrice(185.50);
    return 0;
}""",
            "StockTicker notifies all registered IObserver instances automatically upon price mutation.",
            "GUI event listeners (button clicks), Message brokers (Kafka, RabbitMQ), Reactive Extensions (RxCpp).",
            "Use whenever changes in one object require updating an open-ended set of other objects.",
            "Do not use when observer notification chains can create circular update loops.",
            "Loose coupling between subject and observers; broadcast communication.",
            "Subscribers can leak memory if not properly detached before destruction (Lapsed Listener problem).",
            "Push Model (Subject pushes data), Pull Model (Subject sends reference, observer pulls).",
            "Forgetting to unsubscribe observers before destruction causing dangling callbacks.",
            "How do you prevent the Lapsed Listener memory leak in C++ Observer implementations?",
            "Store observers as <code>std::weak_ptr&lt;IObserver&gt;</code> in the subject's collection. If an observer is deleted, <code>lock()</code> returns null and the subject cleans it up automatically.",
            "Weather Station Observer",
            "Implement WeatherStation notifying PhoneDisplay and StatsDisplay on temperature change.",
            "class WeatherStation { vector<shared_ptr<IObserver>> obs; public: void setTemp(double t) { for(auto& o: obs) o->update(t); } };"
        ),
        make_18_step_topic(
            "strategy-pattern", "Strategy Pattern & Interchangeable Algorithms",
            "Defining a family of algorithms, encapsulating each one, and making them interchangeable at runtime.",
            "The <strong>Strategy Pattern</strong> lets the algorithm vary independently from clients that use it by encapsulating algorithms into distinct classes.",
            "Eliminates giant if-else/switch blocks for payment calculations, routing algorithms, and compression formats.",
            "Context class contains a pointer to <code>IStrategy</code> and delegates computation to it.",
            "<code>navigator.setRouteStrategy(new FastestRoute())</code> switches algorithm dynamically at runtime.",
            {"callout": {"type": "tip", "title": "Strategy Interchangeability", "text": "PaymentProcessor -> executes strategy->pay() -> works with CreditCard, PayPal, UPI, Crypto"}},
            "strategy_pattern.cpp",
            """#include <iostream>
#include <memory>

class ISortStrategy {
public:
    virtual ~ISortStrategy() = default;
    virtual void sortData() const = 0;
};

class QuickSortStrategy : public ISortStrategy {
public:
    void sortData() const override { std::cout << "[QuickSort] O(N log N) in-place sort\\n"; }
};

class MergeSortStrategy : public ISortStrategy {
public:
    void sortData() const override { std::cout << "[MergeSort] O(N log N) stable external sort\\n"; }
};

class DataContext {
private:
    std::unique_ptr<ISortStrategy> strategy;
public:
    void setStrategy(std::unique_ptr<ISortStrategy> strat) { strategy = std::move(strat); }
    void executeSort() const { if (strategy) strategy->sortData(); }
};

int main() {
    DataContext ctx;
    ctx.setStrategy(std::make_unique<QuickSortStrategy>());
    ctx.executeSort();
    ctx.setStrategy(std::make_unique<MergeSortStrategy>());
    ctx.executeSort();
    return 0;
}""",
            "DataContext swaps between QuickSortStrategy and MergeSortStrategy seamlessly.",
            "Sorting algorithms, compression formats (GZIP vs ZSTD), routing path algorithms in GPS navigation.",
            "Use when you have multiple variants of an algorithm that should be selectable at runtime.",
            "Do not use if an algorithm never changes and only one implementation will ever exist.",
            "Adheres to Open/Closed Principle; eliminates conditional switch logic.",
            "Clients must be aware of differences between strategies to select the right one.",
            "Object-Oriented Strategy, Modern C++ Functional Strategy (using <code>std::function</code>).",
            "Passing large context state unnecessarily to simple stateless strategies.",
            "How can the Strategy Pattern be implemented using modern C++ lambdas?",
            "By replacing the strategy interface hierarchy with <code>std::function&lt;double(double)&gt;</code>, allowing callers to pass inline lambdas directly without class boilerplate.",
            "Compression Strategy",
            "Implement FileArchiver using ZipCompression and RarCompression strategies.",
            "class ICompress { public: virtual ~ICompress() = default; virtual void compress() = 0; };"
        ),
        make_18_step_topic(
            "command-pattern", "Command Pattern & Undo/Redo Architecture",
            "Encapsulating a request as an object, enabling parameterization with queues, logs, and undoable operations.",
            "The <strong>Command Pattern</strong> turns a request into a stand-alone object containing all information about the request (receiver, method, arguments), enabling undo/redo, queuing, and transaction logging.",
            "Directly executing mutations makes undo/redo and background job queuing impossible.",
            "<code>ICommand</code> defines <code>execute()</code> and <code>undo()</code>.",
            "An Invoker maintains a history stack of executed commands. Calling Undo pops the top command and executes <code>cmd->undo()</code>.",
            {"callout": {"type": "tip", "title": "Command Stack", "text": "CommandHistory: [TypeCommand('A'), TypeCommand('B'), DeleteCommand()] -> Undo() -> calls DeleteCommand::undo()"}},
            "command_undo_redo.cpp",
            """#include <iostream>
#include <vector>
#include <memory>
#include <string>

// Receiver
class TextEditor {
public:
    std::string text;
    void append(const std::string& str) { text += str; }
    void erase(size_t count) { text.erase(text.length() - count); }
};

// Command Interface
class ICommand {
public:
    virtual ~ICommand() = default;
    virtual void execute() = 0;
    virtual void undo() = 0;
};

// Concrete Command: InsertText
class InsertTextCommand : public ICommand {
private:
    TextEditor& editor;
    std::string addedText;
public:
    InsertTextCommand(TextEditor& ed, std::string t) : editor(ed), addedText(std::move(t)) {}

    void execute() override { editor.append(addedText); }
    void undo() override { editor.erase(addedText.length()); }
};

// Invoker: Command History Manager
class CommandManager {
private:
    std::vector<std::unique_ptr<ICommand>> history;
public:
    void executeCommand(std::unique_ptr<ICommand> cmd) {
        cmd->execute();
        history.push_back(std::move(cmd));
    }

    void undo() {
        if (!history.empty()) {
            history.back()->undo();
            history.pop_back();
        }
    }
};

int main() {
    TextEditor editor;
    CommandManager mgr;

    mgr.executeCommand(std::make_unique<InsertTextCommand>(editor, "Hello "));
    mgr.executeCommand(std::make_unique<InsertTextCommand>(editor, "World!"));
    std::cout << "Text: " << editor.text << "\\n";

    mgr.undo();
    std::cout << "After Undo: " << editor.text << "\\n";
    return 0;
}""",
            "CommandManager tracks InsertTextCommand history stack supporting execute and undo.",
            "Text editor undo/redo, GUI button action bindings, transactional rollback systems, thread pool task queues.",
            "Use for undo/redo, task scheduling, asynchronous job queues, and macro recording.",
            "Do not use for simple direct method invocations with no queuing or undo needs.",
            "Decouples invoker from receiver; enables reversible operations.",
            "Increases number of command classes.",
            "Undoable Command, Macro Command (Composite Command), Asynchronous Task Command.",
            "Failing to capture complete state required to accurately undo the operation.",
            "How is Command pattern used to implement Transactional Rollbacks?",
            "Each database mutation is wrapped in a Command object with execute() committing SQL and undo() issuing compensating rollback queries in reverse execution order.",
            "Smart Home Remote Command",
            "Implement LightOnCommand and LightOffCommand for a remote control invoker.",
            "class ICommand { public: virtual ~ICommand() = default; virtual void execute() = 0; };"
        ),
        make_18_step_topic(
            "state-pattern", "State Pattern & Finite State Machines",
            "Allowing an object to alter its behavior when its internal state changes, appearing to change its class.",
            "The <strong>State Pattern</strong> encapsulates state-specific behavior inside separate state classes, eliminating massive switch-case state machines.",
            "When an object's behavior depends heavily on its state, adding new states requires editing giant conditional blocks across every method.",
            "Context contains a pointer to <code>IState</code> and delegates state-dependent actions to <code>state->handle()</code>.",
            "State methods transition the Context to a new <code>IState</code> instance upon valid triggers.",
            {"callout": {"type": "tip", "title": "State Pattern Structure", "text": "TCPConnection -> state->open() -> If ClosedState: transitions to SynSentState. If EstablishedState: throws error."}},
            "state_pattern.cpp",
            """#include <iostream>
#include <memory>
#include <string>

class DocumentContext;

// State Interface
class IDocumentState {
public:
    virtual ~IDocumentState() = default;
    virtual void publish(DocumentContext& context) = 0;
};

// Forward declaration of states
class DraftState;
class ModerationState;
class PublishedState;

// Context
class DocumentContext {
private:
    std::shared_ptr<IDocumentState> state;
public:
    explicit DocumentContext(std::shared_ptr<IDocumentState> initState) : state(std::move(initState)) {}
    void setState(std::shared_ptr<IDocumentState> s) { state = std::move(s); }
    void publish() { state->publish(*this); }
};

class PublishedState : public IDocumentState {
public:
    void publish(DocumentContext&) override { std::cout << "[Published] Document is already live!\\n"; }
};

class ModerationState : public IDocumentState {
public:
    void publish(DocumentContext& context) override {
        std::cout << "[Moderation] Approved! Transitioning to Published.\\n";
        context.setState(std::make_shared<PublishedState>());
    }
};

class DraftState : public IDocumentState {
public:
    void publish(DocumentContext& context) override {
        std::cout << "[Draft] Submitted for review. Transitioning to Moderation.\\n";
        context.setState(std::make_shared<ModerationState>());
    }
};

int main() {
    DocumentContext doc(std::make_shared<DraftState>());
    doc.publish(); // Draft -> Moderation
    doc.publish(); // Moderation -> Published
    doc.publish(); // Already published!
    return 0;
}""",
            "DocumentContext delegates publish() to DraftState -> ModerationState -> PublishedState.",
            "TCP connection lifecycles, Order processing state machines, Vending machines, Game character states (Idle, Run, Jump, Attack).",
            "Use when an object has complex state-dependent behaviors with many state transitions.",
            "Do not use if the object only has 2 simple states with minimal logic.",
            "Eliminates monolithic switch-cases; encapsulates state transitions cleanly.",
            "Increases class count.",
            "State with Context back-reference, Stateless Shared States.",
            "Allowing transitions from terminal states.",
            "What is the difference between State and Strategy patterns?",
            "Structure is identical, but <strong>Intent</strong> differs: <strong>Strategy</strong> provides interchangeable algorithms chosen by the client. <strong>State</strong> manages dynamic lifecycle transitions controlled by internal events.",
            "Vending Machine State Pattern",
            "Implement NoCoinState, HasCoinState, and SoldState.",
            "class IState { public: virtual ~IState() = default; virtual void insertCoin() = 0; };"
        ),
        make_18_step_topic(
            "chain-of-responsibility", "Chain of Responsibility Pattern",
            "Passing requests along a chain of potential handlers until one of them handles it.",
            "<strong>Chain of Responsibility</strong> decouples the sender of a request from its receivers by giving multiple objects a chance to handle the request sequentially.",
            "Hardcoding request dispatchers creates tight coupling between callers and all possible handler classes.",
            "Each handler holds a pointer to <code>nextHandler</code> in the chain.",
            "<code>handle(request)</code> checks if it can process the request; if yes, it executes; if no, it forwards to <code>nextHandler->handle(request)</code>.",
            {"callout": {"type": "tip", "title": "Chain Flow", "text": "AuthMiddleware -> LoggingMiddleware -> RateLimitMiddleware -> ControllerHandler"}},
            "chain_of_responsibility.cpp",
            """#include <iostream>
#include <memory>
#include <string>

enum class LogLevel { INFO, WARNING, ERROR };

class ILoggerHandler {
protected:
    std::shared_ptr<ILoggerHandler> nextHandler;
public:
    virtual ~ILoggerHandler() = default;
    void setNext(std::shared_ptr<ILoggerHandler> next) { nextHandler = std::move(next); }

    virtual void log(LogLevel level, const std::string& msg) {
        if (nextHandler) nextHandler->log(level, msg);
    }
};

class ConsoleLoggerHandler : public ILoggerHandler {
public:
    void log(LogLevel level, const std::string& msg) override {
        if (level == LogLevel::INFO) {
            std::cout << "[CONSOLE INFO] " << msg << "\\n";
        } else {
            ILoggerHandler::log(level, msg); // Pass down chain
        }
    }
};

class ErrorFileLoggerHandler : public ILoggerHandler {
public:
    void log(LogLevel level, const std::string& msg) override {
        if (level == LogLevel::ERROR) {
            std::cout << "[ERROR LOG FILE] ALERT: " << msg << "\\n";
        } else {
            ILoggerHandler::log(level, msg);
        }
    }
};

int main() {
    auto console = std::make_shared<ConsoleLoggerHandler>();
    auto errorLog = std::make_shared<ErrorFileLoggerHandler>();
    console->setNext(errorLog); // Build Chain: Console -> ErrorFile

    console->log(LogLevel::INFO, "Server started.");
    console->log(LogLevel::ERROR, "Database connection failed!");
    return 0;
}""",
            "ConsoleLoggerHandler and ErrorFileLoggerHandler chain log processing sequentially.",
            "HTTP Request Middleware filters, Technical Support escalation tiers (L1 -> L2 -> L3), GUI event bubbling.",
            "Use when multiple objects can handle a request and the exact handler isn't known up-front.",
            "Do not use when every request must be handled by a single deterministic method.",
            "Loose coupling between sender and receivers; dynamic chain configuration.",
            "A request can fall off the end of the chain unhandled.",
            "Terminating Chain (first handler stops), Pass-Through Chain (all handlers process).",
            "Creating circular chain references causing infinite loops.",
            "How is Chain of Responsibility used in web server middleware?",
            "Each middleware layer (Authentication -> Rate Limiting -> CORS -> Logging -> Handler) executes preprocessing, calls next.handle(), and executes postprocessing.",
            "Support Ticket Escalation",
            "Build L1Support, L2Support, and L3Support ticket handlers.",
            "class SupportHandler { shared_ptr<SupportHandler> next; public: virtual void handle(int level) {} };"
        ),
        make_18_step_topic(
            "template-method-pattern", "Template Method Pattern",
            "Defining the skeleton of an algorithm in a base class, letting subclasses override specific steps without changing structure.",
            "<strong>Template Method</strong> defines the invariant skeleton of an algorithm in a base method, deferring some steps to subclasses.",
            "Duplicating algorithm structure across subclasses while only 1 or 2 steps differ leads to code duplication.",
            "Base class defines a <code>final</code> or non-virtual template method calling private/protected virtual step hooks.",
            "Subclasses override the hook methods; the base template method coordinates the execution sequence.",
            {"callout": {"type": "tip", "title": "Hollywood Principle", "text": "'Don't call us, we'll call you.' The base class algorithm calls the derived class hooks, not the other way around!"}},
            "template_method.cpp",
            """#include <iostream>

class DataMiner {
public:
    virtual ~DataMiner() = default;

    // The Template Method (Defines immutable algorithm skeleton!)
    void mineData() {
        openFile();
        extractData();
        parseData();
        closeFile();
        std::cout << "Data mining completed successfully.\\n";
    }

protected:
    virtual void openFile() = 0;
    virtual void extractData() = 0;
    virtual void parseData() { std::cout << "Default generic parsing\\n"; }
    virtual void closeFile() { std::cout << "Closed file handle.\\n"; }
};

class PdfDataMiner : public DataMiner {
protected:
    void openFile() override { std::cout << "[PDF] Opened PDF stream.\\n"; }
    void extractData() override { std::cout << "[PDF] Extracted raw PDF bytes.\\n"; }
};

class CsvDataMiner : public DataMiner {
protected:
    void openFile() override { std::cout << "[CSV] Opened CSV stream.\\n"; }
    void extractData() override { std::cout << "[CSV] Extracted comma-delimited rows.\\n"; }
};

int main() {
    PdfDataMiner pdfMiner;
    pdfMiner.mineData();
    return 0;
}""",
            "DataMiner::mineData() coordinates the execution skeleton while PdfDataMiner overrides extraction steps.",
            "Game loop update lifecycles, Data ETL pipelines, Build system build stages (compile -> test -> package).",
            "Use when multiple classes share an identical multi-step workflow where only individual steps vary.",
            "Do not use when the entire workflow structure varies between subclasses.",
            "Eliminates code duplication; enforces standard workflow sequence.",
            "Subclasses are tightly coupled to base class algorithm order.",
            "Template Method with Hooks, Pure Virtual Template Steps.",
            "Overriding the main template method in subclasses and breaking workflow invariants.",
            "Why is the template method in the base class usually non-virtual or final?",
            "To prevent subclasses from overriding and corrupting the overarching execution sequence of the algorithm.",
            "Game Turn Template Method",
            "Implement GameTurn template method calling startTurn(), takeAction(), and endTurn().",
            "class Turn { public: void play() { start(); act(); end(); } virtual void start() = 0; virtual void act() = 0; virtual void end() = 0; };"
        ),
        make_18_step_topic(
            "mediator-pattern", "Mediator Pattern & Loose Coupling",
            "Reducing chaotic dependencies between objects by forcing them to communicate through a central mediator object.",
            "The <strong>Mediator Pattern</strong> encapsulates how a set of objects interact, preventing chaotic many-to-many direct references (all-to-all coupling).",
            "In an air traffic control network, 20 airplanes communicating directly with each other requires $O(N^2)$ communication links. A central control tower reduces links to $O(N)$.",
            "Colleagues hold a reference to <code>IMediator</code> and send notifications through it.",
            "The Mediator receives events and orchestrates responses across other colleagues.",
            {"callout": {"type": "tip", "title": "Many-to-Many vs Mediator", "text": "Direct: 10 UI widgets talk directly to each other (100 coupling links!)\\nMediator: 10 UI widgets talk ONLY to DialogMediator (10 links!)"}},
            "mediator_chat.cpp",
            """#include <iostream>
#include <vector>
#include <string>
#include <memory>

class IMediator;

class UserColleague {
protected:
    IMediator* mediator;
    std::string name;
public:
    UserColleague(IMediator* med, std::string n) : mediator(med), name(std::move(n)) {}
    virtual ~UserColleague() = default;
    virtual void send(const std::string& msg) = 0;
    virtual void receive(const std::string& msg) = 0;
    [[nodiscard]] std::string getName() const { return name; }
};

class IMediator {
public:
    virtual ~IMediator() = default;
    virtual void broadcast(const std::string& msg, UserColleague* sender) = 0;
};

class ChatRoomMediator : public IMediator {
private:
    std::vector<UserColleague*> users;
public:
    void addUser(UserColleague* u) { users.push_back(u); }

    void broadcast(const std::string& msg, UserColleague* sender) override {
        for (auto* u : users) {
            if (u != sender) u->receive(sender->getName() + ": " + msg);
        }
    }
};

class ConcreteChatUser : public UserColleague {
public:
    ConcreteChatUser(IMediator* med, std::string n) : UserColleague(med, std::move(n)) {}

    void send(const std::string& msg) override {
        std::cout << "[" << name << " Sending] " << msg << "\\n";
        mediator->broadcast(msg, this);
    }
    void receive(const std::string& msg) override {
        std::cout << "  [" << name << " Received] " << msg << "\\n";
    }
};

int main() {
    ChatRoomMediator chatRoom;
    ConcreteChatUser u1(&chatRoom, "Alice");
    ConcreteChatUser u2(&chatRoom, "Bob");
    chatRoom.addUser(&u1);
    chatRoom.addUser(&u2);

    u1.send("Hello everyone!");
    return 0;
}""",
            "ChatRoomMediator coordinates message delivery between Alice and Bob without direct coupling.",
            "Air Traffic Control towers, Chat room servers, Complex UI Dialog forms.",
            "Use when a group of objects communicate in complex, tightly coupled many-to-many ways.",
            "Do not use when objects only have simple one-to-one communication.",
            "Decouples colleagues; centralizes interaction control.",
            "The Mediator can turn into a complex God Object.",
            "Event Aggregator, UI Dialog Mediator.",
            "Putting business calculation logic inside the mediator instead of keeping it in colleagues.",
            "What is the difference between Mediator and Observer?",
            "<strong>Observer</strong> is <em>one-to-many unidirectional</em> communication. <strong>Mediator</strong> is <em>many-to-many bidirectional</em> communication coordinating complex interactions across multiple colleagues.",
            "Air Traffic Control Mediator",
            "Build AirTrafficControl tower mediating landing runway access for Airplane colleagues.",
            "class IATC { public: virtual void requestLanding(Airplane* a) = 0; };"
        ),
        make_18_step_topic(
            "iterator-pattern", "Iterator Pattern & Custom Iterators",
            "Accessing elements of an aggregate object sequentially without exposing its underlying representation.",
            "The <strong>Iterator Pattern</strong> provides a standard way to traverse elements of a collection sequentially without exposing its internal data structure (array, linked list, tree, hash map).",
            "Clients should not need to write different traversal algorithms depending on whether data is in a vector, binary tree, or linked list.",
            "Iterator defines <code>hasNext()</code>, <code>next()</code>, or standard C++ <code>operator++</code> and <code>operator*</code>.",
            "C++ Range-based for loops (<code>for (auto& item : container)</code>) work automatically by calling <code>begin()</code> and <code>end()</code> iterators.",
            {"callout": {"type": "tip", "title": "C++ Standard Iterators", "text": "Implementing operator*, operator++, and operator!= allows your custom container to work seamlessly with C++ range-based for loops and std::sort algorithms!"}},
            "custom_iterator.cpp",
            """#include <iostream>
#include <vector>

template <typename T>
class CustomList {
private:
    std::vector<T> elements;
public:
    void add(T val) { elements.push_back(std::move(val)); }

    // Custom Iterator
    class Iterator {
    private:
        typename std::vector<T>::const_iterator iter;
    public:
        explicit Iterator(typename std::vector<T>::const_iterator it) : iter(it) {}
        const T& operator*() const { return *iter; }
        Iterator& operator++() { ++iter; return *this; }
        bool operator!=(const Iterator& other) const { return iter != other.iter; }
    };

    Iterator begin() const { return Iterator(elements.cbegin()); }
    Iterator end() const { return Iterator(elements.cend()); }
};

int main() {
    CustomList<int> list;
    list.add(10);
    list.add(20);
    list.add(30);

    // Works with C++ range-based for loops!
    for (int val : list) {
        std::cout << "Item: " << val << "\\n";
    }
    return 0;
}""",
            "CustomList implements standard begin() and end() iterators enabling C++ range-based for loops.",
            "All C++ STL containers (<code>std::vector</code>, <code>std::map</code>, <code>std::list</code>), database cursor query iterators.",
            "Use when providing a clean, uniform traversal interface over complex internal collections.",
            "Do not use if random index access (<code>operator[]</code>) is the only traversal pattern needed.",
            "Decouples traversal algorithms from container data structures.",
            "Writing bidirectional/random-access iterator boilerplate requires care.",
            "Input, Output, Forward, Bidirectional, Random Access, and Contiguous Iterators.",
            "Invalidating iterators by modifying the container during iteration without updating iterator pointers.",
            "What methods must a C++ class implement to support range-based for loops?",
            "It must provide <code>begin()</code> and <code>end()</code> methods returning an iterator type that implements <code>operator*</code>, prefix <code>operator++</code>, and <code>operator!=</code>.",
            "Binary Tree In-Order Iterator",
            "Implement a forward iterator for an in-order binary tree traversal.",
            "class TreeIterator { public: int operator*() const; TreeIterator& operator++(); };"
        ),
        make_18_step_topic(
            "memento-pattern", "Memento Pattern (State Snapshots)",
            "Capturing and externalizing an object's internal state so it can be restored later without violating encapsulation.",
            "The <strong>Memento Pattern</strong> captures and stores the internal state of an object so that the object can be restored to this exact state later (Undo / Checkpointing).",
            "Exposing private fields to create backups violates encapsulation.",
            "<strong>Originator</strong> creates Memento snapshot. <strong>Caretaker</strong> stores snapshots. <strong>Memento</strong> stores immutable state.",
            "<code>originator.restoreFromMemento(caretaker.popSnapshot())</code>.",
            {"callout": {"type": "tip", "title": "Memento Encapsulation", "text": "The Memento object has private fields accessible ONLY by the Originator (via friend class), keeping internal state strictly hidden from the Caretaker!"}},
            "memento_pattern.cpp",
            """#include <iostream>
#include <string>
#include <vector>
#include <memory>

// 1. Memento: Stores state snapshot
class EditorMemento {
private:
    friend class CodeEditor; // Only CodeEditor can read/write Memento state
    std::string textSnapshot;
    explicit EditorMemento(std::string text) : textSnapshot(std::move(text)) {}
};

// 2. Originator: Creates and restores from Memento
class CodeEditor {
public:
    std::string content;

    std::unique_ptr<EditorMemento> saveSnapshot() const {
        return std::unique_ptr<EditorMemento>(new EditorMemento(content));
    }

    void restore(const EditorMemento& memento) {
        content = memento.textSnapshot;
    }
};

// 3. Caretaker: Manages history stack
class HistoryCaretaker {
private:
    std::vector<std::unique_ptr<EditorMemento>> history;
public:
    void push(std::unique_ptr<EditorMemento> m) { history.push_back(std::move(m)); }
    std::unique_ptr<EditorMemento> pop() {
        if (history.empty()) return nullptr;
        auto m = std::move(history.back());
        history.pop_back();
        return m;
    }
};

int main() {
    CodeEditor editor;
    HistoryCaretaker history;

    editor.content = "int main() {}";
    history.push(editor.saveSnapshot()); // Save state 1

    editor.content = "int main() { return 0; }"; // Mutate state
    std::cout << "Current: " << editor.content << "\\n";

    auto prev = history.pop();
    if (prev) editor.restore(*prev); // Restore state 1
    std::cout << "Restored: " << editor.content << "\\n";
    return 0;
}""",
            "CodeEditor creates and restores EditorMemento snapshots managed by HistoryCaretaker.",
            "IDE checkpoints, Game save files, Database transaction savepoints.",
            "Use for undo/redo and checkpoint rollback when state snapshotting is required.",
            "Do not use if saving full object snapshots consumes excessive RAM (use command undo diffs instead).",
            "Preserves encapsulation while providing robust state restoration.",
            "High memory consumption if snapshots are frequent and large.",
            "Full Memento Snapshot, Incremental Diff Memento.",
            "Making Memento state public so other classes can tamper with internal state.",
            "How does Memento protect encapsulation in C++?",
            "By declaring the Originator as a <code>friend class</code> of the Memento and making all Memento constructors and fields <code>private</code>.",
            "Game Checkpoint Memento",
            "Implement PlayerState memento for checkpoint save/load.",
            "class PlayerMemento { friend class Player; int hp; };"
        ),
        make_18_step_topic(
            "visitor-pattern", "Visitor Pattern & Double Dispatch",
            "Representing an operation to be performed on elements of an object structure without changing their classes.",
            "The <strong>Visitor Pattern</strong> lets you define a new operation on a collection of polymorphic objects without modifying their classes (<strong>Double Dispatch</strong>).",
            "Adding a new operation (e.g. ExportToXML, CalculateTaxes, RenderSVG) across 15 class types requires modifying all 15 classes.",
            "Elements accept a visitor: <code>element->accept(visitor)</code>, which double-dispatches: <code>visitor->visit(this)</code>.",
            "First dispatch: Virtual <code>accept()</code> on Element. Second dispatch: Overloaded <code>visit()</code> on Visitor.",
            {"callout": {"type": "tip", "title": "Double Dispatch Flow", "text": "Shape::accept(Visitor& v) { v.visit(*this); } -> Dynamic type of Shape + Overloaded type of Visitor resolved!"}},
            "visitor_pattern.cpp",
            """#include <iostream>
#include <vector>
#include <memory>

class Circle;
class Rectangle;

// Visitor Interface
class IShapeVisitor {
public:
    virtual ~IShapeVisitor() = default;
    virtual void visit(const Circle& c) = 0;
    virtual void visit(const Rectangle& r) = 0;
};

// Element Interface
class IShapeElement {
public:
    virtual ~IShapeElement() = default;
    virtual void accept(IShapeVisitor& visitor) const = 0;
};

class Circle : public IShapeElement {
public:
    double radius{5.0};
    void accept(IShapeVisitor& visitor) const override { visitor.visit(*this); }
};

class Rectangle : public IShapeElement {
public:
    double width{4.0}, height{6.0};
    void accept(IShapeVisitor& visitor) const override { visitor.visit(*this); }
};

// Concrete Visitor: Area Calculator (Added without touching Circle or Rectangle code!)
class AreaCalculatorVisitor : public IShapeVisitor {
public:
    double totalArea{0.0};
    void visit(const Circle& c) override { totalArea += 3.14159 * c.radius * c.radius; }
    void visit(const Rectangle& r) override { totalArea += r.width * r.height; }
};

int main() {
    std::vector<std::unique_ptr<IShapeElement>> shapes;
    shapes.push_back(std::make_unique<Circle>());
    shapes.push_back(std::make_unique<Rectangle>());

    AreaCalculatorVisitor areaCalc;
    for (const auto& s : shapes) {
        s->accept(areaCalc); // Double dispatch!
    }
    std::cout << "Total Computed Area: " << areaCalc.totalArea << "\\n";
    return 0;
}""",
            "AreaCalculatorVisitor visits Circle and Rectangle polymorphically via double dispatch accept().",
            "Compiler Abstract Syntax Tree (AST) analyzers, Document format exporters (HTML, PDF, Markdown), Tax calculation engines.",
            "Use when an object structure rarely changes but you frequently need to add new operations over it.",
            "Do not use if the object class hierarchy changes frequently (every new class breaks the visitor interface).",
            "Easy to add new operations; groups related operation logic together.",
            "Extremely difficult to add new element classes to the hierarchy.",
            "Classic Double-Dispatch Visitor, Acyclic Visitor, std::visit with std::variant (C++17).",
            "Forgetting to implement double dispatch and calling static overloads directly.",
            "What is Double Dispatch in C++ and how does Visitor achieve it?",
            "Double dispatch means the executed function depends on the runtime types of TWO objects. Visitor achieves it by first calling virtual <code>element->accept(visitor)</code> (first dispatch), which then calls <code>visitor->visit(*this)</code> (second dispatch).",
            "AST Code Generator Visitor",
            "Implement a CodeGenVisitor traversing BinaryOpNode and NumberNode.",
            "class IVisitor { public: virtual void visit(const BinaryOp&) = 0; virtual void visit(const Number&) = 0; };"
        )
    ]
}

write_module(mod_09)
write_module(mod_10)
write_module(mod_11)
