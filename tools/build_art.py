#!/usr/bin/env python3
"""정령의 팔찌 II - 무료 라이선스 그림 팩으로 게임용 에셋 만들기.

  python3 tools/build_art.py          # 원본 팩 내려받기(assets_src/packs, 캐시) + assets/*.png 생성 + CREDITS.md 갱신

원본: OpenGameArt.org 의 LPC(Liberated Pixel Cup) 계열 팩과 Universal LPC Spritesheet Character Generator
(라이선스는 CREDITS.md). 캐릭터 옷/머리 색을 바꾸려면 아래 CHARS 의 레이어 경로만 바꾸고 다시 실행하세요.
필요: Python 3 + Pillow + numpy (인터넷 연결)."""
import os, io, csv, sys, json, zipfile, urllib.request, colorsys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PK = os.path.join(ROOT, 'assets_src', 'packs'); OUT = os.path.join(ROOT, 'assets')
os.makedirs(PK, exist_ok=True); os.makedirs(OUT, exist_ok=True)
SF = 'https://raw.githubusercontent.com/sanderfrenken/Universal-LPC-Spritesheet-Character-Generator/master/'
OGA = 'https://opengameart.org/sites/default/files/'
USED = {}

def fetch(url, name):
    p = os.path.join(PK, name)
    if not os.path.exists(p):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (asset build script)'})
        with urllib.request.urlopen(req, timeout=60) as r, open(p, 'wb') as f: f.write(r.read())
    return p

_Z = {}
def zipped(zipname, member):
    if zipname not in _Z: _Z[zipname] = zipfile.ZipFile(fetch(OGA + zipname, zipname))
    return Image.open(io.BytesIO(_Z[zipname].read(member))).convert('RGBA')
BASE = lambda f: zipped('lpc_base_assets.zip', 'LPC Base Assets/' + f)
def TERRAIN(): return zipped('Atlas_0.zip', 'terrain_atlas.png')

def lpc(path):
    USED['sf:' + path] = path
    return Image.open(fetch(SF + 'spritesheets/' + path, 'sf_' + path.replace('/', '_'))).convert('RGBA')

def compose(layers, h=1344):
    out = Image.new('RGBA', (832, h), (0, 0, 0, 0))
    for l in layers:
        if not l: continue
        im = lpc(l) if isinstance(l, str) else l
        im = im.crop((0, 0, 832, min(h, im.height)))
        out.alpha_composite(im, (0, 0))
    return out

def slash_sheet(layers, weapon_behind=None, weapon_front=None):
    """1152x768: 6 frames x 4 dirs (up,left,down,right), 192x192 cells; body slash rows 12-15 centred."""
    body = compose(layers); out = Image.new('RGBA', (1152, 768), (0, 0, 0, 0))
    if weapon_behind: out.alpha_composite(lpc(weapon_behind))
    for d in range(4):
        for f in range(6):
            out.alpha_composite(body.crop((f * 64, (12 + d) * 64, f * 64 + 64, (13 + d) * 64)), (f * 192 + 64, d * 192 + 64))
    if weapon_front: out.alpha_composite(lpc(weapon_front))
    return out

def tint(im, rgb, amount=1.0):
    a = np.array(im).astype(np.float32)
    lum = (a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11) / 255
    col = np.stack([lum * rgb[i] * 1.5 for i in range(3)], -1)
    a[..., :3] = a[..., :3] * (1 - amount) + np.clip(col, 0, 255) * amount
    return Image.fromarray(a.astype(np.uint8))

def hue(im, dh=0.0, ds=1.0, dv=1.0):
    a = np.array(im.convert('RGBA')); hsv = np.array(Image.fromarray(a[..., :3]).convert('HSV')).astype(np.int32)
    hsv[..., 0] = (hsv[..., 0] + int(dh * 255)) % 256; hsv[..., 1] = np.clip(hsv[..., 1] * ds, 0, 255); hsv[..., 2] = np.clip(hsv[..., 2] * dv, 0, 255)
    rgb = np.array(Image.fromarray(hsv.astype(np.uint8), 'HSV').convert('RGB'))
    return Image.fromarray(np.dstack([rgb, a[..., 3]]))

def autocrop(im):
    b = im.getbbox(); return im.crop(b) if b else im

def human(sex='male', skin='light', hair=None, eyes='brown', torso=None, legs=None, feet=None, extra=(), behind=(), beard=None):
    L = list(behind) + [f'body/bodies/{sex}/{skin}.png', f'head/heads/human/{sex}/{skin}.png', f'eyes/human/adult/{eyes}.png']
    for x in (feet, legs): 
        if x: L.append(x)
    if torso: L += torso if isinstance(torso, list) else [torso]
    if beard: L.append(beard)
    if hair: L.append(hair)
    return L + list(extra)

HERO = human('male', 'light', hair='hair/messy1/male/chestnut.png', torso=['torso/clothes/longsleeve/longsleeve/male/white.png', 'torso/clothes/vest/male/leather.png'],
             legs='legs/pants/male/brown.png', feet='feet/boots/male/brown.png',
             behind=['cape/solid_behind/green.png'], extra=['cape/solid/male/green.png'])
CHARS = {
  'npc_elder':   human('male', 'light', hair='hair/plain/male/white.png', beard='beards/beard/basic/white.png', torso='torso/clothes/longsleeve/longsleeve/male/purple.png', legs='legs/pants/male/brown.png', feet='feet/boots/male/brown.png'),
  'npc_smith':   human('male', 'bronze', beard='beards/beard/basic/black.png', torso='torso/clothes/vest/male/leather.png', legs='legs/pants/male/charcoal.png', feet='feet/boots/male/black.png'),
  'npc_inn':     human('female', 'light', hair='hair/ponytail/female/chestnut.png', torso='torso/clothes/blouse/female/white.png', legs='legs/skirts/belle/female/maroon.png', feet='feet/shoes/female/brown.png'),
  'npc_girl':    human('female', 'light', hair='hair/pigtails/female/blonde.png', torso='torso/clothes/blouse/female/pink.png', legs='legs/skirts/belle/female/blue.png', feet='feet/shoes/female/brown.png'),
  'npc_boy':     human('male', 'light', hair='hair/messy2/male/carrot.png', torso='torso/clothes/longsleeve/longsleeve/male/sky.png', legs='legs/pants/male/navy.png', feet='feet/boots/male/brown.png'),
  'npc_merchant':human('male', 'brown', hair='hair/plain/male/black.png', torso='torso/clothes/longsleeve/longsleeve/male/orange.png', legs='legs/pants/male/leather.png', feet='feet/boots/male/brown.png'),
  'npc_inn2':    human('female', 'olive', hair='hair/bunches/female/black.png', torso='torso/clothes/blouse/female/green.png', legs='legs/skirts/belle/female/brown.png', feet='feet/shoes/female/black.png'),
  'npc_sailor':  human('male', 'light', hair='hair/plain/male/gray.png', beard='beards/beard/basic/gray.png', torso='torso/clothes/longsleeve/longsleeve/male/navy.png', legs='legs/pants/male/gray.png', feet='feet/boots/male/black.png'),
  'npc_villager':human('male', 'light', hair='hair/plain/male/dark_brown.png', torso='torso/clothes/longsleeve/longsleeve/male/green.png', legs='legs/pants/male/brown.png', feet='feet/boots/male/brown.png'),
  'enemy_skel':  ['body/bodies/skeleton/universal.png', 'weapon/sword/dagger/dagger.png'],
  'enemy_knight':human('male', 'light', torso='torso/armour/plate/male/steel.png', legs='legs/armour/plate/male/steel.png', feet='feet/boots/male/black.png',
                       extra=['hat/helmet/barbuta/male/steel.png', 'weapon/sword/longsword/longsword.png']),
  'enemy_mage':  human('female', 'light', hair='hair/long/female/ash.png', torso='torso/clothes/robe/female/blue.png', feet='feet/shoes/female/black.png',
                       extra=['hat/magic/wizard/base/adult/blue.png', 'weapon/magic/simple/foreground/simple.png'], behind=['weapon/magic/simple/background/simple.png']),
  'boss_priest': human('female', 'light', torso='torso/clothes/robe/female/black.png', feet='feet/shoes/female/black.png',
                       extra=['hat/cloth/hood/adult/black.png', 'weapon/magic/gnarled/universal/foreground/dark.png'], behind=['weapon/magic/gnarled/universal/background/dark.png']),
}

def save(im, name):
    p = os.path.join(OUT, name); im.save(p, optimize=True); print(f'  {name:24s} {im.size[0]}x{im.size[1]} {os.path.getsize(p)//1024} KB')

def build_chars():
    print('characters')
    save(compose(HERO), 'hero.png')
    save(slash_sheet(HERO, 'weapon/sword/longsword/attack_slash/behind/longsword.png', 'weapon/sword/longsword/attack_slash/longsword.png'), 'hero_slash.png')
    for k, L in CHARS.items():
        im = compose(L)
        if k == 'boss_priest': im = tint(im, (150, 90, 210), .35)
        save(im, k + '.png')

def build_monsters():
    print('monsters')
    USED['oga:lpc-base'] = 1
    for n, f in [('enemy_slime', 'slime'), ('enemy_bat', 'bat'), ('enemy_wisp', 'ghost'), ('enemy_snapper', 'man_eater_flower')]:
        save(BASE(f'sprites/monsters/{f}.png'), n + '.png')
    g = BASE('sprites/monsters/ghost.png')
    for sid, col in [('water', (80, 170, 255)), ('fire', (255, 120, 50)), ('shadow', (150, 110, 230)), ('plant', (110, 230, 110))]:
        save(tint(g, col, .85), f'spirit_{sid}.png')
    USED['oga:lpc-golem'] = 1
    save(Image.open(fetch(OGA + 'golem-walk.png', 'golem-walk.png')).convert('RGBA'), 'boss_golem.png')
    USED['oga:red-dragon'] = 1
    d = Image.open(fetch(OGA + 'reddragonfly.png', 'reddragonfly.png')).convert('RGBA')
    save(hue(d.crop((0, 0, 820, 322)), dh=0.75, ds=.9, dv=1.35), 'boss_wyvern.png')

def build_tiles():
    print('tiles')
    USED['oga:lpc-tile-atlas'] = 1; USED['oga:lpc-base'] = 1
    T = TERRAIN(); H = BASE('tiles/house.png')
    blocks = {'grass': T.crop((672, 0, 768, 192)), 'dirt': BASE('tiles/dirt.png'), 'dirt2': BASE('tiles/dirt2.png'),
              'water': BASE('tiles/water.png'), 'sand': T.crop((0, 288, 96, 480)), 'pit': T.crop((768, 0, 864, 192)),
              'chasm': T.crop((864, 0, 960, 192)), 'darkstone': T.crop((576, 192, 672, 384)), 'lava': BASE('tiles/lava.png')}
    tile = lambda c, r: T.crop((c * 32, r * 32, c * 32 + 32, r * 32 + 32))
    face = H.crop((128, 128, 160, 160))
    singles = {'flowers0': tile(21, 11), 'flowers1': tile(22, 11), 'flowers2': tile(23, 11),
        'cobble0': tile(30, 17), 'cobble1': tile(31, 18), 'cobble2': tile(30, 19),
        'stone0': tile(16, 26), 'stone1': tile(17, 26), 'stone2': tile(16, 27), 'stone3': tile(17, 27),
        'teal0': tile(29, 11), 'teal1': tile(30, 13), 'cream0': tile(27, 10), 'cream1': tile(31, 11),
        'plank': tile(17, 20), 'stairs': tile(27, 8), 'plate': tile(19, 30), 'crack': tile(25, 11),
        'door': H.crop((96, 32, 128, 64)), 'face_grey': face,
        'face_cave': tint(face, (150, 110, 80), .8), 'face_temple': tint(face, (90, 150, 100), .75), 'face_canyon': tint(face, (190, 110, 70), .8),
        'face_town': tint(face, (160, 150, 130), .6)}
    W = 96 * len(blocks); per = W // 32; rows = (len(singles) + per - 1) // per
    atlas = Image.new('RGBA', (W, 192 + rows * 32), (0, 0, 0, 0)); meta = {'block': {}, 'tile': {}}
    for i, n in enumerate(blocks):
        atlas.alpha_composite(blocks[n].convert('RGBA').crop((0, 0, 96, 192)), (i * 96, 0)); meta['block'][n] = [i * 96, 0]
    for i, (n, im) in enumerate(singles.items()):
        x, y = (i % per) * 32, 192 + (i // per) * 32; atlas.alpha_composite(im.convert('RGBA'), (x, y)); meta['tile'][n] = [x, y]
    save(atlas, 'tiles.png'); return meta

def build_props():
    print('props')
    T = TERRAIN(); H = BASE('tiles/house.png'); P = {}
    P['tree'] = autocrop(T.crop((928, 896, 1024, 1024)))
    P['tree2'] = autocrop(T.crop((864, 928, 928, 1024)))
    P['pine'] = autocrop(T.crop((960, 0, 1024, 160)))
    P['rock'] = autocrop(T.crop((832, 800, 896, 832)))
    P['block'] = T.crop((608, 448, 640, 480))
    C = BASE('tiles/chests.png'); P['chest'] = autocrop(C.crop((0, 0, 32, 32))); P['chest_open'] = autocrop(C.crop((0, 32, 32, 64)))
    L = BASE('tiles/castle_lightsources.png'); torch = autocrop(L.crop((64, 0, 96, 64)))
    a = np.array(torch); hot = (a[..., 0] > 150) & (a[..., 2] < 140) & (a[..., 1] > 60); a2 = a.copy(); a2[hot, 3] = 0
    P['torch_lit'] = torch; P['torch'] = autocrop(Image.fromarray(a2))
    P['altar'] = autocrop(T.crop((544, 384, 576, 448)))
    roof = Image.new('RGBA', (128, 64))
    for x, sx in [(0, 96), (32, 128), (64, 128), (96, 160)]:          # house.png cols 3,4,4,5 / rows 3 (top edge) + 6 (eaves)
        roof.alpha_composite(H.crop((sx, 96, sx + 32, 128)), (x, 0)); roof.alpha_composite(H.crop((sx, 192, sx + 32, 224)), (x, 32))
    wall = Image.new('RGBA', (128, 64)); wb = H.crop((0, 0, 96, 96))
    for x, sx in [(0, 0), (32, 32), (64, 32), (96, 64)]: wall.alpha_composite(wb.crop((sx, 32, sx + 32, 96)), (x, 0))
    house = Image.new('RGBA', (128, 128)); house.alpha_composite(roof, (0, 0)); house.alpha_composite(wall, (0, 64))
    house.alpha_composite(H.crop((96, 0, 128, 64)), (64, 64))
    win = H.crop((224, 0, 256, 32)); house.alpha_composite(win, (14, 76)); house.alpha_composite(win, (98, 76))
    P['house'] = house
    H2 = max(im.height for im in P.values()); x = 0; meta = {}
    atlas = Image.new('RGBA', (sum(im.width + 2 for im in P.values()), H2), (0, 0, 0, 0))
    for n, im in P.items():
        atlas.alpha_composite(im, (x, H2 - im.height)); meta[n] = [x, H2 - im.height, im.width, im.height]; x += im.width + 2
    save(atlas, 'props.png'); return meta

OGA_PACKS = {
  'oga:lpc-base': ('Liberated Pixel Cup (LPC) Base Assets — 지형, 몬스터(슬라임·박쥐·유령·식인초), 상자, 집, 횃불', 'Lanea Zimmerman (Sharm), Stephen Challener (Redshrike), Charles Sanchez (CharlesGabriel), Manuel Riecke (MrBeast), Daniel Armstrong (HughSpectrum)', 'CC-BY-SA 3.0 / GPL 3.0', 'https://opengameart.org/content/liberated-pixel-cup-lpc-base-assets-sprites-map-tiles'),
  'oga:lpc-tile-atlas': ('LPC Tile Atlas (Atlas_0: terrain_atlas.png) — 지형, 나무, 바위, 바닥, 제단, 계단', 'Lanea Zimmerman (Sharm), Stephen Challener (Redshrike), Charles Sanchez (CharlesGabriel), Manuel Riecke (MrBeast), Daniel Armstrong (HughSpectrum), Casper Nilsson, Daniel Eddeland, Johann Charlot, Skyler Robert Colladay; 아틀라스 정리: Lanea Zimmerman 외 LPC 참가자 (원본 Attribution.txt 는 assets/LICENSES/ 에 포함)', 'CC-BY-SA 3.0 / GPL 3.0 (일부 조각: Casper Nilsson·Daniel Eddeland 은 GPL 3.0+, Johann Charlot 은 LGPL 3.0+)', 'https://opengameart.org/content/lpc-tile-atlas'),
  'oga:lpc-golem': ('[LPC] Golem — 보스 이끼 골렘', 'Stephen Challener (Redshrike), William.Thompsonj (submitter)', 'CC-BY 3.0 (OGA-BY 3.0 / GPL 도 선택 가능)', 'https://opengameart.org/content/lpc-golem'),
  'oga:red-dragon': ('Red Dragon — 보스 밤날개 와이번 (색상 변경)', 'Buko Studios (submitted by ZaPaper)', 'CC-BY 3.0', 'https://opengameart.org/content/red-dragon'),
}
def write_credits():
    rows = list(csv.DictReader(open(fetch(SF + 'CREDITS.csv', 'sf_CREDITS.csv'), encoding='utf-8')))
    L = ['# CREDITS / 저작권 표시', '',
         '이 게임의 코드·이야기·음악은 오리지널입니다. 그림은 아래 무료 라이선스 팩을 사용했습니다.',
         '- 변경 사항: 레이어 합성, 잘라내기, 색조 변경, 아틀라스 재배치(`tools/build_art.py`)',
         '- CC-BY-SA 3.0 / GPL 3.0 그림을 바꾼 결과물(`assets/*.png`)도 같은 라이선스(CC-BY-SA 3.0 또는 GPL 3.0)로 배포합니다.', '',
         '라이선스 전문:', '',
         '- CC-BY-SA 3.0: https://creativecommons.org/licenses/by-sa/3.0/',
         '- CC-BY 3.0: https://creativecommons.org/licenses/by/3.0/',
         '- OGA-BY 3.0: https://opengameart.org/content/oga-by-30-faq', '- GPL 3.0: https://www.gnu.org/licenses/gpl-3.0.html', '',
         '## 지형·소품·몬스터 (OpenGameArt.org)', '', '| 팩 | 작가 | 라이선스 | 출처 |', '|---|---|---|---|']
    for k, (t, a, l, u) in OGA_PACKS.items():
        if k in USED: L.append(f'| {t} | {a} | {l} | {u} |')
    L += ['', '## 캐릭터 레이어 (Universal LPC Spritesheet Character Generator)', '',
          '- 합성에 쓴 저장소: https://github.com/sanderfrenken/Universal-LPC-Spritesheet-Character-Generator',
          '- 각 레이어의 작가·라이선스·원 출처는 그 저장소의 `CREDITS.csv` 기준입니다.',
          '- 주인공, 마을 사람, 해골병사, 흑기사, 모래술사, 흑요 사제가 이 레이어들로 만들어졌습니다.', '',
          '| 레이어 파일 | 작가 | 라이선스 | 원 출처 |', '|---|---|---|---|']
    for key in sorted(k for k in USED if k.startswith('sf:')):
        path = USED[key]; best = None
        for r in rows:
            fn = (r.get('filename') or '').strip().rstrip('/')
            if fn and (r.get('authors') or '').strip() and (path == fn or path.startswith(fn + '/') or path.rsplit('.', 1)[0] == fn):
                if best is None or len(fn) > len(best['filename'].strip().rstrip('/')): best = r
        if best:
            urls = ' '.join(best[k].strip() for k in best if k and k.startswith('url') and best[k] and best[k].strip())
            L.append(f"| {path} | {best['authors'].strip()} | {best['licenses'].strip()} | {urls} |")
        else: L.append(f'| {path} | (원 저장소 CREDITS.csv 참고) | CC-BY-SA 3.0 / GPL 3.0 | https://github.com/sanderfrenken/Universal-LPC-Spritesheet-Character-Generator |')
    txt = '\n'.join(L).replace('Sj?lund', 'Sjölund') + '\n'
    open(os.path.join(ROOT, 'CREDITS.md'), 'w', encoding='utf-8').write(txt)
    lic = os.path.join(OUT, 'LICENSES'); os.makedirs(lic, exist_ok=True)
    open(os.path.join(lic, 'LPC_Tile_Atlas_Attribution.txt'), 'wb').write(_Z['Atlas_0.zip'].read('Attribution.txt'))
    open(os.path.join(lic, 'LPC_Base_Assets_CREDITS.TXT'), 'wb').write(_Z['lpc_base_assets.zip'].read('LPC Base Assets/CREDITS.TXT'))
    open(os.path.join(lic, 'Universal_LPC_CREDITS.csv'), 'wb').write(open(fetch(SF + 'CREDITS.csv', 'sf_CREDITS.csv'), 'rb').read())
    print('CREDITS.md', len(L), 'lines')

if __name__ == '__main__':
    build_chars(); build_monsters(); tm = build_tiles(); pm = build_props()
    json.dump({'tiles': tm, 'props': pm}, open(os.path.join(ROOT, 'assets_src', 'atlas_meta.json'), 'w'), indent=1)
    write_credits()

def patch_index(meta):
    """index.html 의 PROP_RECTS / TILE_POS 표를 방금 만든 아틀라스 좌표로 갱신."""
    import re
    p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
    pr = 'const PROP_RECTS=' + json.dumps(meta['props'], separators=(',', ':')) + ';\n'
    tp = 'const TILE_POS=' + json.dumps(meta['tiles'], separators=(',', ':')) + ';\n'
    s, n1 = re.subn(r'const PROP_RECTS=\{.*?\};\n', lambda m: pr, s, count=1, flags=re.S)
    s, n2 = re.subn(r'const TILE_POS=\{.*?\}\};\n', lambda m: tp, s, count=1, flags=re.S)
    open(p, 'w', encoding='utf-8').write(s); print('index.html atlas tables updated', n1, n2)

if __name__ == '__main__':
    patch_index(json.load(open(os.path.join(ROOT, 'assets_src', 'atlas_meta.json'))))
