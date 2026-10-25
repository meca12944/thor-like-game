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
# 5) 달리기 머리 오르내림
for n in ['run_right','run_n','run_down','run_dr','run_up']:
    L=H['anims'][n]
    def tops(): return [bbox(get(f[1])[0])[1]-C[f[1]][5] for f in L]
    T=tops();bots=[bbox(get(f[1])[0])[3]-C[f[1]][5] for f in L];rng=max(T)-min(T)
    if 4<=rng<=6: continue
    if rng>6:   # 가장 높은 장은 내리고 가장 낮은 장은 올려 6으로
        hi=T.index(min(T));lo=T.index(max(T));over=rng-6;dn=min(over,max(0,-bots[hi]));C[L[hi][1]][5]-=dn;up=over-dn;C[L[lo][1]][5]+=up
        log.append(('머리',n,'내림',L[hi][1],dn,'올림',L[lo][1],up))
    else:       # 발이 가장 높이 뜬 장(공중) 들을 1px씩 올려 4로
        need=4-rng;air=sorted(range(len(L)),key=lambda i:bots[i])[:2]
        for i in air: C[L[i][1]][5]+=need
        log.append(('머리',n,'공중 올림',[L[i][1] for i in air],need))
S.save(SP,lossless=True);H['_fix3_note']='10-25 회의 2차 3단계: 대시 [3,3,5,3,3,3]·구운 빛 지움·늘어난 다리 줄임·발 땅·달리기 머리 4~6 (handoff/claude/hero_fix2/fix3.py)'
save(R,s,j,k,H)
for l in log: print(*l)
