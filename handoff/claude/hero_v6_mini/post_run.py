"""Run-cycle post-process (pixels untouched, only placement and timing), same idea as tools/anim/stabilize_v1.py:
  1. ground line: every frame's lowest opaque pixel snapped to the foot root y (189) -> no 4-5 px body bob
  2. torso x: gold (pauldron / trim) centroid in the torso band follows a circular 5-frame average -> no side-to-side jitter
  3. timing: per-frame ticks from the planted foot's travel to the next frame at the run speed (px per tick), so the foot stays put
python3 post_run.py <frames dir> <out dir> [speed px/tick=2.2]
Writes <out>/000.png.. (256 canvas) and <out>/timing.json {ticks, shift}."""
import sys, os, glob, json
import numpy as np
from PIL import Image
SRC, OUT = sys.argv[1], sys.argv[2]; SP = float(sys.argv[3]) if len(sys.argv) > 3 else 2.2; GY = 189
os.makedirs(OUT, exist_ok=True)
F = [np.array(Image.open(f).convert('RGBA')) for f in sorted(glob.glob(os.path.join(SRC, '*.png')))]; N = len(F)

def bottom(a): ys = np.nonzero(a[..., 3] > 128)[0]; return int(ys.max())
def torso_x(a):
    al = a[..., 3] > 128; r, g, b = [a[..., i].astype(int) for i in range(3)]
    gold = al & (r > 150) & (g > 90) & (b < 90) & (r > g)
    bt = bottom(a); band = np.zeros(al.shape, bool); band[max(0, bt - 100):max(0, bt - 45)] = True
    ys, xs = np.nonzero(gold & band)
    if len(xs) < 5: return None
    m = np.median(xs); xs = xs[np.abs(xs - m) < 25]; return float(xs.mean())
dy = [GY - bottom(a) for a in F]
X = [torso_x(a) for a in F]
if any(v is None for v in X): X = [128.0] * N
tgt = [float(np.mean([X[(i + j) % N] for j in range(-2, 3)])) for i in range(N)]
dx = [int(round(tgt[i] - X[i])) for i in range(N)]
G = []
for i, a in enumerate(F):
    im = Image.fromarray(a); can = Image.new('RGBA', im.size); can.alpha_composite(im, (dx[i], dy[i])); G.append(can)

def contact(im):
    a = np.array(im)[..., 3] > 128; xs = np.sort(np.nonzero(a[GY - 3:GY + 1].any(axis=0))[0])
    g = []
    for v in xs:
        if g and v - g[-1][-1] <= 3: g[-1].append(int(v))
        else: g.append([int(v)])
    return [(q[0] + q[-1]) / 2 for q in g]
C = [contact(im) for im in G]
ticks = []
for i in range(N):
    a, b = C[i], C[(i + 1) % N]
    # planted foot = the pair (x in a, y in b) that moved backwards closest to a plausible stride; travel = x - y
    moves = [x - y for x in a for y in b if 0 <= x - y <= 30]
    t = round(min(moves, key=lambda m: abs(m - SP * 4)) / SP) if moves else 4   # no planted match (foot swap / flight) -> 4 ticks
    ticks.append(int(min(8, max(2, t))))
for i, im in enumerate(G): im.save(os.path.join(OUT, f'{i:03d}.png'))
json.dump({'ticks': ticks, 'dx': dx, 'dy': dy, 'cycle_ticks': sum(ticks), 'speed': SP}, open(os.path.join(OUT, 'timing.json'), 'w'))
print('dy', dy, 'dx', dx, 'ticks', ticks, 'cycle', sum(ticks))
