// 시험용 가짜 그록 봇 + 가짜 깃허브 (공동 개발 시험용). 쓰는 법은 공동개발_규칙.md 「시험」
const http = require('http'), fs = require('fs');
const comments = []; let n = 100;
http.createServer((q, s) => { let d = ''; q.on('data', (c) => (d += c)); q.on('end', () => {
  if (q.url === '/hook' && q.method === 'POST') {
    fs.appendFileSync('hook.log', (q.headers.authorization === 'Bearer hook-key' ? 'AUTH_OK ' : 'AUTH_BAD ') + d + '\n');
    const b = JSON.parse(d); const id = (b.command.match(/\[relay:([0-9a-f]+)\]/) || [])[1];
    setTimeout(() => comments.push({ id: ++n, body: `[그록] [relay:${id}]\n그록 봇이에요. 망토는 진홍색이 좋아요!` }), 2000);
    s.end('{"ok":true}'); return;
  }
  if (q.url === '/add' && q.method === 'POST') { comments.push({ id: ++n, body: d }); return s.end('ok'); }
  if (q.url.startsWith('/repos/meca12944/thor-like-game/issues/207/comments')) { s.setHeader('content-type', 'application/json'); s.setHeader('x-ratelimit-remaining', '50'); return s.end(JSON.stringify(comments.slice().reverse())); }
  s.statusCode = 404; s.end('{}');
}); }).listen(7810);
