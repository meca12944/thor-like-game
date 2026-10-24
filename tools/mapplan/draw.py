#!/usr/bin/env python3
"""챕터 지도 설계도 그리기 (팀 공용, 사장님 10-24 「전체 챕터 지도·아이템·인물 배치」).

  python3 tools/mapplan/draw.py docs_maps/ch1/ch1_map.json      # → 같은 폴더에 ch1_overview.png
  python3 tools/mapplan/draw.py docs_maps/ch1/ch1_map.json --zone felt   # 구역 하나 확대 → ch1_zone_felt.png
  python3 tools/mapplan/draw.py docs_maps/ch1/ch1_map.json --check       # 규칙 검사만

좌표는 전부 「게임 타일」(1타일 = 16px, 주인공 달리기 약 5타일/초). 형식은 docs_maps/README_ko.md.
"""
import json, math, sys, os
from PIL import Image, ImageDraw, ImageFont

FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
def font(sz):
    try: return ImageFont.truetype(FONT, sz)
    except OSError: return ImageFont.load_default()

ZONE_COL = {  # 구역 바닥색
    'town': (92, 84, 70), 'field': (70, 72, 62), 'dungeon': (52, 46, 54), 'boss': (78, 36, 40),
    'interior': (84, 70, 58), 'hidden': (40, 52, 60), 'sky': (60, 20, 28)}
AREA_COL = {  # 지형 덩어리
    'water': (44, 70, 92), 'poison': (60, 92, 48), 'mercury': (130, 140, 150), 'cliff': (30, 28, 28),
    'forest': (44, 62, 40), 'ruin': (96, 92, 86), 'ash': (120, 116, 108), 'fire': (150, 60, 30),
    'web': (150, 40, 50), 'wall': (20, 18, 18), 'pit': (10, 10, 12), 'building': (110, 96, 80),
    'grave': (80, 80, 84), 'gear': (140, 110, 50), 'books': (90, 70, 50), 'void': (90, 20, 34)}
PATH_COL = {'road': (176, 156, 120), 'river': (60, 96, 130), 'wall': (16, 14, 14), 'cliff': (24, 20, 20),
            'bridge': (150, 110, 70), 'corridor': (128, 118, 110), 'sewer': (70, 96, 60), 'rail': (110, 100, 90)}
MARK = {  # type: (색, 모양, 글자)
    'start': ((255, 255, 255), 'star', 'S'), 'save': ((255, 150, 40), 'circle', '화'),
    'npc': ((90, 170, 255), 'circle', ''), 'item': ((255, 210, 60), 'diamond', ''),
    'chest': ((255, 210, 60), 'square', ''), 'mob': ((230, 70, 60), 'tri', ''),
    'elite': ((200, 90, 255), 'tri', '정'), 'hidden_elite': ((200, 90, 255), 'tri', '히'),
    'midboss': ((200, 60, 200), 'star', '중'), 'boss': ((255, 40, 60), 'star', '보'),
    'quest': ((120, 255, 160), 'circle', '!'), 'landmark': ((220, 220, 220), 'square', ''),
    'shortcut': ((80, 230, 120), 'diamond', '⇄'), 'trap': ((255, 90, 160), 'tri', '!'),
    'shop': ((90, 170, 255), 'square', '$')}
LINK_COL = {'gate': (240, 240, 240), 'door': (220, 200, 160), 'stairs': (200, 200, 255), 'lift': (120, 230, 140),
            'shortcut': (80, 230, 120), 'secret': (255, 120, 200), 'oneway': (255, 170, 80)}

def load(p):
    with open(p, encoding='utf-8') as f: return json.load(f)

def check(m):
    """규칙 검사. 반환: 문제 목록."""
    bad = []
    W, H = m['w'], m['h']
    zones = {z['id']: z for z in m['zones']}
    for z in m['zones']:
        if z['x'] < 0 or z['y'] < 0 or z['x'] + z['w'] > W or z['y'] + z['h'] > H:
            bad.append(f"구역 {z['id']} 이 지도 밖으로 나감")
        if z['w'] * z['h'] > 260 * 260 and z.get('kind') != 'sky':
            bad.append(f"구역 {z['id']} {z['w']}x{z['h']} 너무 큼 (한 구역 ≤ 260x260, 나눠서 링크)")
    for k in m.get('markers', []):
        zid = k.get('zone')
        if zid and zid in zones:
            z = zones[zid]
            if not (z['x'] <= k['x'] < z['x'] + z['w'] and z['y'] <= k['y'] < z['y'] + z['h']):
                bad.append(f"표시 {k.get('name')} 가 구역 {zid} 밖 ({k['x']},{k['y']})")
        elif zid:
            bad.append(f"표시 {k.get('name')} 의 구역 {zid} 없음")
        if k['type'] not in MARK: bad.append(f"표시 종류 {k['type']} 모름 ({k.get('name')})")
    for l in m.get('links', []):
        for e in ('from', 'to'):
            if l[e] not in zones and not l[e].startswith('ch'): bad.append(f"링크 {l[e]} 구역 없음")
    # 빠르게 달려 붙는 재미: 몹 무리 사이가 너무 비면 안 됨 (필드 구역만)
    for z in m['zones']:
        if z.get('kind') != 'field': continue
        mobs = [k for k in m.get('markers', []) if k.get('zone') == z['id'] and k['type'] in ('mob', 'elite', 'hidden_elite')]
        need = max(1, (z['w'] * z['h']) // 2500)  # 50x50 타일(달리기 10초)마다 1무리
        if len(mobs) < need: bad.append(f"필드 {z['id']} 몹 무리 {len(mobs)}개 < 권장 {need}개 (50x50마다 1무리)")
    return bad

def draw(m, out, zone=None, maxpx=3000):
    X0, Y0, W, H = 0, 0, m['w'], m['h']
    if zone:
        z = next(z for z in m['zones'] if z['id'] == zone)
        pad = 6; X0, Y0, W, H = z['x'] - pad, z['y'] - pad, z['w'] + pad * 2, z['h'] + pad * 2
    s = max(2, min(24, maxpx // max(W, H)))
    top = 70
    im = Image.new('RGB', (W * s, H * s + top + 150), (14, 12, 14))
    d = ImageDraw.Draw(im)
    P = lambda x, y: ((x - X0) * s, (y - Y0) * s + top)
    f1, f2, f3 = font(max(12, s * 2)), font(max(11, int(s * 1.5))), font(28)
    for z in m['zones']:
        a, b = P(z['x'], z['y']); c, e = P(z['x'] + z['w'], z['y'] + z['h'])
        d.rectangle([a, b, c, e], fill=ZONE_COL.get(z.get('kind'), (70, 70, 70)), outline=(200, 190, 170), width=2)
    for ar in m.get('areas', []):
        pts = [P(x, y) for x, y in ar['poly']]
        d.polygon(pts, fill=AREA_COL.get(ar['kind'], (100, 100, 100)))
    for p in m.get('paths', []):
        pts = [P(x, y) for x, y in p['pts']]
        d.line(pts, fill=PATH_COL.get(p['kind'], (150, 150, 150)), width=max(2, int(p.get('w', 2) * s)), joint='curve')
    # 격자 (10타일마다 얇게, 50타일마다 굵게 + 숫자)
    for gx in range((X0 // 10) * 10, X0 + W + 1, 10):
        a, _ = P(gx, Y0); col = (60, 60, 64) if gx % 50 else (110, 110, 120)
        d.line([(a, top), (a, top + H * s)], fill=col, width=1)
        if gx % 50 == 0: d.text((a + 2, top - 18), str(gx), fill=(170, 170, 180), font=font(14))
    for gy in range((Y0 // 10) * 10, Y0 + H + 1, 10):
        _, b = P(X0, gy); col = (60, 60, 64) if gy % 50 else (110, 110, 120)
        d.line([(0, b), (W * s, b)], fill=col, width=1)
        if gy % 50 == 0: d.text((2, b + 2), str(gy), fill=(170, 170, 180), font=font(14))
    for z in m['zones']:
        a, b = P(z['x'], z['y'])
        t = f"{z['name']}  {z['w']}x{z['h']}"
        d.text((a + 6, b + 4), t, fill=(255, 245, 220), font=f1, stroke_width=3, stroke_fill=(0, 0, 0))
    for l in m.get('links', []):
        x, y = P(*l['at']); r = max(5, s)
        d.rectangle([x - r, y - r, x + r, y + r], outline=LINK_COL.get(l['kind'], (255, 255, 255)), width=3)
        if l.get('label'): d.text((x + r + 3, y - r), l['label'], fill=LINK_COL.get(l['kind'], (255, 255, 255)), font=f2, stroke_width=2, stroke_fill=(0, 0, 0))
    for i, k in enumerate(m.get('markers', []), 1):
        col, shp, ch = MARK.get(k['type'], ((255, 255, 255), 'circle', '?'))
        x, y = P(k['x'], k['y']); r = max(6, int(s * 1.4)) * (2 if k['type'] in ('boss', 'midboss') else 1)
        if shp == 'circle': d.ellipse([x - r, y - r, x + r, y + r], fill=col, outline=(0, 0, 0), width=2)
        elif shp == 'square': d.rectangle([x - r, y - r, x + r, y + r], fill=col, outline=(0, 0, 0), width=2)
        elif shp == 'diamond': d.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=col, outline=(0, 0, 0))
        elif shp == 'tri': d.polygon([(x, y - r), (x + r, y + r), (x - r, y + r)], fill=col, outline=(0, 0, 0))
        else:
            pts = [(x + r * math.cos(-math.pi / 2 + j * math.pi / 5) * (1 if j % 2 == 0 else .45),
                    y + r * math.sin(-math.pi / 2 + j * math.pi / 5) * (1 if j % 2 == 0 else .45)) for j in range(10)]
            d.polygon(pts, fill=col, outline=(0, 0, 0))
        if ch: d.text((x - r * .45, y - r * .7), ch, fill=(0, 0, 0), font=font(max(10, r)))
        k['_n'] = i
        d.text((x + r + 2, y - r), f"{i}.{k['name']}", fill=col, font=f2, stroke_width=2, stroke_fill=(0, 0, 0))
    d.text((10, 10), f"{m['chapter']} {m['title']}   전체 {m['w']}x{m['h']} 타일 (1타일=16px, 달리기 약 5타일/초 → 가로 {m['w'] / 5:.0f}초)",
           fill=(255, 230, 200), font=f3)
    # 범례
    lx, ly = 10, top + H * s + 10
    for t, (col, shp, ch) in MARK.items():
        d.rectangle([lx, ly, lx + 14, ly + 14], fill=col); d.text((lx + 18, ly - 2), t, fill=(220, 220, 220), font=font(14))
        lx += 130
        if lx > W * s - 140: lx, ly = 10, ly + 22
    im.save(out)
    return out

if __name__ == '__main__':
    a = sys.argv[1:]
    p = a[0]; m = load(p)
    bad = check(m)
    for b in bad: print('⚠', b)
    if '--check' in a: sys.exit(1 if bad else 0)
    base = os.path.join(os.path.dirname(p), m['chapter'])
    if '--zone' in a:
        zid = a[a.index('--zone') + 1]
        print(draw(m, f"{base}_zone_{zid}.png", zone=zid))
    else:
        print(draw(m, f"{base}_overview.png"))
