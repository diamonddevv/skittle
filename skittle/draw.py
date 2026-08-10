import skittle
import moderngl
from pyglm import glm

class _Meshes():

    _line: skittle.render.mesh.LineMesh

    @staticmethod
    def _init(ctx: moderngl.Context):
        _Meshes._line = skittle.render.mesh.LineMesh(ctx)



def line(ctx: moderngl.Context, camera: skittle.camera.Camera, points: list[glm.vec2], color: skittle.color.Color, closed: bool = False, layer: int = 0, thickness: float = 1.0, overlay: bool = False):
    def _submission():
        ctx.line_width = thickness
        print(len(points))
        _Meshes._line.rebake(points, closed)
        _Meshes._line._render_now(camera, color, overlay)

    camera.submit(_submission, camera.calc_layer(layer, overlay))