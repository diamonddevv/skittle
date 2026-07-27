import _ctx

from pyglm import glm
import moderngl
import pygame
import skittle
import random

class test_Tileset(skittle.render.Window):
    def __init__(self) -> None:
        super().__init__("spritesheet", 500, 500, target_fps=0, fps_in_title=True)
        
        self.spritesheet = skittle.resource.spritesheet("tests/asset/tileset.png")
        self.map_render = skittle.render.MultiInstanceSpritesheetQuad(self.mgl_ctx, self.spritesheet)

        self.tilemap = skittle.resource.Tilemap()

        self.panning = False
        self.last_mouse_pos = glm.vec2()

        self.sprite_idx_x = 0
        self.sprite_idx_y = 0

        
        self.map_render.bake_instances(self.tilemap.bake_instanced_render())

    def draw(self, ctx: moderngl.Context, camera: skittle.render.Camera):
        self.mgl_ctx.clear(1,1,1)
        self.map_render.render(camera)

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
    wnd = test_Tileset()

    skittle.bind_pygame_event_handler(wnd.handle_zoom, pygame.MOUSEWHEEL)
    skittle.bind_pygame_event_handler(wnd.handle_pan, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION)

    wnd.run()