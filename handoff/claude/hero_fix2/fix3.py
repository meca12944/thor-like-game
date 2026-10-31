# hero-fix2 3차 (크레딧 0): hero_check 빨간 칸·4번방 지적 정리
#  1) 회피대시 틱 [3,3,5,3,3,3] (마지막 2틱 → 3틱)
#  2) 그림에 구워진 빛·먼지 지우기 (흰·청백 빛줄기, 발밑 흰 먼지) — 얼굴(살색 3px 안)은 그대로
#  3) 늘어난 다리 줄이기: 걷기보다 얼굴이 8px 넘게 높은 장 → 허리 아래만 세로로 줄여 5px 차이로
#  4) 발 땅에 맞추기: 맞기·공격·대시 첫 장의 뜬/묻힌 발
#  5) 달리기 머리 오르내림 4~6px: 공중 장만 1~2px 올림
import sys,json;sys.path.insert(0,sys.argv[2] if len(sys.argv)>2 else '.')
from h8lib import load,save
from fxclean import clean,skin
from PIL import Image
R=sys.argv[1];s,j,k,H=load(R);base=H['sheets'].index('anim/hero_grok_0.webp')
SP=f'{R}/test128/assets/anim/hero_grok_0.webp';S=Image.open(SP).convert('RGBA');log=[]
C=H['cells'][base]
def get(c): x,y,w,h,ax,ay=C[c];return S.crop((x,y,x+w,y+h)),ax,ay
def put(c,im): x,y,w,h,ax,ay=C[c];S.paste(Image.new('RGBA',(w,h)),(x,y));S.paste(im,(x,y))
def bbox(im): return im.split()[3].point(lambda v:255 if v>40 else 0).getbbox()
def newcell(c,dax=0,day=0):   # 같은 그림을 다른 기준점으로 (다른 동작과 함께 쓰는 칸은 건드리지 않음)
    e=list(C[c]);e[4]+=dax;e[5]+=day;C.append(e);return len(C)-1
used={}
for n,L in H['anims'].items():
    for f in L:
        if f[0]==base: used.setdefault(f[1],set()).add(n)
mine=lambda n:H['anims'][n] and H['anims'][n][0][0]==base
# 1) 대시 틱
for n in H['anims']:
    if mine(n) and n.startswith('dash_') and len(H['anims'][n])==6:
        for f,t in zip(H['anims'][n],[3,3,5,3,3,3]): f[2]=t
        log.append(('틱',n,[3,3,5,3,3,3]))
# 2) 빛·먼지
for c in sorted(used):
    im,ax,ay=get(c);im2,nrm=clean(im)
    if nrm>=15: put(c,im2);log.append(('빛·먼지',c,nrm))
# 2b) 대시 첫 장 발밑 회색 먼지 (발밑 20줄의 회색만)
for n in H['anims']:
    if not (mine(n) and n.startswith('dash_')): continue
    c=H['anims'][n][0][1];im,ax,ay=get(c);px=im.load();W,Hh=im.size;m=0
    for y in range(max(0,ay-20),min(Hh,ay+1)):
        for x in range(W):
            r,g,b,a=px[x,y]
            if a>40 and (r+g+b)/3>55 and abs(r-b)<22 and abs(r-g)<22: px[x,y]=(0,0,0,0);m+=1
    if m: put(c,clean(im)[0]);log.append(('발밑 먼지',n,c,m))
# 3) 늘어난 다리
def facetop(c):
    im,ax,ay=get(c);px=im.load();W,Hh=im.size;ys=[y for y in range(Hh) for x in range(W) if skin(px[x,y])]
    return (min(ys)-ay) if len(ys)>=8 else None
ref={}
for d in ['down','dr','right']:
    v=[facetop(f[1]) for f in H['anims']['walk_'+d]];ref[d]=min(x for x in v if x is not None)
for n in list(H['anims']):
    if not mine(n) or n.startswith(('walk','run','idle')): continue
    d=n.split('_',1)[1] if '_' in n else ''
    if d not in ref: continue
    for f in H['anims'][n]:
        c=f[1];t=facetop(c)
        if t is None or t>=ref[d]-8: continue
        im,ax,ay=get(c);delta=(ref[d]-t)-5;belt=ay+t+58;w,h=im.size
        top=im.crop((0,0,w,belt));low=im.crop((0,belt,w,ay+1));lh=low.height-delta
        low2=low.resize((w,lh),Image.NEAREST)
        out=Image.new('RGBA',(w,h));out.paste(top,(0,delta));out.paste(low2,(0,belt+delta),low2)
        if h>ay+1: out.paste(im.crop((0,ay+1,w,h)),(0,ay+1))
        put(c,out);log.append(('다리 줄임',n,c,delta))
# 3b) 서기 장 땅에 (걷기와 같이 쓰는 칸이면 서기용 칸을 따로 만들어 공격·맞기 끝 장도 같이 씀)
for d in ['down','dr','right','up','n']:
    n='idle_'+d
    if n not in H['anims'] or not mine(n): continue
    c=H['anims'][n][0][1];b=bbox(get(c)[0]);bot=b[3]-C[c][5]
    if bot:
        nc=newcell(c,0,bot)
        for m,L in H['anims'].items():
            if m==n or m.startswith(('hit','hurt')):
                for f in L:
                    if f[0]==base and f[1]==c: f[1]=nc
        log.append(('서기 땅',n,c,'→',nc,-bot))
# 4) 발 땅에 맞추기 (bot = 발 아래 끝 - 기준점, 0이 땅)
FEET={'hurt_up':None,'hit1_up':None}
for n in H['anims']:
    if not mine(n): continue
    if not (n.startswith(('hurt','hit')) or n.startswith('dash_')): continue
    L=H['anims'][n]
    for i,f in enumerate(L):
        if n.startswith('dash_') and i!=0: continue   # 대시는 첫 장(땅 차기)만
        im,ax,ay=get(f[1]);b=bbox(im);bot=b[3]-ay
        if abs(bot)>=2:
            nc=newcell(f[1],0,bot) if len(used.get(f[1],()))>1 else None
            if nc is None: C[f[1]][5]+=bot
            else: f[1]=nc
            log.append(('발',n,f[1],-bot))
# 6) 4번방 2차: 걷기는 한 발이 늘 땅(뜬 장 0으로), 달리기 공중은 4px 이하 (같이 쓰는 칸이면 새 칸)
for n in list(H['anims']):
    if not mine(n) or not n.startswith(('walk_','run_')): continue
    L=H['anims'][n]
    T=[bbox(get(f[1])[0])[1]-C[f[1]][5] for f in L];B=[bbox(get(f[1])[0])[3]-C[f[1]][5] for f in L]
    if n.startswith('walk_'): ds=[max(0,-b) for b in B]   # 걷기: 한 발이 늘 땅
    else:   # 달리기: 머리 오르내림 4~6 안에서 가장 덜 뜨게 (땅 밑 금지)
        best=None
        for Wn in range(min(T)-20,max(T)+20):
            d2=[min(Wn+6-t,-b) for t,b in zip(T,B)]
            if any(d<Wn-t for d,t in zip(d2,T)): continue
            tt=[t+d for t,d in zip(T,d2)]
            fl=max(-(b+d) for b,d in zip(B,d2));key=(max(tt)-min(tt)<4,fl)
            if best is None or key<best[0]: best=(key,d2)
        ds=best[1];tt=[t+d for t,d in zip(T,ds)];rng=max(tt)-min(tt)
        if rng<4:   # 너무 평평 → 발이 가장 높이 뜬 장 2개를 더 올림 (공중 = 몸이 뜸)
            for i in sorted(range(len(L)),key=lambda i:B[i]+ds[i])[:2]: ds[i]-=4-rng
    for f,d in zip(L,ds):
        if not d: continue
        if len(used.get(f[1],()))>1: f[1]=newcell(f[1],0,-d)
        else: C[f[1]][5]-=d
    log.append(('발 높이',n,'내림',ds))
_sl={'x':0,'y':None,'rh':0}
def slot(w,h):   # 시트 아래에 새 줄을 붙여 자리 주기
    global S
    if _sl['y'] is None: _sl['y']=S.height+2
    if _sl['x']+w>S.width: _sl['x']=0;_sl['y']+=_sl['rh']+2;_sl['rh']=0
    need=_sl['y']+h+2
    if need>S.height: T=Image.new('RGBA',(S.width,need));T.paste(S,(0,0));S=T
    x,y=_sl['x'],_sl['y'];_sl['x']+=w+2;_sl['rh']=max(_sl['rh'],h);return x,y
# 7) 4번방 3차: 그래도 4px 넘게 뜬 달리기 장(↗ 다리 접은 공중 장) → 허리 아래를 세로로 늘여 발을 −4px로 (머리는 그대로)
for n in list(H['anims']):
    if not mine(n) or not n.startswith('run_'): continue
    for f in H['anims'][n]:
        im,ax,ay=get(f[1]);b=bbox(im);bot=b[3]-C[f[1]][5]
        if bot>=-4: continue
        dd=-4-bot;w,h=im.size;belt=b[1]+int((b[3]-b[1])*.52);h2=h+dd
        low=im.crop((0,belt,w,b[3])).resize((w,b[3]-belt+dd),Image.NEAREST);o=Image.new('RGBA',(w,h2));o.paste(im.crop((0,0,w,belt)),(0,0));o.paste(low,(0,belt),low)
        x,y=slot(w,h2);S.paste(o,(x,y));e=list(C[f[1]]);C.append([x,y,w,h2,e[4],e[5]]);f[1]=len(C)-1   # 늘인 그림은 칸이 커져서 시트 아래 새 자리에
        log.append(('다리 늘임',n,f[1],dd))
S.save(SP,lossless=True);H['_fix3_note']='10-25 회의 2차 3단계: 대시 [3,3,5,3,3,3]·구운 빛 지움·늘어난 다리 줄임·발 땅·달리기 머리 4~6 (handoff/claude/hero_fix2/fix3.py)'
save(R,s,j,k,H)
for l in log: print(*l)
