import json
import glob
import os

search_index = []

# 1. Index LLD Modules
lld_files = sorted(glob.glob("content/module_*.json"))
for cf in lld_files:
    try:
        with open(cf, "r", encoding="utf-8") as f:
            data = json.load(f)
        mod_id = data.get("module_id", "")
        mod_title = data.get("module_title", "")
        
        for t in data.get("topics", []):
            t_id = t["id"]
            t_title = t.get("title", "")
            summary = t.get("description") or t.get("definition") or ""
            search_index.append({
                "title": f"[LLD] {t_title} (Module {mod_id})",
                "url": f"/module/{int(mod_id):02d}#{t_id}",
                "type": "lld_topic",
                "module_id": mod_id,
                "module_title": mod_title,
                "topic_id": t_id,
                "summary": summary[:200] + "..." if len(summary) > 200 else summary,
                "tags": [mod_title, t_title, f"Module {mod_id}", "LLD", "C++"]
            })
    except Exception as e:
        print(f"Error indexing LLD file {cf}: {e}")

# 2. Index HLD Roadmap Topics
hld_roadmap_path = "app/data/hld_roadmap.json"
if os.path.exists(hld_roadmap_path):
    with open(hld_roadmap_path, "r", encoding="utf-8") as f:
        hld_data = json.load(f)

    for mod in hld_data.get("modules", []):
        mod_id = mod["id"]
        mod_title = mod["title"]
        mod_desc = mod.get("description", "")
        
        search_index.append({
            "title": f"[HLD Module] {mod_title} (HLD {mod_id})",
            "url": f"/hld/module/{mod_id}",
            "type": "hld_module",
            "module_id": mod_id,
            "module_title": mod_title,
            "topic_id": mod["slug"],
            "summary": mod_desc,
            "tags": [mod_title, mod["level"], mod["category"], "HLD", "System Design", "Architecture"]
        })

        for t in mod.get("topics", []):
            t_id = t["id"]
            t_title = t.get("title", "")
            search_index.append({
                "title": f"[HLD] {t_title} (HLD {mod_id})",
                "url": f"/hld/module/{mod_id}#{t_id}",
                "type": "hld_topic",
                "module_id": mod_id,
                "module_title": mod_title,
                "topic_id": t_id,
                "summary": f"{mod_title} &bull; {mod['category']}",
                "tags": [mod_title, t_title, f"HLD {mod_id}", "HLD", "System Design", "Distributed Systems"]
            })

# 3. High-Level Pages & Tools
search_index.append({
    "title": "[HLD Tool] Interactive Capacity & Back-of-the-Envelope Calculator",
    "url": "/hld/calculator",
    "type": "hld_tool",
    "module_id": "03",
    "module_title": "Capacity Estimation",
    "topic_id": "capacity-calculator",
    "summary": "Interactive QPS, Storage, Bandwidth, Memory, and Cache sizing calculator for System Design interviews.",
    "tags": ["HLD", "Capacity Estimation", "Calculator", "QPS", "Storage", "Bandwidth", "Back-of-the-Envelope"]
})

search_index.append({
    "title": "[LLD Guide] 14-Step Systematic LLD Interview Roadmap",
    "url": "/interview-framework",
    "type": "guide",
    "module_id": "21",
    "module_title": "14-Step LLD Interview Framework",
    "topic_id": "the-14-step-interview-process",
    "summary": "Master the repeatable 14-step battle-tested interview roadmap from requirement gathering to clean C++ code.",
    "tags": ["LLD", "Interview", "Framework", "Roadmap", "Process"]
})

search_index.append({
    "title": "[LLD Guide] Quick Revision Cheat Sheets (SOLID, Patterns, UML, Pointers)",
    "url": "/cheat-sheets",
    "type": "cheatsheet",
    "module_id": "24",
    "module_title": "Quick Revision Cheat Sheets",
    "topic_id": "solid-cheat-sheet",
    "summary": "High-yield summary sheets for fast revision: SOLID matrix, Pattern decision tree, UML cheat sheet, Smart Pointers, Concurrency.",
    "tags": ["LLD", "Cheat Sheet", "SOLID", "Patterns", "UML", "Smart Pointers"]
})

search_index.append({
    "title": "[LLD Tool] Interactive Modern C++ Design Pattern Playground",
    "url": "/playground",
    "type": "playground",
    "module_id": "00",
    "module_title": "Interactive Playground",
    "topic_id": "playground",
    "summary": "Interactive C++ design sandbox with preset design patterns (Singleton, Strategy, Observer, Factory, State, ThreadSafe LRU Cache).",
    "tags": ["LLD", "Playground", "Sandbox", "Interactive", "C++"]
})

with open("app/data/search_index.json", "w", encoding="utf-8") as f:
    json.dump(search_index, f, indent=2)

print(f"Generated unified search_index.json with {len(search_index)} indexed items across LLD & HLD!")
