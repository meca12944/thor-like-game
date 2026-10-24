# CMU mocap: arm swing during walk / run (body frame): upper-arm swing angle (sagittal), elbow bend, hand fwd/back & up/down travel in body heights, phase vs legs
import sys, numpy as np
sys.path.insert(0, 'mocap'); import bvh
def ang(a, b): a = a / np.linalg.norm(a, axis=1, keepdims=True); b = b / np.linalg.norm(b, axis=1, keepdims=True); return np.degrees(np.arccos(np.clip((a * b).sum(1), -1, 1)))
for c, kind in [('07_01', 'walk'), ('09_01', 'run'), ('16_35', 'run/jog')]:
    n, P, ft = bvh.load(f'mocap/{c}.bvh'); ix = lambda s: n.index(s)
    H = P[:, ix('Hips')]; R = P[:, ix('RightUpLeg')] - P[:, ix('LeftUpLeg')]; R[:, 1] = 0; R /= np.linalg.norm(R, axis=1, keepdims=True)
    up = np.array([0, 1, 0.]); F = np.cross(R, up)
    vel = np.gradient(H, axis=0); s = np.sign(np.median(np.einsum('ij,ij->i', vel, F))); F *= s  # forward = travel direction
    head = P[:, ix('Head')]; height = np.median(head[:, 1] - np.minimum(P[:, ix('LeftFoot')][:, 1], P[:, ix('RightFoot')][:, 1])) * 1.08
    mv = np.linalg.norm(vel, axis=1) / ft; sel = mv > np.percentile(mv, 40)  # moving frames only
    for side in ['Right', 'Left']:
        sh, el, ha = P[:, ix(f'{side}Arm')], P[:, ix(f'{side}ForeArm')], P[:, ix(f'{side}Hand')]
        uarm = el - sh; fore = ha - el
        swing = np.degrees(np.arctan2(np.einsum('ij,ij->i', uarm, F), -uarm[:, 1]))  # + = upper arm forward of vertical
        elbow = 180 - ang(-uarm, fore)  # 0 = straight
        hf = np.einsum('ij,ij->i', ha - H, F) / height; hu = (ha[:, 1] - H[:, 1]) / height
        leg = np.einsum('ij,ij->i', P[:, ix(f'{side}Foot')] - H, F)
        corr = np.corrcoef(hf[sel], leg[sel])[0, 1]
        q = lambda x: f"{np.percentile(x[sel], 5):+.0f}..{np.percentile(x[sel], 95):+.0f}"
        print(f"{c} {kind:7s} {side:5s} 위팔 흔들림 {q(swing)}°  팔꿈치 굽힘 {q(elbow)}°  손 앞뒤 {np.percentile(hf[sel],5):+.2f}..{np.percentile(hf[sel],95):+.2f} 키  손 위아래 폭 {np.percentile(hu[sel],95)-np.percentile(hu[sel],5):.2f} 키  같은쪽 발과 상관 {corr:+.2f}")
