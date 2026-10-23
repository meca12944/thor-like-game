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
 'run':{'right':(SK+'/run_east_back',None,[3]*12),'down':(V1+'/run/south',list(range(8)),[5,4]*4),'up':(V1+'/run/north',list(range(8)),[5,4]*4)},
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
HD='/tmp/claude-0/-home-user-thor-like-game/a29f4f91-dc28-5c8c-bba3-8521caf6b08f/scratchpad/herodiag'
for _m in ('idle','walk','run','dash'):   # owner 10-20: diagonal idle/walk/run/dash = hero's diagonal motions put on Linette (skeleton); ticks = hero's
    for _d,_dd in (('down','south-east'),('up','north-east')):
        _t=json.load(open(f'{HD}/{_m}_{_d}/ticks.json')) if os.path.exists(f'{HD}/{_m}_{_d}/ticks.json') else json.load(open(f'{SK}/{_m}_{_dd}_diag.ticks.json'))
        SRC[_m][_d]=(f'{SK}/{_m}_{_dd}_diag',None,_t)
SRC['jump']={'right':(f'{SK}/jump_east',None,json.load(open(f'{SK}/jump_east.ticks.json'))),   # owner 10-20: jump from the hero's jump (skeleton), side + diagonal
             'down':(f'{SK}/jump_south-east_diag',None,json.load(open(f'{SK}/jump_south-east_diag.ticks.json'))),
             'up':(f'{SK}/jump_north-east_diag',None,json.load(open(f'{SK}/jump_north-east_diag.ticks.json')))}
SRC['idle']['right']=(f'{SK}/idle_east_facefix',[0,1,2,3,4,5,4,3,2,1],[7]*10)   # owner 10-20: side idle redrawn by PixelLab from the face-fixed frame (visible eye/nose/chin); frames 6-7 swing the needles -> ping-pong 0-5
SRC['atk2']['right']=(f'{SK}/atk2_east_face',None,CL['atk2_right']['ticks'])   # owner 10-20: atk2/atk3 heads too big + different faces -> redrawn by PixelLab skeleton from the new face (atk2: legs of frames 1-2 pasted from frame 0)
SRC['atk3']['right']=(f'{SK}/atk3_east_face',list(range(9))+[7,6,5,4,0],CL['atk3_right']['ticks'])
for _m,_pick in (('idle',None),('walk',[11]+list(range(1,12))),('run',None)):   # owner 10-20: down-diagonal arms like the side clips (skeleton arms from side; walk frame 0 kept the old spread arms -> replaced)
    SRC[_m]['down']=(f'{SK}/{_m}_south-east_sidearms',_pick,SRC[_m]['down'][2])
SRC['walk']['right']=(f'{SK}/walk_east_face',None,[4]*12)   # owner 10-20 "걸을때 얼굴 이상": walks redrawn by PixelLab skeleton from the new face (side from the new idle, diagonal from the new diagonal idle)
SRC['walk']['down']=(f'{SK}/walk_south-east_face',None,SRC['walk']['down'][2])
for _m,_t in (('walk',[5]*8),('run',[4]*8)):   # 10-21: runs + back walk = CMU mocap (09_01 run / 07_01 walk) seen front/back with depth tilt, legs alternate under the hips (mocap_ns.py)   # owner 10-20: true front/back (south/north) walk + run from the hero's front/back motions (skeleton); dirs 'south'/'north', no mirror
    SRC[_m]['south']=(f'{SK}/{_m}_south_ns',None,_t);SRC[_m]['north']=(f'{SK}/{_m}_north_ns',None,_t)
# owner 10-21: front walk = CMU walk skeleton seen from the front with a strong depth tilt (legs visibly swing forward/back), feet under the hips (walk_south_ns v7)
KN=B+'/linette_ns_keys_v1'   # owner 10-21 "2번 해라 ... 인간의 자연스러운 움직임": front/back walk + run = 2 PixelLab key poses (edit-images-v2) + PixelLab in-betweens (animate-with-text-v3), cycle_ns.py
SRC['walk']['south']=(f'{KN}/walk_south_keys',None,[6]*8);SRC['walk']['north']=(f'{KN}/walk_north_keys',None,[6]*8)
SRC['run']['south']=(f'{KN}/run_south_keys',None,[4]*8);SRC['run']['north']=(f'{KN}/run_north_keys',None,[4]*8)
for _m in ('idle','walk','run'):   # owner 10-21 "대각선 이상": up-diagonal = hero diagonal skeleton + side-clip arms (generated 10-20, put back now that diagonals are used for diagonal input)
    SRC[_m]['up']=(f'{SK}/{_m}_north-east_sidearms',None,SRC[_m]['up'][2])
# owner 10-21 "해야지": diagonal walk + run also by the key-pose method (near/far leg keys + in-betweens), left = mirrored
SRC['walk']['down']=(f'{KN}/walk_se_keys',None,[6]*8);SRC['walk']['up']=(f'{KN}/walk_ne_keys',None,[6]*8)
SRC['run']['down']=(f'{KN}/run_se_keys8',None,[4]*8);SRC['run']['up']=(f'{KN}/run_ne_keys8',None,[4]*8)   # 10-21 "다리교차 이상": one full 8-frame cycle key->same key (cycle8.py)
# owner 10-21 "좌우 캐릭터 크기 차이, 자연스럽지 않음": side walk + run also by key pose (original east still) + one 8-frame key->key cycle, same look as the other directions
SRC['walk']['right']=(f'{KN}/walk_e_keys8',None,[6]*8);SRC['run']['right']=(f'{KN}/run_e_raw8',None,[4]*8)
# owner 10-21 "모든 모션 팔을 흔드는걸로": front/back/diagonal walk + run redrawn with arm swing (one arm-swing key per motion + one 8-frame key->key cycle);
# back views keep the bikini back strap visible. Sizes are evened out in polish.py (SIZE_TARGET).
for _m in ('walk','run'):
    for _d,_k in (('south','s'),('north','n'),('down','se'),('up','ne')):SRC[_m][_d]=(f'{KN}/a_{_k}_{_m}8',None,[6]*8 if _m=='walk' else [4]*8)
SRC['run']['south']=(f'{KN}/b_s_run8',None,[4]*8)   # 10-21 "아래 뛸때 한쪽팔 고정": front run redrawn with both arms swinging
SRC['rjump']={'right':(f'{SK}/rjump_east_v2',None,[3]*12)}   # owner 10-20: running jump = the hero's own rjump skeleton (CMU 127_25, frames 2-13) refit to Linette, run arms kept (v1 from estimated hero frames was too crouched); side only (left mirrored)
SRC['cast']['down']=(V1+'/cast/south-east',None,[5]*9); SRC['cast']['up']=(V1+'/cast/north-east',None,[5]*9)   # owner 10-20: diagonal cast (down-right / up-right; mirrored -> downl/upl)
# owner 10-21 "실 감고 던지기": new cast = X-cross the rapiers at the chest, twirl (winding thread), step and throw (PixelLab key pose + in-betweens, linette_cast_v1);
# the throw key lands at tick 20 (skills fire at 20-22), held, then back to idle; 45 ticks like before so the magic circle timing is unchanged.
CV=B+'/linette_cast_v1';_back=[2,3,3,3,4,3,2,12,4,4,5]
SRC['cast']={'right':(CV+'/cast_e_seq',[0,1,2,3,4,6,7,8,7,1,0],_back),
             'down':(CV+'/tw_se',[0,2,3,4,5,6,7,8,7,1,0],[2,3,3,3,4,3,2,12,4,4,5]),
             'up':(CV+'/tw_ne',[0,2,3,4,5,6,7,8,7,1,0],[2,3,3,3,4,3,2,12,4,4,5])}
# owner 10-22 "가만히 서있는 얼굴과 뛰는 얼굴이 틀리다": side walk + run redrawn from the face-fixed idle (new face) - key pose + one 8-frame key->key cycle (linette_face_v2)
FV=B+'/linette_face_v2';SRC['walk']['right']=(FV+'/walk_e8',None,[6]*8);SRC['run']['right']=(FV+'/run_e8',None,[4]*8)
# owner 10-22 "주인공 대시 모션 그대로 가지고와": side dash = the hero's side dash (hero8 dash_right: stand, low lunge, hold, recover) on Linette by skeleton,
# same ticks as the hero (4,4,4,5); diagonal dashes were already the hero's (dash_*_diag, ticks 2,1,3,2,3,3,3)
SRC['dash']['right']=(SK+'/dash_east_hero',None,[4,4,4,5])
# owner 10-22 "일반 점프시 다리 모양이 부자연" -> A (re-time, no new art): the wide landing stances were shown while she was in the air.
# New order: stand -> crouch (anticipation) -> legs-together frame while rising -> slightly opened frame at the peak/fall -> landing stance
# (only after touching down) -> crouch (absorb) -> stand. Air = ticks 8..32 (linette.html JUMP_AIR), same for all three views.
_JT=[2,6,14,10,5,4,2]
SRC['jump']['right']=(SK+'/jump_east',[0,1,2,3,7,1,0],_JT)
SRC['jump']['down']=(SK+'/jump_south-east_diag',[0,3,4,5,11,3,0],_JT)
SRC['jump']['up']=(SK+'/jump_north-east_diag',[0,3,4,5,13,3,0],_JT)
# owner 10-22 "위로 달리기가 완전한 위방향이 아니라 살짝 오른쪽": back run redrawn as a STRICT straight back view (key from the straight back walk + 8-frame key->key cycle, linette_runn_v2)
SRC['run']['north']=(B+'/linette_runn_v2/run_n8',None,[4]*8)
# owner 10-23 "기본 서있는 자세가 정면이 아니고 대각선": straight front / back idle from the v1 front/back idle frames (already made, 0 credits);
# front: calm frames 0-2 ping-pong (frames 3-8 flick the ponytail), back: 0-7 ping-pong. Used when she faces straight down/up and at the start.
SRC['idle']['south']=(V1+'/idle/south',[0,1,2,1],[9]*4)
SRC['idle']['north']=(V1+'/idle/north',[0,1,2,3,4,3,2,1],[8]*8)
# owner 10-23 "대시 방향별로 / 리네트 폼대로": straight front/back dash in Linette's own form (key pose: knees bent, feet under her, arms close, leaning in;
# + idle->key in-betweens, linette_dashns_v1), 17 ticks like the other dashes: stand, drop, lunge (held), back up
DN=B+'/linette_dashns_v1';_DT=[2,2,3,6,2,2]
SRC['dash']['south']=(DN+'/tw_s',[0,1,3,4,3,1],_DT);SRC['dash']['north']=(DN+'/tw_n',[0,1,3,4,3,1],_DT)
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
