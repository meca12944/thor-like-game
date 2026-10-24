# 동작별 칼 지우기 설정 (눈으로 보고 고른 값). 'anim/장' 키가 있으면 그 장만 따로.
#  ovr = 칼 양쪽에서 몸을 찾는 거리(망토 위를 지나던 칼 자리 메우기), gthr/back = 손 쪽 어두운 칼날 조각까지 지우기
#  axial = 칼 방향 앞뒤로 몸이 있으면 메움(칼이 정강이를 가리던 장), patch = 손으로 그린 메우기 다각형(256 캔버스 좌표)
CFG={'run_right':{'ovr':9},'run_up':{'gthr':55,'back':12},
     'walk_right/003':{'axial':6,'patch':[[(146,160),(159,160),(158,173),(145,173)]]},'walk_right/007':{'ovr':0,'axial':8}}
def cfg(k,f):return CFG.get(f'{k}/{f[:3]}',CFG.get(k,{}))
