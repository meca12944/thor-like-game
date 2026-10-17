# Combo + skill sprite extraction. Reuses the chroma-key / connected-component helpers from extract.py
# (same key(), components(), crop()), adds per-frame anchors (tunic centre x, row ground y),
# blond->brown hair recolour (concept hero is brown-haired) and hero/effect splits.
import numpy as np, json, colorsys
from PIL import Image
from scipy import ndimage as ndi
_src=open('/workspace/town-demo/tools/extract.py').read().split('meta={}')[0]
exec(_src)   # defines key, components, crop, feetx, strip, SRC, OUT
meta=json.load(open(OUT+'sprites.json'))
for k in [k for k in meta if k.startswith(('cb_','sk_','fx_'))]: del meta[k]

# world scale of the existing hero (walk sheet) -> source standing heights per sheet
_,fgw,_=key('hero_walk_sheet.jpg'); rw=components(fgw)
H0=np.median([o['box'][3]-o['box'][1] for o in rw[0]]); HS=162.5/H0
STAND={'hero_combo_sheet.jpg':None,'skill_sheet_1.jpg':None,'skill_sheet_2.jpg':None,'skill_sheet_3.jpg':None}

def hsv(a):
    a=a.astype(np.float32)/255; r,g,b=a[...,0],a[...,1],a[...,2]
    mx=a.max(-1); mn=a.min(-1); d=mx-mn+1e-6
    h=np.where(mx==r,((g-b)/d)%6,np.where(mx==g,(b-r)/d+2,(r-g)/d+4))*60
    return h,d/(mx+1e-6),mx

def tunic_cx(c,m):
    r,g,b=[c[...,i].astype(int) for i in range(3)]
    t=m&(b>90)&(b>r+30)&(b>g+20)&(r<110)
    ys,xs=np.nonzero(t)
    return (xs.mean(),ys.mean()) if len(xs)>80 else (None,None)

def boot_bottom(c,m,cx):
    r,g,b=[c[...,i].astype(int) for i in range(3)]
    bm=m&(r>g+25)&(g>b+5)&(r<170)&(b<70)&(g>25)&(r>55)
    if cx is not None:
        x0=max(0,int(cx-70)); bm[:,:x0]=False; bm[:,int(cx+70):]=False
    ys,xs=np.nonzero(bm)
    return ys.max() if len(ys) else None

def recolor_hair(c,m,top,cx,rect=None):
    """blond -> concept brown, only near the head (top of the body, around tunic x).
    rect=(x0,y0,x1,y1) in crop coords: recolour every blond pixel inside it instead (manual fix-ups)."""
    h,s,v=hsv(c[...,:3])
    y=(h>28)&(h<62)&(s>.30)&(v>.42)&m
    if rect is not None:
        r=np.zeros_like(y); r[max(0,rect[1]):rect[3],max(0,rect[0]):rect[2]]=True; y&=r
        top,cx=-999,None
    lab,n=ndi.label(ndi.binary_closing(y,iterations=1))
    out=c.copy()
    for i,sl in enumerate(ndi.find_objects(lab)):
        mm=lab[sl]==i+1; area=mm.sum()
        if area<25 or (area>2600 and cx is not None): continue
        ys,xs=np.nonzero(mm); y0=sl[0].start+ys.min(); xc=sl[1].start+xs.mean()
        if cx is not None and (y0>top+48 or abs(xc-cx)>48): continue
        full=np.zeros_like(y); full[sl]=mm; full&=y
        vv=v[full]; nv=np.clip(.10+(vv-.42)*.95,.08,.62)   # brown ramp like the walk sheet
        hh=24/360.; ss=np.clip(.82-(nv-.1)*.5,.5,.85)
        rgb=np.array([colorsys.hsv_to_rgb(hh,a,b) for a,b in zip(ss,nv)])*255
        out[...,:3][full]=rgb.astype(np.uint8)
    return out

SHEETS={}
def sheet(fn):
    if fn not in SHEETS:
        rgba,fg,bg=key(fn); rows=components(fg)
        NR=4 if fn=='skill_sheet_3.jpg' else 3   # grid rows: bin by centre y (row heuristics merge rows on the 4-row sheet)
        objs=[]
        for o in [o for r in rows for o in r]:   # split objects that bridge two grid rows (sparks touching the next row)
            x0,y0,x1,y1=o['box']; gh=720/NR; cut=[int(k*gh) for k in range(1,NR) if y0+25<k*gh<y1-25]
            if not cut: objs.append(o); continue
            for a,b in zip([y0]+cut,cut+[y1]):
                m=o['mask'][a-y0:b-y0]; ys,xs=np.nonzero(m)
                if len(xs)<1500: continue
                objs.append(dict(box=(x0+xs.min(),a+ys.min(),x0+xs.max()+1,a+ys.max()+1),mask=m[ys.min():ys.max()+1,xs.min():xs.max()+1],cy=a+(ys.min()+ys.max())/2,cx=x0+(xs.min()+xs.max())/2))
        rows=[sorted([o for o in objs if int(o['cy']//(720/NR))==i],key=lambda o:o['cx']) for i in range(NR)]
        SHEETS[fn]=(rgba,fg,rows)
        print(fn,'cells/row',[len(r) for r in rows])
    return SHEETS[fn]

def cell(fn,r,c,xr=None):
    rgba,fg,rows=sheet(fn); o=rows[r][c]
    x0,y0,x1,y1=o['box']; m=o['mask'].copy()
    if xr:  # keep only source x in [xr[0],xr[1])
        xs=np.arange(x0,x1); keep=(xs>=xr[0])&(xs<xr[1]); m[:,~keep]=False
    return rgba[y0:y1,x0:x1].copy(),m,(x0,y0)

def row_ground(fn,r):
    rgba,fg,rows=sheet(fn); gs=[]
    for o in rows[r]:
        c,m,(x0,y0)=cell(fn,r,rows[r].index(o)); cx,_=tunic_cx(c,m); b=boot_bottom(c,m,cx)
        if b is not None: gs.append(b+y0)
    return int(np.median(gs)) if gs else None

def pack(name,frames,scale):
    """frames: list of (rgba_crop, mask, ax, ay) in crop coords; common anchor in packed strip."""
    out=[]
    for c,m,ax,ay in frames:
        c=c.copy(); c[...,3]=(m*255).astype(np.uint8)
        ys,xs=np.nonzero(m)
        if len(xs)==0: continue
        bx0,by0,bx1,by1=xs.min(),ys.min(),xs.max()+1,ys.max()+1
        c=c[by0:by1,bx0:bx1]; ax-=bx0; ay-=by0
        im=Image.fromarray(c,'RGBA'); w,h=im.size
        nw,nh=max(1,round(w*scale)),max(1,round(h*scale))
        im=im.resize((nw,nh),Image.LANCZOS); a=np.asarray(im).copy(); a[...,3]=np.where(a[...,3]>110,255,0)
        out.append((Image.fromarray(a,'RGBA'),ax*scale,ay*scale))
    L=max(ax for _,ax,_ in out); R=max(f.size[0]-ax for f,ax,_ in out)
    T=max(ay for _,_,ay in out); B=max(f.size[1]-ay for f,_,ay in out)
    cw=int(np.ceil(L+R))+4; ch=int(np.ceil(T+B))+4; AX=int(np.ceil(L))+2; AY=int(np.ceil(T))+2
    sh=Image.new('RGBA',(cw*len(out),ch),(0,0,0,0))
    for i,(f,ax,ay) in enumerate(out): sh.paste(f,(i*cw+AX-int(round(ax)),AY-int(round(ay))),f)
    sh.save(OUT+name+'.png')
    meta[name]=dict(src=name+'.png',w=cw,h=ch,n=len(out),ax=AX,ay=AY)
    return meta[name]

def hero_strip(name,fn,r,cols,scale,splits=None,manual=None,hair=True,hairrect=None,nohair=()):
    """splits: {col:(xmin,xmax)} source-x range for the hero part. manual: {col:(ax_src,ay_src)}"""
    g=row_ground(fn,r); frames=[]; anchors=[]
    for c in cols:
        crop,m,(x0,y0)=cell(fn,r,c,(splits or {}).get(c))
        cx,cy=tunic_cx(crop,m)
        if manual and c in manual: cx,gg=manual[c][0]-x0,(manual[c][1] if len(manual[c])>1 else g)
        else: gg=g
        if cx is None: ys,xs=np.nonzero(m); cx=xs.mean()
        ay=gg-y0
        if hairrect and c in hairrect:
            q=hairrect[c]; crop=recolor_hair(crop,m,0,0,(q[0]-x0,q[1]-y0,q[2]-x0,q[3]-y0))
        elif hair and c not in nohair:
            ys,xs=np.nonzero(m[:, max(0,int(cx-45)):int(cx+45)]); top=ys.min() if len(ys) else 0
            crop=recolor_hair(crop,m,top,cx)
        frames.append((crop,m,cx,ay)); anchors.append((cx+x0,gg))
    pack(name,frames,scale); meta[name]['srcAnchor']=[[float(a),float(b)] for a,b in anchors]
    return anchors

def fx_strip(name,fn,r,cols,scale,xr=None,hero_anchor=None,anchor='center'):
    frames=[];offs=[]
    for i,c in enumerate(cols):
        crop,m,(x0,y0)=cell(fn,r,c,xr)
        ys,xs=np.nonzero(m)
        ax=(xs.min()+xs.max())/2; ay=ys.max() if anchor=='bottom' else (ys.min()+ys.max())/2
        frames.append((crop,m,ax,ay))
        if hero_anchor: offs.append([float((ax+x0-hero_anchor[i][0])*scale),float((ay+y0-hero_anchor[i][1])*scale)])
    pack(name,frames,scale)
    if offs: meta[name]['off']=offs

# --- per-sheet scale from standing / matching poses (source px heights, measured once, see notes) ---
SC=HS*173/183.   # combo sheet standing hero ~183px vs walk ~173px
S1=SC            # skill sheet 1: lunge poses match the combo sheet to within 1px
S2=SC*183/150.   # skill sheet 2: standing hero ~150px
S3=HS*173/132.   # skill sheet 3 (4 rows): standing hero ~132px

C='hero_combo_sheet.jpg'
hero_strip('cb_slash',C,0,[0,1,2],SC)
hero_strip('cb_thrust',C,1,[0,1,2],SC)
hero_strip('cb_spin',C,2,[0,1,2,3,4],SC)
A='skill_sheet_1.jpg'
hero_strip('sk_quake',A,0,[0,1],S1)
fx_strip('fx_crystal',A,0,[2,3],S1,anchor='bottom')
hero_strip('sk_thread',A,1,[0,1,2,3],S1)
hero_strip('sk_sand',A,2,[0,1,2,3],S1)
B='skill_sheet_2.jpg'
ha=hero_strip('sk_pact',B,0,[0,1],S2,splits={1:(0,517)})
fx_strip('fx_ghost',B,0,[1],S2,xr=(517,9999),hero_anchor=[ha[1]])
ha=hero_strip('sk_water',B,1,[0,1,2,3],S2,splits={1:(0,522)},hairrect={2:(810,330,875,400)})
fx_strip('fx_water',B,1,[1],S2,xr=(522,9999),hero_anchor=[ha[1]])
hero_strip('sk_shield',B,2,[0,1,2,3],S2)
D='skill_sheet_3.jpg'
ha=hero_strip('sk_fire',D,0,[0,1,2,3],S3,splits={2:(0,826)})
fx_strip('fx_fire',D,0,[2],S3,xr=(826,9999),hero_anchor=[ha[2]])
hero_strip('sk_bolt',D,1,[0,1,2,3],S3)
hero_strip('sk_time',D,2,[0,1,2,3],S3,manual={2:(762,)},hairrect={2:(722,365,792,412)})  # ring blue biases tunic detection
hero_strip('sk_dragon',D,3,[0,1,2,3],S3,manual={0:(165,),1:(478,),2:(752,),3:(1070,)},
           hairrect={0:(145,555,210,608),2:(725,555,790,602),3:(1045,555,1110,602)},nohair=(1,))  # golden-armour frame keeps gold
json.dump(meta,open(OUT+'sprites.json','w'),indent=1)
for k,v in meta.items():
    if k.startswith(('cb_','sk_','fx_')): print(k,{a:b for a,b in v.items() if a not in('src','srcAnchor')})

# --- skill icons (48x48, keyed crops of each skill's signature effect) ---
ICONS=[('skill_sheet_1.jpg',(700,40,910,236)),('skill_sheet_1.jpg',(560,290,652,382)),('skill_sheet_1.jpg',(838,515,940,617)),
 ('skill_sheet_2.jpg',(515,60,635,180)),('skill_sheet_2.jpg',(540,290,650,400)),('skill_sheet_2.jpg',(170,500,290,620)),
 ('skill_sheet_3.jpg',(505,25,645,165)),('skill_sheet_3.jpg',(210,205,310,305)),('skill_sheet_3.jpg',(192,346,258,412)),
 ('skill_sheet_3.jpg',(55,512,155,612))]
IS=48; ic=Image.new('RGBA',(IS*len(ICONS),IS),(0,0,0,0))
for i,(fn,(x0,y0,x1,y1)) in enumerate(ICONS):
    rgba=sheet(fn)[0]; c=rgba[y0:y1,x0:x1].copy()
    im=Image.fromarray(c,'RGBA'); im.thumbnail((IS-4,IS-4),Image.LANCZOS); a=np.asarray(im).copy(); a[...,3]=np.where(a[...,3]>110,255,0)
    im=Image.fromarray(a,'RGBA'); ic.paste(im,(i*IS+(IS-im.size[0])//2,(IS-im.size[1])//2),im)
ic.save(OUT+'ui_icons.png'); meta['ui_icons']=dict(src='ui_icons.png',w=IS,h=IS,n=len(ICONS),ax=0,ay=0)
json.dump(meta,open(OUT+'sprites.json','w'),indent=1)
