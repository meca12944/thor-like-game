"""Builds test128/maps/felt.json (chapter 1 town 「펠트」) + assets/world/felt_bg.png from PixelLab parts.
python3 tools/felt/build_felt.py [overlay.png]

Parts (tools/felt/parts/*.png) are PixelLab map-objects and Wang tilesets made for this map
(generator + usage log: handoff/claude/felt_pixellab/). The ground is Wang corner-tiled from two tilesets
(ashen grass <-> dirt, dirt <-> cobblestone); buildings and props are pasted 1:1 (16 px = 1 tile) and every
opaque tile of a building or a solid prop becomes collision. Edit LAYOUT / ROADS / PROPS / NPCS below and re-run."""
import sys, os, json, base64, io, random
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..'); P = os.path.join(HERE, 'parts')
OV = sys.argv[1] if len(sys.argv) > 1 else None
W, H, T = 56, 34, 16

# ---- ground: vertex terrain grid (W+1) x (H+1): 0 grass, 1 dirt, 2 cobble ----
def rect(g, x0, y0, x1, y1, v):  # vertex rect, inclusive
    for y in range(max(0, y0), min(H, y1) + 1):
        for x in range(max(0, x0), min(W, x1) + 1): g[y][x] = max(g[y][x], v) if v else v
ROADS = [  # dirt (vertex rects x0, y0, x1, y1)
 (1, 13, 55, 15),    # north lane
 (1, 23, 55, 25),    # south lane
 (27, 13, 30, 34),   # centre road -> south exit
 (17, 13, 19, 33),   # west cross lane
 (45, 13, 47, 33),   # east cross lane
 (0, 23, 2, 25),     # west edge
]
PLAZA = (22, 15, 35, 23)   # cobble (vertex rect), inside a dirt ring

# ---- buildings: part, centre tile x, bottom tile y (sprite bottom edge), door (dx from centre) ----
LAYOUT = [
 ('ruin_wall1_s101', 8, 7, None), ('ruin_wall2_s101', 24, 6, None), ('ruin_wall1_s202', 40, 7, None), ('ruin_wall2_s202', 54, 6, None),
 ('bld_guard_s101', 4, 13, ('f_door_guard', 0)),
 ('bld_smith_s101', 12, 13, ('f_door_smith', 0)),
 ('bld_chief_s101', 28, 13, ('f_door_chief', 0)),
 ('bld_chapel_s101', 39, 13, ('f_door_chapel', 0)),
 ('bld_burned_s101', 51, 13, None),
 ('bld_weapon_s101', 6, 23, ('f_door_weapon', 0)),
 ('bld_tool_s101', 13, 23, ('f_door_tool', 0)),
 ('bld_inn_s101', 40, 23, ('f_door_inn', 0)),
 ('bld_herb_s101', 51, 23, ('f_door_herb', 0)),
 ('bld_shack1_s101', 5, 32, None),
 ('bld_shack2_s101', 11, 32, None),
 ('bld_shack1_s202', 23, 32, None),
 ('bld_atelier_s101', 36, 32, ('f_door_atelier', 0)),
 ('bld_stall_s101', 42, 32, None),
 ('web_ruin_s101', 52, 32, ('f_arachne_gate', 0)),
 ('fountain_s101', 28.5, 20.5, None),
]
# props: part, tile x (left), tile y (bottom), solid
PROPS = [
 ('p_lamp_s101', 16, 15, 1), ('p_lamp_s101', 31, 15, 1), ('p_lamp_s101', 44, 15, 1), ('p_lamp_s101', 21, 25, 1), ('p_lamp_s101', 35, 25, 1),
 ('p_board_s101', 23, 17, 1), ('p_bench_s101', 32, 22, 1), ('p_bench_s202', 23, 22, 1),
 ('p_brazier_s101', 7, 14, 1), ('p_crates_s101', 1, 21, 1), ('p_sacks_s101', 16, 21, 1), ('p_cart_s101', 9, 28, 1),
 ('p_deadtree_s101', 0, 33, 1), ('p_deadtree_s202', 15, 31, 1), ('p_deadtree_s101', 33, 21, 1), ('p_deadtree_s202', 54, 21, 1),
 ('p_rubble_s101', 47, 21, 1), ('p_rubble_s202', 19, 33, 1), ('p_pillar_s101', 33, 33, 1), ('p_pillar_s202', 48, 12, 1),
 ('p_fence_s101', 2, 33, 1), ('p_fence_s202', 37, 33, 1),
 ('p_web_s101', 49, 31, 0), ('p_web_s202', 54, 28, 0), ('p_web_s101', 50, 26, 0),
 ('prop_barrel', 9, 22, 1), ('prop_barrel', 44, 22, 1),
]
NPCS = [  # id, tile x, tile y, name, role, art (placeholder sprites from towns A/C/F), idle line
 ('f_bart',    26, 14, '바르트', '이장',      'a_chief',     '30년 전 그 불길을 아직도 기억하네. 하늘까지 붉었지…… 왕도는 하룻밤 사이에 재가 됐어.'),
 ('f_rom',     14, 14, '롬',     '대장장이',  'a_smith',     '괴물한테 칼을 팔 생각은 없어. …돈은 있나? 그럼 얘기가 달라지지.'),
 ('f_sera',    49, 24, '세라',   '약초꾼',    'a_herb',      '요즘 약초를 말리다 보면…… 잎사귀가 꿈틀거리는 것 같아. 내가 피곤한 거겠지?'),
 ('f_gas',      6, 14, '가스',   '경비대장',  'a_guard',     '밤만 되면 어디선가 실 잣는 소리가 들려. 철사를 긁는 것 같은…… 외지인, 해 지면 돌아다니지 마.'),
 ('f_martha',  38, 24, '마르타', '여관 주인', 'c_innkeeper', '외지인은 안 받아. …하룻밤만이야. 문제 일으키면 바로 내쫓을 거다.'),
 ('f_toby',    25, 21, '토비',   '아이',      'a_kid',       '펠릭스가 공방 쪽으로 공 주우러 갔는데 안 돌아와요…… 아저씨, 혹시 못 봤어요?'),
 ('f_oswald',  41, 14, '오스왈드','수도사',   'c_priest',    '오늘 밤에도 기도회가 열립니다. 이 땅의 독을 씻어 낼 것은 오직 기도뿐이오.'),
 ('f_ben',     42, 33, '벤',     '떠돌이 상인','f_merchant', '이 장부, 분명 30년 전 거라는데 글씨가 하나도 안 바랬어. 이상하지 않아?'),
 ('f_luca',    32, 17, '루카',   '시인',      'a_bard',      '「불탄 왕도에 실이 내리고……」 아, 또 이런 가사가 나오네. 요즘은 밝은 노래가 안 써져.'),
 ('f_linette', 34, 33, '리네트', '재봉사',    'a_tailor',    '여긴 왕실 의상실이 있던 자리예요. 언젠가 여기서 영웅의 망토를 만들 거예요!'),
]
DOORS = {  # id -> name, extra
 'f_door_weapon': ('중고 무기점', {'shop': 'f_weapon'}),
 'f_door_tool': ('잡화점', {'shop': 'f_tool'}),
 'f_door_smith': ('롬의 대장간', {'text': '롬의 대장간 — 모루 강화는 준비 중이다. (placeholder)'}),
 'f_door_chief': ('이장 바르트의 집', {'text': '이장 바르트의 집 — 실내는 준비 중이다. (placeholder)'}),
 'f_door_herb': ('세라의 약초 오두막', {'text': '세라의 약초 오두막 — 실내는 준비 중이다. (placeholder)'}),
 'f_door_guard': ('경비 초소', {'text': '경비 초소와 감시탑 — 실내는 준비 중이다. (placeholder)'}),
 'f_door_inn': ('마르타의 여관', {'heal': 1, 'text': '마르타의 여관 — 하룻밤 쉬었다. 체력이 모두 회복됐다.'}),
 'f_door_chapel': ('낡은 예배당', {'text': '낡은 예배당 — 기도회는 밤에만 열린다. 실내는 준비 중이다. (placeholder)'}),
 'f_door_atelier': ('리네트의 공방', {'text': '리네트의 공방 (왕실 의상실 폐허) — 실내는 준비 중이다. (placeholder)'}),
 'f_arachne_gate': ('아라크네의 폐공방', {'text': '거미줄로 뒤덮인 폐허가 마을 울타리 너머로 이어진다. 안쪽에서 철사 긁는 소리가 난다.\n(1장 보스 던전 — 준비 중)'}),
}

def load_tiles(name):
    t = json.load(open(os.path.join(P, name)))['tileset']['tiles']; out = {}
    for tl in t:
        c = tl['corners']; key = tuple(c[k] == 'upper' for k in ('NW', 'NE', 'SW', 'SE'))
        out.setdefault(key, []).append(Image.open(io.BytesIO(base64.b64decode(tl['image']['base64']))).convert('RGBA'))
    return out

def part(name):
    im = Image.open(os.path.join(P, name + '.png')).convert('RGBA'); bb = im.getbbox(); return im.crop(bb) if bb else im

def main():
    rnd = random.Random(7)
    g = [[0] * (W + 1) for _ in range(H + 1)]
    for r in ROADS: rect(g, *r, 1)
    x0, y0, x1, y1 = PLAZA; rect(g, x0 - 1, y0 - 1, x1 + 1, y1 + 1, 1); rect(g, x0, y0, x1, y1, 2)
    TG, TC = load_tiles('tiles_grass_dirt.json'), load_tiles('tiles_dirt_cobble.json')
    bg = Image.new('RGBA', (W * T, H * T))
    for y in range(H):
        for x in range(W):
            c = (g[y][x], g[y][x + 1], g[y + 1][x], g[y + 1][x + 1])
            if max(c) == 2: key, S = tuple(v == 2 for v in c), TC
            else: key, S = tuple(v >= 1 for v in c), TG
            bg.paste(rnd.choice(S[key]), (x * T, y * T))
    solid = [[False] * W for _ in range(H)]
    for x in range(W): solid[0][x] = solid[H - 1][x] = True
    for y in range(H): solid[y][0] = solid[y][W - 1] = True
    for x in range(27, 30): solid[H - 1][x] = False          # south exit gap
    def stamp(im, px, py, mark):
        bg.alpha_composite(im, (int(px), int(py)))
        if not mark: return
        a = im.split()[3]
        for ty in range(int(py) // T, (int(py) + im.height - 1) // T + 1):
            for tx in range(int(px) // T, (int(px) + im.width - 1) // T + 1):
                if not (0 <= tx < W and 0 <= ty < H): continue
                box = (tx * T - int(px), ty * T - int(py), tx * T - int(px) + T, ty * T - int(py) + T)
                cov = sum(1 for v in a.crop(box).getdata() if v > 128) / (T * T)
                if cov > .3: solid[ty][tx] = True
    doors = []
    for name, cx, by, door in LAYOUT:
        im = part(name); px, py = cx * T - im.width / 2, by * T - im.height; stamp(im, px, py, True)
        if door: doors.append((door[0], int(cx + door[1]), int(by) - 1))
    for name, tx, by, sol in PROPS:
        im = part(name); stamp(im, tx * T, by * T - im.height, bool(sol))
    objs = [{'type': 'exit', 'x': 27, 'y': H - 1, 'w': 3, 'h': 1, 'to': 'world', 'spawn': 'townA', 'label': '↓ 차가운 대지 · 월드맵'},
            {'type': 'sign', 'x': 26, 'y': 26, 'text': '펠트\n← 무기점 · 잡화점 · 대장간   ↑ 이장 집 · 예배당   → 여관 · 약초 오두막   ↘ 리네트의 공방'}]
    for i, x, y in doors:
        solid[y][x] = True; n, extra = DOORS[i]; objs.append(dict({'type': 'door', 'id': i, 'x': x, 'y': y, 'name': n}, **extra))
    for i, x, y, name, role, art, idle in NPCS:
        objs.append({'type': 'npc', 'id': i, 'x': x, 'y': y, 'name': name, 'role': role, 'main': 1 if i in ('f_linette', 'f_bart') else 0, 'idle': idle, 'art': art})
    rows = [''.join('#' if solid[y][x] else '.' for x in range(W)) for y in range(H)]
    for o in objs:   # npcs / signs must stand on open ground (the engine makes their tile solid)
        if o['type'] in ('npc', 'sign') and rows[o['y']][o['x']] == '#': print('WARN', o['type'], o.get('id'), 'on a solid tile', o['x'], o['y'])
    j = {'id': 'felt', 'type': 'town', 'area': 1, 'region': 'felt', 'name': '펠트',
         'title': {'kicker': 'CHAPTER 1', 'name': '펠트', 'sub': '불탄 왕도 외곽의 빈민가'},
         'bgm': 'town_ruin', 'battleBgm': 'field_battle', 'tileset': 'field', 'tile': T, 'w': W, 'h': H,
         'bg': 'assets/world/felt_bg.png',
         'note': 'generated by tools/felt/build_felt.py from PixelLab parts (tools/felt/parts) — do not hand-edit. NPC art = placeholders from towns A/C/F.',
         'legend': {'.': 'dirt', '#': {'ground': 'dirt', 'solid': True}}, 'solid': ['#'],
         'spawns': {'default': [28.5, 31.5, 'up'], 'world': [28.5, 31.5, 'up']},
         'objects': objs, 'ground': rows}
    json.dump(j, open(os.path.join(ROOT, 'maps', 'felt.json'), 'w'), ensure_ascii=False, indent=1)
    bg.convert('RGB').save(os.path.join(ROOT, 'assets', 'world', 'felt_bg.png'), optimize=True)
    if OV:
        ov = bg.copy(); d = ImageDraw.Draw(ov, 'RGBA')
        for y, r in enumerate(rows):
            for x, c in enumerate(r):
                if c == '#': d.rectangle([x * T, y * T, x * T + T - 1, y * T + T - 1], fill=(255, 0, 0, 70))
        for o in objs:
            col = {'npc': (60, 160, 255, 230), 'door': (255, 220, 0, 230), 'exit': (0, 255, 120, 200), 'sign': (255, 255, 255, 230)}[o['type']]
            d.rectangle([o['x'] * T, o['y'] * T, (o['x'] + o.get('w', 1)) * T - 1, (o['y'] + o.get('h', 1)) * T - 1], fill=col)
        ov.resize((ov.width * 2, ov.height * 2), Image.NEAREST).save(OV)
    print('ok', sum(r.count('.') for r in rows), 'walkable tiles')
main()
