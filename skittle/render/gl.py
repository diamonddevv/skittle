import skittle
import pygame
import moderngl
from pyglm import glm


def uv_quad(w: int = 1, h: int = 1, u0: float = 0.0, v0: float = 0.0, u1: float = 1.0, v1: float = 1.0, no_uv: bool = False) -> tuple[bytes, bytes]:
    hw = w / 2
    hh = h / 2

    vertices = []

    if no_uv:
        vertices = [
            -hw,  hh, # top left
             hw,  hh, # top right
             hw, -hh, # bottom right
            -hw, -hh, # bottom left
            ]
    else:
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
        glm.array.from_numbers(glm.float32, *vertices).to_bytes(), 
        glm.array.from_numbers(glm.int32, *indices).to_bytes()
        )

def surf_texture(ctx: moderngl.Context, surface: pygame.Surface, filter: int = moderngl.NEAREST) -> moderngl.Texture:
    tex = ctx.texture(surface.size, 4, pygame.image.tobytes(surface, "RGBA"))
    tex.filter = (filter, filter)
    return tex

class InstancedBuffer():
    def __init__(self, ctx: moderngl.Context) -> None:
        self.ctx = ctx

        self._buf = ctx.buffer(reserve=1, dynamic=True)
        self._capacity = 1
        self._instances = 0
        self._overshoot = 1.2
        self._instance_size = 0
        self._released = False

    def set_instance_size(self, nbytes: int):
        self._assert_not_released()
        self._instance_size = nbytes

    def clear(self):
        self._buf.clear()

    def resize(self, instances: int):
        if instances > self._instances:
            self._assert_not_released()
            self._instances = instances
            self._buf.release()
            self._capacity = int(self._instances * self._instance_size * self._overshoot)
            self._buf = self.ctx.buffer(reserve=self._capacity, dynamic=True)

    def update_instance(self, instance_data: bytes, index: int):
        self._assert_not_released()
        if len(instance_data) != self._instance_size:
            raise BufferError(f"data is wrong size (expected {self._instance_size} bytes, got {len(instance_data)})")
            
        self._buf.write(instance_data, index * self._instance_size)

    def write(self, data: bytes):
        self._assert_not_released()
        self._buf.write(data)

    def get(self) -> moderngl.Buffer:
        self._assert_not_released()
        return self._buf

    def release(self):
        self._released = True
        self._buf.release()

    def _assert_not_released(self):
        if self._released:
            raise ValueError("instance buf was previously released")