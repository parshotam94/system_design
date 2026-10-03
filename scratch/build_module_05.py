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
# MODULE 05: Class Relationships & Coupling
# ==============================================================================
mod_05 = {
    "module_id": "05",
    "title": "Class Relationships & Coupling",
    "level": "Beginner",
    "category": "Modeling",
    "description": "Deep comparison of Association, Aggregation, Composition, Inheritance, Dependency, and Realization using the same real-world domain example.",
    "topics": [
        {
            "id": "association",
            "title": "Association ('uses a')",
            "description": "A structural 'uses a' relationship where two independent objects interact without owning each other's lifetimes.",
            "sections": [
                {"step_number": 1, "title": "1. What is it?", "content": "<p><strong>Association</strong> is a structural relationship where one class holds a persistent reference or pointer to another class to use its services without claiming lifecycle ownership.</p>"},
                {"step_number": 2, "title": "2. Why do we need it?", "content": "<p>Objects in a domain model must collaborate (e.g., a <code>Student</code> enrolls in a <code>Course</code>). Neither object owns the other's lifecycle.</p>"},
                {"step_number": 3, "title": "3. Core idea", "content": "<p>Class A knows about Class B. When Class A is destroyed, Class B continues to exist completely unaffected.</p>"},
                {"step_number": 4, "title": "4. How it works", "content": "<p>In C++, Association is represented by holding a raw pointer (<code>Course*</code>), a reference (<code>Course&</code>), or a <code>std::shared_ptr&lt;Course&gt;</code>/<code>std::weak_ptr&lt;Course&gt;</code>.</p>"},
                {"step_number": 5, "title": "5. Visual explanation", "content": "<p>Association Diagram:</p>", "diagram": {
                    "title": "Student and Course Association UML",
                    "classes": [
                        {"name": "Student", "attributes": [{"visibility": "-", "name": "name", "type": "std::string"}, {"visibility": "-", "name": "enrolledCourses", "type": "std::vector<Course*>"}]},
                        {"name": "Course", "attributes": [{"visibility": "-", "name": "title", "type": "std::string"}]}
                    ],
                    "relationships": [{"from": "Student", "to": "Course", "type": "association", "label": "enrolled in", "ownership": "None", "lifetime": "Independent", "coupling": "Loose", "cppSyntax": "class Student { std::vector<Course*> courses; };"}]
                }},
                {"step_number": 6, "title": "6. C++ implementation", "content": "<p>Student-Course Association in C++:</p>", "code_example": {
                    "filename": "association_demo.cpp",
                    "code": """#include <iostream>
#include <string>
#include <vector>

class Course {
public:
    std::string title;
    explicit Course(std::string t) : title(std::move(t)) {}
};

class Student {
private:
    std::string name;
    std::vector<Course*> enrolledCourses; // Non-owning association pointers

public:
    explicit Student(std::string n) : name(std::move(n)) {}

    void enroll(Course* c) {
        if (c) enrolledCourses.push_back(c);
    }

    void showSchedule() const {
        std::cout << "[Student " << name << "] Enrolled Courses:\\n";
        for (const auto* c : enrolledCourses) {
            std::cout << "  - " << c->title << "\\n";
        }
    }
};

int main() {
    Course c1{"Advanced C++ Low-Level Design"};
    Course c2{"Distributed Systems Architecture"};

    {
        Student alice{"Alice"};
        alice.enroll(&c1);
        alice.enroll(&c2);
        alice.showSchedule();
    } // Alice is destroyed here; c1 and c2 continue to exist!

    std::cout << "Course '" << c1.title << "' still exists independently.\\n";
    return 0;
}"""
                }},
                {"step_number": 7, "title": "7. Code walkthrough", "content": "<p><strong>Line 13:</strong> <code>std::vector&lt;Course*&gt;</code> stores non-owning pointers. When <code>Student</code> is destroyed, courses remain in memory.</p>"},
                {"step_number": 8, "title": "8. Real-world example", "content": "<p>Doctor and Patient, Customer and Product, Driver and Car Rental reservation.</p>"},
                {"step_number": 9, "title": "9. When to use", "content": "<p>Use when two peer domain entities need to interact without lifecycle dependencies.</p>"},
                {"step_number": 10, "title": "10. When NOT to use", "content": "<p>Do not use simple association when one object strictly owns the creation and destruction of the other (use Composition).</p>"},
                {"step_number": 11, "title": "11. Advantages", "content": "<p>Loose coupling; objects can be reused independently.</p>"},
                {"step_number": 12, "title": "12. Disadvantages", "content": "<p>Potential dangling pointers if an associated object is deleted while other objects hold pointers to it.</p>"},
                {"step_number": 13, "title": "13. Variations / Types", "content": "<p>Unidirectional Association, Bidirectional Association, Many-to-Many Association.</p>"},
                {"step_number": 14, "title": "14. Common mistakes", "content": "<p>Deleting associated pointers in the destructor (accidental deletion of shared objects).</p>"},
                {"step_number": 15, "title": "15. Interview questions", "content": "<p><strong>Q:</strong> How do you prevent dangling pointers in bidirectional associations in C++?</p>"},
                {"step_number": 16, "title": "16. Interview answer", "content": "<p><strong>Answer:</strong> Use <code>std::weak_ptr</code> instead of raw pointers, or implement an explicit unregister/observer pattern where objects notify each other before destruction.</p>"},
                {"step_number": 17, "title": "17. Practice problem", "content": "<p>Implement a bidirectional Association between <code>Author</code> and <code>Book</code> without creating cyclic ownership memory leaks.</p>", "practice": {
                    "title": "Bidirectional Association Practice",
                    "problemStatement": "Link Author and Book without memory leaks.",
                    "requirements": ["Author has books", "Book has author pointer"],
                    "constraints": ["Zero memory leaks"],
                    "hint": "Use raw non-owning pointers or std::weak_ptr.",
                    "expectedEntities": [{"name": "Author", "responsibility": "Author metadata."}, {"name": "Book", "responsibility": "Book details."}],
                    "referenceCode": {
                        "filename": "author_book_assoc.cpp",
                        "code": """#include <string>
#include <vector>
class Book;
class Author {
public:
    std::string name;
    std::vector<Book*> books;
};
class Book {
public:
    std::string title;
    Author* author{nullptr};
};"""
                    }
                }},
                {"step_number": 18, "title": "18. Summary", "content": "<p>Association represents peer-to-peer relationships with independent lifecycles.</p>"}
            ]
        },
        {
            "id": "aggregation",
            "title": "Aggregation ('has a' - weak ownership)",
            "description": "Weak container ownership where child objects can belong to multiple parents and outlive the container.",
            "sections": [
                {"step_number": 1, "title": "1. What is it?", "content": "<p><strong>Aggregation</strong> is a specialized 'has-a' relationship (whole-part) where the container (whole) references parts that have an independent lifecycle outside the container.</p>"},
                {"step_number": 2, "title": "2. Why do we need it?", "content": "<p>A <code>Department</code> has <code>Professors</code>. If the Department is closed, the Professors do not cease to exist; they can be transferred to another department.</p>"},
                {"step_number": 3, "title": "3. Core idea", "content": "<p>Whole-part relationship with <strong>weak ownership</strong>. The child outlives the parent.</p>"},
                {"step_number": 4, "title": "4. How it works", "content": "<p>Represented in C++ using collections of non-owning raw pointers (<code>std::vector&lt;Professor*&gt;</code>) or <code>std::shared_ptr&lt;Professor&gt;</code>.</p>"},
                {"step_number": 5, "title": "5. Visual explanation", "content": "<p>Department and Professor Aggregation (Hollow Diamond ──◇):</p>", "diagram": {
                    "title": "Department and Professor Aggregation UML",
                    "classes": [
                        {"name": "Department", "attributes": [{"visibility": "-", "name": "deptName", "type": "std::string"}, {"visibility": "-", "name": "faculty", "type": "std::vector<Professor*>"}]},
                        {"name": "Professor", "attributes": [{"visibility": "-", "name": "name", "type": "std::string"}]}
                    ],
                    "relationships": [{"from": "Department", "to": "Professor", "type": "aggregation", "label": "employs", "ownership": "Weak", "lifetime": "Independent", "coupling": "Moderate", "cppSyntax": "class Department { std::vector<Professor*> faculty; };"}]
                }},
                {"step_number": 6, "title": "6. C++ implementation", "content": "<p>Aggregation Implementation in C++:</p>", "code_example": {
                    "filename": "aggregation_department.cpp",
                    "code": """#include <iostream>
#include <string>
#include <vector>

class Professor {
public:
    std::string name;
    explicit Professor(std::string n) : name(std::move(n)) {}
    ~Professor() { std::cout << "[Professor " << name << "] Destructor executed.\\n"; }
};

class Department {
private:
    std::string name;
    std::vector<Professor*> faculty; // Aggregation: Non-owning references

public:
    explicit Department(std::string n) : name(std::move(n)) {}

    void addProfessor(Professor* p) {
        if (p) faculty.push_back(p);
    }

    ~Department() {
        std::cout << "[Department " << name << "] Disbanded. (Professors remain safe!)\\n";
    }
};

int main() {
    Professor profKnuth{"Donald Knuth"};
    {
        Department csDept{"Computer Science"};
        csDept.addProfessor(&profKnuth);
    } // Department disbanded here!

    std::cout << "Professor '" << profKnuth.name << "' is still alive and teaching!\\n";
    return 0;
}"""
                }},
                {"step_number": 7, "title": "7. Code walkthrough", "content": "<p><strong>Lines 21-23:</strong> <code>~Department()</code> does NOT delete professors. <code>profKnuth</code> outlives the department scope.</p>"},
                {"step_number": 8, "title": "8. Real-world example", "content": "<p>University Department and Faculty, Sports Team and Players, Playlist and Songs.</p>"},
                {"step_number": 9, "title": "9. When to use", "content": "<p>Use Aggregation for whole-part systems where components can be shared or outlive the parent container.</p>"},
                {"step_number": 10, "title": "10. When NOT to use", "content": "<p>Do not use Aggregation when the child is strictly created and destroyed with the parent (use Composition).</p>"},
                {"step_number": 11, "title": "11. Advantages", "content": "<p>Allows flexible resource sharing and transfer between containers.</p>"},
                {"step_number": 12, "title": "12. Disadvantages", "content": "<p>Requires external lifetime coordination so containers don't hold dangling pointers.</p>"},
                {"step_number": 13, "title": "13. Variations / Types", "content": "<p>Shared pointer aggregation, Observer list aggregation.</p>"},
                {"step_number": 14, "title": "14. Common mistakes", "content": "<p>Calling <code>delete</code> on aggregated pointers inside the container's destructor.</p>"},
                {"step_number": 15, "title": "15. Interview questions", "content": "<p><strong>Q:</strong> What is the key difference between Composition and Aggregation?</p>"},
                {"step_number": 16, "title": "16. Interview answer", "content": "<p><strong>Answer:</strong> In <strong>Composition</strong>, the child's lifetime is bound to the parent (child dies with parent). In <strong>Aggregation</strong>, the child exists independently and can outlive the parent container.</p>"},
                {"step_number": 17, "title": "17. Practice problem", "content": "<p>Model a <code>MusicPlaylist</code> aggregation containing <code>Song*</code> pointers.</p>", "practice": {
                    "title": "Music Playlist Aggregation",
                    "problemStatement": "Implement a playlist that references shared songs.",
                    "requirements": ["Playlist holds Song*", "Destroying playlist does not delete songs"],
                    "constraints": ["Const-correct getters"],
                    "hint": "Use vector of raw pointers.",
                    "expectedEntities": [{"name": "MusicPlaylist", "responsibility": "Maintains song sequence."}],
                    "referenceCode": {
                        "filename": "playlist_agg.cpp",
                        "code": """#include <vector>
#include <string>
class Song { public: std::string title; };
class Playlist {
    std::vector<Song*> songs;
public:
    void addSong(Song* s) { songs.push_back(s); }
};"""
                    }
                }},
                {"step_number": 18, "title": "18. Summary", "content": "<p>Aggregation represents weak whole-part relationships where parts exist independently of the container.</p>"}
            ]
        },
        {
            "id": "composition",
            "title": "Composition ('has a' - strong ownership)",
            "description": "Exclusive lifetime ownership where the parent object manages the complete creation and destruction of its child components.",
            "sections": [
                {"step_number": 1, "title": "1. What is it?", "content": "<p><strong>Composition</strong> is a strong whole-part relationship where the child component has no independent existence outside the parent. The child is created by the parent and destroyed when the parent dies.</p>"},
                {"step_number": 2, "title": "2. Why do we need it?", "content": "<p>It encapsulates internal subsystems (e.g., a <code>Building</code> owns <code>Rooms</code>). If the Building is demolished, all Rooms are destroyed simultaneously.</p>"},
                {"step_number": 3, "title": "3. Core idea", "content": "<p>Strict lifetime ownership (Filled Diamond ──◆).</p>"},
                {"step_number": 4, "title": "4. How it works", "content": "<p>In C++, Composition is implemented via direct value members (<code>Engine engine;</code>) or <code>std::unique_ptr&lt;Engine&gt;</code>.</p>"},
                {"step_number": 5, "title": "5. Visual explanation", "content": "<p>Composition Diagram:</p>", "diagram": {
                    "title": "Building and Room Composition UML",
                    "classes": [
                        {"name": "Building", "attributes": [{"visibility": "-", "name": "rooms", "type": "std::vector<Room>"}]},
                        {"name": "Room", "attributes": [{"visibility": "-", "name": "areaSqFt", "type": "double"}]}
                    ],
                    "relationships": [{"from": "Building", "to": "Room", "type": "composition", "label": "owns", "ownership": "Strict", "lifetime": "Coupled", "coupling": "High", "cppSyntax": "class Building { std::vector<Room> rooms; };"}]
                }},
                {"step_number": 6, "title": "6. C++ implementation", "content": "<p>Production C++ Composition with Automatic Cleanup:</p>", "code_example": {
                    "filename": "composition_building.cpp",
                    "code": """#include <iostream>
#include <vector>
#include <string>

class Room {
public:
    int roomNumber;
    explicit Room(int num) : roomNumber(num) {
        std::cout << "  [Room " << roomNumber << "] Constructed.\\n";
    }
    ~Room() {
        std::cout << "  [Room " << roomNumber << "] Destroyed.\\n";
    }
};

class Building {
private:
    std::string name;
    std::vector<Room> rooms; // Composition: Building directly owns Rooms!

public:
    Building(std::string n, int roomCount) : name(std::move(n)) {
        std::cout << "[Building " << name << "] Constructing rooms:\\n";
        for (int i = 1; i <= roomCount; ++i) {
            rooms.emplace_back(i);
        }
    }

    ~Building() {
        std::cout << "[Building " << name << "] Demolishing building (Destroys all rooms!):\\n";
    }
};

int main() {
    {
        Building skyscraper{"Empire State", 3};
    } // Building and all 3 Rooms destroyed automatically!
    return 0;
}"""
                }},
                {"step_number": 7, "title": "7. Code walkthrough", "content": "<p><strong>Line 19:</strong> <code>std::vector&lt;Room&gt; rooms;</code> holds rooms by value. When <code>Building</code> goes out of scope, vector automatically calls <code>~Room()</code> for all 3 rooms.</p>"},
                {"step_number": 8, "title": "8. Real-world example", "content": "<p>TCP Packet header + payload, ChessBoard and Squares, Desktop Window and Titlebar.</p>"},
                {"step_number": 9, "title": "9. When to use", "content": "<p>Use Composition whenever child objects are strictly internal parts that cannot exist without the parent.</p>"},
                {"step_number": 10, "title": "10. When NOT to use", "content": "<p>Do not use Composition when objects need to be shared across multiple containers.</p>"},
                {"step_number": 11, "title": "11. Advantages", "content": "<p>Deterministic automatic destruction; zero risk of memory leaks.</p>"},
                {"step_number": 12, "title": "12. Disadvantages", "content": "<p>High coupling between parent and child implementation.</p>"},
                {"step_number": 13, "title": "13. Variations / Types", "content": "<p>Direct Value Composition, Exclusive Smart Pointer Composition (<code>std::unique_ptr</code>).</p>"},
                {"step_number": 14, "title": "14. Common mistakes", "content": "<p>Leaking raw pointers to internal composite members that outlive the parent object.</p>"},
                {"step_number": 15, "title": "15. Interview questions", "content": "<p><strong>Q:</strong> How does C++ implement Composition with polymorphic child types?</p>"},
                {"step_number": 16, "title": "16. Interview answer", "content": "<p><strong>Answer:</strong> Use <code>std::unique_ptr&lt;IChildInterface&gt;</code>. This preserves exclusive lifetime ownership (Composition) while allowing the parent to hold polymorphic derived implementations.</p>"},
                {"step_number": 17, "title": "17. Practice problem", "content": "<p>Model a <code>CpuProcessor</code> that has Composition with <code>ALU</code> and <code>Registers</code>.</p>", "practice": {
                    "title": "CPU Hardware Composition",
                    "problemStatement": "Implement CPU composition with ALU and Registers.",
                    "requirements": ["CPU owns ALU and Registers", "Automatic cleanup"],
                    "constraints": ["Zero leaks"],
                    "hint": "Use direct value members.",
                    "expectedEntities": [{"name": "CPU", "responsibility": "Hardware processor."}],
                    "referenceCode": {
                        "filename": "cpu_comp.cpp",
                        "code": """class ALU {};
class Registers {};
class CPU {
    ALU alu;
    Registers reg;
};"""
                    }
                }},
                {"step_number": 18, "title": "18. Summary", "content": "<p>Composition is the strongest form of association, guaranteeing tightly bound lifetime and encapsulation.</p>"}
            ]
        },
        {
            "id": "inheritance-vs-realization",
            "title": "Inheritance ('is a') vs Realization ('implements')",
            "description": "Class extension with concrete code reuse vs Interface implementation contracts in C++.",
            "sections": [
                {"step_number": 1, "title": "1. What is it?", "content": "<p><strong>Inheritance (──▷)</strong> inherits both interface and implementation code from a base class. <strong>Realization (..▷)</strong> implements a pure abstract interface contract without inheriting state.</p>"},
                {"step_number": 2, "title": "2. Why do we need it?", "content": "<p>Distinguishing between code reuse (inheritance) and contract fulfillment (realization) prevents bloated, tightly coupled class hierarchies.</p>"},
                {"step_number": 3, "title": "3. Core idea", "content": "<p>Inheritance = Is-a subclass. Realization = Implements interface behavior.</p>"},
                {"step_number": 4, "title": "4. How it works", "content": "<p>Inheritance: <code>class Dog : public Animal</code> (inherits fields and methods). Realization: <code>class Button : public IClickable</code> (overrides pure virtual functions).</p>"},
                {"step_number": 5, "title": "5. Visual explanation", "content": "<p>Comparison Matrix:</p>", "comparison": {
                    "title": "Inheritance vs Realization Matrix",
                    "columns": ["Aspect", "Inheritance (──▷)", "Realization (..▷)", "Best Practice"],
                    "rows": [
                        ["Code Inherited?", "Yes (State & concrete methods)", "No (Only method signatures)", "Prefer Realization for contracts"],
                        ["Multiple?", "Multiple inheritance can cause diamond problem", "Safe to implement multiple interfaces", "Use Realization for mixins"],
                        ["Coupling", "High (White-box)", "Loose (Black-box)", "Realization minimizes coupling"]
                    ]
                }},
                {"step_number": 6, "title": "6. C++ implementation", "content": "<p>Inheritance vs Realization in C++:</p>", "code_example": {
                    "filename": "inherit_vs_realize.cpp",
                    "code": """#include <iostream>
#include <string>

// 1. Realization Target: Pure Interface Contract
class ISerializable {
public:
    virtual ~ISerializable() = default;
    virtual std::string toJson() const = 0;
};

// 2. Inheritance Target: Base Entity with state
class Entity {
protected:
    std::string id;
public:
    explicit Entity(std::string entityId) : id(std::move(entityId)) {}
    virtual ~Entity() = default;
};

// User HAS Inheritance from Entity AND Realization of ISerializable
class User : public Entity, public ISerializable {
private:
    std::string email;
public:
    User(std::string id, std::string mail)
        : Entity(std::move(id)), email(std::move(mail)) {}

    std::string toJson() const override { // Realization override
        return "{\\"id\\": \\"" + id + "\\", \\"email\\": \\"" + email + "\\"}";
    }
};

int main() {
    User u{"U-101", "alice@corp.com"};
    std::cout << u.toJson() << "\\n";
    return 0;
}"""
                }},
                {"step_number": 7, "title": "7. Code walkthrough", "content": "<p><strong>Line 19:</strong> <code>User : public Entity, public ISerializable</code> combines inheritance of state with realization of a serialization contract.</p>"},
                {"step_number": 8, "title": "8. Real-world example", "content": "<p>Java-style <code>implements Serializable, Cloneable</code> mapped to C++ pure virtual mixins.</p>"},
                {"step_number": 9, "title": "9. When to use", "content": "<p>Use Realization for capabilities (e.g. <code>IComparable</code>, <code>IClonable</code>, <code>IObservable</code>). Use Inheritance for genuine domain subtypes.</p>"},
                {"step_number": 10, "title": "10. When NOT to use", "content": "<p>Do not use inheritance just to share a utility function (use composition or free functions).</p>"},
                {"step_number": 11, "title": "11. Advantages", "content": "<p>Realization avoids the diamond problem and enables true decoupling.</p>"},
                {"step_number": 12, "title": "12. Disadvantages", "content": "<p>Realization provides zero default code reuse without helper mixins.</p>"},
                {"step_number": 13, "title": "13. Variations / Types", "content": "<p>Interface realization, Abstract class partial realization.</p>"},
                {"step_number": 14, "title": "14. Common mistakes", "content": "<p>Putting state member variables inside an interface class.</p>"},
                {"step_number": 15, "title": "15. Interview questions", "content": "<p><strong>Q:</strong> Does C++ have an explicit <code>interface</code> or <code>implements</code> keyword like Java/C#?</p>"},
                {"step_number": 16, "title": "16. Interview answer", "content": "<p><strong>Answer:</strong> No. C++ implements interfaces using abstract classes containing only pure virtual functions (<code>= 0</code>) and virtual destructors, and implements realization using public inheritance.</p>"},
                {"step_number": 17, "title": "17. Practice problem", "content": "<p>Design an <code>IComparable</code> interface and realize it in a <code>Product</code> class comparing by price.</p>", "practice": {
                    "title": "IComparable Realization",
                    "problemStatement": "Realize IComparable in a Product class.",
                    "requirements": ["IComparable with compareTo(const IComparable&)", "Product realization"],
                    "constraints": ["Const-correct"],
                    "hint": "Return -1, 0, or 1.",
                    "expectedEntities": [{"name": "IComparable", "responsibility": "Comparison contract."}],
                    "referenceCode": {
                        "filename": "comparable_interface.cpp",
                        "code": """class IComparable {
public:
    virtual ~IComparable() = default;
    virtual int compareTo(const IComparable& other) const = 0;
};"""
                    }
                }},
                {"step_number": 18, "title": "18. Summary", "content": "<p>Realization enforces contract compliance without the tight coupling of state inheritance.</p>"}
            ]
        },
        {
            "id": "dependency",
            "title": "Dependency ('depends on')",
            "description": "The weakest relationship: temporary method parameter, local variable, or return type dependency.",
            "sections": [
                {"step_number": 1, "title": "1. What is it?", "content": "<p><strong>Dependency (..>)</strong> is a transient relationship where class A uses class B temporarily (as a method argument, local variable, or return value) without holding a persistent member variable.</p>"},
                {"step_number": 2, "title": "2. Why do we need it?", "content": "<p>Minimizing persistent state relationships keeps classes decoupled and lightweight.</p>"},
                {"step_number": 3, "title": "3. Core idea", "content": "<p>A change to Class B may require Class A to change, but Class A does not store Class B in memory.</p>"},
                {"step_number": 4, "title": "4. How it works", "content": "<p>Syntax in C++: <code>void generatePdf(const Invoice& inv);</code>.</p>"},
                {"step_number": 5, "title": "5. Visual explanation", "content": "<p>Dependency Flow (Dashed line with open arrow ..>):</p>", "callout": {
                    "type": "tip",
                    "title": "Dependency in C++",
                    "text": "PrinterService - - - > Invoice: PrinterService receives Invoice as a parameter in print(Invoice i), but does NOT have Invoice as a member variable!"
                }},
                {"step_number": 6, "title": "6. C++ implementation", "content": "<p>Transient Dependency in C++:</p>", "code_example": {
                    "filename": "dependency_demo.cpp",
                    "code": """#include <iostream>
#include <string>

class Invoice {
public:
    std::string invoiceId;
    double totalAmount;
    Invoice(std::string id, double amount) : invoiceId(std::move(id)), totalAmount(amount) {}
};

class InvoicePrinter {
public:
    // Dependency: Invoice is used ONLY as a parameter!
    void printToPaper(const Invoice& invoice) const {
        std::cout << "[PRINTER] Printing Invoice #" << invoice.invoiceId 
                  << " | Total: $" << invoice.totalAmount << "\\n";
    }
};

int main() {
    Invoice inv{"INV-9021", 450.00};
    InvoicePrinter printer;
    printer.printToPaper(inv); // Temporary dependency
    return 0;
}"""
                }},
                {"step_number": 7, "title": "7. Code walkthrough", "content": "<p><strong>Line 13:</strong> <code>InvoicePrinter</code> holds NO instance of <code>Invoice</code>; it depends on it only during the execution of <code>printToPaper()</code>.</p>"},
                {"step_number": 8, "title": "8. Real-world example", "content": "<p>Formatters, Serializers, Validators, and Utility math libraries.</p>"},
                {"step_number": 9, "title": "9. When to use", "content": "<p>Use Dependency for stateless helper operations and utility services.</p>"},
                {"step_number": 10, "title": "10. When NOT to use", "content": "<p>Do not pass an object as a parameter repeatedly if the caller logically owns it long-term (use Association/Composition).</p>"},
                {"step_number": 11, "title": "11. Advantages", "content": "<p>Lowest possible coupling between classes.</p>"},
                {"step_number": 12, "title": "12. Disadvantages", "content": "<p>Requires passing parameters at every call site.</p>"},
                {"step_number": 13, "title": "13. Variations / Types", "content": "<p>Parameter Dependency, Local Variable Dependency, Return Type Dependency.</p>"},
                {"step_number": 14, "title": "14. Common mistakes", "content": "<p>Unnecessary heavy <code>#include</code> in headers when a forward declaration in header + include in <code>.cpp</code> suffices.</p>"},
                {"step_number": 15, "title": "15. Interview questions", "content": "<p><strong>Q:</strong> How does Dependency Inversion (DIP) alter classic Dependency relationships?</p>"},
                {"step_number": 16, "title": "16. Interview answer", "content": "<p><strong>Answer:</strong> Classic dependency: High-level class depends on Low-level concrete class (<code>A -> B</code>). With Dependency Inversion: Both High-level and Low-level classes depend on an Abstraction (<code>A -> I <- B</code>), inverting the direction of runtime coupling.</p>"},
                {"step_number": 17, "title": "17. Practice problem", "content": "<p>Create a stateless <code>CsvExporter</code> class that depends on a <code>std::vector&lt;User&gt;</code> parameter.</p>", "practice": {
                    "title": "Stateless Exporter Dependency",
                    "problemStatement": "Build a CsvExporter dependent on User collections.",
                    "requirements": ["Stateless exportToCsv(vector<User>)", "Zero stored state"],
                    "constraints": ["Const reference parameters"],
                    "hint": "Loop through users and print CSV string.",
                    "expectedEntities": [{"name": "CsvExporter", "responsibility": "Formats users to CSV."}],
                    "referenceCode": {
                        "filename": "csv_dep.cpp",
                        "code": """#include <iostream>
#include <vector>
#include <string>
struct User { std::string name, email; };
class CsvExporter {
public:
    void exportToCsv(const std::vector<User>& users) const {
        for (const auto& u : users) {
            std::cout << u.name << "," << u.email << "\\n";
        }
    }
};"""
                    }
                }},
                {"step_number": 18, "title": "18. Summary", "content": "<p>Dependency is the most decoupled relationship, representing temporary method-level collaboration.</p>"}
            ]
        },
        {
            "id": "relationships-matrix",
            "title": "The Master Class Relationship Comparison Matrix",
            "description": "Comprehensive comparative matrix mapping all 6 class relationships with lifetime, ownership, coupling, and C++ code representations.",
            "sections": [
                {"step_number": 1, "title": "1. What is it?", "content": "<p>A unified comparative master guide analyzing all 6 class relationships across 7 critical architectural dimensions.</p>"},
                {"step_number": 2, "title": "2. Why do we need it?", "content": "<p>LLD interviewers frequently test your ability to explain the subtle trade-offs between Association, Aggregation, and Composition.</p>"},
                {"step_number": 3, "title": "3. Core idea", "content": "<p>Coupling and lifetime ownership form a spectrum: Dependency (weakest) -&gt; Association -&gt; Aggregation -&gt; Composition -&gt; Inheritance (strongest).</p>"},
                {"step_number": 4, "title": "4. How it works", "content": "<p>Analyze ownership (Who calls delete?), lifetime (Can child outlive parent?), and C++ memory representation.</p>"},
                {"step_number": 5, "title": "5. Visual explanation", "content": "<p>The Master Class Relationship Comparison Matrix:</p>", "comparison": {
                    "title": "Master LLD Class Relationships Comparison Matrix",
                    "columns": ["Relationship", "Meaning", "Ownership", "Lifetime", "Coupling", "UML Notation", "C++ Implementation"],
                    "rows": [
                        ["Dependency", "'uses a'", "None", "Transient (function scope)", "Lowest", " - - - >", "void foo(const Resource& r);"],
                        ["Association", "'knows a'", "None", "Independent", "Low", "──────>", "class A { B* bPtr; };"],
                        ["Aggregation", "'has a' (shared)", "Weak (Container)", "Independent (Child outlives Parent)", "Moderate", "──────◇", "class Dept { std::vector<Prof*> p; };"],
                        ["Composition", "'has a' (exclusive)", "Strict (Parent)", "Bound (Child dies with Parent)", "High", "──────◆", "class Car { Engine eng; };"],
                        ["Realization", "'implements'", "Contract only", "Polymorphic", "Decoupled", " - - - ▷", "class Svc : public IService"],
                        ["Inheritance", "'is a'", "Subtype", "Unified object memory", "Highest", "──────▷", "class Dog : public Animal"]
                    ]
                }},
                {"step_number": 6, "title": "6. C++ implementation", "content": "<p>Unified C++ Example demonstrating the complete relationship spectrum:</p>", "code_example": {
                    "filename": "master_relationships_spectrum.cpp",
                    "code": """#include <iostream>
#include <vector>
#include <memory>
#include <string>

// 1. Realization Target
class IDriveable {
public:
    virtual ~IDriveable() = default;
    virtual void drive() = 0;
};

// 2. Base for Inheritance
class Vehicle {
protected:
    std::string vin;
public:
    explicit Vehicle(std::string id) : vin(std::move(id)) {}
};

// 3. Composition Target
class Engine {
public:
    void start() { std::cout << "Engine running\\n"; }
};

// 4. Aggregation Target
class Passenger {
public:
    std::string name;
    explicit Passenger(std::string n) : name(std::move(n)) {}
};

// 5. Dependency Target
class Destination {
public:
    std::string address;
};

// Car unifies all 6 relationships in a single class!
class Car : public Vehicle, public IDriveable { // Inheritance + Realization
private:
    Engine engine;                      // Composition (──◆)
    std::vector<Passenger*> passengers;  // Aggregation (──◇)

public:
    Car(std::string id) : Vehicle(std::move(id)) {}

    void boardPassenger(Passenger* p) { // Aggregation
        passengers.push_back(p);
    }

    void travelTo(const Destination& dest) { // Dependency (..>)
        std::cout << "[Car " << vin << "] Navigating to " << dest.address << "\\n";
        engine.start();
    }

    void drive() override { // Realization
        std::cout << "[Car " << vin << "] Cruising on highway with " << passengers.size() << " passenger(s).\\n";
    }
};

int main() {
    Passenger alice{"Alice"};
    Destination beach{"Miami Beach, FL"};

    {
        Car sedan{"VIN-882193"};
        sedan.boardPassenger(&alice);
        sedan.travelTo(beach);
        sedan.drive();
    } // Car & Engine destroyed; Alice and Beach still exist safely!

    return 0;
}"""
                }},
                {"step_number": 7, "title": "7. Code walkthrough", "content": "<p>Shows all 6 relationships working in concert within a single production-grade domain class.</p>"},
                {"step_number": 8, "title": "8. Real-world example", "content": "<p>Automotive telematics, flight reservation systems, and enterprise banking architectures.</p>"},
                {"step_number": 9, "title": "9. When to use", "content": "<p>Review this matrix before any Low-Level Design interview to choose relationships consciously.</p>"},
                {"step_number": 10, "title": "10. When NOT to use", "content": "<p>Do not default to Inheritance when Association or Composition solves the problem with lower coupling.</p>"},
                {"step_number": 11, "title": "11. Advantages", "content": "<p>Provides a standardized mental checklist for evaluating coupling and lifetime.</p>"},
                {"step_number": 12, "title": "12. Disadvantages", "content": "<p>None.</p>"},
                {"step_number": 13, "title": "13. Variations / Types", "content": "<p>Full spectrum analysis.</p>"},
                {"step_number": 14, "title": "14. Common mistakes", "content": "<p>Choosing Inheritance when Composition is needed, creating brittle base classes.</p>"},
                {"step_number": 15, "title": "15. Interview questions", "content": "<p><strong>Q:</strong> Rank the 6 relationships from lowest coupling to highest coupling.</p>"},
                {"step_number": 16, "title": "16. Interview answer", "content": "<p><strong>Answer:</strong> Dependency (lowest) -&gt; Association -&gt; Aggregation -&gt; Realization -&gt; Composition -&gt; Inheritance (highest coupling).</p>"},
                {"step_number": 17, "title": "17. Practice problem", "content": "<p>Identify the relationship in: <code>Order</code> and <code>OrderItem</code> (Composition), <code>Order</code> and <code>Customer</code> (Association), <code>Order</code> and <code>CreditCardPayment</code> (Dependency).</p>", "practice": {
                    "title": "Relationship Identification Practice",
                    "problemStatement": "Map Order relationships correctly.",
                    "requirements": ["OrderItem is composed", "Customer is associated", "Payment is parameter dependency"],
                    "constraints": ["Clean C++ code"],
                    "hint": "Vector of OrderItem values, Customer* pointer, Payment in pay() method.",
                    "expectedEntities": [{"name": "Order", "responsibility": "E-commerce order aggregate."}],
                    "referenceCode": {
                        "filename": "order_relations.cpp",
                        "code": """#include <vector>
class OrderItem {};
class Customer {};
class PaymentToken {};
class Order {
    std::vector<OrderItem> items; // Composition
    Customer* customer;           // Association
public:
    void pay(const PaymentToken& p) {} // Dependency
};"""
                    }
                }},
                {"step_number": 18, "title": "18. Summary", "content": "<p>Understanding the relationship spectrum is the foundation of elegant, maintainable object-oriented software architecture.</p>"}
            ]
        }
    ]
}

write_module(mod_05)
