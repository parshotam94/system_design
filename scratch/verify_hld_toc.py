"""
Verify the HLD module TOC is rendered correctly.
Run from project root: python scratch/verify_hld_toc.py
"""
import sys, os
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=" * 60)
print("HLD TOC Verification")
print("=" * 60)

test_modules = ['01', '06', '24', '40']
all_pass = True

for mod_id in test_modules:
    res = client.get(f'/hld/module/{mod_id}')
    checks = {
        'HTTP 200': res.status_code == 200,
        'module-toc aside': 'class="module-toc"' in res.text,
        'toc-list ul': 'id="hld-toc-list"' in res.text,
        'hld-toc-link class': 'class="hld-toc-link"' in res.text,
        'data-topic-id attr': 'data-topic-id=' in res.text,
        'toc-status-icon': 'class="toc-status-icon"' in res.text,
        'topic-container div': 'class="topic-container"' in res.text,
        'btn-hld-topic-toggle': 'btn-hld-topic-toggle' in res.text,
        'syncTOCIcons JS': 'syncTOCIcons' in res.text,
        'IntersectionObserver': 'IntersectionObserver' in res.text,
        'hld_progress.js loaded': 'hld_progress.js' in res.text,
    }
    
    passed = sum(1 for v in checks.values() if v)
    failed = [k for k, v in checks.items() if not v]
    
    print(f"\nModule {mod_id}: {passed}/{len(checks)} checks passed")
    for check, result in checks.items():
        status = "✓" if result else "✗"
        print(f"  {status} {check}")
    
    if failed:
        all_pass = False
        print(f"  FAILED: {failed}")

print("\n" + "=" * 60)
print("OVERALL:", "ALL PASS ✓" if all_pass else "SOME FAILURES ✗")
print("=" * 60)
