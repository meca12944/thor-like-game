# 서기 3방향을 키 H로 (한 번만 줄임): 2배 판에 몸(그대로 2배)+머리 A(2배 판 그대로)를 붙이고 → LANCZOS 한 번 → 몸은 서기 색표로, 머리 칸(A)은 색 맞추기 없이(A하프 스무스와 같은 방식)
# 쓰는 법: python3 stand.py <hero3_v1 폴더> <H> <출력 폴더>   (주인공: H 144 → game144/)
import sys, os, numpy as np
from PIL import Image
V3, H, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
os.makedirs(out, exist_ok=True)
FOOT = (128, 246)                 # 판 발 기준 (218 그림과 같음)
def lanczos_pm(rgba, w2, h2):
    a = rgba.astype(np.float32); al = a[..., 3:4] / 255; pm = np.concatenate([a[..., :3] * al, a[..., 3:4]], 2)
    ch = [np.asarray(Image.fromarray(pm[..., k], 'F').resize((w2, h2), Image.LANCZOS)) for k in range(4)]
    A = np.clip(ch[3], 0, 255); rgb = np.stack([np.clip(ch[k] / np.maximum(A, 1e-3) * 255, 0, 255) for k in range(3)], 2)
    return rgb, A
def snap(rgb, pal):
    flat = rgb.reshape(-1, 3); idx = np.empty(len(flat), int)
    for i in range(0, len(flat), 8192): idx[i:i + 8192] = ((flat[i:i + 8192, None] - pal[None]) ** 2).sum(2).argmin(1)
    return pal[idx].reshape(rgb.shape)
def make(body, head, hx, hy):
    B = np.asarray(Image.open(body).convert('RGBA'))
    pal = np.unique(B[B[..., 3] > 0][:, :3], axis=0).astype(np.float32)
    big = np.repeat(np.repeat(B, 2, 0), 2, 1).copy()            # 몸 2배 (칸 그대로)
    box = None
    if head:
        A = np.asarray(Image.open(head).convert('RGBA')); big[2 * hy:2 * hy + A.shape[0], 2 * hx:2 * hx + A.shape[1]] = A   # 머리 칸 통째로 (게임 얼굴과 같은 붙이기)
        box = (2 * hx, 2 * hy, 2 * hx + A.shape[1], 2 * hy + A.shape[0])
    # 발 기준이 정수 칸에 오도록: 2배 판에서 키 218(=436칸) 만큼을 H칸으로
    S = 2 * 218; x0, y0 = 2 * FOOT[0] - S // 2, 2 * FOOT[1] - S
    crop = np.zeros((S, S, 4), np.uint8); sy0, sx0 = max(0, y0), max(0, x0)
    crop[sy0 - y0:, sx0 - x0:] = big[sy0:y0 + S, sx0:x0 + S][:S - (sy0 - y0), :S - (sx0 - x0)]
    rgb, al = lanczos_pm(crop, H, H)
    keep = al > 110
    yy, xx = np.mgrid[0:H, 0:H]; cx = (xx + .5) * S / H; cy = (yy + .5) * S / H   # 칸 가운데가 2배 판 어디인지
    inhead = np.zeros((H, H), bool)
    if box: inhead = (cx + x0 >= box[0]) & (cx + x0 < box[2]) & (cy + y0 >= box[1]) & (cy + y0 < box[3])
    body_rgb = snap(rgb, pal)
    o = np.where(inhead[..., None], rgb, body_rgb)
    o = np.concatenate([o, (keep * 255)[..., None]], 2).astype(np.uint8)
    c = Image.new('RGBA', (256, 256)); im = Image.fromarray(o, 'RGBA'); c.paste(im, (FOOT[0] - H // 2, FOOT[1] - H), im)
    return c
make(f'{V3}/ref/down.png', f'{V3}/face/hiface_2x.png', 68, 24).save(f'{out}/down_face.png')
make(f'{V3}/ref/right.png', f'{V3}/face/side_A.png', 104, 24).save(f'{out}/right_face.png')
make(f'{V3}/ref/up.png', None, 0, 0).save(f'{out}/up.png')
make(f'{V3}/ref/down.png', None, 0, 0).save(f'{out}/down.png')
make(f'{V3}/ref/right.png', None, 0, 0).save(f'{out}/right.png')
for n in ['down_face', 'right_face', 'up']:
    im = Image.open(f'{out}/{n}.png'); print(n, im.getbbox(), '키', im.getbbox()[3] - im.getbbox()[1])
