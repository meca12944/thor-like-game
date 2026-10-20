# Owner 10-20 "가만히 서있는 얼굴에 코가 없다, 얼굴 윤곽이 없음": pixel touch-up of the side idle face (PixelLab 0).
# Edits are defined on idle/right/000 (nose bump below the eye, darker front-of-face outline) and follow each frame's head
# (best shift of the head crop vs frame 0); idle/left gets the mirrored result. Run after polish.py, before build_atlas.py.
import glob,os,numpy as np
from PIL import Image,ImageOps
H=os.path.dirname(os.path.abspath(__file__));P=H+'/frames_polished/idle'
fs=sorted(glob.glob(P+'/right/*.png'));A=[np.array(Image.open(f).convert('RGBA')).astype(int) for f in fs]
BOX=(128,84,148,106)   # x0,y0,x1,y1 head crop on frame 0
ref=A[0][BOX[1]:BOX[3],BOX[0]:BOX[2]]
OUT=tuple(A[0][93,140][:3]);SKIN=tuple(A[0][96,138][:3]);LIP=(214,120,120);SHD=tuple(A[0][98,135][:3])   # outline / cheek / lip / skin shade
T=None   # transparent
# new profile (frame-0 coords): bridge 94, nose tip 95 (1px out), under-nose 96, lips 97, chin 98-99, jaw 100 back to the neck
EDITS=[((140,94),SKIN),((141,94),OUT),((140,95),SKIN),((141,95),SKIN),((142,95),OUT),((140,96),SKIN),((141,96),OUT),
       ((139,97),SKIN),((140,97),LIP),((141,97),T),((139,98),SKIN),((140,98),OUT),((141,98),T),((138,99),SKIN),((139,99),OUT),((140,99),T),
       ((136,100),OUT),((137,100),OUT),((138,100),OUT),((139,100),T),((138,96),SHD),
       # eye (owner "눈도 보이게"): lash line 91-92, eye white + dark iris + highlight 93, light-purple lower iris 94
       ((137,91),(63,31,59)),((138,91),(63,31,59)),((139,91),(63,31,59)),((137,92),(63,31,59)),((138,92),(70,24,62)),((139,92),(96,44,104)),((140,92),(63,31,59)),
       ((137,93),(238,222,224)),((138,93),(78,30,84)),((139,93),(255,255,255)),((138,94),(150,92,168)),((139,94),(214,170,186))]
for f,a in zip(fs,A):
    best=None
    for dy in range(-5,6):
        for dx in range(-5,6):
            c=a[BOX[1]+dy:BOX[3]+dy,BOX[0]+dx:BOX[2]+dx];e=np.abs(c-ref).sum()
            if best is None or e<best[0]:best=(e,dx,dy)
    _,dx,dy=best
    for (x,y),col in EDITS:a[y+dy,x+dx]=[0,0,0,0] if col is None else [*col,255]
    im=Image.fromarray(a.astype('uint8'));im.save(f)
    ImageOps.mirror(im).save(f.replace('/right/','/left/'))
    print(os.path.basename(f),'shift',dx,dy)
