shader_type spatial;
render_mode specular_disabled;
// 시험 3: 만화풍 빛(3단) + 테두리 빛 + 붉은 안감·채도 올림
uniform sampler2D albedo_tex : source_color, filter_linear_mipmap;
uniform float sat = 1.2;
uniform vec3 rim_col : source_color = vec3(0.70, 0.93, 1.0);
uniform float rim_pow = 2.6;
uniform float rim_str = 0.45;
void fragment() {
	vec3 c = texture(albedo_tex, UV).rgb;
	float l = dot(c, vec3(0.299, 0.587, 0.114));
	c = mix(vec3(l), c, sat);
	float red = clamp((c.r / (max(c.g, c.b) + 0.03) - 1.9) * 1.5, 0.0, 1.0);
	c = mix(c, c * vec3(1.6, 0.75, 0.75), red * 0.7);
	ALBEDO = clamp(c * 1.25, 0.0, 1.0);
	float rim = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), rim_pow);
	EMISSION = rim_col * rim * rim_str;
}
void light() {
	float nd = dot(NORMAL, LIGHT);
	float b = nd > 0.3 ? 1.0 : (nd > -0.15 ? 0.6 : 0.32);
	DIFFUSE_LIGHT += ALBEDO * LIGHT_COLOR * b * mix(0.55, 1.0, ATTENUATION);
}
