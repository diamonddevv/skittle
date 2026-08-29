#version 330

out vec4 fragColor;

uniform sampler2D u_screen_texture;
uniform vec2 u_resolution;
uniform float u_time;


void main()
{
    vec2 uv = gl_FragCoord.xy / u_resolution;
    fragColor = texture(u_screen_texture, uv) * vec4(0.65, 1, 0.65, 1.0);
}