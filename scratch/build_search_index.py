import json
import os
import glob

content_files = sorted(glob.glob("content/module_*.json"))
search_index = []

for cf in content_files:
    with open(cf, "r", encoding="utf-8") as f:
        data = json.load(f)
    mod_id = data.get("module_id", "")
    mod_title = data.get("module_title", "")
    
    for t in data.get("topics", []):
        t_id = t["id"]
        t_title = t.get("title", "")
        summary = t.get("description") or t.get("definition") or ""
        tags = [mod_title, t_title, f"Module {mod_id}"]
        if "cpp" in t_id or "oop" in t_id:
            tags.append("C++")
        if "solid" in t_id:
            tags.append("SOLID")
        if "pattern" in t_id:
            tags.append("Design Patterns")
        if "concurrency" in t_id or "mutex" in t_id or "atomic" in t_id:
            tags.append("Concurrency")

        search_index.append({
            "title": f"{t_title} (Module {mod_id})",
            "url": f"/module/{int(mod_id):02d}#{t_id}",
            "type": "topic",
            "module_id": mod_id,
            "module_title": mod_title,
            "topic_id": t_id,
            "summary": summary[:200] + "..." if len(summary) > 200 else summary,
            "tags": tags
        })

# Also add high-level pages
search_index.append({
    "title": "14-Step Systematic LLD Interview Roadmap",
    "url": "/interview-framework",
    "type": "guide",
    "module_id": "21",
    "module_title": "14-Step LLD Interview Framework",
    "topic_id": "the-14-step-interview-process",
    "summary": "Master the repeatable 14-step battle-tested interview roadmap from requirement gathering to clean C++ code.",
    "tags": ["Interview", "Framework", "Roadmap", "Process"]
})
search_index.append({
    "title": "Quick Revision Cheat Sheets (SOLID, Patterns, UML, Pointers, Mutexes)",
    "url": "/cheat-sheets",
    "type": "cheatsheet",
    "module_id": "24",
    "module_title": "Quick Revision Cheat Sheets",
    "topic_id": "solid-cheat-sheet",
    "summary": "High-yield summary sheets for fast revision before tech interviews: SOLID matrix, Pattern decision tree, UML cheat sheet, Smart Pointers, Concurrency.",
    "tags": ["Cheat Sheet", "SOLID", "Patterns", "UML", "Smart Pointers", "Mutex"]
})
search_index.append({
    "title": "Interactive Modern C++ LLD Playground",
    "url": "/playground",
    "type": "playground",
    "module_id": "00",
    "module_title": "Interactive Playground",
    "topic_id": "playground",
    "summary": "Interactive C++ design sandbox with preset design patterns (Singleton, Strategy, Observer, Factory, State, ThreadSafe LRU Cache).",
    "tags": ["Playground", "Sandbox", "Interactive", "C++"]
})

with open("app/data/search_index.json", "w", encoding="utf-8") as f:
    json.dump(search_index, f, indent=2)

print(f"Generated search_index.json with {len(search_index)} indexed items!")
