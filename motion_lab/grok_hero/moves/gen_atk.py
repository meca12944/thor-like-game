# 공격 사이 장 (검흔 담당 추천 PixelLab, 사장님 10-25 컨펌): 서기→1타, 1타→2타, 2타→3타 사이 4장씩(각 4). 방향 ↓ → ↑ (←는 뒤집기). 칼·검기는 그리지 않음(코드)
import subprocess,sys,os
k=sys.argv[1];d=k.split('_')[1];step=k.split('_')[0]
IDLE={'down':'idle_down.png','right':'idle_right.png','up':'idle_up.png'}
A=lambda i:f'../frames/atk{i}_{d}/000.png'
pair={'t01':(IDLE[d],A(1)),'t12':(A(1),A(2)),'t23':(A(2),A(3))}[step]
view={'down':'front view facing the viewer','right':'strict side view facing right','up':'straight back view'}[d]
act=f"quick sword-slash body motion between two attack poses, {view} the whole time, empty hands (the sword is drawn later in code), no sword, no slash effect, no motion lines, no glow, no effects"
if not os.path.exists(f'{k}/004.png'): subprocess.run(['python3','tween.py',pair[0],pair[1],k,'4',act,'7'],check=True)
print('done',k)
