# 칸 1: 그록 일러스트(작은그림) → 도트 한 번 줄이기 (미리곱 LANCZOS, 단단한 투명, 128색 — 48색이면 눈·입이 사라짐)
# 쓰는 법: python3 conv_mini.py  (안의 파일 이름·키 목록을 바꿔 씀) · 다른 데서: from conv_mini import conv; conv(<그림>, <키>, 128).save(...)
# 그록 작은그림 → 도트 (한 번만 줄임: 미리곱한 LANCZOS, 단단한 투명, 48색)
import sys, numpy as np
from PIL import Image
def conv(src, H, ncol=128):
    im = Image.open(src).convert('RGBA'); a = np.asarray(im).astype(np.float32); al = a[..., 3:4] / 255
    pm = np.concatenate([a[..., :3] * al, a[..., 3:4]], 2)
    s = H / im.height; w2, h2 = max(1, round(im.width * s)), H
    ch = [np.asarray(Image.fromarray(pm[..., k], 'F').resize((w2, h2), Image.LANCZOS)) for k in range(4)]
    A = np.clip(ch[3], 0, 255); rgb = np.stack([np.clip(ch[k] / np.maximum(A, 1e-3) * 255, 0, 255) for k in range(3)], 2)
    keep = A > 110
    px = rgb[keep].astype(np.uint8)                       # 색표는 보이는 칸에서만 (투명 칸의 초록 찌꺼기 빼기)
    pal = Image.fromarray(px[None]).quantize(ncol, method=Image.Quantize.MEDIANCUT)
    P = np.asarray(pal.getpalette()[:ncol * 3]).reshape(-1, 3).astype(np.float32)
    flat = rgb.reshape(-1, 3); idx = np.empty(len(flat), int)
    for i in range(0, len(flat), 8192):
        idx[i:i + 8192] = ((flat[i:i + 8192, None] - P[None]) ** 2).sum(2).argmin(1)
    o = np.concatenate([P[idx].reshape(h2, w2, 3), (keep * 255)[..., None]], 2).astype(np.uint8)
    return Image.fromarray(o, 'RGBA')
if __name__ == '__main__':
    for d in ['front', 'side', 'back']:
        for H in (145, 218, 290):
            conv(f'hero_armsopen_v3_{d}.png', H).save(f'px_{d}_{H}.png')
