// in-page: put the 5 scenefx objects around the hero (tiles) in the live map
window.__putSfx = (only) => { const H = __worldHooks, m = H.M(), h = H.hero, T = m.T, hx = Math.floor(h.x / T), hy = Math.floor(h.y / T);
  const L = [{ kind: 'shade', x: hx - 12, y: hy - 6, w: 24, h: 3 }, { kind: 'ashfall', x: hx + 7, y: hy - 7, w: 2, h: 9 }, { kind: 'updraft', x: hx - 10, y: hy + 2, w: 8, h: 4 },
    { kind: 'thread', x: hx - 11, y: hy - 2, w: 9, h: -5 }, { kind: 'lake', x: hx + 2, y: hy + 1, w: 10, h: 5 }].filter(o => !only || only.includes(o.kind));
  for (const o of L) m.objs.push(Object.assign({ type: 'scenefx', tx: o.x, ty: o.y, x: (o.x + .5) * T, y: (o.y + .5) * T }, o, { x: (o.x + .5) * T, y: (o.y + .5) * T })); m.sfxObjs = null; return L.length; };
window.__putOne = (kind) => { const H = __worldHooks, m = H.M(), h = H.hero, T = m.T, hx = Math.floor(h.x / T), hy = Math.floor(h.y / T);
  const o = { shade: { x: hx - 10, y: hy + 1, w: 20, h: 3 }, ashfall: { x: hx + 3, y: hy - 4, w: 2, h: 10 }, updraft: { x: hx - 9, y: hy + 1, w: 8, h: 4 }, thread: { x: hx - 9, y: hy + 4, w: 14, h: -8 }, lake: { x: hx + 2, y: hy - 2, w: 10, h: 6 } }[kind];
  m.objs = m.objs.filter(q => q.type !== 'scenefx'); m.objs.push(Object.assign({ type: 'scenefx', kind, tx: o.x, ty: o.y }, o, { x: (o.x + .5) * T, y: (o.y + .5) * T })); m.sfxObjs = null; return [hx, hy]; };
