# 맞기·사망·점프 (사장님 10-25 핵심 자세 방식, 교과서 0부 5·6번): 핵심 자세 1장(편집 10) + 서기→핵심 사이 장(4). 점프는 핵심(공중)→착지 사이 장(4) 더. 사망은 서기→쓰러짐 8장(8)
import subprocess,sys,os
T=" Keep the exact same character design and body proportions (same head size, same face, same long black hair, dark coat with bronze shoulder armor, dark red cape lining, brown boots), same colors, size and pixel art style, full body, empty hands, no weapon, no effects, no blood, no motion lines, no shadow."
J={
'hurt_down':('idle_down.png',"HIT REACTION pose, STRICT front view facing the viewer: he flinches backward from a hit to the chest, upper body bent back a little, head tilted back, shoulders raised, knees slightly bent, feet still under the body, arms pulled in close to the body, eyes squeezed shut.","gets hit and flinches back, front view",None),
'hurt_right':('idle_right.png',"HIT REACTION pose, STRICT side view facing RIGHT: he is knocked backward by a hit from the front, upper body bent back away to the left, head jerked back, the back foot taking his weight, front foot lifted slightly, arms pulled in close to the body, the hair and cape swing forward.","gets hit from the front and recoils backward, side view",None),
'hurt_up':('idle_up.png',"HIT REACTION pose, STRICT straight back view, face not visible: he is hit in the back, upper body arched forward away from the viewer, shoulders hunched up, head down, knees slightly bent, arms pulled in close to the body, the cape flaps up.","gets hit in the back and flinches forward, back view",None),
'jump_down':('idle_down.png',"JUMP pose in mid-air, STRICT front view facing the viewer: both knees tucked up together under the body, feet off the ground and close together, arms close to the sides, the cape and hair lifted up by the jump.","jumps up from a small crouch into the air, front view","lands softly with bent knees and stands up again, front view"),
'jump_dr':('idle_dr.png',"JUMP pose in mid-air, three-quarter view facing DOWN-RIGHT: both knees tucked up together under the body, feet off the ground and close together, arms close to the sides, the cape and hair lifted up.","jumps up from a small crouch into the air, three-quarter front view","lands softly with bent knees and stands up again, three-quarter front view"),
'jump_right':('idle_right.png',"JUMP pose in mid-air, STRICT side view facing RIGHT: both knees tucked up together under the body, feet off the ground and close together, arms close to the sides, the cape and hair lifted up behind.","jumps up from a small crouch into the air, side view","lands softly with bent knees and stands up again, side view"),
'jump_ur':('idle_ur.png',"JUMP pose in mid-air, three-quarter BACK view facing UP-RIGHT, face not visible: both knees tucked up together under the body, feet off the ground and close together, arms close to the sides, the cape and hair lifted up.","jumps up from a small crouch into the air, three-quarter back view","lands softly with bent knees and stands up again, three-quarter back view"),
'jump_up':('idle_up.png',"JUMP pose in mid-air, STRICT straight back view, face not visible: both knees tucked up together under the body, feet off the ground and close together, arms close to the sides, the cape lifted up.","jumps up from a small crouch into the air, back view","lands softly with bent knees and stands up again, back view"),
'rjump_right':('../se_test/run_r3/002.png',"RUNNING LONG JUMP pose in mid-air, STRICT side view facing RIGHT: leaping forward, front leg stretched forward, back leg bent behind, both feet off the ground, torso leaning forward, arms close to the body, the cape and hair streaming back.","takes off from running into a long forward leap, side view","lands from the leap onto the front foot and keeps running, side view"),
}
DEATH=('idle_right.png',"DEFEATED pose, lying on the ground: he has collapsed and lies horizontally on his side low on the ground, facing right, eyes closed, the cape spread over him, body length the same as when standing.","collapses and falls to the ground, side view")
k=sys.argv[1]
if k=='death_right':
    src,ep,act=DEATH
    if not os.path.exists(f'key_{k}.png'): subprocess.run(['python3','edit_pose.py',src,f'key_{k}.png',k,ep+T,'7'],check=True)
    if not os.path.exists(f'in_{k}/008.png'): subprocess.run(['python3','tween.py',src,f'key_{k}.png',f'in_{k}','8',act+": knees buckle, he drops to his knees and falls onto his side, same side view the whole time, no effects",'7'],check=True)
else:
    src,ep,a_in,a_out=J[k]
    if not os.path.exists(f'key_{k}.png'): subprocess.run(['python3','edit_pose.py',src,f'key_{k}.png',k,ep+T,'7'],check=True)
    if not os.path.exists(f'in_{k}/004.png'): subprocess.run(['python3','tween.py',src,f'key_{k}.png',f'in_{k}','4',a_in+", same view the whole time, no effects",'7'],check=True)
    if a_out and not os.path.exists(f'out_{k}/004.png'):
        end=src if k!='rjump_right' else '../se_test/run_r3/006.png'
        subprocess.run(['python3','tween.py',f'key_{k}.png',end,f'out_{k}','4',a_out+", same view the whole time, no effects",'7'],check=True)
print('done',k)
