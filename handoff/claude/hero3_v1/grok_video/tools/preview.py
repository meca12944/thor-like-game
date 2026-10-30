# 러닝머신 미리보기 영상(장): 땅이 게임 빠르기로 흐르고 장은 걸은 거리로 넘김 → 발이 땅에 붙는지 눈으로. 안의 lanes 표를 바꿔 씀
# 쓰는 법: python3 preview.py <게임 화면 그림 1280×720(땅 띠를 380~560줄에서 씀)> <한글 글꼴 ttf> <출력 폴더>  → 출력/0000.png… → ffmpeg -framerate 30 -i 출력/%04d.png 영상.mp4
# 러닝머신 미리보기: 땅이 게임 빠르기로 흐르고, 장은 걸은 거리(gp)로 넘김 → 발이 땅에 붙는지(미끄러지는지) 눈으로
import sys, glob, os, numpy as np
from PIL import Image, ImageDraw, ImageFont
BG = sys.argv[1]; FONT = sys.argv[2]; out = sys.argv[3]
bg = Image.open(BG).convert('RGB')
tile = bg.crop((0, 380, 1280, 560)).resize((1280 * 2, 360), Image.NEAREST)   # 땅 띠(2배)
font = ImageFont.truetype(FONT, 26); small = ImageFont.truetype(FONT, 20)
def load(d): return [Image.open(f) for f in sorted(glob.glob(d + '/0*.png'))]
lanes = [   # (제목, 장들, 게임 빠르기 그림칸/초, 한 바퀴 거리 그림칸, 메모) — 필드 72/초 = 248칸/초, 108/초 = 372칸/초 (키 144)
    ('옆 달리기 (게임 달리기 빠르기)', load('sp_run_side_face'), 371.7, 17 * 14.8, '발 붙음'),
    ('옆 걷기 그대로 (게임 걷기 빠르기)', load('sp_walk_side_face'), 247.8, 161.0, '발 미끄러짐'),
    ('옆 걷기 영상 빠르기 (게임의 ¼)', load('sp_walk_side_face'), 2.5 * 24, 30 * 2.5, '발 붙음, 느림'),
]
Z = 2; W = 1280 // 3; FPS = 30; T = 6
os.makedirs(out, exist_ok=True)
dist = [0.0] * 3
for n in range(FPS * T):
    o = Image.new('RGB', (1280, 720), (30, 30, 34)); d = ImageDraw.Draw(o)
    for k, (title, fr, spd, cyc, note) in enumerate(lanes):
        x0 = k * W; lane = Image.new('RGB', (W, 720), (40, 40, 44))
        sx = int(dist[k] * Z) % 1280
        lane.paste(tile.crop((sx, 0, sx + W, 360)), (0, 330))
        for t in range(-1, 6):                                        # 땅 표시(말뚝) — 미끄러짐이 잘 보이게
            mx = int(t * 160 - (dist[k] * Z) % 160)
            d2 = ImageDraw.Draw(lane); d2.rectangle([mx, 560, mx + 6, 600], fill=(230, 210, 120))
        gp = (dist[k] / cyc) % 1; im = fr[int(gp * len(fr)) % len(fr)]
        big = im.resize((256 * Z, 256 * Z), Image.NEAREST)
        lane.paste(big, (W // 2 - 128 * Z, 580 - 246 * Z), big)
        dd = ImageDraw.Draw(lane); dd.text((12, 14), title, font=font, fill=(255, 235, 140)); dd.text((12, 52), note, font=small, fill=(255, 255, 255))
        o.paste(lane, (x0, 0)); d.line([(x0, 0), (x0, 720)], fill=(0, 0, 0), width=3)
        dist[k] += spd / FPS
    o.save(f'{out}/{n:04d}.png')
