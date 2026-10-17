# Headless test for the PC keyboard controls (CONTROLS.md): default keymap, every action, rebinding, conflicts, reset, persistence.
import asyncio, json
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
U='http://localhost:18931/index.html'; D='/workspace/town-demo/'
R={}; FAIL=[]
def ok(name,cond,info=None):
  R[name]=bool(cond) if info is None else [bool(cond),info]
  if not cond: FAIL.append(name)
async def ready(pg):
  for i in range(100):
    if await pg.evaluate('!!(window.__game&&window.__game.ready)'): return
    await pg.wait_for_timeout(100)
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':720}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
    await pg.goto(U); await ready(pg); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await ready(pg)
    G="__game"
    async def ev(js,arg=None): return await pg.evaluate(js,arg) if arg is not None else await pg.evaluate(js)
    async def adv(t=.05): await ev(f"()=>{G}.advance({t})")
    await ev("()=>{const g=__game;g.setManual(true);window.__marker=1;const h=g.hero;h.x=520;h.y=600;h.face='down';g.slimes.forEach(m=>{m.t=99});}")
    km=await ev("()=>__game.ctl.KEYMAP"); ok('defaults',km==await ev("()=>__game.ctl.defaultKeys()"),km)
    ok('noConflicts',await ev("()=>__game.ctl.allConflicts().length===0"))
    # attack J / Z (and Korean IME: key 'ㅓ' with code KeyJ)
    await pg.keyboard.press('j'); await adv(); ok('attack_J',await ev("()=>!!__game.hero.atk"))
    await adv(1.2); await pg.keyboard.press('z'); await adv(); ok('attack_Z',await ev("()=>!!__game.hero.atk"))
    await adv(1.2); await ev("()=>{dispatchEvent(new KeyboardEvent('keydown',{key:'ㅓ',code:'KeyJ'}));dispatchEvent(new KeyboardEvent('keyup',{key:'ㅓ',code:'KeyJ'}))}"); await adv(); ok('attack_hangulIME',await ev("()=>!!__game.hero.atk"))
    await adv(1.2)
    # dash K / X
    x0=await ev("()=>__game.hero.x"); await pg.keyboard.down('a'); await pg.keyboard.press('k'); await adv(.25); await pg.keyboard.up('a')
    ok('dash_K',await ev("(x)=>x-__game.hero.x>90",x0),await ev("(x)=>Math.round(x-__game.hero.x)",x0))
    await adv(.6); await pg.keyboard.press('x'); await adv(.02); ok('dash_X',await ev("()=>!!__game.hero.dash"))
    await adv(.6)
    # target Tab
    await pg.keyboard.press('Tab'); ok('target_Tab',await ev("()=>!!__game.target"))
    # potion E
    await ev("()=>{__game.hero.hp=1}"); await pg.keyboard.press('e'); ok('potion_E',await ev("()=>__game.hero.hp===3&&__game.potions===2"))
    # area Q: none -> message; 일월식 -> damage + cooldown
    await pg.keyboard.press('q'); await adv(.02); ok('area_none_msg',await ev("()=>(__game.msg||'').includes('광역 스킬 없음')"))
    await ev("()=>{__game.ctl.setAreaMode('chan');__game.slimes.forEach(m=>{if(!m.dead){m.hp=m.maxHp||m.hp}})}")
    hp0=await ev("()=>__game.slimes.filter(m=>!m.dead).map(m=>m.hp)")
    await pg.keyboard.press('q'); await adv(.3)
    ok('area_Q_chan',await ev("()=>__game.areaCd>0"),[hp0,await ev("()=>__game.slimes.map(m=>m.dead?'x':m.hp)")])
    await pg.screenshot(path='/tmp/ctl_area.png'); await adv(1.5)
    # skills 1
    await ev("()=>{__game.gauge=1}"); await pg.keyboard.press('1'); await adv(.02); ok('skill_1',await ev("()=>!!__game.hero.sk"))
    await adv(3)
    # G gear
    await pg.keyboard.press('g'); ok('gear_G',await ev("()=>__gear().idx===1"))
    # windows: I / M / O / P / Esc
    await pg.keyboard.press('i'); ok('inv_I',await ev("()=>__game.ui==='inv'")); await pg.screenshot(path='/tmp/ctl_inv.png')
    await pg.keyboard.press('Escape'); ok('inv_close',await ev("()=>__game.ui===null"))
    await pg.keyboard.press('m'); await pg.wait_for_timeout(400); ok('map_M',await ev("()=>__game.ui==='map'&&document.querySelector('img.wmap').naturalWidth>0"))
    await pg.screenshot(path='/tmp/ctl_map.png'); await pg.keyboard.press('m'); ok('map_close',await ev("()=>__game.ui===null"))
    await pg.keyboard.press('o'); ok('skills_O',await ev("()=>__game.winOpen")); await pg.keyboard.press('p'); ok('skills_P_close',await ev("()=>!__game.winOpen"))
    await pg.keyboard.press('p'); await pg.keyboard.press('Escape'); ok('skills_Esc',await ev("()=>!__game.winOpen&&__game.ui===null"))
    # paused while menu open
    await ev("()=>__game.setManual(false)"); await pg.keyboard.press('Escape'); ok('menu_Esc',await ev("()=>__game.ui==='menu'"))
    hx=await ev("()=>__game.hero.x"); await pg.keyboard.down('d'); await pg.wait_for_timeout(300); await pg.keyboard.up('d')
    ok('menu_pauses',await ev("(x)=>__game.hero.x===x",hx)); await pg.screenshot(path='/tmp/ctl_menu.png')
    await pg.keyboard.press('ArrowDown'); await pg.keyboard.press('Enter'); ok('menu_to_options',await ev("()=>__game.ui==='options'"))
    # rebinding: attack slot 1 -> F
    await pg.click('.kc[data-r="4"][data-c="0"]'); await pg.keyboard.press('f')
    ok('rebind_F',await ev("()=>__game.ctl.KEYMAP.attack[0]==='KeyF'&&JSON.parse(localStorage.getItem('townDemo.keys')).attack[0]==='KeyF'"))
    # conflict: attack slot 1 -> K (dash) : first press warns, second swaps
    await pg.click('.kc[data-r="4"][data-c="0"]'); await pg.keyboard.press('k')
    ok('conflict_warn',await ev("()=>__game.ctl.optNote.includes('이미')&&__game.ctl.KEYMAP.attack[0]==='KeyF'&&!!__game.ctl.rebind"),await ev("()=>__game.ctl.optNote"))
    await pg.screenshot(path='/tmp/ctl_conflict.png')
    await pg.keyboard.press('k')
    ok('conflict_swap',await ev("()=>{const m=__game.ctl.KEYMAP;return m.attack[0]==='KeyK'&&m.dash.includes('KeyF')&&!m.dash.includes('KeyK')&&__game.ctl.allConflicts().length===0}"),await ev("()=>[__game.ctl.KEYMAP.attack,__game.ctl.KEYMAP.dash]"))
    # Esc is locked on menu
    await pg.click('.kc[data-r="18"][data-c="0"]'); ok('esc_locked',await ev("()=>!__game.ctl.rebind&&__game.ctl.optNote.includes('Esc')"))
    await pg.keyboard.press('Escape'); await pg.keyboard.press('Escape'); ok('back_to_game',await ev("()=>__game.ui===null"))
    # rebound key works in game; persists after reload
    await ev("()=>__game.setManual(true)"); await adv(1); await pg.keyboard.press('k'); await adv(); ok('rebound_attack_works',await ev("()=>!!__game.hero.atk&&!__game.hero.dash"))
    await pg.reload(); await ready(pg); ok('persist',await ev("()=>__game.ctl.KEYMAP.attack[0]==='KeyK'"))
    await ev("()=>__game.ctl.openUI('options')"); await pg.click('#kreset')
    ok('reset',await ev("()=>JSON.stringify(__game.ctl.KEYMAP)===JSON.stringify(__game.ctl.defaultKeys())&&JSON.parse(localStorage.getItem('townDemo.keys')).attack[0]==='KeyJ'"))
    await pg.screenshot(path='/tmp/ctl_options.png'); await pg.keyboard.press('Escape'); await pg.keyboard.press('Escape')
    # interact L / C / Enter -> dialog with key hints
    await ev("()=>{const g=__game;g.setManual(true);g.hero.x=640;g.hero.y=560;g.slimes.forEach(m=>{m.dead=true;m.respawn=99});}")
    for k,name in (('l','L'),('c','C'),('Enter','Enter')):
      await pg.keyboard.press(k); ok('interact_'+name,await ev("()=>__game.ui==='dialog'")); 
      if name=='L':
        await pg.keyboard.press('l'); ok('dialog_next',await ev("()=>__game.dlg&&__game.dlg.i===1&&document.querySelector('#dlg .dh').textContent.includes('L/C')"))
        await pg.screenshot(path='/tmp/ctl_dialog.png')
      await pg.keyboard.press('Escape')
    # dive Space next to the rain barrel spot; Space again surfaces
    await ev("()=>{const h=__game.hero;h.x=450;h.y=190;h.face='up';}"); await pg.keyboard.press('Space'); await adv(.02)
    ok('dive_Space',await ev("()=>__game.hero.sk&&__game.hero.sk.id==='dive'"))
    await adv(1.5); ok('underwater',await ev("()=>!!__game.uw")); await pg.keyboard.press('Space'); await adv(2); ok('surface_Space',await ev("()=>!__game.uw"))
    # F5 quick save (no reload) -> restored on load
    await ev("()=>{window.__marker=2;const h=__game.hero;h.sk=null;h.x=700;h.y=520;h.hp=2;__game.potions=1}"); await pg.keyboard.press('F5'); await pg.wait_for_timeout(200)
    ok('F5_no_reload',await ev("()=>window.__marker===2&&!!localStorage.getItem('townDemo.quicksave')"))
    await pg.reload(); await ready(pg); ok('quickload',await ev("()=>{const h=__game.hero;return h.x===700&&h.y===520&&h.hp===2&&__game.potions===1}"))
    # HUD key bar
    await ev("()=>{__game.setManual(false)}"); await pg.wait_for_timeout(300)
    kh=await ev("()=>document.getElementById('khud').textContent"); ok('khud',('J' in kh and 'Esc' in kh and 'K' in kh),kh)
    ok('slotKeys',await ev("()=>[...document.querySelectorAll('.slot .k')].map(e=>e.textContent).join()==='1,2,3'"))
    await pg.screenshot(path='/tmp/ctl_hud.png')
    ok('noErrors',not errs,errs)
    await b.close()
  # contact sheet
  f=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',22)
  tiles=[('/tmp/ctl_hud.png','HUD 키 안내'),('/tmp/ctl_menu.png','Esc 메뉴 (일시정지)'),('/tmp/ctl_options.png','조작 설정 (키 변경)'),('/tmp/ctl_conflict.png','충돌 감지'),('/tmp/ctl_dialog.png','대화 (L/C/Enter)'),('/tmp/ctl_inv.png','인벤토리 (I)'),('/tmp/ctl_map.png','월드맵 (M)'),('/tmp/ctl_area.png','Q 광역: 일월식')]
  W,H=640,360; sheet=Image.new('RGB',(W*4,(H+36)*2),(16,16,20)); d=ImageDraw.Draw(sheet)
  for i,(fn,t) in enumerate(tiles):
    im=Image.open(fn).convert('RGB').resize((W,H)); x,y=(i%4)*W,(i//4)*(H+36); sheet.paste(im,(x,y+36)); d.text((x+10,y+5),t,font=f,fill='white')
  sheet.save(D+'shot_controls.png')
  print(json.dumps(R,ensure_ascii=False,indent=0)); print('FAIL',FAIL)
asyncio.run(main())
