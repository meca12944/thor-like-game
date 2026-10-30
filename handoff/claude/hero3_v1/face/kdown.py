# 도트 그림 반으로 줄이기 (K-centroid: 2x2 칸마다 많은 쪽 색, 섞지 않음 → 새 색 없음)
import sys, numpy as np
from PIL import Image
def kdown(im, f=2):
    a = np.asarray(im.convert('RGBA')).astype(int); H, W = a.shape[0] // f, a.shape[1] // f
    out = np.zeros((H, W, 4), np.uint8)
    for y in range(H):
        for x in range(W):
            blk = a[y*f:(y+1)*f, x*f:(x+1)*f].reshape(-1, 4)
            vis = blk[blk[:, 3] > 0]
            if len(vis) * 2 < len(blk): continue
            L = vis[:, :3] @ [.299, .587, .114]
            # 2묶음으로 나눠 많은 쪽; 같으면 더 어두운 쪽(선·눈을 살림)
            lo, hi = vis[L <= np.median(L)], vis[L > np.median(L)]
            pick = lo if len(lo) >= len(hi) else hi
            pick = pick[np.argmin(pick[:, :3] @ [.299, .587, .114])] if len(pick) else vis[0]
            out[y, x] = pick
    return Image.fromarray(out)
if __name__ == '__main__':
    kdown(Image.open(sys.argv[1])).save(sys.argv[2])
