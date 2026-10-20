import json,sys
from PIL import Image,ImageDraw
B=[('NECK','LEFT SHOULDER'),('NECK','RIGHT SHOULDER'),('LEFT SHOULDER','LEFT ELBOW'),('LEFT ELBOW','LEFT ARM'),('RIGHT SHOULDER','RIGHT ELBOW'),('RIGHT ELBOW','RIGHT ARM'),
   ('NECK','LEFT HIP'),('NECK','RIGHT HIP'),('LEFT HIP','RIGHT HIP'),('LEFT HIP','LEFT KNEE'),('LEFT KNEE','LEFT LEG'),('RIGHT HIP','RIGHT KNEE'),('RIGHT KNEE','RIGHT LEG'),('NECK','NOSE')]
rows=sys.argv[2:];W=Image.new('RGB',(120*15,120*len(rows)),(30,30,40));d=ImageDraw.Draw(W)
for r,f in enumerate(rows):
    for c,fr in enumerate(json.load(open(f))):
        K={k['label']:(k['x']*256,k['y']*256) for k in fr};ox,oy=c*120-68,r*120-70
        for a,b in B:
            col=(255,90,90) if 'LEFT' in a+b and ('ARM' in b or 'ELBOW' in b) else (90,200,255) if 'RIGHT' in b and ('ARM' in b or 'ELBOW' in b) else (230,230,230)
            d.line([(K[a][0]*0.75+ox,K[a][1]*0.75+oy),(K[b][0]*0.75+ox,K[b][1]*0.75+oy)],fill=col,width=2)
        sx,sy=K['LEFT ARM'];ex,ey=K['LEFT ELBOW'];dx,dy=sx-ex,sy-ey;L=(dx*dx+dy*dy)**.5 or 1
        d.line([(sx*0.75+ox,sy*0.75+oy),((sx+dx/L*45)*0.75+ox,(sy+dy/L*45)*0.75+oy)],fill=(255,255,120),width=1)  # rough sword direction
W.save(sys.argv[1])
