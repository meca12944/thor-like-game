"""Item icon atlas builder.
Slices equipment sheets (src/items, 5x2, magenta) + hidden swords (dark bg) + generated consumable/material sheets
(src/icons, 5x4, magenta) into square icons, makes derived variants (corrupted x_*, tiered recipe scrolls) and packs
assets/icons/icons32.png + icons64.png + icons.json (id -> rects, name, kind, rarity, ...).
Run from /workspace/town-demo:  python3 tools/icons.py
"""
import json, re, os, sys, colorsys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_I=ROOT+'/src/items/'; SRC_G=ROOT+'/src/icons/'; OUT=ROOT+'/assets/icons/'
DATA=json.load(open(ROOT+'/data/towns.json'))
sys.path.insert(0,ROOT+'/tools'); from icon_prompts import SHEETS as MAT_SHEETS

def items_md_order():
    """equipment ids in ITEMS.md section order (= order of the 5x2 sheets)."""
    md=open(ROOT+'/src/monsters/ITEMS.md' if os.path.exists(ROOT+'/src/monsters/ITEMS.md') else '/workspace/thor-like-game/ITEMS.md').read()
    secs={};cur=None
    for line in md.split('\n'):
        if line.startswith('## '):cur=line[3:]
        m=re.match(r'\| `([a-z0-9_]+)` \|',line)
        if m and cur:secs.setdefault(cur,[]).append(m.group(1))
    get=lambda pre:next(v for k,v in secs.items() if k.startswith(pre))
    return get('무기'),get('방어구'),get('보조무기')

# ---------------- keying ----------------
def key_magenta(rgb):
    """rgb uint8 HxWx3 -> rgba float [0,1]; bg = border-connected magenta, soft unblended edge."""
    f=rgb.astype(np.float32)
    border=np.concatenate([f[:4].reshape(-1,3),f[-4:].reshape(-1,3),f[:,:4].reshape(-1,3),f[:,-4:].reshape(-1,3)])
    bg=np.median(border,0)
    d=np.sqrt(((f-bg)**2).sum(2))
    # magenta-ish = high R & B, low G (also catches darker/lighter magenta gradients)
    mag=(f[...,1]<70)&(f[...,0]>120)&(f[...,2]>60)&(np.abs(f[...,0]-bg[0])<60)
    hard=(d<55)|mag
    lab,n=ndi.label(hard)
    edge_l=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    sizes=ndi.sum(hard,lab,range(1,n+1))
    keep=[i+1 for i,s in enumerate(sizes) if (i+1) in edge_l or s>4000]
    bgm=np.isin(lab,keep)
    # enclosed holes (ring interiors, sword guards): near-exact background colour, not border-connected
    hole=(d<42)&~bgm
    hl,hn=ndi.label(hole)
    if hn:
        hs=ndi.sum(hole,hl,range(1,hn+1));bgm|=np.isin(hl,[i+1 for i,z in enumerate(hs) if z>=12])
    a=np.ones(d.shape,np.float32);a[bgm]=0
    near=ndi.binary_dilation(bgm,iterations=3)&~bgm
    soft=np.clip((d-55)/90,0,1)
    a[near]=np.minimum(a[near],soft[near])
    # unblend semi-transparent edge pixels from the magenta background (despill)
    aa=np.clip(a,1e-3,1)[...,None]
    un=np.clip((f-(1-aa)*bg)/aa,0,255)
    out=np.where((a>0)&(a<1)[...,None] if False else ((a>0)&(a<1))[...,None],un,f)
    # residual spill: pull magenta tint down on edge pixels
    e=near[...,None]
    spill=np.maximum(0,np.minimum(out[...,0],out[...,2])-out[...,1]-40)[...,None]
    out=np.where(e,out-spill*np.array([.6,0,.6]),out)
    return np.dstack([np.clip(out,0,255)/255,a])

def key_dark(rgb):
    """dark-background art (hidden swords): keep the bright sword body, fade glow/particles, drop the backdrop."""
    f=rgb.astype(np.float32)/255;v=f.max(2)
    bright=v>0.5
    closed=cv2.morphologyEx(bright.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))>0
    lab,n=ndi.label(closed)
    sizes=ndi.sum(closed,lab,range(1,n+1));big=np.argmax(sizes)+1
    keep=[i+1 for i,z in enumerate(sizes) if z>=0.02*sizes[big-1]]
    main=ndi.binary_dilation(np.isin(lab,keep),iterations=2)
    main=cv2.morphologyEx(main.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((25,25),np.uint8))
    main=cv2.morphologyEx(main,cv2.MORPH_CLOSE,np.ones((91,5),np.uint8))  # bridge dark grips between pommel and guard (upright swords)
    main=ndi.binary_fill_holes(main>0)
    soft=np.clip((v-0.30)/0.35,0,1)
    a=np.where(main,np.maximum(soft,0.92),0)
    return np.dstack([f,a.astype(np.float32)])

def rotate_sq(sq,deg):
    """rotate a square rgba (tall upright sword -> diagonal like the other weapon icons) and re-trim."""
    s=sq.shape[0];M=cv2.getRotationMatrix2D((s/2,s/2),deg,1.0)
    pm=sq.copy();pm[...,:3]*=pm[...,3:4]
    r=cv2.warpAffine(pm,M,(s,s),flags=cv2.INTER_CUBIC,borderValue=(0,0,0,0))
    a=np.clip(r[...,3:4],0,1);rgb=np.where(a>1e-4,r[...,:3]/np.maximum(a,1e-4),0);r=np.dstack([np.clip(rgb,0,1),a])
    ys,xs=np.where(r[...,3]>0.1);return to_square(r[ys.min():ys.max()+1,xs.min():xs.max()+1],0.04)

# ---------------- cells -> icons ----------------
def cell_objects(rgba,cols,rows):
    """assign foreground components to grid cells by centroid; return list of rgba crops (row-major)."""
    a=rgba[...,3];H,W=a.shape
    fg=a>0.25
    lab,n=ndi.label(fg,structure=np.ones((3,3)))
    objs=ndi.find_objects(lab);sizes=ndi.sum(fg,lab,range(1,n+1));coms=ndi.center_of_mass(fg,lab,range(1,n+1))
    cells=[[] for _ in range(cols*rows)]
    for i in range(n):
        if sizes[i]<6:continue
        cy,cx=coms[i];c=min(cols-1,int(cx/(W/cols)));r=min(rows-1,int(cy/(H/rows)))
        cells[r*cols+c].append(i)
    res=[]
    for k,ids in enumerate(cells):
        if not ids:res.append(None);continue
        big=max(ids,key=lambda i:sizes[i]);by,bx=objs[big]
        keep=[]
        for i in ids:
            sy,sx=objs[i]
            gap=max(by.start-sy.stop,sy.start-by.stop,bx.start-sx.stop,sx.start-bx.stop,0)
            if i==big or sizes[i]>=0.03*sizes[big] or gap<28:keep.append(i)
        m=np.isin(lab,[i+1 for i in keep])
        m=ndi.binary_dilation(m,iterations=3)
        ys,xs=np.where(m);y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
        crop=rgba[y0:y1,x0:x1].copy();crop[...,3]*=m[y0:y1,x0:x1]
        res.append(crop)
    return res

def to_square(crop,pad=0.06):
    h,w=crop.shape[:2];s=int(max(h,w)*(1+2*pad))+1
    out=np.zeros((s,s,4),np.float32);oy,ox=(s-h)//2,(s-w)//2;out[oy:oy+h,ox:ox+w]=crop;return out

def resize_rgba(sq,size):
    """premultiplied-alpha area/lanczos downscale, then crisp-up: unsharp + alpha hardening."""
    pm=sq.copy();pm[...,:3]*=pm[...,3:4]
    big=cv2.resize(pm,(size*4,size*4),interpolation=cv2.INTER_AREA)
    sm=cv2.resize(big,(size,size),interpolation=cv2.INTER_AREA)
    a=sm[...,3:4];rgb=np.where(a>1e-4,sm[...,:3]/np.maximum(a,1e-4),0)
    blur=cv2.GaussianBlur(rgb,(0,0),0.8);rgb=np.clip(rgb+(rgb-blur)*(0.6 if size<=32 else 0.35),0,1)
    a=np.clip((a-0.12)/0.62,0,1)  # harden edges -> crisp silhouette
    return np.dstack([rgb,a])

def outline(icon,col=(0.05,0.04,0.08),strength=0.85):
    """1px dark outline under the icon (keeps 32px icons readable on any slot colour)."""
    a=icon[...,3];d=cv2.dilate((a>0.35).astype(np.uint8),np.ones((3,3),np.uint8)).astype(np.float32)
    ring=np.clip(d-a,0,1)*strength
    rgb=icon[...,:3]*a[...,None]+np.array(col)*ring[...,None];na=np.clip(a+ring,0,1)
    rgb=np.where(na[...,None]>1e-4,rgb/np.maximum(na[...,None],1e-4),0)
    return np.dstack([rgb,na])

def pil(icon):return Image.fromarray((np.clip(icon,0,1)*255).astype(np.uint8),'RGBA')

# ---------------- variants ----------------
def corrupt(sq):
    """타락(x_) variant: desaturate, map to purple ramp (#7a2ad0 family), dark violet aura."""
    rgb=sq[...,:3];a=sq[...,3]
    l=(rgb*[.3,.59,.11]).sum(2,keepdims=True)
    ramp_lo=np.array([.10,.02,.16]);ramp_mid=np.array([.48,.16,.82]);ramp_hi=np.array([.92,.80,1.0])
    t=np.clip(l*1.15,0,1)
    p=np.where(t<.5,ramp_lo+(ramp_mid-ramp_lo)*(t/.5),ramp_mid+(ramp_hi-ramp_mid)*((t-.5)/.5))
    rgb=rgb*0.25+p*0.75
    au=cv2.GaussianBlur((a>0.3).astype(np.float32),(0,0),sq.shape[0]/40);aura=np.clip(au*1.4-a,0,1)*0.75
    out_rgb=rgb*a[...,None]+np.array([.35,.05,.55])*aura[...,None];na=np.clip(a+aura,0,1)
    out_rgb=np.where(na[...,None]>1e-4,out_rgb/np.maximum(na[...,None],1e-4),0)
    return np.dstack([out_rgb,na])
TIER_SEAL=['#c8302a','#e07a20','#d8b020','#5aa83a','#2a9ad0','#3a5ad8','#8a4ad8','#d04aa0','#e8e8f0','#202028']
def reseal(sq,hexcol):
    """recolour the red wax seal of the scroll-fragment icon to a tier colour."""
    rgb=sq[...,:3].copy();a=sq[...,3]
    hsv=cv2.cvtColor((rgb*255).astype(np.uint8),cv2.COLOR_RGB2HSV).astype(np.float32)
    red=((hsv[...,0]<10)|(hsv[...,0]>165))&(hsv[...,1]>110)&(a>0.3)
    c=np.array([int(hexcol[i:i+2],16)/255 for i in (1,3,5)])
    l=(rgb*[.3,.59,.11]).sum(2,keepdims=True)/0.45
    rgb[red]=np.clip(c*l[red]*1.1,0,1)
    return np.dstack([rgb,a])

# ---------------- main ----------------
def main():
    W,A,O=items_md_order()
    cat=DATA['catalog'];cons=[c['id'] for c in cat['consumables']]
    allitems={}
    for k in ('weapons','armor','offhand'):
        for it in cat[k]:allitems[it['id']]=dict(it,kind=k)
    for it in DATA['hidden_swords']['items']:allitems[it['id']]=dict(it,kind='hidden')
    for c in cat['consumables']:allitems[c['id']]=dict(c,kind='consumable')
    for m in DATA['materials']:allitems[m['id']]=dict(m,kind='material')
    icons={}  # id -> square float rgba (source resolution)
    src={}
    for pre,ids in (('weapons',W),('armor',A),('offhand',O)):
        for s in range(3):
            rgba=key_magenta(np.array(Image.open(SRC_I+f'{pre}_{s+1}.jpg').convert('RGB')))
            crops=cell_objects(rgba,5,2)
            for j,cr in enumerate(crops):
                iid=ids[s*10+j];assert cr is not None,iid;icons[iid]=to_square(cr);src[iid]=f'src/items/{pre}_{s+1}.jpg#{j}'
    hs=np.array(Image.open(SRC_I+'hidden_swords.jpg').convert('RGB'))
    for iid,(x0,y0,x1,y1) in (('hs_tak',(150,0,525,636)),('hs_gyu',(790,8,1050,636))):
        icons[iid]=rotate_sq(to_square(key_dark(hs[y0:y1,x0:x1]),0.0),135);src[iid]='src/items/hidden_swords.jpg'
    ch=np.array(Image.open(SRC_I+'chan_sword.jpg').convert('RGB'))
    icons['hs_chan']=rotate_sq(to_square(key_dark(ch[8:716,440:840]),0.0),-45);src['hs_chan']='src/items/chan_sword.jpg'  # chan art is point-up
    for s in range(3):
        crops=cell_objects(key_magenta(np.array(Image.open(SRC_G+f'cons_{s+1}.jpg').convert('RGB'))),5,4)
        for j,cr in enumerate(crops):
            iid=cons[s*20+j];assert cr is not None,iid;icons[iid]=to_square(cr);src[iid]=f'src/icons/cons_{s+1}.jpg#{j}'
    extra={}
    for sheet,lst in MAT_SHEETS.items():
        crops=cell_objects(key_magenta(np.array(Image.open(SRC_G+sheet+'.jpg').convert('RGB'))),5,4)
        names=[i for i,_ in lst]
        if sheet=='mat_7':names=names+['tk_mago_v2','ui_coins','ui_bag','ui_anvil']
        for j,cr in enumerate(crops):
            if j>=len(names):break
            assert cr is not None,(sheet,j);extra[names[j]]=(to_square(cr),f'src/icons/{sheet}.jpg#{j}')
    extra['tk_mago']=extra.pop('tk_mago_v2')  # mat_6 #8 was a bare hat; the medallion redo lives in mat_7 #17
    variants={}
    for iid,(sq,s) in extra.items():
        if iid in ('scroll_area','scroll_full'):continue
        icons[iid]=sq;src[iid]=s
    mats=[m['id'] for m in DATA['materials']]
    for m in mats:
        if m.startswith('scroll_area'):
            t=int(m[len('scroll_area'):]);icons[m]=reseal(extra['scroll_area'][0],TIER_SEAL[t-1]);src[m]=extra['scroll_area'][1];variants[m]=f'scroll_area + 봉랍 색 {TIER_SEAL[t-1]} (티어 {t})'
        elif m=='scroll_first_bearer':icons[m]=extra['scroll_full'][0];src[m]=extra['scroll_full'][1]
    for m in mats:
        if m.startswith('x_'):
            base=m[2:];icons[m]=corrupt(icons[base]);src[m]=src[base];variants[m]=f'{base} + 타락 보라 틴트·오라'
    need=W+A+O+['hs_tak','hs_gyu','hs_chan']+cons+mats
    miss=[i for i in need if i not in icons];assert not miss,miss
    order=need+['ui_coins','ui_bag','ui_anvil']
    # pack
    os.makedirs(OUT,exist_ok=True);cols=16;rows=(len(order)+cols-1)//cols
    meta={'cols':cols,'count':len(order),'sizes':[32,64],'icons':{}}
    RAR={1:'common',2:'common',3:'uncommon',4:'uncommon',5:'rare',6:'rare',7:'epic',8:'epic',9:'legendary',10:'legendary'}
    for size in (32,64):
        at=Image.new('RGBA',(cols*size,rows*size),(0,0,0,0))
        for k,iid in enumerate(order):
            ic=outline(resize_rgba(icons[iid],size)) if size==32 else outline(resize_rgba(icons[iid],size),strength=.7)
            at.paste(pil(ic),((k%cols)*size,(k//cols)*size))
        at.save(OUT+f'icons{size}.png',optimize=True)
    for k,iid in enumerate(order):
        it=allitems.get(iid,{});tier=it.get('tier')
        rar='unique' if it.get('kind')=='hidden' else (RAR.get(tier,'common') if tier else ('rare' if it.get('kind')=='consumable' and it.get('category') in ('영구',) else 'common'))
        if iid.startswith('x_'):rar='corrupt'
        src_ = (it.get('source') or {}).get('type') if isinstance(it.get('source'),dict) else None
        if it.get('kind') in ('weapons','armor','offhand') and src_ in ('boss','champion','quest','craft_only','dive'):
            rar={'common':'uncommon','uncommon':'rare','rare':'epic'}.get(rar,rar)
        meta['icons'][iid]={'i':k,'r32':[(k%cols)*32,(k//cols)*32,32,32],'r64':[(k%cols)*64,(k//cols)*64,64,64],
            'name':it.get('name',{'ui_coins':'금화','ui_bag':'가방','ui_anvil':'대장간'}.get(iid,iid)),'kind':it.get('kind','ui'),'rarity':rar,'src':src[iid],**({'variant':variants[iid]} if iid in variants else {})}
    json.dump(meta,open(OUT+'icons.json','w'),ensure_ascii=False,separators=(',',':'))
    kinds={}
    for v in meta['icons'].values():kinds[v['kind']]=kinds.get(v['kind'],0)+1
    print('icons',len(order),kinds,'variants',len(variants))
    demo_data(meta)

SELL_RATE=0.5           # shop sell price = 50% of buy price (per item 'sell' in items_demo.json)
SELL_DROP_PER_TIER=60   # sell price for unpriced rare-drop gear, per tier
def demo_data(meta):
    """compact item info for the town demo (injected by build.py as /*ITEMS*/)."""
    md=open(ROOT+'/src/monsters/ITEMS.md').read();stat={};src_txt={}
    for line in md.split('\n'):
        m=re.match(r'\| `([a-z0-9_]+)` \|(.*)',line)
        if not m:continue
        cells=[c.strip() for c in m.group(2).split('|')]
        if len(cells)>=5 and cells[1] in ('체력','게이지','치료','버프','영구','이동','잠수','도구','강화','선악'):stat[m.group(1)]=cells[2]
        elif len(cells)>=5:stat[m.group(1)]=cells[3];src_txt[m.group(1)]=cells[4]
    cat=DATA['catalog'];items={}
    TYPE_KO={'metal':'금속','cloth':'천·깃털','essence':'정수','crystal':'결정','hide':'가죽','core':'핵','shell':'껍데기','bone':'뼈·뿔','token':'징표','wood':'목재','scrap':'잡동사니'}
    for k in ('weapons','armor','offhand'):
        for it in cat[k]:
            slot='helmet' if it['id'].startswith('h_') else {'weapons':'weapon','armor':'armor','offhand':'offhand'}[k]
            items[it['id']]=dict(n=it['name'],s=slot,t=it['tier'],atk=it.get('atk'),df=it.get('defense'),fx=stat.get(it['id'],''),p=it.get('price'),src=src_txt.get(it['id'],''))
    for it in DATA['hidden_swords']['items']:
        items[it['id']]=dict(n=it['name'],s='weapon',t=it['tier'],atk=it.get('atk'),fx='공격 %d · 숨겨진 전설검 (영웅의 길 전용)'%it.get('atk',0),p=None,src=it.get('where',''))
    for c in cat['consumables']:
        items[c['id']]=dict(n=c['name'],s='consumable',cat=c['category'],fx=c['effect'],p=c['price'])
    for m in DATA['materials']:
        items[m['id']]=dict(n=m['name'],s='material',t=m['tier'],cat=TYPE_KO.get(m['type'],m['type']),p=next((x.get('price') for x in m['sources'] if x.get('price')),None),sell=m.get('sell'),
            src=' · '.join(x.get('where','') for x in m['sources'][:2]))
    for i,v in items.items():
        v['ic']=meta['icons'][i]['i'];v['r']=meta['icons'][i]['rarity']
        # sell price (shop 판매 tab only): SELL_RATE x buy price; materials keep their own MATERIALS.md price;
        # unpriced rare-drop gear = SELL_DROP_PER_TIER x tier; hidden swords / price-0 key items can't be sold (sell 0)
        if v['s']!='material' or v.get('sell') is None:
            v['sell']=0 if i.startswith('hs_') else int((v.get('p') or 0)*SELL_RATE) if v.get('p') is not None else SELL_DROP_PER_TIER*(v.get('t') or 1)
        for k in [k for k,x in v.items() if x in (None,'')]:del v[k]
    shopA=[x['id'] for k in ('weapons','armor','offhand') for x in cat[k] if x['source'].get('type')=='shop' and x['source'].get('where')=='A']
    shopA+=[c['id'] for c in cat['consumables'] if any(s['town']=='A' for s in c.get('shops',[]))]
    shopA+=[m['id'] for m in DATA['materials'] if any(x.get('kind')=='forge_shop' for x in m['sources']) and m['tier']<=2]
    recA=[dict(id=r['id'],item=r['item'],mats=[[x['mat'],x['count']] for x in r['materials']],c=r['coins'],ok=r['success']) for r in DATA['recipes'] if r['town']=='A']
    enh=[dict(l=x['level'],ok=x['success'],c=x['coins'],pct=x['atk_pct'],mt=x['tier'],n=x['count']) for x in DATA['enhancement']['levels']]
    enh_t={t['tier']:t['name'] for t in DATA['enhancement']['tiers']}
    ui={k:meta['icons'][k]['i'] for k in ('ui_coins','ui_bag','ui_anvil')}
    out=dict(cols=meta['cols'],items=items,shopA=shopA,recA=recA,enh=enh,enhT=enh_t,ui=ui)
    json.dump(out,open(OUT+'items_demo.json','w'),ensure_ascii=False,separators=(',',':'))
    print('demo items',len(items),'shopA',len(shopA),'recipesA',len(recA))

if __name__=='__main__':main()
