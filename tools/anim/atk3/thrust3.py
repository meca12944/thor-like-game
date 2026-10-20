# all-thrust 3-hit (owner 2026-10-20: every hero attack is a thrust): 1 = quick jab, 2 = step-through level thrust, 3 = coiled long lunge.
# each hit starts in the previous hit's end pose. writes <outdir>/thrust_side.json {h1,h2,h3} (side skeletons, <=15 each) + sword angles.
# usage: thrust3.py <outdir> <east_kp.json>
import sys,os,json;os.environ['EAST_KP']=sys.argv[2];sys.argv=[sys.argv[0],sys.argv[1],sys.argv[2]]
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)));from design import *
T1=[R,
 dict(dx=-3,dy=1,lean=-4,Ra=[-35,75],La=[40,80],Rf=0,Lf=-12,sw=95),                  # chamber: hand pulled to the hip, blade level
 dict(dx=10,dy=4,lean=16,Ra=[88,90],La=[-40,-60],Rf=22,Lf=-14,sw=90),                # jab: arm straight ahead
 dict(dx=12,dy=4,lean=18,Ra=[90,90],La=[-42,-62],Rf=22,Lf=-14,sw=90),                # hold
 dict(dx=10,dy=3,lean=10,Ra=[40,85],La=[0,30],Rf=20,Lf=-14,sw=92)]                   # half retract
T2=[T1[-1],
 dict(dx=8,dy=7,lean=-6,Ra=[-45,70],La=[60,100],Rf=16,Lf=-16,sw=100),                # low chamber
 dict(dx=24,dy=3,lean=12,Ra=[92,90],La=[-50,-70],Rf=22,Lf=30,sw=90),                # back foot steps through, level thrust
 dict(dx=26,dy=3,lean=14,Ra=[92,90],La=[-52,-72],Rf=22,Lf=30,sw=90),                # hold
 dict(dx=22,dy=4,lean=2,Ra=[-20,80],La=[30,70],Rf=22,Lf=30,sw=95)]                   # pulled back into the chamber for hit 3
T3=[T2[-1],
 dict(dx=16,dy=11,lean=-14,Ra=[-70,60],La=[70,110],Rf=24,Lf=26,sw=80),               # coil: deep crouch, sword drawn far back at the hip
 dict(dx=40,dy=12,lean=28,Ra=[90,90],La=[-80,-100],Rf=60,Lf=8,sw=90),                # explode into a long lunge, arm and blade level
 dict(dx=42,dy=13,lean=30,Ra=[90,90],La=[-82,-102],Rf=60,Lf=8,sw=90),                # hold the lunge
 dict(dx=42,dy=13,lean=29,Ra=[89,90],La=[-82,-102],Rf=60,Lf=8,sw=90)]
OUT={'h1':build(T1,[4,2,3,3]),'h2':build(T2,[4,2,3,4]),'h3':build(T3,[5,2,4,3])}
json.dump({n:[kp(J) for J in L] for n,L in OUT.items()},open(sys.argv[1]+'/side_kp.json','w'))
json.dump({n:[{'hand':J['RIGHT ARM'],'sw':J['_sw']} for J in L] for n,L in OUT.items()},open(sys.argv[1]+'/side_sword.json','w'))
print({n:len(L) for n,L in OUT.items()})
