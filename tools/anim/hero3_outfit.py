# 주인공 옷 전체 색 = 장착 망토 색 (사장님 10-31 「망토색에 따라서 옷색깔도 전부」 「바지색깔도」 「옷전체 색깔 다 바꿔야된다구」 → 「넣어」)
# 게임에 넣을 자료(/*OUTFIT*/ 한 줄)를 test128/index.html 에 씀: 밝기 기준 P, 그대로 둘 따뜻한 색 34개, 망토별 색 띠 64칸.
# 칠하기 규칙은 handoff/claude/hero3_v1/outfit/outfit.py 와 똑같음(게임 JS = outfitBuildMap / outfitApply). 새 망토를 넣거나 아이콘을 바꾸면 이 파일을 다시 돌림.
# 쓰는 법: python3 tools/anim/hero3_outfit.py   (저장소 맨 위에서)
import json, re, os, importlib.util
import numpy as np
from PIL import Image
R = os.path.dirname(os.path.abspath(__file__)) + '/../../'
OF = R + 'handoff/claude/hero3_v1/outfit/'
spec = importlib.util.spec_from_file_location('of', OF + 'outfit.py'); of = importlib.util.module_from_spec(spec); spec.loader.exec_module(of)
idx = open(R + 'test128/index.html', encoding='utf-8').read()
ids = sorted(set(re.findall(r'"([a-z0-9_]+)":\{[^{}]*"s":"cloak"', idx)))
ramp = {}
for k in ids:
    ic = R + f'test128/assets/icons/grok/{k}_128.webp'
    if not os.path.exists(ic): print('아이콘 없음(원래 옷 색):', k); continue
    a = np.array(Image.open(ic).convert('RGBA')).reshape(-1, 4); a = a[a[:, 3] > 200][:, :3].astype(float); a = a[np.argsort(of.lum(a))]
    a = a[int(len(a) * .08):int(len(a) * .97)]; n = 64
    rr = np.array([a[int(i / n * len(a)):max(int(i / n * len(a)) + 1, int((i + 1) / n * len(a)))].mean(0) for i in range(n)])
    ramp[k] = [int(v) for v in rr.astype(np.uint8).reshape(-1)]   # 파이썬 astype(uint8) = 버림 → 게임과 칸 하나까지 같음
keep = []
for c, v in of.CLS.items():
    r, g, b = c; L = .299 * r + .587 * g + .114 * b; warm = r - b >= 10; skin = warm and L >= 95 and r > b + 30
    if v == 'keep' and warm and L >= 70 and not skin: keep.append(r * 65536 + g * 256 + b)
O = {'_doc': '주인공 옷 전체 색 = 장착 망토 색 (사장님 10-31). tools/anim/hero3_outfit.py 가 씀. 살·머리·눈은 그대로, 남색(코트·망토) = 띠 가운데, 바지·장화·가죽 = 제 밝기대로.',
     'P': [float(of.P5), float(of.P50), float(of.P95)], 'keep': sorted(keep), 'ramp': ramp}
line = '/*OUTFIT*/const OUTFIT=' + json.dumps(O, ensure_ascii=False, separators=(',', ':')) + ';'
if '/*OUTFIT*/' in idx:
    idx = re.sub(r'/\*OUTFIT\*/const OUTFIT=.*?;\n', lambda m: line + '\n', idx, count=1)
else:
    i = idx.index('/*H8*/'); j = idx.index('\n', i) + 1; idx = idx[:j] + line + '\n' + idx[j:]
open(R + 'test128/index.html', 'w', encoding='utf-8').write(idx)
print('망토', len(ramp), '그대로 색', len(keep), 'P', O['P'], '글자', len(line))
