# Attack clips v2: side = key-pose thrusts (atk2 = left-hand chain straight out of the atk1 lunge), down/up = true front/back thrusts
# from edited key poses (atk2 down/up = atk1 mirrored -> the other hand). Writes attack_src/<atk>/<dir>/NNN.png + attack_src/clips.json
import os,json,shutil
from PIL import Image,ImageOps
H=os.path.dirname(os.path.abspath(__file__)); B=os.path.dirname(H); TH=B+'/linette_thrust_v1'; SK=B+'/linette_skel_v1'; OUT=H+'/attack_src'
R=[2,1,1,2,2,2,2,1]; REC=[(7,2),(6,2),(5,2),(4,2),(0,2)]
def P(folder,picks): return [(f'{folder}/{i:03d}.png',t) for i,t in picks]
C={
 ('atk1','right'):(P(TH+'/atk1/east',list(zip(range(9),R+[10]))+REC),8),
 ('atk2','right'):(P(SK+'/swap_east',[(0,1),(1,2),(2,12)])+P(SK+'/atk2chain_east',[(4,3),(5,3),(6,3)]),2),
 ('atk3','right'):(P(TH+'/atk3/east',list(zip(range(9),R+[18]))+REC),8),
 ('atk1','down'):(P(TH+'/atk1/south-east',list(zip(range(9),R+[10]))+REC),8),        # owner 10-20: down/up attacks = the diagonal art (down-right / up-right)
 ('atk2','down'):(P(SK+'/swap_south-east',[(0,1),(1,2),(2,12)])+P(SK+'/atk2chain_south-east',[(4,3),(5,3),(6,3)]),2),
 ('atk3','down'):(P(TH+'/atk3/south-east',list(zip(range(9),R+[18]))+REC),8),
 ('atk1','up'):(P(TH+'/atk1/north-east',list(zip(range(9),R+[10]))+REC),8),
 ('atk2','up'):(P(SK+'/swap_north-east',[(0,1),(1,2),(2,12)])+P(SK+'/atk2chain_north-east',[(4,3),(5,3),(6,3)]),2),
 ('atk3','up'):(P(TH+'/atk3/north-east',list(zip(range(9),R+[18]))+REC),8),
}

shutil.rmtree(OUT,ignore_errors=True); meta={}
for (m,d),spec in C.items():
    o=f'{OUT}/{m}/{d}'; os.makedirs(o)
    if spec[0]=='mirror':
        src=C[(spec[1],spec[2])]; frames,lunge=src
        for i,(f,t) in enumerate(frames): ImageOps.mirror(Image.open(f).convert('RGBA')).save(f'{o}/{i:03d}.png')
    else:
        frames,lunge=spec
        for i,(f,t) in enumerate(frames): Image.open(f).convert('RGBA').save(f'{o}/{i:03d}.png')
    meta[f'{m}_{d}']={'ticks':[t for _,t in frames],'lunge':lunge,'src':[os.path.relpath(f,B) for f,_ in frames]+(['(mirrored)'] if spec[0]=='mirror' else [])}
json.dump(meta,open(OUT+'/clips.json','w'),indent=1); print('clips',len(meta))
