import skittle
import moderngl

class _Meshes():
    _RECT: skittle.render.QuadMesh

    @staticmethod
    def _init(ctx: moderngl.Context):
        _Meshes._RECT = skittle.render.QuadMesh(ctx)


def rect(camera: skittle.render.Camera, rect: skittle.math.Rect, col: skittle.color.Color):
    _Meshes._RECT.position = rect.pos()
    _Meshes._RECT.scale = rect.size()
    _Meshes._RECT.color = col
    _Meshes._RECT.render(camera)