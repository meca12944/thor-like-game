# 찍은 낱장(2배) → 웹 시험판용: 낱장마다 빈 곳 잘라 4096 판(WebP)에 빽빽이 + web_atlas.json
# 쓰는 법: python3 pack_web.py <proj> <출력 폴더> [줄임=0.375]
import glob, json, os, sys
from PIL import Image

proj, dst = sys.argv[1], sys.argv[2]
SC = float(sys.argv[3]) if len(sys.argv) > 3 else 0.375
SKIP = {'Walk'}
src = os.path.join(proj, 'bake')
os.makedirs(dst, exist_ok=True)
meta = None
for jf in sorted(glob.glob(os.path.join(src, 'bake_*.json'))):
    m = json.load(open(jf))
    if meta is None:
        meta = m
    else:
        for n, a in m['anims'].items():
            meta['anims'][n]['tips'].update(a['tips'])
ox, oy = meta['origin'][0] * SC, meta['origin'][1] * SC
DIRS = ['down', 'right', 'up', 'left']
P = 4096
pages, cur = [], None
x = y = shelf = 0
out = {'fps': meta['fps'], 'ppu': meta['px'] * SC / meta['cam_size'], 'anims': {}, 'pages': []}

def new_page():
    global cur, x, y, shelf
    cur = Image.new('RGBA', (P, P)); pages.append(cur); x = y = shelf = 0

new_page()
for n, a in meta['anims'].items():
    if n in SKIP:
        continue
    nf = a['frames']
    ent = {'frames': nf, 'dirs': {}}
    for d in DIRS:
        fr = []
        for f in range(nf):
            im = Image.open(os.path.join(src, f'{n}_{d}_{f:03d}.png')).convert('RGBA')
            im = im.resize((round(im.width * SC), round(im.height * SC)), Image.LANCZOS)
            bb = im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox() or (0, 0, 1, 1)
            bb = (max(bb[0] - 1, 0), max(bb[1] - 1, 0), min(bb[2] + 1, im.width), min(bb[3] + 1, im.height))
            c = im.crop(bb); w, h = c.size
            if x + w > P:
                x = 0; y += shelf; shelf = 0
            if y + h > P:
                new_page()
            cur.paste(c, (x, y))
            t = a['tips'][d][f]
            # [판, x, y, w, h, 발 기준 x, y, 칼밑 x, y, 칼끝 x, y] (칼 자리는 발 기준, px)
            fr.append([len(pages) - 1, x, y, w, h, round(ox - bb[0], 1), round(oy - bb[1], 1),
                       round(t[0] * SC - ox, 1), round(t[1] * SC - oy, 1), round(t[2] * SC - ox, 1), round(t[3] * SC - oy, 1)])
            x += w + 1; shelf = max(shelf, h + 1)
        ent['dirs'][d] = fr
    out['anims'][n] = ent
    print(n, nf, '장 ×4')
for i, pg in enumerate(pages):
    bb = pg.getbbox()
    pg = pg.crop((0, 0, P, bb[3])) if bb else pg
    fn = f'hero_{i}.webp'
    pg.save(os.path.join(dst, fn), 'WEBP', quality=88, method=6)
    out['pages'].append(fn)
    print(fn, pg.size, round(os.path.getsize(os.path.join(dst, fn)) / 1e6, 2), 'MB')
json.dump(out, open(os.path.join(dst, 'hero.json'), 'w'), separators=(',', ':'))
print('json', round(os.path.getsize(os.path.join(dst, 'hero.json')) / 1e3), 'KB')
