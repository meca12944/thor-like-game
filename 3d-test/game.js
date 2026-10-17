import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/GLTFLoader.js';
import { clone as skClone } from 'three/addons/SkeletonUtils.js';

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x9fc4d6);
scene.fog = new THREE.Fog(0x9fc4d6, 30, 62);

const camera = new THREE.PerspectiveCamera(32, innerWidth / innerHeight, 1, 120);
const CAM_ANGLE = THREE.MathUtils.degToRad(51);
const camOff = new THREE.Vector3();
function setCam() { const a = innerWidth / innerHeight, d = a < 1 ? 26 + (1 / a - 1) * 14 : 24; camOff.set(0, Math.sin(CAM_ANGLE) * d, Math.cos(CAM_ANGLE) * d); }
setCam();

scene.add(new THREE.HemisphereLight(0xfff1d6, 0x5a6b48, 1.1));
const sun = new THREE.DirectionalLight(0xffd9a8, 2.6);
sun.position.set(-10, 18, 8);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -26, right: 26, top: 26, bottom: -26, near: 1, far: 60 });
sun.shadow.bias = -0.0005; sun.shadow.normalBias = 0.03; sun.shadow.radius = 4;
scene.add(sun, sun.target);

// ---------- ground: procedural cobblestone plaza + grass ----------
function cobbleTex() {
  const c = document.createElement('canvas'); c.width = c.height = 512; const g = c.getContext('2d');
  g.fillStyle = '#6b6156'; g.fillRect(0, 0, 512, 512);
  let rnd = 7; const R = () => (rnd = (rnd * 16807) % 2147483647) / 2147483647;
  for (let row = 0; row < 16; row++) for (let col = 0; col < 13; col++) {
    const x = col * 40 + (row % 2) * 20 + R() * 4, y = row * 32 + R() * 3;
    const v = 140 + R() * 50 | 0;
    g.fillStyle = `rgb(${v},${v - 8},${v - 20})`;
    g.beginPath(); g.roundRect(x + 2, y + 2, 34 + R() * 4, 27, 9); g.fill();
    g.fillStyle = 'rgba(255,240,210,.12)'; g.beginPath(); g.roundRect(x + 5, y + 4, 26, 9, 5); g.fill();
  }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4; return t;
}
function grassTex() {
  const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d');
  g.fillStyle = '#6d9a4a'; g.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 1400; i++) { const v = Math.random(); g.fillStyle = v < .5 ? '#5f8c3f' : '#7eab55'; g.fillRect(Math.random() * 256, Math.random() * 256, 2, 4); }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; return t;
}
const gt = grassTex(); gt.repeat.set(30, 30);
const grass = new THREE.Mesh(new THREE.PlaneGeometry(120, 120), new THREE.MeshLambertMaterial({ map: gt }));
grass.rotation.x = -Math.PI / 2; grass.receiveShadow = true; scene.add(grass);
const ct = cobbleTex(); ct.repeat.set(6, 6);
const plaza = new THREE.Mesh(new THREE.CircleGeometry(12.5, 48), new THREE.MeshLambertMaterial({ map: ct }));
plaza.rotation.x = -Math.PI / 2; plaza.position.y = 0.01; plaza.receiveShadow = true; scene.add(plaza);
const pt = cobbleTex(); pt.repeat.set(1, 8);
for (const [x, z, w, h] of [[0, 19, 4, 14], [-19, 0, 14, 4], [19, 0, 14, 4]]) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshLambertMaterial({ map: pt }));
  m.rotation.x = -Math.PI / 2; m.position.set(x, 0.008, z); m.receiveShadow = true; scene.add(m);
}
// soft blob shadows (fake AO) under characters
const blobTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d');
  const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(0,0,0,.45)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(c); })();
const blobMat = new THREE.MeshBasicMaterial({ map: blobTex, transparent: true, depthWrite: false });
function blob(r) { const m = new THREE.Mesh(new THREE.PlaneGeometry(r * 2, r * 2), blobMat); m.rotation.x = -Math.PI / 2; m.position.y = 0.03; return m; }

// ---------- loading ----------
const loader = new GLTFLoader();
const cache = {};
const load = url => cache[url] ??= loader.loadAsync(url);
const kk = n => `assets/kk/${n}/${n}.gltf`;
const colliders = []; // {x,z,r} circles or {box:[minx,minz,maxx,maxz]}

function prep(obj, shadow = true) {
  obj.traverse(o => { if (o.isMesh) { o.castShadow = shadow; o.receiveShadow = true;
    if (o.material && o.material.isMeshStandardMaterial) { o.material.roughness = Math.max(o.material.roughness, .8); o.material.metalness = 0; } } });
  return obj;
}
async function place(url, x, z, { h = 1, rot = 0, col = 'circle', cr = null, shadow = true } = {}) {
  const g = await load(url);
  const o = prep(g.scene.clone(true), shadow);
  const b = new THREE.Box3().setFromObject(o), s = h / (b.max.y - b.min.y);
  o.scale.setScalar(s); o.rotation.y = rot; o.position.set(x, -b.min.y * s, z);
  scene.add(o); o.updateMatrixWorld(true);
  const bb = new THREE.Box3().setFromObject(o);
  if (col === 'box') colliders.push({ box: [bb.min.x + .15, bb.min.z + .15, bb.max.x - .15, bb.max.z - .15] });
  else if (col === 'circle') colliders.push({ x, z, r: cr ?? Math.min(bb.max.x - bb.min.x, bb.max.z - bb.min.z) * .42 });
  return o;
}

async function buildTown() {
  const P = [];
  // houses ring
  P.push(place(kk('building_tavern_yellow'), -9, -12, { h: 6.5, col: 'box' }));
  P.push(place(kk('building_home_A_blue'), -1, -14, { h: 5.5, col: 'box' }));
  P.push(place(kk('building_home_B_red'), 7, -12.5, { h: 5.5, rot: .3, col: 'box' }));
  P.push(place(kk('building_blacksmith_red'), 14.5, -6, { h: 5, rot: -.6, col: 'box' }));
  P.push(place(kk('building_home_A_green'), -15, -5, { h: 5.5, rot: .5, col: 'box' }));
  P.push(place(kk('building_market_yellow'), -14, 8, { h: 4.5, rot: 1.2, col: 'box' }));
  P.push(place(kk('building_home_B_red'), 14, 9, { h: 5.5, rot: -1.1, col: 'box' }));
  P.push(place(kk('building_well_blue'), 7, 6, { h: 2.4, cr: 1.1 }));
  // fountain center
  P.push(place('assets/town/fountain-round-detail.glb', 0, 0, { h: 1.0, cr: 1.9 }));
  // stalls
  P.push(place('assets/town/stall-red.glb', -7, -5, { h: 2.6, rot: .8, col: 'box' }));
  P.push(place('assets/town/stall-green.glb', 6.5, -6, { h: 2.6, rot: -.6, col: 'box' }));
  P.push(place('assets/town/cart.glb', -8.5, 5.5, { h: 1.0, rot: 2.2 }));
  for (const [x, z] of [[-4, -9], [4.5, -9.5], [-10, 1], [10, 2], [-3, 10], [3, 10]]) P.push(place('assets/town/lantern.glb', x, z, { h: 2.1, cr: .3 }));
  // props
  for (const [n, x, z, h] of [['barrel', -5.2, -10.5, 1], ['barrel', -4.3, -11, 1], ['crate_A_big', 9.5, -9, 1], ['crate_B_small', 10.4, -8.3, .7], ['sack', -9.5, -6.5, .7],
    ['bucket_water', 8.3, 7.4, .5], ['wheelbarrow', 11.5, -3, 1], ['barrel', 12, 4.5, 1], ['crate_A_big', -11.5, 4, 1]])
    P.push(place(kk(n), x, z, { h, rot: Math.random() * 6, cr: h * .45 }));
  // trees
  const trees = [[-20, -14], [-18, -18], [20, -14], [18, -18], [-22, 4], [-21, 12], [22, 4], [21, 13], [-8, 18], [8, 18], [-14, 16], [14, 17], [-4, -20], [4, -20], [-24, -6], [24, -6], [-10, -19], [11, -19]];
  trees.forEach(([x, z], i) => P.push(place(`assets/nature/${['tree_oak', 'tree_default', 'tree_detailed'][i % 3]}.glb`, x, z, { h: 4.5 + (i % 4) * .6, rot: i, cr: .7 })));
  // rocks
  for (const [x, z, h] of [[-17, 14, 1.2], [17, -15, 1.4], [-6, 15, .6], [9, 14, .8], [16, 2, .6]]) P.push(place(kk('rock_single_C'), x, z, { h, rot: x, cr: h * .8 }));
  // flowers / grass (no collision, no shadow)
  let s = 3; const R = () => (s = (s * 16807) % 2147483647) / 2147483647;
  const fl = ['flower_redA', 'flower_yellowA', 'flower_purpleA', 'grass_large', 'grass'];
  for (let i = 0; i < 70; i++) {
    const a = R() * Math.PI * 2, d = 13.2 + R() * 7; const x = Math.cos(a) * d, z = Math.sin(a) * d;
    if (Math.abs(x) < 2.5 && z > 0) continue; if (Math.abs(z) < 2.5 && Math.abs(x) > 12) continue;
    P.push(place(`assets/nature/${fl[i % 5]}.glb`, x, z, { h: .5 + R() * .3, rot: R() * 6, col: 'none', shadow: false }));
  }
  // flower beds around fountain
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; P.push(place(`assets/nature/${fl[i % 3]}.glb`, Math.cos(a) * 3.3, Math.sin(a) * 3.3, { h: .45, col: 'none', shadow: false })); }
  // fences along south edge
  for (let i = -6; i <= 6; i++) { if (Math.abs(i) < 2) continue; P.push(place('assets/nature/fence_simple.glb', i * 1.6, 15, { h: .9, col: 'none' })); }
  colliders.push({ box: [-11, 14.8, -2.6, 15.3] }, { box: [2.6, 14.8, 11, 15.3] });
  await Promise.all(P);
}

// ---------- characters ----------
async function makeChar(file, h, keep) {
  const g = await load(`assets/chars/${file}.glb`);
  const o = skClone(g.scene); prep(o);
  if (keep) o.traverse(m => { if (m.isMesh && keep.hide.some(n => m.name.startsWith(n))) m.visible = false; });
  const b = new THREE.Box3().setFromObject(o); const s = h / (b.max.y - b.min.y); o.scale.setScalar(s);
  const root = new THREE.Group(); root.add(o); root.add(blob(.55)); scene.add(root);
  const mixer = new THREE.AnimationMixer(o); const acts = {};
  for (const c of g.animations) acts[c.name] = mixer.clipAction(c);
  let cur = null;
  const play = (n, fade = .15, once = false) => { const a = acts[n]; if (!a || cur === a) return a; a.reset(); a.setLoop(once ? THREE.LoopOnce : THREE.LoopRepeat); a.clampWhenFinished = once; a.fadeIn(fade).play(); cur?.fadeOut(fade); cur = a; return a; };
  return { root, mixer, acts, play, get cur() { return cur; } };
}

const hero = { x: 0, z: 6, face: Math.PI, hp: 6, maxHp: 6, atkT: 0, hurtT: 0 };
const enemies = [], npcs = [];
const keys = {}; const joy = { x: 0, z: 0 };
let attackPressed = false;

function collide(p, r) {
  for (const c of colliders) {
    if (c.box) { const [a, b, cx, d] = c.box; const nx = Math.max(a, Math.min(p.x, cx)), nz = Math.max(b, Math.min(p.z, d));
      const dx = p.x - nx, dz = p.z - nz, dd = dx * dx + dz * dz;
      if (dd < r * r) { if (dd > 1e-6) { const k = (r - Math.sqrt(dd)) / Math.sqrt(dd); p.x += dx * k; p.z += dz * k; }
        else { const o = [p.x - a, cx - p.x, p.z - b, d - p.z]; const m = Math.min(...o); if (m === o[0]) p.x = a - r; else if (m === o[1]) p.x = cx + r; else if (m === o[2]) p.z = b - r; else p.z = d + r; } } }
    else { const dx = p.x - c.x, dz = p.z - c.z, d = Math.hypot(dx, dz), m = c.r + r; if (d < m && d > 1e-4) { p.x = c.x + dx / d * m; p.z = c.z + dz / d * m; } }
  }
  const d = Math.hypot(p.x, p.z); if (d > 23) { p.x *= 23 / d; p.z *= 23 / d; }
}

function makeSlime(x, z, color) {
  const geo = new THREE.SphereGeometry(.6, 20, 14); geo.translate(0, .45, 0);
  const pos = geo.attributes.position; for (let i = 0; i < pos.count; i++) if (pos.getY(i) < .45) pos.setY(i, .45 - (.45 - pos.getY(i)) * .75);
  geo.computeVertexNormals();
  const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color, roughness: .25, transparent: true, opacity: .9 }));
  m.castShadow = true;
  const eyeM = new THREE.MeshBasicMaterial({ color: 0x1b1b1b });
  for (const sx of [-.18, .18]) { const e = new THREE.Mesh(new THREE.SphereGeometry(.07, 8, 6), eyeM); e.position.set(sx, .65, .5); m.add(e); }
  const root = new THREE.Group(); root.add(m, blob(.6)); root.position.set(x, 0, z); scene.add(root);
  return { kind: 'slime', root, body: m, x, z, hp: 2, vx: 0, vz: 0, t: Math.random() * 6, r: .55, dead: 0, home: [x, z], hurt: 0 };
}

const $ = id => document.getElementById(id);
function hud() { $('hearts').textContent = '❤'.repeat(Math.max(0, hero.hp)) + '♡'.repeat(hero.maxHp - Math.max(0, hero.hp)); }
let msgT; function say(t) { const m = $('msg'); m.textContent = t; m.style.opacity = 1; clearTimeout(msgT); msgT = setTimeout(() => m.style.opacity = 0, 1800); }

async function init() {
  await buildTown();
  hero.c = await makeChar('Knight', 1.9, { hide: ['2H_Sword', '1H_Sword_Offhand', 'Badge_Shield', 'Rectangle_Shield', 'Spike_Shield'] });
  hero.c.play('Idle');
  hero.c.mixer.addEventListener('finished', () => { hero.atkT = 0; });
  for (const [f, x, z, rot, hide] of [['Mage', -4.5, -7, .4, []], ['Rogue_Hooded', 4, -3.8, -1, []], ['Barbarian', 9.2, 4.8, -2.2, []]]) {
    const n = await makeChar(f, 1.85, { hide }); n.root.position.set(x, 0, z); n.root.rotation.y = rot;
    n.play(f === 'Barbarian' ? 'Sit_Floor_Idle' : 'Idle'); n.acts.Idle && (n.acts.Idle.time = Math.random());
    npcs.push(n); colliders.push({ x, z, r: .45 });
  }
  for (const [x, z] of [[-6, 11], [6.5, 11.5]]) {
    const s = await makeChar('Skeleton_Minion', 1.8, { hide: [] }); s.root.position.set(x, 0, z); s.play('Idle_Combat') || s.play('Idle');
    s.mixer.addEventListener('finished', e => { if (e.action === s.acts.Hit_A) s.play('Idle_Combat'); });
    enemies.push({ kind: 'skel', c: s, root: s.root, x, z, hp: 3, vx: 0, vz: 0, r: .45, dead: 0, home: [x, z], hurt: 0, t: 0 });
  }
  enemies.push(makeSlime(-3, 13, 0x6fdc5b), makeSlime(2.5, 12.6, 0x5bb8dc), makeSlime(17, -1, 0xe07ad0));
  hud(); $('load').remove();
}

// ---------- input ----------
addEventListener('keydown', e => { keys[e.code] = true; if (e.code === 'KeyZ' || e.code === 'Space') attackPressed = true; });
addEventListener('keyup', e => keys[e.code] = false);
const joyEl = $('joy'), knob = $('knob'); let joyId = null;
function joyMove(t) { const r = joyEl.getBoundingClientRect(); let dx = t.clientX - (r.left + r.width / 2), dy = t.clientY - (r.top + r.height / 2);
  const d = Math.hypot(dx, dy), m = 50; if (d > m) { dx *= m / d; dy *= m / d; }
  knob.style.transform = `translate(${dx}px,${dy}px)`; joy.x = dx / m; joy.z = dy / m; }
joyEl.addEventListener('pointerdown', e => { joyId = e.pointerId; joyEl.setPointerCapture(e.pointerId); joyMove(e); });
joyEl.addEventListener('pointermove', e => { if (e.pointerId === joyId) joyMove(e); });
const joyEnd = e => { if (e.pointerId === joyId) { joyId = null; joy.x = joy.z = 0; knob.style.transform = ''; } };
joyEl.addEventListener('pointerup', joyEnd); joyEl.addEventListener('pointercancel', joyEnd);
$('atk').addEventListener('pointerdown', e => { e.preventDefault(); attackPressed = true; });

// ---------- loop ----------
const clock = new THREE.Clock();
const camTarget = new THREE.Vector3(hero.x, 0, hero.z);
function update(dt) {
  if (!hero.c) return;
  let ix = (keys.KeyD || keys.ArrowRight ? 1 : 0) - (keys.KeyA || keys.ArrowLeft ? 1 : 0) + joy.x;
  let iz = (keys.KeyS || keys.ArrowDown ? 1 : 0) - (keys.KeyW || keys.ArrowUp ? 1 : 0) + joy.z;
  const il = Math.hypot(ix, iz); if (il > 1) { ix /= il; iz /= il; }
  hero.hurtT = Math.max(0, hero.hurtT - dt);
  if (attackPressed && hero.atkT <= 0 && hero.hp > 0) {
    hero.atkT = .55; hero.hitDone = false;
    const a = hero.c.play('1H_Melee_Attack_Slice_Horizontal', .08, true); a.timeScale = 1.6;
  }
  attackPressed = false;
  if (hero.atkT > 0) {
    hero.atkT -= dt;
    if (!hero.hitDone && hero.atkT < .35) { hero.hitDone = true;
      const fx = Math.sin(hero.face), fz = Math.cos(hero.face);
      for (const e of enemies) { if (e.dead) continue; const dx = e.x - hero.x, dz = e.z - hero.z, d = Math.hypot(dx, dz);
        if (d < 2.1 && (dx * fx + dz * fz) / (d || 1) > -.1) { e.hp--; e.hurt = .3; const k = e.kind === 'slime' ? 11 : 8; e.vx = dx / d * k; e.vz = dz / d * k;
          if (e.kind === 'skel') { if (e.hp <= 0) e.c.play('Death_A', .1, true); else e.c.play('Hit_A', .05, true); }
          if (e.hp <= 0) { e.dead = 1e-3; if (enemies.every(q => q.dead)) say('마을을 지켰다!'); } } }
    }
    if (hero.atkT <= 0) hero.c.play('Idle');
  } else if (il > .1 && hero.hp > 0) {
    const sp = 5 * Math.min(1, il); hero.x += ix * sp * dt; hero.z += iz * sp * dt;
    const tf = Math.atan2(ix, iz); let df = tf - hero.face; df = Math.atan2(Math.sin(df), Math.cos(df)); hero.face += df * Math.min(1, dt * 14);
    hero.c.play(il > .6 ? 'Running_A' : 'Walking_A');
  } else if (hero.hp > 0) hero.c.play('Idle');
  collide(hero, .45);
  hero.c.root.position.set(hero.x, 0, hero.z); hero.c.root.rotation.y = hero.face;
  hero.c.root.visible = hero.hurtT > 0 ? (performance.now() / 70 | 0) % 2 === 0 : true;
  hero.c.mixer.update(dt);
  npcs.forEach(n => n.mixer.update(dt));

  for (const e of enemies) {
    e.t += dt;
    if (e.dead) {
      e.dead += dt; e.x += e.vx * dt; e.z += e.vz * dt; e.vx *= .9; e.vz *= .9;
      if (e.kind === 'slime') { const s = Math.max(0, 1 - e.dead * 2.5); e.body.scale.set(1 + e.dead * 2, s, 1 + e.dead * 2); if (s === 0) e.root.visible = false; }
      else { e.c.mixer.update(dt); if (e.dead > 2.5) e.root.position.y = -(e.dead - 2.5); if (e.dead > 4) e.root.visible = false; }
      e.root.position.x = e.x; e.root.position.z = e.z; continue;
    }
    const dx = hero.x - e.x, dz = hero.z - e.z, d = Math.hypot(dx, dz);
    let mx = 0, mz = 0;
    if (e.hurt > 0) e.hurt -= dt;
    else if (d < 7) { mx = dx / d; mz = dz / d; } else { const hx = e.home[0] - e.x, hz = e.home[1] - e.z, hd = Math.hypot(hx, hz); if (hd > .5) { mx = hx / hd * .5; mz = hz / hd * .5; } }
    const sp = e.kind === 'slime' ? (Math.sin(e.t * 6) > 0 ? 2.6 : .4) : 1.9;
    e.x += (mx * sp + e.vx) * dt; e.z += (mz * sp + e.vz) * dt; e.vx *= Math.pow(.02, dt); e.vz *= Math.pow(.02, dt);
    collide(e, e.r);
    if (d < .95 && hero.hurtT <= 0 && hero.hp > 0 && e.hurt <= 0) { hero.hp--; hero.hurtT = 1; hud(); hero.x += dx / d * .8; hero.z += dz / d * .8;
      if (hero.hp <= 0) { hero.c.play('Death_A', .1, true); say('쓰러졌다… 3초 뒤 부활'); setTimeout(() => { hero.hp = hero.maxHp; hero.x = 0; hero.z = 6; hero.atkT = 0; hero.c.play('Idle'); hud(); }, 3000); } }
    e.root.position.set(e.x, 0, e.z);
    if (mx || mz) e.root.rotation.y = Math.atan2(mx, mz);
    if (e.kind === 'slime') { const b = Math.abs(Math.sin(e.t * 6)); e.body.scale.set(1 + (1 - b) * .15, .85 + b * .25, 1 + (1 - b) * .15); e.body.position.y = b * .25;
      e.body.material.emissive.setHex(e.hurt > 0 ? 0x662222 : 0); }
    else { if (e.c.cur !== e.c.acts.Hit_A || !e.c.cur.isRunning()) e.c.play(mx || mz ? 'Walking_A' : 'Idle_Combat'); e.c.mixer.update(dt); }
  }
  camTarget.lerp(new THREE.Vector3(hero.x, 0, hero.z), Math.min(1, dt * 5));
  camera.position.copy(camTarget).add(camOff); camera.lookAt(camTarget.x, camTarget.y + .6, camTarget.z);
  sun.target.position.copy(camTarget); sun.position.copy(camTarget).add(new THREE.Vector3(-10, 18, 8));
}
renderer.setAnimationLoop(() => { const dt = Math.min(clock.getDelta(), .05); update(dt); renderer.render(scene, camera); });
addEventListener('resize', () => { camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); setCam(); renderer.setSize(innerWidth, innerHeight); });
window.__game = { hero, enemies, renderer, keys, attack: () => attackPressed = true };
init().catch(e => { console.error(e); $('load').textContent = '로딩 실패: ' + e.message; });
