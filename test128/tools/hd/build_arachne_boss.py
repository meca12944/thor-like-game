"""1장 보스방 「실타래의 베틀방」 (4번방 10-26, 팀장: 조립표 2절 베틀방 120×65 · 그록 고치실 타일 + 어둡게 · 17d 보스방 뒷문 · 19d 빈 고치).
Replaces the old 28×20 「재단사의 방」 under the same map id `arachne_boss` (the 폐공방 boss door, quest targets and scene keys keep working;
the id moves to ch1_ws_boss when the story room's new 4-floor workshop lands).
- 싸움 원: 지름 40 타일 (rx 20, ry 16 — top-down, 화면에서 둥글게), 가운데 지름 16은 비움. 북쪽 들어간 자리 = 베틀·고치 왕좌(아라크네 시작),
  남쪽 = 폐공방에서 들어오는 계단, 동쪽 복도 끝 = 17d 뒷문 → 무명 무덤가 (설계도 지름길①, 보스를 쓰러뜨려야 열림: stairs_down 은 보스가 살아 있으면 막힘).
- 기둥 5개: 원 가운데에서 반지름 13 타일 고리, 2 타일 굵기 → 필살 「천 갈래 붉은 실」 숨을 곳, 2페이즈 붉은 실은 기둥 사이에 쳐짐.
- 고치 8개(hd.phase2.cocoons) = 「고치 비」가 떨어지는 천장 자리 (world_mobs.js ARA.ceil 이 지도에서 읽음).
- 바닥 = 그록 B2 고치실 16px 타일 (바닥 8×8 무늬, 벽면 3줄) × 0.8 어둡게, 원 가장자리는 픽셀 단위로 둥글게.
python3 test128/tools/hd/build_arachne_boss.py   -> maps/arachne_boss.json, assets/world/arachne/{arachne_boss_ground.webp, d_*}"""
import os, json, math
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..'); REPO = os.path.join(ROOT, '..')
OUT = os.path.join(ROOT, 'assets', 'world', 'arachne')
GROK = os.path.join(REPO, 'handoff', 'grok_in', '16-22_소품_인물_주인공동작_20261025')
TILES = os.path.join(GROK, '18_workshop_tiles', 'B2_cocoon', 'tiles16')
T, W, H = 16, 120, 65
CX, CY, RX, RY = 60, 33, 20, 16           # 싸움 원 (타일)
DARK = .8                                  # 조립표: 고치실 타일 + 어둡게

def in_ring(x, y): return ((x - CX) / RX) ** 2 + ((y - CY) / RY) ** 2 <= 1
g = [['#'] * W for _ in range(H)]
def room(x0, y0, x1, y1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1): g[y][x] = '.'
for y in range(H):
    for x in range(W):
        if in_ring(x + .5, y + .5): g[y][x] = '.'
room(52, 11, 68, 18)       # 북쪽: 베틀·왕좌 자리 (아라크네 시작)
room(58, 48, 62, 53)       # 남쪽: 폐공방 계단에서 들어오는 짧은 길 (싸움은 원 안에서 시작)
room(79, 31, 117, 35)      # 동쪽: 뒷문 복도
g[53][60] = 'U'; g[33][117] = 'D'
PILLARS = []
for deg in (-140, -40, 20, 105, 160):   # 기둥 5: 위 둘 · 옆 둘 · 아래 하나(입구 → 보스 일직선에서 비켜 둠: 들어오자마자 기둥에 막히지 않게)
    a = math.radians(deg); px, py = round(CX + 13 * math.cos(a) - .5), round(CY + 13 * .8 * math.sin(a) - .5)
    g[py][px] = 'p'; g[py][px + 1] = 'q'; PILLARS.append((px + 1, py + 1))   # 2 타일 굵기 (오른쪽 칸은 보이지 않는 벽)
rows = [''.join(r) for r in g]

# ---------------- 바닥 그림 (D=1, 그록 16px 타일) ----------------
def tile(n): return np.asarray(Image.open(os.path.join(TILES, n + '.png')).convert('RGBA'), float)
FL = [[tile(f'floor_r{r}c{c}') for c in range(8)] for r in range(8)]
WF = [[tile(f'wall_r{r}c{c}') for c in range(5)] for r in range(3)]
CAP = tile('cap_fill'); SHD = tile('floor_shadow_under_wall_overlay')
GW, GH = W * T, H * T
yy, xx = np.mgrid[0:GH, 0:GW].astype(float)
ring = (((xx + .5) / T - CX) / RX) ** 2 + (((yy + .5) / T - CY) / RY) ** 2 <= 1
tg = np.array([[c for c in r] for r in rows]); tfloor = tg != '#'
tq = (tg == 'q') | (tg == 'p'); tfloor &= ~(tg == 'q')
rectf = np.zeros((GH, GW), bool)
for (x0, y0, x1, y1) in ((52, 11, 68, 18), (58, 48, 62, 53), (79, 31, 117, 35)): rectf[y0 * T:(y1 + 1) * T, x0 * T:(x1 + 1) * T] = True
floor = ring | rectf
img = np.zeros((GH, GW, 3))
fl_big = np.zeros((8 * T, 8 * T, 3))
for r in range(8):
    for c in range(8): fl_big[r * T:(r + 1) * T, c * T:(c + 1) * T] = FL[r][c][..., :3]
img[:] = fl_big[(yy % (8 * T)).astype(int), (xx % (8 * T)).astype(int)]
cap = CAP[..., :3][(yy % T).astype(int), (xx % T).astype(int)]
wf_big = np.zeros((3 * T, 5 * T, 3))
for r in range(3):
    for c in range(5): wf_big[r * T:(r + 1) * T, c * T:(c + 1) * T] = WF[r][c][..., :3]
# 벽면: 바닥 바로 위 3 타일(48px) — 열마다 아래로 몇 px 가면 바닥인지
dist = np.full((GH, GW), 999)
below = np.zeros(GW, int) + 999
for y in range(GH - 1, -1, -1):
    below = np.where(floor[y], 0, below + 1); dist[y] = below
face = (~floor) & (dist >= 1) & (dist <= 3 * T)
fr = (3 * T - dist).clip(0, 3 * T - 1)
wall_img = wf_big[fr.astype(int), (xx % (5 * T)).astype(int)]
img = np.where(floor[..., None], img, np.where(face[..., None], wall_img, cap))
# 벽 아래 그림자 · 원 가장자리 어둡게(바깥으로 갈수록) · 전체 어둡게
up = np.full((GH, GW), 999); above = np.zeros(GW, int) + 999
for y in range(GH):
    above = np.where(~floor[y], 0, above + 1); up[y] = above
sh = floor & (up <= 10); img[sh] *= (.55 + .045 * up[sh])[:, None]
rr = np.sqrt((((xx + .5) / T - CX) / RX) ** 2 + (((yy + .5) / T - CY) / RY) ** 2)
img *= np.where(ring, 1 - .18 * np.clip((rr - .75) / .25, 0, 1), 1)[..., None]
from scipy import ndimage
edge_in = floor & ~ndimage.binary_erosion(floor, iterations=6)                       # 바닥 가장자리 6px: 안쪽으로 그림자
dd_in = ndimage.distance_transform_edt(floor); img[edge_in] *= (.5 + .5 * (dd_in[edge_in] / 6))[:, None]
ink = ~floor & ~face & ndimage.binary_dilation(floor, iterations=2); img[ink] = [14, 10, 8]   # 벽 윗면 테두리 (먹선)
img *= DARK
Image.fromarray(img.clip(0, 255).astype(np.uint8)).save(os.path.join(OUT, 'arachne_boss_ground.webp'), quality=88)

# ---------------- 물체 ----------------
def scaled(src, dst, k, dark=1.0):
    im = Image.open(src).convert('RGBA'); im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    if dark != 1.0: a = np.asarray(im, float); a[..., :3] *= dark; im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    im.save(os.path.join(OUT, dst)); return im.size
pw, ph = scaled(os.path.join(OUT, 'd_thread_pillar.png'), 'd_thread_pillar_big.png', 2)          # 기둥 2배 (2 타일 굵기, D3 그림)
bw, bh = scaled(os.path.join(GROK, '17_shortcuts', '17d_boss_backdoor_256x320_4x_master.png'), 'd_boss_backdoor.png', .75, .8)   # 4x → D3, 바깥 기준 밝음 → ×0.8
cw, chh = scaled(os.path.join(GROK, '19_story_props', '19d_empty_cocoon_256x192_4x_master.png'), 'd_empty_cocoon.png', .75)
PJ = {'d_boss_loom': (153, 279), 'd_cocoon_throne': (100, 224), 'd_cocoon_l': (42, 93), 'd_cocoon_m': (15, 103), 'd_web_sheet': (41, 106), 'd_bones': (36, 41),
      'd_boss_backdoor': (bw // 2, bh - 3), 'd_empty_cocoon': (cw // 2, chh - 6)}
props = []
def P(pid, x, y, solid=None):
    ax, ay = PJ[pid]; o = {'id': f'{pid}_{len(props)}', 'img': f'assets/world/arachne/{pid}.png', 'x': x, 'y': y, 'ax': ax, 'ay': ay, 'D': 3, 'fade': 1 if pid in ('d_boss_loom', 'd_cocoon_throne', 'd_boss_backdoor') else 0, 'shadow': 1}
    if solid: o['solid'] = solid
    props.append(o)
P('d_boss_loom', 60, 14.2); P('d_cocoon_throne', 60, 17.4)
for x in (54, 66): P('d_web_sheet', x, 12.6)
for x, y in ((53.5, 17.5), (66.5, 17.5)): P('d_cocoon_l', x, y)
P('d_boss_backdoor', 117.5, 33.2)
for x, y in ((44, 24), (77, 41), (47, 43)): P('d_empty_cocoon', x, y)                          # 19d 빈 고치: 원 가장자리 (붉은 목도리는 B2 아이템)
for x, y in ((50, 30), (70, 37), (56, 44), (66, 25), (82, 33), (100, 34)): P('d_bones', x, y)
for x, y in ((44, 24), (77, 41), (47, 43)):
    for dx in (-1, 0):
        if rows[int(y) - 1][int(x) + dx] == '.': g[int(y) - 1][int(x) + dx] = '#'                  # 빈 고치 밑은 막힘
rows = [''.join(r) for r in g]
COCOONS = [[52, 24], [68, 24], [46, 33], [74, 33], [52, 42], [68, 42], [60, 27], [60, 39]]       # 천장 고치 8 = 고치 비 자리 (지름 16 가운데 둘레·바깥 고리)
LIGHTS = [[60, 16, 120, '#b080ff', .6], [60, 33, 200, '#c8d8ff', .3], [60, 50, 60, '#ffb070', .45], [114, 33, 60, '#c8d8ff', .4]]
threads = [[p[0], p[1] - .3, q[0], q[1] - .3, 1.5] for i, p in enumerate(PILLARS) for q in PILLARS[i + 1:] if math.hypot(p[0] - q[0], p[1] - q[1]) < 18]
threads += [[p[0], p[1] - .3, CX + (p[0] - CX) * 1.5, CY + (p[1] - CY) * 1.5, 1] for p in PILLARS]  # 기둥 → 벽

old = json.load(open(os.path.join(ROOT, 'maps', 'arachne_boss.json')))
b = {'id': 'arachne_boss', 'type': 'boss', 'region': 'ch1', 'area': 1, 'mapPos': [0, 0], 'name': '실타래의 베틀방',
     'title': {'kicker': 'BOSS', 'name': '실타래의 재단사 아라크네', 'sub': '실타래의 베틀방'}, 'bgm': 'battle_boss', 'bgm2': 'battle_boss_phase2', 'dark': .4,
     'tileset': 'dungeon', 'tile': T, 'w': W, 'h': H,
     'legend': {'#': 'wall', '.': 'floor', 'U': {'ground': 'floor', 'obj': 'stairs_up'}, 'D': {'ground': 'floor', 'obj': 'stairs_down'},
                'p': {'ground': 'floor', 'deco': 'pillar', 'solid': True}, 'q': {'ground': 'floor', 'solid': True}},
     'solid': ['#'], 'ground': rows, 'spawns': {'default': [60.5, 48.5, 'up'], 'back': [114.5, 33.5, 'left']},
     'links': {'stairs_up': {'to': 'arachne', 'spawn': 'boss'}, 'stairs_down': {'to': 'prologue_grave', 'spawn': 'resume'}},   # 설계도 지름길① 베틀방 뒷문 → 무명 무덤가 (스토리 10-26; 남쪽 들판이 생기면 spawn 'loom_back')
     'boss': dict(old['boss'], x=60.5, y=21.5, exitMsg='동쪽 뒷문이 열렸다 — 뒷문은 무명 무덤가로, 빛의 문은 펠트로 이어진다'),
     'arena': {'cx': CX, 'cy': CY, 'rx': RX, 'ry': RY},
     'objects': [],
     'hd': {'D': 1, 'ground': 'assets/world/arachne/arachne_boss_ground.webp', 'props': props,
            'decoArt': {'p': [{'img': 'assets/world/arachne/d_thread_pillar_big.png', 'ax': pw // 2 - 24, 'ay': ph - 2, 'flip': False}]},
            'phase2': {'threads': threads, 'cocoons': COCOONS}, 'lights': LIGHTS},
     'note': 'GENERATED by tools/hd/build_arachne_boss.py — edit the script'}
open(os.path.join(ROOT, 'maps', 'arachne_boss.json'), 'w').write(json.dumps(b, ensure_ascii=False, indent=1) + '\n')
print('ok arachne_boss', W, 'x', H, 'pillars', PILLARS, 'props', len(props))
print('\n'.join(r[30:92] for r in rows[8:64]))
