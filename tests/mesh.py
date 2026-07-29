import _ctx

from pyglm import glm
import moderngl
import pygame
import skittle

class test_TexturedQuad(skittle.render.Window):
    def __init__(self) -> None:
        super().__init__(None, "textured quad", 500, 500, fps_in_title=True)
        
        self.img = skittle.resource.image("tests/asset/scotland.png")
        self.quad = skittle.render.SpriteQuad(self.ctx, self.img)

        self.panning = False
        self.last_mouse_pos = glm.vec2()

    def draw(self, ctx: moderngl.Context, camera: skittle.render.Camera):
        self.ctx.clear(1,1,1)
        self.quad.render(camera)

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
    wnd = test_TexturedQuad()

    skittle.bind_pygame_event_handler(wnd.handle_zoom, pygame.MOUSEWHEEL)
    skittle.bind_pygame_event_handler(wnd.handle_pan, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION)

    wnd.run()