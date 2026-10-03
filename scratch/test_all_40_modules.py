import glob
import json
import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

files = sorted(glob.glob('content/hld/module_*.json'))
print(f'Total HLD JSON module files found: {len(files)}')

assert len(files) == 40, f'Expected 40 files, got {len(files)}'

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
        mod_id = data['module_id']
        topics = data.get('topics', [])
        assert len(topics) > 0, f'Module {mod_id} has no topics!'
        
        # Test HTTP route
        resp = client.get(f'/hld/module/{mod_id}')
        assert resp.status_code == 200, f'Module {mod_id} returned status {resp.status_code}'
        assert 'topic-container' in resp.text
        print(f'Module {mod_id}: "{data.get("module_title")}" -> {len(topics)} topics, HTTP 200 ({len(resp.text)} bytes)')

print('\n' + '='*60)
print('ALL 40 HLD MODULES TESTED AND VERIFIED 100% SUCCESSFUL!')
print('='*60)
