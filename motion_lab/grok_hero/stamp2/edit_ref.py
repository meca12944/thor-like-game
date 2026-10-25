# 그록 얼굴 그림을 참고(reference)로, 게임 크기 144 걷기 0번 장의 얼굴만 도트로 다시 (edit-images-v2 edit_with_reference, 장당 10)
# usage: edit_ref.py <src.png> <ref.png> <out.png> <tag> "<description>" [seed]
import sys,os,base64
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)));from pl import *
from PIL import Image
src,ref,out,tag,desc=sys.argv[1:6];seed=int(sys.argv[6]) if len(sys.argv)>6 else 7;rw,rh=Image.open(ref).size
body={'method':'edit_with_reference','edit_images':[{'image':b64(src),'width':256,'height':256}],'image_size':{'width':256,'height':256},
      'reference_image':{'image':b64(ref),'width':rw,'height':rh},'description':desc,'no_background':True,'seed':seed}
st,r=req('POST','/edit-images-v2',body);open(f'{RAW}/submit_{tag}.json','w').write(scrub({'http':st,'body':r}))
if st not in (200,202): log('EDIT FAIL',tag,st,scrub(r)[:300]);sys.exit(1)
j=wait(r.get('background_job_id') or r['background_job_ids'][0],tag);ims=(j.get('last_response') or {}).get('images') or []
log('edit_ref',tag,j.get('status'),'usage',j.get('usage'))
if ims: open(out,'wb').write(base64.b64decode(ims[0]['base64'].split(',')[-1]))
