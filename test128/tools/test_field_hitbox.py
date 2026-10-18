# field00: hero basic-attack hitbox uses H8HB (x29/96), ?hitbox=1 overlay draws
import sys,json
from playwright.sync_api import sync_playwright
B=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8931/index.html'; O='/workspace/review/test128_field'
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1280,'height':720}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(B+'?hitbox=1'); pg.wait_for_function('window.__world&&window.__game',timeout=30000); pg.wait_for_timeout(1500)
    pg.evaluate("()=>{const W=__world;W.setManual(true);W.go('field00');}"); pg.evaluate("()=>__world.advance(2)");pg.evaluate("()=>{for(let i=0;i<20&&__world.trans;i++)__world.advance(.5)}")
    res={'scene':pg.evaluate("__world.scene"),'dbg':pg.evaluate("__game.HBDBG")}
    for f in ['right','down','up','left']:
        res[f]=pg.evaluate(f"()=>{{const W=__world;W.hero.face='{f}';return [0,1,2].map(i=>Math.round(W.hbR(i)*10)/10).concat([0,1,2].map(i=>W.hbA(i)))}}")
    res['hit']=pg.evaluate('''()=>{const W=__world,h=W.hero,out={};h.face='right';const m=W.mobs.find(m=>!m.dead);if(!m)return 'nomob';
      for(const d of [40,46,52,60]){m.x=h.x+d;m.y=h.y+((m.D.h||20)*(m.scale||1))*.3-4;m.hp=999;h.atk={t:0,hit:new Set(),i:0};let hit=false;for(let k=0;k<20&&h.atk;k++){m.x=h.x+d;W.advance(1/60);hit=hit||h.atk&&h.atk.hit.has(m);}out[d]=hit;h.atk=null;}
      h.atk={t:0,hit:new Set(),i:0};W.advance(.1);return {r:m.r,out}}'''); pg.screenshot(path=O+'/field_hitbox.png')
    pg.evaluate("()=>{__game.HBDBG=false}"); res['dbg_off']=pg.evaluate("__game.HBDBG")
    res['errors']=errs; print(json.dumps(res)); b.close()
