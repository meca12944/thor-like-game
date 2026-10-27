import json
from PIL import Image
def load(repo):
    p=f'{repo}/test128/index.html';s=open(p,encoding='utf-8').read();i=s.index('/*H8*/');j=s.index('{',i);d=0
    for k in range(j,len(s)):
        if s[k]=='{':d+=1
        elif s[k]=='}':
            d-=1
            if d==0: break
    return s,j,k,json.loads(s[j:k+1])
def save(repo,s,j,k,H):
    s=s[:j]+json.dumps(H,ensure_ascii=False,separators=(',',':'))+s[k+1:];open(f'{repo}/test128/index.html','w',encoding='utf-8').write(s)
_im={}
def cell(repo,H,sh,c):
    if sh not in _im: _im[sh]=Image.open(f'{repo}/test128/assets/'+H['sheets'][sh]).convert('RGBA')
    x,y,w,h,ax,ay=H['cells'][sh][c];return _im[sh].crop((x,y,x+w,y+h)),ax,ay
def meas(im,ax,ay):
    a=im.split()[3].point(lambda v:255 if v>40 else 0);b=a.getbbox()
    if not b: return None
    px=im.load();W,Hh=im.size;white=0
    for yy in range(Hh):
        for xx in range(W):
            r,g,bb,al=px[xx,yy]
            if al>40 and r>225 and g>225 and bb>225: white+=1
    return dict(top=b[1]-ay,bot=b[3]-ay,l=b[0]-ax,r=b[2]-ax,H=b[3]-b[1],white=white)
