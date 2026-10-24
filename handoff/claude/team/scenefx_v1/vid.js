const {chromium}=require('playwright');const fs=require('fs');(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:1280,height:720}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.addInitScript(()=>{const real=performance.now.bind(performance);window.__vt=0;window.__vtOn=false;performance.now=()=>window.__vtOn?window.__vt:real();});
await p.goto('http://localhost:8790/test128/index.html?nosave&worldreset&noscene&go=felt');await p.waitForFunction('window.__world&&__world.map',{timeout:30000});await p.waitForTimeout(2500);
await p.evaluate(()=>{__world.setManual(true);window.__vt=performance.now();window.__vtOn=true;});
const L=[['cg_felt_arrival',150],['cg_linette_meet',150],['cg_arachne_past',150],['cg_felix_scarf',130],['cg_arachne_end',170],['cg_memory_fire',150,'last']];fs.rmSync('v',{recursive:true,force:true});fs.mkdirSync('v');let n=0;
for(const [nm,F,extra] of L){await p.evaluate(nm=>{__world.S.dialog={text:'……',name:'',cg:'cg/'+nm+'.png',cgLast:false,narr:true,pitch:1,t:0,ch:0,pi:0};},nm);
 for(let f=0;f<F+(extra?90:0);f++){if(extra&&f===F)await p.evaluate(()=>{const d=__world.S.dialog;d.cgLast=true;d.t=0;});
  await p.evaluate(()=>{window.__vt+=1000/60;const d=__world.S.dialog;if(d)d.t=(d.t||0)+1/60;__world.advance(0);});
  await p.screenshot({path:`v/${String(n++).padStart(5,'0')}.png`,clip:{x:64,y:36,width:1152,height:648}});}
 await p.evaluate(()=>{__world.S.dialog=null;__world.S.cgL=null;});}
console.log(n,'errs',errs.slice(0,3));await b.close();})();
