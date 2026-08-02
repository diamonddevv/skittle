"""
rewrite from original mesh.py bc the old one annoyed me
"""

import time
import pygame
import moderngl
import skittle
import numpy
from pyglm import glm


class Mesh():
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

    def _render(self):
        """renders the mesh to the screen at the moment of this call. ignores depth, renders on top of anything that has been drawn already."""
        pass

    def draw(self, camera: skittle.render.Camera):
        """renders the mesh, respecting depth."""
        pass

    def release(self):
        """releases memory used by the mesh."""
        pass

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