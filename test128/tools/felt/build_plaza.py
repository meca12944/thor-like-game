"""Felt plaza vignette: test128/maps/felt_plaza.json + assets/world/felt_plaza_bg.png (one screen and a bit, 28x17 tiles).
python3 tools/felt/build_plaza.py [overlay.png]
Parts: tools/felt/parts_plaza/ (PixelLab map-objects + a pro Wang tileset, see handoff/claude/felt_pixellab/).
Look: organic cobble/earth ground, dense props placed by hand, drop shadows, a dusk grade, lantern glow and a vignette.
Every opaque tile of a solid part is collision; decals, crows and the lantern string are walk-over."""
import sys, os, json, base64, io, random, math
from PIL import Image, ImageDraw, ImageFilter, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..'); P = os.path.join(HERE, 'parts_plaza')
OV = sys.argv[1] if len(sys.argv) > 1 else None
W, H, T = 28, 17, 16; PW, PH = W * T, H * T
rnd = random.Random(5)

# ---- placement: part, x (centre px), y (base px = where it touches the ground), solid, shadow ----
PARTS = [
 ('pz_house_a', 80, 104, 1, 1), ('pz_house_b', 226, 100, 1, 1), ('pz_house_c', 372, 104, 1, 1),
 ('pz_board', 150, 118, 1, 1), ('pz_planter', 300, 112, 1, 1), ('pz_lamp', 18, 122, 1, 1), ('pz_lamp', 430, 122, 1, 1),
 ('pz_fountain', 224, 192, 1, 1),
 ('pz_stall_a', 62, 182, 1, 1), ('pz_pots', 110, 186, 1, 1), ('pz_crates', 398, 196, 1, 1), ('pz_stall_b', 388, 168, 1, 1),
 ('pz_bench', 150, 214, 1, 1), ('pz_well', 312, 236, 1, 1),
 ('pz_tent', 66, 262, 1, 1), ('pz_brazier', 120, 254, 1, 1), ('pz_cart', 150, 268, 1, 1),
 ('pz_statue', 392, 262, 1, 1), ('pz_rubble', 330, 270, 1, 1), ('pz_webs', 440, 270, 1, 0),
 ('pz_deadtree', 8, 214, 1, 1), ('pz_crows', 270, 222, 0, 0), ('pz_crows', 180, 140, 0, 0),
]
LANTERN_STRINGS = [(110, 124), (338, 124)]   # (centre x, y) of the hanging lantern rope (drawn on top, walk-over)
GLOWS = [(18, 74, 46), (430, 74, 46), (120, 236, 40), (66, 248, 34), (80, 70, 26), (372, 72, 26)]  # (x, y, radius) warm light
EXIT = (12, 15)   # south exit tiles x0..x1 on the bottom row
NPCS = [
 ('f_luca',    18, 11, '루카',   '시인',      'a_bard',      '「불탄 왕도에 실이 내리고……」 아, 또 이런 가사가 나오네. 요즘은 밝은 노래가 안 써져.'),
 ('f_toby',    10, 12, '토비',   '아이',      'a_kid',       '펠릭스가 공방 쪽으로 공 주우러 갔는데 안 돌아와요…… 아저씨, 혹시 못 봤어요?'),
 ('f_ben',     21, 12, '벤',     '떠돌이 상인','f_merchant', '이 장부, 분명 30년 전 거라는데 글씨가 하나도 안 바랬어. 이상하지 않아?'),
 ('f_linette', 25,  7, '리네트', '재봉사',    'a_tailor',    '여긴 왕실 의상실이 있던 자리예요. 언젠가 여기서 영웅의 망토를 만들 거예요!'),
]

def load_tiles(name):
    t = json.load(open(os.path.join(P, name)))['tileset']['tiles']; out = {}
    for tl in t:
        c = tl['corners']; key = tuple(c[k] == 'upper' for k in ('NW', 'NE', 'SW', 'SE'))
        out.setdefault(key, []).append(Image.open(io.BytesIO(base64.b64decode(tl['image']['base64']))).convert('RGBA'))
    return out

def part(name):
    im = Image.open(os.path.join(P, name + '.png')).convert('RGBA'); bb = im.getbbox(); return im.crop(bb) if bb else im

def ground():
    # cobble (upper) = a wobbly ellipse around the fountain + the lane to the houses; earth at the edges and in a few worn patches
    g = [[0] * (W + 1) for _ in range(H + 1)]
    for y in range(H + 1):
        for x in range(W + 1):
            dx, dy = (x - 14) / 12.5, (y - 10.5) / 7.2
            wob = .12 * math.sin(x * 1.3 + y * .7) + .1 * math.cos(y * 1.9 - x * .4)
            g[y][x] = 1 if dx * dx + dy * dy < 1 + wob else 0
    for (x, y) in [(5, 14), (6, 14), (22, 4), (23, 13), (24, 13), (9, 8)]:   # worn earth patches
        if 0 <= y <= H and 0 <= x <= W: g[y][x] = 0
    for y in range(13, H + 1):   # earth road leaving south
        for x in range(EXIT[0], EXIT[1] + 2): g[y][x] = 0
    TL = load_tiles('tiles_cobble_pro.json'); bg = Image.new('RGBA', (PW, PH))
    for y in range(H):
        for x in range(W):
            key = (g[y][x] == 1, g[y][x + 1] == 1, g[y + 1][x] == 1, g[y + 1][x + 1] == 1)
            bg.paste(rnd.choice(TL[key]), (x * T, y * T))
    return bg, g

def shadow(im, k=.55, dx=4, dy=3):
    a = im.split()[3].point(lambda v: int(v * k)); sh = Image.new('RGBA', im.size, (12, 8, 14, 0)); sh.putalpha(a)
    pad = Image.new('RGBA', (im.width + 12, im.height + 12)); pad.alpha_composite(sh, (dx + 2, dy + 2))
    return pad.filter(ImageFilter.GaussianBlur(2))

def main():
    bg, g = ground()
    # decals scattered on the ground (seeded), never under the fountain centre
    for i in range(26):
        n = rnd.choice(['dc_puddle', 'dc_cracks', 'dc_ash', 'dc_moss', 'dc_leaves', 'dc_cracks', 'dc_leaves'])
        im = part(n); x, y = rnd.randrange(8, PW - 40), rnd.randrange(96, PH - 20)
        if abs(x - 224) < 70 and abs(y - 170) < 50: continue
        if rnd.random() < .5: im = im.transpose(Image.FLIP_LEFT_RIGHT)
        bg.alpha_composite(im, (x, y))
    solid = [[False] * W for _ in range(H)]
    for x in range(W): solid[0][x] = solid[H - 1][x] = True
    for y in range(H): solid[y][0] = solid[y][W - 1] = True
    for x in range(EXIT[0], EXIT[1] + 1): solid[H - 1][x] = False
    placed = []
    for name, cx, by, sol, sh in sorted(PARTS, key=lambda p: p[2]):   # back to front
        im = part(name)
        if name == 'pz_crows' and cx < 200: im = im.transpose(Image.FLIP_LEFT_RIGHT)
        px, py = int(cx - im.width / 2), int(by - im.height)
        if sh: s = shadow(im); bg.alpha_composite(s, (px - 2, py - 2))
        bg.alpha_composite(im, (px, py)); placed.append((name, px, py, im, sol))
    for cx, y in LANTERN_STRINGS:
        im = part('pz_lanterns'); bg.alpha_composite(im, (int(cx - im.width / 2), int(y - im.height)))
    # collision from part alpha (the lower 80 % of a building; the very top of roofs is still walk-behind-free since bg is flat)
    for name, px, py, im, sol in placed:
        if not sol: continue
        a = im.split()[3]
        for ty in range(max(0, py // T), min(H, (py + im.height - 1) // T + 1)):
            for tx in range(max(0, px // T), min(W, (px + im.width - 1) // T + 1)):
                box = (tx * T - px, ty * T - py, tx * T - px + T, ty * T - py + T)
                cov = sum(1 for v in a.crop(box).tobytes() if v > 128) / (T * T)
                if cov > .3: solid[ty][tx] = True
    # ---- light: dusk grade (warm top-left -> cool dark bottom-right), lantern glow, vignette ----
    rgb = bg.convert('RGB')
    grad = Image.new('RGB', (PW, PH)); gp = grad.load()
    for y in range(PH):
        for x in range(PW):
            t = (x / PW * .55 + y / PH * .45)
            gp[x, y] = (int(255 - 70 * t), int(236 - 80 * t), int(214 - 70 * t))
    rgb = ImageChops.multiply(rgb, grad)
    glow = Image.new('RGB', (PW, PH)); gd = ImageDraw.Draw(glow)
    for x, y, r in GLOWS:
        for k in range(r, 0, -2):
            v = int(70 * (1 - k / r) ** 1.6); gd.ellipse([x - k, y - k * .8, x + k, y + k * .8], fill=(v, int(v * .62), int(v * .25)))
    rgb = ImageChops.add(rgb, glow.filter(ImageFilter.GaussianBlur(6)))
    vig = Image.new('L', (PW, PH)); vp = vig.load()
    for y in range(PH):
        for x in range(PW):
            d = ((x - PW / 2) / (PW / 2)) ** 2 + ((y - PH / 2) / (PH / 2)) ** 2
            vp[x, y] = int(255 * max(.55, 1 - .38 * d))
    rgb = ImageChops.multiply(rgb, Image.merge('RGB', (vig, vig, vig)))
    rgb.save(os.path.join(ROOT, 'assets', 'world', 'felt_plaza_bg.png'), optimize=True)
    objs = [{'type': 'exit', 'x': EXIT[0], 'y': H - 1, 'w': EXIT[1] - EXIT[0] + 1, 'h': 1, 'to': 'felt', 'spawn': 'default', 'label': '↓ 펠트 남쪽 길'},
            {'type': 'door', 'id': 'pz_door_inn', 'x': 5, 'y': 5, 'name': '마르타의 여관', 'heal': 1, 'text': '마르타의 여관 — 하룻밤 쉬었다. 체력이 모두 회복됐다.'},
            {'type': 'door', 'id': 'pz_door_house', 'x': 14, 'y': 5, 'name': '이장 바르트의 집', 'text': '이장 바르트의 집 — 실내는 준비 중이다. (placeholder)'},
            {'type': 'door', 'id': 'pz_door_atelier', 'x': 23, 'y': 5, 'name': '리네트의 공방', 'text': '리네트의 공방 — 실내는 준비 중이다. (placeholder)'},
            {'type': 'sign', 'x': 9, 'y': 7, 'text': '게시판\n찢긴 공고문이 겹겹이 붙어 있다. 「실종 — 펠릭스, 열 살. 공방 근처에서……」 뒤는 찢겨 나갔다.'}]
    for i, x, y, name, role, art, idle in NPCS:
        objs.append({'type': 'npc', 'id': i, 'x': x, 'y': y, 'name': name, 'role': role, 'main': 1 if i == 'f_linette' else 0, 'idle': idle, 'art': art})
    for o in objs:
        if o['type'] == 'door': solid[o['y']][o['x']] = True
    rows = [''.join('#' if solid[y][x] else '.' for x in range(W)) for y in range(H)]
    for o in objs:
        if o['type'] in ('npc', 'sign') and rows[o['y']][o['x']] == '#': print('WARN', o['type'], o.get('id'), 'on a solid tile', o['x'], o['y'])
    j = {'id': 'felt_plaza', 'type': 'town', 'area': 1, 'region': 'felt', 'name': '펠트 광장',
         'title': {'kicker': 'CHAPTER 1', 'name': '펠트 광장', 'sub': '금 간 분수와 왕의 석상'},
         'bgm': 'town_ruin', 'battleBgm': 'field_battle', 'tileset': 'field', 'tile': T, 'w': W, 'h': H,
         'bg': 'assets/world/felt_plaza_bg.png',
         'note': 'generated by tools/felt/build_plaza.py from PixelLab parts (tools/felt/parts_plaza) — do not hand-edit.',
         'legend': {'.': 'dirt', '#': {'ground': 'dirt', 'solid': True}}, 'solid': ['#'],
         'spawns': {'default': [13.5, 15.2, 'up']}, 'objects': objs, 'ground': rows}
    json.dump(j, open(os.path.join(ROOT, 'maps', 'felt_plaza.json'), 'w'), ensure_ascii=False, indent=1)
    if OV:
        ov = rgb.convert('RGBA'); lay = Image.new('RGBA', ov.size); d = ImageDraw.Draw(lay)
        for y, r in enumerate(rows):
            for x, c in enumerate(r):
                if c == '#': d.rectangle([x * T, y * T, x * T + T - 1, y * T + T - 1], fill=(255, 0, 0, 70))
        for o in objs:
            col = {'npc': (60, 160, 255, 230), 'door': (255, 220, 0, 230), 'exit': (0, 255, 120, 200), 'sign': (255, 255, 255, 230)}[o['type']]
            d.rectangle([o['x'] * T, o['y'] * T, (o['x'] + o.get('w', 1)) * T - 1, (o['y'] + o.get('h', 1)) * T - 1], fill=col)
        ov.alpha_composite(lay); ov.resize((PW * 3, PH * 3), Image.NEAREST).save(OV)
    print('ok', sum(r.count('.') for r in rows), 'walkable tiles')
main()
