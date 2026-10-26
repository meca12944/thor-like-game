#!/usr/bin/env python3
"""1장 동쪽 들판 · 가도 들머리 (ch1_field_e, 190x260) — 그록 1장 그림으로 조립 (팀장 10-25 「동쪽 들판부터」).

설계도: docs_maps/ch1/ch1_map.json 구역 field_e (전체 좌표 440,70 → 이 맵 0,0). 조립표: docs_maps/ch1/CH1_ASSEMBLY_PLAN_ko.md.
그림: handoff/grok_in/1장_풍경_20261025 (1배 = 1타일 16px), 16-22_소품_인물 (4배 원본은 D=4로 또렷하게).
- 바닥: 잿빛 바닥 512px 4장(v0~v3)을 32타일 조각마다 섞어 깔고, 길(흙)·잿더미·마른 풀을 구움.
- 거인 기사상(안 늘린 판)·검·호수 = 바닥 높이(under) + 막힘 칸은 그림의 알파로. 손바닥 = 걷는 쉼터.
- 투구·승강기·베르디 정문 = 세워진 소품(주인공과 앞뒤 정렬, 뒤에 가면 반투명).
- 남쪽 끝 = 펠트 성벽(펠트 v5 성벽 그림 재사용) + 1장 정문, 북쪽 끝 = 낭떠러지 + 먼 왕성(무덤가와 같은 원경).
- 효과(호수에 비친 왕성·종소리·재·바람)는 코드 몫 → 검흔 담당 목록 (조립표 4절).
몹: 마물 다시 기획 전이라 지금 1장 몹 4종을 설계도 무리 자리에 돌려 놓음 (큰 3 / 보통 2 / 작은 1마리).
usage: python3 tools/hd/fields/build_ch1_east.py   (test128 에서)
"""
import json, os, random, math
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); T128 = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
REPO = os.path.dirname(T128)
G1 = os.path.join(REPO, 'handoff/grok_in/1장_풍경_20261025'); G2 = os.path.join(REPO, 'handoff/grok_in/16-22_소품_인물_주인공동작_20261025')
OUT = 'assets/world/ch1_east'; OUTD = os.path.join(T128, OUT); os.makedirs(OUTD, exist_ok=True)
W, H, TS = 190, 260, 16
OX, OY = 440, 70          # 설계도 전체 좌표 → 이 맵
rnd = random.Random(1025)

grid = [['.'] * W for _ in range(H)]
def put(x, y, c):
    if 0 <= x < W and 0 <= y < H: grid[y][x] = c
def rect(x0, y0, x1, y1, c):
    for y in range(y0, y1):
        for x in range(x0, x1): put(x, y, c)

# ---- 바닥 그림 ----
GW, GH = W * TS, H * TS
ground = Image.new('RGBA', (GW, GH))
tiles = [Image.open(f'{G1}/01_ash_field/01_ash_ground_512_v{i}.png').convert('RGBA') for i in range(4)]
for cy in range(0, GH, 512):           # v0 를 깔고 (스스로 이음매 없음) v1~v3 는 부드러운 얼룩으로 덮음 → 조각 경계 줄이 안 보임
    for cx in range(0, GW, 512): ground.paste(tiles[0], (cx, cy))
for i in (1, 2, 3):
    full = Image.new('RGBA', (GW, GH))
    for cy in range(0, GH, 512):
        for cx in range(0, GW, 512): full.paste(tiles[i], (cx, cy))
    m = Image.new('L', (GW // 8, GH // 8)); dm = ImageDraw.Draw(m)
    for _ in range(14):
        x, y, r = rnd.uniform(0, GW / 8), rnd.uniform(0, GH / 8), rnd.uniform(25, 70); dm.ellipse([x - r, y - r * .7, x + r, y + r * .7], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(14)).resize((GW, GH), Image.BILINEAR)
    ground.paste(full, (0, 0), m)

def paint_road(pts, wtiles, col=(92, 80, 68), a=95):
    m = Image.new('L', (GW, GH)); d = ImageDraw.Draw(m)
    d.line([(x * TS, y * TS) for x, y in pts], fill=255, width=int(wtiles * TS), joint='curve')
    for x, y in pts: r = wtiles * TS / 2; d.ellipse([x * TS - r, y * TS - r, x * TS + r, y * TS + r], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * a / 255))
    ground.paste(Image.new('RGBA', (GW, GH), col + (255,)), (0, 0), m)
    return m

ROAD1 = [(75.5, 259), (75.5, 236), (62, 224), (40, 214), (18, 210), (0, 210)]          # 1장 정문 → 서쪽(들판 중앙 쪽)
ROAD2 = [(40, 214), (60, 196), (92, 176), (118, 140), (128, 96), (150, 56), (174, 32), (189, 26)]  # 갈림길 → 북동쪽 2장 가도
paint_road(ROAD1, 3.2); paint_road(ROAD2, 3.0)
foot = Image.open(f'{G1}/01_ash_field/deco/01_footprint_stamp_4x7.png').convert('RGBA')

# ---- 큰 경관 ----
props, under = [], []
def alpha_mask(im, x0, y0, c, keep=None, thr=.5, dark=None):
    a = im.split()[3]; px = im.load(); w, h = im.size
    for ty in range(math.ceil(h / TS)):
        for tx in range(math.ceil(w / TS)):
            if keep and keep(tx, ty): continue
            n = hit = 0
            for yy in range(ty * TS, min(h, ty * TS + TS), 2):
                for xx in range(tx * TS, min(w, tx * TS + TS), 2):
                    n += 1; r, g, b, al = px[xx, yy]
                    if al > 128 and (dark is None or (r + g + b) / 3 < dark): hit += 1
            if n and hit / n > thr: put(x0 + tx, y0 + ty, c)

def save_img(src, name, scale=None):
    im = Image.open(src).convert('RGBA')
    if scale: im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    p = f'{OUT}/{name}.webp'; im.save(os.path.join(T128, p), 'WEBP', quality=88, method=6); return p, im

# 검은 호수 (설계도 524,104 → 84,34), 물 = 막힘
LX, LY = 84, 34
import numpy as np
from scipy import ndimage as ndi
def lake_art():   # 팀장 10-25 「까만 면」: 물가 한 줄 밝은 물결 + 물 깊이 옅은 남색 (반사 왕성·종탑·잔물결은 효과 담당 코드 lakeart)
    im = Image.open(f'{G1}/08_black_lake/08_black_lake_empty_back.png').convert('RGBA'); a = np.asarray(im).astype(np.float32)
    water = (a[..., 3] > 128) & (a[..., :3].mean(-1) < 40)
    rim = water & ~ndi.binary_erosion(water, iterations=5); rim = ndi.gaussian_filter(rim.astype(np.float32), 2.5)
    glow = ndi.gaussian_filter(water.astype(np.float32), 40) * water   # 물 가운데로 갈수록 아주 조금 밝은 남색 (깊이)
    out = a.copy(); out[..., :3] += (rim[..., None] * np.array([70, 72, 80]) * .9) + ((1 - glow)[..., None] * water[..., None] * np.array([10, 12, 18]))
    o = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    p = f'{OUT}/black_lake.webp'; o.save(os.path.join(T128, p), 'WEBP', quality=90, method=6); return p, im   # 종탑 거꾸로 비침은 코드(lakeart)가 그림 → 여기선 안 구움
lake_p, lake = lake_art()
under.append({'id': 'black_lake', 'img': lake_p, 'x': LX, 'y': LY, 'ax': 0, 'ay': 0, 'D': 1, 'under': 1})
alpha_mask(lake, LX, LY, '~', thr=.45, dark=40)
tip_p, tip = save_img(f'{G1}/08_black_lake/08_sunken_belltower_tip_back.png', 'belltower_tip')
props.append({'id': 'belltower_tip', 'img': tip_p, 'x': 128.5, 'y': 62, 'D': 1, 'fade': 0, 'shadow': 0})

# 쓰러진 거인 기사상 (안 늘린 판 120x38, 설계도 466,160 → 26,90). 손바닥(왼쪽 끝 11타일) = 걸어 올라가는 쉼터
kn_p, kn = save_img(f'{G1}/05_giant_knight/05_knight_body_alt_uniform_back.png', 'giant_knight')
KX, KY, KD = 26, 96, 1.6   # 팀장 10-25 「거인 전체가 보이게」: 120타일(화면 3.4개)은 전망에서도 안 들어와서 1/1.6 = 75x24타일 (몸 길이 = 주인공 키 42px의 약 29배, 누운 몸 폭 약 9배), 그림도 줄여 그려 더 또렷
under.append({'id': 'giant_knight', 'img': kn_p, 'x': KX, 'y': KY, 'ax': 0, 'ay': 0, 'D': KD, 'under': 1})
alpha_mask(kn.resize((round(kn.width / KD), round(kn.height / KD)), Image.LANCZOS), KX, KY, 'K', keep=lambda tx, ty: tx <= 7 and ty >= 16, thr=.55)
hm_p, hm = save_img(f'{G1}/05_giant_knight/05_knight_helmet_back.png', 'giant_helmet')
props.append({'id': 'giant_helmet', 'img': hm_p, 'x': 136, 'y': 181, 'D': 1, 'fade': 1, 'shadow': 1})
rect(130, 175, 143, 181, 'X')
sw_p, sw = save_img(f'{G1}/05_giant_knight/05_knight_sword_back.png', 'giant_sword')
under.append({'id': 'giant_sword', 'img': sw_p, 'x': 6, 'y': 186, 'ax': 0, 'ay': 0, 'D': 1, 'under': 1})   # 칼날 위는 걸을 수 있음

# 1~2장 승강기 (설계도 600,280 → 160,210), 4배 원본 D=4
lf_p, lf = save_img(f'{G2}/17_shortcuts/17b_lift_256x320_4x_master.png', 'lift')
HS = 42 / 34   # 주인공 실제 화면 키 42 필드px (팀장 10-25, 그록은 34 기준으로 그림) → 사람 크기에 맞춘 소품(승강기·베르디)은 1.24배
props.append({'id': 'lift_ch2', 'img': lf_p, 'x': 162, 'y': 214, 'D': round(4 / HS, 2), 'fade': 1, 'shadow': 1})
rect(159, 210, 165, 214, 'X')

# 1장 정문 옆 베르디의 돌기둥 문 (4배 원본, 정문 서쪽)
vd_p, vd = save_img(f'{G2}/16_gate_verdi/16_gate_verdi_384x320_4x_master.png', 'verdi_gate')
props.append({'id': 'verdi_gate', 'img': vd_p, 'x': 64, 'y': 246, 'D': round(4 / HS, 2), 'fade': 1, 'shadow': 1})
rect(60, 243, 68, 246, 'X')

# 작은 경관 (그록 12a·b·d): 정문~거인 사이 빈 벌판에 눈 둘 곳. back = 바닥 높이, front = 위쪽(주인공을 가림), 가로 기준선 = 그록 README 값
SM = f'{G1}/12_small_sceneries'
_sm_n = {}
def save_fl(src, name, fl):
    im = Image.open(src).convert('RGBA')
    if fl: im = im.transpose(Image.FLIP_LEFT_RIGHT); name += '_fl'
    p = f'{OUT}/{name}.webp'
    if not os.path.exists(os.path.join(T128, p)) or p not in _sm_n: im.save(os.path.join(T128, p), 'WEBP', quality=88, method=6); _sm_n[p] = 1
    return p, im
def small(name, x, y, split, solid_thr=None, fl=False):
    k = _sm_n[name] = _sm_n.get(name, 0) + 1
    bp, bi = save_fl(f'{SM}/{name}_back.png', name + '_back', fl)
    under.append({'id': f'{name}_b{k}', 'img': bp, 'x': x, 'y': y, 'ax': 0, 'ay': 0, 'D': 1, 'under': 1})
    if split is not None:
        fp, fi = save_fl(f'{SM}/{name}_front.png', name + '_front', fl)
        props.append({'id': f'{name}_f{k}', 'img': fp, 'x': x, 'y': round(y + split * fi.height / TS, 2), 'ax': 0, 'ay': round(split * fi.height), 'D': 1, 'fade': 1, 'shadow': 0})
    if solid_thr:
        ref = Image.open(f'{SM}/{name}_full_ref.png' if split is not None else f'{SM}/{name}_back.png').convert('RGBA')
        if fl: ref = ref.transpose(Image.FLIP_LEFT_RIGHT)
        alpha_mask(ref, x, y, 'X', thr=solid_thr, keep=lambda tx, ty: split is not None and ty < split * 0.9 * bi.height / TS)
    return bi.width / TS, bi.height / TS
small('12a_collapsed_tower', 14, 150, .5, .6)
small('12b_old_battlefield_spears', 98, 204, .45)
small('12d_ash_mound_hill', 120, 230, None, .8)

# 남쪽 = 펠트 성벽 (펠트 v5 성벽·성문 그림 그대로, 밑동 y 259)
felt = json.load(open(os.path.join(T128, 'maps/felt.json')))
for q in felt['hd']['props']:
    if q['id'].startswith('wall_') or q['id'] == 'gate_tunnel':
        props.append(dict(q, id='fw_' + q['id'], y=259.6 if q['id'] != 'gate_tunnel' else 258.6, fade=1))
rect(0, 247, W, H, '#'); rect(72, 247, 80, H, '.')       # 성벽 띠는 막힘, 1장 정문(72~79)만 열림

# 북쪽 끝 = 낭떠러지 (위 12줄), 동·서 끝 막힘
rect(0, 0, W, 12, '#'); rect(0, 0, 1, H, '#'); rect(W - 1, 0, W, H, '#')
# (그록 절벽 띠는 아래 가장자리가 딱 끊겨 줄이 보여서 여기선 안 씀 → 북쪽 절벽 맵에서 낙석으로 덮어 씀) 위 12줄 = 낭떠러지, 그 너머 먼 왕성
rocks = [save_img(f'{G1}/11_north_cliff/11_fallen_rock_{n}_back.png', 'rock_' + n) for n in ('boulder_pile', 'rock_slab', 'pebbles')]

# 잿더미·마른 풀·발자국 (길·호수·거인 피함)
deco = [Image.open(f'{G1}/01_ash_field/deco/{n}.png').convert('RGBA') for n in ['01_ash_mound_a', '01_ash_mound_b', '01_ash_drift_long', '01_ash_mound_beam']]
tufts = [Image.open(f'{G1}/01_ash_field/deco/01_grass_tuft_{i:02d}.png').convert('RGBA') for i in range(12)]
road_m = Image.new('L', (W, H)); rd = ImageDraw.Draw(road_m)
rd.line(ROAD1, fill=255, width=5); rd.line(ROAD2, fill=255, width=5)
rpx = road_m.load()
def free(x, y, r=2):
    for yy in range(int(y) - r, int(y) + r + 1):
        for xx in range(int(x) - r, int(x) + r + 1):
            if not (0 <= xx < W and 0 <= yy < H) or grid[yy][xx] != '.' or rpx[xx, yy]: return False
    return True
edge = Image.new('L', (GW, 15 * TS)); de = ImageDraw.Draw(edge)   # 낭떠러지 가장자리: 아래로 어두워지는 띠 + 낙석 줄
for y in range(15 * TS): de.line([(0, y), (GW, y)], fill=int(255 * max(0, min(1, (15 * TS - y) / (5 * TS))) ** 1.5 * .8))
ground.paste(Image.new('RGBA', (GW, 15 * TS), (28, 24, 22, 255)), (0, 0), edge)
for i, x in enumerate(range(3, W - 2, 9)):
    (rp, ri) = rocks[2 if i % 3 else 0]; props.append({'id': f'edge_{i}', 'img': rp, 'x': x + rnd.uniform(-1.5, 1.5), 'y': 13.2 + rnd.uniform(0, 1.2), 'D': 1, 'fade': 1, 'shadow': 0})
for i in range(26):                    # 떨어진 바위 (세워진 소품, 밑동만 막힘) — 넓은 재 벌판에 눈 둘 곳
    (rp, ri) = rocks[i % 3]; w, h = ri.width / TS, ri.height / TS
    for _ in range(30):
        x, y = rnd.uniform(6, W - 8), rnd.uniform(20, 238)
        if free(x, y - 1, 4): break
    else: continue
    props.append({'id': f'rock_{i}', 'img': rp, 'x': round(x, 1), 'y': round(y, 1), 'D': 1, 'fade': 1, 'shadow': 1})
    if i % 3 != 2: rect(int(x - w / 2 + .5), int(y - 1), int(x + w / 2 - .5), int(y), 'X')
# ---- 화면마다 눈 둘 것 하나 (팀장 10-25 「너무 비어 보임」, 엘든링식 멀리 보이는 표지물) ----
# PC 1080p 화면 ≈ 30x17타일 → 그 크기 칸마다 큰 경관이 없으면 하나 놓음: 마른 나무 숲 / 그록 작은 경관(뒤집은 판 포함) / 돌무더기 / 부서진 무기
BIG = [(26, 96, 75, 24), (84, 34, 85, 50), (129, 161, 15, 20), (6, 186, 60, 6), (156, 204, 9, 10), (55, 234, 30, 14), (14, 150, 24, 18), (98, 204, 30, 21), (120, 230, 28, 16)]
felt_deco = felt['hd'].get('decoArt', {})
def crop_at(x, y, k):   # 길가·옛 싸움 흔적 = 펠트 잔해 그림 (그록 옛 싸움터 그림은 무기가 땅과 붙어 있어 낱개로 못 자름)
    q = felt_deco['R'][k % len(felt_deco['R'])]; props.append(dict(q, id=f'wreck_{len(props)}', x=round(x, 1), y=round(y, 1), fade=1, shadow=1))
def chars_near(cx, cy, ch, k, r):
    for _ in range(k * 6):
        if k <= 0: break
        x, y = int(cx + rnd.uniform(-r, r)), int(cy + rnd.uniform(-r * .6, r * .6))
        if free(x, y, 1): put(x, y, ch); k -= 1
_dbg = [0, 0]
SMALLS = [('12a_collapsed_tower', .5, .6), ('12b_old_battlefield_spears', .45, None), ('12c_petrified_grove', .55, None), ('12d_ash_mound_hill', None, .8)]
for cy in range(18, 236, 17):
    for cx in range(0, W - 10, 30):
        if any(bx - 6 < cx + 15 < bx + bw + 6 and by - 4 < cy + 8.5 < by + bh + 4 for bx, by, bw, bh in BIG): continue   # 칸 가운데가 큰 경관 곁이면 이미 볼 것이 있음
        kind = rnd.random(); x, y = cx + rnd.uniform(6, 24), cy + rnd.uniform(4, 13)
        _dbg[0] += 1
        if kind < .32:                                   # 마른 나무 숲
            chars_near(x, y, 'T', rnd.randint(4, 7), 6); chars_near(x, y, 's', 2, 7)
        elif kind < .62:                                 # 그록 작은 경관
            nm, sp, st = rnd.choice(SMALLS); w0, h0 = (24, 18) if nm.startswith('12a') else (30, 21) if nm.startswith('12b') else (32, 22) if nm.startswith('12c') else (28, 16)
            x0, y0 = min(W - w0 - 2, max(2, x - w0 / 2)), min(240 - h0, max(16, y - h0 / 2))
            if all(free(x0 + i * w0 / 3, y0 + j * h0 / 2, 1) for i in range(4) for j in range(3)):
                small(nm, round(x0), round(y0), sp, st, fl=rnd.random() < .5); BIG.append((round(x0), round(y0), w0, h0)); _dbg[1] += 1
            else: chars_near(x, y, 'T', 4, 6)
        elif kind < .82:                                 # 돌무더기
            (rp, ri) = rocks[rnd.randrange(2)]
            if free(x, y - 1, 2): props.append({'id': f'rock_c{len(props)}', 'img': rp, 'x': round(x, 1), 'y': round(y, 1), 'D': 1, 'fade': 1, 'shadow': 1}); rect(int(x - 2), int(y - 1), int(x + 2), int(y), 'X')
            chars_near(x, y, 'R', rnd.randint(3, 5), 6)
        else:                                            # 옛 싸움의 잔해
            for k in range(rnd.randint(3, 5)):
                px_, py_ = x + rnd.uniform(-5, 5), y + rnd.uniform(-3, 3)
                if free(px_, py_, 1): crop_at(px_, py_, rnd.randrange(99))
for Rd in (ROAD1, ROAD2):                                # 길가 흔적: 그루터기·부서진 무기·자갈 (길 = 사람이 다녔던 곳)
    for i in range(len(Rd) - 1):
        (x0, y0), (x1, y1) = Rd[i], Rd[i + 1]; L_ = math.hypot(x1 - x0, y1 - y0); nx, ny = -(y1 - y0) / max(L_, 1e-6), (x1 - x0) / max(L_, 1e-6)
        for k in range(int(L_ / 7)):
            t = (k + .5) / max(1, int(L_ / 7)); sd = 3.5 if (k + i) % 2 else -3.5; x, y = x0 + (x1 - x0) * t + nx * sd, y0 + (y1 - y0) * t + ny * sd
            if not (16 < y < 240) or grid[int(y)][int(x)] != '.': continue
            r_ = rnd.random()
            if r_ < .35: put(int(x), int(y), 's')
            elif r_ < .7: crop_at(x, y, rnd.randrange(99))
            else: props.append({'id': f'peb_{len(props)}', 'img': rocks[2][0], 'x': round(x, 1), 'y': round(y, 1), 'D': 1, 'fade': 0, 'shadow': 0})

for _ in range(140):
    x, y = rnd.uniform(4, W - 8), rnd.uniform(16, 240); im = rnd.choice(deco)
    if free(x + im.width / 32, y + im.height / 32, 4): ground.alpha_composite(im, (int(x * TS), int(y * TS)))
for _ in range(900):
    x, y = rnd.uniform(2, W - 3), rnd.uniform(14, 245); im = rnd.choice(tufts)
    if free(x, y, 0): ground.alpha_composite(im, (int(x * TS - im.width / 2), int(y * TS - im.height)))
for R in (ROAD1, ROAD2):               # 길을 따라 재에 찍힌 발자국 (길 = 사람이 다닌 자리)
    for i in range(len(R) - 1):
        (x0, y0), (x1, y1) = R[i], R[i + 1]; n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 5))
        for k in range(n):
            t = (k + .5) / n; ground.alpha_composite(foot, (int((x0 + (x1 - x0) * t) * TS + rnd.uniform(-6, 6)), int((y0 + (y1 - y0) * t) * TS)))

ground.convert('RGB').save(os.path.join(OUTD, 'ground.webp'), 'WEBP', quality=82, method=6)

# ---- 물체 ----
def L(gx, gy): return gx - OX, gy - OY
objs = []
objs.append({'type': 'exit', 'x': 72, 'y': 259, 'w': 8, 'h': 1, 'to': 'felt', 'spawn': 'gate', 'label': '↓ 펠트 마을'})
objs.append({'type': 'npc', 'id': 'f_verdi', 'x': 65, 'y': 243, 'name': '베르디', 'role': '기록관', 'main': 1, 'art': 'hd', 'portrait': 'f_verdi', 'face0': 'right',
             'idle': '오늘도 적을 것이 없군. 다행인지 불행인지.'})
objs.append({'type': 'waystone', 'id': 'ws_giant_palm', 'x': 30, 'y': 115, 'name': '거인 손바닥 모닥불'})
objs.append({'type': 'waystone', 'id': 'ws_road_head', 'x': 120, 'y': 80, 'name': '가도 들머리 모닥불'})
objs.append({'type': 'vista', 'id': 'ce_giant', 'x': 64, 'y': 142, 'r': 3.5, 'zoom': 0.27, 'dir': 270, 'pan': 24, 'hold': 1,
             'name': '쓰러진 거인', 'sub': '성문의 맹세를 지키다 누운 기사'})
objs.append({'type': 'vista', 'id': 'ce_lake', 'x': 126, 'y': 89, 'r': 3, 'zoom': 0.62, 'dir': 270, 'pan': 24, 'hold': 1,   # 효과 담당 lakeart(반사 왕성·잔물결) 뒤 다시 켬
             'name': '검은 호수', 'sub': '물 위로 종탑 끝만 남은 옛 거리'})
objs.append({'type': 'vista', 'id': 'ce_gate', 'x': 75, 'y': 238, 'r': 3, 'zoom': 0.62, 'dir': 270, 'pan': 0, 'hold': 1,
             'name': '1장 정문 밖', 'sub': '돌기둥에 앉은 기록관이 문을 지킨다'})
objs.append({'type': 'clue', 'id': 'ce_remains', 'x': 80, 'y': 160, 'name': '쓰러진 탈영병', 'flag': 'ce_look_remains',
             'text': '빈 망토와 팔 보호대만 남았다. 성벽 쪽을 향해 쓰러져 있다.\n…끝까지 밖으로 나가려 했던 모양이다.', 'textDone': '성벽 쪽을 향해 쓰러진 빈 망토.'})
objs.append({'type': 'clue', 'id': 'ce_belltower', 'x': 127, 'y': 85, 'name': '물 위의 종탑 끝', 'flag': 'ce_look_bell',
             'text': '검은 물 위로 종탑 지붕 끝만 솟아 있다. 물이 너무 잔잔해서 바닥이 보이지 않는다.\n…아주 멀리서, 종소리가 한 번.', 'textDone': '물 위로 솟은 종탑 끝.'})
objs.append({'type': 'clue', 'id': 'ce_lift', 'x': 162, 'y': 216, 'name': '낡은 승강기', 'flag': 'ce_look_lift',
             'text': '나무 틀과 도르래, 끊어진 사슬. 위에서 누군가 내려 줘야 움직일 것 같다.', 'textDone': '위에서 내려 줘야 움직이는 승강기.'})
objs.append({'type': 'sign', 'x': 3, 'y': 207, 'text': '길이 무너져 있다. 서쪽 들판 중앙으로는 아직 갈 수 없다.'})
rect(0, 200, 2, 222, '#')
rect(176, 20, W, 31, '.'); rect(W - 1, 20, W, 31, '#')
objs.append({'type': 'sign', 'x': 186, 'y': 25, 'text': '부서진 이정표. 「철혈의 가도 →」\n길 끝이 무너진 성벽 잔해로 막혀 있다.'})
objs.append({'type': 'sign', 'x': 186, 'y': 130, 'text': '돌무더기로 막힌 좁은 샛길. 누군가 일부러 막아 둔 것 같다.'})
objs.append({'type': 'hint', 'id': 'ce_h_palm', 'x': 31, 'y': 121, 'r': 3, 'text': '거인의 손바닥 위로 올라갈 수 있다'})

# 몹 무리: 설계도 자리 → 지금 1장 몹 4종을 돌려 씀
MOBS = ['c1_thread_scarecrow', 'c1_shear_tailor', 'c1_spool_spider', 'c1_quilted_boar']
M = json.load(open(os.path.join(REPO, 'docs_maps/ch1/ch1_map.json')))
gi = 0
for mk in M['markers']:
    if mk['zone'] != 'field_e' or mk['type'] != 'mob': continue
    x, y = L(mk['x'], mk['y']); n = 3 if '큰' in mk['name'] else 2 if '보통' in mk['name'] else 1
    if 222 <= y and 60 <= x <= 92: continue      # 정문 앞 첫 걸음엔 몹 없음
    for k in range(n):
        for _ in range(20):
            sx, sy = x + rnd.uniform(-3, 3), y + rnd.uniform(-3, 3)
            if 0 < sx < W and 14 < sy < 246 and grid[int(sy)][int(sx)] == '.': break
        else: continue
        objs.append({'type': 'spawn', 'mob': MOBS[(gi + k) % 4], 'x': round(sx), 'y': round(sy), 'respawn': 30})
    if n == 3:   # 큰 무리: 맨 뒤 1마리 = 바늘 사수 (그록 03, 4번방 10-26 「설계도 자리」)
        last = [o for o in objs if o['type'] == 'spawn' and abs(o['x'] - x) <= 4 and abs(o['y'] - y) <= 4]
        if last: last[-1]['mob'] = 'c1_needle_marksman'
    gi += 1
for mk in M['markers']:   # 들판 챔피언 자리 = 철장 간수 (그록 04, 들판 정예 후보)
    if mk['zone'] == 'field_e' and mk['type'] == 'elite': ex, ey = L(mk['x'], mk['y']); objs.append({'type': 'spawn', 'mob': 'c1_iron_warden', 'x': ex, 'y': ey, 'respawn': 60})

prol = json.load(open(os.path.join(T128, 'maps/prologue_grave.json')))
bd = dict(prol['hd']['backdrop']); bd['x'] = 60; bd['clipY'] = 12.6; bd.pop('front', None)   # 앞 띠(펠트 마을 지붕)는 빼기: 여긴 펠트 북쪽

mp = {
    'id': 'ch1_field_e', 'type': 'field', 'area': 1, 'region': 'felt', 'mapPos': [0, 0],
    'name': '잿빛 들판 — 동쪽', 'title': {'kicker': '1장 · 펠트', 'name': '잿빛 들판', 'sub': '쓰러진 거인과 검은 호수, 가도로 가는 들머리'},
    'bgm': 'area01_forest', 'battleBgm': json.load(open(os.path.join(T128, 'maps/field_felt.json'))).get('battleBgm'), 'tileset': 'field', 'tile': 16, 'grade': 'ash', 'fog': .22, 'ash': 1, 'wind': [5, 1],
    'w': W, 'h': H,
    'legend': {'.': 'dirt', '#': 'cliff', '~': {'ground': 'dirt', 'solid': True}, 'K': {'ground': 'dirt', 'solid': True}, 'X': {'ground': 'dirt', 'solid': True},
               'T': {'ground': 'dirt', 'deco': 'tree'}, 'R': {'ground': 'dirt', 'deco': 'boulder'}, 's': {'ground': 'dirt', 'deco': 'stump', 'solid': False}},
    'solid': ['#', '~', 'K', 'X', 'T', 'R'],
    'ground': [''.join(r) for r in grid],
    'objects': objs,
    'camZones': [{'x0': 0, 'y0': 12, 'x1': W, 'y1': 34, 'zoom': 0.8, 'look': -7.5, 'f': 8}],   # 북쪽 끝에선 위를 올려다봄 (무덤가와 같은 값) → 낭떠러지 너머 왕성
    'spawns': {'default': [75.5, 243.5, 'up'], 'felt': [75.5, 243.5, 'up']},
    'hd': {'D': 1, 'ground': f'{OUT}/ground.webp', 'props': under + props, 'backdrop': bd, 'grade': 'ash', 'decoArt': {k: felt_deco[k] for k in ('T', 'R', 's') if k in felt_deco}, 'fx': {},   # 마른 나무·돌무더기·그루터기 = 펠트와 같은 그림
           # 모닥불 2곳 (거인 손바닥 30,115 / 가도 들머리 120,80): 불·연기·깜빡이는 빛은 코드 (효과 담당 10-25)
           'fires': [[30.5, 115.4, 1.1], [120.5, 80.4, 1.0]], 'smoke': [[30.5, 115.0, 1.0], [120.5, 80.0, 0.9]], 'flick': [[30.5, 115.4, 48, '#ff8a3a', 1], [120.5, 80.4, 44, '#ff8a3a', 1]]},
    'note': '1장 동쪽 들판 (build_ch1_east.py 가 만든다, 고칠 땐 빌더를 고치고 다시 돌린다). 설계도 field_e = 전체 440,70.',
}
# 코드 효과 (효과 담당 10-25, world.js scenefx): 검은 호수에 비친 왕성 + 잔물결 + 물가 반짝임 / 종탑 물결·먼 종 / 북쪽 낭떠러지 안개 + 모닥불 쉼터 그림
for o in mp['objects']:
    if o['type'] == 'waystone' and o['id'] in ('ws_giant_palm', 'ws_road_head'): o['art'] = 'camp'
mp['objects'] += [{'type': 'scenefx', 'kind': 'lakeart', 'x': 84, 'y': 34, 'w': 85, 'h': 50, 'img': 'assets/world/ch1_east/black_lake.webp', 'cw': .5, 'ch': .6},
                  {'type': 'scenefx', 'kind': 'bell', 'x': 128.5, 'y': 61.7, 'w': 1, 'h': 1, 'r': 3, 'per': 20},
                  {'type': 'scenefx', 'kind': 'mistband', 'x': 0, 'y': 9, 'w': 190, 'h': 9, 'a': 1, 'sp': 7}]
json.dump(mp, open(os.path.join(T128, 'maps/ch1_field_e.json'), 'w'), ensure_ascii=False, indent=1)
print('cells', _dbg, 'ok', W, H, 'mobs', sum(1 for o in objs if o['type'] == 'spawn'), 'props', len(props), 'under', len(under))
