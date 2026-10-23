import json,numpy as np
from PIL import Image
s=open('test128/index.html').read();i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/');H=json.loads(s[j:e])
SH={}
def fr(f):
    if f[0] not in SH:SH[f[0]]=Image.open('test128/assets/'+H['sheets'][f[0]]).convert('RGBA')
    x,y,w,h,ax,ay=H['cells'][f[0]][f[1]][:6];c=Image.new('RGBA',(256,256));c.paste(SH[f[0]].crop((x,y,x+w,y+h)),(128-ax,189-ay));return c
def head(im):  # top of head (top of opaque), bottom of dark body, widths
    a=np.array(im).astype(int);al=a[...,3]>0;ys,xs=np.nonzero(al);return ys.min(),ys.max()
for base in ['idle','walk','run','dash','jump']:
    row=[]
    for d in ['right','down','up','dr']:
        k=f'{base}_{d}'
        if k not in H['anims']:row.append(f'{d}:-');continue
        hs=[];tops=[]
        for f in H['anims'][k]:
            t,b=head(fr(f));hs.append(b-t);tops.append(t)
        row.append(f'{d}: 키{np.median(hs):.0f} 머리y{min(tops)}~{max(tops)}')
    print(base,' | '.join(row))
from PIL import ImageDraw
rows=['idle','walk','run','dash','jump'];cols=['right','down','dr','up']
W=Image.new('RGBA',(170*len(cols),150*len(rows)),(70,110,60,255))
for r,b in enumerate(rows):
    for c,d in enumerate(cols):
        k=f'{b}_{d}'
        if k not in H['anims']:continue
        L=H['anims'][k];im=fr(L[min(len(L)-1,len(L)//2 if b in('walk','run') else (2 if b=='dash' else 0))])
        W.alpha_composite(im.crop((43,40,213,190)),(c*170,r*150))
g=ImageDraw.Draw(W)
for r in range(len(rows)):g.line((0,r*150+149,W.width,r*150+149),fill=(255,255,0));g.line((0,r*150+27,W.width,r*150+27),fill=(255,80,80))
W.resize((W.width*2,W.height*2),Image.NEAREST).save('/tmp/claude-0/-home-user-thor-like-game/07fd8ca2-ea28-5b70-9774-cc61d04fa98a/scratchpad/ml/sizes.png')
