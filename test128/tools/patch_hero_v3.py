# patch_hero_v3.py — wire hero v3 (assets/anim/hero8.json from hero_v3_atlas.py) into index128.html (the hero8 test128 build).
# Re-run safe for the data block; code patches are applied from the pre-v3 source (_backup_hero8_pre_v3/index128.html) every time.
import re
SRC='/workspace/town-demo/_backup_hero8_pre_v3/index128.html'; P='/workspace/town-demo/index128.html'
s=open(SRC,encoding='utf-8').read(); H8=open('/workspace/town-demo/assets/anim/hero8.json').read()
s=re.sub(r'/\*H8\*/.*?/\*/H8\*/',lambda m:"/*H8*/const H8=new URLSearchParams(location.search).get('hero8')==='0'?null:"+H8+";/*/H8*/",s,count=1,flags=re.S)
def rep(old,new,cnt=1):
    global s
    n=s.count(old); assert n==cnt,(n,old[:90]); s=s.replace(old,new)
# combo timing = combo3_arc.json (per hit: dur / hit tick / cancel tick / hit-stop), every weapon
rep("if(H8)L.forEach((h,i)=>{const f=[8/17,8/17,20/41][i];if(f)for(const k of ['dur','a0','a1','cancel'])h[k]*=f;});",
    "if(H8&&H8.combo)L.forEach((h,i)=>{const C=H8.combo[i];if(!C)return;h.dur=C.dur/60;h.a0=Math.max(0,C.hit-2)/60;h.a1=(C.hit+2)/60;h.cancel=C.cancel/60;h.v3c=C.cancel/60;h.stop=C.stop;}); /* hero v3: combo3_arc timing 20/26/39 ticks, hits 6/8/13 in-hit, cancel windows */\n else if(H8)L.forEach((h,i)=>{const f=[8/17,8/17,20/41][i];if(f)for(const k of ['dur','a0','a1','cancel'])h[k]*=f;});")
# chain inside the cancel window (buffered attack press -> next hit at the cancel tick)
rep("if(a.t>=s.dur){hero.atk=null;hero.z=0;","if(s.v3c!==undefined&&!s.special&&hero.buffered&&a.i<2&&a.t>=s.v3c){startSwing(a.i+1);}else if(a.t>=s.dur){hero.atk=null;hero.z=0;")
# 4-way sprite: diagonals -> nearest of 4 (hero.face)
rep("function sdir(){const f=face8();","function sdir(){if(H8&&H8.v3)return hero.face||'down';const f=face8();")
# cell picker: per-frame ticks, fx layers, cast variant S1-S3 by skill slot
rep("function castFrame(sk,d){ // cast clip:","function h8castKey(d){const sl=hero.sk?hero.sk.slot:hero.lastSlot;if(hero.sk)hero.lastSlot=sl;return H8.v3?'s'+(((Math.max(0,sl??0))%3)+1)+'_'+d:d;}\nfunction castFrame(sk,d){ // cast clip:")
rep("const M=H8.cast[d],F=SKFX[sk.id]","const M=H8.cast[h8castKey(d)],F=SKFX[sk.id]")
rep("const A=k=>H8.anims[k+'_'+d];let e=null,bob=0;","const A=k=>H8.anims[(H8.v3&&k==='cast'?'cast_'+h8castKey(d).split('_')[0]:k)+'_'+d];let e=null,bob=0;")
rep("const L=A(nm);e=h8seq(L,Math.min(.999,h.atk.t/s.dur)*h8tot(L));}","const L=A(nm);e=h8seq(L,H8.v3&&!s.special?h.atk.t*60:Math.min(.999,h.atk.t/s.dur)*h8tot(L));}")
rep("else{e=A('idle')[0];const q=","else if(H8.v3){const L=A('idle');e=h8seq(L,(h.idleT||0)%h8tot(L));}\n else{e=A('idle')[0];const q=")
rep("if(!e)return null;const c=H8.cells[e[0]][e[1]];return {c,dx:0,dy:0,fl,sy:1,h8:e[0],bob};}",
    "if(!e)return null;const c=H8.cells[e[0]][e[1]];const o={c,dx:0,dy:0,fl,sy:1,h8:e[0],bob};\n if(H8.v3&&e.length>3){if(/cast/.test(String(h.sk||h.castRec?'cast':''))&&e.length>=7){if(e[3]>=0)o.fxb=[e[3],e[4]];if(e[5]>=0)o.fxf=[e[5],e[6]];}else if(e.length>=5&&e[3]>=0)o.fxf=[e[3],e[4]];}\n return o;}\nfunction h8fx(r,fl){const h=hero;blitHero({c:H8.cells[r[0]][r[1]],dx:0,dy:0,fl,h8:r[0]},h.x,h.y-(h.z||0));}")
rep("const o=heroCell();if(o){blitHero(o,h.x,h.y-(h.z||0));","const o=heroCell();if(o){if(o.fxb)h8fx(o.fxb,o.fl);blitHero(o,h.x,h.y-(h.z||0));if(o.fxf)h8fx(o.fxf,o.fl);")
rep("castRec={t:0,f0:H8.cast[d].rs};}","castRec={t:0,f0:H8.cast[H8.v3?h8castKey(d):d].rs};}")
rep("castRec={t:0,f0:H8.cast[d].e};}","castRec={t:0,f0:H8.cast[H8.v3?h8castKey(d):d].e};}")
rep("H8.cast.right.n;","(H8.v3?H8.cast['s1_right']:H8.cast.right).n;")
open(P,'w',encoding='utf-8').write(s); print('patched',len(s))
