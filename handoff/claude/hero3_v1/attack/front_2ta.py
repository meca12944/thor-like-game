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
    def plan(seq):
        out = []; t0 = None
        for n, k in enumerate(seq):
            if t0 is None and k == 'c2_014': t0 = n
            if t0 is None or n - t0 >= 34: out.append(None); continue
            t = n - t0; g = 1 - (1 - min(t + 1, 24) / 24) ** 2; f = 1.0 if t < 24 else 1 - (t - 24) / 10
            out.append((g, f))
        return out
    part0 = fr.part
    def part(k):
        if isinstance(k, str): return '2타 가로베기(그록 다시)'
        return part0(k)
    fr.part = part
    cut_old = [k for k in fr.expand(fr.ORIG) if 60 <= k <= 120]
    cut_new = [k for k in fr.expand(NEW2) if isinstance(k, str) or 60 <= k <= 120]
    a, c = fr.pad(cut_old, cut_new); GP = plan(c)
    one = list(range(len(a))); slow = [x for x in one for _ in range(2)]
    idx = one + [one[-1]] * 20 + one + [one[-1]] * 20 + slow
    seq = [(a[i], (c[i], i), (c[i], i)) for i in idx]
    plain = lambda kc: game2(kc[0])
    withA = lambda kc: fr.draw_ground(game2(kc[0]), GP[kc[1]])
    lab = lambda n: '제 빠르기' if n < 2 * (len(one) + 20) else '반 빠르기(천천히 보기)'
    fr.render([(game2, '전 2타 (그록 1차)'), (plain, '새 2타 (그록 다시: 칼끝이 카메라 쪽)'), (withA, '새 2타 + 땅 위 큰 검흔(A안)')], seq, '../fc2/정면2타_그록다시_비교.mp4', note=lab)
    # 전체 콤보 (새 2타 + 검흔)
    a2, f2 = fr.pad(fr.expand(fr.ORIG), fr.expand(NEW2)); GPf = plan(f2)
    withAf = lambda kc: fr.draw_ground(game2(kc[0]), GPf[kc[1]])
    s2 = [(a2[i], (f2[i], i)) for i in range(len(a2))]; s2 = s2 + [s2[-1]] * 30 + s2
    fr.render([(fr.grok, '그록 원본 콤보 (전 2타)'), (withAf, '새 2타 넣은 콤보 + 2타 검흔')], s2, '../fc2/정면콤보_새2타.mp4')
    print('ok', '새 2타', sum(n for _, n in H2N), '칸')
