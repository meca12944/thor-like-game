# atk2 key pose fix: the atk2 state came out with the same (right) arm thrusting. Edit each atk1 full-lunge frame so the LEFT arm thrusts.
# edit-images-v2 edit_with_text (Pro). usage: edit_left.py <dir...>   -> keypose_atk2_left/<dir>.png
import sys,os,json,base64; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from pl import *
DESC=("Same character, same outfit, same colors, same size, same legs and same lunge stance. Change ONLY the arms: now the LEFT arm (the arm on the far side of the body) "
      "is fully extended straight forward at chest height and its needle points straight ahead like a rapier; the RIGHT arm (the near arm) is pulled back "
      "beside the hip with its needle pointing backward. No effects.")
for d in sys.argv[1:]:
    src=f'{C}/atk1/{d}/008.png'
    body={'method':'edit_with_text','edit_images':[{'image':b64(src),'width':256,'height':256}],'image_size':{'width':256,'height':256},'description':DESC,'seed':5,'no_background':True}
    st,r=req('POST','/edit-images-v2',body); open(f'{RAW}/submit_edit_atk2_{d}.json','w').write(scrub({'http':st,'body':r}))
    if st not in (200,202): log('EDIT FAIL',d,st,scrub(r)[:300]); continue
    jid=r.get('background_job_id') or (r.get('background_job_ids') or [None])[0]; j=wait(jid,f'edit_atk2_{d}'); lr=j.get('last_response') or {}
    log('edit atk2 left',d,j.get('status'),'usage',j.get('usage'),'keys',list(lr.keys()))
    os.makedirs(f'{C}/keypose_atk2_left',exist_ok=True); ims=lr.get('images') or []
    if ims:
        im=ims[0]; b=im.get('base64') if isinstance(im,dict) else None
        if b: open(f'{C}/keypose_atk2_left/{d}.png','wb').write(base64.b64decode(b.split(',')[-1]))
        else: dl(im if isinstance(im,str) else im.get('url'),f'{C}/keypose_atk2_left/{d}.png')
