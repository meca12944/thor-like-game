import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from proportions import *
from chars import CH, V
from PIL import ImageFont
FT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 13)
R = json.load(open('/workspace/town-demo/style_sample/work/src_landmarks.json'))
def ruled(f, y0, y1, mag):
    t = Image.fromarray(np.dstack([f[..., :3], f[..., 3] * 255]).astype(np.uint8), 'RGBA').crop((0, y0, f.shape[1], y1))
    bg = Image.new('RGBA', t.size, (60, 80, 60, 255)); bg.alpha_composite(t); im = bg.convert('RGB').resize((t.width * mag, t.height * mag), Image.NEAREST)
    out = Image.new('RGB', (im.width + 46, im.height), (20, 20, 20)); out.paste(im, (46, 0)); d = ImageDraw.Draw(out)
    for y in range(y0 - y0 % 5, y1, 5):
        yy = (y - y0) * mag
        if yy < 0: continue
        L = 14 if y % 10 else 30
        d.line((46 - L, yy, 46 + im.width if y % 10 == 0 else 46, yy), fill=(255, 255, 255) if y % 10 == 0 else (150, 150, 150))
        if y % 10 == 0: d.text((0, yy - 7), str(y), fill=(255, 255, 0), font=FT)
    return out
if __name__ == '__main__':
  for name, p in CH:
      if sys.argv[1:] and name not in sys.argv[1:]: continue
      fr = load_frames(p, 3); parts = []
      for v, f in zip(V, fr):
          r = R[name][v]; H = r['sole'] - r['crown']
          parts.append(ruled(f, 0, int(H * .30), 1))
      for v, f in zip(V, fr):
          if v == 'side': continue
          r = R[name][v]; s = r['split'] or int(r['sole'] * .55)
          parts.append(ruled(f, max(0, s - 60), s + 30, 1))
      W = sum(p.width + 10 for p in parts); Hh = max(p.height for p in parts); img = Image.new('RGB', (W, Hh), (0, 0, 0)); x = 0
      for q in parts: img.paste(q, (x, 0)); x += q.width + 10
      img.save(f'/workspace/town-demo/style_sample/work/ruler_{name}.png'); print(name, img.size)
