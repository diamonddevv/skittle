import moderngl
from _ctx import asd
import pygame

class Test_TexturedQuad(asd.render.window.Window):
    def __init__(self) -> None:
        super().__init__("textured quad", 500, 500)
        
        self.img = pygame.image.load("tests/asset/scotland.png").convert_alpha()
        self.quad = asd.render.mesh.TextureQuad(self.mgl_ctx, 1, 1, self.img)

    def draw(self, ctx: moderngl.Context, camera: asd.render.Camera):
        self.quad.render(camera)



if __name__ == "__main__":
    Test_TexturedQuad().run()