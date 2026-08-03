import _ctx

from pyglm import glm
import moderngl
import pygame
import skittle
import random

class test_Instanced(skittle.render.Window):
    def __init__(self) -> None:
        super().__init__(None, "spritesheet", 500, 500, target_fps=0, fps_in_title=True)
        
        self.spritesheet = skittle.resource.spritesheet("tests/asset/spritesheet.png")
        self.mesh = skittle.render.MultiInstanceSpritesheetQuad(self.ctx, self.spritesheet)

        self.panning = False
        self.last_mouse_pos = glm.vec2()

        self.sprite_idx_x = 0
        self.sprite_idx_y = 0

        self.mesh.bake_instances([(x * 16, y * 16, random.randint(0, 2), random.randint(0, 7), skittle.color.WHITE, random.uniform(0, glm.two_pi()), glm.vec2(random.uniform(1/2, 2))) for x in range(500) for y in range(250)])

    def draw(self, ctx: moderngl.Context, camera: skittle.render.Camera):
        self.ctx.clear()
        self.mesh.render(camera)

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
    wnd = test_Instanced()

    skittle.bind_pygame_event_handler(wnd.handle_zoom, pygame.MOUSEWHEEL)
    skittle.bind_pygame_event_handler(wnd.handle_pan, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION)

    wnd.run()