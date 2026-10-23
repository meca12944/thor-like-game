# Semi-open world (owner 10-23): seamless 바람길 -> 시작의 숲, area card + first-visit auto-save, F5 save (refused in combat),
# champion thorn ring, death -> retry from just before the fight / last waystone, old 'field01' links, resume after a reload.
# usage: test_openworld.py [base url] [out dir]   (PW_CHROME = chromium path)
import sys, json, os
from playwright.sync_api import sync_playwright
B = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8931/index.html'; O = sys.argv[2] if len(sys.argv) > 2 else '/tmp/ow_test'; os.makedirs(O, exist_ok=True)
res = {}; ok = True
def check(name, cond, info=None):
    global ok
    res[name] = 'ok' if cond else ('FAIL ' + json.dumps(info, ensure_ascii=False)); ok = ok and bool(cond)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('PW_CHROME') or None); pg = b.new_page(viewport={'width': 1280, 'height': 720}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(B + '?worldreset&nosave'); pg.wait_for_function('window.__world&&window.__game&&__world.ready', timeout=30000); pg.wait_for_timeout(1200)
    ev = pg.evaluate; adv = lambda s: ev(f'()=>__world.advance({s})')
    def settle():  # the map load is async (fetch): advance in separate evaluates so the promise can resolve
        for _ in range(80):
            if ev('()=>{__world.advance(.1);return !__world.trans&&__world.scene!=="town"}'): break
    ev("()=>{localStorage.removeItem('thor.world.v1');__world.reset();__world.setManual(true);__world.go('field00','town')}"); settle(); adv(.5)
    m = ev('()=>({id:__world.map.id,w:__world.map.w,h:__world.map.h,areas:(__world.map.areas||[]).map(a=>a.name)})')
    check('stitched map', m['w'] == 120 and len(m['areas']) == 2, m)
    # walk east across the old seam: no transition, area card, auto-save
    ev("()=>{__world.killAll(m=>!m.D.champion);__world.setHeroTile(52,19,'right');__world.S.area='a1_windroad'}"); ev("()=>__world.key('ArrowRight',true)")
    seen = ev("()=>{let tr=false;for(let i=0;i<120;i++){__world.advance(1/60);if(__world.trans)tr=true;}__world.key('ArrowRight',false);return {tr,x:__world.tile()[0],card:__world.S.areaCard&&__world.S.areaCard.a.name,map:__world.map.id,resume:__world.SAVE.resume}}")
    pg.screenshot(path=O + '/1_seam.png')
    check('seamless walk', not seen['tr'] and seen['x'] >= 57 and seen['map'] == 'field00', seen)
    check('area card', seen['card'] == '시작의 숲', seen)
    check('first-visit autosave', bool(seen['resume']) and seen['resume']['map'] == 'field00', seen)
    # F5: refused next to a mob, accepted when calm
    ev("()=>{__world.SAVE.resume=null;const h=__world.hero;__world.spawn('slime',h.x+30,h.y)}"); adv(1); ev("()=>__world.tap('F5')"); adv(.05)
    r1 = ev("()=>({resume:__world.SAVE.resume,msg:__world.S.msg&&__world.S.msg.text})"); pg.screenshot(path=O + '/2_save_refused.png')
    check('F5 refused in combat', not r1['resume'] and r1['msg'] and '저장할 수 없다' in r1['msg'], r1)
    for _ in range(3): ev("()=>__world.killAll(m=>!m.D.champion)"); adv(.6)  # slimes split on death
    adv(1); ev("()=>__world.tap('F5')"); adv(.05)
    r2 = ev("()=>({resume:__world.SAVE.resume,msg:__world.S.msg&&__world.S.msg.text,near:__world.mobs.filter(m=>!m.dead&&Math.hypot(m.x-__world.hero.x,m.y-__world.hero.y)<140).map(m=>m.kind+':'+m.spawnT)})"); pg.screenshot(path=O + '/3_saved.png')
    check('F5 saves when calm', bool(r2['resume']), r2)
    # waystone (신전 앞 비석 at 98,9): register = respawn point
    ev("()=>{__world.setHeroTile(98,10,'up')}"); ev("()=>__world.tap('KeyL')"); adv(.05)
    r3 = ev("()=>__world.SAVE.lastWay"); ev("()=>__world.tap('KeyL')"); adv(.05)
    check('waystone = respawn point', r3 and r3['id'] == 'ws_temple', r3)
    # champion ring: walk up to 돌엄니 (49+56, 26)
    ev("()=>{__world.killAll(m=>!m.D.champion);const c=__world.mobs.find(m=>m.kind==='champ_boar');__world.hero.x=c.x-70;__world.hero.y=c.y;__world.hero.hp=__world.hero.maxHp}"); adv(.1)
    lk = ev("()=>!!__world.S.lock"); ev("()=>__world.key('ArrowLeft',true)"); adv(2.5); ev("()=>__world.key('ArrowLeft',false)")
    d = ev("()=>{const L=__world.S.lock,h=__world.hero;return L?Math.hypot(h.x-L.x,(h.y-L.y)/.75):-1}"); pg.screenshot(path=O + '/4_ring.png')
    check('champion ring holds the hero', lk and 0 < d <= 150, {'lock': lk, 'd': d})
    # death -> retry from just before the fight
    ev("()=>{__world.hero.inv=0;__world.hurt(999)}"); adv(2); pg.screenshot(path=O + '/5_dead.png')
    dm = ev("()=>({dead:__world.S.deadT>0,snap:__world.S.snap})"); ev("()=>__world.tap('KeyJ')"); adv(.05); settle(); adv(.2)
    rt = ev("()=>({map:__world.map.id,t:__world.tile(),hp:__world.hero.hp,max:__world.hero.maxHp,lock:!!__world.S.lock,dead:__world.S.deadT})"); pg.screenshot(path=O + '/6_retry.png')
    check('retry before the fight', dm['dead'] and dm['snap'] and rt['map'] == 'field00' and abs(rt['t'][0] - dm['snap']['x']) < 2 and rt['hp'] >= rt['max'] / 2 and not rt['dead'], {'dm': dm, 'rt': rt})
    # death -> T = last waystone
    ev("()=>{__world.hero.inv=0;__world.hurt(999)}"); adv(2); ev("()=>__world.tap('KeyT')"); adv(.05); settle(); adv(.2)
    wt = ev("()=>({t:__world.tile(),hp:__world.hero.hp,max:__world.hero.maxHp})"); pg.screenshot(path=O + '/7_waystone.png')
    check('T = last waystone', abs(wt['t'][0] - 98) <= 1 and abs(wt['t'][1] - 10) <= 2 and wt['hp'] == wt['max'], wt)
    # old field01 links (dungeon / boss exits)
    ev("()=>__world.go('dungeon01_b1','default')"); settle(); ev("()=>__world.go('field01','dungeon')"); settle(); adv(.2)
    al = ev("()=>({map:__world.map.id,t:__world.tile()})")
    check('field01 alias', al['map'] == 'field00' and abs(al['t'][0] - 102) <= 1, al)
    # temple: B1 + B2 are one map now, the slope corridor replaces the stairs (no fade)
    ev("()=>__world.go('dungeon01_b1','default')"); settle(); adv(.2)
    ev("()=>{__world.killAll();__world.setHeroTile(35,3,'right');__world.S.area='t1_b1'}"); ev("()=>__world.key('ArrowRight',true)")
    tp = ev("()=>{let tr=false,card=null;for(let i=0;i<260;i++){__world.advance(1/60);if(__world.trans)tr=true;if(__world.S.areaCard)card=__world.S.areaCard.a.name;}__world.key('ArrowRight',false);return {tr,x:__world.tile()[0],w:__world.map.w,card,ws:__world.objs.some(o=>o.type==='waystone'&&o.id==='ws_temple_b2')}}")
    pg.screenshot(path=O + '/9_temple_slope.png')
    check('temple one map, slope walk', tp['w'] == 92 and not tp['tr'] and tp['x'] >= 50 and tp['card'] and '아래층' in tp['card'] and tp['ws'], tp)
    ev("()=>__world.go('dungeon01_b2','boss')"); settle(); adv(.2)
    b2 = ev("()=>({map:__world.map.id,t:__world.tile()})")
    check('dungeon01_b2 alias (boss room exit)', b2['map'] == 'dungeon01_b1' and abs(b2['t'][0] - 84) <= 1, b2)
    # resume after a reload: last save = here
    ev("()=>{__world.killAll();__world.tap('F5')}"); adv(.1); sv = ev("()=>__world.SAVE.resume")
    pg.goto(B); pg.wait_for_function('window.__world&&__world.ready&&__world.scene!=="town"&&!__world.trans', timeout=30000); pg.wait_for_timeout(600)
    rs = ev("()=>({scene:__world.scene,map:__world.map&&__world.map.id,t:__world.tile()})"); pg.screenshot(path=O + '/8_resume.png')
    check('resume after reload', rs['map'] == sv['map'] and abs(rs['t'][0] - sv['x']) < 2, {'saved': sv, 'got': rs})
    check('no page errors', not errs, errs[:5])
    b.close()
print(json.dumps(res, ensure_ascii=False, indent=1)); sys.exit(0 if ok else 1)
