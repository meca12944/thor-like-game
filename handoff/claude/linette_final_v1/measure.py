import glob,json,numpy as np
from PIL import Image
def body(f):
    a=np.asarray(Image.open(f))[...,3]>40
    rows=np.nonzero(a.sum(1)>=4)[0]            # ignore thin needle tips
    top,bot=rows.min(),rows.max(); r=a[bot-6:bot+1]; xs=np.nonzero(r.any(0))[0]
    return top,bot,(xs.min()+xs.max())/2
if __name__=='__main__':
    man=json.load(open('manifest.json'))['motions']
    for d in ['down','up','right']:
        for m in man:
            t,b,c=body(sorted(glob.glob(f'frames/{m}/{d}/*.png'))[0]); print(d,m,'top',t,'bot',b,'h',b-t+1,'feetx',c)
