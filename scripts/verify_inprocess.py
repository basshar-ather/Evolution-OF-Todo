"""Quick in-process verification using FastAPI TestClient.
"""
from pathlib import Path
import sys, time
ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "phases" / "phase-1" / "backend"
sys.path.insert(0, str(BACKEND))

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

time.sleep(0.1)

def assert_ok(cond,msg):
    if not cond:
        raise SystemExit(msg)

resp = client.get('/health')
assert_ok(resp.status_code==200, 'health failed')

# create
payload = {"title":"verify","description":"inproc"}
r = client.post('/todos', json=payload)
assert_ok(r.status_code==201, f'post failed {r.status_code}')
tid = r.json().get('id')
assert_ok(tid, 'missing id')

# list
r = client.get('/todos')
assert_ok(r.status_code==200 and any(t['id']==tid for t in r.json()), 'list failed')

# update
upd = {"title":"v2","description":"x","status":"completed"}
r = client.put(f'/todos/{tid}', json=upd)
assert_ok(r.status_code==200 and r.json().get('title')=='v2', 'update failed')

# delete
r = client.delete(f'/todos/{tid}')
assert_ok(r.status_code==204, 'delete failed')

print('in-process verification passed')
