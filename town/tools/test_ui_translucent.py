# Headless test: semi-transparent windows (--ui-alpha), 창 투명도 option, F5 persistence. Writes the two screenshots.
import asyncio, json
from playwright.async_api import async_playwright
U='http://localhost:18931/index.html'; D='/workspace/town-demo/'
R={}; FAIL=[]
def ok(n,c,i=None):
  R[n]=bool(c) if i is None else [bool(c),i]
  if not c: FAIL.append(n)
async def ready(pg):
  for i in range(100):
    if await pg.evaluate('!!(window.__game&&window.__game.ready)'): return
    await pg.wait_for_timeout(100)
BG="(sel)=>getComputedStyle(document.querySelector(sel)).backgroundColor"
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':720}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
    await pg.goto(U); await ready(pg); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await ready(pg)
    ev=pg.evaluate
    await ev("()=>{const g=__game;document.getElementById('hint').style.display='none';const h=g.hero;h.x=600;h.y=560;h.face='right';}")
    await pg.wait_for_timeout(600)
    ok('default_alpha',await ev("()=>__game.uiAlpha===0.65&&getComputedStyle(document.documentElement).getPropertyValue('--ui-alpha').trim()==='0.65'"))
    # dialogue box with portrait
    await pg.keyboard.press('l'); await pg.wait_for_timeout(300)
    bg=await ev(BG,'#dlg'); ok('dialog_translucent','rgba' in bg and '0.65' in bg,bg)
    ok('portrait_opaque',await ev("()=>{const i=document.querySelector('#dlg .dp');if(!i)return 'noportrait';const c=getComputedStyle(i);return c.opacity==='1'&&c.backgroundColor==='rgb(11, 11, 20)'}"))
    await pg.keyboard.press('l'); await pg.wait_for_timeout(400)   # second line = spirit speaking
    await pg.screenshot(path=D+'shot_ui_translucent_dialogue.png')
    await pg.keyboard.press('Escape')
    # inventory + tooltip
    await pg.keyboard.press('i'); await pg.wait_for_timeout(500)
    idx=await ev("()=>__game.INV.bag.findIndex(b=>b.id==='w_boar_tusk')"); await pg.click(f'#ovp [data-bag="{idx}"]'); await pg.mouse.move(5,5)
    bg=await ev(BG,'#ovp'); ok('inv_translucent','0.65' in bg,bg)
    ok('tip_translucent','rgba' in await ev(BG,'#ovp .tip'),await ev(BG,'#ovp .tip'))
    ok('backdrop_light',await ev("()=>{const m=getComputedStyle(document.getElementById('ov')).backgroundColor.match(/[\\d.]+/g);return +m[3]<0.2}"))
    await pg.wait_for_timeout(200); await pg.screenshot(path=D+'shot_ui_translucent_inv.png')
    await pg.keyboard.press('Escape')
    # Esc menu option: select '창 투명도' (3rd item) and press → / Enter
    await pg.keyboard.press('Escape'); await pg.keyboard.press('ArrowDown'); await pg.keyboard.press('ArrowDown')
    t0=await ev("()=>document.querySelector('.mi.sel').textContent"); await pg.keyboard.press('ArrowRight')
    ok('menu_option',('창 투명도' in t0) and await ev("()=>__game.uiAlpha===0.5"),[t0,await ev("()=>__game.uiAlpha")])
    await pg.screenshot(path='/tmp/ui_menu.png')
    await pg.keyboard.press('Enter'); ok('menu_cycle',await ev("()=>__game.uiAlpha===0.35"))
    for _ in range(2): await pg.keyboard.press('ArrowLeft')
    ok('menu_left',await ev("()=>Math.abs(__game.uiAlpha-0.65)<1e-9"),await ev("()=>__game.uiAlpha"))
    # options screen buttons
    await pg.keyboard.press('ArrowUp'); await pg.keyboard.press('Enter'); ok('options_open',await ev("()=>__game.ui==='options'"))
    await pg.click('[data-ua="0.2"]'); ok('options_button',await ev("()=>Math.abs(__game.uiAlpha-0.8)<1e-9&&getComputedStyle(document.querySelector('#ovp')).backgroundColor.includes('0.8')"))
    await pg.keyboard.press('Escape'); await pg.keyboard.press('Escape')
    # F5 quick save keeps it even if localStorage value changes
    await pg.keyboard.press('F5'); await ev("()=>localStorage.setItem('townDemo.uiAlpha','0.5')"); await pg.reload(); await ready(pg)
    ok('f5_restore',await ev("()=>Math.abs(__game.uiAlpha-0.8)<1e-9"),await ev("()=>__game.uiAlpha"))
    ok('noErrors',not errs,errs)
    await b.close()
  print(json.dumps(R,ensure_ascii=False)); print('FAIL',FAIL)
asyncio.run(main())
