#!/usr/bin/env python3
"""dash_v2 finalize: pick per-direction source, keep largest body component (strip stray FX/smoke specks),
snap sole to y=189 on 256 canvas, write final/<dir>/NNN.png, scale report, 4-dir GIF with afterimages, frames sheet."""
import sys,os,json; import numpy as np; from PIL import Image, ImageDraw; from scipy import ndimage as nd
A='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018/dash_v2'; sys.path.insert(0,A); import afterimage as AI
SRC=json.loads(sys.argv[1]); DIRS=['south','north','east','west']; FEET_Y=189
REF=json.load(open(A+'/../cast_death_guard_v2/SCALE_REF.json'))['directions']
F=sys.argv[2] if len(sys.argv)>2 else A+'/final'; os.makedirs(F,exist_ok=True); rep={'sources':SRC,'feet_root':[128,FEET_Y],'frames':{}}
def head_w(a,top):
    rows=[]
    for y in range(top+8,top+12):
        xs=np.nonzero(a[y]>0)[0]; c=int(np.median(xs)); 
        # contiguous run through the column centre of the topmost 6 rows
        tc=int(np.median(np.nonzero(a[top:top+6].any(0))[0])); l=r=tc
        while l>0 and a[y,l-1]>0: l-=1
        while r<255 and a[y,r+1]>0: r+=1
        rows.append(r-l+1)
    return int(np.median(rows))
out={}
for d in DIRS:
    os.makedirs(f'{F}/{d}',exist_ok=True); [os.remove(f'{F}/{d}/{x}') for x in os.listdir(f'{F}/{d}')]
    fr=[]; rep['frames'][d]=[]
    base=np.array(Image.open(f'{A}/../v1_1x_descA/{d}.png').convert('RGBA'))
    bt=np.nonzero(base[...,3].any(1))[0][0]; bhw=head_w(base[...,3],bt)
    for i in range(8):
        im=np.array(Image.open(f'{A}/{SRC[d]}/{d}/{i:03d}.png').convert('RGBA'))
        m=im[...,3]>0; lab,n=nd.label(m,structure=np.ones((3,3)))
        if n>1:
            sz=nd.sum(m,lab,range(1,n+1)); keep=lab==(1+int(np.argmax(sz))); im[~keep]=0
        im[...,3]=np.where(im[...,3]>0,255,0)
        ys=np.nonzero(im[...,3].any(1))[0]; dy=FEET_Y-ys[-1]
        im=np.roll(im,dy,axis=0)
        if dy>0: im[:dy]=0
        elif dy<0: im[dy:]=0
        a=im[...,3]; ys=np.nonzero(a.any(1))[0]; h=int(ys[-1]-ys[0]+1); hw=head_w(a,ys[0])
        Image.fromarray(im).save(f'{F}/{d}/{i:03d}.png'); fr.append(Image.fromarray(im))
        rep['frames'][d].append({'i':i,'dy':int(dy),'bbox_h':h,'bbox_h_ratio':round(h/REF[d]['total_h'],3),'head_w':hw,'head_w_ratio':round(hw/bhw,3)})
    out[d]=fr
json.dump(rep,open(F+'/report.json','w'),indent=1)
# sheet: base + 8 frames per dir, 2x crop
C=(40,40,216,216); cw=(C[2]-C[0])*2; S=Image.new('RGBA',(cw*9,cw*4+0),(58,62,72,255)); dr=ImageDraw.Draw(S)
for r,d in enumerate(DIRS):
    b=Image.open(f'{A}/../v1_1x_descA/{d}.png').convert('RGBA')
    for j,im in enumerate([b]+out[d]):
        S.alpha_composite(im.crop(C).resize((cw,cw),0),(j*cw,r*cw))
        dr.text((j*cw+4,r*cw+4),('base ' if j==0 else f'{j-1:03d} ')+d,fill=(230,230,230,255))
    dr.line([(0,r*cw+(FEET_Y-C[1])*2),(S.width,r*cw+(FEET_Y-C[1])*2)],fill=(255,80,80,120))
S.save(F+'/dash_v2_frames_sheet.png')
# gif: 2x2 grid, each cell a 400x400 stage, ghosts per spec
spec=AI.load_spec(); cell=400; frames=[]
org={'south':(72,20),'north':(72,124),'east':(20,72),'west':(124,72)}
comp={d:AI.compose(out[d],d,(cell,cell),org[d],spec) for d in DIRS}
for t in range(8):
    g=Image.new('RGBA',(cell*2,cell*2),(46,52,60,255))
    for k,d in enumerate(DIRS):
        g.alpha_composite(comp[d][t],((k%2)*cell,(k//2)*cell)); ImageDraw.Draw(g).text(((k%2)*cell+6,(k//2)*cell+6),d,fill=(220,220,220,255))
    frames.append(g.convert('RGB'))
dur=[spec['frame_ms']]*7+[spec['frame_ms']+spec['loop_pause_ms']]
frames[0].save(F+'/dash_v2_4dir.gif',save_all=True,append_images=frames[1:],duration=dur,loop=0,disposal=1)
open(F+'/README.txt','w').write(f"hero dash_v2 (glide) final frames. sources: {SRC}. 8 frames/dir, 256 canvas, sole snapped to y={FEET_Y}, x as generated (root ~128).\n"
 "Clean body only: no baked FX; game draws afterimages per ../afterimage_spec.json. dash_v2_4dir.gif = preview with spec ghosts. report.json = per-frame offsets/scale.\n")
print(json.dumps({d:[(f['bbox_h_ratio'],f['head_w_ratio'],f['dy']) for f in rep['frames'][d]] for d in DIRS}))
