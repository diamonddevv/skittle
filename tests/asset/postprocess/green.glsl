#version 330

in vec2 v_uv;

out vec4 fragColor;

uniform sampler2D u_screen_texture;
uniform vec2 u_resolution;
uniform float u_time;


void main()
{
    fragColor = texture(u_screen_texture, v_uv) * vec4(0.65, 1, 0.65, 1.0);
}