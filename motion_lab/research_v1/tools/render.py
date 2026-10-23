# lanes: list of dict(frames, ticks, speed(px/tick), dx(list of per-frame x offsets), dy, label)
import numpy as np,subprocess
from PIL import Image,ImageDraw,ImageFont
FONT=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',12)
def video(out,lanes,secs=4,S=2,W=420,H=170,fps=60):
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{H*S*len(lanes)}','-r',str(fps),'-i','-','-pix_fmt','yuv420p','-vcodec','libx264','-crf','18',out],stdin=subprocess.PIPE)
    for t in range(secs*fps):
        im=Image.new('RGB',(W,H*len(lanes)),(70,84,70));d=ImageDraw.Draw(im)
        for r,L in enumerate(lanes):
            oy=r*H;tt=t;cyc=sum(L['ticks']);k=tt%cyc;i=0
            while k>=L['ticks'][i]:k-=L['ticks'][i];i+=1
            camx=L['speed']*t  # camera follows hero: ground scrolls
            d.rectangle([0,oy+150,W,oy+H],fill=(90,74,56))
            for gx in range(-int(camx)%24-24,W,24):d.line([gx,oy+150,gx,oy+H],fill=(120,100,76),width=2)
            fr=Image.fromarray(L['frames'][i]);x=W//2-128+round(L.get('dx',[0]*99)[i]);y=150-189+round(L.get('dy',[0]*99)[i])
            im.paste(fr,(x,oy+y),fr)
            if L.get('flip'):pass
            d.text((6,oy+4),L['label'],fill=(255,240,120),font=FONT)
        p.stdin.write(im.resize((W*S,H*S*len(lanes)),Image.NEAREST).tobytes())
    p.stdin.close();p.wait()
