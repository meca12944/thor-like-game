# 줄 세우기 그림: python3 strip.py <장 폴더> <출력 png> [배율=2] [한 줄 장 수]  (회색 줄 = 발 기준 246)
import sys, glob
from PIL import Image, ImageDraw
d, out = sys.argv[1], sys.argv[2]; Z = int(sys.argv[3]) if len(sys.argv) > 3 else 2
fs = sorted(glob.glob(d + '/0*.png')); per = int(sys.argv[4]) if len(sys.argv) > 4 else len(fs)
bbs = [Image.open(f).getbbox() for f in fs]; x0 = min(b[0] for b in bbs) - 2; x1 = max(b[2] for b in bbs) + 2; y0 = min(b[1] for b in bbs) - 2; y1 = 250
W, H = (x1 - x0) * Z, (y1 - y0) * Z; rows = (len(fs) + per - 1) // per
o = Image.new('RGB', (per * W, rows * (H + 18)), (46, 48, 56)); dr = ImageDraw.Draw(o)
for i, f in enumerate(fs):
    im = Image.open(f).crop((x0, y0, x1, y1)).resize((W, H), Image.NEAREST); X = (i % per) * W; Y = (i // per) * (H + 18)
    o.paste(im, (X, Y + 18), im); dr.text((X + 3, Y + 3), str(i), fill=(255, 255, 0)); dr.line([(X, Y + 18 + (246 - y0) * Z), (X + W, Y + 18 + (246 - y0) * Z)], fill=(90, 90, 90))
o.save(out); print(o.size)
