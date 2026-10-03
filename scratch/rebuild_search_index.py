import json
import glob
import sys
import os

sys.path.insert(0, os.path.abspath('.'))

with open('app/data/roadmap.json', 'r', encoding='utf-8') as f:
    lld_roadmap = json.load(f)

with open('app/data/hld_roadmap.json', 'r', encoding='utf-8') as f:
    hld_roadmap = json.load(f)

search_items = []

# Index LLD
for mod in lld_roadmap['modules']:
    mod_id = mod['id']
    search_items.append({
        'title': f"[LLD] Module {mod_id}: {mod['title']}",
        'url': f"/module/{mod_id}",
        'category': f"LLD - {mod.get('category', 'Module')}",
        'track': 'lld',
        'keywords': f"{mod['title']} LLD Low-Level Design C++ {mod.get('description', '')}"
    })
    for top in mod.get('topics', []):
        search_items.append({
            'title': f"[LLD] {top['title']}",
            'url': f"/module/{mod_id}#{top['id']}",
            'category': f"LLD - Module {mod_id}",
            'track': 'lld',
            'keywords': f"{top['title']} {mod['title']} C++"
        })

# Index HLD
for mod in hld_roadmap['modules']:
    mod_id = mod['id']
    search_items.append({
        'title': f"[HLD] Module {mod_id}: {mod['title']}",
        'url': f"/hld/module/{mod_id}",
        'category': f"HLD - {mod.get('category', 'Module')}",
        'track': 'hld',
        'keywords': f"{mod['title']} HLD System Design Architecture {mod.get('description', '')}"
    })
    for top in mod.get('topics', []):
        search_items.append({
            'title': f"[HLD] {top['title']}",
            'url': f"/hld/module/{mod_id}#{top['id']}",
            'category': f"HLD - Module {mod_id}",
            'track': 'hld',
            'keywords': f"{top['title']} {mod['title']} System Design Distributed Architecture"
        })

with open('app/data/search_index.json', 'w', encoding='utf-8') as f:
    json.dump(search_items, f, indent=2)

print(f"Total search index items generated: {len(search_items)}")
