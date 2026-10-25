// in-page helper: set the zoom of the area the hero stands in (compose maps) or the map
window.__setZ = z => { const H = __worldHooks, m = H.M(), h = H.hero; if (m.compose && m.areas) { const a = m.areas.find(a => h.x >= a.x * m.T && h.x < (a.x + a.w) * m.T && h.y >= a.y * m.T && h.y < (a.y + a.h) * m.T); if (a) { a.zoom = z; return a.id || 'area'; } } m.viewZoom = z; return 'map'; };
