#!/usr/bin/env node
// 그록 터널 — 클로드 직원이 그록(xAI)과 바로 이야기하고 그림·영상을 받는 도구.
// 쓰는 법 (직원 셸에서):
//   grok ask "질문" [--img 그림.png ...] [--thread 이름]      그록에게 묻기 (같은 thread 면 앞 대화를 기억)
//   grok image "그려 줄 것" --out 결과.png [--n 2] [--ref 참고그림.png]   그림 받기 (--ref 를 주면 그 그림을 고쳐 그림)
//   grok video "움직임 설명" --out 결과.mp4 [--img 첫장면.png] [--sec 6]    영상 받기
//   grok spent                                              오늘 쓴 돈
// 키는 회사 설정에만 있고, 이 도구는 환경 변수 XAI_API_KEY 로만 받는다. 키를 출력하지 않는다.
'use strict';
const fs = require('fs');
const path = require('path');
const http = require('http');

const BASE = (process.env.XAI_BASE_URL || 'https://api.x.ai').replace(/\/$/, '');
const KEY = process.env.XAI_API_KEY || '';
const DATA = path.join(process.env.OFFICE_DATA || path.join(__dirname, '..', 'data'), 'grok');
const M_CHAT = process.env.GROK_CHAT_MODEL || 'grok-4.7';
const M_IMG = process.env.GROK_IMAGE_MODEL || 'grok-imagine-image-2.0';
const M_VID = process.env.GROK_VIDEO_MODEL || 'grok-imagine-video-1.5';
const BUDGET = Number(process.env.GROK_DAILY_BUDGET || 5); // 하루 한도 (달러)
const PRICE = { image: 0.04, videoSec: 0.08, chat: 0.02 }; // 대략값 (xAI 가격표 2026-11)
fs.mkdirSync(DATA, { recursive: true });

function die(msg) { console.error('그록 터널: ' + msg); process.exit(1); }
function args(list) {
  const o = { _: [] };
  for (let i = 0; i < list.length; i++) {
    const a = list[i];
    if (a.startsWith('--')) { const k = a.slice(2); const v = list[i + 1] && !list[i + 1].startsWith('--') ? list[++i] : true; if (o[k] === undefined) o[k] = v; else o[k] = [].concat(o[k], v); }
    else o._.push(a);
  }
  return o;
}
const day = () => new Date().toISOString().slice(0, 10);
function spend(add) {
  const f = path.join(DATA, 'spend.json');
  let s = {}; try { s = JSON.parse(fs.readFileSync(f, 'utf8')); } catch (e) { /* */ }
  if (add) { s[day()] = Math.round(((s[day()] || 0) + add) * 1000) / 1000; fs.writeFileSync(f, JSON.stringify(s)); }
  return s[day()] || 0;
}
function guard(cost) {
  const used = spend(0);
  if (used + cost > BUDGET) die(`오늘 그록 한도 $${BUDGET} 를 넘어요 (쓴 돈 $${used.toFixed(2)}, 이번 $${cost.toFixed(2)}). 사장님께 한도를 올려 달라고 보고하세요.`);
}
function tellOffice(kind, text, files) {
  const url = process.env.OFFICE_URL; if (!url) return Promise.resolve();
  return new Promise((ok) => {
    const body = JSON.stringify({ emp: process.env.OFFICE_EMP || '', kind, text, files: (files || []).map((f) => path.resolve(f)) });
    const req = http.request(new URL('/api/grok/log', url), { method: 'POST', headers: { 'content-type': 'application/json', 'content-length': Buffer.byteLength(body) } }, (r) => { r.resume(); r.on('end', ok); });
    req.on('error', ok); req.end(body);
  });
}
// ── 반자동: 키가 없으면 회사 화면에 부탁을 띄우고, 사장님이 붙여 넣은 그록 답을 기다림 ──
function office(p, body) {
  return new Promise((ok, no) => {
    const data = JSON.stringify(body);
    const req = http.request(new URL(p, process.env.OFFICE_URL), { method: 'POST', headers: { 'content-type': 'application/json', 'content-length': Buffer.byteLength(data) } }, (r) => {
      let d = ''; r.setEncoding('utf8'); r.on('data', (c) => (d += c)); r.on('end', () => { try { ok(JSON.parse(d)); } catch (e) { no(new Error('회사 답을 못 읽음')); } });
    });
    req.on('error', () => no(new Error('회사 화면이 꺼져 있어요')));
    req.end(data);
  });
}
const PASTE = !KEY && !!process.env.OFFICE_URL;
async function waitRelay(id) {
  let r = { pending: true };
  while (r.pending) r = await office('/api/room/wait', { id, wait: 540000 });
  if (r.error) die(r.error);
  return r;
}
async function relay(kind, text, files) {
  const { id } = await office('/api/room/relay', { emp: process.env.OFFICE_EMP || '', kind, text, files: (files || []).map((f) => path.resolve(f)) });
  console.error(`그록 답 기다리는 중 (번호 ${id}) — 사장님이 그록 앱에 옮겨 주는 중이에요. 끊기면: grok wait ${id}`);
  return waitRelay(id);
}
async function relayFiles(r, out) {
  const files = (r.files || []).filter((f) => fs.existsSync(f));
  if (!files.length) { console.log(r.text || '(그록이 파일 없이 답했어요)'); return; }
  const saved = files.map((f, i) => { const o = numbered(out, i, files.length); fs.mkdirSync(path.dirname(path.resolve(o)), { recursive: true }); fs.copyFileSync(f, o); return path.resolve(o); });
  if (r.text) console.log(r.text);
  console.log(saved.join('\n'));
}

async function call(method, p, body) {
  if (!KEY) die('그록 키가 없어요. 사장님께 「설정 → 그록 키」를 넣어 달라고 보고하세요.');
  const r = await fetch(BASE + p, { method, headers: { authorization: 'Bearer ' + KEY, 'content-type': 'application/json' }, body: body ? JSON.stringify(body) : undefined });
  const t = await r.text();
  let j; try { j = JSON.parse(t); } catch (e) { j = { raw: t }; }
  if (!r.ok) die(`그록이 거절했어요 (${r.status}): ${(j.error && (j.error.message || j.error)) || j.raw || t}`.slice(0, 800));
  return j;
}
function dataUri(file) {
  const ext = path.extname(file).slice(1).toLowerCase().replace('jpg', 'jpeg');
  return `data:image/${ext || 'png'};base64,${fs.readFileSync(file).toString('base64')}`;
}
async function save(item, out) {
  fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
  if (item.b64_json) fs.writeFileSync(out, Buffer.from(item.b64_json, 'base64'));
  else if (item.url) { const r = await fetch(item.url); if (!r.ok) die('파일 받기 실패 ' + r.status); fs.writeFileSync(out, Buffer.from(await r.arrayBuffer())); }
  else die('그록 답에 파일이 없어요: ' + JSON.stringify(item).slice(0, 300));
  return out;
}
function numbered(out, i, n) { if (n <= 1) return out; const e = path.extname(out); return out.slice(0, out.length - e.length) + `_${i + 1}` + e; }

async function ask(o) {
  const text = o._.join(' ').trim(); if (!text) die('물을 말을 적어 주세요.');
  const thread = String(o.thread || 'main').replace(/[^\w가-힣-]/g, '_');
  const tf = path.join(DATA, 'thread_' + thread + '.json');
  let prev = null; try { prev = JSON.parse(fs.readFileSync(tf, 'utf8')).id; } catch (e) { /* 새 대화 */ }
  if (o.new) prev = null;
  const imgs = [].concat(o.img || []).filter((x) => x !== true);
  for (const f of imgs) if (!fs.existsSync(f)) die('그림이 없어요: ' + f);
  if (PASTE) { const r = await relay('chat', text, imgs); return console.log(r.text || '(그록이 그림만 보냈어요: ' + (r.files || []).join(', ') + ')'); }
  let content = imgs.length ? [{ type: 'input_text', text }, ...imgs.map((f) => ({ type: 'input_image', image_url: dataUri(f) }))] : text;
  guard(PRICE.chat);
  await tellOffice('ask', text, imgs);
  if (thread === 'room' && typeof content === 'string' && !/^\[클로드/.test(content)) content = '[클로드 직원] ' + content;
  const body = { model: o.model || M_CHAT, input: [{ role: 'user', content }] };
  if (prev) body.previous_response_id = prev;
  const j = await call('POST', '/v1/responses', body);
  let answer = j.output_text || '';
  if (!answer && Array.isArray(j.output)) for (const it of j.output) for (const c of it.content || []) if (c.type === 'output_text' && c.text) answer += c.text;
  fs.writeFileSync(tf, JSON.stringify({ id: j.id, time: new Date().toISOString() }));
  spend(PRICE.chat);
  await tellOffice('answer', answer || '(빈 답)');
  console.log(answer);
}
async function image(o) {
  const prompt = o._.join(' ').trim(); if (!prompt) die('그릴 것을 적어 주세요.');
  const out = typeof o.out === 'string' ? o.out : `grok_image_${Date.now()}.png`;
  const n = Math.max(1, Math.min(4, Number(o.n) || 1));
  if (PASTE) return relayFiles(await relay('image', prompt + (n > 1 ? ` (${n}장)` : ''), [].concat(o.ref || []).filter((x) => x !== true)), out);
  guard(PRICE.image * n);
  const refs = [].concat(o.ref || []).filter((x) => x !== true);
  await tellOffice('ask', '🎨 그림 부탁: ' + prompt, refs);
  let j;
  if (refs.length) j = await call('POST', '/v1/images/edits', { model: o.model || M_IMG, prompt, image: { url: dataUri(refs[0]), type: 'image_url' } });
  else j = await call('POST', '/v1/images/generations', { model: o.model || M_IMG, prompt, n });
  const files = [];
  for (const [i, it] of (j.data || []).entries()) files.push(await save(it, numbered(out, i, (j.data || []).length)));
  spend(PRICE.image * Math.max(1, files.length));
  await tellOffice('image', `그림 ${files.length}장 받음`, files);
  console.log(files.map((f) => path.resolve(f)).join('\n'));
}
async function video(o) {
  const prompt = o._.join(' ').trim(); if (!prompt) die('영상 설명을 적어 주세요.');
  const out = typeof o.out === 'string' ? o.out : `grok_video_${Date.now()}.mp4`;
  const sec = Math.max(1, Math.min(15, Number(o.sec) || 6));
  if (PASTE) return relayFiles(await relay('video', `${prompt} (${sec}초)`, typeof o.img === 'string' ? [o.img] : []), out);
  guard(PRICE.videoSec * sec);
  const img = typeof o.img === 'string' ? o.img : null;
  await tellOffice('ask', `🎬 영상 부탁 (${sec}초): ${prompt}`, img ? [img] : []);
  const body = { model: o.model || M_VID, prompt, duration: sec };
  if (img) body.image = { url: dataUri(img) };
  const start = await call('POST', '/v1/videos/generations', body);
  const id = start.request_id || start.id; if (!id) die('영상 번호를 못 받았어요: ' + JSON.stringify(start).slice(0, 300));
  const until = Date.now() + 15 * 60 * 1000;
  for (;;) {
    await new Promise((r) => setTimeout(r, 5000));
    const s = await call('GET', '/v1/videos/' + id);
    if (s.status === 'done' || (s.video && s.video.url)) { await save(s.video, out); break; }
    if (s.status === 'failed' || s.status === 'expired') die('영상 만들기 실패: ' + s.status + ' ' + JSON.stringify(s.error || '').slice(0, 300));
    if (Date.now() > until) die('15분이 지나도 영상이 안 나왔어요. 번호: ' + id);
  }
  spend(PRICE.videoSec * sec);
  await tellOffice('video', `영상 받음 (${sec}초)`, [out]);
  console.log(path.resolve(out));
}

(async () => {
  const [cmd, ...rest] = process.argv.slice(2);
  const o = args(rest);
  if (cmd === 'wait') { const r = await waitRelay(o._[0]); if (r.text) console.log(r.text); if ((r.files || []).length) console.log(r.files.join('\n')); return; }
  if (cmd === 'ask') return ask(o);
  if (cmd === 'image') return image(o);
  if (cmd === 'video') return video(o);
  if (cmd === 'spent') return console.log(`오늘 그록에 쓴 돈: $${spend(0).toFixed(2)} / 하루 한도 $${BUDGET}`);
  console.log('쓰는 법: grok ask "질문" | grok image "그림 설명" --out a.png | grok video "영상 설명" --out a.mp4 --img 첫장면.png | grok spent');
})().catch((e) => die(e.message));
