"""리네트 게임 그림판(linette8.json)의 모든 동작 얼굴 모으기"""
import json,numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
R='/home/user/thor-like-game/test128/';A=json.load(open(R+'assets/anim/linette8.json'));SH={}
def cell(e):
    p=A['sheets'][e[0]]
    if p not in SH:SH[p]=Image.open(R+'assets/'+p).convert('RGBA')
    x,y,w,h,ax,ay=A['cells'][e[0]][e[1]];return np.array(SH[p].crop((x,y,x+w,y+h))),ax,ay
def skinmask(a,rows=34):
    r,g,b,al=[a[...,c].astype(int) for c in range(4)]
    m=(al>200)&(r>200)&(g>150)&(b>120)&(r>g+8)&(g>=b-5)&((r-b)>25)
    top=np.nonzero((al>40).any(1))[0].min();m[:top+6]=False;m[top+rows:]=False   # 얼굴만(목·몸 피부 빼기)
    lab,n=ndimage.label(m)
    if not n:return m
    k=np.argmax(ndimage.sum(m,lab,range(1,n+1)))+1;return lab==k
def face(a):
    m=skinmask(a)
    if m.sum()<6:return None
    ys,xs=np.nonzero(m);return int(ys.mean()),int(xs.mean()),len(ys)
if __name__=='__main__':
    F=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',10)
    ks=[k for k in sorted(A['anims']) if k.split('_')[-1] in('right','down','south') and not k.startswith('atk')]
    S=24;W=max(len(A['anims'][k]) for k in ks);im=Image.new('RGB',(90+W*(S*3+2),len(ks)*(S*3+4)),(50,55,50));d=ImageDraw.Draw(im)
    for ri,k in enumerate(ks):
        d.text((2,ri*(S*3+4)+30),k,fill=(255,255,0),font=F);ar=[]
        for ci,e in enumerate(A['anims'][k]):
            a=cell(e)[0];f=face(a)
            if not f:continue
            ar.append(f[2]);cy,cx=f[0],f[1]
            c=Image.fromarray(a).crop((cx-S//2,cy-S//2-2,cx+S//2,cy+S//2-2)).resize((S*3,S*3),Image.NEAREST);im.paste(c,(90+ci*(S*3+2),ri*(S*3+4)),c)
        print(f'{k:14s}',A['sheets'][A['anims'][k][0][0]].split('/')[-1],'얼굴 넓이',ar)
    im.save('lfaces_all.png');print(im.size)
