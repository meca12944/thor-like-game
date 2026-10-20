# Assemble Linette's full motion set (256 canvas, feet root (128,189)) from the sources made on 2026-10-19 and write manifest.json.
# Side views = skeleton (walk/run/dash/hurt) or key-pose thrusts (atk1-3); left = right mirrored (owner rule); front/back = PixelLab v1 frames.
import os,glob,json,shutil
from PIL import Image,ImageOps
H=os.path.dirname(os.path.abspath(__file__)); B=os.path.dirname(H)
V1=B+'/linette_moves_v1'; SK=B+'/linette_skel_v1'; TH=B+'/linette_thrust_v1'
def frames(p): return sorted(glob.glob(p+'/*.png'))
ATK=[2,1,1,2,2,2,2,1]   # thrust: quick start, windup, snap; then hold and reverse recovery (frames 7,6,5,4,0)
def atk(hold): return ('seq',list(range(8))+[8,7,6,5,4,0],ATK+[hold,2,2,2,2,2])
SRC={ # motion: {dir: (folder, frame filter or seq spec, ticks)}
 'idle':{'right':(V1+'/idle/east',list(range(8)),[7]*8),'down':(V1+'/idle/south',list(range(8)),[7]*8),'up':(V1+'/idle/north',list(range(8)),[7]*8)},
 'walk':{'right':(SK+'/walk_east',None,[4]*12),'down':(V1+'/walk/south',list(range(8)),[6]*8),'up':(V1+'/walk/north',list(range(8)),[6]*8)},
 'run':{'right':(SK+'/run_east_back2',None,[3]*12),'down':(V1+'/run/south',list(range(8)),[5,4]*4),'up':(V1+'/run/north',list(range(8)),[5,4]*4)},
 'dash':{'right':(SK+'/dash_east',None,[3,3,4,4,3,3]),'down':(SK+'/dash_south_v3',None,[3,3,4,4,3,3]),'up':(SK+'/dash_north',None,[3,3,4,4,3,3])},
 'hurt':{'right':(SK+'/hurt_east',None,[3,4,5,4,3,3]),'down':(SK+'/hurt_south',None,[3,4,5,4,3,3]),'up':(SK+'/hurt_north',None,[3,4,5,4,3,3])},  # front/back dash+hurt redone with skeleton (v1 text frames had splayed crab legs)
 'death':{'right':(V1+'/death/east',None,[6]*9),'down':(V1+'/death/south',None,[6]*9),'up':(V1+'/death/north',None,[6]*9)},
 'cast':{'right':(V1+'/cast/east',None,[5]*9),'down':(V1+'/cast/south',None,[5]*9),'up':(V1+'/cast/north',None,[5]*9)},
 '_atk_old_atk1':{'right':(TH+'/atk1/east',)+atk(10)[1:],'down':(TH+'/atk1/south-east',)+atk(10)[1:],'up':(TH+'/atk1/north-east',)+atk(10)[1:]},
 '_atk_old_atk2':{'right':(TH+'/atk2/east',)+atk(10)[1:],'down':(TH+'/atk2/south-east',)+atk(10)[1:],'up':(TH+'/atk2/north-east',)+atk(10)[1:]},
 '_atk_old_atk3':{'right':(TH+'/atk3/east',)+atk(18)[1:],'down':(TH+'/atk3/south-east',)+atk(18)[1:],'up':(TH+'/atk3/north-east',)+atk(18)[1:]},
}
AS=H+'/attack_src'; CL=json.load(open(AS+'/clips.json'))
for k in [k for k in SRC if k.startswith('_atk_old_')]: del SRC[k]
for m in ('atk1','atk2','atk3'): SRC[m]={d:(f'{AS}/{m}/{d}',None,CL[f'{m}_{d}']['ticks']) for d in ('right','down','up')}   # down/up = diagonal art; mirrored copies -> downl/upl
# owner 10-20: north/south views are not used any more (hard to generate, lower quality) -> drop every down/up clip except the attacks,
# which already use the diagonal art (down = down-right, up = up-right; downl/upl mirrored). Vertical movement faces the last left/right side.
for m in SRC:
    if not m.startswith('atk'): SRC[m]={d:v for d,v in SRC[m].items() if d=='right'}
SRC['cast']['down']=(V1+'/cast/south-east',None,[5]*9); SRC['cast']['up']=(V1+'/cast/north-east',None,[5]*9)   # owner 10-20: diagonal cast (down-right / up-right; mirrored -> downl/upl)
man={'_doc':'Linette (PixelLab 7e26e0f3, 117px) motion set v1. frames/<motion>/<dir>/NNN.png, 256x256, feet root (128,189). left = right mirrored. ticks @60fps per frame.','motions':{}}
for m,dd in SRC.items():
    man['motions'][m]={}
    for d,(src,sel,ticks) in dd.items():
        fs=frames(src); sel=sel if sel is not None else list(range(len(fs)))
        assert len(sel)==len(ticks),(m,d,len(sel),len(ticks),len(fs))
        for dn,flip in ((d,False),)+((('left',True),) if d=='right' else (('downl',True),) if d=='down' else (('upl',True),) if d=='up' else ()):
            out=f'{H}/frames/{m}/{dn}'; shutil.rmtree(out,ignore_errors=True); os.makedirs(out)
            for i,k in enumerate(sel):
                im=Image.open(fs[k]).convert('RGBA'); im=ImageOps.mirror(im) if flip else im; im.save(f'{out}/{i:03d}.png')
            man['motions'][m][dn]={'ticks':ticks,'lunge':CL.get(f'{m}_{d}',{}).get('lunge'),'src':os.path.relpath(src,B)+(' (mirrored)' if flip else ''),'pick':sel}
json.dump(man,open(H+'/manifest.json','w'),indent=1,ensure_ascii=False); print('ok',sum(len(v) for v in man['motions'].values()),'clips')
