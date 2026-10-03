import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

res = client.get('/hld')
print(f"HLD Home status: {res.status_code}")
assert res.status_code == 200

all_ok = True
for i in range(1, 41):
    mod_id = f"{i:02d}"
    res = client.get(f'/hld/module/{mod_id}')
    if res.status_code != 200:
        print(f"[FAIL] Module {mod_id} returned status {res.status_code}")
        all_ok = False
    else:
        # Check that page rendered successfully with topics
        assert "topic-container" in res.text
        print(f"Module {mod_id} OK - Status 200 - Rendered with topics")

print(f"\nAll 40 HLD module endpoints verified: {all_ok}")
