import _ctx

import moderngl
import numpy
import skittle

vrtx = """
#version 330 core

in vec2 in_position;
in vec3 in_color;
out vec3 v_color;

void main() {
    v_color = in_color;
    gl_Position = vec4(in_position, 0.0, 1.0);
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



class test_Window(skittle.render.Window):
    def __init__(self) -> None:
        super().__init__(None, "hello, world!", 500, 500)

        self.program = self.ctx.program(vrtx, frag)
        vertices = numpy.array([
            # x,     y,     r,   g,   b
            0.0,   0.8,   1.0, 0.0, 0.0,
            -0.8,  -0.8,   0.0, 1.0, 0.0,
            0.8,  -0.8,   0.0, 0.0, 1.0,
        ], dtype='f4')

        vbo = self.ctx.buffer(vertices.tobytes())

        self.vao = self.ctx.vertex_array(
            self.program,
            [
                (vbo, '2f 3f', 'in_position', 'in_color'),
            ],
        )

        self.age = 0.0

    def update(self, dt: float):
        self.age += dt

    def draw(self, ctx: moderngl.Context, camera: skittle.render.Camera):
        self.vao.render(moderngl.TRIANGLES)


if __name__ == "__main__":
    skittle.init()

    wnd = test_Window()
    wnd.run()