# bake the final side thrust frames (polished, face fixed, lance streak on the thrust frames) -> handoff/.../frames/<hit>_NN.png
import os,sys
P='/tmp/claude-0/-home-user-thor-like-game/605da03e-2542-5329-b23f-a50876f99780/scratchpad/'
src=open(P+'th/compare.py').read().split("os.makedirs(P+'th/vid'")[0];exec(src)
O='/home/user/thor-like-game/handoff/claude/hero_attack_thrust_v1/frames/'
for h in ['hit1','hit2']:
    T=[e[2] for e in A['anims'][h+'_right']];fr=[Image.open(P+f'jit/{h}_th/{i:02d}.png').convert('RGBA') for i in range(8)]
    fr=[SK.fix_face(im,f'{h}_th',i)[0] for i,im in enumerate(fr)];pol=PL.polish(list(zip(fr,T)),f'{h}_th','side',{2,3,4,5,6})
    tp=trail3.tip(pol[3][0])
    for i,(im,t) in enumerate(pol):
        if 3<=i<=5 and tp: im=lance(im,(tp[0],tp[1]),[0,4,7][i-3],big=(h=='hit2'))  # strong -> mid -> faint
        im.save(O+f'{h}_{i:02d}.png')
print('ok')
