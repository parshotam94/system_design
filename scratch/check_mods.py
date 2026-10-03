import json

with open('app/data/hld_roadmap.json', 'r', encoding='utf-8') as f:
    roadmap = json.load(f)

for m in roadmap['modules'][28:]:
    print(f"=== Module {m['id']}: {m['title']} ===")
    for t in m['topics']:
        print(f"  - {t['id']}: {t['title']}")
