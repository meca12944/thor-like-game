# 새 그록 주인공을 게임에 넣기 (팀장이 main 위에서 실행): python3 handoff/claude/hero_grok_v1/apply.py [저장소 경로]
# 1) test128/assets/anim/hero_grok_*.webp 복사 2) index.html /*H8*/ 에 새 시트·칸을 붙이고 동작(anims)을 새 주인공으로 바꿈
#    (cast_s* 는 마법진 효과 층은 그대로 두고 몸만 새 서기로, *_left 는 H8.left=0 이라 안 씀) 3) figH 144, 칼 grip 은 새 칸 것이 오면 넣고 지금은 비움
# 4) world.js: H128FIG 30→34, 그림 키 117 → ART_FIG(=H8.figH) (사장님 10-25 「크기는 중간」 키 144 art px, 필드 34px)
import sys,os,json,re,shutil,glob
R=os.path.dirname(os.path.abspath(__file__));REPO=os.path.abspath(sys.argv[1] if len(sys.argv)>1 else os.path.join(R,'../../..'))
NEW=json.load(open(f'{R}/hero_grok.json'))
for f in glob.glob(f'{R}/hero_grok_*.webp'): shutil.copy(f,f'{REPO}/test128/assets/anim/')
p=f'{REPO}/test128/index.html';html=open(p,encoding='utf-8').read()
i=html.index('/*H8*/');j=html.index('{',i);d=0
for k in range(j,len(html)):
    if html[k]=='{': d+=1
    elif html[k]=='}':
        d-=1
        if d==0: break
H=json.loads(html[j:k+1]);base=len(H['sheets'])
H['sheets']+=NEW['sheets'];H['cells']+=NEW['cells']
for n,v in NEW['anims'].items(): H['anims'][n]=[[e[0]+base,e[1],e[2]] for e in v]
idle=H['anims']['idle_right'][0]
for n,v in H['anims'].items():
    if n.startswith('cast_'): H['anims'][n]=[[idle[0],idle[1]]+e[2:] for e in v]   # 마법진(fx) 층은 그대로, 몸만 새 주인공
H['figH']=NEW['figH'];H['jumpPh'].update(NEW['jumpPh']);H['grip']={}
# 걷기 보폭(팀장 10-25 ②): 새 그림 옆 걷기·달리기 한 바퀴에 땅 디딘 발이 뒤로 간 거리(slip8 방식, 144) 걷기 120·달리기 143 art px → 한 바퀴 거리 = cyc×(32/84 | 46/119)×144/34 가 같게
# ↘는 같은 바퀴에 발이 덜 감(걷기 85·달리기 119) → 그 그림만 다리 빠르게(gaitMul = 옆/↘). 정면·뒷면은 제자리걸음(탑다운 흔함)이라 그대로
H['gait']={'walkCyc':74.4,'runCyc':87.3};H['gaitMul']={'walk_dr':1.41,'run_dr':1.2}
gp=f'{R}/grip.json'
if os.path.exists(gp):   # 검흔 담당 grip(새 칸 기준 "시트:칸") → 번호 옮김
    for kk,vv in json.load(open(gp)).items(): s,c=kk.split(':');H['grip'][f'{int(s)+base}:{c}']=vv
H['_grok_note']='10-25 새 그록 주인공(handoff/claude/hero_grok_v1): 걷기·달리기·서기 5방향, 회피대시·점프 4방향, 맞기 3방향, 사망·달리기 점프 옆, 공격 3방향(사이 장). 옛 칸은 시트 0~%d에 그대로(되돌리기 쉬움).'%(base-1)
html=html[:j]+json.dumps(H,ensure_ascii=False,separators=(',',':'))+html[k+1:];open(p,'w',encoding='utf-8').write(html)
w=f'{REPO}/test128/world.js';s=open(w,encoding='utf-8').read();n0=s.count('117')
s=s.replace('const H128FIG = 30;','const H128FIG = 34; const ART_FIG = (window.H8 && H8.figH) || 117;',1)
s=s.replace('H128FIG / 117','H128FIG / ART_FIG').replace('117 / H128FIG','ART_FIG / H128FIG').replace("- v[0] * K.lean * gy / 117 +","- v[0] * K.lean * gy / ART_FIG +")
open(w,'w',encoding='utf-8').write(s);print('H8 시트',base,'→',len(H['sheets']),'동작',len(NEW['anims']),'| world.js 117 남은 곳',s.count('117'),'(전',n0,')')
