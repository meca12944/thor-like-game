"""주인공 게임 그림판(/*H8*/)의 모든 동작에서 얼굴만 잘라 모으고 숫자로 비교"""
import json,numpy as np,sys
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
R='/home/user/thor-like-game/test128/'
s=open(R+'index.html').read();i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/');H=json.loads(s[j:e])
SH={}
def cell(e):
    if e[0] not in SH:SH[e[0]]=Image.open(R+'assets/'+H['sheets'][e[0]]).convert('RGBA')
    x,y,w,h,ax,ay=H['cells'][e[0]][e[1]];return np.array(SH[e[0]].crop((x,y,x+w,y+h))),ax,ay
def face(a):
    r,g,b,al=[a[...,c].astype(int) for c in range(4)]
    skin=(al>200)&(r>150)&(g>95)&(b>70)&(r>g+15)&(g>b)&(r<250)
    top=np.nonzero((al>40).any(1))[0].min();skin[top+45:]=False   # 머리 쪽만
    lab,n=ndimage.label(skin)
    if not n:return None
    k=np.argmax(ndimage.sum(skin,lab,range(1,n+1)))+1;ys,xs=np.nonzero(lab==k)
    return int(ys.mean()),int(xs.mean()),len(ys),a[ys,xs,:3].mean(0)
if __name__=='__main__':
    F=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',10)
    names=[k for k in H['anims'] if k.split('_')[-1] in('right','down') and not k.startswith(('hit','rec','hold','fx'))]
    rows=[]
    for k in sorted(names):
        L=H['anims'][k];fr=[cell(e) for e in L];fs=[face(a) for a,_,_ in fr]
        ok=[f for f in fs if f]
        if not ok:continue
        src=sorted(set(H['sheets'][e[0]].split('/')[-1] for e in L))
        rows.append((k,fr,fs,src))
        print(f'{k:16s} 시트 {",".join(src):40s} 얼굴 넓이 {np.mean([f[2] for f in ok]):5.0f} 범위 {min(f[2] for f in ok)}-{max(f[2] for f in ok)} 피부색 {np.round(np.mean([f[3] for f in ok],0))}')
    S=26;W=max(len(r[1]) for r in rows)
    im=Image.new('RGB',(90+W*(S*3+2),len(rows)*(S*3+4)),(50,55,50));d=ImageDraw.Draw(im)
    for ri,(k,fr,fs,src) in enumerate(rows):
        d.text((2,ri*(S*3+4)+30),k,fill=(255,255,0),font=F)
        for ci,((a,ax,ay),f) in enumerate(zip(fr,fs)):
            if not f:continue
            cy,cx=f[0],f[1];c=Image.fromarray(a).crop((cx-S//2,cy-S//2-3,cx+S//2,cy+S//2-3)).resize((S*3,S*3),Image.NEAREST)
            im.paste(c,(90+ci*(S*3+2),ri*(S*3+4)),c)
    im.save('faces_all.png');print(im.size)
