"""PixelLab 배경으로 1~8장 임시 구역 만들기 (사장님 11-12 「전부 게임에 올려」).
Reads maps_v2/pixellab/chN/index.json (tools/pixellab/import_assets.py) and writes, for test128:
  test128/maps/px_hub.json                      시험장 입구 (?go=px_hub): 1~8장 첫 구역으로 가는 문
  test128/maps/px_chN_<zone>.json               구역 하나 = 맵 하나. 바닥 = PixelLab 바닥 타일(wang 모서리), 소품 = hd props, 서쪽/동쪽 출구로 이어짐
  test128/maps/px_chN_int_<room>.json           PixelLab 방 그림 = 실내 (bg)
  test128/assets/world/px/<map>/ground.webp     바닥 그림 (D=2: PixelLab 32px = 1칸)
Outdoor zones keep the hand-drawn castle far view (hd.backdrop, same as prologue_grave). Mobs are ch1 placeholders.
python3 tools/pixellab/build_px_zones.py"""
import json, os, random, math, shutil
from PIL import Image
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PX = os.path.join(ROOT, 'maps_v2', 'pixellab'); T128 = os.path.join(ROOT, 'test128'); MAPS = os.path.join(T128, 'maps'); GR = os.path.join(T128, 'assets', 'world', 'px')
REL = '../maps_v2/pixellab/'  # asset url from test128/
TS = 32; D = 2; SKY = 10
EXIST = {1: {'field_c', 'field_e', 'field_s', 'felt', 'ws_1f', 'ws_boss'}}  # ch1 zones that already have real maps: their items show in the first placeholder
OUTDOOR = {(2, 'gate'), (2, 'forge'), (4, 'grave')}
MOBS = ['c1_silmamul', 'c1_unrotting_hound', 'c1_shear_tailor', 'c1_spool_spider', 'c1_thread_puppet', 'c1_thread_scarecrow', 'c1_quilted_boar']
CH_NAME = {1: '1장 · 잿빛 들판', 2: '2장 · 철혈의 가도', 3: '3장 · 침묵의 대서고', 4: '4장 · 잿더미 연회장', 5: '5장 · 대성당', 6: '6장 · 연금술 심장부', 7: '7장 · 왕성', 8: '8장 · 공허의 틈새'}
proto = json.load(open(os.path.join(MAPS, 'prologue_grave.json')))
BACKDROP = proto['hd']['backdrop']
for d in (GR,): shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
for f in os.listdir(MAPS):
    if f.startswith('px_'): os.remove(os.path.join(MAPS, f))

def load_ts(e):
    d = os.path.join(PX, e['file']); meta = json.load(open(os.path.join(d, 'tiles.json')))
    by = {}
    for m in meta:
        c = m['corners']; key = tuple(1 if c[k] == 'upper' else 0 for k in ('NW', 'NE', 'SW', 'SE'))
        by.setdefault(key, Image.open(os.path.join(d, m['f'])).convert('RGBA'))
    return by
_FM = None
def feather(im):
    global _FM
    if _FM is None:
        _FM = Image.new('L', (TS, TS)); px = _FM.load()
        for y in range(TS):
            for x in range(TS):
                r = math.hypot(x + .5 - TS / 2, y + .5 - TS / 2) / (TS / 2); px[x, y] = int(255 * max(0, min(1, (1 - r) / .45)))
    o = im.copy(); a = o.getchannel('A'); from PIL import ImageChops; o.putalpha(ImageChops.multiply(a, _FM)); return o
def noise(w, h, rnd, cell=5):
    gw, gh = w // cell + 3, h // cell + 3; g = [[rnd.random() for _ in range(gw)] for _ in range(gh)]
    def at(x, y):
        fx, fy = x / cell, y / cell; ix, iy = int(fx), int(fy); tx, ty = fx - ix, fy - iy
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        a = g[iy][ix] * (1 - tx) + g[iy][ix + 1] * tx; b = g[iy + 1][ix] * (1 - tx) + g[iy + 1][ix + 1] * tx
        return a * (1 - ty) + b * ty
    return [[at(x, y) for x in range(w)] for y in range(h)]
def ground_image(w, h, bands, rnd, top, decals, dark):
    """bands = [(x0, x1, tileset dict)] in tiles; rows < top = sky / wall strip"""
    img = Image.new('RGBA', (w * TS, h * TS), (36, 32, 30, 255)); N = noise(w + 1, h + 1, rnd)
    flat = sorted(v for row in N for v in row); thr = flat[int(len(flat) * .25)]  # ~75 % 'upper' (the described floor)
    C = [[1 if N[y][x] > thr else 0 for x in range(w + 1)] for y in range(h + 1)]
    for x0, x1, by in bands:
        for y in range(top, h):
            for x in range(x0, x1):
                k = (C[y][x], C[y][x + 1], C[y + 1][x], C[y + 1][x + 1]); t = by.get(k) or by.get((1, 1, 1, 1)) or next(iter(by.values()))
                img.paste(t, (x * TS, y * TS))
    for (dx, dy, dimg) in decals:  # feathered: the decal's own floor fades into ours
        if all(C[yy][xx] for yy in (dy, dy + 1) for xx in (dx, dx + 1)): img.alpha_composite(feather(dimg), (dx * TS, dy * TS))
    if dark:  # dungeon: outer 2-tile ring = dark wall / void
        ov = Image.new('RGBA', img.size, (0, 0, 0, 0)); px = ov.load()
        from PIL import ImageDraw
        dr = ImageDraw.Draw(ov); a = (14, 10, 9, 215)
        dr.rectangle([0, 0, w * TS, top * TS + 2 * TS], fill=a); dr.rectangle([0, (h - 2) * TS, w * TS, h * TS], fill=a)
        dr.rectangle([0, 0, 2 * TS, h * TS], fill=a); dr.rectangle([(w - 2) * TS, 0, w * TS, h * TS], fill=a)
        img.alpha_composite(ov)
    return img.convert('RGB')

IDX = {c: json.load(open(os.path.join(PX, f'ch{c}', 'index.json'))) for c in range(1, 9)}
chap_first = {}; all_maps = []
for c in range(1, 9):
    I = IDX[c]; zinfo = {z['id']: z for z in I['zones']}; items = I['items']
    zones = [z['id'] for z in I['zones'] if any(e['zone'] == z['id'] for e in items) and z['id'] not in EXIST.get(c, ())]
    fold = {z: zones[0] for z in EXIST.get(c, ())}
    def zitems(z, types): return [e for e in items if (fold.get(e['zone'], e['zone']) == z) and e['type'] in types]
    floors_ch = [e for e in items if e['type'] == 'tileset' and e['tile'] == 32 and not e['transition']]
    floors_ch.sort(key=lambda e: e['verdict'] != 'ok')
    decal_ch = [e for e in items if e['type'] == 'decal']
    ids = [f'px_ch{c}_{z}' for z in zones]; chap_first[c] = ids[0]
    for zi, z in enumerate(zones):
        mid = ids[zi]; rnd = random.Random(mid); kind = zinfo[z].get('kind'); out = kind in ('field', 'sky') or (c, z) in OUTDOOR or c == 8
        props = zitems(z, ('prop', 'building')); rooms = zitems(z, ('room',))
        fl = [e for e in zitems(z, ('tileset',)) if e['tile'] == 32 and not e['transition']]
        seen = set(); fl2 = []
        for e in sorted(fl, key=lambda e: e['verdict'] != 'ok'):
            if e['slot'] in seen: continue
            seen.add(e['slot']); fl2.append(e)
        fl2 = fl2[:4] or floors_ch[:1]
        W = max(56, min(112, 40 + int(len(props) * 2.2)), 26 * len(fl2)); top = SKY if out else 0; H = top + 40
        bands = []; bw = W // len(fl2)
        for bi, e in enumerate(fl2): bands.append((bi * bw, W if bi == len(fl2) - 1 else (bi + 1) * bw, load_ts(e)))
        midy = top + 20
        # decals baked into the floor
        dz = zitems(z, ('decal',)) or decal_ch[:1]; decals = []
        dimgs = [Image.open(os.path.join(PX, d['file'], f)).convert('RGBA') for d in dz for f in sorted(os.listdir(os.path.join(PX, d['file']))) if f.endswith('.png')]
        if dimgs:
            for _ in range(max(5, W * 40 // 160)):
                x, y = rnd.randrange(3, W - 3), rnd.randrange(top + 3, H - 3)
                if abs(y - midy) > 2: decals.append((x, y, rnd.choice(dimgs)))
        img = ground_image(W, H, bands, rnd, top, decals, not out)
        os.makedirs(os.path.join(GR, mid)); gpath = os.path.join(GR, mid, 'ground.webp'); img.save(gpath, 'WEBP', quality=90, method=6)
        rows = [['.'] * W for _ in range(H)]
        for y in range(H):
            for x in range(W):
                if y < top + (0 if out else 2) or y >= H - 2 or x < (0 if out else 2) or x >= W - (0 if out else 2): rows[y][x] = '#'
                if out and (y >= H - 1 or (y < top)): rows[y][x] = '#'
        for y in range(midy - 2, midy + 3):  # west / east gates
            for x in range(0, 3): rows[y][x] = '.'
            for x in range(W - 3, W): rows[y][x] = '.'
        # props: no overlap, corridor (midy +-2) kept free of solids
        occ = []; hdprops = []; placed = []
        def free(r):
            return all(r[2] <= o[0] or r[0] >= o[2] or r[3] <= o[1] or r[1] >= o[3] for o in occ)
        props.sort(key=lambda e: -(e['bbox'][2] - e['bbox'][0]) * (e['bbox'][3] - e['bbox'][1]))
        for e in props:
            bx0, by0, bx1, by1 = e['bbox']; wt, ht = (bx1 - bx0) / TS, (by1 - by0) / TS
            for _ in range(400):
                fx = rnd.uniform(3 + wt / 2, W - 3 - wt / 2); fy = rnd.uniform(top + 3 + min(ht, 6), H - 3)
                r = (fx - wt / 2 - .4, fy - ht - .2, fx + wt / 2 + .4, fy + .6)
                if fy > midy - 3.5 and fy - min(ht, 3) < midy + 3: continue
                if free(r): break
            else: continue
            occ.append(r); q = dict(id=e['id'], img=REL + e['file'], x=round(fx, 2), y=round(fy, 2), ax=(bx0 + bx1) // 2, ay=by1, D=D, shadow=1)
            if e['type'] == 'building' or ht >= 1.5:
                fh = max(1, min(4, round(ht * (.45 if e['type'] == 'building' else .3)))); fw = max(1, wt * .7)
                q['solid'] = [int(fx - fw / 2), int(fy - fh), int(fx + fw / 2 - .01), int(fy - .01)]
            if rnd.random() < .5 and e['type'] != 'building' and 'flag' not in e: q['flip'] = True
            hdprops.append(q); placed.append(e['id'])
        objs = []; spawns = {'default': [3.5, midy + .5, 'right'], 'west': [3.5, midy + .5, 'right'], 'east': [W - 3.5, midy + .5, 'left']}
        prev_ = ids[zi - 1] if zi else 'px_hub'; nxt = ids[zi + 1] if zi + 1 < len(ids) else (chap_first.get(c + 1) or f'px_ch{c + 1}_' if c < 8 else 'px_hub')
        objs.append(dict(type='exit', x=0, y=midy - 2, w=1, h=5, to=prev_, spawn='east' if zi else f'ch{c}', label='← ' + (zinfo[zones[zi - 1]]['name'] if zi else '시험장 입구')))
        objs.append(dict(type='exit', x=W - 1, y=midy - 2, w=1, h=5, to=nxt, spawn='west' if (zi + 1 < len(ids) or c < 8) else f'ch{c}', label='→ ' + (zinfo[zones[zi + 1]]['name'] if zi + 1 < len(ids) else (CH_NAME[c + 1] if c < 8 else '시험장 입구'))))
        objs.append(dict(type='sign', x=5, y=midy - 2, text=f'{CH_NAME[c]} — {zinfo[z]["name"]}\nPixelLab 배경 임시 구역 (사장님 11-12). 바닥·소품은 PixelLab, 하늘·먼 성은 손그림.'))
        for ri, r in enumerate(rooms):
            rx = 8 + ri * 6
            for _ in range(200):
                if all(rows[midy + 3][x] == '.' for x in range(rx, rx + 2)): break
                rx = rnd.randrange(6, W - 8)
            rid = f'px_ch{c}_int_{r["id"]}'; objs.append(dict(type='exit', x=rx, y=midy + 3, w=2, h=1, to=rid, spawn='door', label='▼ ' + (r['item'] or r['id'])))
            spawns['room_' + r['id']] = [rx + 1, midy + 2.5, 'down']
            build_room = (r, rid, mid, 'room_' + r['id'], c)
            all_maps.append(('room', build_room))
        if kind not in ('town',):
            for k in range(4 + W // 30):
                for _ in range(200):
                    x, y = rnd.randrange(4, W - 4), rnd.randrange(top + 3, H - 3)
                    if x > 14 and rows[y][x] == '.' and all(not (o[0] - 1 <= x <= o[2] + 1 and o[1] <= y <= o[3] + 1) for o in occ): break
                objs.append(dict(type='spawn', mob=rnd.choice(MOBS[:5] if c > 1 else MOBS), x=x, y=y, respawn=40))
        hd = dict(D=D, ground=f'assets/world/px/{mid}/ground.webp', decoArt={}, lights=[], props=hdprops)
        if out: hd['backdrop'] = dict(BACKDROP, x=W // 2, clipY=top + 2.7)
        m = dict(id=mid, type='field' if kind != 'town' else 'town', area=c, region=f'px_ch{c}', name=zinfo[z]['name'],
                 title=dict(kicker=f'{CH_NAME[c]} · PixelLab 시험', name=zinfo[z]['name'], sub='임시 구역 — PixelLab 바닥·소품 + 손그림 하늘'),
                 bgm='field', battleBgm='field_battle', tileset='field', tile=16, w=W, h=H, legend={'.': 'dirt', '#': 'cliff'}, solid=['#'],
                 fog=.18 if out else .08, ash=40 if out else 0, wind=[3, 1], objects=objs, spawns=spawns, hd=hd, ground=[''.join(r) for r in rows],
                 note=f'PixelLab 임시 구역 (tools/pixellab/build_px_zones.py, 11-12). 소품 {len(placed)}개, 바닥 {", ".join(e["id"] for e in fl2)}. 몹은 1장 몹 임시.')
        if out: m['skyTop'] = top
        json.dump(m, open(os.path.join(MAPS, mid + '.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
        all_maps.append(('zone', dict(id=mid, ch=c, zone=z, w=W, h=H, props=len(placed), props_total=len(props), floors=[e['id'] for e in fl2], rooms=[r['id'] for r in rooms], outdoor=out)))
# fix chapter-to-chapter links now that first ids are known
for f in os.listdir(MAPS):
    if not f.startswith('px_ch'): continue
    p = os.path.join(MAPS, f); m = json.load(open(p)); ch = None
    for o in m['objects']:
        if o['type'] == 'exit' and o['to'].endswith('_') and o['to'].startswith('px_ch'): o['to'] = chap_first[int(o['to'][5])]
    json.dump(m, open(p, 'w'), ensure_ascii=False, separators=(',', ':'))
# rooms
def room_map(r, rid, back, back_spawn, c):
    src = os.path.join(PX, r['file'], 'room.png'); im = Image.open(src).convert('RGB'); W, H = im.size[0] // 16, im.size[1] // 16
    void = [[sum(im.crop((x * 16, y * 16, x * 16 + 16, y * 16 + 16)).resize((1, 1), Image.BOX).getpixel((0, 0))) < 40 for x in range(W)] for y in range(H)]
    sol = [[void[y][x] for x in range(W)] for y in range(H)]
    for x in range(W):
        ys = [y for y in range(H) if not void[y][x]]
        if not ys: continue
        for y in range(ys[0], min(ys[0] + 4, H)): sol[y][x] = True
        sol[ys[-1]][x] = True
    for y in range(H):
        xs = [x for x in range(W) if not void[y][x]]
        if xs: sol[y][xs[0]] = sol[y][xs[-1]] = True
    walk = [(x, y) for y in range(H) for x in range(W) if not sol[y][x]]
    by = max(y for x, y in walk); cx = W / 2; bx = min((x for x, y in walk if y == by), key=lambda x: abs(x + .5 - cx))
    ey = by + 1 if by + 1 < H else by
    sol[ey][bx] = False
    if bx + 1 < W: sol[ey][bx + 1] = False
    rows = [''.join('#' if sol[y][x] else '.' for x in range(W)) for y in range(H)]
    m = dict(id=rid, type='town', area=c, region=f'px_ch{c}', name=r['item'] or r['id'], title=dict(kicker=f'{CH_NAME[c]} · PixelLab 방', name=r['item'] or r['id'], sub='PixelLab 방 그림'),
             bgm='town', tileset='field', tile=16, w=W, h=H, bg=REL + r['file'] + '/room.png', artPx=list(im.size), legend={'.': 'dirt', '#': {'ground': 'dirt', 'solid': True}}, solid=['#'],
             spawns={'default': [bx + 1, by + .5, 'up'], 'door': [bx + 1, by + .5, 'up']}, objects=[dict(type='exit', x=bx, y=ey, w=2, h=1, to=back, spawn=back_spawn, label='↓ 밖으로')],
             ground=rows, note=f'PixelLab 방 {r["id"]} ({r["verdict"]}). 벽 칸은 그림 밝기로 자동 계산.')
    json.dump(m, open(os.path.join(MAPS, rid + '.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
for kind, v in all_maps:
    if kind == 'room': room_map(*v)
# hub
zones = [v for k, v in all_maps if k == 'zone']
W, H, top = 60, 34, SKY; rows = [['#' if (y < top or y >= H - 1 or x == 0 or x == W - 1) else '.' for x in range(W)] for y in range(H)]
rnd = random.Random('hub'); by = load_ts(next(e for e in IDX[1]['items'] if e['type'] == 'tileset' and e['tile'] == 32 and not e['transition'] and e['verdict'] == 'ok'))
img = ground_image(W, H, [(0, W, by)], rnd, top, [], False); os.makedirs(os.path.join(GR, 'px_hub')); img.save(os.path.join(GR, 'px_hub', 'ground.webp'), 'WEBP', quality=90, method=6)
objs = []; spawns = {'default': [W / 2, H - 4.5, 'up']}
for c in range(1, 9):
    x = 4 + (c - 1) * 7; y = top + 4
    objs.append(dict(type='exit', x=x, y=y, w=3, h=2, to=chap_first[c], spawn='west', label=f'▲ {CH_NAME[c]}'))
    objs.append(dict(type='sign', x=x + 1, y=y + 3, text=f'{CH_NAME[c]} — PixelLab 임시 구역 {sum(1 for z in zones if z["ch"] == c)}곳'))
    spawns[f'ch{c}'] = [x + 1.5, y + 3.5, 'down']
objs.append(dict(type='exit', x=W // 2 - 2, y=H - 2, w=4, h=1, to='felt', spawn='default', label='↓ 펠트 마을로'))
objs.append(dict(type='sign', x=W // 2, y=H - 6, text='PixelLab 배경 시험장 (사장님 11-12 「전부 게임에 올려」).\n위의 문으로 1~8장 임시 구역에 간다. 구역 끝 동쪽 출구 = 다음 구역.'))
hd = dict(D=D, ground='assets/world/px/px_hub/ground.webp', decoArt={}, lights=[], props=[], backdrop=dict(BACKDROP, x=W // 2, clipY=top + 2.7))
m = dict(id='px_hub', type='town', area=1, region='px', name='PixelLab 시험장', title=dict(kicker='PixelLab 시험', name='배경 시험장', sub='1~8장 임시 구역 입구'), bgm='field', tileset='field', tile=16,
         w=W, h=H, skyTop=top, legend={'.': 'dirt', '#': 'cliff'}, solid=['#'], fog=.15, ash=30, wind=[3, 1], objects=objs, spawns=spawns, hd=hd, ground=[''.join(r) for r in rows], note='tools/pixellab/build_px_zones.py')
json.dump(m, open(os.path.join(MAPS, 'px_hub.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
json.dump(dict(hub='px_hub', zones=zones, rooms=[v[1] for k, v in all_maps if k == 'room']), open(os.path.join(PX, 'px_zones.json'), 'w'), ensure_ascii=False, indent=1)
print(len(zones), 'zones', sum(1 for k, v in all_maps if k == 'room'), 'rooms', sum(z['props'] for z in zones), 'props placed of', sum(z['props_total'] for z in zones))
for z in zones: print(z['id'], z['w'], z['h'], z['props'], '/', z['props_total'], z['floors'], z['rooms'])
