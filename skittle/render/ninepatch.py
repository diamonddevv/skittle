import moderngl
import skittle



class NinePatchRender():
    def __init__(self, ctx: moderngl.Context, spritesheet: skittle.resource.Spritesheet) -> None:
        self.ctx = ctx
        self.spritesheet = spritesheet

    def draw(self):
        pass