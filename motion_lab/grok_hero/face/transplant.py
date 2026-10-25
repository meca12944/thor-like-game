# 실험(크레딧 0): 옛 주인공 정면 얼굴의 도트 짜임(눈·반짝임·코·입·턱선)을 새 주인공 피부·눈 색으로 바꿔 144 정면 머리에 얹기
import sys,numpy as np
sys.path.insert(0,'../ratio');sys.path.insert(0,'../se_test')
from PIL import Image,ImageDraw,ImageFont
from measure_ratio import meas,skin
from pxscale import pxscale
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
def to144(f):
    im=Image.open(f).convert('RGBA');b=im.getbbox();s=144/164;c=pxscale(im.crop(b),s);o=Image.new('RGBA',(256,256));o.paste(c,(round(128+(b[0]-128)*s),round(189+(b[1]-189)*s)),c);return o
dst=to144('../frames/walk_down/000.png');dst.save('/tmp/_d.png');md=meas('/tmp/_d.png')
src_f='../../hero8/frames/walk_down/000.png';ms=meas(src_f)
S=np.array(Image.open(src_f).convert('RGBA')).astype(int);D=np.array(dst).astype(int)
sx0,sy0,sx1,sy1,_=ms['face'];dx0,dy0,dx1,dy1,_=md['face']
# 옛 얼굴 칸: 살색 상자 +1 (눈 포함)
patch=S[sy0-1:sy1+2,sx0-1:sx1+2].copy();ph,pw=patch.shape[:2]
# 새 피부 3단(새 얼굴 살색에서 밝음·가운데·어둠)
dsk=D[...,:3][skin(D)&(np.arange(256)[:,None]<dy1+1)&(np.arange(256)[:,None]>=dy0)];Ls=dsk.mean(1);order=np.argsort(Ls)
tone=[dsk[order[int(len(order)*q)]] for q in (.15,.5,.9)]
ssk=skin(patch);Lp=patch[...,:3].mean(2)
if ssk.any():
    t1,t2=np.percentile(Lp[ssk],[33,66])
    for m,t in ((ssk&(Lp<t1),tone[0]),(ssk&(Lp>=t1)&(Lp<t2),tone[1]),(ssk&(Lp>=t2),tone[2])): patch[m,:3]=t
# 눈 색(옛 파랑) → 짙은 갈색, 흰 반짝임은 그대로
r,g,b=patch[...,0],patch[...,1],patch[...,2];eye=(patch[...,3]>0)&(b>r+10)&~ssk&(Lp>60)&(Lp<200);patch[eye,:3]=[60,38,30]
# 얹기: 얼굴 가운데 맞춤, 살색·눈 칸만(머리카락은 새 것 그대로)
cy,cx=(dy0+dy1)//2,(dx0+dx1)//2;oy,ox=cy-ph//2,cx-pw//2
keep=ssk|eye|((patch[...,:3].mean(2)<70)&(patch[...,3]>0)&np.pad(np.ones((ph-4,pw-4),bool),2))  # 안쪽 어두운 칸(눈동자·입)
out=D.copy();sub=out[oy:oy+ph,ox:ox+pw];sub[keep]=patch[keep];Image.fromarray(out.astype('uint8')).save('transplant_front.png')
Z=8;C=30
W=Image.new('RGB',(3*(C*Z+8),C*Z+30),(70,74,80));d=ImageDraw.Draw(W)
for i,(t,im) in enumerate((('지금(144)',dst),('옛 얼굴 짜임 얹음',Image.fromarray(out.astype('uint8'))),('옛 주인공 얼굴',Image.open(src_f).convert('RGBA')))):
    m=md if i<2 else ms;x0,y0,x1,y1,_=m['face'];cxx,cyy=(x0+x1)//2,(y0+y1)//2
    cr=im.crop((cxx-C//2,cyy-C//2,cxx+C//2,cyy+C//2));bg=Image.new('RGBA',cr.size,(70,74,80,255));bg.alpha_composite(cr)
    W.paste(bg.convert('RGB').resize((C*Z,C*Z),Image.NEAREST),(i*(C*Z+8),26));d.text((i*(C*Z+8)+4,4),t,font=F,fill=(255,255,255))
W.save('transplant_test.png');print('ok')
