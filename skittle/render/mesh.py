import pygame
import numpy
import moderngl
import skittle
from pyglm import glm

class Mesh():
    VERTEX: str = """
#version 330 core

in vec2 in_vertex_pos;
in vec2 in_uv;

uniform mat4 u_proj_view;
uniform vec2 u_position;

out vec2 v_uv;

void main() {
    v_uv = in_uv;
    vec2 world_pos = in_vertex_pos + u_position;
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

    def __init__(self, 
                 ctx: moderngl.Context,
                 vertices: list[float],
                 format: str = "2f 2f",
                 attribute_names: list[str] = ['in_vertex_pos', 'in_uv'],
                 indices: list[int] | None = None,
                 vertex: str = VERTEX,
                 fragment: str = FRAGMENT,
                 ) -> None:
        self.ctx = ctx
        self.program = ctx.program(vertex, fragment)

        self.vbo = ctx.buffer(numpy.array(vertices, dtype='f4').tobytes())
        self.ibo = ctx.buffer(numpy.array(indices, dtype='i4').tobytes()) if indices != None else None
        self.vao = ctx.vertex_array(self.program, [(self.vbo, format, *attribute_names)], index_buffer=self.ibo)

        self.position = glm.vec2(0, 0)

    def render(self, camera: skittle.render.Camera, mode: int = moderngl.TRIANGLES):
        self.uniform('u_proj_view', camera.proj_view_mat().to_bytes())
        self.uniform('u_position', (self.position.x, self.position.y))
        self.vao.render(mode)

    def release(self):
        self.vbo.release()
        if self.ibo != None:
            self.ibo.release()
        self.vao.release()

    def uniform(self, key: str, value):
        if key in self.program:
            if type(value) == bytes:
                self.program[key].write(value) # type: ignore
            else:
                self.program[key].value = value # type: ignore

    def read_uniform(self, key: str):
        return self.program[key]

    @staticmethod
    def uv_quad(width: int, height: int, u0: float = 0.0, v0: float = 0.0, u1: float = 1.0, v1: float = 1.0) -> tuple[list[float], list[int]]:
        hw = width / 2
        hh = height / 2

        vertices = [
                    -hw,  hh, u0, v0,  # top left
                     hw,  hh, u1, v0, # top right
                     hw, -hh, u1, v1, # bottom right
                    -hw, -hh, u0, v1, # bottom left
                    ]
        indices = [
            0, 1, 2,
            2, 3, 0
            ]

        return vertices, indices


class TextureMesh(Mesh):
    def __init__(self, ctx: moderngl.Context, width: int, height: int, u0: float, v0: float, u1: float, v1: float, texture: pygame.Surface, vertex: str = Mesh.VERTEX, fragment: str = Mesh.FRAGMENT) -> None:
        vertices, indices = Mesh.uv_quad(width, height, u0, v0, u1, v1)
        
        super().__init__(
            ctx, 
            vertices,
            indices=indices,
            vertex=vertex,
            fragment=fragment
        )

        self._width = width
        self._height = height

        self.texture: moderngl.Texture
        self.load_texture(texture) 

    def load_texture(self, surface: pygame.Surface, filter: int = moderngl.NEAREST):
        data = pygame.image.tobytes(surface, "RGBA")
        self.texture = self.ctx.texture(surface.get_size(), 4, data)
        self.texture.filter = (filter, filter)
    
    def render(self, camera: skittle.render.Camera, mode: int = moderngl.TRIANGLES):
        self.texture.use(0)
        self.uniform('u_texture', 0)
        return super().render(camera, mode)


class SpriteQuad(TextureMesh):
    def __init__(self, ctx: moderngl.Context, width: int, height: int, texture: pygame.Surface, vertex: str = Mesh.VERTEX, fragment: str = Mesh.FRAGMENT) -> None:
        super().__init__(ctx, width, height, 0, 0, 1, 1, texture, vertex, fragment)

class SpritesheetQuad(TextureMesh):
    def __init__(self, ctx: moderngl.Context, width: int, height: int, spritesheet: skittle.resource.Spritesheet, vertex: str = Mesh.VERTEX, fragment: str = Mesh.FRAGMENT) -> None:
        self.frame = (0, 0)
        u0, v0, u1, v1 = spritesheet.xyuv(0, 0)

        super().__init__(ctx, width, height, u0, v0, u1, v1, spritesheet.surface, vertex, fragment)

        self.spritesheet = spritesheet

    def set_sprite(self, frame: tuple[int, int]):
        if frame == self.frame:
            return
        u0, v0, u1, v1 = self.spritesheet.xyuv(*frame)
        vertices, _ = Mesh.uv_quad(self._width, self._height, u0, v0, u1, v1)
        self.vbo.write(numpy.array(vertices, dtype='f4').tobytes())
        self.frame = frame