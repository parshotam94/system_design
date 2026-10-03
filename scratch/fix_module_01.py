import json

with open("content/module_01.json", "r", encoding="utf-8") as f:
    m1 = json.load(f)

header_topic = {
    "id": "header-source-separation",
    "title": "Header & Source File Separation",
    "description": "Mastering the compilation model: header files (.hpp), implementation files (.cpp), Include Guards (#pragma once), Forward Declarations, and the One Definition Rule (ODR).",
    "sections": [
        {
            "step_number": 1,
            "title": "1. What is it",
            "content": "<p>In C++, code is partitioned into <strong>Header Files</strong> (<code>.hpp</code> / <code>.h</code>) containing interface declarations, class layouts, and function prototypes, and <strong>Source Files</strong> (<code>.cpp</code>) containing compiled method definitions and executable logic.</p>"
        },
        {
            "step_number": 2,
            "title": "2. Why it exists",
            "content": "<p>C++ uses a translation unit (TU) compilation model. Separating declarations from definitions allows independent compilation of separate <code>.cpp</code> files into <code>.o</code> / <code>.obj</code> object files, dramatically accelerating incremental build times and enabling clean interface distribution without exposing proprietary source code.</p>"
        },
        {
            "step_number": 3,
            "title": "3. Real-world analogy",
            "content": "<p>A restaurant menu (Header File): customers read the list of available dishes and ingredients (interfaces) without needing to stand inside the kitchen and watch the chef chop onions and cook (Source File implementation).</p>"
        },
        {
            "step_number": 4,
            "title": "4. How it works",
            "content": "<p>The preprocessor replaces <code>#include \"file.hpp\"</code> with the raw text of the header. <strong>Include guards</strong> (<code>#pragma once</code>) prevent circular compilation errors. <strong>Forward declarations</strong> (<code>class Order;</code>) reduce compile-time header coupling by telling the compiler a type exists without needing to parse its full header.</p>"
        },
        {
            "step_number": 5,
            "title": "5. Visual explanation",
            "content": "<p>Compilation pipeline: Preprocessor -> Compiler -> Assembler -> Linker:</p>",
            "callout": {
                "type": "tip",
                "title": "Forward Declarations vs #include",
                "text": "If a header file only holds a pointer or reference to Class B (e.g. B* or const B&), use a forward declaration 'class B;' instead of '#include \"B.hpp\"' to prevent massive recompilation cascades across your project."
            }
        },
        {
            "step_number": 6,
            "title": "6. C++ implementation",
            "content": "<p>Clean Header (.hpp) and Source (.cpp) separation with Forward Declaration:</p>",
            "code_example": {
                "filename": "CustomerService.hpp",
                "code": "// CustomerService.hpp\n#pragma once\n#include <string>\n#include <memory>\n\n// Forward declaration: does NOT require #include \"Order.hpp\"\nclass Order;\n\nclass CustomerService {\nprivate:\n    std::string serviceRegion;\n\npublic:\n    explicit CustomerService(std::string region);\n    ~CustomerService();\n\n    // Takes reference to forward-declared type\n    [[nodiscard]] bool processOrder(const Order& order) const;\n};"
            }
        },
        {
            "step_number": 7,
            "title": "7. Code walkthrough",
            "content": "<p><strong>#pragma once:</strong> Directs the preprocessor to include this file only once per translation unit.<br><strong>class Order;:</strong> Forward declaration. Informs the compiler that <code>Order</code> is a class type without parsing <code>Order.hpp</code>.<br><strong>CustomerService.cpp:</strong> Includes <code>Order.hpp</code> internally to execute methods on the order.</p>"
        },
        {
            "step_number": 8,
            "title": "8. Real-world example",
            "content": "<p>All major production C++ libraries (Boost, Qt, Unreal Engine, Chromium, LLVM) separate public API headers from private implementation details.</p>"
        },
        {
            "step_number": 9,
            "title": "9. When to use",
            "content": "<p>Use for all non-template production C++ classes to minimize build times and decouple module dependencies.</p>"
        },
        {
            "step_number": 10,
            "title": "10. When NOT to use",
            "content": "<p>C++ template classes and <code>constexpr</code> functions must have their definitions available in header files because the compiler instantiates templates at compile-time.</p>"
        },
        {
            "step_number": 11,
            "title": "11. Advantages",
            "content": "<ul style='margin-left: 1.25rem;'><li>Fast incremental compilation.</li><li>Prevents circular dependency include deadlocks.</li><li>Enforces separation of interface from implementation.</li></ul>"
        },
        {
            "step_number": 12,
            "title": "12. Disadvantages",
            "content": "<ul style='margin-left: 1.25rem;'><li>Requires maintaining two synchronized files (.hpp and .cpp) for each class.</li></ul>"
        },
        {
            "step_number": 13,
            "title": "13. Variations / Types",
            "content": "<p>Header-only libraries, PImpl (Pointer to Implementation) idiom, C++20 Modules (<code>import std;</code>).</p>"
        },
        {
            "step_number": 14,
            "title": "14. Common mistakes",
            "content": "<p>Defining non-inline functions in header files, causing 'multiple definition' linker errors (ODR violation).</p>"
        },
        {
            "step_number": 15,
            "title": "15. Refactoring / Anti-patterns",
            "content": "<p>Refactoring <code>#include \"HeavyEngine.hpp\"</code> in headers to forward declarations cuts compile times by 80%.</p>"
        },
        {
            "step_number": 16,
            "title": "16. Interview questions",
            "content": "<p><strong>Q: What is the One Definition Rule (ODR)?</strong><br><em>A:</em> A rule stating that any variable, function, class, or template can have only one definition across the entire program (or per translation unit for inline functions).</p>"
        },
        {
            "step_number": 17,
            "title": "17. Edge cases",
            "content": "<p>Inline functions and static template members require special handling to ensure single identical linkage across translation units.</p>"
        },
        {
            "step_number": 18,
            "title": "18. Practice exercise",
            "content": "<p>Convert a circular include between Class A and Class B into a clean forward declaration design.</p>"
        }
    ]
}

# Replace topic 6 (index 6, which was topic 7) or insert if needed
found = False
for idx, t in enumerate(m1["topics"]):
    if t["id"] in ["composition", "header-source-separation"]:
        m1["topics"][idx] = header_topic
        found = True
        break

if not found:
    m1["topics"].append(header_topic)

with open("content/module_01.json", "w", encoding="utf-8") as f:
    json.dump(m1, f, indent=2)

print("Updated module_01.json with header-source-separation topic!")
