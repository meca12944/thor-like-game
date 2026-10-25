# 들판 30초 봇 (몬스터 교본 1-8): 가까운 몹에 달려 붙어 베기, 경고 끝 직전 회피대시, 스태미나 30 밑이면 물러나 70까지 기다림, 몹 150px 안에선 질주 안 함. usage: field30_bot.py <base> <pace:""|souls> [secs] [runs] [x,y]
import asyncio, sys, json
from playwright.async_api import async_playwright
BASE = sys.argv[1]; PACE = sys.argv[2]; SECS = float(sys.argv[3]) if len(sys.argv) > 3 else 30; RUNS = int(sys.argv[4]) if len(sys.argv) > 4 else 3
AT = [int(v) for v in sys.argv[5].split(',')] if len(sys.argv) > 5 else None  # 시작 칸 (지도가 바뀌면 몹 무리 가운데로)
BOT = """(dt)=>{const W=__world,S=W.S,h=W.hero;const st=window.__bot||(window.__bot={keys:{},t:0,hits:0,hp:h.hp,kills:0,dead:new Set(),chase:0,swing:0,dodge:0,press:0,atks:0,lastAtk:null,dmg:0,mhp:new Map(),ex:0});st.t+=dt; if(h.atk&&h.atk!==st.lastAtk){st.atks++;} st.lastAtk=h.atk; if(h.stEx)st.ex+=dt; for(const m of S.mobs){const p=st.mhp.get(m);if(p!==undefined&&m.hp<p)st.dmg+=p-m.hp;st.mhp.set(m,m.hp);}
 const set=(c,v)=>{if(!!st.keys[c]!==v){W.key(c,v);st.keys[c]=v;}};
 if(h.hp<st.hp-.01)st.hits++; if(h.hp<20)h.hp=h.maxHp; st.hp=h.hp;
 for(const m of S.mobs) if(m.dead&&!st.dead.has(m)){st.dead.add(m);st.kills++;}
 const inside=z=>{if(z.shape==='circle')return Math.hypot(h.x-z.x,(h.y-z.y)*1.15)<z.r+7;if(z.shape==='line'){const vx=z.x2-z.x,vy=z.y2-z.y,L=Math.hypot(vx,vy)||1,u=((h.x-z.x)*vx+(h.y-z.y)*vy)/(L*L);if(u<0||u>1)return false;return Math.hypot(z.x+vx*u-h.x,z.y+vy*u-h.y)<z.width/2+7;}if(z.shape==='ring'){const d=Math.hypot(h.x-z.x,h.y-z.y);return d<z.r+6&&d>(z.r0||0)-6;}return false;};
 const danger=S.hazards.find(z=>z.dmg&&!z.hit&&inside(z)&&z.warn-z.t<.12&&z.warn-z.t>0);
 let tg=null,bd=400;for(const m of S.mobs){if(m.dead||m.spawnT>0||m.noBar)continue;const d=Math.hypot(m.x-h.x,m.y-h.y);if(d<bd){bd=d;tg=m;}}
 let mx=0,my=0,atk=false;
 const stam=h.st==null?100:h.st; if(stam>=70)st.wait=false; if(stam<30)st.wait=true;
 if(danger&&!h.roll&&stam>=18){set('ShiftLeft',true);st.dodge++;} else set('ShiftLeft',false);
 if(tg){const dx=tg.x-h.x,dy=tg.y-h.y,d=Math.hypot(dx,dy);if(st.wait){if(d<70){mx=-dx/d;my=-dy/d;}else{const a=Math.atan2(dy,dx)+1.57;mx=Math.cos(a)*.5;my=Math.sin(a)*.5;}}else if(d>26){mx=dx/d;my=dy/d;st.chase+=dt;if(d>150)h.runReq=true;}else{atk=true;st.swing+=dt;}}
 set('ArrowRight',mx>.35);set('ArrowLeft',mx<-.35);set('ArrowDown',my>.35);set('ArrowUp',my<-.35);
 st.press=!st.press&&atk; set('KeyJ',st.press);
 return {atks:st.atks,dmg:Math.round(st.dmg),exhausted:+st.ex.toFixed(1),kills:st.kills,hits:st.hits,chase:+st.chase.toFixed(1),swing:+st.swing.toFixed(1),dodge:st.dodge,alive:S.mobs.filter(m=>!m.dead).length};}"""
async def one(pg):
    url = f'{BASE}/index.html?nosave&worldreset&noscene&go=field_felt&at=28,17' + ('&pace=' + PACE if PACE else '')
    await pg.goto(url); await pg.wait_for_function('window.__world&&__world.ready&&__world.map&&__world.S.mobs.length>0', timeout=90000); await pg.wait_for_timeout(500)
    await pg.evaluate("t=>{__world.setManual(true);window.__bot=null;if(t)__world.setHeroTile(t[0],t[1]);}", AT)
    r = None
    for i in range(int(SECS * 30)): r = await pg.evaluate("dt=>{const r=(" + BOT + ")(dt);__world.S.dialog=null;__world.advance(dt);return r}", 1 / 30)
    return r
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium'); pg = await b.new_page(viewport={'width': 960, 'height': 540}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        out = [await one(pg) for _ in range(RUNS)]
        print(PACE or 'base', json.dumps(out, ensure_ascii=False)); print('errs', errs[:2]); await b.close()
asyncio.run(main())
