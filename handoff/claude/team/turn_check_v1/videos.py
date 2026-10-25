# (b) 제자리 돌기 영상 + 띠 그림, (d) 8방향 원 배치 동시 재생 영상
import numpy as np, json, glob, os, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageOps
F = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 18); FS = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 14)
M = json.load(open('turn_measure.json')); BG = (54, 56, 64, 255)
ORDER = [('↓', 'walk_s2', 'run_s', 0), ('↘', 'walk_se', 'run_se2', 0), ('→', 'walk_r2', 'run_r2', 0), ('↗', 'walk_ne', 'run_ne2', 0), ('↑', 'walk_up', 'run_n', 0), ('↖', 'walk_ne', 'run_ne2', 1), ('←', 'walk_r2', 'run_r2', 1), ('↙', 'walk_se', 'run_se2', 1)]
def fr(d, i, flip):
    fs = sorted(glob.glob(f'{d}/[0-9][0-9][0-9].png')); im = Image.open(fs[i % len(fs)]).convert('RGBA'); return ImageOps.mirror(im) if flip else im, len(fs)
def guides(dr, ox, oy, S=1):
    ref = M['걷기 ↓']; cr = sum(ref['crown']) / 2; eye = cr + sum(ref['eye_from_crown']) / 2
    for y, col, t in [(189, (120, 255, 140), '발 189'), (cr, (255, 110, 110), '정면 걷기 꼭대기'), (eye, (255, 220, 90), '정면 걷기 눈')]:
        dr.line([(ox, oy + y * S), (ox + 256 * S, oy + y * S)], fill=col, width=1)
    dr.line([(ox + 128 * S, oy), (ox + 128 * S, oy + 256 * S)], fill=(110, 160, 255), width=1)
# ---- (b) strip image: 8 directions walk / run frame 0 side by side with guide lines
W = Image.new('RGBA', (256 * 8, 256 * 2 + 70), BG); d = ImageDraw.Draw(W)
for j, (ar, w, r, fl) in enumerate(ORDER):
    for k, (src, kind) in enumerate(((w, '걷기'), (r, '달리기'))):
        im, _ = fr(src, 0, fl); W.alpha_composite(im, (j * 256, 40 + k * 256)); guides(d, j * 256, 40 + k * 256)
        m = M[f'{kind} {dict(zip("↖←↙", "↗→↘")).get(ar, ar)}']; d.text((j * 256 + 4, 44 + k * 256), f"{kind} {ar}  키 {m['height_avg']:.0f}  얼굴폭 {m['face_w']}", fill=(230, 235, 255), font=FS)
d.text((6, 8), '8방향 나란히 (첫 장) — 빨강 = 정면 걷기 머리 꼭대기, 노랑 = 정면 걷기 눈, 초록 = 발 189, 파랑 = 가운데 128', fill=(255, 255, 255), font=F)
W.save('turn_strip.png')
# ---- (b) turntable video: rotate in place 45° at a time (walk frame 0 and run frame 0), guide lines
os.makedirs('tt', exist_ok=True); n = 0; S = 2
for loop in range(2):
    for j, (ar, w, r, fl) in enumerate(ORDER):
        for hold in range(10):  # 1/3 s per direction
            C = Image.new('RGBA', (256 * S * 2 + 20, 256 * S + 50), BG); dd = ImageDraw.Draw(C)
            for k, (src, kind) in enumerate(((w, '걷기'), (r, '달리기'))):
                im, _ = fr(src, 0, fl); im = im.resize((256 * S, 256 * S), Image.NEAREST); C.alpha_composite(im, (k * (256 * S + 20), 50)); guides(dd, k * (256 * S + 20), 50, S)
                dd.text((k * (256 * S + 20) + 8, 56), kind, fill=(230, 235, 255), font=F)
            dd.text((8, 10), f'제자리 돌기 {ar}   (빨강 꼭대기 · 노랑 눈 · 초록 발 = 정면 걷기 기준)', fill=(255, 255, 255), font=F)
            C.convert('RGB').save(f'tt/{n:04d}.png'); n += 1
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '30', '-i', 'tt/%04d.png', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', 'turntable_v1.mp4'], check=True)
# ---- (d) circle: 8 directions on a circle, same beat (walk 6 ticks/frame, run 4 ticks/frame), 4 s each
os.makedirs('cc', exist_ok=True); n = 0; R = 300; CX, CY = 460, 470
pos = {ar: (CX + R * math.cos(a), CY + R * math.sin(a) * .8) for ar, a in zip(['→', '↘', '↓', '↙', '←', '↖', '↑', '↗'], [i * math.pi / 4 for i in range(8)])}
for kind, tpf in (('걷기', 6), ('달리기', 4)):
    for t in range(0, 240, 2):
        C = Image.new('RGBA', (920, 900), BG); dd = ImageDraw.Draw(C); dd.text((10, 10), f'8방향 원 — {kind} 같은 박자 ({tpf}틱마다 1장), 아래 = 정면', fill=(255, 255, 255), font=F)
        for ar, w, r, fl in sorted(ORDER, key=lambda o: pos[o[0]][1]):
            src = w if kind == '걷기' else r; _, nf = fr(src, 0, fl); im, _ = fr(src, t // tpf, fl); x, y = pos[ar]
            C.alpha_composite(im, (int(x - 128), int(y - 189))); dd.text((int(x) - 8, int(y) + 6), ar, fill=(255, 230, 150), font=F)
        C.convert('RGB').save(f'cc/{n:04d}.png'); n += 1
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '30', '-i', 'cc/%04d.png', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '22', 'circle8_v1.mp4'], check=True)
print('ok')
