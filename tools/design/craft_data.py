# -*- coding: utf-8 -*-
# 재료 · 드롭 테이블 · 대장간 · 제작 레시피. towns_data.py 끝에서 import 후 make_recipes() 호출.
# icon: shape(아이콘 모양) + color(주색). 아이콘 시트 ui_materials.png(32x32)용 묘사.
AREA_NAMES={1:'시작의 숲',2:'수정 동굴',3:'모래 사막',4:'피라미드',5:'산호 바다',6:'해안 절벽',7:'화산 성채',8:'설산 뇌전 탑',9:'어둠 신전',10:'마룡의 둥지'}
SHAPE={'hide':'접힌 가죽 조각','bone':'뼈·뿔 조각','crystal':'각진 결정','essence':'빛나는 방울 병','cloth':'둘둘 만 천','wood':'나뭇가지 묶음','metal':'금속 덩이','shell':'껍데기 조각','core':'맥동하는 구체','token':'문장이 새겨진 패','scrap':'잡동사니'}
# 지역별: 공통 재료(모든 몹 저확률) + 몹 8종의 대표 재료 (몹 이름, 재료 id, 재료 이름, 종류, 색)
AREAS={
 1:dict(shared=('m_a1_shared','초록 정기 조각','essence','#7ccf3a'),mobs=[
  ('독버섯','m_spore','독버섯 포자','essence','#b04ac0'),('뿔토끼','m_rabbit_horn','뿔토끼 뿔','bone','#f0e0c0'),('말벌','m_wasp_sting','말벌 독침','bone','#f0c020'),
  ('멧돼지','m_boar_hide','멧돼지 가죽','hide','#6a4a30'),('호박 허수아비','m_pumpkin_vine','호박 덩굴','cloth','#e08a20'),('숲 슬라임','m_forest_gel','숲 슬라임 젤','essence','#7ccf3a'),
  ('도토리 다람쥐','m_acorn_shell','단단한 도토리 껍질','wood','#a06a30'),('나무 정령 새싹','m_sprout_wood','정령 새싹 가지','wood','#5aa84a')]),
 2:dict(shared=('m_a2_shared','동굴 수정 파편','crystal','#5ee0e0'),mobs=[
  ('가시덩굴','m_thorn_vine','가시덩굴 줄기','wood','#4a7a3a'),('박쥐','m_bat_wing','박쥐 날개','hide','#4a3a5a'),('수정 딱정벌레','m_beetle_shell','수정 딱정벌레 껍질','shell','#80e0ff'),
  ('동굴 거미','m_spider_silk','거미 명주실','cloth','#e8e8f0'),('곡괭이 바위도깨비','m_goblin_pick','도깨비 곡괭이 날','metal','#8a8a90'),('반딧불 지렁이','m_glow_gland','반딧불 발광샘','essence','#e8ff80'),
  ('동굴 두더지','m_mole_claw','두더지 발톱','bone','#d8c8b0'),('수정 슬라임','m_crystal_gel','수정 슬라임 핵','crystal','#a0f0ff')]),
 3:dict(shared=('m_a3_shared','사막 모래철','metal','#c0a060'),mobs=[
  ('전갈','m_scorpion_sac','전갈 독주머니','essence','#ffa020'),('선인장 골렘','m_cactus_spine','선인장 가시','wood','#5a9a3a'),('모래 독사','m_viper_scale','독사 비늘','hide','#c0a050'),
  ('대머리 독수리','m_vulture_feather','독수리 깃털','cloth','#5a4a3a'),('사막 도적','m_bandit_cloth','도적의 터번천','cloth','#d8c090'),('모래 정령','m_sand_dust','모래 정령 가루','essence','#f0d890'),
  ('낙타 거북','m_camel_shell','낙타 거북 등딱지','shell','#a08050'),('개미귀신','m_antlion_jaw','개미귀신 턱','bone','#8a6a40')]),
 4:dict(shared=('m_a4_shared','저주받은 금박','metal','#ffc820'),mobs=[
  ('미라','m_mummy_wrap','미라 붕대','cloth','#e0d8b0'),('스카라베 떼','m_scarab_wing','스카라베 날개딱지','shell','#1a6a5a'),('아누비스 경비병','m_anubis_blade','아누비스 창날','metal','#ffd860'),
  ('저주 항아리','m_cursed_shard','저주 항아리 파편','scrap','#6a4a8a'),('뱀 머리 석상','m_statue_gem','석상 눈알 보석','crystal','#40e0a0'),('고양이 망령','m_ghostcat_fur','망령 고양이 털','essence','#c0c0ff'),
  ('함정 석판 골렘','m_slab_chunk','석판 골렘 조각','metal','#a09080'),('모래 해골 궁수','m_bowstring','해골 궁수 활시위','cloth','#d8d0c0')]),
 5:dict(shared=('m_a5_shared','심해 비늘 조각','shell','#3080c0'),mobs=[
  ('어인','m_fishman_scale','어인 비늘','hide','#30a090'),('해파리','m_jelly_tendril','해파리 촉수','essence','#e0a0ff'),('가시 복어','m_puffer_spine','복어 가시','bone','#f0e080'),
  ('상어 돌격병','m_shark_tooth','상어 이빨','bone','#f8f8f8'),('문어 먹물병','m_ink_sac','문어 먹물주머니','essence','#2a1a3a'),('전기 뱀장어','m_eel_organ','뱀장어 발전기관','essence','#ffe040'),
  ('아귀','m_angler_lure','아귀 등불','crystal','#80ffe0'),('소라게','m_conch_shell','소라 껍데기','shell','#ffb0a0')]),
 6:dict(shared=('m_a6_shared','바다 소금 결정','crystal','#f0f8ff'),mobs=[
  ('집게 병사','m_claw_shell','집게 껍질','shell','#c04a2a'),('갈매기','m_gull_feather','갈매기 깃털','cloth','#ffffff'),('해적 해골','m_pirate_bone','해적 해골 뼈','bone','#e0d8c0'),
  ('따개비 골렘','m_barnacle_plate','따개비 판','shell','#8a9a8a'),('바다 거북 방패병','m_turtle_plate','바다거북 등판','shell','#4a7a4a'),('파도 정령','m_wave_drop','파도 정령 물방울','essence','#60c0ff'),
  ('불가사리','m_starfish_flesh','불가사리 재생살','hide','#ff8a6a'),('해적 앵무새','m_parrot_plume','앵무새 꽁지깃','cloth','#30c040')]),
 7:dict(shared=('m_a7_shared','용암석 조각','metal','#ff6a00'),mobs=[
  ('용암 슬라임','m_lava_gel','용암 슬라임 핵','essence','#ff8a20'),('불 도롱뇽','m_fire_gland','도롱뇽 불주머니','essence','#ff4a10'),('용암 바위 골렘','m_magma_heart','용암 바위 심','metal','#a03a10'),
  ('불꽃 임프','m_imp_trident','임프 삼지창 끝','metal','#c02020'),('잿불 불사조 새끼','m_ash_feather','불사조 잿깃','cloth','#ffb040'),('저주받은 갑옷','m_cursed_plate','저주 갑옷 파편','metal','#3a3a46'),
  ('화염 사냥개','m_hound_fang','화염 사냥개 송곳니','bone','#ffd0a0'),('흑요석 궁수','m_obsidian_tip','흑요석 화살촉','crystal','#20202a')]),
 8:dict(shared=('m_a8_shared','영구 서리 결정','crystal','#a0d8ff'),mobs=[
  ('서리 늑대','m_wolf_pelt','서리 늑대 모피','hide','#c0c8d8'),('얼음 슬라임','m_ice_gel','얼음 슬라임 젤','essence','#c0f0ff'),('설인 새끼','m_yeti_fur','설인 새끼 털','hide','#f0f0f8'),
  ('서리 요정','m_fairy_wing','서리 요정 날개','cloth','#e0f8ff'),('펭귄 기사','m_penguin_helm','펭귄 기사 깃털 투구','metal','#2a3a5a'),('뇌운 새','m_storm_feather','뇌운 새 깃털','cloth','#ffe040'),
  ('얼음 거북','m_ice_shell','얼음 거북 등딱지','shell','#80b0e0'),('폭풍 가고일','m_gargoyle_shard','가고일 날개 석편','metal','#6a6a7a')]),
 9:dict(shared=('m_a9_shared','공허의 먼지','essence','#7a2ad0'),mobs=[
  ('해골 창병','m_skeleton_femur','해골 창병 대퇴골','bone','#e8e0d0'),('고블린','m_goblin_pouch','고블린 도둑 주머니','cloth','#6a8a3a'),('보라 도깨비불','m_wisp_essence','도깨비불 정수','essence','#b46cff'),
  ('어둠 마법사','m_grimoire_page','마도서 쪽','cloth','#3a1a4a'),('그림자 암살자','m_shadow_cloth','그림자 천','cloth','#14141e'),('공허 눈알','m_void_lens','공허 눈알 수정체','crystal','#9a7aff'),
  ('가고일 석상','m_heartstone','가고일 심장석','metal','#5a5a6a'),('저주 인형','m_doll_stuffing','저주 인형 솜','cloth','#d8a0a0')]),
}
# 챔피언 (지역, 이름, 재료 id, 재료 이름, 종류, 색) — 기존 강화 재료(CHAMPION_DROPS)는 그대로 유지
CHAMPS=[
 (1,"거대 왕멧돼지 '돌엄니'",'m_c_tusk','돌엄니의 거대 엄니','bone','#fff8e0'),(1,'여왕 말벌','m_c_queen_gland','여왕벌 왕관 독샘','essence','#ffd020'),
 (2,'흡혈 박쥐왕','m_c_blood_wing','박쥐왕의 피날개','hide','#a00010'),(2,'광부 도깨비 대장','m_c_fuse','도깨비 대장의 폭약 심지','scrap','#ff6a20'),
 (3,"황금 전갈 '태양침'",'m_c_sun_tail','태양침의 황금 꼬리','metal','#ffcf40'),(3,'사막 도적 두목','m_c_silk_cape','도적 두목의 비단 망토천','cloth','#d01030'),
 (4,'쌍둥이 아누비스','m_c_twin_mask','쌍둥이의 황금 가면 조각','metal','#ffd860'),(4,'저주받은 대신관','m_c_curse_staff','대신관의 저주 홀 조각','crystal','#7a2ad0'),
 (5,'백상어 장군','m_c_shark_fin','백상어 장군의 지느러미','hide','#9aaabb'),(5,'심해 아귀 여왕','m_c_abyss_lamp','아귀 여왕의 심해 등불','crystal','#80ffe0'),
 (6,'유령 해적 선장','m_c_cursed_coin','유령 선장의 저주 금화','metal','#c0a050'),(6,'거대 바닷가재','m_c_great_claw','바닷가재의 대집게','shell','#ff5a3a'),
 (7,'용암 거인 수문장','m_c_giant_heart','용암 거인의 심장석','metal','#ff6a00'),(7,'화염 마녀','m_c_flame_hair','화염 마녀의 불꽃 머리칼','cloth','#ff2a4a'),
 (8,'어미 설인','m_c_silver_fur','어미 설인의 은빛 털','hide','#f0f4ff'),(8,'번개 그리폰','m_c_thunder_plume','그리폰의 뇌전 깃털','cloth','#ffe040'),
 (9,'그림자 쌍검사','m_c_shadow_edge','쌍검사의 그림자 칼날','metal','#3a3a5a'),(9,'공허의 수문장','m_c_gravity_core','수문장의 중력핵','core','#7a2ad0'),
]
BOSSES=[(1,'이끼 수정 골렘','m_core_moss','이끼 수정 핵','#6ad0c0'),(2,'수정 여왕거미','m_core_spider','여왕거미의 수정 심장','#a070e0'),(3,'모래 대지렁이','m_core_sandworm','대지렁이의 모래 핵','#f0d890'),
 (4,'황금가면 미라왕','m_core_pharaoh','미라왕의 황금 심장','#ffc820'),(5,'심해 크라켄 뱀','m_core_kraken','크라켄의 심연 핵','#9a4ac0'),(6,'산호 거대게','m_core_crab','거대게의 산호 심장','#ff7a5a'),
 (7,'화염검 흑기사','m_core_hellfire','흑기사의 업화 핵','#ff2a00'),(8,'뇌전 와이번','m_core_storm','와이번의 뇌전 핵','#ffe040'),(9,'공허의 대사제','m_core_void','대사제의 공허 핵','#7a2ad0'),
 (10,'머리 셋 달린 그림자 마룡','m_core_dragon','마룡의 삼두 핵','#b070ff')]
BASIC=[('m_iron_ingot','철 주괴',1,'metal','#9aa8b8',15),('m_leather_strap','질긴 가죽끈',1,'hide','#8a5a2e',10),('m_hardwood','단단한 목재',1,'wood','#9a6a36',8),
 ('m_steel_ingot','강철 주괴',3,'metal','#7fb0e0',45),('m_magic_thread','마력 실',4,'cloth','#c0a0ff',60),('m_blacksteel_ingot','흑철 주괴',6,'metal','#3a3a44',120),('m_mithril_ingot','미스릴 주괴',9,'metal','#80e0ff',320)]
TOWNSFOLK_MATS=[('tf_cloth','피 묻은 천 조각','cloth','#a03030'),('tf_scrap','녹슨 쇠붙이','scrap','#8a5a3a'),('tf_herb','말린 약초 다발','wood','#7a9a4a'),('tf_tool','손때 묻은 연장','metal','#8a8a90'),
 ('tf_jewel','작은 장신구','crystal','#ffd860'),('tf_page','찢어진 책장','cloth','#e8d8b0'),('tf_holy','성물 조각','crystal','#fff8e0'),('tf_soul','원한 서린 혼석','core','#6a0a2a')]
STRONG_TOKENS={'A':('tk_kalbaram','칼바람의 징표'),'B':('tk_sol','매눈 솔의 징표'),'H':('tk_gomsoe','곰쇠의 징표'),'G':('tk_zahra','자흐라의 징표'),
 'F':('tk_mago','마고의 징표'),'E':('tk_garon','가론의 징표'),'C':('tk_hanbing','한빙의 징표'),'D':('tk_grim','그림의 징표')}

MATERIALS={}; MOB_DROPS=[]
def M(id,name,tier,typ,color,sources,sell,note=None):
    MATERIALS[id]=dict(id=id,name=name,tier=tier,type=typ,sources=sources,sell=sell,icon=dict(shape=SHAPE[typ],color=color),**({'note':note} if note else {}))
for i,(id,n,t,ty,c,p) in enumerate(BASIC):
    M(id,n,t,ty,c,[dict(kind='forge_shop',where='대장간에서 구매',rate=None,price=p)],p//2)
for a,d in AREAS.items():
    sid,sn,sty,sc=d['shared']
    M(sid,sn,a,sty,sc,[dict(kind='mob',where=f'{a}지역 일반 몹 전부',rate=12),dict(kind='champion',where=f'{a}지역 챔피언',rate='2개 확정')],a*12)
    for mob,id,n,ty,c in d['mobs']:
        rate=55 if ty in('hide','cloth','essence') else 45
        M(id,n,a,ty,c,[dict(kind='mob',where=f'{a}지역 {mob}',rate=rate)],a*8)
        MOB_DROPS.append(dict(area=a,mob=mob,kind='normal',drops=[(id,rate),(sid,12)]+([('scroll_area%d'%a,1)] if mob==d['mobs'][0][0] else [])))
for a,ch,id,n,ty,c in CHAMPS:
    M(id,n,a,ty,c,[dict(kind='champion',where=f'{a}지역 {ch}',rate='첫 격파 2개 확정, 이후 35%')],a*60)
    MOB_DROPS.append(dict(area=a,mob=ch,kind='champion',drops=[(id,35),(AREAS[a]['shared'][0],100),('enh_tier%d'%((a+1)//2),'CHAMPION_DROPS 표')]))
for a,b,id,n,c in BOSSES:
    M(id,n,a,'core',c,[dict(kind='boss',where=f'{a}지역 {b}',rate=100)],a*300,'보스 고유 핵. 핵 레시피(전설)는 E 마스터 대장간(또는 마염 대장간)에서만 제작')
    MOB_DROPS.append(dict(area=a,mob=b,kind='boss',drops=[(id,100)]+([(AREAS[a]['shared'][0],100)] if a<10 else [('x_m_a9_shared',100)])))
# 10지역 강화판: 공통 재료·챔피언 재료의 「타락한」 변형
for a in range(1,10):
    sid,sn,sty,sc=AREAS[a]['shared']
    M('x_'+sid,'타락한 '+sn,10,sty,'#7a2ad0',[dict(kind='mob',where=f'10지역 강화판 {a}지역 몹 전부',rate=15)],a*12*6,'보랏빛 오라가 감도는 변형')
    for mob,id,n,ty,c in AREAS[a]['mobs']:
        MOB_DROPS.append(dict(area=10,mob='강화 '+mob,kind='enhanced',drops=[(id,40),('x_'+sid,15)]))
for a,ch,id,n,ty,c in CHAMPS:
    M('x_'+id,'타락한 '+n,10,ty,'#7a2ad0',[dict(kind='champion',where=f'10지역 강화 {ch}',rate=30)],a*60*4)
    MOB_DROPS.append(dict(area=10,mob='강화 '+ch,kind='enhanced_champion',drops=[('x_'+id,30),(id,60),('enh_tier5','CHAMPION_DROPS 표')]))
for id,n,ty,c in TOWNSFOLK_MATS:
    M(id,n,1 if id!='tf_soul' else 5,ty,c,[dict(kind='townsfolk',where='마을 사람 (악의 길 전용)',rate='NPC별')],5 if id!='tf_soul' else 150,
      '마을 사람을 죽여야 나온다. 선악 감소는 살해 페널티(TOWNSFOLK_COMBAT.md) 그대로' if id!='tf_soul' else '모든 살해 NPC 15%, 마을 파괴 보상. 마염 대장간에서 금화 대신 쓸 수 있음')
for t,(id,n) in STRONG_TOKENS.items():
    M(id,n,8,'token','#ffd860',[dict(kind='strongman',where=f'{t} 마을 강자 (살려 주면 건네받음 / 죽이면 시신에서)',rate=100)],0,'원탁의 심연 입장 조건. 팔 수 없음')
M('m_aeon_core','영겁의 핵',10,'core','#e8f0ff',[dict(kind='boss',where='원탁의 주인 아스란',rate=100)],5000,'선대의 부러진 검 복원 레시피 재료')
M('m_round_shard','원탁의 파편',10,'token','#c0c8d8',[dict(kind='boss',where='원탁의 주인 아스란',rate=100)],800)
# 레시피 두루마리 (지역별 희귀 레시피 해금용)
for a in range(1,11):
    M('scroll_area%d'%a,f'{a}지역 레시피 두루마리 조각',a,'cloth','#e8d6b0',[dict(kind='mob',where=f'{a}지역 첫 번째 몹 1%, 보스 첫 격파 확정',rate=1)],0,'5조각 모으면 그 지역 희귀 장비 레시피 1개 해금 (대장장이가 해독)')

def npc_material(role):
    for k,v in [('대장장이','tf_tool'),('무기','tf_tool'),('조선공','tf_tool'),('광부','tf_tool'),('반장','tf_tool'),('약','tf_herb'),('약초','tf_herb'),('의원','tf_herb'),
                ('외형','tf_jewel'),('상인','tf_jewel'),('시장','tf_jewel'),('보석','tf_jewel'),('공방','tf_jewel'),('학자','tf_page'),('서고','tf_page'),('측량','tf_page'),('점술','tf_page'),('예언','tf_page'),
                ('사제','tf_holy'),('주교','tf_holy'),('성녀','tf_holy'),('수도승','tf_holy'),('경비','tf_scrap'),('기사','tf_scrap'),('선장','tf_scrap'),('사냥','tf_scrap')]:
        if k in role: return v
    return 'tf_cloth'
# ---------------------------------------------------------------- 대장간
FORGE_RULES=dict(
 services=['제작: 레시피 + 재료 + 금화. 대장간 등급 이상의 티어만 제작 가능','강화: 기존 +0~+9 시스템 (SYSTEMS.md 1장, 마을별 최대 단계)',
           '수리: 장비 내구도(100)는 쓰러질 때 -10, 산성·녹 공격에 맞을 때 -2. 0이 되면 능력치 절반. 수리비 = 티어 × 20 금화 / 내구도 10',
           '분해: 장비를 재료로 되돌림. 기본 재료·지역 재료의 50%(내림) 반환, 핵·징표는 반환 안 함. 강화 단계당 해당 강화 재료 1개 추가 반환',
           '판매: 장비는 기준가의 40%, 재료는 재료별 판매가'],
 success=[('티어 1~6',100),('티어 7~8',90),('티어 9',80),('티어 10·핵 레시피',70)],
 fail='실패하면 금화 전액과 핵이 아닌 재료 절반을 잃는다. 핵은 실패해도 잃지 않는다. E 마스터 대장간은 성공률 +10%p (상한 100%).',
 unlock=['기본: 그 마을 상점에서 파는 장비의 레시피는 대장장이에게 말을 걸면 바로 배운다',
         '대장간 의뢰(각 마을 ⑪, E는 E3 장인의 시험): 완료하면 대장간 등급 +1 (E는 10으로)',
         '레시피 두루마리: 희귀 장비 레시피. 보스 첫 격파 시 그 보스 장비 두루마리 확정, 챔피언 15%, 잠수 지점 장비는 같은 지점에서 두루마리, 퀘스트 장비는 퀘스트 보상과 함께. 지역 두루마리 조각 5개로도 해독 가능',
         '핵 레시피(전설): 보스 핵이 있어야 하고 E 마스터 대장간(또는 마왕의 길의 마염 대장간)에서만 제작'],
 upgrade='아래 티어 장비를 재료로 넣는 「승급 제작」: 같은 분류·같은 종류의 바로 아래 장비 1개를 넣으면 기본·지역 재료가 40% 줄어든다(핵·챔피언 재료는 그대로). 강화 단계는 1단계 낮아진 채로 이어진다.',
)
FORGES=[
 dict(town='A',npc='a_smith',name='강철의 대장간',tier=1,tier_after=2,quest='A11',sells=['m_iron_ingot','m_leather_strap','m_hardwood']),
 dict(town='B',npc='b_smith',name='담금의 물레 대장간',tier=2,tier_after=3,quest='B11',sells=['m_iron_ingot','m_leather_strap','m_hardwood']),
 dict(town='H',npc='h_smith',name='불꽃 망치 제련소',tier=2,tier_after=3,quest='H11',sells=['m_iron_ingot','m_leather_strap','m_hardwood','m_steel_ingot']),
 dict(town='G',npc='g_smith',name='칼림의 곡도 공방',tier=3,tier_after=4,quest='G11',sells=['m_iron_ingot','m_leather_strap','m_steel_ingot','m_magic_thread']),
 dict(town='F',npc='f_smith',name='너울의 조선 대장간',tier=5,tier_after=6,quest='F11',sells=['m_steel_ingot','m_leather_strap','m_hardwood','m_magic_thread','m_blacksteel_ingot']),
 dict(town='E',npc='e_master',name='불칼의 마스터 대장간',tier=7,tier_after=10,quest='E3',sells=['m_steel_ingot','m_magic_thread','m_blacksteel_ingot','m_mithril_ingot'],master=True),
 dict(town='C',npc='c_smith',name='서리망치 대장간',tier=7,tier_after=8,quest='C11',sells=['m_steel_ingot','m_magic_thread','m_blacksteel_ingot']),
 dict(town='D',npc='d_smith',name='왕실 무기고',tier=8,tier_after=9,quest='D11',sells=['m_steel_ingot','m_magic_thread','m_blacksteel_ingot','m_mithril_ingot']),
]
FORGE_QUESTS={
 'A':('A11','강철의 첫 망치','강철은 필멸자가 쓸 검을 직접 벼려 보고 싶어 한다. 「검은 휘두르는 놈 손을 닮지. 재료는 네 손으로 구해 와.」','멧돼지 가죽 5 + 단단한 도토리 껍질 3 + 철 주괴 3 전달','대장간 등급 2 + 레시피 「돌엄니 송곳검」 두루마리'),
 'B':('B11','물레 망치의 비밀','담금은 물레방아 힘으로 망치를 돌리는 장치를 고치고 싶다.','가시덩굴 줄기 4 + 박쥐 날개 4 + 강철 주괴 1','대장간 등급 3 + 레시피 「흡혈 박쥐왕의 반지」 두루마리'),
 'H':('H11','수정 담금질','단단은 수정 슬라임 핵으로 담금질하면 날이 빛난다고 믿는다.','수정 슬라임 핵 5 + 동굴 수정 파편 6','대장간 등급 3 + 투척 곡괭이 강화 레시피'),
 'G':('G11','곡도의 혼','칼림은 아버지가 남긴 미완성 곡도 도면을 완성하고 싶다. 도면의 마지막 장은 피라미드에 있다.','피라미드 벽화 방에서 도면 조각 획득 + 저주받은 금박 6','대장간 등급 4 + 레시피 「태양침 독검」 두루마리'),
 'F':('F11','용골 수리','너울은 마고의 배 용골을 고쳐 주기로 했다. 바다거북 등판과 따개비 판이 필요하다.','바다거북 등판 5 + 따개비 판 5 + 흑철 주괴 2','대장간 등급 6 + 레시피 「백상어 지느러미 방패」 두루마리'),
 'C':('C11','얼지 않는 쇠','혹한은 영구 서리 결정으로 얼지 않는 쇠를 만들려 한다.','영구 서리 결정 8 + 서리 늑대 모피 4 + 흑철 주괴 3','대장간 등급 8 + 레시피 「설인 털 팔보호대」 두루마리'),
 'D':('D11','왕실 무기고의 열쇠','백련은 봉인된 옛 무기고를 열고 싶다. 열쇠는 가고일 심장석으로 만든다.','가고일 심장석 4 + 미스릴 주괴 2','대장간 등급 9 + 레시피 「그림자 표창」 두루마리'),
}
CRAFT_ONLY={'w_hellfire':'m_core_hellfire','b_wyvern_scale':'m_core_storm','h_void_crown':'m_core_void','o_dragon_eye':'m_core_dragon'}
SLOT_PREF={'weapon':['metal','bone','crystal','shell'],'armor':['hide','cloth','shell'],'helmet':['metal','shell','hide','cloth'],
 'shield':['wood','shell','metal'],'throw':['bone','metal','wood'],'orb':['essence','crystal'],'ring':['crystal','essence'],'amulet':['crystal','essence'],'bracer':['hide','metal'],'boots':['hide','cloth']}
def _ingot(t): return 'm_iron_ingot' if t<=2 else 'm_steel_ingot' if t<=5 else 'm_blacksteel_ingot' if t<=8 else 'm_mithril_ingot'
def _area_mats(a,kind,n=2):
    a=min(max(a,1),9); pref=SLOT_PREF[kind]; mobs=AREAS[a]['mobs']; out=[]
    for ty in pref:
        for _,id,_,t,_ in mobs:
            if t==ty and id not in out: out.append(id)
    for _,id,_,_,_ in mobs:
        if id not in out: out.append(id)
    return out[:n]
def make_recipes(items,town_order):
    by={}; R={}
    for e in items:
        kind=e['slot'] if e['slot']!='offhand' else e['effect']['kind']
        by.setdefault((e['slot'],kind),[]).append(e)
    for e in items:
        t=e['tier']; slot=e['slot']; kind=slot if slot!='offhand' else e['effect']['kind']
        n=1 if slot in('helmet',) or kind in('ring','amulet') else 2
        mats=[(_ingot(t),max(1,t//2+n))]
        if kind in('shield','throw') and t<=4: mats.append(('m_hardwood',2))
        if slot=='armor' or kind in('bracer','boots'): mats.append(('m_leather_strap',2+t//3))
        if t>=4 and kind in('orb','ring','amulet','armor'): mats.append(('m_magic_thread',1+t//4))
        for i,m in enumerate(_area_mats(t if t<10 else 9,kind)): mats.append((m,3+t//2-i))
        mats.append((AREAS[min(t,9)]['shared'][0],2+t//3))
        if t==10: mats.append(('x_'+AREAS[9]['shared'][0],3))
        src=e['source']; where=src.get('where',''); core=None
        for a,ch,id,*_ in CHAMPS:
            if ch.split("'")[0].strip() in where or ch in where: mats.append((id,2))
        for a,b,id,*_ in BOSSES:
            if b in where: core=id
        if e['id'] in CRAFT_ONLY: core=CRAFT_ONLY[e['id']]
        if e['id']=='w_first_bearer': core='m_aeon_core'; mats.append(('m_round_shard',2))
        if e['id']=='b_shadow_garb': mats.append(('m_c_shadow_edge',1)); mats.append(('m_shadow_cloth',4))
        if src['type']=='dive': mats.append(('scroll_area%d'%min(t,10),2))
        if core: mats.append((core,1))
        coins=60+t*t*45+(800 if core else 0)
        need=t if not core else 10
        town=next((f['town'] for f in [x for o in town_order for x in FORGES if x['town']==o] if f['tier_after']>=need),'E')
        if core: town='E'
        succ=100 if t<=6 else 90 if t<=8 else 80 if t<=9 else 70
        if core: succ=70
        sib=sorted([x for x in by[(slot,kind)] if x['tier']<t],key=lambda x:x['tier'])
        up=sib[-1]['id'] if sib else None
        unlock=('상점 판매 마을 대장장이에게서 기본 습득' if src['type']=='shop' else
                '핵 레시피: 보스 첫 격파 시 두루마리 확정 + E 마스터 대장간' if core else
                f"레시피 두루마리 ({SRC_LABEL[src['type']]}: {where})")
        R['r_'+e['id']]=dict(id='r_'+e['id'],item=e['id'],materials=[dict(mat=m,count=c) for m,c in mats],coins=coins,forge_tier=need,town=town,
            success=succ,craft_only=e['id'] in CRAFT_ONLY,upgrade_from=up,unlock=unlock)
    return R
SRC_LABEL={'shop':'상점','boss':'보스','champion':'챔피언','mob':'일반 몹','quest':'퀘스트','dive':'잠수','craft':'제작 전용'}
M('scroll_first_bearer','레시피 두루마리: 선대의 부러진 검 복원',10,'cloth','#fff8e0',[dict(kind='boss',where='원탁의 주인 아스란',rate=100)],0,'「선대의 부러진 검」을 영겁의 핵으로 복원하는 레시피')
