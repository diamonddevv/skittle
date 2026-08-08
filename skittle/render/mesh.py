import typing
import pygame
import moderngl
import skittle
import numpy
from pyglm import glm

class TextureMesh():
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
	mat2 rotation = mat2(vec2(cos(angle), -sin(angle)),
						 vec2(sin(angle), cos(angle)));
	
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
uniform sampler2D u_texture;

void main() {
    fragColor = texture(u_texture, v_uv) * u_tint;
}
"""

    def __init__(self, 
                 ctx: moderngl.Context,
                 texture: pygame.Surface,
                 w: int = 1,
                 h: int = 1,
                 u0: float = 0.0,
                 v0: float = 0.0,
                 u1: float = 1.0,
                 v1: float = 1.0,
                 vertex: str = VERTEX,
                 fragment: str = FRAGMENT,
                 ) -> None:
        self._ctx = ctx
        self._program = ctx.program(vertex, fragment)

        vertices, indices = skittle.render.gl.uv_quad(w, h, u0, v0, u1, v1)
        self._vbo = ctx.buffer(vertices)
        self._ibo = ctx.buffer(indices)
        self._vao = ctx.vertex_array(self._program, [(self._vbo, "2f 2f", 'in_vertex_pos', 'in_uv')], index_buffer=self._ibo)
        
        self._render_instances = -1

        self._texture = skittle.render.gl.surf_texture(self._ctx, texture)
        self._size = glm.vec2(texture.width, texture.height)

    def _render_now(self, camera: skittle.camera.Camera, 
                    position: glm.vec2, 
                    scale: glm.vec2 = glm.vec2(1.0), 
                    color: skittle.color.Color = skittle.color.WHITE, 
                    rotation: float = 0.0, 
                    overlay: bool = False, 
                    mode: int = moderngl.TRIANGLES):
        
        self._texture.use(0)

        self.uniform('u_proj_view', camera.proj_view_mat(overlay).to_bytes())
        self.uniform('u_position', (position.x, -position.y))
        self.uniform('u_scale', (scale.x, scale.y))
        self.uniform('u_tint', (color.r / 255, color.g / 255, color.b / 255, color.a / 255))
        self.uniform('u_rot_rad', rotation)
        self.uniform('u_texture', 0)

        self._vao.render(mode, instances=self._render_instances)

    

    def render(self, camera: skittle.camera.Camera, 
                    position: glm.vec2, 
                    scale: glm.vec2 = glm.vec2(1.0), 
                    color: skittle.color.Color = skittle.color.WHITE, 
                    rotation: float = 0.0, 
                    layer: int = 0,
                    overlay: bool = False, 
                    mode: int = moderngl.TRIANGLES,
                    ignore_camera: bool = False):
    
        if ignore_camera:
            self._render_now(camera, position, scale, color, rotation, overlay, mode)
        else:
            layer = camera.calc_layer(layer, overlay)
            camera.submit(lambda: self._render_now(camera, position, scale, color, rotation, overlay, mode), layer)

    def release(self):
        self._vbo.release()
        if self._ibo != None:
            self._ibo.release()
        self._vao.release()

        if self._texture != None:
            self._texture.release()

        self._program.release()

    def uniform(self, key: str, value):
        if key in self._program:
            if type(value) == bytes:
                self._program[key].write(value) # type: ignore
            else:
                self._program[key].value = value # type: ignore

    def read_uniform(self, key: str):
        return self._program[key]


class SpritesheetMesh(TextureMesh):
    def __init__(self, ctx: moderngl.Context, spritesheet: skittle.resource.Spritesheet, frame: tuple[int, int] = (0, 0), vertex: str = TextureMesh.VERTEX, fragment: str = TextureMesh.FRAGMENT) -> None:
        self.frame = frame
        u0, v0, u1, v1 = spritesheet.uv(*self.frame)

        super().__init__(ctx, spritesheet.surface, spritesheet.sprite_w, spritesheet.sprite_h, u0, v0, u1, v1, vertex, fragment)

        self.spritesheet = spritesheet
        self._size = glm.vec2(self.spritesheet.sprite_w, self.spritesheet.sprite_h)

    def set_sprite(self, frame: tuple[int, int]):
        if frame == self.frame:
            return
        u0, v0, u1, v1 = self.spritesheet.uv(*frame)
        vertices, _ = skittle.render.gl.uv_quad(self.spritesheet.sprite_w, self.spritesheet.sprite_h, u0, v0, u1, v1)
        self._vbo.write(vertices)
        self.frame = frame

class InstancedSpritesheetMesh(TextureMesh):
    VERTEX: str = """
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
    FRAGMENT: str = """
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
        

    def __init__(self, ctx: moderngl.Context, spritesheet: skittle.resource.Spritesheet, vertex: str = VERTEX, fragment: str = FRAGMENT) -> None:
        super().__init__(ctx, spritesheet.surface, spritesheet.sprite_w, spritesheet.sprite_h, 0, 0, 1, 1, vertex, fragment)
        self.spritesheet = spritesheet
        self._size = glm.vec2(self.spritesheet.sprite_w, self.spritesheet.sprite_h)

        # make new vbo and instanced vao
        self._ivbo = skittle.render.gl.InstancedBuffer(ctx)
        self._ivbo.set_instance_size(13*4)

        self._instance_data: list[InstancedSpritesheetMesh._InstanceData] = []
        
        self.build_vao_vbo()

    def build_vao_vbo(self):
        if hasattr(self, "_vao"): self._vao.release()

        self._vao = self._ctx.vertex_array(self._program, [
            (self._vbo, "2f 2f", 'in_vertex_pos', 'in_uv'),
            (self._ivbo.get(), "2f 2f 2f 4f f 2f /i", 
             "in_instance_pos", "in_instance_uv_offset", 
             "in_instance_uv_scale", "in_instance_col",
             "in_instance_rotation", "in_instance_scale")
        ], index_buffer=self._ibo)

    def update_instance(self, idx: int, update: typing.Callable[[_InstanceData], _InstanceData]):
        self._instance_data[idx] = update(self._instance_data[idx])
        self._ivbo.update_instance(self.instance_data_to_bytes(self._instance_data[idx]), idx)

    def bake_instances(self, instances: list[_InstanceData] | None = None):
        if instances is not None:
            self._instance_data = instances

        self._ivbo.clear()
        self._ivbo.resize(len(self._instance_data))
        for i, instance in enumerate(self._instance_data):
            self._ivbo.update_instance(self.instance_data_to_bytes(instance), i)

        
        self.build_vao_vbo()


    def _render_now(self, camera: skittle.camera.Camera, position: glm.vec2, scale: glm.vec2 = glm.vec2(1), color: skittle.color.Color = skittle.color.WHITE, rotation: float = 0, overlay: bool = False, mode: int = moderngl.TRIANGLES):
        if self._ivbo._instances > 0:
            self._render_instances = self._ivbo._instances
            return super()._render_now(camera, position, scale, color, rotation, overlay, mode)
    
    def instance_data_to_bytes(self, instance: _InstanceData) -> bytes:
        data = numpy.empty((1, 13), dtype=numpy.float32)
        (x, y, cx, cy, col, rot, scale) = instance
        u0, v0, u1, v1 = self.spritesheet.uv(cx, cy)

        data[0] = [
            x, y, 
            u0, v0, 
            u1-u0, v1-v0,
            col.r/255, col.g/255, col.b/255, col.a/255,
            rot,
            scale.x, scale.y,
        ]

        return data.tobytes()
    
    def indexes(self) -> range:
        return range(len(self._instance_data))