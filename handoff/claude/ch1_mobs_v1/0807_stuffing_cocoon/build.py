# 08 핀이빨 솜뭉치 + 07 고치 어미 (크레딧 0): 걷기 그림 없이 그록 자세만 → 256칸 띠(발 y249). 움직임(통통 튀기·떠다니기)은 코드 anim.walk.bob.
import os
from PIL import Image
C=os.path.dirname(os.path.abspath(__file__)); G=C+'/../../../grok_in/1장_마물_20261025/'
FLIP={'cocoon_burst'}
def strip(name, poses, folder, pre, cellh, anchor):
    ss=Image.open(G+folder+'/'+pre+'side_stand.png').convert('RGBA'); b=ss.getbbox(); S=cellh/(b[3]-b[1]); cells=[]
    for n in poses:
        im=Image.open(G+folder+'/'+pre+n+'.png').convert('RGBA'); im=im.crop(im.getbbox())
        if n in FLIP: im=im.transpose(Image.FLIP_LEFT_RIGHT)  # 그록 고치 터뜨리기는 왼쪽을 봄 → 오른쪽 보기로
        im=im.resize((round(im.width*S),round(im.height*S)),Image.LANCZOS)
        c=Image.new('RGBA',(256,256),(0,0,0,0)); c.alpha_composite(im,(round(128-im.width*anchor.get(n,.5)),249-im.height)); cells.append(c)
    s=Image.new('RGBA',(256*len(cells),256),(0,0,0,0))
    for i,c in enumerate(cells): s.alpha_composite(c,(256*i,0))
    s.save(f'{C}/strips/{name}.png'); print(name,round(S,4),[c.getbbox() for c in cells])
# 솜뭉치: 띠 속 키 100 (작아서 그림이 뭉개지지 않게), 무는 그림은 입이 앞이라 몸 가운데를 맞춤
strip('c1_pin_stuffing_walk',['side_stand'],'08_pin_tooth_stuffing','m08_',100,{})
strip('c1_pin_stuffing_attack',['side_stand','bite'],'08_pin_tooth_stuffing','m08_',100,{'bite':.4})
# 고치 어미: 띠 속 키 200 (중간 보스 크게)
strip('c1_cocoon_mother_walk',['side_stand'],'07_cocoon_mother','m07_',200,{})
strip('c1_cocoon_mother_attack',['side_stand','cocoon_burst'],'07_cocoon_mother','m07_',200,{})
strip('c1_cocoon_mother_shoot',['side_stand','cocoon_burst'],'07_cocoon_mother','m07_',200,{})
