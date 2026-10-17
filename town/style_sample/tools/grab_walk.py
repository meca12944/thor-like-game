# copy newest N generated attachments into src/fem_walk/<char>_<view>.jpg, matching char by colour histogram vs turnaround
import sys, os, numpy as np
from PIL import Image
A='/cursor/stores/store-795156a0-7465-4f60-aac0-5ea8cd38a231/grok-bot/agents/4fedc784-0420-4bf1-b51b-e98cbd24f667/attachments/'
S='/workspace/town-demo/style_sample/src/'
view=sys.argv[1]; n=int(sys.argv[2]); names=sys.argv[3].split(',')
fs=sorted(os.listdir(A), key=lambda f: os.path.getmtime(A+f))[-n:]
def hist(p):
    a=np.asarray(Image.open(p).convert('RGB').resize((256,144))).reshape(-1,3).astype(int)
    m=~((a[:,0]>170)&(a[:,2]>140)&(a[:,1]<110))   # drop magenta
    a=a[m]//32; h=np.bincount(a[:,0]*64+a[:,1]*8+a[:,2], minlength=512).astype(float); return h/h.sum()
ref={c:hist(S+f'fem/{c}_turn.jpg') for c in names}
for f in fs:
    h=hist(A+f); sc={c:np.minimum(h,ref[c]).sum() for c in names}
    best=max(sc,key=sc.get); print(f[:8], best, round(sc[best],3), sorted(sc.values())[-2].__round__(3))
    dst=S+f'fem_walk/{best}_{view}.jpg'
    if os.path.exists(dst): print('  DUP', dst)
    else: os.system(f'cp {A+f} {dst}')
