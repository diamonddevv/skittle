import skittle
import moderngl

class Context():
    """
    skittle context. 

    alot of functions take moderngl context and skittle camera as arguments, 
    so this class encapsulates those.
    """
    def __init__(self, mgl_ctx: moderngl.Context, camera: skittle.camera.Camera) -> None:
        self.mgl_ctx = mgl_ctx
        self.camera = camera