# Visit field00 (Linette companion + area-1 mobs on room-3 strips), field01 and the region fields field02..09 (god mode),
# let the mobs fight the idle hero and record. usage: test_place_all.py [base url] [out dir] -> place_all.mp4 + stats
import sys,json,os,subprocess
from playwright.sync_api import sync_playwright
B=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8931/test128/index.html'; O=sys.argv[2] if len(sys.argv)>2 else '/tmp/place_all'; os.makedirs(O+'/f',exist_ok=True)
MAPS=['field00','field01']+[f'field0{a}' for a in range(2,10)]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ.get('PW_CHROME') or None); pg=b.new_page(viewport={'width':1280,'height':720}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(B); pg.wait_for_function('window.__world&&window.__game',timeout=30000); pg.wait_for_timeout(1500); n=0; stats={}
    for mp in MAPS:
        pg.evaluate("(mp)=>{const W=__world;W.setManual(true);W.go(mp,'world');}",mp); pg.evaluate("()=>{for(let i=0;i<30&&__world.trans;i++)__world.advance(.5)}")
        pg.evaluate('''()=>{const W=__world,M=W.S.map;W.god=true;let bx=Math.floor(M.w/2),by=Math.floor(M.h/2);for(let r=0;r<12&&M.solidG[by*M.w+bx];r++){bx++;}W.setHeroTile(bx,by,'down');const h=W.hero;
          let k=0;for(const m of W.mobs){if(m.dead||m.D.champion)continue;const a=k*2.4;m.x=h.x+Math.cos(a)*(55+k%3*18);m.y=h.y+Math.sin(a)*(40+k%3*12);m.home=[m.x,m.y];const sol=(x,y)=>M.solidG[Math.floor(y/M.T)*M.w+Math.floor(x/M.T)];if(sol(m.x,m.y)){m.x=h.x+(k%2?40:-40);m.y=h.y;}k++;if(k>=7)m.dead=true;}}''')
        pg.wait_for_timeout(800); seen={'shots':set(),'anims':set(),'haz':0}
        for i in range(150):
            r=pg.evaluate('''()=>{const W=__world;W.hero.hp=W.hero.maxHp;W.advance(1/30);return {s:W.S.shots.map(s=>s.kind),h:W.hazards.length,a:W.mobs.filter(m=>!m.dead).map(m=>m.kind+':'+(m.anim||m.st)),pet:W.S.pet?[W.S.pet.atk?W.S.pet.atk.clip:'-',Math.round(W.S.pet.x),Math.round(W.S.pet.y)]:null}}''')
            seen['shots'].update(r['s']);seen['anims'].update(r['a']);seen['haz']=max(seen['haz'],r['h'])
            if r['pet'] and r['pet'][0]!='-':seen['anims'].add('PET:'+r['pet'][0])
            if i%3==0:pg.screenshot(path=f'{O}/f/{n:04d}.png');n+=1
        stats[mp]={'shots':sorted(seen['shots']),'maxHaz':seen['haz'],'anims':len(seen['anims']),'pet':sorted(a for a in seen['anims'] if a.startswith('PET'))}
    print(json.dumps({'stats':stats,'errors':errs[:5]},ensure_ascii=False,indent=0)); b.close()
subprocess.run(['ffmpeg','-loglevel','error','-y','-framerate','15','-i',f'{O}/f/%04d.png','-vf','scale=960:-2','-c:v','libx264','-pix_fmt','yuv420p','-crf','22',f'{O}/place_all.mp4'],check=True)
