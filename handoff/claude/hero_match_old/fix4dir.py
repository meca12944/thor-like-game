# 4방향 그림 (사장님 10-26 「앞으로 대각선은 뺀다」): *_dr(↘) 지움, ↗(3/4 뒷면) walk/run/idle_up 지우고 *_n(곧은 뒷면) → *_up 로 이름 바꿈.
# dash_up·jump_up 은 곧은 뒷면 그림이 없어 3/4 뒷면 그대로 뒷면으로 씀(그록 곧은 뒷면 대기). H8.diag 플래그는 마을 공격 박자용이라 둠.
import sys;sys.path.insert(0,sys.argv[2])
from h8lib import load,save
R=sys.argv[1];s,j,k,H=load(R);A=H['anims'];gone=[]
for n in list(A):
    if n.endswith('_dr'): del A[n];gone.append(n)
for kind in ['walk','run','idle']:
    if kind+'_n' in A:
        if kind+'_up' in A: del A[kind+'_up'];gone.append(kind+'_up(↗)')
        A[kind+'_up']=A.pop(kind+'_n');gone.append(kind+'_n→_up')
gm=H.get('gaitMul') or {}
for n in list(gm):
    if n.endswith('_dr'): del gm[n];gone.append('gaitMul.'+n)
jp=H.get('jumpPh') or {}
for n in list(jp):
    if n.endswith('_dr'): del jp[n]
H['_4dir_note']='10-26 사장님 「앞으로 대각선은 뺀다」: 그림 4방향(정면 *_down · 옆 *_right(왼쪽 뒤집기) · 뒷면 *_up). 대각선 입력은 옆 그림(world.js h8Cell · index.html heroCell8). ↘/↗ 그림 지움, 곧은 뒷면 *_n → *_up. dash_up·jump_up 은 3/4 뒷면 그림 그대로(곧은 뒷면 그록 대기)'
save(R,s,j,k,H);print(gone)
