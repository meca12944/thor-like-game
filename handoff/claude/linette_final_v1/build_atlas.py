# Pack frames_polished/ into a hero8-style atlas: linette8_<motion>.webp sheets + linette8.json
# json: sheets, cells[sheet][i]=[x,y,w,h,ax,ay] (ax,ay = root (128,189) inside the crop), anims["<motion>_<dir>"]=[[sheet,cell,ticks],...]
import glob,json,os
from PIL import Image
H=os.path.dirname(os.path.abspath(__file__)); IN=H+'/frames_polished'; OUT=H+'/atlas'; os.makedirs(OUT,exist_ok=True)
man=json.load(open(H+'/manifest.json'))['motions']; DIRS=['down','up','right','left','downl','upl']; RX,RY=128,189; MAXW=2048   # downl/upl: attacks only (diagonal art mirrored)
sheets=[];cells=[];anims={}
for si,m in enumerate(man):
    items=[]
    for d in [d for d in DIRS if d in man[m]]:
        for i,f in enumerate(sorted(glob.glob(f'{IN}/{m}/{d}/*.png'))):
            im=Image.open(f).convert('RGBA'); bb=im.getbbox(); items.append((d,i,im.crop(bb),RX-bb[0],RY-bb[1]))
    x=y=rowh=0; pos=[]
    for d,i,c,ax,ay in items:          # simple shelf packing
        if x+c.width>MAXW: x=0;y+=rowh+1;rowh=0
        pos.append((x,y)); x+=c.width+1; rowh=max(rowh,c.height)
    sh=Image.new('RGBA',(MAXW,y+rowh)); cl=[]
    for (d,i,c,ax,ay),(px,py) in zip(items,pos): sh.paste(c,(px,py)); cl.append([px,py,c.width,c.height,ax,ay])
    sh=sh.crop((0,0,max(p[0]+c[2].width for p,c in zip(pos,items)),sh.height))
    name=f'anim/linette8_{m}.webp'; sh.save(f'{OUT}/linette8_{m}.webp',lossless=True); sheets.append(name); cells.append(cl)
    k=0
    for d in [d for d in DIRS if d in man[m]]:
        n=len(man[m][d]['ticks']); anims[f'{m}_{d}']=[[si,k+j,t] for j,t in enumerate(man[m][d]['ticks'])]; k+=n
json.dump({'_doc':'Linette (PixelLab 7e26e0f3, 117px) atlas, hero8-style. anchor = feet root (128,189) of the 256 canvas, 1:1. left = right mirrored. ticks @60fps.',
           'figH':117,'dirs':DIRS,'sheets':sheets,'cells':cells,'anims':anims},open(f'{OUT}/linette8.json','w'),separators=(',',':'))
print('sheets',len(sheets),'anims',len(anims),'bytes',sum(os.path.getsize(f'{OUT}/'+os.path.basename(s)) for s in sheets))
