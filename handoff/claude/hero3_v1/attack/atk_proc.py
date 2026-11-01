# 공격 영상 → 게임 크기 몸 그림 + 칼 자리표 (분홍 칼 = 손 자리·각도·앞뒤)
# 쓰는 법: 영상 장면을 f/0001.png… 로 꺼낸 폴더에 이 파일을 두고 돌림(ffmpeg -i 영상 f/%04d.png). 결과 body/*.png(칼 지운 몸, 300칸) + grip.json(장마다 코등이 자리·칼 각도·몸 앞/뒤)
# 사장님 10-31 「검 공격 시안 나왔다」(그록 v9, 옆). 76~80장(두 겹 겹친 장)·113장부터(긴 멈춤) 뺌.
import numpy as np, json, os, sys, cv2
from PIL import Image
D=os.path.dirname(os.path.abspath(__file__))+'/'
G='/home/user/thor-like-game/handoff/claude/hero3_v1/game144/'
FR=list(range(1,76))+list(range(81,113))      # 76~80 겹친 장 뺌, 마지막 멈춤은 113부터 자름
S=54/130                                        # 머리끝→허리띠: 영상 130칸 = 게임 54칸
def key(a):
    r,g,b=a[...,0],a[...,1],a[...,2]
    green=g-np.maximum(r,b); al=np.clip(1-(green-40)/60,0,1)
    g2=np.minimum(g,np.maximum(r,b)+10)
    return np.dstack([r,g2,b]),al
pal=np.concatenate([np.asarray(Image.open(G+n).convert('RGBA')).reshape(-1,4) for n in ['right_face.png','down_face.png','up.png']])
pal=np.unique(pal[pal[:,3]>0][:,:3],axis=0).astype(np.float32)
def shrink(rgb,al):
    pm=np.concatenate([rgb*al[...,None],al[...,None]*255],2)
    H,W=al.shape; w2,h2=round(W*S),round(H*S)
    ch=[np.asarray(Image.fromarray(pm[...,k].astype(np.float32),'F').resize((w2,h2),Image.LANCZOS)) for k in range(4)]
    A=np.clip(ch[3],0,255); c=np.stack([np.clip(ch[k]/np.maximum(A,1e-3)*255,0,255) for k in range(3)],2)
    flat=c.reshape(-1,3); idx=np.empty(len(flat),int)
    for i in range(0,len(flat),8192): idx[i:i+8192]=((flat[i:i+8192,None]-pal[None])**2).sum(2).argmin(1)
    return np.concatenate([pal[idx].reshape(h2,w2,3),((A>128)*255)[...,None]],2).astype(np.uint8)
rows=[]; bodies=[]
for k in FR:
    a=np.asarray(Image.open(f'{D}f/{k:04d}.png').convert('RGB')).astype(np.float32)
    r,g,b=a[...,0],a[...,1],a[...,2]
    mg=((r-g>60)&(b-g>50))
    mg=cv2.dilate(mg.astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))>0   # 분홍+초록 섞인 회색 가장자리까지
    rgb,al=key(a)
    # 칼 모양: 축(PCA) → 코등이(가장 넓은 곳) → 칼끝(코등이에서 먼 끝)
    ys,xs=np.nonzero((r-g>60)&(b-g>50)); P=np.stack([xs,ys],1).astype(float); c=P.mean(0)
    w,v=np.linalg.eigh(np.cov((P-c).T)); u=v[:,1]; t=(P-c)@u; p=(P-c)@np.array([-u[1],u[0]])
    bins=np.arange(t.min(),t.max()+4,4); wid=[]
    for i in range(len(bins)-1):
        s_=(t>=bins[i])&(t<bins[i+1]); wid.append(p[s_].max()-p[s_].min() if s_.sum()>2 else 0)
    gi=int(np.argmax(wid)); tg=(bins[gi]+bins[gi+1])/2
    tip_t=t.max() if abs(t.max()-tg)>abs(t.min()-tg) else t.min()
    d=u if tip_t>tg else -u
    guard=c+u*tg; blade=abs(tip_t-tg)
    # 분홍 지우기: 몸 위에 있던 분홍은 둘레 몸 색으로 메우고, 바깥 분홍은 투명
    body=(al>0.5)&~mg
    closed=cv2.morphologyEx(body.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))>0
    over=mg&closed
    img=np.clip(rgb,0,255).astype(np.uint8).copy()
    img=cv2.inpaint(img,over.astype(np.uint8)*255,5,cv2.INPAINT_TELEA)
    al2=al.copy(); al2[mg&~over]=0; al2[over]=1
    sm=shrink(img.astype(np.float32),al2)
    # 앞/뒤: 코등이→칼끝 선(평균 날 길이)에서 몸에 가려진 비율
    rows.append(dict(k=k,guard=(guard*S).tolist(),ang=float(np.degrees(np.arctan2(d[1],d[0]))),blade=float(blade*S),dir=d.tolist(),guard_v=guard.tolist()))
    bodies.append((sm,body,mg))
L=np.median([r_['blade'] for r_ in rows])/S
for r_,(sm,body,mg) in zip(rows,bodies):
    gx,gy=r_['guard_v']; dx,dy=r_['dir']; n=0; hid=0
    for tt in np.linspace(L*0.15,L*0.95,40):
        x,y=int(gx+dx*tt),int(gy+dy*tt)
        if 0<=x<540 and 0<=y<540:
            n+=1; hid+= int(body[y,x] and not mg[y,x])
    r_['behind']=bool(n and hid/n>0.35); r_['hid']=round(hid/max(n,1),2)
# 한 자리로 옮기기(장마다 같은 만큼): 첫 장 발 = 246, 몸 가운데 = 128
bb=[Image.fromarray(s).getbbox() for s,_,_ in bodies]
ox=128-round((bb[0][0]+bb[0][2])/2); oy=246-max(b[3] for b in bb[:20])
os.makedirs(D+'body',exist_ok=True)
for i,((sm,_,_),r_) in enumerate(zip(bodies,rows)):
    c=Image.new('RGBA',(300,300)); im=Image.fromarray(sm); c.paste(im,(ox+22,oy+22),im); c.save(f'{D}body/{i:03d}.png')
    r_['guard']=[r_['guard'][0]+ox+22,r_['guard'][1]+oy+22]
json.dump(dict(frames=rows,canvas=300,foot=246+22,scale=S,videoBladeLen=round(L*S,1)),open(D+'grip.json','w'),indent=0)
print('장',len(rows),'영상 칼날 길이(게임칸)',round(L*S,1),'뒤로 간 장',[r_['k'] for r_ in rows if r_['behind']])
