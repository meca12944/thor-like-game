# Key pose by one PixelLab edit (edit-images-v2 edit_with_text, Pro, ~10). usage: edit_pose.py <src.png> <out.png> <tag> "<description>" [seed]
import sys,os,base64; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from pl import *
src,out,tag,desc=sys.argv[1:5]; seed=int(sys.argv[5]) if len(sys.argv)>5 else 5
body={'method':'edit_with_text','edit_images':[{'image':b64(src),'width':256,'height':256}],'image_size':{'width':256,'height':256},'description':desc,'seed':seed,'no_background':True}
st,r=req('POST','/edit-images-v2',body); open(f'{RAW}/submit_edit_{tag}.json','w').write(scrub({'http':st,'body':r}))
if st not in (200,202): log('EDIT FAIL',tag,st,scrub(r)[:300]); sys.exit(1)
j=wait(r.get('background_job_id') or r['background_job_ids'][0],f'edit_{tag}'); ims=(j.get('last_response') or {}).get('images') or []
log('edit',tag,j.get('status'),'usage',j.get('usage'))
if ims: open(out,'wb').write(base64.b64decode(ims[0]['base64'].split(',')[-1]))
