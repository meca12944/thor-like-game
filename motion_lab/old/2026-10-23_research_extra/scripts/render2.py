import numpy as np,subprocess
from PIL import Image,ImageDraw,ImageFont
FONT=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',12)
def tick_frame(ticks,t):
    k=t%sum(ticks);i=0
    while k>=ticks[i]:k-=ticks[i];i+=1
    return i
def grid(out,rows,secs=5,S=2,W=260,H=165,fps=60,title=None):
    """rows: list of (name, [lane,...]); lane=dict(frames,ticks,speed,label,vx,vy) camera follows"""
    nc=max(len(r[1]) for r in rows);TH=18 if title else 0
    WW,HH=W*nc,H*len(rows)+TH
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{WW*S}x{HH*S}','-r',str(fps),'-i','-','-pix_fmt','yuv420p','-vcodec','libx264','-crf','18',out],stdin=subprocess.PIPE)
    for t in range(secs*fps):
        im=Image.new('RGB',(WW,HH),(40,44,40));d=ImageDraw.Draw(im)
        if title:d.text((6,2),title,fill=(255,255,255),font=FONT)
        for r,(name,lanes) in enumerate(rows):
            for c,L in enumerate(lanes):
                ox,oy=c*W,TH+r*H;i=tick_frame(L['ticks'],t)
                d.rectangle([ox,oy,ox+W-2,oy+H-2],fill=(70,84,70))
                vx,vy=L.get('vx',L.get('speed',0)),L.get('vy',0)
                for gx in range(-int(vx*t)%20-20,W,20):d.line([ox+max(0,gx),oy,ox+max(0,gx),oy+H-2],fill=(78,93,78))
                for gy in range(-int(vy*t)%20-20,H,20):d.line([ox,oy+max(0,gy),ox+W-2,oy+max(0,gy)],fill=(78,93,78))
                fr=Image.fromarray(L['frames'][i]);
                if L.get('flip'):fr=fr.transpose(Image.FLIP_LEFT_RIGHT)
                cell=Image.new('RGB',(W-2,H-2));cell.paste(im.crop((ox,oy,ox+W-2,oy+H-2)));cd=ImageDraw.Draw(cell);cd.ellipse([W//2-16,H-20-4,W//2+16,H-20+4],fill=(52,62,52));cell.paste(fr,(W//2-128,H-20-189),fr)
                im.paste(cell,(ox,oy));d.text((ox+4,oy+2),name+' '+L['label'],fill=(255,240,120),font=FONT)
        p.stdin.write(im.resize((WW*S,HH*S),Image.NEAREST).tobytes())
    p.stdin.close();p.wait()
