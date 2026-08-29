import moderngl
import skittle
from pyglm import glm

class PhysicsWorld():

    def __init__(self) -> None: 
        self._next_id = 0
        self._phys_objs: dict[int, PhysicsObject] = {}

    def track(self, obj: PhysicsObject):
        id = self._next_id
        self._next_id += 1
        obj._id = id
        self._phys_objs[id] = obj

    def remove(self, id: int):
        del self._phys_objs[id]

    def update(self, dt: float):
        for obj in self._phys_objs.values():
            for other in self._phys_objs.values():
                if obj._id == other._id:
                    continue

                if obj.rect.collides_rect(other.rect):
                    if obj._static:
                        continue

                    obj.report_collision(other)

                    if obj._report_only or other._report_only:
                        continue

                    overlap, polarity = obj.rect.calc_overlap(other.rect)

                    obj.try_move(obj._pos + polarity * glm.vec2(
                        overlap.x if overlap.x <= overlap.y else 0,
                        overlap.y if overlap.y <= overlap.x else 0
                    ))       


class PhysicsObject():
    def __init__(self, width: float, height: float, owner: object, x: float = 0, y: float = 0, static: bool = False, report_only: bool = False) -> None:

        self._id: int | None = None
        self.owner = owner

        self._pos = glm.vec2(x, y)
        self.rect = skittle.math.Rect(x - width/2, y -height/2, width, height)
        self._static = static
        self._report_only = report_only

        self.collision_signal = skittle.observer.Signal()

    def try_move(self, pos: glm.vec2):
        self._pos = pos

        self.rect.x = self._pos.x - self.rect.w / 2
        self.rect.y = self._pos.y - self.rect.h / 2

    def get_confirmed_pos(self) -> glm.vec2:
        return self._pos

    def owner_is(self, clazz: type) -> bool:
        return isinstance(self.owner, clazz)

    def get_owner(self):
        return self.owner

    def _render_bounding_box(self, ctx: moderngl.Context, camera: skittle.camera.Camera, layer: int = 10, overlay: bool = False):
        skittle.draw.rect(ctx, camera, self.rect, skittle.color.RED, outline_width=4, layer=layer, overlay=overlay)

    def report_collision(self, other: PhysicsObject):
        self.collision_signal.emit(other)