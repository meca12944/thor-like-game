# 겹쳐 보기: 서기(빨강)·걷기(초록)·달리기(파랑)를 같은 발 기준점(128,189)에 겹쳐서 크기·위치 차이를 눈으로
import sys,os,numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from measure8 import load,body
def tint(a,col):
    m=body(a);o=np.zeros((256,256,4),np.uint8);o[m]=col+(110,);return Image.fromarray(o)
def sheet(groups,out,labels=None):
    W=Image.new('RGBA',(180*len(groups),190),(30,30,30,255));d=ImageDraw.Draw(W)
    for i,g in enumerate(groups):
        for a,col in g:W.alpha_composite(tint(a,col).crop((38,30,218,220)),(i*180,0))
        d.line((i*180+90,0,i*180+90,190),fill=(255,255,255,80));d.line((i*180,159,i*180+179,159),fill=(255,255,255,80))
        if labels:d.text((i*180+4,4),labels[i],fill=(255,255,255))
    W.resize((W.width*2,W.height*2),Image.NEAREST).save(out)
