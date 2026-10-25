# 얼굴 도장 (사장님 10-25 「얼굴 도장 시작해」): 게임 크기(final/)의 모든 장에, 방향별 기준 얼굴(face_<방향>.png, 144에서 PixelLab로 다듬음)을 C 방식으로 찍음
# C = 지금 장에서도 피부인 곳만(앞을 가리는 머리카락·손은 남김) + 그 장 피부 밝기에 맞춤. 자리 = 피부 겹침(IoU) 가장 큰 곳, 0.5 미만은 안 찍음. 얼굴 크기 8% 넘게 다르면 도장 크기 맞춤
# ↗·↑ 은 얼굴이 거의 안 보여 안 찍음. 결과 final_stamped/<동작>/, stamp_all.json
import glob,json,os,shutil,numpy as np
from PIL import Image
from common import load,face
from stamp import ref_head,scale_stamp,place
R=os.path.dirname(os.path.abspath(__file__));G=f'{R}/..'
DIRS={'down':['walk_down','run_down'],'dr':['walk_dr','run_dr'],'right':['walk_right','run_right']}
out={}
for d in os.listdir(f'{G}/final'):
    os.makedirs(f'{G}/final_stamped/{d}',exist_ok=True)
    for f in glob.glob(f'{G}/final/{d}/*.png'): shutil.copy(f,f'{G}/final_stamped/{d}/')
for dn,clips in DIRS.items():
    ra=load(f'{R}/face_{dn}.png');P,M,C=ref_head(ra,grow=1,smax=.58)   # 기준 얼굴은 피부가 더 진하고 또렷해 채도 기준을 넓힘
    for cl in clips:
        for f in sorted(glob.glob(f'{G}/final/{cl}/*.png')):
            a=load(f);k=1.0   # 기준 얼굴은 같은 크기(144)의 0번 장에서 만들었으니 크기 그대로 — 피부 넓이 차이는 머리카락이 가린 정도 차이라 배율로 쓰지 않음(줄이면 눈이 뭉개짐)
            P2,M2,C2=P,M,C;o,sc,at=place(a,P2,M2,C2,'D',thr=.35)   # D = 얼굴+둘레 통째 + 피부 밝기 맞춤 (C는 ↘ 눈이 빠지고, A는 옆얼굴이 밝게 튐)   # 옆얼굴: 기준 얼굴이 피부를 더 드러내 겹침이 0.41~0.49 → 얼굴+둘레 1칸 통째(A)로, 기준 0.35
            Image.fromarray(o).save(f'{G}/final_stamped/{cl}/{os.path.basename(f)}');out[f'{cl}/{os.path.basename(f)}']=dict(iou=sc,k=round(k,2),ok=at is not None)
        r=[v for kk,v in out.items() if kk.startswith(cl+'/')];print(cl,'찍음',sum(v['ok'] for v in r),'/',len(r),'겹침',[v['iou'] for v in r])
json.dump(out,open(f'{R}/stamp_all.json','w'),indent=1)
