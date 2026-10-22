# In-game sound check: auto-play a field fight (hero swings / rolls, mobs attack), log every sound call with its game time,
# then render the same sounds offline (code SFX2 + the town's recorded SFX_DATA) and mux them onto the frames -> mp4 with audio.
# usage: sfx_preview.py [base url] [map] [out dir]
import sys,os,json,wave,struct,subprocess
from playwright.sync_api import sync_playwright
B=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8931/index.html';MP=sys.argv[2] if len(sys.argv)>2 else 'field00';O=sys.argv[3] if len(sys.argv)>3 else '/tmp/sfx_prev'
os.makedirs(O+'/f',exist_ok=True);FPS=30;N=FPS*14
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ.get('PW_CHROME') or None);pg=b.new_page(viewport={'width':1280,'height':720});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(B);pg.wait_for_function('window.__world&&window.__game&&window.SFX2',timeout=30000);pg.wait_for_timeout(1200)
    pg.evaluate("(mp)=>{const W=__world;W.setManual(true);W.go(mp,'default');}",MP);pg.evaluate("()=>{for(let i=0;i<30&&__world.trans;i++)__world.advance(.5)}")
    pg.evaluate('''()=>{const W=__world,M=W.S.map;window.__LOG=[];const T0=W.S.t;const lg=(k,v)=>__LOG.push([k,W.S.t-T0,v==null?1:v]);
      SFX2.play=(k,v)=>lg(k,v);const G=__game;if(G.SFX)G.SFX.play=(k,v)=>lg(k,v);
      let bx=Math.floor(M.w/2),by=Math.floor(M.h/2);for(let r=0;r<12&&M.solidG[by*M.w+bx];r++)bx++;W.setHeroTile(bx,by,'right');const h=W.hero;
      let k=0;for(const m of W.mobs){if(m.dead||m.D.champion)continue;if(k>=4){m.dead=true;continue;}const a=k*1.6;m.x=h.x+Math.cos(a)*50;m.y=h.y+Math.sin(a)*36;m.home=[m.x,m.y];k++;}}''')
    for i in range(N):
        pg.evaluate('''(i)=>{const W=__world,h=W.hero;h.hp=Math.max(h.hp,20);let best=null,bd=1e9;for(const m of W.mobs){if(m.dead)continue;const d=Math.hypot(m.x-h.x,m.y-h.y);if(d<bd){bd=d;best=m;}}
          if(best){const dx=best.x-h.x,dy=best.y-h.y;h.face=Math.abs(dx)>Math.abs(dy)?(dx>0?'right':'left'):(dy>0?'down':'up');}
          if(i%40===20)W.tap('KeyK');else if(i%9===0&&bd<40)W.tap('KeyJ');
          if(best&&bd>34){W.key('ArrowRight',best.x>h.x+4);W.key('ArrowLeft',best.x<h.x-4);W.key('ArrowDown',best.y>h.y+4);W.key('ArrowUp',best.y<h.y-4);}else['ArrowRight','ArrowLeft','ArrowDown','ArrowUp'].forEach(c=>W.key(c,false));
          W.advance(1/30);}''',i)
        pg.screenshot(path=f'{O}/f/{i:04d}.png')
    log=pg.evaluate('()=>__LOG')
    pcm=pg.evaluate('''async([log,secs])=>{const sr=44100,syn=log.filter(e=>SFX2.has(e[0])),a=await SFX2.render(syn,secs),out=Float32Array.from(a);
      const oc=new OfflineAudioContext(1,sr*secs,sr),dec={};for(const e of log){if(SFX2.has(e[0])||dec[e[0]]||typeof SFX_DATA==='undefined'||!SFX_DATA[e[0]])continue;
        const ab=await (await fetch(SFX_DATA[e[0]])).arrayBuffer();dec[e[0]]=await oc.decodeAudioData(ab);}
      for(const e of log){const bf=dec[e[0]];if(!bf)continue;const s=bf.getChannelData(0),o=Math.floor(e[1]*sr);for(let i=0;i<s.length&&o+i<out.length;i++)out[o+i]+=s[i]*e[2]*.6;}
      return Array.from(out);}''',[log,N/FPS])
    print(json.dumps({'sounds':sorted({e[0] for e in log}),'calls':len(log),'errors':errs[:3]},ensure_ascii=False));b.close()
with wave.open(f'{O}/a.wav','wb') as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(44100);w.writeframes(b''.join(struct.pack('<h',max(-32767,min(32767,int(v*32767)))) for v in pcm))
subprocess.run(['ffmpeg','-loglevel','error','-y','-framerate',str(FPS),'-i',f'{O}/f/%04d.png','-i',f'{O}/a.wav','-vf','scale=960:-2','-c:v','libx264','-pix_fmt','yuv420p','-crf','22','-c:a','aac','-b:a','128k','-shortest',f'{O}/sfx_preview.mp4'],check=True)
