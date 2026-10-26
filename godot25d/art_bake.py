# 설정화(앞·옆·뒤) → 3D 인형 색 그림(텍스처)으로 다시 칠하기. 크레딧 0.
# 인형은 그림과 같은 T자세라서, 꼭짓점마다 "그 방향 그림에서 보이는 자리"의 색을 가져온다(가려진 곳은 깊이로 걸러냄).
# 쓰는 법: python3 art_bake.py <glb> <앞.png> <옆(오른쪽 봄).png> <뒤.png> <출력.png> [크기=2048]
import sys, io, json, struct
import numpy as np
from PIL import Image

glb, f_front, f_side, f_back, out = sys.argv[1:6]
TS = int(sys.argv[6]) if len(sys.argv) > 6 else 2048

# ── GLB 읽기 (메시 0, 프리미티브 0) ──
raw = open(glb, 'rb').read()
jl = struct.unpack_from('<I', raw, 12)[0]
js = json.loads(raw[20:20 + jl])
bin0 = 20 + jl + 8
CT = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}
def acc(i):
    a = js['accessors'][i]; bv = js['bufferViews'][a['bufferView']]
    off = bin0 + bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    n = a['count'] * NC[a['type']]
    return np.frombuffer(raw, CT[a['componentType']], n, off).reshape(a['count'], NC[a['type']]) if NC[a['type']] > 1 else np.frombuffer(raw, CT[a['componentType']], n, off)
prim = js['meshes'][0]['primitives'][0]
P = acc(prim['attributes']['POSITION']).astype(np.float64)
N = acc(prim['attributes']['NORMAL']).astype(np.float64)
UV = acc(prim['attributes']['TEXCOORD_0']).astype(np.float64)
I = acc(prim['indices']).astype(np.int64).reshape(-1, 3)
mat = js['materials'][prim['material']]
ti = mat['pbrMetallicRoughness']['baseColorTexture']['index']
img = js['images'][js['textures'][ti]['source']]
bv = js['bufferViews'][img['bufferView']]
base = Image.open(io.BytesIO(raw[bin0 + bv.get('byteOffset', 0): bin0 + bv.get('byteOffset', 0) + bv['byteLength']])).convert('RGB')
print('정점', len(P), '면', len(I), '원래 그림', base.size)
base = np.asarray(base.resize((TS, TS), Image.LANCZOS), dtype=np.float64) / 255.0

# 머리 = 위쪽 12% 꼭짓점의 가운데
y0, y1 = P[:, 1].min(), P[:, 1].max()
head = P[P[:, 1] > y1 - (y1 - y0) * 0.12]
hx, hz = head[:, 0].mean(), head[:, 2].mean()

def load_art(f, mirror=False):
    a = Image.open(f).convert('RGBA')
    if mirror:
        a = a.transpose(Image.FLIP_LEFT_RIGHT)
    A = np.asarray(a, dtype=np.float64) / 255.0
    al = A[:, :, 3] > 0.15
    ys, xs = np.nonzero(al)
    top, bot = ys.min(), ys.max()
    hrow = al[top: top + int((bot - top) * 0.12)]
    cx = np.nonzero(hrow)[1].mean()
    return A, top, bot, cx

# 보기: (그림, 가로축 = 인형의 어느 좌표와 부호, 깊이(카메라 쪽이 큰 값), 보는 방향 법선)
views = []
A, t, b, cx = load_art(f_front); views.append(('앞', A, t, b, cx, lambda p: p[:, 0] - hx, lambda p: p[:, 2], np.array([0, 0, 1.0])))
A, t, b, cx = load_art(f_back); views.append(('뒤', A, t, b, cx, lambda p: -(p[:, 0] - hx), lambda p: -p[:, 2], np.array([0, 0, -1.0])))
A, t, b, cx = load_art(f_side); views.append(('오른옆', A, t, b, cx, lambda p: p[:, 2] - hz, lambda p: -p[:, 0], np.array([-1.0, 0, 0])))
A, t, b, cx = load_art(f_side, True); views.append(('왼옆', A, t, b, cx, lambda p: -(p[:, 2] - hz), lambda p: p[:, 0], np.array([1.0, 0, 0])))

def proj(v, p):
    name, A, top, bot, cx, fx, fd, d = v
    s = (bot - top) / (y1 - y0)
    return cx + fx(p) * s, bot - (p[:, 1] - y0) * s, fd(p)

def raster(xy, tris, W, H, vals=None):
    """삼각형마다 화면 칸 채우기. vals 없으면 깊이 버퍼(가까운 값), 있으면 (면 번호, 무게중심) 버퍼."""
    if vals is None:
        zb = np.full((H, W), -1e9)
    else:
        tid = np.full((H, W), -1, np.int64); bc = np.zeros((H, W, 3))
    for k, (a, b_, c) in enumerate(tris):
        pa, pb, pc = xy[a], xy[b_], xy[c]
        xmin = max(int(np.floor(min(pa[0], pb[0], pc[0]))), 0); xmax = min(int(np.ceil(max(pa[0], pb[0], pc[0]))), W - 1)
        ymin = max(int(np.floor(min(pa[1], pb[1], pc[1]))), 0); ymax = min(int(np.ceil(max(pa[1], pb[1], pc[1]))), H - 1)
        if xmin > xmax or ymin > ymax:
            continue
        gx, gy = np.meshgrid(np.arange(xmin, xmax + 1) + 0.5, np.arange(ymin, ymax + 1) + 0.5)
        den = (pb[1] - pc[1]) * (pa[0] - pc[0]) + (pc[0] - pb[0]) * (pa[1] - pc[1])
        if abs(den) < 1e-12:
            continue
        l1 = ((pb[1] - pc[1]) * (gx - pc[0]) + (pc[0] - pb[0]) * (gy - pc[1])) / den
        l2 = ((pc[1] - pa[1]) * (gx - pc[0]) + (pa[0] - pc[0]) * (gy - pc[1])) / den
        l3 = 1 - l1 - l2
        m = (l1 >= -1e-4) & (l2 >= -1e-4) & (l3 >= -1e-4)
        if not m.any():
            continue
        if vals is None:
            z = l1 * pa[2] + l2 * pb[2] + l3 * pc[2]
            sub = zb[ymin:ymax + 1, xmin:xmax + 1]
            upd = m & (z > sub)
            sub[upd] = z[upd]
        else:
            sub = tid[ymin:ymax + 1, xmin:xmax + 1]
            sub[m] = k
            bsub = bc[ymin:ymax + 1, xmin:xmax + 1]
            bsub[m] = np.stack([l1[m], l2[m], l3[m]], -1)
    return zb if vals is None else (tid, bc)

# 1) 색 그림 칸마다 → 어느 면의 어느 자리인지
uvp = np.stack([UV[:, 0] * TS, UV[:, 1] * TS], -1)
tid, bc = raster(uvp, I, TS, TS, vals=True)
mask = tid >= 0
ti_ = tid[mask]; b_ = bc[mask]
tri = I[ti_]
pos = (P[tri[:, 0]] * b_[:, :1] + P[tri[:, 1]] * b_[:, 1:2] + P[tri[:, 2]] * b_[:, 2:3])
nrm = (N[tri[:, 0]] * b_[:, :1] + N[tri[:, 1]] * b_[:, 1:2] + N[tri[:, 2]] * b_[:, 2:3])
nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
print('칠할 칸', mask.sum())

acc_c = np.zeros((len(pos), 3)); acc_w = np.zeros(len(pos))
for v in views:
    name, A, top, bot, cx, fx, fd, d = v
    H, W = A.shape[:2]
    # 2) 그 방향에서 본 깊이 (가려진 곳 거르기)
    vx, vy, vz = proj(v, P)
    zb = raster(np.stack([vx, vy, vz], -1), I, W, H)
    px, py, pz = proj(v, pos)
    ix = np.clip(px.astype(int), 0, W - 1); iy = np.clip(py.astype(int), 0, H - 1)
    s = (bot - top) / (y1 - y0)
    vis = pz >= zb[iy, ix] - 0.012 * (y1 - y0)
    inside = (px >= 0) & (px < W) & (py >= 0) & (py < H)
    al = A[iy, ix, 3]
    w = np.clip(nrm @ d, 0, 1) ** 2 * vis * inside * (al > 0.5)
    acc_c += A[iy, ix, :3] * w[:, None]; acc_w += w
    print(name, '보임', round(float((w > 0).mean()), 3))

col = base[mask].copy()
k = np.clip(acc_w * 2.5, 0, 1)[:, None]
col = col * (1 - k) + (acc_c / np.maximum(acc_w, 1e-6)[:, None]) * k
outimg = base.copy(); outimg[mask] = col
Image.fromarray((np.clip(outimg, 0, 1) * 255).astype(np.uint8)).save(out)
print('저장', out, '그림으로 칠한 비율', round(float((k[:, 0] > 0.5).mean()), 3))
