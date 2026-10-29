# 5등신 정면 얼굴을 한 칸씩 그리기 (회의 10-29 규칙). 머리 맨 위 y0 = 그림 45줄, 턱 y28 = 73줄, 얼굴 x0..13 = 123..136
import sys, numpy as np
from PIL import Image
src, dst, E = sys.argv[1], sys.argv[2], int(sys.argv[3])   # E = 눈 윗줄 (14/15/16)
C = {'L': (204, 154, 128), 'B': (186, 136, 114), 's': (146, 106, 100), 'd': (96, 66, 70),
     'k': (40, 30, 36), 'p': (44, 52, 72), 'H': (33, 31, 32)}
Y0, X0 = 45, 123
rows = {}
def face(y, s14): rows[y] = s14
# v2: 앞머리 끝은 가닥(들쭉날쭉), 턱 짧게, 그늘 쪽 2줄
for y in range(11, E - 3): face(y, 'H' * 14)
face(E - 3, 'HHdHHHdHHHdHHH')          # 앞머리 가닥 사이로 이마 그늘
face(E - 2, 'HkkkdHddHdkkkH')          # 눈썹 + 가운데 앞머리 끝 2가닥
face(E - 1, 'HssskBBBBksssd')          # 눈썹 안쪽 1칸 내림
face(E,     'HBkkkBBBBkkksd')          # 윗눈꺼풀 3칸 (왼쪽 끝 = 옆머리 가닥)
face(E + 1, 'sBspsBBBBspssd')          # 눈동자 1칸
for y in range(E + 2, 19): face(y, 'BLBBBBBBBBBssd' if y == 18 else 'BBBBBBBBBBBssd')
face(19, 'sBBBBBBsBBBssd'); face(20, 'HBBBBBssBBBssd')                       # 코 = 그림자만
face(21, 'HBBBBBBBBBBssH'); face(22, 'HBBBBBBBBBBsdH')
face(23, 'HHBBBsddsBBsHH')             # 입
face(24, 'HHBBBBssBBsdHH')             # 아랫입술 밑
face(25, 'HHHBBBBBBBsdHH'); face(26, 'HHHHsBBBBsdHHH')                       # 턱
face(27, 'HHHHHddddHHHHH'); face(28, 'HHHHHkddkHHHHH')                       # 턱 밑 그늘·목
A = np.asarray(Image.open(src).convert('RGBA')).astype(int).copy()
def put(y, x, ch):
    if ch == 'H':
        if A[y, x, 3] > 0 and A[y, x, :3].mean() < 70: return
        A[y, x] = (*C['H'], 255); return
    A[y, x] = (*C[ch], 255)
for y, s in rows.items():
    for i, ch in enumerate(s): put(Y0 + y, X0 + i, ch)
    for x in (X0 - 2, X0 - 1, X0 + 14, X0 + 15): put(Y0 + y, x, 'H')   # 옆머리가 얼굴을 ∩로 감쌈
Image.fromarray(A.astype(np.uint8)).save(dst)
