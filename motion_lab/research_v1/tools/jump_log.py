import os,json,sys
from playwright.sync_api import sync_playwright
page=sys.argv[1];out=sys.argv[2];keys=sys.argv[3] if len(sys.argv)>3 else ''
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ['PW_CHROME']);pg=b.new_page(viewport={'width':1280,'height':720});errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://127.0.0.1:8931/'+page);pg.wait_for_timeout(4000)
    pg.evaluate("""()=>{window.__L=[];const g=window.__game;const f=()=>{const h=g.hero;const c=g.heroCell8&&g.heroCell8();window.__L.push({t:performance.now(),z:h.z||0,j:!!h.jump,c:c?c.c:null,h8:c?c.h8:null,fl:c?!!c.fl:false,x:h.x,y:h.y,face:h.face});requestAnimationFrame(f)};requestAnimationFrame(f)}""")
    if keys:pg.keyboard.down(keys);pg.wait_for_timeout(500)
    pg.keyboard.press('Space');pg.wait_for_timeout(1300)
    if keys:pg.keyboard.up(keys)
    L=pg.evaluate("()=>window.__L");json.dump(L,open(out,'w'));print(page,'frames',len(L),'errors',errs[:3])
    b.close()
