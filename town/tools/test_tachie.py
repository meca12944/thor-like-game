"""Full-body dialogue portraits (town/tachie.js): wiring, expression swap, fallback, dim/lit, FPS + screenshots.
Run: python3 tools/test_tachie.py [outdir]   (serves town/ on :18951)"""
import asyncio, json, socket, subprocess, sys, os
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/';PORT=18951;U='http://127.0.0.1:%d/index.html?nosave=1'%PORT
OUT=sys.argv[1] if len(sys.argv)>1 else '/tmp/tachie_test'
os.makedirs(OUT,exist_ok=True)
def srv():
  s=socket.socket()
  try: s.connect(('127.0.0.1',PORT));s.close();return None
  except OSError: return subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
ST="()=>{const s=__tachie.slots;const f=S=>({on:S.el.classList.contains('on'),dim:S.el.classList.contains('dim'),id:S.id,expr:S.expr,src:(S.imgs[S.cur].getAttribute('src')||'')});return {L:f(s.L),R:f(s.R),dp:!!document.querySelector('#dlg .dp'),text:document.querySelector('#dlg .dt')&&document.querySelector('#dlg .dt').textContent}}"
async def main():
  p0=srv();await asyncio.sleep(.8);R={};errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=['--enable-gpu-rasterization','--ignore-gpu-blocklist']);pg=await b.new_page(viewport={'width':1920,'height':1080});pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto(U);await pg.wait_for_function('window.__game&&window.__game.ready&&window.__tachie',timeout=30000)
    await pg.evaluate("()=>{const g=__game;g.slimes.forEach(m=>{m.dead=true;m.respawn=1e9});}")
    R['chars']=[sorted(await pg.evaluate("()=>__tachie.chars()"))==sorted(['hero','a_tailor','h_mystic','g_dancer','f_diver','e_tailor','c_priest','d_yuna']),await pg.evaluate("()=>__tachie.chars()")]
    # walk-up interaction with 나비 in town
    n=await pg.evaluate("()=>{const n=__tachie.nabi,h=__game.hero;h.x=n.x-60;h.y=n.y;return [n.x,n.y]}")
    await pg.wait_for_timeout(200);await pg.keyboard.press('KeyE');await pg.wait_for_timeout(100)
    tgt=await pg.evaluate("()=>__game.ui");key=None
    if tgt!='dialog':
      for k in ['KeyF','Enter','Space','KeyZ']:
        await pg.keyboard.press(k);await pg.wait_for_timeout(100)
        if await pg.evaluate("()=>__game.ui")=='dialog':key=k;break
    else:key='KeyE'
    st=await pg.evaluate(ST);R['talk_nabi_walkup']=[st['R']['id']=='a_tailor' and st['R']['on'],{'key':key,'nabi':n,**st}]
    await pg.evaluate("()=>closeUI()")
    # each heroine: every line -> speaker lit, listener dim, expression file matches line
    ok=True;det={}
    for cid in ['a_tailor','h_mystic','g_dancer','f_diver','e_tailor','c_priest','d_yuna']:
      await pg.evaluate("(c)=>__tachie.openTalk(c)",cid);seen=set()
      while True:
        await pg.wait_for_timeout(260);st=await pg.evaluate(ST)
        L=await pg.evaluate("()=>{const T=TALK[dlg.id];const l=T.lines[dlg.i]();return l}")
        who='L' if L.get('who')=='hero' else 'R';oth='R' if who=='L' else 'L'
        good=st[who]['on'] and not st[who]['dim'] and st[oth]['on'] and st[oth]['dim'] and st[who]['src'].endswith('_%s.png'%L.get('expr','neutral')) and not st['dp']
        seen.add(L.get('expr'));ok=ok and good
        if not good:det[cid]=[L,st]
        last=await pg.evaluate("()=>dlg.i>=TALK[dlg.id].lines.length-1")
        if last:break
        await pg.evaluate("()=>dialogNext()")
      det.setdefault(cid,sorted(x for x in seen if x))
      await pg.evaluate("()=>closeUI()");await pg.wait_for_timeout(350)
      st=await pg.evaluate(ST);ok=ok and not st['L']['on'] and not st['R']['on']
    R['lines_lit_dim_expr']=[ok,det]
    # fallback: unknown expression -> neutral
    fb=await pg.evaluate("()=>{TALK.__fb={name:'t',por:'c_priest',lines:[()=>({who:'c_priest',expr:'nonexistent',t:'x'})]};__tachie.openTalk('__fb');return 1}")
    await pg.wait_for_timeout(300);st=await pg.evaluate(ST);R['fallback_neutral']=[st['R']['src'].endswith('c_priest_neutral.png'),st['R']];await pg.evaluate("()=>closeUI()")
    # existing dialogues untouched: spirit keeps its small portrait; hero tachie appears (hero takes part)
    await pg.evaluate("()=>{dlg={id:'spirit',i:1};openUI('dialog')}");await pg.wait_for_timeout(300);st=await pg.evaluate(ST)
    R['spirit_small_portrait']=[st['dp'] and st['L']['on'] and st['L']['dim'] and not st['R']['on'],st];await pg.evaluate("()=>closeUI()")
    # screenshots
    await pg.evaluate("()=>{const n=__tachie.nabi,h=__game.hero;h.x=n.x-70;h.y=n.y+10;h.face='right'}");await pg.wait_for_timeout(300)
    await pg.evaluate("()=>__tachie.openTalk('a_tailor',1)");await pg.wait_for_timeout(700)
    print('probe',await pg.evaluate("()=>{const S=__tachie.slots.R;return [S.el.className,getComputedStyle(S.el).opacity,...S.imgs.map(i=>i.className+':'+getComputedStyle(i).opacity+':'+(i.getAttribute('src')||'').slice(-22))]}"))
    await pg.screenshot(path=OUT+'/dialogue_hero_talking.png')
    await pg.evaluate("()=>{dialogNext()}");await pg.wait_for_timeout(700)
    await pg.screenshot(path=OUT+'/dialogue_heroine_speaking.png')
    await pg.evaluate("()=>closeUI()")
    await pg.evaluate("()=>__tachie.openTalk('d_yuna',3)");await pg.wait_for_timeout(700);await pg.screenshot(path=OUT+'/dialogue_yuna_smile.png');await pg.evaluate("()=>closeUI()")
    # FPS: F3 overlay on, run dialogue with line changes every 0.5 s for ~6 s (real rAF time)
    await pg.keyboard.press('F3');await pg.evaluate("()=>__tachie.openTalk('g_dancer')")
    fps=await pg.evaluate("""async()=>{const ts=[];let run=true;const loop=t=>{ts.push(t);if(run)requestAnimationFrame(loop)};requestAnimationFrame(loop);
      for(let k=0;k<12;k++){await new Promise(r=>setTimeout(r,500));if(dlg.i>=TALK[dlg.id].lines.length-1)dlg.i=-1;dialogNext();}
      run=false;const d=[];for(let i=1;i<ts.length;i++)d.push(ts[i]-ts[i-1]);d.sort((a,b)=>a-b);
      return {frames:ts.length,avg:1000*(ts.length-1)/(ts[ts.length-1]-ts[0]),p99:d[Math.floor(d.length*.99)],max:d[d.length-1],hud:__game.fpsVal!==undefined?__game.fpsVal:null}}""")
    await pg.screenshot(path=OUT+'/dialogue_fps_f3.png')
    R['fps']=[fps['avg']>57,fps]
    await b.close()
  if p0:p0.terminate()
  R['no_page_errors']=[not errs,errs[:5]]
  allok=all(v[0] for v in R.values())
  for k,v in R.items():print(('PASS' if v[0] else 'FAIL'),k,json.dumps(v[1],ensure_ascii=False)[:600])
  print('ALL PASS' if allok else 'SOME FAILED');sys.exit(0 if allok else 1)
asyncio.run(main())
