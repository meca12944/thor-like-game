# 주인공 옆 크기 비교 + 걷기 영상 (게임 크기: 주인공 30 field px, 아라크네 96 field px = 3.2배), 화면 1 field px = 3px
import sys, os, json, subprocess, numpy as np
from PIL import Image
C = os.path.dirname(os.path.abspath(__file__)); G = sys.argv[1]; out = sys.argv[2]
H = json.load(open(G + '/assets/anim/hero8.json')); e = H['anims']['idle_right'][0]; cell = H['cells'][e[0]][e[1]]
him = Image.open(G + '/assets/' + H['sheets'][e[0]]).convert('RGBA').crop((cell[0], cell[1], cell[0] + cell[2], cell[1] + cell[3]))
K = 3; hs = 30 / 117 * K; hero = him.resize((round(him.width * hs), round(him.height * hs)), Image.LANCZOS)
st = Image.open(C + '/strips/c1_boss_arachne_g_walk.png'); n = st.width // 256; FH = 153; asc = 96 / FH * K
fr = [st.crop((256 * i, 0, 256 * i + 256, 256)).resize((round(256 * asc), round(256 * asc)), Image.LANCZOS) for i in range(n)]
tmp = C + '/_raw/pv'; os.makedirs(tmp, exist_ok=True); [os.remove(tmp + '/' + f) for f in os.listdir(tmp)]
Wd, Ht = 960, 540; gy = 430; k = 0
for t in range(n * 6 * 4):
    c = Image.new('RGBA', (Wd, Ht), (58, 56, 54, 255)); i = (t // 6) % n; f = fr[i]
    c.alpha_composite(hero, (250 - round(cell[4] * hs), gy - round(cell[5] * hs)))
    c.alpha_composite(f, (520 - f.width // 2, gy - round(249 * asc)))
    c.convert('RGB').save(f'{tmp}/{k:04d}.png'); k += 1
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '60', '-i', tmp + '/%04d.png', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', out])
print(out, k)
