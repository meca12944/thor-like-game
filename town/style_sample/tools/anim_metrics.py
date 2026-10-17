"""Per-frame measurement of the women's idle/walk sheets: baseline (sole row), crown row, head-band centroid x,
torso centroid x; frame-to-frame jitter. -> fem_anim_metrics.csv"""
import json, csv, numpy as np
from PIL import Image
S = '/workspace/town-demo/style_sample/'
meta = json.load(open(S + 'assets/walk_meta.json'))
rows = []; summ = []
for n, m in meta.items():
    sh = np.asarray(Image.open(S + f'assets/walk_{n}.png')); cw, ch = m['cw'], m['ch']
    for r, d in enumerate(m['rows']):
        for anim, (a, k) in (('idle', m['idle']), ('walk', m['walk'])):
            cs = []
            for i in range(k):
                c = sh[r * ch:(r + 1) * ch, (a + i) * cw:(a + i + 1) * cw, 3] > 0
                ys = np.where(c.sum(1) >= 2)[0]; crown, sole = ys[0], ys[-1]
                hb = c[crown:crown + 13]; hx = np.where(hb)[1].mean()
                tb = c[14 + 1:36 + 1]; tx = np.where(tb)[1].mean()
                rows.append([n, d, anim, i, int(sole), int(crown), int(sole - crown + 1), round(hx, 2), round(tx, 2)]); cs.append((sole, crown, hx, tx))
            cs = np.array(cs, float)
            dj = np.abs(np.diff(np.vstack([cs, cs[:1]]), axis=0))
            summ.append([n, d, anim, k, int(np.ptp(cs[:, 0])), int(np.ptp(cs[:, 1])), round(dj[:, 2].max(), 2), round(dj[:, 3].max(), 2)])
with open(S + 'fem_anim_metrics.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['id', 'dir', 'anim', 'frame', 'sole_row', 'crown_row', 'height', 'head_cx', 'torso_cx'])
    w.writerows(rows); w.writerow([])
    w.writerow(['SUMMARY id', 'dir', 'anim', 'frames', 'baseline_range_px', 'crown_range_px', 'max_head_dx_px', 'max_torso_dx_px']); w.writerows(summ)
for s in summ: print(s)
