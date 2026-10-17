# Headless capture: hero walk / combo / weapon-type GIFs + FPS check. python3 tools/anim/capture_gifs.py
import asyncio, io, json
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
U='http://localhost:18931/index.html?nosave=1'; D='/workspace/town-demo/'
F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',18)
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':720}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e)))
    await pg.goto(U)
    for i in range(100):
      if await pg.evaluate('!!(window.__game&&window.__game.ready)'): break
      await pg.wait_for_timeout(100)
    # --- FPS (real rAF loop, fixed 60 Hz sim) ---
    await pg.evaluate("()=>{__game.setShowFps(true);document.getElementById('hint').style.display='none'}")
    await pg.wait_for_timeout(3000); fps=[]
    for i in range(6): fps.append(round(await pg.evaluate('()=>__game.fps'),2)); await pg.wait_for_timeout(500)
    await pg.screenshot(path=D+'shot_fps.png')
    await pg.evaluate("""()=>{const g=__game;g.setManual(true);g.setShowFps(false);g.slimes.forEach(m=>{m.dead=true;m.respawn=1e9});const h=g.hero;h.x=420;h.y=560;h.face='right';h.hz='right';h.vx=h.vy=0;}""")
    async def grab(cx,cy,w=420,h=260,label=None):
      png=await pg.screenshot(clip={'x':cx-w/2,'y':cy-h/2,'width':w,'height':h})
      im=Image.open(io.BytesIO(png)).convert('RGB')
      if label: d=ImageDraw.Draw(im); d.text((8,6),label,font=F,fill='white',stroke_width=2,stroke_fill='black')
      return im
    async def run(js_each,n,step=2,center=None,label=None):
      out=[]
      for i in range(n):
        await pg.evaluate(js_each,i)
        await pg.evaluate(f"()=>{{for(let k=0;k<{step};k++)__game.advance(1/60);__game.render()}}")
        hx,hy=await pg.evaluate("()=>[__game.hero.x,__game.hero.y]")
        c=center or (hx,hy-40)
        out.append(await grab(c[0],c[1],label=label(i) if callable(label) else label))
      return out
    # --- walk: right, down, left, up, then release (skid -> idle) ---
    seq=[('right',24),('down',18),('left',24),('up',18),(None,22)]
    frames=[]
    for k,n in seq:
      js="(i)=>{const K=__game.keys;K.right=K.left=K.up=K.down=false;"+(f"K.{k}=true;" if k else "")+"}"
      frames+=await run(js,n,label='walk 8f/dir · 60Hz' if k else 'skid → idle (breathing)')
    frames[0].save(D+'anim_hero_walk.gif',save_all=True,append_images=frames[1:],duration=33,loop=0)
    # --- combo vs slimes ---
    await pg.evaluate("""()=>{const g=__game;const h=g.hero;h.x=520;h.y=480;h.face='right';h.hz='right';
      g.slimes.forEach((m,i)=>{if(m.kind==='boar'){m.dead=true;m.respawn=1e9;return;}m.dead=false;m.x=[585,600,560][i];m.y=[480,505,455][i];m.hp=99;m.maxHp=99;m.hpLag=99;m.t=99;m.state='idle';m.spawnT=0;m.hz=0;m.kx=m.ky=0;});}""")
    press=lambda i: "(i)=>{if(i===0||i===8||i===17)__game.press();}"
    frames=await run("(i)=>{if(i===0||i===8||i===17)__game.press();}",44,center=(560,440),label='한손검 3연타: 횡베기 → 되베기 → 내려베기 (모두 휘두르기 · 정면 전용)')
    frames[0].save(D+'anim_hero_combo.gif',save_all=True,append_images=frames[1:],duration=33,loop=0)
    frames[22].save(D+'shot_combo_new.png')
    # --- weapon types: every combo is forward-only (slime behind the hero must never be hit) ---
    allf=[];hitlog={}
    WT=[('sword','w_bronze_long','한손검'),('saber','w_desert_crescent','곡도'),('greatsword','w_anchor_great','대검'),('dagger','w_forest_dagger','단검'),('spear','w_storm_spear','창'),
        ('whip','w_kraken_whip','채찍검'),('twin','w_shadow_twin','쌍검'),('hidden','hs_tak','숨겨진 전설검'),('chan','hs_chan','찬검'),('demon','demon_end','마왕 종언')]
    for typ,wid,lab in WT:
      await pg.evaluate("""(w)=>{const g=__game;g.INV.equip.weapon={id:w,plus:0};const h=g.hero;h.atk=null;h.combo=0;h.chainT=0;h.cool=0;h.x=520;h.y=480;h.face='right';h.hz='right';g.syncWeapon();
        g.slimes.forEach((m,i)=>{if(m.kind==='boar'){m.dead=true;m.respawn=1e9;return;}m.dead=false;m.x=[585,610,488][i];m.y=[478,500,484][i];m.hp=999;m.maxHp=999;m.hpLag=999;m.t=99;m.state='idle';m.spawnT=0;m.hz=0;m.kx=m.ky=0;m.respawn=1e9;});}""",wid)
      info=await pg.evaluate("()=>[__game.weaponType,__game.SWINGS.slice(0,3).map(s=>[s.name,s.kind,Math.round(s.dur*60)])]")
      tot=[x[2] for x in info[1]]
      t1,t2=tot[0]-3,tot[0]+tot[1]-6; n=(sum(tot)+20)//2
      js="(i)=>{const g=__game;g.slimes.forEach(m=>{m.x+=0;});const t=i*2;if(t===0||(t>=%d&&t<%d)||(t>=%d&&t<%d))g.press();}"%(t1,t1+2,t2,t2+2)
      names=' → '.join(x[0] for x in info[1])
      fr=await run(js,n,center=(540,440),label=f'{lab}: {names}  {tot} ticks')
      hp=await pg.evaluate("()=>__game.slimes.filter(m=>m.kind!=='boar').map(m=>999-m.hp)")
      hitlog[typ]={'type':info[0],'combo':info[1],'dmg_front':hp[:2],'dmg_behind':hp[2]}
      fr[0].save(D+f'anim_combo_{typ}.gif',save_all=True,append_images=fr[1:],duration=33,loop=0)
      allf+=fr
    allf[0].save(D+'anim_weapon_types.gif',save_all=True,append_images=allf[1:],duration=33,loop=0)
    # --- 마왕 title: hit 3 = 360 spin + 8 sword waves ---
    await pg.evaluate("""()=>{const g=__game;g.setTitle('마왕');g.INV.equip.weapon={id:'w_bronze_long',plus:0};const h=g.hero;h.atk=null;h.combo=0;h.chainT=0;h.cool=0;h.x=560;h.y=470;h.face='right';h.hz='right';g.syncWeapon();
      const P=[[630,470],[480,480],[560,400],[760,560],[360,380]];let i=0;g.slimes.forEach(m=>{const p=P[i++];m.dead=false;m.x=p[0];m.y=p[1];m.hp=999;m.maxHp=999;m.hpLag=999;m.t=99;m.state='idle';m.spawnT=0;m.kx=m.ky=0;m.respawn=1e9;});}""")
    tot=await pg.evaluate("()=>__game.SWINGS.slice(0,3).map(s=>Math.round(s.dur*60))")
    names=await pg.evaluate("()=>__game.SWINGS.slice(0,3).map(s=>s.name).join(' → ')")
    t1,t2=tot[0]-3,tot[0]+tot[1]-6; n=(sum(tot)+40)//2
    js="(i)=>{const t=i*2;if(t===0||(t>=%d&&t<%d)||(t>=%d&&t<%d))__game.press();}"%(t1,t1+2,t2,t2+2)
    async def grabw(i):
      png=await pg.screenshot(clip={'x':200,'y':170,'width':720,'height':480});im=Image.open(io.BytesIO(png)).convert('RGB').resize((540,360),Image.LANCZOS)
      d=ImageDraw.Draw(im);d.text((8,6),'칭호 마왕: '+names+' (360° + 검기 8발)',font=F,fill='#ffb0b0',stroke_width=2,stroke_fill='black');return im
    fr=[]
    for i in range(n):
      await pg.evaluate(js,i);await pg.evaluate("()=>{for(let k=0;k<2;k++)__game.advance(1/60);__game.render()}");fr.append(await grabw(i))
    hp=await pg.evaluate("()=>__game.slimes.map(m=>[m.kind,999-m.hp])")
    hitlog['maou']={'combo':names,'ticks':tot,'dmg':hp}
    q=[f.quantize(colors=128,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE) for f in fr]
    q[0].save(D+'anim_combo_maou.gif',save_all=True,append_images=q[1:],duration=33,loop=0,optimize=True)
    await pg.evaluate("()=>__game.setTitle('필멸자')")
    print(json.dumps(hitlog,ensure_ascii=False))
    print(json.dumps({'fps':fps,'errs':errs,'weaponFrames':len(allf)}))
    await b.close()
asyncio.run(main())
