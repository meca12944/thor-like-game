# placed/*.png: drop small loose pieces (bits of the neighbouring cell) — keep the biggest body + pieces > 120 px
import glob, numpy as np, cv2
from PIL import Image
for f in glob.glob('placed/atk*.png'):
    a = np.array(Image.open(f)); m = (a[..., 3] > 0).astype(np.uint8); n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    if n <= 2: continue
    big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); keep = np.isin(lab, [k for k in range(1, n) if k == big or st[k, cv2.CC_STAT_AREA] > 120])
    a[..., 3] = np.where(keep, a[..., 3], 0); Image.fromarray(a).save(f)
print('ok')
