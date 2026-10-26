extends Node3D
# 필멸자 2.5D 시험 (Godot 4.3, gl_compatibility): 그록 그림 바닥(2D 그대로) + 3D 인형 주인공.
# 1 단위 = 지도 1칸(16px). 카메라 45도 아래로 → 바닥 세로를 KZ배로 늘려 2D 그림 비율을 그대로 보이게 함.

const PITCH := 45.0
var KZ := 1.0 / sin(deg_to_rad(PITCH))
const HERO_SCREEN_H := 42.0 / 16.0           # 화면 키 42px = 2.625칸
const SECS := 30.0

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

# (이름, 방향, 초, 빠르기 칸/초) — 빠르기 0 = 서기
var plan := [
	["서기", Vector2(0, 1), 1.2, 0.0],
	["걷기 →", Vector2(1, 0), 1.6, 3.2],
	["걷기 ↘", Vector2(1, 1), 1.2, 3.2],
	["걷기 ↓", Vector2(0, 1), 1.2, 3.2],
	["걷기 ←", Vector2(-1, 0), 1.6, 3.2],
	["걷기 ↖", Vector2(-1, -1), 1.2, 3.2],
	["걷기 ↑", Vector2(0, -1), 1.4, 3.2],
	["서기 (멈춤)", Vector2(0, -1), 0.8, 0.0],
	["달리기 →", Vector2(1, 0), 2.0, 7.5],
	["달리기 ↗", Vector2(1, -1), 1.2, 7.5],
	["달리기 ← (180° 꺾기)", Vector2(-1, 0), 2.2, 7.5],
	["달리기 ↙", Vector2(-1, 1), 1.0, 7.5],
	["달리기 ↓", Vector2(0, 1), 1.0, 7.5],
	["멈춤", Vector2(0, 1), 1.0, 0.0],
	["달리기 → (긴 거리)", Vector2(1, 0), 3.0, 7.5],
	["8방향 돌기", Vector2(1, 0), 3.2, -1.0],
	["서기", Vector2(0, 1), 3.0, 0.0],
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
	e.ambient_light_energy = 0.32
	e.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.environment = e
	add_child(env)

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-55, -35, 0)
	sun.light_energy = 0.62
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
	var doc := GLTFDocument.new()
	var st := GLTFState.new()
	doc.append_from_file(ProjectSettings.globalize_path("res://art/Soldier.glb"), st)
	model = doc.generate_scene(st)
	hero.add_child(model)
	var sc := HERO_SCREEN_H / cos(deg_to_rad(PITCH)) / 1.8
	model.scale = Vector3(sc, sc, sc)
	anim = model.find_child("AnimationPlayer", true, false)
	for n in ["Idle", "Walk", "Run"]:
		if anim.has_animation(n):
			anim.get_animation(n).loop_mode = Animation.LOOP_LINEAR
	# 칼 (손에 붙임)
	var skel: Skeleton3D = model.find_child("Skeleton3D", true, false)
	if skel:
		var ba := BoneAttachment3D.new()
		ba.bone_name = "mixamorig:RightHand"
		skel.add_child(ba)
		var blade := MeshInstance3D.new()
		var bm := BoxMesh.new()
		bm.size = Vector3(4, 95, 1.5)
		blade.mesh = bm
		var bmat := StandardMaterial3D.new()
		bmat.albedo_color = Color(0.78, 0.82, 0.86)
		bmat.metallic = 0.8
		bmat.roughness = 0.3
		blade.material_override = bmat
		blade.position = Vector3(0, 55, 4)
		ba.add_child(blade)

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
	cam.size = 17.0
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
	label.add_theme_constant_override("outline_size", 8)
	label.position = Vector2(24, 18)
	ui.add_child(label)
	var sub := Label.new()
	sub.text = "고도 2.5D 시험 · 배경 = 그록 그림 그대로 · 주인공 = 3D 인형(무료 공개 모델, 시험용)"
	sub.add_theme_font_override("font", f)
	sub.add_theme_font_size_override("font_size", 18)
	sub.add_theme_color_override("font_outline_color", Color.BLACK)
	sub.add_theme_constant_override("outline_size", 6)
	sub.position = Vector2(24, 680)
	ui.add_child(sub)

func play(n: String, spd: float) -> void:
	if cur_anim != n:
		anim.play(n, 0.18)
		cur_anim = n
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
	if spd > 5.0:
		play("Run", spd / 6.2)
		target_lean = 0.0
	elif spd > 0.0:
		play("Walk", spd / 2.4)
	else:
		play("Idle", 1.0)
	lean = lerp(lean, target_lean, clamp(dt * 8.0, 0.0, 1.0))
	dust.emitting = spd > 5.0
	dust.position = Vector3(0, 0.1, 0)
	cam.position = pos + Vector3(0, sin(deg_to_rad(PITCH)), cos(deg_to_rad(PITCH))) * 60.0
