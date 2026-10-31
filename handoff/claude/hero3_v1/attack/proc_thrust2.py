# 공격 영상 여러 개 → 이어 붙인 게임 크기 몸 그림 + 칼 자리표 (사장님 10-31 「3타 진입이 끊긴다」 → 이어 찍기, 「바닥 효과 그대로 쓰자」)
# 쓰는 법: python3 atk_proc2.py <작업 폴더>   (작업 폴더/fv = v9 720 장들, f3 = 3타 이어 찍기 960 장들)
import numpy as np, json, os, sys, cv2
from PIL import Image
D=sys.argv[1].rstrip('/')+'/'
G='/home/user/thor-like-game/handoff/claude/hero3_v1/game144/'
S540=54/130                                      # 머리끝→허리띠: 540 영상 130칸 = 게임 54칸
SRC=[('f',960,list(range(57,102))),('fb',960,list(range(2,61)))]   # 찌르기 v3 57~101(달리기·찌르기) + 빼기 이어 찍기 2~60(첫 장 = v3 101장, 겹침 0.995)
pal=np.concatenate([np.asarray(Image.open(G+n).convert('RGBA')).reshape(-1,4) for n in ['right_face.png','down_face.png','up.png']])
pal=np.unique(pal[pal[:,3]>0][:,:3],axis=0).astype(np.float32)
DIRT=np.array([[46,38,28],[70,58,42],[98,82,60],[126,106,78]],np.float32)   # 흙 먼지 색(어두움→밝음)
def snap(c):
    flat=c.reshape(-1,3); idx=np.empty(len(flat),int)
    for i in range(0,len(flat),8192): idx[i:i+8192]=((flat[i:i+8192,None]-pal[None])**2).sum(2).argmin(1)
    return pal[idx].reshape(c.shape)
def shrink(rgb,al,S):
    pm=np.concatenate([rgb*al[...,None],al[...,None]*255],2); H,W=al.shape; w2,h2=round(W*S),round(H*S)
    ch=[np.asarray(Image.fromarray(pm[...,k].astype(np.float32),'F').resize((w2,h2),Image.LANCZOS)) for k in range(4)]
    A=np.clip(ch[3],0,255); c=np.stack([np.clip(ch[k]/np.maximum(A,1e-3)*255,0,255) for k in range(3)],2)
    return c,A
rows=[]; outs=[]
for vid,res,ks in SRC:
    S=S540*540/res
    for k in ks:
        a=np.asarray(Image.open(f'{D}{vid}/{k:04d}.png').convert('RGB')).astype(np.float32)
        r,g,b=a[...,0],a[...,1],a[...,2]; gx=g-np.maximum(r,b)
        mg0=(r-g>60)&(b-g>50); mg=cv2.dilate(mg0.astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))>0
        body=(gx<15)&~mg
        near=cv2.dilate(body.astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))>0
        dust=(gx>=15)&(gx<150)&(r<90)&(b<90)&~near&~mg       # 몸에서 떨어진 초록빛 흙 튀김
        al=np.clip(1-(gx-40)/60,0,1); al[dust]=0
        g2=np.minimum(g,np.maximum(r,b)+10); rgb=np.dstack([r,g2,b])
        # 분홍 칼 지우기: 몸 위 분홍은 둘레 몸 색으로, 바깥 분홍은 투명
        closed=cv2.morphologyEx(body.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))>0; over=mg&closed
        img=cv2.inpaint(np.clip(rgb,0,255).astype(np.uint8),over.astype(np.uint8)*255,5,cv2.INPAINT_TELEA).astype(np.float32)
        al[mg&~over]=0; al[over]=1
        c,A=shrink(img,al,S)
        # 먼지 층: 어두운 정도 → 흙색·불투명도
        dk=np.clip((248-g)/248,0,1)*dust; da=np.clip((dk-.25)/.45,0,1)
        dcol=DIRT[np.clip((1-dk)*4,0,3).astype(int)]
        dc,dA=shrink(dcol,da,S)
        body_px=A>128; dust_px=(dA>110)&~body_px
        out=np.zeros(c.shape[:2]+(4,),np.uint8)
        out[...,:3]=np.where(body_px[...,None],snap(c),np.where(dust_px[...,None],dc,0)).astype(np.uint8); out[...,3]=((body_px|dust_px)*255).astype(np.uint8)
        # 칼: 축 → 코등이(가장 넓은 곳) → 칼끝
        ys,xs=np.nonzero(mg0); P=np.stack([xs,ys],1).astype(float); cc=P.mean(0)
        w,v=np.linalg.eigh(np.cov((P-cc).T)); u=v[:,1]; t=(P-cc)@u; p=(P-cc)@np.array([-u[1],u[0]])
        st=4*res/540; bins=np.arange(t.min(),t.max()+st,st); wid=[]
        for i in range(len(bins)-1):
            s_=(t>=bins[i])&(t<bins[i+1]); wid.append(p[s_].max()-p[s_].min() if s_.sum()>2 else 0)
        gi=int(np.argmax(wid)); tg=(bins[gi]+bins[gi+1])/2
        tip=t.max() if abs(t.max()-tg)>abs(t.min()-tg) else t.min(); d=u if tip>tg else -u
        guard=cc+u*tg; L=abs(tip-tg)
        n=hid=0
        for tt in np.linspace(L*.15,L*.95,40):
            x,y=int(guard[0]+d[0]*tt),int(guard[1]+d[1]*tt)
            if 0<=x<res and 0<=y<res: n+=1; hid+=int(body[y,x])
        rows.append(dict(src=vid,k=k,guard=(guard*S).tolist(),ang=float(np.degrees(np.arctan2(d[1],d[0]))),blade=float(L*S),behind=bool(n and hid/n>.35),dust=int(dust_px.sum())))
        outs.append(out)
        print(vid,k,'먼지칸',int(dust_px.sum()),flush=True)
bb=[Image.fromarray(o).getbbox() for o in outs]
ox=128-round((bb[0][0]+bb[0][2])/2); oy=246-max(b[3] for b in bb[:20])
os.makedirs(D+'body2',exist_ok=True)
for i,(o,r_) in enumerate(zip(outs,rows)):
    cv_=Image.new('RGBA',(300,300)); im=Image.fromarray(o); cv_.paste(im,(ox+22,oy+22),im); cv_.save(f'{D}body2/{i:03d}.png')
    r_['guard']=[r_['guard'][0]+ox+22,r_['guard'][1]+oy+22]
json.dump(dict(frames=rows,canvas=300,foot=246+22,blade=round(float(np.median([r_['blade'] for r_ in rows])),1)),open(D+'grip2.json','w'),indent=0)
print('장',len(rows),'칼날(게임칸)',round(float(np.median([r_['blade'] for r_ in rows])),1),'뒤로 간 장',[(r_['src'],r_['k']) for r_ in rows if r_['behind']])
