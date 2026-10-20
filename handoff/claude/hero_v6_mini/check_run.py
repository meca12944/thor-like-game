"""Run-cycle check: planted-foot slip (same method as handoff/claude/run_fix_v1) + coat-tail change + 4x strip and a scrolling-ground mp4.
python3 check_run.py <frames dir> <ticks per frame> <move px per tick> <out prefix>"""
import sys, os, glob, subprocess, shutil
from PIL import Image, ImageDraw, ImageChops
F = sorted(glob.glob(os.path.join(sys.argv[1], '*.png'))); TK = int(sys.argv[2]); SP = float(sys.argv[3]); OUT = sys.argv[4]
ims = [Image.open(f).convert('RGBA') for f in F]; n = len(ims)
def ground_y(im):
    a = im.split()[3]; return a.getbbox()[3] - 1
def contact(im):
    a = im.split()[3].load(); w, h = im.size; gy = ground_y(im)
    xs = sorted(x for y in range(gy - 3, gy + 1) for x in range(w) if a[x, y] > 128)
    g = []
    for v in xs:
        if g and v - g[-1][-1] <= 3: g[-1].append(v)
        else: g.append([v])
    return [(q[0] + q[-1]) / 2 for q in g]
C = [contact(i) for i in ims]
print('ground y per frame', [ground_y(i) for i in ims])
print('contact clusters  ', [[round(v) for v in c] for c in C])
# slip: for consecutive frames, match the rear-most cluster that moved backwards the least; ideal backward move = SP*TK
slips = []
for i in range(n):
    a, b = C[i], C[(i + 1) % n]
    best = min(((abs((y - x) + SP * TK), y - x) for x in a for y in b), default=(None, None))
    slips.append(round(best[0], 1) if best[0] is not None else None)
print('foot slip per step (0 = planted)', slips, 'sum', round(sum(s for s in slips if s is not None), 1))
diff = [sum(1 for v in ImageChops.difference(ims[i].split()[3], ims[(i + 1) % n].split()[3]).tobytes() if v > 128) for i in range(n)]
print('silhouette change i->i+1', diff, 'wrap/avg', round(diff[-1] / (sum(diff[:-1]) / (n - 1)), 2))
strip = Image.new('RGBA', (n * 140, 150), (150, 150, 155, 255))
for i, im in enumerate(ims): strip.alpha_composite(im.crop((58, 50, 198, 200)), (i * 140, 0))
strip.resize((strip.width * 2, strip.height * 2), Image.NEAREST).save(OUT + '_strip.png')
tmp = OUT + '_frames'; shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
for f in range(240):
    can = Image.new('RGB', (320, 220), (96, 128, 80)); d = ImageDraw.Draw(can)
    for k in range(0, 700, 24):
        xx = int((k - f * SP) % 336) - 8; d.rectangle([xx, 190, xx + 8, 192], fill=(60, 80, 50))
    im = ims[(f // TK) % n]; can.paste(im.crop((32, 0, 288, 200)), (32, -0), im.crop((32, 0, 288, 200)))
    can.resize((640, 440), Image.NEAREST).save(f'{tmp}/{f:04d}.png')
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '60', '-i', f'{tmp}/%04d.png', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', OUT + '.mp4'], check=True)
shutil.rmtree(tmp)
