import _ctx

import moderngl
import numpy
import skittle

vrtx = """
#version 330 core

in vec2 in_position;
in vec3 in_color;
uniform float u_time;
out vec3 v_color;

void main() {
    v_color = in_color;
    gl_Position = vec4(in_position + vec2(cos(u_time), sin(u_time)), 0.0, 1.0);
}
"""

frag = """
#version 330 core

in vec3 v_color;
uniform float u_time;
out vec4 fragColor;

void main() {
    fragColor = vec4(v_color, 1.0);
}
"""



class Test_Window(skittle.render.window.Window):
    def __init__(self) -> None:
        super().__init__("hello, world!", 500, 500)

        self.program = self.mgl_ctx.program(vrtx, frag)
        vertices = numpy.array([
            # x,     y,     r,   g,   b
            0.0,   0.8,   1.0, 0.0, 0.0,
            -0.8,  -0.8,   0.0, 1.0, 0.0,
            0.8,  -0.8,   0.0, 0.0, 1.0,
        ], dtype='f4')

        vbo = self.mgl_ctx.buffer(vertices.tobytes())

        self.vao = self.mgl_ctx.vertex_array(
            self.program,
            [
                (vbo, '2f 3f', 'in_position', 'in_color'),
            ],
        )

        self.age = 0.0

    def update(self, dt: float):
        self.age += dt
        self.program['u_time'].value = self.age

    def draw(self, ctx: moderngl.Context, camera: asd.render.Camera):
        self.vao.render(moderngl.TRIANGLES)


if __name__ == "__main__":
    asd.init()

    wnd = Test_Window()
    wnd.run()