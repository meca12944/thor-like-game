import threading
from pl import anim
E=", STRICT three-quarter FRONT view facing the lower right the whole time, his face stays visible, he never turns to a side view or a straight front view, legs alternate cleanly, one crossing per step, ending back in this exact starting pose, same character design, hair, cape and bare sword as in the first frame, no effects"
J={'cyc_walk_dr':('key_walk_dr.png',"one complete natural human brisk walking cycle toward the lower right with long strides: heel strike, the body passes over the standing leg and rises slightly, the back leg swings forward past it, arms swing opposite to the legs, the sword stays low in the right hand"+E),
   'cyc_run_dr':('key_run_dr.png',"one complete natural human full-speed running cycle toward the lower right with long strides and a clear flight phase: the front foot lands under the body and pushes back, the other knee drives forward, arms pump opposite to the legs, the sword stays in the right hand trailing low"+E)}
ts=[threading.Thread(target=anim,args=(k,k,o,8,p,7)) for o,(k,p) in J.items()];[t.start() for t in ts];[t.join() for t in ts]
