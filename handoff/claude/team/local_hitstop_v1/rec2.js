const {chromium}=require('playwright');(async()=>{const port=process.argv[2];const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:1280,height:720}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(`http://localhost:${port}/test128/index.html?nosave&worldreset&noscene&go=field_felt`);await p.waitForFunction('window.__world&&__world.map&&!__world.trans',{timeout:30000});
const r=await p.evaluate(()=>{const W=__world,h=W.hero,S=W.S;W.setManual(true);for(const m of S.mobs)m.dead=true;W.advance(.1);const out=[];
 for(const f8 of ['up_right','upright','ne','up-right','up_left','nw']){try{h.face='up';h.f8=f8;W.tap('KeyJ');W.advance(1/60);W.advance(1/60);W.advance(1/60);W.advance(1/60);h.atk={t:.05,hit:new Set(),i:3};h.moving=true;h.run=true;W.advance(0);out.push(f8+':ok');}catch(e){out.push(f8+':'+e.message);}}
 return out;});
console.log(port,r.join(' '),'pageerrs',errs.length,errs[0]||'');await b.close();})();
