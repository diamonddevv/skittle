import skittle
import pygame
import moderngl
from pyglm import glm


def uv_quad(ctx: moderngl.Context, w: int = 1, h: int = 1) -> tuple[moderngl.Buffer, moderngl.Buffer]:
    hw = w / 2
    hh = h / 2

    u0 = 0.0
    v0 = 0.0
    u1 = 1.0
    v1 = 1.0

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

    return (
        ctx.buffer(glm.array.from_numbers(glm.float32, vertices).to_bytes()), 
        ctx.buffer(glm.array.from_numbers(glm.int32, indices).to_bytes())
        )

def surf_texture(ctx: moderngl.Context, surface: pygame.Surface) -> moderngl.Texture:
    return ctx.texture(surface.size, 4, pygame.image.tobytes(surface, "RGBA"))

class InstancedBuffer():
    def __init__(self, ctx: moderngl.Context) -> None:
        self.ctx = ctx

        self._buf = ctx.buffer(dynamic=True)
        self._instances = 0
        self._instance_size = 0
        self._released = False

    def set_instance_size(self, nbytes: int):
        self._instance_size = nbytes

    def resize(self, instances: int):
        self._instances = instances

    def write(self, data: bytes):
        self._buf.orphan(self._instances * self._instance_size)
        self._buf.write(data)

    def update_instance(self, instance_data: bytes, index: int):
        if len(instance_data) != self._instance_size:
            raise BufferError(f"data is too long (expected {self._instance_size} bytes, got {len(instance_data)})")
        self._buf.write(instance_data, index * self._instance_size)

    def get(self) -> moderngl.Buffer:
        return self._buf

    def release(self):
        self._released = True
        self._buf.release()