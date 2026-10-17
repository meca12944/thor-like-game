"""Hit-3 tune (after patch_hit3_run.py): arc 100 deg for every weapon, reach 1.15x hit 1, keep the longer swing timing/follow-through.
usage: python3 patch_hit3_tune.py <kind> <in> <out>   kind = src|herojson|index|world|controls|animation|worldmd|testrun"""
import json,sys
def rep(t,a,b):
    if a not in t:
        assert b in t,('missing',a[:90]);return t
    return t.replace(a,b)
def anim_obj(d):
    for w in d['weapons'].values():
        h1,h3=w['combo'][0],w['combo'][2];h3['range']=round(h1['range']*1.15);h3['arc']=100
    if '_weapons_doc' not in d: return d
    d['_weapons_doc']=rep(d['_weapons_doc'],"hit3 = big finishing slash: arc 180-200 deg (dagger 180 / twin 185 / greatsword 200 / others 190, still forward-facing; only the 마왕 title hit 3 spins), reach +20% over the old hit 3,",
                          "hit3 = finishing slash: arc 100 deg for every weapon (narrow, deep forward cut; only the 마왕 title hit 3 spins), reach 1.15x hit 1,")
    d['_weapons_doc']=rep(d['_weapons_doc'],"(150 slashes / 130 overheads)","(150 for hits 1-2 / 100 for hit 3)")
    return d
def index(t):
    k=t.index('const ANIM=')+len('const ANIM=');e=t.index('\n',k);line=t[k:e];d=json.loads(line[:-1])
    return t[:k]+json.dumps(anim_obj(d),separators=(',',':'),ensure_ascii=False)+';'+t[e:]
def world(t):
    return rep(t,"arc3: 190, r3: 1.3 }; // hit 3 = big finishing slash: 190 deg forward, reach x1.3 (old 1.08 +20%)",
                 "arc3: 100, r3: 1.15 }; // hit 3 = finishing slash: 100 deg forward, reach x1.15 (longer swing timing ATK3 kept)")
def controls(t):
    t=rep(t,"3타 **크게 휘두르는 마무리 베기** — 정면 190°(단검 180 · 쌍검 185 · 대검 200), 사거리 1타의 약 1.3배, 판정 구간과 마무리 동작이 더 김)",
            "3타 **마무리 베기** — 정면 100°(모든 무기), 사거리 1타의 1.15배, 판정 구간과 마무리 동작이 더 김)")
    t=rep(t,"; 3타 한손검 2.3타일 · 대검 3.0 · 창 3.4)","; 3타 한손검 2.1타일 · 대검 2.6 · 창 3.0)")
    t=rep(t,"3타는 **크게 휘두르는 마무리 베기** — 정면 180~200°(뒤로 돌지 않음), 사거리 +20%(1타의 약 1.3배), 판정 구간 +60%,",
            "3타는 **마무리 베기** — 정면 100°의 좁고 깊은 베기(모든 무기 공통), 사거리 1타의 1.15배, 판정 구간 +60%,")
    return t
def animation(t):
    t=rep(t,"3타 `atk3` 크게 휘두르는 마무리 베기","3타 `atk3` 마무리 베기")
    return rep(t,"3타는 180~200° · 사거리 +20% · 긴 판정 구간","3타는 100° · 사거리 1타의 1.15배 · 긴 판정 구간")
def worldmd(t):
    return rep(t,"3타 = 크게 휘두르는 마무리 베기: 190° · 반경 ×1.3","3타 = 마무리 베기: 100° · 반경 ×1.15")
def testrun(t):
    t=rep(t,"c.arc>=180&&c.arc<=200&&g.swingRange(c)/g.swingRange(a)>1.25","c.arc===100&&Math.abs(g.swingRange(c)/g.swingRange(a)-1.15)<.02")
    t=rep(t,"# hit 3 = big finisher for every weapon: 180-200 deg, reach ~1.3x hit 1 (old 1.08x +20%),","# hit 3 = finishing slash for every weapon: 100 deg, reach 1.15x hit 1,")
    t=rep(t,"g.SWINGS.slice(0,3).every(s=>g.swingRange(s)>=96&&(s.arc||g.FEEL.arcDeg)>=130)","g.SWINGS.slice(0,3).every((s,i)=>g.swingRange(s)>=96&&(s.arc||g.FEEL.arcDeg)>=(i<2?130:100))")
    return rep(t,"__world.SWING.arc3>=180&&__world.SWING.arc3<=200&&__world.swingR(2)/__world.swingR(0)>1.25","__world.SWING.arc3===100&&Math.abs(__world.swingR(2)/__world.swingR(0)-1.15)<.01")
kind,src,dst=sys.argv[1:4];s=open(src).read()
if kind=='src':o=json.dumps(anim_obj(json.loads(s)),indent=1,ensure_ascii=False)
elif kind=='herojson':o=json.dumps(anim_obj(json.loads(s)),separators=(',',':'),ensure_ascii=False)+('\n' if s.endswith('\n') else '')
else:o={'index':index,'world':world,'controls':controls,'animation':animation,'worldmd':worldmd,'testrun':testrun}[kind](s)
open(dst,'w').write(o)
