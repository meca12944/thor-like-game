"""1장 들판 조립 도구 (새 1장 들판 빌더가 같이 씀: build_ch1_center.py …). 동쪽 들판(build_ch1_east.py)에서 쓴 방법을 함수로 묶음.

Field(맵 id, w, h, 설계도 원점, 그림 폴더, seed):
  grid / put / rect      — 막힘 글자 판 ('.' 길, '#' 벽, '~' 물·구덩이, 'X' 소품 밑동, 'T' 마른 나무, 'R' 돌무더기, 's' 그루터기)
  ground_ash()           — 그록 잿빛 바닥 v0 깔고 v1~3 얼룩 (조각 경계 줄 없음)
  road(pts, w)           — 흙길 + 발자국,  free(x, y, r) — 길·막힘이 없는 자리
  img(src, name) / alpha_mask(im, x, y, ch) / under(…) / prop(…) / small(…) — 그록 그림 놓기
  scatter_rocks / fill_landmarks / roadside / tufts — 「화면마다 눈 둘 것 하나」 (팀장 10-25)
  mobs(설계도 구역 id) / write(map dict)
크기 기준: 주인공 실제 키 42 필드px, 그록은 34 기준 → 사람 크기 소품은 HS = 42/34 배.
"""
import json, os, random, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); T128 = os.path.normpath(os.path.join(HERE, '..', '..', '..')); REPO = os.path.dirname(T128)
G1 = os.path.join(REPO, 'handoff/grok_in/1장_풍경_20261025'); G2 = os.path.join(REPO, 'handoff/grok_in/16-22_소품_인물_주인공동작_20261025')
SM = f'{G1}/12_small_sceneries'; TS = 16; HS = 42 / 34
MOBS = ['c1_silmamul', 'c1_thread_puppet', 'c1_needle_spider', 'c1_unrotting_hound']   # 마물 다시 기획 전 (4번방이 바꿈)
SMALLS = {'12a_collapsed_tower': (.5, .6, 24, 18), '12b_old_battlefield_spears': (.45, None, 30, 21), '12c_petrified_grove': (.55, None, 32, 22), '12d_ash_mound_hill': (None, .8, 28, 16)}


class Field:
    def __init__(self, mid, w, h, ox, oy, out, seed):
        self.id, self.W, self.H, self.OX, self.OY, self.OUT = mid, w, h, ox, oy, out
        self.OUTD = os.path.join(T128, out); os.makedirs(self.OUTD, exist_ok=True)
        self.rnd = random.Random(seed); self.grid = [['.'] * w for _ in range(h)]
        self.props, self.unders, self.objs, self.big, self.roads = [], [], [], [], []
        self.GW, self.GH = w * TS, h * TS; self._saved = set()
        self.felt = json.load(open(os.path.join(T128, 'maps/felt.json'))); self.felt_deco = self.felt['hd'].get('decoArt', {})

    # ---- 판 ----
    def put(self, x, y, c):
        if 0 <= x < self.W and 0 <= y < self.H: self.grid[y][x] = c
    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1):
            for x in range(x0, x1): self.put(x, y, c)
    def on_road(self, x, y):
        return any(math.hypot(x - px, y - py) < 3 for R in self.roads for px, py in self._road_pts(R))
    def _road_pts(self, R):
        if '_pts' not in R:
            pts = []
            for (x0, y0), (x1, y1) in zip(R['pts'], R['pts'][1:]):
                n = max(1, int(math.hypot(x1 - x0, y1 - y0)))
                pts += [(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n) for k in range(n)]
            R['_pts'] = pts
        return R['_pts']
    def free(self, x, y, r=2):
        for yy in range(int(y) - r, int(y) + r + 1):
            for xx in range(int(x) - r, int(x) + r + 1):
                if not (0 <= xx < self.W and 0 <= yy < self.H) or self.grid[yy][xx] != '.' or self._rm[yy][xx]: return False
        return True

    # ---- 바닥 ----
    def ground_ash(self):
        rnd, GW, GH = self.rnd, self.GW, self.GH
        tiles = [Image.open(f'{G1}/01_ash_field/01_ash_ground_512_v{i}.png').convert('RGBA') for i in range(4)]
        g = Image.new('RGBA', (GW, GH))
        for cy in range(0, GH, 512):
            for cx in range(0, GW, 512): g.paste(tiles[0], (cx, cy))
        for i in (1, 2, 3):
            full = Image.new('RGBA', (GW, GH))
            for cy in range(0, GH, 512):
                for cx in range(0, GW, 512): full.paste(tiles[i], (cx, cy))
            m = Image.new('L', (GW // 8, GH // 8)); dm = ImageDraw.Draw(m)
            for _ in range(int(14 * GW * GH / (3040 * 4160)) + 4):
                x, y, r = rnd.uniform(0, GW / 8), rnd.uniform(0, GH / 8), rnd.uniform(25, 70); dm.ellipse([x - r, y - r * .7, x + r, y + r * .7], fill=255)
            g.paste(full, (0, 0), m.filter(ImageFilter.GaussianBlur(14)).resize((GW, GH), Image.BILINEAR))
        self.ground = g; self._rm = [[0] * self.W for _ in range(self.H)]
    def road(self, pts, w=3.0, col=(92, 80, 68), a=95):
        m = Image.new('L', (self.GW, self.GH)); d = ImageDraw.Draw(m)
        d.line([(x * TS, y * TS) for x, y in pts], fill=255, width=int(w * TS), joint='curve')
        for x, y in pts: r = w * TS / 2; d.ellipse([x * TS - r, y * TS - r, x * TS + r, y * TS + r], fill=255)
        self.ground.paste(Image.new('RGBA', (self.GW, self.GH), col + (255,)), (0, 0), m.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * a / 255)))
        R = {'pts': pts, 'w': w}; self.roads.append(R)
        for px, py in self._road_pts(R):
            for yy in range(int(py) - 2, int(py) + 3):
                for xx in range(int(px) - 2, int(px) + 3):
                    if 0 <= xx < self.W and 0 <= yy < self.H: self._rm[yy][xx] = 1
    def footprints(self):
        foot = Image.open(f'{G1}/01_ash_field/deco/01_footprint_stamp_4x7.png').convert('RGBA')
        for R in self.roads:
            P = R['pts']
            for (x0, y0), (x1, y1) in zip(P, P[1:]):
                n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 5))
                for k in range(n):
                    t = (k + .5) / n; self.ground.alpha_composite(foot, (int((x0 + (x1 - x0) * t) * TS + self.rnd.uniform(-6, 6)), int((y0 + (y1 - y0) * t) * TS)))

    # ---- 그림 ----
    def img(self, src, name, scale=None, flip=False):
        im = Image.open(src).convert('RGBA')
        if scale: im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
        if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT); name += '_fl'
        p = f'{self.OUT}/{name}.webp'
        if p not in self._saved: im.save(os.path.join(T128, p), 'WEBP', quality=88, method=6); self._saved.add(p)
        return p, im
    def alpha_mask(self, im, x0, y0, c, keep=None, thr=.5, dark=None, D=1):
        if D != 1: im = im.resize((round(im.width / D), round(im.height / D)), Image.LANCZOS)
        a = np.asarray(im).astype(np.float32); w, h = im.size
        ok = a[..., 3] > 128
        if dark is not None: ok &= a[..., :3].mean(-1) < dark
        for ty in range(math.ceil(h / TS)):
            for tx in range(math.ceil(w / TS)):
                if keep and keep(tx, ty): continue
                blk = ok[ty * TS:ty * TS + TS, tx * TS:tx * TS + TS]
                if blk.size and blk.mean() > thr: self.put(x0 + tx, y0 + ty, c)
    def under(self, pid, p, x, y, D=1):
        self.unders.append({'id': pid, 'img': p, 'x': x, 'y': y, 'ax': 0, 'ay': 0, 'D': D, 'under': 1})
    def prop(self, pid, p, x, y, D=1, fade=1, shadow=1, **k):
        q = {'id': pid, 'img': p, 'x': round(x, 2), 'y': round(y, 2), 'D': D, 'fade': fade, 'shadow': shadow}; q.update(k); self.props.append(q); return q
    def small(self, name, x, y, fl=False):
        split, thr, w0, h0 = SMALLS[name]; k = sum(1 for q in self.unders if q['id'].startswith(name)) + 1
        bp, bi = self.img(f'{SM}/{name}_back.png', name + '_back', flip=fl); self.under(f'{name}_b{k}', bp, x, y)
        if split is not None:
            fp, fi = self.img(f'{SM}/{name}_front.png', name + '_front', flip=fl)
            self.prop(f'{name}_f{k}', fp, x, y + split * fi.height / TS, ax=0, ay=round(split * fi.height), shadow=0)
        if thr:
            ref = Image.open(f'{SM}/{name}_full_ref.png' if split is not None else f'{SM}/{name}_back.png').convert('RGBA')
            if fl: ref = ref.transpose(Image.FLIP_LEFT_RIGHT)
            self.alpha_mask(ref, x, y, 'X', thr=thr, keep=lambda tx, ty: split is not None and ty < split * .9 * bi.height / TS)
        self.big.append((x, y, w0, h0))

    # ---- 채우기 ----
    def rocks(self):
        if not hasattr(self, '_rocks'): self._rocks = [self.img(f'{G1}/11_north_cliff/11_fallen_rock_{n}_back.png', 'rock_' + n) for n in ('boulder_pile', 'rock_slab', 'pebbles')]
        return self._rocks
    def scatter_rocks(self, n, y0, y1):
        R = self.rocks()
        for i in range(n):
            rp, ri = R[i % 3]; w = ri.width / TS
            for _ in range(30):
                x, y = self.rnd.uniform(6, self.W - 8), self.rnd.uniform(y0, y1)
                if self.free(x, y - 1, 4): break
            else: continue
            self.prop(f'rock_{i}', rp, x, y)
            if i % 3 != 2: self.rect(int(x - w / 2 + .5), int(y - 1), int(x + w / 2 - .5), int(y), 'X')
    def chars_near(self, cx, cy, ch, k, r):
        for _ in range(k * 6):
            if k <= 0: break
            x, y = int(cx + self.rnd.uniform(-r, r)), int(cy + self.rnd.uniform(-r * .6, r * .6))
            if self.free(x, y, 1): self.put(x, y, ch); k -= 1
    def wreck(self, x, y):
        q = self.felt_deco['R'][self.rnd.randrange(len(self.felt_deco['R']))]; self.props.append(dict(q, id=f'wreck_{len(self.props)}', x=round(x, 1), y=round(y, 1), fade=1, shadow=1))
    def fill_landmarks(self, y0, y1, cw=30, ch=17):
        """PC 1080p 화면 ≈ 30x17타일: 칸 가운데 곁에 큰 경관이 없으면 하나 — 마른 나무 숲 / 그록 작은 경관 / 돌무더기 / 잔해"""
        rnd = self.rnd
        for cy in range(y0, y1 - 4, ch):
            for cx in range(0, self.W - 10, cw):
                if any(bx - 6 < cx + cw / 2 < bx + bw + 6 and by - 4 < cy + ch / 2 < by + bh + 4 for bx, by, bw, bh in self.big): continue
                kind = rnd.random(); x, y = cx + rnd.uniform(6, cw - 6), cy + rnd.uniform(4, ch - 4)
                if kind < .25: self.chars_near(x, y, 'T', rnd.randint(4, 7), 6); self.chars_near(x, y, 's', 2, 7)
                elif kind < .7:                               # 그록 작은 경관 (팀장 10-26 「잘 안 보임」 → 비율 올리고 자리 3번까지 찾음)
                    nm = rnd.choice(list(SMALLS)); w0, h0 = SMALLS[nm][2:]
                    for _t in range(4):
                        x0, y0_ = min(self.W - w0 - 2, max(2, cx + rnd.uniform(0, cw) - w0 / 2)), min(y1 - h0, max(y0, cy + rnd.uniform(0, ch) - h0 / 2))
                        if all(self.free(x0 + i * w0 / 3, y0_ + j * h0 / 2, 0) for i in range(4) for j in range(3)): self.small(nm, round(x0), round(y0_), fl=rnd.random() < .5); break
                    else: self.chars_near(x, y, 'T', 4, 6)
                elif kind < .87:
                    rp, ri = self.rocks()[rnd.randrange(2)]
                    if self.free(x, y - 1, 2): self.prop(f'rock_c{len(self.props)}', rp, x, y); self.rect(int(x - 2), int(y - 1), int(x + 2), int(y), 'X')
                    self.chars_near(x, y, 'R', rnd.randint(3, 5), 6)
                else:
                    for _ in range(rnd.randint(3, 5)):
                        px, py = x + rnd.uniform(-5, 5), y + rnd.uniform(-3, 3)
                        if self.free(px, py, 1): self.wreck(px, py)
    def roadside(self, y0, y1):
        peb = self.rocks()[2][0]
        for R in self.roads:
            P = R['pts']
            for i, ((x0, ya), (x1, yb)) in enumerate(zip(P, P[1:])):
                L = math.hypot(x1 - x0, yb - ya); nx, ny = -(yb - ya) / max(L, 1e-6), (x1 - x0) / max(L, 1e-6)
                for k in range(int(L / 7)):
                    t = (k + .5) / max(1, int(L / 7)); sd = 3.5 if (k + i) % 2 else -3.5; x, y = x0 + (x1 - x0) * t + nx * sd, ya + (yb - ya) * t + ny * sd
                    if not (y0 < y < y1) or not (0 <= int(x) < self.W) or self.grid[int(y)][int(x)] != '.': continue
                    r = self.rnd.random()
                    if r < .35: self.put(int(x), int(y), 's')
                    elif r < .7: self.wreck(x, y)
                    else: self.prop(f'peb_{len(self.props)}', peb, x, y, fade=0, shadow=0)
    def tufts_mounds(self, y0, y1, nm=140, nt=900):
        deco = [Image.open(f'{G1}/01_ash_field/deco/{n}.png').convert('RGBA') for n in ['01_ash_mound_a', '01_ash_mound_b', '01_ash_drift_long', '01_ash_mound_beam']]
        tufts = [Image.open(f'{G1}/01_ash_field/deco/01_grass_tuft_{i:02d}.png').convert('RGBA') for i in range(12)]
        k = self.W * self.H / (190 * 260)
        for _ in range(int(nm * k)):
            x, y = self.rnd.uniform(4, self.W - 8), self.rnd.uniform(y0, y1); im = self.rnd.choice(deco)
            if self.free(x + im.width / 32, y + im.height / 32, 4): self.ground.alpha_composite(im, (int(x * TS), int(y * TS)))
        for _ in range(int(nt * k)):
            x, y = self.rnd.uniform(2, self.W - 3), self.rnd.uniform(y0, y1); im = self.rnd.choice(tufts)
            if self.free(x, y, 0): self.ground.alpha_composite(im, (int(x * TS - im.width / 2), int(y * TS - im.height)))

    # ---- 몹 · 쓰기 ----
    def mobs(self, zone, skip=lambda x, y: False):
        M = json.load(open(os.path.join(REPO, 'docs_maps/ch1/ch1_map.json'))); gi = 0
        for mk in M['markers']:
            if mk['zone'] != zone or mk['type'] != 'mob': continue
            x, y = mk['x'] - self.OX, mk['y'] - self.OY; n = 3 if '큰' in mk['name'] else 2 if '보통' in mk['name'] else 1
            if skip(x, y): continue
            for k in range(n):
                for _ in range(30):
                    sx, sy = x + self.rnd.uniform(-4, 4), y + self.rnd.uniform(-4, 4)
                    if 0 < sx < self.W and 0 < sy < self.H and self.grid[int(sy)][int(sx)] == '.': break
                else: continue
                self.objs.append({'type': 'spawn', 'mob': MOBS[(gi + k) % 4], 'x': round(sx), 'y': round(sy), 'respawn': 30})
            gi += 1
    def save_ground(self):
        self.ground.convert('RGB').save(os.path.join(self.OUTD, 'ground.webp'), 'WEBP', quality=82, method=6)
    def write(self, extra):
        mp = {'id': self.id, 'type': 'field', 'area': 1, 'region': 'felt', 'mapPos': [0, 0], 'tileset': 'field', 'tile': 16, 'w': self.W, 'h': self.H,
              'legend': {'.': 'dirt', '#': 'cliff', '~': {'ground': 'dirt', 'solid': True}, 'K': {'ground': 'dirt', 'solid': True}, 'X': {'ground': 'dirt', 'solid': True},
                         'T': {'ground': 'dirt', 'deco': 'tree'}, 'R': {'ground': 'dirt', 'deco': 'boulder'}, 's': {'ground': 'dirt', 'deco': 'stump', 'solid': False}},
              'solid': ['#', '~', 'K', 'X', 'T', 'R'], 'ground': [''.join(r) for r in self.grid], 'objects': self.objs}
        mp.update(extra)
        mp['hd'] = dict({'D': 1, 'ground': f'{self.OUT}/ground.webp', 'props': self.unders + self.props, 'grade': 'ash',
                         'decoArt': {k: self.felt_deco[k] for k in ('T', 'R', 's') if k in self.felt_deco}, 'fx': {}}, **extra.get('hd', {}))
        json.dump(mp, open(os.path.join(T128, f'maps/{self.id}.json'), 'w'), ensure_ascii=False, indent=1)
        return mp
