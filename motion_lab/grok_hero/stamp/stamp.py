# 새 그록 주인공 얼굴 도장 (옛 hero8_face_v1 facefix.place2 를 옮김): 피부 기준을 새 주인공 색(어두운 피부, 가죽은 채도 높음)으로, 크기 맞추기 추가
#  자리 찾기 = 지금 그림의 피부(구멍 채움)와 도장 피부가 가장 많이 겹치는 곳 (IoU), 낮으면 안 찍음
#  찍는 법 A = 얼굴 + 둘레 2칸(앞머리까지 통째, 옛 방식) / B = 지금 그림에서도 피부였던 곳만 (앞을 가리는 머리카락·손은 남김)
import numpy as np, json, glob, sys
from PIL import Image
from scipy import ndimage
from common import load, skinmask, face
def ref_head(a, grow=2, smax=.48):
    m = ndimage.binary_closing(ndimage.binary_fill_holes(skinmask(a, smax=smax)), iterations=2); core = m.copy()
    m = ndimage.binary_dilation(m, iterations=grow) & (a[..., 3] > 40); ys, xs = np.nonzero(m); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return a[y0:y1, x0:x1].copy(), m[y0:y1, x0:x1], core[y0:y1, x0:x1]
def scale_stamp(P, M, C, k):
    if abs(k - 1) < .08: return P, M, C
    h, w = M.shape; W, H = max(1, round(w * k)), max(1, round(h * k)); r = lambda x, mode: np.array(Image.fromarray(x).resize((W, H), mode))
    return r(P, Image.NEAREST), r(M.astype(np.uint8) * 255, Image.NEAREST) > 0, r(C.astype(np.uint8) * 255, Image.NEAREST) > 0
def place(a, P, M, C, mode='A', maxd=7, thr=.5):
    sm = ndimage.binary_fill_holes(skinmask(a)); f = face(a)
    if f is None: return a, None, None
    cy, cx = f[0], f[1]; h, w = M.shape; best = (-1, None)
    for dy in range(-maxd, maxd + 1):
        for dx in range(-maxd, maxd + 1):
            y0, x0 = cy - h // 2 + dy, cx - w // 2 + dx
            if y0 < 0 or x0 < 0 or y0 + h > a.shape[0] or x0 + w > a.shape[1]: continue
            win = sm[y0:y0 + h, x0:x0 + w]; sc = (win & C).sum() / max(1, (win | C).sum())
            if sc > best[0]: best = (sc, (y0, x0))
    if best[0] < thr: return a, round(best[0], 2), None
    y0, x0 = best[1]; o = a.copy(); reg = o[y0:y0 + h, x0:x0 + w]
    put = M if mode == 'A' else (C & ndimage.binary_dilation(sm[y0:y0 + h, x0:x0 + w], iterations=1))
    if mode == 'D':  # 10-25 모션: 얼굴+둘레 통째(A) + 도장 피부색만 이 장 피부 밝기에 맞춤(눈·눈썹·머리카락 색은 그대로)
        sk = skinmask(a); tgt = a[sk][:, :3].mean(0) if sk.any() else None; ps = C & (P[..., 3] > 200)
        Q = P.copy()
        if tgt is not None and ps.any():
            src = P[ps][:, :3].mean(0); L = P[..., :3].astype(float).mean(2); skin = ps & (L > 60)
            Q[skin, :3] = np.clip(P[skin, :3] * (tgt / np.maximum(src, 1)), 0, 255).astype(np.uint8)
        reg[M] = Q[M]; return o, round(best[0], 2), (y0, x0)
    if mode == 'C':  # B + 밝기 맞추기: 도장 피부 평균을 이 장의 피부 평균에 맞춤 (조명·명암이 장마다 달라 도장만 밝아 보이는 것 막기)
        put = C & ndimage.binary_dilation(sm[y0:y0 + h, x0:x0 + w], iterations=1); tgt = a[skinmask(a)][:, :3].mean(0); src = P[C & (P[..., 3] > 200)][:, :3].mean(0)
        Q = P.copy(); Q[..., :3] = np.clip(P[..., :3] * (tgt / np.maximum(src, 1)), 0, 255).astype(np.uint8); reg[put] = Q[put]; return o, round(best[0], 2), (y0, x0)
    reg[put] = P[put]; return o, round(best[0], 2), (y0, x0)
if __name__ == '__main__':
    REF = {'walk_r2': 'ref_frames_walk_right_000.png', 'run_se2': 'ref_se_test_walk_se_000.png', 'run_s': 'ref_frames_walk_down_000.png'}
    out = {}
    for d, rf in REF.items():
        ra = load(rf); P, M, C = ref_head(ra); ref_area = face(ra)[2]
        for f in sorted(glob.glob(f'{d}/[0-9][0-9][0-9].png')):
            a = load(f); fc = face(a); k = (fc[2] / ref_area) ** .5 if fc else 1
            for mode in 'ABC':
                P2, M2, C2 = scale_stamp(P, M, C, k); o, sc, at = place(a, P2, M2, C2, mode)
                Image.fromarray(o).save(f.replace('.png', f'_{mode}.png')); out[f + ':' + mode] = dict(iou=sc, at=at, size_k=round(k, 2), stamped=at is not None)
    json.dump(out, open('stamp_result.json', 'w'), indent=1)
    for d in REF:
        for mode in 'ABC':
            r = [v for k, v in out.items() if k.startswith(d + '/') and k.endswith(':' + mode)]
            print(d, mode, '찍음', sum(v['stamped'] for v in r), '/', len(r), 'IoU', [v['iou'] for v in r], '크기비', sorted(set(v['size_k'] for v in r)))
