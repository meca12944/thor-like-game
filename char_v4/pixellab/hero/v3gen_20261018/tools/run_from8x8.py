#!/usr/bin/env python3
"""from8x8_v1 (owner 2026-10-19 13:04 KST): every motion of the old 8x8 design sheet for v3 hero fb140a07, 4 dirs. Preview only.
usage: run_from8x8.py <tag> motion:dir[:seed] ... -> from8x8_v1/_cand/<tag>/<motion>/<dir>_s<seed>/ (seed in path). Budget cap 400 from from8x8_v1/_raw/job_*.json. Key from env only; never printed."""
import os, sys, json, time, glob, threading, urllib.request, urllib.error
O='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; C=O+'/from8x8_v1'; RAW=C+'/_raw'
API='https://api.pixellab.ai/v2'; KEY=os.environ['PIXELLAB_API_KEY']; CID='fb140a07-3f50-40a1-9a11-ca71de7b3c49'
CAP=400; FC=int(os.environ.get('FC','8'))
def scrub(o): return json.dumps(o,indent=1,ensure_ascii=False).replace(KEY,'<REDACTED>')
def req(m,p,b=None):
    r=urllib.request.Request(API+p,data=json.dumps(b).encode() if b is not None else None,method=m,
        headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
    for a in range(25):
        try:
            with urllib.request.urlopen(r,timeout=120) as f: return f.status,json.loads(f.read() or b'{}')
        except urllib.error.HTTPError as e:
            b2=e.read()
            if e.code in (429,500,502,503,504) and a<24: time.sleep(30); continue
            try: return e.code,json.loads(b2)
            except Exception: return e.code,{'raw':b2.decode(errors='replace')[:2000]}
        except Exception as e:
            if a<6: time.sleep(5); continue
            return 0,{'err':str(e)}
def spent():
    s=0
    for f in glob.glob(RAW+'/job_*.json'):
        try: s+=(json.load(open(f)).get('usage') or {}).get('generations') or 0
        except Exception: pass
    return s
COMMON=(" Same character in every frame: long straight black hair, dark coat with gold trim, cape with red lining, gold pauldron, same face, same proportions and same size as the idle image; "
 "longsword in the right hand. Feet stay on the same ground line (animation in place). Bold outline, clean pixels.")
HIT={'idle':("Calm breathing idle stance: sword held low at the right side, blade angled down and forward toward the ground; chest and shoulders rise and fall slightly, "
             "cape and hair sway gently; feet planted. Seamless loop."),
 'walk':("Relaxed walk cycle in place: the sword is held low in the right hand angled down and forward, the blade pointing at the ground ahead; legs alternate in even strides, "
         "the free arm swings a little, a slight up-down bob, the cape sways and trails behind. Seamless loop."),
 'run':("Fast run cycle in place: the body leans forward, long strides with a flight phase where both feet leave the ground, the sword held low and forward in the right hand pointing down-ahead, "
        "the free arm pumps, the cape streams out behind and flares wide, hair flowing back. Seamless loop."),
 'atk1':("Sword attack 1: from the ready stance, quickly raise the sword high above and behind the head, then a big diagonal downward slash from high over the top to low in front, "
         "a wide cyan-white crescent slash trail following the blade tip, cape flaring; follow-through with the sword low in front, then return to the ready stance."),
 'atk2':("Sword attack 2: thrust the sword out low in front, then whip it in a fast wide circular rising slash around the front of the body, a big round cyan-white crescent trail, "
         "ending with the sword raised high and the cape thrown up; then return to the ready stance."),
 'atk3':("Sword attack 3, the finisher: raise the sword high above the head with both hands, then drop into a deep low lunge with a huge, very wide, flat sweeping slash low across the ground in front, "
         "a giant flat cyan-white crescent trail, cape flaring out; hold the low lunge, then rise back to the ready stance."),
 'dash':("Quick dash burst: crouch very low and lean far forward, sword held low pointing forward-down, the cape spread out flat and wide behind like wings; hold the low dash pose, then stand back up into the ready stance."),
 'hurt':("Getting hit: a white impact flash on the chest, the body is knocked back and recoils, head snaps back, the cape flies up, he staggers, then recovers to the ready stance with the sword low."),
 'cast':("Casting a spell: raise the free left hand forward; a glowing cyan magic rune circle appears in front of the hand and a purple magic circle glows on the ground under the feet; energy charges, "
         "then a bright cyan bolt bursts forward from the hand; then lower the hand and return to the ready stance with the sword low.")}
FACE={'south':" Front view facing the camera the whole time; attacks and movement go toward the camera.",
 'east':(" STRICT SIDE VIEW every frame: facing RIGHT in profile, face in profile looking right, chest never turns toward the camera; everything moves toward the RIGHT."),
 'west':(" STRICT SIDE VIEW every frame: facing LEFT in profile, face in profile looking left, chest never turns toward the camera; everything moves toward the LEFT."),
 'north':(" BACK VIEW every frame, facing away from the camera, face never shown, we see the back of the head, hair and cape; "
          "the sword and arms stay visible beside or above the body; movement and attacks go away from the camera (up the screen).")}
FCN={}   # 256px canvas: v3 max 8 frames
usage=[]; T0=time.time(); lock=threading.Lock()
def log(*a):
    s=f'[{time.strftime("%H:%M:%S")}] '+' '.join(map(str,a)); print(s,flush=True); open(C+'/run.log','a').write(s+'\n')
def gen(tag,h,d,seed):
    name=f'f8_{tag}_{h}_{d}_s{seed}'
    desc=HIT[h]+FACE[d]+COMMON
    if os.environ.get('VCLEAVE') and h=='atk3' and d in ('south','north'):
        desc=("Sword attack 3, the finisher, seen "+("from the front" if d=='south' else "from behind")+": raise the sword straight up high above the head with both hands, the blade pointing at the sky, "
              "then a powerful straight VERTICAL overhead cleave straight down in front of him, dropping into a low wide crouch with the cape spreading out flat to both sides; "
              "a thin vertical cyan-white light streak along the path of the blade and a small cyan ring on the ground where it lands; hold the crouch, then rise back to the ready stance.")+FACE[d]+COMMON
    if os.environ.get('A1SIDE') and h=='atk1':
        desc=("Sword attack 1 in side view: from the ready stance, lift the sword up high above the head (blade pointing back over the shoulder), then STEP FORWARD into a wide lunge to the right "
              "and slash down in a big forward arc in front of him, a wide cyan-white crescent trail in front of the body, cape flying out behind; follow-through with the blade extended forward-low, "
              "then step back to the ready stance.")+FACE[d]+COMMON
    if os.environ.get('CASTALT') and h=='cast': desc=desc.replace('a purple magic circle glows on the ground under the feet','a thin magic ring glows on the ground around the feet')
    if os.environ.get('FIX'):
        desc+=" The character's own body and colors never turn white or glow; only effects are bright."
        if h=='hurt' and d=='north': desc+=" He NEVER turns around: back view in every frame (no face, no chest), recoiling while still facing away from the camera."
        if os.environ.get('FIX')=='2': desc+=" IMPORTANT: he stays exactly the same person in every frame: black hair (never blue), dark coat (never light or blue), red-lined cape; he never changes into a different character."
        if h=='atk3' and d=='north': desc+=" He NEVER turns around: back view in every frame (no face, no chest), the slash sweeps in front of him up the screen."
        if h=='hurt': desc+=" The impact flash is small, white, on the body."
        if h=='run': desc+=" Big energetic running strides, knees high, clearly faster than walking."

    body={'character_id':CID,'mode':'v3','action_description':desc,'frame_count':FCN.get(h,FC),'directions':[d],
          'animation_name':name,'keep_first_frame':False,'seed':seed}
    st,r=req('POST','/characters/animations',body)
    open(f'{RAW}/submit_{name}.json','w').write(scrub({'request':body,'http_status':st,'body':r}))
    if st!=200: log('SUBMIT FAIL',name,st,scrub(r)[:300]); return
    j=r['background_job_ids'][0]; log('submitted',name)
    while True:
        time.sleep(10); st,r=req('GET',f'/background-jobs/{j}')
        if r.get('status') in ('completed','failed'): break
    open(f'{RAW}/job_{name}.json','w').write(scrub(r))
    if r['status']!='completed': log('JOB FAIL',name,scrub(r)[:300]); return
    out=f'{C}/_cand/{tag}/{h}/{d}_s{seed}'; os.makedirs(out,exist_ok=True)
    for i,u in enumerate(r['last_response']['storage_urls']['frames']):
        open(f'{out}/{i:03d}.png','wb').write(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=120).read())
    log('done',name,r.get('usage'))
tag=sys.argv[1]; jobs=[]
for a in sys.argv[2:]:
    p=a.split(':'); jobs.append((p[0],p[1],int(p[2]) if len(p)>2 else 8100))
s0=spent(); need=sum(FCN.get(j[0],FC) for j in jobs)
log(f'tag={tag} jobs={len(jobs)} est={need} spent_so_far={s0} cap={CAP}')
if s0+need>CAP: log('BUDGET STOP'); sys.exit(2)
ts=[threading.Thread(target=gen,args=(tag,)+jd) for jd in jobs]
for t in ts: t.start(); time.sleep(1.5)
for t in ts: t.join()
log('spent total from job records:',spent())
