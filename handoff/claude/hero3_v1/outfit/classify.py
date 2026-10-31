# 주인공 색판(1458색) 하나하나를 [살·머리 = 그대로] / [옷 = 망토 색으로]로 나눔. 서기 3장에서 자리별로 표를 모아 정함.
import numpy as np, json
from PIL import Image
H='/home/user/thor-like-game/handoff/claude/hero3_v1/'
G=H+'game144/'
V={'down_face':{'keep':[(94,106,116,129),(79,170,92,188),(116,170,129,188),(84,100,128,116),(80,112,94,134),(116,112,130,134)],
               'out':[(90,136,120,182),(64,150,84,240),(126,150,149,240),(88,186,122,211),(84,214,124,245),(84,122,96,138),(114,122,128,138)]},
   'right_face':{'keep':[(121,106,137,128),(117,170,131,190),(96,102,121,150)],
               'out':[(112,130,140,182),(83,150,110,240),(112,186,140,246),(115,124,134,140)]},
   'up':{'keep':[(88,102,120,168),(62,168,74,190),(134,168,146,190)],
         'out':[(70,180,140,238),(72,130,88,165),(122,130,138,165),(80,222,126,246)]}}
votes={}
for v,R in V.items():
    a=np.array(Image.open(G+v+'.png').convert('RGBA'))
    for cls,boxes in R.items():
        for x0,y0,x1,y1 in boxes:
            c=a[y0:y1,x0:x1].reshape(-1,4); c=c[c[:,3]>100]
            for px in c:
                k=tuple(int(t) for t in px[:3]); votes.setdefault(k,[0,0]); votes[k][0 if cls=='keep' else 1]+=1
allc={tuple(int(t) for t in px[:3]) for v in V for px in np.array(Image.open(G+v+'.png').convert('RGBA')).reshape(-1,4) if px[3]>100}
def rule(c):
    r,g,b=c; L=.299*r+.587*g+.114*b
    if r>110 and r>b+30 and g>70 and r-g<70: return 'keep'   # 살색 비슷
    return 'out'
lab={}
for c in allc:
    k,o=votes.get(c,[0,0])
    if k+o==0: lab[c]=rule(c)
    else: lab[c]='keep' if k*1.0>o*1.5 else 'out'      # 애매하면 옷(남색 머리카락 끝은 옷 쪽으로 감)
print('색',len(allc),'그대로',sum(1 for c in lab if lab[c]=='keep'),'옷',sum(1 for c in lab if lab[c]=='out'))
json.dump({'%d,%d,%d'%c:l for c,l in lab.items()},open(H+'outfit/palette_class.json','w'))
