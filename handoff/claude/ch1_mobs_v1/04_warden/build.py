# 04 철장 간수 (크레딧 0): 걷기 그림 없이 그록 자세만 → 256칸 띠(발 y249, 옆 서기 키 200, 배율 1개). 끌며 걷기 = 코드 anim.walk.bob.drag.
# 방향: 그록 방패 막기만 왼쪽을 봄 → 뒤집어 오른쪽(다른 자세는 오른쪽).
import os
from PIL import Image
C=os.path.dirname(os.path.abspath(__file__)); G=C+'/../../../grok_in/1장_마물_20261025/04_iron_cage_warden/m04_'
ss=Image.open(G+'side_stand.png').convert('RGBA'); b=ss.getbbox(); S=200/(b[3]-b[1]); print('scale',round(S,4))
FLIP={'shield_guard'}; AX={'slam_raise':.42,'slam_down':.45}
def pose(n):
    im=Image.open(G+n+'.png').convert('RGBA'); im=im.crop(im.getbbox())
    if n in FLIP: im=im.transpose(Image.FLIP_LEFT_RIGHT)
    im=im.resize((round(im.width*S),round(im.height*S)),Image.LANCZOS); c=Image.new('RGBA',(256,256),(0,0,0,0))
    c.alpha_composite(im,(round(128-im.width*AX.get(n,.5)),249-im.height)); return c
def save(name,poses):
    cs=[pose(n) for n in poses]; s=Image.new('RGBA',(256*len(cs),256),(0,0,0,0))
    for i,c in enumerate(cs): s.alpha_composite(c,(256*i,0))
    os.makedirs(C+'/strips',exist_ok=True); s.save(f'{C}/strips/c1_iron_warden_{name}.png'); print(name,[c.getbbox() for c in cs])
save('walk',['side_stand']); save('guard',['shield_guard']); save('attack',['side_stand','slam_raise','slam_down']); save('bash',['side_stand','shield_guard'])
