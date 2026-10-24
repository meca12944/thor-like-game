"""주인공 때리기 1~3타 — 옆 말고 나머지 방향(↘ dr, ↓ down, ↗ up, ↑ n) (사장님 10-24 「8방향 시작해」).
 방향마다 자세 3장(A 당김, B 가로베기 끝, D 내리찍기 끝)만 그리고 사이 장 2벌: 1타 = A→B, 2타 = 1타 거꾸로(B→A, 공짜), 3타 = A→D.
 사이 장 중 흰 칼자국이 크게 박힌 장은 뺌, 작은 흰 조각은 atkclean 으로 지움. 장마다 발을 땅(190)에, 서기 얼굴 도장(얼굴 보이는 방향만).
   python3 assemble_atk8.py dr"""
import json,os,sys,numpy as np
from PIL import Image
from fix import boot_bot
from facefix import ref_head,place2
from atkclean import clean
OUT='/home/user/thor-like-game/motion_lab/research_v1/hero8/frames';LATEST='/home/user/thor-like-game/motion_lab/hero8/frames'
# 방향: (1타 사이장 폴더, 쓸 장), (3타 폴더, 쓸 장), 지울 장
SET={'dr':(('tw_dr_AB2',(0,1,3,4)),('tw_dr_AD2',(0,1,3,4)),{('tw_dr_AD2',3)})}
d=sys.argv[1];(ab,ia),(ad,id_),CL=SET[d]
def L(f,ii):
    out=[]
    for i in ii:
        a=np.array(Image.open(f'pl/{f}/{i:03d}.png').convert('RGBA'))
        out.append(clean(a) if (f,i) in CL else a)
    return out
s1=L(ab,ia);C={f'swing1_{d}':s1,f'swing2_{d}':s1[::-1],f'swing3_{d}':L(ad,id_)}
P,M=ref_head(np.array(Image.open(f'{LATEST}/idle_{d}/000.png').convert('RGBA')))
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
