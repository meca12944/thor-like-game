import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
SRC='/workspace/town-demo/src/'; OUT='/workspace/town-demo/assets/'

def key(path):
    im=np.asarray(Image.open(SRC+path).convert('RGB')).astype(np.float32)
    H,W,_=im.shape
    border=np.concatenate([im[:8].reshape(-1,3),im[-8:].reshape(-1,3),im[:,:8].reshape(-1,3),im[:,-8:].reshape(-1,3)])
    bg=np.median(border,0)
    d=np.sqrt(((im-bg)**2).sum(2))
    # magenta-ness: how much min(r,b) exceeds g
    r,g,b=im[...,0],im[...,1],im[...,2]
    mag=np.minimum(r,b)-g
    hard=(d<70)|((mag>90)&(d<130))
    fg=~hard
    fg=ndi.binary_opening(fg,iterations=1)
    fg=ndi.binary_erosion(fg,iterations=1)   # 1px erode against fringe
    fg=ndi.binary_fill_holes(fg) & ~( (d<40) )
    # despill near edges
    edge=fg & ~ndi.binary_erosion(fg,iterations=3)
    ex=np.clip(np.minimum(r,b)-g,0,None)
    out=im.copy()
    sel=edge&(ex>0)
    out[...,0][sel]-=ex[sel]; out[...,2][sel]-=ex[sel]
    rgba=np.dstack([np.clip(out,0,255),fg*255.0]).astype(np.uint8)
    return rgba,fg,bg

def components(fg,minpx=1500,dil=14):
    lab,n=ndi.label(ndi.binary_dilation(fg,iterations=dil))
    objs=[]
    for i,sl in enumerate(ndi.find_objects(lab)):
        m=(lab[sl]==i+1)&fg[sl]
        if m.sum()<minpx: continue
        ys,xs=np.nonzero(m)
        y0,y1=sl[0].start+ys.min(),sl[0].start+ys.max()+1
        x0,x1=sl[1].start+xs.min(),sl[1].start+xs.max()+1
        full=np.zeros_like(fg); full[sl]=m
        objs.append(dict(box=(x0,y0,x1,y1),mask=full[y0:y1,x0:x1],cy=(y0+y1)/2,cx=(x0+x1)/2))
    # rows
    objs.sort(key=lambda o:o['cy'])
    rows=[]
    for o in objs:
        if rows and abs(rows[-1][-1]['cy']-o['cy'])<90: rows[-1].append(o)
        else: rows.append([o])
    for r in rows: r.sort(key=lambda o:o['cx'])
    return rows

def crop(rgba,o):
    x0,y0,x1,y1=o['box']; c=rgba[y0:y1,x0:x1].copy(); c[...,3]=c[...,3]*o['mask']
    return c

def feetx(o):
    m=o['mask']; h=m.shape[0]; ys,xs=np.nonzero(m[int(h*0.85):])
    return xs.mean() if len(xs) else m.shape[1]/2

def strip(name,crops_objs,scale,flipfeet=False):
    frames=[]
    for c,o in crops_objs:
        im=Image.fromarray(c,'RGBA'); w,h=im.size
        nw,nh=max(1,round(w*scale)),max(1,round(h*scale))
        im=im.resize((nw,nh),Image.LANCZOS)
        a=np.asarray(im).copy(); a[...,3]=np.where(a[...,3]>110,255,0)  # crisp alpha
        frames.append((Image.fromarray(a,'RGBA'),feetx(o)*scale))
    L=max(fx for f,fx in frames); R=max(f.size[0]-fx for f,fx in frames)
    cw=int(np.ceil(L+R))+4; ch=max(f.size[1] for f,_ in frames)+2
    ax=int(np.ceil(L))+2
    sheet=Image.new('RGBA',(cw*len(frames),ch),(0,0,0,0))
    for i,(f,fx) in enumerate(frames):
        sheet.paste(f,(i*cw+ax-int(round(fx)),ch-1-f.size[1]),f)
    sheet.save(OUT+name+'.png')
    return dict(src=name+'.png',w=cw,h=ch,n=len(frames),ax=ax,ay=ch-1,
                bodyH=[f.size[1] for f,_ in frames])

meta={}
# world = 1280x720 (bg native). concept spec: hero 130px@1024 -> 162.5; slime 60->75; spirit 80->100
rgba,fg,bg=key('hero_walk_sheet.jpg'); rows=components(fg)
print('walk rows',[len(r) for r in rows],bg)
H0=np.median([o['box'][3]-o['box'][1] for o in rows[0]]); hs=162.5/H0
print('hero src h',H0,'scale',hs)
for nm,r in zip(['walk_down','walk_up','walk_right'],rows):
    items=[(crop(rgba,o),o) for o in r]
    if nm=='walk_right':  # 4th frame in source faces left -> mirror it
        c,o=items[3]; o=dict(o); o['mask']=o['mask'][:,::-1]; items[3]=(c[:,::-1].copy(),o)
    meta['hero_'+nm]=strip('hero_'+nm,items,hs)
rgba,fg,bg=key('hero_attack_sheet.jpg'); rows=components(fg)
print('atk rows',[len(r) for r in rows],[[o['box'] for o in r] for r in rows],bg)
for nm,r in zip(['atk_r1','atk_up','atk_right'],rows):
    meta['hero_'+nm]=strip('hero_'+nm,[(crop(rgba,o),o) for o in r],hs)
rgba,fg,bg=key('slime_spirit_sheet.jpg'); rows=components(fg,minpx=800,dil=10)
print('slime rows',[len(r) for r in rows],[[o['box'] for o in r] for r in rows],bg)
r1=rows[0]; ss=75/(r1[0]['box'][3]-r1[0]['box'][1])
meta['slime']=strip('slime',[(crop(rgba,o),o) for o in [r1[0],r1[1],r1[-1]]],ss)
sp=100/np.median([o['box'][3]-o['box'][1] for o in rows[1]])
meta['spirit']=strip('spirit',[(crop(rgba,o),o) for o in rows[1]],sp)
json.dump(meta,open(OUT+'sprites.json','w'),indent=1)
for k,v in meta.items(): print(k,{a:b for a,b in v.items() if a!='src'})
