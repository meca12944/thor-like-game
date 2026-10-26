shader_type spatial;
render_mode unshaded, cull_front;
// 외곽선: 화면 픽셀 굵기 일정, 얼굴 안쪽(COLOR.r)은 0.2배
uniform float width_px = 1.8;
void vertex() {
	vec4 clip = PROJECTION_MATRIX * (MODELVIEW_MATRIX * vec4(VERTEX, 1.0));
	vec3 n = normalize((MODELVIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
	vec2 off = normalize((PROJECTION_MATRIX * vec4(n, 0.0)).xy + vec2(1e-5));
	clip.xy += off * (width_px * (1.0 - 0.8 * COLOR.r) * 2.0 / VIEWPORT_SIZE) * clip.w;
	POSITION = clip;
}
void fragment() {
	ALBEDO = vec3(0.06, 0.045, 0.08);
}
