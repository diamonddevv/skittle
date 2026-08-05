import time
import pygame
import moderngl
import skittle
import numpy
from pyglm import glm

class Mesh():
    VERTEX: str = """
#version 330 core

in vec2 in_vertex_pos;
in vec2 in_uv;

uniform mat4 u_proj_view;
uniform vec2 u_position;
uniform vec2 u_scale;
uniform float u_rot_rad;

out vec2 v_uv;

const float PI = 3.14159;

vec2 rotate(vec2 uv, float angle)
{
    angle += PI/2;
	mat2 rotation = mat2(vec2(sin(angle), -cos(angle)),
						vec2(cos(angle), sin(angle)));
	
	uv -= vec2(0.5);
	uv = uv * rotation;
	uv += vec2(0.5);
	return uv;
}

void main() {
    v_uv = in_uv;
    vec2 world_pos = rotate(in_vertex_pos * u_scale, u_rot_rad) + u_position;
    gl_Position = u_proj_view * vec4(world_pos, 0.0, 1.0);
}
    """
        
    FRAGMENT: str = """
#version 330 core

in vec2 v_uv;
out vec4 fragColor;

uniform vec4 u_tint;

void main() {
    fragColor = u_tint;
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
                 build_vao: bool = True,
                 ) -> None:
        self._ctx = ctx
        self._program = ctx.program(vertex, fragment)

        if build_vao:
            self._vbo = ctx.buffer(glm.array.from_numbers(glm.float32, *vertices).to_bytes())
            self._ibo = ctx.buffer(glm.array.from_numbers(glm.int32, *indices).to_bytes()) if indices != None else None
            self._vao = ctx.vertex_array(self._program, [(self._vbo, format, *attribute_names)], index_buffer=self._ibo)
        
        self._instances = -1
        self._layers = 999

        self.position = glm.vec2(0, 0)
        self.scale: glm.vec2 = glm.vec2(1.0)
        self.color = skittle.color.WHITE
        self.layer: int = 0
        self.rotation_radians: float = 0.0

    def _render_now(self, camera: skittle.render.Camera, overlay: bool = False, mode: int = moderngl.TRIANGLES):
        
        self.uniform('u_proj_view', camera.proj_view_mat(overlay).to_bytes())
        self.uniform('u_time', time.perf_counter())
        self.uniform('u_position', (self.position.x, -self.position.y))
        self.uniform('u_scale', (self.scale.x, self.scale.y))
        self.uniform('u_tint', (self.color.r / 255, self.color.g / 255, self.color.b / 255, self.color.a / 255))
        self.uniform('u_rot_rad', self.rotation_radians)

        self._vao.render(mode, instances=self._instances)

    

    def render(self, camera: skittle.render.Camera, overlay: bool = False, mode: int = moderngl.TRIANGLES, no_cam: bool = False):
    
        if no_cam:
            self._render_now(camera, overlay, mode)
        else:
            layer = camera.calc_layer(self.layer, overlay)
            camera.await_completion(self._render_now, overlay, mode, layer)

    def release(self):
        self._vbo.release()
        if self._ibo != None:
            self._ibo.release()
        self._vao.release()

    def uniform(self, key: str, value):
        if key in self._program:
            if type(value) == bytes:
                self._program[key].write(value) # type: ignore
            else:
                self._program[key].value = value # type: ignore

    def read_uniform(self, key: str):
        return self._program[key]

    @staticmethod
    def uv_quad(width: int, height: int, u0: float = 0.0, v0: float = 0.0, u1: float = 1.0, v1: float = 1.0) -> tuple[list[float], list[int]]:
        hw = width / 2
        hh = height / 2

        vertices = [
                    -hw,  hh, u0, v0, # top left
                     hw,  hh, u1, v0, # top right
                     hw, -hh, u1, v1, # bottom right
                    -hw, -hh, u0, v1, # bottom left
                    ]
        indices = [
            0, 1, 2,
            2, 3, 0
            ]

        return vertices, indices

class QuadMesh(Mesh):
    QUADMESH_FRAGMENT: str = """
#version 330 core

in vec2 v_uv;
out vec4 fragColor;

uniform vec4 u_tint;
uniform vec2 u_scale;
uniform float u_time;
uniform vec4 u_outline_color;
uniform float u_outline_width;

void main() {

    vec2 width = u_outline_width / u_scale;

    if (v_uv.x < width.x || v_uv.x > 1-width.x || v_uv.y < width.y || v_uv.y > 1-width.y)
    {
        fragColor = u_outline_color;
    }
    else fragColor = u_tint;
}
"""

    def __init__(self, ctx: moderngl.Context, vertex: str = Mesh.VERTEX, fragment: str = QUADMESH_FRAGMENT) -> None:
        vertices, indices = Mesh.uv_quad(1, 1)
        
        super().__init__(
            ctx, 
            vertices,
            indices=indices,
            vertex=vertex,
            fragment=fragment
        )

        self.outline_col: skittle.color.Color | None = None
        self.outline_width = 5.0

    def _render_now(self, camera: skittle.render.Camera, overlay: bool = False, mode: int = moderngl.TRIANGLES):
        if self.outline_col != None:
            self.uniform("u_outline_color", (
                self.outline_col.r/255, 
                self.outline_col.g/255, 
                self.outline_col.b/255, 
                self.outline_col.a/255
                ))
            self.uniform("u_outline_width", self.outline_width)
        super()._render_now(camera, overlay, mode)


class TextureMesh(Mesh):
    TEXTURE_FRAGMENT: str = """
#version 330 core

in vec2 v_uv;
out vec4 fragColor;

uniform vec4 u_tint;
uniform sampler2D u_texture;

void main() {
    fragColor = texture(u_texture, v_uv) * u_tint;
}
"""

    def __init__(self, ctx: moderngl.Context, w: int, h: int, u0: float, v0: float, u1: float, v1: float, texture: pygame.Surface, vertex: str = Mesh.VERTEX, fragment: str = TEXTURE_FRAGMENT) -> None:
        vertices, indices = Mesh.uv_quad(w, h, u0, v0, u1, v1)
        
        super().__init__(
            ctx, 
            vertices,
            indices=indices,
            vertex=vertex,
            fragment=fragment
        )
        
        self.texture: moderngl.Texture
        self.load_texture(texture) 

    def load_texture(self, surface: pygame.Surface, filter: int = moderngl.NEAREST):
        data = pygame.image.tobytes(surface, "RGBA")
        self.texture = self._ctx.texture(surface.get_size(), 4, data)
        self.texture.filter = (filter, filter)
    
    def _render_now(self, camera: skittle.render.Camera, overlay: bool = False, mode: int = moderngl.TRIANGLES):
        self.texture.use(0)
        self.uniform('u_texture', 0)
        return super()._render_now(camera, overlay, mode)
    
    def release(self):
        super().release()
        self.texture.release()

class SpriteQuad(TextureMesh):
    def __init__(self, ctx: moderngl.Context, texture: pygame.Surface, vertex: str = Mesh.VERTEX, fragment: str = TextureMesh.TEXTURE_FRAGMENT) -> None:
        super().__init__(ctx, texture.width, texture.height, 0, 0, 1, 1, texture, vertex, fragment)

class SpritesheetQuad(TextureMesh):
    def __init__(self, ctx: moderngl.Context, spritesheet: skittle.resource.Spritesheet, frame: tuple[int, int] = (0, 0), vertex: str = Mesh.VERTEX, fragment: str = TextureMesh.TEXTURE_FRAGMENT) -> None:
        self.frame = frame
        u0, v0, u1, v1 = spritesheet.uv(*self.frame)

        super().__init__(ctx, spritesheet.sprite_w, spritesheet.sprite_h, u0, v0, u1, v1, spritesheet.surface, vertex, fragment)

        self.spritesheet = spritesheet

    def set_sprite(self, frame: tuple[int, int]):
        if frame == self.frame:
            return
        u0, v0, u1, v1 = self.spritesheet.uv(*frame)
        vertices, _ = Mesh.uv_quad(self.spritesheet.sprite_w, self.spritesheet.sprite_h, u0, v0, u1, v1)
        self._vbo.write(glm.array.from_numbers(glm.int32, *vertices).to_bytes())
        self.frame = frame

class MultiInstanceSpritesheetQuad(TextureMesh):
    PER_INSTANCE_VERTEX: str = """
#version 330 core

in vec2 in_vertex_pos;
in vec2 in_uv;

in vec2 in_instance_pos;
in vec2 in_instance_uv_offset;
in vec2 in_instance_uv_scale;
in vec4 in_instance_col;
in float in_instance_rotation;
in vec2 in_instance_scale;

uniform mat4 u_proj_view;
uniform vec2 u_position;
uniform vec2 u_scale;
uniform float u_layer;

out vec4 v_instance_col;
out vec2 v_uv;

const float PI = 3.14159;

vec2 rotate(vec2 uv, float angle) {

    angle += PI/2;
	mat2 rotation = mat2(vec2(sin(angle), -cos(angle)),
						vec2(cos(angle), sin(angle)));
	                   
	uv -= vec2(0.5);
	uv = uv * rotation;
	uv += vec2(0.5);
	return uv;
}

void main() {

    v_uv = in_uv * in_instance_uv_scale + in_instance_uv_offset;
    v_instance_col = in_instance_col;
    vec2 world_pos = (rotate(in_vertex_pos * in_instance_scale, in_instance_rotation) + u_position + in_instance_pos);
    gl_Position = u_proj_view * vec4(world_pos, 0.0, 1.0);
}
    """

    PER_INSTANCE_FRAGMENT: str = """
#version 330 core

in vec2 v_uv;
in vec4 v_instance_col;

out vec4 fragColor;

uniform vec4 u_tint;
uniform sampler2D u_texture;

void main() {
    fragColor = texture(u_texture, v_uv) * v_instance_col;
}
"""

    type _InstanceData = tuple[
        float, # pos x
        float, # pos y
        int, # spritesheet cell x
        int, # spritesheet cell y
        skittle.color.Color, # tint color
        float, # rotation
        glm.vec2, # scale
        ]
    FLOAT_COUNT: int = 13
        

    def __init__(self, ctx: moderngl.Context, spritesheet: skittle.resource.Spritesheet, vertex: str = PER_INSTANCE_VERTEX, fragment: str = PER_INSTANCE_FRAGMENT) -> None:
        super().__init__(ctx, spritesheet.sprite_w, spritesheet.sprite_h, 0, 0, 1, 1, spritesheet.surface, vertex, fragment)
        self.spritesheet = spritesheet

        # need to remake the vao
        self._vao.release()

        # make new vbo and instanced vao
        self._instances = 0
        self._reserve = self.build_vao_vbo(500)

    def build_vao_vbo(self, reserve: int = 500):
        if hasattr(self, "instance_vbo"): self.instance_vbo.release()
        if hasattr(self, "_vao"): self._vao.release()

        instance_size = MultiInstanceSpritesheetQuad.FLOAT_COUNT * 4

        self.instance_vbo = self._ctx.buffer(reserve=instance_size * reserve, dynamic=True)

        self._vao = self._ctx.vertex_array(self._program, [
            (self._vbo, "2f 2f", 'in_vertex_pos', 'in_uv'),
            (self.instance_vbo, "2f 2f 2f 4f f 2f /i", 
             "in_instance_pos", "in_instance_uv_offset", 
             "in_instance_uv_scale", "in_instance_col",
             "in_instance_rotation", "in_instance_scale")
        ], index_buffer=self._ibo)

        return reserve

    def bake_instances(self, instances: list[_InstanceData]):
        data = numpy.empty((len(instances), MultiInstanceSpritesheetQuad.FLOAT_COUNT), dtype=numpy.float32)


        for i, (x, y, cx, cy, col, rot, scale) in enumerate(instances):
            u0, v0, u1, v1 = self.spritesheet.uv(cx, cy)

            data[i] = [
                x, y, 
                u0, v0, 
                u1-u0, v1-v0,
                col.r/255, col.g/255, col.b/255, col.a/255,
                rot,
                scale.x, scale.y,
            ]

        self._instances = len(instances)

        if len(instances) > self._reserve:
            self._reserve = self.build_vao_vbo(int(len(instances) * 1.2))
        
        self.instance_vbo.write(data.tobytes())

    def _render_now(self, camera: skittle.render.Camera, overlay: bool = False, mode: int = moderngl.TRIANGLES):
        if self._instances > 0:
            return super()._render_now(camera, overlay, mode)
        
