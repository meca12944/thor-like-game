"""Prologue awakening map 「무명 무덤가」 (prologue_grave, 64x64, ch1Origin [270,394]) — owner 10-25 B.
v2 (owner 10-25 C 「주인공은 펠트 바깥에서 들어오는 설정」): the hero wakes OUTSIDE Felt. North of the crest the land drops away and the hd.backdrop
shows Felt's colossal wall seen from outside with the tall ruined castle soaring behind it (same castle as the title / arrival CG);
it grows as the hero walks the outer road east (looking up), and fills the crest vista. South = ash dunes, west = petrified forest,
centre = nameless graves (12x8, the hero wakes in the lane between them), east = the outer road (rows 13..17) to the exit (fade -> Felt west gate, felt spawn 'field').
Tutorial route ~120 tiles: wake (30,26) -> backpack (42,34) [interact] -> cold campfire (16,16) [waystone] -> crest vista (31,8)
-> dry brambles (46..47, 4..8) [attack, breakable flag pg_bramble] -> ground crack (x 53) [dash/jump, soft pit] -> sign (57,4) -> exit (x 63).
Art: everything code-drawn here (no PixelLab): ground painted with numpy, small sprites (graves, backpack, brambles, lantern) drawn with PIL,
felt props reused (dead trees tinted to stone, debris, firepit, banners, sign); the far castle picture is the illustrator's hand-drawn castle_far (castle_far.py). Light / fog / ash / smoke / crows /
footprints / darkness are drawn by world.js at runtime (map keys: dark, steps, hd.fx, hd.smoke).
Rules: no spirits, no gore, no bodies/bones/blood; the backpack holds belongings only; no children, no Linette.
Usage: python3 build_prologue_grave.py -> maps/prologue_grave.json + assets/world/prologue/*"""
import json, os, sys, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import props
from build import bfs
ROOT = props.ROOT; T = 16; W = H = 64; HD = 1.5; G = int(T * HD); OX, OY = 270, 394
PA = 'assets/world/prologue/'; FA = 'assets/world/felt/'
def rel(p): return os.path.join(ROOT, p)
rnd = random.Random(7)
WAKE = (30, 22); PACK = (42, 30); FIRE = (16, 19); CREST = (31, 14); BR_X = (46, 47); CRACK_X = 53; SIGN = (57, 13); EXIT_X = 63
LIP = 12.75; RY = 13                              # v2 (owner 10-25 C): rows < 13 = the drop beyond the crest, where the far wall + castle backdrop shows; the outer road runs on rows 13..17
# ---------------- grid ----------------
g = np.full((H, W), '.', dtype='<U1')
g[:RY, :] = '#'                                  # beyond the crest: the drop to the plain (the backdrop: Felt's colossal wall and the castle behind it)
g[60:, :] = '#'                                  # south: ash dunes (the hero comes from outside, there is no wall behind him any more)
g[:, :4] = '#'                                   # deep petrified forest
g[RY + 5:, 51:] = '#'                            # east slope (rocky drop)
g[RY + 5:RY + 9, 44:51] = '#'                    # ledge under the road: the crest is the only way east
g[RY:RY + 5, 44:] = '.'                          # the outer road along the crest, toward Felt's west gate
for y in range(RY, 60):                           # ragged edges
    for x in range(4, 8):
        if rnd.random() < .35 - (x - 4) * .08: g[y, x] = '#'
for x in range(4, 44):
    if rnd.random() < .3: g[RY, x] = '#'
for x in range(8, 51):
    if rnd.random() < .35: g[59, x] = '#'
SOL = {'#', 'H'}
def solid_at(x, y): return g[y, x] in SOL
props_ = []; objs = []
def art(path, **kw):
    im = Image.open(rel(path)); ax, ay = props.anchor(im); return dict({'img': path, 'ax': ax, 'ay': ay}, **kw)
def sp(a, x, y, D=2.5, solid=True, foot=None, **kw):
    q = dict({'id': f'{os.path.basename(a["img"])[:-4]}_{len(props_)}', 'img': a['img'], 'x': round(x, 2), 'y': round(y, 2), 'ax': a['ax'], 'ay': a['ay'], 'D': D, 'fade': 0, 'shadow': 1}, **kw)
    props_.append(q)
    if solid:
        for (cx, cy) in (foot or [(int(x), int(y - .6))]):
            if 0 <= cx < W and 0 <= cy < H: g[cy, cx] = 'H'
    return q
# ---------------- code-drawn sprites (4x supersampled, ink outline, flat cel + soft wash) ----------------
INK = (34, 28, 26, 255)
def canvas(w, h): return Image.new('RGBA', (w * 4, h * 4), (0, 0, 0, 0))
def finish(im, name, w, h):
    im = im.resize((w, h), Image.LANCZOS); a = np.array(im).astype(np.float32)
    a[..., 3] = np.where(a[..., 3] < 60, 0, 255); im = Image.fromarray(a.astype(np.uint8)); p = PA + name + '.png'; im.save(rel(p), optimize=True); return art(p)
def poly(d, pts, fill, s=4, ink=True, wdt=7):
    P = [(x * s, y * s) for x, y in pts]; d.polygon(P, fill=fill)
    if ink: d.line(P + [P[0]], fill=INK, width=wdt, joint='curve')
def grave_stone(i):
    r = random.Random(100 + i); w, h = 40, 52; im = canvas(w, h); d = ImageDraw.Draw(im)
    d.ellipse((2 * 4, 40 * 4, 38 * 4, 51 * 4), fill=(70, 62, 54, 255))                     # earth mound
    d.ellipse((6 * 4, 41 * 4, 34 * 4, 48 * 4), fill=(88, 78, 66, 255))
    tw = r.randint(14, 20); tl = 20 - tw // 2; top = r.randint(6, 14); tilt = r.uniform(-3, 3)
    pts = [(tl + tilt, top + 4), (tl + tw / 2 + tilt, top - 1), (tl + tw + tilt, top + 4), (tl + tw, 44), (tl, 44)]
    if i % 3 == 2: pts = [(tl + tilt, top), (tl + tw + tilt, top + 2), (tl + tw, 44), (tl, 44)]
    poly(d, pts, (128, 124, 116, 255))
    d.polygon([((tl + tw * .62) * 4, (top + 3) * 4), ((tl + tw + tilt) * 4, (top + 4) * 4), ((tl + tw) * 4, 44 * 4), ((tl + tw * .62) * 4, 44 * 4)], fill=(98, 94, 90, 255))
    for _ in range(2):                                                                         # cracks + blank face (nameless)
        x0 = tl + r.uniform(3, tw - 3); y0 = top + r.uniform(6, 14)
        d.line([(x0 * 4, y0 * 4), ((x0 + r.uniform(-3, 3)) * 4, (y0 + r.uniform(4, 9)) * 4)], fill=(60, 56, 52, 255), width=4)
    d.ellipse(((tl - 2) * 4, 42 * 4, (tl + tw + 2) * 4, 46 * 4), fill=(52, 46, 40, 255))
    return finish(im, f'pg_grave_stone_{i}', w, h)
def grave_stake(i):
    r = random.Random(200 + i); w, h = 34, 56; im = canvas(w, h); d = ImageDraw.Draw(im)
    d.ellipse((2 * 4, 44 * 4, 32 * 4, 55 * 4), fill=(70, 62, 54, 255)); d.ellipse((6 * 4, 45 * 4, 28 * 4, 51 * 4), fill=(86, 76, 64, 255))
    tilt = r.uniform(-4, 4); x = 16
    poly(d, [(x - 2.5 + tilt, 6), (x + 2.5 + tilt, 5), (x + 3, 48), (x - 3, 48)], (92, 74, 56, 255))
    if i % 2 == 0: poly(d, [(x - 9 + tilt * .8, 15), (x + 9 + tilt * .8, 14), (x + 9 + tilt * .8, 18), (x - 9 + tilt * .8, 19)], (100, 82, 62, 255))
    cl = (118, 104, 90, 255) if i % 3 else (96, 70, 64, 255)                                   # a faded rag tied on
    poly(d, [(x + 2 + tilt, 20), (x + 11 + tilt, 23), (x + 8 + tilt, 30), (x + 12 + tilt, 36), (x + 3 + tilt, 30)], cl, wdt=5)
    return finish(im, f'pg_grave_stake_{i}', w, h)
def grave_sword():
    w, h = 30, 58; im = canvas(w, h); d = ImageDraw.Draw(im)
    d.ellipse((2 * 4, 46 * 4, 28 * 4, 57 * 4), fill=(70, 62, 54, 255)); d.ellipse((6 * 4, 47 * 4, 24 * 4, 53 * 4), fill=(86, 76, 64, 255))
    poly(d, [(13.5, 16), (16.5, 16), (16.2, 50), (13.8, 50)], (150, 152, 156, 255), wdt=5)       # blade, tip buried
    d.line([(15 * 4, 17 * 4), (15 * 4, 49 * 4)], fill=(112, 114, 120, 255), width=3)
    poly(d, [(6, 13), (24, 13), (24, 16.5), (6, 16.5)], (88, 70, 50, 255), wdt=5)                # guard
    poly(d, [(13.5, 4), (16.5, 4), (16.5, 13), (13.5, 13)], (70, 52, 40, 255), wdt=5)            # wrapped grip
    for yy in (6, 8.5, 11): d.line([(13.5 * 4, yy * 4), (16.5 * 4, (yy + 1) * 4)], fill=(44, 34, 28, 255), width=3)
    d.ellipse((12 * 4, 1 * 4, 18 * 4, 5 * 4), fill=(96, 84, 70, 255), outline=INK, width=5)
    return finish(im, 'pg_grave_sword', w, h)
def backpack():
    w, h = 46, 40; im = canvas(w, h); d = ImageDraw.Draw(im)
    d.ellipse((3 * 4, 30 * 4, 43 * 4, 39 * 4), fill=(40, 34, 30, 120))
    poly(d, [(10, 12), (34, 10), (37, 34), (8, 35)], (104, 76, 50, 255))                        # leather body
    poly(d, [(9, 11), (35, 9), (34, 20), (10, 21)], (122, 90, 60, 255))                         # flap
    d.line([(21 * 4, 20 * 4), (21 * 4, 26 * 4)], fill=INK, width=6); d.rectangle((19 * 4, 24 * 4, 23 * 4, 27 * 4), fill=(150, 130, 90, 255), outline=INK, width=4)
    poly(d, [(6, 4), (38, 3), (39, 10), (5, 11)], (128, 120, 104, 255))                         # rolled grey bedroll on top
    for xx in (14, 22, 30): d.line([(xx * 4, 3 * 4), (xx * 4 + 4, 11 * 4)], fill=(80, 74, 66, 255), width=4)
    d.line([(12 * 4, 12 * 4), (10 * 4, 34 * 4)], fill=(70, 50, 34, 255), width=5); d.line([(31 * 4, 11 * 4), (34 * 4, 33 * 4)], fill=(70, 50, 34, 255), width=5)
    poly(d, [(36, 26), (44, 25), (44, 33), (37, 34)], (84, 80, 72, 255), wdt=5)                  # a small pouch at the side
    return finish(im, 'pg_backpack', w, h)
def lantern():
    w, h = 20, 30; im = canvas(w, h); d = ImageDraw.Draw(im)
    d.ellipse((2 * 4, 24 * 4, 18 * 4, 29 * 4), fill=(40, 34, 30, 120))
    d.arc((5 * 4, 0, 15 * 4, 9 * 4), 180, 360, fill=INK, width=6)
    poly(d, [(5, 5), (15, 5), (16, 9), (4, 9)], (72, 66, 60, 255), wdt=5)
    poly(d, [(5, 9), (15, 9), (15, 22), (5, 22)], (150, 170, 176, 255), wdt=5)                   # cold glass (unlit)
    d.line([(10 * 4, 9 * 4), (10 * 4, 22 * 4)], fill=INK, width=4)
    poly(d, [(4, 22), (16, 22), (17, 26), (3, 26)], (72, 66, 60, 255), wdt=5)
    return finish(im, 'pg_lantern', w, h)
def bramble(i):
    r = random.Random(300 + i); w, h = 44, 40; im = canvas(w, h); d = ImageDraw.Draw(im)
    d.ellipse((2 * 4, 30 * 4, 42 * 4, 39 * 4), fill=(36, 30, 26, 130))
    for k in range(26):                                                                        # dry thorny canes, ink strokes
        x0 = r.uniform(8, 36); y0 = 35; L = r.uniform(14, 30); a = math.radians(r.uniform(-160, -20))
        pts = [(x0, y0)]
        for s in range(5):
            a += r.uniform(-.5, .5); x0 += math.cos(a) * L / 5; y0 += math.sin(a) * L / 5; pts.append((x0, y0))
        col = r.choice([(78, 62, 46, 255), (96, 78, 56, 255), (60, 48, 38, 255), (112, 94, 70, 255)])
        d.line([(p[0] * 4, p[1] * 4) for p in pts], fill=INK, width=9, joint='curve')
        d.line([(p[0] * 4, p[1] * 4) for p in pts], fill=col, width=5, joint='curve')
        for p in pts[1:-1]:
            if r.random() < .7:
                b = a + r.choice([-1, 1]) * 1.1; d.line([(p[0] * 4, p[1] * 4), ((p[0] + math.cos(b) * 2.6) * 4, (p[1] + math.sin(b) * 2.6) * 4)], fill=INK, width=4)
    return finish(im, f'pg_bramble_{i}', w, h)
def petrify(src, name, seed):
    if not os.path.exists(rel(src)): return art(PA + name + '.png')   # the old Felt source was archived (map-a7): reuse the baked copy
    im = Image.open(rel(src)).convert('RGBA'); a = np.array(im).astype(np.float32); r = np.random.RandomState(seed)
    l = (a[..., :3] * [.3, .59, .11]).sum(-1, keepdims=True); hh, ww = a.shape[:2]
    mott = ndimage.gaussian_filter(r.rand(hh, ww), 1.6)[..., None]; mott = (mott - mott.mean()) / (mott.std() + 1e-6)
    stone = np.clip(l * .82 + 34 + mott * 7, 0, 255) * np.array([.98, .99, 1.04])
    a[..., :3] = np.clip(stone, 0, 255); p = PA + name + '.png'; Image.fromarray(a.astype(np.uint8)).save(rel(p), optimize=True); return art(p)
def tint(src, name, sat=.45, gain=.78):
    if not os.path.exists(rel(src)): return art(PA + name + '.png')
    im = Image.open(rel(src)).convert('RGBA'); a = props._grade(np.array(im).astype(np.float32), sat, (1.0, .97, .93), gain)
    p = PA + name + '.png'; Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(rel(p), optimize=True); return art(p)
stones = [grave_stone(i) for i in range(3)]; stakes = [grave_stake(i) for i in range(3)]; gsword = grave_sword()
packA = backpack(); lantA = lantern(); brA = [bramble(i) for i in range(2)]
petri = [petrify(FA + f'g4_deadtree_{i}.png', f'pg_petri_{i}', i) for i in range(4)]
banner = [tint(FA + f'f3_banner_{i}.png', f'pg_banner_{i}') for i in range(2)]
fireA = art(FA + 'g4_firepit.png'); signA = art(FA + 'sign_post.png')
deadA = art(FA + 'g4_deadtree_1.png'); debris = [art(FA + f'g4_debris_{i}.png') for i in range(4)]
rubA = art(FA + 'rubble.png'); stlowA = art(FA + 'stone_low.png'); stumpA = art(FA + 'g2_burnt_stump_a.png')
# ---------------- props ----------------
back = []                                                                                         # (the far wall + castle are the hd.backdrop picture now)
for x in range(8, 52, 3):                                                                        # south: the ash dunes, dead wood and stones half sunk in ash
    y = 59.4 + rnd.random() * 1.0
    if rnd.random() < .45: sp(rnd.choice(petri), x + rnd.random(), y, D=rnd.uniform(1.9, 2.3), flip=rnd.random() < .5, fade=1)
    else: sp(rnd.choice([rubA, stlowA, stumpA] + debris[:2]), x + rnd.random(), y, D=2.3, flip=rnd.random() < .5)
for y in range(RY + 1, 60, 2):                                                                        # petrified forest (west)
    for x in range(1, 10, 2):
        if rnd.random() < (.95 - (x - 1) * .09) and not (abs(x - FIRE[0]) < 5 and abs(y - FIRE[1]) < 4):
            xx, yy = x + rnd.random() * 1.2, y + rnd.random() * 1.4
            if yy < 59: sp(rnd.choice(petri), xx, yy, D=rnd.uniform(1.8, 2.3), flip=rnd.random() < .5, sway=0, fade=1)
for (x, y) in [(13, 40), (21, 47), (46, 44), (47, 24), (12, 27), (38, 49)]:                     # a few loose petrified trunks inside
    sp(rnd.choice(petri), x + .5, y + .9, D=2.1, flip=rnd.random() < .5, fade=1)
sp(deadA, PACK[0] + 1.5, PACK[1] - .1, D=2.0, foot=[(43, PACK[1] - 1)], flip=True, sway=.3, fade=1)       # the dead tree the backpack leans on
# nameless graves: 12x8 block x 24..35, y 17..24 (rows 17,19,21,23 + offsets); a lane down the middle (x 29..30) stays open
gs = []
for y in (17, 19, 21, 23):
    for x in (24, 26, 28, 32, 34):
        if (x, y) in ((28, 23),): continue
        gs.append((x + rnd.choice([0, 1]) * (x != 28), y))
for k, (x, y) in enumerate(gs):
    kind = k % 5
    a = stones[k % 3] if kind in (0, 2, 4) else stakes[k % 3]
    if k in (6, 13): a = gsword
    sp(a, x + .5, y + .95, D=2.3, flip=rnd.random() < .5)
for (x, y) in [(14, 30), (16, 34), (18, 38), (20, 31), (12, 43), (44, 26), (47, 33), (45, 23), (21, 44), (40, 44), (36, 38), (25, 35)]:  # older scattered graves
    sp(rnd.choice(stones + stakes), x + .5, y + .95, D=2.4, flip=rnd.random() < .5)
for (x, y, b) in [(23, 16, 0), (36, 18, 1), (36, 25, 0)]:                                       # torn banners on poles at the grave corners
    sp(banner[b], x + .5, y + .95, D=3.0, sway=1.0)
sp(fireA, FIRE[0] + .5, FIRE[1] + 1.0, D=2.3, solid=False, shadow=0)                            # the cold campfire (waystone object sits on it)
for (x, y) in [(13, 16), (19, 17), (14, 22), (19, 22)]: sp(stumpA, x + .5, y + .9, D=2.6)        # log seats / burnt stumps round the fire
sp(packA, PACK[0] + .55, PACK[1] + .95, D=2.4, solid=False, shadow=0)                            # belongings only
sp(lantA, PACK[0] - .1, PACK[1] + .9, D=2.4, solid=False, shadow=0, hideFlag='pg_backpack')
for y in range(RY, RY + 5):                                                                       # dry brambles: breakable (flag pg_bramble)
    for j, x in enumerate(BR_X):
        q = sp(brA[(x + y) % 2], x + .5 + rnd.uniform(-.15, .15), y + .95, D=2.2, solid=False, shadow=0, hideFlag='pg_bramble', flip=rnd.random() < .5)
        q['solid'] = [x, y, x, y]
sp(signA, SIGN[0] + .5, SIGN[1] + .95, D=2.6, solid=False)
for (x, y) in [(41, 15), (40, 18), (49, 18), (55, 18), (59, 18), (61, 12)]:                      # road edge stones
    if g[y, x] == '#' or y in (RY - 1, RY + 5): sp(rnd.choice([stlowA, rubA] + debris[:2]), x + .5, y + .9, D=2.6, solid=False)
for k in range(28):                                                                               # scatter on the open ash (keep the route clear)
    for _ in range(40):
        x, y = rnd.randint(10, 49), rnd.randint(RY + 6, 57)
        if g[y, x] != '.' or min(abs(x - a_) + abs(y - b_) for a_, b_ in (WAKE, PACK, FIRE)) < 5: continue
        if np.any(g[y - 1:y + 2, x - 1:x + 2] == 'H'): continue
        sp(rnd.choice(debris + [rubA, stlowA, stumpA]), x + .5, y + .9, D=2.6, flip=rnd.random() < .5); break
# ---------------- objects ----------------
KI = '{interact}'
objs = [
 {'type': 'clue', 'id': 'pg_hollow', 'x': WAKE[0], 'y': WAKE[1] + 1, 'name': '사람 모양으로 꺼진 잿더미', 'flag': 'pg_look_hollow',
  'text': '재가 사람 모양으로 꺼져 있다. 방금까지 내가 누워 있던 자리.\n가장자리가 단단히 굳었다. 한두 번 누운 자리가 아니다.', 'textDone': '내가 누워 있던 자리. 벌써 재가 다시 쌓이고 있다.'},
 {'type': 'clue', 'id': 'pg_sword_marker', 'x': gs[6][0], 'y': gs[6][1] + 1, 'name': '무덤에 꽂힌 장검', 'flag': 'pg_look_sword',
  'text': '무덤 표지 대신 칼이 꽂혀 있다. 손잡이 가죽을 감은 방식이 내 것과 같다.\n이름은 없다. 여기 무덤은 전부 이름이 없다.', 'textDone': '이름 없는 무덤. 칼만 꽂혀 있다.'},
 {'type': 'clue', 'id': 'pg_tally', 'x': 33, 'y': 25, 'name': '돌에 그은 줄', 'flag': 'pg_look_tally',
  'text': '돌마다 칼끝으로 그은 줄이 빼곡하다. 다섯 개씩 묶은 표식.\n어느 돌부터인가 줄이 끊겼다. …세는 걸 그만둔 거다.', 'textDone': '끊긴 줄. 더 긋지 않았다.'},
 {'type': 'clue', 'id': 'pg_backpack', 'x': PACK[0], 'y': PACK[1], 'name': '고사목 아래 가죽 배낭', 'flag': 'pg_backpack', 'loot': [['potion', 1]],
  'text': '마른 나무 밑동에 낡은 가죽 배낭이 기대 놓여 있다. 주인은 보이지 않는다.\n안에는 닳은 등불과 물약 한 병, 실이 다 풀린 바늘쌈.\n배낭 끈을 묶은 매듭이 내가 묶는 방식과 똑같다.\n등불을 들자, 심지에 푸른 불이 옮겨 붙는다.',
  'textDone': '빈 가죽 배낭. 끈의 매듭만 낯익다.'},
 {'type': 'waystone', 'id': 'ws_prologue_grave', 'x': FIRE[0], 'y': FIRE[1], 'name': '무덤가 모닥불(꺼짐)', 'art': 'hd'},
 {'type': 'clue', 'id': 'pg_footprints', 'x': 33, 'y': 15, 'name': '재 위의 발자국', 'flag': 'pg_look_steps',
  'text': '언덕 위로 난 발자국. 반쯤 재에 덮였다.\n내 신발과 크기가 같다.', 'textDone': '반쯤 덮인 발자국.'},
 {'type': 'vista', 'id': 'pg_vista_crest', 'x': CREST[0], 'y': CREST[1], 'r': 3.0, 'zoom': .6, 'dir': 270, 'pan': 10, 'hold': 1, 'tilt': {'z0': .6, 'z1': .9, 'pan': 12}, 'name': '잿빛 들판', 'sub': '저 성벽 너머, 펠트 — 그리고 왕성'},
 {'type': 'breakable', 'id': 'pg_bramble', 'x': BR_X[0], 'y': RY, 'w': len(BR_X), 'h': 5, 'flag': 'pg_bramble', 'name': '마른 가시덤불', 'text': '마른 가시덤불을 베어 길을 텄다'},
] + [{'type': 'pit', 'id': f'pg_crack_{y}', 'x': CRACK_X, 'y': y, 'soft': 1, 'text': '발밑이 꺼진다 — 뛰어넘자'} for y in range(RY, RY + 5)] + [
 {'type': 'sign', 'x': SIGN[0], 'y': SIGN[1], 'text': '기울어진 이정표.\n「펠트 서문 →」'},
 {'type': 'exit', 'x': EXIT_X, 'y': RY, 'w': 1, 'h': 5, 'to': 'felt', 'spawn': 'field', 'label': '→ 펠트 서문', 'setFlag': 'pg_left'},
 {'type': 'hint', 'id': 'pg_h_move', 'x': WAKE[0], 'y': WAKE[1], 'r': 3, 'text': '이동: WASD / 방향키'},
 {'type': 'hint', 'id': 'pg_h_pack', 'x': PACK[0], 'y': PACK[1], 'r': 3.5, 'text': '살펴보기·줍기: ' + KI, 'unless': 'pg_backpack'},
 {'type': 'hint', 'id': 'pg_h_fire', 'x': FIRE[0], 'y': FIRE[1] + 1, 'r': 3.5, 'text': '꺼진 모닥불 — ' + KI + ': 쉬기·저장 (쓰러지면 여기서 다시 시작)'},
 {'type': 'hint', 'id': 'pg_h_crest', 'x': 31, 'y': 17, 'r': 2.0, 'text': '언덕 위로 올라가 보자'},
 {'type': 'hint', 'id': 'pg_h_atk', 'x': 44, 'y': RY + 2, 'r': 2.6, 'text': '공격: {attack} — 마른 가시덤불을 베어 길을 연다', 'unless': 'pg_bramble'},
 {'type': 'hint', 'id': 'pg_h_dash', 'x': 51, 'y': RY + 2, 'r': 2.4, 'text': '점프 {dive} / 회피대시 {dash} — 땅 틈을 뛰어넘는다'},
]
spawns = {'default': [WAKE[0] + .5, WAKE[1] + .5, 'up'], 'wake': [WAKE[0] + .5, WAKE[1] + .5, 'up'], 'resume': [WAKE[0] + .5, WAKE[1] + .5, 'up'], 'from_felt': [61.5, RY + 2.5, 'left']}
for o in objs:                                                                                    # objects stand on free cells
    if o['type'] in ('clue', 'waystone', 'sign', 'hint', 'pit') and g[o['y'], o['x']] == 'H': g[o['y'], o['x']] = '.'
# ---------------- reachability: with brambles solid the exit must be shut; cut, it must open ----------------
free = ~np.isin(g, list(SOL))
for o in objs:
    if o['type'] in ('waystone', 'sign'): free[o['y'], o['x']] = False
sx, sy = WAKE
def reach(fr): return bfs(fr, sx, sy)
fb = free.copy()
for y in range(RY, RY + 5):
    for x in BR_X: fb[y, x] = False
r_shut = reach(fb); r_open = reach(free)
ex_cells = [(EXIT_X, y) for y in range(RY, RY + 5)]
def nb_ok(r, x, y): return r[y, x] or any(0 <= x + a < W and 0 <= y + b < H and r[y + b, x + a] for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
print('reach open', int(r_open.sum()), 'shut', int(r_shut.sum()))
print('exit shut by brambles:', not any(r_shut[y, x] for x, y in ex_cells), '| exit open after cut:', any(r_open[y, x] for x, y in ex_cells))
for o in objs:
    if o['type'] in ('exit', 'hint', 'pit', 'vista'): continue
    if not nb_ok(r_shut if o['type'] != 'sign' else r_open, o['x'], o['y']): print('  UNREACHABLE', o.get('id', o['type']))
# route length (BFS tiles) through the tutorial beats
from collections import deque
def dist(a, b, fr):
    D_ = np.full((H, W), -1); D_[a[1], a[0]] = 0; q = deque([a])
    while q:
        x, y = q.popleft()
        if (x, y) == b: return int(D_[y, x])
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            X, Y = x + dx, y + dy
            if 0 <= X < W and 0 <= Y < H and fr[Y, X] and D_[Y, X] < 0: D_[Y, X] = D_[y, x] + 1; q.append((X, Y))
    return -1
fr2 = free.copy(); fr2[FIRE[1], FIRE[0]] = True
beats = [WAKE, (PACK[0], PACK[1] + 1), (FIRE[0] + 1, FIRE[1]), CREST, (45, RY + 2), (52, RY + 2), (56, RY + 2), (62, RY + 2)]
legs = [dist(a, b, fr2) for a, b in zip(beats, beats[1:])]; print('route legs', legs, 'total', sum(legs))
# ---------------- ground painting (code: ash, worn path, mounds, hollow, crest void, east slope, wall shadow, crack) ----------------
gh = gw = W * G
yy, xx = np.mgrid[0:gh, 0:gw].astype(np.float32); ty, tx = yy / G, xx / G
def sn(scale, seed):
    r = np.random.RandomState(seed); lh, lw = int(gh / scale) + 3, int(gw / scale) + 3
    lo = ndimage.gaussian_filter(r.rand(lh, lw), 1.0); lo = (lo - lo.min()) / (np.ptp(lo) + 1e-6)
    return np.array(Image.fromarray((lo * 255).astype(np.uint8)).resize((gw + 2 * scale, gh + 2 * scale), Image.BICUBIC)).astype(np.float32)[scale:scale + gh, scale:scale + gw] / 255.
def up(a): return np.array(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((gw, gh), Image.BILINEAR)).astype(np.float32) / 255.
base = np.array([116, 110, 102.], np.float32)
tone = sn(260, 1) * .55 + sn(90, 2) * .3 + sn(24, 3) * .15
img = base * (.84 + .3 * tone)[..., None]
wash = sn(140, 4); img = img * (1 - .10 * wash[..., None]) + np.array([132, 120, 104.]) * .10 * wash[..., None]   # sepia watercolor blooms
grain = (np.random.RandomState(5).rand(gh, gw).astype(np.float32) - .5) * 9; img += grain[..., None]
west = np.clip((12 - tx) / 8, 0, 1) * (.6 + .4 * sn(40, 6))                                        # petrified forest floor: colder, stony
img = img * (1 - .55 * west[..., None]) + np.array([104, 106, 108.]) * .55 * west[..., None]
# the worn path (wake -> crest -> corridor), footprints along it
pm = Image.new('L', (W * 4, H * 4), 0); pd = ImageDraw.Draw(pm)
for pts, wd in (([(30.5, 22.5), (30.8, 18.5), (31.2, 14.8), (36, 15.6), (44, 15.5), (52, 15.6), (64, 15.4)], 7), ([(30.5, 23), (36, 27), (42.5, 31)], 3), ([(30, 19.5), (24, 18.6), (17, 19.6)], 3)):
    pd.line([(x * 4, y * 4) for x, y in pts], fill=255, width=wd, joint='curve')
pmask = up(np.array(pm.filter(ImageFilter.GaussianBlur(3))).astype(np.float32) / 255.)
pmask = np.clip(pmask * 1.3 + (sn(30, 7) - .5) * .5, 0, 1)
img = img * (1 - .55 * pmask[..., None]) + (img * np.array([.86, .8, .72]) - 4) * .55 * pmask[..., None]
# grave mounds + older mounds (under the sprites), the body-shaped hollow at the wake spot
def blot(cx, cy, rx, ry, col, a, soft=4):
    m = np.zeros((gh, gw), np.float32); x0, x1 = int((cx - rx - 1) * G), int((cx + rx + 1) * G); y0, y1 = int((cy - ry - 1) * G), int((cy + ry + 1) * G)
    x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(gw, x1), min(gh, y1)
    sub = (((tx[y0:y1, x0:x1] - cx) / rx) ** 2 + ((ty[y0:y1, x0:x1] - cy) / ry) ** 2)
    m[y0:y1, x0:x1] = np.clip(1.2 - sub, 0, 1); m = ndimage.gaussian_filter(m, soft) if soft else m
    return m * a, col
for (x, y) in gs: m_, c = blot(x + .5, y + .75, 1.0, .55, None, .5); img *= (1 - .32 * m_)[..., None]
m_, _ = blot(WAKE[0] + .5, WAKE[1] + .6, 1.25, .55, None, 1, 6); rim, _ = blot(WAKE[0] + .5, WAKE[1] + .6, 1.6, .8, None, 1, 6)
kr = ((rim - m_).clip(0, 1) * .3)[..., None]; img = img * (1 - .35 * m_)[..., None]; img = img * (1 - kr) + np.array([150, 144, 134.]) * kr
# beyond the crest (rows < 3.6): the drop to the plain, a cold misty void; crest lip line
void = np.clip((LIP - .15 - ty) / 2.4, 0, 1)
sky = np.array([84, 84, 92.]) * (1 - np.clip(ty / 4, 0, 1))[..., None] + np.array([70, 68, 72.]) * np.clip(ty / 4, 0, 1)[..., None]
img = img * (1 - void[..., None]) + sky * void[..., None]
lip = np.exp(-((ty - LIP) / .18) ** 2) * (.7 + .3 * sn(12, 8)); img *= (1 - .45 * lip)[..., None]
img += (np.exp(-((ty - LIP - .5) / .25) ** 2) * 14)[..., None]                                       # the crest catches the light
# east slope + ledge: hatched rock drop; the corridor darkens toward the exit (fade)
slope = up(ndimage.gaussian_filter(((np.arange(W)[None, :] >= 51) & (np.arange(H)[:, None] >= RY + 5) | ((np.arange(W)[None, :] >= 44) & (np.arange(H)[:, None] >= RY + 5) & (np.arange(H)[:, None] < RY + 9))).astype(np.float32), .8))
hatch = (np.sin((xx + yy * .6) / 3.2) > .55).astype(np.float32) * .12
img *= (1 - slope * (.38 + hatch + .12 * sn(20, 9)))[..., None]
fadeE = np.clip((tx - 58) / 6, 0, 1) * np.clip(1 - np.abs(ty - RY - 2.5) / 4, 0, 1); img *= (1 - .45 * fadeE)[..., None]
# south: ash dunes (soft pale ridges with blue-grey shade, no wall shadow any more)
dn = np.sin(tx * .55 + sn(60, 21) * 5) * .5 + .5; dun = np.clip((ty - 52) / 8, 0, 1)
img = img * (1 - .18 * dun[..., None]) + np.array([150, 146, 140.]) * (.18 * dun * dn)[..., None]; img *= (1 - .3 * np.clip((ty - 59.5) / 3, 0, 1))[..., None]
# west edge: under the trees
img *= (1 - .35 * np.clip((6 - tx) / 4, 0, 1))[..., None]
# the ground crack at x 53 (rows 3.8 .. 9.1): jagged black fissure, pale broken edges
ck = np.zeros((gh, gw), np.float32); r9 = np.random.RandomState(9)
ys_ = np.arange(int((RY - .2) * G), int((RY + 5.1) * G)); off = ndimage.gaussian_filter1d(r9.randn(len(ys_)) * 5, 3); wid = .30 + .12 * np.sin(ys_ / 9.0) + .06 * r9.rand(len(ys_))
for i, y in enumerate(ys_):
    c = (CRACK_X + .5) * G + off[i]; w_ = wid[i] * G; ck[y, int(c - w_):int(c + w_)] = 1
edge = ndimage.binary_dilation(ck > 0, iterations=3) & ~(ck > 0)
img[edge] = img[edge] * .7 + 38; img[ck > 0] = np.array([18, 16, 18.])
img[ndimage.binary_dilation(ck > 0, iterations=1) & ~(ck > 0)] *= .55
# soft tile-scale ink: darken free/solid borders a touch (reads as hand-inked ground)
sol = up(ndimage.gaussian_filter((g == '#').astype(np.float32), .9)); img *= (1 - .32 * sol)[..., None]
img = np.clip(img, 0, 255)
gimg = Image.fromarray(img.astype(np.uint8)); gp = PA + 'ground.webp'; gimg.save(rel(gp), 'WEBP', quality=88, method=6)
gimg.resize((W * 8, H * 8), Image.LANCZOS).save('/tmp/work/pg_ground_small.png')
# ---------------- backdrop: the royal castle past the end of the road / from the crest (over the field's lip) ----------------
# v8 (owner 10-25 「일러스트 작가랑 손그림풍 성 원화 새로 그려서 써라」「그림이 움직이게」): the illustrator's hand-drawn castle + its 16-frame loop (castle_far.py);
# the picture already has its own outer wall band, so no extra code-drawn Felt wall / gate in front (castle_fortress.py -> tools/hd/_archive_old_felt).
import castle_far as CFAR
backdrop = CFAR.backdrop('pg'); backdrop.update({'x': 46, 'px': .95, 'fit': [-.8, LIP + .3, 1.2, 2.2, 3.4], 'clipY': LIP - .05})
# 사장님 10-25 「펠트 마을도 앞에」: castle_far 앞에 펠트 마을 띠 (felt_far_band.webp, 팀장) — front 는 목록
backdrop['front'] = [backdrop['front'], {'img': 'assets/world/castle_far/felt_far_band.webp', 'y': 1090, 'px': .06}] if isinstance(backdrop.get('front'), dict) else backdrop.get('front')   # (castle_far 'pg' already carries lift .4: brighter under the grave's dark light)
camZones = [{'x0': 8, 'y0': RY, 'x1': 42, 'y1': 25, 'zoom': .8, 'look': -7.5, 'f': 4}, {'x0': 40, 'y0': RY, 'x1': 64, 'y1': RY + 5, 'zoom': .9, 'look': -7.5, 'f': 3}]
# ---------------- tufts (dead grass), hd block, json ----------------
tufts = []
for y in range(RY + 1, 59):
    for x in range(8, 51):
        if g[y, x] == '.' and rnd.random() < .12: tufts.append([round(x + rnd.random(), 2), round(y + .3 + rnd.random() * .7, 2), rnd.randrange(3)])
allp = back + sorted(props_, key=lambda q: q['y'])
smoke = [[FIRE[0] + .5, FIRE[1] + .4, .5, 2]]                                                    # one thin thread of smoke from the cold fire
hd = {'D': HD, 'ground': gp, 'props': allp, 'decoArt': {}, 'lights': [], 'smoke': smoke, 'grade': 'dusk', 'gradeCol': 'rgb(196,192,190)', 'flick': [], 'tufts': tufts, 'fires': [], 'backdrop': backdrop,
      'fx': {'particles': 'ash', 'birds': 3, 'mist': 6, 'tuft': ['#57534a', '#5e5a50', '#4a463d']}}
legend = {'.': 'dirt', '#': 'cliff', 'H': {'ground': 'dirt', 'solid': True}}
out = {'type': 'field', 'area': 1, 'id': 'prologue_grave', 'name': '무명 무덤가', 'region': 'ch1', 'ch1Origin': [OX, OY],
       'title': {'kicker': 'PROLOGUE', 'name': '무명 무덤가', 'sub': '펠트 성벽 바깥, 이름 없는 무덤가 언덕'}, 'bgm': 'field', 'battleBgm': 'field_battle', 'tileset': 'field', 'tile': T,
       'viewZoom': 1.3, 'grade': 'ash', 'fog': .3, 'ash': 70, 'wind': [4, 1.5], 'w': W, 'h': H, 'skyTop': 10, 'camZones': camZones, 'legend': legend, 'solid': ['#', 'H'],
       'ground': [''.join(r) for r in g], 'objects': objs, 'spawns': spawns, 'hd': hd,
       'dark': None, 'pgLight': {'a': .5, 'r': 2, 'r2': 4.5, 'flag': 'pg_backpack', 'col': '#7fb2d6', 'col2': '#d8d0b8'}, 'steps': 1, 'navGoal': {'map': 'prologue_grave', 'x': 62, 'y': RY + 2, 'label': '펠트 서문'},
       'note': 'GENERATED by tools/hd/fields/build_prologue_grave.py (owner 10-25 B: awakening map) - do not hand-edit'}
del out['dark']
json.dump(out, open(rel('maps/prologue_grave.json'), 'w'), ensure_ascii=False, indent=1)
print('\n'.join(out['ground'])); print('props', len(allp))
