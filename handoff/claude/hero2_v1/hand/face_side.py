# 5등신 옆얼굴(오른쪽 봄)을 한 칸씩 그리기 (회의 10-29 규칙). 머리 맨 위 y0 = 그림 42줄, x칸 0 = 140, 얼굴 앞선 F = 151
import sys, numpy as np
from PIL import Image
src, dst, E = sys.argv[1], sys.argv[2], int(sys.argv[3])
C = {'L': (204, 154, 128), 'B': (186, 136, 114), 's': (146, 106, 100), 'd': (96, 66, 70),
     'k': (40, 30, 36), 'p': (44, 52, 72), 'H': (33, 31, 32)}
Y0, X0 = 42, 140
R = {}
for y in range(11, E - 2): R[y] = 'HHHHHHHHHHHH   ' if y == 11 else 'HHHHHHHHHHHHH  '   # 앞머리가 이마보다 1칸 앞으로
R[E - 2] = 'HHHHHHHkkkBBH  '                                  # 눈썹 2~3칸 + 앞머리 끝 1가닥
R[E - 1] = 'HHHHHHsssssd   '                                  # 눈두덩 그늘, 눈 자리 1칸 쏙
R[E]     = 'HHHHHBBkkkB    '                                  # 윗눈꺼풀 (앞선에서 2~4칸 안)
R[E + 1] = 'HHHHHBBBspBB   '                                  # 눈동자 1칸 (앞쪽)
for y in range(E + 2, 19): R[y] = 'HHHHBBBBBBBBB  '              # 코 1칸 나옴
R[19] = 'HHHHsBBBBBBBs  '                                     # 코끝 밑 그늘
R[20] = 'HHHHsBBBBBBs   '                                     # 코 밑 1칸 쏙
R[21] = 'HHHHsBBBBBBB   '                                     # 윗입술
R[22] = 'HHHHHsBBBBBB   '
R[23] = 'HHHHHsBBBBd    '                                     # 입 = 1칸 홈
R[24] = 'HHHHHHsBBBBB   '                                     # 아랫입술·턱 앞으로
R[25] = 'HHHHHHHssBBs   '                                     # 턱선 비스듬히
R[26] = 'HHHHHHHHdddd   '                                     # 턱 밑 그늘
A = np.asarray(Image.open(src).convert('RGBA')).astype(int).copy()
for y, s in R.items():
    for i, ch in enumerate(s):
        yy, xx = Y0 + y, X0 + i
        if ch == ' ': A[yy, xx] = 0; continue
        if ch == 'H':
            if A[yy, xx, 3] > 0 and A[yy, xx, :3].mean() < 70: continue
            A[yy, xx] = (*C['H'], 255); continue
        A[yy, xx] = (*C[ch], 255)
r_, g_, b_ = A[..., 0], A[..., 1], A[..., 2]
ear = (A[..., 3] > 0) & (r_ > g_) & (g_ > b_) & (r_ - b_ > 30) & (r_ > 100)
for yy in range(Y0 + 8, Y0 + 30):           # 머리 뒤 옛 귀 살색 → 새 살색 3단계
    for xx in range(X0 - 14, X0 + 4):
        if ear[yy, xx]:
            l = A[yy, xx, :3].mean(); A[yy, xx] = (*C['B' if l > 150 else 's' if l > 115 else 'd'], 255)
for y in range(8, E + 2):      # 얼굴 앞 허공에 남은 옛 머리카락 점 지우기
    A[Y0 + y, X0 + 15:X0 + 20] = 0
Image.fromarray(A.astype(np.uint8)).save(dst)
