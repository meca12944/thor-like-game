shader_type spatial;
// 회피대시 잔상: 그림 모양만 밝은 푸른빛으로 더함 (효과는 코드로)
render_mode unshaded, blend_add, cull_disabled, depth_test_disabled;
uniform sampler2D tex : source_color, filter_linear_mipmap;
uniform float fade = 1.0;
void fragment() {
	float a = texture(tex, UV).a;
	ALBEDO = vec3(0.45, 0.8, 1.0) * a * fade * 0.55;
}
