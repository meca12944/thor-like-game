# 1->2->3 combo mp4 (cleaned frames). each later hit skips its frame 0 (= previous hit's end pose); hits 1-2 drop their last hold frames when chained.
# columns → ← ↘ ↗ (left/↙/↖ = mirrors). usage: combo.py <clean dir> <out.mp4>
import sys,os,shutil,subprocess
from PIL import Image,ImageDraw,ImageFont,ImageOps
cd,out=sys.argv[1:3];FT=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',22)
D={'e':('h1_e_s71','h2_e_s71','h3_e_s71'),'se':('h1_se_s71','h2_se_chain_s73','h3_se_s71'),'ne':('h1_ne_l15_s72','h2_ne_l15_s72','h3_ne_l15_s72')}
TK=([2,2,2,2,2,3,1,1,1,1,2,2,3,4,4],[2,2,2,2,2,1,1,1,1,1,2,3,4,4],[2,2,2,3,3,3,1,1,1,1,1,3,4,5,6])
CUT=(13,12,15)                                  # frames used per hit when chained (h1/h2 drop the 2 hold frames)
idle={'e':'rot_east','se':'rot_south-east','ne':'rot_north-east'}
def seq(v):
    s=[(Image.open(f'handoff/claude/q34_test/{idle[v]}.png').convert('RGBA'),20)]
    for h in range(3):
        for i in range(1 if h else 0,CUT[h]): s.append((Image.open(f'{cd}/{D[v][h]}/{i:03d}.png').convert('RGBA'),TK[h][i]))
    s.append((s[0][0],30));return s
E,SE,NE=seq('e'),seq('se'),seq('ne');cols=[E,[(ImageOps.mirror(i),k) for i,k in E],SE,NE]
lab=['→','← (반전)','↘ (↙=반전)','↗ (↖=반전)']
C=(20,40,236,212);W,H=C[2]-C[0],C[3]-C[1];S=2
fd=os.path.dirname(out)+'/combof';shutil.rmtree(fd,True);os.makedirs(fd);f=0
T=sum(k for _,k in E)
def at(s,t):
    for im,k in s:
        if t<k: return im
        t-=k
    return s[-1][0]
for slow in (1,1,3):
    for t in range(T):
        im=Image.new('RGB',(W*S*4,H*S+40),(58,62,70));g=ImageDraw.Draw(im)
        for c in range(4):
            fr=at(cols[c],t).crop(C).resize((W*S,H*S),Image.NEAREST);im.paste(fr,(c*W*S,40),fr);g.text((c*W*S+10,8),lab[c],fill=(255,255,255),font=FT)
        if slow>1: g.text((W*S*4-140,8),'1/3 느리게',fill=(255,180,180),font=FT)
        for r in range(slow): im.save(f'{fd}/{f:05d}.png');f+=1
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','60','-i',f'{fd}/%05d.png','-vf','fps=30,pad=ceil(iw/2)*2:ceil(ih/2)*2','-pix_fmt','yuv420p','-c:v','libx264','-crf','20',out],check=True);shutil.rmtree(fd);print('ok',out,T,'ticks')
