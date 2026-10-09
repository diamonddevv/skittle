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

        self._screenshot_request: str | None = None

    def clear(self, r: float = 0.0, g: float = 0.0, b: float = 0.0, a: float = 1.0):
        self.mgl_ctx.clear(r, g, b, a)

    def request_screenshot(self, path: str):
        self._screenshot_request = path