#!/usr/bin/env python3
"""Reachability check (option A 10-24): every map in the chapter-1/field set, walked like world.js buildMap marks solids.
From the default spawn: every spawn, exit, door, npc, chest, clue, waystone must be reachable (blocking objects: a reachable neighbour).
Cross-map: every exit/door 'to' map exists and its spawn exists. Usage: python3 tools/hd/fields/reach_all.py"""
import json, os, glob, sys
from collections import deque
R = os.path.join(os.path.dirname(__file__), '../../..'); MP = os.path.join(R, 'maps')
TS = json.load(open(os.path.join(MP, 'tilesets.json')))
names = ['prologue_grave', 'felt', 'field_felt', 'arachne', 'arachne_boss', 'field00'] + ['field%02d' % i for i in range(2, 10)] + sorted(os.path.basename(p)[:-5] for p in glob.glob(MP + '/felt_int_*.json'))
BLOCK = {'chest', 'sign', 'heal', 'waystone', 'npc', 'door'}
def load(n): return json.load(open(os.path.join(MP, n + '.json')))
def grid(j):
    w, h = j['w'], j['h']; S = set(j.get('solid', [])); ts = TS.get(j.get('tileset', 'field'), {}) if isinstance(TS, dict) else {}
    sol = [[0] * w for _ in range(h)]
    for y in range(h):
        row = j['ground'][y] if y < len(j['ground']) else ''
        for x in range(w):
            ch = row[x] if x < len(row) else '#'; L = j['legend'].get(ch, 'wall' if j.get('tileset') == 'dungeon' else 'grass')
            L = {'ground': L} if isinstance(L, str) else L; s = ch in S
            if 'solid' in L: s = L['solid']
            if L.get('ground') in (ts.get('solidTiles') or []): s = True
            if L.get('hop'): s = True
            sol[y][x] = 1 if s else 0
    hds = j.get('hds') or ([dict(j['hd'], gx=0, gy=0)] if j.get('hd') else [])
    for hd in hds:
        for q in hd.get('props', []):
            if q.get('solid') and not q.get('hideFlag'):  # hideFlag props (breakable brambles) open up in play
                x0, y0, x1, y1 = q['solid']
                for yy in range(y0, y1 + 1):
                    for xx in range(x0, x1 + 1):
                        X, Y = xx + hd['gx'], yy + hd['gy']
                        if 0 <= X < w and 0 <= Y < h: sol[Y][X] = 1
    for o in j.get('objects', []):
        if o['type'] in BLOCK and not o.get('walk') and not o.get('wander'): sol[int(o['y'])][int(o['x'])] = 1
    return sol
bad = 0; out = []
for n in names:
    j = load(n); w, h = j['w'], j['h']; sol = grid(j); sp = j.get('spawns', {})
    st = sp.get('default') or next(iter(sp.values()))
    sx, sy = int(st[0]), int(st[1]); seen = [[0] * w for _ in range(h)]; dq = deque([(sx, sy)]); seen[sy][sx] = 1; cnt = 0
    if sol[sy][sx]: out.append(f'{n}: default spawn on a solid cell'); bad += 1
    while dq:
        x, y = dq.popleft(); cnt += 1
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            X, Y = x + dx, y + dy
            if 0 <= X < w and 0 <= Y < h and not seen[Y][X] and not sol[Y][X]: seen[Y][X] = 1; dq.append((X, Y))
    def ok(x, y, nb):
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and seen[y][x]: return True
        return nb and any(0 <= x + a < w and 0 <= y + b < h and seen[y + b][x + a] for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    probs = []
    for k, s in sp.items():
        if not ok(s[0], s[1], False): probs.append('spawn ' + k)
    for o in j.get('objects', []):
        t = o['type']
        if t in ('spawn', 'mark', 'champion'): continue
        if t == 'exit':
            if not any(ok(o['x'] + a, o['y'] + b, True) for a in range(o.get('w', 1)) for b in range(o.get('h', 1))): probs.append('exit->' + o['to'])
        elif t in ('hidden',) or o.get('hidden'):
            if not ok(o['x'], o['y'], True): probs.append('hidden ' + o.get('id', ''))
        elif t == 'landmark':  # found within 4 cells (world_nav.js)
            if not any(ok(o['x'] + a, o['y'] + b, False) for a in range(-4, 5) for b in range(-4, 5) if abs(a) + abs(b) <= 4): probs.append('landmark ' + o['id'])
        elif not ok(o['x'], o['y'], t in BLOCK or t == 'clue'): probs.append(f"{t} {o.get('id', o.get('name', ''))} @{o['x']},{o['y']}")
        if o.get('to') and t in ('exit', 'door'):
            to = o['to']
            if to in ('world', 'town'): continue  # world map node / old town scene, not map files
            try: tj = load(to)
            except Exception: probs.append(f'{t} {o.get("id","")} -> missing map {to}'); continue
            if (o.get('spawn') or 'default') not in tj.get('spawns', {}): probs.append(f'{t} {o.get("id","")} -> {to} missing spawn {o.get("spawn")}')
    bad += len(probs); out.append(f"{n}: {cnt} cells reached, {len(j.get('objects', []))} objects, {len(sp)} spawns -> " + ('OK' if not probs else 'PROBLEMS ' + '; '.join(probs)))
print('\n'.join(out)); print('TOTAL PROBLEMS', bad); sys.exit(1 if bad else 0)
