# 인게임 = 최신만 (팀장 10-26): 옛 주인공 시트 지우고 sheets 다시 매김 → [0 새 그록 주인공, 1 시전 마법진 castfx]. (castfire 는 index.html CFIRE 가 실행 때 붙임)
import sys,json;sys.path.insert(0,sys.argv[2])
from h8lib import load,save
R=sys.argv[1];s,j,k,H=load(R);sh=H['sheets'];NEW=sh.index('anim/hero_grok_0.webp');FX=sh.index('anim/hero8_castfx.webp')
mp={NEW:0,FX:1}
H['cells']=[H['cells'][NEW],H['cells'][FX]];H['sheets']=['anim/hero_grok_0.webp','anim/hero8_castfx.webp']
for n,L in H['anims'].items():
    for f in L:
        assert f[0] in mp,(n,f);f[0]=mp[f[0]]
        for i in (3,5):
            if len(f)>i and f[i]>=0: assert f[i] in mp,(n,f);f[i]=mp[f[i]]
H['grip']={('%d:%s'%(mp[int(a.split(':')[0])],a.split(':')[1])):v for a,v in H.get('grip',{}).items() if int(a.split(':')[0]) in mp}
H['bare']=[0];H['nsSheets']={}
for key in [x for x in H if x.startswith('_') and x not in ('_doc','_grok_note','_fix2_note','_atk_note','_fix3_note','_matchold_note','_grok81_note','_4dir_note','_clean_note')]: del H[key]
H['_doc']='새 그록 주인공 아틀라스 (10-26 인게임 = 최신만: 옛 hero8 시트·동작 지움). sheets 0 = 주인공 4방향 그림, 1 = 시전 마법진. 방향 = down·right(왼쪽 뒤집기)·up. 만든 과정 handoff/claude/hero_grok_v1 · hero_fix2 · hero_match_old'
save(R,s,j,k,H);print(H['sheets'],len(H['cells'][0]),len(H['cells'][1]),len(H['grip']))
