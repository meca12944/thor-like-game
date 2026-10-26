extends Node3D
# 필멸자 2.5D 시험 (Godot 4.3, gl_compatibility): 그록 그림 바닥(2D 그대로) + 3D 인형 주인공.
# 1 단위 = 지도 1칸(16px). 카메라 45도 아래로 → 바닥 세로를 KZ배로 늘려 2D 그림 비율을 그대로 보이게 함.

const PITCH := 30.0
var KZ := 1.0 / sin(deg_to_rad(PITCH))
const HERO_SCREEN_H := 42.0 / 16.0           # 화면 키 42px = 2.625칸
var SECS := 33.0

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
const ART_W := 815.0
const ART_H := 918.0
const ART_CX := 406.5
var HEAD_UP := OS.get_environment("HEADUP").to_float() if OS.get_environment("HEADUP") != "" else -15.0  # 위에서 내려다보는 카메라라 고개를 살짝 듦
const STEP := 0.0   # 2D 느낌: 그림을 1초에 12장만 바꿈

# (이름, 방향, 초, 빠르기 칸/초) — 빠르기 0 = 서기
var plan := [
	["서기 (숨쉬기)", Vector2(0, 1), 1.6, 0.0, ""],
	["걷기 →", Vector2(1, 0), 1.4, 3.2, ""],
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

# 새 동작 맛보기 (PLAN=new): Meshy 창고 동작 7개 (사장님 10-26)
var IDLE_ANIM := "Idle"
var RUN_ANIM := "Run"
var plan_new := [
	["A1 서기 = 전투 자세 (칼 든 채)", Vector2(1, 0), 2.2, 0.0, ""],
	["B1 달리기 = 앞으로 숙여 질주 →", Vector2(1, 0), 1.8, 7.5, ""],
	["B1 달리기 ↓", Vector2(0, 1), 1.2, 7.5, ""],
	["B1 달리기 ← (꺾기)", Vector2(-1, 0), 1.4, 7.5, ""],
	["C6 회피대시: 웅크려 뒤로 스텝 + 코드로 휙 (적 보며 뒤로)", Vector2(1, 0), 1.6, 0.0, "Crouch_and_Step_Back", {"slide": Vector2(-1, 0), "v": 15.0, "dur": 0.22}],
	["C2 회피대시: 선 채 피하기 1 + 코드로 휙 (적 보며 옆으로)", Vector2(1, 0), 1.3, 0.0, "Stand_Dodge_1", {"slide": Vector2(0, 1), "v": 15.0, "dur": 0.22}],
	["D1 3타 = 3연속 베기 (1·2·3타로 나눠 씀)", Vector2(1, 0), 4.4, 0.0, "Triple_Combo_Attack"],
	["점프: 달리다 점프 (새)", Vector2(1, 0), 2.3, 0.0, "Run_and_Jump", {"slide": Vector2(1, 0), "v": 4.0, "dur": 1.6}],
	["점프: 달리다 멀리 뛰기 (새)", Vector2(-1, 0), 2.6, 0.0, "Run_and_Leap", {"slide": Vector2(-1, 0), "v": 4.0, "dur": 1.8}],
	["점프: 제자리 점프 (지금 것)", Vector2(0, 1), 1.4, 0.0, "Regular_Jump"],
	["A1 서기", Vector2(0, 1), 1.0, 0.0, ""],
]

# 사장님 10-26 확정: 서기 A1 전투 자세 · 달리기 B2 빠른 달리기 · 1·2·3타 = D5 무기 연속 2 나눠 씀 · 모아베기(꾹) = 도끼 회전
# 3타 나눈 자리: 칼끝 빠르기 재서 정함 (휘두름 꼭대기 1.17초·2.03초·2.97초, 사이 느린 곳에서 자름)
const COMBO := "Weapon_Combo_2"
const HIT_CUTS := [[0.35, 1.6], [1.6, 2.42], [2.42, 3.9]]
var plan_new2 := [
	["서기 = A1 전투 자세", Vector2(1, 0), 1.6, 0.0, ""],
	["빠른 달리기 → (출발: 앞으로 크게 숙임)", Vector2(1, 0), 1.5, 7.5, ""],
	["달리다 ← 반대로 꺾기 (미끄러지며 브레이크)", Vector2(-1, 0), 1.5, 7.5, ""],
	["달리기 ↓ (꺾을 때 안쪽으로 기울기)", Vector2(0, 1), 1.0, 7.5, ""],
	["1타", Vector2(-1, 0), 1.0, 0.0, COMBO, {"from": 0.55, "to": 1.6, "hit": 1.17, "stop": 0.05}],
	["2타", Vector2(-1, 0), 0.8, 0.0, COMBO, {"from": 1.6, "to": 2.42, "hit": 2.03, "stop": 0.066}],
	["3타", Vector2(-1, 0), 1.5, 0.0, COMBO, {"from": 2.42, "to": 3.9, "hit": 2.97, "stop": 0.11}],
	["회피대시 (뒤로 휙 + 잔상)", Vector2(-1, 0), 0.9, 0.0, "Crouch_and_Step_Back", {"slide": Vector2(1, 0), "v": 15.0, "dur": 0.22, "ghost": true}],
	["모아베기: 꾹 (모으는 중)", Vector2(-1, 0), 1.2, 0.0, "Axe_Spin_Attack", {"from": 0.0, "to": 0.5, "speed": 0.45, "charge": true}],
	["모아베기: 뗌 → 도끼 회전", Vector2(-1, 0), 1.6, 0.0, "Axe_Spin_Attack", {"from": 0.5, "to": 2.1, "hit": 1.0, "stop": 0.15}],
	["서기", Vector2(0, 1), 1.0, 0.0, ""],
]
var cur_seg := -1

func _ready() -> void:
	if OS.get_environment("PLAN") == "new2":
		plan = plan_new2
		IDLE_ANIM = "Combat_Stance"
		RUN_ANIM = "RunFast"
	if OS.get_environment("PLAN") == "new":
		plan = plan_new
		IDLE_ANIM = "Combat_Stance"
		RUN_ANIM = "Lean_Forward_Sprint"
	SECS = 0.0
	for sg in plan:
		SECS += sg[2]
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
		if not FileAccess.file_exists("res://art/" + extra[0]):
			continue
		var m2 := load_glb(extra[0])
		var p2: AnimationPlayer = m2.find_child("AnimationPlayer", true, false)
		var nm: String = p2.get_animation_list()[0]
		lib.add_animation(extra[1], p2.get_animation(nm).duplicate())
	for n in ["Idle", "Walk", "Run"]:
		if anim.has_animation(n):
			anim.get_animation(n).loop_mode = Animation.LOOP_LINEAR
	for gf in ["actions2.glb", "actions3.glb", "actions4.glb"]:
		if not FileAccess.file_exists("res://art/" + gf):
			continue
		var m3 := load_glb(gf)
		var p3: AnimationPlayer = m3.find_child("AnimationPlayer", true, false)
		for nm3 in p3.get_animation_list():
			lib.add_animation(nm3, p3.get_animation(nm3).duplicate())
	for n in anim.get_animation_list():
		if n in ["Idle", "Walk", "Run", "Combat_Stance", "Lean_Forward_Sprint", "RunFast"]:
			anim.get_animation(n).loop_mode = Animation.LOOP_LINEAR
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
			if FileAccess.file_exists("res://art/art_bake.png") and OS.get_environment("NOBAKE") == "":
				sm.set_shader_parameter("albedo_tex", tex("art_bake"))   # 설정화로 다시 칠한 색 그림 (art_bake.py)
			elif FileAccess.file_exists("res://art/base4k.png"):
				sm.set_shader_parameter("albedo_tex", tex("base4k"))
			elif om is BaseMaterial3D and om.albedo_texture:
				sm.set_shader_parameter("albedo_tex", om.albedo_texture)
			sm.set_shader_parameter("art_tex", tex("art_front"))
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
		bmat.albedo_color = Color(0.72, 0.76, 0.82)   # 칼날: 차가운 쇠색 (설정화 남색·구리색과 어울림)
		bmat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		var gmat := StandardMaterial3D.new()
		gmat.albedo_color = Color(0.62, 0.45, 0.2)    # 코등이: 어깨 갑옷과 같은 구리색
		gmat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		var hmat := StandardMaterial3D.new()
		hmat.albedo_color = Color(0.2, 0.13, 0.09)    # 손잡이: 짙은 가죽
		hmat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		for part in [[Vector3(2.6, 0.8, 100.0), Vector3(0, 0, 58.0), bmat], [Vector3(14.0, 2.4, 2.4), Vector3(0, 0, 7.0), gmat], [Vector3(2.4, 2.4, 14.0), Vector3(0, 0, -1.0), hmat]]:
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
	if OS.get_environment("CAMSZ") != "":
		cam.size = OS.get_environment("CAMSZ").to_float()
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
	sub.text = "시험 9 · 설정화(7~8등신) 그대로 새 인형: 그림 모습 지키기 켬 + 앞·옆·뒤 그림으로 색칠"
	sub.add_theme_font_override("font", f)
	sub.add_theme_font_size_override("font_size", 18)
	sub.add_theme_color_override("font_outline_color", Color.BLACK)
	sub.add_theme_constant_override("outline_size", 3)
	sub.position = Vector2(24, 680)
	ui.add_child(sub)
	if OS.get_environment("PLAN") == "new2":
		sub.text = "2시간 회의 결론 · 새 인형(설정화 망토·머리) · 설정화로 다시 칠함 · 아틀라스 그림 · 공격 1초 15장+과장+타마다 멈칫 · 꺾기 브레이크 · 잔상"
	if OS.get_environment("PLAN") == "new":
		sub.text = "새 동작 맛보기 · Meshy 창고 7개 (21크레딧): 전투 자세 · 숙여 질주 · 회피대시 2종 · 3연속 베기 · 점프 2종"
	if OS.get_environment("ANALYZE") != "":
		analyze(OS.get_environment("ANALYZE"))
		return
	if OS.get_environment("BAKE") != "":
		bake()
	elif OS.get_environment("ATLAS") != "":
		setup_sprite()
		if OS.get_environment("PLAN") != "new2":
			sub.text = "시험 10 · 아틀라스: 3D 인형 동작을 4방향 그림으로 미리 찍어 그림으로 움직임 (1초 20장, 방향 4개)"

# ── 아틀라스 보여 주기: 숨긴 3D 인형과 같은 시간·방향의 그림 칸을 Sprite3D로 ──
var spr: Sprite3D
var atlas := {}
var atlas_tex := {}
var sprite_mode := false
const DIR_ORDER := ["down", "right", "up", "left"]

func setup_sprite() -> void:
	var fj := FileAccess.open("res://atlas/atlas.json", FileAccess.READ)
	atlas = JSON.parse_string(fj.get_as_text())
	for n in atlas["anims"]:
		var img := Image.load_from_file("res://atlas/" + n + ".png")
		img.generate_mipmaps()
		atlas_tex[n] = ImageTexture.create_from_image(img)
	for mi in model.find_children("*", "MeshInstance3D", true, false):
		mi.visible = false
	spr = Sprite3D.new()
	spr.pixel_size = atlas["cam_size"] / atlas["px"]
	spr.region_enabled = true
	spr.shaded = false
	spr.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	spr.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	spr.rotation_degrees = Vector3(-PITCH, 0, 0)
	spr.no_depth_test = true   # 그림판이 비스듬해 발끝이 땅 밑으로 들어가 잘리던 것 막음
	spr.render_priority = 2
	hero.add_child(spr)
	sprite_mode = true

func snap4(a: float) -> float:
	return round(a / (PI / 2.0)) * (PI / 2.0)

func update_sprite() -> void:
	if not atlas["anims"].has(cur_anim):
		return
	var a: Dictionary = atlas["anims"][cur_anim]
	var nf: int = a["frames"]
	var f := int(anim.current_animation_position * float(atlas["fps"]) + 0.001)
	if cur_anim in ["Idle", "Walk", "Run"]:
		f = posmod(f, nf)
	else:
		f = clamp(f, 0, nf - 1)
	var k := int(round(wrapf(model.rotation.y, -PI, PI) / (PI / 2.0)))
	var dn: String = {0: "down", 1: "right", 2: "up", -2: "up", -1: "left"}[k]
	var cols: int = a["cols"]
	var rpd: int = a["rows_per_dir"]
	var w: float = a["w"]
	var h: float = a["h"]
	var row: int = DIR_ORDER.find(dn) * rpd + f / cols
	spr.texture = atlas_tex[cur_anim]
	spr.region_rect = Rect2((f % cols) * w, row * h, w, h)
	spr.offset = Vector2(w / 2.0 - float(a["ox"]), float(a["oy"]) - h / 2.0)
	var rs := root_shift(false)
	spr.position = Vector3(rs.x, 0, rs.z)
	for c in hero.get_children():
		if c is MeshInstance3D:
			c.position = Vector3(rs.x, 0.06, rs.z)   # 발밑 그림자도 같이
	var sq: Vector3 = model.scale / base_sc()
	spr.scale = Vector3(sq.x, sq.y, 1.0)

# ── 아틀라스: 3D 인형 동작을 4방향 그림으로 미리 찍기 (하데스식) ──
var BAKE_PX := 800 * (2 if OS.get_environment("BAKE2X") != "" else 1)   # 2배로 그리고 묶을 때 줄임 → 부드러운 테두리
const BAKE_FPS := 20.0
const BAKE_SIZE := 8.125    # 1080p 게임 화면과 같은 1칸 = 98px
const DIRS := {"down": 0.0, "right": PI / 2.0, "up": PI, "left": -PI / 2.0}

# 칼끝 빠르기 재기 (3타 나눌 자리 찾기)
func analyze(n: String) -> void:
	set_process(false)
	anim.play(n, 0.0)
	var ln: float = anim.get_animation(n).length
	var last := Vector3.ZERO
	var tt := 0.0
	while tt <= ln:
		anim.seek(tt, true)
		await get_tree().process_frame
		var tp := tip.global_position
		if tt > 0.0:
			print("SPD %.3f %.2f" % [tt, (tp - last).length() * 30.0])
		last = tp
		tt += 1.0 / 30.0
	get_tree().quit()

func head_fix() -> void:
	var hb := skel.find_bone("Head")
	if hb >= 0:
		skel.set_bone_pose_rotation(hb, skel.get_bone_pose_rotation(hb).slerp(skel.get_bone_rest(hb).basis.get_rotation_quaternion() * Quaternion(Vector3.RIGHT, deg_to_rad(HEAD_UP)), 0.85))

# 엉덩이(뿌리 뼈)의 바닥 방향 이동: 그림은 제자리로 찍고, 게임에서 그림을 그만큼 옮김
func root_shift(lock: bool) -> Vector3:
	var hb := skel.find_bone("Hips")
	if hb < 0:
		return Vector3.ZERO
	var p := skel.get_bone_pose_position(hb)
	var r := skel.get_bone_rest(hb).origin
	var q := Vector3(r.x, p.y, r.z)
	var d := skel.to_global(p) - skel.to_global(q)
	if lock:
		skel.set_bone_pose_position(hb, q)
	return d

func bake() -> void:
	set_process(false)
	for c in get_children():
		if c is MeshInstance3D:
			c.visible = false
	for c in hero.get_children():
		if c != model:
			c.visible = false
	var sv := SubViewport.new()
	sv.size = Vector2i(BAKE_PX, BAKE_PX)
	sv.transparent_bg = true
	sv.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(sv)
	var bc := Camera3D.new()
	bc.projection = Camera3D.PROJECTION_ORTHOGONAL
	bc.size = BAKE_SIZE
	sv.add_child(bc)
	bc.rotation_degrees = Vector3(-PITCH, 0, 0)
	bc.global_position = hero.global_position + bc.global_transform.basis.z * 60.0 + bc.global_transform.basis.y * 0.9
	bc.current = true
	var out := ProjectSettings.globalize_path("res://bake")
	DirAccess.make_dir_recursive_absolute(out)
	var names := [IDLE_ANIM, "Walk", RUN_ANIM]
	for sg in plan:
		if sg[4] != "" and not names.has(sg[4]):
			names.append(sg[4])
	names = names.filter(func(x): return anim.has_animation(x))
	await RenderingServer.frame_post_draw
	var o := bc.unproject_position(hero.global_position)
	var meta := {"fps": BAKE_FPS, "px": BAKE_PX, "cam_size": BAKE_SIZE, "origin": [o.x, o.y], "anims": {}}
	for n in names:
		var ln: float = anim.get_animation(n).length
		var nf: int = max(1, int(floor(ln * BAKE_FPS + 0.5)))
		anim.play(n, 0.0)
		anim.speed_scale = 1.0
		var am := {"frames": nf, "len": ln, "tips": {}}
		for dn in DIRS:
			if OS.get_environment("BAKEDIRS") != "" and not (dn in OS.get_environment("BAKEDIRS").split(",")):
				continue
			model.rotation.y = DIRS[dn]
			var tips := []
			for f in nf:
				anim.seek(min(f / BAKE_FPS, ln), true)
				head_fix()
				if n.find("Combo") >= 0 or n.find("Axe") >= 0:
					exaggerate(0.8)
				root_shift(true)
				await RenderingServer.frame_post_draw
				await RenderingServer.frame_post_draw
				sv.get_texture().get_image().save_png("%s/%s_%s_%03d.png" % [out, n, dn, f])
				var pb := bc.unproject_position(base.global_position)
				var pt := bc.unproject_position(tip.global_position)
				tips.append([pb.x, pb.y, pt.x, pt.y])
			am["tips"][dn] = tips
		meta["anims"][n] = am
		print("BAKED ", n, " ", nf)
	var fj := FileAccess.open(out + "/bake_%s.json" % OS.get_environment("BAKEDIRS").replace(",", "_"), FileAccess.WRITE)
	fj.store_string(JSON.stringify(meta))
	fj.close()
	get_tree().quit()

# 얼굴 표시: Head 뼈 무게 × 앞쪽(+Z) 법선 → 정점 색 R (회의 결론 3)
func add_face_mask(mi: MeshInstance3D) -> void:
	var sk: Skin = mi.skin
	if sk == null:
		return
	var sk_node := mi.get_node_or_null(mi.skeleton) as Skeleton3D
	var head := -1
	for i in sk.get_bind_count():
		var bn: String = sk.get_bind_name(i)
		if bn == "" and sk_node:
			bn = sk_node.get_bone_name(sk.get_bind_bone(i))
		if bn == "Head":
			head = i
	if head < 0:
		return
	var old: ArrayMesh = mi.mesh
	# 설정화 앞모습을 앞에서 비춰 입히기: 인형 키 = 그림 키(918px), 머리 가운데 = 그림 머리 가운데
	var y0 := 1e9
	var y1 := -1e9
	var hx := 0.0
	var hn := 0.0
	for si in old.get_surface_count():
		var a0 := old.surface_get_arrays(si)
		var vs: PackedVector3Array = a0[Mesh.ARRAY_VERTEX]
		var bs: PackedInt32Array = a0[Mesh.ARRAY_BONES]
		var ws: PackedFloat32Array = a0[Mesh.ARRAY_WEIGHTS]
		var pr: int = bs.size() / max(vs.size(), 1)
		for v in vs.size():
			y0 = min(y0, vs[v].y)
			y1 = max(y1, vs[v].y)
			for k in pr:
				if bs[v * pr + k] == head and ws[v * pr + k] > 0.5:
					hx += vs[v].x
					hn += 1.0
	hx /= max(hn, 1.0)
	var s_px: float = ART_H / max(y1 - y0, 1e-4)
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
		var uv2 := PackedVector2Array()
		uv2.resize(vc)
		for v in vc:
			var w := 0.0
			for k in per:
				if bones[v * per + k] == head:
					w += wts[v * per + k]
			var fr: float = clamp((nrm[v].z - 0.15) * 2.5, 0.0, 1.0)
			var pj: float = clamp(w * 1.6 - 0.2, 0.0, 1.0) * clamp(nrm[v].z * 2.5, 0.0, 1.0)
			cols[v] = Color(clamp(w * 1.4, 0.0, 1.0) * fr, pj, clamp(w * 1.3 - 0.1, 0.0, 1.0), 1)   # b = 머리 전체(머리카락 포함) → 둥근 빛
			uv2[v] = Vector2((ART_CX + (verts[v].x - hx) * s_px) / ART_W, (ART_H - (verts[v].y - y0) * s_px) / (ART_H + 1.0))
		arr[Mesh.ARRAY_COLOR] = cols
		arr[Mesh.ARRAY_TEX_UV2] = uv2
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

# ── 움직임 회의 결론 (10-26): 공격은 1초 15장 끊기 + 자세 과장 + 타마다 멈칫, 달리기 숙임·꺾기 브레이크·기울기, 회피대시 잔상 ──
const EXAG := {"Spine": 1.3, "Spine01": 1.3, "Spine02": 1.3, "LeftArm": 1.25, "RightArm": 1.25, "RightForeArm": 1.2, "RightHand": 1.25, "Hips": 1.15, "Head": 0.8}
const ATK_FPS := 15.0
var hs_t := 0.0          # 멈칫(히트스톱) 남은 시간
var hit_done := false
var exag_k := 0.0
var run_t := 0.0         # 달리기 시작 뒤 시간 (출발 숙임)
var skid_t := 0.0        # 꺾기 브레이크
var last_d := Vector2.ZERO
var ghost_acc := 0.0
var ghosts := []
var ghost_q := []

func exaggerate(k: float) -> void:
	if k <= 0.001:
		return
	for b in EXAG:
		var i := skel.find_bone(b)
		if i < 0:
			continue
		var rest := skel.get_bone_rest(i).basis.get_rotation_quaternion()
		var dq := rest.inverse() * skel.get_bone_pose_rotation(i)
		var ang := dq.get_angle()
		if ang < 0.001:
			continue
		var na: float = min(ang * lerp(1.0, float(EXAG[b]), k), deg_to_rad(110.0))
		skel.set_bone_pose_rotation(i, rest * Quaternion(dq.get_axis().normalized(), na))

func spawn_ghost() -> void:
	if sprite_mode:
		var gs: Sprite3D = spr.duplicate(0)
		var gsm := ShaderMaterial.new()
		gsm.shader = load("res://ghost.gdshader")
		gsm.set_shader_parameter("tex", spr.texture)
		gs.material_override = gsm
		add_child(gs)
		gs.global_transform = spr.global_transform
		ghosts.append([gs, gsm, 0.0])
		return
	# 지금 자세 그대로 인형을 하나 복사해 멈춰 둠 (푸른 반투명, 0.18초에 사라짐)
	var g: Node3D = model.duplicate(0)
	for ap in g.find_children("*", "AnimationPlayer", true, false):
		ap.queue_free()
	var gsk: Skeleton3D = g.find_child("Skeleton3D", true, false)
	for i in skel.get_bone_count():
		gsk.set_bone_pose_position(i, skel.get_bone_pose_position(i))
		gsk.set_bone_pose_rotation(i, skel.get_bone_pose_rotation(i))
	var gm := StandardMaterial3D.new()
	gm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	gm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	gm.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	gm.albedo_color = Color(0.55, 0.85, 1.0, 0.4)
	for mi in g.find_children("*", "MeshInstance3D", true, false):
		if mi.skin == null:
			mi.visible = false
			continue
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		for si in mi.mesh.get_surface_count():
			mi.set_surface_override_material(si, gm)
	add_child(g)
	g.global_transform = model.global_transform
	ghosts.append([g, gm, 0.0])

func update_ghosts(dt: float) -> void:
	for e in ghosts:
		e[2] += dt
		e[0].visible = e[0].global_position.distance_to(model.global_position) > 0.45
		if e[1] is ShaderMaterial:
			e[1].set_shader_parameter("fade", max(0.0, 1.0 - e[2] / 0.25))
		elif e[1]:
			e[1].albedo_color.a = 0.4 * max(0.0, 1.0 - e[2] / 0.25)
		else:
			e[0].modulate.a = 0.45 * max(0.0, 1.0 - e[2] / 0.25)
	while ghosts.size() > 0 and ghosts[0][2] > 0.25:
		ghosts[0][0].queue_free()
		ghosts.pop_front()

func _process(dt: float) -> void:
	t += dt
	if t > SECS:
		get_tree().quit()
		return
	var acc := 0.0
	var seg = plan[plan.size() - 1]
	var lt := 0.0
	var si := plan.size() - 1
	for j in plan.size():
		var s = plan[j]
		if t < acc + s[2]:
			seg = s
			si = j
			lt = t - acc
			break
		acc += s[2]
	var ex: Dictionary = seg[5] if seg.size() > 5 else {}
	var new_seg := si != cur_seg
	cur_seg = si
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
	# 꺾기: 달리다 120도 넘게 돌면 0.14초 브레이크(뒤로 젖힘·속도 40%·먼지)
	if spd > 5.0 and last_d != Vector2.ZERO and last_d.dot(d) < -0.5:
		skid_t = 0.14
		run_t = 0.0
	if spd > 5.0:
		last_d = d
	elif act != "":
		last_d = Vector2.ZERO
	var want := atan2(d.x, d.y)
	var mv := d
	if skid_t > 0.0:
		skid_t -= dt
		want = face   # 브레이크 동안엔 아직 안 돎, 끝에 휙
		spd *= 0.4
		dust.emitting = true
	var prev_face := face
	if skid_t <= 0.0:
		face = lerp_angle(face, want, clamp(dt * 14.0, 0.0, 1.0))
	var ang_v: float = wrapf(face - prev_face, -PI, PI) / max(dt, 1e-4)
	pos += Vector3(mv.x, 0, mv.y * KZ) * spd * dt
	# 회피대시·점프: 몸은 d 방향을 본 채 slide 방향으로 코드가 옮김 (블러드본 스텝처럼 짧고 빠르게)
	if seg.size() > 5 and seg[5].has("slide") and lt < seg[5]["dur"]:
		var sl: Vector2 = seg[5]["slide"]
		var k2: float = 1.0 - lt / seg[5]["dur"]
		pos += Vector3(sl.x, 0, sl.y * KZ) * float(seg[5]["v"]) * (0.4 + 1.2 * k2) * dt
	hero.position = pos
	model.rotation.y = snap4(face) if sprite_mode else face
	var target_lean := 0.0
	var is_slash := act.find("Slash") >= 0 or act.find("Combo") >= 0 or act.find("Axe") >= 0
	if act != "":
		if cur_anim != act:
			phase = 0
		play(act, 1.0)
		if new_seg and ex.has("from"):
			anim.play(act, 0.06)
			anim.seek(ex["from"], true)
			phase = 0
		if new_seg:
			hit_done = false
			hs_t = 0.0
		if ex.has("hit"):
			# 시간 다시 맞추기: 준비 0.85배 → 휘두름 2배 → 맞는 순간 멈칫 → 회복 1.15배
			var cp: float = anim.current_animation_position
			var hp: float = ex["hit"]
			if not hit_done and cp >= hp + 0.07:
				hit_done = true
				hs_t = ex["stop"]
				shake = max(shake, 0.06 + float(ex["stop"]) * 1.2)
			if hs_t > 0.0:
				hs_t -= dt
				anim.speed_scale = 0.0
			elif cp < hp - 0.2:
				anim.speed_scale = 0.85
			elif cp < hp + 0.07:
				anim.speed_scale = 2.0
			else:
				anim.speed_scale = 1.15
			exag_k = move_toward(exag_k, 1.0 if (cp > hp - 0.25 and cp < hp + 0.3) else 0.5, dt * 6.0)
		elif ex.has("speed"):
			anim.speed_scale = ex["speed"]
			exag_k = move_toward(exag_k, 0.6, dt * 6.0)
		elif is_slash:
			punch(dt)
		if ex.has("to") and anim.current_animation_position >= float(ex["to"]):
			anim.speed_scale = 0.0   # 이 타 끝: 다음 버튼까지 멈춤 자세
		if ex.has("charge"):
			shake = max(shake, 0.04)   # 모으는 중 떨림
		if ex.has("ghost") and lt < float(ex.get("dur", 0.22)):
			ghost_acc += dt
			if ghost_acc >= 0.045:
				ghost_acc = 0.0
				ghost_q.append(model.global_transform)   # 자세를 남길 자리 (몸이 떠난 뒤 그림)
				spawn_ghost()
	elif spd > 5.0:
		play(RUN_ANIM, spd / 6.0 if RUN_ANIM == "Run" else spd / 7.5)
		target_lean = 0.0
	elif spd > 0.0:
		play("Walk", spd / 2.6)
	else:
		play(IDLE_ANIM, 1.0)
	if act == "" or not is_slash:
		exag_k = move_toward(exag_k, 0.0, dt * 6.0)
	if spd > 5.0 and act == "":
		run_t += dt
		target_lean = deg_to_rad(0.0 + (8.0 if run_t < 0.18 else 0.0))   # 빠른 달리기 동작에 숙임이 이미 있어 조금만 더함
	else:
		run_t = 0.0
	if skid_t > 0.0:
		target_lean = deg_to_rad(-12.0)
	lean = lerp(lean, target_lean, clamp(dt * 12.0, 0.0, 1.0))
	model.rotation.x = lean
	model.rotation.z = lerp(model.rotation.z, clamp(-ang_v * 0.035, -0.24, 0.24) if spd > 5.0 else 0.0, clamp(dt * 10.0, 0.0, 1.0))
	dust.emitting = spd > 5.0
	dust.position = Vector3(0, 0.1, 0)
	step_acc += dt
	var step_now: float = 1.0 / ATK_FPS if (is_slash and OS.get_environment("SMOOTHATK") == "") else STEP
	if step_acc >= step_now:
		anim.advance(step_acc)
		step_acc = 0.0
		exaggerate(exag_k)
		for bn in CHIBI:
			var bi := skel.find_bone(bn)
			if bi >= 0:
				skel.set_bone_pose_scale(bi, Vector3.ONE * CHIBI[bn])
		var hb := skel.find_bone("Head")
		if hb >= 0:
			skel.set_bone_pose_rotation(hb, skel.get_bone_pose_rotation(hb).slerp(skel.get_bone_rest(hb).basis.get_rotation_quaternion() * Quaternion(Vector3.RIGHT, deg_to_rad(HEAD_UP)), 0.85))
	var trail_on := is_slash and ((phase == 1 or phase == 2) if not ex.has("hit") else (anim.current_animation_position > float(ex["hit"]) - 0.22 and anim.current_animation_position < float(ex["hit"]) + 0.12))
	update_trail(dt if hs_t <= 0.0 else 0.0, trail_on)
	update_ghosts(dt)
	var hbi := skel.find_bone("Head")
	if hbi >= 0:
		var hc_w: Vector3 = skel.global_transform * (skel.get_bone_global_pose(hbi).origin + skel.get_bone_global_pose(hbi).basis.y * 9.0)
		for mi in model.find_children("*", "MeshInstance3D", true, false):
			if mi.skin == null:
				continue
			var hc_l: Vector3 = mi.global_transform.affine_inverse() * hc_w
			for sj in mi.mesh.get_surface_count():
				var m = mi.get_surface_override_material(sj)
				if m is ShaderMaterial:
					m.set_shader_parameter("head_c", hc_l)
	if sprite_mode:
		update_sprite()
	else:
		var rs3 := root_shift(false)
		for c in hero.get_children():
			if c is MeshInstance3D:
				c.position = Vector3(rs3.x, 0.06, rs3.z)   # 발밑 그림자가 몸을 따라감
	shake = max(0.0, shake - dt)
	var sk := Vector3(randf_range(-1, 1), 0, randf_range(-1, 1)) * shake * 0.6
	cam.position = pos + sk + Vector3(0, sin(deg_to_rad(PITCH)), cos(deg_to_rad(PITCH))) * 60.0 + Vector3(0, OS.get_environment("CAMY").to_float(), 0)

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
			if v > 9.0:
				phase = 1   # 연속 베기: 다음 타
			model.scale = model.scale.lerp(Vector3.ONE * base_sc(), 0.2)

func base_sc() -> float:
	return HERO_SCREEN_H / cos(deg_to_rad(PITCH)) / 1.8 * 1.05

func update_trail(dt: float, on: bool) -> void:
	if on and tip:
		trail.push_front([base.global_position, tip.global_position, 0.0])
	for e in trail:
		e[2] += dt
	while trail.size() > 0 and trail[trail.size() - 1][2] > 0.1:
		trail.pop_back()
	trail_mesh.clear_surfaces()
	if trail.size() < 2:
		return
	trail_mesh.surface_begin(Mesh.PRIMITIVE_TRIANGLE_STRIP)
	for i in trail.size():
		var e = trail[i]
		var a: float = clamp(1.0 - e[2] / 0.1, 0.0, 1.0) * (1.0 - float(i) / trail.size())
		trail_mesh.surface_set_color(Color(0.78, 0.96, 1.0, 0.1 * a))
		trail_mesh.surface_add_vertex(e[0])
		trail_mesh.surface_set_color(Color(0.78, 0.96, 1.0, 0.55 * a))
		trail_mesh.surface_add_vertex(e[1])
	trail_mesh.surface_end()
