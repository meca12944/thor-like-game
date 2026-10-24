# 높은 길 시제품 시험 (?height=1). 장면마다 주인공을 그 자리에 두고 시킴:
#  A 땅 → 서쪽 계단 → 높은 길 / B 3칸 틈으로 걸어감 → 떨어짐 → 돌아옴 / C 3칸 틈 앞에서 회피대시 → 넘음 / D 북쪽 갈래 5칸 틈 회피대시 → 떨어짐 / E 동쪽 계단으로 땅에 내려감
#   python3 heighttest.py <주소> <frames 폴더> <log.json>
import os,sys,json
from playwright.sync_api import sync_playwright
URL,FR,LOG=sys.argv[1:4];os.makedirs(FR,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ['PW_CHROME']);pg=b.new_page(viewport={'width':960,'height':540});E=[]
    pg.on('pageerror',lambda e:E.append(str(e)))
    pg.goto(URL);pg.wait_for_function('window.__world&&window.__world.ready&&__world.map&&__world.map.id==="height_test"',timeout=60000);pg.wait_for_timeout(1500)
    pg.evaluate("()=>{__world.setManual(true)}")
    n=0;L=[];R={}
    def st():return pg.evaluate("()=>{const h=__world.mobApi.hero;return {x:+(h.x/16).toFixed(2),y:+(h.y/16).toFixed(2),hl:h.hl||0,fall:!!h.hfall,hp:h.hp,edge:!!h.hiEdge,roll:!!h.roll}}")
    def put(x,y,hl,face):pg.evaluate(f"()=>{{const h=__world.mobApi.hero;h.x={x}*16;h.y={y}*16;h.hl={hl};h.hfall=null;h.hiSafe=null;h.face='{face}';h.hp=h.maxHp;h.inv=0;__world.advance(.3)}}")
    def run(ticks,keys=(),every=2,tag='',dash=False):
        global n
        for k in keys:pg.evaluate("(k)=>__world.key(k,true)",k)
        for i in range(ticks):
            if dash and i==0:pg.evaluate("()=>__world.key('KeyK',true)")
            if dash and i==1:pg.evaluate("()=>__world.key('KeyK',false)")
            pg.evaluate("()=>__world.advance(1/60)")
            if i%every==0:pg.screenshot(path=f'{FR}/{n:04d}.png');n+=1;L.append(dict(tag=tag,**st()))
        for k in keys:pg.evaluate("(k)=>__world.key(k,false)",k)
    put(2.5,12.5,0,'right');run(90,['ArrowRight'],tag='A 땅→계단→높은 길');R['A']=st();run(20,tag='A')
    put(12.5,12.5,1,'right');run(10,tag='B');run(80,['ArrowRight'],tag='B 틈으로 걸어감');run(40,tag='B 떨어짐→돌아옴');R['B']=st()
    put(15.2,12.5,1,'right');run(10,tag='C');run(36,['ArrowRight'],tag='C 회피대시로 3칸 틈 넘기',dash=True);R['C']=st();run(20,tag='C')
    put(27.5,10.7,1,'up');run(10,tag='D');run(50,['ArrowUp'],tag='D 5칸 틈 회피대시 → 떨어짐',dash=True);run(20,tag='D');R['D']=st()
    put(33.5,12.5,1,'right');run(90,['ArrowRight'],tag='E 동쪽 계단 내려감');run(20,tag='E');R['E']=st()
    print(json.dumps(R,ensure_ascii=False),'errs',E[:3])
    json.dump(dict(log=L,res=R,errs=E),open(LOG,'w'),ensure_ascii=False)
    b.close()
