import moderngl
import skittle
from pyglm import glm

class AABB():
    def __init__(self, width: float, height: float, x: float = 0, y: float = 0, static: bool = False) -> None:
        self.rect = skittle.math.Rect(x - width/2, y -height/2, width, height)
        
        self._pos = glm.vec2(x, y)
        self._pos_dirty = False

        self._static = static

    def try_move(self, pos: glm.vec2):
        self._pos = pos
        self._pos_dirty = True

        self.rect.x = self._pos.x - self.rect.w / 2
        self.rect.y = self._pos.y - self.rect.h / 2

    def get_confirmed_pos(self) -> glm.vec2:
        return self._pos

    def _render_bounding_box(self, ctx: moderngl.Context, camera: skittle.camera.Camera, layer: int = 10, overlay: bool = False):
        skittle.draw.rect(ctx, camera, self.rect, skittle.color.RED, outline_width=4, layer=layer, overlay=overlay)

class PhysicsWorld():
    """
    this is so ass ill replace it with pymunk or something later
    """

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
                    overlap, polarity = aabb.rect.calc_overlap(other.rect)

                    aabb.try_move(aabb._pos + polarity * glm.vec2(
                        overlap.x if overlap.x <= overlap.y else 0,
                        overlap.y if overlap.y <= overlap.x else 0
                    ))