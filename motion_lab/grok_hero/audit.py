# 움직임 숫자 (audit2 방식): 클립마다 머리 오르내림(머리 꼭대기 y 범위), 발 오르내림(발바닥 y 범위), 좌우 흔들림(몸 가운데 x 범위), 반복 이음새(마지막→첫 장 변화 / 장 사이 평균 변화, 1.8 넘으면 끊겨 보임)
import os,json,numpy as np
from PIL import Image
def load(d):return [np.array(Image.open(f'{d}/{f}').convert('RGBA')).astype(int) for f in sorted(os.listdir(d))]
def diff(a,b):m=(a[...,3]>0)|(b[...,3]>0);return (np.abs(a[...,:3]-b[...,:3]).sum(2)*m).sum()/max(1,m.sum())
def audit(fr):
    top=[];bot=[];cx=[]
    for f in fr:
        al=f[...,3]>40;ys,xs=np.nonzero(al);top.append(ys.min());bot.append(ys.max());cx.append(xs.mean())
    dd=[diff(fr[i],fr[i+1]) for i in range(len(fr)-1)];seam=diff(fr[-1],fr[0])/max(1e-3,np.mean(dd))
    return dict(n=len(fr),head=int(max(top)-min(top)),feet=int(max(bot)-min(bot)),sway=round(float(max(cx)-min(cx)),1),seam=round(float(seam),2),H=int(np.median(np.array(bot)-np.array(top))))
if __name__=='__main__':
    R=os.path.dirname(os.path.abspath(__file__));H8='/home/user/thor-like-game/motion_lab/hero8/frames';out={}
    for k in ['walk_down','walk_right','walk_up','walk_left','run_down','run_right','run_up','run_left']:
        g=audit(load(f'{R}/frames/{k}'))
        hk=k.replace('_left','_right');h=audit(load(f'{H8}/{hk}'))
        out[k]=dict(grok=g,h8=h);print(k,'그록',g,'| 지금',h)
    json.dump(out,open(f'{R}/audit.json','w'),ensure_ascii=False,indent=1)
