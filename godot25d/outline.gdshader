shader_type spatial;
render_mode unshaded, cull_front;
// 굵은 외곽선(뒤집은 껍질, 화면 픽셀 두께)
uniform float width_px = 1.0;
void vertex() {
	vec4 clip = PROJECTION_MATRIX * (MODELVIEW_MATRIX * vec4(VERTEX, 1.0));
	vec3 n = normalize((MODELVIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
	vec2 off = normalize((PROJECTION_MATRIX * vec4(n, 0.0)).xy + vec2(1e-5));
	clip.xy += off * (width_px * 2.0 / VIEWPORT_SIZE) * clip.w;
	POSITION = clip;
}
void fragment() {
	ALBEDO = vec3(0.035, 0.025, 0.045);
}
