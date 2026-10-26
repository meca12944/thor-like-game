extends Node3D
# 필멸자 2.5D 시험 (Godot 4.3, gl_compatibility): 그록 그림 바닥(2D 그대로) + 3D 인형 주인공.
# 1 단위 = 지도 1칸(16px). 카메라 45도 아래로 → 바닥 세로를 KZ배로 늘려 2D 그림 비율을 그대로 보이게 함.

const PITCH := 30.0
var KZ := 1.0 / sin(deg_to_rad(PITCH))
const HERO_SCREEN_H := 42.0 / 16.0           # 화면 키 42px = 2.625칸
const SECS := 33.0

var hero: Node3D
var model: Node3D
var anim: AnimationPlayer
var cam: Camera3D
var dust: CPUParticles3D
var label: Label
var t := 0.0
var pos := Vector3(62, 0, 121)
var face := 0.0
var lean := 0.0
var cur_anim := ""
var tip: Node3D
var base: Node3D
var trail_mesh := ImmediateMesh.new()
var trail := []           # [base, tip, age]
var last_tip := Vector3.ZERO
var phase := 0            # 공격: 0 준비, 1 휘두름, 2 멈춤, 3 회복
var hold_t := 0.0
var shake := 0.0
var skel: Skeleton3D
const CHIBI := {} # 회의: 뼈 키우기 안 함 (옛 값 "Head": 1.3, "LeftUpLeg": 0.86, "RightUpLeg": 0.86, "Spine01": 0.95, "LeftArm": 0.95, "RightArm": 0.95, "LeftFoot": 1.25, "RightFoot": 1.25}   # 미니 귀여운 비율(뼈 크기, 크레딧 0)
var step_acc := 0.0
const STEP := 0.0   # 2D 느낌: 그림을 1초에 12장만 바꿈

# (이름, 방향, 초, 빠르기 칸/초) — 빠르기 0 = 서기
var plan := [
	["서기 (숨쉬기)", Vector2(0, 1), 1.6, 0.0, ""],
	["걷기 →", Vector2(1, 0), 1.4, 3.2, ""],
	["걷기 ↘", Vector2(1, 1), 1.2, 3.2, ""],
	["걷기 ↓", Vector2(0, 1), 1.0, 3.2, ""],
	["걷기 ↑", Vector2(0, -1), 1.0, 3.2, ""],
	["달리기 →", Vector2(1, 0), 1.6, 7.5, ""],
	["달리기 ← (180° 꺾기)", Vector2(-1, 0), 1.6, 7.5, ""],
	["달리다 멈춤", Vector2(-1, 0), 1.3, 0.0, "Sprint_and_Sudden_Stop"],
	["베기 1타", Vector2(1, 0), 2.3, 0.0, "Left_Slash"],
	["베기 2타", Vector2(1, 0), 1.3, 0.0, "Right_Hand_Sword_Slash"],
	["베기 3타 (모아 베기)", Vector2(1, 0), 1.9, 0.0, "Charged_Slash"],
	["회피대시 (구르기)", Vector2(1, 0), 1.4, 0.0, "Roll_Dodge"],
	["점프", Vector2(0, 1), 1.4, 0.0, "Regular_Jump"],
	["달리기 점프", Vector2(1, 0), 1.3, 0.0, "Jump_Run"],
	["맞기", Vector2(0, 1), 1.3, 0.0, "Hit_Reaction"],
	["크게 맞기 (날아감)", Vector2(0, 1), 1.8, 0.0, "BeHit_FlyUp"],
	["기술 1 (모아 쏘기)", Vector2(0, 1), 2.2, 0.0, "Charged_Spell_Cast"],
	["기술 2", Vector2(1, 0), 1.8, 0.0, "mage_soell_cast"],
	["기술 3", Vector2(0, 1), 1.8, 0.0, "mage_soell_cast_3"],
	["쓰러짐", Vector2(0, 1), 2.6, 0.0, "dying_backwards"],
]

func tex(p: String) -> ImageTexture:
	var img := Image.load_from_file("res://art/" + p + ".png")
	return ImageTexture.create_from_image(img)

func flat(p: String, tx: float, ty: float, d: float, h: float) -> void:
	var tt := tex(p)
	var w := tt.get_width() / 16.0 / d
	var hh := tt.get_height() / 16.0 / d
	var m := MeshInstance3D.new()
	var q := PlaneMesh.new()
	q.size = Vector2(w, hh * KZ)
	m.mesh = q
	var mat := StandardMaterial3D.new()
	mat.albedo_texture = tt
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
	mat.alpha_scissor_threshold = 0.5
	mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	m.material_override = mat
	m.position = Vector3(tx + w / 2.0, h, (ty + hh / 2.0) * KZ)
	add_child(m)

func _ready() -> void:
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color(0.2, 0.2, 0.2)
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.70, 0.70, 0.74)
	e.ambient_light_energy = 0.45
	e.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	env.environment = e
	add_child(env)

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-55, -35, 0)
	sun.light_energy = 1.0
	sun.light_color = Color(1.0, 0.93, 0.85)
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 80.0
	add_child(sun)

	# 바닥 = 동쪽 들판 그림 그대로 (빛 받지 않음 → 2D와 같은 색)
	flat("ground", 0, 0, 1.0, 0.0)
	flat("giant_knight", 26, 96, 1.6, 0.02)
	flat("giant_helmet", 96, 122, 1.0, 0.03)
	flat("giant_sword", 30, 150, 1.6, 0.03)
	flat("12a_collapsed_tower_back", 92, 128, 1.0, 0.03)
	flat("12d_ash_mound_hill_back", 30, 140, 1.0, 0.03)
	flat("12c_petrified_grove_back", 84, 140, 1.0, 0.03)

	# 그림자 받는 투명 바닥 (그림 위에 그림자만)
	var sh := MeshInstance3D.new()
	var sp := PlaneMesh.new()
	sp.size = Vector2(400, 400)
	sh.mesh = sp
	var smat := StandardMaterial3D.new()
	smat.shading_mode = BaseMaterial3D.SHADING_MODE_PER_PIXEL
	smat.albedo_color = Color(0.08, 0.06, 0.06, 0.55)
	smat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	smat.shadow_to_opacity = true
	sh.material_override = smat
	sh.position = Vector3(95, 0.05, 130 * KZ)
	add_child(sh)
	pos.z *= KZ

	# 주인공 = 3D 인형 (무료 공개 모델, 시험용)
	hero = Node3D.new()
	add_child(hero)
	model = load_glb("actions.glb")
	hero.add_child(model)
	var sc := base_sc()
	model.scale = Vector3(sc, sc, sc)
	anim = model.find_child("AnimationPlayer", true, false)
	anim.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	var lib: AnimationLibrary = anim.get_animation_library("")
	for extra in [["walking.glb", "Walk"], ["running.glb", "Run"]]:
		var m2 := load_glb(extra[0])
		var p2: AnimationPlayer = m2.find_child("AnimationPlayer", true, false)
		var nm: String = p2.get_animation_list()[0]
		lib.add_animation(extra[1], p2.get_animation(nm).duplicate())
	for n in ["Idle", "Walk", "Run"]:
		if anim.has_animation(n):
			anim.get_animation(n).loop_mode = Animation.LOOP_LINEAR
	var m3 := load_glb("actions2.glb")
	var p3: AnimationPlayer = m3.find_child("AnimationPlayer", true, false)
	for nm3 in p3.get_animation_list():
		lib.add_animation(nm3, p3.get_animation(nm3).duplicate())
	for n in anim.get_animation_list():
		if n in ["Idle", "Walk", "Run"]:
			continue
		anim.get_animation(n).loop_mode = Animation.LOOP_NONE
	# 3) 만화풍 빛 + 외곽선 + 테두리 빛
	var toon := load("res://toon.gdshader")
	var outl := load("res://outline.gdshader")
	for mi in model.find_children("*", "MeshInstance3D", true, false):
		add_face_mask(mi)
		for si in mi.mesh.get_surface_count():
			var om = mi.get_active_material(si)
			var sm := ShaderMaterial.new()
			sm.shader = toon
			if FileAccess.file_exists("res://art/base4k.png"):
				sm.set_shader_parameter("albedo_tex", tex("base4k"))
			elif om is BaseMaterial3D and om.albedo_texture:
				sm.set_shader_parameter("albedo_tex", om.albedo_texture)
			var ol := ShaderMaterial.new()
			ol.shader = outl
			sm.next_pass = ol
			mi.set_surface_override_material(si, sm)
	# 칼 (손에 붙임)
	skel = model.find_child("Skeleton3D", true, false)
	if skel:
		var ba := BoneAttachment3D.new()
		ba.bone_name = "RightHand"
		skel.add_child(ba)
		var blade_root := Node3D.new()
		blade_root.position = Vector3(0, 9.0, 0)
		ba.add_child(blade_root)
		var bmat := StandardMaterial3D.new()
		bmat.albedo_color = Color(0.86, 0.9, 0.95)
		bmat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		bmat.emission_enabled = true
		bmat.emission = Color(0.45, 0.85, 1.0)
		bmat.emission_energy_multiplier = 0.35
		for part in [[Vector3(3.2, 1.2, 105.0), Vector3(0, 0, 58.0), bmat], [Vector3(20.0, 3.0, 3.0), Vector3(0, 0, 6.0), null], [Vector3(3.0, 3.0, 14.0), Vector3(0, 0, -4.0), null]]:
			var mi2 := MeshInstance3D.new()
			var bx := BoxMesh.new()
			bx.size = part[0]
			mi2.mesh = bx
			if part[2]:
				mi2.material_override = part[2]
			else:
				var gm := StandardMaterial3D.new()
				gm.albedo_color = Color(0.55, 0.38, 0.18)
				mi2.material_override = gm
			mi2.position = part[1]
			blade_root.add_child(mi2)
		base = Node3D.new()
		base.position = Vector3(0, 0, 14.0)
		blade_root.add_child(base)
		tip = Node3D.new()
		tip.position = Vector3(0, 0, 110.0)
		blade_root.add_child(tip)
		# 2) 가슴 코어 푸른빛
		var cb := BoneAttachment3D.new()
		cb.bone_name = "Spine02"
		skel.add_child(cb)
		var gimg := Image.create(64, 64, false, Image.FORMAT_RGBA8)
		for yy in 64:
			for xx in 64:
				var rr := Vector2(xx - 31.5, yy - 31.5).length() / 32.0
				gimg.set_pixel(xx, yy, Color(0.5, 0.9, 1.0, pow(clamp(1.0 - rr, 0.0, 1.0), 2.0)))
		var core := MeshInstance3D.new()
		var cq := QuadMesh.new()
		cq.size = Vector2(26, 26)
		core.mesh = cq
		var cm := StandardMaterial3D.new()
		cm.albedo_texture = ImageTexture.create_from_image(gimg)
		cm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		cm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		cm.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
		cm.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
		cm.billboard_keep_scale = true
		core.material_override = cm
		core.position = Vector3(0, 6, 14)

	# 4) 청록 궤적
	var tr := MeshInstance3D.new()
	tr.mesh = trail_mesh
	var tm := StandardMaterial3D.new()
	tm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	tm.vertex_color_use_as_albedo = true
	tm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	tm.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	tm.cull_mode = BaseMaterial3D.CULL_DISABLED
	tr.material_override = tm
	add_child(tr)

	# 발밑 그림자 (둥근 반투명)
	var gi := Image.create(64, 64, false, Image.FORMAT_RGBA8)
	for yy in 64:
		for xx in 64:
			var r := Vector2(xx - 31.5, yy - 31.5).length() / 32.0
			gi.set_pixel(xx, yy, Color(0.05, 0.04, 0.04, clamp(1.0 - r, 0.0, 1.0) * 0.55))
	var blob := MeshInstance3D.new()
	var bp := PlaneMesh.new()
	bp.size = Vector2(1.9, 1.0 * KZ)
	blob.mesh = bp
	var blm := StandardMaterial3D.new()
	blm.albedo_texture = ImageTexture.create_from_image(gi)
	blm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	blm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	blob.material_override = blm
	blob.position = Vector3(0, 0.06, 0)
	hero.add_child(blob)

	# 먼지
	dust = CPUParticles3D.new()
	dust.amount = 24
	dust.lifetime = 0.6
	dust.emitting = false
	dust.direction = Vector3(0, 1, 0)
	dust.spread = 60.0
	dust.initial_velocity_min = 0.6
	dust.initial_velocity_max = 1.4
	dust.gravity = Vector3(0, -0.6, 0)
	dust.scale_amount_min = 0.12
	dust.scale_amount_max = 0.3
	dust.amount = 10
	var dm := SphereMesh.new()
	dm.radius = 0.5
	dm.height = 1.0
	var dmat := StandardMaterial3D.new()
	dmat.albedo_color = Color(0.62, 0.60, 0.58, 0.35)
	dmat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	dmat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	dm.material = dmat
	dust.mesh = dm
	hero.add_child(dust)

	cam = Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.size = 11.0
	cam.rotation_degrees = Vector3(-PITCH, 0, 0)
	add_child(cam)
	cam.current = true

	var ui := CanvasLayer.new()
	add_child(ui)
	label = Label.new()
	var f := FontFile.new()
	f.load_dynamic_font("res://art/NanumGothic.ttf")
	label.add_theme_font_override("font", f)
	label.add_theme_font_size_override("font_size", 26)
	label.add_theme_color_override("font_outline_color", Color.BLACK)
	label.add_theme_constant_override("outline_size", 4)
	label.position = Vector2(24, 18)
	ui.add_child(label)
	var sub := Label.new()
	sub.text = "시험 8 · 회의 결론 4~6: 2칸 빛·보랏빛 그림자·얼굴 평평하게 / 외곽선 몸 둘레만 / 부드러운 움직임 + 공격만 멈칫"
	sub.add_theme_font_override("font", f)
	sub.add_theme_font_size_override("font_size", 18)
	sub.add_theme_color_override("font_outline_color", Color.BLACK)
	sub.add_theme_constant_override("outline_size", 3)
	sub.position = Vector2(24, 680)
	ui.add_child(sub)

# 얼굴 표시: Head 뼈 무게 × 앞쪽(+Z) 법선 → 정점 색 R (회의 결론 3)
func add_face_mask(mi: MeshInstance3D) -> void:
	var sk: Skin = mi.skin
	if sk == null:
		return
	var head := -1
	for i in sk.get_bind_count():
		if sk.get_bind_name(i) == "Head":
			head = i
	if head < 0:
		return
	var old: ArrayMesh = mi.mesh
	var nm := ArrayMesh.new()
	for si in old.get_surface_count():
		var arr := old.surface_get_arrays(si)
		var bones: PackedInt32Array = arr[Mesh.ARRAY_BONES]
		var wts: PackedFloat32Array = arr[Mesh.ARRAY_WEIGHTS]
		var nrm: PackedVector3Array = arr[Mesh.ARRAY_NORMAL]
		var verts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
		var vc: int = verts.size()
		var per: int = bones.size() / max(vc, 1)
		var cols := PackedColorArray()
		cols.resize(vc)
		for v in vc:
			var w := 0.0
			for k in per:
				if bones[v * per + k] == head:
					w += wts[v * per + k]
			var fr: float = clamp((nrm[v].z - 0.15) * 2.5, 0.0, 1.0)
			cols[v] = Color(clamp(w * 1.4, 0.0, 1.0) * fr, 0, 0, 1)
		arr[Mesh.ARRAY_COLOR] = cols
		var fl := 0
		if per == 8:
			fl = Mesh.ARRAY_FLAG_USE_8_BONE_WEIGHTS
		nm.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr, [], {}, fl)
		nm.surface_set_material(si, old.surface_get_material(si))
	mi.mesh = nm

func load_glb(f: String) -> Node3D:
	var doc := GLTFDocument.new()
	var st := GLTFState.new()
	doc.append_from_file(ProjectSettings.globalize_path("res://art/" + f), st)
	return doc.generate_scene(st)

func play(n: String, spd: float) -> void:
	if cur_anim != n:
		anim.play(n, 0.12)
		cur_anim = n
		model.scale = Vector3.ONE * base_sc()
	if n.find("Slash") < 0:
		anim.speed_scale = spd

func _process(dt: float) -> void:
	t += dt
	if t > SECS:
		get_tree().quit()
		return
	var acc := 0.0
	var seg = plan[plan.size() - 1]
	var lt := 0.0
	for s in plan:
		if t < acc + s[2]:
			seg = s
			lt = t - acc
			break
		acc += s[2]
	label.text = seg[0]
	var spd: float = seg[3]
	var act: String = seg[4]
	var d: Vector2 = (seg[1] as Vector2).normalized()
	if spd < 0.0:
		# 제자리 8방향 돌기: 0.4초마다 45도
		var k := int(lt / 0.4)
		var a := k * PI / 4.0
		d = Vector2(cos(a), sin(a))
		spd = 0.0
	var want := atan2(d.x, d.y)
	face = lerp_angle(face, want, clamp(dt * 14.0, 0.0, 1.0))
	pos += Vector3(d.x, 0, d.y * KZ) * spd * dt
	hero.position = pos
	model.rotation.y = face
	var target_lean := 0.0
	var is_slash := act.find("Slash") >= 0
	if act != "":
		if cur_anim != act:
			phase = 0
		play(act, 1.0)
		if is_slash:
			punch(dt)
	elif spd > 5.0:
		play("Run", spd / 6.0)
		target_lean = 0.0
	elif spd > 0.0:
		play("Walk", spd / 2.6)
	else:
		play("Idle", 1.0)
	lean = lerp(lean, target_lean, clamp(dt * 8.0, 0.0, 1.0))
	dust.emitting = spd > 5.0
	dust.position = Vector3(0, 0.1, 0)
	step_acc += dt
	if step_acc >= STEP:
		anim.advance(step_acc)
		step_acc = 0.0
		for bn in CHIBI:
			var bi := skel.find_bone(bn)
			if bi >= 0:
				skel.set_bone_pose_scale(bi, Vector3.ONE * CHIBI[bn])
		var hb := skel.find_bone("Head")
		if hb >= 0:
			skel.set_bone_pose_rotation(hb, skel.get_bone_pose_rotation(hb).slerp(skel.get_bone_rest(hb).basis.get_rotation_quaternion(), 0.85))
	update_trail(dt, is_slash and (phase == 1 or phase == 2))
	shake = max(0.0, shake - dt)
	var sk := Vector3(randf_range(-1, 1), 0, randf_range(-1, 1)) * shake * 0.6
	cam.position = pos + sk + Vector3(0, sin(deg_to_rad(PITCH)), cos(deg_to_rad(PITCH))) * 60.0

# 5) 동작에 힘: 준비는 느리게, 휘두름은 빠르게, 휘두른 뒤 잠깐 멈춤(+화면 흔들림), 회복
func punch(dt: float) -> void:
	if not tip:
		return
	var tp := tip.global_position
	var v: float = (tp - last_tip).length() / max(dt, 1e-4) / max(anim.speed_scale, 0.05)
	last_tip = tp
	match phase:
		0:
			anim.speed_scale = 0.8
			model.scale = model.scale.lerp(Vector3.ONE * base_sc() * Vector3(1.03, 0.96, 1.03), 0.2)
			if v > 9.0:
				phase = 1
		1:
			anim.speed_scale = 2.1
			model.scale = model.scale.lerp(Vector3.ONE * base_sc() * Vector3(0.97, 1.05, 0.97), 0.4)
			if v < 5.0:
				phase = 2
				hold_t = 0.06
				shake = 0.12
		2:
			anim.speed_scale = 0.04
			hold_t -= dt
			if hold_t <= 0.0:
				phase = 3
		3:
			anim.speed_scale = 1.35
			model.scale = model.scale.lerp(Vector3.ONE * base_sc(), 0.2)

func base_sc() -> float:
	return HERO_SCREEN_H / cos(deg_to_rad(PITCH)) / 1.8 * 1.05

func update_trail(dt: float, on: bool) -> void:
	if on and tip:
		trail.push_front([base.global_position, tip.global_position, 0.0])
	for e in trail:
		e[2] += dt
	while trail.size() > 0 and trail[trail.size() - 1][2] > 0.16:
		trail.pop_back()
	trail_mesh.clear_surfaces()
	if trail.size() < 2:
		return
	trail_mesh.surface_begin(Mesh.PRIMITIVE_TRIANGLE_STRIP)
	for i in trail.size():
		var e = trail[i]
		var a: float = clamp(1.0 - e[2] / 0.16, 0.0, 1.0) * (1.0 - float(i) / trail.size())
		trail_mesh.surface_set_color(Color(0.78, 0.96, 1.0, 0.1 * a))
		trail_mesh.surface_add_vertex(e[0])
		trail_mesh.surface_set_color(Color(0.78, 0.96, 1.0, 0.95 * a))
		trail_mesh.surface_add_vertex(e[1])
	trail_mesh.surface_end()
