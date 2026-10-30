# 그록 영상 → 게임 도트 장 (사장님 10-30 「그대로 써도 되겠네」)
# 1) 초록 빼기(+초록 번짐 지우기) 2) 영상 전체에 배율 하나(서 있는 첫 장 키 → 게임 키 H, 지금 144) 3) 미리곱 LANCZOS로 한 번만 줄이고 서기 그림 색으로 맞춤
# 4) 한 바퀴 장들을 한 번에 같은 만큼 옮김(장마다 따로 안 옮김 = 영상 그대로의 흔들림), 가장 낮은 발 = 246
import sys, glob, os, numpy as np
from PIL import Image
frames_dir, start, period, ref, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
HT = int(sys.argv[6]) if len(sys.argv) > 6 else 144   # 게임 그림 키 (사장님 10-30 「작아져야지」 → 144, 옛 218)
ZOOM = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0   # 영상이 슬쩍 확대된 만큼 되돌리기 (zoomfit.py: 한 바퀴 윗몸을 첫 장 서기와 겹쳐 잼, 정면 걷기 0.93)
fs = sorted(glob.glob(frames_dir + '/*.png'))
def key(f):
    a = np.asarray(Image.open(f).convert('RGB')).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    green = g - np.maximum(r, b)                     # 초록 정도
    alpha = np.clip(1 - (green - 40) / 60, 0, 1)      # 40 아래 = 몸, 100 위 = 바탕
    g2 = np.minimum(g, np.maximum(r, b) + 10)         # 가장자리 초록 번짐 빼기
    rgba = np.dstack([r, g2, b, alpha * 255])
    return rgba
A0 = key(fs[0]); ys = np.nonzero(A0[..., 3] > 128)[0]; H0 = ys.max() - ys.min()
s = HT / H0 * ZOOM
pal = np.asarray(Image.open(ref).convert('RGBA')).reshape(-1, 4); pal = np.unique(pal[pal[:, 3] > 0][:, :3], axis=0).astype(np.float32)
def shrink(rgba):
    al = rgba[..., 3:4] / 255; pm = np.concatenate([rgba[..., :3] * al, rgba[..., 3:4]], 2)
    W, H = rgba.shape[1], rgba.shape[0]; w2, h2 = round(W * s), round(H * s)
    ch = [np.asarray(Image.fromarray(pm[..., k].astype(np.float32), 'F').resize((w2, h2), Image.LANCZOS)) for k in range(4)]
    A = np.clip(ch[3], 0, 255); rgb = np.stack([np.clip(ch[k] / np.maximum(A, 1e-3) * 255, 0, 255) for k in range(3)], 2)
    flat = rgb.reshape(-1, 3); idx = np.empty(len(flat), int)
    for i in range(0, len(flat), 8192): idx[i:i + 8192] = ((flat[i:i + 8192, None] - pal[None]) ** 2).sum(2).argmin(1)
    o = np.concatenate([pal[idx].reshape(h2, w2, 3), ((A > 128) * 255)[..., None]], 2).astype(np.uint8)
    return Image.fromarray(o, 'RGBA')
ims = [shrink(key(fs[i])) for i in range(start, start + period)]
bbs = [im.getbbox() for im in ims]
bot = max(b[3] for b in bbs); cx = np.mean([(b[0] + b[2]) / 2 for b in bbs])
dx, dy = round(128 - cx), 246 - bot
os.makedirs(out, exist_ok=True)
for i, im in enumerate(ims):
    c = Image.new('RGBA', (256, 256)); c.paste(im, (dx, dy), im); c.save(f'{out}/{i:03d}.png')
print('배율', round(s, 4), '첫 장 키', H0, '→', HT, '장', period, '옮김', dx, dy, '키들', [b[3] - b[1] for b in bbs])
