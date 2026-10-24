# make sword-less copies of the hero sheets (research mock-up): blade = bright grey pixels + their thin grey/dark outline, grown 1px;
# pixels inside the body silhouette are refilled from the nearest body pixel, pixels sticking out become transparent
import sys,os,numpy as np
from PIL import Image
from scipy import ndimage as nd
src,dst=sys.argv[1],sys.argv[2]
for f in sorted(os.listdir(src)):
    if not f.startswith('hero8_') or not f.endswith('.webp'): continue
    a=np.asarray(Image.open(os.path.join(src,f)).convert('RGBA')).astype(np.int32); rgb=a[...,:3]; op=a[...,3]>40
    mx=rgb.max(-1); mn=rgb.min(-1); sat=mx-mn
    bright=op&(mn>140)&(sat<40)
    # keep only thin elongated bright groups (blade), drop small round highlights (eyes etc.)
    lab,n=nd.label(bright,structure=np.ones((3,3)))
    keep=np.zeros_like(bright)
    for i,sl in enumerate(nd.find_objects(lab),1):
        h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start; cnt=(lab[sl]==i).sum()
        if max(h,w)>=10 and cnt<=(h+w)*4: keep[sl]|=(lab[sl]==i)
    grey=op&(sat<45)&(mx<200)  # blade outline/shadow greys next to the bright core
    near=nd.binary_dilation(keep,iterations=2)
    blade=nd.binary_dilation(keep|(grey&near),iterations=1)&op
    body=op&~blade; bodyc=nd.binary_closing(body,structure=np.ones((5,5)),iterations=2)
    out=a.copy()
    idx=nd.distance_transform_edt(~body,return_distances=False,return_indices=True)
    fill=blade&bodyc
    out[fill]=a[idx[0][fill],idx[1][fill]]
    out[blade&~bodyc,3]=0
    Image.fromarray(out.astype(np.uint8),'RGBA').save(os.path.join(dst,f),lossless=True)
    print(f, int(blade.sum()))
