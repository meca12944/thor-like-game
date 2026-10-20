"""Tiny PixelLab v2 client for the Felt exterior build. Key ONLY from env PIXELLAB_API_KEY (never printed / logged).
Every finished job is appended to usage.jsonl (endpoint, name, status, billing_usage) so the real spend can be summed."""
import os, sys, json, time, base64, urllib.request, urllib.error
K = os.environ.get('PIXELLAB_API_KEY') or sys.exit('PIXELLAB_API_KEY missing')
API = 'https://api.pixellab.ai/v2'; D = os.path.dirname(os.path.abspath(__file__))
USAGE = os.path.join(D, 'usage.jsonl'); CAP = float(os.environ.get('HERO_CAP', 180))

def req(m, p, body=None):
    r = urllib.request.Request(API + p, method=m, data=json.dumps(body).encode() if body is not None else None,
        headers={'Authorization': 'Bearer ' + K, 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    for i in range(5):
        try:
            with urllib.request.urlopen(r, timeout=180) as f: return json.load(f)
        except urllib.error.HTTPError as e:
            return {'_http': e.code, '_err': e.read().decode('utf-8', 'replace')[:600]}
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            if m == 'POST' and i == 0 and '/background-jobs' not in p: pass  # connection never reached the server -> safe to retry
            time.sleep(2 ** (i + 1))
    return {'_http': -1, '_err': 'network'}

def spent():
    if not os.path.exists(USAGE): return 0.0
    t = 0.0
    for l in open(USAGE):
        u = json.loads(l).get('usage') or {}
        t += float(u.get('usd_or_generations') or u.get('generations') or u.get('total') or 0)
    return t

def usage_num(u):
    if not isinstance(u, dict): return 0.0
    for k in ('generations', 'total', 'amount', 'usd_or_generations'):
        if isinstance(u.get(k), (int, float)): return float(u[k])
    return 0.0

def b64(path): return base64.b64encode(open(path, 'rb').read()).decode()

def submit(endpoint, body):
    if total() >= CAP: sys.exit(f"cap {CAP} reached ({total()})")
    for i in range(6):
        r = req('POST', endpoint, body)
        if r.get('_http') == 429 or 'heavy load' in str(r.get('_err', '')): time.sleep(10 + 10 * i); continue
        return r
    return r

def wait(jid, every=6, limit=900):
    t0 = time.time()
    while time.time() - t0 < limit:
        time.sleep(every); j = req('GET', f'/background-jobs/{jid}')
        if j.get('status') in ('completed', 'failed', 'error') or j.get('_http'): return j
    return {'status': 'timeout'}

def log(name, endpoint, j):
    u = j.get('billing_usage') or j.get('usage') or (j.get('last_response') or {}).get('billing_usage')
    rec = {'t': time.strftime('%F %T'), 'name': name, 'endpoint': endpoint, 'status': j.get('status'), 'usage': u, 'n': usage_num(u)}
    with open(USAGE, 'a') as f: f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    return rec

def images(j):
    lr = j.get('last_response') or {}
    out = []
    for im in (lr.get('images') or []) + ([lr['image']] if lr.get('image') else []):
        if isinstance(im, dict) and im.get('base64'): out.append(base64.b64decode(im['base64']))
        elif isinstance(im, str) and len(im) > 100: out.append(base64.b64decode(im.split(',')[-1]))
    return out

def total(): return sum(json.loads(l).get('n', 0) for l in open(USAGE)) if os.path.exists(USAGE) else 0.0
