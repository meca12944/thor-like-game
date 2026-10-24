#!/usr/bin/env python3
"""지도 설계도(docs_maps/chN/chN_map.json) → 게임 지도 파일 (test128/maps/) 시험판 (팀장, 2026-10-24).
그록 그림이 오기 전이라 땅은 지금 있는 타일(임시)로 채운다: 길=흙, 성벽·절벽·구덩이·거대 구조물=막힘, 물=물, 잿더미 언덕=모래.
  python3 tools/mapplan/build_game.py docs_maps/ch1/ch1_map.json c1n
  → test128/maps/c1n.json (바깥 구역들을 이어 붙인 compose 지도) + c1n_<구역>.json (구역마다)
마물은 아직 정하지 않았으므로 몹은 넣지 않는다 (사장님 10-24). 전망 자리(vista)는 게임 물체로 넣는다.
"""
import json, os, sys, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOLID_KINDS = {'cliff', 'wall', 'citywall', 'oldwall', 'chasm', 'pit', 'building', 'colossus', 'sword', 'aqueduct', 'void'}
WATER_KINDS = {'water', 'blacklake', 'poison', 'mercury'}
SAND_KINDS = {'dune', 'ash'}
STONE_KINDS = {'grave', 'plateau', 'ruin'}   # 잔해는 밟고 지나감
TREE_KINDS = {'petrified'}   # 석화 나무·숲: 가운데 줄기(반지름 4)만 막힘, 나머지는 그늘 바닥
OUTDOOR = ('field', 'town')

def inpoly(x, y, poly):
    c = False; n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1: c = not c
    return c

def seg_d(px, py, a, b):
    ax, ay = a; bx, by = b; dx, dy = bx - ax, by - ay; L = dx * dx + dy * dy or 1
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L)); return math.hypot(px - ax - t * dx, py - ay - t * dy)

def build(src, gid):
    m = json.load(open(src, encoding='utf-8'))
    outdoor = [z for z in m['zones'] if z['kind'] in OUTDOOR]
    ox = min(z['x'] for z in outdoor); oy = min(z['y'] for z in outdoor)
    polys = m.get('areas', []) + m.get('scenery', [])
    out_dir = os.path.join(ROOT, 'test128', 'maps'); parts = []
    for z in outdoor:
        W, H = z['w'], z['h']; rows = []
        for ty in range(H):
            r = []
            for tx in range(W):
                X, Y = z['x'] + tx + .5, z['y'] + ty + .5; ch = '.'
                for a in polys:
                    if not inpoly(X, Y, a['poly']): continue
                    k = a['kind']
                    if k in TREE_KINDS:
                        cx = sum(p[0] for p in a['poly']) / len(a['poly']); cy = sum(p[1] for p in a['poly']) / len(a['poly'])
                        ch = '#' if math.hypot(X - cx, Y - cy) < 4 else (':' if ch == '.' else ch); continue
                    if k in SOLID_KINDS: ch = '#'
                    elif k in WATER_KINDS: ch = '~'
                    elif k in SAND_KINDS and ch == '.': ch = '_'
                    elif k in STONE_KINDS and ch == '.': ch = ':'
                for p in m.get('paths', []):   # 길은 막힘을 뚫는다 (수도교 아치 밑, 문)
                    if p['kind'] in ('road', 'corridor', 'bridge') and any(seg_d(X, Y, p['pts'][i], p['pts'][i + 1]) <= p.get('w', 2) / 2 + .5 for i in range(len(p['pts']) - 1)):
                        ch = '=' if p['kind'] != 'bridge' else ':'
                if tx in (0, W - 1) or ty in (0, H - 1): ch = '#' if ch == '.' else ch   # 구역 둘레 (이웃 구역과 닿는 곳은 아래에서 연다)
                r.append(ch)
            rows.append(r)
        # 이웃 구역과 맞닿은 가장자리는 열기
        for o in outdoor:
            if o is z: continue
            for ty in range(H):
                for tx in (0, W - 1):
                    X, Y = z['x'] + tx + (-1 if tx == 0 else 1), z['y'] + ty
                    if o['x'] <= X < o['x'] + o['w'] and o['y'] <= Y < o['y'] + o['h'] and rows[ty][tx] == '#': rows[ty][tx] = '.'
            for tx in range(W):
                for ty in (0, H - 1):
                    X, Y = z['x'] + tx, z['y'] + ty + (-1 if ty == 0 else 1)
                    if o['x'] <= X < o['x'] + o['w'] and o['y'] <= Y < o['y'] + o['h'] and rows[ty][tx] == '#': rows[ty][tx] = '.'
        objs = []
        for v in m.get('vistas', []):
            if z['x'] <= v['x'] < z['x'] + z['w'] and z['y'] <= v['y'] < z['y'] + z['h']:
                objs.append({'type': 'vista', 'id': f"{gid}_{v['name'][:1]}", 'x': v['x'] - z['x'], 'y': v['y'] - z['y'], 'r': v.get('r', 5), 'zoom': v.get('zoom', .72),
                             'dir': v.get('dir', 270), 'pan': v.get('pan', 40), 'name': v.get('sub', v['name']), 'sub': v.get('show', '')})
        spawns = {}
        for k in m['markers']:
            if k['type'] == 'start' and k.get('zone') == z['id']: spawns['default'] = [k['x'] - z['x'] + .5, k['y'] - z['y'] + .5, 'up']
        if not spawns: spawns['default'] = [W / 2, H / 2, 'down']
        part = {'type': z['kind'], 'id': f"{gid}_{z['id']}", 'name': z['name'], 'title': {'kicker': 'CHAPTER 1 · 시험판', 'name': z['name'], 'sub': z.get('note', '')},
                'tileset': 'field', 'tile': 16, 'w': W, 'h': H, 'grade': 'ash' if z['kind'] == 'field' else None, 'viewZoom': 1.3 if z['kind'] == 'town' else None,
                'bgm': 'town_ruin' if z['kind'] == 'town' else 'field_battle',
                'legend': {'.': 'grass', ',': 'grass_tuft', '=': 'dirt', '~': {'ground': 'water', 'hop': True}, ':': 'stones', '#': 'cliff', '_': 'sand'},
                'solid': ['#', '~'], 'ground': [''.join(r) for r in rows], 'objects': objs, 'spawns': spawns,
                'note': f'GENERATED by tools/mapplan/build_game.py from {os.path.relpath(src, ROOT)} (그록 그림 오기 전 임시 타일)'}
        part = {k: v for k, v in part.items() if v is not None}
        json.dump(part, open(os.path.join(out_dir, part['id'] + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
        parts.append({'map': part['id'], 'x': z['x'] - ox, 'y': z['y'] - oy})
    start = next((p for p, z in zip(parts, outdoor) if any(k['type'] == 'start' and k.get('zone') == z['id'] for k in m['markers'])), parts[0])
    parts.sort(key=lambda p: p is not start)   # 시작 구역을 맨 앞에 (compose 의 default spawn)
    comp = {'id': gid, 'compose': parts, 'region': 'ch1', 'area': 1, 'note': f'새 1장 시험판 (임시 타일). GENERATED by tools/mapplan/build_game.py'}
    json.dump(comp, open(os.path.join(out_dir, gid + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(gid, 'parts', len(parts), [p['map'] for p in parts])

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'c1n')
