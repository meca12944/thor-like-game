"""female_proportions_v2.csv + female_vs_hero_v2.png from pixel measurements of the final sprites."""
import sys, os, json, csv, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from measure_fem import measure, C, O
from build_fem import NAMES
from PIL import Image, ImageDraw, ImageFont
F = lambda s: ImageFont.truetype('/usr/share/fonts/truetype/sand-box/google/Nanum Gothic/NanumGothic-Bold.ttf', s)
rows = []; M = {}
for name, cells in C.items():
    sh = np.asarray(Image.open(O + f'assets/idle_{name}.png')).astype(float); sh[..., 3] /= 255
    for v, (x, y, w, h, ax, ay) in cells.items():
        m = measure(sh[y:y + h, x:x + w], v, f'{name}.{v}'); M[(name, v)] = m
ref = M[('hero', 'front')]
def ok(a, b, tol=1): return '' if a is None or b is None else ('PASS' if abs(a - b) <= tol else 'FAIL')
fields = ['id', 'name', 'view', 'crown_row', 'chin_row', 'split_row', 'sole_row(baseline)', 'total_h', 'head_h', 'heads_tall', 'legs_px', 'leg_ratio', 'shoulder_w',
          'd_total_vs_hero', 'd_head_vs_hero', 'd_legs_vs_hero', 'd_baseline_vs_hero', 'shoulder_vs_hero', 'result', 'note']
with open(O + 'female_proportions_v2.csv', 'w', newline='') as fh:
    wr = csv.writer(fh); wr.writerow(fields)
    for (name, v), m in M.items():
        notes = []
        if v == 'back': notes.append('head: face hidden in back view (not measurable)')
        if v == 'side': notes.append('legs overlap in side view (split not measurable)')
        if name in ('h_mystic', 'g_dancer') and v != 'side': notes.append('long sheer/wrap skirt covers the leg gap -> visible split lower than the remapped crotch')
        if name == 'hero' and v == 'back' and m['split'] and m['split'] != ref['split']: notes.append('1-px leg seam closes in the 8:1 downsample -> visible gap starts lower')
        dt = m['H'] - ref['H']; dh = (m['head'] - ref['head']) if m['head'] else None; dl = (m['legs'] - ref['legs']) if m['legs'] else None; db = m['sole'] - ref['sole']
        res = [ok(m['H'], ref['H']), ok(m['head'], ref['head']), ok(m['legs'], ref['legs']), ok(m['sole'], ref['sole'])]
        result = 'FAIL' if 'FAIL' in res else 'PASS'
        wr.writerow([name, NAMES[name], v, m['crown'], m['chin'], m['split'], m['sole'], m['H'], m['head'], m['heads'], m['legs'], m['leg_ratio'], m['shoulder'],
                     dt, dh, dl, db, round(m['shoulder'] / M[('hero', v)]['shoulder'], 2), result, '; '.join(notes)])
        rows.append((name, v, m, result))
# sheet: hero + each woman, front/side/back, x5, landmark lines across
S = 5; names = list(C); VW = 32 * S + 6; colw = 3 * VW + 30
img = Image.new('RGB', (40 + len(names) * colw, 56 * S + 200), (34, 38, 44)); d = ImageDraw.Draw(img)
top = 70; d.text((10, 8), 'Hero FRONT idle = reference.  crown row 0 / chin row %d / leg split row %d / baseline row %d  (56 px tall, head %d px = %.2f heads, legs %d px = %.3f)' % (ref['chin'], ref['split'], ref['sole'], ref['head'], ref['heads'], ref['legs'], ref['leg_ratio']), font=F(20), fill='white')
for yy, col in ((0, (255, 230, 80)), (ref['chin'] + 1, (255, 90, 90)), (ref['split'], (80, 200, 255)), (ref['sole'] + 1, (255, 255, 255))):
    d.line((0, top + yy * S, img.width, top + yy * S), fill=col)
for i, n in enumerate(names):
    sh = Image.open(O + f'assets/idle_{n}.png'); x = 40 + i * colw
    for j, v in enumerate(('front', 'side', 'back')):
        cx, cy, w, h, ax, ay = C[n][v]; t = sh.crop((cx, cy, cx + w, cy + h)).resize((w * S, h * S), Image.NEAREST)
        img.paste(t, (x + j * VW, top + (56 - h) * S), t)
    r = [rr for rr in rows if rr[0] == n]; ff = 'FAIL' if any(rr[3] == 'FAIL' for rr in r) else 'PASS'
    d.text((x, top + 56 * S + 10), NAMES[n], font=F(18), fill='white')
    fm = M[(n, 'front')]; d.text((x, top + 56 * S + 34), f"H {fm['H']} head {fm['head']} legs {fm['legs']}", font=F(15), fill=(220, 220, 220))
    d.text((x, top + 56 * S + 54), f"shoulder {fm['shoulder']}px ({fm['shoulder'] / ref['shoulder']:.2f}x)", font=F(15), fill=(220, 220, 220))
    d.text((x, top + 56 * S + 76), ff, font=F(18), fill=(140, 255, 140) if ff == 'PASS' else (255, 140, 140))
img.save(O + 'female_vs_hero_v2.png'); print(img.size)
for r in rows: print(r[0], r[1], r[3], {k: r[2][k] for k in ('H', 'head', 'legs', 'sole', 'shoulder')})
