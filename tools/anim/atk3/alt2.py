# hit-2 variant "가로베기": starts in hit-1's end pose, ends in the thrust's chambered stance (hit 3 = Linette-style thrust).
# usage: alt2.py <outdir> <east_kp.json>
import sys,os,json;os.environ['EAST_KP']=sys.argv[2];sys.argv=[sys.argv[0],sys.argv[1],sys.argv[2]]
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)));from design import *
A=[H1[-1],
 dict(dx=10,dy=4,lean=-6,Ra=[-75,-95],La=[40,70],Rf=22,Lf=-12,sw=-95),               # sword pulled back across the body at chest height
 dict(dx=16,dy=6,lean=8,Ra=[20,60],La=[-20,-40],Rf=24,Lf=-6,sw=60),                  # sweep starts, back foot slides in
 dict(dx=22,dy=6,lean=14,Ra=[88,92],La=[-40,-70],Rf=30,Lf=0,sw=92),                   # horizontal cut: arm and blade level, straight ahead
 dict(dx=22,dy=5,lean=10,Ra=[110,140],La=[-40,-70],Rf=30,Lf=0,sw=150),                # follow-through: blade swings on past the front
 dict(dx=14,dy=2,lean=4,Ra=[15,70],La=[25,60],Rf=22,Lf=-2,sw=125)]                    # pulled into the thrust chamber (hit 3 starts here)
F=build(A,[3,2,2,3,4])
json.dump([kp(J) for J in F],open(sys.argv[1]+'/side_h2b.json','w'))
D=json.load(open(sys.argv[1]+'/side_sword.json'));D['h2b']=[{'hand':J['RIGHT ARM'],'sw':J['_sw']} for J in F];json.dump(D,open(sys.argv[1]+'/side_sword.json','w'))
print('h2b',len(F))
