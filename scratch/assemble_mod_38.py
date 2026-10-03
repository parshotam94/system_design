import json

with open('scratch/t1_t4.json', 'r', encoding='utf-8') as f:
    t1_4 = json.load(f)

with open('scratch/t5_t8.json', 'r', encoding='utf-8') as f:
    t5_8 = json.load(f)

with open('scratch/t9_t13.json', 'r', encoding='utf-8') as f:
    t9_13 = json.load(f)

all_topics = t1_4 + t5_8 + t9_13

mod38 = {
    "module_id": 38,
    "title": "Real-World System Design Problem Library",
    "description": "Master 13 real-world, end-to-end system design case studies commonly asked in FAANG/top-tier engineering interviews, progressing from beginner fundamentals (TinyURL, Pastebin, Notification System) to intermediate industry standards (YouTube, Twitter, WhatsApp, Uber, Rate Limiter, Redis Cache) to advanced distributed platforms (Google Drive, Google Docs OT/CRDT, Distributed Web Crawler, Distributed Job Scheduler).",
    "topics": all_topics
}

with open('content/hld/module_38.json', 'w', encoding='utf-8') as f:
    json.dump(mod38, f, indent=2, ensure_ascii=False)

print(f"Module 38 assembled successfully with {len(all_topics)} topics!")
