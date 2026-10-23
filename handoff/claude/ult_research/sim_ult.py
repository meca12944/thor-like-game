"""심연 초필살기 방식 비교: 골렘 보스전 몬테카를로 (test128 숫자).
보스 1673 HP, 2초마다 공격 1회(맞으면 11), 주인공 50 HP, 물약 5개(+15, 4초), 칼 DPS 35 x 붙어 있는 비율,
필살기 게이지: 맞으면 1HP당 +0.5, 저스트 회피 +8, 100에서 일반 필살기(보스 22%).
python3 sim_ult.py -> 표 출력 + results.json"""
import random, json
BOSS, HERO, HIT, PERIOD, DPS, POT_N, POT_HP, POT_CD, DT, TMAX = 1673, 50, 11, 2.0, 35, 5, 15, 4, 0.1, 300
SKILL = {'초보': dict(hit=.45, just=.05, up=.30), '보통': dict(hit=.25, just=.15, up=.40), '숙련': dict(hit=.10, just=.35, up=.50)}
ABY = dict(hp=.25, dur=8, atk=1.8)
VAR = {
 'A 없음': None,
 'B 지금 (45초마다, 게이지X, 보스35%)': dict(once=False, cd=45, gauge=False, boss=.35, stun=0, trig='key'),
 'C 추천안 (한 번, 게이지 가득, 15%+기절3초)': dict(once=True, gauge=True, boss=.15, stun=3, trig='key'),
 'D 철권식 (한 번, 피 적을수록 셈 8~40%)': dict(once=True, gauge=False, boss='scale', stun=0, trig='key'),
 'E 반격식 (한 번, 심연 중 저스트회피로 발동, 20%+기절3초)': dict(once=True, gauge=False, boss=.20, stun=3, trig='just'),
 'F 한 번, 게이지X, 15%+기절3초': dict(once=True, gauge=False, boss=.15, stun=3, trig='key'),
}
def fight(sk, v, rng):
    hp, b, pots, pcd, g, t, nxt = HERO, BOSS, POT_N, 0, 0, 0, PERIOD
    aby_t, aby_cd, used, super_dmg, stun, abyss_dmg = 0, 0, 0, 0, 0, 0
    while t < TMAX:
        t += DT; pcd -= DT; aby_cd -= DT; stun -= DT
        on = aby_t > 0; aby_t -= DT
        if on and aby_t <= 0 and v: aby_cd = v.get('cd', 1e9)
        mul = ABY['atk'] if (aby_t > 0 and v) else 1
        d = DPS * (1 if stun > 0 else SKILL[sk]['up']) * mul * DT; b -= d
        if mul > 1: abyss_dmg += d * (mul - 1) / mul
        def do_super():
            nonlocal b, super_dmg, used, stun, aby_t, g
            frac = (0.08 + 0.32 * (1 - hp / HERO)) if v['boss'] == 'scale' else v['boss']
            dd = BOSS * frac; b -= dd; super_dmg += dd; used += 1; stun = v['stun']; aby_t = 0
            if v['gauge']: g = 0
        if v and aby_t > 0 and v['trig'] == 'key' and (not v['gauge'] or g >= 100): do_super()
        if g >= 100 and not (v and v['gauge'] and aby_t > 0): b -= BOSS * .22; g = 0
        if b <= 0: return dict(win=1, t=t, used=used, sup=super_dmg, aby=abyss_dmg)
        if t >= nxt and stun <= 0:
            nxt = t + PERIOD * rng.uniform(.8, 1.2); r = rng.random(); s = SKILL[sk]
            if r < s['hit']:
                hp -= HIT; g = min(100, g + HIT * .5)
                if v and hp > 0 and hp <= HERO * ABY['hp'] and aby_t <= 0 and aby_cd <= 0 and not (v['once'] and used): aby_t = ABY['dur']
            elif r < s['hit'] + s['just']:
                g = min(100, g + 8)
                if v and v['trig'] == 'just' and aby_t > 0: do_super()
            if hp <= 0: return dict(win=0, t=t, used=used, sup=super_dmg, aby=abyss_dmg)
        elif t >= nxt: nxt = t + .1
        if hp <= 15 and pots and pcd <= 0: hp = min(HERO, hp + POT_HP); pots -= 1; pcd = POT_CD
    return dict(win=0, t=t, used=used, sup=super_dmg, aby=abyss_dmg)
def run(N=10000, seed=7):
    R = {}
    for vn, v in VAR.items():
        for sk in SKILL:
            rng = random.Random(seed); rs = [fight(sk, v, rng) for _ in range(N)]
            w = [r for r in rs if r['win']]
            R[(vn, sk)] = dict(win=round(100 * len(w) / N, 1), time=round(sum(r['t'] for r in w) / max(1, len(w)), 1),
                               uses=round(sum(r['used'] for r in rs) / N, 2), share=round(100 * sum(r['sup'] + r['aby'] for r in rs) / (N * BOSS), 1))
    return R
if __name__ == '__main__':
    R = run(); base = {sk: R[('A 없음', sk)]['win'] for sk in SKILL}
    print(f"{'방식':<44}" + ''.join(f"{sk:>22}" for sk in SKILL))
    for vn in VAR:
        print(f"{vn:<44}" + ''.join(f"{R[(vn,sk)]['win']:>6}% ({R[(vn,sk)]['win']-base[sk]:+5.1f}) 쓴횟수{R[(vn,sk)]['uses']:>4}" for sk in SKILL))
    print('\n보스 체력 중 심연(초필살기+강화)이 깎은 비율 %')
    for vn in VAR: print(f"{vn:<44}" + ''.join(f"{R[(vn,sk)]['share']:>22}" for sk in SKILL))
    json.dump({f'{k[0]}|{k[1]}': v for k, v in R.items()}, open(__file__.replace('sim_ult.py', 'results.json'), 'w'), ensure_ascii=False, indent=1)
