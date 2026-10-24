# video: per direction [grok original (fx baked) | fx-removed pose + current code slash (파쇄 강철 부채꼴)], combo 1-2-3
import numpy as np, json, os, subprocess
from PIL import Image, ImageDraw, ImageFont
F = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 18)
meta = json.load(open('cells/meta.json')); SC = .35; HX, HY = 640, 390; CW, CH = 300, 300; X0, Y0 = HX - 150, HY - 210
DIRS = ['down', 'right', 'up', 'left']; NAME = {'down': '정면', 'right': '오른쪽', 'up': '뒤', 'left': '왼쪽'}
def pose(d, i, kind):
    m = meta[f'{d}_{i}']; im = Image.open(f'cells/{d}_{i}_{kind}.png').convert('RGBA'); w, h = im.size
    im = im.resize((int(w * SC), int(h * SC)), Image.LANCZOS); return im, int(m['body_x'] * SC), int(m['feet_y'] * SC)
os.makedirs('frames', exist_ok=True); n = 0
logs = {d: json.load(open(f'gc_{d}/log.json')) for d in DIRS}
for hit in range(3):
    taps = [k for k, l in enumerate(logs['down']) if l['tap']]; f0 = taps[hit]
    for f in range(f0 - 1, f0 + 21):
        out = Image.new('RGB', (CW * 4, CH * 2 + 40), (24, 22, 26)); d2 = ImageDraw.Draw(out)
        for j, d in enumerate(DIRS):
            a = np.asarray(Image.open(f'gc_{d}/{f:03d}a.png').convert('RGB')).astype(int); b = np.asarray(Image.open(f'gc_{d}/{f:03d}b.png').convert('RGB'))
            diff = np.abs(a - b.astype(int)).sum(axis=2) > 12; bg = Image.open(f'gc_{d}/000b.png').convert('RGB').crop((X0, Y0, X0 + CW, Y0 + CH))  # ground before the swing (no code sword line)
            slash = np.dstack([a.astype(np.uint8), (diff * 255).astype(np.uint8)]); sl = Image.fromarray(slash, 'RGBA').crop((X0, Y0, X0 + CW, Y0 + CH))
            cx, cy = (j % 2) * CW * 2, (j // 2) * CH + 40
            # left: grok original cell with the baked fx, same scale and feet
            o, bx, fy = pose(d, hit + 1, 'origcut'); p0 = bg.copy(); p0.paste(o, (HX - X0 - bx, HY - Y0 - fy), o); out.paste(p0, (cx, cy))
            r, bx, fy = pose(d, hit + 1, 'rgba'); p1 = bg.copy(); p1.paste(r, (HX - X0 - bx, HY - Y0 - fy), r)
            # the code slash: the dark fan goes under the body (as in game, layer 0), the bright rim over it (layer 1)
            rim = np.asarray(sl).astype(int); bright = (rim[..., :3].sum(axis=2) > 330) & (rim[..., 3] > 0)
            p1 = bg.copy(); p1.paste(sl, (0, 0), Image.fromarray(((np.asarray(sl)[..., 3] > 0) & ~bright).astype(np.uint8) * 255)); p1.paste(r, (HX - X0 - bx, HY - Y0 - fy), r)
            p1.paste(sl, (0, 0), Image.fromarray(bright.astype(np.uint8) * 255))
            out.paste(p1, (cx + CW, cy))
            d2.text((cx + 6, cy + 4), f'{NAME[d]} 그록 원본', fill=(255, 220, 180), font=F, stroke_width=2, stroke_fill=(0, 0, 0))
            d2.text((cx + CW + 6, cy + 4), f'{NAME[d]} 검기 지움 + 코드 검흔', fill=(180, 255, 200), font=F, stroke_width=2, stroke_fill=(0, 0, 0))
        d2.text((8, 8), f'{hit + 1}타  (게임 틱 {f - f0:+d})   왼쪽 = 그록 그림 그대로, 오른쪽 = 검기를 지운 몸 + 지금 게임의 코드 검흔(파쇄 강철)', fill=(240, 240, 240), font=F)
        for rep in range(2): out.save(f'frames/{n:04d}.png'); n += 1   # half speed
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '30', '-i', 'frames/%04d.png', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '22', 'grok_atk_codeslash_v1.mp4'], check=True)
print(n, 'frames')
