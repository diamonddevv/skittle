import pygame
import numpy
import moderngl
import skittle

class Mesh():
    def __init__(self, 
                 ctx: moderngl.Context,
                 vertex: str,
                 fragment: str,
                 vertices: list[float],
                 format: str,
                 attribute_names: list[str],
                 indices: list[int] | None = None,
                 ) -> None:
        self.ctx = ctx
        self.program = ctx.program(vertex, fragment)

        self.vbo = ctx.buffer(numpy.array(vertices, dtype='f4').tobytes())
        self.ibo = ctx.buffer(numpy.array(indices, dtype='i4').tobytes()) if indices != None else None
        content = [(self.vbo, format, *attribute_names)]

        self.vao = ctx.vertex_array(self.program, content, index_buffer=self.ibo)

    def render(self, camera: skittle.render.Camera, mode: int = moderngl.TRIANGLES):
        self.vao.render(mode)

    def release(self):
        self.vbo.release()
        if self.ibo != None:
            self.ibo.release()
        self.vao.release()

    @staticmethod
    def uv_quad(width: int, height: int, x: float = 0.0, y: float = 0.0, u: float = 1.0, v: float = 1.0, ) -> tuple[list[float], list[int]]:
        hw = width / 2
        hh = height / 2

        vertices = [
                    -hw,  hh, x, v, # bottom left
                     hw,  hh, u, v, # bottom right
                     hw, -hh, u, y, # top right
                    -hw, -hh, x, y  # top left
                    ]
        indices = [
            0, 1, 2,
            2, 3, 0
            ]

        return vertices, indices


class TextureQuad(Mesh):
    VERTEX: str = """
#version 330 core

in vec2 in_position;
in vec2 in_uv;

uniform mat4 u_proj_view;
uniform vec2 u_model_pos;   // per-object world position

out vec2 v_uv;

void main() {
    v_uv = in_uv;
    vec2 world_pos = in_position + u_model_pos;
    gl_Position = u_proj_view * vec4(world_pos, 0.0, 1.0);
}
    """

    FRAGMENT: str = """
#version 330 core

in vec2 v_uv;
out vec4 fragColor;

uniform sampler2D u_texture;

void main() {
    fragColor = texture(u_texture, v_uv);
}
"""

    def __init__(self, ctx: moderngl.Context, width: int, height: int, texture: pygame.Surface, x: float = 0.0, y: float = 0.0, u: float = 1.0, v: float = 1.0, vertex: str = VERTEX, fragment: str = FRAGMENT) -> None:

        vertices, indices = Mesh.uv_quad(width, height, x, y, u, v)
        
        super().__init__(
            ctx, vertex, fragment, 
            vertices, "2f 2f", ['in_position', 'in_uv'], 
            indices
        )
        self.texture: moderngl.Texture
        self.load_texture(texture)
    

    def load_texture(self, surface: pygame.Surface, filter: int = moderngl.NEAREST):
        data = pygame.image.tobytes(surface, "RGBA", True)
        self.texture = self.ctx.texture(surface.get_size(), 4, data)
        self.texture.filter = (filter, filter)
    
    def render(self, camera: skittle.render.Camera, mode: int = moderngl.TRIANGLES):
        self.texture.use(0)
        self.program['u_texture'].value = 0
        self.program['u_proj_view'].write(camera.proj_view_mat().to_bytes())
        self.program['u_model_pos'].value = (0, 0)
        return super().render(camera, mode)