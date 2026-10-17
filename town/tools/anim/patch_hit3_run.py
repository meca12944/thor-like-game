"""Hit-3 'big finisher' + run 1.9x patch. Pure text/json transform so it can be applied to
HEAD blobs (for a clean commit) and to working copies that hold other workers' WIP.
usage: python3 patch_hit3_run.py <kind> <in> <out>   kind = src|herojson|template|world|index"""
import json,sys,re
ARC3={'dagger':180,'twin':185,'greatsword':200}   # others 190 (forward, never a full spin)
HIT3_DOC=(" hit3 = big finishing slash: arc 180-200 deg (dagger 180 / twin 185 / greatsword 200 / others 190, still forward-facing;"
 " only the 마왕 title hit 3 spins), reach +20% over the old hit 3, active window +60%, longer follow-through;"
 " 'strike' = [anim fraction at a0, at a1] so the swing frames line up with the active window (windup before, follow-through after).")
def weapons(W):
    for t,w in W.items():
        h=w['combo'][2]
        if h.get('strike'): continue           # idempotent
        old_act=h['a1']-h['a0'];ext=round(old_act*.6)
        h['range']=round(h['range']*1.2);h['arc']=ARC3.get(t,190)
        h['a1']+=ext;h['cancel']+=ext+2;h['dur']+=ext+5;h['strike']=[0.3,0.6]
    return W
def anim_obj(d):
    d['weapons']=weapons(d['weapons'])
    if '_weapons_doc' in d and 'big finishing slash' not in d['_weapons_doc']:d['_weapons_doc']+=HIT3_DOC
    return d
def rep(t,a,b,count=1):
    if b in t: return t                                      # already applied (idempotent)
    assert t.count(a)>=1,('missing',a[:80]);return t.replace(a,b,count)
def template(t):
    t=rep(t,"runMul:1.72,runStartMul:2.3,runStartTicks:10,runSkidTicks:12,dblTap:.25, // double-tap a direction -> dash start + run while held (1.72x walk)",
             "runMul:1.9,runStride:.55,runStartMul:2.3,runStartTicks:10,runSkidTicks:12,dblTap:.25, // double-tap a direction -> dash start + run while held (1.9x walk; runStride = run-cycle phase per walk-distance unit, 8 frames = ~208 world px, no foot sliding)")
    t=rep(t,"*(hero.run?.62:1)","*(hero.run?FEEL.runStride:1)")
    t=rep(t," if(h.atk)tick=h.atk.t/h.atk.s.dur*A.ticks;                 // anim stretched to the weapon's swing timing",
             " if(h.atk)tick=atkAnimP(h.atk)*A.ticks;                     // anim stretched to the weapon's swing timing (hit 3: strike frames pinned to the active window)")
    t=rep(t,"function heroCell(){",
             "function atkAnimP(a){const s=a.s,t=a.t,k=s.strike;if(!k||!(s.a1>s.a0))return t/s.dur; // windup -> [0,k0], active -> [k0,k1], follow-through -> [k1,1]\n"
             " if(t<s.a0)return k[0]*t/Math.max(1e-6,s.a0);if(t<s.a1)return k[0]+(k[1]-k[0])*(t-s.a0)/(s.a1-s.a0);return k[1]+(1-k[1])*Math.min(1,(t-s.a1)/Math.max(1e-6,s.dur-s.a1));}\n"
             "function heroCell(){")
    t=rep(t,"const p=(a.t-s.a0*0.5)/(s.a1-s.a0*0.5+.06);if(p<0||p>1.2)return;const fade=(p>1?1-(p-1)/.2:1)*(dv[1]?1:.6);",
             "const tl=s.strike?.4:.2; // hit 3: longer follow-through fade of the big trail\n const p=(a.t-s.a0*0.5)/(s.a1-s.a0*0.5+.06);if(p<0||p>1+tl)return;const fade=(p>1?1-(p-1)/tl:1)*(dv[1]?1:.6);")
    return t
def world(t):
    t=rep(t,"const RUN = { mul: 1.72, startMul: 2.3, startT: 0.17, skidT: 0.2, dblTap: 0.25 }; // run: 1.72x walk, no MP/stamina",
             "const RUN = { mul: 1.9, startMul: 2.3, startT: 0.17, skidT: 0.2, dblTap: 0.25, cadence: .9 }; // run: 1.9x walk, no MP/stamina; anim cadence = speed x .9 (no foot sliding)")
    t=rep(t,"const SWING = { range: 29, arc: 150, arc3: 130 };",
             "const SWING = { range: 29, arc: 150, arc3: 190, r3: 1.3 }; // hit 3 = big finishing slash: 190 deg forward, reach x1.3 (old 1.08 +20%)")
    t=rep(t,"const ATK = { dur: 0.26, a0: 0.05, a1: 0.16, chain: 0.32, reach: 15, r: 13 };",
             "const ATK = { dur: 0.26, a0: 0.05, a1: 0.16, chain: 0.32, reach: 15, r: 13 };\n  const ATK3 = Object.assign({}, ATK, { dur: 0.38, a0: 0.07, a1: 0.24 }); // hit 3: longer active window + follow-through\n  const atkT = i => i === 2 ? ATK3 : ATK;")
    t=rep(t,"(!hero.atk || hero.atk.t > ATK.a1)","(!hero.atk || hero.atk.t > atkT(hero.atk.i).a1)")
    t=rep(t,"const lv = a.runSlash && a.t < ATK.a1 ? 20 + HERO_SPEED * RUN.mul * (1 - a.t / ATK.a1) : 20;",
             "const AT = atkT(a.i), lv = a.runSlash && a.t < AT.a1 ? 20 + HERO_SPEED * RUN.mul * (1 - a.t / AT.a1) : 20;")
    t=rep(t,"if (a.t >= ATK.a0 && a.t <= ATK.a1) { const R = swingR(a.i)","if (a.t >= AT.a0 && a.t <= AT.a1) { const R = swingR(a.i)")
    t=rep(t,"if (a.t >= ATK.dur) { hero.atk = null;","if (a.t >= AT.dur) { hero.atk = null;")
    t=rep(t,"hero.walkT += dt * (hero.run ? 1.6 : 1);","hero.walkT += dt * (hero.run ? rk * RUN.cadence : 1);")
    t=rep(t,"return SWING.range * k * (i === 2 ? 1.08 : 1); }","return SWING.range * k * (i === 2 ? SWING.r3 : 1); }")
    t=rep(t,"const a = hero.atk, p = a.t / ATK.dur, dv","const a = hero.atk, AT = atkT(a.i), p = a.t / AT.dur, dv")
    t=rep(t,"if (p > .85) return; const sweep","if (p > (a.i === 2 ? .9 : .85)) return; const sweep")
    t=rep(t,"a1 = a0 + sweep * 2 * half * Math.min(1, p / .6);","a1 = a0 + sweep * 2 * half * Math.min(1, p / (AT.a1 / AT.dur));")
    return t
def index(t):
    t=template(t);k=t.index('const ANIM=')+len('const ANIM=');e=t.index('\n',k);line=t[k:e]
    assert line.endswith(';');d=json.loads(line[:-1])
    return t[:k]+json.dumps(anim_obj(d),separators=(',',':'),ensure_ascii=False)+';'+t[e:]
def controls(t):
    t=rep(t,"**달리기**(걷기의 1.72배, 8프레임 달리기 동작, 발 디딜 때마다 흙먼지)","**달리기**(걷기의 1.9배, 8프레임 달리기 동작 — 보폭이 커져 발이 미끄러지지 않음(한 주기 ≈ 208px), 발 디딜 때마다 흙먼지)")
    t=rep(t,"3타 정면 내려베기). 판정 = 정면 **부채꼴**: 한손검 반경 1.8타일 · 150°(대검 2.3 · 창 2.6 · 단검 1.4타일, 3타 +8% · 130°)",
             "3타 **크게 휘두르는 마무리 베기** — 정면 190°(단검 180 · 쌍검 185 · 대검 200), 사거리 1타의 약 1.3배, 판정 구간과 마무리 동작이 더 김). 판정 = 정면 **부채꼴**: 한손검 반경 1.8타일 · 150°(대검 2.3 · 창 2.6 · 단검 1.4타일; 3타 한손검 2.3타일 · 대검 3.0 · 창 3.4)")
    t=rep(t,"3타는 강한 정면 내려베기이고 1 · 2타보다 후딜이 김.","3타는 **크게 휘두르는 마무리 베기** — 정면 180~200°(뒤로 돌지 않음), 사거리 +20%(1타의 약 1.3배), 판정 구간 +60%, 휘두름 뒤 마무리 동작(follow-through)이 길다. 휘두름 프레임은 판정 구간에 맞춰 재생(`strike` = [판정 시작, 끝]의 애니 비율). 화면 흔들림 추가 없음.")
    for a,b in [("(17 · 17 · 32)","(17 · 17 · 41)"),("(14 · 14 · 28)","(14 · 14 · 37)"),("(26 · 28 · 46)","(26 · 28 · 55)"),("(10 · 10 · 18)","(10 · 10 · 26)"),
                ("(18 · 20 · 36)","(18 · 20 · 45)"),("(20 · 20 · 34)","(20 · 20 · 43)"),("(12 · 12 · 28)","(12 · 12 · 37)"),("(16 · 17 · 32)","(16 · 17 · 41)"),
                ("(20 · 22 · 36)","(20 · 22 · 45)"),("(22 · 22 · 42)","(22 · 22 · 51)")]: t=rep(t,a,b)
    return t
def animation(t):
    t=rep(t,"2타 `atk2s` (atk1 프레임을 거꾸로 재생한 되베기, 궤적 반전), 3타 `atk3` 정면 내려베기 (전용 6프레임 × 3방향 새 그림). 모든 타격은 앞쪽 120°(`FEEL.arcDeg`) 안만 맞는다.",
             "2타 `atk2b` 전용 되베기 프레임(정면을 반대 방향으로 가로지름), 3타 `atk3` 크게 휘두르는 마무리 베기 (전용 6프레임 × 3방향). 1 · 2타는 앞쪽 150°(`FEEL.arcDeg`), 3타는 180~200° · 사거리 +20% · 긴 판정 구간 · 긴 마무리 동작. 3타 애니는 콤보 데이터의 `strike` 비율로 구간 재생(예비동작 → 판정 구간 동안 휘두름 프레임 → 남은 시간 동안 마무리 프레임).")
    t=rep(t,"| run (더블탭 달리기) | 8 × 3방향 | 4 | `run_right/down/up` — 팔 흔들기, 발 디딜 때 흙먼지.",
             "| run (더블탭 달리기) | 8 × 3방향 | 거리 연동 | `run_right/down/up` — 걷기 ×1.9, 재생은 이동 거리에 연동(`FEEL.runStride` .55 → 8프레임 한 주기 ≈ 208px, 발 미끄러짐 없음). 팔 흔들기, 발 디딜 때 흙먼지.")
    return t
def worldmd(t):
    t=rep(t,"걷기 ×1.72, 손 떼면","걷기 ×1.9 · 걸음 애니 속도도 이동 속도에 비례, 손 떼면")
    t=rep(t,"· 150°(3타 130°), 궤적이","· 150°(3타 = 크게 휘두르는 마무리 베기: 190° · 반경 ×1.3 · 판정 0.07~0.24초 · 전체 0.38초), 궤적이")
    return t
kind,src,dst=sys.argv[1:4];s=open(src).read()
if kind=='src':o=json.dumps(anim_obj(json.loads(s)),indent=1,ensure_ascii=False)
elif kind=='herojson':o=json.dumps(anim_obj(json.loads(s)),separators=(',',':'),ensure_ascii=False)+('\n' if s.endswith('\n') else '')
else:o={'template':template,'world':world,'index':index,'controls':controls,'animation':animation,'worldmd':worldmd}[kind](s)
open(dst,'w').write(o)
