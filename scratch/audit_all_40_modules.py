import os
import json

with open('app/data/hld_roadmap.json', 'r', encoding='utf-8') as f:
    roadmap = json.load(f)

total_modules = len(roadmap['modules'])
print(f"Total modules in roadmap: {total_modules}")

all_pass = True
total_topics_count = 0
total_kb_size = 0

for m in roadmap['modules']:
    m_id = int(m['id'])
    m_title = m['title']
    expected_topic_ids = [t['id'] for t in m['topics']]
    
    file_path = f"content/hld/module_{m_id:02d}.json"
    if not os.path.exists(file_path):
        print(f"[FAIL] Missing file: {file_path}")
        all_pass = False
        continue
    
    file_size_kb = os.path.getsize(file_path) / 1024
    total_kb_size += file_size_kb
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            mod_data = json.load(f)
    except Exception as e:
        print(f"[FAIL] JSON decode error in {file_path}: {e}")
        all_pass = False
        continue
    
    actual_topic_ids = [t['id'] for t in mod_data.get('topics', [])]
    total_topics_count += len(actual_topic_ids)
    
    # Check for missing topics
    missing = set(expected_topic_ids) - set(actual_topic_ids)
    extra = set(actual_topic_ids) - set(expected_topic_ids)
    
    if missing:
        print(f"[FAIL] Module {m_id:02d} ({file_size_kb:.1f} KB) MISSING TOPICS: {missing}")
        all_pass = False
    elif extra:
        print(f"[WARN] Module {m_id:02d} ({file_size_kb:.1f} KB) EXTRA TOPICS: {extra}")
    else:
        # Verify keys in each topic
        for t in mod_data['topics']:
            required_keys = ['id', 'title', 'definition', 'why_we_need_it', 'real_world_analogy', 'how_it_works', 'conceptual_breakdown', 'arch_diagram', 'tradeoffs', 'failure_scenarios', 'common_mistakes', 'interview_questions']
            missing_keys = [k for k in required_keys if k not in t]
            if missing_keys:
                print(f"[FAIL] Module {m_id:02d} topic {t.get('id')} missing keys: {missing_keys}")
                all_pass = False

    print(f"Module {m_id:02d}: {len(actual_topic_ids)}/{len(expected_topic_ids)} topics OK ({file_size_kb:.1f} KB) - {m_title[:45]}")

print("\n" + "="*50)
print(f"Audit Complete: All Pass = {all_pass}")
print(f"Total Topics: {total_topics_count}")
print(f"Total Content Size: {total_kb_size:.1f} KB ({total_kb_size/1024:.2f} MB)")
