# face skin tone match: skin pixels near the nose take frame 0's skin ramp by brightness rank (fixes the darker/orange faces on hit1 4-6)
import json,os,colorsys,numpy as np
from PIL import Image
P='/tmp/claude-0/-home-user-thor-like-game/605da03e-2542-5329-b23f-a50876f99780/scratchpad/'
def nose(clip,i):
    kf=P+f'jit/{clip}/{i:02d}_kp.json' if os.path.exists(P+f'jit/{clip}/{i:02d}_kp.json') else P+f'all/{clip.split("_")[0]}_right/k{i}_kpfix.json'
    K={k['label']:(k['x']*256,k['y']*256) for k in json.load(open(kf))['keypoints']};return K['NOSE']
def skinmask(a,c,r=13):
    h,w=a.shape[:2];yy,xx=np.mgrid[:h,:w];near=(xx-c[0])**2+(yy-c[1])**2<r*r
    rgb=a[...,:3].astype(float)/255;mx=rgb.max(-1);mn=rgb.min(-1);sat=(mx-mn)/(mx+1e-6)
    R,G,B=rgb[...,0],rgb[...,1],rgb[...,2]
    return near&(a[...,3]>0)&(R>G)&(G>B)&(mx>0.45)&(sat>0.12)&(sat<0.62)&((R-G)>0.06)
def ramp(img,c):
    a=np.array(img.convert('RGBA'));m=skinmask(a,c);px=a[m][:,:3].astype(float)
    return px[np.argsort(px.sum(1))]
def match(img,c,ref):
    a=np.array(img.convert('RGBA'));m=skinmask(a,c)
    if m.sum()==0 or len(ref)==0: return img
    px=a[m][:,:3].astype(float);order=np.argsort(np.argsort(px.sum(1)));q=(order/(max(1,len(px)-1))*(len(ref)-1)).round().astype(int)
    a[m,:3]=ref[q].astype(np.uint8);return Image.fromarray(a)
LIGHT,MID,SHADE=(239,204,161),(240,192,134),(226,162,92)  # hit1 frame 0 skin ramp
def fix_face(img,clip,i,r=12):
    import json
    kf=P+f'jit/{clip}/{i:02d}_kp.json' if os.path.exists(P+f'jit/{clip}/{i:02d}_kp.json') else P+f'all/{clip.split("_")[0]}_right/k{i}_kpfix.json'
    K={k['label']:(k['x']*256,k['y']*256) for k in json.load(open(kf))['keypoints']}
    c=K['NOSE'];ny=K['NECK'][1]-3
    a=np.array(img.convert('RGBA'));h,w=a.shape[:2];yy,xx=np.mgrid[:h,:w]
    rgb=a[...,:3].astype(int);R,G,B=rgb[...,0],rgb[...,1],rgb[...,2];mx=rgb.max(-1);mn=rgb.min(-1)
    warm=(a[...,3]>0)&(R>140)&(R>G+25)&(G>B+15)&((mx-mn)/(mx+1e-6)>0.4)
    m=warm&((xx-c[0])**2+(yy-c[1])**2<r*r)&(yy<ny)
    s=rgb.sum(-1);a[m&(s>=560),:3]=LIGHT;a[m&(s>=430)&(s<560),:3]=MID;a[m&(s<430),:3]=SHADE
    return Image.fromarray(a),int(m.sum())
