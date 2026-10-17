"""Score format -> timed note events.

A song is a plain Python dict (see songs/*.py and README.md).  Grid unit = one 16th note ("step").
"""
import re

NOTE_PC = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}
SCALES = {'major': [0, 2, 4, 5, 7, 9, 11], 'minor': [0, 2, 3, 5, 7, 8, 10], 'harmonic': [0, 2, 3, 5, 7, 8, 11],
          'dorian': [0, 2, 3, 5, 7, 9, 10], 'phrygian': [0, 1, 3, 5, 7, 8, 10], 'phrydom': [0, 1, 4, 5, 7, 8, 10],
          'mixolydian': [0, 2, 4, 5, 7, 9, 10], 'lydian': [0, 2, 4, 6, 7, 9, 11]}
CHORD_IV = {'': [0, 4, 7], 'm': [0, 3, 7], '7': [0, 4, 7, 10], 'm7': [0, 3, 7, 10], 'maj7': [0, 4, 7, 11],
            'dim': [0, 3, 6], 'dim7': [0, 3, 6, 9], 'aug': [0, 4, 8], 'sus4': [0, 5, 7], 'sus2': [0, 2, 7],
            '5': [0, 7], 'm7b5': [0, 3, 6, 10], 'add9': [0, 4, 7, 14], 'madd9': [0, 3, 7, 14], '7sus4': [0, 5, 7, 10],
            'm9': [0, 3, 7, 10, 14], '9': [0, 4, 7, 10, 14], 'mmaj7': [0, 3, 7, 11], '6': [0, 4, 7, 9], 'm6': [0, 3, 7, 9]}


def note_num(s):
    """'c#4' -> 61 (c4 = 60)."""
    m = re.fullmatch(r'([a-gA-G])([#b]?)(-?\d)', s)
    if not m:
        raise ValueError('bad note ' + s)
    pc = NOTE_PC[m.group(1).lower()] + {'#': 1, 'b': -1, '': 0}[m.group(2)]
    return 12 * (int(m.group(3)) + 1) + pc


def pc_of(name):
    return (NOTE_PC[name[0].lower()] + {'#': 1, 'b': -1}.get(name[1:2], 0)) % 12


# ---------------------------------------------------------------- melody (MML-like)
TOK = re.compile(r'([~`!*^]*)(r|-|[a-gA-G][#b]?-?\d)(?:/([\d.]+))?')


def parse_mel(s):
    """'~a4/4 c5/2 e5 r/2 -/4' -> list of (step, len, midi|None, flags).
    flags: ~ bend up 2 semis into note, ` bend 1 semi, ! accent, * staccato, ^ glide from previous note.
    Duration (in 16ths) is sticky like MML; '-' ties onto the previous note; '|' is only visual."""
    out, step, dur, last = [], 0.0, 4.0, None
    for tok in s.replace('|', ' ').split():
        m = TOK.fullmatch(tok)
        if not m:
            raise ValueError('bad melody token %r' % tok)
        fl, n, d = m.groups()
        if d:
            dur = float(d)
        if n == '-':
            if out and last != 'r':
                st, ln, nn, f = out[-1]
                out[-1] = (st, ln + dur, nn, f)
        elif n == 'r':
            pass
        else:
            out.append((step, dur, note_num(n.lower()), fl))
        if n != '-':
            last = n
        step += dur
    return out, step


# ---------------------------------------------------------------- chords
CH = re.compile(r'([A-G][#b]?)([a-z0-9#]*?)(?:/([A-G][#b]?))?(?::([\d.]+))?$')


def parse_chords(s, bar):
    out, step = [], 0.0
    for tok in s.replace('|', ' ').split():
        if tok in ('N', 'N.C.'):
            out.append((step, bar, None)); step += bar; continue
        if tok.startswith('N:'):
            d = float(tok[2:]); out.append((step, d, None)); step += d; continue
        m = CH.match(tok)
        if not m:
            raise ValueError('bad chord ' + tok)
        root, q, bass, d = m.groups()
        if q not in CHORD_IV:
            raise ValueError('unknown chord quality %r in %s' % (q, tok))
        d = float(d) if d else bar
        r = pc_of(root)
        out.append((step, d, dict(root=r, bass=pc_of(bass) if bass else r, iv=CHORD_IV[q], name=tok)))
        step += d
    return out, step


def voice(ch, center=62, n=None):
    """close voicing of the chord pitch classes around `center`."""
    pcs = [(ch['root'] + i) % 12 for i in ch['iv']]
    notes = []
    for pc in pcs:
        m = center - 6 + ((pc - (center - 6)) % 12)
        notes.append(m)
    return sorted(set(notes))


def chord_tones(ch, low=52, count=8):
    pcs = [(ch['root'] + i) % 12 for i in ch['iv'] if i < 12]
    out, m = [], low
    while len(out) < count:
        if m % 12 in pcs:
            out.append(m)
        m += 1
    return out


def bass_note(ch, low=28):  # E1 = 28
    return low + ((ch['bass'] - low) % 12)


# ---------------------------------------------------------------- pattern libraries
BASS = {
    'drive8': 'R-R-R-R-R-R-O-R-', 'drive8o': 'R-R-O-R-R-R-O-R-', 'gallop': 'R-RRR-RRR-RRR-RR',
    'slap': 'R.xRO.xR.RO.xRO.', 'slap2': 'R.RxO.R.xRO.R5O.', 'slap3': 'R..RO..R.RO.R.OA',
    'sync': 'R--R--R-R--R--O-', 'sync2': 'R--R--R-O-R-5-R-', 'walk': 'R---3---5---O---', 'walk8': 'R-3-5-O-5-3-R-A-',
    'half': 'R-----------R-R-', 'half2': 'R---------R-----', 'root1': 'R---------------', 'root2': 'R-------R-------',
    'town': 'R---5---O---5---', 'bounce': 'R--R5--RO--R5-R-', 'chug': 'RRRRRRRRRRRRRRRR', 'chug8': 'R-R-R-R-R-R-R-R-',
    'waltz': 'R---5---5---', 'waltz2': 'R-------5---', 'six8': 'R-----5-----', 'march': 'R---R---5---R-5-',
    'octs': 'R-O-R-O-R-O-R-O-', 'dark': 'R-----R-R-----A-', 'darkchug': 'R.RR.RR.R.RR.R5O', 'none': '................',
}
COMP = {
    'power8': 'm.m.m.m.m.m.m.m.', 'chug16': 'mmmmmmmmmmmmmmmm', 'powersync': 'x--x--x-x-.-x-.-', 'power1': 'x---------------',
    'stab': 'x.......x.....x.', 'stab2': 'x..x..x.....x...', 'offbeat': '..x...x...x...x.', 'pad': 'x---------------',
    'strum': 'x---x-x---x-x-x-', 'waltz': '....x...x...', 'six8': 'x--x--x--x--', 'gallop': 'm.mmm.mmm.mmm.mm',
    'darkpow': 'x-----x-x-------', 'push': 'x-----x-----x---', 'none': '................',
}
ARP = {
    'up16': '0123432101234321', 'up8': '0-1-2-3-4-3-2-1-', 'alberti': '0201020102010201', 'cascade': '5432104321054321',
    'rise': '0123456701234567', 'waltz': '0-2-4-2-4-2-', 'six8': '024642024642', 'twinkle': '4-2-5-3-4-2-6-3-',
    'trem': '0202020202020202', 'pulse': '0.0.0.0.0.0.0.0.',
}
DRUMS = {
    'none': {},
    'rock': dict(k='x.....x.x.......', s='....x.......x...', h='x.x.x.x.x.x.x.x.'),
    'drive': dict(k='x.x...x.x.x...x.', s='....X.......X...', h='x.x.x.x.x.x.x.x.'),
    'drive16': dict(k='x.x...x.x.x..x..', s='....X..o....X..o', h='xoxoxoxoxoxoxoxo'),
    'gallop': dict(k='x..xx..xx..xx..x', s='....X.......X...', h='x.x.x.x.x.x.x.x.'),
    'double': dict(k='xxxxxxxxxxxxxxxx', s='....X.......X...', r='x.x.x.x.x.x.x.x.'),
    'four': dict(k='x...x...x...x...', s='....X.......X...', H='..x...x...x...x.', h='x...x...x...x...'),
    'half': dict(k='x.........x.....', s='........X.......', h='x.x.x.x.x.x.x.x.'),
    'darkhalf': dict(k='x......x..x.....', s='........X.......', T='x..........x....', h='x...x...x...x...'),
    'darkdrive': dict(k='x.xx..x.x.xx..x.', s='....X.......X...', T='x...........x...', r='x...x...x...x...'),
    'taiko': dict(T='X..x..x...X.x...', k='x.........x.....', p='........x.......'),
    'taiko2': dict(T='X.xx..X.x.X.xx.x', k='x.......x.......'),
    'march': dict(k='x.......x.......', s='x..ox.oxx..ox.ox', c=''),
    'town': dict(k='x.......x.......', p='....x.......x...', sh='x.xxx.xxx.xxx.xx'),
    'town2': dict(k='x.....x.x.......', p='....x.......x...', sh='x.x.x.x.x.x.x.x.', h=''),
    'waltz': dict(k='x...........', p='....x...x...', sh='x.x.x.x.x.x.'),
    'six8': dict(k='x.....x.....', p='...x.....x..', sh='x.xx.xx.xx.x'),
    'shuffle': dict(k='x.....x.x.....x.', s='....x.......x...', h='x..xx..xx..xx..x'),
    'pulse': dict(k='x...x...x...x...'),
    'heart': dict(k='x..x............'),
    'ride': dict(k='x.......x.x.....', s='....x.......x...', r='x.xxx.xxx.xxx.xx'),
    'bossa': dict(k='x..x..x.x..x..x.', p='x..x...x..x..x..', sh='xxxxxxxxxxxxxxxx'),
}
FILLS = {
    'fill': dict(k='x.....x.x.......', s='....x...x.xxXXXX', h='x.x.x.x.........'),
    'tom': dict(k='x.......x.......', s='....x...........', t1='........xx......', t2='..........xx....', t3='............xXX.'),
    'snare': dict(k='x.......x.......', s='....x.......xxxx', h='x.x.x.x.x.x.....'),
    'roll': dict(s='xoxoxoxoxxxxXXXX', k='x...x...x...x...'),
    'taiko': dict(T='X...X...X.X.XXXX', k='x...x...x...x...'),
    'stop': dict(k='x.......', s='x.......', c='x.......'),
    'waltz': dict(k='x...........', p='....x...xxxx'),
}


def _len_ok(p, bar):
    return p if len(p) % bar == 0 else (p * bar)[:bar] if len(p) < bar else p[:bar]


# ---------------------------------------------------------------- harmony helper
def scale_pcs(key_pc, mode):
    return [(key_pc + i) % 12 for i in SCALES[mode]]


def diatonic_shift(m, steps, key_pc, mode):
    """move a note by `steps` scale degrees (e.g. -2 = a diatonic third below)."""
    pcs = set(scale_pcs(key_pc, mode))
    ladder = [n for n in range(0, 128) if n % 12 in pcs]
    if m in ladder:
        i = ladder.index(m)
    else:  # chromatic note: use the scale note just below and keep the offset
        i = max(k for k, n in enumerate(ladder) if n < m)
        return ladder[i + steps] + (m - ladder[i])
    return ladder[i + steps]


# ---------------------------------------------------------------- build events
DEFAULT_CH = {
    'lead': dict(type='mel', inst='guitar', gain=0.30, pan=0.0, rev=0.20, dly=0.16, lp=5800, hp=140),
    'lead2': dict(type='mel', harm_of='lead', shift=-2, inst='guitar', gain=0.17, pan=0.32, rev=0.25, dly=0.10, lp=4500, hp=160),
    'counter': dict(type='mel', inst='psg', gain=0.13, pan=-0.35, rev=0.2, dly=0.15, lp=6500, hp=200, opt=dict(duty=0.25)),
    'bell': dict(type='mel', inst='bell', gain=0.17, pan=0.25, rev=0.45, dly=0.25, lp=9000, hp=300),
    'choir': dict(type='padmel', inst='choir', gain=0.42, pan=0.0, rev=0.5, dly=0.0, lp=6000, hp=150),
    'bass': dict(type='bass', inst='slap', gain=0.42, pan=0.0, rev=0.02, dly=0.0, lp=3800, hp=30),
    'comp': dict(type='comp', inst='power', gain=0.24, pan=-0.45, rev=0.08, dly=0.0, lp=3600, hp=110, double=0.45),
    'arp': dict(type='arp', inst='psg', gain=0.12, pan=0.35, rev=0.22, dly=0.3, lp=7000, hp=250, opt=dict(duty=0.5)),
    'pad': dict(type='pad', inst='strings', gain=0.15, pan=0.0, rev=0.4, dly=0.0, lp=5500, hp=180),
    'drone': dict(type='drone', inst='drone', gain=0.26, pan=0.0, rev=0.25, dly=0.0, lp=1400, hp=25),
    'drums': dict(type='drums', gain=0.38, rev=0.15),
    'choirpad': dict(type='pad', inst='choir', gain=0.27, pan=0.0, rev=0.5, dly=0.0, lp=6000, hp=150, center=60),
    'toll': dict(type='mel', inst='toll', gain=0.30, pan=-0.1, rev=0.55, dly=0.0, lp=5000, hp=40),
    'ost': dict(type='arp', inst='stacc_str', gain=0.22, pan=-0.3, rev=0.3, dly=0.0, lp=5000, hp=150, low=52),
    'organ': dict(type='pad', inst='organ', gain=0.19, pan=0.15, rev=0.45, dly=0.0, lp=5000, hp=80, center=58),
    'brasspad': dict(type='comp', inst='brass', gain=0.16, pan=0.2, rev=0.3, dly=0.0, lp=4000, hp=120, center=62),
}


def build(song, which):
    """which = 'intro' | 'loop' | 'all'.  returns (events per channel, total_steps, step_sec, chmap)."""
    bar = song.get('bar', 16)
    sps = 60.0 / song['bpm'] / 4
    key_pc = pc_of(song['key'])
    mode = song.get('mode', 'minor')
    chmap = {}
    for name, cfg in DEFAULT_CH.items():
        chmap[name] = dict(cfg)
    for name, cfg in song.get('ch', {}).items():
        base = dict(chmap.get(name, {}))
        if 'like' in cfg:
            base = dict(chmap[cfg['like']])
        base.update(cfg)
        chmap[name] = base
    order = song.get(which, []) if which != 'all' else song.get('intro', []) + song.get('loop', [])
    ev = {k: [] for k in chmap}
    pos = 0.0
    for sname in order:
        sec = song['sections'][sname]
        nbars = sec['bars']
        slen = nbars * bar
        chords, clen = parse_chords(sec.get('chords', 'N'), bar)
        if clen < slen:  # repeat chord string to fill
            base, blen, k = list(chords), clen, 1
            while clen < slen:
                chords += [(st + k * blen, d, c) for st, d, c in base]
                clen += blen; k += 1
        def chord_at(step):
            for st, d, c in chords:
                if st <= step < st + d:
                    return c
            return chords[-1][2] if chords else None

        def next_chord(step):
            for st, d, c in chords:
                if st > step:
                    return c
            return chords[0][2]

        for cname, cfg in chmap.items():
            part = sec.get(cname)
            if part is None or part is False:
                continue
            typ = cfg['type']
            vol = sec.get('vol', {}).get(cname, 1.0)
            if typ in ('mel', 'padmel'):
                notes, ln = parse_mel(part) if isinstance(part, str) else (part, 0)
                if ln and abs(ln - slen) > 1e-6 and not sec.get('free'):
                    raise ValueError('%s/%s/%s: melody is %g steps, section is %d' % (song['id'], sname, cname, ln, slen))
                prev = None
                for st, d, m, fl in notes:
                    ev[cname].append(dict(t=(pos + st) * sps, d=d * sps, m=m, v=(1.0 if '!' in fl else 0.82) * vol,
                                          bend=2.0 if '~' in fl else (1.0 if '`' in fl else 0.0), stacc='*' in fl,
                                          glide=(prev - m) if ('^' in fl and prev) else None))
                    prev = m
                # harmony voice derived from this part (opt-in per section: harm=True or harm=<degree shift>)
                hv = sec.get('harm')
                if hv:
                    for hname, hcfg in chmap.items():
                        if hcfg.get('harm_of') != cname or sec.get(hname):
                            continue
                        sh = hcfg.get('shift', -2) if hv is True else hv
                        for st, d, m, fl in notes:
                            ev[hname].append(dict(t=(pos + st) * sps, d=d * sps, m=diatonic_shift(m, sh, key_pc, mode),
                                                  v=0.8 * vol, bend=0.0, stacc='*' in fl, glide=None))
            elif typ == 'bass':
                pat = _len_ok(BASS.get(part, part), bar)
                low = cfg.get('low', 28)
                for b in range(nbars):
                    for i, c in enumerate(pat):
                        if c in '.-':
                            continue
                        st = b * bar + i
                        ch = chord_at(st)
                        if ch is None:
                            continue
                        j = i + 1
                        while j < len(pat) and pat[j] == '-':
                            j += 1
                        d = (j - i) if (j - i) > 1 else 0.9
                        root = bass_note(ch, low)
                        if c in 'Rx': m = root
                        elif c == 'O': m = root + 12
                        elif c == '5': m = root + 7
                        elif c == '3': m = root + (ch['iv'][1] if len(ch['iv']) > 1 else 4)
                        elif c == '7': m = root + 10
                        elif c == 'A':
                            nc = chord_at(st + (bar - i)) or ch
                            m = bass_note(nc, low) - 1
                        else:
                            continue
                        ev[cname].append(dict(t=(pos + st) * sps, d=d * sps, m=m, v=(0.85 if c != 'x' else 0.5) * vol, ghost=c == 'x'))
            elif typ == 'comp':
                pat = _len_ok(COMP.get(part, part), bar)
                for b in range(nbars):
                    for i, c in enumerate(pat):
                        if c in '.-':
                            continue
                        st = b * bar + i
                        ch = chord_at(st)
                        if ch is None:
                            continue
                        j = i + 1
                        while j < len(pat) and pat[j] == '-':
                            j += 1
                        if part == 'pad':  # hold until chord changes
                            j = i + bar
                        d = j - i
                        if cfg['inst'] == 'power':
                            r = 40 + ((ch['root'] - 40) % 12)  # E2..D#3
                            ms = [r, r + 7, r + 12] if 3 not in ch['iv'] or True else [r, r + 7]
                            if 6 in ch['iv'][:3]: ms = [r, r + 6, r + 12]
                        else:
                            ms = voice(ch, cfg.get('center', 62))
                        ev[cname].append(dict(t=(pos + st) * sps, d=d * sps, ms=ms, v=(0.8 if c == 'm' else 0.9) * vol, mute=c == 'm'))
            elif typ == 'arp':
                pat = _len_ok(ARP.get(part, part), bar)
                for b in range(nbars):
                    for i, c in enumerate(pat):
                        if not c.isdigit():
                            continue
                        st = b * bar + i
                        ch = chord_at(st)
                        if ch is None:
                            continue
                        j = i + 1
                        while j < len(pat) and pat[j] == '-':
                            j += 1
                        tones = chord_tones(ch, cfg.get('low', 64))
                        ev[cname].append(dict(t=(pos + st) * sps, d=(j - i) * sps, m=tones[int(c)], v=0.75 * vol, bend=0, stacc=False, glide=None))
            elif typ == 'pad':
                inst = part if isinstance(part, str) and part != 'x' and part is not True else None
                for st, d, ch in chords:
                    if ch is None or st >= slen:
                        continue
                    for m in voice(ch, cfg.get('center', 62)):
                        ev[cname].append(dict(t=(pos + st) * sps, d=min(d, slen - st) * sps, m=m, v=0.7 * vol))
            elif typ == 'drone':
                m = note_num(part) if isinstance(part, str) else None
                if m is not None:
                    ev[cname].append(dict(t=pos * sps, d=slen * sps, m=m, v=0.8 * vol))
                else:
                    for st, d, ch in chords:
                        if ch is None: continue
                        ev[cname].append(dict(t=(pos + st) * sps, d=d * sps, m=bass_note(ch, 28), v=0.8 * vol))
            elif typ == 'drums':
                pat = DRUMS[part] if isinstance(part, str) else part
                fill = sec.get('fill', 'fill' if nbars >= 4 else None)
                fillp = FILLS.get(fill, fill) if fill else None
                extra = sec.get('perc', {})
                for b in range(nbars):
                    use = fillp if (fillp and b == nbars - 1) else pat
                    lines = dict(use)
                    for kname, kpat in extra.items():
                        if not (fillp and b == nbars - 1) or kname in ('T', 'b'):
                            lines[kname] = kpat
                    if b == 0 and sec.get('crash', True):
                        lines = dict(lines); lines['c'] = 'x' + (lines.get('c', '')[1:] if lines.get('c') else '')
                    for dn, p in lines.items():
                        if not p:
                            continue
                        plen = len(p)
                        for i in range(bar):
                            c = p[(i + (b * bar) % plen) % plen] if plen > bar else (p[i] if i < plen else '.')
                            if c in 'xXo':
                                v = {'x': 0.8, 'X': 1.0, 'o': 0.38}[c]
                                if dn in ('h', 'sh') and i % 2: v *= 0.75
                                ev[cname].append(dict(t=(pos + b * bar + i) * sps, dn=dn, v=v * vol))
        pos += slen
    return ev, pos, sps, chmap
