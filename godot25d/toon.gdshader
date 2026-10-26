shader_type spatial;
render_mode specular_disabled, ambient_light_disabled;
// 회의 결론 4·5: 2칸 빛 + 색 있는 그림자, 얼굴(COLOR.r = Head 뼈 무게×앞쪽)은 평평하게·테두리 빛 없음
uniform sampler2D albedo_tex : source_color, filter_linear_mipmap;
// 설정화 앞모습(COLOR.g = 머리 앞쪽, UV2 = 그림 자리)을 그대로 입힘
uniform sampler2D art_tex : source_color, filter_linear, repeat_disable;
uniform vec3 shade_tint : source_color = vec3(0.84, 0.8, 0.9);  // 설정화로 칠한 색에 이미 그림자가 있어 얕게
uniform vec3 face_tint : source_color = vec3(0.97, 0.93, 0.92);
uniform vec3 rim_col : source_color = vec3(0.75, 0.9, 1.0);
uniform float rim_pow = 3.0;
uniform float rim_str = 0.25;
varying float face;
varying float proj;
// 머리·머리카락은 머리 가운데에서 바깥으로 둥근 법선 (AI 인형의 울퉁불퉁 그림자 없앰)
uniform vec3 head_c = vec3(0.0, 1.6, 0.0);
uniform float head_round = 0.85;
void vertex() {
	proj = COLOR.g;
	vec3 sph = normalize((VERTEX - head_c) * vec3(1.0, 0.85, 1.0));
	NORMAL = normalize(mix(NORMAL, sph, COLOR.b * head_round));
	face = max(COLOR.r, proj);
}
void fragment() {
	vec3 c = texture(albedo_tex, UV).rgb;
	vec4 art = texture(art_tex, UV2);
	c = mix(c, art.rgb, proj * smoothstep(0.3, 0.9, art.a));
	ALBEDO = min(c, vec3(0.95));
	float rim = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), rim_pow);
	EMISSION = rim_col * rim * rim_str * (1.0 - face) * ALBEDO;
}
void light() {
	float nl = dot(NORMAL, LIGHT);
	float lit = smoothstep(0.0, 0.06, nl) * mix(0.35, 1.0, step(0.5, ATTENUATION));
	vec3 ramp = mix(shade_tint, vec3(1.0), lit);
	ramp = mix(ramp, face_tint, face);
	DIFFUSE_LIGHT += ramp * min(LIGHT_COLOR / PI, vec3(1.0));
}
