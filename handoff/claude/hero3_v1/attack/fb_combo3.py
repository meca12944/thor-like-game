# 그록 3차 (11-01, 회의 결론대로 부탁 → 「폴더 확인」): 정면 2타 가로베기 + 뒷면 3타 → 게임 크기 가안 영상
# 회의 결론: 자세만 쓰고 빠르기는 코드 — 감기 → 휙(1틱씩) → 맞는 자세 4틱 멈춤 → 팔로스루. 길이 30/30/45틱, 맞는 장 8/8/11틱(옆과 같음)
#  정면 2타 가로(f2x, 720): 0~18 감기(칼 왼쪽 수평) → [21~33 칼이 머리 위로 넘어감 = 뺌] → 36 칼이 발 아래로 곧게(맞는 자세) → 54·57 오른쪽으로 → 60 끝(= w_all 102장)
#  뒷면(720, 서기 키 454칸 → 게임 143칸): 1타 b1 · 2타 b2x(왼쪽 → 머리 위로 곧게 → 오른쪽) + 되돌려베기 br · 3타 b3. 다음 영상 처음 = 앞 영상 끝 그림(그록 고정)
#  뒷면 발 높이가 그록 자세 그림마다 달라(593~649/720) 장마다 몸 덩어리 발끝을 땅 줄에 맞춤
# 쓰는 법: python3 fb_combo3.py <fc(w_all)> <fc2(2타 다시)> <fc3(f2x, b1, b2x, br, b3)>
import sys, os, json, importlib.util, numpy as np, cv2
from PIL import Image
from multiprocessing import Pool
FC, F2, F3 = [a.rstrip('/') + '/' for a in sys.argv[1:4]]
HERE = os.path.dirname(os.path.abspath(__file__))
SB = 143 / 454   # 뒷면 서기 키(b1 0장 머리끝 162 → 발 616) → 게임 뒷면 서기 143칸
def load(name, argv):
    sys.argv = ['x'] + argv
    sp = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py')); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
F2X = [0, 3, 6, 9, 12, 15, 18, 36, 40, 45, 51, 54, 57, 60, 66, 72]
BK = {'b1': [0, 6, 9, 12, 15, 18, 24, 27, 29, 30, 31, 33, 36, 40, 44, 48], 'b2x': [0, 3, 12, 24, 30, 33, 36, 39, 42, 45, 51, 54, 57, 60, 66, 72],
      'br': [0, 9, 12, 15, 18, 21, 24, 30, 72], 'b3': [0, 3, 9, 12, 15, 18, 21, 24, 26, 28, 30, 33, 36, 40, 44, 48]}
NEED = [('f2x', k, None) for k in F2X] + [(v, k, SB) for v, ks in BK.items() for k in ks]
def job(x):
    fp = load('front_proc', [F3]); v, k, s = x
    return fp.one((v, 720, k) if s is None else (v, 720, k, s))
def body_bottom(a):
    n_, lab, st, _ = cv2.connectedComponentsWithStats((a[..., 3] > 0).astype(np.uint8), connectivity=8)
    if n_ < 2: return a.shape[0] - 1
    m = lab == 1 + int(np.argmax(st[1:, 4])); return int(np.nonzero(m.any(1))[0].max())
if __name__ == '__main__':
    GJ = F3 + 'grip3.json'
    if not os.path.exists(GJ):
        with Pool(4) as P: res = P.map(job, NEED)
        os.makedirs(F3 + 'body3', exist_ok=True); G = {}
        b72 = Image.open(FC + 'body/072.png').getbbox(); bf = Image.fromarray(res[0][1]).getbbox()
        oxf, oyf = round((b72[0] + b72[2]) / 2 - (bf[0] + bf[2]) / 2), b72[3] - bf[3]      # 정면: f2x 0장 = w_all 72장에 맞춤
        b0 = Image.fromarray(res[len(F2X)][1]).getbbox(); oxb = round(150 - (b0[0] + b0[2]) / 2)   # 뒷면: b1 0장 몸 가운데 = 150, 발 = 268
        for (v, k, s), (row, out) in zip(NEED, res):
            if v == 'f2x': ox, oy = oxf, oyf
            else: ox, oy = oxb, 268 - body_bottom(out)   # 장마다 발끝을 땅 줄에
            cv_ = Image.new('RGBA', (300, 300)); im = Image.fromarray(out); cv_.paste(im, (ox, oy), im); cv_.save(F3 + f'body3/{v}_{k:03d}.png')
            row['guard'] = [row['guard'][0] + ox, row['guard'][1] + oy]; G[f'{v}_{k:03d}'] = row
        # 칼이 가려졌거나 흐린 장(칼날 25칸 밑)은 같은 영상 안 앞뒤 멀쩡한 장 사이로 칼 자리·각도를 이음(짧은 쪽으로 돌기)
        for v in ['f2x'] + list(BK):
            ks = [f'{v}_{k:03d}' for k in (F2X if v == 'f2x' else BK[v])]; ok = [G[q]['blade'] >= 25 for q in ks]
            for i, q in enumerate(ks):
                if ok[i]: continue
                p = max([j for j in range(i) if ok[j]], default=None); n = min([j for j in range(i + 1, len(ks)) if ok[j]], default=None)
                if p is None and n is None: continue
                if p is None or n is None: src = G[ks[n if p is None else p]]; G[q].update(guard=list(src['guard']), ang=src['ang'], behind=True); continue
                t = (i - p) / (n - p); A0, A1 = G[ks[p]], G[ks[n]]; da = (A1['ang'] - A0['ang'] + 180) % 360 - 180
                G[q].update(guard=[A0['guard'][j] * (1 - t) + A1['guard'][j] * t for j in range(2)], ang=A0['ang'] + da * t)
        json.dump(G, open(GJ, 'w'), indent=0); print('처리', len(G))
    G = json.load(open(GJ))
    for key in sorted(G):
        r = G[key]; print(key, [round(q) for q in r['guard']], round(r['ang']), round(r['blade']), 'B' if r['behind'] else '')
    fr = load('front_render', [FC])
    G2 = json.load(open(F2 + 'grip2.json'))['frames']
    cache = {}
    def game3(k):
        if k in cache: return cache[k]
        if isinstance(k, str) and k.split('_')[0] in ('f2x', 'b1', 'b2x', 'br', 'b3'):
            r = G[k]; foot = fr.FOOT
            if k.startswith('f2x'): fr.FOOT = 999   # 새 정면 2타: 칼이 발 아래로 제 길이 그대로(회의 결론) → 땅 위 멈춤 안 씀
            cache[k] = fr.comp(fr.clean(Image.open(F3 + f'body3/{k}.png'), 0), r, fr.H1, fr.RA); fr.FOOT = foot
        elif isinstance(k, str):   # 지난 2타(c2·m)
            src, n = k.split('_'); r = dict(G2[f'{src}_{int(n)}']); s0 = r.get('s', 1.0); im, hx, hy, L = fr.H1; hd = fr.H1
            if s0 < .999: hd = (im.resize((im.width, max(1, round(im.height * s0))), Image.NEAREST), hx, hy * s0, L * s0)
            cache[k] = fr.comp(fr.clean(Image.open(F2 + f'body2/{k}.png'), 0), r, hd, fr.RA)
        else: cache[k] = fr.game(k)
        return cache[k]
    T = lambda L: sum(n for _, n in L)
    def at(L, key):
        t = 0
        for k, n in L:
            if k == key: return t
            t += n
    # 정면 (1타·3타 = 지금 게임 그대로, 2타만 새것)
    S1 = [(6, 1), (10, 1), (14, 1), (18, 1), (22, 2), (26, 1), (28, 1), (30, 1), (31, 1), (32, 1), (33, 1), (34, 1), (35, 1), (36, 1), (38, 2), (40, 2), (42, 2), (44, 2), (46, 7)]
    S2old = [('c2_013', 3), ('c2_014', 1), ('c2_015', 1), ('c2_016', 1), ('c2_017', 2), ('c2_021', 1)] + [(f'm_{k:03d}', 1) for k in (29, 31, 32, 33, 34, 36, 38, 42, 48)] \
            + [(k, 1) for k in (109, 113, 117, 121, 125, 129, 133)] + [(137, 1), (140, 1), (144, 3)]
    S2new = [('f2x_003', 1), ('f2x_006', 2), ('f2x_012', 1), ('f2x_015', 2), ('f2x_018', 2)] + [('f2x_036', 4)] \
            + [('f2x_054', 1), ('f2x_057', 1), ('f2x_060', 4)] + [(k, 1) for k in (109, 113, 117, 121, 125, 129, 133, 137, 140)] + [(144, 3)]
    S3 = [(156, 1), (168, 1), (172, 1), (176, 1), (180, 1), (182, 3), (192, 1), (194, 1), (196, 1), (198, 1)] + [(k, 2) for k in (200, 202, 204, 206, 208, 212, 216, 220, 224, 228, 232, 236, 240, 246)] + [(252, 5)]
    assert (T(S1), T(S2old), T(S2new), T(S3)) == (30, 30, 30, 45), (T(S1), T(S2old), T(S2new), T(S3))
    assert at(S2new, 'f2x_036') == 8
    # 뒷면 3타
    B1 = [('b1_009', 2), ('b1_015', 1), ('b1_024', 2), ('b1_027', 1), ('b1_029', 1), ('b1_031', 1)] + [('b1_033', 4)] \
         + [('b1_036', 2), ('b1_040', 3), ('b1_044', 3), ('b1_048', 10)]
    B2 = [('b2x_003', 1), ('b2x_012', 1), ('b2x_024', 2), ('b2x_030', 1), ('b2x_033', 1), ('b2x_036', 2)] + [('b2x_042', 4)] \
         + [('b2x_051', 1), ('b2x_054', 1), ('b2x_057', 1), ('b2x_060', 2)] + [('br_009', 1), ('br_012', 1), ('br_015', 1), ('br_018', 1), ('br_021', 2), ('br_024', 2), ('br_030', 5)]
    B3 = [('b3_003', 1), ('b3_009', 1), ('b3_012', 1), ('b3_015', 1), ('b3_018', 2), ('b3_021', 2), ('b3_024', 1), ('b3_026', 1), ('b3_028', 1)] + [('b3_030', 4)] \
         + [('b3_033', 2), ('b3_036', 3), ('b3_040', 4), ('b3_044', 4), ('b3_048', 17)]
    assert (T(B1), T(B2), T(B3)) == (30, 30, 45), (T(B1), T(B2), T(B3))
    assert (at(B1, 'b1_033'), at(B2, 'b2x_042'), at(B3, 'b3_030')) == (8, 8, 11)
    def part(k):
        if isinstance(k, str):
            p = k.split('_')[0]
            return {'f2x': '2타 가로베기(새)', 'c2': '2타(지난)', 'm': '2타(지난)', 'b1': '뒷면 1타', 'b2x': '뒷면 2타 가로', 'br': '뒷면 되돌려베기', 'b3': '뒷면 3타'}[p]
        return '1타' if k < 72 else ('되돌려베기' if k < 150 else '3타')
    fr.part = part
    E = fr.expand
    one_old, one_new = E(S1 + S2old + S3), E(S1 + S2new + S3)
    a, c = fr.pad(one_old, one_new); seq = list(zip(a, c)); seq = seq + [seq[-1]] * 30
    slow = [x for x in seq for _ in range(2)]
    fr.render([(game3, '정면 · 지난 2타 (칼끝이 카메라 쪽)'), (game3, '정면 · 새 2타 (몸 앞 옆으로 크게)')], seq + seq + slow, '../fc3/정면_새2타_비교.mp4')
    back = E(B1 + B2 + B3); bs = [(k,) for k in back] + [(back[-1],)] * 30
    bslow = [x for x in bs for _ in range(2)]
    fr.render([(game3, '뒷면 3타 (처음) · 1타 내려베기 · 2타 가로+되돌려 · 3타 내려찍기')], bs + bs + bslow, '../fc3/뒷면_3타_가안.mp4')
    print('ok 정면 2타', T(S2new), '뒷면', T(B1), T(B2), T(B3))
