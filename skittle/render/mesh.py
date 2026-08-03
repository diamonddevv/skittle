"""
rewrite from original mesh.py bc the old one annoyed me
"""

import pygame
import moderngl
import skittle
from pyglm import glm


class Mesh():
    UNIFORM_KEY_PROJECTION_MATRIX: str = "u_projection"
    UNIFORM_KEY_VIEW_MATRIX: str = "u_view"
    UNIFORM_KEY_SIZE: str = "u_size"
    UNIFORM_KEY_POSITION: str = "u_world_position"
    UNIFORM_KEY_SCALE: str = "u_scale"
    UNIFORM_KEY_ROTATION: str = "u_rotation"
    UNIFORM_KEY_COLOR: str = "u_tint"
    UNIFORM_KEY_TIME: str = "u_time"
    UNIFORM_KEY_TEXTURE: str = "u_texture"

    def __init__(self, 
                 ctx: moderngl.Context,
                 program: moderngl.Program,
                 buffers: list[tuple[moderngl.Buffer, str, tuple[str, ...]]],
                 indices: list[int] | None = None,
                 ) -> None:
        self.ctx = ctx
        self._program = program

        self._buffers = buffers
        self._ibo = ctx.buffer(glm.array.from_numbers(glm.int32, *indices).to_bytes()) if indices != None else None
        self._vao: moderngl.VertexArray | None = None
        self.build_vao()

        self._spritesheet: skittle.resource.Spritesheet | None = None

    def _render(self, camera: skittle.render.Camera, 
                position: glm.vec2 = glm.vec2(0),
                size: glm.vec2 = glm.vec2(1),
                scale: glm.vec2 = glm.vec2(1),
                rotation: float = 0,
                color: skittle.color.Color = skittle.color.WHITE,
                overlay: bool = False,
                mode: int = moderngl.TRIANGLES
                ):
        """renders the mesh to the screen at the moment of this call. ignores depth, renders on top of anything that has been drawn already."""

        if self._vao == None:
            return

        self.uniform(Mesh.UNIFORM_KEY_PROJECTION_MATRIX, camera.projection(overlay).to_bytes())
        self.uniform(Mesh.UNIFORM_KEY_VIEW_MATRIX, camera.view_matrix(overlay).to_bytes())
        self.uniform(Mesh.UNIFORM_KEY_POSITION, position)
        self.uniform(Mesh.UNIFORM_KEY_SIZE, size)
        self.uniform(Mesh.UNIFORM_KEY_SCALE, scale)
        self.uniform(Mesh.UNIFORM_KEY_ROTATION, rotation)
        self.uniform(Mesh.UNIFORM_KEY_COLOR, color)
        self.uniform(Mesh.UNIFORM_KEY_TIME, pygame.time.get_ticks())

        self._vao.render(mode)

    def draw(self, camera: skittle.render.Camera, 
                position: glm.vec2 = glm.vec2(0),
                size: glm.vec2 = glm.vec2(1),
                scale: glm.vec2 = glm.vec2(1),
                rotation: float = 0,
                color: skittle.color.Color = skittle.color.WHITE,
                overlay: bool = False,
                layer: int = 0,
                now: bool = False,
                mode: int = moderngl.TRIANGLES):
        """renders the mesh, respecting depth."""
        if now:
            self._render(camera, position, size, scale, rotation, color, overlay, mode)
        else:
            layer = camera.calc_layer(layer, overlay)
            camera.await_completion(self._render, position, size, scale, rotation, color, overlay, mode=mode, layer=layer)

    def release(self):
        """releases memory used by the mesh."""
        if self._vao != None:
            self._vao.release()

        self.release_buffers()

        if self._ibo != None:
            self._ibo.release()

    def release_buffers(self):
        for buf, fmt, names, in self._buffers:
            buf.release()

    def uniform(self, key: str, value):
        """sets a uniform in the mesh shader."""
        if key in self._program:
            if type(value) == bytes:
                self._program[key].write(value) # type: ignore
            else:
                self._program[key].value = value # type: ignore

    def build_vao(self):
        if self._vao != None:
            self._vao.release()
        
        self._vao = self.ctx.vertex_array(self._program, [
            (vbo, fmt, *names)
            for (vbo, fmt, names) in self._buffers
        ], index_buffer=self._ibo)


class InstanceMesh(Mesh):
    def __init__(self, ctx: moderngl.Context, program: moderngl.Program, 
                 vertex_buffer: tuple[moderngl.Buffer, str, tuple[str, ...]], instance_fmt_names_size: tuple[str, tuple[str, ...], int], indices: list[int] | None = None) -> None:
        
        self._instance_fmt, self._instance_names, self._instance_size = instance_fmt_names_size

        self._min_alloc_instances = 64
        self._instance_vbo = ctx.buffer(reserve=self._min_alloc_instances*self._instance_size, dynamic=True)
        self._instances: list[tuple] = []
        self._dirty_instances: list[int] = []

        super().__init__(ctx, program, [vertex_buffer, (
            self._instance_vbo,
            self._instance_fmt,
            self._instance_names
        )], indices)

    def build_instances_vbo(self):
        self._instance_vbo.orphan(max(len(self._instances), self._min_alloc_instances) * self._instance_size) # poor victorian child vbo

        for dirty_idx in self._dirty_instances:
            instance = self._instances[dirty_idx]
            chunk = glm.array(instance)
            self._instance_vbo.write(chunk, dirty_idx * self._instance_size)
        self._dirty_instances.clear()

    def update_instance(self, idx: int, instance: tuple):
        self._instances[idx] = instance
        self._dirty_instances.append(True)

type VerticesIndices = tuple[list[float], list[int]]

def quad() -> VerticesIndices:
    p = 0.5
    u = 0.0
    v = 1.0

    vertices = [
    #    x   y  u  v
        -p,  p, u, u, # top left
         p,  p, u, v, # top right
        -p, -p, v, u, # bottom left
         p, -p, v, v, # bottom right
    ]

    indices = [0, 1, 2, 2, 3, 0]

    return vertices, indices
