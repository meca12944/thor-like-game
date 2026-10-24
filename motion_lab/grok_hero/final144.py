# 사장님 10-24 「크기는 중간으로」: 게임 크기 = 정면 걷기 키 144 (작업은 164로 그리고 마지막에 한 번만 줄임: 144/164, 발 (128,189) 기준, pxscale)
# 동작마다 같은 배율 한 번 → 비율·움직임 그대로.  python3 final144.py [키]  → final/<동작>/
import sys,os,glob,json
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'se_test'))
from PIL import Image
from pxscale import pxscale
R=os.path.dirname(os.path.abspath(__file__));H=float(sys.argv[1]) if len(sys.argv)>1 else 144.;S=H/164
CL=json.load(open(f'{R}/final_clips.json'))   # {"walk_down":"frames/walk_down", ...} 고른 최종본
for k,src in CL.items():
    o=f'{R}/final/{k}';os.makedirs(o,exist_ok=True)
    for f in sorted(glob.glob(f'{R}/{src}/*.png')):
        if f.endswith('_raw.png'): continue
        im=Image.open(f).convert('RGBA');b=im.getbbox();c=pxscale(im.crop(b),S);out=Image.new('RGBA',(256,256))
        out.paste(c,(round(128+(b[0]-128)*S),round(189+(b[1]-189)*S)),c);out.save(f'{o}/{os.path.basename(f)}')
    print(k,src)
