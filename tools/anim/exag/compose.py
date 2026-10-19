# compare video per motion: top row = in-game, bottom row = exaggerated skeleton version. cols right/left/down/up
import json,os,sys,subprocess
from PIL import Image,ImageDraw
man=json.load(open('all/manifest.json'));LOOP={'walk','idle'}
def L(p): return Image.open(p).convert('RGBA')
def orig(n): return [(L(f'all/{n}/k{i}.png'),t) for i,t in enumerate(man[n])]
def new(n):
    a,dr=n.split('_');T=man[n];N=len(T);fr=[];src=[]
    if dr=='right':
        g=sorted(os.listdir(f'all/{n}/gen_side'));k=0
        for i,t in enumerate(T):
            e=L(f'all/{n}/gen_side/{g[k]}');k+=1
            if k<len(g) and (i<N-1 or a in LOOP):
                m=L(f'all/{n}/gen_side/{g[k]}');k+=1;fr+=[(e,(t+1)//2)]+([(m,t//2)] if t//2 else []);src+=[i]+([None] if t//2 else [])
            else: fr.append((e,t));src.append(i)
    else:
        for i,t in enumerate(T):
            if i<N-1 or a in LOOP:
                fr+=[(L(f'all/{n}/gen_{i}/000.png'),(t+1)//2)]+([(L(f'all/{n}/gen_{i}/001.png'),t//2)] if t//2 else []);src+=[i]+([None] if t//2 else [])
            else: fr.append((L(f'all/{n}/gen_{N-2}/002.png'),t));src.append(i)
    return retrail(n,fr,src) if a.startswith('hit') else fr
import numpy as np
sys.path.insert(0,'all');from trail import trail
def retrail(n,seq,src):
    # attacks: wipe any trail PixelLab redrew, then lay the in-game crescent of that key back on top
    out=[]
    for (im,t),k in zip(seq,src):
        a=np.array(im);old,c=trail(im,420)
        if c: a[np.array(old)[...,3]>0]=0
        im=Image.fromarray(a,'RGBA')
        if k is not None:
            tr,c=trail(L(f'all/{n}/k{k}.png'),420)
            if c: im.alpha_composite(tr)
        out.append((im,t))
    return out
def ticks(seq): return [im for im,t in seq for _ in range(t)]
def clip(names,loops):
    cols={}
    for dr in ['right','down','up']:
        o=sum((ticks(orig(f'{n}_{dr}')) for n in names),[]);w=sum((ticks(new(f'{n}_{dr}')) for n in names),[])
        cols[dr]=(o,w)
    cols['left']=tuple([im.transpose(Image.FLIP_LEFT_RIGHT) for im in s] for s in cols['right'])
    T=max(len(cols[d][0]) for d in cols);out=[]
    for r in range(loops):
        for t in range(T):
            cv=Image.new('RGB',(4*384,2*384),(58,74,52));dd=ImageDraw.Draw(cv)
            for c,dr in enumerate(['right','left','down','up']):
                for row in (0,1):
                    s=cols[dr][row];im=s[t%len(s)].resize((384,384),Image.NEAREST);cv.paste(im,(c*384,row*384),im)
            dd.text((8,8),'in-game',fill=(255,255,0));dd.text((8,392),'NEW (exaggerated)',fill=(255,255,0))
            out.append(cv)
    return out
def save(frames,path,slow=1):
    d=path+'_f';os.makedirs(d,exist_ok=True);[f.save(f'{d}/{i:05d}.png') for i,f in enumerate(frames)]
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(60//slow),'-i',f'{d}/%05d.png','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',path+'.mp4'],check=True)
os.makedirs('all/out',exist_ok=True)
for name,parts,loops in [('walk',['walk'],4),('idle',['idle'],3),('hurt',['hurt'],4),('combo',['hit1','hit2','hit3'],3)]:
    if sys.argv[1:] and name not in sys.argv[1:]: continue
    fr=clip(parts,loops);save(fr,f'all/out/{name}')
    if name in ('combo','hurt'): save(fr,f'all/out/{name}_slow',2)
    print(name,len(fr))
