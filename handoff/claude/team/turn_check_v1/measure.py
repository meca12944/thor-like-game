# 8방향 제자리 돌기 검사 (모션 담당 부탁 b): 방향마다 머리 꼭대기·눈 높이·얼굴(피부) 크기·어깨 폭을 숫자로 (모든 장 평균과 흔들림)
import numpy as np, json, glob, sys
from PIL import Image
from common import load, skinmask
FEET = 189
DIRS = [('↓', 'walk_s2', 'run_s', False), ('↘', 'walk_se', 'run_se2', False), ('→', 'walk_r2', 'run_r2', False), ('↗', 'walk_ne', 'run_ne2', False), ('↑', 'walk_up', 'run_n', False)]
def meas(a):
    al = a[..., 3] > 40; ys, xs = np.nonzero(al); crown = ys.min(); bottom = ys.max(); H = FEET - crown
    sk = skinmask(a); sy, sx = np.nonzero(sk); face = None; eye = None
    if len(sy) > 15:
        y0, y1, x0, x1 = sy.min(), sy.max(), sx.min(), sx.max(); face = dict(h=int(y1 - y0 + 1), w=int(x1 - x0 + 1), cx=float(sx.mean()))
        lum = a[..., :3].astype(int).sum(2); box = np.zeros_like(al); box[y0:y0 + int((y1 - y0) * .7) + 1, x0:x1 + 1] = True
        dark = box & (lum < 170) & al & ~sk  # eye pixels: dark marks inside the upper face
        rows = dark.sum(1); eye = int(np.argmax(rows)) if rows.max() >= 2 else None
    sh_row = crown + int(round(H * .24)); row = al[sh_row]; xs_r = np.nonzero(row)[0]; shoulder = int(xs_r.max() - xs_r.min() + 1) if len(xs_r) else 0
    return dict(crown=int(crown), height=int(H), eye_y=eye, eye_from_crown=int(eye - crown) if eye is not None else None, face=face, shoulder=shoulder, bottom=int(bottom))
out = {}
for arrow, w, r, _ in DIRS:
    for kind, d in (('걷기', w), ('달리기', r)):
        M = [meas(load(f)) for f in sorted(glob.glob(f'{d}/[0-9][0-9][0-9].png'))]
        g = lambda k: [m[k] for m in M if m[k] is not None]
        fh = [m['face']['h'] for m in M if m['face']]; fw = [m['face']['w'] for m in M if m['face']]
        out[f'{kind} {arrow}'] = dict(src=d, n=len(M), crown=[min(g('crown')), max(g('crown'))], height_avg=round(float(np.mean(g('height'))), 1), eye_from_crown=[min(g('eye_from_crown')), max(g('eye_from_crown'))] if g('eye_from_crown') else None,
            face_h=[min(fh), max(fh)] if fh else None, face_w=[min(fw), max(fw)] if fw else None, shoulder=[min(g('shoulder')), max(g('shoulder'))])
json.dump(out, open('turn_measure.json', 'w'), ensure_ascii=False, indent=1, default=int)
print(f"{'':10s} {'키(발189-꼭대기)':>14s} {'꼭대기y':>9s} {'눈(꼭대기에서)':>12s} {'얼굴 높이':>9s} {'얼굴 폭':>8s} {'어깨줄 폭':>9s}")
for k, v in out.items(): print(f"{k:10s} {v['height_avg']:>14} {str(v['crown']):>9s} {str(v['eye_from_crown']):>12s} {str(v['face_h']):>9s} {str(v['face_w']):>8s} {str(v['shoulder']):>9s}")
