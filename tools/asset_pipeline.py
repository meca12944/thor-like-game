#!/usr/bin/env python3
"""정령의 팔찌 II - 그림 에셋 후처리 도구 (Python 3 + Pillow + numpy)

생성/그린 원본 그림을 게임용 파일로 바꿉니다.

  # 단색 배경 위 캐릭터 그림들 -> 배경 제거, 같은 기준(발밑)으로 정렬, 가로 프레임 스트립 PNG
  python3 tools/asset_pipeline.py sprite in1.png in2.png ... -o assets/hero_d_walk.png --height 144

  # 한 장에 여러 포즈가 격자로 그려진 시트 -> 칸별로 잘라 저장 (그 다음 sprite 명령에 넣기)
  python3 tools/asset_pipeline.py split sheet.png --cols 4 --rows 1 -o work/hero_walk_%d.png

  # 방 배경 그림 -> 4:3 으로 맞춰 자르고 1280x960 JPG
  python3 tools/asset_pipeline.py bg painted.png -o assets/bg_town1.jpg

  # index.html 의 ASSETS 목록과 assets/ 폴더를 비교 (빠진 파일/크기 확인)
  python3 tools/asset_pipeline.py check

--height 는 프레임 높이(px). 게임 안 높이(ASSETS 의 h) x 4 정도면 고해상도 휴대폰에서도 선명합니다.
"""
import sys, os, re, json, argparse
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def bg_color(a):
    b = np.concatenate([a[0, :, :3], a[-1, :, :3], a[:, 0, :3], a[:, -1, :3]]).astype(np.float32)
    return np.median(b, axis=0)

def remove_bg(im, tol=38, soft=22):
    """배경(테두리와 이어진 단색 영역)을 투명하게. tol: 배경으로 볼 색 차이, soft: 가장자리 부드럽게."""
    a = np.array(im.convert('RGBA'))
    if a[..., 3].min() < 250:            # 이미 투명 배경
        return Image.fromarray(a)
    bc = bg_color(a)
    d = np.sqrt(((a[..., :3].astype(np.float32) - bc) ** 2).sum(-1))
    sim = d < tol
    reach = np.zeros_like(sim)
    reach[0, :] = sim[0, :]; reach[-1, :] = sim[-1, :]; reach[:, 0] = sim[:, 0]; reach[:, -1] = sim[:, -1]
    while True:                           # 테두리에서 이어진 배경만 (캐릭터 안쪽 같은 색은 보존)
        n = reach.copy()
        n[1:] |= reach[:-1]; n[:-1] |= reach[1:]; n[:, 1:] |= reach[:, :-1]; n[:, :-1] |= reach[:, 1:]
        n &= sim
        if (n == reach).all(): break
        reach = n
    alpha = np.where(reach, 0, 255).astype(np.float32)
    edge = (~reach) & (d < tol + soft)    # 경계 반투명 + 배경색 번짐 제거
    k = np.clip((d - tol) / soft, 0, 1)
    alpha = np.where(edge, 255 * k, alpha)
    rgb = a[..., :3].astype(np.float32)
    kk = np.clip(k, .25, 1)[..., None]
    rgb = np.where(edge[..., None], np.clip((rgb - bc * (1 - kk)) / kk, 0, 255), rgb)
    al = Image.fromarray(alpha.astype(np.uint8)).filter(ImageFilter.GaussianBlur(.6))
    out = Image.fromarray(rgb.astype(np.uint8)).convert('RGBA'); out.putalpha(al)
    return out

def bbox(im, thr=16):
    a = np.array(im)[..., 3] > thr
    ys, xs = np.where(a)
    if not len(xs): return (0, 0, im.width, im.height)
    return (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)

def cmd_sprite(args):
    frames = [remove_bg(Image.open(f), args.tol, args.soft) for f in args.inputs]
    boxes = [bbox(f) for f in frames]
    # 프레임마다 가운데·발밑 정렬: 가장 큰 폭/높이 상자에 맞춤
    ws = max(b[2] - b[0] for b in boxes); hs = max(b[3] - b[1] for b in boxes)
    pad = int(hs * .04)
    cells = []
    for f, b in zip(frames, boxes):
        c = Image.new('RGBA', (ws + pad * 2, hs + pad * 2), (0, 0, 0, 0))
        cxm = (b[0] + b[2]) // 2
        c.paste(f.crop(b), (pad + ws // 2 - (cxm - b[0]), pad + hs - (b[3] - b[1])))
        cells.append(c)
    s = args.height / cells[0].height
    cw, ch = max(1, round(cells[0].width * s)), args.height
    strip = Image.new('RGBA', (cw * len(cells), ch), (0, 0, 0, 0))
    for i, c in enumerate(cells):
        strip.paste(c.resize((cw, ch), Image.LANCZOS), (i * cw, 0))
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    strip.save(args.output, optimize=True)
    print(f'{args.output}: {len(cells)} frames, frame {cw}x{ch}, {os.path.getsize(args.output)//1024} KB')

def cmd_split(args):
    im = Image.open(args.input); W, H = im.size
    for r in range(args.rows):
        for c in range(args.cols):
            i = r * args.cols + c
            im.crop((c * W // args.cols, r * H // args.rows, (c + 1) * W // args.cols, (r + 1) * H // args.rows)).save(args.output % i)
            print(args.output % i)

def cmd_bg(args):
    im = Image.open(args.input).convert('RGB'); W, H = im.size
    if W / H > 4 / 3: nw = round(H * 4 / 3); im = im.crop(((W - nw) // 2, 0, (W - nw) // 2 + nw, H))
    else: nh = round(W * 3 / 4); im = im.crop((0, (H - nh) // 2, W, (H - nh) // 2 + nh))
    im = im.resize((args.width, args.width * 3 // 4), Image.LANCZOS)
    fmt = 'WEBP' if args.output.lower().endswith('.webp') else 'JPEG'
    im.save(args.output, fmt, quality=args.quality, optimize=True) if fmt == 'JPEG' else im.save(args.output, fmt, quality=args.quality)
    print(f'{args.output}: {im.size[0]}x{im.size[1]}, {os.path.getsize(args.output)//1024} KB')

def cmd_check(args):
    html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    block = html.split('const ASSETS = {', 1)[1].split('\n};', 1)[0]
    files = sorted(set(re.findall(r"'([\w\-]+\.(?:png|jpg|jpeg|webp))'", block)))
    miss = 0; total = 0
    for f in files:
        p = os.path.join(ROOT, 'assets', f)
        if os.path.exists(p):
            sz = os.path.getsize(p); total += sz; w, h = Image.open(p).size
            print(f'  OK   {f:28s} {w}x{h} {sz//1024} KB')
        else:
            print(f'  MISS {f}'); miss += 1
    print(f'{len(files)} listed, {miss} missing, total {total//1024} KB')
    return 1 if miss else 0

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
sp = ap.add_subparsers(dest='cmd', required=True)
a = sp.add_parser('sprite'); a.add_argument('inputs', nargs='+'); a.add_argument('-o', '--output', required=True)
a.add_argument('--height', type=int, default=144); a.add_argument('--tol', type=float, default=38); a.add_argument('--soft', type=float, default=22)
a = sp.add_parser('split'); a.add_argument('input'); a.add_argument('--cols', type=int, default=1); a.add_argument('--rows', type=int, default=1); a.add_argument('-o', '--output', required=True)
a = sp.add_parser('bg'); a.add_argument('input'); a.add_argument('-o', '--output', required=True); a.add_argument('--width', type=int, default=1280); a.add_argument('--quality', type=int, default=80)
sp.add_parser('check')
args = ap.parse_args()
sys.exit({'sprite': cmd_sprite, 'split': cmd_split, 'bg': cmd_bg, 'check': cmd_check}[args.cmd](args) or 0)
