import skittle
import moderngl
from pyglm import glm

class _Meshes():

    _line: skittle.render.mesh.LineMesh

    @staticmethod
    def _init(ctx: moderngl.Context):
        _Meshes._line = skittle.render.mesh.LineMesh(ctx)



def line(ctx: moderngl.Context, camera: skittle.camera.Camera, points: list[glm.vec2], color: skittle.color.Color, closed: bool = False, fill: skittle.color.Color | None = None, layer: int = 0, thickness: float = 1.0, overlay: bool = False):
    def _submission():
        ctx.line_width = thickness
        _Meshes._line.bake(points, closed)
        _Meshes._line._render_now(camera, color, overlay, fill)

    camera.submit(_submission, camera.calc_layer(layer, overlay))


def circle(ctx: moderngl.Context, camera: skittle.camera.Camera, origin: glm.vec2, radius: float, color: skittle.color.Color, filled: bool = False, fill_col: skittle.color.Color | None = None, outline_width: float = 1.0, layer: int = 0, overlay: bool = False):
    """actually just a dodecagon but close enough right"""
    line(ctx, camera, skittle.math.n_gon_vertices(origin, 12, radius), color, filled != None, None if not filled else (fill_col if fill_col != None else color), layer, outline_width, overlay)

def rect(ctx: moderngl.Context, camera: skittle.camera.Camera, rect: skittle.math.Rect, color: skittle.color.Color, filled: bool = False, fill_col: skittle.color.Color | None = None, outline_width: float = 1.0, layer: int = 0, overlay: bool = False):
    points = [
        glm.vec2(rect.x, rect.y),
        glm.vec2(rect.x + rect.w, rect.y),
        glm.vec2(rect.x + rect.w, rect.y + rect.h),
        glm.vec2(rect.x, rect.y + rect.h),
    ]

    line(ctx, camera, points, color, filled != None, None if not filled else (fill_col if fill_col != None else color), layer, outline_width, overlay)

