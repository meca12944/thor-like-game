import threading
from pl import edit
T=" Keep the exact same character design, face, colors, the long black hair hanging down as in the original, the dark coat with gold trim, gold shoulder armor, the red-lined cape hanging behind him (not spread out), size and the sword, full body, human proportions, no effects."
J={
 'key_walk_d2':('src_walk_d.png',"Natural brisk walking pose toward the viewer, straight front view, face visible, mid-stride contact: his RIGHT leg (on the left side of the image) steps forward toward the viewer, heel touching the ground, that foot lower in the image; his LEFT leg is behind him, knee slightly bent, heel lifted, that foot higher in the image. The feet stay under the hips about hip width apart, legs NOT spread sideways, not crossed. Hips level, torso upright, arms swing gently opposite to the legs, the sword held low in the right hand pointing down."+T),
 'key_run_d2':('src_run_d.png',"Natural human RUNNING pose toward the viewer, straight front view, face visible: his RIGHT knee (on the left side of the image) drives up and forward toward the viewer, thigh raised, foot off the ground under the knee; his LEFT leg pushes off behind him, nearly straight, only the toes touching the ground, that foot higher in the image. The legs stay under the hips, not spread sideways. Torso leaning slightly forward, both arms at his sides, neither hand raised above the chest, the sword in the right hand pointing down."+T),
}
ts=[threading.Thread(target=edit,args=(s,k+'.png',p,11)) for k,(s,p) in J.items()];[t.start() for t in ts];[t.join() for t in ts]
