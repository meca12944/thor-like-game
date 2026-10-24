"""주인공 옆모습 때리기 1~3타 (사장님 10-24 「가안으로 가자」: 당김·휘두름·마무리 그림, 10-22 「칼 베는 몸동작 안 씀」을 바꿈).
 1타 = 당김(A) → 가로 베기 → 끝(B), 2타 = B → 되돌려 베기 → A (사이 장 중 하얀 효과 그린 2장은 뺌), 3타 = 머리 위(C) → 내려찍기 → 끝(D).
 크기 그대로(얼굴 넓이 57 = 서기와 같음), 발을 땅에 디딘 공격이라 장마다 발을 땅(190)에, 서기 얼굴 도장."""
import json,os,numpy as np
from PIL import Image
from fix import boot_bot
from facefix import ref_head,place2
OUT='/home/user/thor-like-game/motion_lab/research_v1/hero8/frames';LATEST='/home/user/thor-like-game/motion_lab/hero8/frames'
L=lambda d,ii:[np.array(Image.open(f'pl/{d}/{i:03d}.png').convert('RGBA')) for i in ii]
C={'swing1_right':L('tw_atk_AB',range(5)),'swing2_right':L('tw_atk_BA',(0,3,4)),'swing3_right':L('tw_atk_CD',(0,1,2,4))}  # 3타 4번째 장 = 머리카락 삐죽 + 흰 칼자국 박힘 → 뺌 (팀장 10-24)
P,M=ref_head(np.array(Image.open(f'{LATEST}/idle_right/000.png').convert('RGBA')))
CJ='/home/user/thor-like-game/motion_lab/research_v1/hero8/clips.json';J=json.load(open(CJ))
for k,fr in C.items():
    out=[]
    for a in fr:
        a=np.roll(a,190-boot_bot(a),0);b,sc=place2(a,P,M,thr=0.3);out.append(b)
    os.makedirs(f'{OUT}/{k}',exist_ok=True)
    for f in os.listdir(f'{OUT}/{k}'):os.remove(f'{OUT}/{k}/{f}')
    for i,a in enumerate(out):Image.fromarray(a).save(f'{OUT}/{k}/{i:03d}.png')
    J[k]={'frames':len(out),'ticks':[3]*len(out)};print(k,len(out),'발',[boot_bot(a) for a in out])
json.dump(J,open(CJ,'w'),ensure_ascii=False,indent=1)
