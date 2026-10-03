import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))
from fastapi.testclient import TestClient
from app.main import app

def verify():
    roadmap_path = os.path.join("app", "data", "roadmap.json")
    with open(roadmap_path, "r", encoding="utf-8") as f:
        roadmap = json.load(f)

    total_modules = len(roadmap["modules"])
    print(f"Total modules in roadmap: {total_modules}")
    assert total_modules == 24, f"Expected 24 modules, got {total_modules}"

    total_topics_checked = 0
    missing_topics = []

    for mod in roadmap["modules"]:
        mod_id = mod["id"]
        mod_num = int(mod_id)
        filename = f"module_{mod_num:02d}.json"
        content_path = os.path.join("content", filename)

        assert os.path.exists(content_path), f"Missing content file: {content_path}"

        with open(content_path, "r", encoding="utf-8") as f:
            content = json.load(f)

        content_topic_ids = {t["id"]: t for t in content["topics"]}

        for topic in mod["topics"]:
            t_id = topic["id"]
            if t_id not in content_topic_ids:
                missing_topics.append((mod_id, t_id, topic["title"]))
            else:
                t_data = content_topic_ids[t_id]
                assert "title" in t_data and len(t_data["title"]) > 0
                if "sections" in t_data:
                    assert len(t_data["sections"]) > 0
                else:
                    assert "definition" in t_data and len(t_data["definition"]) > 0
                    assert "why_it_matters" in t_data and len(t_data["why_it_matters"]) > 0
                    assert "cpp_implementation" in t_data and len(t_data["cpp_implementation"]) > 50
                total_topics_checked += 1

    print(f"Successfully verified {total_topics_checked} topics across all 24 modules!")
    if missing_topics:
        print(f"WARNING: Missing {len(missing_topics)} topics: {missing_topics}")
    else:
        print("ALL TOPICS FROM ROADMAP ARE FULLY POPULATED!")

    # Test FastAPI endpoints
    client = TestClient(app)
    
    # 1. Main Pages
    res = client.get("/")
    assert res.status_code == 200, f"Root returned {res.status_code}"

    res = client.get("/interview-framework")
    assert res.status_code == 200, f"Framework returned {res.status_code}"

    res = client.get("/cheat-sheets")
    assert res.status_code == 200, f"Cheat sheets returned {res.status_code}"

    res = client.get("/playground")
    assert res.status_code == 200, f"Playground returned {res.status_code}"

    # 2. Test All 24 Module Pages
    for i in range(1, 25):
        slug_num = f"{i:02d}"
        res = client.get(f"/module/{slug_num}")
        assert res.status_code == 200, f"Module {slug_num} returned {res.status_code}"

    # 3. Test APIs
    res = client.get("/api/modules")
    assert res.status_code == 200
    assert len(res.json()["modules"]) == 24

    res = client.get("/api/search?q=singleton")
    assert res.status_code == 200
    assert len(res.json()["results"]) > 0

    print("ALL 24 MODULE ROUTES AND API ENDPOINTS RETURNED HTTP 200 OK!")

if __name__ == "__main__":
    verify()
