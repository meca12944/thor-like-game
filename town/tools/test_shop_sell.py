# Headless test: shop-only selling (판매 tab inside the shop, opened by talking to the shop NPC 미라벨) + rarity stars
# on icons (bag, equipment, shop, forge, tooltip, drop notification). Writes shot_shop_sell.png.
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
STARS_OK="""()=>{const g=__game;const bad=[];let n=0;
 document.querySelectorAll('#ovp .cell[data-bag],#ovp .cell[data-eq]').forEach(c=>{const i=c.dataset.bag!==undefined?g.INV.bag[+c.dataset.bag]:g.INV.equip[['weapon','helmet','armor','offhand'][+c.dataset.eq]];if(!i)return;
  const s=c.querySelector('.stars'),k=s?+s.dataset.stars:0;n++;if(k!==g.starCount(i.id))bad.push(i.id+':'+k);});return [n,bad]}"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':720}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
    await pg.goto(U); await ready(pg); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await ready(pg)
    ev=pg.evaluate; key=pg.keyboard.press
    await ev("()=>{__game.setManual(true);document.getElementById('hint').style.display='none';}")
    # --- rarity stars config
    ok('stars_config',await ev("()=>JSON.stringify(__game.RARITY_STARS)===JSON.stringify({common:0,uncommon:1,rare:2,epic:3,legendary:4,unique:4,corrupt:3})"))
    ok('stars_items',await ev("()=>[__game.starCount('potion'),__game.starCount('w_boar_tusk'),__game.starCount('pearl'),__game.starCount('tk_kalbaram'),__game.starCount('hs_gyu'),__game.starCount('hs_tak'),__game.starCount('hs_chan')].join()==='0,1,2,3,4,4,4'"))
    await key('i'); await pg.wait_for_timeout(200)
    n,bad=await ev(STARS_OK); ok('stars_bag_equip',n>=25 and not bad,[n,bad])
    gi=await ev("()=>__game.INV.bag.findIndex(b=>b.id==='hs_gyu')"); await pg.click(f'#ovp [data-bag="{gi}"]')
    ok('stars_tooltip',await ev("()=>{const s=document.querySelector('#ovp .tip .bigw .stars');return !!s&&s.dataset.stars==='4'&&s.style.width==='50px'&&document.querySelector('#ovp .tip .rst').textContent==='★★★★'}"))
    ok('stars_pixel',await ev("()=>{const s=document.querySelector('#ovp .cell.sel .stars');const c=getComputedStyle(s);return c.imageRendering==='pixelated'&&s.style.width==='25px'&&s.style.height==='7px'}"))
    # --- no selling from the inventory; shop tab locked
    g0=await ev("()=>__game.INV.gold"); await key('Delete'); ok('inv_no_sell',await ev("(g)=>__game.INV.gold===g&&__game.invCount('hs_gyu')===1",g0))
    await key('2'); ok('shop_tab_locked',await ev("()=>__game.invTab===0"))
    await key('Escape')
    # --- demo shortcut is labelled demo-only
    await key('Escape'); ok('menu_demo_label',await ev("()=>[...document.querySelectorAll('.menu .mi')].some(e=>e.textContent.includes('상점 (데모 전용'))")); await key('Escape')
    # --- shop NPC: walk up, khud hint, talk -> shop
    await ev("()=>{const h=__game.hero,n=__game.shopNpc;h.x=n.x-60;h.y=n.y+30;h.hz='right';}"); await pg.wait_for_timeout(300)
    ok('khud_shop',await ev("()=>document.getElementById('khud').textContent.includes('미라벨과 거래')"))
    await key('l'); ok('shop_dialog_portrait',await ev("()=>__game.dlg&&__game.dlg.id==='shop'&&document.querySelector('#dlg .dp').src.includes('a_tool')"))
    for _ in range(3): await key('l')
    ok('shop_open',await ev("()=>__game.ui==='inv'&&__game.invTab===1&&__game.shopAt==='a_tool'&&__game.shopMode==='buy'&&document.querySelector('#ovp h2').textContent.includes('보따리')"))
    # buy -> drop notification
    for _ in range(8): await key('ArrowDown')
    await key('Enter'); ok('buy_drop_note',await ev("()=>[...document.querySelectorAll('#dropn .dn1')].some(e=>e.dataset.id==='potion'&&e.textContent.includes('구매'))"))
    # --- sell mode (Tab)
    await key('Tab'); ok('sell_mode',await ev("()=>__game.shopMode==='sell'&&document.querySelectorAll('#ovp .grid .cell .ic32').length===__game.INV.bag.length"))
    n,bad=await ev(STARS_OK); ok('stars_shop_sell',n>=25 and not bad,[n,bad])
    # sell one potion: Enter asks, Enter confirms
    pi=await ev("()=>__game.INV.bag.findIndex(b=>b.id==='potion')"); await pg.click(f'#ovp [data-bag="{pi}"]')
    ok('sell_price_shown',await ev("()=>document.querySelector('#ovp .sellp').textContent.includes('10')"))
    g0=await ev("()=>__game.INV.gold"); c0=await ev("()=>__game.invCount('potion')")
    await key('Enter'); ok('sell_confirm_ask',await ev("([g,c])=>__game.INV.gold===g&&__game.invCount('potion')===c&&!!__game.sellPend",[g0,c0]))
    await key('Enter'); ok('sell_potion',await ev("([g,c])=>__game.INV.gold===g+10&&__game.invCount('potion')===c-1&&!__game.sellPend",[g0,c0]),await ev("()=>__game.invNote"))
    # Esc cancels a pending sale without closing the shop
    si=await ev("()=>__game.INV.bag.findIndex(b=>b.id==='o_sling')"); await pg.click(f'#ovp [data-bag="{si}"]'); await key('Enter'); await key('Escape')
    ok('esc_cancels',await ev("()=>__game.ui==='inv'&&!__game.sellPend&&__game.INV.bag.some(b=>b.id==='o_sling')"))
    # equipment sells by its own slot (non-stackable); 50% of buy price
    g0=await ev("()=>__game.INV.gold"); await key('Enter'); await key('Enter')
    ok('sell_gear',await ev("(g)=>__game.INV.gold===g+45&&!__game.INV.bag.some(b=>b.id==='o_sling')",g0))
    # unsellable (hidden sword)
    gi=await ev("()=>__game.INV.bag.findIndex(b=>b.id==='hs_gyu')"); await pg.click(f'#ovp [data-bag="{gi}"]'); await key('Enter')
    ok('unsellable',await ev("()=>__game.invNote.includes('팔 수 없는')&&__game.invCount('hs_gyu')===1"))
    # equipped item blocked
    g0=await ev("()=>__game.INV.gold"); await pg.click('#ovp [data-eq="0"]'); await key('Enter'); await key('Enter')
    ok('equipped_blocked',await ev("(g)=>__game.INV.gold===g&&__game.INV.equip.weapon.id==='w_bronze_long'&&__game.invNote.includes('장착')",g0),await ev("()=>__game.invNote"))
    # unequip in tab 1, come back to the shop (still at the NPC) and sell it
    await key('1'); await pg.click('#ovp [data-eq="0"]'); await key('Enter')
    ok('unequipped',await ev("()=>!__game.INV.equip.weapon&&__game.INV.bag.some(b=>b.id==='w_bronze_long')"))
    await key('2'); ok('back_to_shop',await ev("()=>__game.invTab===1&&__game.shopMode==='sell'"))
    wi=await ev("()=>__game.INV.bag.findIndex(b=>b.id==='w_bronze_long')"); await pg.click(f'#ovp [data-bag="{wi}"]')
    g0=await ev("()=>__game.INV.gold"); await key('Enter'); await key('Enter')
    ok('sell_after_unequip',await ev("(g)=>__game.INV.gold===g+140&&!__game.INV.bag.some(b=>b.id==='w_bronze_long')",g0))
    # screenshot: sell tab, cursor on the +5 boar tusk (1 star) with a pending confirm, drop notification with stars
    await ev("()=>{__game.dropNote('pearl',1,'획득');__game.dropNote('hs_gyu',1,'획득');}")
    ok('drop_note_stars',await ev("()=>{const e=[...document.querySelectorAll('#dropn .dn1')].find(x=>x.dataset.id==='hs_gyu');return !!e&&e.querySelector('.stars').dataset.stars==='4'}"))
    ti=await ev("()=>__game.INV.bag.findIndex(b=>b.id==='w_boar_tusk')"); await pg.click(f'#ovp [data-bag="{ti}"]'); await key('Enter'); await pg.mouse.move(5,5)
    await pg.wait_for_timeout(350); await pg.screenshot(path=D+'shot_shop_sell.png')
    await key('Escape'); await key('Escape'); ok('closed',await ev("()=>__game.ui===null&&__game.shopAt===null"))
    # forge rows carry stars too (same cell renderer)
    await key('i'); await key('3'); ok('forge_cells',await ev("()=>document.querySelectorAll('#ovp .list .row .cell').length>0")); await key('Escape')
    ok('noErrors',not errs,errs)
    await b.close()
  print(json.dumps(R,ensure_ascii=False)); print('FAIL',FAIL)
try: asyncio.run(main())
except Exception as e:
  print(json.dumps(R,ensure_ascii=False)); print('FAIL',FAIL+['exception: '+str(e).splitlines()[0]])
