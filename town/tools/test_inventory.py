# Headless test: icon inventory / equipment / quick slot / shop / forge + keyboard navigation. Writes shot_inventory.png.
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
    pg.on('requestfailed',lambda r: errs.append('FAIL '+r.url))
    await pg.goto(U); await ready(pg); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await ready(pg)
    ev=pg.evaluate
    await ev("()=>{__game.setManual(true);document.getElementById('hint').style.display='none';const h=__game.hero;h.x=520;h.y=600;h.hp=2;}")
    # HUD quick slot shows the potion icon + count
    ok('quickslot_hud',await ev("()=>{const q=document.getElementById('qslot');return !!q.querySelector('.ic32')&&q.querySelector('.cnt').textContent==='3'}"))
    await pg.keyboard.press('i'); await pg.wait_for_timeout(400)
    ok('inv_open',await ev("()=>__game.ui==='inv'&&__game.invTab===0"))
    ok('icons_loaded',await ev("()=>new Promise(r=>{const i=new Image();i.onload=()=>r(i.naturalWidth===512);i.onerror=()=>r(false);i.src='assets/icons/icons32.png'})"))
    ncell=await ev("()=>document.querySelectorAll('#ovp .grid .cell .ic32').length"); ok('bag_icons',ncell==await ev("()=>__game.INV.bag.length"),ncell)
    ok('equip_icons',await ev("()=>document.querySelectorAll('#ovp .eqrow .cell .ic32').length")==5)
    ok('stack_counts',await ev("()=>[...document.querySelectorAll('#ovp .grid .cell .cnt')].map(e=>e.textContent).includes('12')"))
    ok('plus_badge',await ev("()=>[...document.querySelectorAll('#ovp .cell .pl')].map(e=>e.textContent).includes('+3')"))
    ok('rarity_border',await ev("()=>{const c=[...document.querySelectorAll('#ovp .grid .cell')].map(e=>e.style.getPropertyValue('--rc'));return new Set(c.filter(Boolean)).size>=4}"))
    # keyboard nav: arrows move cursor; tooltip follows
    await pg.keyboard.press('ArrowRight'); await pg.keyboard.press('ArrowRight'); await pg.keyboard.press('ArrowDown')
    ok('arrow_nav',await ev("()=>__game.invZone==='bag'&&__game.invSel===10"))
    await pg.keyboard.press('s'); ok('wasd_nav',await ev("()=>__game.invSel===18"))
    for k in ['ArrowUp','ArrowUp','ArrowLeft','ArrowLeft']: await pg.keyboard.press(k)
    # select the +5 boar tusk (bag index 8) and check the tooltip
    await ev("()=>{}"); idx=await ev("()=>__game.INV.bag.findIndex(b=>b.id==='w_boar_tusk')")
    await pg.click(f'#ovp [data-bag="{idx}"]')
    tip=await ev("()=>document.querySelector('#ovp .tip').innerText"); ok('tooltip',('돌엄니 송곳검' in tip and '+5' in tip and '공격' in tip),tip)
    ok('tooltip_64',await ev("()=>!!document.querySelector('#ovp .tip .ic64')"))
    await pg.screenshot(path=D+'shot_inventory.png')
    # equip with Enter -> swapped into weapon slot
    await pg.keyboard.press('Enter'); ok('equip',await ev("()=>__game.INV.equip.weapon.id==='w_boar_tusk'&&__game.INV.equip.weapon.plus===5&&__game.INV.bag.some(b=>b.id==='w_bronze_long'&&b.plus===3)"))
    # use a potion from the bag (Enter) -> heals
    await ev("()=>{__game.hero.hp=20;__game.potionCd=0}"); hp0=20
    pidx=await ev("()=>__game.INV.bag.findIndex(b=>b.id==='potion')"); await pg.click(f'#ovp [data-bag="{pidx}"]'); await pg.keyboard.press('Enter')
    ok('use_potion',await ev("()=>__game.hero.hp===35&&__game.potions===2"))
    # register herb as quick item (R), press E in game
    hidx=await ev("()=>__game.INV.bag.findIndex(b=>b.id==='herb_red')"); await pg.click(f'#ovp [data-bag="{hidx}"]'); await pg.keyboard.press('r')
    ok('quick_register',await ev("()=>__game.INV.quick==='herb_red'"))
    # left from column 0 goes to equipment column
    await pg.click('#ovp [data-bag="0"]'); await pg.keyboard.press('ArrowLeft'); ok('to_equip_zone',await ev("()=>__game.invZone==='equip'"))
    # selling is shop-only: Del in the inventory does nothing but explain; tab 2 (상점) is locked away from a shop NPC
    g0=await ev("()=>__game.INV.gold"); nb=await ev("()=>__game.INV.bag.length"); await pg.click('#ovp [data-bag="7"]'); await pg.keyboard.press('Delete')
    ok('no_del_sell',await ev("([g,n])=>__game.INV.gold===g&&__game.INV.bag.length===n&&__game.invNote.includes('상점')",[g0,nb]),await ev("()=>__game.invNote"))
    await pg.keyboard.press('2'); ok('shop_locked',await ev("()=>__game.invTab===0&&__game.invNote.includes('상점 NPC')&&!!document.querySelector('#ovp .tab.lock')"))
    await pg.keyboard.press('e'); ok('qe_skips_shop',await ev("()=>__game.invTab===2")); await pg.keyboard.press('1')
    # talk to the shop NPC (미소) -> dialogue -> shop window (tab 2)
    await pg.keyboard.press('Escape'); await ev("()=>{const h=__game.hero,n=__game.shopNpc;h.x=n.x-60;h.y=n.y+30;}")
    await pg.keyboard.press('l'); ok('shop_npc_dialog',await ev("()=>__game.ui==='dialog'&&__game.dlg.id==='shop'"))
    for _ in range(3): await pg.keyboard.press('l')
    ok('shop_tab',await ev("()=>__game.ui==='inv'&&__game.shopAt==='a_tool'&&__game.invTab===1&&document.querySelectorAll('#ovp .list .row .ic32').length>=17"))
    n0=await ev("()=>__game.invCount('potion')")
    for _ in range(8): await pg.keyboard.press('ArrowDown')
    await pg.keyboard.press('Enter')
    ok('shop_buy',await ev("([g,n])=>__game.INV.gold===g-20&&__game.invCount('potion')===n+1",[g0,n0]),await ev("()=>__game.invNote"))
    await pg.screenshot(path='/tmp/inv_shop.png')
    # forge tab (3): enhance + craft 견습 철검 (materials present)
    await pg.keyboard.press('e'); ok('forge_tab',await ev("()=>__game.invTab===2"))
    await ev("()=>{window.__forceSuccess=1}")
    await pg.keyboard.press('Enter'); ok('enhance_cap',await ev("()=>__game.invNote.includes('+3')"),await ev("()=>__game.invNote"))
    await pg.keyboard.press('ArrowDown'); c0=await ev("()=>__game.INV.bag.filter(b=>b.id==='w_iron_trainee').length")
    await pg.keyboard.press('Enter')
    ok('craft',await ev("(c)=>__game.INV.bag.filter(b=>b.id==='w_iron_trainee').length===c+1&&__game.invCount('m_iron_ingot')===10",c0),await ev("()=>__game.invNote"))
    await pg.screenshot(path='/tmp/inv_forge.png')
    await pg.keyboard.press('Escape'); ok('close',await ev("()=>__game.ui===null"))
    # E in game uses quick item (herb +1)
    await ev("()=>{__game.hero.hp=1;__game.potionCd=0}"); await pg.keyboard.press('e'); ok('quick_E_herb',await ev("()=>__game.hero.hp===6&&__game.invCount('herb_red')===4"))  # 빨간 약초 = 10% of 50
    # inventory survives quick save/load
    await pg.keyboard.press('F5'); await pg.reload(); await ready(pg)
    ok('save_inv',await ev("()=>__game.INV.equip.weapon.id==='w_boar_tusk'&&__game.INV.quick==='herb_red'"))
    ok('noErrors',not errs,errs)
    await b.close()
  f=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',22)
  tiles=[(D+'shot_inventory.png','가방 · 장비 (툴팁)'),('/tmp/inv_shop.png','상점'),('/tmp/inv_forge.png','대장간')]
  W,H=640,360; sh=Image.new('RGB',(W*3,H+36),(16,16,20)); d=ImageDraw.Draw(sh)
  for i,(fn,t) in enumerate(tiles): sh.paste(Image.open(fn).convert('RGB').resize((W,H)),(i*W,36)); d.text((i*W+10,5),t,font=f,fill='white')
  sh.save(D+'shot_inventory_tabs.png')
  print(json.dumps(R,ensure_ascii=False)); print('FAIL',FAIL)
asyncio.run(main())
