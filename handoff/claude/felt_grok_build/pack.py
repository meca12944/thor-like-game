"""최종 부품 묶음 → final/<id>.png (투명, D=3, 크기 그대로) + final/parts.json
- 건물: out/<id>_<판>.png 에 모양 틀 → 손질 틀(TRIM, 결과 그림 좌표)로 남은 땅 지움
- 소품: 글자만으로 뽑은 것, 테두리까지 잘라 냄
- 재사용: 리네트 공방 = felt_hd atelier_v2, 주민 집(bl_house) = felt_hd house_v2, 등불·화로·수레·상자 = felt_hd
grok_foot = 그록 원본(1536x864)에서 건물 발밑 가운데. 월드 자리 = grok_foot × 0.8 (3번방 구도 판과 같은 셈)."""
import os, json, shutil, numpy as np
os.environ.setdefault('PIXELLAB_API_KEY', 'unused')
from PIL import Image, ImageDraw
import gen
from shapes import POLY
PICK = {'inn': 'q', 'se_house': 'q', 's_house': 'q', 'shop_sign': 'q', 'castle_l': 'q', 'e_row': 'p', 'chapel': 'p',
        'west_a': 'p', 'west_b': 'p', 'stall_n': 'p', 'sw_house': 'p', 'west_edge': 'p', 'web_arch': 'p',
        'red_stall': 'p', 'fountain': 'p', 'castle_r': 'p'}
TRIM = {
 'se_house':  [(0,360),(0,130),(40,55),(75,20),(120,5),(272,5),(310,50),(350,100),(385,110),(400,120),(400,360)],
 's_house':   [(0,352),(0,190),(40,150),(90,125),(135,110),(170,55),(190,45),(215,60),(240,25),(265,15),(285,40),(300,85),(330,130),(365,150),(400,165),(400,352)],
 'shop_sign': [(0,396),(0,130),(40,80),(90,45),(120,25),(250,20),(300,60),(330,110),(335,230),(400,240),(400,396)],
 'west_a':    [(50,400),(50,300),(20,280),(20,120),(45,60),(100,35),(155,15),(185,40),(215,90),(224,100),(224,400)],
 'e_row':     [(20,400),(20,110),(60,50),(120,15),(240,20),(280,70),(296,110),(296,400)],
 'west_b':    [(0,400),(0,150),(40,90),(80,40),(120,5),(200,10),(230,50),(272,90),(272,400)],
 'west_edge': [(0,400),(0,30),(30,15),(40,40),(110,40),(140,30),(172,60),(172,400)],
}
ROLE = {'inn': '[7] 마르타의 여관', 'se_house': '[11] 롬의 대장간', 's_house': '[12] 이장 바르트의 집', 'e_row': '[8] 세라의 약초 오두막',
        'chapel': '[5] 예배당 종탑', 'west_a': '[14] 중고 무기점', 'west_b': '[15] 시장 거리 집', 'stall_n': '[15] 시장 노점',
        'shop_sign': '[13] 잡화점', 'sw_house': '[16] 주민 빈집', 'west_edge': '경비 초소 본채(맨 왼쪽)', 'web_arch': '[9] 아라크네의 폐공방',
        'red_stall': '[10] 벤의 노점', 'fountain': '[1] 분수', 'castle_l': '[2] 불탄 왕성 왼쪽', 'castle_r': '[2] 불탄 왕성 오른쪽',
        'linette': '[3] 리네트의 공방 (felt_hd atelier_v2)', 'bl_house': '주민 집 (felt_hd house_v2)'}
os.makedirs('final', exist_ok=True)
PALIMG = Image.open('../felt_grok_layout/palette_32.png').convert('RGB')
PCOL = np.array([PALIMG.getpixel((i * 8 + 4, 4)) for i in range(32)], float)
def to_pal(im):
    # 밝기 순서를 지키며 마을 색으로 옮김: 각 점을 밝기가 가장 가까운 바탕 24색 + 색이 남는 점은 가장 가까운 32색
    a = np.array(im).astype(float); rgb = a[:, :, :3].reshape(-1, 3)
    lum = lambda c: c @ np.array([.299, .587, .114])
    base = PCOL[:24]; L = lum(rgb); bl = lum(base)
    lo, hi = np.percentile(L[a[:, :, 3].reshape(-1) > 0], [2, 98]); Ln = (L - lo) / max(hi - lo, 1) * (bl.max() - bl.min()) + bl.min()
    near_b = np.abs(Ln[:, None] - bl[None]).argmin(1)
    sat = rgb.max(1) - rgb.min(1)
    d = ((rgb[:, None] - PCOL[None]) ** 2).sum(2); near_c = d.argmin(1)
    out = np.where((sat > 70)[:, None], PCOL[near_c], base[near_b])
    a[:, :, :3] = out.reshape(a.shape[0], a.shape[1], 3)
    return Image.fromarray(a.astype(np.uint8))
parts = {}
def tight(a):
    ys, xs = np.nonzero(a[:, :, 3]); return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
PICK.pop('fountain')
for pid, v in PICK.items():
    a = np.array(Image.open(f'out/{pid}_{v}.png').convert('RGBA'))
    keep = np.array(gen.mask_of(pid)) > 127
    if pid in TRIM:
        t = Image.new('L', (a.shape[1], a.shape[0]), 0); ImageDraw.Draw(t).polygon(TRIM[pid], fill=255); keep &= np.array(t) > 127
    a[:, :, 3] = np.where(keep & (a[:, :, 3] > 0), 255, 0)   # PixelLab이 이미 투명하게 둔 곳은 그대로
    (x0, y0, x1, y1), s, (w, h) = gen.geom(pid)
    a = tight(a); Image.fromarray(a).save(f'final/{pid}.png')
    P = POLY[pid]; by = max(p[1] for p in P); bx = [p[0] for p in P if p[1] >= by - 3]
    parts[pid] = {'img': f'{pid}.png', 'w': a.shape[1], 'h': a.shape[0], 'ax': a.shape[1] // 2, 'ay': a.shape[0] - 1,
                  'grok_foot': [round(sum(bx) / len(bx)), by], 'role': ROLE[pid], 'kind': 'building'}
from scipy import ndimage
def key(a, thr=14):   # 테두리와 이어진 단색 바탕 지우기
    c = a[0, 0, :3].astype(int); flat = np.abs(a[:, :, :3].astype(int) - c).sum(2) < thr
    fl, _ = ndimage.label(flat); e = set(np.unique(np.concatenate([fl[0], fl[-1], fl[:, 0], fl[:, -1]]))) - {0}
    a[:, :, 3] = np.where(np.isin(fl, list(e)), 0, a[:, :, 3]); return a
SKIP = {'fountain_king', 'fountain_king2', 'cocoons'}   # 버린 판 (석상 분수는 아래 fountain 으로, 고치는 cocoons2)
for pid in gen.TEXT:
    if pid in SKIP: continue
    a = tight(key(np.array(Image.open(f'out/{pid}_t.png').convert('RGBA')))); Image.fromarray(a).save(f'final/{pid}.png')
    parts[pid] = {'img': f'{pid}.png', 'w': a.shape[1], 'h': a.shape[0], 'ax': a.shape[1] // 2, 'ay': a.shape[0] - 1, 'kind': 'prop'}
# 분수 = 그록 분수 + 부서진 왕 석상 (3번방 배치 연구: 랜드마크·저장 비석 역할), 물은 마름
a = tight(key(np.array(Image.open('out/fountain_king_i.png').convert('RGBA')))); Image.fromarray(a).save('final/fountain.png')
parts['fountain'] = {'img': 'fountain.png', 'w': a.shape[1], 'h': a.shape[0], 'ax': a.shape[1] // 2, 'ay': a.shape[0] - 1,
                     'grok_foot': [692, 530], 'role': '[1] 금 간 분수 + 부서진 왕 석상 (광장 랜드마크)', 'kind': 'building'}
parts['cocoons'] = parts.pop('cocoons2'); parts['cocoons']['img'] = 'cocoons.png'; os.replace('final/cocoons2.png', 'final/cocoons.png')
ZONE = {'south_gate': '남 입구 문', 'fence_wood': '남 입구 나무 울타리', 'anvil': '남(대장간) 모루', 'woodpile': '남(대장간) 장작',
        'string_lights': '서 시장 줄등', 'candelabra': '북동 예배당 촛대', 'tombs': '북동 묘비', 'fence_iron': '북동 묘지 쇠울타리',
        'cocoons': '동 거미줄 구역 고치', 'ember_rubble': '북 왕성 불씨 잔해', 'rubble': '북 왕성 잔해'}
for k, z in ZONE.items(): parts[k]['zone'] = z
parts['watchtower'].update(role='[4] 경비 초소 감시탑', grok_foot=[455, 200], kind='building')
parts['mausoleum'].update(role='[6] 예배당 뒤 묘지 납골당', grok_foot=[1385, 215])
# 리네트 공방: atelier_v2 를 init 으로 마을 색 다시 그림 (out/linette_r.png)
a = np.array(Image.open('out/linette_r.png').convert('RGBA'))
from scipy import ndimage
bgc = a[0, 0, :3].astype(int); flat = np.abs(a[:, :, :3].astype(int) - bgc).sum(2) < 12   # 단색 바탕(테두리와 이어진 것) 지우기
fl, _ = ndimage.label(flat); edge = set(np.unique(np.concatenate([fl[0], fl[-1], fl[:, 0], fl[:, -1]]))) - {0}
a[:, :, 3] = np.where(np.isin(fl, list(edge)), 0, a[:, :, 3])
lab, n = ndimage.label(a[:, :, 3] > 0); k = 1 + int(np.argmax(ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))))
a[:, :, 3] = np.where(lab == k, 255, 0); a = tight(a); Image.fromarray(a).save('final/linette.png')
parts['linette'] = {'img': 'linette.png', 'w': a.shape[1], 'h': a.shape[0], 'ax': a.shape[1] // 2, 'ay': a.shape[0] - 1,
                    'grok_foot': [700, 305], 'role': '[3] 리네트의 공방 (왕실 의상실 폐허)', 'kind': 'building'}
for pid, src, gf in [('bl_house', 'house_v2', [70, 860]),
                     ('lamp', 'lamp', None), ('brazier', 'brazier', None), ('cart', 'cart', None), ('crates', 'crates', None)]:
    im = to_pal(Image.open(f'../felt_hd/cut/{src}.png').convert('RGBA')); im.save(f'final/{pid}.png')
    parts[pid] = {'img': f'{pid}.png', 'w': im.width, 'h': im.height, 'ax': im.width // 2, 'ay': im.height - 1,
                  'kind': 'building' if gf else 'prop', **({'grok_foot': gf, 'role': ROLE[pid]} if gf else {})}
json.dump({'_doc': 'Felt (그록 대표 그림 배치) 부품. D=3 (월드 1px = 그림 3px), view low top-down, 빛 왼쪽 위, 마을 32색. '
                   '투명 PNG 크기 그대로 쓰기. ax/ay = 발밑 기준점. grok_foot × 0.8 = 3번방 구도 판 월드 px 자리. '
                   '건물은 그록 크기의 0.7배 이하로 그렸으니 충돌 칸(solid)은 그림 아래쪽 폭에 맞춰 다시 잡기.',
           'D': 3, 'parts': parts}, open('final/parts.json', 'w'), ensure_ascii=False, indent=1)
# 확인 그림
items = list(parts.items()); cols = 7; cw, ch = 300, 330
o = Image.new('RGBA', (cols * cw, ((len(items) + cols - 1) // cols) * ch), (58, 52, 44, 255)); d = ImageDraw.Draw(o)
for i, (k, p) in enumerate(items):
    im = Image.open('final/' + p['img']).convert('RGBA'); s = min(1, 290 / im.width, 300 / im.height)
    if s < 1: im = im.resize((int(im.width * s), int(im.height * s)), Image.NEAREST)
    x, y = (i % cols) * cw + 5, (i // cols) * ch + 20; o.alpha_composite(im, (x, y)); d.text((x, y - 15), k, fill=(255, 230, 180))
o.save('final_sheet.png'); print(len(parts), 'parts')
