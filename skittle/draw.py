import skittle
import moderngl

class _Meshes():
    _SPRITESHEET_TEXTURE: skittle.render.Mesh

    @staticmethod
    def _init(ctx: moderngl.Context):
        _Meshes._SPRITESHEET_TEXTURE = skittle.render.Mesh(ctx)



def spritesheet_texture():
    pass