# 몹 점검 (monster textbook 0부 10): one command measures every felt mob against the attack / movement standard and saves a table image.
#   python3 test128/tools/mob_check.py [base_url=http://127.0.0.1:8931] [out.png] [kind,kind,...]
#   works for any mob kind (felt, s47 strips, area-1 mobs). Owner 10-23: run it on EVERY new or changed mob and report the table image.
#   per mob, in the canonical 잿빛 들판 (field_felt -> ch1, open spot 28,17; the old field01 now aliases into 바람길 where Linette kills the test mob) with the hero standing still (no damage):
#     1 mob, 60 s : attacks (a chain that restarts within 0.35 s = one combo), longest run of the same attack, seconds standing still after attacks (the opening)
#     3 mobs, 20 s: % of walking time facing away from the hero, % of time two of them overlap
import asyncio, json, sys, subprocess
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8931'
OUT = sys.argv[2] if len(sys.argv) > 2 else '/tmp/mob_check.png'
KINDS = (sys.argv[3].split(',') if len(sys.argv) > 3 else ['c1_silmamul', 'c1_thread_puppet', 'c1_needle_spider', 'c1_unrotting_hound'])
SETUP = "()=>{const W=__world;W.setManual(true);(W.map.objects||[]).forEach(o=>{if(o.type==='spawn')o.respawn=1e9});}"
ONE = """(K)=>{const W=__world,h=W.hero;{const q=window.__worldHooks.aliasPt?__worldHooks.aliasPt({map:'field_felt',x:28,y:17}):{x:28,y:17};W.setHeroTile(q.x,q.y);}W.killAll(m=>!m.D.boss);W.S.mobs.length=0;W.S.hazards.length=0;W.S.shots.length=0;const m=W.spawn(K,h.x+60,h.y);
  const seq=[];let prev='',still=0,endT=-9,endS='';const X=['idle','rest','hop','walk','stagger','stun','dormant','rise','aim','intro','phase'];for(let i=0;i<3600;i++){h.hp=999;h.inv=0;W.S.dialog=null;W.advance(1/60);let s=m.st;if(s==='shoot')s+=m.pi;if(s==='atk')s+=':'+(m.last||m.D.ai||'');if(s!==prev){if(!X.includes(prev)){endT=i/60;endS=prev;}if(!X.includes(s)&&!(s===endS&&i/60-endT<.35))seq.push(s);prev=s;}
   if(m.st==='rest'||(m.st==='lunge'&&m.sub==='rec'))still+=1/60;}
  let run=1,best=1;for(let i=1;i<seq.length;i++){run=seq[i]===seq[i-1]?run+1:1;best=Math.max(best,run);}return {name:m.D.name,attacks:seq.length,longestRepeat:best,openSec:+still.toFixed(1)}}"""
PACK = """(K)=>{const W=__world,h=W.hero;{const q=window.__worldHooks.aliasPt?__worldHooks.aliasPt({map:'field_felt',x:28,y:17}):{x:28,y:17};W.setHeroTile(q.x,q.y);}W.killAll(m=>!m.D.boss);W.S.mobs.length=0;W.S.hazards.length=0;W.S.shots.length=0;
  const ms=[0,1,2].map(i=>W.spawn(K,h.x+70*Math.cos(i*2.1),h.y+70*Math.sin(i*2.1)));let away=0,mv=0,ov=0,n=0;
  for(let i=0;i<1200;i++){h.hp=999;h.inv=0;W.S.dialog=null;W.advance(1/60);n++;
   for(const m of ms){if(m.dead)continue;if(m.moving&&m.st==='idle'){mv++;if((h.x-m.x)*m.face<0)away++;}}
   for(let a=0;a<3;a++)for(let c=a+1;c<3;c++)if(Math.hypot(ms[a].x-ms[c].x,ms[a].y-ms[c].y)<ms[a].r+ms[c].r)ov++;}
  return {facingAwayPct:Math.round(away/Math.max(1,mv)*100),overlapPct:Math.round(ov/n/3*100)}}"""
async def main():
    rows = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium'); pg = await b.new_page(viewport={'width': 960, 'height': 540}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(BASE + '/index.html?nosave=1&go=field_felt'); await pg.wait_for_function('window.__world&&__world.ready&&__world.scene&&__world.scene!="town"&&__world.map', timeout=90000); await pg.wait_for_timeout(2500)
        await pg.evaluate(SETUP)
        for k in KINDS:
            r = await pg.evaluate(ONE, k); r.update(await pg.evaluate(PACK, k)); r['kind'] = k; rows.append(r); print(json.dumps(r, ensure_ascii=False))
        await b.close()
    if errs: print('page errors', errs[:3])
    # table image (standard: longest repeat <= 2, openings > 0, facing away ~0%, overlap < 10%)
    f = subprocess.run(['fc-match', '-f', '%{file}', ':lang=ko'], capture_output=True, text=True).stdout; F = ImageFont.truetype(f, 20); H = ImageFont.truetype(f, 17)
    cols = [('몹', 'name', 200), ('공격/60초', 'attacks', 110), ('같은 공격 연속', 'longestRepeat', 150), ('서 있는 빈틈(초)', 'openSec', 160), ('등 돌림', 'facingAwayPct', 100), ('겹침', 'overlapPct', 90)]
    ok = {'longestRepeat': lambda v: v <= 2, 'openSec': lambda v: v > 2, 'facingAwayPct': lambda v: v <= 5, 'overlapPct': lambda v: v < 10}
    W = 20 + sum(c[2] for c in cols); im = Image.new('RGB', (W, 60 + 40 * len(rows) + 30), '#1b1f2a'); d = ImageDraw.Draw(im); x = 20
    for t, _, w in cols: d.text((x, 18), t, font=H, fill='#aab'); x += w
    for i, r in enumerate(rows):
        x = 20; y = 56 + i * 40
        for t, k, w in cols:
            v = r[k]; good = ok.get(k, lambda v: True)(v); d.text((x, y), f'{v}{"%" if k.endswith("Pct") else ""}', font=F, fill='#fff' if k == 'name' else ('#9fe8a0' if good else '#ff8a7a')); x += w
    d.text((20, 60 + 40 * len(rows)), '초록 = 기준 통과 (연속 2번 이하 · 빈틈 2초 이상 · 등 돌림 5% 이하 · 겹침 10% 미만)', font=H, fill='#889')
    im.save(OUT); print('saved', OUT)
asyncio.run(main())
