# 모든 동작 얼굴 모음표: 장마다 얼굴(살색 덩어리) 가운데로 28×28 잘라 8배 확대. 줄 = 동작, 칸 = 장
# 숫자: 얼굴 칸 색 수(많을수록 흐린 그림), 이웃 칸 밝기 차 평균(작을수록 뭉개짐)
import sys,glob,json,numpy as np
sys.path.insert(0,'../ratio');sys.path.insert(0,'../se_test')
from PIL import Image,ImageDraw,ImageFont
from measure_ratio import meas
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
G='..'
CL=[('그록 걷기↓',f'{G}/frames/walk_down'),('그록 걷기→',f'{G}/frames/walk_right'),('그록 달리기↓',f'{G}/frames/run_down'),('그록 달리기→',f'{G}/frames/run_right'),
    ('새 걷기↘',f'{G}/se_test/walk_se'),('새 걷기→(B)',f'{G}/se_test/walk_r2'),('새 달리기↓',f'{G}/se_test/run_s'),('새 달리기↘(B)',f'{G}/se_test/run_se2'),
    ('옛 주인공 걷기↓',f'{G}/../hero8/frames/walk_down'),('옛 주인공 걷기→',f'{G}/../hero8/frames/walk_right')]
Z=8;C=28;R={}
W=Image.new('RGB',(170+9*(C*Z+4),len(CL)*(C*Z+4)),(70,74,80));d=ImageDraw.Draw(W)
for r,(n,p) in enumerate(CL):
    fs=sorted(glob.glob(p+'/*.png'))[:8];cols=[];sharp=[]
    d.text((4,r*(C*Z+4)+C*Z//2),n,font=F,fill=(255,255,255))
    for c,f in enumerate(fs):
        m=meas(f)
        if not m['face']: continue
        x0,y0,x1,y1,_=m['face'];cx,cy=(x0+x1)//2,(y0+y1)//2
        im=Image.open(f).convert('RGBA').crop((cx-C//2,cy-C//2,cx+C//2,cy+C//2))
        A=np.array(im).astype(int);fm=A[...,3]>0
        sk=np.zeros(A.shape[:2],bool);sk[(y0-cy+C//2):(y1-cy+C//2+1),(x0-cx+C//2):(x1-cx+C//2+1)]=True;sk&=fm
        if sk.sum()>10:
            cols.append(len({tuple(v) for v in A[...,:3][sk]}));L=A[...,:3].mean(2);dx=np.abs(np.diff(L,axis=1))[sk[:,1:]&sk[:,:-1]];sharp.append(float(dx.mean()))
        bg=Image.new('RGBA',im.size,(70,74,80,255));bg.alpha_composite(im)
        W.paste(bg.convert('RGB').resize((C*Z,C*Z),Image.NEAREST),(170+c*(C*Z+4),r*(C*Z+4)))
    R[n]=dict(colors=round(float(np.median(cols)),1) if cols else None,edge=round(float(np.median(sharp)),1) if sharp else None,frames=len(fs))
    print(n,R[n])
W.save('face_sheet.png');json.dump(R,open('face_sheet.json','w'),ensure_ascii=False,indent=1)
