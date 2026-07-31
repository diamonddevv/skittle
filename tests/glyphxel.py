import _ctx

from pyglm import glm
import moderngl
import pygame
import skittle

class test_Text(skittle.render.Window):
    def __init__(self) -> None:
        super().__init__(None, "textured quad", 500, 500, fps_in_title=True)
        
        self.spritesheet = skittle.resource.spritesheet("tests/asset/glyphxel.png")
        self.font = skittle.render.TextRenderer(
            self.ctx,
            self.spritesheet,
            "ABCDEFGHIJKLMNOP" +
            "QRSTUVWXYZ ,.!?|" +
            "abcdefghijklmnop" +
            "qrstuvwxyz£¢$€\"'"+
            "0123456789=-+*/\\"+
            "ÄÅÖÕÜŽŠẞ        " +
            "äåöõüžšß        " +
            "()<>[]{}:;^%&_  ",
            16, 16, caps_only=False, default_glyph_width=8,
            glyph_widths={
                'a': 7,
                'i': 5,
                'l': 6,
                't': 5,
                '.': 4,
                ',': 4,
                "'": 4,
                ':': 4,
                ';': 4,
            })

        self.img = skittle.resource.image("tests/asset/scotland.png")
        self.quad = skittle.render.SpriteQuad(self.ctx, self.img)

        self.panning = False
        self.last_mouse_pos = glm.vec2()


    def draw(self, ctx: moderngl.Context, camera: skittle.render.Camera):
        self.ctx.clear()

        self.quad.render(camera)
        self.font.render(camera, 
                         "nopean tekstin renderimaan varten,\n" +
                         "vastaus on vbo-rebaking!\n\n" +
                         "ja se ei liiku :)\n\n\n" +
                         "this is a list: alpha, beta, gamma sekä delta", 
                         pos=glm.vec2(20, 20), overlay=True)

    def handle_zoom(self, event: pygame.Event):
            if event.y == 0:
                return
            self.camera.zoom *= (1.1 if event.y > 0 else 0.9)
    
    def handle_pan(self, event: pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # i dont know why pygame doesnt expose constants for the mouse buttons?
                self.panning = True
                self.last_mouse_pos = event.pos
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.panning = False

        if event.type == pygame.MOUSEMOTION:
            if self.panning:
                current_pos = glm.vec2(event.pos)
                delta = (current_pos - self.last_mouse_pos) / self.camera.zoom
                self.camera.move(*delta)
                self.last_mouse_pos = current_pos
    

if __name__ == "__main__":
    wnd = test_Text()
    skittle.bind_pygame_event_handler(wnd.handle_zoom, pygame.MOUSEWHEEL)
    skittle.bind_pygame_event_handler(wnd.handle_pan, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION)
    wnd.run()