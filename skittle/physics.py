import moderngl
import skittle
from pyglm import glm

class AABB():
    def __init__(self, width: float, height: float, x: float = 0, y: float = 0, static: bool = False) -> None:
        self.rect = skittle.math.Rect(x, y, width, height)
        
        self._pos = self.get_pos()
        self._last_pos = self._pos
        
        self._static = static

    def move(self, pos: glm.vec2):
        self._last_pos = self._pos
        self._pos = pos

        self.rect.x = pos.x - self.rect.w / 2
        self.rect.y = pos.y - self.rect.h / 2


    def get_pos(self) -> glm.vec2:
        return glm.vec2(
            self.rect.x + self.rect.w / 2,
            self.rect.y + self.rect.h / 2
        )

    def render(self, ctx: moderngl.Context, camera: skittle.camera.Camera):
        skittle.draw.rect(ctx, camera, self.rect, skittle.color.RED, outline_width=4, layer=10)

    def render_last_pos(self, ctx: moderngl.Context, camera: skittle.camera.Camera):
        skittle.draw.rect(ctx, camera, skittle.math.Rect(
            self._last_pos.x - self.rect.w / 2, 
            self._last_pos.y - self.rect.h / 2,
            self.rect.w,
            self.rect.h
        ), skittle.color.BLUE, outline_width=4, layer=10)

class PhysicsWorld():
    def __init__(self) -> None: 
        self._aabbs: list[AABB] = []

    def track(self, aabb: AABB):
        self._aabbs.append(aabb)

    def update(self, dt: float):
        for aabb in self._aabbs:
            # push back whichever thing moved more
            for other in self._aabbs:
                if aabb.rect == other.rect:
                    continue

                if aabb.rect.collides_rect(other.rect) and not aabb._static:
                    # resolve.
                    pass