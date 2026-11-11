// 클로드 작업장 — 권한 창구 (클로드 코드가 "이거 해도 돼요?" 물을 때 회사 화면으로 넘겨 줌)
'use strict';
const http = require('http');
const OFFICE = process.env.OFFICE_URL || 'http://127.0.0.1:7788';
const EMP = process.env.OFFICE_EMP || '';
let buf = '';
function send(o) { process.stdout.write(JSON.stringify(o) + '\n'); }
function ask(toolName, input) {
  return new Promise((resolve) => {
    const body = JSON.stringify({ emp: EMP, tool_name: toolName, input });
    const u = new URL('/api/perm/ask', OFFICE);
    const req = http.request(u, { method: 'POST', headers: { 'content-type': 'application/json', 'content-length': Buffer.byteLength(body) }, timeout: 0 }, (res) => {
      let d = ''; res.setEncoding('utf8');
      res.on('data', (c) => (d += c));
      res.on('end', () => { try { resolve(JSON.parse(d)); } catch (e) { resolve({ allow: false, message: '회사 화면 답을 못 읽음' }); } });
    });
    req.on('error', () => resolve({ allow: false, message: '회사 화면이 꺼져 있어서 허락을 못 받음' }));
    req.end(body);
  });
}
async function handle(m) {
  if (m.method === 'initialize') return send({ jsonrpc: '2.0', id: m.id, result: { protocolVersion: (m.params && m.params.protocolVersion) || '2025-06-18', capabilities: { tools: {} }, serverInfo: { name: 'office', version: '1.0.0' } } });
  if (m.method === 'ping') return send({ jsonrpc: '2.0', id: m.id, result: {} });
  if (m.method === 'tools/list') return send({ jsonrpc: '2.0', id: m.id, result: { tools: [{ name: 'approve', description: 'Ask the office (the boss) whether a tool call may run.', inputSchema: { type: 'object', properties: { tool_name: { type: 'string' }, input: { type: 'object' }, tool_use_id: { type: 'string' } }, required: ['tool_name', 'input'] } }] } });
  if (m.method === 'tools/call') {
    const a = (m.params && m.params.arguments) || {};
    const r = await ask(a.tool_name, a.input || {});
    const out = r.allow ? { behavior: 'allow', updatedInput: a.input || {} } : { behavior: 'deny', message: r.message || '사장님이 거절함' };
    return send({ jsonrpc: '2.0', id: m.id, result: { content: [{ type: 'text', text: JSON.stringify(out) }] } });
  }
  if (m.id !== undefined) send({ jsonrpc: '2.0', id: m.id, error: { code: -32601, message: 'unknown method' } });
}
process.stdin.setEncoding('utf8');
process.stdin.on('data', (c) => {
  buf += c; let i;
  while ((i = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, i).trim(); buf = buf.slice(i + 1);
    if (!line) continue;
    try { handle(JSON.parse(line)); } catch (e) { /* 무시 */ }
  }
});
