# 바닥에서 달리기 (사장님 10-30 「캐릭이 뛸 때 점프하듯이 이상하다」 「바닥에서 달려야지」): 그록 영상 달리기는 두 발이 다 뜨는 장이 있어(정면 최대 20칸 = 키의 14%)
# 게임에선 그림자 위로 깡충깡충 뜀 → ① 가장 낮은 발이 땅에서 <뺄 뜸> 칸 넘게 뜬 장은 빼고 ② 남은 장은 가장 낮은 발이 땅(<발 줄>)에서 <남길 뜸> 칸 안으로 오게 그 장만 아래로 내림.
# (뜬 장을 내리기만 하면 그 장에서 머리가 거꾸로 푹 꺼짐(정면 19칸) → 크게 뜬 장은 빼는 게 나음)
# 쓰는 법: python3 ground.py <장 폴더> <출력 폴더> [뺄 뜸=10] [남길 뜸=0] [발 줄=245]  → 출력/000.png… + ground.json(뺀 장·내린 칸·원래 번호)
import sys, os, glob, json, shutil, numpy as np
from PIL import Image
src, out = sys.argv[1], sys.argv[2]; drop = int(sys.argv[3]) if len(sys.argv) > 3 else 10; keep = int(sys.argv[4]) if len(sys.argv) > 4 else 0; foot = int(sys.argv[5]) if len(sys.argv) > 5 else 245
fs = sorted(glob.glob(src + '/0*.png')); os.makedirs(out, exist_ok=True); rec = []
for i, f in enumerate(fs):
    im = Image.open(f).convert('RGBA'); a = np.asarray(im)[..., 3] > 0; b = int(np.nonzero(a.any(1))[0].max()); gap = foot - b
    if gap >= drop: rec.append({'from': i, 'gap': gap, 'dropped': True}); continue
    dy = max(0, gap - keep); o = Image.new('RGBA', im.size); o.paste(im, (0, dy), im)
    o.save(f'{out}/{len([r for r in rec if not r.get("dropped")]):03d}.png'); rec.append({'from': i, 'gap': gap, 'down': dy})
for j in glob.glob(src + '/*.json'): shutil.copy(j, out)
json.dump({'drop_at': drop, 'keep_gap': keep, 'foot': foot, 'frames': rec}, open(out + '/ground.json', 'w'), ensure_ascii=False, indent=1)
kept = [r for r in rec if not r.get('dropped')]
print(os.path.basename(src.rstrip('/')), '장', len(fs), '→', len(kept), '뺀 장', [r['from'] for r in rec if r.get('dropped')], '내린 칸', [r['down'] for r in kept])
