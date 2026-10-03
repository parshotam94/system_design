import sys, os
sys.path.insert(0, '.')
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

for mod_id in ['01', '06', '24', '40']:
    res = client.get(f'/hld/module/{mod_id}')
    checks = [
        ('HTTP_200', res.status_code == 200),
        ('module-toc aside', 'module-toc' in res.text),
        ('hld-toc-list', 'hld-toc-list' in res.text),
        ('hld-toc-link', 'hld-toc-link' in res.text),
        ('data-topic-id', 'data-topic-id' in res.text),
        ('toc-status-icon', 'toc-status-icon' in res.text),
        ('topic-container', 'topic-container' in res.text),
        ('btn-hld-topic-toggle', 'btn-hld-topic-toggle' in res.text),
        ('syncTOCIcons', 'syncTOCIcons' in res.text),
        ('IntersectionObserver', 'IntersectionObserver' in res.text),
    ]
    passed = sum(1 for _, v in checks)
    failed = [k for k, v in checks if not v]
    print(f'Module {mod_id}: {sum(1 for _,v in checks if v)}/{len(checks)}  FAILED:{failed}')
