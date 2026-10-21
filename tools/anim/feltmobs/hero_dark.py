# Darker outfit variant of the hero sandbox sheets: every opaque pixel except skin (warm, light), whites/silver (low saturation, bright)
# and the eyes' highlights is pulled down in value and a little in saturation. usage: hero_dark.py <in.webp> <out.webp> [value=0.62] [sat=0.85]
import sys,numpy as np
from PIL import Image
src,out=sys.argv[1:3];V=float(sys.argv[3]) if len(sys.argv)>3 else .62;SA=float(sys.argv[4]) if len(sys.argv)>4 else .85
im=Image.open(src).convert('RGBA');a=np.array(im).astype(float)/255;rgb=a[...,:3]
mx=rgb.max(-1);mn=rgb.min(-1);sat=np.where(mx>0,(mx-mn)/np.maximum(mx,1e-6),0)
hsv=np.array(Image.fromarray((rgb*255).astype('uint8')).convert('HSV')).astype(float);hue=hsv[...,0]*360/255
skin=(hue>=8)&(hue<=40)&(sat>.18)&(sat<.6)&(mx>.62)
metal=(sat<.16)&(mx>.58)
keep=skin|metal|(a[...,3]==0)
lum=rgb.mean(-1,keepdims=True);d=lum+(rgb-lum)*SA;d=d*V
rgb2=np.where(keep[...,None],rgb,d)
o=np.dstack([rgb2,a[...,3:]]);Image.fromarray((np.clip(o,0,1)*255).astype('uint8'),'RGBA').save(out,'WEBP',lossless=True)
print(out,'changed',round(float((~keep).mean()),3))
