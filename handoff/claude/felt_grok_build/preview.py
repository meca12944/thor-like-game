"""부품을 그록 배치 자리에 세워 본 미리보기 (바닥은 임시 단색+잡음). preview_full.png(월드 1/3 축소), preview_plaza.png(실제 D=3 한 화면)"""
import json, numpy as np
from PIL import Image
P = json.load(open('final/parts.json'))['parts']
SP = 0.7  # 자리 간격도 건물처럼 0.7배 → 맵 약 54×30칸
W, H = int(1536 * 2.4 * SP), int(864 * 2.4 * SP)
rng = np.random.default_rng(1)
g = np.zeros((H // 3, W // 3, 3)); g[:] = (93, 76, 60); g += rng.normal(0, 6, g.shape)
bg = Image.fromarray(g.clip(0, 255).astype(np.uint8)).resize((W, H), Image.NEAREST).convert('RGBA')
items = sorted([(k, p) for k, p in P.items() if 'grok_foot' in p], key=lambda kp: kp[1]['grok_foot'][1])
for k, p in items:
    fx, fy = p['grok_foot'][0] * 2.4 * SP, p['grok_foot'][1] * 2.4 * SP
    im = Image.open('final/' + p['img']).convert('RGBA')
    bg.alpha_composite(im, (int(fx - p['ax']), int(fy - p['ay'])))
bg.resize((W // 3, H // 3), Image.NEAREST).save('preview_full.png')
cx, cy = 690 * 2.4 * SP, 560 * 2.4 * SP
bg.crop((int(cx - 960), int(cy - 540), int(cx + 960), int(cy + 540))).save('preview_plaza.png')

# 입구 첫 장면 제안 (3번방 "가장 공들여"): 남문 → 가스 화로 → 롬 대장간(모루·장작) → 이장 집 → 북쪽 석상 분수
SCENE = [('fence_wood', 770, 866), ('fence_wood', 960, 866), ('south_gate', 860, 870), ('brazier', 800, 835),
         ('anvil', 1000, 745), ('woodpile', 1060, 740), ('barrels', 790, 745), ('sign_post', 900, 800),
         ('string_lights', 330, 445), ('candelabra', 1080, 205), ('tombs', 1300, 280), ('cocoons', 1420, 720), ('ember_rubble', 640, 330)]
for k, gx, gy in sorted(SCENE, key=lambda t: t[2]):
    p = P[k]; im = Image.open('final/' + p['img']).convert('RGBA')
    bg.alpha_composite(im, (int(gx * 2.4 * SP - p['ax']), int(gy * 2.4 * SP - p['ay'])))
for k, p in items:   # 뒤에 있는 건물이 소품을 덮지 않게 앞쪽 건물 다시 (단순 정렬 대신)
    pass
bg.resize((W // 3, H // 3), Image.NEAREST).save('preview_full.png')
cx, cy = 800 * 2.4 * SP, 700 * 2.4 * SP
bg.crop((int(cx - 960), int(cy - 600), int(cx + 960), int(cy + 480))).save('preview_entrance.png')
json.dump({'SP': SP, 'scene': SCENE, 'note': '그록 좌표. 월드 px = 그록 × 0.8 × SP'}, open('final/scene_suggest.json', 'w'), ensure_ascii=False, indent=1)
