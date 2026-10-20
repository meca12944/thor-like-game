# side hit1/hit2: frames where the sword swings behind the body -> sword arm thrown forward (sword hand = LEFT), redrawn from that same frame
import json,math
P='/tmp/claude-0/-home-user-thor-like-game/605da03e-2542-5329-b23f-a50876f99780/scratchpad/'
FIX={('hit1',3):(28,22),('hit1',4):(10,4),('hit1',5):(-8,-14),('hit2',3):(6,0)}  # (upper-arm deg, forearm deg) below the forward horizontal
jobs=[]
for (h,i),(ae,aw) in FIX.items():
    K={k['label']:k for k in json.load(open(P+f'all/{h}_right/k{i}_kpfix.json'))['keypoints']}
    L=lambda a,b:math.hypot((K[a]['x']-K[b]['x'])*256,(K[a]['y']-K[b]['y'])*256)
    up,fo=L('LEFT SHOULDER','LEFT ELBOW'),L('LEFT ELBOW','LEFT ARM');s=K['LEFT SHOULDER']
    el=(s['x']*256+up*math.cos(math.radians(ae)),s['y']*256+up*math.sin(math.radians(ae)))
    wr=(el[0]+fo*math.cos(math.radians(aw)),el[1]+fo*math.sin(math.radians(aw)))
    fr=[]
    for l,k in K.items():
        x,y=k['x'],k['y']
        if l=='LEFT ELBOW': x,y=el[0]/256,el[1]/256
        if l=='LEFT ARM': x,y=wr[0]/256,wr[1]/256
        fr.append(dict(x=x,y=y,label=l,z_index=1 if l in ('LEFT ELBOW','LEFT ARM') else int(k.get('z_index',0))))
    json.dump([fr,fr,fr],open(P+f'fw/{h}_k{i}.json','w'))
    jobs.append(dict(first=P+f'all/{h}_right/k{i}.png',fkp=P+f'all/{h}_right/k{i}_kpfix.json',kp=P+f'fw/{h}_k{i}.json',dir='east',out=P+f'fw/out_{h}_k{i}',
                     act='sword slash, the sword swung far forward in front of the body, no effects, no trails, no slash marks'))
json.dump(jobs,open(P+'fw/jobs.json','w'));print(len(jobs))
