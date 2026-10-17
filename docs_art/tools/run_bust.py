import sys,os,json,numpy as np
sys.path.insert(0,'/workspace/art_work/prop'); from normalize import warp
from PIL import Image
D='/workspace/thor-like-game/docs_art/bust/'; ORIG='/workspace/art_work/prop/bust_orig/'
# measured (eye, chin, cx, shoulder_y, shoulder_half, chest, waist)
M={'hero':(207,325,505,473,330,664,900),'a_tailor':(277,412,506,500,290,718,900),
'h_mystic':(270,393,512,482,215,673,882),'g_dancer':(255,368,510,491,277,673,955),
'f_diver':(295,407,511,527,240,727,990),'e_tailor':(285,405,487,500,235,673,936),
'c_priest':(310,423,510,518,205,718,918),'d_yuna':(285,420,511,545,277,745,955)}
T=dict(eye=391,chin=565,sh=660,chest=843,waist=1042,half=235,cx=512)
CAP=(0.85,1.15); info={}
for c,(e,ch,cx,sh,hw,cs,wa) in M.items():
    sh_=(T['chin']-T['eye'])/(ch-e)
    ty=(T['sh']-T['chin']+T['waist']-T['sh'])  # unused
    vs=(T['waist']-T['sh'])/(wa-sh)            # torso vertical scale
    want=T['half']/hw; asp=np.clip(want/vs,*CAP); bsx=vs*asp
    ct=[T['eye'],T['chin'],T['sh'],T['chest'],T['waist']]; csy=[e,ch,sh,cs,wa]
    sxy=[0,T['chin'],T['sh'],1280]; sxv=[sh_,sh_,bsx,bsx]
    info[c]=dict(head_scale=round(sh_,3),torso_v=round(vs,3),x_body=round(bsx,3),aspect=round(float(asp),3),shoulder_half_out=round(hw*bsx))
    for f in sorted(os.listdir(ORIG+c)):
        im=np.array(Image.open(ORIG+c+'/'+f).convert('RGBA'))
        o=warp(im,(1024,1280),ct,csy,sxy,sxv,T['cx'],[0,1280],[cx,cx])
        Image.fromarray(o,'RGBA').save(D+c+'/'+f,optimize=True)
    print(c,info[c])
json.dump(dict(target=T,measured=M,applied=info),open('/workspace/art_work/prop/bust_norm.json','w'),indent=1)
