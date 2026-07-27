import _ctx

import moderngl
import skittle

class Test_TexturedQuad(skittle.render.Window):
    def __init__(self) -> None:
        super().__init__("textured quad", 500, 500, fps_in_title=True)
        
        self.img = skittle.resource.image("tests/asset/scotland.png")
        self.quad = skittle.render.TextureQuad(self.mgl_ctx, 64, 64, self.img)

    def draw(self, ctx: moderngl.Context, camera: skittle.render.Camera):
        self.mgl_ctx.clear(1,1,1)
        self.quad.render(camera)



if __name__ == "__main__":
    Test_TexturedQuad().run()