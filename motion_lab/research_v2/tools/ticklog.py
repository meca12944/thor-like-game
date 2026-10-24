# 공격 틱 표: 허수아비를 앞에 두고 1·2·3타를 1틱(1/60초)씩 넘기며 몸 반동·판정·칼 숨김·멈춤·몹 반응을 적음 + 회피대시 캔슬 시험
#   python3 ticklog.py <주소> <out.json>
import os,sys,json
from playwright.sync_api import sync_playwright
URL,OUT=sys.argv[1],sys.argv[2]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ['PW_CHROME']);pg=b.new_page(viewport={'width':1280,'height':720});E=[]
    pg.on('pageerror',lambda e:E.append(str(e)))
    pg.goto(URL);pg.wait_for_function('window.__world&&window.__world.ready',timeout=60000);pg.wait_for_timeout(1500)
    setup="""(mob)=>{const W=__world;W.setManual(true);W.killAll&&W.killAll();W.hero.x=488;W.hero.y=470;W.hero.atk=null;W.hero.roll=null;W.hero.rollCd=0;W.hero.combo=0;W.hero.comboT=0;W.advance(.3);
      W.key('ArrowRight',true);W.advance(.05);W.key('ArrowRight',false);W.advance(.4);
      if(mob){const m=W.mobApi.spawn('slime',W.hero.x+16,W.hero.y);if(m){m.hp=m.maxHp=99999;m.spawnT=0;m.D=Object.assign({},m.D,{update(){},init:null});m.st='idle';}W.advance(.2);} return !!W.mobApi.mobs.length}"""
    tick="""()=>{const W=__world;W.hero.hp=W.hero.maxHp;W.advance(1/60);const a=W.atkTick(),m=W.mobApi.mobs[0];return {a,roll:!!W.hero.roll,mob:m?{hp:m.hp,flash:+(m.flash||0).toFixed(3),kx:+(m.kx||0).toFixed(2)}:null}}"""
    R={}
    print('mob',pg.evaluate(setup,True))
    rows=[]
    for hit in range(3):
        pg.evaluate("()=>__world.key('KeyJ',true)")
        for k in range(26 if hit<2 else 34):
            if k==1:pg.evaluate("()=>__world.key('KeyJ',false)")
            rows.append(dict(hit=hit,k=k,**pg.evaluate(tick)))
    R['combo']=rows
    # 회피대시 캔슬: 공격 시작 뒤 k틱에 회피 누르면 몇 틱 뒤 회피가 시작되나
    C=[]
    for hit in (0,2):
        for k in range(0,24,2):
            pg.evaluate(setup,True)
            for h in range(hit+1):
                pg.evaluate("()=>{__world.key('KeyJ',true)}");pg.evaluate("()=>__world.advance(1/60)");pg.evaluate("()=>__world.key('KeyJ',false)")
                if h<hit:pg.evaluate("()=>__world.advance(.2)")
            pg.evaluate(f"()=>__world.advance({max(0,k-1)}/60)")
            pre=pg.evaluate("()=>__world.atkTick()")
            pg.evaluate("()=>__world.key('KeyK',true)");lat=None
            for j in range(12):
                pg.evaluate("()=>__world.advance(1/60)")
                if j==0:pg.evaluate("()=>__world.key('KeyK',false)")
                if pg.evaluate("()=>!!__world.hero.roll"):lat=j+1;break
            C.append(dict(hit=hit,k=k,atk_i=pre and pre['i'],atk_tk=pre and round(pre['tk'],1),latency=lat))
    R['cancel']=C;R['errs']=E[:3]
    json.dump(R,open(OUT,'w'),ensure_ascii=False,indent=0);print('errs',E[:3])
    b.close()
