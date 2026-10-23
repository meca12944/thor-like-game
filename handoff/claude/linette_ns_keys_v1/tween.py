# In-betweens between two key poses with PixelLab animate-with-text-v3 (first_frame + last_frame). usage: tween.py <first.png> <last.png> <outdir> <frames> "<action>" [seed]
# owner 10-21 "2번 해라, 인간의 자연스러운 움직임": key poses by edit-images-v2, in-betweens here, assembled into the cycle by cycle_ns.py
import sys,os,base64
sys.path.insert(0,os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'linette_thrust_v1'));from pl import *
a,b,out,n,act=sys.argv[1:6];seed=int(sys.argv[6]) if len(sys.argv)>6 else 7
body={'first_frame':b64(a),'last_frame':b64(b),'action':act,'frame_count':int(n),'seed':seed,'no_background':True}
st,r=req('POST','/animate-with-text-v3',body)
if st not in (200,202):print('SUBMIT FAIL',st,scrub(r)[:400]);sys.exit(1)
j=wait(r.get('background_job_id') or r['background_job_ids'][0],'tween_'+os.path.basename(out))
ims=(j.get('last_response') or {}).get('images') or [];os.makedirs(out,exist_ok=True)
for i,im in enumerate(ims):
    if isinstance(im,dict) and im.get('base64'):open(f'{out}/{i:03d}.png','wb').write(base64.b64decode(im['base64'].split(',')[-1]))
    elif isinstance(im,dict) and im.get('url'):dl(im['url'],f'{out}/{i:03d}.png')
    elif isinstance(im,str):dl(im,f'{out}/{i:03d}.png')
log('tween',out,j.get('status'),'frames',len(ims),'usage',j.get('usage'))
