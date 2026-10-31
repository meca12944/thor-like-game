# 주인공 옷 = 장착 망토의 그록 옷 디자인 색 (사장님 10-31 「망토색에 따라서 옷색깔도 전부」 → 「그록이 망토 디자인 새로 올림」 → 「추천대로 하고 넣어」)
# 1) test128/assets/anim/hero3_0_outfit.png : 주인공 그림판과 같은 크기, 칸마다 255 = 그대로(살·머리·눈), 아니면 부위×32 + 밝기칸(0~31)
#    부위 0 망토·코트(남색) 1 바지(어두운 무채색) 2 어깨 3 허리·팔 가죽 4 장화 — 나누는 규칙은 handoff/claude/hero3_v1/outfit/outfit2.py 그대로
# 2) test128/index.html /*OUTFIT*/ 한 줄 : 망토 13종 × 부위 5 × 밝기 32칸 색(그록 시트 grok13/그록_망토NN_정면옆뒤.jpg 에서 뽑음) + 효과(fx)
# 주인공 그림판(hero3_0.webp)을 바꾸면(동작 추가 등) 반드시 다시 돌림 — 크기가 다르면 게임은 옷 색을 안 바꾸고 원래 그림을 씀(콘솔 경고).
# 쓰는 법: python3 tools/anim/hero3_outfit.py   (저장소 맨 위에서)
import json, re, os, importlib.util
import numpy as np
from PIL import Image
R = os.path.dirname(os.path.abspath(__file__)) + '/../../'
OF = R + 'handoff/claude/hero3_v1/outfit/'
spec = importlib.util.spec_from_file_location('o2', OF + 'outfit2.py'); o2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(o2)
idx = open(R + 'test128/index.html', encoding='utf-8').read()
i = idx.index('/*H8*/'); j = idx.index('{', i); H8, _ = json.JSONDecoder().raw_decode(idx[j:])
cells = H8['cells'][0]
sheet = np.array(Image.open(R + 'test128/assets/' + H8['sheets'][0]).convert('RGBA'))
P, L = o2.parts(sheet, cells); PART = ['cloak', 'pants', 'sh', 'belt', 'boots']
M = np.full(sheet.shape[:2], 255, np.uint8)
for pi, k in enumerate(PART):
    p5, p50, p95 = o2.REF[k]; t = .5 + (L - p50) / max(1, p95 - p5) * .8; ix = np.clip((t * (o2.N - 1)).round().astype(int), 0, o2.N - 1)
    M[P[k]] = (pi * 32 + ix)[P[k]]
Image.fromarray(M, 'L').save(R + 'test128/assets/anim/hero3_0_outfit.png', optimize=True)
band = {}
for n, (cid, _) in enumerate(o2.of.KS, 1):
    B = o2.bands(n); band[cid] = [int(v) for k in PART for v in B[k].astype(np.uint8).reshape(-1)]   # 파이썬 astype(uint8) = 버림 → 게임과 칸 하나까지 같음
O = {'_doc': '주인공 옷 = 장착 망토의 그록 옷 디자인 색 (사장님 10-31 「추천대로 하고 넣어」). tools/anim/hero3_outfit.py 가 씀. map 칸 = 255 그대로 / 부위×32+밝기칸, 부위 = parts 순서, band = 망토마다 부위 5 × 32칸 × RGB. fx = 코드 효과.',
     'map': 'anim/hero3_0_outfit.png', 'size': [int(sheet.shape[1]), int(sheet.shape[0])], 'parts': PART, 'band': band, 'fx': {'c_burning_noble': 'ember'}}
line = '/*OUTFIT*/const OUTFIT=' + json.dumps(O, ensure_ascii=False, separators=(',', ':')) + ';'
idx = re.sub(r'/\*OUTFIT\*/const OUTFIT=.*?;\n', lambda m: line + '\n', idx, count=1)
open(R + 'test128/index.html', 'w', encoding='utf-8').write(idx)
print('지도', M.shape, '옷 칸', int((M != 255).sum()), '망토', len(band), '글자', len(line), '지도 파일', os.path.getsize(R + 'test128/assets/anim/hero3_0_outfit.png'))
