# 2단계(크레딧 0): 새 주인공 아틀라스 틱만 다시 나누기 (설계표 DESIGN_ko.md 1절) — 보이는 장 최소 3틱, 치는/높은 칸을 코드 박자에
import sys,json
REPO=sys.argv[1] if len(sys.argv)>1 else '.'
T={'dash':[3,3,6,3,3,2],'jump':[4,4,4,10,6,6,8],'rjump':[4,4,14,6,6,8],'hurt3':[4,10,6]}
p=f'{REPO}/test128/index.html';s=open(p,encoding='utf-8').read();i=s.index('/*H8*/');j=s.index('{',i);d=0
for k in range(j,len(s)):
    if s[k]=='{':d+=1
    elif s[k]=='}':
        d-=1
        if d==0: break
H=json.loads(s[j:k+1]);base=H['sheets'].index('anim/hero_grok_0.webp');ch=[]
for n,L in H['anims'].items():
    if not L or L[0][0]<base: continue   # 새 주인공 칸만
    kind=n.split('_')[0];new=None
    if kind=='dash' and len(L)==6: new=T['dash']
    elif kind=='jump' and len(L)==7: new=T['jump']
    elif kind=='rjump' and len(L)==6: new=T['rjump']
    elif kind in('hurt','hurtys') and len(L)==3: new=T['hurt3']
    elif kind in('hurt','hurtys') and len(L)==1: new=[20]
    if new:
        for e,t in zip(L,new): e[2]=t
        ch.append(n)
H['_fix2_note']='10-25 회의 2차: 틱 다시 나누기(handoff/claude/hero_fix2/DESIGN_ko.md) — 대시 20·점프 42·맞기 20틱, 보이는 장 최소 3틱'
s=s[:j]+json.dumps(H,ensure_ascii=False,separators=(',',':'))+s[k+1:];open(p,'w',encoding='utf-8').write(s);print('바꾼 동작',ch)
