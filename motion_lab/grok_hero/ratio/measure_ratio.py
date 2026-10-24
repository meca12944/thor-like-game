# 팀장 10-24 사장님 숙제: 동작마다 얼굴·몸 크기 비율이 왜 다른가 + 팔 흔들기 숫자.
# 장마다: 정수리(맨 위 줄), 얼굴(살색 덩어리, 위 40% 안) 위·아래, 어깨 보호대(청동) 맨 위 줄·바깥 폭, 손(살색 작은 덩어리) 위치.
# 표시 그림 sheet_<묶음>.png 로 눈으로 확인(잘못 잡은 장은 손으로 점 찍기)
import glob,json,os,sys,numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
G='..'
CLIPS={'walk_down':f'{G}/frames/walk_down','walk_se':f'{G}/se_test/walk_se','walk_right':f'{G}/frames/walk_right','walk_ne':f'{G}/se_test/walk_ne','walk_up':f'{G}/frames/walk_up',
       'run_down(그록)':f'{G}/frames/run_down','run_s':f'{G}/se_test/run_s','run_se':f'{G}/se_test/run_se','run_right':f'{G}/frames/run_right','run_ne':f'{G}/se_test/run_ne','run_n':f'{G}/se_test/run_n','run_up(그록)':f'{G}/frames/run_up'}
def skin(A):
    r,g,b,a=[A[...,i] for i in range(4)];return (a>0)&(r>130)&(r-g>18)&(r-g<70)&(g-b>2)&(g-b<45)
def bronze(A):
    r,g,b,a=[A[...,i] for i in range(4)];return (a>0)&(r>95)&(r-g>22)&(g-b>8)&~skin(A)
def meas(f):
    A=np.array(Image.open(f).convert('RGBA')).astype(int);op=A[...,3]>0
    rows=np.nonzero(op.sum(1)>=3)[0];top,bot=int(rows.min()),int(rows.max());H=bot-top
    sk=skin(A);L,n=ndimage.label(ndimage.binary_closing(sk,iterations=1));face=None;hands=[]
    for i in range(1,n+1):
        ys,xs=np.nonzero(L==i)
        if len(ys)<6: continue
        cy=ys.mean()
        if cy<top+0.33*H and len(ys)>=25 and (face is None or len(ys)>face[4]): face=(int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max()),len(ys))
        elif cy>top+0.3*H and len(ys)<400: hands.append((round(float(xs.mean()),1),round(float(ys.mean()),1),len(ys)))
    br=bronze(A);br[:top+10]=0;br[top+int(.45*H):]=0;by=np.nonzero(br.sum(1)>=2)[0]
    sh=None
    if len(by): y0=int(by.min());band=br[y0:y0+14];xs=np.nonzero(band.any(0))[0];sh=(y0,int(xs.min()),int(xs.max()))
    return dict(top=top,bot=bot,H=H,face=face,sh=sh,hands=hands)
if __name__=='__main__':
    R={}
    for k,d in CLIPS.items():
        R[k]=[dict(meas(f),f=os.path.relpath(f)) for f in sorted(glob.glob(d+'/*.png'))[:8]]
    json.dump(R,open('ratio_raw.json','w'),indent=1,ensure_ascii=False)
    # 표시 그림
    for grp,ks in (('walk',[k for k in CLIPS if k.startswith('walk')]),('run',[k for k in CLIPS if k.startswith('run')])):
        S=2;W=Image.new('RGB',(176*S*8,200*S*len(ks)),(70,74,80));d=ImageDraw.Draw(W)
        for r,k in enumerate(ks):
            for c,m in enumerate(R[k]):
                im=Image.open(m['f']).convert('RGBA').crop((40,0,216,200));ox,oy=c*176*S,r*200*S
                W.paste(im.resize((176*S,200*S),Image.NEAREST),(ox,oy),im.resize((176*S,200*S),Image.NEAREST))
                P=lambda x,y:(ox+(x-40)*S,oy+y*S)
                d.line([P(40,m['top']),P(216,m['top'])],fill=(80,200,255))
                if m['face']: x0,y0,x1,y1,_=m['face'];d.rectangle([P(x0,y0),P(x1,y1)],outline=(255,255,0))
                if m['sh']: y,x0,x1=m['sh'];d.line([P(x0,y),P(x1,y)],fill=(255,80,80),width=2)
                for hx,hy,_ in m['hands']: d.ellipse([P(hx-3,hy-3),P(hx+3,hy+3)],outline=(0,255,0),width=2)
            d.text((4,r*200*S+4),k,fill=(255,255,255))
        W.save(f'sheet_{grp}.png')
    print('ok')
