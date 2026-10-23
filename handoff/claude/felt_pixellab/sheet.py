"""Contact sheet of out/assets: every asset, both seeds side by side, on grey (150,150,155), 2x nearest."""
import os, sys
from PIL import Image, ImageDraw
D = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(D, 'out', 'assets')
sys.path.insert(0, D); from specs import ASSETS
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, 'assets_sheet.png')
cells = []
for aid, (w, h), _ in ASSETS:
    ims = [Image.open(os.path.join(A, f'{aid}_s{s}.png')).convert('RGBA') if os.path.exists(os.path.join(A, f'{aid}_s{s}.png')) else None for s in (101, 202)]
    cells.append((aid, w, h, ims))
CW = max(w for _, w, _, _ in cells) * 2 * 2 + 30; rows = []
y = 0; can = Image.new('RGB', (CW * 2, 10), (40, 40, 44))
pos = []; x = 0; rowh = 0
for aid, w, h, ims in cells:
    cw = w * 4 + 30
    if x + cw > CW * 2: x = 0; y += rowh + 24; rowh = 0
    pos.append((aid, x, y, ims, w, h)); x += cw; rowh = max(rowh, h * 2)
can = Image.new('RGB', (CW * 2, y + rowh + 30), (40, 40, 44)); d = ImageDraw.Draw(can)
for aid, x, y, ims, w, h in pos:
    for k, im in enumerate(ims):
        bx = x + k * (w * 2 + 6); d.rectangle([bx, y + 18, bx + w * 2 - 1, y + 18 + h * 2 - 1], fill=(150, 150, 155))
        if im: can.paste(im.resize((im.width * 2, im.height * 2), Image.NEAREST), (bx, y + 18), im.resize((im.width * 2, im.height * 2), Image.NEAREST))
        d.text((bx + 2, y + 4), f'{aid} s{(101, 202)[k]}', fill=(255, 230, 150))
can.save(OUT); print(OUT, can.size)
