# 정면 2타 다시(그록 11-01 「정면 2타 다시」 메인 m + 후보2 c2, 720) → 게임 그림 + 비교 영상
# 그록 추천대로 섞음: 후보2 13~21장(시작 → 칼끝이 카메라를 가리키는 한가운데, 머리 위로 안 올라감) + 메인 28~48장(한가운데 → 오른쪽으로 쭉 뻗은 끝)
#  이음새: w_all 72장 ≈ c2 0장(겹침 0.97), c2 21장 ≈ m 28장(0.96), m 48장 ≈ w_all 102장(0.97) → 앞뒤 콤보와 그대로 이어짐
# 칼: 칼끝이 카메라를 가리키는 장(c2 17~21, m 28~31)은 그록 분홍이 코등이만 보여 각도를 못 잡음 → 아래(카메라 쪽)로 아주 짧게(0.15배).
#     오른쪽으로 펼쳐지는 장은 그록 분홍 칼날 길이 / 끝 자세(m 48) 칼날 길이 만큼 짧게 → 원근(카메라 쪽 → 옆)이 그대로 보임
# 검흔(A안): 휙 하는 동안 몸 앞 땅 위 반원이 왼쪽 → 앞 → 오른쪽으로 자라고 옅어짐
# 쓰는 법: python3 front_2ta.py <w_all 작업 폴더(fc: body/, grip.json, w/)> <2타 다시 작업 폴더(fc2: c2/, m/)>
import sys, os, json, importlib.util, numpy as np
from PIL import Image, ImageDraw
from multiprocessing import Pool
FC, F2 = sys.argv[1].rstrip('/') + '/', sys.argv[2].rstrip('/') + '/'
HERE = os.path.dirname(os.path.abspath(__file__))
def load(name, argv):
    sys.argv = ['x'] + argv
    sp = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py')); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
NEED = [('c2', k) for k in range(0, 22)] + [('m', k) for k in range(28, 49)]
MIDS = {('c2', k) for k in range(17, 22)} | {('m', k) for k in range(28, 32)}
def job(x):
    fp = load('front_proc', [F2]); return fp.one((x[0], 720, x[1]))
if __name__ == '__main__':
    if not os.path.exists(F2 + 'grip2.json'):
        with Pool(4) as P: res = P.map(job, NEED)
        # 자리 맞춤: c2 0장 몸 그림을 w_all 72장 몸 그림(300판)과 발 높이·가운데로 맞춤
        b72 = Image.open(FC + 'body/072.png').getbbox(); b0 = Image.fromarray(res[0][1]).getbbox()
        ox, oy = round((b72[0] + b72[2]) / 2 - (b0[0] + b0[2]) / 2), b72[3] - b0[3]
        os.makedirs(F2 + 'body2', exist_ok=True); G = {}
        full = None
        for (src, k), (row, out) in zip(NEED, res):
            cv_ = Image.new('RGBA', (300, 300)); im = Image.fromarray(out); cv_.paste(im, (ox, oy), im); cv_.save(F2 + f'body2/{src}_{k:03d}.png')
            row['guard'] = [row['guard'][0] + ox, row['guard'][1] + oy]; G[f'{src}_{k}'] = row
        full = G['m_48']['blade']
        for key, r in G.items():
            src, k = key.split('_'); k = int(k)
            if (src, k) in MIDS: r['ang'] = 90.0; r['s'] = .15; r['behind'] = False
            else: r['s'] = float(min(1.0, r['blade'] / full)) if r['blade'] < .9 * full else 1.0
        json.dump(dict(frames=G, offset=[ox, oy], full=full), open(F2 + 'grip2.json', 'w'), indent=0)
        print('맞춤', ox, oy, '끝 자세 칼날', round(full, 1))
    G = json.load(open(F2 + 'grip2.json'))['frames']
    fr = load('front_render', [FC])
    for key, r in G.items(): print(key, [round(v) for v in r['guard']], round(r['ang']), round(r['blade']), round(r.get('s', 1), 2), 'B' if r['behind'] else '')
    # 새 몸 그림·칼 자리를 front_render 에 끼워 넣기: 이름표 'c2_17' 같은 글자 키
    def body(k):
        return Image.open(F2 + f'body2/{k}.png' if isinstance(k, str) else FC + f'body/{k:03d}.png')
    cache = {}
    def game2(k):
        if k in cache: return cache[k]
        if isinstance(k, str):
            src, n = k.split('_'); r = dict(G[f'{src}_{int(n)}']); s0 = r.get('s', 1.0)
            hd = fr.H1; im, hx, hy, L = hd
            if s0 < .999:
                im2 = im.resize((im.width, max(1, round(im.height * s0))), Image.NEAREST); hd = (im2, hx, hy * s0, L * s0)
            cache[k] = fr.comp(fr.clean(body(k), 0), r, hd, fr.RA)
        else: cache[k] = fr.game(k)
        return cache[k]
    K2 = lambda src, ks: [f'{src}_{k:03d}' for k in ks]
    # 새 2타 칸 수(60장/초): 1타 끝 자세에서 잠깐 감기 → 휙 시작 → 칼끝이 카메라 → 오른쪽으로 쭉 → 끝 자세 멈춤
    H2N = [('c2_013', 4), ('c2_014', 2), ('c2_015', 2), ('c2_016', 2), ('c2_017', 2), ('c2_019', 2), ('c2_021', 3),
           ('m_029', 2), ('m_031', 2), ('m_032', 2), ('m_033', 2), ('m_034', 2), ('m_035', 2), ('m_036', 2), ('m_037', 2), ('m_038', 3),
           ('m_040', 3), ('m_042', 3), ('m_044', 3), ('m_046', 3), ('m_048', 6)]
    NEW2 = [x for x in fr.ORIG if x[0] < 72] + H2N + [x for x in fr.ORIG if 102 < x[0] <= 108] + fr.rest(108)
    def plan(seq, grow=24):
        out = []; t0 = None
        for n, k in enumerate(seq):
            if t0 is None and k == 'c2_014': t0 = n
            if t0 is None or n - t0 >= grow + 10: out.append(None); continue
            t = n - t0; g = 1 - (1 - min(t + 1, grow) / grow) ** 2; f = 1.0 if t < grow else 1 - (t - grow) / 10
            out.append((g, f))
        return out
    part0 = fr.part
    def part(k):
        if isinstance(k, str): return '2타 가로베기(그록 다시)'
        return part0(k)
    fr.part = part
    # 2타 → 3타 사이 짧게 (사장님 11-01 「2타에서 3타까지 너무 길다 짧아야되」): 2타 끝 자세 짧게 → 되돌려베기를 빠르게(1틱씩) →
    #  되돌려베기 뒤 1초 서 있기(144~168장)를 4틱으로 → 칼 들기(168~182)도 1틱씩 → 머리 위에서 잠깐(6틱) → 내려찍기
    TAIL = [('m_048', 3)] + [(k, 1) for k in range(109, 135, 2)] + [(135, 2), (137, 2), (140, 2), (144, 2), (156, 2), (168, 1)] \
           + [(k, 1) for k in range(170, 183, 2)] + [(182, 6)] + [x for x in fr.ORIG if x[0] > 182 and x[0] not in fr.SKIP]
    NEW3 = [x for x in fr.ORIG if x[0] < 72] + H2N[:-1] + TAIL
    # 1타도 짧게 (사장님 11-01 「1타도 줄여」): 서기 6틱 → 오른 어깨로 감기(1~2틱씩, 22장에서 3틱 버팀) → 머리 위를 넘어 왼쪽 아래로 휙(24~34장 1틱씩) → 멈춤(37~46장) → 1타 끝 자세 버티기(46~72장, 1.1초)는 빼고 바로 2타
    H1F = [(0, 4), (6, 2)] + [(10, 1), (12, 1), (14, 1), (16, 1), (18, 2), (20, 2), (22, 3)] + [(k, 1) for k in range(24, 35)] \
          + [(35, 1), (36, 2), (38, 1), (40, 1), (42, 2), (44, 2), (46, 2)]
    NEW4 = H1F + H2N[:-1] + TAIL
    def hit_secs(L):
        e = [k for k, n in L for _ in range(n)]
        i2 = e.index('c2_014'); i3 = e.index(109); i4 = next(i for i, k in enumerate(e) if isinstance(k, int) and k >= 192)
        return [round(i2 / 60, 2), round((i3 - i2) / 60, 2), round((i4 - i3) / 60, 2), round((len(e) - i4) / 60, 2), round(len(e) / 60, 2)]
    # 3타 모두 같은 길이 (사장님 11-01 「3타 전부 똑같은 프레임으로 휘둘러야지」): 1타 = 내려베기, 2타 = 가로베기 + 되돌려베기, 3타 = 내려찍기
    #  → 세 타 모두 42틱(0.7초), 휘두르는 장은 모두 1틱씩(같은 빠르기), 감기·멈춤만 2~4틱
    HIT = 42
    E1 = [(0, 3), (6, 2)] + [(10, 1), (12, 1), (14, 1), (16, 1), (18, 2), (20, 2), (22, 3)] + [(k, 1) for k in range(24, 35)] \
         + [(35, 1), (36, 2), (38, 1), (40, 2), (42, 2), (44, 2), (46, 5)]
    E2 = [('c2_013', 3), ('c2_014', 1), ('c2_015', 1), ('c2_016', 1), ('c2_017', 1), ('c2_019', 1), ('c2_021', 2)] \
         + [(f'm_{k:03d}', 1) for k in (29, 31, 32, 33, 34, 35, 36)] + [('m_038', 2), ('m_042', 2), ('m_048', 2)] \
         + [(k, 1) for k in range(109, 135, 2)] + [(135, 1), (137, 1), (140, 2), (144, 2)]
    E3 = [(156, 1), (168, 1)] + [(k, 1) for k in range(170, 182, 2)] + [(182, 4)] \
         + [(192, 1), (194, 1), (196, 1), (198, 1), (200, 2), (202, 2), (204, 2)] \
         + [(208, 2), (212, 2), (216, 2), (220, 2), (224, 2), (228, 2), (232, 2), (240, 2), (252, 4)]
    tk = lambda L: sum(n for _, n in L)
    assert tk(E1) == tk(E2) == tk(E3) == HIT, (tk(E1), tk(E2), tk(E3))
    NEW5 = E1 + E2 + E3
    def hits3(L):
        e = [k for k, n in L for _ in range(n)]
        i2 = e.index('c2_013'); i3 = next(i for i, k in enumerate(e) if isinstance(k, int) and k >= 150)
        return [round(i2 / 60, 2), round((i3 - i2) / 60, 2), round((len(e) - i3) / 60, 2), round(len(e) / 60, 2)]
    print('1타 · 2타(가로+되돌려) · 3타(내려찍기) · 전체(초): 지난 판', hits3(NEW4), '→ 같은 길이 판', hits3(NEW5))
    # 옆모습과 똑같이 (사장님 11-01 「옆모습이랑 똑같이 맞춰」): 옆 게임 공격과 같은 길이 1타 30 · 2타 30 · 3타 45틱,
    #  칼이 맞는 장(판정)도 옆과 같은 틱(8 · 8 · 11)에 시작 — 1타 = 30장(칼이 몸 앞을 가로지름), 2타 = c2 21장(칼끝이 카메라), 3타 = 198장(내려쳐 맞음)
    S1 = [(6, 1), (10, 1), (14, 1), (18, 1), (22, 2), (26, 1), (28, 1)] + [(30, 1)] \
         + [(31, 1), (32, 1), (33, 1), (34, 1), (35, 1), (36, 1), (38, 2), (40, 2), (42, 2), (44, 2), (46, 7)]
    S2 = [('c2_013', 3), ('c2_014', 1), ('c2_015', 1), ('c2_016', 1), ('c2_017', 2)] + [('c2_021', 1)] \
         + [(f'm_{k:03d}', 1) for k in (29, 31, 32, 33, 34, 36, 38, 42, 48)] \
         + [(k, 1) for k in (109, 113, 117, 121, 125, 129, 133)] + [(137, 1), (140, 1), (144, 3)]
    S3 = [(156, 1), (168, 1), (172, 1), (176, 1), (180, 1), (182, 3), (192, 1), (194, 1), (196, 1)] + [(198, 1)] \
         + [(k, 2) for k in (200, 202, 204, 206, 208, 212, 216, 220, 224, 228, 232, 236, 240, 246)] + [(252, 5)]
    def hit_tick(L, key):
        t = 0
        for k, n in L:
            if k == key: return t
            t += n
    assert (tk(S1), tk(S2), tk(S3)) == (30, 30, 45), (tk(S1), tk(S2), tk(S3))
    assert (hit_tick(S1, 30), hit_tick(S2, 'c2_021'), hit_tick(S3, 198)) == (8, 8, 11)
    NEW6 = S1 + S2 + S3
    print('옆과 같은 판: 1타', tk(S1), '· 2타', tk(S2), '· 3타', tk(S3), '틱, 맞는 장', (8, 8, 11), '틱 · 전체', round(tk(NEW6) / 60, 2), '초')
    a2, f2 = fr.pad(fr.expand(NEW5), fr.expand(NEW6)); GA_, GB_ = plan(a2, grow=12), plan(f2, grow=8)
    left = lambda kc: fr.draw_ground(game2(kc[0]), GA_[kc[1]]); right = lambda kc: fr.draw_ground(game2(kc[0]), GB_[kc[1]])
    def part3(k):
        if isinstance(k, str): return '2타'
        return '1타' if k < 72 else ('2타' if k < 150 else '3타')
    fr.part = part3
    s2 = [((a2[i], i), (f2[i], i)) for i in range(len(a2))]; one = s2 + [s2[-1]] * 30
    fr.render([(left, '지난 판 (셋 다 0.7초)'), (right, '옆모습과 같게 (0.5 · 0.5 · 0.75초)')], one + one, '../fc2/정면콤보_옆과같게.mp4')
    print('ok')
