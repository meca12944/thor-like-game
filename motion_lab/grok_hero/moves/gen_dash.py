# 회피대시 (사장님 10-25 「핵심 자세부터」, 교과서 0부 5번): 방향마다 핵심 자세 1장(편집 10) + 서기→핵심(4) + 핵심→서기(4) = 18
# 교과서: 정면·대각선 대시는 발은 몸 밑, 무릎만 굽히고 상체만 숙임(다리 벌리면 게다리), 팔은 몸에 붙여 작게(벌리면 T자). 출발 순간이 가장 빠름 → 처음부터 숙인 자세
import subprocess,sys,os
T=" Keep the exact same character design and body proportions (same head size, same face, same long black hair, dark coat with bronze shoulder armor, dark red cape lining, brown boots), same colors, size and pixel art style, full body, empty hands, no weapon, no effects, no motion lines, no shadow."
ARMS=" Both arms stay close to the body (no T-pose, arms not spread)."
J={
'dash_right':('idle_right.png',"Fast evasive DASH pose, STRICT side view facing RIGHT: the body leans far forward low to the ground, the front knee deeply bent with the front foot planted ahead, the back leg stretched behind pushing off, torso low and forward, head forward, the long hair and the cape stream straight back behind him."+ARMS,"quick dash forward to the right"),
'dash_down':('idle_down.png',"Fast evasive DASH pose toward the viewer, STRICT straight front view: both feet stay under the body about hip width apart (not spread wide), knees bent in a low crouch, upper body leaning forward toward the viewer, head slightly down, the cape and hair flare out behind and to the sides."+ARMS,"quick dash toward the viewer, front view"),
'dash_dr':('idle_dr.png',"Fast evasive DASH pose, three-quarter view facing DOWN-RIGHT: the feet stay under the body, knees bent in a low crouch, the near leg stepping forward down-right, upper body leaning forward toward the bottom-right, the cape and hair stream back behind him."+ARMS,"quick dash diagonally down-right"),
'dash_ur':('idle_ur.png',"Fast evasive DASH pose, three-quarter BACK view facing UP-RIGHT, his face not visible: the feet stay under the body, knees bent in a low crouch, the far leg stepping forward up-right, upper body leaning forward toward the top-right, the cape and hair stream back toward the viewer."+ARMS,"quick dash diagonally away up-right, back view"),
'dash_up':('idle_up.png',"Fast evasive DASH pose running AWAY from the viewer, STRICT straight back view, face not visible: both feet under the body about hip width apart, knees bent in a low crouch, upper body leaning forward away from the viewer, the cape and long hair flare back toward the viewer."+ARMS,"quick dash away from the viewer, back view"),
}
k=sys.argv[1];src,ep,act=J[k]
if not os.path.exists(f'key_{k}.png'): subprocess.run(['python3','edit_pose.py',src,f'key_{k}.png',k,ep+T,'7'],check=True)
if not os.path.exists(f'in_{k}/004.png'): subprocess.run(['python3','tween.py',src,f'key_{k}.png',f'in_{k}','4',act+": from standing quickly drop into the low dash pose, same view the whole time, no effects",'7'],check=True)
if not os.path.exists(f'out_{k}/004.png'): subprocess.run(['python3','tween.py',f'key_{k}.png',src,f'out_{k}','4',act+": from the low dash pose rise back up to standing, same view the whole time, no effects",'7'],check=True)
print('done',k)
