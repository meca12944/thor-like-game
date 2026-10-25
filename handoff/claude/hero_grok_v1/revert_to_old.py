# 옛 주인공(hero8)으로 되돌리기 (10-25 긴급회의, 사장님 허락 뒤 팀장이 실행): python3 handoff/claude/hero_grok_v1/revert_to_old.py [저장소]
# - index.html /*H8*/: 동작 표(anims)·figH·gait·gaitMul·jumpPh·grip 을 #182 직전(7093980f) 것으로. 시트·칸은 그대로 둠(새 주인공 칸이 남아 다시 넣기 쉬움)
# - world.js: H128FIG 34→30, ART_FIG → 117 고정(리네트·NPC 크기도 원래대로). 평소 칼(carryGrip)은 새 주인공(figH≥140)일 때만 → 옛 주인공은 그림 칼 그대로
# - 연습장 그림(test128/sandbox/assets/hero_game.*)도 7093980f 것으로
import sys,os,json,subprocess
REPO=os.path.abspath(sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'../../..'));PRE='7093980f'
def H8span(s):
    i=s.index('/*H8*/');j=s.index('{',i);d=0
    for k in range(j,len(s)):
        if s[k]=='{':d+=1
        elif s[k]=='}':
            d-=1
            if d==0: return j,k+1
old=subprocess.run(['git','-C',REPO,'show',f'{PRE}:test128/index.html'],capture_output=True,text=True,check=True).stdout
oj,ok=H8span(old);O=json.loads(old[oj:ok])
p=f'{REPO}/test128/index.html';html=open(p,encoding='utf-8').read();j,k=H8span(html);H=json.loads(html[j:k])
for key in ('anims','figH','gait','gaitMul','jumpPh','grip'):
    if key in O: H[key]=O[key]
    else: H.pop(key,None)
H['_revert_note']='10-25 긴급회의: 옛 주인공으로 되돌림(동작 표만). 새 주인공 칸은 시트 뒤쪽에 남음 → handoff/claude/hero_grok_v1/apply.py 로 다시'
html=html[:j]+json.dumps(H,ensure_ascii=False,separators=(',',':'))+html[k:];open(p,'w',encoding='utf-8').write(html)
w=f'{REPO}/test128/world.js';s=open(w,encoding='utf-8').read()
s=s.replace('const H128FIG = 34; const ART_FIG = (window.H8 && H8.figH) || 117;','const H128FIG = 30; const ART_FIG = 117;',1)
s=s.replace("const g = H.grip[c.h8 + ':' + c.ci]; if (!g) return null; const fl = !!c.fl, d =","if (!(H.figH >= 140)) return null; const g = H.grip[c.h8 + ':' + c.ci]; if (!g) return null; const fl = !!c.fl, d =",1)
open(w,'w',encoding='utf-8').write(s)
for f in ('test128/sandbox/assets/hero_game.json','test128/sandbox/assets/hero_game_0.webp'):
    data=subprocess.run(['git','-C',REPO,'show',f'{PRE}:{f}'],capture_output=True,check=True).stdout;open(f'{REPO}/{f}','wb').write(data)
print('되돌림 완료: figH',H.get('figH'),'| H128FIG 30, ART_FIG 117 |',('carryGrip 막음' if 'H.figH >= 140' in s else '⚠ carryGrip 못 찾음'))
