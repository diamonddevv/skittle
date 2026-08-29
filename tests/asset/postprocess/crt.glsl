#version 330

out vec4 fragColor;

uniform sampler2D u_screen_texture;
uniform vec2 u_resolution;
uniform float u_time;

uniform float u_warping;                    // simulate curvature of CRT monitor
uniform float u_scanline_darkness;          // simulate darkness between scanlines
uniform float u_scanline_resolution_height; // scanline resolution

void main()
{
    // squared distance from center
    vec2 uv = gl_FragCoord.xy / u_resolution;
    vec2 dc = abs(0.5 - uv);
    dc *= dc;
    
    // warp the fragment coordinates
    uv.x -= 0.5; 
    uv.x *= 1.0 + (dc.y * (0.3 * u_warping)); 
    uv.x += 0.5;

    uv.y -= 0.5;
    uv.y *= 1.0 + (dc.x * (0.4 * u_warping)); 
    uv.y += 0.5;

    // sample inside boundaries, otherwise set to black
    if (uv.y > 1.0 || uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0)
        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
    else
    {
        // determine if we are drawing in a scanline
        float apply = abs(sin(uv.y * u_scanline_resolution_height) * 0.5 * u_scanline_darkness);
        // sample the texture
        fragColor = vec4(mix(texture(u_screen_texture, uv).rgb, vec3(0.0), apply), 1.0);
    }
}