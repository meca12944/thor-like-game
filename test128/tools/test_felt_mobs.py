# field00: spawn the 4 chapter-1 Felt mobs around the hero (god mode, hero idle) and record their walk / melee / 4-way shots.
# usage: test_felt_mobs.py [base url] [out dir]  -> frames + felt_ingame.mp4, prints counts of shots / hazards seen and page errors
import sys,json,os,subprocess
from playwright.sync_api import sync_playwright
B=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8931/index.html'; O=sys.argv[2] if len(sys.argv)>2 else '/tmp/felt_test'; os.makedirs(O+'/f',exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ.get('PW_CHROME') or None); pg=b.new_page(viewport={'width':1280,'height':720}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(B); pg.wait_for_function('window.__world&&window.__game',timeout=30000); pg.wait_for_timeout(1500)
    pg.evaluate("()=>{const W=__world;W.setManual(true);W.go('field00');}"); pg.evaluate("()=>__world.advance(2)");pg.evaluate("()=>{for(let i=0;i<20&&__world.trans;i++)__world.advance(.5)}")
    pg.evaluate('''()=>{const W=__world,h=W.hero,M=W.S.map;W.god=true;let best=null;for(let y=6;y<M.h-6;y++)for(let x=8;x<M.w-8;x++){let ok=true;for(let dy=-3;dy<=3&&ok;dy++)for(let dx=-5;dx<=5;dx++)if(M.solidG[(y+dy)*M.w+x+dx]){ok=false;break;}if(ok){best=[x,y];break;}}if(best)W.setHeroTile(best[0],best[1],'down');W.killAll();W.advance(.6);W.S.fx.length=0;
      [['c1_silmamul',-60,-25],['c1_thread_puppet',60,-25],['c1_needle_spider',-60,30],['c1_unrotting_hound',60,30]].forEach(([k,dx,dy])=>{const m=W.spawn(k,h.x+dx,h.y+dy);m.noDrop=true;});}''')
    seen={'shots':set(),'haz':0,'anims':set()}
    for i in range(420):
        r=pg.evaluate('''()=>{const W=__world;W.advance(1/30);return {s:W.S.shots.map(s=>s.kind),h:W.hazards.length,a:W.mobs.map(m=>m.kind+':'+(m.anim||'')),hp:W.mobs.map(m=>m.hp)}}''')
        seen['shots'].update(r['s']);seen['haz']=max(seen['haz'],r['h']);seen['anims'].update(r['a'])
        if i%2==0:pg.screenshot(path=f'{O}/f/{i//2:04d}.png')
    print(json.dumps({'shots':sorted(seen['shots']),'maxHaz':seen['haz'],'anims':sorted(seen['anims']),'errors':errs[:5]},ensure_ascii=False)); b.close()
subprocess.run(['ffmpeg','-loglevel','error','-y','-framerate','15','-i',f'{O}/f/%04d.png','-vf','scale=960:-2','-c:v','libx264','-pix_fmt','yuv420p','-crf','20',f'{O}/felt_ingame.mp4'],check=True)
