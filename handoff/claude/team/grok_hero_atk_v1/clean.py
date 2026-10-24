# grok hero_attack3_4dir.jpg -> 12 cells: fx mask (cyan/white glow), inpainted pose, transparent-bg pose
import numpy as np, cv2, json
from PIL import Image
src = np.asarray(Image.open('atk.jpg').convert('RGB'))
ROWS = {'down': (75, 475), 'right': (540, 945), 'up': (1010, 1415), 'left': (1480, 1950)}
COLS = [(0, 341), (341, 683), (683, 1024)]
out = {}
for d, (y0, y1) in ROWS.items():
    for i, (x0, x1) in enumerate(COLS):
        c = src[y0:y1, x0:x1].copy(); H, W = c.shape[:2]
        if i == 0: c[0:60, 0:90] = c[60:120, 0:90]  # row label (정면/오른쪽/뒤/왼쪽) -> background patch
        f = c.astype(int); r, g, b = f[..., 0], f[..., 1], f[..., 2]
        hsv = cv2.cvtColor(c, cv2.COLOR_RGB2HSV).astype(int)  # H 0-180
        cyan = (b - r > 22) & (g - r > 12) & (b > 95)                       # glow body + soft halo over the grey floor
        white = (r > 175) & (g > 190) & (b > 195) & (b >= r)                 # hot white core
        strong = (cyan | white).astype(np.uint8)
        zone = cv2.dilate(strong, np.ones((3, 3), np.uint8), iterations=14)  # 42 px around the glow
        weak = (b - r > 1) & (b > 78)                                          # faint halo: any blue tint over the grey floor / cloth near the glow
        m = (strong | (zone.astype(bool) & weak)).astype(np.uint8)
        m = cv2.dilate(m, np.ones((3, 3), np.uint8), iterations=2)          # include the jpeg fringe
        clean = cv2.inpaint(c, m * 255, 5, cv2.INPAINT_TELEA)
        # background (grey floor) -> alpha 0: distance from the floor colour sampled at the cell border
        bord = np.concatenate([clean[2, :], clean[-3, :], clean[:, 2], clean[:, -3]]).astype(int); bg = np.median(bord, axis=0)
        dist = np.abs(clean.astype(int) - bg).sum(axis=2)
        fg = (dist > 38).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(fg, 8)
        keep = np.zeros_like(fg)
        if n > 1:
            big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); keep[lab == big] = 1
            for k in range(1, n):  # small pieces close to the body (hair tips, cape) stay
                if k != big and st[k, cv2.CC_STAT_AREA] > 30: keep[lab == k] = 1
        keep = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        # shadow under the feet stays as part of the pose? no: game draws its own shadow
        rgba = np.dstack([clean, keep * 255]).astype(np.uint8)
        name = f'{d}_{i + 1}'
        Image.fromarray(c).save(f'cells/{name}_orig.png'); Image.fromarray(clean).save(f'cells/{name}_clean.png'); Image.fromarray(rgba).save(f'cells/{name}_rgba.png')
        Image.fromarray(m * 255).save(f'cells/{name}_mask.png')
        fxa = cv2.dilate(m, np.ones((3, 3), np.uint8), 1); Image.fromarray(np.dstack([c, np.maximum(keep, fxa) * 255]).astype(np.uint8)).save(f'cells/{name}_origcut.png')  # grok original with its baked fx, floor removed
        ys, xs = np.nonzero(keep); feet = int(ys.max()) if len(ys) else H
        out[name] = {'fx_px': int(m.sum()), 'feet_y': feet, 'body_x': int(np.median(xs)) if len(xs) else W // 2, 'w': W, 'h': H, 'body_top': int(ys.min()) if len(ys) else 0}
json.dump(out, open('cells/meta.json', 'w'), indent=1); print(json.dumps(out)[:600])
