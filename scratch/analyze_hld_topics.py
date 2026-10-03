import json
from pathlib import Path

roadmap = json.load(open('app/data/hld_roadmap.json', encoding='utf-8'))
print(f"Total modules in roadmap: {len(roadmap['modules'])}")

short_modules = []
for m in roadmap['modules']:
    mid = m['id']
    rtopics = m.get('topics', [])
    cfile = Path(f'content/hld/module_{mid}.json')
    if cfile.exists():
        cdata = json.load(open(cfile, encoding='utf-8'))
        ctopics = cdata.get('topics', [])
        size_kb = round(cfile.stat().st_size / 1024, 1)
        r_ids = [t['id'] for t in rtopics]
        c_ids = [t['id'] for t in ctopics]
        missing = [t for t in r_ids if t not in c_ids]
        print(f"Mod {mid} ({m['title'][:30]}): {len(ctopics)}/{len(rtopics)} topics | {size_kb} KB | missing in content: {missing}")
        if len(ctopics) < len(rtopics) or size_kb < 20:
            short_modules.append(mid)
    else:
        print(f"Mod {mid}: MISSING")
        short_modules.append(mid)

print(f"\nModules needing expansion: {len(short_modules)} -> {short_modules}")
