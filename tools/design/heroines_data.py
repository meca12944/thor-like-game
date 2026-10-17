# -*- coding: utf-8 -*-
# 히로인(성인 여성 NPC) 6명 + 동료 서브퀘스트 + 호감도. gen_docs.py 가 HEROINES.md 와 towns.json(heroines, 각 마을 quests)에 반영.
COMPANION_RULE=dict(
 ai='임시 AI 동료: 주인공을 1.5타일 뒤에서 따라오며, 화면 안 가장 가까운 적을 우선 공격(기본 공격 + 고유 스킬 1개, 쿨타임 제). 전용 HP바(화면 좌상단 주인공 HP 아래)를 가진다.',
 down='HP 0이면 「쓰러짐」 상태로 30초 동안 바닥에 남는다. 주인공이 옆에서 공격 버튼을 2초 누르거나 회복약을 쓰면 HP 30%로 부활. 30초가 지나면 마을로 귀환하고 해당 퀘스트 단계는 실패(재도전 가능). 사망하지 않는다(마왕 루트의 직접 살해 제외).',
 limit='동료는 한 번에 1명. 동료 퀘스트 진행 중에만 필드 동행, 호감도 80 이상이면 퀘스트 밖에서도 마을에서 불러 동행 가능.',
 affinity='호감도 0~100. 퀘스트 단계 완료 +15~25, 선물(취향 품목) +5~10 하루 1회, 싫어하는 선물 -5, 동행 중 쓰러뜨림 방치(귀환) -10. 선악 수치와 별개지만 아래 루트 규칙을 따른다.',
 thresholds={20:'개인 대화 해금',40:'고유 보조무기/장신구 선물',60:'듀오 합동기 해금',80:'특별 장면(비노출, 모닥불 대화·축제 데이트 등) + 상시 동행',100:'엔딩 후일담 장면'},
 karma='선악이 「악명」 이하로 떨어지면 히로인별 반응(떠남/적대/잔류). 마왕 루트에서는 다른 성인 NPC와 마찬가지로 살해할 수 있으며, 살해 시 다시 되돌릴 수 없다.',
)
def H(**k): return k
HEROINES=[
H(id='a_tailor',town='A',name='나비',role='외형상점 「나비 재봉소」 주인 · 쌍침 재봉사',age='22세 (성인)',special=False,
  concept='시작 마을의 발랄한 재봉사. 바늘 두 개로 싸우는 첫 동료.',
  personality='밝고 수다스럽다. 유행과 색 이야기에 눈이 반짝이지만, 실은 겁이 많아 혼자 숲에 못 간다.',
  backstory='왕도 궁정 의상실 견습이었으나 스승(비단결)과 다툰 뒤 고향으로 돌아왔다. 언젠가 「영웅의 망토」를 직접 지어 주는 게 꿈.',
  combat='근접·속도형. 길쭉한 재봉 바늘 두 자루로 3연 찌르기.',skill=dict(name='실타래 묶기',desc='전방 부채꼴 적 2초 속박 (쿨 10초)'),hp=60,
  outfit='짧은 하늘색 주름 미니스커트, 배꼽이 드러나는 나비 리본 크롭 블라우스, 허리에 바늘꽂이 벨트, 무릎 위 줄무늬 스타킹. 금발 트윈테일.',
  visual_en='petite cheerful adult woman (22), golden blonde twin-tails, bright amber eyes, sky-blue pleated mini skirt, cropped white blouse with big butterfly ribbon showing midriff, needle-cushion belt, striped thigh-high stockings, playful energetic vibe',
  likes=['비단 천','나비 날개 가루','꽃'],dislikes=['광석'],
  quests=[('실 한 타래의 용기','가까운 숲에서 「은빛 거미줄」 5개 채집 — 나비 동행, 거미 몹으로부터 그녀를 지킨다','호감도 +20, 금화 100'),
          ('허수아비 패션쇼','보리의 허수아비 옷감을 훔쳐 간 까마귀 무리 처치 후 옷감 회수 — 나비 동행','호감도 +20, 외형 「나비 리본 망토」'),
          ('영웅의 망토','B 강변 수정 동굴 입구까지 동행해 「물빛 실크」 획득, 재봉소로 귀환','호감도 +25, 망토 염색 무료권')],
  rewards={40:'보조무기 「나비 골무 부적」 (회피 +5%)',60:'듀오 합동기 「매듭 베기」: 나비가 속박 → 주인공 회전베기 피해 2배',80:'장면 「분수 축제의 밤」: 분수 광장 축제에서 함께 등불을 띄우는 데이트'},
  karma_route='악명: 울면서 재봉소 문을 닫고 B로 떠난다. 마왕: 겁에 질려 도망치며 공격하면 살해 가능 (전투력 낮음).',
  cg=[('first meet','cheerful blonde twin-tail seamstress in mini skirt waving a giant needle in front of a cozy tailor shop at sunset'),
      ('festival date','blonde twin-tail woman in butterfly crop top releasing a paper lantern by a town fountain at night festival, warm lights, smiling at viewer')]),
H(id='h_mystic',town='H',name='운',role='보랏빛 점술가 · 수정 술사',age='27세 (성인)',special=False,
  concept='광산의 수수께끼 점술가. 수정 구슬로 원거리 마법을 쏜다.',
  personality='몽환적이고 말을 빙빙 돌린다. 운명을 믿지만 정해진 미래를 바꾸는 사람을 보고 싶어 한다.',
  backstory='광산 깊은 곳 「노래하는 수정」의 목소리를 듣고 마을에 정착. 필멸자의 운명이 두 갈래로 갈라지는 환시를 보았다.',
  combat='원거리형. 떠다니는 수정 구슬 2개가 보라색 광탄 발사.',skill=dict(name='예지의 장막',desc='3초간 주인공 피격 1회 무효 (쿨 15초)'),hp=50,
  outfit='보라색 반투명 베일, 금 동전 장식 비키니 탑, 옆트임이 허벅지까지 있는 짧은 보라 랩스커트, 팔찌와 발찌 다수. 은빛 긴 생머리.',
  visual_en='mysterious adult fortune teller (27), long straight silver hair, violet glowing eyes, sheer purple veil, gold-coin bikini top, short purple wrap skirt with high slit, many bangles, two floating crystal orbs, dreamy enigmatic vibe',
  likes=['수정 원석','향초'],dislikes=['횃불'],
  quests=[('노래하는 수정','폐갱도 3층까지 동행해 「노래하는 수정 조각」 회수 — 박쥐 떼 습격','호감도 +20, 금화 200'),
          ('갈라진 운명','운의 환시 속 장소(지하 호수)에서 수정 골렘 처치','호감도 +25, 「점술 카드」 3'),
          ('별이 보이는 갱도','천장이 뚫린 옛 갱도에서 함께 별자리 점 — 도중 광석 도마뱀 무리','호감도 +20, 장면 해금 조건 충족')],
  rewards={40:'보조무기 「운명의 수정구」 (오브, 스킬 게이지 +10%)',60:'듀오 합동기 「별똥 낙하」: 수정 광탄 5발 + 주인공 찌르기 연계',80:'장면 「갱도 위의 별」: 뚫린 천장 아래 모닥불 앞에서 서로의 운명을 이야기'},
  karma_route='악명: 「예견한 대로군요」 하고 사라져 마왕 루트 최종장에 적으로 재등장(환영 마법). 마왕: 마주치면 적대, 살해 가능.',
  cg=[('fortune reading','silver-haired fortune teller in purple veil and gold-coin bikini top reading a glowing crystal ball in a dark mine tent'),
      ('stars campfire','silver-haired woman sitting by a campfire under a starry sky seen through a collapsed mine ceiling, soft violet glow')]),
H(id='g_dancer',town='G',name='방울',role='무희 겸 바자르 장신구 상인',age='24세 (성인)',special=True,
  concept='짙은 붉은 머리의 사막 무희 상인. 쌍곡도 칼춤으로 싸우는 특별 히로인.',
  personality='명랑하고 능청스럽다. 소문과 흥정에 밝지만 약속은 반드시 지킨다.',
  backstory='대상 행렬의 고아로 자라 춤과 장사로 살아남았다. 도적에게 빼앗긴 어머니의 「태양 방울」을 되찾는 것이 소원.',
  combat='근접 회전형. 초승달 쌍곡도 칼날 회전 춤.',skill=dict(name='방울 매혹',desc='주변 적 1.5초 경직 + 받는 피해 +20% (쿨 12초)'),hp=70,
  outfit='짙은 붉은 긴 웨이브 머리, 금 동전과 방울이 달린 진홍 비키니 탑(풍만한 가슴), 허리에 걸친 짧은 반투명 시폰 스커트, 금팔찌·발찌. 이벤트 변형: 마이크로 비키니 축제 의상(female_sample_microbikini.jpg).',
  art=['/workspace/town-demo/src/npcs/female_sample_desert_v2.jpg','/workspace/town-demo/src/npcs/female_sample_microbikini.jpg'],
  visual_en='voluptuous curvy adult desert dancer-merchant (24), long wavy dark-red hair, golden eyes, tanned skin, crimson bikini top with gold coins and tiny bells, low-slung short sheer chiffon skirt, gold bangles and anklets, twin crescent scimitars, flirty confident vibe',
  likes=['사막 태양석','향신료','금 장신구'],dislikes=['모래쥐 고기'],
  quests=[('대상 행렬 호위','바자르 → 오아시스 길에서 방울의 장신구 수레 호위 (도적 3파)','호감도 +20, 금화 300'),
          ('도둑맞은 태양 방울','사막 도적 은신처 잠입, 두목 처치 후 「태양 방울」 회수 — 방울 동행','호감도 +25, 「사막 태양석」 2'),
          ('오아시스 축제의 춤','축제 무대를 노리는 전갈 떼를 막아 공연을 지킨다','호감도 +20, 외형 「축제 무희 장식 망토」')],
  rewards={40:'보조무기 「태양 방울 팔찌」 (공격 속도 +8%)',60:'듀오 합동기 「모래 폭풍 왈츠」: 둘이 등을 맞대고 회전, 광역 연속 피해',80:'장면 「오아시스 축제 데이트」: 축제 무대 뒤 등불 아래 둘만을 위한 춤'},
  karma_route='악명: 장사꾼답게 「거래 끝」을 선언하고 가격 3배. 마왕: 도적 편에 붙어 적대, 살해 가능. 단, 호감도 100이면 단 한 명 「마왕의 무희」로 잔류(동행 유지, 아이를 해치면 떠남).',
  cg=[('bazaar meet','curvy dark-red haired desert dancer in crimson bikini top with gold coins winking behind a jewelry stall in a sunny bazaar'),
      ('blade dance','dark-red haired dancer spinning with twin scimitars among scorpions at an oasis, flowing chiffon skirt, dynamic action'),
      ('festival dance','dark-red haired dancer in micro bikini festival costume dancing on a lantern-lit oasis stage at night, playful smile')]),
H(id='f_diver',town='F',name='숨비',role='해녀 · 작살 잠수꾼',age='25세 (성인)',special=True,
  concept='항구 최고의 해녀. 작살로 싸우는 건강미 넘치는 특별 히로인.',
  personality='당차고 큰소리 잘 치는 누님 기질. 바다 앞에서만은 진지하다.',
  backstory='유령 해적에게 배를 잃은 아버지의 작살을 물려받았다. 가라앉은 아버지의 배에서 유품을 건지고 싶어 한다.',
  combat='중거리 찌르기형. 작살 찌르기 + 수중에서 이동 속도 증가.',skill=dict(name='물보라 작살',desc='직선 관통 작살 투척, 물가에서 피해 1.5배 (쿨 9초)'),hp=80,
  outfit='짧은 흑청색 해녀 비키니 아머(풍만한 가슴), 허리에 그물 사롱, 조개 장식 목걸이, 다리에 물갈퀴 장화. 젖은 흑발 포니테일, 태닝 피부.',
  visual_en='athletic busty adult sea diver (25), wet black ponytail, sea-green eyes, tanned skin, dark teal bikini armor with shell plates, fishnet sarong, shell necklace, harpoon, confident big-sister grin',
  likes=['진주','구운 생선'],dislikes=['유령 해적 깃발'],
  quests=[('물질 대결','산호초에서 진주 5개를 누가 먼저 캐는지 대결 — 상어 몹 출현 시 협공','호감도 +20, 잠수 시간 +2초'),
          ('가라앉은 배','침몰선 잠수 스폿에서 아버지의 유품 회수, 유령 선원 처치','호감도 +25, 「바다 진주」 3'),
          ('등대의 밤','유령 해적 정찰대를 등대 앞에서 격퇴 — 숨비·빛나와 함께','호감도 +20, 금화 400')],
  rewards={40:'보조무기 「아버지의 작살촉 부적」 (수중 공격 +15%)',60:'듀오 합동기 「해일 찌르기」: 숨비 작살 관통 후 주인공 돌진 찌르기',80:'장면 「해변 모닥불」: 등대 아래 해변 모닥불에서 아버지 이야기와 구운 생선'},
  karma_route='악명: 항구 사람들을 지키려고 주인공에게 결투를 신청(적대). 마왕: 항구 수호자로 적대, 살해 가능.',
  cg=[('pearl contest','busty tanned diver with black ponytail in teal bikini armor surfacing from turquoise water holding a pearl, laughing'),
      ('beach campfire','black-haired diver wrapped in a towel sitting by a beach campfire under a lighthouse at night, gentle expression')]),
H(id='e_tailor',town='E',name='루비',role='외형상점 「불꽃 옷감」 주인 · 화염 채찍술사',age='26세 (성인)',special=False,
  concept='도도한 화산 마을 직조공. 불에 안 타는 채찍으로 싸운다.',
  personality='도도하고 자신만만, 칭찬에 약하다. 실력을 인정한 상대에게만 존댓말을 버린다.',
  backstory='불사조 깃털로 「영원히 타지 않는 천」을 짜는 것이 일생의 목표. 화산 정상에 오를 동료를 찾고 있었다.',
  combat='중거리형. 불꽃 채찍 2연타, 화상 부여.',skill=dict(name='화염 고리',desc='주변 원형 불꽃, 2초 화상 (쿨 12초)'),hp=65,
  outfit='가슴 아래에서 끝나는 검은 가죽 크롭 뷔스티에(배 완전 노출), 몸에 딱 붙는 검은 가죽 H라인(펜슬) 미니스커트(허벅지 중간, 옆트임), 불꽃 무늬 사이하이 부츠, 허리에 감긴 채찍. 붉은 단발과 루비 귀걸이.',
  visual_en='haughty adult weaver (26), sharp red bob haircut, ruby eyes, black leather cropped bustier ending under the bust with fully bare midriff, tight black leather H-line pencil mini skirt (mid-thigh, side slit), flame-pattern thigh-high boots, coiled fire whip, ruby earrings, proud tsundere vibe',
  likes=['불사조 깃털','흑요석'],dislikes=['물'],
  quests=[('타지 않는 실','용암 동굴에서 「화염 누에고치」 6개 — 루비 동행','호감도 +20, 금화 300'),
          ('불사조의 깃털','화산 중턱에서 불새 무리 처치 후 깃털 회수','호감도 +25, 외형 「불꽃 실크 망토」'),
          ('불꽃 옷감 품평회','품평회를 망치려는 쇠메의 라이벌 상인 패거리 격퇴','호감도 +20, 방어구 화염 저항 염색')],
  rewards={40:'보조무기 「루비 채찍 팔찌」 (화상 확률 +10%)',60:'듀오 합동기 「불꽃 회오리」: 화염 고리 + 주인공 회전베기 = 화염 소용돌이',80:'장면 「용암 강가의 밤」: 식은 용암 바위 위에서 완성한 천을 주인공 망토에 둘러 준다'},
  karma_route='악명: 「실망이야」 한마디로 상점 거래 거부. 마왕: 마왕군과 싸우다 적대, 살해 가능.',
  cg=[('workshop','red bob haired woman in black corset crop top and ruby mini skirt weaving glowing fire cloth in a forge workshop'),
      ('lava night','red-haired woman draping a shimmering flame cloak over the viewer beside a cooled lava river at night')]),
H(id='c_priest',town='C',name='설화',role='눈의 신전 사제(성녀) · 서리 치유사',age='23세 (성인)',special=False,
  concept='어둠 신전을 두려워하는 설산의 성녀. 유일한 치유형 동료.',
  personality='온화하고 다정하지만 고집이 있다. 두려움을 숨기고 웃는다.',
  backstory='어린 시절 어둠 신전 사제들에게 납치될 뻔한 기억을 지녔다. 신전의 봉인을 지키는 마지막 성녀.',
  combat='후방 지원형. 서리 지팡이로 얼음 탄환.',skill=dict(name='눈꽃 축복',desc='주인공 HP 25% 회복 (쿨 20초)'),hp=55,
  outfit='흰 털 장식 짧은 크롭 상의(배 완전 노출)와 분리형 털 소매, 몸에 붙다가 밑단이 살짝 퍼지는 흰 머메이드 미니스커트(허벅지 중간), 하늘색 보석 장식, 흰 사이하이 스타킹, 눈꽃 머리장식. 연한 하늘빛 긴 머리.',
  visual_en='gentle adult snow priestess (23), long pale ice-blue hair, soft blue eyes, short white fur-trimmed crop top with fully bare midriff, detached fur-trimmed sleeves, snug white mermaid-silhouette mini skirt flaring slightly at the mid-thigh hem, ice-jewel accents, white thigh-high stockings, snowflake hair ornament, frost staff, kind but brave vibe',
  likes=['눈꽃 결정','따뜻한 수프'],dislikes=['어둠의 파편'],
  quests=[('얼어붙은 순례길','신전 순례길의 설인 무리 정리 — 설화 동행','호감도 +20, 회복약 3'),
          ('봉인의 종','설산 동굴의 「봉인의 종」 3개를 다시 울린다, 어둠 사제 처치','호감도 +25, 「성수」 2'),
          ('눈꽃 축제','눈꽃 축제 등불을 노리는 서리 늑대 떼 격퇴','호감도 +20, 외형 「눈꽃 망토」')],
  rewards={40:'보조무기 「성녀의 눈꽃 부적」 (부적, 받는 피해 -5%)',60:'듀오 합동기 「성광 서리검」: 축복 후 주인공 검에 빙결 부여 10초',80:'장면 「눈꽃 축제 데이트」: 산장 앞 눈꽃 축제에서 따뜻한 수프를 나누며 걷기'},
  karma_route='악명: 신전에 틀어박혀 회복 서비스 거부. 마왕: 마지막 봉인을 지키며 적대(정화 마법이 마왕에게 추가 피해), 살해 가능.',
  cg=[('temple','ice-blue haired priestess in short white fur-trimmed dress praying in a snowy temple with glowing snowflakes'),
      ('snow festival','ice-blue haired priestess holding a warm soup bowl at a snow festival with lanterns, blushing smile')]),
]
# 7번째: 현세에서 온 이방인 (마을 NPC 10명 정원 밖 '손님' NPC로 D에 머문다)
HEROINES.append(H(id='d_yuna',town='D',name='유나',guest=True,role='현세에서 온 이방인 · 왕도 서고의 객원 조사원',age='25세 (성인)',special=True,
  concept='현대 세계에서 떨어진 흑발 대학원생. 짧은 검과 「낙인 공명」으로 싸우는 특별 히로인.',
  personality='밝고 붙임성 있지만 속으로는 집이 그리워 밤마다 휴대폰(배터리 0%)을 만지작거린다. 이 세계를 「게임 같다」며 의외로 빨리 적응했다.',
  backstory='서울의 대학원생(고고학). 박물관에서 낙인 문양이 새겨진 동판을 만진 순간 빛에 삼켜져 왕도 성벽 밖 폐허에 떨어졌다. 그녀의 손등에도 옅은 「포식의 낙인」 문양이 떠 있어, 그 낙인이 세계 사이의 문을 여는 열쇠라는 것을 서고지기 먼지와 함께 알아낸다. 귀환 방법은 마룡의 심장에서 흘러나오는 차원 균열뿐 — 필멸자와 함께 끝까지 가야만 선택할 수 있다. 엔딩(호감도 100)에서 귀환할지 남을지 직접 고른다.',
  combat='근접 기동형. 박물관 진열장에서 함께 떨어진 짧은 의례용 검으로 빠른 2연 베기 + 백스텝.',skill=dict(name='낙인 공명',desc='주인공의 포식의 낙인과 공명, 5초간 둘 다 공격력 +20%·흡수 효율 +1 (쿨 18초)'),hp=65,
  outfit='흰 오프숄더 크롭 블라우스(풍만한 가슴, 배꼽 노출), 검은 주름 미니스커트와 체인 벨트, 검은 사이하이 스타킹, 하트 펜던트 초커, 허리에 짧은 검. 긴 흑발에 앞머리, 보랏빛 눈.',
  art=['/workspace/town-demo/src/heroines/cg_modern_sample.jpg'],
  visual_en='curvy adult modern-world woman (mid-20s), long straight black hair with bangs, violet eyes, white off-shoulder puff-sleeve crop top showing midriff, black pleated mini skirt with chain belt, black thigh-high stockings, black choker with heart pendant, short ornate sword at hip, cheerful but homesick vibe',
  likes=['단 과자','고대 문서','반짝이는 돌(휴대폰 충전용이라 믿음)'],dislikes=['벌레'],
  quests=[('하늘에서 떨어진 여자','성벽 밖 폐허에서 몹에 둘러싸인 유나 구출 후 왕도까지 호위 — 유나 동행','호감도 +20, 금화 300'),
          ('낙인의 동판','서고지기 먼지의 단서로 고대 묘지 지하에서 「낙인 동판 조각」 회수, 묘지기 해골 기사 처치','호감도 +25, 「고대 문서」 2'),
          ('두 세계의 등불','왕도 등불 축제 날, 차원 균열에서 새어 나온 그림자 몹을 막아 축제를 지킨다','호감도 +20, 외형 「이방인의 초커」')],
  rewards={40:'보조무기 「방전된 휴대폰」 (부적: 던지면 0.5초 섬광 경직, 쿨 30초)',60:'듀오 합동기 「쌍낙인 폭주」: 낙인 공명 중 동시 돌진 X자 베기, 흡수 게이지 즉시 1칸',80:'장면 「노을빛 왕도 산책」: 등불 축제 저녁, 성벽 위에서 고향 이야기와 「여기도 나쁘지 않네」',100:'엔딩 후일담: 차원 균열 앞에서 귀환/잔류 선택 — 잔류 시 필멸자의 집에 함께 사는 장면, 귀환 시 현대 거리에서 낙인이 빛나는 여운'},
  karma_route='악명: 「너 그런 사람 아니었잖아…」 하고 서고에 숨어 동행 거부. 마왕: 포식의 낙인이 공명해 마왕에게 끌려가며 적대하지 않지만 대화 불가 상태로 따라오다가, 아이를 해치는 순간 낙인을 거꾸로 써서 마왕에게 저주(최대 HP -10%)를 건 뒤 적대. 다른 성인처럼 살해 가능 — 살해하면 귀환 엔딩은 영구 소실.',
  cg=[('lantern street greeting','black-haired woman with bangs in white off-shoulder crop top and black pleated mini skirt waving on a lantern-lit fantasy street at sunset (sample, cg_d_yuna_1.jpg)'),
      ('fallen from the sky','black-haired modern woman in white crop top sitting dazed among glowing ruins outside a castle wall, holding a dead smartphone, short sword beside her'),
      ('rampart sunset talk','black-haired woman in black choker sitting on a castle rampart at dusk beside the viewer, lanterns below, wistful smile')]))
# 대사 표정 훅: line['expr'] ∈ PORTRAIT_EXPRS → 초상화 <id>_<expr>.png
PORTRAIT_EXPRS=['normal','smile','angry','blush']
def _lines(h):
    n=h['name']
    return [dict(when='첫 만남',expr='normal',text=f"{n}예요. 잘 부탁해요."),
            dict(when='퀘스트 완료',expr='smile',text='역시! 같이 오길 잘했어요.'),
            dict(when='쓰러짐 방치·싫은 선물',expr='angry',text='…지금 장난해요?'),
            dict(when='호감도 80',expr='blush',text='저기… 오늘은 조금 더 같이 있어도 돼요?')]
for _h in HEROINES:
    _h['lines']=_lines(_h)
    _h['portraits']={e:f"{_h['id']}_{e}.png" for e in PORTRAIT_EXPRS}
# 고해상도 바스트업 초상화 (머리~허리, 대화창 확대 표시용)
PORTRAIT_SIZES=dict(bustup=[192,256],bustup_small=[96,128],face_fallback=[128,128])
COMPANION_RULE['portraits']=('대화 초상화: 1순위 `<id>_<expr>_bu.png` (192×256 바스트업, 머리~허리, 대화창에서 1.5~2배 크게 표시 권장), '
  '작은 창은 `<id>_<expr>_bu_s.png` (96×128), 없으면 기존 `<id>_<expr>.png`/`<id>.png` (128×128 얼굴). 경로 town/assets/portraits/, 목록은 index.json의 expressions_bustup.')
for _h in HEROINES:
    _h['portraits_bustup']={e:dict(large=f"{_h['id']}_{e}_bu.png",small=f"{_h['id']}_{e}_bu_s.png") for e in PORTRAIT_EXPRS}
COMPANION_RULE['outfit_rule']=('성인 여성 의상 규칙: 상의는 배가 완전히 드러나는 짧은 크롭 탑 또는 비키니 탑만(원피스·코르셋·배를 덮는 상의 금지, 비노출). '
 '하의 선택지: 짧은 주름 미니스커트, 비키니 하의/마이크로 비키니(축제 변형), **H라인(펜슬) 미니스커트**(몸에 딱 붙는 일자, 허벅지 중간), '
 '**머메이드 미니스커트**(엉덩이까지 밀착, 허벅지 중간 밑단이 살짝 퍼짐). 적용: 루비=검은 가죽 H라인, 설화=흰 머메이드, 상인 미소=갈색 H라인, 책벌레 연=보라 H라인, 공주 세린=보라·금 머메이드. '
 '비키니 탑 변형(가리는 면적은 일반 비키니 이상, 언더붓 노출 금지): **스트래피 비키니**(일반 비키니 탑 + 갈비뼈·허리를 감는 가는 교차 끈), **홀터넥 비키니**(목 뒤로 묶는 삼각 탑, 컵 사이 작은 키홀 허용), **메탈 장식 비키니**(금·은 판금, 체인, 보석 장식의 비키니 아머). 적용: 미소=빨강 스트래피, 연=보라 홀터넥, 빛나=노랑 홀터넥, 세린=금·보라 메탈 장식. '
 '참고 샘플: female_sample_hline_mermaid.jpg, female_sample_bikini_variants.jpg. 아이는 대상 아님.')
COMPANION_RULE['outfit_rule']+=(' **삼각 비키니 단독 착용**(상·하의 모두 일반 삼각 비키니, 치마·바지 없음; 샌들·작은 장신구·소지품만 허용, 일반 비키니 노출 범위, 비노출, 명백한 성인): 쪽빛(b_dyer, 강변 염색공방·남색), 사프란(g_tool, 사막 바자르 도구상·빨강), 자스민(g_tailor, 사막 바자르 의상상·연보라), 진주(f_tailor, 항구 의상상·라벤더). 히로인(운 등)은 고유 의상 유지.')
COMPANION_RULE['body_standard']=('성인 여성 맵 스프라이트 체형 기준(실측 검증): 기준 = female_sample_bikini_variants.jpg 맨 오른쪽 여성. 목표 7.9등신(정수리~턱 = 키/7.9), 다리비(가랑이~발바닥 / 키) 0.50, 허용 범위 7.5~8.3등신·다리비 0.47~0.53. '
 '캔버스 규격: town/assets/npcs/<id>.png는 위쪽 여백 = 키의 7%(정수리 위), 아래 = 발바닥(기준선) 고정 → 엔진이 n.h=120px로 그릴 때 몸 높이 112.2px로 전원 동일(±3% 이내), 같은 기준선. 정수리 6.54%, 턱 18.37%, 가랑이 53.27% 위치. '
 '머리 위로 튀어나온 소품(횃불·창끝·모자 장식)은 몸을 줄이지 않도록 잘라냄. 측정법: 알파 bbox 기준 확대 눈금자 수동 판독(정수리·턱·가랑이) → 머리 구간은 가로세로, 몸통·다리는 세로 구간별 보정. '
 '2026-10 전수 재측정: 24명 중 23명이 기준 밖(재측정 전 6.1~10.1등신, 다리비 0.50~0.55, 게임 내 몸 높이 109~119px) → 24명 전원 재비율, 결과 표는 town-demo/female_proportions.csv, 확인용 female_lineup_after.png. 의상·색·머리 유지(세린 보라 슬릿 랩스커트 유지). 아이는 대상 아님. 비노출.')
