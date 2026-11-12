import json,re,collections
SRC='/workspace/pixellab_bg_20261111'
def verdict(s):
    s=(s or '').strip()
    if s.startswith('OK'): return 'ok'
    if s.startswith('보통'): return 'soso'
    return 'reject'
def slot_of(jid):
    s=re.sub(r'^(rd_|fl_)','',jid)
    while True:
        n=re.sub(r'_(s\d+|r\d+|std\d+|pro\d+|[abc])$','',s)
        if n==s: break
        s=n
    return s
def chapter_of(j):
    g=j['group']
    m=re.search(r'ch(\d)',g)
    if m: return int(m.group(1))
    m=re.search(r'ch(\d)',j.get('item',''))
    if m: return int(m.group(1))
    m=re.match(r'(?:rd_|fl_)?c(\d)_',j['id'])
    return int(m.group(1)) if m else 2
def type_of(j):
    e=j['endpoint']; g=j['group']
    if e=='/create-tileset': return 'tileset'
    if e=='/create-room': return 'room'
    if e=='/create-tiles-pro':
        if 'decal' in g or 'decal' in j['id']: return 'decal'
        return 'kit'
    if e=='/map-objects':
        p=j.get('params',{})
        if 'init_image' in p or 'ext' in j['id'] or 'shanty' in j['id'] or 'building' in j['id']: return 'building'
        return 'prop'
    return None
