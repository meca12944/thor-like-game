# 인게임 = 최신만 (10-26): 옛 주인공 *_left 동작(옛 시트, H8.left=0 이라 안 쓰임) 지우고, 새 시트에서 어떤 동작도 안 쓰는 칸(지운 대각선 ↘↗·바뀐 장)은 그림을 비움(칸 번호는 그대로)
import sys;sys.path.insert(0,sys.argv[2])
from h8lib import load,save
from PIL import Image
R=sys.argv[1];s,j,k,H=load(R);base=H['sheets'].index('anim/hero_grok_0.webp');A=H['anims']
gone=[n for n,L in A.items() if L and any(f[0]!=base for f in L)]
for n in gone: del A[n]
used=set(f[1] for L in A.values() for f in L if f[0]==base)
SP=f'{R}/test128/assets/anim/hero_grok_0.webp';S=Image.open(SP).convert('RGBA');C=H['cells'][base];blank=[]
for i,c in enumerate(C):
    if i in used: continue
    x,y,w,h,ax,ay=c;S.paste(Image.new('RGBA',(w,h)),(x,y));blank.append(i)
S.save(SP,lossless=True)
H['_clean_note']='10-26 인게임 = 최신만: 옛 주인공 *_left 동작 %d개 지움, 새 시트 안 쓰는 칸 %d개 그림 비움(대각선 ↘↗ 포함)'%(len(gone),len(blank))
save(R,s,j,k,H);print('지운 동작',gone);print('비운 칸',len(blank),blank[:60])
